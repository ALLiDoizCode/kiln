"""Blade plant generator: one seed, one rosette (source/blade_plant/brief.md).

Shared by the variants' build scripts (source/blade_plant_1, _2, _3), which
each call `build_plant(spec)`. Everything is drawn from `random.Random(seed)`
in a fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Rootstock: a low closed mound (the rootstock) on the ground at the origin.
2. Blades: two rings of them from the rootstock, all round. The inner ring stands
   and bends over a little; the outer ring lies out and droops. Each blade is
   one open strip along a curve, widest two fifths of the way along, folded
   along its middle and ending in a point.
3. Fit: the blades are drawn as far out as fills the bounds, and the plant is
   then stretched about the origin, each side by what it needs, to the spec's
   bounds exactly: the rootstock stays at the origin.
"""

import math
import random

from mathutils import Vector
from plant_parts import Z, Parts, blade, drawn_to_fit, mound, to_object

ROOTSTOCK_RADIUS = 0.12
ROOTSTOCK_HEIGHT = 0.07
ROOTSTOCK_SIDES = 6
FOOT_RING = 0.045  # blades leave the rootstock this far from its middle
FOOT_STEP = 0.003  # and each a little higher up it than the one before
INNER = (4, 6)  # blades in the inner ring
OUTER_PER_M = 5.5  # blades in the outer ring, per metre of the plant's width
OUTER = (5, 10)
# A blade's curve, as shares of the plant's half width (out) and height (up): where it ends, and
# the point it bends toward on the way.
INNER_TIP = ((0.42, 0.62), (0.8, 1.0))
INNER_BEND = ((0.1, 0.2), (0.7, 0.9))
OUTER_TIP = ((0.85, 1.0), (0.2, 0.45))
OUTER_BEND = ((0.4, 0.55), (0.6, 0.85))
ARCH = 1.0  # how far a blade's curve stands off the straight line from its foot to its tip, over what is drawn
ALONG = (0.0, 0.3, 0.58, 0.82, 1.0)  # where along its curve a blade's rows stand; the last is its tip
WIDE = (0.3, 1.0, 0.85, 0.45)  # its width at each row but the tip, over its greatest
WIDTH = (0.13, 0.17)  # greatest width over the blade's length
FOLD = 0.3  # how far its edges stand above its middle, over its half width
FLOOR = 0.02  # no tip comes nearer the ground than this
MAX_STRETCH = (0.7, 1.4)  # the fit may not change any side by more: blades are of many lengths as it is


def sketch(spec, spread):
    """The plant before the fit, its blades reaching `spread` times as far as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    half, tall = min(hi.x - lo.x, hi.y - lo.y) / 2 * spread, hi.z - lo.z
    parts = Parts()
    mound(parts, rng, ROOTSTOCK_RADIUS, ROOTSTOCK_HEIGHT, ROOTSTOCK_SIDES)

    def grow(azimuth, tip, bend):
        out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
        side = Vector((-out.y, out.x, 0))
        # Each foot a little higher than the last: two blades' corners never share a place, which would be lit as a hard edge.
        foot = out * FOOT_RING + Z * (ROOTSTOCK_HEIGHT * 0.45 + FOOT_STEP * len(parts.piece_out))
        reach, rise = (rng.uniform(*span) for span in tip)
        end = out * half * reach + side * half * rng.uniform(-0.12, 0.12) + Z * max(FLOOR, tall * rise)
        reach, rise = (rng.uniform(*span) for span in bend)
        toward = out * half * reach + Z * tall * rise * 1.25
        toward = (foot + end) / 2 + (toward - (foot + end) / 2) * ARCH
        spine = [foot * (1 - t) ** 2 + toward * 2 * t * (1 - t) + end * t * t for t in ALONG]
        length = sum((b - a).length for a, b in zip(spine, spine[1:]))
        width = length * rng.uniform(*WIDTH)
        # Its upper face looks up and back toward the middle of the plant.
        blade(parts, spine, [width * share for share in WIDE], (Z - out * 0.5).normalized(), fold=FOLD)

    turn = rng.uniform(0, 2 * math.pi)
    count = rng.randint(*INNER)
    for k in range(count):
        grow(turn + 2 * math.pi * (k + rng.uniform(-0.25, 0.25)) / count, INNER_TIP, INNER_BEND)
    turn = rng.uniform(0, 2 * math.pi)
    count = min(OUTER[1], max(OUTER[0], round(OUTER_PER_M * (hi.x - lo.x))))
    for k in range(count):
        grow(turn + 2 * math.pi * (k + rng.uniform(-0.25, 0.25)) / count, OUTER_TIP, OUTER_BEND)

    return parts


def draw(spec):
    """The plant, drawn as wide as fills the bounds, and fitted."""
    return drawn_to_fit(lambda spread: sketch(spec, spread), spec["bounds_m"]["min"], spec["bounds_m"]["max"], about_origin=True, most=MAX_STRETCH)


def build_plant(spec):
    """Build the spec's one object from its seed. The rootstock is the material that is not the foliage's."""
    return to_object(draw(spec), spec)
