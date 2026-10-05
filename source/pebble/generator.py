"""Pebble: a small, low, rounded stone, a flat plate with a broad rim, one closed piece.

docs/style/rock-shapes.md, Pebble. The stone is made of planes, in three rings from the ground
up (ADR 9: deliberate planes, no noise; tools/stone.py, `prism`): six to eight short sides that
lean in, round an uneven outline; over each a broad plane of the rim; and one cap that tips a
little. It is softened on its own
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
from mathutils import Vector
from pipeline import conventions

PEBBLES = 120  # how many whole pebbles one seed may draw before it is given up
SOFT = (0.012, 0.03)  # the least and most a soft edge eats into each plane beside it, as a share of the stone's width
SIDES = (6, 8)  # how many sides go round the stone: enough that none is a face of its own
SIDE_JITTER = 0.25  # how far a side's direction strays from an even spacing round the stone, as a share of that spacing
SIDE_REACH = (0.85, 1.0)  # where a side meets the ground, as a share of the footprint's radius that way: the outline is uneven
SIDE_SLOPE = (55.0, 70.0)  # how far from level a side stands, degrees: it leans in, and is never upright
RIM_DROP = (0.45, 0.6)  # how far below the cap the sides stop and the rim begins, as a share of the height
RIM_SLOPE = (24.0, 36.0)  # how far from level the rim over each side is, degrees: broad, and lit as the top is
CAP_DROP = (0.2, 0.35)  # how far the cap falls from one side of the stone to the other, as a share of the height: the summit goes off the middle


def draw(rng, lo, hi):
    """One raw pebble filling the bounds lo..hi (stone.prism), or None when its planes do not make a convex plate."""
    half, height = (hi - lo) / 2, hi.z - lo.z
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    count = rng.randint(*SIDES)
    turn = rng.uniform(0, math.tau)
    drop = height * rng.uniform(*RIM_DROP)
    walls, insets = [], []
    for i in range(count):
        angle = turn + (i + rng.uniform(-SIDE_JITTER, SIDE_JITTER)) * math.tau / count
        slope = math.radians(rng.uniform(*SIDE_SLOPE))
        # A side faces out as the footprint's ellipse does there, and meets the ground a little inside it.
        out = Vector((math.cos(angle) / half.x, math.sin(angle) / half.y, 0)).normalized()
        normal = out * math.sin(slope) + stone.Z * math.cos(slope)
        foot = middle + Vector((half.x * math.cos(angle), half.y * math.sin(angle), 0)) * rng.uniform(*SIDE_REACH)
        walls.append((normal, normal.dot(foot)))
        # The rim runs in from the side's top edge to the cap: its slope gives how far in it meets the cap.
        insets.append(drop / math.tan(math.radians(rng.uniform(*RIM_SLOPE))) - drop / math.tan(slope))
    # The cap: nearly level, falling CAP_DROP of the height across the stone's width.
    tip = math.atan(height * rng.uniform(*CAP_DROP) / (2 * half.x))
    cap = stone.leaning(rng.uniform(0, math.tau), math.pi / 2 - tip)
    bm = stone.prism(walls, (cap, cap.dot(middle + stone.Z * height)), drop, insets, floor=lo.z)
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
            refused.append(f"pebble {take}: sides, rim and cap that do not make a convex plate")
            continue
        pieces = [bm]
        done = stone.finish(pieces, metre, SOFT)
        problems = [done] if isinstance(done, str) else []
        if not problems:
            for vert in bm.verts:
                vert.co *= shrink
            bm.normal_update()
            problems = stone.unmet(name, pieces, spec, conv, extra=(("fullness", validate.check_fullness), ("low", validate.check_low), ("rounded", validate.check_rounded))) if strict else []
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
