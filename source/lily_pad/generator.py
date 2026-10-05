"""Lily pad generator: one seed, one group (source/lily_pad/brief.md).

Shared by the variants' build scripts (source/lily_pad_1, _2, _3), which each
call `build_group(spec)`. Everything is drawn from `random.Random(seed)` in a
fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Sizes: the widest disc is a share of the group's longer side, the narrowest
   hand-sized, and the others between them at uneven steps.
2. Places: the widest first; each next disc beside one already placed, chosen
   by chance, a gap of its own away, wherever it overlaps nothing. So a group
   straggles: it is not packed round its middle and has no row and no ring.
   The whole is turned to lie along the bounds, and a draw that would not fill
   them without being stretched out of shape is drawn again.
3. Discs: each a level floor at one height with a raised rim and a notch that
   opens a way of its own.
4. Blooms: one or two, where there is open water nearest the middle of the
   group: a low ring of open petals round a raised, pointed middle, leaning a little.
5. Fit: the group is stretched the little that is left, one stretch along each
   level axis, to the spec's bounds exactly. The taller bloom is as tall as the bounds.
"""

import math
import random

from mathutils import Vector
from plant_parts import Parts, bloom, disc, fit, to_object

WIDEST = (0.40, 0.45)  # the widest disc's width over the group's longer side
HAND = (0.10, 0.16)  # the narrowest disc's width, metres
STEP = 1.5  # about this many times from one size to the next: it sets how many discs there are
STEPS = (1.15, 1.85)  # and no step is less or more than these
GAP = (0.03, 0.4)  # clear water between a disc and the one it is placed beside, over the smaller one's radius
CLEAR = 0.1  # and between any two, over the smaller one's radius
STRAY = 0.25  # one disc in this many is placed twice as far out
REACH = 1.1  # a disc's outline may stand this far out, over its radius: its oval and its unevenness
FILL = (0.9, 1.1)  # a draw is kept when it fills the bounds' longer side within these,
ASPECT = 0.08  # is this near the bounds' shape,
SCATTER = 0.36  # and its discs' middles spread this far across over along, and differ this much in their distance from the group's middle, over the mean: no row, no ring
FLOAT = 0.012  # the floors lie this far above the water, metres
DIP = 0.06  # a disc's middle sinks this share of its radius under its floor, and no lower than the water
RIM = (0.1, 0.15)  # the rim's width over the radius
RISE = (0.07, 0.1)  # how far the rim's edge stands above the floor, over the radius
NOTCH = (0.3, 0.6)  # the notch's width, radians
SIDES = (6.0, 12.0, 0.7)  # a disc has the first plus the second times the root of (its radius over the third) sides,
SIDES_LIMITS = (8, 16)  # and no fewer or more than these
BLOOM = (0.06, 0.075, 0.13)  # a bloom's radius: over the group's longer side, and the least and the most, metres
SECOND = (0.66, 0.8)  # the second bloom's size over the first's
BLOOM_TRIES = 400  # places tried for a bloom
BLOOM_CLEAR = 0.8  # a bloom's middle is at least this share of its radius clear of every disc's reach
LEAN = (2.0, 12.0)  # degrees a bloom leans from upright
PETALS = 5
# A bloom's rings (tools/plant_parts.py `bloom`): the open petals, and the shorter ones that stand round its pointed middle.
# Convex from every petal's edge inward: lit smooth, a cup's inside would be lit from behind.
RINGS = ((1.0, 0.5, 0.3, 0.3, 0.0), (0.55, 0.28, 0.7, 0.6, 0.0))
MAX_STRETCH = (0.82, 1.2)  # the last stretch may not change any side by more


def sizes(rng, widest, counts):
    """The discs' radii, widest first: uneven steps down to a hand's width. `counts` are the fewest and the most discs the spec allows."""
    hand = rng.uniform(*HAND)
    count = min(counts[1], max(counts[0], round(math.log(widest / hand) / math.log(STEP)) + 1 + rng.randint(0, 1)))
    while True:
        cuts = sorted(rng.uniform(0, 1) for _ in range(count - 2))
        widths = [widest * (hand / widest) ** share for share in [0.0] + cuts + [1.0]]
        if all(STEPS[0] <= a / b <= STEPS[1] for a, b in zip(widths, widths[1:])):
            return [width / 2 for width in widths]


def places(rng, radii):
    """Where the discs lie, as (x, y, radius): each beside one already placed, clear of all."""
    placed = [(0.0, 0.0, radii[0])]
    for radius in radii[1:]:
        while True:
            x, y, beside = rng.choice(placed)
            angle = rng.uniform(0, 2 * math.pi)
            gap = rng.uniform(*GAP) * min(radius, beside) * (2.0 if rng.random() < STRAY else 1.0)
            reach = (beside + radius) * REACH + gap
            at = (x + math.cos(angle) * reach, y + math.sin(angle) * reach)
            if all(math.dist(at, (px, py)) >= (pr + radius) * REACH + CLEAR * min(pr, radius) for px, py, pr in placed):
                placed.append((at[0], at[1], radius))
                break
    return placed


def turned(placed, wide, deep):
    """The places turned to lie along the bounds, about the middle of what they cover; and (how much of the longer side they fill, how far their shape is from the bounds')."""
    best = None
    for step in range(72):
        angle = math.pi * step / 36
        c, s = math.cos(angle), math.sin(angle)
        spun = [(x * c - y * s, x * s + y * c, r) for x, y, r in placed]
        lo = [min(p[i] - p[2] for p in spun) for i in range(2)]
        hi = [max(p[i] + p[2] for p in spun) for i in range(2)]
        off = abs(math.log((hi[0] - lo[0]) / (hi[1] - lo[1]) / (wide / deep)))
        if best is None or off < best[0]:
            best = (off, [(x - (lo[0] + hi[0]) / 2, y - (lo[1] + hi[1]) / 2, r) for x, y, r in spun], (hi[0] - lo[0]) / wide)
    return best[1], best[2], best[0]


def scattered(placed):
    """The lesser of: how far the discs' middles spread across the group over along it, and how much their distances from the group's middle differ, over the mean distance."""
    n = len(placed)
    mx, my = sum(p[0] for p in placed) / n, sum(p[1] for p in placed) / n
    xx, yy, xy = (sum((p[i] - a) * (p[j] - b) for p in placed) / n for i, a, j, b in ((0, mx, 0, mx), (1, my, 1, my), (0, mx, 1, my)))
    root = math.sqrt(max(((xx - yy) / 2) ** 2 + xy * xy, 0.0))
    across = math.sqrt(max((xx + yy) / 2 - root, 0.0) / max((xx + yy) / 2 + root, 1e-12))
    out = [math.dist((p[0], p[1]), (mx, my)) for p in placed]
    mean = sum(out) / n
    return min(across, math.sqrt(sum((d - mean) ** 2 for d in out) / n) / max(mean, 1e-12))


def sketch(spec):
    """The group before the last stretch."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, deep, tall = hi.x - lo.x, hi.y - lo.y, hi.z - lo.z
    while True:
        placed, fill, off = turned(places(rng, sizes(rng, max(wide, deep) * rng.uniform(*WIDEST), spec["discs"]["count"])), wide, deep)
        if FILL[0] <= fill <= FILL[1] and off <= ASPECT and scattered(placed) >= SCATTER:
            break

    parts = Parts()
    for x, y, radius in placed:
        sides = min(SIDES_LIMITS[1], max(SIDES_LIMITS[0], round(SIDES[0] + SIDES[1] * math.sqrt(radius / SIDES[2]))))
        disc(parts, rng, (x, y), radius, sides, rng.uniform(0, 2 * math.pi), rng.uniform(*NOTCH), FLOAT, rng.uniform(*RIM), radius * rng.uniform(*RISE), min(FLOAT, DIP * radius))

    # Blooms: on open water, as near the middle of the discs as there is room.
    middle = (sum(x * r * r for x, y, r in placed) / sum(r * r for x, y, r in placed), sum(y * r * r for x, y, r in placed) / sum(r * r for x, y, r in placed))
    size = min(BLOOM[2], max(BLOOM[1], BLOOM[0] * max(wide, deep)))
    blooms = []
    for radius in [size] + [size * rng.uniform(*SECOND)] * (spec["blooms"]["count"][0] - 1):
        tries = [(rng.uniform(lo.x + radius, hi.x - radius), rng.uniform(lo.y + radius, hi.y - radius)) for _ in range(BLOOM_TRIES)]
        free = [at for at in tries if all(math.dist(at, (x, y)) >= r * REACH + radius * BLOOM_CLEAR for x, y, r in placed) and all(math.dist(at, (x, y)) >= (r + radius) * 2.5 for x, y, r in blooms)]
        if not free:
            raise RuntimeError(f"seed {spec['seed']}: no open water for a bloom of radius {radius:.3f} m among the discs")
        # One of the three nearest the middle, by chance: between the discs, not out past them.
        at = rng.choice(sorted(free, key=lambda at: math.dist(at, middle))[:3])
        blooms.append((at[0], at[1], radius))
        lean, way = math.radians(rng.uniform(*LEAN)), rng.uniform(0, 2 * math.pi)
        up = Vector((math.sin(lean) * math.cos(way), math.sin(lean) * math.sin(way), math.cos(lean)))
        height = (tall - FLOAT) * radius / size
        base = Vector((at[0], at[1], FLOAT))
        bloom(parts, base, base + up * height, [(tips * radius, notches * radius, tips_up, notches_up, turn) for tips, notches, tips_up, notches_up, turn in RINGS], PETALS, spin=rng.uniform(0, math.pi))
    # The taller bloom is as tall as the bounds: everything above the floors is stretched the little its lean cost it.
    top = max(v.z for v in parts.verts)
    for v in parts.verts:
        if v.z > FLOAT:
            v.z = FLOAT + (v.z - FLOAT) * (tall - FLOAT) / (top - FLOAT)
    return parts


def draw(spec):
    """The group, fitted to the spec's bounds."""
    parts = sketch(spec)
    fit(parts, spec["bounds_m"]["min"], spec["bounds_m"]["max"], most=MAX_STRETCH)
    return parts


def build_group(spec):
    """Build the spec's one object from its seed. The blooms are of the material that is not the foliage's."""
    return to_object(draw(spec), spec)
