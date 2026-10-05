"""Stepped spire: a wide fluted base, narrower tiers stacked on it like a telescope, and buttresses and blocks at its foot.

docs/style/rock-shapes.md, Stepped spire. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py): sides that lean in toward a flat cap ringed by chamfers. The base stands on the
ground; each tier above stands on the cap of the one below, its bottom sunk into it; buttresses
and blocks stand on the ground and pass into the base. Each piece is softened on its own and
they stay separate closed pieces in the one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: the base, the tiers each a clear step narrower than
   the one below, buttresses in a run of heights, and two blocks a fraction of their size.
2. Nothing upright where there is radius to spend: the base flares, and a buttress leans in
   against it, so its outer face leans further still. The upper tiers taper only a little.
3. The tallest part is off-centre: every tier stands off the middle of the one below, to one
   side, and the buttresses stand round the other side. One flank is sheer, the other steps.
4. A foot: buttresses whose caps slope outward, and a block either side of the sheer flank.
5. Flat caps ringed by chamfers; the caps of the tiers show as ledges.
6. Long vertical edges: seven or eight sides on the base, running from the ground to its shoulder.

A spec gives the seed, the bounds, how many tiers and how many pieces. A seed draws whole spires,
one after another, until one meets the spec, and fails the build with the reasons when none does.
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
OUTLINE_JITTER = 0.2  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.92, 1.0)  # how far out each side stands, as a share of the piece's radius that way
BLOCKS = 2  # the pieces that are neither tiers nor blocks are buttresses
# Where the cap of each tier but the last is, as a share of the spire's height, by how many tiers there are.
TOPS = {3: ((0.42, 0.47), (0.72, 0.77)), 4: ((0.34, 0.38), (0.58, 0.62), (0.8, 0.84))}
# The base: its sides; how far they lean in, degrees; how far its cap tips; how far below the cap its chamfers
# start, as a share of its lesser radius at the shoulder; and how far in a chamfer meets the cap, over that.
BASE = dict(sides=(7, 8), lean=(9.5, 12.0), tilt=(2.0, 5.0), shoulder=(0.14, 0.2), inset=(0.8, 1.1))
# A tier above the base: its sides (the last tier's are `top_sides`); the ledge left round it on the cap of the one
# below, where that cap is narrowest, as a share of that one's lesser radius at its shoulder; how far off the middle
# of the one below it stands, as a share of that ledge, and how far round from the common way, radians; how much narrower it is at its own shoulder, as a
# share of its radius; its chamfers as the base's (the last tier's start lower and stand steeper: `top_shoulder`, `top_inset`); its cap's tip, degrees.
# Four tiers have less radius each to spend than three: `SLIM` gives the ledge and the narrowing by how many there are.
TIER = dict(sides=(5, 6), top_sides=(4, 5), off=(0.6, 0.9), off_turn=0.35, shoulder=(0.18, 0.26), top_shoulder=(0.45, 0.6), top_inset=(0.6, 0.8), inset=(0.8, 1.1), tilt=(2.0, 5.0))
SLIM = {3: dict(ledge=(0.16, 0.22), narrower=(0.13, 0.19)), 4: dict(ledge=(0.12, 0.16), narrower=(0.08, 0.12))}
# A buttress: how far round from straight opposite the way the tiers step it stands, by how many there are, degrees, and
# how far that strays; how far out along the base's radius its middle is; its sides, how far they lean in, and how far
# the whole leans toward the base, degrees; how far its cap slopes down and outward; and its chamfers, as a share of
# its radius. Its size is in `SIZES`.
RIB = dict(at={1: (0.0,), 2: (-48.0, 48.0), 3: (-72.0, 0.0, 72.0)}, stray=10.0, out=(0.92, 1.0), sides=(4, 5), taper=(3.0, 5.0), lean=(7.0, 10.0), slant=(14.0, 24.0), shoulder=(0.12, 0.18), inset=(1.3, 1.9))
# A block: how far round from the way the tiers step each stands, degrees, one to either side; how far out along the
# base's radius; the second's radius over the first's; its height over its radius; and its shape.
BLOCK = dict(at=((15.0, 35.0), (-70.0, -50.0)), out=(0.85, 0.95), shrink=0.75, tall=(0.7, 1.0), sides=(4, 5), lean=(8.0, 14.0), slant=(3.0, 9.0), shoulder=(0.2, 0.28), inset=(0.6, 0.9))
# How large the pieces at the foot are, by how many tiers there are, so that the surfaces the pieces show fall in a
# run with no two alike (the tiers' own sizes fall between the buttresses'). The first buttress's radius over the
# base's, and its height as a share of the height of the base's shoulder: below the band the foot is measured in.
# Then, for each next buttress, its radius and its height over the last one's. And the first block's radius over the base's.
SIZES = {
    3: dict(radius=(0.35, 0.39), tall=(0.63, 0.7), steps=(((0.68, 0.74), (0.58, 0.64)), ((0.82, 0.88), (0.8, 0.86))), block=(0.22, 0.28)),
    4: dict(radius=(0.27, 0.31), tall=(0.52, 0.58), steps=(((0.7, 0.76), (0.62, 0.68)), ((0.82, 0.88), (0.8, 0.86))), block=(0.19, 0.22)),
}


def piece(rng, sides, centre, radii, lifts, top, drop, inset, tip=None):
    """One piece (stone.prism) standing on the level through `centre`, where it is `radii` wide.

    Each side leans in by one of `lifts`, degrees; with `tip`, (a direction, degrees), the whole
    leans that way, so the side facing it hangs over and the one behind leans in further.
    `top` is the plane of its cap, and its chamfers start `drop` below it."""
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        tilt = rng.uniform(*lifts) - (tip[1] * math.cos(azimuth - tip[0]) if tip else 0.0)
        normal = stone.leaning(azimuth, math.radians(tilt))
        walls.append((normal, normal.dot(centre + out * reach)))
    return stone.prism(walls, top, drop, [drop * rng.uniform(*inset) for _ in walls], floor=centre.z)


def cap(rng, over, slant, toward=None):
    """The plane of a cap through the point `over`, tipped `slant` degrees (a range) down toward `toward`, or any way."""
    azimuth = rng.uniform(0, math.tau) if toward is None else toward
    normal = stone.leaning(azimuth, math.radians(90 - rng.uniform(*slant)))
    return normal, normal.dot(over)


def draw(rng, spec):
    """The raw pieces of one spire: the tiers from the base up, then the buttresses, then the blocks; or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    tiers = spec["spire"]["tiers"]
    count = rng.randint(spec["overlap"]["min_count"], spec["overlap"]["max_count"])
    ribs = count - tiers - BLOCKS
    way = rng.uniform(0, math.tau)  # the way the tiers step off-centre; the buttresses stand round the other side

    # Where the pieces on the ground stand, round a base of radius 1 at the origin: (direction, how far out, radius).
    sizes = SIZES[tiers]
    feet = []
    radius = rng.uniform(*sizes["radius"])
    for turn, (shrink, _) in zip(rng.sample(RIB["at"][ribs], ribs), sizes["steps"] + sizes["steps"][-1:]):
        feet.append((way + math.pi + math.radians(turn + rng.uniform(-RIB["stray"], RIB["stray"])), rng.uniform(*RIB["out"]), radius))
        radius *= rng.uniform(*shrink)
    side = rng.choice((-1, 1))
    radius = rng.uniform(*sizes["block"])
    for turn in BLOCK["at"]:
        feet.append((way + side * math.radians(rng.uniform(*turn)), rng.uniform(*BLOCK["out"]), radius))
        radius *= BLOCK["shrink"]
    # Stretched so that the base and what stands round it fill the bounds' width and depth.
    scale, shift = [], []
    for axis in range(2):
        ends = [(0.0, 1.0)] + [(stone.leaning(at, 0)[axis] * out, radius) for at, out, radius in feet]
        low, high = min(c - r for c, r in ends), max(c + r for c, r in ends)
        scale.append((hi[axis] - lo[axis]) / (high - low))
        shift.append(lo[axis] - low * scale[axis])
    # Everything is drawn round, with the base's lesser radius, and the whole is widened along the other axis at the
    # end: planes stay planes, and every tier keeps the base's proportions however much radius the ones below spent.
    wide = 0 if scale[0] >= scale[1] else 1
    widen = scale[wide] / scale[1 - wide]
    shift[wide] /= widen
    middle = Vector((shift[0], shift[1], lo.z))  # of the base, on the ground
    base = (scale[1 - wide],) * 2

    # The tiers, from the base up.
    shares = [rng.uniform(*span) for span in TOPS[tiers]] + [1.0]
    pieces = []
    centre, radii = middle, base
    for index, share in enumerate(shares):
        last = index == tiers - 1
        top = lo.z + share * height
        tall = top - centre.z
        if index == 0:
            lifts = BASE["lean"]
            loss = tall * math.tan(math.radians(sum(lifts) / 2))
            sides, shoulder, inset, tilt = rng.randint(*BASE["sides"]), BASE["shoulder"], BASE["inset"], BASE["tilt"]
        else:
            loss = min(radii) * rng.uniform(*SLIM[tiers]["narrower"])
            lean = math.degrees(math.atan(loss / tall))
            lifts = (0.85 * lean, 1.15 * lean)
            sides, shoulder, inset, tilt = rng.randint(*TIER["top_sides" if last else "sides"]), TIER["top_shoulder" if last else "shoulder"], TIER["top_inset" if last else "inset"], TIER["tilt"]
        # At the shoulder. The base loses the same from each radius, as its lean asks; a tier above keeps its proportions.
        narrow = (radii[0] - loss, radii[1] - loss) if index == 0 else tuple(r * (1 - loss / min(radii)) for r in radii)
        drop = min(narrow) * rng.uniform(*shoulder)
        pieces.append(piece(rng, sides, centre, radii, lifts, cap(rng, Vector((centre.x, centre.y, top)), tilt), drop, inset))
        if index == 0:
            shoulder_height = tall - drop
        if last:
            break
        # The next stands on this one's cap, inside its chamfers, off the middle toward `way`, and is sunk into it.
        flat = [r - drop * inset[1] for r in narrow]
        room = min(narrow) * rng.uniform(*SLIM[tiers]["ledge"])
        foot = (min(flat) - room) / min(narrow)
        radii = (narrow[0] * foot, narrow[1] * foot)
        off = stone.leaning(way + rng.uniform(-TIER["off_turn"], TIER["off_turn"]), 0) * (room * rng.uniform(*TIER["off"]))
        sink = 0.5 * drop + (max(radii) + off.length) * math.tan(math.radians(tilt[1])) + 0.005 * height
        centre = Vector((centre.x + off.x, centre.y + off.y, top - sink))

    # The buttresses and the blocks, on the ground round the base.
    tall = shoulder_height * rng.uniform(*sizes["tall"])
    for index, (at, out, radius) in enumerate(feet):
        outward = stone.leaning(at, 0)
        centre = middle + Vector((outward.x * out * base[0], outward.y * out * base[1], 0))
        radii = (radius * base[0], radius * base[1])
        if index < ribs:
            tip = (at + math.pi, rng.uniform(*RIB["lean"]))
            over = centre + stone.Z * tall + stone.leaning(tip[0], 0) * (tall * math.tan(math.radians(tip[1])))
            pieces.append(piece(rng, rng.randint(*RIB["sides"]), centre, radii, RIB["taper"], cap(rng, over, RIB["slant"], at), min(radii) * rng.uniform(*RIB["shoulder"]), RIB["inset"], tip))
            tall *= rng.uniform(*sizes["steps"][min(index, len(sizes["steps"]) - 1)][1])
        else:
            low = min(radii) * rng.uniform(*BLOCK["tall"])
            pieces.append(piece(rng, rng.randint(*BLOCK["sides"]), centre, radii, BLOCK["lean"], cap(rng, centre + stone.Z * low, BLOCK["slant"]), low * rng.uniform(*BLOCK["shoulder"]), BLOCK["inset"]))
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
