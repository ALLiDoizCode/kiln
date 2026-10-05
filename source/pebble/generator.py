"""Pebble: a small, low, rounded stone of a few broad planes, one closed piece.

docs/style/rock-shapes.md, Pebble. The stone is cut from a block by about a dozen planes that
touch a tipped ellipsoid, no two facing close together, and by the ground, below its widest
part (ADR 9: deliberate planes, no noise). It is softened on its own
(tools/stone.py) and stays one closed skin: a pebble is one stone, so it is not built under
the pieces rule of ADR 13 (source/pebble/brief.md, Decisions).

Every pebble is drawn one metre wide, softened there, and shrunk to its spec's bounds, so a
soft edge is a share of the stone's width and the run of sizes is one construction.

A spec gives the seed and the bounds. A seed draws whole pebbles, one after another, until
one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Matrix, Vector
from pipeline import conventions

PEBBLES = 120  # how many whole pebbles one seed may draw before it is given up
SOFT = (0.012, 0.03)  # the least and most a soft edge eats into each plane beside it, as a share of the stone's width
# The planes, in rings from the ground up: how many, and how far up each faces (the upward part of
# its direction on the ellipsoid). A side faces a little down or a little up, never level: facing
# down it is undercut and meets the ground leaning out; level it would stand upright.
RINGS = (
    dict(name="sides", count=(5, 6), up=(0.14, 0.3), either_way=True),
    dict(name="shoulders", count=(3, 5), up=(0.45, 0.75)),
    dict(name="cap", count=(1, 1), up=(0.95, 1.0)),
)
RING_JITTER = 0.3  # how far a plane's direction strays from an even spacing round its ring, as a share of that spacing
APART = 0.5  # no two planes face closer together than this, radians: the planes are few and broad
REACH = (0.86, 1.0)  # how far out each plane stands, as a share of the ellipsoid's radius that way
SUNK = (0.2, 0.32)  # how far above the ground the ellipsoid's middle is, as a share of the stone's height: it is cut where it still widens
TIP = (6.0, 14.0)  # how far the ellipsoid is tipped from level, degrees: the summit goes off the middle


def draw(rng, lo, hi):
    """One raw pebble filling the bounds lo..hi, or None when its planes would not do."""
    half, height = (hi - lo) / 2, hi.z - lo.z
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z + height * rng.uniform(*SUNK)))
    radii = Vector((half.x, half.y, hi.z - middle.z))
    spin = Matrix.Rotation(rng.uniform(0, math.tau), 3, "Z") @ Matrix.Rotation(math.radians(rng.uniform(*TIP)), 3, "Y")
    directions = []
    for ring in RINGS:
        count = rng.randint(*ring["count"])
        turn = rng.uniform(0, math.tau)
        for i in range(count):
            for _ in range(40):
                angle = turn + (i + rng.uniform(-RING_JITTER, RING_JITTER)) * math.tau / count
                z = rng.uniform(*ring["up"]) * (rng.choice((-1, 1)) if ring.get("either_way") else 1)
                direction = Vector((math.sqrt(1 - z * z) * math.cos(angle), math.sqrt(1 - z * z) * math.sin(angle), z))
                if all(direction.angle(other) > APART for other in directions):
                    directions.append(direction)
                    break
            else:
                return None
    # Each plane touches the ellipsoid, or stands a little inside it, where its direction leaves it.
    planes = [(-stone.Z, -lo.z)]
    for direction in directions:
        direction = spin @ direction
        touch = middle + Vector((direction.x * radii.x, direction.y * radii.y, direction.z * radii.z)) * rng.uniform(*REACH)
        normal = Vector((direction.x / radii.x, direction.y / radii.y, direction.z / radii.z)).normalized()
        planes.append((normal, normal.dot(touch)))
    bm = stone.solid(planes)
    if bm is None:
        return None
    stone.fit([bm], lo, hi)
    return bm


def shape(spec, strict=True):
    """The softened pebble for the spec's seed, as (its one piece in a list, the corner normals).

    With `strict` off the first pebble that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    # Drawn one metre wide: the kit's least sizes are a metre rock's, and a soft edge is a share of the width.
    shrink = hi.x - lo.x
    metre = {**spec, "bounds_m": {"min": list(lo / shrink), "max": list(hi / shrink)}}
    refused = []
    for take in range(1, PEBBLES + 1):
        bm = draw(rng, lo / shrink, hi / shrink)
        if bm is None:
            refused.append(f"pebble {take}: planes that face too close together, or leave one out")
            continue
        pieces = [bm]
        done = stone.finish(pieces, metre, SOFT)
        problems = [done] if isinstance(done, str) else []
        if not problems:
            for vert in bm.verts:
                vert.co *= shrink
            bm.normal_update()
            problems = stone.unmet(name, pieces, spec, conv, extra=(("fullness", validate.check_fullness),)) if strict else []
        if not problems:
            print(f"{name} seed {spec['seed']}: pebble {take} of up to {PEBBLES} meets the spec")
            return pieces, done[1]
        refused.append(f"pebble {take}: " + "; ".join(problems))
        bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its pebbles meets the spec:\n  " + "\n  ".join(refused))


def build_pebble(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    obj = stone.join(spec["objects"][0], pieces, normals, material, colour)
    # Where the surface may be cut to lie flat (tools/paint.py): only round the ground. What is seen
    # of a pebble is one dome, and it is painted as one island, with no cut across it.
    floor = spec["bounds_m"]["min"][2]
    for edge in obj.data.edges:
        edge.use_seam = all(abs(obj.data.vertices[v].co.z - floor) < stone.FLAT for v in edge.vertices)
    return obj
