"""Standing stone: a tall stone that tapers and leans, with one or two small blocks against its foot.

docs/style/rock-shapes.md, Standing stone. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py): the stone has four to six sides that taper toward a slanted cap ringed by
chamfers; a foot block is a low plate. The pieces stand on the ground and pass into each other;
each is softened on its own and they stay separate closed pieces in the one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: the stone, and one or two blocks a fraction of its size.
2. It tapers and leans: every side leans in, and the whole stone leans a few degrees one way,
   so its top stands off the middle of its foot.
3. A foot: the blocks sit low against the base and reach out past it.
4. A flat cap, slanted, ringed by chamfers. Long vertical edges run from the ground to the shoulder.

A spec gives the seed, the bounds and how many pieces. A seed draws whole stones, one after
another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
from mathutils import Vector
from pipeline import conventions

STONES = 40  # how many whole stones one seed may draw before it is given up
SOFT = (0.012, 0.05)  # the least and most a soft edge eats into each plane beside it, metres
SIDES = (4, 6)  # how many sides the stone has
FLAT = (0.55, 1.0)  # the stone's depth over its width at the ground: a slab at one end, a lozenge at the other
TAPER = (3.0, 5.5)  # how far each side leans in, degrees
LEAN = (4.0, 7.0)  # how far the whole stone leans, degrees
CAP_SLANT = (10.0, 22.0)  # how far the cap slants from level, degrees
OUTLINE_JITTER = 0.25  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.88, 1.0)  # how far out each side stands, as a share of the stone's radius that way
SHOULDER = (0.06, 0.11)  # how far below the cap its chamfers start, as a share of the stone's height
CHAMFER_INSET = (0.5, 1.0)  # how far in from the side a chamfer meets the cap, over how far below the cap it starts
# A foot block: where round the stone it stands (the first anywhere, the second this many degrees on), how far out
# along the stone's radius its middle is, its radius over the stone's, its height as a share of the bounds', and its shape.
BLOCK = dict(apart=(100.0, 220.0), out=(0.75, 1.0), radius=(0.5, 0.68), shrink=0.7, tall=(0.1, 0.18), sides=(4, 5), lean=(10.0, 20.0), slant=(3.0, 9.0), shoulder=(0.25, 0.4))


def prism(rng, sides, centre, radii, height, lean, slant, shoulder, tip=None):
    """One piece (stone.prism). `lean` and `slant` are ranges, degrees; `tip` is (the way the whole piece leans, how far in degrees)."""
    way = rng.uniform(0, math.tau)
    cap = stone.leaning(way if tip is None else tip[0] + rng.uniform(-0.8, 0.8), math.radians(90 - rng.uniform(*slant)))
    top = (cap, cap.dot(centre + stone.Z * height))
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        # A side facing the way the piece leans stands nearer upright, and the one behind leans in further.
        tilt = rng.uniform(*lean) - (tip[1] * math.cos(azimuth - tip[0]) if tip else 0.0)
        normal = stone.leaning(azimuth, math.radians(tilt))
        walls.append((normal, normal.dot(centre + out * reach)))
    drop = height * rng.uniform(*shoulder)
    return stone.prism(walls, top, drop, [drop * rng.uniform(*CHAMFER_INSET) for _ in walls])


def draw(rng, spec):
    """The raw pieces of one standing stone, largest first, or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    count = rng.randint(spec["overlap"]["min_count"], spec["overlap"]["max_count"])
    tip = (rng.uniform(0, math.tau), rng.uniform(*LEAN))
    # Laid out round a stone of radius 1, then moved and scaled so the outlines fill the bounds. The
    # stone's top stands off its foot the way it leans, and the layout leaves room for that.
    plans = [(Vector((0, 0)), 1.0, height)]
    at = rng.uniform(0, math.tau)
    radius = rng.uniform(*BLOCK["radius"])
    for _ in range(count - 1):
        plans.append((stone.leaning(at, 0).to_2d() * rng.uniform(*BLOCK["out"]), radius, height * rng.uniform(*BLOCK["tall"])))
        at += math.radians(rng.uniform(*BLOCK["apart"]))
        radius *= BLOCK["shrink"]
    low = [min(centre[i] - radius for centre, radius, _ in plans) for i in range(2)]
    high = [max(centre[i] + radius for centre, radius, _ in plans) for i in range(2)]
    scale = [(hi[i] - lo[i]) / (high[i] - low[i]) for i in range(2)]
    pieces = []
    for index, (centre, radius, tall) in enumerate(plans):
        middle = Vector((lo.x + (centre.x - low[0]) * scale[0], lo.y + (centre.y - low[1]) * scale[1], lo.z))
        radii = (radius * scale[0], radius * scale[1])
        if index == 0:
            bm = prism(rng, rng.randint(*SIDES), middle, radii, tall, TAPER, CAP_SLANT, SHOULDER, tip)
        else:
            bm = prism(rng, rng.randint(*BLOCK["sides"]), middle, radii, tall, BLOCK["lean"], BLOCK["slant"], BLOCK["shoulder"])
        if bm is None:
            for made in pieces:
                made.free()
            return None
        pieces.append(bm)
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the stone for the spec's seed, and their corner normals.

    With `strict` off the first stone that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    refused = []
    for take in range(1, STONES + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"stone {take}: a piece that is not convex")
            continue
        done = stone.finish(pieces, spec, SOFT)
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: stone {take} of up to {STONES} meets the spec")
            return pieces, done[1]
        refused.append(f"stone {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its stones meets the spec:\n  " + "\n  ".join(refused))


def build_standing_stone(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
