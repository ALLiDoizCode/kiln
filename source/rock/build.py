"""Rock: a full boulder chiselled from a block by plane cuts, with three forms cut into it.

Every surface is a deliberate plane (ADR 9); nothing is displaced by noise.
The cuts are drawn from a seeded generator, role by role:

1. sides that lean in a little, round a footprint between an ellipse and the box;
2. a tipped top;
3. chamfers across the corners where the top meets the sides;
4. a step: a notch in the top that leaves a raised slab above a lower shelf;
5. a fracture: a V-shaped groove down one side, deepest at the top;
6. a shoulder: a bench cut into another side at about half height.

The three forms sit about a third of the way round from each other, so each
side of the rock shows one. A cut is redrawn when it would leave an edge too
short to bevel or would eat a form already made. Nothing is left out: a seed
whose cuts do not fit, or whose rock does not meet the spec, fails the build
and says why. Edges are softened by a one-segment bevel whose strips blend
between the normals of the planes on either side, so each plane is lit flat
and each edge is lit round. The finished mesh is stretched to the spec's
bounds. Run through tools/build.py.
"""

import contextlib
import io
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from pipeline import Checks, conventions, linear_rgb
from validate import check_fullness, check_planes

SEED = 2  # the shipped rock; see the brief for how it was chosen
BEVEL = 0.07  # how far a soft edge eats into each plane beside it, metres
MIN_EDGE = 0.24  # a cut may not leave a plane edge shorter than this
BODY_EDGE = 0.4  # and the body, before the forms are cut into it, none shorter than this
MIN_PLANE_M2 = 0.45  # nor a plane smaller than this once the bevel has eaten its border: every plane is a large one
MIN_ANGLE = math.radians(12)  # nor two planes closer in tilt than this: they would read as one bent plane
DRAWS = 60  # how often each cut is drawn
ROCKS = 40  # how many whole rocks one seed may draw before it is given up
SIDES = 9  # side planes round the footprint
SQUARENESS = 0.5  # the footprint, from an ellipse inside the bounds (0) to the bounds' own rectangle (1)
# The forms, in metres before the rock is stretched to its bounds, and the least area (m2) each must leave its planes.
STEP_RISE = (0.38, 0.46)  # how far the shelf sits below the raised slab
STEP_RISER_M2, STEP_TREAD_M2, SUMMIT_M2 = 0.7, 0.9, 1.3
FRACTURE_DEPTH, FRACTURE_FOOT, FRACTURE_MOUTH = (0.5, 0.75), (0.3, 0.42), (0.3, 0.42)  # into the rock at the top and at the ground; along the rim
FRACTURE_WALL_M2 = 0.7
SHOULDER_LEVEL, SHOULDER_DEPTH = (0.4, 0.55), (0.5, 0.85)  # the shelf's height as a share of the rock's; how far in its wall stands
SHOULDER_RISER_M2, SHOULDER_TREAD_M2 = 0.7, 0.7
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


def notch(bm, corner, first, second):
    """Remove the part of the rock that is in front of both planes through `corner`.

    `first` and `second` are the planes' unit normals; `corner` is a point on
    the line where they meet. Done with an exact boolean against a skewed
    box, the one operation here that leaves an inward corner.
    """
    reach = 10.0
    along = first.cross(second).normalized()
    # The box's edges lie in the two planes: one runs up the first, one out along the second.
    out, up = second.cross(along), along.cross(first)
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


def area_on(bm, point, normal):
    """The area of the mesh's faces that lie on the plane through `point` facing `normal`."""
    return sum(f.calc_area() for f in bm.faces if f.normal.dot(normal) > 1 - 1e-5 and abs((f.calc_center_median() - point).dot(normal)) < FLAT)


def surface(bm, azimuth, height):
    """Where a level line from outside, aimed at the rock's middle from `azimuth`, meets it: (point, the plane's normal)."""
    out = leaning(azimuth, 0)
    point, normal, _, _ = BVHTree.FromBMesh(bm).ray_cast(out * 10 + Z * height, -out)
    return point, normal


def unbevelable(bm, min_edge=None):
    """Why the mesh cannot take soft edges, or None: it must be closed, with every plane big and distinct enough."""
    min_edge = min_edge or MIN_EDGE
    bm.normal_update()
    if not bm.faces or any(not e.is_manifold for e in bm.edges):
        return "not a closed solid"
    if any(e.calc_length() < min_edge for e in bm.edges):
        return f"an edge shorter than {min_edge} m"
    if any(e.calc_face_angle() < MIN_ANGLE for e in bm.edges):
        return f"two planes within {math.degrees(MIN_ANGLE):.0f} degrees"
    # What the bevel leaves of a plane: its area less a strip along its border.
    if any(f.calc_area() - BEVEL * f.calc_perimeter() < MIN_PLANE_M2 for f in bm.faces if f.normal.z > -0.999):
        return f"a plane under {MIN_PLANE_M2} m2 once bevelled"
    return None


def attempt(bm, rng, draw, what):
    """Apply one drawn cut. Returns the new mesh and what the cut says must be kept.

    `draw` cuts a copy of the mesh and returns why the cut will not do (a
    string), or the planes it made that later cuts must not eat (a list). The
    cut is drawn DRAWS times and, of the draws that fit, the one that leaves
    the longest shortest edge is kept: the most room for the cuts still to
    come. A cut that never fits fails the build, with what stopped it.
    """
    best, reasons = None, {}
    for _ in range(DRAWS):
        trial = bm.copy()
        result = draw(trial, rng)
        reason = result if isinstance(result, str) else unbevelable(trial)
        if reason is None:
            room = min(e.calc_length() for e in trial.edges)
            if best is None or room > best[0]:
                best, trial = (room, trial, result), (best[1] if best else None)
        else:
            reasons[reason] = reasons.get(reason, 0) + 1
        if trial:
            trial.free()
    if best is None:
        tally = ", ".join(f"{reason} ({count})" for reason, count in sorted(reasons.items(), key=lambda item: -item[1]))
        raise RuntimeError(f"no room for {what} in {DRAWS} draws: {tally}")
    bm.free()
    return best[1], best[2]


def fit(bm, lo, hi):
    """Stretch the mesh so its bounding box is exactly lo..hi."""
    have_lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    have_hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    for vert in bm.verts:
        vert.co = Vector(lo[i] + (vert.co[i] - have_lo[i]) / (have_hi[i] - have_lo[i]) * (hi[i] - lo[i]) for i in range(3))


def chisel(lo, hi, rng):
    """The rock as exact planes with hard edges: one face per plane."""
    half = (hi - lo) / 2
    height = hi.z - lo.z
    bm = bmesh.new()
    # Larger than the rock, so that the cuts remove every face of the block.
    bmesh.ops.create_cube(bm, size=1.0)
    for vert in bm.verts:
        vert.co = Vector((vert.co.x * half.x * 3.2, vert.co.y * half.y * 3.2, (vert.co.z + 0.5) * height * 1.5))

    def foot(azimuth, scale):
        """How far out the footprint reaches at `azimuth`: between an ellipse and the bounds' rectangle."""
        c, s = math.cos(azimuth), math.sin(azimuth)
        ellipse, rectangle = math.hypot(half.x * c, half.y * s), half.x * abs(c) + half.y * abs(s)
        return leaning(azimuth, 0) * (ellipse + (rectangle - ellipse) * SQUARENESS) * scale

    # The sides, numbered round the rock from a random start, either way round, each a little
    # wider or narrower than the next. The forms are placed by side number, so that each has
    # rim to itself: the step runs from side 0 to side 3, the fracture opens the corner between
    # sides 4 and 5, and the shoulder is cut across side 7. That puts the three about a third
    # of the way round from each other, and every side of the rock shows one.
    turn, hand = rng.uniform(0, math.tau), rng.choice((-1, 1))
    widths = [rng.uniform(0.92, 1.1) for _ in range(SIDES)]
    facing = [turn + hand * math.tau * (sum(widths[:i]) + widths[i] / 2) / sum(widths) for i in range(SIDES)]

    def summit(trial):
        return max(trial.faces, key=lambda f: f.normal.z)

    def side(trial, i):
        sides = [f for f in trial.faces if abs(f.normal.z) < 0.5 and any(abs(v.co.z) < FLAT for v in f.verts)]
        return max(sides, key=lambda f: f.normal.dot(leaning(facing[i], 0)))

    def shared(a, b):
        return next((e for e in a.edges if b in e.link_faces), None)

    kept = []  # (what, point, normal, least area) of planes that later cuts must not eat

    def spoiled(trial, new=()):
        """Why a cut will not do: it left a form's plane too small. Otherwise, the planes to keep from now on."""
        for what, point, normal, least in kept + list(new):
            if area_on(trial, point, normal) < least:
                return f"leaves {what} under {least} m2"
        return list(new)

    def carve(draw, what):
        nonlocal bm
        bm, new = attempt(bm, rng, draw, what)
        kept.extend(new)

    # The body: a tipped top, and sides that lean in toward the top by different amounts, slight
    # and steeper by turns. The base is the widest part and the top is still broad.
    def body(trial, r):
        slice_through(trial, Z * height * 0.95, leaning(r.uniform(0, math.tau), math.radians(r.uniform(84, 87.5))))
        for i in range(SIDES):
            lean = r.uniform(2, 7) if i % 2 else r.uniform(8, 13)
            slice_through(trial, foot(facing[i], r.uniform(0.98, 1.03)), leaning(facing[i], math.radians(lean)))
        return unbevelable(trial, BODY_EDGE) or []

    carve(body, "the body")

    # The step: a notch in the top that leaves a raised slab above a lower shelf. The riser runs
    # from the rim of side 0 to the rim of side 3 and leans back from the shelf, as a fracture
    # does; the shelf falls away from it, over sides 1 and 2.
    def step(trial, r):
        top = summit(trial)
        centre, top_normal = top.calc_center_median(), top.normal.copy()
        rims = [shared(side(trial, i), top) for i in (0, 3)]
        if None in rims:
            return "a side does not reach the top"
        start, end = (e.verts[0].co.lerp(e.verts[1].co, r.uniform(0.35, 0.65)) for e in rims)
        along = (end - start).normalized()
        outward = along.cross(Z).normalized()
        outward *= 1 if outward.dot(leaning(facing[1], 0) + leaning(facing[2], 0)) > 0 else -1
        lean = math.radians(r.uniform(10, 20))
        riser = outward * math.cos(lean) + Z * math.sin(lean)
        riser = (riser - along * riser.dot(along)).normalized()
        fall, roll = math.radians(r.uniform(3, 8)), math.radians(r.uniform(-4, 4))
        tread = (Z * math.cos(fall) + outward * math.sin(fall) + along * math.sin(roll)).normalized()
        down = (riser * riser.z - Z).normalized()  # straight down the riser
        corner = (start + end) / 2 + down * (r.uniform(*STEP_RISE) / -down.z)
        notch(trial, corner, riser, tread)
        return spoiled(trial, [("the step's riser", corner, riser, STEP_RISER_M2), ("the step's shelf", corner, tread, STEP_TREAD_M2), ("the raised slab", centre, top_normal, SUMMIT_M2)])

    carve(step, "the step")

    # The fracture: the corner between sides 4 and 5 split open into a V-shaped groove, widest
    # and deepest at the top and narrow at the ground. Each wall runs from a point on the rim, a
    # little along from the corner, to the groove's line, which leans into the rock.
    def fracture(trial, r):
        edge = shared(side(trial, 4), side(trial, 5))
        if edge is None:
            return "sides 4 and 5 do not meet"
        low, high = sorted(edge.verts, key=lambda v: v.co.z)
        if len(high.link_edges) != 3 or len(low.link_edges) != 3 or low.co.z > FLAT:
            return "the corner does not run from the ground to the rim"
        # At each end: the two edges that leave the corner, one along each side.
        rim = [e.other_vert(high).co - high.co for e in high.link_edges if e is not edge]
        ground = [e.other_vert(low).co - low.co for e in low.link_edges if e is not edge]
        top_in = high.co + sum((v.normalized() for v in rim), Vector()).normalized() * r.uniform(*FRACTURE_DEPTH)
        low_in = low.co + sum((v.normalized() for v in ground), Vector()).normalized() * r.uniform(*FRACTURE_FOOT)
        walls = []
        for along in rim:
            mouth = high.co + along.normalized() * min(r.uniform(*FRACTURE_MOUTH), along.length - MIN_EDGE - 0.1)
            normal = (top_in - mouth).cross(low_in - mouth).normalized()
            walls.append(normal if normal.dot(high.co - top_in) > 0 else -normal)
        notch(trial, top_in, *walls)
        return spoiled(trial, [("a wall of the fracture", top_in, wall, FRACTURE_WALL_M2) for wall in walls])

    carve(fracture, "the fracture")

    # The shoulder: a bench across side 7, a shelf at about half height with a wall behind it.
    # The wall leans back, so it takes little of the rim.
    def shoulder(trial, r):
        normal = side(trial, 7).normal
        azimuth = math.atan2(normal.y, normal.x)
        point, _ = surface(trial, azimuth, height * r.uniform(*SHOULDER_LEVEL))
        outward = leaning(azimuth, 0)
        fall, roll = math.radians(r.uniform(4, 9)), math.radians(r.uniform(-4, 4))
        tread = (Z * math.cos(fall) + outward * math.sin(fall) + leaning(azimuth + math.pi / 2, 0) * math.sin(roll)).normalized()
        riser = leaning(azimuth + math.radians(r.uniform(-5, 5)), math.radians(r.uniform(16, 22)))
        corner = point - outward * r.uniform(*SHOULDER_DEPTH)
        notch(trial, corner, riser, tread)
        return spoiled(trial, [("the shoulder's wall", corner, riser, SHOULDER_RISER_M2), ("the shoulder's shelf", corner, tread, SHOULDER_TREAD_M2)])

    carve(shoulder, "the shoulder")
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


def unmet(bm, spec):
    """What the spec asks of the shape and this mesh does not give, as the gate's own failure lines."""
    checks = Checks("build", "rock")
    conv = conventions()
    with contextlib.redirect_stdout(io.StringIO()):
        check_planes(checks, "rock", bm, spec, conv)
        check_fullness(checks, "rock", bm, spec, conv)
    triangles = sum(len(f.verts) - 2 for f in bm.faces)
    checks.check("budget.triangles", triangles <= spec["max_triangles"], f"{triangles} > {spec['max_triangles']}")
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def shape(spec, seed):
    """The softened rock for one seed, at the spec's bounds, as (mesh, plane tags).

    A seed draws whole rocks, one after another from the same generator, until
    one meets the spec. The gate measures the saved scene; this is the same
    measurement made early, so that a seed that cannot pass stops here with
    the reasons instead of shipping a lesser rock.
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    rng = random.Random(seed)
    refused = []
    for take in range(1, ROCKS + 1):
        try:
            bm = chisel(lo, hi, rng)
        except RuntimeError as error:
            refused.append(f"rock {take}: {error}")
            continue
        fit(bm, lo, hi)
        tag = soften(bm)
        fit(bm, lo, hi)
        # Triangulation hands its faces back in an order that changes from run to run. The
        # shape is the same, but the exported file is not; put the faces in a fixed order.
        for index, face in enumerate(sorted(bm.faces, key=lambda face: tuple(round(c, 5) for c in face.calc_center_median()))):
            face.index = index
        bm.faces.sort()
        bm.normal_update()
        problems = unmet(bm, spec)
        if not problems:
            print(f"rock seed {seed}: rock {take} of up to {ROCKS} meets the spec")
            return bm, tag
        refused.append(f"rock {take}: " + "; ".join(problems))
        bm.free()
    raise RuntimeError(f"rock seed {seed}: none of its {ROCKS} rocks meets the spec:\n  " + "\n  ".join(refused))


def build(spec, seed=SEED):
    bm, tag = shape(spec, seed)
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
