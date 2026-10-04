"""Rock: a boulder chiselled from a block by plane cuts, with one notch cut in as a ledge.

Every surface is a deliberate plane (ADR 9); nothing is displaced by noise.
The cuts are drawn from a seeded generator, role by role (leaning sides, a
top, a notch, shoulder chamfers), and a cut is redrawn when it would leave an
edge too short to bevel. Not every seed meets the spec: tools/gate.sh decides. Edges are softened by a one-segment bevel whose
strips blend between the normals of the planes on either side, so each plane
is lit flat and each edge is lit round. The finished mesh is stretched to the
spec's bounds. Run through tools/build.py.
"""

import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from pipeline import linear_rgb

SEED = 2  # the shipped rock: of seeds 1 to 40, five pass the gate (1, 2, 21, 28, 36); 2 has the clearest shoulder
BEVEL = 0.07  # how far a soft edge eats into each plane beside it, metres
MIN_EDGE = 0.3  # a cut may not leave a plane edge shorter than this
MIN_ANGLE = math.radians(12)  # nor two planes closer in tilt than this: they would read as one bent plane
SIDES = 6  # main side planes round the footprint
SLAB_SHARE = 1.8  # how much more of the way round the slab takes than any other side
LEDGE_RISER_M2, LEDGE_TREAD_M2 = 0.5, 0.7  # the notch must leave a wall and a shelf at least this big
LEDGE_TAKES = (0.04, 0.16)  # and remove this share of the rock's volume: a shoulder, not a fin
SUMMIT_M2 = 0.9  # and leave this much of the top standing above the shelf
FLAT = 1e-4  # tolerance for "on this plane"

Z = Vector((0, 0, 1))


def leaning(azimuth, lift):
    """A unit normal pointing out at `azimuth` about Z, raised `lift` above horizontal (radians)."""
    return Vector((math.cos(azimuth) * math.cos(lift), math.sin(azimuth) * math.cos(lift), math.sin(lift)))


def cut(bm, normal, depth):
    """Slice off everything further than `depth` inside the mesh's furthest point along `normal`."""
    reach = max(v.co.dot(normal) for v in bm.verts)
    result = bmesh.ops.bisect_plane(
        bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
        plane_co=normal * (reach - depth), plane_no=normal, clear_outer=True,
    )
    rim = [g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
    if len(rim) < 3:
        return False
    bmesh.ops.holes_fill(bm, edges=rim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return True


def slice_through(bm, point, normal):
    """Slice off everything in front of the plane through `point` facing `normal`."""
    reach = max(v.co.dot(normal) for v in bm.verts)
    return cut(bm, normal, reach - point.dot(normal))


def notch(bm, corner, riser, tread):
    """Remove the part of the rock that is both in front of the riser plane and above the tread plane.

    `corner` is a point on the line where the two planes meet; `riser` and
    `tread` are their unit normals. Done with an exact boolean against a
    skewed box, the one operation here that leaves an inward corner.
    """
    reach = 10.0
    along = riser.cross(tread).normalized()
    # The box's edges lie in the two planes: one runs up the riser, one out along the tread.
    out, up = tread.cross(along), along.cross(riser)
    frame = Matrix((out, up, along)).transposed().to_4x4()
    frame.translation = corner
    box = bmesh.new()
    bmesh.ops.create_cube(box, size=reach, matrix=frame @ Matrix.Translation((reach / 2, reach / 2, 0)))

    scene = bpy.context.scene
    temporary = []
    for name, source in (("rock_uncut", bm), ("rock_cutter", box)):
        mesh = bpy.data.meshes.new(name)
        source.to_mesh(mesh)
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        temporary.append(obj)
    box.free()
    uncut, cutter = temporary
    modifier = uncut.modifiers.new("notch", "BOOLEAN")
    modifier.operation, modifier.solver, modifier.object = "DIFFERENCE", "EXACT", cutter

    bm.clear()
    bm.from_object(uncut, bpy.context.evaluated_depsgraph_get())
    for obj in temporary:
        mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)
    # The solver leaves coplanar pieces; put each plane back as one face.
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return True


def area_on(bm, point, normal):
    """The area of the mesh's faces that lie on the plane through `point` facing `normal`."""
    return sum(f.calc_area() for f in bm.faces if f.normal.dot(normal) > 1 - 1e-5 and abs((f.calc_center_median() - point).dot(normal)) < FLAT)


def bevelable(bm):
    """True when the mesh is closed and every plane is big and distinct enough to take soft edges."""
    bm.normal_update()
    if not bm.faces or any(not e.is_manifold for e in bm.edges):
        return False
    if any(e.calc_length() < MIN_EDGE for e in bm.edges):
        return False
    return all(e.calc_face_angle() >= MIN_ANGLE for e in bm.edges)


def attempt(bm, rng, draw, required=None):
    """Apply one drawn operation, redrawing until it leaves a bevelable mesh. Returns the new mesh.

    A cut that never fits is left out, unless it is `required`, which names it in the error.
    """
    for _ in range(80):
        trial = bm.copy()
        if draw(trial, rng) and bevelable(trial):
            bm.free()
            return trial
        trial.free()
    if required:
        raise RuntimeError(f"this seed leaves no room for {required}")
    return bm


def fit(bm, lo, hi):
    """Stretch the mesh so its bounding box is exactly lo..hi."""
    have_lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    have_hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    for vert in bm.verts:
        vert.co = Vector(lo[i] + (vert.co[i] - have_lo[i]) / (have_hi[i] - have_lo[i]) * (hi[i] - lo[i]) for i in range(3))


def chisel(lo, hi, rng):
    """The rock as exact planes with hard edges: one face per plane."""
    half = (hi - lo) / 2
    bm = bmesh.new()
    # Larger than the rock, so that the side cuts remove every wall of the block.
    bmesh.ops.create_cube(bm, size=1.0)
    for vert in bm.verts:
        vert.co = Vector((vert.co.x * half.x * 3.2, vert.co.y * half.y * 3.2, (vert.co.z + 0.5) * (hi.z - lo.z)))

    def foot(azimuth, scale):
        """A point on the ground, on the ellipse that fills the footprint, pulled in by `scale`."""
        return Vector((math.cos(azimuth) * half.x, math.sin(azimuth) * half.y, 0)) * scale

    # Sides, at uneven spacing round the footprint. Each leans in toward the top by a different
    # amount, so the base is the widest part. One, the slab, takes a wider share of the way round
    # and leans further, which makes it the largest plane.
    slab = rng.randrange(SIDES)
    shares = [SLAB_SHARE if i == slab else 1.0 for i in range(SIDES)]
    turn = rng.uniform(0, math.tau)
    for i in range(SIDES):
        low, high = (24, 34) if i == slab else ((0, 6) if i % 2 else (7, 15))
        middle = (sum(shares[:i]) + shares[i] / 2) / sum(shares)

        def side(trial, r):
            azimuth = turn + math.tau * (middle + r.uniform(-0.2, 0.2) / sum(shares))
            return slice_through(trial, foot(azimuth, r.uniform(0.95, 1.12)), leaning(azimuth, math.radians(r.uniform(low, high))))

        bm = attempt(bm, rng, side)

    # The top: one broad plane, tipped so that no view shows it level.
    def top(trial, r):
        done = cut(trial, leaning(r.uniform(0, math.tau), math.radians(r.uniform(74, 84))), r.uniform(0.3, 0.9))
        return done and not any(f.normal.z > 1 - 1e-6 for f in trial.faces)  # nothing of the block's level top is left

    bm = attempt(bm, rng, top, required="the top")

    # The ledge: a notch in the top that leaves a raised slab above a lower shelf. The riser
    # leans back from the shelf, as a fracture does, and both are tipped off the axes.
    kept = []  # (point, normal, least area) for the riser and the tread, which later cuts must not eat

    def ledge(trial, r):
        summit = max(trial.faces, key=lambda f: f.normal.z)
        centre, summit_normal, height = summit.calc_center_median(), summit.normal.copy(), max(v.co.z for v in trial.verts)
        azimuth = r.uniform(0, math.tau)
        outward, sideways = leaning(azimuth, 0), leaning(azimuth + math.pi / 2, 0)
        tread = Matrix.Rotation(math.radians(r.uniform(4, 14)), 3, sideways) @ (Matrix.Rotation(math.radians(r.uniform(-10, 10)), 3, outward) @ Z)
        riser = Matrix.Rotation(math.radians(r.uniform(-14, 14)), 3, Z) @ leaning(azimuth, math.radians(r.uniform(8, 24)))
        corner = Vector((centre.x, centre.y, height * r.uniform(0.55, 0.75))) + outward * r.uniform(-0.3, 0.4)
        before = trial.calc_volume()
        notch(trial, corner, riser, tread)
        taken = 1 - trial.calc_volume() / before
        kept[:] = [(corner, riser, LEDGE_RISER_M2), (corner, tread, LEDGE_TREAD_M2), (centre, summit_normal, SUMMIT_M2)]
        return LEDGE_TAKES[0] <= taken <= LEDGE_TAKES[1] and intact(trial)

    def intact(trial):
        return all(area_on(trial, point, normal) >= least for point, normal, least in kept)

    bm = attempt(bm, rng, ledge, required="the ledge")

    # Shoulders: cuts across the corners where the top and the sides meet, three broad and three slight.
    for low, high in ((0.3, 0.55),) * 3 + ((0.14, 0.3),) * 3:
        bm = attempt(bm, rng, lambda t, r: cut(t, leaning(r.uniform(0, math.tau), math.radians(r.uniform(30, 64))), r.uniform(low, high)) and intact(t))
    return bm


def soften(bm):
    """Bevel every edge above the ground, and return each face's plane normal (None for bevel faces)."""
    bm.normal_update()  # the mesh has just been stretched
    planes = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in bm.faces]
    edges = [e for e in bm.edges if not all(abs(v.co.z) < FLAT for v in e.verts)]
    bmesh.ops.bevel(bm, geom=edges, offset=BEVEL, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()

    tag = bm.faces.layers.int.new("plane")
    for face in bm.faces:
        centre = face.calc_center_median()
        face[tag] = next(
            (i + 1 for i, (normal, offset) in enumerate(planes) if face.normal.dot(normal) > 1 - 1e-6 and abs(normal.dot(centre) - offset) < FLAT), 0
        )
    # Gates allow at most four sides; cut the larger planes into triangles. They stay coplanar.
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="BEAUTY")
    return tag


def plane_normals(bm, tag):
    """One normal per face corner: a plane's own normal on the plane, and on a bevel face the
    normal of the plane each corner touches, so the strip blends from one plane to the next."""
    bm.normal_update()
    normals = []
    for face in bm.faces:
        for loop in face.loops:
            if face[tag]:
                normals.append(face.normal.copy())
                continue
            # The ground face is never blended into: the rock meets the ground at a hard edge.
            beside = [f.normal for f in loop.vert.link_faces if f[tag] and f.normal.z > -0.999]
            blend = sum(beside, Vector())
            normals.append(blend.normalized() if blend.length > 1e-6 else face.normal.copy())
    return normals


def build(spec, seed=SEED):
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    bm = chisel(lo, hi, random.Random(seed))
    fit(bm, lo, hi)
    tag = soften(bm)
    fit(bm, lo, hi)
    # Triangulation hands its faces back in an order that changes from run to run. The
    # shape is the same, but the exported file is not; put the faces in a fixed order.
    for index, face in enumerate(sorted(bm.faces, key=lambda face: tuple(round(c, 5) for c in face.calc_center_median()))):
        face.index = index
    bm.faces.sort()
    normals = plane_normals(bm, tag)
    bm.faces.layers.int.remove(tag)

    mesh = bpy.data.meshes.new("rock")
    bm.to_mesh(mesh)
    bm.free()
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.normals_split_custom_set(normals)

    material = bpy.data.materials.new("m_rock")
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*linear_rgb(spec["materials"]["m_rock"]), 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    mesh.materials.append(material)

    obj = bpy.data.objects.new("rock", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
