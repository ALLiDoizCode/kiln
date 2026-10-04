"""Painted shading (ADR 9, ADR 10): colour computed from an asset's shape and baked into one texture.

`apply(spec)` is called by tools/build.py after an asset's own build script,
when the spec has a `painted_shading` block. The build script stays as it is:
it gives each material one flat colour, and this step unwraps the mesh, bakes
the painted colour from that flat colour and the spec, and puts the texture on
the material in place of the flat colour.

The colour at a point, in linear RGB, is

    mix(material colour, growth colour at the material's own lightness, growth mask)
      * mix(base_tint, top_tint, height within the spec's bounds)
      * (1 - side_shade * how upright the face is * how near mid height the point is)
      * (1 + blotch * a broad patch pattern between -1 and 1)
      * (1 - crevice_shadow * how enclosed the point is)
      * (1 + edge_light * how close the point is to an exposed edge)

The growth mask is the largest of three: below `growth_height_m`, with a ragged
top; patches covering about `growth_up` of the faces that are near level; and
patches along about `growth_edges` of the exposed edges in the upper part.
Growth changes hue and never value, and the blotch pattern averages nothing, so
crates/asset_smoke can still measure the exported texture against these lines.
Nothing here is random: the patterns are Blender's noise texture at fixed
places in space and Cycles runs on the CPU with a fixed seed, so a rebuild
gives the same texels.

Run under Blender, through tools/build.py.
"""

import math

import addon_utils
import bmesh
import bpy
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
GROWTH_EDGE_M = 0.2  # how far in from an upper edge its growth reaches
GROWTH_EDGES_FROM = (0.5, 0.75)  # share of the height over which edge growth comes in
BLOTCH_EDGE = 0.1  # how much of the noise's range a blotch's border takes: soft, but a patch and not a haze
# The crevice shadow is full where a fifth of the sky is hidden, as in the corner of a
# ledge whose wall leans back; the edge light is full where a sixteenth of the solid behind
# the face is missing, as beside the bevel strip of a right-angled corner.
FULL_SHADE_OCCLUSION = 0.2
FULL_EDGE_OCCLUSION = 0.06
# Faces within this of straight down, at the floor of the bounds, are the hidden underside.
UNDERSIDE_COS = 0.999
UNDERSIDE_UV_SCALE = 0.05  # texel density of an underside nobody sees, beside the rest


def luminance(rgb):
    return sum(c * w for c, w in zip(rgb, LUMA))


def growth_colour(material_rgb, growth_hex):
    """The growth colour scaled to the material's lightness: growth changes hue, the tints change value."""
    growth = linear_rgb(growth_hex)
    scale = luminance(material_rgb) / luminance(growth)
    return tuple(min(1.0, c * scale) for c in growth)


def unwrap(objects, spec, conv):
    """Give every object one shared, non-overlapping UV layout filling the 0..1 square."""
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


def paint_nodes(tree, colour_rgb, spec, conv):
    """Build the painted colour as nodes in `tree`. Returns (the nodes made, the colour output)."""
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
        threshold = 0.5 + NOISE_SPREAD * (1 - 2 * cover)
        return ramp(noise(GROWTH_PATCH_SCALE, 2.0, shift), threshold - PATCH_EDGE / 2, threshold + PATCH_EDGE / 2)

    def hidden(inside, distance):
        occlusion = node("ShaderNodeAmbientOcclusion", samples=16, only_local=True, inside=inside)
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
    if "growth" in paint:
        reach = paint["growth_height_m"]
        # Where the growth stops at this spot: reach, raised or lowered by the noise.
        wander = math_node("MULTIPLY", math_node("SUBTRACT", noise(GROWTH_NOISE_SCALE, 3.0, 0.0), 0.5), 2 * GROWTH_RAGGED * reach)
        top = math_node("ADD", wander, z0 + reach)
        mask = math_node("DIVIDE", math_node("SUBTRACT", top, z), GROWTH_FADE * reach, clamp=True)
        if paint.get("growth_up"):
            # On faces near level, where it would settle.
            mask = math_node("MAXIMUM", mask, math_node("MULTIPLY", ramp(up, *rules["growth_up_normal_z"]), patches(paint["growth_up"], 11.0)))
        if paint.get("growth_edges"):
            # Along exposed edges, in the upper part of the asset.
            rim = math_node("DIVIDE", hidden(True, GROWTH_EDGE_M), FULL_EDGE_OCCLUSION, clamp=True)
            upper = ramp(z, *(z0 + share * (z1 - z0) for share in GROWTH_EDGES_FROM))
            mask = math_node("MAXIMUM", mask, math_node("MULTIPLY", math_node("MULTIPLY", rim, upper), patches(paint["growth_edges"], 23.0)))
        colour = mix("MIX", mask, colour, growth_colour(colour_rgb, paint["growth"]))

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

    if paint.get("blotch"):
        # Broad patches of lighter and darker tone, as much one as the other.
        pattern = ramp(noise(1 / paint["blotch_size_m"], 1.0, 37.0), 0.5 - BLOTCH_EDGE, 0.5 + BLOTCH_EDGE, smooth=True)
        colour = times(colour, math_node("ADD", 1.0 - paint["blotch"], math_node("MULTIPLY", pattern, 2 * paint["blotch"])))

    # Both masks come from Cycles' ambient occlusion node, aimed along the face's own normal
    # (the shading normal of a soft edge would darken every bevel strip).
    # Crevice: how much of the sky above the face other faces hide.
    shade = math_node("DIVIDE", hidden(False, paint["crevice_width_m"]), FULL_SHADE_OCCLUSION, clamp=True)
    colour = mix("MULTIPLY", math_node("MULTIPLY", shade, paint["crevice_shadow"]), colour, (0.0, 0.0, 0.0))

    # Exposed edge: how much of the solid behind the face is missing, because another face cuts it off.
    edge = math_node("DIVIDE", hidden(True, paint["edge_width_m"]), FULL_EDGE_OCCLUSION, clamp=True)
    if paint["hidden_underside"]:
        # The edge the asset stands on is not exposed: fade the light out toward the ground.
        edge = math_node("MULTIPLY", edge, math_node("DIVIDE", math_node("SUBTRACT", z, z0), 2 * paint["edge_width_m"], clamp=True))
    colour = mix("ADD", math_node("MULTIPLY", edge, paint["edge_light"]), colour, colour)
    return made, colour


def principled(material):
    """The Principled BSDF feeding a material's active output."""
    output = next(n for n in material.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output)
    return output, output.inputs["Surface"].links[0].from_node


def apply(spec, conv):
    """Unwrap the spec's objects and replace their flat colours with one baked, painted texture."""
    paint = spec["painted_shading"]
    scene = bpy.context.scene
    objects = [bpy.data.objects[name] for name in spec["objects"]]
    unwrap(objects, spec, conv)

    size = paint["texture_px"]
    image = bpy.data.images.new(f"{spec['asset']}_paint", size, size, alpha=False)
    image.colorspace_settings.name = "sRGB"

    # Cycles is a bundled add-on, and --factory-startup leaves it off.
    addon_utils.enable("cycles")
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = conv["painted_shading"]["bake_samples"]
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False

    materials = list(dict.fromkeys(slot.material for obj in objects for slot in obj.material_slots))
    temporary = []
    for material in materials:
        tree = material.node_tree
        output, bsdf = principled(material)
        made, colour = paint_nodes(tree, tuple(bsdf.inputs["Base Color"].default_value)[:3], spec, conv)
        emission = tree.nodes.new("ShaderNodeEmission")
        tree.links.new(colour, emission.inputs["Color"])
        tree.links.new(emission.outputs[0], output.inputs["Surface"])
        target = tree.nodes.new("ShaderNodeTexImage")
        target.name = "paint"
        target.image = image
        tree.nodes.active = target
        temporary.append((tree, made + [emission], output, bsdf, target))

    result = bpy.ops.object.bake(type="EMIT", margin=conv["painted_shading"]["island_gap_px"] // 2, margin_type="EXTEND", use_clear=True)
    if result != {"FINISHED"}:
        raise RuntimeError(f"bake failed: {result}")

    for tree, made, output, bsdf, target in temporary:
        for node in made:
            tree.nodes.remove(node)
        tree.links.new(bsdf.outputs[0], output.inputs["Surface"])
        # The flat colour stays on the socket, unlinked, as the record of what was painted over.
        tree.links.new(target.outputs["Color"], bsdf.inputs["Base Color"])
    image.pack()
    return image
