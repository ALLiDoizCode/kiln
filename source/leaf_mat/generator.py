"""Leaf mat generator: one seed, one mat (source/leaf_mat/brief.md).

Shared by the variants' build scripts (source/leaf_mat_1, _2, _3), which each
call `build_mat(spec)`. Everything is drawn from `random.Random(seed)` in a
fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. The patch: three to five round lobes of different sizes, each beside one
   already placed, and one or two bays where nothing grows. What lies in a
   lobe and in no bay is the mat; its outline is theirs, and so is ragged.
2. Runners: two thin straight spindles on the ground, each from one
   lobe's middle toward another's.
3. Leaves: leaf pieces at chance places in the patch, thinning toward the rim
   of each lobe, each lying nearly level, pointing away from its lobe's middle
   give or take, at a height of its own within the mat's thickness. A few lie
   a little way outside.
4. Fit: the leaves' places are drawn as far apart, along x and along y, as
   fills the bounds, with the leaves as they are; then the mat is stretched the
   little that is left, one stretch along each axis, to the spec's bounds exactly.
"""

import math
import random

from mathutils import Matrix, Vector
from plant_parts import Z, Parts, fit, head, leaf_piece, to_object

LOBES = (3, 5)
LOBE = (0.16, 0.3)  # a lobe's radius over the mat's wider side; the first is the largest
BESIDE = (0.55, 1.0)  # a lobe's middle lies this far from the one it is placed beside, over the two radii together
BAYS = (1, 2)
BAY = (0.07, 0.13)  # a bay's radius over the mat's wider side
COVER = 0.53  # leaves are laid until their surface is this share of the bounds' footprint; lapping takes about a third of it away
LEAF_AREA = 0.5  # a leaf piece's surface over its length times its width
LEAF_GROWS = (0.42, 0.8, 1.07)  # a leaf is longer in a larger mat: by the root of (the footprint over the first, m2), no less and no more than these
LEAF = (0.09, 0.13)  # a leaf's length, metres
LEAF_WIDTH = (0.48, 0.6)  # its width over its length
STRAY = 0.05  # the share of leaves that lie up to a leaf's length outside their lobe
THIN = 1.0  # leaves thin toward a lobe's rim: the higher above 1, the more of them near its middle
TILT = 14.0  # degrees a leaf may tip from level
SWING = 1.2  # radians a leaf may point away from straight out of its lobe
FLOOR = 0.004  # no leaf's corner is lower, metres
RUNNERS = (2, 2)
RUNNER_RADIUS = 0.007  # metres
RUNNER_MOST = 0.35  # no runner is longer, metres: a longer one is painted too coarsely for the light along its edges to show
RUNNER_SIDES = 4
RUNNER_RINGS = ((0.06, 1.0), (0.94, 1.0))
MAX_STRETCH = (0.93, 1.08)  # the fit may not change any side by more


def sketch(spec, spread):
    """The mat before the fit, its leaves' places `spread` (along x, along y) times as far apart as first drawn. The leaves themselves stay as they are."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = max(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    lobes = [(Vector((0.0, 0.0)), wide * LOBE[1] * rng.uniform(0.85, 1.0))]
    for _ in range(rng.randint(*LOBES) - 1):
        at, beside = rng.choice(lobes)
        radius = wide * rng.uniform(*LOBE)
        angle = rng.uniform(0, 2 * math.pi)
        lobes.append((at + Vector((math.cos(angle), math.sin(angle))) * (beside + radius) * rng.uniform(*BESIDE), radius))
    bays = []
    for _ in range(rng.randint(*BAYS)):
        at, radius = rng.choice(lobes)
        angle = rng.uniform(0, 2 * math.pi)
        bays.append((at + Vector((math.cos(angle), math.sin(angle))) * radius * rng.uniform(0.3, 1.0), wide * rng.uniform(*BAY)))
    apart = lambda at: Vector((at.x * spread[0], at.y * spread[1]))

    parts = Parts()
    order = list(range(len(lobes)))
    rng.shuffle(order)
    for k in range(min(len(lobes) - 1, rng.randint(*RUNNERS))):
        (a, ra), (b, rb) = lobes[order[k]], lobes[order[k + 1]]
        start = a + (a - b).normalized() * ra * rng.uniform(0.0, 0.5)
        end = b + (b - a).normalized() * rb * rng.uniform(0.0, 0.5)
        start, end = apart(start), apart(end)
        if (end - start).length > RUNNER_MOST:
            end = start + (end - start).normalized() * RUNNER_MOST
        head(parts, Vector((start.x, start.y, 0.0)), Vector((end.x, end.y, rng.uniform(0.0, 0.006))), RUNNER_RADIUS, RUNNER_SIDES, rings=RUNNER_RINGS, spin=rng.uniform(0, math.pi))
    # A runner lies on the ground: its lowest corner is on it.
    lowest = min(v.z for v in parts.verts)
    for v in parts.verts:
        v.z -= lowest

    area = (hi.x - lo.x) * (hi.y - lo.y)
    grows = min(LEAF_GROWS[2], max(LEAF_GROWS[1], math.sqrt(area / LEAF_GROWS[0])))
    weights = [radius * radius for _, radius in lobes]
    laid = 0.0
    while laid < COVER * area and parts.triangles() + 4 <= spec["max_triangles"]:  # and never past the budget
        at, radius = rng.choices(lobes, weights)[0]
        angle, reach = rng.uniform(0, 2 * math.pi), radius * rng.uniform(0, 1) ** (THIN / 2)
        length = rng.uniform(*LEAF) * grows
        if rng.random() < STRAY:
            reach = radius + length * rng.uniform(0.2, 1.0)
        out = Vector((math.cos(angle), math.sin(angle)))
        point = at + out * reach
        if any((point - bay).length < bay_radius for bay, bay_radius in bays):
            continue
        point = apart(point)
        way = Matrix.Rotation(rng.uniform(-SWING, SWING), 2) @ out
        tilt = math.radians(rng.uniform(-TILT, TILT))
        axis = Vector((way.x * math.cos(tilt), way.y * math.cos(tilt), math.sin(tilt)))
        up = (Z - axis * axis.z).normalized()
        width = length * rng.uniform(*LEAF_WIDTH)
        first = len(parts.verts)
        leaf_piece(parts, rng, Vector((point.x, point.y, FLOOR + rng.uniform(0.0, 1.0) * (tall - FLOOR))), up, axis, length, width, 0.5, TILT, 0.3, floor=FLOOR)
        # No corner stands above the mat's height: a leaf tipped up at the top of the mat is lowered, whole, to it.
        over = max(v.z for v in parts.verts[first:]) - tall
        if over > 0:
            for v in parts.verts[first:]:
                v.z -= over
        laid += LEAF_AREA * length * width
    return parts


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
