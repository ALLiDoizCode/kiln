"""Stepped spire of weathered rock: a base that is a broken column, narrower tiers each off the middle of the one below and leaning, and blocks at its foot.

docs/style/rock-shapes.md, Stepped spire. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py): sides round a tipped cap ringed by chamfers. The base's main mass stands on the
ground with two lower shoulders against it; each tier above stands on the cap of the one below,
its bottom sunk into it; two blocks stand at the foot, and on some seeds a small block sits on
the base's ledge. Each piece is softened on its own and they stay separate closed pieces in the
one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Nothing is upright: every piece leans, each a different amount, all roughly one way.
2. The tallest part is off-centre: each tier sits toward the edge of the cap below, on the side
   the spire leans to, so one flank climbs in ledges and the other is nearly one face.
3. A clear size order, and no two alike: tiers of different heights, one much narrower than the
   one below and another only a little, each with its own number of sides and squeezed its own way.
4. A foot: the shoulders stand behind the lean and the blocks under it, each large enough to read.
5. Caps are tipped planes ringed by chamfers, each tipped its own way; they show as ledges.
6. Long vertical edges: six to eight sides on the main mass, and a groove from the ground up
   wherever a shoulder passes into it.

A spec gives the seed, the bounds, how many tiers and pieces there may be. A seed draws whole
spires, one after another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Vector
from pipeline import conventions

SPIRES = 40  # how many whole spires one seed may draw before it is given up
SOFT = (0.012, 0.025)  # the least and most a soft edge eats into each plane beside it, metres
SOFT_SHARE = 0.005  # and the most as a share of the spire's height
OUTLINE_JITTER = {4: 0.1, 5: 0.14, 6: 0.16}  # how far a side's direction strays from an even spacing, as a share of that spacing, by how many sides; 0.22 with more
OUTLINE_IN = (0.9, 1.0)  # how far out each side stands, as a share of the piece's radius that way
MIN_DROP = 0.045  # the least a piece's chamfers start below its cap, metres: their edges must be long enough to soften
SQUEEZE = (0.75, 0.95)  # a piece is narrower one way than the other by this
TOGETHER = 0.7  # the pieces lean within this of one direction, radians
# How the height is shared, by how many tiers there are: the base's share, and how the rest is split among the
# tiers above it (weights: the first is the top tier's, the rest dealt in any order): never evenly.
HEIGHTS = {3: dict(base=(0.36, 0.46), rest=((0.56, 0.68), (1.0, 1.0))), 4: dict(base=(0.3, 0.36), rest=((0.6, 0.72), (1.0, 1.0), (1.35, 1.6)))}
# How far each tier above the base leans, degrees: one range each, dealt in any order. The base leans `BASE["lean"]`.
LEANS = ((2.0, 4.0), (5.0, 8.0), (8.0, 11.0))
# A tier's radius where it stands, over the radius of the one below at its shoulder, by how many tiers
# there are: one range for each tier above the base, dealt in any order, so one step is large and another small.
STEPS = {3: ((0.47, 0.53), (0.66, 0.72)), 4: ((0.52, 0.58), (0.66, 0.72), (0.68, 0.74))}
# The base's main mass: its sides; how far they lean in and how far the whole leans, degrees; how far its cap tips;
# how far below the cap its chamfers start, as a share of its lesser radius at the shoulder; and how far in a chamfer meets the cap, over that.
BASE = dict(sides=(6, 8), taper=(2.5, 5.5), lean=(3.0, 5.0), tilt=(4.0, 9.0), shoulder=(0.12, 0.18), inset=(0.8, 1.1))
# A tier above the base: its sides (never as many as the tier below); its taper and its cap as the base's; how far
# toward the edge of the cap below it sits, as a share of the room between its own side and that edge, and how far
# round from the way the spire leans, radians; its chamfers (the last tier's start lower and stand steeper).
TIER = dict(sides=(4, 6), taper=(1.0, 2.5), tilt=(4.0, 9.0), off=(0.9, 1.15), off_turn=0.6, shoulder=(0.16, 0.24), top_shoulder=(0.22, 0.3), inset=(0.8, 1.1), top_inset=(0.6, 0.8))
# The shoulders of the base, the larger first: how far round from straight behind the lean each stands, degrees, one
# to either side; how far out along the base's radius its middle is; its radius over the base's; its height over the
# base's; its sides; its taper, lean and cap tip, degrees; and its chamfers.
SHOULDERS = (
    dict(at=(15.0, 55.0), out=(0.4, 0.52), radius=(0.62, 0.72), tall=(0.66, 0.8), sides=(5, 6)),
    dict(at=(-95.0, -55.0), out=(0.6, 0.75), radius=(0.45, 0.55), tall=(0.42, 0.54), sides=(4, 5)),
)
SHOULDER = dict(taper=(3.0, 6.0), lean=(3.0, 7.0), tilt=(6.0, 14.0), shoulder=(0.12, 0.18), inset=(0.8, 1.2))
# The blocks at the foot, the larger first: how far round from the way the spire leans each stands, degrees, one to
# either side; how far out; its radius over the base's; its height over the base's; and its shape.
BLOCKS = (
    dict(at=(40.0, 80.0), out=(0.8, 0.92), radius=(0.32, 0.4), tall=(0.16, 0.24)),
    dict(at=(-50.0, -20.0), out=(0.85, 0.95), radius=(0.23, 0.29), tall=(0.11, 0.16)),
)
BLOCK = dict(sides=(4, 5), taper=(6.0, 12.0), lean=(0.0, 4.0), tilt=(4.0, 12.0), shoulder=(0.2, 0.28), inset=(0.6, 0.9))
# A block on the base's ledge, on some seeds: how likely; how far from the middle of the base's cap it sits, on the
# side away from the tier above, and its radius, both over the base's lesser radius at its shoulder; its height over
# that tier's; and its shape.
LEDGE = dict(chance=0.6, out=(0.45, 0.55), radius=(0.34, 0.44), tall=(0.3, 0.5), sides=(4, 5), taper=(4.0, 8.0), lean=(3.0, 8.0), tilt=(5.0, 11.0), shoulder=(0.14, 0.2), inset=(0.6, 0.9))


def piece(rng, sides, centre, radii, lifts, top, drop, inset, tip=None, even=True):
    """One piece (stone.prism) standing on the level through `centre`, where it is `radii` wide.

    Its sides lean in by one of `lifts`, degrees. When `even`, that is the lean of a side at the
    piece's lesser radius and each side leans in proportion to how far out it stands, and so do
    the chamfers: the piece keeps its outline all the way up, only smaller, which a slender
    piece must or a short side runs out before the shoulder. With `tip`, (a direction, degrees), the whole is sheared that way: the side facing
    it hangs over and the one behind leans in further. `top` is the plane of its cap; its
    chamfers start `drop` below it and meet it `inset` (a range, over `drop`) in."""
    turn = rng.uniform(0, math.tau)
    lift, into = rng.uniform(*lifts), rng.uniform(*inset)
    shear = stone.leaning(tip[0], 0) * math.tan(math.radians(tip[1])) if tip else Vector((0, 0, 0))
    drop = max(drop, MIN_DROP)
    walls, reaches = [], []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-1, 1) * OUTLINE_JITTER.get(sides, 0.22)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        reaches.append(reach / min(radii))
        normal = stone.leaning(azimuth, math.atan(math.tan(math.radians(lift)) * reaches[-1]) if even else math.radians(rng.uniform(*lifts)))
        # Sheared about the level it stands on: a point z above that level moves `shear` times z.
        normal = Vector((normal.x, normal.y, normal.z - normal.dot(shear))).normalized()
        walls.append((normal, normal.dot(centre + out * reach)))
    return stone.prism(walls, top, drop, [drop * (into * reach if even else rng.uniform(*inset)) for reach in reaches], floor=centre.z)


def cap(over, toward, tilt):
    """The plane of a cap through the point `over`, tipped `tilt` degrees down toward `toward`."""
    normal = stone.leaning(toward, math.radians(90 - tilt))
    return normal, normal.dot(over)


def squeezed(rng, radius):
    """A piece's two radii: more than `radius` one way and less the other, the same in area."""
    by = math.sqrt(rng.uniform(*SQUEEZE))
    radii = (radius / by, radius * by)
    return radii if rng.random() < 0.5 else radii[::-1]


def over(centre, tall, tip):
    """Where the middle of a piece is `tall` above its foot, leaning as `tip` says."""
    return centre + stone.Z * tall + stone.leaning(tip[0], 0) * (tall * math.tan(math.radians(tip[1])))


def standing(rng, shape, sides, centre, radii, tall, tip):
    """A piece on the ground or on a ledge, of one of the shapes above (SHOULDER, BLOCK, LEDGE)."""
    top = cap(over(centre, tall, tip), rng.uniform(0, math.tau), rng.uniform(*shape["tilt"]))
    return piece(rng, sides, centre, radii, shape["taper"], top, min(min(radii), tall) * rng.uniform(*shape["shoulder"]), shape["inset"], tip)


def draw(rng, spec):
    """The raw pieces of one spire: the tiers from the base up, then the shoulders, the blocks, and the block on the ledge if there is one; or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    least, most = spec["overlap"]["min_count"], spec["overlap"]["max_count"]
    foot_pieces = len(SHOULDERS) + len(BLOCKS)
    tiers = rng.randint(max(spec["spire"]["tiers"][0], least - foot_pieces - 1), min(spec["spire"]["tiers"][1], most - foot_pieces))
    count = tiers + foot_pieces
    on_ledge = count < most and (count < least or rng.random() < LEDGE["chance"])
    way = rng.uniform(0, math.tau)  # the way the spire leans, and the side of each cap the next tier sits toward
    side = rng.choice((-1, 1))

    # Where the pieces on the ground stand, round a main mass of radius 1 at the origin: (direction, how far out, radius, shape).
    feet = [(way + math.pi + side * math.radians(rng.uniform(*part["at"])), rng.uniform(*part["out"]), rng.uniform(*part["radius"]), part) for part in SHOULDERS]
    feet += [(way + side * math.radians(rng.uniform(*part["at"])), rng.uniform(*part["out"]), rng.uniform(*part["radius"]), part) for part in BLOCKS]
    # Stretched so that the base and what stands round it fill the bounds' width and depth.
    scale, shift = [], []
    for axis in range(2):
        ends = [(0.0, 1.0)] + [(stone.leaning(at, 0)[axis] * out, radius) for at, out, radius, _ in feet]
        low, high = min(c - r for c, r in ends), max(c + r for c, r in ends)
        scale.append((hi[axis] - lo[axis]) / (high - low))
        shift.append(lo[axis] - low * scale[axis])
    # Everything is drawn with the base's lesser radius, and the whole is widened along the other axis at the end: planes stay planes.
    wide = 0 if scale[0] >= scale[1] else 1
    widen = scale[wide] / scale[1 - wide]
    shift[wide] /= widen
    middle = Vector((shift[0], shift[1], lo.z))  # of the main mass, on the ground
    base = scale[1 - wide]

    # The tiers, from the base up.
    plan = HEIGHTS[tiers]
    share = rng.uniform(*plan["base"])
    # The top tier takes the least of the height and never the most of the lean: it is a tier of rock, not a post.
    weights = [rng.uniform(*span) for span in rng.sample(plan["rest"][1:], tiers - 2) + [plan["rest"][0]]]
    tops, at = [share], share
    for weight in weights:
        at += (1 - share) * weight / sum(weights)
        tops.append(at)
    leans = [BASE["lean"]] + rng.sample(LEANS, tiers - 1)
    if leans[-1] is LEANS[-1]:
        leans[-1], leans[-2] = leans[-2], leans[-1]
    steps = rng.sample(STEPS[tiers], tiers - 1)
    pieces = []
    centre, radii, sides = middle, squeezed(rng, base), rng.randint(*BASE["sides"])
    base_tall = ledge = None
    for index in range(tiers):
        last = index == tiers - 1
        kind = BASE if index == 0 else TIER
        tall = lo.z + tops[index] * height - centre.z
        tip = (way + rng.uniform(-TOGETHER, TOGETHER), rng.uniform(*leans[index]))
        head = over(centre, tall, tip)
        tilt, toward = rng.uniform(*kind["tilt"]), rng.uniform(0, math.tau)
        loss = tall * math.tan(math.radians(sum(kind["taper"]) / 2))
        narrow = tuple(max(r - loss, 0.6 * r) for r in radii)  # at the shoulder
        drop = min(narrow) * rng.uniform(*(TIER["top_shoulder"] if last else kind["shoulder"]))
        pieces.append(piece(rng, sides, centre, radii, kind["taper"], cap(head, toward, tilt), drop, TIER["top_inset"] if last else kind["inset"], tip, even=index > 0))
        if index == 0:
            base_tall, base_tip = tall, tip
        if last:
            break
        # The next sits on this one's cap, toward its edge on the side the spire leans to, and is sunk into it.
        radius = math.sqrt(narrow[0] * narrow[1]) * rng.uniform(*steps[index])
        off = stone.leaning(way + rng.uniform(-TIER["off_turn"], TIER["off_turn"]), 0) * (max(min(narrow) - radius, 0.1 * radius) * rng.uniform(*TIER["off"]))
        sink = drop + (off.length + radius) * math.tan(math.radians(tilt)) + 0.01 * height
        if index == 0:
            ledge = (head, off, min(narrow), sink, lo.z + tops[1] * height - head.z)
        centre = Vector((head.x + off.x, head.y + off.y, head.z - sink))
        radii = squeezed(rng, radius)
        sides = rng.choice([n for n in range(TIER["sides"][0], TIER["sides"][1] + 1) if n != sides])

    # The shoulders and the blocks, on the ground round the main mass.
    for at, out, radius, part in feet:
        centre = middle + stone.leaning(at, 0) * (out * base)
        shape = SHOULDER if part in SHOULDERS else BLOCK
        tip = (base_tip[0] + rng.uniform(-0.4, 0.4), rng.uniform(*shape["lean"]))
        pieces.append(standing(rng, shape, rng.randint(*part.get("sides", BLOCK["sides"])), centre, squeezed(rng, radius * base), base_tall * rng.uniform(*part["tall"]), tip))
    if on_ledge:
        head, off, room, sink, above = ledge
        centre = head - off.normalized() * (room * rng.uniform(*LEDGE["out"])) - stone.Z * sink
        tip = (math.atan2(off.y, off.x), rng.uniform(*LEDGE["lean"]))
        pieces.append(standing(rng, LEDGE, rng.randint(*LEDGE["sides"]), centre, squeezed(rng, room * rng.uniform(*LEDGE["radius"])), sink + above * rng.uniform(*LEDGE["tall"]), tip))
    if any(bm is None for bm in pieces):
        for bm in pieces:
            if bm is not None:
                bm.free()
        return None
    for bm in pieces:
        for vert in bm.verts:
            vert.co[wide] *= widen
        bm.normal_update()
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the spire for the spec's seed, and their corner normals.

    With `strict` off the first spire that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
    soft = (SOFT[0], max(SOFT[0], min(SOFT[1], SOFT_SHARE * height)))
    refused = []
    for take in range(1, SPIRES + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"spire {take}: a piece that is not convex")
            continue
        done = stone.finish(pieces, spec, soft)
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv, (("spire", validate.check_spire),)) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: spire {take} of up to {SPIRES} meets the spec")
            return pieces, done[1]
        refused.append(f"spire {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its spires meets the spec:\n  " + "\n  ".join(refused))


def build_spire(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
