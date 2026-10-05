"""Rock: a boulder of several lumps pushed together into one closed mesh.

Every surface is a deliberate plane (ADR 9); nothing is displaced by noise.
Each piece is the convex hull of a few points scattered in a squashed
ellipsoid: a lump of flat planes of clearly different sizes and tilts, which
bulges, so it is widest above the ground and nothing in it is upright or
level by rule. Each is cut off at the ground, so it sits in the ground and
not on it. The habits of docs/style/rock-shapes.md, as the script applies them:

1. Several pieces with a clear size order: one dominant lump that fills most
   of the bounds, a high and a low secondary lump pushed a third of the way
   into its sides, and two small low ones against its base. An exact
   boolean union joins them into one closed surface.
2. Nothing upright: the dominant lump's long axis is tipped, so the whole
   mass leans, and its highest point is off the middle.
3. A foot: the small lumps reach out past the base.
4. Chamfers come from the hulls themselves: a point a little inside a corner
   makes a plane across it.

A seed draws whole rocks, one after another, until one meets the spec, and
fails the build with the reasons when none does. Nothing is left out
silently. What the pieces are is recorded beside the mesh (a text
data-block, `rock.pieces`) for tools/validate.py to hold against the mesh.
Each larger lump is softened on its own, before the union, by a one-segment
bevel whose strips blend between the normals of the planes on either side, so
each plane is lit flat and each edge is lit round; where lumps meet, and on
the small ones, the faces round a corner share one normal. The finished mesh is stretched to the spec's bounds. Run
through tools/build.py.
"""

import contextlib
import io
import json
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector
from pipeline import Checks, conventions, linear_rgb
from validate import check_chamfers, check_foot, check_fullness, check_lean, check_pieces, check_planes

SEED = 1  # the shipped rock; see the brief for how it was chosen
SOFT_PLANE_M2 = 0.004  # a lump has no plane smaller than this once its soft edges have eaten its border
SOFT_EDGE = 4  # a lump has no edge shorter than this many times the width of its soft edge
MIN_EDGE = 0.002  # the joined pieces may not leave an edge shorter than this, metres: next to nothing
MIN_PLANE_M2 = 0.00001  # nor a face smaller than this
ROCKS = 12  # how many whole rocks one seed may draw before it is given up
DRAWS = 80  # how often each piece is drawn
FLAT = 1e-4  # tolerance for "on this plane"
PLANE_OWNS = 0.25  # a vertex takes its one plane's normal when every face round it agrees with that plane at least this much (cosine)
FACING = 0.02  # the least a soft edge's normal may agree with the face it is on (cosine); the load test fails at 0, lit from behind

Z = Vector((0, 0, 1))

# The pieces, largest first. Each is the hull of `points` points in an ellipsoid whose radii
# are `radii`, as shares of the bounds' half width, half depth and height. The dominant one
# stands on the middle; each of the others is pushed into its side: `at` is where round it, in
# degrees on from the high secondary, give or take `stray`; `out` how far from the middle its
# centre is, as a share of the dominant lump's own reach that way (1 is on its surface); `up`
# how high its centre is, as a share of the bounds' height. A lump's centre is below its
# middle, so the ground cuts it where it is still widening. `soft` is how far a
# lump's soft edge eats into each plane beside it, metres: less on the small ones.
PIECES = (
    dict(name="dominant", points=10, radii=(0.98, 0.98, 0.72), up=0.28, soft=0.05),
    dict(name="high secondary", points=7, radii=(0.48, 0.52, 0.36), at=0, stray=25, out=(0.46, 0.6), up=0.5, soft=0.05),
    dict(name="low secondary", points=6, radii=(0.44, 0.48, 0.3), at=150, stray=25, out=(0.62, 0.76), up=0.12, soft=0.05),
    dict(name="first foot", points=6, radii=(0.38, 0.42, 0.11), at=255, stray=20, out=(0.8, 0.92), up=0.02, soft=0.03),
    dict(name="second foot", points=6, radii=(0.31, 0.35, 0.09), at=75, stray=20, out=(0.82, 0.94), up=0.02, soft=0.03),
)
SHELL = (0.9, 1.0)  # how far out in its ellipsoid each point lies: near the surface, so the hull keeps the ellipsoid's bulk
APART = 0.55  # no two points of a lump are closer in direction than this, radians: its planes are few and broad
CLEAR_OF_GROUND = 0.22  # no corner of a lump is nearer the ground than this share of the lump's vertical radius
TIP = (8, 14)  # how far the dominant lump's long axis is tipped from level, degrees


def lump(rng, plan, half, height, centre, turn, tip):
    """One piece: the convex hull of points scattered in a tipped ellipsoid, cut off at the ground, as
    (mesh, the record of the piece, its planes). None if the points will not do."""
    radii = Vector((half.x * plan["radii"][0], half.y * plan["radii"][1], height * plan["radii"][2]))
    directions = []
    for _ in range(400):
        if len(directions) == plan["points"]:
            break
        z = rng.uniform(-1, 1)
        angle = rng.uniform(0, math.tau)
        direction = Vector((math.sqrt(1 - z * z) * math.cos(angle), math.sqrt(1 - z * z) * math.sin(angle), z))
        if all(direction.angle(other) > APART for other in directions):
            directions.append(direction)
    if len(directions) < plan["points"]:
        return None
    spin = Matrix.Rotation(turn, 3, "Z") @ Matrix.Rotation(tip, 3, "Y")
    bm = bmesh.new()
    for direction in directions:
        reach = rng.uniform(*SHELL)
        point = centre + spin @ Vector((direction.x * radii.x, direction.y * radii.y, direction.z * radii.z)) * reach
        # A corner close to the ground, above it or below, would leave short edges where the ground cuts the lump.
        if abs(point.z) < CLEAR_OF_GROUND * radii.z:
            point.z = math.copysign(CLEAR_OF_GROUND * radii.z * rng.uniform(1.0, 1.5), point.z)
        bm.verts.new(point)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    cut = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(0, 0, 0), plane_no=(0, 0, 1), clear_inner=True)
    rim = [g for g in cut["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
    if len(rim) >= 3:
        bmesh.ops.holes_fill(bm, edges=rim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.verts.index_update()
    bm.normal_update()
    record = {"name": plan["name"], "vertices": [list(v.co) for v in bm.verts], "faces": [[v.index for v in f.verts] for f in bm.faces]}
    planes = [(f.normal.copy(), f.normal.dot(f.calc_center_median())) for f in bm.faces]
    if True:
        # A lump is softened on its own, before it is joined to the others: it is convex, with
        # edges of a known least length, so the bevel always forms. Where lumps then meet, the
        # corner between them is lit round by its normals alone (corner_normals).
        width = plan["soft"]
        if any(e.calc_length() < SOFT_EDGE * width for e in bm.edges) or any(f.calc_area() - width * f.calc_perimeter() < SOFT_PLANE_M2 for f in bm.faces):
            bm.free()
            return None
        edges = [e for e in bm.edges if not all(abs(v.co.z) < FLAT for v in e.verts)]
        bmesh.ops.bevel(bm, geom=edges, offset=width, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES", clamp_overlap=True)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.normal_update()
    return bm, record, planes


def union(solids):
    """Join solids into one closed surface with the exact boolean, one face per plane."""
    scene = bpy.context.scene
    temporary = []
    for index, source in enumerate(solids):
        mesh = bpy.data.meshes.new(f"rock_piece_{index}")
        source.to_mesh(mesh)
        obj = bpy.data.objects.new(mesh.name, mesh)
        scene.collection.objects.link(obj)
        temporary.append(obj)
    whole = temporary[0]
    for other in temporary[1:]:
        modifier = whole.modifiers.new(other.name, "BOOLEAN")
        modifier.operation, modifier.solver, modifier.object = "UNION", "EXACT", other
    bm = bmesh.new()
    bm.from_object(whole, bpy.context.evaluated_depsgraph_get())
    for obj in temporary:
        mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)
    # The solver leaves coplanar pieces; put each plane back as one face. The underside first:
    # every piece stands on the ground, so it is one outline, filled again as one face.
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(abs(v.co.z) < FLAT for v in f.verts)], context="FACES")
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts, edges=bm.edges)
    # A vertex left part of the way along a straight edge supports nothing.
    bmesh.ops.dissolve_verts(bm, verts=[v for v in bm.verts if len(v.link_edges) == 2])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def unjoined(bm):
    """Why the mesh will not do as it stands, or None."""
    bm.normal_update()
    if not bm.faces or any(not e.is_manifold for e in bm.edges):
        return "not a closed solid"
    reached, front = {bm.verts[:][0]}, [bm.verts[:][0]]
    while front:
        for edge in front.pop().link_edges:
            other = edge.verts[0] if edge.verts[1] in reached else edge.verts[1]
            if other not in reached:
                reached.add(other)
                front.append(other)
    if len(reached) != len(bm.verts):
        return "pieces that do not touch"
    if any(e.calc_length() < MIN_EDGE for e in bm.edges):
        return f"an edge shorter than {MIN_EDGE} m"
    if any(f.calc_area() < MIN_PLANE_M2 for f in bm.faces):
        return f"a plane under {MIN_PLANE_M2} m2"
    return None


def fit(bm, lo, hi):
    """Stretch the mesh so its bounding box is exactly lo..hi. Returns the stretch as (scale, shift) per axis."""
    have_lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    have_hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    scale = [(hi[i] - lo[i]) / (have_hi[i] - have_lo[i]) for i in range(3)]
    shift = [lo[i] - have_lo[i] * scale[i] for i in range(3)]
    for vert in bm.verts:
        vert.co = Vector(vert.co[i] * scale[i] + shift[i] for i in range(3))
    return scale, shift


def on_ground(face):
    return face.normal.z < -0.999 and all(abs(v.co.z) < FLAT for v in face.verts)


def tag_planes(bm, planes):
    """Mark each face with the plane it lies on (0 for the strip of a soft edge), and cut faces of more than four sides into triangles. They stay coplanar."""
    bm.normal_update()
    tag = bm.faces.layers.int.new("plane")
    for face in bm.faces:
        centre = face.calc_center_median()
        face[tag] = next((i + 1 for i, (normal, offset) in enumerate(planes) if face.normal.dot(normal) > 1 - 1e-6 and abs(normal.dot(centre) - offset) < FLAT), 0)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4], quad_method="BEAUTY", ngon_method="BEAUTY")
    return tag


def corner_normals(bm, tag):
    """One normal per face corner, and the same one for every face round a vertex, which is
    what makes every edge soft.

    Where a vertex touches one plane and the strips beside it, that normal is the plane's: the
    plane is lit flat and the strip blends to the next plane. Anywhere else (where two lumps
    meet, and all over a lump too small to bevel) it is the normals of the faces round the
    vertex, weighted by their area and their angle there. The underside keeps its own normal:
    the rock meets the ground at a hard edge."""
    bm.normal_update()
    shared = {}
    for vert in bm.verts:
        faces = [f for f in vert.link_faces if not on_ground(f)]
        planes = {f[tag]: f.normal for f in faces if f[tag]}
        only = next(iter(planes.values())) if len(planes) == 1 else None
        # One plane, and nothing round the vertex turned far from it: a strip of another lump's soft edge can end here too.
        if only is not None and all(f.normal.dot(only) > PLANE_OWNS for f in faces):
            shared[vert] = only.copy()
            continue
        total = sum((loop.face.normal * loop.face.calc_area() * loop.calc_angle() for loop in vert.link_loops if not on_ground(loop.face)), Vector())
        shared[vert] = total.normalized() if total.length > 1e-9 else None
    return [face.normal.copy() if on_ground(face) or shared[loop.vert] is None else shared[loop.vert] for face in bm.faces for loop in face.loops]


def lit_from_behind(bm, tag):
    """Faces with a corner normal that faces against the face itself: the engine would light them wrongly."""
    normals = iter(corner_normals(bm, tag))
    return sum(1 for face in bm.faces if min([next(normals).dot(face.normal) for _ in face.loops]) <= FACING)


def unmet(bm, tag, record, spec):
    """What the spec asks of the shape and this mesh does not give, as the gate's own failure lines."""
    checks = Checks("build", "rock")
    conv = conventions()
    with contextlib.redirect_stdout(io.StringIO()):
        check_fullness(checks, "rock", bm, spec, conv)
        check_planes(checks, "rock", bm, spec, conv)
        check_pieces(checks, "rock", bm, spec, conv, record)
        check_foot(checks, "rock", bm, spec, conv)
        check_chamfers(checks, "rock", bm, spec, conv)
        check_lean(checks, "rock", bm, spec, conv)
    triangles = sum(len(f.verts) - 2 for f in bm.faces)
    checks.check("budget.triangles", triangles <= spec["max_triangles"], f"{triangles} > {spec['max_triangles']}")
    # What the Bevy load test would find later (crates/asset_smoke): caught here, where the rock can still be redrawn.
    behind = lit_from_behind(bm, tag)
    checks.check("rock.normals_with_winding", behind == 0, f"{behind} faces would be lit from behind")
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def shape(spec, seed):
    """The rock for one seed, at the spec's bounds, as (mesh, the pieces it is made of).

    A seed draws whole rocks, one after another from the same generator, until
    one meets the spec. The gate measures the saved scene; this is the same
    measurement made early, so that a seed that cannot pass stops here with
    the reasons instead of shipping a lesser rock.
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    half, height = (hi - lo) / 2, hi.z - lo.z
    rng = random.Random(seed)
    refused = []
    for take in range(1, ROCKS + 1):
        start, hand = rng.uniform(0, math.tau), rng.choice((-1, 1))
        # The pieces are pushed together one at a time, largest first. Each is redrawn until
        # it joins what is there without leaving a sliver.
        bm, record, planes = None, [], []
        for plan in PIECES:
            tally = {}
            for _ in range(DRAWS):
                if bm is None:
                    centre, turn, tip = Vector((0, 0, height * plan["up"])), rng.uniform(0, math.tau), math.radians(rng.uniform(*TIP))
                    reach = (half.x * plan["radii"][0], half.y * plan["radii"][1])
                else:
                    at = start + hand * math.radians(plan["at"] + rng.uniform(-plan["stray"], plan["stray"]))
                    far = rng.uniform(*plan["out"]) / math.hypot(math.cos(at) / reach[0], math.sin(at) / reach[1])
                    centre, turn, tip = Vector((math.cos(at) * far, math.sin(at) * far, height * plan["up"])), rng.uniform(0, math.tau), math.radians(rng.uniform(-12, 12))
                drawn = lump(rng, plan, half, height, centre, turn, tip)
                if drawn is None:
                    tally["a lump with an edge or a plane too small to soften"] = tally.get("a lump with an edge or a plane too small to soften", 0) + 1
                    continue
                part, described, flat = drawn
                joined = union([bm, part]) if bm else part.copy()
                reason = unjoined(joined)
                if reason is None:
                    record.append(described)
                    planes.extend(flat)
                    part.free()
                    break
                tally[reason] = tally.get(reason, 0) + 1
                part.free()
                joined.free()
            else:
                reasons = ", ".join(f"{reason} ({count})" for reason, count in sorted(tally.items(), key=lambda item: -item[1]))
                refused.append(f"rock {take}: no room for the {plan['name']} in {DRAWS} draws: {reasons}")
                break
            if bm:
                bm.free()
            bm = joined
        if len(record) < len(PIECES):
            if bm:
                bm.free()
            continue
        tag = tag_planes(bm, planes)
        scale, shift = fit(bm, lo, hi)
        for part in record:
            part["vertices"] = [[c * scale[i] + shift[i] for i, c in enumerate(co)] for co in part["vertices"]]
        # Triangulation hands its faces back in an order that changes from run to run. The
        # shape is the same, but the exported file is not; put the faces in a fixed order.
        for index, face in enumerate(sorted(bm.faces, key=lambda face: tuple(round(c, 5) for c in face.calc_center_median()))):
            face.index = index
        bm.faces.sort()
        bm.normal_update()
        problems = unmet(bm, tag, record, spec)
        if not problems:
            print(f"rock seed {seed}: rock {take} of up to {ROCKS} meets the spec")
            return bm, tag, record
        refused.append(f"rock {take}: " + "; ".join(problems))
        bm.free()
    raise RuntimeError(f"rock seed {seed}: none of its {ROCKS} rocks meets the spec:\n  " + "\n  ".join(refused))


def build(spec, seed=SEED):
    bm, tag, record = shape(spec, seed)
    normals = corner_normals(bm, tag)
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
    # What the rock is made of, for the gate to hold against the mesh (tools/validate.py, check_pieces).
    text = bpy.data.texts.get("rock.pieces") or bpy.data.texts.new("rock.pieces")
    text.clear()
    text.write(json.dumps([{**part, "vertices": [[round(c, 6) for c in co] for co in part["vertices"]]} for part in record]))
    return obj
