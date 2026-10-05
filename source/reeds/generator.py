"""Reeds generator: one seed, one bed (source/reeds/brief.md).

Shared by the variants' build scripts (source/reeds_1, _2, _3), which each
call `build_bed(spec)`. Everything is drawn from `random.Random(seed)` in a
fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. The bed: how many stalks, where their feet stand (each new foot is the one
   of a few tries that is furthest from those already placed, inside an oval
   turned by chance), which way and how far the whole bed leans, and how much
   shorter than the tallest a stalk may be. These are what make seeds differ.
2. Mud: a low closed mound under the feet.
3. Stalks: each a thin three-sided tube from the mud to a tip a few millimetres across, nearly upright
   and nearly straight. The tallest few carry a head: a closed sausage of the
   mud's material round the stalk, under its point.
4. Leaves: two or three strips from each stalk, each from its own height and
   side. A leaf leaves the stalk steeply, bends outward and droops toward its
   tip, and its heading turns as it goes, so it does not lie in one upright plane.
5. Fit: the feet are drawn as far apart, along x and along y, as fills the
   bounds, with the stalks, heads and leaves as they are; then the whole bed is
   stretched the little that is left, one stretch along each axis, to the
   spec's bounds exactly. So a stalk stays round and a head stays a sausage.
"""

import math
import random

from mathutils import Matrix, Vector
from plant_parts import Z, Parts, blade, fit, head, mound, parted, stalk, to_object

STALKS_PER_M = (8.75, 15.0)  # the fewest and the most stalks a seed may draw, per metre of the bed's width, and
STALKS = (6, 14)  # the fewest and the most at any width
BED = 0.3  # the feet stand within this share of the bed's width of its middle,
OVAL = (1.0, 1.45)  # in an oval this many times as long as it is wide, turned by chance
TRIES = 10  # a new foot is the furthest from the others of this many tries
MUD = 1.1  # the mud's radius over the feet's
MUD_HEIGHT = 0.035  # metres
MUD_SIDES = 8
FOOT_UP = 0.01  # a stalk's foot is this far above the ground, in the mud
BED_LEAN = (0.0, 3.0)  # degrees the whole bed leans, one way
OWN_LEAN = (0.0, 2.2)  # and each stalk besides, its own way
SHORTEST = (0.6, 0.8)  # the shortest a stalk may be in this bed, over the tallest: drawn once for the bed
HEAD_STALK = (0.82, 1.0)  # a stalk that carries a head is at least this tall, over the tallest
BOW = (0.004, 0.012)  # how far a stalk's middle stands off the straight line, over its length
STALK_ALONG = (0.0, 0.5, 0.8, 1.0)  # where its rings stand; the last is its point
STALK_TAPER = (1.0, 0.8, 0.5)  # its radius at each ring but the last, over that at its foot,
STALK_TIP = 0.003  # and at its tip, metres
STALK_RADIUS = (0.013, 0.016)  # metres, at its foot
HEADS = (0.25, 0.65)  # the share of stalks that carry a head, and
HEAD_COUNT = (2, 8)  # the fewest and the most
HEAD_TOP = 0.93  # a head ends this far up its stalk: the stalk's point stands above it
HEAD_LENGTH = (0.09, 0.13)  # over the bed's height,
HEAD_LIMITS = (0.15, 0.36)  # and the least and the most, metres
HEAD_RADIUS = (0.021, 0.025)  # metres
HEAD_SIDES = 6
HEAD_RINGS = ((0.1, 1.0), (0.9, 1.0))  # nearly a cylinder, with a short point at each end
LEAVES = (2, 2, 3, 3, 3)  # leaves on a stalk, drawn from these
LEAF_FROM = (0.04, 0.64)  # they leave it between these shares of its length,
LEAF_ROUND = 2.4  # each about this many radians round the stalk from the last, give or take
LEAF_LENGTH = (0.36, 0.58)  # a leaf's length over its stalk's
LEAF_WIDTH = (0.034, 0.05)  # its greatest width over its length
LEAF_START = (4.0, 11.0)  # degrees from upright as it leaves the stalk
LEAF_END = (40.0, 125.0)  # and at its tip: past 90 it hangs
LEAF_BEND = (1.6, 2.6)  # how late along itself it bends over: 1 is evenly
LEAF_REACH = 0.22  # no leaf's tip is further out from its foot, level, than this share of the bed's width: one that would be bends over less
LEAF_TURN = (0.6, 1.5)  # radians its heading turns from foot to tip, either way
LEAF_ROLL = 0.4  # and its face rolls about its own length by up to this many radians
LEAF_ALONG = (0.0, 0.45, 0.72, 0.9, 1.0)  # where along its curve its rows stand; the last is its tip
LEAF_WIDE = (0.7, 1.0, 0.85, 0.55)  # its width at each row but the tip, over its greatest
MAX_STRETCH = (0.9, 1.1)  # the last stretch may not change any side by more


def feet(rng, count, radius):
    """Where the stalks stand: each new foot the furthest from the others of a few tries, inside an oval turned by chance."""
    long = rng.uniform(*OVAL)
    turn = Matrix.Rotation(rng.uniform(0, math.pi), 3, "Z")
    found = []
    for _ in range(count):
        tries = []
        for _ in range(TRIES):
            angle, reach = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1))
            tries.append(turn @ Vector((math.cos(angle) * reach * radius * math.sqrt(long), math.sin(angle) * reach * radius / math.sqrt(long), 0)))
        found.append(max(tries, key=lambda at: min(((at - other).length for other in found), default=0.0)))
    return found


def leaf_curve(rng, foot, heading, length, reach):
    """The points along a leaf's middle and the way it lies across itself at each: up the stalk, then out and over, its heading turning as it goes."""
    start, end = math.radians(rng.uniform(*LEAF_START)), math.radians(rng.uniform(*LEAF_END))
    bend, turn, roll = rng.uniform(*LEAF_BEND), rng.uniform(*LEAF_TURN) * rng.choice((-1, 1)), rng.uniform(-LEAF_ROLL, LEAF_ROLL)
    steps = 48
    while True:
        fine, lies = [foot.copy()], []
        for k in range(steps + 1):
            t = k / steps
            tilt, way = start + (end - start) * t**bend, heading + turn * t
            tangent = Vector((math.sin(tilt) * math.cos(way), math.sin(tilt) * math.sin(way), math.cos(tilt)))
            level = Vector((-math.sin(way), math.cos(way), 0))
            lies.append(Matrix.Rotation(roll * t, 3, tangent) @ level)
            if k < steps:
                fine.append(fine[-1] + tangent * length / steps)
        if max(Vector((at.x - foot.x, at.y - foot.y)).length for at in fine) <= reach:
            break
        start, end = start * 0.97, end * 0.9  # it stands closer to its stalk, and bends over less
    return [fine[round(share * steps)] for share in LEAF_ALONG], [lies[round(share * steps)] for share in LEAF_ALONG[:-1]]


def sketch(spec, spread):
    """The bed before the last stretch, its feet standing `spread` (along x, along y) times as far apart as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = min(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    parts = Parts()

    count = rng.randint(*(min(STALKS[1], max(STALKS[0], round(per * wide))) for per in STALKS_PER_M))
    radius = wide * BED
    stand = [Vector((at.x * spread[0], at.y * spread[1], 0)) for at in feet(rng, count, radius)]
    bed_way = rng.uniform(0, 2 * math.pi)
    bed_lean = math.radians(rng.uniform(*BED_LEAN))
    shortest = rng.uniform(*SHORTEST)
    heights = [1.0] + [rng.uniform(shortest, 1.0) for _ in range(count - 1)]
    rng.shuffle(heights)
    # The tallest stalks are the ones that carry heads.
    carrying = min(HEAD_COUNT[1], max(HEAD_COUNT[0], round(count * rng.uniform(*HEADS))))
    headed = set(sorted(range(count), key=lambda k: -heights[k])[:carrying])
    for k in headed:
        heights[k] = max(heights[k], rng.uniform(*HEAD_STALK))

    mound(parts, rng, radius * MUD, MUD_HEIGHT, MUD_SIDES, seams=True)
    for at in parts.verts:  # the mud lies under the feet, wherever they were drawn to
        at.x, at.y = at.x * spread[0], at.y * spread[1]

    for k, at in enumerate(stand):
        own_way, own_lean = rng.uniform(0, 2 * math.pi), math.radians(rng.uniform(*OWN_LEAN))
        up = (Z + Vector((math.cos(bed_way), math.sin(bed_way), 0)) * math.tan(bed_lean) + Vector((math.cos(own_way), math.sin(own_way), 0)) * math.tan(own_lean)).normalized()
        length = tall * heights[k]
        foot = at + Z * FOOT_UP
        bow_way = rng.uniform(0, 2 * math.pi)
        bow = Vector((math.cos(bow_way), math.sin(bow_way), 0)) * length * rng.uniform(*BOW)
        spine = [foot + up * length * share + bow * math.sin(math.pi * share) for share in STALK_ALONG]
        radius_here = rng.uniform(*STALK_RADIUS)
        stalk(parts, spine, [radius_here * part for part in STALK_TAPER] + [STALK_TIP], spin=rng.uniform(0, 2 * math.pi))
        if k in headed:
            long = min(HEAD_LIMITS[1], max(HEAD_LIMITS[0], tall * rng.uniform(*HEAD_LENGTH)))
            top = foot + up * length * HEAD_TOP
            head(parts, top - up * long, top, rng.uniform(*HEAD_RADIUS), HEAD_SIDES, rings=HEAD_RINGS, spin=rng.uniform(0, math.pi))
        leaves = rng.choice(LEAVES)
        heading = rng.uniform(0, 2 * math.pi)
        for n in range(leaves):
            share = LEAF_FROM[0] + (LEAF_FROM[1] - LEAF_FROM[0]) * (n + rng.uniform(0.1, 0.9)) / leaves
            heading += LEAF_ROUND + rng.uniform(-0.5, 0.5)
            leaf_length = length * rng.uniform(*LEAF_LENGTH)
            points, lies = leaf_curve(rng, foot + up * length * share + bow * math.sin(math.pi * share), heading, leaf_length, wide * LEAF_REACH)
            width = leaf_length * rng.uniform(*LEAF_WIDTH)
            blade(parts, points, [width * part for part in LEAF_WIDE], Z, across=lies)
    return parts


def draw(spec):
    """The bed, its feet drawn as far apart as fills the bounds, and fitted."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    spread = [1.0, 1.0]
    for _ in range(8):
        parts = sketch(spec, spread)
        for i in range(2):
            spread[i] *= (hi[i] - lo[i]) / (max(v[i] for v in parts.verts) - min(v[i] for v in parts.verts))
    parts = sketch(spec, spread)
    fit(parts, lo, hi, most=MAX_STRETCH)
    return parted(parts)


def build_bed(spec):
    """Build the spec's one object from its seed. The mud and the heads are of the material that is not the foliage's."""
    return to_object(draw(spec), spec)
