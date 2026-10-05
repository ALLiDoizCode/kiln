"""Tree generator: one spec, one tree (source/tree/brief.md, ADR 13).

Shared by the build scripts of every tree asset (source/tree_1, ...), which
each call `build_tree(spec)`. A spec gives a `species`, a `growth_stage`, a
`seed` and bounds. The species is a recipe, species/<name>.toml: every number
below that says how the trunk forks, where the pads sit and what a leaf piece
is. The growth stage is the tree's height over a mature tree's; the recipe
says how girth, lean, fork, pad count, pad width and leaf length follow it
(`grown`).
Everything else is drawn from `random.Random(seed)`, in a fixed order, and
built as plain lists of vertices and faces, so the same spec gives the same
mesh. A new tree is a new spec; a new species is a new recipe.

1. Pads: three to five, of clearly different widths, placed round and above
   the trunk inside the spec's bounds, at staggered heights, and pushed apart
   until clear air separates every pair. A pad is two to four overlapping
   lobes of different sizes: rounded masses, wider than tall and flat
   underneath, the largest on the pad's outer side.
2. Trunk: a tube of flat sides with a narrow strip along every corner (the
   soft edge), leaning and bending a little, tapering, its corners pulled out
   into a few roots at the ground. It carries on past the fork as the leader,
   into the highest pad.
3. Branches: one tapering tube per remaining pad, leaving the trunk near the
   fork (or the middle of an earlier branch, when that is much nearer),
   running out first and then up, and ending inside its pad's main lobe; a
   twig runs on from there into each of the pad's other lobes.
4. Cores: a closed, low-triangle dome inside every lobe, in the leaf
   material (ADR 9 as amended). It is what shows between the pieces, and from
   below it closes the view up into the pad.
5. Leaves: flat pointed pieces with a notch on either side. On each lobe a
   shell of them, overlapping like shingles (lying near the surface, pointing
   down it and lifted outward); a skirt hanging from its rim, pointing out
   and down past the underside; and a few hanging under it.
6. Fit: the whole tree is stretched, about the foot of the trunk, to the
   spec's bounds.
7. Keep or redraw: the tree is measured as the gate measures it, against the
   brief's shape checks with room to spare (MARGINS). A tree that misses is
   thrown away and the seed draws the next one; a seed none of whose trees
   passes fails the build with every tree's reasons.

Normals are set by hand. Bark: each flat side is lit flat across and smooth
along its length, and the strips blend from one side to the next. Leaves:
every corner of a piece carries one normal, part the piece's own and part the
direction out of its lobe and upward, so a lobe is lit as a round mass and
each piece still catches the light at its own angle. Cores are lit round.

Each material gets one flat colour; tools/paint.py paints the bark (with its
grain, which runs along each limb by the `grain` attribute written here: ADR
12) and gives each leaf piece and core its colour (ADR 10, ADR 11).
"""

import contextlib
import copy
import io
import json
import math
import random
import tomllib
from pathlib import Path
from types import SimpleNamespace

import bmesh
import bpy
import foliage
import numpy
from mathutils import Quaternion, Vector
from pipeline import Checks, conventions, linear_rgb
from validate import check_canopy, check_foliage, check_skeleton

Z = Vector((0, 0, 1))

MAX_STRETCH = (0.85, 1.2)  # the fit may not change any dimension by more
TREES = 40  # how many whole trees one seed may draw before it is given up

# Room to spare. A tree is kept only when it meets the brief's shape checks with these in place
# of the spec's own limits, so that no variant sits on the edge of one (spec key -> stricter value).
def inside(low, high):
    """A range drawn in by shares of its own width, so that a stage with its own range keeps the same room."""
    return lambda span: [round(span[0] + (span[1] - span[0]) * low, 3), round(span[1] - (span[1] - span[0]) * high, 3)]


# A value is the stricter limit itself, or a function of the spec's own limit where the brief gives
# each growth stage its own (for the mature tree: 3,800 triangles, a fork between 2.2 and 3.3 m, a lean of 0.22 to 0.7 m,
# bark 0.028 of what is seen above the fork).
MARGINS = {
    "max_triangles": lambda most: round(most * 0.95),
    "skeleton.fork_m": inside(2 / 15, 2 / 15),
    "skeleton.lean_m": inside(7 / 65, 10 / 65),
    "skeleton.max_taper": 0.85,
    "skeleton.max_branch_taper": 0.72,
    "skeleton.min_flare": 2.3,
    "skeleton.min_seen_share": lambda least: round(least * 1.4, 3),
    "skeleton.min_seen_views": 7,
    "foliage.piece_m": lambda span: [round(span[0] + 0.03, 3), round(span[1] - 0.03, 3)],
    "foliage.min_pointing_out": 0.84,
    "foliage.min_pointing_down": 0.75,
    "foliage.sky_share": [0.23, 0.46],
    "foliage.min_sky_views": 6,
    "foliage.min_lobe_ratio": 1.28,
    "foliage.max_core_seen": 0.085,
    "foliage.max_core_seen_below": 0.42,
    "foliage.min_pad_flatness": lambda least: round(least + 0.1, 3),
    "foliage.min_pad_spread": lambda least: round(least + 0.1, 3),
    "foliage.max_seen_into": 0.125,
    "foliage.min_rim_points_per_m": 1.2,
}

# A conifer's (a spec with `tiers`), in place of or beside those: the leader shows from the four level views and from below,
# and from none above, so no view is left to spare; the tiers' own limits are drawn in a little.
TIER_MARGINS = {
    "skeleton.min_seen_views": lambda views: views,
    "skeleton.min_seen_share": lambda least: round(least * 1.15, 3),
    "foliage.sky_share": [0.21, 0.49],
    "foliage.max_core_seen": 0.095,
    "foliage.max_seen_into": 0.14,
    "skeleton.max_branch_taper": 0.78,
    "tiers.max_top_share": lambda most: round(most - 0.03, 3),
    "tiers.min_droop": lambda least: round(least + 0.03, 3),
    "tiers.max_tip_width_m": lambda most: round(most - 0.08, 3),
    "tiers.max_leader_bow_m": lambda most: round(most - 0.04, 3),
    "tiers.tip_off_m": inside(0.1, 0.1),
}

SIDE, STRIP_FACE, CONE, GROUND, LEAF, CORE_FACE = range(6)

SPECIES = Path(__file__).resolve().parent / "species"


def recipe_of(spec):
    """The spec's species recipe as written: a table of tables (species/<name>.toml)."""
    with open(SPECIES / f"{spec['species']}.toml", "rb") as f:
        return tomllib.load(f)


def at_stage(curve, stages, stage):
    """A growth multiplier at a stage: straight lines between the stages the recipe names, level beyond them."""
    if stage <= stages[0]:
        return curve[0]
    for (a, b), (low, high) in zip(zip(stages, stages[1:]), zip(curve, curve[1:])):
        if stage <= b:
            return low + (high - low) * (stage - a) / (b - a)
    return curve[-1]


def grown(recipe, stage):
    """The recipe at a growth stage, to read as `r.trunk.sides`: the mature tree's numbers, scaled as `[growth]` says."""
    recipe = copy.deepcopy(recipe)
    growth = recipe.pop("growth")
    by = {name: at_stage(curve, growth["stage"], stage) for name, curve in growth.items() if name not in ("stage", "mature_height_m")}

    def scale(table, key, factor):
        value = recipe[table][key]
        recipe[table][key] = [v * factor for v in value] if isinstance(value, list) else value * factor

    if "follows" in recipe:
        # A recipe that says itself which of its numbers each curve scales (the conifer's).
        for curve, keys in recipe.pop("follows").items():
            for key in keys:
                scale(*key.split("."), by[curve])
        return SimpleNamespace(**{name: SimpleNamespace(**table) for name, table in recipe.items()})
    for key in ("breast_radius", "root_rise"):
        scale("trunk", key, by["girth"])
    scale("trunk", "tip_radius", math.sqrt(by["girth"]))
    scale("branches", "twig_radius", math.sqrt(by["girth"]))
    for key in ("lean", "bend"):
        scale("trunk", key, by["lean"])
    for key in ("fork_lowest", "fork_spread"):
        scale("branches", key, by["fork"])
    for key in ("largest", "smallest"):
        scale("pads", key, by["pad_width"])
    for table, key in (("leaf", "length"), ("skirt", "drop"), ("pads", "reach")):
        scale(table, key, by["leaf"])
    for table, key in (("leaf", "spacing"), ("skirt", "spacing"), ("skirt", "under_spacing")):
        scale(table, key, by["leaf_spacing"])
    scale("pads", "floor", by["pad_floor"])
    scale("leaf", "foot", by["leaf_foot"])
    scale("trunk", "rings", by["trunk_rings"])
    recipe["pads"]["count_share"] = by["pad_count"]
    return SimpleNamespace(**{name: SimpleNamespace(**table) for name, table in recipe.items()})

_MEASURED = {}  # (spec, constants, which tree of the seed) -> what `unmet` said of it, within this process


class Tree:
    """The mesh as lists, in the order they are made."""

    def __init__(self):
        self.verts = []
        self.faces = []
        self.kinds = []
        self.pads = []  # leaf faces only: which pad (index) each belongs to; -1 for bark
        self.pieces = []  # and which piece; -1 for bark
        self.piece_count = 0
        self.piece_out = []  # per piece: the direction out of its lobe
        self.core_normals = {}  # core vertex -> its normal
        self.seams = []  # pairs of vertices: bark edges along which the surface is cut open to be painted
        # Bark faces only: per corner, (metres round the limb, metres along it, a number for the limb), which
        # tools/paint.py reads to run the grain along each limb; None for every other face.
        self.grain = []
        self.limbs = 0

    def vert(self, co):
        self.verts.append(Vector(co))
        return len(self.verts) - 1

    def face(self, corners, kind, pad=-1, piece=-1, grain=None):
        self.faces.append(tuple(corners))
        self.grain.append(grain)
        self.kinds.append(kind)
        self.pads.append(pad)
        self.pieces.append(piece)


def frames(points, first=None):
    """A tangent and two axes across it at every point, carried along without twisting.

    `first` is the direction the first axis starts nearest to."""
    tangents = []
    for i in range(len(points)):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        tangents.append((b - a).normalized())
    first = first or tangents[0].orthogonal()
    first = (first - tangents[0] * first.dot(tangents[0])).normalized()
    result = []
    for i, tangent in enumerate(tangents):
        if i:
            first = (tangents[i - 1].rotation_difference(tangent) @ first).normalized()
        result.append((tangent, first, tangent.cross(first).normalized()))
    return result


def tube(tree, points, radii, sides, strip=0.0, spin=0.0, ground=False, reach=None, frame=None, valleys=None, valley=1.0, grain_from=0):
    """A closed tapering tube along `points`.

    With `strip` each corner is two vertices, with a narrow face between them.
    `reach[ring][corner]` scales a corner's distance from the axis (roots).
    `ground` makes the first ring level at its own height with a flat cap
    under it; otherwise both ends close to a point.
    `frame[ring]` is that ring's (tangent, axis across, axis across), in place
    of the frames carried along the points.
    `valleys[ring][side]` gives each of the lowest rings one more vertex in
    every side: that share of the way from the side's first corner to its
    second, and pulled in to `valley` times the ring's radius, so that the
    ground between two roots comes back to the trunk. The first ring above
    them joins those vertices to its own corners with triangles.
    `grain_from` is the first ring whose grain is measured round itself;
    the rings below it (the foot) take its measure at their corners, and on
    a root's flank measure on from the root's crest over the flank itself.
    """
    rings = []
    frame = frame or frames(points, Vector((1, 0, 0)) if ground else None)
    per = 2 if strip else 1
    for k, (point, radius) in enumerate(zip(points, radii)):
        tangent, across, along = frame[k]
        if ground and k == 0:
            across, along = Vector((1, 0, 0)), Vector((0, 1, 0))
        corners = []
        for j in range(sides):
            scale = reach[k][j] if reach and k < len(reach) else 1.0
            # A root is a fin: its two corner vertices stay close together however far it reaches.
            half = strip * math.pi / sides / (scale if scale > 1.2 else 1.0)
            for step in range(per):
                angle = spin + 2 * math.pi * j / sides + (half * (2 * step - 1) if strip else 0.0)
                corners.append(point + (across * math.cos(angle) + along * math.sin(angle)) * radius * scale)
        ring = []
        for j in range(sides):
            ring += [tree.vert(co) for co in corners[per * j : per * j + per]]
            if valleys and k < len(valleys):
                between = corners[per * j + per - 1].lerp(corners[per * (j + 1) % len(corners)], valleys[k][j]) - point
                ring.append(tree.vert(point + between * min(1.0, radius * valley / between.length)))
        rings.append(ring)
    count = sides * per

    def chain(k, j):
        """Side `j` of ring `k`: where in the ring its vertices are, from the last vertex of one corner to the first of the next."""
        size = len(rings[k]) // sides
        return list(range(size * j + per - 1, size * (j + 1) + 1))

    # Grain: how far round the limb each corner of a ring is, in metres over its own surface (so the
    # grain is as fine on a root's fin as on the trunk above it), and how far along the limb each ring is.
    round_at = []
    for ring in rings:
        far = [0.0]
        for i in range(len(ring)):
            far.append(far[-1] + (tree.verts[ring[(i + 1) % len(ring)]] - tree.verts[ring[i]]).length)
        round_at.append(far)
    # But not below `grain_from`, on the foot: a ring there is far longer than the trunk's above it, and by its own
    # measure the grain would slant across the flare by the difference. Those rings take that ring's measure, corner
    # for corner, so a streak runs straight down the trunk and out along a root's crest.
    # A root's flank is several times as wide as the side of the trunk it grows from, and by the trunk's measure
    # its grain would be stretched into broad patches. So a flank measures on from its root's crest over its own
    # surface: `flank_at[ring, place]` is a valley vertex's measure as each of the two flanks that meet there
    # has it. The grain breaks along the valley, where the bark folds and the painted islands are cut anyway.
    flank_at = {}
    for k in range(grain_from):
        above, far, own = round_at[grain_from], [], round_at[k]
        for j in range(sides):
            far += above[per * j : per * j + per]
            if len(rings[k]) > count:
                place = len(far)
                flank_at[k, place] = (above[per * j + per - 1] + own[place] - own[place - 1], above[per * j + per] - (own[place + 1] - own[place]))
                far.append(above[per * j + per - 1] + (above[per * j + per] - above[per * j + per - 1]) * valleys[k][j])
        round_at[k] = far + [above[count]]
    along_at = [0.0]
    for a, b in zip(points, points[1:]):
        along_at.append(along_at[-1] + (b - a).length)
    limb = tree.limbs * 3.7
    tree.limbs += 1

    def face(kind, *corners, flank=None):
        """A face from (ring, place in the ring) corners; a place one past a ring's end is its first vertex again.

        `flank` says which root's flank the face is: 0 that of the corner before its valley vertices, 1 the one after."""
        across = [round_at[k][i] if flank is None or (k, i) not in flank_at else flank_at[k, i][flank] for k, i in corners]
        tree.face([rings[k][i % len(rings[k])] for k, i in corners], kind, grain=[(far, along_at[k], limb) for far, (k, _) in zip(across, corners)])

    for k in range(len(rings) - 1):
        for j in range(sides):
            lower, upper = chain(k, j), chain(k + 1, j)
            if strip:
                face(STRIP_FACE, (k, lower[0] - 1), (k, lower[0]), (k + 1, upper[0]), (k + 1, upper[0] - 1))
            if len(lower) == len(upper):
                for flank, (a, b, c, d) in enumerate(zip(lower, lower[1:], upper[1:], upper)):
                    face(SIDE, (k, a), (k, b), (k + 1, c), (k + 1, d), flank=flank if len(lower) == 3 else None)
            else:
                # Where the valley's vertices end: a fan from each to the two corners above it.
                first, middle, last = lower
                face(SIDE, (k, first), (k, middle), (k + 1, upper[0]), flank=0)
                face(SIDE, (k, middle), (k + 1, upper[1]), (k + 1, upper[0]))
                face(SIDE, (k, middle), (k, last), (k + 1, upper[1]), flank=1)
        # Each stretch between two rings is cut once along its length, to unroll flat.
        tree.seams.append((rings[k][0], rings[k + 1][0]))
        # The foot does not unroll: a band of fins folds over itself. It is cut along every valley, so each
        # root lies flat by itself, its two flanks either side of its crest.
        if len(rings[k]) > count:
            for j in range(sides):
                lower, upper = chain(k, j), chain(k + 1, j)
                tree.seams.append((rings[k][lower[1]], rings[k + 1][upper[1] % len(rings[k + 1])]))
    # And every ring is a cut, so no painted island is longer than one stretch of a limb.
    for ring in rings:
        tree.seams += [(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))]
    start, end = points[0], points[-1]
    first, last = rings[0], rings[-1]
    if ground:
        centre = tree.vert(start)
        for i in range(len(first)):
            tree.face((centre, first[(i + 1) % len(first)], first[i]), GROUND, grain=[(round_at[0][i], -radii[0], limb), (round_at[0][i + 1], 0.0, limb), (round_at[0][i], 0.0, limb)])
    else:
        apex = tree.vert(start - frame[0][0] * radii[0] * 0.35)
        for i in range(count):
            tree.face((apex, first[(i + 1) % count], first[i]), CONE, grain=[(round_at[0][i], -radii[0], limb), (round_at[0][i + 1], 0.0, limb), (round_at[0][i], 0.0, limb)])
        tree.seams.append((first[0], apex))
    apex = tree.vert(end + frame[-1][0] * radii[-1] * 2.0)
    for i in range(count):
        tree.face((last[i], last[(i + 1) % count], apex), CONE, grain=[(round_at[-1][i], along_at[-1], limb), (round_at[-1][i + 1], along_at[-1], limb), (round_at[-1][i], along_at[-1] + radii[-1] * 2, limb)])
    tree.seams.append((last[0], apex))


def bezier(a, c, b, t):
    return a * (1 - t) ** 2 + c * (2 * t * (1 - t)) + b * t**2


class Lobe:
    """One rounded mass of a pad: an ellipsoid, flatter below its middle than above."""

    def __init__(self, centre, radius, up, down):
        self.centre, self.radius, self.up, self.down = centre, radius, up, down

    def surface(self, unit):
        """The surface point and outward normal for a point on the unit sphere."""
        vertical = self.up if unit.z >= 0 else self.down
        point = self.centre + Vector((unit.x * self.radius, unit.y * self.radius, unit.z * vertical))
        normal = Vector((unit.x / self.radius, unit.y / self.radius, unit.z / vertical)).normalized()
        return point, normal

    def depth(self, point):
        """Where a point lies: 0 at the lobe's middle, 1 on its surface."""
        offset = point - self.centre
        vertical = self.up if offset.z >= 0 else self.down
        return math.sqrt((offset.x**2 + offset.y**2) / self.radius**2 + offset.z**2 / vertical**2)


class Pad:
    """A clump of foliage: two to four overlapping lobes inside a circle of `radius` about `centre`."""

    def __init__(self, r, centre, radius, shapes):
        self.r = r
        self.centre = centre
        self.radius = radius  # half the pad's width
        # Each lobe as shares of the pad's radius: (offset from the pad's middle, radius, height above its middle).
        self.shapes = shapes

    def lobes(self):
        return [Lobe(self.centre + offset * self.radius, share * self.radius, tall * self.radius, tall * self.radius * self.r.lobes.under) for offset, share, tall in self.shapes]

    def above(self):
        """How far the pad's surface rises above its middle."""
        return max(offset.z + tall for offset, _, tall in self.shapes) * self.radius

    def below(self):
        """How far it hangs below its middle, skirt included."""
        return max(tall * self.r.lobes.under - offset.z for offset, _, tall in self.shapes) * self.radius + self.r.skirt.drop

    def reach(self, direction):
        """Distance from the middle to the outside of the pad along a unit direction, leaf tips included."""
        vertical = self.above() if direction.z >= 0 else self.below()
        return self.r.pads.reach + 1.0 / math.sqrt((direction.x**2 + direction.y**2) / self.radius**2 + direction.z**2 / vertical**2)


class Bough(Lobe):
    """One bough of a tier: a lobe drawn out along `out`, level, from the leader, that hangs lower the further out it goes.

    `root` is on the leader's axis. The foliage runs from `inner` behind it to `length` in front, `wide`
    to either side, `up` above and `down` below a middle line that sags by `droop` times the length at
    the tip, as (share of the length) to the power `sag`."""

    def __init__(self, root, out, length, inner, wide, up, down, droop, sag):
        self.root, self.out, self.side = root, out, Vector((-out.y, out.x, 0))
        self.length, self.droop, self.sag = length, droop, sag
        self.long, self.wide, self.up, self.down = (length + inner) / 2, wide, up, down
        self.middle = (length - inner) / 2  # how far out the foliage's middle is
        self.radius = math.sqrt(self.long * self.wide)
        self.centre = self.at(0.0, 0.0, 0.0)

    def hang(self, far):
        """How far the middle line has sunk, `far` metres out from the leader."""
        return -self.droop * self.length * max(far / self.length, 0.0) ** self.sag

    def slope(self, far):
        return -self.droop * self.sag * max(far / self.length, 0.0) ** (self.sag - 1)

    def at(self, x, y, z):
        """A point given along the bough, across it and above its middle line, from the foliage's middle."""
        far = self.middle + x
        return self.root + self.out * far + self.side * y + Z * (z + self.hang(far))

    def inside(self, unit):
        """The point for a place in the unit ball (not only on its surface)."""
        return self.at(unit.x * self.long, unit.y * self.wide, unit.z * (self.up if unit.z >= 0 else self.down))

    def out_of(self, unit):
        """The direction out of the bough at a place on the unit sphere."""
        vertical = self.up if unit.z >= 0 else self.down
        x, y, z = unit.x / self.long, unit.y / self.wide, unit.z / vertical
        return (self.out * (x - z * self.slope(self.middle + unit.x * self.long)) + self.side * y + Z * z).normalized()

    def surface(self, unit):
        return self.inside(unit), self.out_of(unit)

    def unit_of(self, point):
        offset = point - self.root
        far = offset.dot(self.out)
        z = offset.z - self.hang(far)
        return Vector(((far - self.middle) / self.long, offset.dot(self.side) / self.wide, z / (self.up if z >= 0 else self.down)))

    def depth(self, point):
        return self.unit_of(point).length


class Tier:
    """A whorl of boughs round the leader at one height, or the top: a spire over a few short boughs."""

    def __init__(self, boughs):
        self.boughs = boughs
        self.radius = max((b.length for b in boughs if isinstance(b, Bough)), default=0.0)
        self.shapes = boughs

    def lobes(self):
        return self.boughs


def draw_lobes(r, rng, toward):
    """A pad's lobes, as shares of its radius: one main lobe on the side `toward` (an azimuth) and one to three smaller ones round it."""
    count = rng.choices([c for c, _ in r.lobes.counts], [w for _, w in r.lobes.counts])[0]
    turn = toward + rng.uniform(-0.5, 0.5)
    main = rng.uniform(*r.lobes.main)
    # The main lobe touches the pad's circle on one side; the others touch it on the other sides.
    shapes = [(Vector((math.cos(turn), math.sin(turn), 0)) * (1 - main), main, main * rng.uniform(*r.lobes.tall))]
    for k in range(count - 1):
        side = rng.uniform(*r.lobes.side) * (1.0 - 0.12 * k)
        azimuth = turn + math.pi + (k - (count - 2) / 2) * 2 * math.pi / 3.2 + rng.uniform(-0.3, 0.3)
        offset = Vector((math.cos(azimuth), math.sin(azimuth), 0)) * (1 - side) + Z * main * rng.uniform(*r.lobes.drop)
        shapes.append((offset, side, side * rng.uniform(*r.lobes.tall)))
    return shapes


def place_pads(r, rng, lo, hi, fork_z):
    """Pads inside the bounds, staggered in height, with clear air between every pair."""
    count = rng.choices([c for c, _ in r.pads.counts], [w for _, w in r.pads.counts])[0]
    # The mature tree's count, scaled by the growth stage: a sapling has two pads, an old tree five or six.
    count = min(r.pads.most, max(r.pads.fewest, math.floor(count * r.pads.count_share + 0.5)))
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0))
    half = Vector(((hi.x - lo.x) / 2, (hi.y - lo.y) / 2, 0))
    floor, top = fork_z + r.pads.floor, hi.z
    # Two pads are a row, not a ring: they lie along the longer side of the bounds, one toward each end.
    row = count == 2

    def room(azimuth):
        """How far the bounds reach from their middle, for a pad that way: the shorter half, or for a row the ellipse's radius there."""
        if not row:
            return min(half.x, half.y)
        return 1.0 / math.hypot(math.cos(azimuth) / half.x, math.sin(azimuth) / half.y)

    def pad(azimuth, level, radius):
        # The main lobe on the outer side, so the canopy reaches the bounds there.
        new = Pad(r, Vector(), radius, draw_lobes(r, rng, azimuth))
        # Its outer edge on the ellipse the bounds allow; its height a share of the crown's.
        out = max(0.0, 1.0 - (radius + (r.pads.reach if row else 0.0)) / room(azimuth))
        new.centre = middle + Vector((half.x * out * math.cos(azimuth), half.y * out * math.sin(azimuth), 0))
        low, high = floor + new.below(), top - new.above()
        new.centre.z = low + (high - low) * level
        return new

    start = rng.uniform(0, 2 * math.pi)
    if row:
        start = (0.0 if half.x >= half.y else math.pi / 2) + math.pi * rng.randrange(2) + rng.uniform(-0.15, 0.15)
    # The crown pad is the widest and one pad is much narrower; the others fall between, in any order.
    radii = [rng.uniform(*r.pads.largest), rng.uniform(*r.pads.smallest)] + [rng.uniform(r.pads.smallest[1], r.pads.largest[0]) for _ in range(count - 2)]
    radii[1:] = rng.sample(radii[1:], count - 1)
    # The highest pad sits over the middle; the rest go round it, low and high by turns. In a row it keeps its end.
    crown = pad(start, 1.0, radii[0])
    lean = rng.uniform(0.0, 0.35)
    if not row:
        crown.centre = Vector((middle.x + half.x * lean * math.cos(start), middle.y + half.y * lean * math.sin(start), crown.centre.z))
    pads = [crown]
    levels = [0.0, 0.5, 0.12, 0.62, 0.3]
    rng.shuffle(levels)
    for i in range(count - 1):
        azimuth = start + math.pi + 2 * math.pi * (i + rng.uniform(-0.18, 0.18)) / (count - 1)
        pads.append(pad(azimuth, levels[i] + rng.uniform(-0.05, 0.05), radii[i + 1]))

    for _ in range(400):
        moved = False
        for i, a in enumerate(pads):
            for b in pads[i + 1 :]:
                between = b.centre - a.centre
                distance = between.length
                direction = between / distance
                short = a.reach(direction) + b.reach(-direction) + r.pads.clear - distance
                if short > 1e-4:
                    # Mostly up and down: sideways there is little room inside the bounds.
                    push = Vector((direction.x * 0.5, direction.y * 0.5, direction.z if abs(direction.z) > 0.15 else 0.15)).normalized() * short * 0.5
                    a.centre -= push
                    b.centre += push
                    moved = True
        for p in pads:
            p.centre.z = min(max(p.centre.z, floor + p.below()), top - p.above())
            offset = p.centre - middle
            limit = max(0.0, 1.0 - p.radius / room(math.atan2(offset.y, offset.x)))
            share = math.hypot(offset.x / half.x, offset.y / half.y)
            if share > limit:
                scale = limit / share
                p.centre.x, p.centre.y = middle.x + offset.x * scale, middle.y + offset.y * scale
        if not moved:
            return pads
        for p in pads:
            p.radius *= 0.999
    raise RuntimeError(f"{count} pads do not fit in the bounds with {r.pads.clear} m between them")


def grow_trunk(r, tree, rng, hi, fork_z, crown):
    """The trunk and its leader. Returns the path as (points, radii) for branches to leave from."""
    sides = rng.choice(r.trunk.sides)
    breast = rng.uniform(*r.trunk.breast_radius)
    lean = rng.uniform(*r.trunk.lean)
    toward = math.atan2(crown.centre.y, crown.centre.x) + rng.uniform(-0.8, 0.8)
    fork = Vector((lean * math.cos(toward), lean * math.sin(toward), fork_z))
    bend = rng.uniform(*r.trunk.bend) * rng.choice((-1, 1))
    sideways = Vector((-math.sin(toward), math.cos(toward), 0))

    def trunk_at(z):
        share = z / fork_z
        return Vector((fork.x, fork.y, 0)) * share**1.7 + sideways * bend * math.sin(math.pi * share) + Z * z

    def radius_at(z):
        if z <= 1.3:
            return breast * (1.0 + 0.22 * (1.0 - z / 1.3) ** 2)
        return breast * (1.0 - (1.0 - r.trunk.top) * (z - 1.3) / (fork_z - 1.3))

    low, high = r.trunk.rings
    heights = [0.0, r.trunk.root_rise, low, high, (high + fork_z) / 2, fork_z]
    points = [trunk_at(z) for z in heights]
    radii = [radius_at(z) for z in heights]
    # The leader: on from the fork, turning toward the crown pad and thinning at once.
    main = crown.lobes()[0]
    end = main.centre + Z * main.up * 0.2
    control = fork + Vector((0, 0, (end.z - fork.z) * 0.55)) + (fork - Vector((0, 0, fork_z))) * 0.5
    for share in (0.3, 0.62, 1.0):
        points.append(bezier(fork, control, end, share))
        radii.append(r.trunk.tip_radius + (breast * r.trunk.top * r.trunk.leader - r.trunk.tip_radius) * (1 - share) ** 0.9)

    roots = rng.sample(range(sides), rng.choice(r.trunk.roots))
    ground = [rng.uniform(*r.trunk.root_reach) if j in roots else rng.uniform(1.1, 1.3) for j in range(sides)]
    spin = rng.uniform(0, 2 * math.pi)
    # The foot: a root's crest does not run straight from its tip to the trunk. It leaves the trunk steeply and
    # sweeps out into the ground, through rings between the ground and `root_rise` that are level, like the
    # ground's (a ring tipped with a leaning trunk would dip under the ground on its low side).
    frame = frames(points, Vector((1, 0, 0)))
    level = (Z, Vector((1, 0, 0)), Vector((0, 1, 0)))
    sweep = []
    for share, left in r.trunk.root_curve[:-1]:
        # A thin stem's foot is low: a ring too close above the last one shows nothing, and is left out.
        if not sweep or share * r.trunk.root_rise - sweep[-1][0] >= r.trunk.root_ring_gap:
            sweep.append((share * r.trunk.root_rise, left))
    foot = [trunk_at(z) for z, _ in sweep]
    reach = [[1.0 + (g - 1.0) * (0.16 + 0.84 * left) for g in ground] for _, left in list(sweep) + [(r.trunk.root_rise, 0.0)]]
    # And a root is a ridge of its own: between two corners the lowest rings come back to the trunk, close
    # beside a root where its neighbour is not one, so that ground shows between the roots.
    def beside(j):
        a, b = j in roots, (j + 1) % sides in roots
        return 0.5 if a == b else r.trunk.root_width if a else 1.0 - r.trunk.root_width

    valleys = [[beside(j) for j in range(sides)]] * min(r.trunk.root_valleys, len(sweep))
    tube(tree, foot + points[1:], [radius_at(z) for z, _ in sweep] + radii[1:], sides, strip=r.trunk.strip, spin=spin, ground=True,
         reach=reach, frame=[level] * len(sweep) + frame[1:], valleys=valleys, valley=r.trunk.root_valley, grain_from=len(sweep) + 1)
    return points, radii


def along(points, radii, share):
    """A point a share of the way along a path (by index), and the radius there."""
    at = share * (len(points) - 1)
    i = min(int(at), len(points) - 2)
    t = at - i
    return points[i].lerp(points[i + 1], t), radii[i] + (radii[i + 1] - radii[i]) * t


def equal_turns(a, c, b, count):
    """Where along a limb's curve (`bezier`) its `count` rings sit, as shares from 0 to 1: at equal turns of its direction.

    At equal steps along the curve the bends between its stretches are unequal, and the sharpest, where
    the limb turns up out of the trunk, shows from below as an elbow. The curve's direction is
    (c - a) at its start and (b - c) at its end and turns one way between, so the share at which it
    has turned a given part of the whole is found by halving.
    """
    first, last = c - a, b - c
    whole = first.angle(last, 0.0)
    if whole < 1e-6:
        return [k / (count - 1) for k in range(count)]
    shares = [0.0]
    for k in range(1, count - 1):
        low, high = 0.0, 1.0
        for _ in range(40):
            middle = (low + high) / 2
            if first.angle(first.lerp(last, middle), 0.0) < whole * k / (count - 1):
                low = middle
            else:
                high = middle
        shares.append((low + high) / 2)
    return shares + [1.0]


def grow_branches(r, tree, rng, pads, trunk):
    """A branch to every pad but the crown's, and a twig from its end into each of the pad's side lobes."""
    points, radii = trunk
    fork_index = 5
    fork_z = points[fork_index].z
    paths = []
    order = sorted(range(1, len(pads)), key=lambda i: pads[i].centre.z)
    for rank, i in enumerate(order):
        pad = pads[i]
        main = pad.lobes()[0]
        end = main.centre - Z * main.down * 0.4
        # From the trunk, a little below the fork, lower for lower pads.
        z = fork_z - r.branches.fork_spread * (1.0 - rank / max(1, len(order) - 1)) * rng.uniform(0.6, 1.0)
        share = next(k + (z - points[k].z) / (points[k + 1].z - points[k].z) for k in range(fork_index) if points[k + 1].z >= z) / (len(points) - 1)
        start, parent = along(points, radii, share)
        # Or from the middle of an earlier branch, when that is much nearer and below the pad.
        if rank >= 2:
            for other_points, other_radii in paths:
                middle, radius = along(other_points, other_radii, 0.45)
                if middle.z < end.z - 0.3 and (end - middle).length < 0.6 * (end - start).length:
                    start, parent = middle, radius
        span = end - start
        control = start + Vector((span.x, span.y, 0)) * 0.62 + Z * span.z * 0.12
        # Begin a little way out from the parent's axis, so the buried end does not come out of its far side.
        start = start + (control - start).normalized() * parent * r.branches.start
        first = parent * r.branches.radius

        def rings_at(shares):
            return [bezier(start, control, end, s) for s in shares], [r.trunk.tip_radius + (first - r.trunk.tip_radius) * (1 - s) ** 0.85 for s in shares]

        # The rings sit at equal turns of the limb's curve. A branch that leaves this one is still placed
        # on it as when the rings sat at equal steps, so no limb's path moves with its rings.
        path, widths = rings_at(equal_turns(start, control, end, r.branches.rings))
        tube(tree, path, widths, r.branches.sides, strip=r.trunk.strip, spin=rng.uniform(0, 2 * math.pi))
        paths.append(rings_at([k / (r.branches.rings - 1) for k in range(r.branches.rings)]))

    ends = {0: points[-1]}
    for rank, i in enumerate(order):
        ends[i] = paths[rank][0][-1]
    for i, pad in enumerate(pads):
        for lobe in pad.lobes()[1:]:
            tip = lobe.centre
            base = ends[i] - (tip - ends[i]).normalized() * 0.05
            tube(tree, [base, base.lerp(tip, 0.5) - Z * 0.05, tip], [r.branches.twig_radius, r.branches.twig_radius * 0.75, r.branches.twig_radius * 0.4], 3)


def leaf(r, tree, rng, pad, point, normal, axis, foot_share):
    """One piece through `point`, lying along `axis`, its front toward `normal` (the way out of its lobe)."""
    across = normal.cross(axis)
    across = (across if across.length > 1e-6 else axis.orthogonal()).normalized()
    across = Quaternion(axis, math.radians(rng.uniform(-r.leaf.roll, r.leaf.roll))) @ across
    length = rng.uniform(*r.leaf.length)
    width = length * rng.uniform(*r.leaf.width)
    mirror = rng.choice((-1, 1))
    foot = point - axis * length * foot_share
    corners = [tree.vert(foot + axis * (u * length) + across * (v * width * mirror)) for u, v in r.leaf.outline]
    face_normal = axis.cross(across) * mirror
    fan = [tuple(corners[i] for i in triangle) for triangle in r.leaf.triangles]
    if face_normal.dot(normal) < 0:
        fan = [(a, c, b) for a, b, c in fan]
    for triangle in fan:
        tree.face(triangle, LEAF, pad, tree.piece_count)
    tree.piece_out.append(normal.copy())
    tree.piece_count += 1


def grow_core(r, tree, rng, pad, lobe):
    """A closed solid inside a lobe: an apex, two rings of corners and a low point underneath."""
    # A dome: widest at its rim, just under the lobe's middle, where it closes the view up into the
    # pad from below; narrower above, where the shell of pieces lies over it.
    def at(radius, height):
        if isinstance(lobe, Bough):
            return lobe.inside(Vector((radius.x, radius.y, height * r.core.flat)) * r.core.size)
        return lobe.centre + Vector((radius.x * lobe.radius, radius.y * lobe.radius, height * (lobe.up if height >= 0 else lobe.down))) * r.core.size

    spin = rng.uniform(0, 2 * math.pi)
    rings = []
    for share, height, shift in ((0.72, 0.55, 0.0), (0.97, -0.15, 0.5)):
        ring = []
        for j in range(r.core.sides):
            angle = spin + 2 * math.pi * (j + shift) / r.core.sides
            out = share * (1 + rng.uniform(-r.core.rough, r.core.rough))
            ring.append(tree.vert(at(Vector((math.cos(angle) * out, math.sin(angle) * out, 0)), height)))
        rings.append(ring)
    top, bottom = tree.vert(at(Vector(), 0.9)), tree.vert(at(Vector(), -0.8))
    upper, lower = rings
    triangles = []
    for j in range(r.core.sides):
        k = (j + 1) % r.core.sides
        triangles += [(top, upper[j], upper[k]), (upper[j], lower[j], upper[k]), (upper[k], lower[j], lower[k]), (bottom, lower[k], lower[j])]
    for a, b, c in triangles:
        middle = (tree.verts[a] + tree.verts[b] + tree.verts[c]) / 3
        if (tree.verts[b] - tree.verts[a]).cross(tree.verts[c] - tree.verts[a]).dot(middle - lobe.centre) < 0:
            b, c = c, b
        tree.face((a, b, c), CORE_FACE, pad)
    for i in upper + lower + [top, bottom]:
        if isinstance(lobe, Bough):
            tree.core_normals[i] = lobe.out_of(lobe.unit_of(tree.verts[i]).normalized())
            continue
        offset = tree.verts[i] - lobe.centre
        vertical = lobe.up if offset.z >= 0 else lobe.down
        tree.core_normals[i] = Vector((offset.x / lobe.radius**2, offset.y / lobe.radius**2, offset.z / vertical**2)).normalized()


def grow_leaves(r, tree, rng, pads):
    """Every pad's cores, and the pieces over them: a shell on each lobe, a skirt hanging from its rim and a few pieces under it."""
    golden = math.pi * (3 - math.sqrt(5))
    for index, pad in enumerate(pads):
        lobes = pad.lobes()
        for lobe in lobes:
            grow_core(r, tree, rng, index, lobe)
        for lobe in lobes:
            others = [other for other in lobes if other is not lobe]

            def buried(point):
                return any(other.depth(point) < r.lobes.buried for other in others)

            # The shell. Area, near enough: the upper half and the part of the squashed lower half kept.
            area = 2 * math.pi * lobe.radius * (lobe.radius + lobe.up) / 2 * (1 + 0.5 * -r.lobes.open)
            total = round(area / r.leaf.spacing**2 * 2 / (1 - r.lobes.open))
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(total):
                height = 1 - (2 * k + 1) / total
                if height < r.lobes.open:
                    break
                ring = math.sqrt(1 - height * height)
                azimuth = turn + golden * k + rng.uniform(-0.12, 0.12)
                unit = Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height + rng.uniform(-0.04, 0.04))).normalized()
                point, normal = lobe.surface(unit)
                yaw, lift = rng.uniform(-r.leaf.yaw, r.leaf.yaw), rng.uniform(*r.leaf.lift)
                down = -Z - normal * normal.dot(-Z)
                if down.length < 0.25:
                    # On the crown of a lobe nothing is downhill: point any way round.
                    down = Quaternion(normal, rng.uniform(0, 2 * math.pi)) @ normal.orthogonal().normalized()
                down = Quaternion(normal, math.radians(yaw)) @ down.normalized()
                axis = (down * math.cos(math.radians(lift)) + normal * math.sin(math.radians(lift))).normalized()
                if not buried(point):
                    leaf(r, tree, rng, index, point, normal, axis, r.leaf.foot)

            def hang(point, azimuth, droop, normal):
                out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
                axis = out * math.cos(math.radians(droop)) - Z * math.sin(math.radians(droop))
                if not buried(point):
                    leaf(r, tree, rng, index, point, (normal + out * 0.5 - Z * 0.3).normalized(), axis, r.skirt.foot)

            # The skirt: round the rim, pointing out and down past the underside.
            count = max(5, round(2 * math.pi * lobe.radius / r.skirt.spacing))
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(count):
                azimuth = turn + 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / count
                height = rng.uniform(r.lobes.open - 0.25, r.lobes.open + 0.05)
                ring = math.sqrt(1 - height * height)
                point, normal = lobe.surface(Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height)))
                hang(point, azimuth + rng.uniform(-0.5, 0.5), rng.uniform(*r.skirt.droop), normal)
            # And a few under the lobe, hanging steeply.
            count = round(math.pi * (lobe.radius * 0.75) ** 2 / r.skirt.under_spacing**2)
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(count):
                share = math.sqrt((k + 0.5) / count) * 0.75
                azimuth = turn + golden * k
                point, normal = lobe.surface(Vector((share * math.cos(azimuth), share * math.sin(azimuth), -math.sqrt(1 - share * share))))
                hang(point, azimuth + rng.uniform(-0.8, 0.8), rng.uniform(*r.skirt.under_droop), normal)


def at_height(points, radii, z):
    """The leader's middle and radius at a height, between the rings of its path."""
    for (a, b), (ra, rb) in zip(zip(points, points[1:]), zip(radii, radii[1:])):
        if b.z >= z and b.z > a.z:
            t = min(max((z - a.z) / (b.z - a.z), 0.0), 1.0)
            return a.lerp(b, t), ra + (rb - ra) * t
    return points[-1].copy(), radii[-1]


def grow_tiers(r, tree, rng, lo, hi):
    """The second crown form: one leader to the tip and tiers of drooping boughs round it, with their wood. Returns the tiers, lowest first, the top last."""
    height = hi.z
    lowest = min(max(height * rng.uniform(*r.trunk.fork_height), r.tiers.lowest[0]), r.tiers.lowest[1])
    # The top first: the leader grows to it. A spire of foliage, a little to one side of the foot.
    turn, off = rng.uniform(0, 2 * math.pi), rng.uniform(*r.top.off)
    spire_radius, spire_up = rng.uniform(*r.top.spire_radius), rng.uniform(*r.top.spire_up)
    spire = Lobe(Vector((off * math.cos(turn), off * math.sin(turn), height - r.top.tip - spire_up)), spire_radius, spire_up, spire_radius * r.top.spire_down)
    points, radii = grow_trunk(r, tree, rng, hi, lowest, SimpleNamespace(centre=spire.centre, lobes=lambda: [spire]))
    top_z = spire.centre.z - r.top.drop

    # How far a bough may reach each way: the bounds are not the same on every side of the foot.
    def room(azimuth):
        x = hi.x if math.cos(azimuth) >= 0 else -lo.x
        y = hi.y if math.sin(azimuth) >= 0 else -lo.y
        return 1.0 / math.hypot(math.cos(azimuth) / x, math.sin(azimuth) / y) - r.tiers.reach

    widest = min(hi.x, -lo.x, hi.y, -lo.y) - r.tiers.reach
    count = rng.choices([c for c, _ in r.tiers.counts], [w for _, w in r.tiers.counts])[0]
    count = max(r.tiers.fewest, math.floor(count * r.tiers.count_share + 0.5))
    power, top_width = rng.uniform(*r.tiers.taper), rng.uniform(*r.top.width)
    while True:
        # Widths down the cone, each a little off it; droops; and how thick each tier's foliage is.
        widths = [(top_width + (1 - top_width) * (1 - k / count) ** power) * rng.uniform(*r.tiers.jitter) for k in range(count)]
        widths[0] *= rng.uniform(*r.tiers.first)
        widths = [min(w, 1.0) for w in widths] + [top_width]
        droops = [rng.uniform(*r.tiers.droop) for _ in range(count)] + [rng.uniform(*r.top.droop)]
        thick = [r.tiers.thin + (1 - r.tiers.thin) * w for w in widths]

        def hang(k, far):
            return droops[k] * far**r.tiers.sag / (widths[k] * widest) ** (r.tiers.sag - 1)

        # The least each tier must stand above the one below it: both tiers' foliage, clear air, and
        # whatever the upper one's tips hang lower than the lower one's surface does at that distance.
        need = []
        for k in range(count):
            above = (r.boughs.lift + r.boughs.up + r.tiers.reach) * thick[k] + r.boughs.scatter
            below = (r.boughs.down + r.skirt.drop) * thick[k + 1] + r.boughs.scatter
            reach = widths[k + 1] * widest
            need.append(above + below + r.tiers.clear + max(0.0, hang(k + 1, reach) - hang(k, reach)))
        spare = top_z - lowest - sum(need)
        if spare >= 0:
            break
        count -= 1
        if count < r.tiers.fewest:
            raise RuntimeError(f"{r.tiers.fewest} tiers do not fit between {lowest:.2f} and {top_z:.2f} m")
    # The room left over, shared out unequally: some tiers stand close and one or two apart, with the leader bare between.
    shares = [rng.random() ** r.tiers.slack for _ in range(count)]
    shares[-1] *= r.top.slack  # the top stands close over the highest tier
    heights = [lowest]
    for k in range(count):
        heights.append(heights[-1] + need[k] + spare * shares[k] / sum(shares))

    # Boughs: (tier, azimuth, length as a share of what the bounds allow that way).
    drawn = []
    for k in range(count + 1):
        if k == count:
            number = r.top.boughs
        else:
            share = (widths[k] - top_width) / (1 - top_width)
            number = max(3, round(rng.uniform(*r.boughs.count) * (r.boughs.fewer + (1 - r.boughs.fewer) * share)))
        start = rng.uniform(0, 2 * math.pi)
        lengths = [1.0, rng.uniform(r.boughs.length[0], r.boughs.short)] + [rng.uniform(*r.boughs.length) for _ in range(number - 2)]
        rng.shuffle(lengths)
        for j in range(number):
            azimuth = start + 2 * math.pi * (j + rng.uniform(-r.boughs.turn, r.boughs.turn)) / number
            drawn.append([k, azimuth, widths[k] * lengths[j]])
    # Each side of the bounds is reached by the bough that reaches furthest that way: lengths are scaled, by how
    # far a bough points to each side, so that the furthest on every side just reaches it.
    axis = [at_height(points, radii, z)[0] for z in heights]

    def reaches(k, azimuth, share):
        return axis[k] + Vector((math.cos(azimuth), math.sin(azimuth), 0)) * (share * room(azimuth) + r.tiers.reach)

    ends = [reaches(*bough) for bough in drawn]
    by = {"x+": hi.x / max(e.x for e in ends), "x-": lo.x / min(e.x for e in ends), "y+": hi.y / max(e.y for e in ends), "y-": lo.y / min(e.y for e in ends)}
    by = {side: min(max(factor, 0.6), 1.6) for side, factor in by.items()}
    for bough in drawn:
        c, s = math.cos(bough[1]), math.sin(bough[1])
        bough[2] *= by["x+" if c >= 0 else "x-"] * c * c + by["y+" if s >= 0 else "y-"] * s * s

    tiers = []
    for k in range(count + 1):
        boughs = []
        for tier, azimuth, share in drawn:
            if tier != k:
                continue
            out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
            length = share * room(azimuth)
            z = heights[k] + rng.uniform(-r.boughs.scatter, r.boughs.scatter) * thick[k]
            root, parent = at_height(points, radii, z)
            wide = max(length * rng.uniform(*r.boughs.width), r.boughs.least_width)
            bough = Bough(root + Z * r.boughs.lift * thick[k], out, length, r.boughs.inner, wide, r.boughs.up * thick[k], r.boughs.down * thick[k], droops[k], r.tiers.sag)
            boughs.append(bough)
            # Its wood: out of the leader, level at first, and down into the foliage.
            start = root + out * parent * r.boughs.start
            end = bough.at(r.boughs.wood * length - bough.middle, 0.0, -r.boughs.lift * thick[k])
            control = start + out * (end - start).dot(out) * 0.5
            first = max(parent * r.boughs.radius, r.trunk.tip_radius * 1.2)
            turns = equal_turns(start, control, end, r.boughs.rings[0 if k < 2 else 1])
            tube(tree, [bezier(start, control, end, s) for s in turns], [r.trunk.tip_radius * 0.7 + (first - r.trunk.tip_radius * 0.7) * (1 - s) ** 0.85 for s in turns],
                 r.boughs.sides[0 if k < 2 else 1], spin=rng.uniform(0, 2 * math.pi))
        tiers.append(Tier(boughs + ([spire] if k == count else [])))
    return tiers


def grow_needles(r, tree, rng, tiers):
    """Every bough's core, and the pieces over it: a shell lying along it, pointing away from the leader and down; a skirt hanging from its rim; a few under it; and the point of the top."""
    golden = math.pi * (3 - math.sqrt(5))
    for index, tier in enumerate(tiers):
        lobes = tier.lobes()
        for lobe in lobes:
            grow_core(r, tree, rng, index, lobe)
        for lobe in lobes:
            others = [other for other in lobes if other is not lobe]
            bough = isinstance(lobe, Bough)

            def buried(point):
                return any(other.depth(point) < r.lobes.buried for other in others)

            def away(point):
                """Level, away from the leader (a bough), or out of the spire."""
                flat = point - (lobe.root if bough else lobe.centre)
                flat.z = 0.0
                return flat.normalized() if flat.length > 1e-6 else Vector((1, 0, 0))

            # The shell: over the top of the bough and a little way down its sides.
            plan = math.pi * lobe.long * lobe.wide if bough else math.pi * lobe.radius * (lobe.radius + lobe.up)
            total = round(plan * 1.25 / r.leaf.spacing**2 * 2 / (1 - r.lobes.open))
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(total):
                height = 1 - (2 * k + 1) / total
                if height < r.lobes.open:
                    break
                ring = math.sqrt(1 - height * height)
                azimuth = turn + golden * k + rng.uniform(-0.12, 0.12)
                unit = Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height + rng.uniform(-0.04, 0.04))).normalized()
                point, normal = lobe.surface(unit)
                yaw, lift = rng.uniform(-r.leaf.yaw, r.leaf.yaw), rng.uniform(*r.leaf.lift)
                fall = away(point) * math.cos(math.radians(r.leaf.fall)) - Z * math.sin(math.radians(r.leaf.fall)) if bough else -Z
                down = fall - normal * normal.dot(fall)
                if down.length < 0.25:
                    down = Quaternion(normal, rng.uniform(0, 2 * math.pi)) @ normal.orthogonal().normalized()
                down = Quaternion(normal, math.radians(yaw)) @ down.normalized()
                axis = (down * math.cos(math.radians(lift)) + normal * math.sin(math.radians(lift))).normalized()
                if not buried(point):
                    leaf(r, tree, rng, index, point, normal, axis, r.leaf.foot)

            def hang(point, flat, droop, normal):
                axis = flat * math.cos(math.radians(droop)) - Z * math.sin(math.radians(droop))
                if not buried(point):
                    leaf(r, tree, rng, index, point, (normal + flat * 0.5 - Z * 0.3).normalized(), axis, r.skirt.foot)

            # The skirt: round the rim, pointing out of the bough and away from the leader, and down.
            around = 2 * math.pi * math.sqrt((lobe.long**2 + lobe.wide**2) / 2) if bough else 2 * math.pi * lobe.radius
            count = max(5, round(around / r.skirt.spacing))
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(count):
                azimuth = turn + 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / count
                height = rng.uniform(r.lobes.open - 0.25, r.lobes.open + 0.05)
                ring = math.sqrt(1 - height * height)
                point, normal = lobe.surface(Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height)))
                rim = Vector((normal.x, normal.y, 0))
                flat = (rim.normalized() * 0.6 + away(point) * r.skirt.out) if rim.length > 1e-6 else away(point)
                flat = Quaternion(Z, rng.uniform(-0.4, 0.4)) @ flat.normalized()
                hang(point, flat, rng.uniform(*r.skirt.droop), normal)
            # And a few under it, hanging steeply.
            count = round(plan * 0.6 / r.skirt.under_spacing**2)
            turn = rng.uniform(0, 2 * math.pi)
            for k in range(count):
                share = math.sqrt((k + 0.5) / count) * 0.75
                azimuth = turn + golden * k
                point, normal = lobe.surface(Vector((share * math.cos(azimuth), share * math.sin(azimuth), -math.sqrt(1 - share * share))))
                hang(point, Quaternion(Z, rng.uniform(-0.6, 0.6)) @ away(point), rng.uniform(*r.skirt.under_droop), normal)
            if not bough:
                # The point: a few pieces standing on the spire's top, nearly upright.
                turn = rng.uniform(0, 2 * math.pi)
                for k in range(r.top.tip_pieces):
                    azimuth = turn + 2 * math.pi * (k + rng.uniform(-0.2, 0.2)) / r.top.tip_pieces
                    out = Vector((math.cos(azimuth), math.sin(azimuth), 0))
                    axis = (Z + out * rng.uniform(0.08, 0.22)).normalized()
                    leaf(r, tree, rng, index, lobe.centre + Z * lobe.up, out, axis, 0.55)


def fit(tree, lo, hi):
    """Stretch every point about the foot of the trunk so the bounds are exactly lo..hi."""
    have_lo = [min(v[i] for v in tree.verts) for i in range(3)]
    have_hi = [max(v[i] for v in tree.verts) for i in range(3)]
    low = [lo[i] / have_lo[i] if i < 2 else 1.0 for i in range(3)]
    high = [hi[i] / have_hi[i] for i in range(3)]
    worst = [s for s in low + high if not MAX_STRETCH[0] <= s <= MAX_STRETCH[1]]
    if worst or abs(have_lo[2]) > 1e-6:
        raise RuntimeError(
            f"the tree drawn spans {[round(v, 2) for v in have_lo]}..{[round(v, 2) for v in have_hi]}; reaching the bounds "
            f"{tuple(lo)}..{tuple(hi)} would stretch it by {[round(s, 2) for s in low + high]}, outside {MAX_STRETCH}"
        )
    def stretch(v, by):
        for i in range(3):
            v[i] *= high[i] if by[i] > 0 else low[i]

    # A leaf piece is stretched as one thing, by the side its foot is on, so it stays flat.
    first, foot = {}, {}
    for face, piece in zip(tree.faces, tree.pieces):
        if piece >= 0:
            first.setdefault(piece, face[0])
            for i in face:
                foot[i] = first[piece]
    feet = {i: tree.verts[j].copy() for i, j in foot.items()}
    for i, v in enumerate(tree.verts):
        stretch(v, feet.get(i, v))


def separate(tree, count, gap):
    """Refuse a tree whose pads, measured as the gate measures them, are not the pads drawn."""
    # Pieces, and after them the cores (one part for each of a pad's), as the gate groups them.
    leaves = [(face, piece) for face, kind, piece in zip(tree.faces, tree.kinds, tree.pieces) if kind == LEAF]
    cores = [(face, tree.piece_count + pad) for face, kind, pad in zip(tree.faces, tree.kinds, tree.pads) if kind == CORE_FACE]
    corners = numpy.array([[tree.verts[i] for i in face] for face, _ in leaves + cores])
    owner = numpy.array([part for _, part in leaves + cores])
    found = foliage.pads_of(corners, owner, tree.piece_count + count, gap)[: tree.piece_count]
    if max(found) + 1 != count:
        raise RuntimeError(f"{count} pads were drawn but {max(found) + 1} are separated by {gap} m of clear air")


def corner_normals(r, tree):
    """One normal per face corner, in the order the mesh stores them."""
    face_normals = []
    for face in tree.faces:
        a, b, c = (tree.verts[i] for i in face[:3])
        normal = (b - a).cross(c - a)
        if len(face) == 4:
            normal += (c - a).cross(tree.verts[face[3]] - a)
        face_normals.append(normal.normalized())

    sides = [Vector() for _ in tree.verts]
    every = [Vector() for _ in tree.verts]
    for face, kind, normal in zip(tree.faces, tree.kinds, face_normals):
        for i in face:
            if kind == SIDE:
                sides[i] += normal
            if kind in (SIDE, STRIP_FACE, CONE):
                every[i] += normal

    # Bark: one normal per vertex, so no edge above the ground is lit hard. It is the blend of the
    # flat sides that meet there; where that would face away from a face it belongs to (the end
    # of a thin, bent twig), the blend of every face that meets there instead.
    around = [[] for _ in tree.verts]
    for face, kind, normal in zip(tree.faces, tree.kinds, face_normals):
        if kind in (SIDE, STRIP_FACE, CONE):
            for i in face:
                around[i].append(normal)
    bark_normals = {}
    for i, faces in enumerate(around):
        if not faces:
            continue
        lit = (sides[i] if sides[i].length > 1e-6 else every[i]).normalized()
        if min(lit.dot(normal) for normal in faces) < 0.1:
            lit = every[i].normalized()
        if min(lit.dot(normal) for normal in faces) <= 0.02:
            raise RuntimeError(f"a bark corner at {tuple(round(c, 2) for c in tree.verts[i])} is folded too sharply to light")
        bark_normals[i] = lit

    # One normal for a whole piece, so that it is lit as one flat thing.
    piece_normals = {}
    for face, pad, piece, normal in zip(tree.faces, tree.pads, tree.pieces, face_normals):
        if piece >= 0 and piece not in piece_normals:
            out = tree.piece_out[piece]
            lit = (normal * (1 - r.leaf.round) + out * r.leaf.round + Z * r.leaf.up).normalized()
            # Never round the back of its own piece: the engine would light it from behind.
            if lit.dot(normal) < 0.3:
                lit = (lit + normal * (0.3 - lit.dot(normal)) * 1.5).normalized()
            # Nor lift the front of a piece that faces the ground or stands near upright: tipped toward the sky it
            # would be lit by a sun that cannot reach it, a light piece among dark ones to an eye under the canopy.
            if normal.z < 0.3 and lit.z > normal.z:
                lit = Vector((lit.x, lit.y, normal.z)).normalized()
            piece_normals[piece] = lit

    normals = []
    for face, kind, piece, normal in zip(tree.faces, tree.kinds, tree.pieces, face_normals):
        if kind == GROUND:
            normals += [normal] * len(face)
        elif kind == LEAF:
            normals += [piece_normals[piece]] * len(face)
        elif kind == CORE_FACE:
            # Lit as one round mass; where the fit has tipped a corner's normal behind a face, the face's own.
            normals += [tree.core_normals[i] if tree.core_normals[i].dot(normal) > 0.05 else normal for i in face]
        else:
            normals += [bark_normals[i] for i in face]
    return normals


def unmet(tree, spec):
    """What the brief asks of the shape and this tree does not give with room to spare, as the gate's own failure lines.

    The measurements are the gate's (tools/validate.py), made on the lists
    before any Blender object exists, against the spec with MARGINS in place
    of its limits."""
    strict = copy.deepcopy(spec)
    for key, value in {**MARGINS, **(TIER_MARGINS if "tiers" in spec else {})}.items():
        *path, last = key.split(".")
        block = strict
        for part in path:
            block = block[part]
        block[last] = value(block[last]) if callable(value) else value
    name = spec["objects"][0]
    leaf = spec["foliage"]["material"]
    slots = [next(m for m in spec["materials"] if m != leaf), leaf]
    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in tree.verts]
    for face, kind in zip(tree.faces, tree.kinds):
        bm.faces.new([verts[i] for i in face]).material_index = 1 if kind in (LEAF, CORE_FACE) else 0
    bm.verts.index_update()
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    checks = Checks("build", name)
    conv = conventions()
    with contextlib.redirect_stdout(io.StringIO()):
        fork = check_skeleton(checks, name, bm, slots, strict, conv)
        check_foliage(checks, name, bm, slots, strict, conv, fork)
        check_canopy(checks, name, bm, slots, strict, conv)
    triangles = sum(len(face) - 2 for face in tree.faces)
    checks.check("budget.triangles", triangles <= strict["max_triangles"], f"{triangles} > {strict['max_triangles']}")
    bm.free()
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def draw(spec, strict=True, recipe=None):
    """The tree for the spec's seed, species and growth stage, as lists, fitted to the spec's bounds.

    `recipe` stands in for the species recipe the spec names (the tests' broken trees).

    A seed draws whole trees, one after another from the same generator, until
    one fills the bounds without being stretched out of shape and meets the
    brief's shape checks with room to spare (`unmet`). The gate measures the
    saved scene; this is the same measurement made early, so that a seed that
    cannot pass stops here with its reasons. If no tree does, the build fails
    and says why each was refused. `strict=False` keeps the first tree that
    fills the bounds, whatever it measures (the tests' broken trees).
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    rng = random.Random(spec["seed"])
    recipe = recipe or recipe_of(spec)
    r = grown(recipe, spec["growth_stage"])
    refused = []
    # The crown's form: pads on a forked trunk (the default), or tiers of boughs round one leader.
    tiered = hasattr(r, "crown") and r.crown.form == "tiers"
    for take in range(1, TREES + 1):
        tree = Tree()
        try:
            if tiered:
                pads = grow_tiers(r, tree, rng, lo, hi)
                grow_needles(r, tree, rng, pads)
            else:
                fork_z = max(hi.z * rng.uniform(*r.trunk.fork_height), r.branches.fork_lowest + r.branches.fork_spread)
                pads = place_pads(r, rng, lo, hi, fork_z)
                trunk = grow_trunk(r, tree, rng, hi, fork_z, pads[0])
                grow_branches(r, tree, rng, pads, trunk)
                grow_leaves(r, tree, rng, pads)
            fit(tree, lo, hi)
            separate(tree, len(pads), spec["foliage"]["pad_gap_m"])
        except RuntimeError as error:
            refused.append(f"tree {take}: {error}")
            continue
        # Measuring a tree takes several seconds, and one process may draw the same tree many times
        # (the gate draws each sibling variant; the tests draw one tree per mutation). The answer
        # for a tree already measured here, under the same spec and constants, is remembered.
        key = (json.dumps(spec, sort_keys=True), json.dumps(recipe, sort_keys=True), take)
        if strict and key not in _MEASURED:
            _MEASURED[key] = unmet(tree, spec)
        problems = _MEASURED[key] if strict else []
        if problems:
            refused.append(f"tree {take}: " + "; ".join(problems))
            continue
        triangles = [sum(len(face) - 2 for face, kind in zip(tree.faces, tree.kinds) if kind in kinds) for kinds in ((SIDE, STRIP_FACE, CONE, GROUND), (CORE_FACE,), (LEAF,))]
        print(f"tree seed {spec['seed']}: tree {take} of up to {TREES} fills the bounds{" and meets the brief with room to spare" if strict else ""}; {len(pads)} pads of half-width {[round(p.radius, 2) for p in pads]} with {[len(p.shapes) for p in pads]} lobes, "
              f"{tree.piece_count} leaf pieces; triangles: bark {triangles[0]}, core {triangles[1]}, leaf {triangles[2]}, total {sum(triangles)}")
        return tree, r
    raise RuntimeError(f"tree seed {spec['seed']}: none of its {TREES} trees fills the bounds and meets the brief with room to spare:\n  " + "\n  ".join(refused))


def flat_material(name, colour, two_sided):
    material = bpy.data.materials.new(name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(colour), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    if two_sided:
        # A leaf piece has no gloss (exported as KHR_materials_specular, specularFactor 0). With it, a flat piece
        # the sun grazes shows the sun's glare to an eye under the canopy: near-white among dark neighbours.
        bsdf.inputs["Specular IOR Level"].default_value = 0.0
    # Exported as glTF doubleSided: a leaf piece is seen, and lit, from both sides.
    material.use_backface_culling = not two_sided
    return material


def build_tree(spec, strict=True, recipe=None):
    """Build the spec's one object from its seed, species and growth stage. Bark is the first material in `materials`, leaf the foliage's."""
    tree, r = draw(spec, strict, recipe)
    name = spec["objects"][0]
    leaf = spec["foliage"]["material"]
    bark = next(m for m in spec["materials"] if m != leaf)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in tree.verts], [], tree.faces)
    mesh.materials.append(flat_material(bark, spec["materials"][bark], two_sided=False))
    mesh.materials.append(flat_material(leaf, spec["materials"][leaf], two_sided=True))
    mesh.polygons.foreach_set("material_index", [1 if kind in (LEAF, CORE_FACE) else 0 for kind in tree.kinds])
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    # Seams say where the bark may be cut to lie flat; tools/paint.py unwraps along them.
    cuts = {frozenset(pair) for pair in tree.seams}
    for edge in mesh.edges:
        edge.use_seam = frozenset(edge.vertices) in cuts
    mesh.normals_split_custom_set([tuple(n) for n in corner_normals(r, tree)])
    # Where each corner of the bark lies round and along its limb, for the grain (tools/paint.py).
    grain = mesh.attributes.new("grain", "FLOAT_VECTOR", "CORNER")
    grain.data.foreach_set("vector", [c for face, corners in zip(tree.faces, tree.grain) for corner in (corners or [(0.0, 0.0, 0.0)] * len(face)) for c in corner])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
