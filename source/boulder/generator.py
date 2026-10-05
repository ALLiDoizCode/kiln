"""Boulder: one full, heavy, weathered lump, wider than tall, one closed piece.

docs/style/rock-shapes.md, Boulder. The stone is the space behind a set of planes (ADR 9:
deliberate planes, no noise; tools/stone.py, `solid`), each touching, or cutting a little into,
an ellipsoid that sits low in the bounds: a cap that tips, a ring of shoulders, a ring of sides
and one to three chamfers across corners. The ellipsoid's middle is below the middle of the
height, so the ground cuts it near its widest and the stone bulges; its upper part is pushed
to one side, so the summit is off the middle and one flank is steeper than the other. It is
softened on its own (tools/stone.py) and stays one closed skin: a boulder is one stone, so it
is not built under the pieces rule of ADR 13 (source/boulder/brief.md, Decisions).

Every boulder is drawn three metres wide, softened there, and shrunk to its spec's bounds, so
a soft edge is a share of the stone's width and the run of sizes is one construction.

A spec gives the seed and the bounds. A seed draws whole boulders, one after another, until
one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Vector
from pipeline import conventions

BOULDERS = 2000  # how many whole boulders one seed may draw before it is given up
DRAWN_M = 3.0  # the width every boulder is drawn at, metres: the kit's least sizes are a rock's of this size
SOFT = (0.035, 0.06)  # the least and most a soft edge eats into each plane beside it, metres at the drawn width
MIDDLE_UP = (0.12, 0.26)  # how high the ellipsoid's middle is, as a share of the height: the ground cuts it near its widest
PUSH = (0.22, 0.5)  # how far the top of the stone is pushed to one side, as a share of the half extents
CAP_TIP = (3.0, 11.0)  # how far the cap is from level, degrees
CAP_DEPTH = (0.9, 1.0)  # how far out a plane stands, as a share of the ellipsoid's reach that way: below 1 it cuts in
SHOULDERS = (4, 6)  # how many planes ring the cap
SHOULDER_LIFT = (34.0, 58.0)  # how far above level a shoulder faces, degrees
SHOULDER_DEPTH = (0.86, 1.0)
SIDES = (5, 8)  # how many planes go round the stone
SIDE_LIFT = (-12.0, 24.0)  # how far above level a side faces, degrees: below 0 it is undercut, and the stone bulges over its foot
SIDE_DEPTH = (0.88, 1.0)
CHAMFERS = (1, 3)  # planes across corners, wide enough to catch the light as faces of their own
CHAMFER_LIFT = (12.0, 44.0)
CHAMFER_DEPTH = (0.82, 0.93)
JITTER = 0.3  # how far a plane's direction strays from an even spacing round the stone, as a share of that spacing


def draw(rng, lo, hi):
    """One raw boulder filling the bounds lo..hi, or None when one of its planes cuts nothing off."""
    half, height = (hi - lo) / 2, hi.z - lo.z
    up = height * rng.uniform(*MIDDLE_UP)
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z + up))
    radii = Vector((half.x, half.y, height - up))
    way = rng.uniform(0, math.tau)
    push = Vector((math.cos(way) * half.x, math.sin(way) * half.y, 0)) * rng.uniform(*PUSH)

    def plane(azimuth, lift, depth):
        normal = stone.leaning(azimuth, math.radians(lift))
        reach = math.sqrt(sum((radii[i] * normal[i]) ** 2 for i in range(3)))
        # The higher a plane faces, the further it is pushed with the top of the stone.
        return normal, normal.dot(middle + push * max(0.0, normal.z)) + reach * rng.uniform(*depth)

    def ring(count, lift, depth):
        turn = rng.uniform(0, math.tau)
        return [plane(turn + (i + rng.uniform(-JITTER, JITTER)) * math.tau / count, rng.uniform(*lift), depth) for i in range(count)]

    planes = [(-stone.Z, -lo.z), plane(rng.uniform(0, math.tau), 90 - rng.uniform(*CAP_TIP), CAP_DEPTH)]
    planes += ring(rng.randint(*SHOULDERS), SHOULDER_LIFT, SHOULDER_DEPTH)
    planes += ring(rng.randint(*SIDES), SIDE_LIFT, SIDE_DEPTH)
    planes += [plane(rng.uniform(0, math.tau), rng.uniform(*CHAMFER_LIFT), CHAMFER_DEPTH) for _ in range(rng.randint(*CHAMFERS))]
    return stone.solid(planes)


def shape(spec, strict=True):
    """The softened boulder for the spec's seed, as (its one piece in a list, the corner normals).

    With `strict` off the first boulder that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    # Drawn three metres wide: the kit's least sizes are a rock's of that size, and a soft edge is a share of the width.
    shrink = (hi.x - lo.x) / DRAWN_M
    drawn = {**spec, "bounds_m": {"min": list(lo / shrink), "max": list(hi / shrink)}}
    extra = (("fullness", validate.check_fullness), ("low", validate.check_low), ("mass", validate.check_mass))
    refused = []
    for take in range(1, BOULDERS + 1):
        bm = draw(rng, lo / shrink, hi / shrink)
        if bm is None:
            refused.append(f"boulder {take}: a plane that cuts nothing off")
            continue
        pieces = [bm]
        done = stone.finish(pieces, drawn, SOFT)
        problems = [done] if isinstance(done, str) else []
        if not problems:
            for vert in bm.verts:
                vert.co *= shrink
            bm.normal_update()
            problems = stone.unmet(name, pieces, spec, conv, extra=extra) if strict else []
        if not problems:
            print(f"{name} seed {spec['seed']}: boulder {take} of up to {BOULDERS} meets the spec")
            return pieces, done[1]
        refused.append(f"boulder {take}: " + "; ".join(problems))
        bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its boulders meets the spec:\n  " + "\n  ".join(refused))


def build_boulder(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
