"""Tall grass generator: one seed, one clump (source/tall_grass/brief.md).

Shared by the variants' build scripts (source/tall_grass_1, _2, _3), which
each call `build_clump(spec)`. Everything is drawn from `random.Random(seed)`
in a fixed order, as plain lists (tools/plant_parts.py), so a seed gives one mesh.

1. Rootstock: a low closed mound on the ground at the origin.
2. Blades: many thin strips from the rootstock, each from its own place on a
   spiral. A blade leaves the rootstock nearly upright (the further out its
   foot, the less so, and the shorter it is), and bends over toward its tip,
   outward, a different amount for each. Each is turned about its own length
   by chance, so that from no side are all of them seen edge on.
3. Seed stalks: a few thin, nearly straight blades from the middle, taller than
   the leaves, each with a seed head on its end: a closed spindle of the
   rootstock's material.
4. Fit: the clump is drawn as far out as fills the bounds and then stretched
   about the origin, each side by what it needs, to the spec's bounds exactly.
"""

import math
import random

from mathutils import Matrix, Vector
from plant_parts import Z, Parts, blade, drawn_to_fit, head, mound, parted, to_object

ROOTSTOCK_RADIUS = 0.13  # over the clump's width
ROOTSTOCK_HEIGHT = 0.25  # over its own radius
ROOTSTOCK_SIDES = 6
FEET = 0.85  # blades leave the rootstock within this share of its radius
FOOT_UP = 0.02  # a blade's foot is this far above the ground, metres: none of its corners goes under it
BLADES_PER_M = 84  # blades per metre of the clump's width, and
BLADES = (72, 84)  # the least and the most
INNER_LEAN = (0.0, 5.0)  # degrees from upright at its foot, for a blade from the middle
OUTER_LEAN = (5.0, 15.0)  # and for one from the rim
LEAVES_TOP = 1.0  # the longest leaf, over the clump's height: the seed heads stand above the leaves
OUTER_SHORT = 0.85  # a blade from the rim is this long, over one from the middle
LENGTH = (0.86, 1.0)  # a blade's length, over what its place gives
DROOP = (0.08, 0.42)  # how far its tip is carried outward by the bend, over its length
INNER_DROOP = 0.4  # a blade from the middle bends this much, over one from the rim: the middle of the clump stands
STAND = 0.8  # a blade keeps the way it left the rootstock for this share of its length, and bends over after it
SINK = 0.45  # and how far down, over that
SWING = 0.7  # a blade bends outward within this many radians of straight out from the middle
TWIST = 0.6  # and its face is turned by up to this many radians
ALONG = (0.0, 0.45, 0.72, 0.9, 1.0)  # where along its curve a blade's rows stand; the last is its tip
WIDE = (0.75, 1.0, 0.8, 0.5)  # its width at each row but the tip, over its greatest
WIDTH = (0.038, 0.052)  # greatest width over the blade's length,
WIDTH_MOST = 0.045  # and the most its mean width may be, over the straight line from its foot to its tip (`narrowed`)
STALKS = (3, 6)  # seed stalks
STALK_FEET = 0.5  # they leave the rootstock within this share of its radius
STALK_LEAN = (1.0, 7.0)  # degrees from upright
STALK_LENGTH = (0.9, 1.0)  # over the clump's height
STALK_BOW = (0.03, 0.06)  # how far its middle stands off the straight line, over its length
STALK_ALONG = (0.0, 0.5, 0.86, 1.0)
STALK_WIDTH = 0.013  # over its length
HEAD_LENGTH = (0.1, 0.15)  # a seed head's length over the clump's height,
HEAD_MOST = 0.19  # and the most it may be, metres
HEAD_RADIUS = 0.13  # its radius over its length
HEAD_SIDES = 4
MAX_STRETCH = (0.7, 1.4)  # the fit may not change any side by more


def curve(foot, toward, end, along):
    """Points on the curve from `foot` to `end` that bends toward `toward`, at the shares `along` of its length."""
    fine = [foot * (1 - t) ** 2 + toward * 2 * t * (1 - t) + end * t * t for t in (k / 48 for k in range(49))]
    run = [0.0]
    for a, b in zip(fine, fine[1:]):
        run.append(run[-1] + (b - a).length)
    points = []
    for share in along:
        at = share * run[-1]
        k = max(i for i in range(len(run) - 1) if run[i] <= at + 1e-12)
        points.append(fine[k].lerp(fine[k + 1], min(1.0, (at - run[k]) / max(run[k + 1] - run[k], 1e-12))))
    return points


def sketch(spec, spread):
    """The clump before the fit, its blades leaning and bending `spread` times as far out as first drawn."""
    rng = random.Random(spec["seed"])
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    wide, tall = min(hi.x - lo.x, hi.y - lo.y), hi.z - lo.z
    parts = Parts()
    radius = wide * ROOTSTOCK_RADIUS
    mound(parts, rng, radius, radius * ROOTSTOCK_HEIGHT, ROOTSTOCK_SIDES, seams=True)

    count = min(BLADES[1], max(BLADES[0], round(BLADES_PER_M * wide)))
    golden = math.pi * (3 - math.sqrt(5))
    turn = rng.uniform(0, 2 * math.pi)
    for k in range(count):
        share = math.sqrt((k + 0.5) / count)  # 0 at the middle of the clump, 1 at its rim
        azimuth = turn + golden * k + rng.uniform(-0.2, 0.2)
        out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
        foot = out * radius * FEET * share + Z * (FOOT_UP + radius * ROOTSTOCK_HEIGHT * 0.4 * (1 - share))
        way = Matrix.Rotation(rng.uniform(-SWING, SWING), 3, "Z") @ out
        low, high = (a + (b - a) * share * share for a, b in zip(INNER_LEAN, OUTER_LEAN))
        wider = 1 + (spread - 1) * share  # the rim is what is drawn further out to fill the bounds; the middle stands as it is
        lean = math.radians(min(50.0, rng.uniform(low, high) * wider))
        length = tall * LEAVES_TOP * (1 - (1 - OUTER_SHORT) * share) * rng.uniform(*LENGTH)
        start = way * math.sin(lean) + Z * math.cos(lean)
        droop = rng.uniform(*DROOP) * min(wider, 1.8) * (INNER_DROOP + (1 - INNER_DROOP) * share * share)
        end = foot + start * length * 0.95 + (way - Z * SINK) * length * droop
        spine = curve(foot, foot + start * length * STAND, end, ALONG)
        width = length * rng.uniform(*WIDTH)
        # Its upper face looks back at the middle of the clump and up, square to the straight line from its
        # foot to its tip, and is then turned about that line: never along the blade itself, wherever it bends.
        straight = (spine[-1] - spine[0]).normalized()
        front = Matrix.Rotation(rng.uniform(-TWIST, TWIST), 3, straight) @ straight.cross(Z.cross(way)).normalized()
        blade(parts, spine, [width * part for part in WIDE], front)

    stalks = rng.randint(*STALKS)
    turn = rng.uniform(0, 2 * math.pi)
    for k in range(stalks):
        azimuth = turn + 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / stalks
        out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
        foot = out * radius * STALK_FEET * rng.uniform(0.3, 1.0) + Z * radius * ROOTSTOCK_HEIGHT * 0.5
        lean = math.radians(rng.uniform(*STALK_LEAN))
        way = out * math.sin(lean) + Z * math.cos(lean)
        length = tall * (1.0 if k == 0 else rng.uniform(*STALK_LENGTH))
        end = foot + way * length
        toward = (foot + end) / 2 + (out * math.cos(lean) - Z * math.sin(lean)) * -length * rng.uniform(*STALK_BOW)
        spine = curve(foot, toward, end, STALK_ALONG)
        blade(parts, spine, [length * STALK_WIDTH] * 3, Matrix.Rotation(rng.uniform(-math.pi, math.pi), 3, "Z") @ Vector((1, 0, 0)))
        long = min(HEAD_MOST, tall * rng.uniform(*HEAD_LENGTH))
        along = (spine[-1] - spine[-2]).normalized()
        # The stalk's point is inside the head: the head ends a little past it.
        head(parts, end - along * long * 0.97, end + along * long * 0.03, long * HEAD_RADIUS, HEAD_SIDES, spin=rng.uniform(0, math.pi))
    return parts


def narrowed(parts):
    """The fitted clump with every leaf no wider than WIDTH_MOST: the fit stretches some, and a blade bent far over is short from foot to tip."""
    for piece in range(len(parts.piece_out)):
        faces = [face for face, owner in zip(parts.faces, parts.pieces) if owner == piece]
        rows = [face[:2] for face in faces if len(face) == 4] + [faces[-2][3:1:-1]]
        tip = parts.verts[faces[-1][2]]
        foot = (parts.verts[rows[0][0]] + parts.verts[rows[0][1]]) / 2
        area = sum(((parts.verts[a] - parts.verts[b]).length + (parts.verts[c] - parts.verts[d]).length) / 2 * ((parts.verts[a] + parts.verts[b]) / 2 - (parts.verts[c] + parts.verts[d]) / 2).length for (a, b), (c, d) in zip(rows, rows[1:]))
        over = area / (tip - foot).length_squared / WIDTH_MOST
        if over > 1:
            for a, b in rows:
                middle = (parts.verts[a] + parts.verts[b]) / 2
                parts.verts[a], parts.verts[b] = middle + (parts.verts[a] - middle) / over, middle + (parts.verts[b] - middle) / over
    return parts


def draw(spec):
    """The clump, drawn as wide as fills the bounds, fitted, and its blades held to their width."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    return parted(narrowed(drawn_to_fit(lambda spread: sketch(spec, spread), lo, hi, about_origin=True, most=MAX_STRETCH)))


def build_clump(spec):
    """Build the spec's one object from its seed. The rootstock and the seed heads are of the material that is not the foliage's."""
    return to_object(draw(spec), spec)
