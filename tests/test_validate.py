"""Proves each L1 check goes red: breaks the tracer one way at a time and
asserts that the matching check, by id, fails.

Usage: tools/bl tests/test_validate.py [--asset <name>] [--only <regex>] [--part <i>/<n> | --unbroken]
       With no arguments every mutation runs, after each asset has been checked unbroken.
       --asset keeps the mutations of one asset, and --only those whose name or check id
       matches. tests/run.sh splits an asset's run to do the pieces side by side: --part runs
       the i-th of n shares of the mutations and no unbroken check, --unbroken that check alone.
       Selecting nothing is an error.
"""

import json
import math
import re
import runpy
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector, noise

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import paint
from pipeline import Asset, Checks, conventions, script_args
from validate import check_scene

def edit(fn, name="tracer"):
    """Apply fn(bm) to the named object's mesh."""
    mesh = bpy.data.objects[name].data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    fn(bm)
    bm.to_mesh(mesh)
    bm.free()


def delete_face(spec):
    edit(lambda bm: bmesh.ops.delete(bm, geom=[bm.faces[0]], context="FACES_ONLY"))


def flip_all(spec):
    edit(lambda bm: bmesh.ops.reverse_faces(bm, faces=bm.faces))


def flip_one(spec):
    edit(lambda bm: bmesh.ops.reverse_faces(bm, faces=[bm.faces[0]]))


def unapplied_scale(spec):
    bpy.data.objects["tracer"].scale = (2, 2, 2)


def rotated(spec):
    bpy.data.objects["tracer"].rotation_euler = (0, 0, 1.5708)


def shifted(spec):
    edit(lambda bm: bmesh.ops.translate(bm, verts=bm.verts, vec=(0.1, 0, 0)))


def mirrored_front_to_back(spec):
    def mirror(bm):
        bmesh.ops.scale(bm, verts=bm.verts, vec=(1, -1, 1))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)

    edit(mirror)


def default_name(spec):
    bpy.data.objects["tracer"].data.name = "Cube.001"


def stray_object(spec):
    stray = bpy.data.objects.new("leftover", bpy.data.objects["tracer"].data.copy())
    bpy.context.scene.collection.objects.link(stray)


def ngon(spec):
    def dissolve(bm):
        cap = [f for f in bm.faces if f.normal.x > 0.9]
        bmesh.ops.dissolve_faces(bm, faces=cap)

    edit(dissolve)


def loose_vertex(spec):
    edit(lambda bm: bm.verts.new((0, 0, 0.5)))


def duplicate_vertices(spec):
    edit(lambda bm: bmesh.ops.split_edges(bm, edges=bm.edges))


def no_material(spec):
    bpy.data.objects["tracer"].data.materials.clear()


def emission_material(spec):
    tree = bpy.data.materials["m_tracer"].node_tree
    emission = tree.nodes.new("ShaderNodeEmission")
    output = next(n for n in tree.nodes if n.type == "OUTPUT_MATERIAL")
    tree.links.new(emission.outputs[0], output.inputs["Surface"])


def wrong_colour(spec):
    bsdf = bpy.data.materials["m_tracer"].node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.8, 0.1, 1.0)


def extra_material(spec):
    bpy.data.objects["tracer"].data.materials.append(bpy.data.materials.new("m_extra"))


def over_budget(spec):
    spec["max_triangles"] = 10


def shallow_recess(spec):
    """Push every crate panel 0.02 m outward, leaving the frame where it is."""

    def push(bm):
        for face in [f for f in bm.faces if f.material_index == 1]:
            bmesh.ops.translate(bm, verts=face.verts, vec=face.normal * 0.02)

    edit(push, "crate")


def narrow_frame(spec):
    """Grow every crate panel in its own plane, so the frame around it is narrower."""

    def grow(bm):
        for face in [f for f in bm.faces if f.material_index == 1]:
            centre = face.calc_center_median()
            for vert in face.verts:
                vert.co = centre + (vert.co - centre) * 1.1

    edit(grow, "crate")


def recess_respecified(spec):
    spec["recess_m"]["m_crate_panel"] = 0.03


def fit_to_bounds(bm, spec):
    """Stretch a mesh to the spec's bounds, so only its shape differs from the asset's."""
    want_lo, want_hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    lo = [min(v.co[i] for v in bm.verts) for i in range(3)]
    hi = [max(v.co[i] for v in bm.verts) for i in range(3)]
    for vert in bm.verts:
        vert.co = Vector(want_lo[i] + (vert.co[i] - lo[i]) / (hi[i] - lo[i]) * (want_hi[i] - want_lo[i]) for i in range(3))


def replace_shape(spec, make):
    """Swap the rock's geometry for make(bm)'s, at the same bounds and with the same material."""

    def swap(bm):
        bm.clear()
        make(bm)
        fit_to_bounds(bm, spec)

    edit(swap, "rock")


def noise_lump(spec):
    """The shape ADR 9 rules out: a 320-triangle ball pushed about by fractal noise."""

    def lump(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        for vert in bm.verts:
            vert.co += vert.co.normalized() * noise.fractal(vert.co * 1.3, 1.0, 2.0, 4) * 0.35

    replace_shape(spec, lump)


def even_facets(spec):
    """Twenty flat faces of one size: planes, but a faceted ball and not a boulder."""
    replace_shape(spec, lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0))


def no_ledge(spec):
    """Shrink-wrap the rock in its convex hull: every plane survives except the inward corners."""

    def hull(bm):
        result = bmesh.ops.convex_hull(bm, input=bm.verts)
        inside = set(result["geom_interior"]) | set(result["geom_unused"])
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v in inside], context="VERTS")
        hull_faces = {g for g in result["geom"] if isinstance(g, bmesh.types.BMFace)}
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f not in hull_faces], context="FACES")

    edit(hull, "rock")


def thin_wedge(spec):
    """The rock the owner rejected on 2026-10-04: seed 2 of the first generator. A wedge with a
    narrow ridge, one plane across most of the back, and its only ledge a small notch."""
    data = json.loads((ROOT / "tests" / "fixtures" / "rock_thin_wedge.json").read_text())

    def swap(bm):
        bm.clear()
        verts = [bm.verts.new(co) for co in data["vertices"]]
        for face in data["faces"]:
            bm.faces.new([verts[i] for i in face])

    edit(swap, "rock")


def too_many_planes(spec):
    spec["planes"]["max_count"] = 3


# The habits of docs/style/rock-shapes.md: several pieces in a size order, a foot, big chamfers, nothing upright.


def record_pieces(pieces):
    """Replace what the build recorded the rock as being made of."""
    text = bpy.data.texts.get("rock.pieces") or bpy.data.texts.new("rock.pieces")
    text.clear()
    text.write(json.dumps(pieces))


def box(lo, hi):
    """A box as a recorded piece: its corners and its six faces, wound outward."""
    corners = [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    return {"vertices": corners, "faces": [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]}


def single_block(spec):
    """The rock the owner called a cut block on 2026-10-04: seed 2 of the second generator. One
    piece with near-upright walls and nine similar sides, no foot and no chamfers. Whatever the
    build recorded is left as it is, so the record describes a rock that is no longer there."""
    data = json.loads((ROOT / "tests" / "fixtures" / "rock_single_block.json").read_text())

    def swap(bm):
        bm.clear()
        verts = [bm.verts.new(co) for co in data["vertices"]]
        for face in data["faces"]:
            bm.faces.new([verts[i] for i in face])

    edit(swap, "rock")


def phantom_pieces(spec):
    """The single block again, with a record written to pass: the block's own hull as the
    dominant piece, and five more pieces that are nowhere on its surface."""
    single_block(spec)
    mesh = bpy.data.objects["rock"].data
    hull = bmesh.new()
    hull.from_mesh(mesh)
    result = bmesh.ops.convex_hull(hull, input=hull.verts)
    kept = {g for g in result["geom"] if isinstance(g, bmesh.types.BMFace)}
    bmesh.ops.delete(hull, geom=[f for f in hull.faces if f not in kept], context="FACES")
    bmesh.ops.delete(hull, geom=[v for v in hull.verts if not v.link_faces], context="VERTS")
    bmesh.ops.recalc_face_normals(hull, faces=hull.faces)
    hull.verts.index_update()
    pieces = [{"vertices": [list(v.co) for v in hull.verts], "faces": [[v.index for v in f.verts] for f in hull.faces]}]
    hull.free()
    for i in range(5):
        size = 0.5 - 0.07 * i
        pieces.append(box((-0.6 + 0.2 * i, -0.3, 0.0), (-0.6 + 0.2 * i + size, -0.3 + size, size)))
    record_pieces(pieces)


def twin_pieces(spec):
    """Two blocks of one size side by side, recorded truthfully: pieces, but no size order."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    halves = [box(lo, (-0.1, hi[1], hi[2])), box((0.1, lo[1], lo[2]), hi)]

    def swap(bm):
        bm.clear()
        for half in halves:
            verts = [bm.verts.new(co) for co in half["vertices"]]
            for face in half["faces"]:
                bm.faces.new([verts[i] for i in face])

    edit(swap, "rock")
    record_pieces(halves)


def paint_removed(spec):
    """The rock back to its flat colour: the texture is no longer what colours it."""
    socket = bpy.data.materials["m_rock"].node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    bpy.data.materials["m_rock"].node_tree.links.remove(socket.links[0])


def painted_at_another_size(spec):
    spec["painted_shading"]["texture_px"] *= 2


def painted_over_another_colour(spec):
    spec["materials"]["m_rock"] = "#806040"


def textured(spec):
    """A flat-coloured asset whose colour comes from an image instead."""
    tree = bpy.data.materials["m_tracer"].node_tree
    image = tree.nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.new("stray", 8, 8)
    tree.links.new(image.outputs["Color"], tree.nodes["Principled BSDF"].inputs["Base Color"])


def regrow(spec, **constants):
    """Build the tree again with some of its generator's constants changed."""
    import generator

    saved = {key: getattr(generator, key) for key in constants}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        for key, value in constants.items():
            setattr(generator, key, value)
        # The first tree that fills the bounds, whatever it measures: the generator would refuse these.
        generator.build_tree(spec, strict=False)
    finally:
        for key, value in saved.items():
            setattr(generator, key, value)


def leaf_slot(spec):
    names = [slot.material.name for slot in bpy.data.objects["tree_1"].material_slots]
    return names.index(spec["foliage"]["material"])


def each_piece(spec, change):
    """Apply change(piece's vertices, its middle, its faces, bm) to every leaf piece of the tree."""
    import foliage

    def run(bm):
        for piece in foliage.pieces_of(bm, leaf_slot(spec)):
            verts = list({v for face in piece for v in face.verts})
            change(verts, sum((v.co for v in verts), Vector()) / len(verts), piece, bm)

    edit(run, "tree_1")


def bark_hole(spec):
    """One face of the trunk missing: the bark is no longer closed."""
    slot = leaf_slot(spec)
    edit(lambda bm: bmesh.ops.delete(bm, geom=[next(f for f in bm.faces if f.material_index != slot)], context="FACES_ONLY"), "tree_1")


def round_trunk(spec):
    regrow(spec, TRUNK_SIDES=(14, 14))


def pole_trunk(spec):
    """A trunk as thick below the fork as at breast height."""
    regrow(spec, TRUNK_TOP=1.0)


def stout_limbs(spec):
    """Limbs and twigs that end as thick as they begin."""
    regrow(spec, TIP_RADIUS=0.11, TWIG_RADIUS=0.11)


def no_branches(spec):
    """Only the trunk and its leader: every other piece of bark removed."""
    slot = leaf_slot(spec)

    def strip(bm):
        lowest = min((v for f in bm.faces if f.material_index != slot for v in f.verts), key=lambda v: v.co.z)
        keep, queue = {lowest}, [lowest]
        while queue:
            for edge in queue.pop().link_edges:
                for vert in edge.verts:
                    if vert not in keep:
                        keep.add(vert)
                        queue.append(vert)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index != slot and f.verts[0] not in keep], context="FACES")

    edit(strip, "tree_1")


def no_roots(spec):
    regrow(spec, ROOT_REACH=(1.0, 1.0))


def upright_trunk(spec):
    regrow(spec, LEAN=(0.0, 0.0), BEND=(0.0, 0.0))


def solid_ball(spec):
    """The foliage ADR 9 rules out: one solid ball where the canopy was."""
    slot = leaf_slot(spec)

    def swap(bm):
        leaves = [f for f in bm.faces if f.material_index == slot]
        points = [v.co.copy() for f in leaves for v in f.verts]
        lo = Vector(min(p[i] for p in points) for i in range(3))
        hi = Vector(max(p[i] for p in points) for i in range(3))
        bmesh.ops.delete(bm, geom=leaves, context="FACES")
        before = set(bm.faces)
        result = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        for vert in result["verts"]:
            vert.co = (lo + hi) / 2 + Vector(vert.co[i] * (hi[i] - lo[i]) / 2 for i in range(3))
        for face in bm.faces:
            if face not in before:
                face.material_index = slot

    edit(swap, "tree_1")


def confetti(spec):
    """Every piece shrunk to a third of its size."""

    def shrink(verts, middle, piece, bm):
        for vert in verts:
            vert.co = middle + (vert.co - middle) * 0.3

    each_piece(spec, shrink)


def round_leaves(spec):
    """Every piece swapped for a flat eight-sided disc of its own size: neither pointed nor jagged."""

    def disc(verts, middle, piece, bm):
        normal = piece[0].normal.copy()
        across = normal.orthogonal().normalized()
        along = normal.cross(across)
        radius = max((v.co - middle).length for v in verts)
        slot = piece[0].material_index
        bmesh.ops.delete(bm, geom=piece, context="FACES")
        rim = [bm.verts.new(middle + (across * math.cos(i * math.pi / 4) + along * math.sin(i * math.pi / 4)) * radius) for i in range(8)]
        hub = bm.verts.new(middle)
        for a, b in zip(rim, rim[1:] + rim[:1]):
            bm.faces.new((hub, a, b)).material_index = slot

    each_piece(spec, disc)


def merged_pads(spec):
    """Every piece moved, whole, halfway toward the middle of the canopy: the pads run into each other."""
    slot = leaf_slot(spec)
    mesh = bpy.data.objects["tree_1"].data
    points = [mesh.vertices[i].co for polygon in mesh.polygons if polygon.material_index == slot for i in polygon.vertices]
    centre = sum(points, Vector()) / len(points)

    def gather(verts, middle, piece, bm):
        for vert in verts:
            vert.co += (centre - middle) * 0.5

    each_piece(spec, gather)


def leaves_point_in(spec):
    """Every piece turned end for end about its own middle: tips toward the inside of the pad and upward."""

    def turn(verts, middle, piece, bm):
        for vert in verts:
            vert.co = middle * 2 - vert.co

    each_piece(spec, turn)


def edit_cores(spec, change):
    """Apply change(bm, the cores as lists of faces) to the tree."""
    import foliage

    edit(lambda bm: change(bm, foliage.cores_of(bm, leaf_slot(spec))), "tree_1")


def no_cores(spec):
    """Every core removed: pads are open shells again, and from below one looks up into them."""
    edit_cores(spec, lambda bm, cores: bmesh.ops.delete(bm, geom=[f for core in cores for f in core], context="FACES"))


def core_hole(spec):
    """One face missing from one core: it is no longer closed."""
    edit_cores(spec, lambda bm, cores: bmesh.ops.delete(bm, geom=[cores[0][0]], context="FACES_ONLY"))


def core_inside_out(spec):
    edit_cores(spec, lambda bm, cores: bmesh.ops.reverse_faces(bm, faces=[f for core in cores for f in core]))


def even_lobes(spec):
    """Every lobe of a pad the same size."""
    regrow(spec, LOBE_MAIN=(0.56, 0.56), LOBE_SIDE=(0.56, 0.56), LOBE_TALL=(0.8, 0.8))


def one_lobe_pads(spec):
    """Every pad a single round cap, as the first generator drew them."""
    regrow(spec, LOBE_COUNTS=((1, 1.0),))


def bare_cores(spec):
    """A third of the pieces: the cores are what is seen."""
    regrow(spec, LEAF_SPACING=0.5, SKIRT_SPACING=1.2, UNDER_SPACING=1.5)


def ball_pads(spec):
    """Every pad stretched to more than twice its height about its own middle: as tall as it is wide."""
    import foliage

    def stretch(bm):
        slot = leaf_slot(spec)
        pieces, cores = foliage.pieces_of(bm, slot), foliage.cores_of(bm, slot)
        pads = [pad for found in foliage.pads_with_cores(pieces, cores, spec["foliage"]["pad_gap_m"]) for pad in found]
        for pad in set(pads):
            verts = list({v for part, at in zip(pieces + cores, pads) if at == pad for face in part for v in face.verts})
            middle = sum(v.co.z for v in verts) / len(verts)
            for vert in verts:
                vert.co.z = middle + (vert.co.z - middle) * 2.2

    edit(stretch, "tree_1")


def even_pads(spec):
    """Every pad the same width."""
    regrow(spec, PAD_LARGEST=(1.2, 1.2), PAD_SMALLEST=(1.2, 1.2))


def identical_variants(spec):
    """The tree compared with itself, as three variants from one seed would be."""
    spec["variants"]["siblings"] = ["tree_1"]


# mutation -> the check id that must fail because of it. Cases break the
# tracer unless they name another asset.
CASES = [
    (delete_face, "tracer.manifold"),
    (flip_all, "tracer.normals_outward"),
    (flip_one, "tracer.winding_consistent"),
    (unapplied_scale, "tracer.transform_applied"),
    (rotated, "tracer.transform_applied"),
    (shifted, "bounds.match_spec"),
    (mirrored_front_to_back, "bounds.match_spec"),
    (default_name, "tracer.naming"),
    (stray_object, "objects.unexpected"),
    (ngon, "tracer.no_ngons"),
    (loose_vertex, "tracer.no_loose_vertices"),
    (duplicate_vertices, "tracer.no_duplicate_vertices"),
    (no_material, "tracer.materials_assigned"),
    (emission_material, "m_tracer.principled"),
    (wrong_colour, "m_tracer.base_colour"),
    (extra_material, "materials.match_spec"),
    (over_budget, "budget.triangles"),
    (shallow_recess, "m_crate_panel.recess", "crate"),
    (recess_respecified, "m_crate_panel.recess", "crate"),
    (narrow_frame, "m_crate_panel.margin", "crate"),
    (noise_lump, "rock.planes_area_share", "rock"),
    (even_facets, "rock.planes_size_ratio", "rock"),
    (no_ledge, "rock.planes_ledges", "rock"),
    (too_many_planes, "rock.planes_count", "rock"),
    (single_block, "rock.pieces_match", "rock"),
    (single_block, "rock.foot", "rock"),
    (single_block, "rock.chamfers", "rock"),
    (single_block, "rock.lean", "rock"),
    (phantom_pieces, "rock.pieces_count", "rock"),
    (twin_pieces, "rock.pieces_size_order", "rock"),
    (even_facets, "rock.summit_off_centre", "rock"),
    (thin_wedge, "rock.fullness", "rock"),
    (thin_wedge, "rock.crown", "rock"),
    (thin_wedge, "rock.planes_view_share", "rock"),
    (thin_wedge, "rock.planes_ledge_views", "rock"),
    (paint_removed, "m_rock.painted", "rock"),
    (painted_at_another_size, "m_rock.painted", "rock"),
    (painted_over_another_colour, "m_rock.base_colour", "rock"),
    (textured, "m_tracer.base_colour"),
    (bark_hole, "tree_1.manifold", "tree_1"),
    (round_trunk, "tree_1.trunk_sides", "tree_1"),
    (pole_trunk, "tree_1.trunk_tapers", "tree_1"),
    (no_branches, "tree_1.fork", "tree_1"),
    (no_branches, "tree_1.branches", "tree_1"),
    (stout_limbs, "tree_1.branches_taper", "tree_1"),
    (no_roots, "tree_1.roots", "tree_1"),
    (upright_trunk, "tree_1.lean", "tree_1"),
    (solid_ball, "tree_1.branches_seen", "tree_1"),
    (solid_ball, "tree_1.sky", "tree_1"),
    (solid_ball, "tree_1.leaf_shape", "tree_1"),
    (solid_ball, "tree_1.pads", "tree_1"),
    (confetti, "tree_1.leaf_size", "tree_1"),
    (round_leaves, "tree_1.leaf_shape", "tree_1"),
    (merged_pads, "tree_1.pads", "tree_1"),
    (leaves_point_in, "tree_1.leaves_point_out", "tree_1"),
    (identical_variants, "variants.differ", "tree_1"),
    (solid_ball, "tree_1.cores", "tree_1"),
    (no_cores, "tree_1.cores", "tree_1"),
    (no_cores, "tree_1.under_closed", "tree_1"),
    (core_hole, "tree_1.cores", "tree_1"),
    (core_inside_out, "tree_1.cores", "tree_1"),
    (even_lobes, "tree_1.lobes_differ", "tree_1"),
    (one_lobe_pads, "tree_1.cores", "tree_1"),
    (bare_cores, "tree_1.core_hidden", "tree_1"),
    (ball_pads, "tree_1.pads_wide", "tree_1"),
    (even_pads, "tree_1.pads_differ", "tree_1"),
    (round_leaves, "tree_1.under_rim", "tree_1"),
]


def failures_after(mutate, name="tracer"):
    asset = Asset(name)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    spec = asset.spec()
    runpy.run_path(str(asset.source / "build.py"))["build"](spec)
    if "painted_shading" in spec:
        # As tools/build.py does. A small texture is enough for L1, which reads no texels.
        spec["painted_shading"]["texture_px"] = 64
        # Too small to give a trunk its close texels (ADR 12); L4 measures those on the real texture.
        for key in ("close_height_m", "close_texels_per_m"):
            spec["painted_shading"].pop(key, None)
        paint.apply(spec, conventions())
    if mutate and mutate is not identical_variants:
        # Only the unbroken asset and `identical_variants` are compared with their siblings: building two
        # more trees for every mutation of one tree would take most of the suite's time.
        spec.pop("variants", None)
    if mutate:
        mutate(spec)
    checks = Checks("L1-mesh", name)
    check_scene(checks, spec, conventions())
    return {r["id"] for r in checks.failed()}


def asset_of(case):
    return case[2] if len(case) > 2 else "tracer"


def selected(args):
    """The cases the arguments ask for, and the assets to check unbroken first."""

    def option(flag):
        return args[args.index(flag) + 1] if flag in args else None

    cases = CASES
    if asset := option("--asset"):
        cases = [case for case in cases if asset_of(case) == asset]
    if only := option("--only"):
        cases = [case for case in cases if re.search(only, case[0].__name__) or re.search(only, case[1])]
    unbroken = sorted({asset_of(case) for case in cases})
    if "--unbroken" in args:
        return [], unbroken
    if share := option("--part"):
        part, parts = (int(n) for n in share.split("/"))
        # A mutation stays whole in one part, however many checks it must turn red.
        mutations = list(dict.fromkeys(case[0] for case in cases))[part - 1 :: parts]
        return [case for case in cases if case[0] in mutations], []
    return cases, unbroken


cases, unbroken = selected(script_args())
if not cases and not unbroken:
    sys.exit(f"no mutation is selected by {script_args()}")
problems = []
seen = {}  # one build per mutation, however many checks it must turn red
for name in unbroken:
    clean = failures_after(None, name)
    print(f"unbroken   {name:24} {'passes every check' if not clean else f'FAILS {sorted(clean)}'}")
    if clean:
        problems.append(f"unmodified {name} fails {sorted(clean)}")
for mutate, expected, *asset_name in cases:
    if mutate not in seen:
        seen[mutate] = failures_after(mutate, *asset_name)
    failed = seen[mutate]
    status = "ok" if expected in failed else "NOT CAUGHT"
    print(f"{status:10} {mutate.__name__:24} {expected:28} -> {sorted(failed)}")
    if expected not in failed:
        problems.append(f"{mutate.__name__} did not fail {expected}")

for problem in problems:
    print("FAIL", problem)
print(f"{len(cases) - len(problems)}/{len(cases)} mutations caught" if not problems else f"{len(problems)} problems")
sys.exit(1 if problems else 0)
