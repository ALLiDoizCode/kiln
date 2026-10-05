"""Wood as plain lists: tubes of flat sides ring by ring, with the grain's direction written on every face.

Shared by generators of dead wood (source/log). A generator draws its rings
into a `Wood`, joins them with `skin`, closes the ends and turns the lists into
one Blender object with `to_object`.

`frames`, the two vertices and narrow strip at every corner of a ring (the
soft edge), the seams (one cut along each stretch, and every ring a cut), the
`grain` attribute (metres round the limb, metres along it, a number per limb:
ADR 12) and `flat_material` are the tree's (source/tree/generator.py), lifted
here without changing that file: the tree keeps its own copies, in a `tube`
that also draws its roots' fins and closes both ends itself. A tree could be
drawn from these; until it is, a change to how bark is skinned or its grain
measured has to be made in both.

Each material gets one flat colour; tools/paint.py paints them (ADR 10).
"""

import math

import bpy
from mathutils import Vector
from pipeline import linear_rgb

# What a face is. SIDE: a flat side of a limb. STRIP: the narrow face along a corner between two sides.
# END: where the wood is broken or sawn through. RIM: a narrow face round a sawn end, between bark and cut.
# INNER: the wall of a hollow, seen from inside. UNDER: flat on the ground, facing down.
SIDE, STRIP, END, RIM, INNER, UNDER = "side", "strip", "end", "rim", "inner", "under"


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


class Wood:
    """The mesh as lists, in the order they are made."""

    def __init__(self):
        self.verts = []
        self.faces = []
        self.kinds = []
        self.materials = []  # per face: an index into the object's materials
        # Per face, per corner: (metres across the grain, metres along it, a number for the limb), which
        # tools/paint.py reads to run the grain along each limb.
        self.grain = []
        self.seams = []  # pairs of vertices: edges along which the surface is cut open to be painted
        self.limbs = 0

    def vert(self, co):
        self.verts.append(Vector(co))
        return len(self.verts) - 1

    def face(self, corners, kind, material, grain):
        self.faces.append(tuple(corners))
        self.kinds.append(kind)
        self.materials.append(material)
        self.grain.append(list(grain))

    def limb(self):
        """A number for the next limb, so that no two limbs share a pattern."""
        self.limbs += 1
        return (self.limbs - 1) * 3.7

    def triangles(self):
        return sum(len(face) - 2 for face in self.faces)

    def normal(self, index):
        face = self.faces[index]
        a, b, c = (self.verts[i] for i in face[:3])
        normal = (b - a).cross(c - a)
        if len(face) == 4:
            normal += (c - a).cross(self.verts[face[3]] - a)
        return normal.normalized() if normal.length > 1e-12 else normal


def ring(wood, point, frame, radius, sides, strip=0.0, spin=0.0, reach=None, shift=None):
    """One ring of a limb round `point`: `sides` corners, each two vertices when `strip` is given.

    `reach[corner]` scales a corner's distance from the axis, and `shift[corner]` moves it along
    the limb (a broken end). A corner that reaches far is a fin: its two vertices stay close."""
    tangent, across, along = frame
    made = []
    for j in range(sides):
        scale = reach[j] if reach else 1.0
        half = strip * math.pi / sides / (scale if scale > 1.2 else 1.0)
        for step in range(2 if strip else 1):
            angle = spin + 2 * math.pi * j / sides + (half * (2 * step - 1) if strip else 0.0)
            co = point + (across * math.cos(angle) + along * math.sin(angle)) * radius * scale
            made.append(wood.vert(co + tangent * (shift[j] if shift else 0.0)))
    return made


def round_of(wood, loop):
    """How far round a ring each of its vertices is, in metres over the ring itself; one more entry closes it."""
    far = [0.0]
    for i in range(len(loop)):
        far.append(far[-1] + (wood.verts[loop[(i + 1) % len(loop)]] - wood.verts[loop[i]]).length)
    return far


def skin(wood, rings, far, material, limb, strips=False, inward=False, seam=0):
    """Join each ring to the next with quads, all of one vertex count. `far[k]` is how far along the limb ring k is.

    With `strips` the rings have two vertices to a corner and every other face is a STRIP.
    `inward` turns the faces to be seen from inside (the wall of a hollow).
    Each stretch between two rings is cut once along its length, at vertex `seam` of the ring,
    and every ring is a cut, so no painted island is longer than one stretch of the limb."""
    count = len(rings[0])
    rounds = [round_of(wood, loop) for loop in rings]
    for k in range(len(rings) - 1):
        lower, upper = rings[k], rings[k + 1]
        for i in range(count):
            j = (i + 1) % count
            kind = INNER if inward else STRIP if strips and i % 2 == 0 else SIDE
            corners = [lower[i], lower[j], upper[j], upper[i]]
            grain = [(rounds[k][i], far[k], limb), (rounds[k][i + 1], far[k], limb), (rounds[k + 1][i + 1], far[k + 1], limb), (rounds[k + 1][i], far[k + 1], limb)]
            if inward:
                corners.reverse()
                grain.reverse()
            wood.face(corners, kind, material, grain)
        wood.seams.append((lower[seam], upper[seam]))
    for loop in rings:
        wood.seams += [(loop[i], loop[(i + 1) % count]) for i in range(count)]


def flat_material(name, colour):
    material = bpy.data.materials.new(name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(colour), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    material.use_backface_culling = True
    return material


def corner_normals(wood, floor_z, tol):
    """One normal per face corner, in the order the mesh stores them.

    Every vertex has one normal, so no edge above the ground is lit hard: the blend of the flat
    faces that meet there (sides, ends, the wall of a hollow), and where there are none, or where
    that blend would face away from a face it belongs to, the blend of every face that meets
    there. Faces flat on the ground keep their own: the edge a shape stands on may be hard. So
    may a vertex on the ground be: where no one normal suits every face that meets there (the lip
    of a hollow, pressed onto the ground), each face that the blend faces away from keeps its own."""
    face_normals = [wood.normal(i) for i in range(len(wood.faces))]
    flat = [Vector() for _ in wood.verts]
    every = [Vector() for _ in wood.verts]
    around = [[] for _ in wood.verts]
    for face, kind, normal in zip(wood.faces, wood.kinds, face_normals):
        if kind == UNDER:
            continue
        # A quad is exported as two triangles, cut either way, and a wrung quad's triangles face apart:
        # a vertex's normal must suit each triangle it may become a corner of.
        halves = [normal]
        if len(face) == 4:
            p = [wood.verts[i] for i in face]
            halves += [(p[b] - p[a]).cross(p[c] - p[a]).normalized() for a, b, c in ((0, 1, 2), (0, 2, 3), (1, 2, 3), (1, 3, 0))]
        for i in face:
            if kind not in (STRIP, RIM):
                flat[i] += normal
            every[i] += normal
            around[i] += halves
    lit = {}
    for i, faces in enumerate(around):
        if not faces:
            continue
        normal = (flat[i] if flat[i].length > 1e-6 else every[i]).normalized()
        if min(normal.dot(n) for n in faces) < 0.1:
            normal = every[i].normalized()
        if min(normal.dot(n) for n in faces) <= 0.02 and wood.verts[i].z > floor_z + tol:
            raise RuntimeError(f"a corner at {tuple(round(c, 2) for c in wood.verts[i])} is folded too sharply to light")
        lit[i] = normal
    normals = []
    for face, kind, normal in zip(wood.faces, wood.kinds, face_normals):
        if kind == UNDER:
            normals += [normal] * len(face)
            continue
        p = [wood.verts[i] for i in face]
        halves = [normal] + ([(p[b] - p[a]).cross(p[c] - p[a]).normalized() for a, b, c in ((0, 1, 2), (0, 2, 3), (1, 2, 3), (1, 3, 0))] if len(face) == 4 else [])
        normals += [lit[i] if min(lit[i].dot(half) for half in halves) > 0.02 else normal for i in face]
    return normals


def to_object(wood, name, materials, floor_z=0.0, tol=0.001):
    """The lists as one Blender object: `materials` is [(name, sRGB hex)], in the order faces index them."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in wood.verts], [], wood.faces)
    for material, colour in materials:
        mesh.materials.append(flat_material(material, colour))
    mesh.polygons.foreach_set("material_index", wood.materials)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    # Seams say where the surface may be cut to lie flat; tools/paint.py unwraps along them.
    cuts = {frozenset(pair) for pair in wood.seams}
    for edge in mesh.edges:
        edge.use_seam = frozenset(edge.vertices) in cuts
    mesh.normals_split_custom_set([tuple(n) for n in corner_normals(wood, floor_z, tol)])
    # Where each corner lies round and along its limb, for the grain (tools/paint.py).
    grain = mesh.attributes.new("grain", "FLOAT_VECTOR", "CORNER")
    grain.data.foreach_set("vector", [c for corners in wood.grain for corner in corners for c in corner])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
