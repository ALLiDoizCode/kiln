"""The parts small plants are built from: leaf pieces, cores, stems, blades and heads, as plain lists.

Shared by the generators of the small-plant families (source/dome_bush,
source/blade_plant, source/grass_tuft, source/tall_grass, source/reeds). A generator draws its plant into a
`Parts`, fits it to the spec's bounds and turns it into one Blender object of
two materials: a closed one (stems, a crown) and the open foliage material
(leaf pieces and blades, with the cores under them).

The leaf piece and the core are the tree's (source/tree/generator.py, ADR 9):
the same outline, the same dome. They are written again here because that
file takes its sizes from its own constants; a tree could be drawn from these.

Each material gets one flat colour; tools/paint.py paints the closed material
and gives every piece its colour from the palette (ADR 10, ADR 11).
"""

import importlib.util
import math
import sys

import bpy
from mathutils import Quaternion, Vector
from pipeline import ROOT, linear_rgb

Z = Vector((0, 0, 1))
LEAF, CORE, STEM, GROUND = "leaf", "core", "stem", "ground"

# A leaf piece's outline in its own plane (along its length, across it), from its foot: the
# foot, a shoulder, a notch and a tooth up one side, the tip, and a shoulder on the other side.
LEAF_OUTLINE = [(0.0, 0.0), (0.28, -0.5), (0.47, -0.24), (0.6, -0.38), (1.0, 0.0), (0.38, 0.5)]
LEAF_TRIANGLES = [(0, 1, 2), (2, 3, 4), (0, 2, 4), (0, 4, 5)]


def family_generator(family):
    """The module source/<family>/generator.py, loaded once under a name of its own.

    Every family calls its generator `generator.py`; imported by that name, the
    second family built in one Blender process would get the first one's."""
    name = f"{family}_generator"
    if name not in sys.modules:
        found = importlib.util.spec_from_file_location(name, ROOT / "source" / family / "generator.py")
        module = importlib.util.module_from_spec(found)
        sys.modules[name] = module
        found.loader.exec_module(module)
    return sys.modules[name]


class Parts:
    """The mesh as lists, in the order they are made."""

    def __init__(self):
        self.verts = []
        self.faces = []
        self.kinds = []
        self.pieces = []  # per face: which piece it belongs to; -1 for anything else
        self.piece_out = []  # per piece: the direction it is lit from (out of its lobe, or its own front)
        self.piece_round = []  # per piece: the share of its normal taken from that direction; None for a bent piece, lit smooth
        self.round_normals = {}  # core vertex -> its normal
        self.seams = []  # pairs of vertices: edges along which the closed surface is cut open to be painted
        self.whole = []  # (first vertex, how many): runs of vertices the fit stretches as one thing, by what it gives their middle (a head)

    def vert(self, co):
        self.verts.append(Vector(co))
        return len(self.verts) - 1

    def face(self, corners, kind, piece=-1):
        self.faces.append(tuple(corners))
        self.kinds.append(kind)
        self.pieces.append(piece)

    def piece(self, out, rounded):
        self.piece_out.append(Vector(out).normalized())
        self.piece_round.append(rounded)
        return len(self.piece_out) - 1

    def triangles(self):
        return sum(len(face) - 2 for face in self.faces)


class Lobe:
    """A rounded mass: half an ellipsoid above its middle and a shallower half below."""

    def __init__(self, centre, radius, up, down):
        self.centre, self.radius, self.up, self.down = Vector(centre), radius, up, down

    def surface(self, unit):
        """(the point of the lobe's surface in the direction `unit` of a unit sphere, the way out of the lobe there)."""
        vertical = self.up if unit.z >= 0 else self.down
        point = self.centre + Vector((unit.x * self.radius, unit.y * self.radius, unit.z * vertical))
        return point, Vector((unit.x / self.radius, unit.y / self.radius, unit.z / vertical)).normalized()

    def depth(self, point):
        """How far out of the lobe a point is: below 1 inside it, 1 on its surface."""
        offset = point - self.centre
        vertical = self.up if offset.z >= 0 else self.down
        return math.sqrt((offset.x / self.radius) ** 2 + (offset.y / self.radius) ** 2 + (offset.z / vertical) ** 2)


def leaf_piece(parts, rng, point, out, axis, length, width, foot_share, roll_deg, rounded, floor=None):
    """One flat, pointed, notched piece through `point`, lying along `axis`, its front toward `out`.

    `foot_share` of its length lies behind `point`. With `floor`, a piece that
    would dip below that height is lifted, whole, to stand on it."""
    across = out.cross(axis)
    across = (across if across.length > 1e-6 else axis.orthogonal()).normalized()
    across = Quaternion(axis, math.radians(rng.uniform(-roll_deg, roll_deg))) @ across
    mirror = rng.choice((-1, 1))
    foot = point - axis * length * foot_share
    corners = [foot + axis * (u * length) + across * (v * width * mirror) for u, v in LEAF_OUTLINE]
    if floor is not None:
        lowest = min(corner.z for corner in corners)
        if lowest < floor:
            corners = [corner + Z * (floor - lowest) for corner in corners]
    corners = [parts.vert(corner) for corner in corners]
    fan = [tuple(corners[i] for i in triangle) for triangle in LEAF_TRIANGLES]
    if (axis.cross(across) * mirror).dot(out) < 0:
        fan = [(a, c, b) for a, b, c in fan]
    piece = parts.piece(out, rounded)
    for triangle in fan:
        parts.face(triangle, LEAF, piece)
    return piece


def core(parts, rng, lobe, size, sides=6, rough=0.12):
    """A closed, low-triangle dome inside a lobe (ADR 9 as amended): an apex, two rings of corners and a low point underneath."""

    def at(radius, height):
        return lobe.centre + Vector((radius.x * lobe.radius, radius.y * lobe.radius, height * (lobe.up if height >= 0 else lobe.down))) * size

    spin = rng.uniform(0, 2 * math.pi)
    rings = []
    for share, height, shift in ((0.72, 0.55, 0.0), (0.97, -0.15, 0.5)):
        ring = []
        for j in range(sides):
            angle = spin + 2 * math.pi * (j + shift) / sides
            reach = share * (1 + rng.uniform(-rough, rough))
            ring.append(parts.vert(at(Vector((math.cos(angle) * reach, math.sin(angle) * reach, 0)), height)))
        rings.append(ring)
    top, bottom = parts.vert(at(Vector(), 0.9)), parts.vert(at(Vector(), -0.8))
    upper, lower = rings
    triangles = []
    for j in range(sides):
        k = (j + 1) % sides
        triangles += [(top, upper[j], upper[k]), (upper[j], lower[j], upper[k]), (upper[k], lower[j], lower[k]), (bottom, lower[k], lower[j])]
    for a, b, c in triangles:
        middle = (parts.verts[a] + parts.verts[b] + parts.verts[c]) / 3
        if (parts.verts[b] - parts.verts[a]).cross(parts.verts[c] - parts.verts[a]).dot(middle - lobe.centre) < 0:
            b, c = c, b
        parts.face((a, b, c), CORE)
    for i in upper + lower + [top, bottom]:
        offset = parts.verts[i] - lobe.centre
        vertical = lobe.up if offset.z >= 0 else lobe.down
        parts.round_normals[i] = Vector((offset.x / lobe.radius**2, offset.y / lobe.radius**2, offset.z / vertical**2)).normalized()


def stem(parts, points, radii, sides, spin=0.0):
    """A closed tapering tube along `points`, standing on the ground: a level first ring with a flat cap under it, and a flat end."""
    rings = []
    for k, (point, radius) in enumerate(zip(points, radii)):
        tangent = (points[min(k + 1, len(points) - 1)] - points[max(k - 1, 0)]).normalized()
        if k == 0:
            across, along = Vector((1, 0, 0)), Vector((0, 1, 0))
        else:
            across = (Vector((1, 0, 0)) - tangent * tangent.x).normalized()
            along = tangent.cross(across).normalized()
        rings.append([parts.vert(point + (across * math.cos(spin + 2 * math.pi * j / sides) + along * math.sin(spin + 2 * math.pi * j / sides)) * radius) for j in range(sides)])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            parts.face((lower[i], lower[j], upper[j], upper[i]), STEM)
        # Each stretch between two rings is cut once along its length, to unroll flat.
        parts.seams.append((lower[0], upper[0]))
    # And every ring is a cut: short, nearly square islands pack closer than long tapering strips.
    for ring in rings:
        parts.seams += [(ring[i], ring[(i + 1) % sides]) for i in range(sides)]
    centre = parts.vert(points[0])
    for i in range(sides):
        parts.face((centre, rings[0][(i + 1) % sides], rings[0][i]), GROUND)
    # The far end is closed flat: it is buried in what the stem carries.
    if sides == 4:
        parts.face(tuple(rings[-1]), STEM)
    else:
        apex = parts.vert(points[-1])
        for i in range(sides):
            parts.face((rings[-1][i], rings[-1][(i + 1) % sides], apex), STEM)


def mound(parts, rng, radius, height, sides, rough=0.08, seams=False):
    """A closed, low, faceted mound on the ground about the origin: the crown a rosette of blades grows from.

    With `seams` it is cut round its foot, for a plant whose closed surface has other pieces that
    are cut open to be painted (heads): tools/paint.py then unwraps all of it along its seams."""
    spin = rng.uniform(0, 2 * math.pi)
    rings = []
    # Shallow enough all over that tools/paint.py unwraps what is seen of it as one island, from above.
    for share, level in ((1.0, 0.0), (0.6, 0.6)):
        rings.append([parts.vert((math.cos(spin + 2 * math.pi * j / sides) * radius * share * (1 + rng.uniform(-rough, rough)),
                                  math.sin(spin + 2 * math.pi * j / sides) * radius * share * (1 + rng.uniform(-rough, rough)), height * level)) for j in range(sides)])
    lower, upper = rings
    for i in range(sides):
        j = (i + 1) % sides
        parts.face((lower[i], lower[j], upper[j], upper[i]), STEM)
    centre, apex = parts.vert((0, 0, 0)), parts.vert((0, 0, height))
    for i in range(sides):
        j = (i + 1) % sides
        parts.face((centre, lower[j], lower[i]), GROUND)
        parts.face((upper[i], upper[j], apex), STEM)
    if seams:
        parts.seams += [(lower[i], lower[(i + 1) % sides]) for i in range(sides)]


def head(parts, base, top, radius, sides, rings=((0.35, 1.0),), spin=0.0):
    """One head (a seed head, a cattail): a closed spindle from `base` to `top`, pointed at both ends.

    It is of the closed material and lit smooth, as a stem is, and stands on
    nothing: what carries it is a blade drawn through it. `rings` are the
    loops of corners between its two points, each as (how far along it, its
    radius over `radius`)."""
    axis = top - base
    unit = axis.normalized()
    across = unit.orthogonal().normalized()
    along = unit.cross(across)
    loops = [
        [parts.vert(base + axis * share + (across * math.cos(spin + 2 * math.pi * j / sides) + along * math.sin(spin + 2 * math.pi * j / sides)) * radius * wide) for j in range(sides)]
        for share, wide in rings
    ]
    low, high = parts.vert(base), parts.vert(top)
    # Stretched as one thing by the fit: bent where it crosses one of the origin's axes, a spindle this small is no longer convex.
    parts.whole.append((loops[0][0], sides * len(loops) + 2))
    for i in range(sides):
        j = (i + 1) % sides
        parts.face((low, loops[0][j], loops[0][i]), STEM)
        for lower, upper in zip(loops, loops[1:]):
            parts.face((lower[i], lower[j], upper[j], upper[i]), STEM)
        parts.face((loops[-1][i], loops[-1][j], high), STEM)
    # Cut once from point to point, it unrolls as one island.
    line = [low] + [loop[0] for loop in loops] + [high]
    parts.seams += list(zip(line, line[1:]))


def stalk(parts, spine, radii, sides=3, spin=0.0):
    """One stalk (a reed's): a thin tube along `spine` that tapers to its tip, open at its foot, as one open piece of the foliage.

    `spine` is the points along its middle, from its foot to its tip; `radii`
    the tube's radius at each, the last a few millimetres. It is round, where a
    blade is a strip: seen at the same width from every side, and lit smooth
    round itself. Its tip is a ring closed by a cap and not one corner: one
    corner shared by sides that long would be lit along the stalk, square to
    every face it belongs to, and the load test finds such normals against their faces."""
    piece = parts.piece(Z, None)
    rings = []
    for k, (point, radius) in enumerate(zip(spine, radii)):
        tangent = (spine[min(k + 1, len(spine) - 1)] - spine[max(k - 1, 0)]).normalized()
        across = (Vector((1, 0, 0)) - tangent * tangent.x).normalized()
        along = tangent.cross(across).normalized()
        rings.append([parts.vert(point + (across * math.cos(spin + 2 * math.pi * j / sides) + along * math.sin(spin + 2 * math.pi * j / sides)) * radius) for j in range(sides)])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(sides):
            j = (i + 1) % sides
            parts.face((lower[i], lower[j], upper[j], upper[i]), LEAF, piece)
    parts.face(tuple(rings[-1]), LEAF, piece)
    return piece


def blade(parts, spine, widths, front, fold=0.0, across=None):
    """One blade: a strip along `spine` that tapers to a point, as one open piece.

    `spine` is the points along its middle, from its foot to its tip; `widths`
    the blade's whole width at each but the tip. `front` is the side its upper
    face looks to at the foot. With `fold` the blade is a shallow V along its
    middle: its edges are raised by that share of its half width. With `across`,
    one direction for each row, the strip lies that way across its spine at each
    row and not square to `front`: a leaf that turns as it goes."""
    piece = parts.piece(front, None)  # lit smooth, not as one flat thing
    rows = []
    for k, (point, width) in enumerate(zip(spine[:-1], widths)):
        tangent = (spine[k + 1] - spine[max(k - 1, 0)]).normalized()
        if across is not None:
            lies = across[k] - tangent * across[k].dot(tangent)
            lies = (lies if lies.length > 1e-6 else tangent.orthogonal()).normalized()
        else:
            lies = tangent.cross(front)
            lies = (lies if lies.length > 1e-6 else tangent.orthogonal()).normalized()
        across_row = lies
        up = across_row.cross(tangent).normalized()
        half = width / 2
        row = [parts.vert(point - across_row * half + up * half * fold)]
        if fold:
            row.append(parts.vert(point))
        row.append(parts.vert(point + across_row * half + up * half * fold))
        rows.append(row)
    for lower, upper in zip(rows, rows[1:]):
        for i in range(len(lower) - 1):
            parts.face((lower[i], lower[i + 1], upper[i + 1], upper[i]), LEAF, piece)
    tip = parts.vert(spine[-1])
    for i in range(len(rows[-1]) - 1):
        parts.face((rows[-1][i], rows[-1][i + 1], tip), LEAF, piece)
    return piece


def fit(parts, lo, hi, about_origin=False, most=(0.8, 1.25)):
    """Stretch the plant so its bounds are exactly lo..hi. The ground stays the ground.

    Level, it is stretched and slid: one stretch for the whole plant along each
    axis, so flat pieces stay flat. With `about_origin` it is not slid: each side
    of the origin is stretched by what that side needs, so what grows from the
    origin still does; pieces that cross the origin's axes bend a little there."""
    have_lo = [min(v[i] for v in parts.verts) for i in range(3)]
    have_hi = [max(v[i] for v in parts.verts) for i in range(3)]
    if about_origin:
        low = [lo[i] / have_lo[i] for i in range(2)] + [1.0]
        high = [hi[i] / have_hi[i] for i in range(3)]
    else:
        low = high = [(hi[i] - lo[i]) / (have_hi[i] - have_lo[i]) for i in range(3)]
    if abs(have_lo[2] - lo[2]) > 1e-6 or any(not most[0] <= s <= most[1] for s in low + high):
        raise RuntimeError(
            f"the plant drawn spans {[round(v, 3) for v in have_lo]}..{[round(v, 3) for v in have_hi]}; reaching the bounds "
            f"{tuple(lo)}..{tuple(hi)} would stretch it by {[round(s, 2) for s in low + high]}, outside {most}, or it does not stand on the ground"
        )
    # A run of vertices in `parts.whole` goes by the side of the origin its middle is on.
    side = list(parts.verts)
    for first, count in parts.whole:
        middle = sum(parts.verts[first : first + count], Vector()) / count
        side[first : first + count] = [middle] * count
    for v, by in zip(parts.verts, side):
        for i in range(3):
            v[i] = v[i] * (high[i] if by[i] > 0 else low[i]) if about_origin else lo[i] + (v[i] - have_lo[i]) * high[i]


def parted(parts, least=0.0015, step=0.003):
    """The plant with no two vertices nearer than `least` on every axis: the later of such a pair is moved `step` toward the middle of the plant.

    Two corners of different pieces at one place are lit as a hard edge, and
    among the feet of a hundred blades in one rootstock some pair meets by chance."""
    middle = sum(parts.verts, Vector()) / len(parts.verts)
    for _ in range(8):
        moved = False
        order = sorted(range(len(parts.verts)), key=lambda i: parts.verts[i].x)
        for n, i in enumerate(order):
            for j in order[n + 1 :]:
                if parts.verts[j].x - parts.verts[i].x >= least:
                    break
                if all(abs(parts.verts[i][axis] - parts.verts[j][axis]) < least for axis in (1, 2)):
                    later = max(i, j)
                    parts.verts[later] += (middle - parts.verts[later]).normalized() * step
                    moved = True
        if not moved:
            break
    return parts


def drawn_to_fit(sketch, lo, hi, about_origin=False, most=(0.8, 1.25)):
    """`sketch(spread)` draws a plant `spread` times as wide as its first idea; this finds the width that fills the bounds, and fits it.

    A plant reaches further one way than another by chance, so the width it
    must be drawn at is found by drawing: the same seed gives the same plant, wider."""
    spread = 1.0
    for _ in range(3):
        parts = sketch(spread)
        have = [max(v[i] for v in parts.verts) - min(v[i] for v in parts.verts) for i in range(2)]
        spread *= math.sqrt((hi[0] - lo[0]) / have[0] * (hi[1] - lo[1]) / have[1])
    parts = sketch(spread)
    fit(parts, lo, hi, about_origin, most)
    return parts


def corner_normals(parts, lift=0.3):
    """One normal per face corner, in the order the mesh stores them.

    The closed surface is lit smooth above the ground. Every corner of a flat
    piece carries one normal: part the piece's own and part the direction it
    was given (out of its lobe), tipped toward the sky by `lift`. A blade is
    lit smooth along and across itself. Cores are lit round."""
    face_normals = []
    for face in parts.faces:
        a, b, c = (parts.verts[i] for i in face[:3])
        normal = (b - a).cross(c - a)
        if len(face) == 4:
            normal += (c - a).cross(parts.verts[face[3]] - a)
        face_normals.append(normal.normalized())
    smooth = [Vector() for _ in parts.verts]
    for face, kind, normal in zip(parts.faces, parts.kinds, face_normals):
        if kind == STEM:
            for i in face:
                smooth[i] += normal
    # A bent piece (a blade) is lit smooth, one normal per vertex, so no edge within it is hard.
    for face, kind, piece, normal in zip(parts.faces, parts.kinds, parts.pieces, face_normals):
        if kind == LEAF and parts.piece_round[piece] is None:
            for i in face:
                smooth[i] += normal
    normals = []
    for face, kind, piece, normal in zip(parts.faces, parts.kinds, parts.pieces, face_normals):
        if kind == GROUND:
            normals += [normal] * len(face)
        elif kind == LEAF and parts.piece_round[piece] is not None:
            share = parts.piece_round[piece]
            lit = (normal * (1 - share) + parts.piece_out[piece] * share + Z * lift).normalized()
            # Never round the back of its own face: the engine would light it from behind.
            if lit.dot(normal) < 0.3:
                lit = (lit + normal * (0.3 - lit.dot(normal)) * 1.5).normalized()
            normals += [lit] * len(face)
        elif kind == CORE:
            normals += [parts.round_normals[i] if parts.round_normals[i].dot(normal) > 0.05 else normal for i in face]
        else:
            normals += [smooth[i].normalized() for i in face]
    return normals


def flat_material(name, colour, two_sided):
    material = bpy.data.materials.new(name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(colour), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    # Exported as glTF doubleSided: a leaf piece is seen, and lit, from both sides.
    material.use_backface_culling = not two_sided
    return material


def to_object(parts, spec):
    """The spec's one object from the lists. The foliage's material holds the pieces and cores; the other material the closed surface."""
    name = spec["objects"][0]
    leaf = spec["foliage"]["material"]
    closed = next(m for m in spec["materials"] if m != leaf)
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in parts.verts], [], parts.faces)
    mesh.materials.append(flat_material(closed, spec["materials"][closed], two_sided=False))
    mesh.materials.append(flat_material(leaf, spec["materials"][leaf], two_sided=True))
    mesh.polygons.foreach_set("material_index", [1 if kind in (LEAF, CORE) else 0 for kind in parts.kinds])
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    # Seams say where the closed surface may be cut to lie flat; tools/paint.py unwraps along them.
    cuts = {frozenset(pair) for pair in parts.seams}
    for edge in mesh.edges:
        edge.use_seam = frozenset(edge.vertices) in cuts
    mesh.normals_split_custom_set([tuple(n) for n in corner_normals(parts)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
