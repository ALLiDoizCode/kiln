"""Rubble: a handful of small broken stones lying together as they fell, each a closed piece of its own.

docs/style/rock-shapes.md, Rubble. A fragment is a shard: the space behind a few planes
(ADR 9: deliberate planes, no noise; tools/stone.py, `solid`) that touch, or cut well into, a
flattened ellipsoid: a top, an underside, four to six sides at their own angles and one or two
corners knocked off. It is tipped over, each its own way, sunk a little and cut off by the
ground. Each is softened on its own (tools/stone.py).

The group is laid out seen from above, largest first and off the middle. Each next fragment
is aimed at a spot inside the bounds and slid toward a fragment already there until it lies
against it, with its high end toward it, or a drawn gap away. The fragments never pass into
each other (source/rubble/brief.md, Decisions): they stay separate closed stones in the one
mesh, and the spec's `scatter` block says what the group must measure.

Every group is drawn eight metres wide, softened there, and shrunk to its spec's bounds, so
the kit's least sizes, a metre rock's, are left as they are.

A spec gives the seed, the bounds and how many fragments. A seed draws whole groups, one after
another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from pipeline import conventions

GROUPS = 60  # how many whole groups one seed may draw before it is given up
DRAWN_M = 8.0  # the width every group is drawn at, metres
SOFT = (0.015, 0.1)  # the least and most a soft edge eats into each plane beside it, metres at the drawn width
SHARDS = 400  # how many shards may be drawn for one fragment before the group is given up
# A shard, drawn one unit long: the half axes of the ellipsoid its planes touch (the first is 0.5).
HALF_DEPTH = (0.3, 0.42)
HALF_HEIGHT = (0.2, 0.31)
TOP_TIP = (4.0, 16.0)  # how far the top is from level before the shard is tipped, degrees
UNDER_TIP = (0.0, 12.0)
TOP_DEPTH = (0.8, 1.0)  # how far out a plane stands, as a share of the ellipsoid's reach that way: below 1 it cuts in
SIDES = ((5, 6), (4, 5), (4, 5))  # how many sides the largest fragment has, the next, and the others
SIDE_LIFT = (-16.0, 30.0)  # how far above level a side faces, degrees: below 0 it is undercut
SIDE_DEPTH = (0.76, 1.0)
SIDE_JITTER = 0.32  # how far a side's direction strays from an even spacing, as a share of that spacing
BREAKS = ((1, 2), (1, 1), (0, 1))  # corners knocked off the largest fragment, the next, and the others
BREAK_LIFT = (26.0, 62.0)
BREAK_DEPTH = (0.6, 0.82)
TILT = (8.0, 32.0)  # how far a fragment is tipped over from the way it was cut, degrees
SINK = (0.1, 0.25)  # how far it is sunk into the ground, as a share of its height
MIN_EDGE = 0.08  # the shortest edge a shard may have above the ground, as a share of its length
LARGEST_STANDS = (0.48, 0.64)  # the largest fragment's height over its length: the group's height fixes its size
STANDS_MARGIN = 1.1  # every fragment is drawn to stand this much above what the spec asks
RANGE_MARGIN, STEP_MARGIN = 1.06, 1.03  # the size order is drawn this much clearer than the spec asks
STEP_GROWTH = (1.2, 1.28)  # the size range of a group goes as these to the power of its steps, where that is more
OFF_MIDDLE = (0.5, 1.0)  # how far toward the edge of the bounds the largest fragment lies
TRIES = 40  # places tried for one fragment
LAYOUTS = 30  # layouts tried for one set of fragments
AIMS = 3  # a fragment that touches nothing is aimed at the emptiest of this many spots
UPRIGHT_CLEAR = 2.0  # a shard's sides are counted upright this many degrees sooner than the gate counts them
UPRIGHT_MARGIN = 0.7  # and it may have this share of the upright surface the spec allows the group
TRIANGLES = (1.3, 1.15)  # the largest fragment's share of the triangles, over an even share, and the next one's
OFF_UPRIGHT = (11.0, 16.0)  # a plane that would stand nearer upright than the first is leant to between the two, degrees
TOUCH = (0.2, 0.6)  # the gap between two fragments that touch, as a share of the touching distance (conventions)
APART = (0.25, 0.85)  # the gap between two that do not, as a share of the largest the spec allows
MORE_TOUCH = 0.4  # how often one more pair touches than the spec asks
HIGH_END = 0.6  # a fragment against another has its high end within this of straight toward it, radians
FILL = 0.82  # a layout must reach this share of the bounds' width and depth before it is stretched to them


def off_upright(rng, normal):
    """The normal of a plane, leant in or out when it would stand upright: nothing in a group does."""
    lift = math.degrees(math.asin(max(-1.0, min(1.0, normal.z))))
    if abs(lift) >= OFF_UPRIGHT[0]:
        return normal
    lean = rng.uniform(*OFF_UPRIGHT) * (1 if lift >= -OFF_UPRIGHT[0] / 3 else -1)
    return stone.leaning(math.atan2(normal.y, normal.x), math.radians(lean))


def shard(rng, rank):
    """One raw fragment a unit long, tipped, sunk and cut off by the ground at z = 0, with its middle
    over the origin; and the direction, seen from above, of its high end. None when its planes do not make one."""
    radii = (0.5, rng.uniform(*HALF_DEPTH), rng.uniform(*HALF_HEIGHT))

    def plane(azimuth, lift, depth):
        normal = stone.leaning(azimuth, math.radians(lift))
        return normal, math.sqrt(sum((radii[i] * normal[i]) ** 2 for i in range(3))) * rng.uniform(*depth)

    turn = rng.uniform(0, math.tau)
    sides = rng.randint(*SIDES[min(rank, 2)])
    planes = [plane(rng.uniform(0, math.tau), 90 - rng.uniform(*TOP_TIP), TOP_DEPTH), plane(rng.uniform(0, math.tau), rng.uniform(*UNDER_TIP) - 90, TOP_DEPTH)]
    planes += [plane(turn + (i + rng.uniform(-SIDE_JITTER, SIDE_JITTER)) * math.tau / sides, rng.uniform(*SIDE_LIFT), SIDE_DEPTH) for i in range(sides)]
    planes += [plane(rng.uniform(0, math.tau), rng.uniform(*BREAK_LIFT), BREAK_DEPTH) for _ in range(rng.randint(*BREAKS[min(rank, 2)]))]
    # Tipped over about a level axis: the top then faces a little to one side, and the other side is the high end.
    about = rng.uniform(0, math.tau)
    tip = Matrix.Rotation(math.radians(rng.uniform(*TILT)), 3, stone.leaning(about, 0))
    planes = [(off_upright(rng, tip @ normal), offset) for normal, offset in planes]
    high_end = -(tip @ stone.Z).to_2d()
    sink = rng.uniform(*SINK)
    whole = stone.solid(planes)
    if whole is None:
        return None
    low, high = min(v.co.z for v in whole.verts), max(v.co.z for v in whole.verts)
    whole.free()
    lift = -(low + sink * (high - low))
    lifted = [(normal, offset + normal.z * lift) for normal, offset in planes]
    # The ground cuts the underside away, or leaves part of it as an undercut face.
    bm = stone.solid(lifted + [(-stone.Z, 0.0)]) or stone.solid(lifted[:1] + lifted[2:] + [(-stone.Z, 0.0)])
    if bm is None:
        return None
    length = max((a.co - b.co).length for a in bm.verts for b in bm.verts)
    middle = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    for vert in bm.verts:
        vert.co = Vector(((vert.co.x - middle.x) / length, (vert.co.y - middle.y) / length, vert.co.z / length))
    bm.normal_update()
    if stone.shortest_edge(bm, 0.0) < MIN_EDGE:
        bm.free()
        return None
    return bm, high_end.normalized()


class Placed:
    """A raw fragment at its size, turned and put down: what the next one is slid against."""

    def __init__(self, bm, size, turn, at):
        place = Matrix.Translation(Vector((at.x, at.y, 0.0))) @ Matrix.Rotation(turn, 4, "Z") @ Matrix.Scale(size, 4)
        self.at = at
        self.verts = [place @ v.co for v in bm.verts]
        self.faces = [[v.index for v in face.verts] for face in bm.faces]
        self.points = self.verts + [(place @ ((e.verts[0].co + e.verts[1].co) / 2)) for e in bm.edges] + [place @ f.calc_center_median() for f in bm.faces]
        self.tree = BVHTree.FromPolygons(self.verts, self.faces)
        self.matrix = place
        self.reach = max((v - Vector((at.x, at.y, v.z))).length for v in self.verts)
        self.lo = [min(v[i] for v in self.verts) for i in range(2)]
        self.hi = [max(v[i] for v in self.verts) for i in range(2)]

    def gap(self, other):
        """The least distance between the two, or -1 when they pass into each other."""
        if self.tree.overlap(other.tree):
            return -1.0
        return min(min(b.tree.find_nearest(point)[3] for point in a.points) for a, b in ((self, other), (other, self)))


def lengths(rng, count, want):
    """The fragments' lengths, the largest first as 1: a size order clearer than the spec asks."""
    least = max(RANGE_MARGIN * want["min_size_range"], STEP_GROWTH[0] ** (count - 1))
    whole = rng.uniform(least, max(least + 0.3, STEP_GROWTH[1] ** (count - 1)))
    while True:
        weights = [rng.uniform(0.6, 1.4) for _ in range(count - 1)]
        steps = [whole ** (weight / sum(weights)) for weight in weights]
        if min(steps) >= STEP_MARGIN * want["min_step_ratio"]:
            break
    found = [1.0]
    for step in steps:
        found.append(found[-1] / step)
    return found


def layout(rng, shards, sizes, touching, lo, hi, touch_m, gap_m):
    """The fragments put down in the bounds lo..hi, largest first, or None when this layout does not fill them."""
    half = (hi - lo) / 2
    middle = (lo + hi) / 2
    placed = []
    for index, ((bm, high_end), size) in enumerate(zip(shards, sizes)):
        for _ in range(TRIES):
            turn = rng.uniform(0, math.tau)
            if not placed:
                way = rng.uniform(0, math.tau)
                trial = Placed(bm, size, turn, Vector((0.0, 0.0)))
                room = [half[i] - (trial.hi[i] - trial.lo[i]) / 2 for i in range(2)]
                at = Vector((middle.x + room[0] * math.cos(way) * rng.uniform(*OFF_MIDDLE), middle.y + room[1] * math.sin(way) * rng.uniform(*OFF_MIDDLE)))
                at -= Vector(((trial.lo[0] + trial.hi[0]) / 2, (trial.lo[1] + trial.hi[1]) / 2))
                mine = Placed(bm, size, turn, at)
            else:
                aims = [Vector((rng.uniform(lo.x, hi.x), rng.uniform(lo.y, hi.y))) for _ in range(AIMS)]
                aim = aims[0] if index in touching else max(aims, key=lambda spot: min((other.at - spot).length for other in placed))
                against = rng.choice(placed) if index in touching else min(placed, key=lambda other: (other.at - aim).length)
                way = aim - against.at
                if way.length < 1e-6:
                    continue
                way.normalize()
                if index in touching:
                    # Its high end toward the fragment it lies against.
                    turn = math.atan2(-way.y, -way.x) - math.atan2(high_end.y, high_end.x) + rng.uniform(-HIGH_END, HIGH_END)
                    gap = touch_m * rng.uniform(*TOUCH)
                else:
                    gap = gap_m * rng.uniform(*APART)
                near, far = 0.0, against.reach + size + gap
                for _ in range(16):
                    reach = (near + far) / 2
                    if Placed(bm, size, turn, against.at + way * reach).gap(against) < gap:
                        near = reach
                    else:
                        far = reach
                mine = Placed(bm, size, turn, against.at + way * far)
                if any(mine.gap(other) < touch_m * TOUCH[0] for other in placed):
                    continue
            if all(lo[i] <= mine.lo[i] and mine.hi[i] <= hi[i] for i in range(2)):
                placed.append(mine)
                break
        else:
            return None
    reached = [(max(p.hi[i] for p in placed) - min(p.lo[i] for p in placed)) / (hi[i] - lo[i]) for i in range(2)]
    return placed if min(reached) >= FILL else None


def softened(bm, size):
    """How many triangles the shard has once it is softened at this size, or None when it cannot be:
    an edge too short, a plane the soft edges would eat, or a soft edge lit from behind."""
    trial = bm.copy()
    for vert in trial.verts:
        vert.co *= size
    trial.normal_update()
    width = min(SOFT[1], stone.shortest_edge(trial, 0.0) / stone.SOFT_EDGES_PER_EDGE)
    triangles = None
    if width >= SOFT[0] and stone.unsoftenable(trial, width, 0.0) is None:
        tag = stone.soften(trial, width, 0.0)
        if tag is not None and not stone.plane_normals(trial, tag, 0.0)[1]:
            triangles = sum(len(face.verts) - 2 for face in trial.faces)
    trial.free()
    return triangles


def upright_share(bm, conv):
    """How much of the shard's side surface is upright, as the gate's `lean` measures it."""
    rules = conv["lean"]
    sides = [f for f in bm.faces if abs(f.normal.z) < rules["side_normal_z"]]
    upright = sum(f.calc_area() for f in sides if abs(f.normal.z) < math.sin(math.radians(rules["upright_deg"] + UPRIGHT_CLEAR)))
    return upright / sum(f.calc_area() for f in sides) if sides else 0.0


def draw(rng, spec, conv, lo, hi, touch_m, gap_m):
    """The raw fragments of one group in the bounds lo..hi, largest first, or a string saying why there is none."""
    want = spec["scatter"]
    count = rng.randint(want["min_count"], want["max_count"])
    sizes = [1.0] + lengths(rng, count, want)[1:]
    # The largest fragment has a larger share of the triangles than the others.
    budget = spec["max_triangles"] / count
    shards = []
    for index in range(count):
        for _ in range(SHARDS):
            found = shard(rng, index)
            if found is None:
                continue
            stands = max(v.co.z for v in found[0].verts)
            if index == 0:
                # The largest fragment is as tall as the bounds; the others follow from it.
                largest = (hi.z - lo.z) / stands
                ok = LARGEST_STANDS[0] <= stands <= LARGEST_STANDS[1]
                most = budget * TRIANGLES[0]
            else:
                ok = stands >= STANDS_MARGIN * want["min_stand_share"]
                most = budget * (TRIANGLES[1] if index == 1 else (count - sum(TRIANGLES)) / (count - 2))
            if ok and upright_share(found[0], conv) <= spec["lean"]["max_upright_share"] * UPRIGHT_MARGIN:
                triangles = softened(found[0], largest * sizes[index])
                if triangles is not None and triangles <= most:
                    break
            found[0].free()
        else:
            for bm, _ in shards:
                bm.free()
            return f"no shard of {SHARDS} for fragment {index + 1} that can be softened, leans and is within its triangles"
        shards.append(found)
    sizes = [largest * size for size in sizes]
    touching = set(rng.sample(range(1, count), min(count - 1, want["min_touching"] + (rng.random() < MORE_TOUCH))))
    for _ in range(LAYOUTS):
        placed = layout(rng, shards, sizes, touching, lo, hi, touch_m, gap_m)
        if placed is not None:
            break
    else:
        for made, _ in shards:
            made.free()
        return f"no layout of {LAYOUTS} that puts every fragment in the bounds and reaches {FILL} of their width and depth"
    pieces = []
    for (bm, _), mine in zip(shards, placed):
        bm.transform(mine.matrix)
        bm.normal_update()
        pieces.append(bm)
    return pieces


def shape(spec, strict=True):
    """The softened fragments of the group for the spec's seed, and their corner normals.

    With `strict` off the first group that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    shrink = (hi.x - lo.x) / DRAWN_M
    drawn = {**spec, "bounds_m": {"min": list(lo / shrink), "max": list(hi / shrink)}}
    extra = (("scatter", validate.check_scatter),)
    touch_m = conv["scatter"]["touch_m"] / shrink
    refused = []
    for take in range(1, GROUPS + 1):
        pieces = draw(rng, spec, conv, lo / shrink, hi / shrink, touch_m, spec["scatter"]["max_gap_m"] / shrink)
        if isinstance(pieces, str):
            refused.append(f"group {take}: {pieces}")
            continue
        done = stone.finish(pieces, drawn, SOFT)
        problems = [done] if isinstance(done, str) else []
        if not problems:
            for bm in pieces:
                for vert in bm.verts:
                    vert.co *= shrink
                bm.normal_update()
            problems = stone.unmet(name, pieces, spec, conv, extra) if strict else []
        if not problems:
            print(f"{name} seed {spec['seed']}: group {take} of up to {GROUPS} meets the spec")
            return pieces, done[1]
        refused.append(f"group {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its groups meets the spec:\n  " + "\n  ".join(refused))


def build_rubble(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    # No seams are marked: a fragment is a lump with undercut sides, and laid flat as one dome, as a
    # pebble's plate is, its sides fold over each other. tools/paint.py unwraps it by angle.
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
