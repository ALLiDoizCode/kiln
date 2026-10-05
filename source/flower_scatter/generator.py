"""Flower scatter generator: one seed, one scatter (source/flower_scatter/brief.md).

Shared by the variants' build scripts (source/flower_scatter_1, _2, _3), which
each call `build_scatter(spec)`. Everything is drawn from `random.Random(seed)`
in a fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Places: each flower's foot is the one of a few tries that is furthest from
   those already placed, inside an oval turned by chance: apart, and in no row.
2. Flowers: each a thin stem from the ground, of a height of its own, leaning a
   way of its own and bowed a little, with a bloom on its end: a closed
   five-pointed star that looks along the stem and a little further over.
3. Leaves: two to four leaf pieces at the foot of each stem, pointing out and up.
4. Fit: the feet are drawn as far apart, along x and along y, as fills the
   bounds, with the flowers as they are; then the scatter is stretched the
   little that is left, one stretch along each axis, to the spec's bounds exactly.
"""

import math
import random

from mathutils import Matrix, Vector
from plant_parts import Z, Parts, blade, bloom, fit, leaf_piece, to_object

BED = 0.36  # the feet stand within this share of the scatter's width of its middle,
OVAL = (1.0, 1.5)  # in an oval this many times as long as it is wide, turned by chance
TRIES = 4  # a new foot is the furthest from the others of this many tries
HEIGHT = (0.42, 0.95)  # a flower's height over the scatter's; the first is the tallest, at 1
LEAN = (5.0, 24.0)  # degrees a stem leans from upright, its own way:
WAY = 0.9  # within this many radians of its share of the compass
APART = 0.2  # no two feet are nearer than this share of the scatter's width, before they are drawn apart to fill the bounds
BOW = (0.03, 0.09)  # how far a stem's middle stands off the straight line, over its length
STEM_WIDTH = 0.005  # metres
BLOOM = (0.025, 0.031)  # a bloom's radius, metres
BLOOM_DEEP = 0.5  # its depth from base to top over its radius
BLOOM_TIP = 0.35  # how much further over than its stem a bloom looks, over the stem's lean
PETALS = 5
RINGS = ((1.0, 0.42, 0.5, 0.5, 0.0),)  # tools/plant_parts.py `bloom`: one flat star
LEAVES = (2, 2, 3, 3, 4)  # leaves at a stem's foot, drawn from these
LEAF = (0.06, 0.1)  # a leaf's length, metres,
LEAF_MOST = 0.42  # and no more than this share of the lowest flower's height
LEAF_WIDTH = (0.42, 0.56)  # its width over its length
LEAF_UP = (15.0, 40.0)  # degrees it points above level
MAX_STRETCH = (0.9, 1.12)  # the last stretch may not change any side by more


def sketch(spec, spread):
    """The scatter before the last stretch, its feet standing `spread` (along x, along y) times as far apart as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = min(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    count = rng.randint(*spec["blooms"]["count"])
    long, turn = rng.uniform(*OVAL), Matrix.Rotation(rng.uniform(0, math.pi), 3, "Z")
    feet = []
    for _ in range(count):
        tries = []
        for _ in range(TRIES):
            angle, reach = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * wide * BED
            tries.append(turn @ Vector((math.cos(angle) * reach * math.sqrt(long), math.sin(angle) * reach / math.sqrt(long), 0)))
        best = max(tries, key=lambda at: min(((at - other).length for other in feet), default=0.0))
        while feet and min((best - other).length for other in feet) < wide * APART * min(1.0, 4.5 / count):
            angle, reach = rng.uniform(0, 2 * math.pi), math.sqrt(rng.uniform(0, 1)) * wide * BED
            best = turn @ Vector((math.cos(angle) * reach * math.sqrt(long), math.sin(angle) * reach / math.sqrt(long), 0))
        feet.append(best)
    heights = [1.0] + [rng.uniform(*HEIGHT) for _ in range(count - 1)]
    rng.shuffle(heights)

    parts = Parts()
    first_way = rng.uniform(0, 2 * math.pi)
    for k, (at, share) in enumerate(zip(feet, heights)):
        foot = Vector((at.x * spread[0], at.y * spread[1], 0.0))
        # Each leans its own way: round the compass from the first, give or take, so that no scatter leans all one way.
        way, lean = first_way + 2 * math.pi * k / count + rng.uniform(-WAY, WAY), math.radians(rng.uniform(*LEAN))
        out = Vector((math.cos(way), math.sin(way), 0))
        up = out * math.sin(lean) + Z * math.cos(lean)
        radius = rng.uniform(*BLOOM)
        # The bloom's top is the flower's height: the stem ends at its base.
        looks = (up + out * math.sin(lean) * BLOOM_TIP).normalized()
        deep = radius * BLOOM_DEEP
        length = (tall * share - deep * looks.z) / up.z
        bow = (out * math.cos(lean) - Z * math.sin(lean)) * -length * rng.uniform(*BOW)
        end = foot + up * length
        blade(parts, [foot, (foot + end) / 2 + bow, end + looks * deep * 0.5], [STEM_WIDTH, STEM_WIDTH], Matrix.Rotation(rng.uniform(-math.pi, math.pi), 3, "Z") @ Vector((1, 0, 0)))
        bloom(parts, end, end + looks * deep, [(tips * radius, notches * radius, tips_up, notches_up, turned) for tips, notches, tips_up, notches_up, turned in RINGS], PETALS, spin=rng.uniform(0, math.pi))
        heading = rng.uniform(0, 2 * math.pi)
        # As many leaves as the budget has left for it, when every flower still to come has its stem, its bloom and two leaves.
        spare = spec["max_triangles"] - parts.triangles() - (count - k - 1) * (parts.triangles() // (k + 1) if k else 40)
        leaves = max(2, min(rng.choice(LEAVES), spare // 4))
        for n in range(leaves):
            heading += 2 * math.pi / leaves + rng.uniform(-0.6, 0.6)
            rise = math.radians(rng.uniform(*LEAF_UP))
            axis = Vector((math.cos(heading) * math.cos(rise), math.sin(heading) * math.cos(rise), math.sin(rise)))
            long_leaf = min(rng.uniform(*LEAF), tall * min(heights) * LEAF_MOST / math.sin(math.radians(LEAF_UP[1])))
            leaf_piece(parts, rng, foot + Vector((math.cos(heading), math.sin(heading), 0)) * 0.006 + Z * 0.004, (Z - axis * axis.z).normalized(), axis, long_leaf, long_leaf * rng.uniform(*LEAF_WIDTH), 0.0, 20.0, 0.3, floor=0.002)
    # A stem's foot is a strip's end, and one corner of it dips a hair under the ground: the scatter is stood on its lowest corner.
    lowest = min(v.z for v in parts.verts)
    for v in parts.verts:
        v.z -= lowest
    return parts


def draw(spec):
    """The scatter, its feet drawn as far apart as fills the bounds, and fitted."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    spread = [1.0, 1.0]
    for _ in range(8):
        parts = sketch(spec, spread)
        for i in range(2):
            spread[i] *= (hi[i] - lo[i]) / (max(v[i] for v in parts.verts) - min(v[i] for v in parts.verts))
    parts = sketch(spec, spread)
    fit(parts, lo, hi, most=MAX_STRETCH)
    return parts


def build_scatter(spec):
    """Build the spec's one object from its seed. The blooms are of the material that is not the foliage's."""
    return to_object(draw(spec), spec)
