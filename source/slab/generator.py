"""Slab: a wide, low plate of rock with a polygonal outline and a nearly flat top, two or three overlapped.

docs/style/rock-shapes.md, Slab. Every piece is a plate cut from a block by planes (ADR 9): the
ground, a gently tipped top, five to seven sides that lean in, and a chamfer between the top
and each side. The pieces stand on the ground and pass into each other; each is softened on
its own and they stay separate closed pieces in the one mesh (ADR 13, tools/stone.py).

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: a dominant plate, a smaller and taller one pushed
   halfway into one side of it, and (when the spec asks for three) a small low one at its foot.
2. Nothing upright: every side leans in by its own amount.
3. The tallest part is off-centre: the taller plate stands toward one side of the bounds.
4. Flat caps ringed by chamfers: the tops tip a few degrees, roughly the same way.

A spec gives the seed, the bounds and how many pieces. A seed draws whole slabs, one after
another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
from mathutils import Vector
from pipeline import conventions

SLABS = 40  # how many whole slabs one seed may draw before it is given up
SOFT = (0.012, 0.045)  # the least and most a soft edge eats into each plane beside it, metres
SIDES = ((6, 7), (5, 6), (5, 5))  # how many sides each piece's outline has, largest piece first
LEAN = (12.0, 24.0)  # how far a side leans in from upright, degrees
TILT = (2.0, 5.5)  # how far a top tips from level, degrees
TILT_TOGETHER = 0.7  # the tops tip within this of one direction, radians
OUTLINE_JITTER = 0.3  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.86, 1.0)  # how far out each side stands, as a share of the piece's radius that way
CHAMFER_DROP = (0.22, 0.34)  # how far below the cap its chamfers start, as a share of the piece's height
CHAMFER_INSET = (0.7, 1.5)  # how far in from the side a chamfer meets the cap, over how far below the cap it starts
# The dominant plate: its height as a share of the bounds'. The plates are laid out round it, and the layout is then fitted to the bounds.
DOMINANT = dict(tall=(0.52, 0.66))
# The taller plate: how far out along the dominant one's radius its middle stands, and its radius over the dominant one's.
SECOND = dict(out=(0.56, 0.7), radius=(0.56, 0.66))
# The small one at the foot: where round the dominant plate it stands, in degrees on from the taller plate; then as above.
THIRD = dict(at=(115.0, 245.0), out=(0.86, 1.0), radius=(0.3, 0.38), tall=(0.26, 0.38))


def plate(rng, sides, centre, radii, height, group):
    """One plate (stone.prism): sides that lean in round an outline of `sides` sides, a gently tipped cap, a chamfer over each side."""
    cap = stone.leaning(group + rng.uniform(-TILT_TOGETHER, TILT_TOGETHER), math.radians(90 - rng.uniform(*TILT)))
    top = (cap, cap.dot(centre + stone.Z * height))
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        normal = stone.leaning(azimuth, math.radians(rng.uniform(*LEAN)))
        walls.append((normal, normal.dot(centre + out * reach)))
    drop = height * rng.uniform(*CHAMFER_DROP)
    return stone.prism(walls, top, drop, [drop * rng.uniform(*CHAMFER_INSET) for _ in walls])


def draw(rng, spec):
    """The raw pieces of one slab, largest first, or None when a plate did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    count = rng.randint(spec["overlap"]["min_count"], spec["overlap"]["max_count"])
    toward = rng.uniform(0, math.tau)  # where the taller plate stands, seen from the dominant one
    group = rng.uniform(0, math.tau)  # the way the tops tip
    # Laid out round a dominant plate of radius 1, then moved and scaled so the plates' outlines fill the bounds.
    plans = [(Vector((0, 0)), 1.0, height * rng.uniform(*DOMINANT["tall"]))]
    out = stone.leaning(toward, 0).to_2d()
    plans.append((out * rng.uniform(*SECOND["out"]), rng.uniform(*SECOND["radius"]), height))
    if count >= 3:
        at = stone.leaning(toward + math.radians(rng.uniform(*THIRD["at"])), 0).to_2d()
        plans.append((at * rng.uniform(*THIRD["out"]), rng.uniform(*THIRD["radius"]), height * rng.uniform(*THIRD["tall"])))
    low = [min(centre[i] - radius for centre, radius, _ in plans) for i in range(2)]
    high = [max(centre[i] + radius for centre, radius, _ in plans) for i in range(2)]
    scale = [(hi[i] - lo[i]) / (high[i] - low[i]) for i in range(2)]
    pieces = []
    for (centre, radius, tall), sides in zip(plans, SIDES):
        middle = Vector((lo.x + (centre.x - low[0]) * scale[0], lo.y + (centre.y - low[1]) * scale[1], lo.z))
        bm = plate(rng, rng.randint(*sides), middle, (radius * scale[0], radius * scale[1]), tall, group)
        if bm is None:
            for made in pieces:
                made.free()
            return None
        pieces.append(bm)
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the slab for the spec's seed, and their corner normals.

    With `strict` off the first slab that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    refused = []
    for take in range(1, SLABS + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"slab {take}: a plate that is not convex")
            continue
        done = stone.finish(pieces, spec, SOFT)
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: slab {take} of up to {SLABS} meets the spec")
            return pieces, done[1]
        refused.append(f"slab {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its slabs meets the spec:\n  " + "\n  ".join(refused))


def build_slab(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
