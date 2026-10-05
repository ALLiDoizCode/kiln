"""Painted shading (ADR 9, ADR 10): colour computed from an asset's shape and baked into one texture.

`apply(spec)` is called by tools/build.py after an asset's own build script,
when the spec has a `painted_shading` block. The build script stays as it is:
it gives each material one flat colour, and this step unwraps the mesh, bakes
the painted colour from that flat colour and the spec, and puts the texture on
the material in place of the flat colour.

The colour at a point, in linear RGB, is

    mix(material colour, growth colour at the material's own lightness, growth mask)
      * (1 - growth_darker * the patches of growth above the reach of the growth at the base)
      * mix(base_tint, top_tint, height within the spec's bounds)
      * (1 - side_shade * how upright the face is * how near mid height the point is)
      * (1 + blotch * a broad patch pattern between -1 and 1)
      * (1 - crevice_shadow * how enclosed the point is), where the spec asks a crevice shadow
      * (1 + edge_light * how close the point is to an exposed edge)

The growth mask is the largest of three: below `growth_height_m`, with a ragged
top; patches covering about `growth_up` of the faces that are near level; and
patches along about `growth_edges` of the exposed edges in the upper part,
reaching `growth_edge_m` in from an edge.
Growth changes hue, and the blotch pattern averages nothing. Where a spec gives
`growth_darker`, the patches on level faces and along edges are that much darker
than the surface round them as well, as moss is on pale lit rock; the growth
at the base stays at the material's lightness. The darkening multiplies the
colour and leaves its hue alone, so crates/asset_smoke can still tell how much
growth a texel shows by hue, and measure the rest against these lines. With
`growth_patch_m` the patches are about that size and broken up by a finer pattern.
Nothing here is random: the patterns are Blender's noise texture at fixed
places in space and Cycles runs on the CPU with a fixed seed, so a rebuild
gives the same texels.

`KILN_BAKE=gpu` in the environment bakes on the graphics card instead (CUDA),
in a tenth of the time, for looking at candidates: a handful of texels in a
million then differ by one level from one run to the next, so nothing gated
or committed is baked that way (tools/gate.sh unsets it). Unset, or `cpu`,
the bake is the CPU's. See `bake` for what is done about a card that is busy,
missing or out of memory (docs/research/gpu-acceleration.md has the measurements).

Foliage is not baked (ADR 11). A spec with a `foliage` block names the leaf
material; its faces are left out of the unwrap and the bake, and `leaf_colours`
gives every leaf piece one flat colour instead: a strip along the top of the
same texture holds a palette of swatches, and all of a piece's UVs sit on the
middle of one swatch. Which swatch comes from the mesh alone (tools/foliage.py):
the shade from how high the piece sits in its pad, the tone from a fixed
shuffle, so neighbouring pieces differ.

Run under Blender, through tools/build.py.
"""

import fcntl
import math
import os
import random
import time

import addon_utils
import bmesh
import bpy
import foliage
import numpy
from pipeline import linear_rgb

UV_LAYER = "paint"
LUMA = (0.2126, 0.7152, 0.0722)
# The outline of the growth: its top edge wanders by this share of growth_height_m,
# over lumps about 1 / GROWTH_NOISE_SCALE metres across, and fades out over GROWTH_FADE of it.
GROWTH_RAGGED = 0.5
GROWTH_NOISE_SCALE = 1.6
GROWTH_FADE = 0.3
# Patches of growth, on level faces and along upper edges: lumps about 1 / GROWTH_PATCH_SCALE metres
# across with an edge PATCH_EDGE of the noise's range wide. The noise is near 0.5 on average and
# NOISE_SPREAD either side for most of a surface, which turns a cover asked for into a threshold.
GROWTH_PATCH_SCALE = 1.7
PATCH_EDGE = 0.05
NOISE_SPREAD = 0.2
# With `growth_patch_m`: a second pattern, GROWTH_BREAK_SCALE times finer, knocks holes in the
# patches and leaves GROWTH_BREAK_KEEP of each, and the patches are that much commoner to make up for it.
GROWTH_BREAK_SCALE, GROWTH_BREAK_KEEP = 2.5, 0.7
GROWTH_EDGES_FROM = (0.5, 0.75)  # share of the height over which edge growth comes in
BLOTCH_EDGE = 0.1  # how much of the noise's range a blotch's border takes: soft, but a patch and not a haze
# The crevice shadow is full where `crevice_sky_hidden` of the sky is hidden (conventions.toml, which
# crates/asset_smoke reads too: one definition of a crevice), and where pieces overlap (ADR 13) the shadow
# at a join is full where another piece hides `join_sky_hidden` of it. The edge light is full where a
# sixteenth of the solid behind the face is missing, as beside the bevel strip of a right-angled corner.
FULL_EDGE_OCCLUSION = 0.06
# Faces within this of straight down, at the floor of the bounds, are the hidden underside.
UNDERSIDE_COS = 0.999
UNDERSIDE_UV_SCALE = 0.05  # texel density of an underside nobody sees, beside the rest
# Grain (bark): tone that runs in streaks along a limb. The build script says which way that is with a
# face-corner attribute of this name: (metres across the grain, metres along it, a number per limb).
GRAIN_ATTRIBUTE = "grain"
GRAIN_STRETCH = 7.0  # a streak is this many times as long as it is wide
GRAIN_FINE = 0.5  # fine streaks: their width over `grain_width_m`
GRAIN_FINE_TONE = 0.8  # and how far they lighten and darken, over `grain`
# Furrows: dark lines that wander along the limb and run into each other, with plates of bark between.
FURROW_WIDTH = 3.0  # plates are about this many grain widths across
FURROW_HALF = 0.1  # half a furrow's width, as a share of the noise's range
FURROW_DEPTH = 1.8  # how dark a furrow is, over `grain`
FURROW_WANDER = 1.2  # how far furrows wander (the noise's distortion)
GRAIN_LIFT = 0.96  # the tone is lifted by this, times `grain`, to keep its mean: furrows darken more than ridges lighten
RIDGE_LIGHT = 0.7  # how light the lip of a plate beside a furrow is, over `grain`
PLATE_TONE = 0.15  # how far neighbouring plates differ in tone, over `grain`
KNOT_SPACING_M = 0.3  # one place a knot may be per square of this size
KNOT_SHARE = 0.22  # share of those places that have one
KNOT_RADIUS_M = 0.035
KNOT_DEPTH = 1.3  # how dark a knot's middle is, over `grain`
CLOSE_PASSES = 5  # how many times the layout is repacked to give close faces their texels
# Overlapping pieces are baked apart, so that a piece's edge light comes from its own shape (`paint_nodes`, hidden).
# tests/slab_mutations.py turns this off to paint a slab as one solid, joins lit as edges.
SPLIT_PIECES = True
# The bake on the graphics card (`KILN_BAKE=gpu`). One at a time on the whole machine, whichever working
# copy asks: eight at once ran a 10 GB card out of memory. The lock is this file, held while the card is in use.
BAKE_ENV = "KILN_BAKE"
GPU_LOCK = "/tmp/kiln-gpu-bake.lock"
# Cycles sizes its working memory by the card and not by the scene; this share of it is plenty for one texture.
GPU_STATES_FACTOR = "0.25"
# A card out of memory can leave a wrong texture and say the bake finished. So the same bake is done
# again on the CPU, CHECK_SHRINK times smaller each way, and the two compared texel by coarse texel, away
# from the borders of islands: they disagree when they are more than CHECK_STEP apart (of 1) in any
# channel, and the bake is wrong when more than CHECK_SHARE of them disagree. Measured: 0 of a right
# slab's and rock's disagree and 0.001 of a tree's bark, and all of a bake that ran out of memory.
CHECK_SHRINK = 8
CHECK_STEP = 0.12
CHECK_SHARE = 0.02


def grain_tones(paint):
    """What grain makes of a surface's tone, over the tone without it, for the load test to hold open faces to.

    Grain is two tones and not one with a little variation: furrows, and the plates between them, each
    about half the surface. Their mean is 1 (GRAIN_LIFT), but only over a whole limb; over a few open faces
    the shares differ and the mean with them. Each tone is the same wherever it is: the middle of a furrow
    (the fine streaks lighten it as much as they darken it), the top of the range the streaks give a furrow,
    and the middle of a plate.
    """
    grain = paint["grain"]
    plate, furrow = 1.0 + grain * GRAIN_LIFT, 1.0 - grain * FURROW_DEPTH
    return {"grain_furrow_tone": round(plate * furrow, 6), "grain_furrow_top": round((plate + grain * GRAIN_FINE_TONE) * furrow, 6), "grain_plate_tone": round(plate, 6)}


def luminance(rgb):
    return sum(c * w for c, w in zip(rgb, LUMA))


def growth_colour(material_rgb, growth_hex):
    """The growth colour scaled to the material's lightness: growth changes hue, the tints change value."""
    growth = linear_rgb(growth_hex)
    scale = luminance(material_rgb) / luminance(growth)
    return tuple(min(1.0, c * scale) for c in growth)


def unwrap(objects, spec, conv, skip=None, keep_clear=0.0):
    """Give every object one shared, non-overlapping UV layout filling the 0..1 square.

    Faces of the material named `skip` are left out, and `keep_clear` is the
    share of the texture's height, at the top, that the layout stays out of."""
    paint = spec["painted_shading"]
    floor_z = spec["bounds_m"]["min"][2]
    tol = spec["bounds_tolerance_m"]
    for obj in objects:
        mesh = obj.data
        while mesh.uv_layers:
            mesh.uv_layers.remove(mesh.uv_layers[0])
        mesh.uv_layers.new(name=UV_LAYER)
    view_layer = bpy.context.view_layer
    for obj in bpy.context.scene.objects:
        obj.select_set(obj in objects)
    view_layer.objects.active = objects[0]

    # Unwrapping has no data API. Operators report failure by return value.
    margin = conv["painted_shading"]["island_gap_px"] / paint["texture_px"]

    def run(operator, **options):
        result = operator(**options)
        if result != {"FINISHED"}:
            raise RuntimeError(f"{operator.idname()} failed: {result}")

    run(bpy.ops.object.mode_set, mode="EDIT")
    run(bpy.ops.mesh.select_all, action="SELECT")
    if skip is not None:
        # Leaf pieces take their colour from the palette, not from an island of their own.
        for obj in objects:
            bm = bmesh.from_edit_mesh(obj.data)
            for face in bm.faces:
                if obj.material_slots[face.material_index].material.name == skip:
                    face.select_set(False)
            bm.select_flush_mode()
            bmesh.update_edit_mesh(obj.data)
    if any(edge.use_seam for obj in objects for edge in obj.data.edges):
        # The build script marked seams: where the surface may be cut to lie flat. A tree's limbs,
        # unwrapped by angle, come out as strips as long as the trunk; the longest sets the scale
        # of the whole layout and most of the texture stays empty.
        run(bpy.ops.uv.unwrap, method="ANGLE_BASED", margin=margin)
        run(bpy.ops.uv.average_islands_scale)
    else:
        run(bpy.ops.uv.smart_project, angle_limit=math.radians(conv["painted_shading"]["unwrap_angle_deg"]), island_margin=margin, scale_to_bounds=False)
    if paint["hidden_underside"]:
        # Shrink the underside's islands before packing, so the visible faces get the texels.
        for obj in objects:
            bm = bmesh.from_edit_mesh(obj.data)
            uv = bm.loops.layers.uv[UV_LAYER]
            world = obj.matrix_world
            for face in bm.faces:
                if (world.to_3x3() @ face.normal).z < -UNDERSIDE_COS and all(abs((world @ v.co).z - floor_z) <= tol for v in face.verts):
                    for loop in face.loops:
                        loop[uv].uv *= UNDERSIDE_UV_SCALE
            bmesh.update_edit_mesh(obj.data)
    # The exact (concave) packer takes 15 s on the rock for 3% more of the texture; boxes take none.
    run(bpy.ops.uv.pack_islands, rotate=True, scale=True, margin_method="FRACTION", margin=margin, shape_method="AABB")
    run(bpy.ops.object.mode_set, mode="OBJECT")
    if "close_texels_per_m" in paint:
        def repack():
            run(bpy.ops.object.mode_set, mode="EDIT")
            run(bpy.ops.uv.pack_islands, rotate=True, scale=True, margin_method="FRACTION", margin=margin, shape_method="AABB")
            run(bpy.ops.object.mode_set, mode="OBJECT")

        densify_close(objects, spec, conv, skip, keep_clear, repack)
    if keep_clear:
        # Shrink the layout toward the bottom-left corner; texels stay square.
        for obj in objects:
            for corner in obj.data.uv_layers[UV_LAYER].data:
                corner.uv = corner.uv * (1.0 - keep_clear)


def texel_densities(obj, size):
    """Texels per metre of every polygon of an object, as its UVs lie now: the sparsest of the triangles it exports as."""
    mesh, world = obj.data, obj.matrix_world
    uvs = mesh.uv_layers[UV_LAYER].data
    found = []
    for polygon in mesh.polygons:
        corners = [uvs[i].uv for i in polygon.loop_indices]
        points = [world @ mesh.vertices[i].co for i in polygon.vertices]
        least = float("inf")
        # Both ways of cutting a quad in two: the exporter picks one.
        for first in range(2 if len(points) == 4 else 1):
            for step in range(1, len(points) - 1):
                a, b, c = (first, first + step, first + step + 1) if len(points) == 4 and step == 1 else (first, (first + step) % len(points), (first + step + 1) % len(points))
                area = abs((corners[b] - corners[a]).cross(corners[c] - corners[a])) / 2
                surface = (points[b] - points[a]).cross(points[c] - points[a]).length / 2
                if surface > 0:
                    least = min(least, math.sqrt(area * size * size / surface))
        found.append(least if least < float("inf") else 0.0)
    return found


def densify_close(objects, spec, conv, skip, keep_clear, repack):
    """Give the surface a player stands against its texels (`close_height_m`, `close_texels_per_m`).

    Islands that reach below `close_height_m` are enlarged, and the layout
    packed again, until their sparsest face has `close_texels_per_m`. The
    rest of the surface shrinks to make room; the conventions' own least
    density still holds for it, and the load test says so if it does not.
    Call in object mode; `repack` packs the islands again and returns there.
    """
    from bpy_extras import mesh_utils

    paint = spec["painted_shading"]
    size = paint["texture_px"]
    ceiling = spec["bounds_m"]["min"][2] + paint["close_height_m"]
    for _ in range(CLOSE_PASSES):
        least, close = float("inf"), []
        for obj in objects:
            mesh, world = obj.data, obj.matrix_world
            densities = texel_densities(obj, size)
            for island in mesh_utils.mesh_linked_uv_islands(mesh):
                polygons = [mesh.polygons[i] for i in island]
                if skip is not None and any(obj.material_slots[p.material_index].material.name == skip for p in polygons):
                    continue
                if any((world @ mesh.vertices[i].co).z <= ceiling for p in polygons for i in p.vertices):
                    close.append((mesh, polygons))
                    # The hidden underside keeps its few texels.
                    least = min([least] + [densities[p.index] for p in polygons if densities[p.index] > 0 and not (p.normal.z < -UNDERSIDE_COS and paint["hidden_underside"])])
        least *= 1.0 - keep_clear
        if not close or least >= paint["close_texels_per_m"]:
            return
        grow = paint["close_texels_per_m"] / least * 1.08
        for mesh, polygons in close:
            uvs = mesh.uv_layers[UV_LAYER].data
            corners = [i for p in polygons for i in p.loop_indices]
            middle = sum((uvs[i].uv for i in corners), uvs[corners[0]].uv * 0) / len(corners)
            for i in corners:
                uvs[i].uv = middle + (uvs[i].uv - middle) * grow
        repack()
    raise RuntimeError(f"the surface below {paint['close_height_m']} m cannot be given {paint['close_texels_per_m']} texels per metre on a {size} px texture: {least:.0f} after {CLOSE_PASSES} passes")


def no_growth_on(spec):
    """The materials growth does not take on: the wood a log shows where it is broken or sawn through (`log.wood`).

    Moss grows on bark; wood laid bare is paler than the bark and stays so (source/log/brief.md, Covers).
    tools/export.py writes these into the manifest, and the load test holds them bare (`painted.growth_wood`)."""
    return [spec["log"]["wood"]] if "log" in spec else []


def paint_nodes(tree, colour_rgb, spec, conv, grows=True):
    """Build the painted colour as nodes in `tree`. Returns (the nodes made, the colour output).

    `grows` is whether growth takes on this material: not on the wood of a log's broken and sawn ends (`no_growth_on`)."""
    paint = spec["painted_shading"]
    z0, z1 = spec["bounds_m"]["min"][2], spec["bounds_m"]["max"][2]
    made = []

    def node(kind, **settings):
        new = tree.nodes.new(kind)
        for key, value in settings.items():
            setattr(new, key, value)
        made.append(new)
        return new

    def feed(socket, value):
        if isinstance(value, bpy.types.NodeSocket):
            tree.links.new(value, socket)
        elif isinstance(value, tuple):
            socket.default_value = (*value, 1.0)
        else:
            socket.default_value = value

    def math_node(operation, a, b, clamp=False):
        new = node("ShaderNodeMath", operation=operation, use_clamp=clamp)
        feed(new.inputs[0], a)
        feed(new.inputs[1], b)
        return new.outputs[0]

    def mix(blend, factor, a, b):
        new = node("ShaderNodeMix", data_type="RGBA", blend_type=blend, clamp_result=True)
        feed(new.inputs["Factor"], factor)
        feed(new.inputs["A"], a)
        feed(new.inputs["B"], b)
        return new.outputs["Result"]

    geometry = node("ShaderNodeNewGeometry")
    split = node("ShaderNodeSeparateXYZ")
    tree.links.new(geometry.outputs["Position"], split.inputs[0])
    z = split.outputs["Z"]

    normal = node("ShaderNodeSeparateXYZ")
    tree.links.new(geometry.outputs["True Normal"], normal.inputs[0])
    up = normal.outputs["Z"]
    rules = conv["painted_shading"]

    def ramp(value, low, high, smooth=False):
        """0 at `low`, 1 at `high`, clamped; `low` may be above `high`."""
        new = node("ShaderNodeMapRange", clamp=True, interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        feed(new.inputs["Value"], value)
        new.inputs["From Min"].default_value, new.inputs["From Max"].default_value = low, high
        return new.outputs["Result"]

    def noise(scale, detail, shift):
        """Blender's noise texture over the asset's own space; `shift` moves it, so two patterns do not line up."""
        mapping = node("ShaderNodeMapping")
        tree.links.new(geometry.outputs["Position"], mapping.inputs["Vector"])
        mapping.inputs["Location"].default_value = (shift, shift * 0.7, shift * 1.3)
        new = node("ShaderNodeTexNoise", noise_dimensions="3D")
        tree.links.new(mapping.outputs["Vector"], new.inputs["Vector"])
        new.inputs["Scale"].default_value, new.inputs["Detail"].default_value = scale, detail
        return new.outputs["Fac"]

    def patches(cover, shift):
        """A mask of irregular patches covering about `cover` of a surface."""

        def above(scale, detail, share, offset):
            threshold = 0.5 + NOISE_SPREAD * (1 - 2 * share)
            return ramp(noise(scale, detail, offset), threshold - PATCH_EDGE / 2, threshold + PATCH_EDGE / 2)

        if "growth_patch_m" not in paint:
            return above(GROWTH_PATCH_SCALE, 2.0, cover, shift)
        # Small patches of the size asked for, with ragged outlines and holes knocked in them.
        scale = 1 / paint["growth_patch_m"]
        whole = above(scale, 3.0, min(0.95, cover / GROWTH_BREAK_KEEP), shift)
        return math_node("MULTIPLY", whole, above(scale * GROWTH_BREAK_SCALE, 2.0, GROWTH_BREAK_KEEP, shift + 5.0))

    # Overlapping pieces (ADR 13) are baked as an object each (`apply`). What hides the sky above
    # a face may then be another piece: that is the crevice at a join. What is missing of the
    # solid behind a face is asked of its own piece alone: another piece passing through it takes
    # nothing away, and would otherwise light every join as an exposed edge.
    apart = SPLIT_PIECES and "overlap" in spec

    def hidden(inside, distance, own_piece=None):
        occlusion = node("ShaderNodeAmbientOcclusion", samples=16, only_local=(inside or not apart) if own_piece is None else own_piece, inside=inside)
        occlusion.inputs["Distance"].default_value = distance
        tree.links.new(geometry.outputs["True Normal"], occlusion.inputs["Normal"])
        return math_node("SUBTRACT", 1.0, occlusion.outputs["AO"])

    def times(colour, factor):
        """A colour multiplied by a number."""
        grey = node("ShaderNodeCombineColor")
        for channel in grey.inputs[:3]:
            feed(channel, factor)
        return mix("MULTIPLY", 1.0, colour, grey.outputs["Color"])

    colour = colour_rgb
    if "growth" in paint and grows:
        reach = paint["growth_height_m"]
        # Where the growth stops at this spot: reach, raised or lowered by the noise.
        wander = math_node("MULTIPLY", math_node("SUBTRACT", noise(GROWTH_NOISE_SCALE, 3.0, 0.0), 0.5), 2 * GROWTH_RAGGED * reach)
        top = math_node("ADD", wander, z0 + reach)
        mask = base = math_node("DIVIDE", math_node("SUBTRACT", top, z), GROWTH_FADE * reach, clamp=True)
        settled = 0.0  # the patches, apart from the growth at the base
        if paint.get("growth_up"):
            # On faces near level, where it would settle.
            settled = math_node("MULTIPLY", ramp(up, *rules["growth_up_normal_z"]), patches(paint["growth_up"], 11.0))
        if paint.get("growth_edges"):
            # Along exposed edges, in the upper part of the asset, as far in from an edge as the spec says (`growth_edge_m`).
            rim = math_node("DIVIDE", hidden(True, paint["growth_edge_m"]), FULL_EDGE_OCCLUSION, clamp=True)
            upper = ramp(z, *(z0 + share * (z1 - z0) for share in GROWTH_EDGES_FROM))
            if "log" in spec:
                # A limb that lies has its upper edges all along it, and the upper part of its bounds is whatever
                # stands highest (a root plate, a stub): the edges of every side that faces up, from the tilt at
                # which a face is no longer upright (`side_shade_normal_z`).
                upper = ramp(up, 0.0, rules["side_shade_normal_z"][0])
            settled = math_node("MAXIMUM", settled, math_node("MULTIPLY", math_node("MULTIPLY", rim, upper), patches(paint["growth_edges"], 23.0)))
        mask = math_node("MAXIMUM", mask, settled)
        colour = mix("MIX", mask, colour, growth_colour(colour_rgb, paint["growth"]))
        if paint.get("growth_darker"):
            # The patches are darker than what they grow on; the growth at the base is not, and where it reaches they are not either.
            darker = math_node("MULTIPLY", math_node("MULTIPLY", settled, math_node("SUBTRACT", 1.0, base)), paint["growth_darker"])
            colour = times(colour, math_node("SUBTRACT", 1.0, darker))

    height = node("ShaderNodeMapRange", clamp=True)
    tree.links.new(z, height.inputs["Value"])
    height.inputs["From Min"].default_value, height.inputs["From Max"].default_value = z0, z1
    tint = mix("MIX", height.outputs["Result"], linear_rgb(paint["base_tint"]), linear_rgb(paint["top_tint"]))
    colour = mix("MULTIPLY", 1.0, colour, tint)

    if paint.get("side_shade"):
        # Upright faces are darker at mid height: whole on a side, none on a face past the second tilt.
        low, high = rules["side_shade_normal_z"]
        upright = ramp(math_node("ABSOLUTE", up, 0.0), high, low)
        from_middle = math_node("ABSOLUTE", math_node("SUBTRACT", height.outputs["Result"], 0.5), 0.0)
        band = math_node("SUBTRACT", 1.0, math_node("DIVIDE", from_middle, rules["side_shade_half_band"]), clamp=True)
        colour = times(colour, math_node("SUBTRACT", 1.0, math_node("MULTIPLY", math_node("MULTIPLY", upright, band), paint["side_shade"])))

    if paint.get("grain"):
        # Streaks along the limb: lighter ridges and darker furrows, and a few knots. Computed from
        # where the point lies round and along its limb, which the build script gives.
        where = node("ShaderNodeAttribute", attribute_type="GEOMETRY", attribute_name=GRAIN_ATTRIBUTE).outputs["Vector"]
        width = paint["grain_width_m"]

        def streaks(across, shift, detail, wander=0.0):
            mapping = node("ShaderNodeMapping")
            tree.links.new(where, mapping.inputs["Vector"])
            mapping.inputs["Scale"].default_value = (1 / (width * across), 1 / (width * across * GRAIN_STRETCH), 1.0)
            mapping.inputs["Location"].default_value = (shift, shift * 0.7, shift * 1.3)
            new = node("ShaderNodeTexNoise", noise_dimensions="3D")
            tree.links.new(mapping.outputs["Vector"], new.inputs["Vector"])
            new.inputs["Scale"].default_value, new.inputs["Detail"].default_value = 1.0, detail
            new.inputs["Distortion"].default_value = wander
            return new.outputs["Fac"]

        def signed(value):
            return math_node("SUBTRACT", math_node("MULTIPLY", ramp(value, 0.5 - NOISE_SPREAD, 0.5 + NOISE_SPREAD), 2.0), 1.0)

        fine = signed(streaks(GRAIN_FINE, 71.0, 1.0))
        plates = streaks(FURROW_WIDTH, 89.0, 1.0, FURROW_WANDER)
        from_line = math_node("ABSOLUTE", math_node("SUBTRACT", plates, 0.5), 0.0)
        furrow = ramp(from_line, FURROW_HALF, FURROW_HALF * 0.4, smooth=True)
        ridge = math_node("MULTIPLY", ramp(from_line, FURROW_HALF * 0.8, FURROW_HALF * 1.3, smooth=True), ramp(from_line, FURROW_HALF * 3.0, FURROW_HALF * 1.3, smooth=True))
        tone = math_node("ADD", math_node("ADD", math_node("MULTIPLY", fine, GRAIN_FINE_TONE), math_node("MULTIPLY", signed(plates), PLATE_TONE)), math_node("MULTIPLY", ridge, RIDGE_LIGHT))
        knots = node("ShaderNodeTexVoronoi", voronoi_dimensions="3D", feature="F1")
        spread = node("ShaderNodeMapping")
        tree.links.new(where, spread.inputs["Vector"])
        spread.inputs["Scale"].default_value = (1 / KNOT_SPACING_M, 1 / KNOT_SPACING_M, 1.0)
        tree.links.new(spread.outputs["Vector"], knots.inputs["Vector"])
        knots.inputs["Scale"].default_value = 1.0
        chosen = node("ShaderNodeSeparateColor")
        tree.links.new(knots.outputs["Color"], chosen.inputs[0])
        knot = math_node("MULTIPLY", ramp(knots.outputs["Distance"], KNOT_RADIUS_M / KNOT_SPACING_M, 0.3 * KNOT_RADIUS_M / KNOT_SPACING_M, smooth=True), math_node("LESS_THAN", chosen.outputs[0], KNOT_SHARE))
        dark = math_node("MAXIMUM", math_node("MULTIPLY", furrow, FURROW_DEPTH), math_node("MULTIPLY", knot, KNOT_DEPTH))
        factor = math_node("MULTIPLY", math_node("ADD", 1.0 + paint["grain"] * GRAIN_LIFT, math_node("MULTIPLY", tone, paint["grain"])), math_node("SUBTRACT", 1.0, math_node("MULTIPLY", dark, paint["grain"])))
        colour = times(colour, factor)

    if paint.get("blotch"):
        # Broad patches of lighter and darker tone, as much one as the other.
        pattern = ramp(noise(1 / paint["blotch_size_m"], 1.0, 37.0), 0.5 - BLOTCH_EDGE, 0.5 + BLOTCH_EDGE, smooth=True)
        colour = times(colour, math_node("ADD", 1.0 - paint["blotch"], math_node("MULTIPLY", pattern, 2 * paint["blotch"])))

    # Both masks come from Cycles' ambient occlusion node, aimed along the face's own normal
    # (the shading normal of a soft edge would darken every bevel strip).
    # Crevice: how much of the sky above the face other faces hide.
    # A spec for a shape with no inside corner asks none (tools/lint_spec.py asks it of overlapping pieces always).
    shade = None
    if "crevice_shadow" in paint:
        shade = math_node("DIVIDE", hidden(False, paint["crevice_width_m"]), rules["crevice_sky_hidden"], clamp=True)
    if apart and shade is not None:
        # A join: the sky another piece hides, over and above what the face's own piece hides. Two
        # pieces often meet in a groove too open to hide a fifth of the sky, and the join must
        # still be dark, since that is what hides it.
        by_others = math_node("SUBTRACT", hidden(False, paint["crevice_width_m"]), hidden(False, paint["crevice_width_m"], own_piece=True), clamp=True)
        shade = math_node("MAXIMUM", shade, math_node("DIVIDE", by_others, rules["join_sky_hidden"], clamp=True))
    if shade is not None:
        colour = mix("MULTIPLY", math_node("MULTIPLY", shade, paint["crevice_shadow"]), colour, (0.0, 0.0, 0.0))

    # Exposed edge: how much of the solid behind the face is missing, because another face cuts it off.
    edge = math_node("DIVIDE", hidden(True, paint["edge_width_m"]), FULL_EDGE_OCCLUSION, clamp=True)
    if apart and shade is not None:
        # An edge that runs into a join is not exposed there.
        edge = math_node("MULTIPLY", edge, math_node("SUBTRACT", 1.0, shade))
    if paint["hidden_underside"]:
        # The edge the asset stands on is not exposed: fade the light out toward the ground.
        edge = math_node("MULTIPLY", edge, math_node("DIVIDE", math_node("SUBTRACT", z, z0), 2 * paint["edge_width_m"], clamp=True))
    colour = mix("ADD", math_node("MULTIPLY", edge, paint["edge_light"]), colour, colour)
    return made, colour


def principled(material):
    """The Principled BSDF feeding a material's active output."""
    output = next(n for n in material.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    return output, output.inputs["Surface"].links[0].from_node


def srgb(linear):
    """Linear 0..1 to sRGB 0..1, as an 8-bit image stores it."""
    return linear * 12.92 if linear <= 0.0031308 else 1.055 * linear ** (1 / 2.4) - 0.055


def leaf_colours(objects, spec, conv, image):
    """Write the foliage palette into the top of `image` and put every leaf piece's UVs on one swatch."""
    want = spec["foliage"]
    size, swatch = spec["painted_shading"]["texture_px"], conv["foliage"]["swatch_px"]
    shades, tones = want["shades"], want["tones"]
    colours = foliage.palette(linear_rgb(spec["materials"][want["material"]]), linear_rgb(want["under_tint"]), linear_rgb(want["top_tint"]), shades, tones, want["variation"])
    per_row, rows, strip = foliage.swatch_layout(size, swatch, shades * tones + 1)

    texels = numpy.empty(size * size * 4, dtype=numpy.float32)
    image.pixels.foreach_get(texels)
    texels = texels.reshape(size, size, 4)  # row 0 is the bottom of the image
    flat = [colour for row in colours for colour in row]
    if "core_tint" in want:
        # One more swatch after the leaves': the cores' colour (ADR 9 as amended).
        flat.append(foliage.core_colour(linear_rgb(spec["materials"][want["material"]]), linear_rgb(want["core_tint"])))
    for index in range(per_row * rows):
        # Swatches past the last colour repeat it, so the strip has no unpainted texel.
        colour = flat[min(index, len(flat) - 1)]
        column, row = index % per_row, index // per_row
        top = size - row * swatch
        texels[top - swatch : top, column * swatch : (column + 1) * swatch, :3] = [srgb(c) for c in colour]
    # The empty band under the swatches takes the colours of the last row above it.
    under = size - rows * swatch
    texels[under - swatch : under, :, :3] = texels[under : under + 1, :, :3]
    texels[size - strip :, :, 3] = 1.0
    image.pixels.foreach_set(texels.ravel())
    image.update()

    shuffle = random.Random(0)
    for obj in objects:
        slot = next((i for i, s in enumerate(obj.material_slots) if s.material.name == want["material"]), None)
        if slot is None:
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.transform(obj.matrix_world)
        bm.faces.index_update()
        pieces = foliage.pieces_of(bm, slot)
        # A core joins the pieces lying on it into one pad (ADR 9 as amended).
        pads, _ = foliage.pads_with_cores(pieces, foliage.cores_of(bm, slot), want["pad_gap_m"])
        heights = foliage.heights_in_pads(pieces, pads)
        uvs = obj.data.uv_layers[UV_LAYER].data
        for piece, height in zip(pieces, heights):
            shade = min(shades - 1, int(height * shades))
            uv = foliage.swatch_uv(shade * tones + shuffle.randrange(tones), size, swatch)
            for face in piece:
                for corner in obj.data.polygons[face.index].loop_indices:
                    uvs[corner].uv = uv
        # Cores: every corner on the one swatch after the leaves'.
        for core in foliage.cores_of(bm, slot):
            for face in core:
                for corner in obj.data.polygons[face.index].loop_indices:
                    uvs[corner].uv = foliage.swatch_uv(shades * tones, size, swatch)
        bm.free()


def pieces_of_mesh(bm):
    """The indices of the faces of each connected piece of a mesh, in the order of their first faces."""
    bm.faces.ensure_lookup_table()
    seen, groups = set(), []
    for start in bm.faces:
        if start.index in seen:
            continue
        seen.add(start.index)
        group, front = set(), [start]
        while front:
            face = front.pop()
            group.add(face.index)
            for vert in face.verts:
                for other in vert.link_faces:
                    if other.index not in seen:
                        seen.add(other.index)
                        front.append(other)
        groups.append(group)
    return groups


def texels_of(image):
    """An image's texels as rows of (r, g, b, a), as stored (sRGB, 0 to 1); row 0 is the bottom."""
    width, height = image.size
    texels = numpy.empty(width * height * 4, dtype=numpy.float32)
    image.pixels.foreach_get(texels)
    return texels.reshape(height, width, 4)


def bakes_disagree(fine, coarse):
    """The share of a coarse bake's texels that a fine bake of the same thing, averaged over each, is more than CHECK_STEP from.

    Of the coarse texels with a painted texel on every side, that is: at the border of an island
    one bake has the bled margin and the other bare texture. With none such, of the painted ones;
    and a coarse bake with nothing painted agrees with nothing (1)."""
    rows, columns = coarse.shape[:2]
    block = fine.shape[0] // rows
    means = fine[: rows * block, : columns * block, :3].reshape(rows, block, columns, block, 3).mean(axis=(1, 3))
    apart = numpy.abs(means - coarse[:, :, :3]).max(axis=2) > CHECK_STEP
    painted = coarse[:, :, :3].max(axis=2) > 0
    padded = numpy.pad(painted, 1)
    inner = painted.copy()
    for down in range(3):
        for along in range(3):
            inner &= padded[down : down + rows, along : along + columns]
    asked = inner if inner.any() else painted
    return float(apart[asked].mean()) if asked.any() else 1.0


def cuda_devices():
    """Turn on Cycles' CUDA devices, and no other; the names of those there are.

    CUDA and not OptiX: OptiX is no faster here, compiles for four minutes on its first run, and its
    texels are further from the CPU's. --factory-startup leaves no device chosen, so this is every run's to do."""
    preferences = bpy.context.preferences.addons["cycles"].preferences
    try:
        preferences.compute_device_type = "CUDA"
    except TypeError:  # this Blender offers no CUDA at all
        return []
    preferences.refresh_devices()
    for device in preferences.devices:
        device.use = device.type == "CUDA"
    return [device.name for device in preferences.devices if device.use]


def run_bake(margin):
    """Bake what is selected into the active image node of each material."""
    result = bpy.ops.object.bake(type="EMIT", margin=margin, margin_type="EXTEND", use_clear=True)
    if result != {"FINISHED"}:
        raise RuntimeError(f"bake failed: {result}")


def gpu_bake(scene, image, targets, margin):
    """Bake on the graphics card, and say whether the texture can be trusted (None), or why not.

    The card is taken by one bake at a time (GPU_LOCK). The texture is then compared with a
    small bake of the same thing on the CPU (`bakes_disagree`), since the operator reports a
    bake that ran out of memory as finished."""
    os.environ.setdefault("CYCLES_CONCURRENT_STATES_FACTOR", GPU_STATES_FACTOR)
    started = time.monotonic()
    # Anyone may take the lock, whoever made the file.
    lock = os.open(GPU_LOCK, os.O_RDONLY | os.O_CREAT, 0o644)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        waited = time.monotonic() - started
        scene.cycles.device = "GPU"
        try:
            run_bake(margin)
        except RuntimeError as error:
            return f"it failed: {str(error).strip().splitlines()[-1]}"
        finally:
            scene.cycles.device = "CPU"
    finally:
        os.close(lock)
    took = time.monotonic() - started - waited

    size = image.size[0]
    coarse = bpy.data.images.new(f"{image.name}_check", size // CHECK_SHRINK, size // CHECK_SHRINK, alpha=False)
    coarse.colorspace_settings.name = image.colorspace_settings.name
    for target in targets:
        target.image = coarse
    try:
        run_bake(margin // CHECK_SHRINK)
        share = bakes_disagree(texels_of(image), texels_of(coarse))
    finally:
        for target in targets:
            target.image = image
        bpy.data.images.remove(coarse)
    print(f"bake: on the graphics card in {took:.1f} s after {waited:.1f} s waiting for it; {share:.4f} of a {size // CHECK_SHRINK} px bake on the CPU disagrees with it")
    if share > CHECK_SHARE:
        return f"{share:.3f} of it is not what a {size // CHECK_SHRINK} px bake on the CPU gives (a right bake: at most {CHECK_SHARE})"
    return None


def bake(scene, image, targets, margin):
    """Bake the painted colour into `image`: on the CPU, or with `KILN_BAKE=gpu` on the graphics card if that can be done and comes out right."""
    asked = os.environ.get(BAKE_ENV, "cpu") or "cpu"
    if asked not in ("cpu", "gpu"):
        raise RuntimeError(f"{BAKE_ENV} is 'cpu' or 'gpu', not '{asked}'")
    scene.cycles.device = "CPU"
    if asked == "gpu":
        devices = cuda_devices()
        if not devices:
            print(f"bake: {BAKE_ENV}=gpu, but Blender sees no CUDA device; baking on the CPU")
        else:
            wrong = gpu_bake(scene, image, targets, margin)
            if wrong is None:
                return
            print(f"WARNING: bake: the bake on the graphics card ({', '.join(devices)}) is thrown away, {wrong}; baking again on the CPU")
    run_bake(margin)


def apply(spec, conv):
    """Unwrap the spec's objects and replace their flat colours with one baked, painted texture."""
    paint = spec["painted_shading"]
    scene = bpy.context.scene
    objects = [bpy.data.objects[name] for name in spec["objects"]]
    size = paint["texture_px"]
    leaf = spec["foliage"]["material"] if "foliage" in spec else None
    strip = 0
    if leaf:
        strip = foliage.swatch_layout(size, conv["foliage"]["swatch_px"], spec["foliage"]["shades"] * spec["foliage"]["tones"] + 1)[2]
    unwrap(objects, spec, conv, skip=leaf, keep_clear=strip / size)

    image = bpy.data.images.new(f"{spec['asset']}_paint", size, size, alpha=False)
    image.colorspace_settings.name = "sRGB"

    # Cycles is a bundled add-on, and --factory-startup leaves it off.
    addon_utils.enable("cycles")
    scene.render.engine = "CYCLES"
    scene.cycles.samples = conv["painted_shading"]["bake_samples"]
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False

    # What is baked: the objects themselves, or, with foliage, copies without their leaf pieces,
    # so that leaves neither take texels nor shade the bark they hang over.
    baked = objects
    if leaf:
        baked = []
        for obj in objects:
            copy = obj.copy()
            copy.data = obj.data.copy()
            scene.collection.objects.link(copy)
            bm = bmesh.new()
            bm.from_mesh(copy.data)
            slot = next(i for i, s in enumerate(copy.material_slots) if s.material.name == leaf)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index == slot], context="FACES")
            bm.to_mesh(copy.data)
            bm.free()
            copy.data.materials.pop(index=slot)
            baked.append(copy)
        for obj in scene.objects:
            obj.select_set(obj in baked)
            obj.hide_render = obj in objects
        bpy.context.view_layer.objects.active = baked[0]

    pieces = []
    if "overlap" in spec and SPLIT_PIECES:
        # Overlapping pieces (ADR 13): each closed piece is baked as an object of its own, with the
        # UVs it already has, into the one texture.
        for obj in baked:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            groups = pieces_of_mesh(bm)
            bm.free()
            for keep in groups:
                copy = obj.copy()
                copy.data = obj.data.copy()
                scene.collection.objects.link(copy)
                bm = bmesh.new()
                bm.from_mesh(copy.data)
                bm.faces.ensure_lookup_table()
                bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in keep], context="FACES")
                bm.to_mesh(copy.data)
                bm.free()
                pieces.append(copy)
        whole = baked
        for obj in scene.objects:
            obj.select_set(obj in pieces)
            obj.hide_render = obj in whole or obj.hide_render
        bpy.context.view_layer.objects.active = pieces[0]

    materials = [m for m in dict.fromkeys(slot.material for obj in objects for slot in obj.material_slots) if m.name != leaf]
    temporary = []
    for material in materials:
        tree = material.node_tree
        output, bsdf = principled(material)
        made, colour = paint_nodes(tree, tuple(bsdf.inputs["Base Color"].default_value)[:3], spec, conv, grows=material.name not in no_growth_on(spec))
        emission = tree.nodes.new("ShaderNodeEmission")
        tree.links.new(colour, emission.inputs["Color"])
        tree.links.new(emission.outputs[0], output.inputs["Surface"])
        target = tree.nodes.new("ShaderNodeTexImage")
        target.name = "paint"
        target.image = image
        tree.nodes.active = target
        temporary.append((tree, made + [emission], output, bsdf, target))

    bake(scene, image, [target for *_, target in temporary], conv["painted_shading"]["island_gap_px"] // 2)

    if pieces:
        for copy in pieces:
            mesh = copy.data
            bpy.data.objects.remove(copy)
            bpy.data.meshes.remove(mesh)
        for obj in whole:
            obj.hide_render = obj in objects and bool(leaf)
            obj.select_set(True)
        bpy.context.view_layer.objects.active = whole[0]

    for tree, made, output, bsdf, target in temporary:
        for node in made:
            tree.nodes.remove(node)
        tree.links.new(bsdf.outputs[0], output.inputs["Surface"])
        # The flat colour stays on the socket, unlinked, as the record of what was painted over.
        tree.links.new(target.outputs["Color"], bsdf.inputs["Base Color"])
    if leaf:
        for copy in baked:
            mesh = copy.data
            bpy.data.objects.remove(copy)
            bpy.data.meshes.remove(mesh)
        for obj in objects:
            obj.hide_render = False
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        leaf_colours(objects, spec, conv, image)
        # The leaf material reads the same texture; its flat colour stays on the socket, as the bark's does.
        material = bpy.data.materials[leaf]
        _, bsdf = principled(material)
        target = material.node_tree.nodes.new("ShaderNodeTexImage")
        target.name = "paint"
        target.image = image
        material.node_tree.links.new(target.outputs["Color"], bsdf.inputs["Base Color"])
    image.pack()
    return image
