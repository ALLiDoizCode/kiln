"""Broadleaf tree generator: one seed, one tree (source/tree/brief.md).

Shared by the variants' build scripts (source/tree_1, tree_2, tree_3), which
each call `build_tree(spec)`. Everything is drawn from `random.Random(seed)`,
in a fixed order, and built as plain lists of vertices and faces, so the same
seed gives the same mesh.

1. Pads: three to six flattened ellipsoids, placed round and above the trunk
   inside the spec's bounds, at staggered heights, and pushed apart until
   clear air separates every pair.
2. Trunk: a tube of flat sides with a narrow strip along every corner (the
   soft edge), leaning and bending a little, tapering, its corners pulled out
   into a few roots at the ground. It carries on past the fork as the leader,
   into the highest pad.
3. Branches: one tapering tube per remaining pad, leaving the trunk near the
   fork (or the middle of an earlier branch, when that is much nearer),
   running out first and then up, and ending inside its pad in a few twigs.
4. Leaves: on each pad's surface, flat pointed pieces with a notch on either
   side, overlapping like shingles: lying near the surface, pointing down it
   and lifted outward. A pad is a shell, open underneath, so the branch that
   carries it shows from below.
5. Fit: the whole tree is stretched, about the foot of the trunk, to the
   spec's bounds.

Normals are set by hand. Bark: each flat side is lit flat across and smooth
along its length, and the strips blend from one side to the next. Leaves:
every corner of a piece carries one normal, part the piece's own and part the
direction out of its pad and upward, so a pad is lit as a round mass and each
piece still catches the light at its own angle.

Each material gets one flat colour; tools/paint.py paints the bark and gives
each leaf piece its colour (ADR 10, ADR 11).
"""

import math
import random

import bpy
import foliage
import numpy
from mathutils import Quaternion, Vector
from pipeline import linear_rgb

Z = Vector((0, 0, 1))

# Trunk, in metres unless a share is named.
TRUNK_SIDES = (6, 7)  # flat sides, drawn per tree
STRIP = 0.2  # the soft-edge strip at a corner, as a share of the angle between corners
BREAST_RADIUS = (0.19, 0.24)  # at 1.3 m
FORK_HEIGHT = (0.37, 0.45)  # share of the tree's height at which the lowest branch leaves
TRUNK_TOP = 0.7  # radius below the fork over the radius at 1.3 m
LEAN = (0.3, 0.55)  # how far the fork stands to one side of the foot
BEND = (0.07, 0.14)  # how far the trunk bows out of the straight line from foot to fork
ROOTS = (3, 4)  # corners pulled out into roots
ROOT_REACH = (2.3, 3.0)  # a root's tip from the trunk's axis, over the radius there
ROOT_RISE = 0.34  # height at which a root has all but joined the trunk
LEADER = 0.72  # radius of the leader just above the fork, over the trunk's just below
TIP_RADIUS = 0.035

# Branches.
BRANCH_SIDES = 5
BRANCH_RADIUS = 0.62  # a branch's radius where it leaves, over its parent's there
BRANCH_RINGS = 5
BRANCH_START = 0.45  # how far from its parent's axis a branch begins, over the parent's radius there
FORK_SPREAD = 0.55  # branches leave the trunk within this far below the fork
TWIGS = 3  # per pad
TWIG_RADIUS = 0.028

# Pads: (count, how often) drawn per tree.
PAD_COUNTS = ((4, 0.45), (5, 0.4), (3, 0.15))
PAD_RADIUS = (1.0, 1.6)  # horizontal, before the fit
PAD_LUMPS = 3  # swellings on each pad
PAD_LUMP = (0.08, 0.22)  # how far one stands out, as a share of the radius
PAD_FLAT = (0.7, 0.85)  # vertical radius over horizontal
PAD_UNDER = 0.7  # how far the shell hangs below the pad's middle, over its vertical radius
PAD_CLEAR = 0.3  # clear air between two pads' surfaces before the fit
PAD_OPEN = -0.7  # the shell stops here (unit sphere height): open underneath

# Leaves.
LEAF_SPACING = 0.24  # between neighbouring pieces on a pad's surface
LEAF_LENGTH = (0.55, 0.75)
LEAF_WIDTH = (0.48, 0.56)  # over the length
LEAF_LIFT = (14.0, 46.0)  # degrees a piece is raised off the surface
LEAF_YAW = 38.0  # degrees it may swing either side of straight down the surface
LEAF_ROLL = 22.0  # and tip about its own length
LEAF_FOOT = 0.8  # how much of a piece's length lies behind the point where it crosses the pad's surface
LEAF_ROUND = 0.4  # share of a piece's normal taken from the direction out of its pad
LEAF_UP = 0.3  # and how far every piece's normal is tipped toward the sky

MAX_STRETCH = (0.85, 1.2)  # the fit may not change any dimension by more
TREES = 40  # how many whole trees one seed may draw before it is given up

SIDE, STRIP_FACE, CONE, GROUND, LEAF = range(5)


class Tree:
    """The mesh as lists, in the order they are made."""

    def __init__(self):
        self.verts = []
        self.faces = []
        self.kinds = []
        self.pads = []  # leaf faces only: which pad (index) each belongs to; -1 for bark
        self.pieces = []  # and which piece; -1 for bark
        self.piece_count = 0
        self.seams = []  # pairs of vertices: bark edges along which the surface is cut open to be painted

    def vert(self, co):
        self.verts.append(Vector(co))
        return len(self.verts) - 1

    def face(self, corners, kind, pad=-1, piece=-1):
        self.faces.append(tuple(corners))
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


def tube(tree, points, radii, sides, strip=0.0, spin=0.0, ground=False, reach=None):
    """A closed tapering tube along `points`.

    With `strip` each corner is two vertices, with a narrow face between them.
    `reach[ring][corner]` scales a corner's distance from the axis (roots).
    `ground` makes the first ring level at its own height with a flat cap
    under it; otherwise both ends close to a point.
    """
    rings = []
    frame = frames(points, Vector((1, 0, 0)) if ground else None)
    per = 2 if strip else 1
    for k, (point, radius) in enumerate(zip(points, radii)):
        tangent, across, along = frame[k]
        if ground and k == 0:
            across, along = Vector((1, 0, 0)), Vector((0, 1, 0))
        ring = []
        for j in range(sides):
            scale = reach[k][j] if reach and k < len(reach) else 1.0
            # A root is a fin: its two corner vertices stay close together however far it reaches.
            half = strip * math.pi / sides / (scale if scale > 1.2 else 1.0)
            for step in range(per):
                angle = spin + 2 * math.pi * j / sides + (half * (2 * step - 1) if strip else 0.0)
                ring.append(tree.vert(point + (across * math.cos(angle) + along * math.sin(angle)) * radius * scale))
        rings.append(ring)
    count = sides * per
    for lower, upper in zip(rings, rings[1:]):
        for i in range(count):
            j = (i + 1) % count
            kind = STRIP_FACE if strip and i % 2 == 0 else SIDE
            tree.face((lower[i], lower[j], upper[j], upper[i]), kind)
        # Each stretch between two rings is cut once along its length, to unroll flat.
        tree.seams.append((lower[0], upper[0]))
    # And every ring is a cut, so no painted island is longer than one stretch of a limb.
    for ring in rings:
        tree.seams += [(ring[i], ring[(i + 1) % count]) for i in range(count)]
    start, end = points[0], points[-1]
    if ground:
        centre = tree.vert(start)
        for i in range(count):
            tree.face((centre, rings[0][(i + 1) % count], rings[0][i]), GROUND)
    else:
        apex = tree.vert(start - frame[0][0] * radii[0] * 0.35)
        for i in range(count):
            tree.face((apex, rings[0][(i + 1) % count], rings[0][i]), CONE)
        tree.seams.append((rings[0][0], apex))
    apex = tree.vert(end + frame[-1][0] * radii[-1] * 2.0)
    for i in range(count):
        tree.face((rings[-1][i], rings[-1][(i + 1) % count], apex), CONE)
    tree.seams.append((rings[-1][0], apex))


def bezier(a, c, b, t):
    return a * (1 - t) ** 2 + c * (2 * t * (1 - t)) + b * t**2


class Pad:
    def __init__(self, centre, radius, flat, lumps):
        self.centre = centre
        self.radius = radius  # horizontal
        self.flat = flat
        self.lumps = lumps  # (unit direction, height as a share of the radius): swellings on the surface

    def swell(self, unit):
        """How far the surface stands off the plain ellipsoid toward `unit`, as a factor."""
        return 1.0 + sum(height * max(0.0, unit.dot(direction)) ** 3 for direction, height in self.lumps)

    def reach(self, direction):
        """Distance from the centre to the surface along a unit direction."""
        vertical = self.radius * self.flat * (PAD_UNDER if direction.z < 0 else 1.0)
        return (1.0 + PAD_LUMP[1]) / math.sqrt((direction.x**2 + direction.y**2) / self.radius**2 + direction.z**2 / vertical**2)

    def surface(self, unit):
        """The surface point and outward normal for a point on the unit sphere."""
        vertical = self.radius * self.flat * (PAD_UNDER if unit.z < 0 else 1.0)
        point = self.centre + Vector((unit.x * self.radius, unit.y * self.radius, unit.z * vertical)) * self.swell(unit)
        normal = Vector((unit.x / self.radius, unit.y / self.radius, unit.z / vertical)).normalized()
        return point, normal


def place_pads(rng, lo, hi, fork_z):
    """Pads inside the bounds, staggered in height, with clear air between every pair."""
    count = rng.choices([c for c, _ in PAD_COUNTS], [w for _, w in PAD_COUNTS])[0]
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0))
    half = Vector(((hi.x - lo.x) / 2, (hi.y - lo.y) / 2, 0))
    floor, top = fork_z + 0.25, hi.z

    def pad(azimuth, level, radius):
        flat = rng.uniform(*PAD_FLAT)
        # Its outer edge on the ellipse the bounds allow; its height a share of the crown's.
        out = max(0.0, 1.0 - radius / min(half.x, half.y))
        centre = middle + Vector((half.x * out * math.cos(azimuth), half.y * out * math.sin(azimuth), 0))
        low, high = floor + radius * flat * PAD_UNDER, top - radius * flat
        centre.z = low + (high - low) * level
        lumps = []
        for _ in range(PAD_LUMPS):
            turn, rise = rng.uniform(0, 2 * math.pi), rng.uniform(-0.2, 0.9)
            lumps.append((Vector((math.cos(turn) * math.cos(rise), math.sin(turn) * math.cos(rise), math.sin(rise))), rng.uniform(*PAD_LUMP)))
        return Pad(centre, radius, flat, lumps)

    start = rng.uniform(0, 2 * math.pi)
    # The crown pad is the largest; the others run down from it.
    radii = sorted((rng.uniform(*PAD_RADIUS) for _ in range(count)), reverse=True)
    radii[1:] = rng.sample(radii[1:], count - 1)
    # The highest pad sits over the middle; the rest go round it, low and high by turns.
    crown = pad(0.0, 1.0, radii[0])
    lean = rng.uniform(0.0, 0.35)
    crown.centre += Vector((half.x * lean * math.cos(start), half.y * lean * math.sin(start), 0))
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
                short = a.reach(direction) + b.reach(-direction) + PAD_CLEAR - distance
                if short > 1e-4:
                    # Mostly up and down: sideways there is little room inside the bounds.
                    push = Vector((direction.x * 0.5, direction.y * 0.5, direction.z if abs(direction.z) > 0.15 else 0.15)).normalized() * short * 0.5
                    a.centre -= push
                    b.centre += push
                    moved = True
        for p in pads:
            vertical = p.radius * p.flat
            p.centre.z = min(max(p.centre.z, floor + vertical * PAD_UNDER), top - vertical)
            offset = p.centre - middle
            limit = max(0.0, 1.0 - p.radius / min(half.x, half.y))
            share = math.hypot(offset.x / half.x, offset.y / half.y)
            if share > limit:
                scale = limit / share
                p.centre.x, p.centre.y = middle.x + offset.x * scale, middle.y + offset.y * scale
        if not moved:
            return pads
        for p in pads:
            p.radius *= 0.999
    raise RuntimeError(f"{count} pads do not fit in the bounds with {PAD_CLEAR} m between them")


def grow_trunk(tree, rng, hi, fork_z, crown):
    """The trunk and its leader. Returns the path as (points, radii) for branches to leave from."""
    sides = rng.choice(TRUNK_SIDES)
    breast = rng.uniform(*BREAST_RADIUS)
    lean = rng.uniform(*LEAN)
    toward = math.atan2(crown.centre.y, crown.centre.x) + rng.uniform(-0.8, 0.8)
    fork = Vector((lean * math.cos(toward), lean * math.sin(toward), fork_z))
    bend = rng.uniform(*BEND) * rng.choice((-1, 1))
    sideways = Vector((-math.sin(toward), math.cos(toward), 0))

    def trunk_at(z):
        share = z / fork_z
        return Vector((fork.x, fork.y, 0)) * share**1.7 + sideways * bend * math.sin(math.pi * share) + Z * z

    def radius_at(z):
        if z <= 1.3:
            return breast * (1.0 + 0.22 * (1.0 - z / 1.3) ** 2)
        return breast * (1.0 - (1.0 - TRUNK_TOP) * (z - 1.3) / (fork_z - 1.3))

    heights = [0.0, ROOT_RISE, 0.85, 1.6, (1.6 + fork_z) / 2, fork_z]
    points = [trunk_at(z) for z in heights]
    radii = [radius_at(z) for z in heights]
    # The leader: on from the fork, turning toward the crown pad and thinning at once.
    end = crown.centre + Vector((0, 0, crown.radius * crown.flat * 0.25))
    control = fork + Vector((0, 0, (end.z - fork.z) * 0.55)) + (fork - Vector((0, 0, fork_z))) * 0.5
    for share in (0.3, 0.62, 1.0):
        points.append(bezier(fork, control, end, share))
        radii.append(TIP_RADIUS + (breast * TRUNK_TOP * LEADER - TIP_RADIUS) * (1 - share) ** 0.9)

    roots = rng.sample(range(sides), rng.choice(ROOTS))
    ground = [rng.uniform(*ROOT_REACH) if j in roots else rng.uniform(1.1, 1.3) for j in range(sides)]
    rise = [1.0 + (g - 1.0) * 0.16 for g in ground]
    tube(tree, points, radii, sides, strip=STRIP, spin=rng.uniform(0, 2 * math.pi), ground=True, reach=[ground, rise])
    return points, radii


def along(points, radii, share):
    """A point a share of the way along a path (by index), and the radius there."""
    at = share * (len(points) - 1)
    i = min(int(at), len(points) - 2)
    t = at - i
    return points[i].lerp(points[i + 1], t), radii[i] + (radii[i + 1] - radii[i]) * t


def grow_branches(tree, rng, pads, trunk):
    """A branch to every pad but the crown's, and twigs inside every pad."""
    points, radii = trunk
    fork_index = 5
    fork_z = points[fork_index].z
    paths = []
    order = sorted(range(1, len(pads)), key=lambda i: pads[i].centre.z)
    for rank, i in enumerate(order):
        pad = pads[i]
        end = pad.centre - Vector((0, 0, pad.radius * pad.flat * PAD_UNDER * 0.3))
        # From the trunk, a little below the fork, lower for lower pads.
        z = fork_z - FORK_SPREAD * (1.0 - rank / max(1, len(order) - 1)) * rng.uniform(0.6, 1.0)
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
        start = start + (control - start).normalized() * parent * BRANCH_START
        shares = [k / (BRANCH_RINGS - 1) for k in range(BRANCH_RINGS)]
        path = [bezier(start, control, end, s) for s in shares]
        first = parent * BRANCH_RADIUS
        widths = [TIP_RADIUS + (first - TIP_RADIUS) * (1 - s) ** 0.85 for s in shares]
        tube(tree, path, widths, BRANCH_SIDES, strip=STRIP, spin=rng.uniform(0, 2 * math.pi))
        paths.append((path, widths))

    ends = {0: points[-1]}
    for rank, i in enumerate(order):
        ends[i] = paths[rank][0][-1]
    for i, pad in enumerate(pads):
        turn = rng.uniform(0, 2 * math.pi)
        for k in range(TWIGS):
            azimuth = turn + 2 * math.pi * k / TWIGS + rng.uniform(-0.4, 0.4)
            rise = rng.uniform(0.25, 0.7)
            unit = Vector((math.cos(azimuth) * math.cos(rise), math.sin(azimuth) * math.cos(rise), math.sin(rise)))
            tip, _ = pad.surface(unit)
            tip = pad.centre + (tip - pad.centre) * 0.72
            base = ends[i] - (tip - ends[i]).normalized() * 0.05
            tube(tree, [base, base.lerp(tip, 0.5) + Z * 0.06, tip], [TWIG_RADIUS, TWIG_RADIUS * 0.7, TWIG_RADIUS * 0.3], 3)


# One piece, as (along its length, across it), both as shares of the length and the width: the
# foot, a shoulder, a notch and a tooth up one side, the tip, and a shoulder on the other side.
# Half the pieces are mirrored. Four triangles fill it.
LEAF_OUTLINE = [(0.0, 0.0), (0.28, -0.5), (0.47, -0.24), (0.6, -0.38), (1.0, 0.0), (0.38, 0.5)]
LEAF_TRIANGLES = [(0, 1, 2), (2, 3, 4), (0, 2, 4), (0, 4, 5)]


def grow_leaves(tree, rng, pads):
    golden = math.pi * (3 - math.sqrt(5))
    for index, pad in enumerate(pads):
        vertical = pad.radius * pad.flat
        # Area of the shell, near enough: the upper half and the part of the squashed lower half kept.
        area = 2 * math.pi * pad.radius * (pad.radius + vertical) / 2 * (1 + 0.5 * -PAD_OPEN)
        count = round(area / LEAF_SPACING**2)
        total = round(count * 2 / (1 - PAD_OPEN))
        turn = rng.uniform(0, 2 * math.pi)
        for k in range(total):
            height = 1 - (2 * k + 1) / total
            if height < PAD_OPEN:
                break
            ring = math.sqrt(1 - height * height)
            azimuth = turn + golden * k + rng.uniform(-0.12, 0.12)
            unit = Vector((ring * math.cos(azimuth), ring * math.sin(azimuth), height + rng.uniform(-0.04, 0.04))).normalized()
            point, normal = pad.surface(unit)
            down = -Z - normal * normal.dot(-Z)
            if down.length < 0.25:
                # On the crown of a pad nothing is downhill: point any way round.
                spin = rng.uniform(0, 2 * math.pi)
                down = normal.orthogonal().normalized()
                down = Quaternion(normal, spin) @ down
            down.normalize()
            down = Quaternion(normal, math.radians(rng.uniform(-LEAF_YAW, LEAF_YAW))) @ down
            lift = math.radians(rng.uniform(*LEAF_LIFT))
            length_axis = (down * math.cos(lift) + normal * math.sin(lift)).normalized()
            across = normal.cross(length_axis).normalized()
            across = Quaternion(length_axis, math.radians(rng.uniform(-LEAF_ROLL, LEAF_ROLL))) @ across
            length = rng.uniform(*LEAF_LENGTH)
            width = length * rng.uniform(*LEAF_WIDTH)
            mirror = rng.choice((-1, 1))
            foot = point - length_axis * length * LEAF_FOOT
            corners = [tree.vert(foot + length_axis * (u * length) + across * (v * width * mirror)) for u, v in LEAF_OUTLINE]
            # Front toward the outside of the pad.
            face_normal = length_axis.cross(across) * mirror
            fan = [tuple(corners[i] for i in triangle) for triangle in LEAF_TRIANGLES]
            if face_normal.dot(normal) < 0:
                fan = [(a, c, b) for a, b, c in fan]
            for triangle in fan:
                tree.face(triangle, LEAF, index, tree.piece_count)
            tree.piece_count += 1


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
    corners = numpy.array([[tree.verts[i] for i in face] for face, kind in zip(tree.faces, tree.kinds) if kind == LEAF])
    owner = numpy.array([piece for piece in tree.pieces if piece >= 0])
    found = foliage.pads_of(corners, owner, tree.piece_count, gap)
    if max(found) + 1 != count:
        raise RuntimeError(f"{count} pads were drawn but {max(found) + 1} are separated by {gap} m of clear air")


def corner_normals(tree):
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

    # Each pad's middle, from its own pieces, to tell which way is out.
    middles = {}
    for face, pad in zip(tree.faces, tree.pads):
        if pad >= 0:
            total, n = middles.get(pad, (Vector(), 0))
            middles[pad] = (total + sum((tree.verts[i] for i in face), Vector()), n + len(face))
    middles = {pad: total / n for pad, (total, n) in middles.items()}

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
            out = (tree.verts[face[0]] - middles[pad]).normalized()
            lit = (normal * (1 - LEAF_ROUND) + out * LEAF_ROUND + Z * LEAF_UP).normalized()
            # Never round the back of its own piece: the engine would light it from behind.
            if lit.dot(normal) < 0.3:
                lit = (lit + normal * (0.3 - lit.dot(normal)) * 1.5).normalized()
            piece_normals[piece] = lit

    normals = []
    for face, kind, piece, normal in zip(tree.faces, tree.kinds, tree.pieces, face_normals):
        if kind == GROUND:
            normals += [normal] * len(face)
        elif kind == LEAF:
            normals += [piece_normals[piece]] * len(face)
        else:
            normals += [bark_normals[i] for i in face]
    return normals


def draw(spec):
    """The tree for the spec's seed, as lists, fitted to the spec's bounds.

    A seed draws whole trees, one after another from the same generator, until
    one fills the bounds without being stretched out of shape. If none does,
    the build fails and says why.
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    rng = random.Random(spec["seed"])
    refused = []
    for take in range(1, TREES + 1):
        tree = Tree()
        fork_z = hi.z * rng.uniform(*FORK_HEIGHT)
        try:
            pads = place_pads(rng, lo, hi, fork_z)
            trunk = grow_trunk(tree, rng, hi, fork_z, pads[0])
            grow_branches(tree, rng, pads, trunk)
            grow_leaves(tree, rng, pads)
            fit(tree, lo, hi)
            separate(tree, len(pads), spec["foliage"]["pad_gap_m"])
        except RuntimeError as error:
            refused.append(f"tree {take}: {error}")
            continue
        print(f"tree seed {spec['seed']}: tree {take} of up to {TREES} fills the bounds; {len(pads)} pads of radius {[round(p.radius, 2) for p in pads]}, {tree.piece_count} leaf pieces")
        return tree
    raise RuntimeError(f"tree seed {spec['seed']}: none of its {TREES} trees fits the bounds:\n  " + "\n  ".join(refused))


def flat_material(name, colour, two_sided):
    material = bpy.data.materials.new(name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(colour), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    # Exported as glTF doubleSided: a leaf piece is seen, and lit, from both sides.
    material.use_backface_culling = not two_sided
    return material


def build_tree(spec):
    """Build the spec's one object from its seed. Bark is the first material in `materials`, leaf the foliage's."""
    tree = draw(spec)
    name = spec["objects"][0]
    leaf = spec["foliage"]["material"]
    bark = next(m for m in spec["materials"] if m != leaf)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in tree.verts], [], tree.faces)
    mesh.materials.append(flat_material(bark, spec["materials"][bark], two_sided=False))
    mesh.materials.append(flat_material(leaf, spec["materials"][leaf], two_sided=True))
    mesh.polygons.foreach_set("material_index", [1 if kind == LEAF else 0 for kind in tree.kinds])
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    # Seams say where the bark may be cut to lie flat; tools/paint.py unwraps along them.
    cuts = {frozenset(pair) for pair in tree.seams}
    for edge in mesh.edges:
        edge.use_seam = frozenset(edge.vertices) in cuts
    mesh.normals_split_custom_set([tuple(n) for n in corner_normals(tree)])
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
