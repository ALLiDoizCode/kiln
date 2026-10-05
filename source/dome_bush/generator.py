"""Dome bush generator: one seed, one bush (source/dome_bush/brief.md).

Shared by the variants' build scripts (source/dome_bush_1, _2, _3), which each
call `build_bush(spec)`. Everything is drawn from `random.Random(seed)` in a
fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Lobes: two or three overlapping rounded masses standing on the ground, the
   main one in the middle and tallest, the others smaller, lower and to its sides.
2. Cores: a closed dome inside every lobe, in the leaf material.
3. Leaves: on each lobe a shell of flat pointed pieces lying like shingles,
   pointing down its surface and lifted outward, left out where another lobe
   buries them; and a skirt round the foot of the dome, pointing out, nearly level.
   A piece that would dip into the ground is lifted to stand on it.
4. Stems: one from the ground beside the origin into each lobe, and one to three more,
   each kept clear of the others.
5. Fit: the lobes are drawn as wide as fills the bounds, and the bush is then
   stretched, one stretch per axis, to the spec's bounds exactly.
"""

import math
import random

from mathutils import Quaternion, Vector
from plant_parts import Z, Lobe, Parts, core, drawn_to_fit, leaf_piece, stem, to_object

LOBE_COUNTS = ((2, 0.4), (3, 0.6))
MAIN_RADIUS = (0.6, 0.68)  # the main lobe's radius, over half the bush's width
SIDE_RADIUS = (0.6, 0.74)  # a side lobe's, over the main lobe's
SIDE_OUT = (0.62, 0.8)  # a side lobe's middle from the main lobe's, over the main lobe's radius
SIDE_TALL = (0.6, 0.8)  # a side lobe's height, over the bush's
MIDDLE = 0.4  # a lobe's middle stands this share of its height above the ground
LOBE_OPEN = -0.7  # the shell of pieces stops here (unit sphere height); the skirt stands below
LOBE_BURIED = 0.92  # a piece is left out when its place is this deep inside another lobe
CORE = 0.7  # the core's size over its lobe's

LEAF_SPACING = 0.155  # between neighbouring pieces on a lobe's surface, on a bush 1.5 m wide
LEAF_LENGTH = (0.29, 0.41)  # on a bush 1.5 m wide
LEAF_GROWS = 0.4  # a bush twice as wide has leaves 2 ** this times as long, and as far apart
LEAF_WIDTH = (0.46, 0.54)  # over the length
LEAF_LIFT = (14.0, 40.0)  # degrees a piece is raised off the surface
LEAF_YAW = 35.0  # degrees it may swing either side of straight down the surface
LEAF_ROLL = 20.0  # and tip about its own length
LEAF_FOOT = 0.75  # how much of a piece's length lies behind the point where it crosses the lobe's surface
LEAF_ROUND = 0.4  # share of a piece's normal taken from the direction out of its lobe
SKIRT_SPACING = 0.2  # between neighbouring pieces round the foot
SKIRT_DROOP = (-8.0, 22.0)  # degrees below level
SKIRT_FOOT = 0.45
FLOOR = 0.012  # no piece comes nearer the ground than this

STEM_SIDES = 4
STEM_RADIUS = (0.03, 0.04)  # at the ground
STEM_TIP = 0.012
STEM_FEET = 0.13  # the stems' feet stand on a ring of this radius about the origin
EXTRA_STEMS = (1, 3)
STEM_RINGS = (0.0, 0.3, 0.65, 1.0)  # where along a stem its rings stand
STEM_CLEAR = 0.1  # between the middles of two stems, everywhere along them
STEM_TRIES = 30


def sketch(spec, spread):
    """The bush before the fit, its lobes `spread` times as wide as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    half, tall = min(hi.x - lo.x, hi.y - lo.y) / 2 * spread, hi.z - lo.z
    parts = Parts()
    # A larger bush has larger leaves, though not in proportion: the same plant, older.
    grown = (min(hi.x - lo.x, hi.y - lo.y) / 1.5) ** LEAF_GROWS

    def lobe(centre, radius, height):
        # Wider than it is tall, and flatter below its middle than above.
        return Lobe(Vector((centre.x, centre.y, MIDDLE * height)), radius, (1 - MIDDLE) * height, MIDDLE * height * 0.95)

    count = rng.choices([n for n, _ in LOBE_COUNTS], [w for _, w in LOBE_COUNTS])[0]
    main_radius = half * rng.uniform(*MAIN_RADIUS)
    lobes = [lobe(Vector((0, 0, 0)), main_radius, tall * 0.9)]
    turn = rng.uniform(0, 2 * math.pi)
    for k in range(count - 1):
        azimuth = turn + k * rng.uniform(1.9, 2.6)
        out = main_radius * rng.uniform(*SIDE_OUT)
        # The second side lobe is the smallest: three sizes in a bush of three.
        radius = main_radius * rng.uniform(*SIDE_RADIUS) * (0.85 if k else 1.0)
        lobes.append(lobe(Vector((math.cos(azimuth) * out, math.sin(azimuth) * out, 0)), radius, tall * rng.uniform(*SIDE_TALL)))
    for each in lobes:
        core(parts, rng, each, CORE)

    golden = math.pi * (3 - math.sqrt(5))
    for each in lobes:
        others = [other for other in lobes if other is not each]

        def buried(point):
            return any(other.depth(point) < LOBE_BURIED for other in others)

        def place(point, normal, axis, foot):
            length = rng.uniform(*LEAF_LENGTH) * grown
            leaf_piece(parts, rng, point, normal, axis, length, length * rng.uniform(*LEAF_WIDTH), foot, LEAF_ROLL, LEAF_ROUND, floor=FLOOR)

        # The shell: the upper half and the part of the squashed lower half kept.
        area = 2 * math.pi * each.radius * (each.radius + each.up) / 2 * (1 - 0.5 * LOBE_OPEN)
        total = round(area / (LEAF_SPACING * grown) ** 2 * 2 / (1 - LOBE_OPEN))
        spin = rng.uniform(0, 2 * math.pi)
        for k in range(total):
            height = 1 - (2 * k + 1) / total
            if height < LOBE_OPEN:
                break
            ring = math.sqrt(1 - height * height)
            azimuth = spin + golden * k + rng.uniform(-0.12, 0.12)
            unit = Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height + rng.uniform(-0.04, 0.04))).normalized()
            point, normal = each.surface(unit)
            yaw, lift = rng.uniform(-LEAF_YAW, LEAF_YAW), rng.uniform(*LEAF_LIFT)
            down = -Z - normal * normal.dot(-Z)
            if down.length < 0.25:
                # On the crown of a lobe nothing is downhill: point any way round.
                down = Quaternion(normal, rng.uniform(0, 2 * math.pi)) @ normal.orthogonal().normalized()
            down = Quaternion(normal, math.radians(yaw)) @ down.normalized()
            axis = (down * math.cos(math.radians(lift)) + normal * math.sin(math.radians(lift))).normalized()
            if not buried(point):
                place(point, normal, axis, LEAF_FOOT)
        # The skirt: round the foot, pointing out and a little down, standing on the ground.
        count = max(5, round(2 * math.pi * each.radius / (SKIRT_SPACING * grown)))
        spin = rng.uniform(0, 2 * math.pi)
        for k in range(count):
            azimuth = spin + 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / count
            height = rng.uniform(-0.9, LOBE_OPEN + 0.1)
            ring = math.sqrt(1 - height * height)
            point, normal = each.surface(Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height)))
            swing = azimuth + rng.uniform(-0.4, 0.4)
            droop = math.radians(rng.uniform(*SKIRT_DROOP))
            out = Vector((math.cos(swing), math.sin(swing), 0))
            if not buried(point):
                place(point, (normal + out * 0.5 + Z * 0.6).normalized(), out * math.cos(droop) - Z * math.sin(droop), SKIRT_FOOT)

    # Stems: from a ring of feet at the origin, bowing out, into the lobes. One to each lobe, then
    # the extra ones, each drawn again until it keeps clear of the stems already there.
    def path(azimuth, end):
        foot = Vector((math.cos(azimuth), math.sin(azimuth), 0)) * STEM_FEET * rng.uniform(0.8, 1.3)
        bow = Vector((end.x, end.y, 0)) * 0.25 + foot
        return [foot + (bow - foot) * t * 2 * (1 - t) + (end - foot) * t * t + Z * end.z * (t - t * t) for t in STEM_RINGS]

    def clear(points, others):
        fine = [a + (b - a) * (i / 4) for a, b in zip(points, points[1:]) for i in range(5)]
        return all((p - q).length > STEM_CLEAR for other in others for p in fine for q in [a + (b - a) * (i / 4) for a, b in zip(other, other[1:]) for i in range(5)])

    stems = []
    wanted = [(each, True) for each in lobes] + [(rng.choice(lobes), False) for _ in range(rng.randint(*EXTRA_STEMS))]
    for each, middle in wanted:
        for _ in range(STEM_TRIES):
            azimuth = rng.uniform(0, 2 * math.pi)
            end = each.centre + Vector((0, 0, each.up * 0.2)) if middle else each.centre + Vector((math.cos(azimuth), math.sin(azimuth), 0)) * each.radius * 0.45
            toward = math.atan2(end.y, end.x) if Vector((end.x, end.y)).length > STEM_FEET else azimuth
            points = path(toward + rng.uniform(-0.5, 0.5), end)
            if clear(points, stems):
                stems.append(points)
                break
    if len(stems) < len(lobes):
        raise RuntimeError(f"bush seed {spec['seed']}: only {len(stems)} stems keep clear of each other; every one of its {len(lobes)} lobes needs one")
    for points in stems:
        thick = rng.uniform(*STEM_RADIUS)
        stem(parts, points, [thick + (STEM_TIP - thick) * t for t in STEM_RINGS], STEM_SIDES, spin=rng.uniform(0, 1))

    return parts


def draw(spec):
    """The bush, drawn as wide as fills the bounds, and fitted."""
    return drawn_to_fit(lambda spread: sketch(spec, spread), spec["bounds_m"]["min"], spec["bounds_m"]["max"])


def build_bush(spec):
    """Build the spec's one object from its seed. The stem is the material that is not the foliage's."""
    return to_object(draw(spec), spec)
