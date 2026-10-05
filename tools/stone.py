"""Rock built as overlapping pieces (ADR 13): what the rock families' generators share.

A piece is a closed convex solid: the space behind a set of planes (`solid`), or
the hull of a set of points (`hull`). Each is given its soft edges on its own
(`soften`), which always works on a convex solid whose edges are long enough,
and the pieces are then put into one mesh as they are, passing into each other
(`join`). Nothing is fused: no boolean, and no short edges along the joins.
Painted crevice shadow hides the joins (tools/paint.py).

A generator draws its pieces, calls `finish` to stretch them to the spec's
bounds and soften them, measures the result with the gate's own checks
(`unmet`), and makes the object with `join`. Run under Blender.
"""

import contextlib
import io
import math

import bmesh
import bpy
from mathutils import Matrix, Vector
from pipeline import Checks, linear_rgb

FLAT = 1e-4  # tolerance for "on this plane" and "on the ground", metres
SOFT_EDGES_PER_EDGE = 3.2  # an edge must be at least this many soft-edge widths long for its bevel to form
SOFT_PLANE_M2 = 0.0004  # and a plane must keep this much once the soft edges have eaten its border
FACING = 0.02  # the least a soft edge's normal may agree with the face it is on (cosine); the load test fails at 0, lit from behind
MIN_ANGLE = math.radians(10)  # two planes of a piece closer in tilt than this would read as one bent plane

Z = Vector((0, 0, 1))


def leaning(azimuth, lift):
    """A unit normal pointing out at `azimuth` about Z, raised `lift` above horizontal (radians)."""
    return Vector((math.cos(azimuth) * math.cos(lift), math.sin(azimuth) * math.cos(lift), math.sin(lift)))


def meeting(*planes):
    """The point where three planes (normal, offset) meet."""
    return Matrix([normal for normal, _ in planes]).inverted() @ Vector([offset for _, offset in planes])


def solid(planes):
    """The convex solid behind every plane (normal, offset), or None when a plane touches nothing of it."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=200.0)
    for normal, offset in planes:
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=normal * offset, plane_no=normal, clear_outer=True)
        rim = [g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
        if len(rim) >= 3:
            bmesh.ops.holes_fill(bm, edges=rim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if len(bm.faces) != len(planes):
        bm.free()
        return None
    return bm


def prism(walls, top, drop, insets, floor=0.0):
    """A prism with a flat cap ringed by chamfers, as a mesh of exact planes, or None when it is not convex.

    `walls` are its sides as planes (normal, offset), in order round it, counter-clockwise seen
    from above; `top` is the plane of its cap. The sides stop at the shoulder, the plane `drop`
    metres below the cap, and from the shoulder edge of side i a chamfer rises to the cap,
    meeting it `insets[i]` metres in from where that side would have. Corner i is where side i
    meets side i + 1. Four planes meet at each shoulder corner, which plane cuts one at a time
    (`solid`) would turn into slivers; here the corners are computed and the faces made from them.
    """
    count = len(walls)
    ground = (Z, floor)
    shoulder = (top[0], top[1] - drop)
    try:
        base = [meeting(walls[i], walls[(i + 1) % count], ground) for i in range(count)]
        ring = [meeting(walls[i], walls[(i + 1) % count], shoulder) for i in range(count)]
        chamfers = []
        for i in range(count):
            a, b = ring[i - 1], ring[i]  # the shoulder edge of side i
            along = (b - a).normalized()
            inward = top[0].cross(along).normalized()  # in the cap's plane, toward its middle
            lifted = (a + b) / 2 + top[0] * drop
            normal = (b - a).cross(lifted + inward * insets[i] - a).normalized()
            if normal.z < 0:
                normal = -normal
            chamfers.append((normal, normal.dot(a)))
        cap = [meeting(chamfers[i], chamfers[(i + 1) % count], top) for i in range(count)]
    except ValueError:  # three planes with no one point in common
        return None
    bm = bmesh.new()
    rings = [[bm.verts.new(co) for co in corners] for corners in (base, ring, cap)]
    bm.faces.new(reversed(rings[0]))
    bm.faces.new(rings[2])
    for lower, upper in zip(rings, rings[1:]):
        for i in range(count):
            bm.faces.new((lower[i - 1], lower[i], upper[i], upper[i - 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    flat = all(abs(face.normal.dot(v.co - face.verts[0].co)) < FLAT for face in bm.faces for v in face.verts)
    if not flat or any(not e.is_convex or e.calc_face_angle() < 1e-3 for e in bm.edges) or bm.calc_volume(signed=True) <= 0:
        bm.free()
        return None
    return bm


def hull(points, floor=None):
    """The convex hull of the points, one face per plane; cut off level at `floor` when one is given."""
    bm = bmesh.new()
    for point in points:
        bm.verts.new(point)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    if floor is not None:
        cut = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(0, 0, floor), plane_no=(0, 0, 1), clear_inner=True)
        rim = [g for g in cut["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
        if len(rim) >= 3:
            bmesh.ops.holes_fill(bm, edges=rim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # The hull is triangles; faces in one plane become one face again.
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    bmesh.ops.dissolve_verts(bm, verts=[v for v in bm.verts if len(v.link_edges) == 2])
    bm.normal_update()
    return bm


def on_floor(element, floor):
    return all(abs(v.co.z - floor) < FLAT for v in element.verts)


def unsoftenable(bm, width, floor):
    """Why a piece cannot take soft edges of this width, or None."""
    bm.normal_update()
    if not bm.faces or any(not e.is_manifold for e in bm.edges):
        return "not a closed solid"
    if any(not e.is_convex for e in bm.edges):
        return "not convex"
    above = [e for e in bm.edges if not on_floor(e, floor)]
    if any(e.calc_length() < SOFT_EDGES_PER_EDGE * width for e in above):
        return f"an edge shorter than {SOFT_EDGES_PER_EDGE} soft-edge widths"
    if any(e.calc_face_angle() < MIN_ANGLE for e in above):
        return f"two planes within {math.degrees(MIN_ANGLE):.0f} degrees"
    if any(f.calc_area() - width * f.calc_perimeter() < SOFT_PLANE_M2 for f in bm.faces if not (f.normal.z < -0.999 and on_floor(f, floor))):
        return "a plane that the soft edges would eat"
    return None


def fit(pieces, lo, hi):
    """Stretch the pieces, together, so their bounding box is exactly lo..hi. Returns the stretch per axis."""
    verts = [v for bm in pieces for v in bm.verts]
    have_lo = [min(v.co[i] for v in verts) for i in range(3)]
    have_hi = [max(v.co[i] for v in verts) for i in range(3)]
    scale = [(hi[i] - lo[i]) / (have_hi[i] - have_lo[i]) for i in range(3)]
    for vert in verts:
        vert.co = Vector(lo[i] + (vert.co[i] - have_lo[i]) * scale[i] for i in range(3))
    for bm in pieces:
        bm.normal_update()
    return scale


def soften(bm, width, floor):
    """Bevel every edge of a piece that is not on the ground. Returns the layer that says which
    plane each face lies on (0 for the strip of a soft edge), or None when the bevel did not form."""
    bm.normal_update()
    planes = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in bm.faces]
    edges = [e for e in bm.edges if not on_floor(e, floor)]
    bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    tag = bm.faces.layers.int.new("plane")
    for face in bm.faces:
        centre = face.calc_center_median()
        face[tag] = next((i + 1 for i, (normal, offset) in enumerate(planes) if face.normal.dot(normal) > 1 - 1e-6 and abs(normal.dot(centre) - offset) < FLAT), 0)
    # An edge left between two planes is a hard edge: the bevel had no room there.
    if any(len(e.link_faces) == 2 and all(f[tag] for f in e.link_faces) and e.link_faces[0][tag] != e.link_faces[1][tag] and not on_floor(e, floor) for e in bm.edges):
        return None
    if any(not e.is_manifold for e in bm.edges):
        return None
    # Gates allow at most four sides; cut the larger planes into triangles. They stay coplanar.
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="BEAUTY")
    # Triangulation hands its faces back in an order that changes from run to run; fix it, so the exported file is the same.
    for index, face in enumerate(sorted(bm.faces, key=lambda face: tuple(round(c, 5) for c in face.calc_center_median()))):
        face.index = index
    bm.faces.sort()
    bm.normal_update()
    return tag


def plane_normals(bm, tag, floor):
    """One normal per face corner: a plane's own normal on the plane, and on the strip of a soft
    edge the normal of the plane each corner touches, so the strip blends from one plane to the
    next. A face lying on the ground keeps its own, and is never blended into: the piece meets
    the ground at a hard edge. Returns (the normals, how many faces they would light from behind)."""
    normals, behind = [], 0
    for face in bm.faces:
        mine = []
        for loop in face.loops:
            if face[tag]:
                mine.append(face.normal.copy())
                continue
            beside = [f.normal for f in loop.vert.link_faces if f[tag] and not (f.normal.z < -0.999 and on_floor(f, floor))]
            blend = sum(beside, Vector())
            mine.append(blend.normalized() if blend.length > 1e-6 else face.normal.copy())
        behind += min(normal.dot(face.normal) for normal in mine) <= FACING
        normals.extend(mine)
    return normals, behind


SAME_NORMAL_COS = 0.99985  # two normals are one when they agree this closely: the gates' limit (tools/validate.py, `soft_edges`)


def hard_places(bm, normals, reach, floor):
    """How many corners of a softened piece, above the ground, share a place with a corner lit by
    another normal: places are one when no further apart than `reach` along any axis, as the gates
    take them (`soft_edges`). `normals` are `plane_normals`'. A soft edge narrower than `reach` is
    such a place, and so is a point where two planes meet with no soft edge between them. `finish`
    does not ask this; a generator whose pieces are small beside the bounds' tolerance does."""
    corners = []
    index = 0
    for face in bm.faces:
        for loop in face.loops:
            if loop.vert.co.z > floor + reach:
                corners.append((loop.vert.co, normals[index]))
            index += 1
    return sum(1 for co, normal in corners if any(other.dot(normal) < SAME_NORMAL_COS and all(abs(c) <= reach for c in at - co) for at, other in corners))


def shortest_edge(bm, floor):
    return min(e.calc_length() for e in bm.edges if not on_floor(e, floor))


def finish(pieces, spec, soft, max_stretch=(0.8, 1.25)):
    """Stretch raw convex pieces to the spec's bounds and soften each on its own.

    `soft` is the (least, most) width of a soft edge, metres: a piece takes the widest its
    shortest edge has room for. Returns (the tag layers, the per-corner normals of each
    piece), or a string saying why this set of pieces will not do.
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    stretch = fit(pieces, lo, hi)
    if not all(max_stretch[0] <= s <= max_stretch[1] for s in stretch):
        return f"the pieces had to be stretched by {[round(s, 2) for s in stretch]} to fill the bounds"
    widths = [min(soft[1], shortest_edge(bm, lo.z) / SOFT_EDGES_PER_EDGE) for bm in pieces]
    if min(widths) < soft[0]:
        return f"a piece with an edge of {min(widths) * SOFT_EDGES_PER_EDGE:.3f} m, too short for a soft edge {soft[0]} m wide"
    for bm, width in zip(pieces, widths):
        reason = unsoftenable(bm, width, lo.z)
        if reason:
            return f"a piece with {reason}"
    tags = []
    for bm, width in zip(pieces, widths):
        tag = soften(bm, width, lo.z)
        if tag is None:
            return "a soft edge that did not form"
        tags.append(tag)
    # The soft edges cut the outermost corners back a little; fill the bounds again.
    fit(pieces, lo, hi)
    normals = []
    for bm, tag in zip(pieces, tags):
        found, behind = plane_normals(bm, tag, lo.z)
        if behind:
            return f"{behind} soft-edge faces that would be lit from behind"
        normals.append(found)
    return tags, normals


def merged(pieces):
    """The pieces in one mesh, each still closed and separate."""
    whole = bmesh.new()
    for bm in pieces:
        verts = {v: whole.verts.new(v.co) for v in bm.verts}
        for face in bm.faces:
            whole.faces.new([verts[v] for v in face.verts])
    whole.verts.index_update()
    whole.faces.index_update()
    whole.faces.ensure_lookup_table()
    whole.normal_update()
    return whole


def unmet(name, pieces, spec, conv, extra=()):
    """What the spec asks of the shape and these pieces do not give, as the gate's own failure lines.

    The gate measures the saved scene; this is the same measurement made early, so that a seed
    that cannot pass stops in the build with its reasons. `extra` is more checks of the same
    form as the gate's, (spec block, function), for what only one family asks.
    """
    import validate

    whole = merged(pieces)
    checks = Checks("build", name)
    with contextlib.redirect_stdout(io.StringIO()):
        if "overlap" in spec:
            validate.check_overlap(checks, name, whole.faces[:], spec, conv)
        for block, check in (("lean", validate.check_lean), ("foot", validate.check_foot), ("top", validate.check_top), *extra):
            if block in spec:
                check(checks, name, whole, spec, conv)
    triangles = sum(len(f.verts) - 2 for f in whole.faces)
    checks.check("budget.triangles", triangles <= spec["max_triangles"], f"{triangles} > {spec['max_triangles']}")
    whole.free()
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def join(name, pieces, normals, material_name, colour_hex):
    """One object of the softened pieces, lit by their plane normals, in one flat colour. Frees the pieces."""
    whole = merged(pieces)
    for bm in pieces:
        bm.free()
    mesh = bpy.data.meshes.new(name)
    whole.to_mesh(mesh)
    whole.free()
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.normals_split_custom_set([normal for piece in normals for normal in piece])

    material = bpy.data.materials.new(material_name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(colour_hex), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    mesh.materials.append(material)

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
