"""Rock: a boulder of several plane-cut pieces pushed together into one closed mesh.

Every surface is a deliberate plane (ADR 9); nothing is displaced by noise.
The habits of docs/style/rock-shapes.md, as the script applies them:

1. Several pieces with a clear size order. One dominant piece, a tall and a
   low secondary piece set against it, and three small pieces at its foot.
   Each is a solid of its own, cut from a block by planes; an exact boolean
   union joins them into one closed surface.
2. Nothing upright. Every side in sight leans in, by its own amount, and the
   pieces' tops tip roughly the same way.
3. The tallest part is off-centre: the dominant piece stands in one corner of
   the bounds and the others gather round the opposite sides of it.
4. A foot: the small pieces sit low against the base and reach out past it.
5. Flat caps: every top is one gently tipped plane.
6. Long vertical edges: each wall of the dominant piece is folded down its
   length, and every piece stands astride one of that piece's upright edges.
7. Big chamfers: corners and a stretch of the dominant piece's rim are cut by
   planes wide enough to be faces of their own.

A seed draws whole rocks, one after another, until one meets the spec, and
fails the build with the reasons when none does. Nothing is left out
silently. What the pieces are is recorded beside the mesh (a text
data-block, `rock.pieces`) for tools/validate.py to hold against the mesh.
Edges are softened by a one-segment bevel whose strips blend between the
normals of the planes on either side, so each plane is lit flat and each edge
is lit round. The finished mesh is stretched to the spec's bounds. Run
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

SEED = 5  # the shipped rock; see the brief for how it was chosen
BEVEL = 0.05  # how far a soft edge eats into each plane beside it, metres
MIN_EDGE = 0.15  # the joined pieces may not leave an edge shorter than this
MIN_ANGLE = math.radians(12)  # nor two planes closer in tilt than this: they would read as one bent plane
MIN_PLANE_M2 = 0.012  # nor a plane smaller than this once the bevel has eaten its border
ROCKS = 200  # how many whole rocks one seed may draw before it is given up
DRAWS = 40  # how often each piece is drawn
CHAMFER_DRAWS = 12  # and each of its chamfers
MIN_LEAN = 9.0  # no side is drawn closer to upright than this, degrees
FLAT = 1e-4  # tolerance for "on this plane"
FACING = 0.02  # the least a soft edge's normal may agree with the face it is on (cosine); the load test fails at 0, lit from behind

Z = Vector((0, 0, 1))

# The pieces, largest first. The dominant piece stands in one corner of the bounds: it touches
# two of their sides and reaches `across` of the way over to the other two, which leaves an
# L-shaped strip of ground free. Each of the other pieces is set against the dominant piece
# astride one of its upright edges (`astride`: the two of its sides that meet there), so
# that the dominant piece falls away from it on both flanks: the tall secondary and the
# first foot on the strip's first side ("a"), the second and third foot on its second ("b"),
# and the low secondary at the corner behind ("far"), so that no side of the rock is bare.
# `out` is how far out the piece's centre is and `outer` how far out its outer side: from the
# middle of the bounds as shares of the way to their edge, or, behind, in metres from the
# edge it stands astride and from its own centre. `flank` is the range its flanks may stand
# from its centre, metres; where one flank has another piece beyond it (`crowded`: the one
# toward the strip's corner or the one toward its end), the other may reach `open`.
# Its back stands under the middle of the dominant piece, where that piece is widest, so the
# back stays inside it. `tall` is a piece's height as a share of the bounds'; `lean` the
# range its sides lean in by, degrees; `corners` and `rims` how many of its rim's corners
# and edges are cut by a chamfer.
PIECES = (
    dict(name="dominant", across=(0.84, 0.87), tall=(1.0, 1.0), sides=8, lean=(9.0, 12.0), corners=1, rims=2),
    dict(name="tall secondary", side="a", astride=(0, 1), crowded="end", out=(0.66, 0.7), outer=(0.96, 1.0), flank=(0.45, 0.62), open=(0.5, 0.8), tall=(0.66, 0.74), sides=4, lean=(9.0, 12), corners=0, rims=0),
    dict(name="low secondary", side="far", astride=(5, 6), out=(0.0, 0.06), outer=(0.26, 0.32), flank=(0.36, 0.5), tall=(0.44, 0.5), sides=4, lean=(10, 15), corners=0, rims=0),
    dict(name="first foot", side="a", astride=(7, 0), crowded="corner", out=(0.7, 0.74), outer=(0.95, 0.99), flank=(0.28, 0.36), open=(0.4, 0.52), tall=(0.25, 0.29), sides=4, lean=(10, 15), corners=0, rims=0),
    dict(name="second foot", side="b", astride=(2, 3), crowded="end", out=(0.7, 0.74), outer=(0.95, 0.99), flank=(0.28, 0.34), open=(0.45, 0.6), tall=(0.2, 0.24), sides=4, lean=(10, 15), corners=0, rims=0),
    dict(name="third foot", side="b", astride=(3, 4), crowded="corner", out=(0.72, 0.76), outer=(0.9, 0.94), flank=(0.22, 0.28), open=(0.24, 0.32), tall=(0.12, 0.15), sides=4, lean=(10, 18), corners=0, rims=0),
)
TOP_TILT = (6, 10)  # how far a piece's top tips from level, degrees
BURIED_LEAN = (3, 8)  # how far the back of a piece set against the dominant one tips outward, degrees
SQUARENESS = 0.55  # the dominant piece's footprint, from an ellipse (0) to a rectangle (1)
WALL_FOLD = (7, 17)  # each wall of the dominant piece is two faces, turned this far either way from square to the strip, degrees
FAR_SIDES, FAR_JITTER = (60, 104, 160, 210), 8  # where the dominant piece's far sides face, in degrees on from its second wall, and how far each may stray
ASTRIDE = 0.05  # how far to either side of its edge a piece's centre may stand, metres
CLEAR_OF_EDGE = 0.18  # a flank stands at least this far along from each upright edge of the dominant piece, metres
CLEAR_OF_SECONDARY = 1.0  # the dominant piece's chamfers keep this far round its rim from the tall secondary, radians
GROUP_LEAN = (0.5, 2)  # how much further the sides facing away from the group's lean tip in, degrees
CORNER_UP = 1.3  # how much more a corner's chamfer faces up than out: it takes the corner off the cap, not down the side
CORNER_DEPTH, RIM_DEPTH = (0.26, 0.36), (0.16, 0.22)  # how far below a corner or a rim its chamfer is cut, metres


def leaning(azimuth, lift):
    """A unit normal pointing out at `azimuth` about Z, raised `lift` above horizontal (radians)."""
    return Vector((math.cos(azimuth) * math.cos(lift), math.sin(azimuth) * math.cos(lift), math.sin(lift)))


def meeting(*planes):
    """The point where three planes (normal, offset) meet."""
    return Matrix([normal for normal, _ in planes]).inverted() @ Vector([offset for _, offset in planes])


def solid(planes):
    """The convex solid behind every plane (normal, offset): one face per plane that touches it."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=20.0)
    for normal, offset in planes:
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=normal * offset, plane_no=normal, clear_outer=True)
        rim = [g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
        if len(rim) >= 3:
            bmesh.ops.holes_fill(bm, edges=rim)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def clear_reach(rng, span, blocked):
    """A distance within `span`, drawn evenly from the parts of it outside every `blocked` stretch, or None when there is none."""
    free, start = [], span[0]
    for low, high in sorted(blocked):
        if low > start:
            free.append((start, min(low, span[1])))
        start = max(start, high)
    free.append((start, span[1]))
    free = [(low, high) for low, high in free if high > low]
    if not free:
        return None
    pick = rng.uniform(0, sum(high - low for low, high in free))
    for low, high in free:
        if pick <= high - low:
            return low + pick
        pick -= high - low
    return free[-1][1]


def piece(rng, plan, half, height, turn, hand, group, core, dominant):
    """One piece drawn from its line in PIECES: its planes (the ground, the top, then the sides
    in order round it), and which of its rim's corners may take a chamfer (corner i is where
    side i meets the next one). `turn` is which corner of the bounds the free strip of ground
    goes round, `hand` which of its two sides is the first, `core` the middle of the dominant piece
    and `dominant` that piece's planes. Returns (None, None) when the piece cannot be placed."""
    sides = plan["sides"]
    tall = height * rng.uniform(*plan["tall"])
    sign = Vector((1 if turn in (0, 3) else -1, 1 if turn in (0, 1) else -1, 0))  # the strip's corner
    if "side" in plan:
        # A piece set against the dominant one: an outer side, one on each flank, and a back
        # that faces into the dominant piece and ends up inside it, tipping outward: the piece
        # leans on the dominant one.
        first = (plan["side"] == "a") == (hand == 1)
        out = rng.uniform(*plan["out"])
        edge = meeting(dominant[2 + plan["astride"][0]], dominant[2 + plan["astride"][1]], (Z, 0.0))
        if plan["side"] == "far":
            at = math.atan2(edge.y - core.y, edge.x - core.x)
            centre = edge + leaning(at, 0) * out
            outer = rng.uniform(*plan["outer"])
        elif first:
            at = math.atan2(0, sign.x)
            centre = Vector((sign.x * half.x * out, edge.y + rng.uniform(-ASTRIDE, ASTRIDE), 0))
            outer = half.x * (rng.uniform(*plan["outer"]) - out)
        else:
            at = math.atan2(sign.y, 0)
            centre = Vector((edge.x + rng.uniform(-ASTRIDE, ASTRIDE), sign.y * half.y * out, 0))
            outer = half.y * (rng.uniform(*plan["outer"]) - out)
        facing = [at - rng.uniform(1.42, 1.72), at + rng.uniform(-0.25, 0.25), at + rng.uniform(1.42, 1.72), at + math.pi]
        reach = [None, outer, None]
        # Which flank has another piece beyond it, and so less room: the one toward the strip's
        # corner or the one away from it.
        toward_corner = [leaning(azimuth, 0).dot(sign) > 0 for azimuth in (facing[0], facing[2])]
        spans = [plan["flank"] if plan.get("crowded") in (None, "corner" if corner_side else "end") else plan["open"] for corner_side in toward_corner]
        spans = [spans[0], None, spans[1]]
        buried, free = sides - 1, {True: [0, 1], False: [0]}
    else:
        # The dominant piece. A wall faces each side of the strip, folded down its length
        # into two faces of unequal width; four more sides go round the far part, where the
        # piece touches the bounds, and the chamfers are cut there.
        centre = core
        radii = [half.x - abs(core.x), half.y - abs(core.y)]
        first, second = math.atan2(0, sign.x), math.atan2(sign.y, 0)
        if hand != 1:
            first, second = second, first
        way = 1 if math.remainder(second - first, math.tau) > 0 else -1
        fold = [math.radians(rng.uniform(*WALL_FOLD)) for _ in range(4)]
        facing = [first - way * fold[0], first + way * fold[1], second - way * fold[2], second + way * fold[3]]
        facing += [second + way * math.radians(turned + rng.uniform(-FAR_JITTER, FAR_JITTER)) for turned in FAR_SIDES]
        through = []
        for azimuth in facing:
            # How far out a side stands: between an ellipse inside the dominant piece's share of the bounds (0) and that share's own rectangle (1).
            round_, square = math.hypot(radii[0] * math.cos(azimuth), radii[1] * math.sin(azimuth)), radii[0] * abs(math.cos(azimuth)) + radii[1] * abs(math.sin(azimuth))
            through.append(centre + leaning(azimuth, 0) * (round_ + (square - round_) * SQUARENESS) * rng.uniform(0.96, 1.0))
        # The chamfers are cut toward the strip, above the pieces set there: the corner where the
        # two walls meet, and the rims of the faces either side of it. That leaves the cap's
        # highest part on the far side, off the middle of the bounds.
        buried, free = None, {True: [1], False: [0, 1]}
    faces = []
    for i, azimuth in enumerate(facing):
        # Each side leans in by its own amount; the ones facing away from the way the group leans tip in a little more.
        lean = max(MIN_LEAN, rng.uniform(*plan["lean"]) - rng.uniform(*GROUP_LEAN) * math.cos(azimuth - group))
        if i == buried:
            lean = -rng.uniform(*BURIED_LEAN)
        normal = leaning(azimuth, math.radians(lean))
        if buried is None:
            faces.append((normal, normal.dot(through[i])))
        elif i == buried:
            faces.append((normal, normal.dot(core)))
        else:
            far = reach[i]
            if far is None:
                # A flank: stood clear of every upright edge of the dominant piece on this side of
                # it, at the ground and at this piece's height. A flank that meets the dominant
                # piece close to one of its edges leaves a sliver between them too thin to bevel.
                out = leaning(at, 0)
                sides_of = dominant[2 : 2 + PIECES[0]["sides"]]
                corners = [meeting(side, sides_of[(j + 1) % len(sides_of)], (Z, level)) for level in (0.0, tall) for j, side in enumerate(sides_of)]
                level = math.cos(math.radians(lean))
                blocked = [((normal.dot(corner - centre) - CLEAR_OF_EDGE) / level, (normal.dot(corner - centre) + CLEAR_OF_EDGE) / level) for corner in corners if (corner - core).dot(out) > 0]
                far = clear_reach(rng, spans[i], blocked)
                if far is None:
                    return None, None
            faces.append((normal, normal.dot(centre + leaning(azimuth, 0) * far)))
    # The tops tip roughly the same way: down toward the strip's corner, so the dominant piece is highest on its far side.
    cap = leaning(math.atan2(sign.y, sign.x) + rng.uniform(-0.6, 0.6), math.radians(90 - rng.uniform(*TOP_TILT)))
    top = (cap, cap.dot(centre + Z * tall))
    return [(-Z, 0.0), top] + faces, free


def chamfer(rng, planes, free, corner):
    """A plane cutting a corner of a piece's rim (facing between the top and the two sides
    that meet there), or a stretch of the rim (facing between the top and one side)."""
    top, faces = planes[1], planes[2:]
    i = rng.choice(free[corner])
    first, second = faces[i], faces[(i + 1) % len(faces)]
    where = meeting(top, first, second)
    if corner:
        normal, depth = (first[0] + second[0] + top[0] * CORNER_UP).normalized(), rng.uniform(*CORNER_DEPTH)
    else:
        normal, depth = (second[0] + top[0]).normalized(), rng.uniform(*RIM_DEPTH)
    return (normal, normal.dot(where) - depth)


def chamfered(rng, plan, planes, free):
    """One piece as a solid: its planes, then its chamfers one at a time, each redrawn until it
    cuts a face of its own and swallows none. The dominant piece must also take soft edges as it
    stands; the others are held to that once they are joined to it, since part of each is buried.
    None when the piece itself, or a chamfer, will not do."""
    alone = plan is PIECES[0]
    part = solid(planes)
    if len(part.faces) != len(planes) or (alone and unbevelable(part)) or (plan["corners"] + plan["rims"] and not free):
        part.free()
        return None
    cuts = []
    for corner in [True] * plan["corners"] + [False] * plan["rims"]:
        for _ in range(CHAMFER_DRAWS):
            cuts.append(chamfer(rng, planes, free, corner))
            cut = solid(planes + cuts)
            if len(cut.faces) == len(part.faces) + 1 and not (alone and unbevelable(cut)):
                break
            cut.free()
            cuts.pop()
        else:
            part.free()
            return None
        part.free()
        part = cut
    return part


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


def unbevelable(bm):
    """Why the joined mesh cannot take soft edges, or None."""
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
    if any(f.normal.z < -0.02 and not all(abs(v.co.z) < FLAT for v in f.verts) for f in bm.faces):
        return "an overhanging side in sight"
    if any(len(v.link_edges) != 3 for v in bm.verts):
        return "a corner where more than three planes meet"
    if any(e.calc_length() < MIN_EDGE for e in bm.edges):
        return f"an edge shorter than {MIN_EDGE} m"
    if any(e.calc_face_angle() < MIN_ANGLE for e in bm.edges):
        return f"two planes within {math.degrees(MIN_ANGLE):.0f} degrees"
    # What the bevel leaves of a plane: its area less a strip along its border.
    if any(f.calc_area() - BEVEL * f.calc_perimeter() < MIN_PLANE_M2 for f in bm.faces if f.normal.z > -0.999):
        return f"a plane under {MIN_PLANE_M2} m2 once bevelled"
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
    normal of the plane each corner touches, so the strip blends from one plane to the next.

    Every face round a vertex gets the same blend there, which is what makes the edge soft. In
    an inward corner that blend can face away from a little bevel face; lit_from_behind()
    counts those, and a rock that has any is refused. (Turning the normal toward the face
    instead would give that vertex two normals: a hard edge, which the load test also fails.)"""
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


def lit_from_behind(bm, tag):
    """Bevel faces with a corner normal that faces against the face itself: the engine would light them wrongly."""
    normals = iter(plane_normals(bm, tag))
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
    hard = sum(1 for e in bm.edges if len(e.link_faces) == 2 and all(f[tag] for f in e.link_faces) and e.link_faces[0][tag] != e.link_faces[1][tag] and not all(abs(v.co.z) < FLAT for v in e.verts))
    checks.check("rock.soft_edges", hard == 0, f"{hard} edges between planes were left hard: the bevel had no room")
    behind = lit_from_behind(bm, tag)
    checks.check("rock.normals_with_winding", behind == 0, f"{behind} soft-edge faces would be lit from behind")
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def shape(spec, seed):
    """The softened rock for one seed, at the spec's bounds, as (mesh, plane tags, the pieces it is made of).

    A seed draws whole rocks, one after another from the same generator, until
    one meets the spec. The gate measures the saved scene; this is the same
    measurement made early, so that a seed that cannot pass stops here with
    the reasons instead of shipping a lesser rock.
    """
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    half, height = (hi - lo) / 2, hi.z - lo.z
    rng = random.Random(seed)
    refused, measured = [], 0
    for take in range(1, ROCKS + 1):
        turn, hand = rng.randrange(4), rng.choice((-1, 1))
        group = rng.uniform(0, math.tau)
        # The pieces are pushed together one at a time, largest first. Each is redrawn until
        # it joins what is there without leaving an edge too short to bevel.
        bm, record, tally = None, [], {}
        across = [rng.uniform(*PIECES[0]["across"]) for _ in range(2)]
        sign = Vector((1 if turn in (0, 3) else -1, 1 if turn in (0, 1) else -1, 0))
        core = Vector((-sign.x * half.x * (1 - across[0]), -sign.y * half.y * (1 - across[1]), 0))
        for plan in PIECES:
            for _ in range(DRAWS):
                planes, free = piece(rng, plan, half, height, turn, hand, group, core, dominant if bm else None)
                if planes is None:
                    tally["no place for a flank clear of the dominant piece's edges"] = tally.get("no place for a flank clear of the dominant piece's edges", 0) + 1
                    continue
                if not bm:
                    dominant = planes
                part = chamfered(rng, plan, planes, free)
                if part is None:
                    tally["the piece alone cannot be softened"] = tally.get("the piece alone cannot be softened", 0) + 1
                    continue
                joined = union([bm, part]) if bm else part.copy()
                reason = unbevelable(joined)
                if reason is None:
                    record.append({"name": plan["name"], "vertices": [list(v.co) for v in part.verts], "faces": [[v.index for v in f.verts] for f in part.faces]})
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
        stretches = [fit(bm, lo, hi)]
        tag = soften(bm)
        stretches.append(fit(bm, lo, hi))
        for part in record:
            for scale, shift in stretches:
                part["vertices"] = [[c * scale[i] + shift[i] for i, c in enumerate(co)] for co in part["vertices"]]
        # Triangulation hands its faces back in an order that changes from run to run. The
        # shape is the same, but the exported file is not; put the faces in a fixed order.
        for index, face in enumerate(sorted(bm.faces, key=lambda face: tuple(round(c, 5) for c in face.calc_center_median()))):
            face.index = index
        bm.faces.sort()
        bm.normal_update()
        problems = unmet(bm, tag, record, spec)
        measured += 1
        if not problems:
            print(f"rock seed {seed}: rock {take} of up to {ROCKS} meets the spec ({measured} measured)")
            return bm, tag, record
        refused.append(f"rock {take}: " + "; ".join(problems))
        bm.free()
    raise RuntimeError(f"rock seed {seed}: none of its rocks meets the spec:\n  " + "\n  ".join(refused))


def build(spec, seed=SEED):
    bm, tag, record = shape(spec, seed)
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
    # What the rock is made of, for the gate to hold against the mesh (tools/validate.py, check_pieces).
    text = bpy.data.texts.get("rock.pieces") or bpy.data.texts.new("rock.pieces")
    text.clear()
    text.write(json.dumps([{**part, "vertices": [[round(c, 6) for c in co] for co in part["vertices"]]} for part in record]))
    return obj
