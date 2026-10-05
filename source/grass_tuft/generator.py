"""Grass tuft generator: one seed, one tuft (source/grass_tuft/brief.md).

Shared by the variants' build scripts (source/grass_tuft_1, _2, _3), which
each call `build_tuft(spec)`. Everything is drawn from `random.Random(seed)`
in a fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Rootstock: a low closed mound on the ground at the origin.
2. Blades: thin strips from the rootstock, all round. Each leaves it at its own
   place, on a spiral, so no two share a foot. The ones from the middle are the
   tallest and stand nearly upright; the further out a blade's foot, the
   shorter it is and the more it leans out. Each curves a little, outward, and
   ends in a point.
3. Fit: the blades are drawn as far out as fills the bounds, and the tuft is
   then stretched about the origin, each side by what it needs, to the spec's
   bounds exactly: the rootstock stays at the origin.
"""

import math
import random

from mathutils import Vector
from plant_parts import Z, Parts, blade, drawn_to_fit, mound

ROOTSTOCK_RADIUS = 0.11  # over the tuft's width
ROOTSTOCK_HEIGHT = 0.3  # over its own radius
ROOTSTOCK_SIDES = 6
FEET = 0.65  # blades leave the rootstock within this share of its radius
BLADES_PER_M = 26  # blades per metre of the tuft's width, and
BLADES = (16, 30)  # the least and the most
INNER_LEAN = (3.0, 12.0)  # degrees from upright, for a blade from the middle
OUTER_LEAN = (38.0, 56.0)  # and for one from the rim
OUTER_SHORT = 0.6  # a blade from the rim is this long, over one from the middle
LENGTH = (0.85, 1.0)  # a blade's length, over what its place gives
CURVE = (0.1, 0.22)  # how far its middle is pushed out and down off the straight line, over its length
ALONG = (0.0, 0.45, 0.8, 1.0)  # where along its curve a blade's rows stand; the last is its tip
WIDE = (0.8, 1.0, 0.6)  # its width at each row but the tip, over its greatest
WIDTH = (0.05, 0.075)  # greatest width over the blade's length
MAX_STRETCH = (0.7, 1.4)  # the fit may not change any side by more


def sketch(spec, spread):
    """The tuft before the fit, its blades leaning `spread` times as far out as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = min(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    parts = Parts()
    radius = wide * ROOTSTOCK_RADIUS
    mound(parts, rng, radius, radius * ROOTSTOCK_HEIGHT, ROOTSTOCK_SIDES)

    count = min(BLADES[1], max(BLADES[0], round(BLADES_PER_M * wide)))
    golden = math.pi * (3 - math.sqrt(5))
    turn = rng.uniform(0, 2 * math.pi)
    for k in range(count):
        share = math.sqrt((k + 0.5) / count)  # 0 at the middle of the tuft, 1 at its rim
        azimuth = turn + golden * k + rng.uniform(-0.2, 0.2)
        out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
        foot = out * radius * FEET * share + Z * radius * ROOTSTOCK_HEIGHT * 0.5
        low, high = (a + (b - a) * share for a, b in zip(INNER_LEAN, OUTER_LEAN))
        lean = math.radians(min(62.0, rng.uniform(low, high) * spread))
        length = tall / math.cos(math.radians(INNER_LEAN[0])) * (1 - (1 - OUTER_SHORT) * share) * rng.uniform(*LENGTH)
        way = out * math.sin(lean) + Z * math.cos(lean)
        end = foot + way * length
        # Curved outward: the middle is pushed up and in, so the tip hangs out past it.
        bow = (Z * math.sin(lean) - out * math.cos(lean)) * -1
        toward = (foot + end) / 2 - bow * length * rng.uniform(*CURVE)
        spine = [foot * (1 - t) ** 2 + toward * 2 * t * (1 - t) + end * t * t for t in ALONG]
        width = length * rng.uniform(*WIDTH)
        blade(parts, spine, [width * part for part in WIDE], (Z * 0.3 - out).normalized())
    return parts


def draw(spec):
    """The tuft, drawn as wide as fills the bounds, and fitted."""
    return drawn_to_fit(lambda spread: sketch(spec, spread), spec["bounds_m"]["min"], spec["bounds_m"]["max"], about_origin=True, most=MAX_STRETCH)


def build_tuft(spec):
    """Build the spec's one object from its seed. The rootstock is the material that is not the foliage's."""
    from plant_parts import to_object

    return to_object(draw(spec), spec)
