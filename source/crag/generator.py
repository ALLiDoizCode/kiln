"""Crag: many leaning prisms of different heights sharing one base, with small blocks at the foot.

docs/style/rock-shapes.md, Crag. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py): four to six sides that taper toward a slanted cap ringed by chamfers. The
pieces stand on the ground and pass into each other; each is softened on its own and they stay
separate closed pieces in the one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Many pieces with a clear size order: the tallest prism, the other prisms each lower and
   narrower than the one before, and two or three blocks a fraction of their size.
2. The tallest is off-centre: it stands at one end and the others fan out to one side of it,
   in two rows, the lower the further out.
3. They lean, and lean together: every piece leans within a few degrees of one direction, back
   from the way the crag steps down, and each cap slants down the way its piece leans.
4. A foot: one block stands beside the tallest prism, one beyond the lowest, and a third between.
5. Flat caps ringed by chamfers. Long vertical edges run from the ground to the shoulder.

A spec gives the seed, the bounds, how many pieces and how many of them are prisms. A seed
draws whole crags, one after another, until one meets the spec, and fails the build with the
reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Vector
from pipeline import conventions

CRAGS = 40  # how many whole crags one seed may draw before it is given up
SOFT = (0.012, 0.045)  # the least and most a soft edge eats into each plane beside it, metres
SOFT_SHARE = 0.012  # and the most as a share of the crag's height: a small crag has small chamfers for it to eat
SIDES = ((5, 6), (4, 5))  # how many sides the tallest prism has, and the others
TAPER = (0.1, 0.22)  # how much narrower a prism is at its cap than at the ground, each side, as a share of its radius
LEAN = (9.0, 15.0)  # how far a prism leans, degrees
LEAN_BACK = (10.0, 40.0)  # the crag leans back from the way it steps down, this far round from straight back, degrees, to the side away from the first block: the tallest prism hangs over its own end and not over the block
LEAN_TOGETHER = 14.0  # the pieces lean within this of one direction, degrees
CAP_SLANT = (8.0, 20.0)  # how far a cap slants from level, degrees
SLANT_TOGETHER = 0.5  # a cap slants down within this of the way its piece leans, radians: a leaning column cut nearly square
OUTLINE_JITTER = 0.25  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.88, 1.0)  # how far out each side stands, as a share of the piece's radius that way
SHOULDER = (0.26, 0.36)  # how far below a prism's cap its chamfers start, as a share of its radius
CHAMFER_INSET = (0.5, 0.9)  # how far in from the side a chamfer meets the cap, over how far below the cap it starts
LOWEST = (0.38, 0.46)  # the lowest prism's height as a share of the tallest's; the others are spaced evenly between, by ratio
HEIGHT_JITTER = 0.04  # how far a prism's height strays from that spacing, as a share of it
NARROWER = (0.78, 0.88)  # each prism's radius over that of the one before
# Where the prisms stand, round a tallest one of radius 1 at the origin: the first row beside it and the
# second beyond, each as (how far out, how far round from the middle of the fan in degrees).
ROWS = dict(near=((1.0, 1.25), (38.0, 62.0)), far=((1.75, 2.1), (6.0, 26.0)), middle=((1.15, 1.4), (0.0, 12.0)))
# A block: how far out from its prism's middle it stands, as a share of that prism's radius; its radius over the
# tallest prism's (each next one `shrink` of the last); its height as a share of the bounds' (each next one `lower`
# of the last); and its shape: `lean` is its lean over a prism's, `shoulder` a share of its height.
BLOCK = dict(out=(0.9, 1.1), radius=(0.75, 0.88), shrink=0.78, tall=(0.17, 0.24), lower=0.8, sides=(4, 5), taper=(8.0, 16.0), lean=0.4, slant=(3.0, 9.0), shoulder=(0.22, 0.34))
# Where round its prism each block stands, in degrees from the way the crag steps down: the first beside the
# tallest prism, the second beyond the lowest, the third beside one between, on the other side from the first.
BLOCK_AT = ((105.0, 125.0), (-25.0, 25.0), (-110.0, -70.0))


def prism(rng, sides, centre, radii, height, tapers, slant, drop, tip):
    """One piece (stone.prism) that leans `tip[1]` degrees toward `tip[0]`. `tapers` is how far each
    side leans in, degrees, as a range; `slant` the cap's, as a range; its chamfers start `drop` below its cap."""
    way, lean = tip
    cap = stone.leaning(way + rng.uniform(-SLANT_TOGETHER, SLANT_TOGETHER), math.radians(90 - rng.uniform(*slant)))
    # The cap is over where the piece's middle has leaned to at that height.
    top = (cap, cap.dot(centre + stone.Z * height + reach_of(tip, height)))
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        # A side facing the way the piece leans hangs over, and the one behind leans in further.
        tilt = rng.uniform(*tapers) - lean * math.cos(azimuth - way)
        normal = stone.leaning(azimuth, math.radians(tilt))
        walls.append((normal, normal.dot(centre + out * reach)))
    return stone.prism(walls, top, drop, [drop * rng.uniform(*CHAMFER_INSET) for _ in walls])


def reach_of(tip, height):
    """How far a piece's top stands from over its foot: `tip` is (the way it leans, how far in degrees)."""
    return stone.leaning(tip[0], 0) * (height * math.tan(math.radians(tip[1])))


def plan(rng, prisms, blocks, shape):
    """Where each piece stands, its radius and its height, prisms from the tallest down and then the
    blocks; the way the crag steps down, seen from the tallest prism; and which side of that the first block is on.

    Laid out round a tallest prism of radius 1 at the origin and a height of 1. `shape` is the
    bounds' (width, depth), which the layout is later stretched to: the further of two prisms
    from the tallest is the further once stretched, and so the lower.
    """
    fan = rng.uniform(0, math.tau)
    others = prisms - 1
    near = (others + 1) // 2
    places = []
    for index in range(others):
        row = "middle" if others == 1 else "near" if index < near else "far"
        out, turn = ROWS[row]
        side = 1 if index % 2 == 0 else -1
        if row == "far" and others - near == 1:
            side = rng.choice((-1, 1))
        at = fan + side * math.radians(rng.uniform(*turn))
        places.append(stone.leaning(at, 0).to_2d() * rng.uniform(*out))
    # Stretched as the bounds are, the nearer stands the taller.
    aspect = shape[0] / shape[1]
    places.sort(key=lambda place: math.hypot(place.x * aspect, place.y))
    step = rng.uniform(*LOWEST) ** (1 / max(others, 1))
    plans = [(Vector((0, 0)), 1.0, 1.0)]
    for place in places:
        _, radius, height = plans[-1]
        plans.append((place, radius * rng.uniform(*NARROWER), height * step * (1 + rng.uniform(-HEIGHT_JITTER, HEIGHT_JITTER))))
    hosts = [plans[0], plans[-1], plans[len(plans) // 2]][:blocks]
    radius, tall = rng.uniform(*BLOCK["radius"]), rng.uniform(*BLOCK["tall"])
    flip = rng.choice((-1, 1))
    made = []
    for (place, host_radius, _), turn in zip(hosts, BLOCK_AT):
        at = fan + flip * math.radians(rng.uniform(*turn))
        made.append((place + stone.leaning(at, 0).to_2d() * (host_radius * rng.uniform(*BLOCK["out"])), radius, tall))
        radius *= BLOCK["shrink"]
        tall *= BLOCK["lower"]
    return plans + made, fan, flip


def draw(rng, spec):
    """The raw pieces of one crag, prisms first, or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    count = rng.randint(spec["overlap"]["min_count"], spec["overlap"]["max_count"])
    prisms = spec["cluster"]["min_prisms"]
    plans, fan, flip = plan(rng, prisms, count - prisms, (hi.x - lo.x, hi.y - lo.y))
    way = fan + math.pi - flip * math.radians(rng.uniform(*LEAN_BACK))  # the way the crag leans
    tips = [(way + math.radians(rng.uniform(-LEAN_TOGETHER, LEAN_TOGETHER)), rng.uniform(*LEAN) * (1.0 if index < prisms else BLOCK["lean"])) for index in range(count)]
    # The layout is scaled so that the pieces fill the bounds, feet and leaning tops together. How far
    # a top leans is in metres whatever the scale, so the scale is found by trying again.
    scale = [1.0, 1.0]
    for _ in range(8):
        low, high = [], []
        for i in range(2):
            ends = [(centre[i] * scale[i] + lean * reach_of(tip, tall * height)[i], radius * scale[i]) for (centre, radius, tall), tip in zip(plans, tips) for lean in (0.0, 1.0)]
            low.append(min(at - radius for at, radius in ends))
            high.append(max(at + radius for at, radius in ends))
            scale[i] *= (hi[i] - lo[i]) / (high[i] - low[i])
    pieces = []
    for index, ((centre, radius, tall), tip) in enumerate(zip(plans, tips)):
        middle = Vector((lo.x + centre.x * scale[0] - low[0], lo.y + centre.y * scale[1] - low[1], lo.z))
        radii = (radius * scale[0], radius * scale[1])
        if index < prisms:
            tapers = [math.degrees(math.atan(min(radii) * share / (tall * height))) for share in TAPER]
            bm = prism(rng, rng.randint(*SIDES[min(index, 1)]), middle, radii, tall * height, tapers, CAP_SLANT, min(radii) * rng.uniform(*SHOULDER), tip)
        else:
            bm = prism(rng, rng.randint(*BLOCK["sides"]), middle, radii, tall * height, BLOCK["taper"], BLOCK["slant"], tall * height * rng.uniform(*BLOCK["shoulder"]), tip)
        if bm is None:
            for made in pieces:
                made.free()
            return None
        pieces.append(bm)
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the crag for the spec's seed, and their corner normals.

    With `strict` off the first crag that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    refused = []
    for take in range(1, CRAGS + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"crag {take}: a piece that is not convex")
            continue
        height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
        done = stone.finish(pieces, spec, (SOFT[0], max(SOFT[0], min(SOFT[1], SOFT_SHARE * height))))
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv, (("cluster", validate.check_cluster),)) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: crag {take} of up to {CRAGS} meets the spec")
            return pieces, done[1]
        refused.append(f"crag {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its crags meets the spec:\n  " + "\n  ".join(refused))


def build_crag(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
