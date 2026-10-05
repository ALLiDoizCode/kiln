"""Leaf mat generator: one seed, one mat (source/leaf_mat/brief.md).

Shared by the variants' build scripts (source/leaf_mat_1, _2, _3), which each
call `build_mat(spec)`. Everything is drawn from `random.Random(seed)` in a
fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Runners: four to six creep out from the middle, at uneven steps round the
   compass and of uneven reach, each in two or more straight lengths with a
   turn between them, and here and there a side length at a turn; a length is
   a thin closed spindle on the ground.
2. Leaves: along every length in pairs, one either side, each starting at the
   runner and pointing away from it and toward its end, smaller toward the
   end, with one at the end pointing on; here and there one of a pair is
   missing. So the mat is dense round the middle, where its runners start
   close together, and ragged where each ends alone.
3. Fit: the runners are drawn as long, along x and along y, as fills the
   bounds, with the leaves as they are; then the mat is stretched the little
   that is left, one stretch along each axis, to the spec's bounds exactly.
"""

import math
import random

from mathutils import Matrix, Vector
from plant_parts import Z, Parts, fit, head, leaf_piece, parted, to_object

RUNNERS = (4, 5)
STEP = (0.55, 1.45)  # the turn from one runner to the next, over an even share of the compass
REACH = (0.38, 0.5)  # a runner reaches this far along itself, over the mat's wider side,
SHORT = (0.7, 1.0)  # times its own share of that: the first runner's is 1,
LENGTH = (0.14, 0.22)  # in lengths each this long, metres, and no fewer than two;
LENGTH_AT = 0.7  # longer in a mat wider than this, metres, by the root of how much wider: a large mat spends its triangles on leaves, not on joints,
TURN = 0.6  # and turned up to this many radians from the length before
FILL = 1.1  # side lengths are added, at corners chosen by chance, until the runners and the leaves they will carry come to this share of the triangle budget
CROWD = 0.6  # a side length ends no nearer another corner than this many leaf lengths
BRANCH_TURN = (0.7, 1.2)  # a side length leaves a runner at a turn, this many radians off its way, to either side;
GAP = 0.012  # a length starts this far on from the end of the one before it, metres,
CLEAR = 0.03  # and no side length comes nearer another length,
NEAR = 0.02  # or nearer the two it leaves: no two touch, so there is no inside corner between them to shade
START = 0.03  # a runner starts this far from the middle, metres: their ends stand in a ring there and do not touch
RUNNER_RADIUS = 0.007  # metres
RUNNER_MOST = 0.35  # no length is longer, metres: a longer one is painted too coarsely for the light along its edges to show
RUNNER_SIDES = 3
RUNNER_RINGS = ((0.06, 1.0), (0.94, 1.0))
LEAF_GROWS = (0.42, 0.8, 1.07)  # a leaf is longer in a larger mat: by the root of (the footprint over the first, m2), no less and no more than these
LEAF = (0.098, 0.12)  # a leaf's length, metres,
TAPER = 0.9  # times this at the end of a runner: the leaves grow smaller toward it
LEAF_WIDTH = (0.52, 0.62)  # its width over its length
PITCH = (0.5, 0.7)  # from one pair to the next along a runner, over a leaf's length
AWAY = (48.0, 78.0)  # degrees a leaf points off its runner's way, toward the runner's end
MISSING = 0.1  # the share of leaves that are not there
TILT = 12.0  # degrees a leaf may tip from level
FLOOR = 0.004  # no leaf's corner is lower, metres
MAX_STRETCH = (0.93, 1.08)  # the fit may not change any side by more


def between(a, b, c, d):
    """How near the straight line from a to b comes to the one from c to d, seen from above."""

    def off(point, start, end):
        along = end - start
        share = min(1.0, max(0.0, (point - start).dot(along) / max(along.length_squared, 1e-12)))
        return (point - (start + along * share)).length

    side = lambda p, q, r: (q - p).cross(r - p)
    if side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0:
        return 0.0
    return min(off(a, c, d), off(b, c, d), off(c, a, b), off(d, a, b))


def sketch(spec, spread):
    """The mat before the fit, its runners `spread` (along x, along y) times as long as first drawn. The leaves themselves stay as they are."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = max(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    area = (hi.x - lo.x) * (hi.y - lo.y)
    grows = min(LEAF_GROWS[2], max(LEAF_GROWS[1], math.sqrt(area / LEAF_GROWS[0])))
    apart = lambda at: Vector((at.x * spread[0], at.y * spread[1]))
    longer = max(grows, math.sqrt(wide / LENGTH_AT))

    # The runners, as the corners of their lengths, from the middle out.
    count = rng.randint(*RUNNERS)
    heading = rng.uniform(0, 2 * math.pi)
    runners = []
    for k in range(count):
        heading += 2 * math.pi / count * rng.uniform(*STEP)
        share = 1.0 if k == 0 else rng.uniform(*SHORT)
        # Each starts a thumb's width out from the middle, its own way: no two spindles share a corner.
        way, at = heading, Vector((math.cos(heading), math.sin(heading))) * START
        corners = [at]
        reach = wide * rng.uniform(*REACH) * share
        lengths = max(2, round(reach / (sum(LENGTH) / 2 * longer)))
        for n in range(lengths):
            at = at + Vector((math.cos(way), math.sin(way))) * min(RUNNER_MOST, reach / lengths * rng.uniform(0.8, 1.2))
            corners.append(at)
            way += rng.uniform(-TURN, TURN)
        runners.append(corners)

    # Side lengths, until the budget is spent: a larger mat has more runner, not longer leaves.
    leaf_long = sum(LEAF) / 2 * grows
    cost = lambda a, b: 12 + 4 * 2 * (1 - MISSING) * (b - a).length / (sum(PITCH) / 2 * leaf_long * (1 + TAPER) / 2)
    planned = sum(cost(a, b) for corners in runners for a, b in zip(corners, corners[1:]))
    for _ in range(400):
        if planned >= FILL * spec["max_triangles"]:
            break
        corners = rng.choice(runners)
        k = rng.randrange(1, len(corners))
        way = corners[k] - corners[k - 1]
        off = math.atan2(way.y, way.x) + rng.choice((-1, 1)) * rng.uniform(*BRANCH_TURN)
        out = Vector((math.cos(off), math.sin(off)))
        start = corners[k] + out * (GAP + 2 * RUNNER_RADIUS)
        end = start + out * min(RUNNER_MOST, rng.uniform(*LENGTH) * longer)
        if all((end - other).length >= CROWD * leaf_long for others in runners for other in others) and all(
            between(start, end, a, b) >= (NEAR if others is corners and (a is corners[k] or b is corners[k]) else CLEAR) for others in runners for a, b in zip(others, others[1:])
        ):
            runners.append([start, end])
            planned += cost(start, end)

    runners = [[apart(corner) for corner in corners] for corners in runners]
    parts = Parts()
    for corners in runners:
        for a, b in zip(corners, corners[1:]):
            a = a + (b - a).normalized() * (GAP if a is not corners[0] else 0.0)
            head(parts, Vector((a.x, a.y, 0.0)), Vector((b.x, b.y, rng.uniform(0.0, 0.004))), RUNNER_RADIUS, RUNNER_SIDES, rings=RUNNER_RINGS, spin=rng.uniform(0, math.pi))
    # A runner lies on the ground: its lowest corner is on it.
    lowest = min(v.z for v in parts.verts)
    for v in parts.verts:
        v.z -= lowest

    def leaf(point, way, length):
        """One leaf starting at `point`, pointing the level way `way`, if the budget has room for it."""
        if parts.triangles() + 4 > spec["max_triangles"]:
            return
        tilt = math.radians(rng.uniform(-TILT, TILT))
        axis = Vector((way.x * math.cos(tilt), way.y * math.cos(tilt), math.sin(tilt)))
        first = len(parts.verts)
        leaf_piece(parts, rng, Vector((point.x, point.y, FLOOR + rng.uniform(0.0, 1.0) * (tall - FLOOR))), (Z - axis * axis.z).normalized(), axis, length, length * rng.uniform(*LEAF_WIDTH), 0.04, TILT, 0.3, floor=FLOOR)
        # No corner stands above the mat's height: a leaf tipped up at the top of the mat is lowered, whole, to it.
        over = max(v.z for v in parts.verts[first:]) - tall
        if over > 0:
            for v in parts.verts[first:]:
                v.z -= over

    # Along the runners in turn from the middle out, a pair at a time, so that a budget that runs out leaves every runner its leaves near the middle.
    stations = []
    for corners in runners:
        whole = sum((b - a).length for a, b in zip(corners, corners[1:]))
        along, side = 0.0, rng.choice((-1, 1))
        for a, b in zip(corners, corners[1:]):
            way = (b - a).normalized()
            at = rng.uniform(0.0, 0.25) * LEAF[0] * grows
            while at < (b - a).length:
                size = 1.0 - (1.0 - TAPER) * (along + at) / whole
                stations.append(((along + at) / whole, a + way * at, way, size, side))
                side = -side
                at += rng.uniform(*PITCH) * LEAF[0] * grows * size
            along += (b - a).length
        stations.append((1.0, corners[-1], (corners[-1] - corners[-2]).normalized(), TAPER, 0))
    for _, point, way, size, side in sorted(stations, key=lambda station: station[0]):
        if side == 0:
            leaf(point, Matrix.Rotation(rng.uniform(-0.3, 0.3), 2) @ way, rng.uniform(*LEAF) * grows * size)
            continue
        for hand in (side, -side):
            if rng.random() < MISSING:
                continue
            leaf(point, Matrix.Rotation(hand * math.radians(rng.uniform(*AWAY)), 2) @ way, rng.uniform(*LEAF) * grows * size)
    # A leaf's foot may by chance lie on a runner's corner: two corners at one place are lit as a hard edge.
    return parted(parts)


def draw(spec):
    """The mat, drawn as wide as fills the bounds, and fitted."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    spread = [1.0, 1.0]
    for _ in range(8):
        parts = sketch(spec, spread)
        for i in range(2):
            spread[i] *= (hi[i] - lo[i]) / (max(v[i] for v in parts.verts) - min(v[i] for v in parts.verts))
    parts = sketch(spec, spread)
    fit(parts, lo, hi, most=MAX_STRETCH)
    return parts


def build_mat(spec):
    """Build the spec's one object from its seed. The runners are of the material that is not the foliage's."""
    return to_object(draw(spec), spec)
