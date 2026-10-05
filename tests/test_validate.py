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
from mathutils import Matrix, Vector, noise

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


# Overlapping pieces (ADR 13): a shape may be several closed pieces that pass into each other.
# The tracer is one closed piece; these add a second, and the spec opts in as a rock's would.

OVERLAP = {"min_count": 2, "max_count": 2, "max_buried_share": 0.3, "min_step_ratio": 1.2}


def add_piece(spec, lo, hi, inside_out=False):
    """A box as a second closed piece of the tracer, and a spec that says the tracer is two overlapping pieces."""
    spec["overlap"] = dict(OVERLAP)
    piece = box(lo, hi)

    def add(bm):
        verts = [bm.verts.new(co) for co in piece["vertices"]]
        faces = [bm.faces.new([verts[i] for i in face]) for face in piece["faces"]]
        if inside_out:
            bmesh.ops.reverse_faces(bm, faces=faces)

    edit(add)


def piece_inside_out(spec):
    """A small second piece pushed into the tracer's leg, inside out. The two together still enclose a positive volume."""
    add_piece(spec, (0.0, 0.3, 0.5), (0.4, 0.5, 0.9), inside_out=True)
    # A sixth of the box is inside the leg; this mutation is about its facing, not about how much is buried.
    spec["overlap"]["max_buried_share"] = 0.9


def piece_floats(spec):
    """A second piece in the air above the tracer's toe, touching nothing."""
    add_piece(spec, (0.0, -1.2, 0.6), (0.4, -0.8, 0.9))


def piece_buried(spec):
    """A second piece nine tenths the tracer's size, wholly inside it: nearly half of all the surface is never seen."""
    spec["overlap"] = dict(OVERLAP)
    about = Vector((0.25, 0.1, 0.2))  # a point every part of the boot can be seen from, so the copy stays inside

    def add(bm):
        copy = bmesh.ops.duplicate(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:])["geom"]
        for vert in (g for g in copy if isinstance(g, bmesh.types.BMVert)):
            vert.co = about + (vert.co - about) * 0.9

    edit(add)


def one_piece(spec):
    """The tracer as it is, with a spec that says it is two overlapping pieces."""
    spec["overlap"] = dict(OVERLAP)


def twin_overlapping_pieces(spec):
    """A copy of the tracer pushed 5 cm along from it: two pieces of one size, neither clearly the larger."""
    spec["overlap"] = dict(OVERLAP)
    spec["overlap"]["max_buried_share"] = 0.9

    def add(bm):
        copy = bmesh.ops.duplicate(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:])["geom"]
        bmesh.ops.translate(bm, verts=[g for g in copy if isinstance(g, bmesh.types.BMVert)], vec=(0.05, 0.0, 0.0))

    edit(add)


# The slab (source/slab): overlapping plates with nearly flat tops.


def slab_pieces(bm):
    """The slab's pieces as lists of vertices, largest first."""
    from validate import pieces_in

    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    return sorted(pieces, key=len, reverse=True)


def tipped_tops(spec):
    """The whole slab sheared so that every cap tips 27 degrees: nothing left level to stand on."""

    def shear(bm):
        for vert in bm.verts:
            vert.co.z += 0.5 * (vert.co.x - spec["bounds_m"]["min"][0])

    edit(shear, "slab_1")


def plate_lifted(spec):
    """The smaller plate lifted clear of the other: it floats."""
    edit(lambda bm: bmesh.ops.translate(bm, verts=slab_pieces(bm)[-1], vec=(0, 0, 2.0)), "slab_1")


def plate_inside_out(spec):
    """The smaller plate turned inside out; the two together still enclose a positive volume."""

    def flip(bm):
        verts = set(slab_pieces(bm)[-1])
        bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f.verts[0] in verts])

    edit(flip, "slab_1")


# The crag (source/crag): leaning prisms of different heights on one base.


def crag_pieces(bm):
    """The crag's pieces as lists of vertices, tallest first."""
    from validate import pieces_in

    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    return sorted(pieces, key=lambda verts: max(v.co.z for v in verts), reverse=True)


def even_heights(spec):
    """Every piece of the crag stretched up to the height of the tallest: a palisade, with no steps down."""
    top = spec["bounds_m"]["max"][2]

    def stretch(bm):
        for verts in crag_pieces(bm):
            scale = top / max(v.co.z for v in verts)
            for v in verts:
                v.co.z *= scale

    edit(stretch, "crag_1")


def one_prism(spec):
    """Every piece but the tallest pressed down to a fifth of the crag's height: one prism among blocks."""
    low = 0.2 * spec["bounds_m"]["max"][2]

    def press(bm):
        for verts in crag_pieces(bm)[1:]:
            scale = min(1.0, low / max(v.co.z for v in verts))
            for v in verts:
                v.co.z *= scale

    edit(press, "crag_1")


def piece_axis(verts):
    """Where a piece stands and where its top is: the middle of its corners on the ground, and of the rest, which ring its cap and its shoulder."""
    low = min(v.co.z for v in verts)
    foot = [v.co for v in verts if v.co.z <= low + 0.001]
    top = [v.co for v in verts if v.co.z > low + 0.001]
    return sum(foot, Vector()) / len(foot), sum(top, Vector()) / len(top)


def upright_prisms(spec):
    """Every piece of the crag sheared until its top stands over its foot: nothing leans."""

    def stand(bm):
        for verts in crag_pieces(bm):
            foot, top = piece_axis(verts)
            for v in verts:
                share = (v.co.z - foot.z) / (top.z - foot.z)
                v.co.x -= (top.x - foot.x) * share
                v.co.y -= (top.y - foot.y) * share

    edit(stand, "crag_1")


def fanned_prisms(spec):
    """Every piece of the crag turned on its foot, each a different way: they lean as much as before, but apart."""

    def fan(bm):
        pieces = crag_pieces(bm)
        for index, verts in enumerate(pieces):
            foot, _ = piece_axis(verts)
            turn = Matrix.Rotation(index * math.tau / len(pieces), 3, "Z")
            for v in verts:
                v.co = foot + turn @ (v.co - foot)

    edit(fan, "crag_1")


# The stepped spire (source/spire): a fluted base and narrower tiers stacked on it like a telescope.


def spire_pieces(bm, spec):
    """The spire's pieces as lists of vertices: (those that stand on the ground, those that stand on another piece from the lowest up)."""
    from validate import pieces_in

    floor = spec["bounds_m"]["min"][2]
    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    ground = [verts for verts in pieces if min(v.co.z for v in verts) <= floor + 0.001]
    raised = sorted((verts for verts in pieces if min(v.co.z for v in verts) > floor + 0.001), key=lambda verts: max(v.co.z for v in verts))
    return ground, raised


def middle_of(verts):
    return sum((v.co for v in verts), Vector()) / len(verts)


def top_tier_removed(spec):
    """Every piece that stands on another taken away but the lowest tier above the base: a base and one tier, fewer than any spire's spec asks."""

    def remove(bm):
        ground, raised = spire_pieces(bm, spec)
        base_top = max(v.co.z for verts in ground for v in verts)
        keep = min((verts for verts in raised if max(v.co.z for v in verts) > base_top), key=lambda verts: max(v.co.z for v in verts))
        bmesh.ops.delete(bm, geom=[v for verts in raised if verts is not keep for v in verts], context="VERTS")

    edit(remove, "spire_1")


def tier_hangs_off(spec):
    """The spire's top tier pushed outward by six tenths of its own width: still sunk into the one below, but with much of its foot over open air."""

    def push(bm):
        ground, raised = spire_pieces(bm, spec)
        top = raised[-1]
        # Away from the middle of everything else, whichever side of the tier below it sits toward.
        away = (middle_of(top) - middle_of([v for verts in ground + raised[:-1] for v in verts])).to_2d()
        away = away.normalized() if away.length > 1e-6 else Vector((1, 0))
        width = max(v.co.x for v in top) - min(v.co.x for v in top)
        for v in top:
            v.co.x += 0.6 * width * away.x
            v.co.y += 0.6 * width * away.y

    edit(push, "spire_1")


def plain_column(spec):
    """Every tier above the base widened to nearly the width of the one below: a column with lines round it, not steps."""

    def widen(bm):
        ground, raised = spire_pieces(bm, spec)
        base = max(ground, key=lambda verts: max(v.co.z for v in verts))
        below = max(v.co.x for v in base) - min(v.co.x for v in base)
        for verts in raised:
            centre = middle_of(verts)
            scale = 0.6 * below / (max(v.co.x for v in verts) - min(v.co.x for v in verts))
            for v in verts:
                v.co.x = centre.x + (v.co.x - centre.x) * scale
                v.co.y = centre.y + (v.co.y - centre.y) * scale
            below *= 0.95

    edit(widen, "spire_1")


def pointed_caps(spec):
    """Every tier's cap drawn in to a point and raised: cones on cones, with no flat cap and no ledge."""

    def pinch(bm):
        ground, raised = spire_pieces(bm, spec)
        base = max(ground, key=lambda verts: max(v.co.z for v in verts))
        for verts in [base] + raised:
            cap = {v for v in verts for f in v.link_faces if f.normal.z > 0.97}
            centre = middle_of(cap)
            rise = 0.5 * max((v.co - centre).to_2d().length for v in cap)
            for v in cap:
                v.co.x = centre.x + (v.co.x - centre.x) * 0.05
                v.co.y = centre.y + (v.co.y - centre.y) * 0.05
                v.co.z += rise

    edit(pinch, "spire_1")


def telescoped(spec):
    """Every tier above the base stood upright on the middle of the one below, each the same share of its width: a telescope."""

    def stack(bm):
        ground, raised = spire_pieces(bm, spec)
        base = max(ground, key=lambda verts: max(v.co.z for v in verts))
        # The tiers: each stands on the one before. Of two pieces standing on one tier (a tier and a block on its ledge) the taller is the tier.
        chain = [base]
        for verts in raised:
            if len(chain) > 1 and min(v.co.z for v in verts) < max(v.co.z for v in chain[-2]):
                chain[-1] = verts
            elif min(v.co.z for v in verts) < max(v.co.z for v in chain[-1]):
                chain.append(verts)

        def ends(verts):
            """The middle of a piece's lowest ring of corners, and of its highest."""
            low, high = min(v.co.z for v in verts), max(v.co.z for v in verts)
            return middle_of([v for v in verts if v.co.z < low + 0.1 * (high - low)]), middle_of([v for v in verts if v.co.z > high - 0.1 * (high - low)])

        # The base stood upright first: its head back over its foot.
        foot, head = ends(base)
        for v in base:
            share = (v.co.z - foot.z) / (head.z - foot.z)
            v.co.x -= (head.x - foot.x) * share
            v.co.y -= (head.y - foot.y) * share
        for below, verts in zip(chain, chain[1:]):
            low, high = min(v.co.z for v in verts), max(v.co.z for v in verts)
            foot = middle_of([v for v in verts if v.co.z < low + 0.1 * (high - low)])
            head = middle_of([v for v in verts if v.co.z > high - 0.1 * (high - low)])
            top = max(v.co.z for v in below)
            under = middle_of([v for v in below if v.co.z > top - 0.1 * (top - min(v.co.z for v in below))])
            def wide(group):
                """About how wide a piece is half way up: the mean of its lowest and highest rings."""
                bottom, height = min(v.co.z for v in group), max(v.co.z for v in group) - min(v.co.z for v in group)
                rings = [[v for v in group if v.co.z < bottom + 0.1 * height], [v for v in group if v.co.z > bottom + 0.9 * height]]
                return sum(math.sqrt((max(v.co.x for v in ring) - min(v.co.x for v in ring)) * (max(v.co.y for v in ring) - min(v.co.y for v in ring))) for ring in rings) / 2

            scale = 0.55 * wide(below) / wide(verts)
            for v in verts:
                share = (v.co.z - low) / (high - low)
                x = v.co.x - foot.x - (head.x - foot.x) * share
                y = v.co.y - foot.y - (head.y - foot.y) * share
                v.co.x, v.co.y = under.x + x * scale, under.y + y * scale

    edit(stack, "spire_1")


def banded_base(spec):
    """Every piece on the ground cut level into bands, each second ring of the cut pushed out: sides in horizontal bands, with no edge running up them."""

    def band(bm):
        ground, _ = spire_pieces(bm, spec)
        top = max(v.co.z for verts in ground for v in verts)
        cuts = [top * (i + 1) / 9 for i in range(8)]
        for verts in ground:
            centre = middle_of(verts)
            for index, height in enumerate(cuts):
                faces = list({f for v in verts if v.is_valid for f in v.link_faces})
                geom = list({e for f in faces for e in f.edges}) + faces + list({v for f in faces for v in f.verts})
                cut = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, height), plane_no=(0, 0, 1))
                ring = [g for g in cut["geom_cut"] if isinstance(g, bmesh.types.BMVert)]
                verts.extend(ring)
                for v in ring:
                    push = 1.12 if index % 2 == 0 else 0.97
                    v.co.x = centre.x + (v.co.x - centre.x) * push
                    v.co.y = centre.y + (v.co.y - centre.y) * push
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        bm.normal_update()

    edit(band, "spire_1")

# The stack (source/stack): flat stones piled one on another.


def stack_stones(bm):
    """The stack's stones as lists of vertices, lowest first."""
    from validate import pieces_in

    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    return sorted(pieces, key=lambda verts: sum(v.co.z for v in verts) / len(verts))


def stones_sunk(spec):
    """Every stone but the lowest pushed down into the one below by 0.6 of its own height: still joined, nothing floats."""

    def sink(bm):
        down = 0.0
        for verts in stack_stones(bm)[1:]:
            down += 0.6 * (max(v.co.z for v in verts) - min(v.co.z for v in verts))
            for v in verts:
                v.co.z -= down

    edit(sink, "stack_1")


def tall_stones(spec):
    """The whole stack stretched to three times its height: a pile of drums, not of flat stones."""

    def stretch(bm):
        for v in bm.verts:
            v.co.z *= 3.0

    edit(stretch, "stack_1")


def even_stones(spec):
    """Every stone widened about its own middle to the width and depth of the lowest: a column."""

    def widen(bm):
        stones = stack_stones(bm)
        want = [max(v.co[i] for v in stones[0]) - min(v.co[i] for v in stones[0]) for i in range(2)]
        for verts in stones[1:]:
            for i in range(2):
                low, high = min(v.co[i] for v in verts), max(v.co[i] for v in verts)
                for v in verts:
                    v.co[i] = (low + high) / 2 + (v.co[i] - (low + high) / 2) * want[i] / (high - low)

    edit(widen, "stack_1")


def pushed_over(spec):
    """Every stone slid along x, each 0.8 of the lowest stone's half width further than the one below: the pile hangs past its base."""

    def slide(bm):
        stones = stack_stones(bm)
        step = 0.4 * (max(v.co.x for v in stones[0]) - min(v.co.x for v in stones[0]))
        for index, verts in enumerate(stones):
            for v in verts:
                v.co.x += index * step

    edit(slide, "stack_1")


# The block (source/block): a near-cuboid with big chamfers, parted along a crack.


def tapered_block(spec):
    """The block drawn in toward its top, to six tenths of its footprint there: a stump of a pyramid, with no side square to anything."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])

    def taper(bm):
        for vert in bm.verts:
            narrow = 1 - 0.4 * (vert.co.z - lo.z) / (hi.z - lo.z)
            vert.co.x, vert.co.y = vert.co.x * narrow, vert.co.y * narrow

    edit(taper, "block_2")


def plain_box(spec):
    """The block's two pieces each swapped for the plain box round it: no chamfer anywhere, and no groove between them."""
    from validate import pieces_in

    def swap(bm):
        boxes = []
        for piece in pieces_in(bm.faces):
            corners = [v.co for f in piece for v in f.verts]
            boxes.append(box([min(co[i] for co in corners) for i in range(3)], [max(co[i] for co in corners) for i in range(3)]))
        bm.clear()
        for piece in boxes:
            verts = [bm.verts.new(co) for co in piece["vertices"]]
            for face in piece["faces"]:
                bm.faces.new([verts[i] for i in face])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    edit(swap, "block_2")


def crack_filled(spec):
    """A flat plate laid into the top of the block, over its whole footprint and up to its full height: the groove of the crack is filled level."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    plate = box((lo[0], lo[1], lo[2] + 0.8 * (hi[2] - lo[2])), hi)

    def fill(bm):
        verts = [bm.verts.new(co) for co in plate["vertices"]]
        for face in plate["faces"]:
            bm.faces.new([verts[i] for i in face])

    edit(fill, "block_2")


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


def regrow(spec, **changes):
    """Build the tree again with some of its species recipe changed: `trunk__sides=[14, 14]` is `sides` in the recipe's `[trunk]`."""
    import generator

    recipe = generator.recipe_of(spec)
    for key, value in changes.items():
        table, name = key.split("__")
        if name not in recipe[table]:
            raise KeyError(f"the recipe's [{table}] has no {name}")
        recipe[table][name] = value
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # The first tree that fills the bounds, whatever it measures: the generator would refuse these.
    generator.build_tree(spec, strict=False, recipe=recipe)


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
    regrow(spec, trunk__sides=[14, 14])


def pole_trunk(spec):
    """A trunk as thick below the fork as at breast height."""
    regrow(spec, trunk__top=1.0)


def stout_limbs(spec):
    """Limbs and twigs that end as thick as they begin."""
    regrow(spec, trunk__tip_radius=0.11, branches__twig_radius=0.11)


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
    regrow(spec, trunk__root_reach=[1.0, 1.0])


def upright_trunk(spec):
    regrow(spec, trunk__lean=[0.0, 0.0], trunk__bend=[0.0, 0.0])


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
    regrow(spec, lobes__main=[0.56, 0.56], lobes__side=[0.56, 0.56], lobes__tall=[0.8, 0.8])


def one_lobe_pads(spec):
    """Every pad a single round cap, as the first generator drew them."""
    regrow(spec, lobes__counts=[[1, 1.0]])


def bare_cores(spec):
    """A third of the pieces: the cores are what is seen."""
    regrow(spec, leaf__spacing=0.5, skirt__spacing=1.2, skirt__under_spacing=1.5)


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
    regrow(spec, pads__largest=[1.2, 1.2], pads__smallest=[1.2, 1.2])


def identical_variants(spec):
    """The tree compared with itself, as three variants from one seed would be."""
    spec["variants"]["siblings"] = ["tree_1"]


def each_blade(spec, change):
    """Apply change(blade's vertices, its foot, its tip, its faces, bm) to every blade of the blade plant."""
    import foliage

    name = spec["objects"][0]
    slot = [slot.material.name for slot in bpy.data.objects[name].material_slots].index(spec["foliage"]["material"])
    ground = Vector((0, 0, spec["bounds_m"]["min"][2]))

    def run(bm):
        for piece in foliage.pieces_of(bm, slot):
            verts = list({v for face in piece for v in face.verts})
            inside = set(piece)
            foot = min(verts, key=lambda v: (v.co - ground).length)

            def corner(v):
                rim = [e for e in v.link_edges if sum(1 for f in e.link_faces if f in inside) == 1]
                return (rim[0].other_vert(v).co - v.co).angle(rim[1].other_vert(v).co - v.co) if len(rim) == 2 else math.pi

            # The tip is the sharpest corner of the blade's outline.
            tip = min((v for v in verts if v is not foot), key=corner)
            change(verts, foot.co.copy(), tip, piece, bm)

    edit(run, name)


def stubby_blades(spec):
    """Every blade shrunk to a quarter of its length, about its foot."""
    def shrink(verts, foot, tip, piece, bm):
        for v in verts:
            v.co = foot + (v.co - foot) * 0.25

    each_blade(spec, shrink)


def wide_blades(spec):
    """Every blade three times as wide: pads, not blades."""
    def widen(verts, foot, tip, piece, bm):
        across = (tip.co - foot).cross(Vector((0, 0, 1))).normalized()
        for v in verts:
            v.co += across * (v.co - foot).dot(across) * 2

    each_blade(spec, widen)


def blunt_blades(spec):
    """Every blade cut off square before its tip."""
    def cut(verts, foot, tip, piece, bm):
        bmesh.ops.delete(bm, geom=[tip], context="VERTS")

    each_blade(spec, cut)


def floating_blades(spec):
    """Every blade lifted 0.3 m off the crown."""
    def lift(verts, foot, tip, piece, bm):
        for v in verts:
            v.co.z += 0.3

    each_blade(spec, lift)


def one_sided_blades(spec):
    """Every blade swung round to one side of the plant: a fan, not a rosette."""
    def swing(verts, foot, tip, piece, bm):
        way = tip.co - foot
        turn = Matrix.Rotation(-math.atan2(way.y, way.x) * 0.75, 3, "Z")
        for v in verts:
            v.co = turn @ v.co

    each_blade(spec, swing)


def upright_blades(spec):
    """Every blade stood straight up on its foot."""
    def stand(verts, foot, tip, piece, bm):
        turn = (tip.co - foot).rotation_difference(Vector((0, 0, 1))).to_matrix()
        for v in verts:
            v.co = foot + turn @ (v.co - foot)

    each_blade(spec, stand)


def straight_blades(spec):
    """The plant drawn again with every blade a straight strip from its foot to its tip: sticks, with no arch."""
    from plant_parts import family_generator

    generator = family_generator("blade_plant")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    saved, generator.ARCH = generator.ARCH, 0.0
    try:
        generator.build_plant(spec)
    finally:
        generator.ARCH = saved


# Tall grass and reeds (source/tall_grass, source/reeds): a clump of blades, some of them stalks that carry a head.


def sparse_clump(spec):
    """Two blades of every three taken out: a few spikes, with sky between them."""
    import foliage

    name = spec["objects"][0]
    slot = [slot.material.name for slot in bpy.data.objects[name].material_slots].index(spec["foliage"]["material"])

    def thin(bm):
        pieces = foliage.pieces_of(bm, slot)
        gone = {face for k, piece in enumerate(pieces) if k % 3 for face in piece}
        bmesh.ops.delete(bm, geom=list(gone), context="FACES")

    edit(thin, name)


def splayed_clump(spec):
    """Every blade tipped 25 degrees further out about its foot: a fan, with nothing standing."""
    def tip_out(verts, foot, tip, piece, bm):
        way = Vector((tip.co.x - foot.x, tip.co.y - foot.y, 0))
        way = way.normalized() if way.length > 1e-6 else Vector((1, 0, 0))
        turn = Matrix.Rotation(math.radians(25), 3, Vector((0, 0, 1)).cross(way))
        for v in verts:
            v.co = foot + turn @ (v.co - foot)

    each_blade(spec, tip_out)


def each_head(spec, change):
    """Apply change(head's vertices, its faces, bm) to every head: every closed piece of the closed material that does not stand on the ground."""
    from validate import pieces_in

    name = spec["objects"][0]
    slot = [slot.material.name for slot in bpy.data.objects[name].material_slots].index(spec["foliage"]["material"])
    ground = spec["bounds_m"]["min"][2]

    def run(bm):
        for piece in pieces_in([f for f in bm.faces if f.material_index != slot]):
            verts = list({v for face in piece for v in face.verts})
            if min(v.co.z for v in verts) > ground + 0.01:
                change(verts, piece, bm)

    edit(run, name)


def no_heads(spec):
    """Every head taken off its stalk."""
    each_head(spec, lambda verts, piece, bm: bmesh.ops.delete(bm, geom=verts, context="VERTS"))


def heads_low(spec):
    """Every head slid down to under half the plant's height."""
    drop = (spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]) * 0.5

    def lower(verts, piece, bm):
        for v in verts:
            v.co.z -= drop

    each_head(spec, lower)


def heads_adrift(spec):
    """Every head moved 0.4 m to one side, and up out of the plant: carried by nothing."""
    def move(verts, piece, bm):
        for v in verts:
            v.co += Vector((0.4, 0.0, 0.3))

    each_head(spec, move)


def fat_heads(spec):
    """Every head made three times its size about its own middle."""
    def swell(verts, piece, bm):
        middle = sum((v.co for v in verts), Vector()) / len(verts)
        for v in verts:
            v.co = middle + (v.co - middle) * 3

    each_head(spec, swell)


# A bed of reeds (source/reeds): stalks that stand apart and carry leaves and heads.


def reed_pieces(bm, slot):
    """(stalks, leaves): the foliage's open pieces, told apart as tools/validate.py tells them: a stalk's open edge is a small ring, a leaf's its whole outline."""
    import foliage

    stalks, leaves = [], []
    for piece in foliage.pieces_of(bm, slot):
        inside = set(piece)
        verts = list({v for face in piece for v in face.verts})
        rim = sum(e.calc_length() for e in {e for face in piece for e in face.edges} if sum(1 for f in e.link_faces if f in inside) == 1)
        (stalks if rim < max((a.co - b.co).length for a in verts for b in verts) else leaves).append(verts)
    return stalks, leaves


def each_reed(spec, change_stalk=None, change_leaf=None):
    """Apply change_stalk(vertices, foot, bm) to every stalk and change_leaf(vertices, bm) to every leaf of a bed of reeds."""
    name = spec["objects"][0]
    slot = [slot.material.name for slot in bpy.data.objects[name].material_slots].index(spec["foliage"]["material"])

    def run(bm):
        stalks, leaves = reed_pieces(bm, slot)
        for verts in stalks if change_stalk else []:
            low = min(v.co.z for v in verts)
            ring = [v.co for v in verts if v.co.z < low + 0.02]
            change_stalk(verts, sum(ring, Vector()) / len(ring), bm)
        for verts in leaves if change_leaf else []:
            change_leaf(verts, bm)

    edit(run, name)


def redrawn_reeds(spec, **constants):
    """The bed drawn again with some of its generator's constants changed."""
    from plant_parts import family_generator

    generator = family_generator("reeds")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    saved = {key: getattr(generator, key) for key in constants}
    try:
        for key, value in constants.items():
            setattr(generator, key, value)
        generator.build_bed(spec)
    finally:
        for key, value in saved.items():
            setattr(generator, key, value)


def flat_stalks(spec):
    """Every stalk pressed flat about its foot: a strip, seen edge on from one side."""
    def press(verts, foot, bm):
        for v in verts:
            v.co.x = foot.x + (v.co.x - foot.x) * 0.1

    each_reed(spec, press)


def gathered_stalks(spec):
    """Every stalk moved to stand at the origin: a rosette from one point, not a bed."""
    def gather(verts, foot, bm):
        for v in verts:
            v.co -= Vector((foot.x, foot.y, 0)) * 0.97

    each_reed(spec, gather)


def floating_stalks(spec):
    """Every stalk lifted 0.2 m off the ground."""
    def lift(verts, foot, bm):
        for v in verts:
            v.co.z += 0.2

    each_reed(spec, lift)


def leaning_stalks(spec):
    """Every stalk tipped 15 degrees over about its foot, all one way: a bed blown flat."""
    turn = Matrix.Rotation(math.radians(15), 3, "X")

    def tip_over(verts, foot, bm):
        for v in verts:
            v.co = foot + turn @ (v.co - foot)

    each_reed(spec, tip_over)


def swaying_stalks(spec):
    """Every stalk tipped 7.5 degrees about its foot, each its own way: none far over, and few upright."""
    turns = iter(range(1000))

    def sway(verts, foot, bm):
        turn = Matrix.Rotation(math.radians(7.5), 3, Matrix.Rotation(next(turns) * 2.4, 3, "Z") @ Vector((1, 0, 0)))
        for v in verts:
            v.co = foot + turn @ (v.co - foot)

    each_reed(spec, sway)


def few_stalks(spec):
    """All but three stalks taken out."""
    name = spec["objects"][0]
    slot = [slot.material.name for slot in bpy.data.objects[name].material_slots].index(spec["foliage"]["material"])

    def thin(bm):
        stalks, _ = reed_pieces(bm, slot)
        bmesh.ops.delete(bm, geom=[v for verts in stalks[3:] for v in verts], context="VERTS")

    edit(thin, name)


def bare_stalks(spec):
    """Every leaf taken off."""
    each_reed(spec, change_leaf=lambda verts, bm: bmesh.ops.delete(bm, geom=verts, context="VERTS"))


def leaves_adrift(spec):
    """Every leaf moved 0.25 m up and to one side of its stalk: on nothing."""
    def move(verts, bm):
        for v in verts:
            v.co += Vector((0.12, 0.12, 0.25))

    each_reed(spec, change_leaf=move)


def broad_leaves(spec):
    """The bed drawn again with leaves five times as wide: paddles."""
    redrawn_reeds(spec, LEAF_WIDTH=(0.2, 0.25))


def planar_leaves(spec):
    """The bed drawn again with every leaf bending in one upright plane, as a tall grass blade does: a star of straight lines from above."""
    redrawn_reeds(spec, LEAF_TURN=(0.0, 0.0), LEAF_ROLL=0.0)


def thin_heads(spec):
    """Every head made a third as thick: a swelling of the stalk, not a cattail."""
    def thin(verts, piece, bm):
        middle = sum((v.co for v in verts), Vector()) / len(verts)
        for v in verts:
            v.co.x, v.co.y = middle.x + (v.co.x - middle.x) * 0.33, middle.y + (v.co.y - middle.y) * 0.33

    each_head(spec, thin)


def spindle_heads(spec):
    """The bed drawn again with every head a spindle pointed at both ends, as a grass's seed head is: not a sausage."""
    redrawn_reeds(spec, HEAD_RINGS=((0.35, 1.0),))


def every_stalk_headed(spec):
    """The bed drawn again with a head on every stalk but one."""
    redrawn_reeds(spec, HEADS=(0.9, 0.9), HEAD_COUNT=(2, 8), STALKS_PER_M=(10.0, 10.0), HEAD_STALK=(0.9, 1.0))


# The table rock (source/table_rock): a cap held off the ground on narrow necks.


def table_pieces(bm):
    """The table rock's pieces as lists of vertices: (the cap, which stands on nothing; the neck, the tallest that stands on the ground; the rest)."""
    from validate import pieces_in

    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    cap = max(pieces, key=lambda verts: min(v.co.z for v in verts))
    standing = sorted((verts for verts in pieces if verts is not cap), key=lambda verts: max(v.co.z for v in verts), reverse=True)
    return cap, standing[0], standing[1:]


def cap_pressed_down(spec):
    """The cap lowered until its underside is half the clearance above the ground: a player no longer fits under it."""

    def press(bm):
        cap = table_pieces(bm)[0]
        drop = min(v.co.z for v in cap) - spec["bounds_m"]["min"][2] - spec["table"]["min_clear_m"] / 2
        bmesh.ops.translate(bm, verts=cap, vec=(0, 0, -drop))

    edit(press, "table_rock_1")


def fat_neck(spec):
    """The neck made 2.5 times as wide: a pedestal, not a neck."""

    def widen(bm):
        neck = table_pieces(bm)[1]
        middle = sum((v.co for v in neck), Vector()) / len(neck)
        for v in neck:
            v.co.x = middle.x + (v.co.x - middle.x) * 2.5
            v.co.y = middle.y + (v.co.y - middle.y) * 2.5

    edit(widen, "table_rock_1")


def neck_cut_short(spec):
    """The neck pressed down to a third of its height: a second block, and nothing holds the cap up."""

    def press(bm):
        floor = spec["bounds_m"]["min"][2]
        for v in table_pieces(bm)[1]:
            v.co.z = floor + (v.co.z - floor) / 3

    edit(press, "table_rock_1")


def neck_at_rim(spec):
    """The neck and its block moved out until the neck stands 0.1 m in from the right of the bounds: the cap overhangs to one side only."""

    def move(bm):
        _, neck, rest = table_pieces(bm)
        shift = spec["bounds_m"]["max"][0] - 0.1 - max(v.co.x for v in neck)
        bmesh.ops.translate(bm, verts=neck + [v for verts in rest for v in verts], vec=(shift, 0, 0))

    edit(move, "table_rock_1")


# The arch (source/arch): two piers that reach the ground and a span resting on both, with open air right through.


def arch_pieces(bm, spec):
    """The arch's pieces as lists of vertices: (the span, the widest piece held off the ground; the other pieces held
    off the ground; the pier blocks on the ground, the two tallest; the rubble, the rest on the ground)."""
    from validate import pieces_in

    floor = spec["bounds_m"]["min"][2]
    pieces = [list({v for f in piece for v in f.verts}) for piece in pieces_in(bm.faces)]
    held = sorted((verts for verts in pieces if min(v.co.z for v in verts) > floor + 0.01), key=lambda verts: max(v.co.x for v in verts) - min(v.co.x for v in verts), reverse=True)
    standing = sorted((verts for verts in pieces if min(v.co.z for v in verts) <= floor + 0.01), key=lambda verts: max(v.co.z for v in verts), reverse=True)
    return held[0], held[1:], standing[:2], standing[2:]


def span_lifted(spec):
    """The lintel raised 0.5 m off its piers: daylight between them, and no hole closed over."""
    edit(lambda bm: bmesh.ops.translate(bm, verts=arch_pieces(bm, spec)[0], vec=(0, 0, 0.5)), "arch_1")


def pier_off_the_ground(spec):
    """The lower block of one pier raised 0.3 m: the pier does not reach the ground. Seen from the front the rubble at its
    foot hides the gap, so the hole stays closed; nothing under the span runs down to the ground on that side."""
    edit(lambda bm: bmesh.ops.translate(bm, verts=arch_pieces(bm, spec)[2][1], vec=(0, 0, 0.3)), "arch_1")


def span_pressed_down(spec):
    """The lintel lowered until its underside is 1.2 m above the ground: a player no longer walks under it."""

    def press(bm):
        span = arch_pieces(bm, spec)[0]
        bmesh.ops.translate(bm, verts=span, vec=(0, 0, spec["bounds_m"]["min"][2] + 1.2 - min(v.co.z for v in span)))

    edit(press, "arch_1")


def rubble_in_the_passage(spec):
    """The largest rubble block moved to the middle of the opening: the passage is blocked."""

    def move(bm):
        _, _, piers, rubble = arch_pieces(bm, spec)
        block = max(rubble, key=lambda verts: max(v.co.z for v in verts))
        inner = sorted(x for verts in piers for x in (min(v.co.x for v in verts), max(v.co.x for v in verts)))[1:3]
        middle = sum(v.co.x for v in block) / len(block)
        bmesh.ops.translate(bm, verts=block, vec=((inner[0] + inner[1]) / 2 - middle, 0, 0))

    edit(move, "arch_1")


def span_behind_the_piers(spec):
    """The lintel moved back by the depth of the bounds: from the front it still closes the opening, and it rests on nothing."""
    depth = spec["bounds_m"]["max"][1] - spec["bounds_m"]["min"][1]
    edit(lambda bm: bmesh.ops.translate(bm, verts=arch_pieces(bm, spec)[0], vec=(0, depth, 0)), "arch_1")


def trilithon(spec):
    """The first arch_1, which passed every gate and reads as a door frame of dressed blocks: two matched upright piers of
    squared blocks under a level squared lintel. Built by the generator of that day (tests/fixtures/arch_trilithon.py)
    from its spec, in place of the arch, and measured against its own bounds."""
    import importlib.util

    module = importlib.util.spec_from_file_location("arch_trilithon", ROOT / "tests" / "fixtures" / "arch_trilithon.py")
    generator = importlib.util.module_from_spec(module)
    module.loader.exec_module(generator)
    old = json.loads((ROOT / "tests" / "fixtures" / "arch_trilithon.spec.json").read_text())
    bpy.data.objects.remove(bpy.data.objects["arch_1"])
    for held in (bpy.data.meshes, bpy.data.materials):
        for block in list(held):
            if not block.users:
                held.remove(block)
    # The first arch that seed drew was the one it kept, so nothing need be measured here: the checks of that day asked less of a spec.
    generator.build_arch(old, strict=False)
    spec["bounds_m"] = old["bounds_m"]


def tall_pebble(spec):
    """The pebble stretched to 0.36 as tall as it is wide, and its spec with it: the proportion the
    first pebble_2 was specified, built and passed with, while its brief said "low"."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]
    height = 0.36 * max(hi[0] - lo[0], hi[1] - lo[1])
    stretch = height / (hi[2] - lo[2])

    def raise_it(bm):
        for vert in bm.verts:
            vert.co.z = lo[2] + (vert.co.z - lo[2]) * stretch

    edit(raise_it, "pebble_2")
    hi[2] = lo[2] + height


def cut_block(spec):
    """The pebble cut through by one steep plane and stretched back to its bounds: a block with one big cut face."""

    def cut(bm):
        lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
        normal = Vector((math.cos(math.radians(20)), 0, math.sin(math.radians(20))))
        through = (lo + hi) / 2 + Vector((0.1 * (hi.x - lo.x), 0, 0))
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-7, plane_co=through, plane_no=normal, clear_outer=True)
        before = set(bm.faces)
        bmesh.ops.holes_fill(bm, edges=[g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)])
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if f not in before])
        fit_to_bounds(bm, spec)

    edit(cut, "pebble_2")


# A boulder (source/boulder): one heavy lump. Each mutation keeps the mesh closed and at its bounds.


def stump_boulder(spec):
    """The boulder above three tenths of its height drawn in to 0.55 of its width: a trunk on a spread foot, the
    stump that `source/rock` read as while passing every gate."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])

    def pinch(bm):
        for vert in bm.verts:
            if vert.co.z > lo.z + 0.3 * (hi.z - lo.z):
                vert.co.x, vert.co.y = 0.55 * vert.co.x, 0.55 * vert.co.y
        fit_to_bounds(bm, spec)

    edit(pinch, "boulder_2")


def rooted_boulder(spec):
    """Three sectors of the boulder drawn in to 0.4 of their reach: seen from above, a lump with roots between notches."""

    def notch(bm):
        for vert in bm.verts:
            if math.cos(3 * math.atan2(vert.co.y, vert.co.x)) < -0.3:
                vert.co.x, vert.co.y = 0.4 * vert.co.x, 0.4 * vert.co.y
        fit_to_bounds(bm, spec)

    edit(notch, "boulder_2")


def tall_boulder(spec):
    """The boulder stretched to three times its height, and its spec with it: every flank a wall."""
    lo, hi = spec["bounds_m"]["min"], spec["bounds_m"]["max"]

    def raise_it(bm):
        for vert in bm.verts:
            vert.co.z = lo[2] + (vert.co.z - lo[2]) * 3

    edit(raise_it, "boulder_2")
    hi[2] = lo[2] + 3 * (hi[2] - lo[2])


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
    (piece_inside_out, "tracer.normals_outward"),
    (piece_floats, "tracer.overlap_touch"),
    (piece_buried, "tracer.overlap_buried"),
    (one_piece, "tracer.overlap_count"),
    (twin_overlapping_pieces, "tracer.overlap_size_order"),
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
    (tipped_tops, "slab_1.top_level", "slab_1"),
    (plate_lifted, "slab_1.overlap_touch", "slab_1"),
    (plate_inside_out, "slab_1.normals_outward", "slab_1"),
    (tall_pebble, "pebble_2.low", "pebble_2"),
    (cut_block, "pebble_2.rounded", "pebble_2"),
    (stump_boulder, "boulder_2.mass_convex", "boulder_2"),
    (rooted_boulder, "boulder_2.mass_outline", "boulder_2"),
    (tall_boulder, "boulder_2.mass_slopes", "boulder_2"),
    (tall_boulder, "boulder_2.low", "boulder_2"),
    (even_heights, "crag_1.cluster_steps_down", "crag_1"),
    (one_prism, "crag_1.cluster_steps_down", "crag_1"),
    (upright_prisms, "crag_1.cluster_leans", "crag_1"),
    (fanned_prisms, "crag_1.cluster_leans_together", "crag_1"),
    (stones_sunk, "stack_1.pile_rests", "stack_1"),
    (tall_stones, "stack_1.pile_flat", "stack_1"),
    (even_stones, "stack_1.pile_smaller", "stack_1"),
    (pushed_over, "stack_1.pile_balanced", "stack_1"),
    (cap_pressed_down, "table_rock_1.table_shelter", "table_rock_1"),
    (fat_neck, "table_rock_1.table_necks", "table_rock_1"),
    (neck_cut_short, "table_rock_1.table_necks", "table_rock_1"),
    (neck_at_rim, "table_rock_1.table_overhang", "table_rock_1"),
    (top_tier_removed, "spire_1.spire_tiers", "spire_1"),
    (tier_hangs_off, "spire_1.spire_stands_on", "spire_1"),
    (plain_column, "spire_1.spire_steps_in", "spire_1"),
    (pointed_caps, "spire_1.spire_ledges", "spire_1"),
    (banded_base, "spire_1.spire_flutes", "spire_1"),
    (telescoped, "spire_1.spire_off_centre", "spire_1"),
    (telescoped, "spire_1.spire_leans", "spire_1"),
    (telescoped, "spire_1.spire_steps_differ", "spire_1"),
    (span_lifted, "arch_1.arch_through", "arch_1"),
    (pier_off_the_ground, "arch_1.arch_rests", "arch_1"),
    (span_pressed_down, "arch_1.arch_opening", "arch_1"),
    (rubble_in_the_passage, "arch_1.arch_opening", "arch_1"),
    (span_behind_the_piers, "arch_1.arch_rests", "arch_1"),
    (trilithon, "arch_1.lean", "arch_1"),
    (trilithon, "arch_1.arch_opening_shape", "arch_1"),
    (trilithon, "arch_1.arch_sides_differ", "arch_1"),
    (trilithon, "arch_1.arch_top_broken", "arch_1"),
    (tapered_block, "block_2.block_square", "block_2"),
    (plain_box, "block_2.block_chamfers", "block_2"),
    (plain_box, "block_2.cracks", "block_2"),
    (crack_filled, "block_2.cracks", "block_2"),
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
    (stubby_blades, "blade_plant_1.blade_size", "blade_plant_1"),
    (wide_blades, "blade_plant_1.blade_shape", "blade_plant_1"),
    (blunt_blades, "blade_plant_1.blade_shape", "blade_plant_1"),
    (floating_blades, "blade_plant_1.blades_rooted", "blade_plant_1"),
    (one_sided_blades, "blade_plant_1.blades_spread", "blade_plant_1"),
    (upright_blades, "blade_plant_1.blades_lean", "blade_plant_1"),
    (straight_blades, "blade_plant_1.blades_arch", "blade_plant_1"),
    (sparse_clump, "tall_grass_1.clump_dense", "tall_grass_1"),
    (splayed_clump, "tall_grass_1.clump_upright", "tall_grass_1"),
    (no_heads, "tall_grass_1.heads", "tall_grass_1"),
    (fat_heads, "tall_grass_1.heads", "tall_grass_1"),
    (heads_low, "tall_grass_1.heads_high", "tall_grass_1"),
    (heads_adrift, "tall_grass_1.heads_carried", "tall_grass_1"),
    (few_stalks, "reeds_1.stalks", "reeds_1"),
    (flat_stalks, "reeds_1.stalk_shape", "reeds_1"),
    (gathered_stalks, "reeds_1.stalks_bed", "reeds_1"),
    (floating_stalks, "reeds_1.stalks_bed", "reeds_1"),
    (leaning_stalks, "reeds_1.stalks_lean", "reeds_1"),
    (swaying_stalks, "reeds_1.clump_upright", "reeds_1"),
    (sparse_clump, "reeds_1.clump_dense", "reeds_1"),
    (bare_stalks, "reeds_1.leaves", "reeds_1"),
    (leaves_adrift, "reeds_1.leaves", "reeds_1"),
    (broad_leaves, "reeds_1.leaf_shape", "reeds_1"),
    (planar_leaves, "reeds_1.leaves_bend", "reeds_1"),
    (thin_heads, "reeds_1.heads_thick", "reeds_1"),
    (spindle_heads, "reeds_1.heads_thick", "reeds_1"),
    (every_stalk_headed, "reeds_1.heads_share", "reeds_1"),
    (no_heads, "reeds_1.heads", "reeds_1"),
    (fat_heads, "reeds_1.heads", "reeds_1"),
    (heads_low, "reeds_1.heads_high", "reeds_1"),
    (heads_adrift, "reeds_1.heads_carried", "reeds_1"),
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
