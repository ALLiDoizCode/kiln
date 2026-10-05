"""Export a built asset to GLB in the Bevy glTF profile, and write its manifest.

Every exporter option that matters is set explicitly; Blender's defaults for
apply-modifiers, tangents and extras are all off.

Usage: tools/bl tools/export.py <asset>
"""

import json
import sys
from pathlib import Path

import bmesh
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import Asset, conventions, gltf_bounds, linear_rgb, script_args, share_textures

asset = Asset(script_args()[0])
spec = asset.spec()
bpy.ops.wm.open_mainfile(filepath=str(asset.blend))

objects = [bpy.data.objects[name] for name in spec["objects"]]
for obj in bpy.data.objects:
    obj.select_set(obj in objects)

asset.glb.parent.mkdir(parents=True, exist_ok=True)
result = bpy.ops.export_scene.gltf(
    filepath=str(asset.glb),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=True,
    export_normals=True,
    export_tangents="TANGENT" in spec["attributes"],
    export_texcoords="TEXCOORD_0" in spec["attributes"],
    export_extras=True,
    export_materials="EXPORT",
    # AUTO keeps a PNG as PNG, the one format the Bevy crates decode (conventions.toml).
    export_image_format="AUTO",
    # Bevy multiplies COLOR_0 into the base colour, so it is written only when the spec lists it.
    export_vertex_color="ACTIVE" if "COLOR_0" in spec["attributes"] else "NONE",
    export_all_vertex_colors=False,
    export_active_vertex_color_when_no_material=False,
    export_cameras=False,
    export_lights=False,
    export_animations=False,
    export_skins=False,
    export_morph=False,
    export_draco_mesh_compression_enable=False,
)
# Operators report failure through their return value, not an exception.
if result != {"FINISHED"}:
    raise RuntimeError(f"glTF export failed: {result}")



share_textures(asset.glb)

depsgraph = bpy.context.evaluated_depsgraph_get()
triangles = 0
for obj in objects:
    bm = bmesh.new()
    bm.from_object(obj, depsgraph)
    triangles += sum(len(f.verts) - 2 for f in bm.faces)
    bm.free()

# What Bevy must see. Bounds come from the spec, not from the mesh, so the
# load test compares the engine's view against the brief.
manifest = {
    "asset": asset.name,
    "nodes": spec["objects"],
    "mesh_count": len({obj.data.name for obj in objects}),
    "materials": {name: [round(c, 6) for c in linear_rgb(colour)] for name, colour in spec["materials"].items()},
    "watertight": spec["watertight"],
    "triangles": triangles,
    "bounds": gltf_bounds(spec["bounds_m"]),
    "bounds_tolerance": spec["bounds_tolerance_m"],
    "attributes": spec["attributes"],
    "soft_edges": spec.get("soft_edges", False),
}
if "open_materials" in spec:
    # Materials whose faces are separate open pieces; the rest is the closed surface.
    manifest["open_materials"] = spec["open_materials"]
if "overlap" in spec:
    # Several closed pieces that pass into each other (ADR 13): the load test asks facing outward of each.
    manifest["overlap"] = True
if "foliage" in spec:
    # What the leaf pieces' colours must do, from the spec, and how they are found and measured, from the conventions.
    want, rules = spec["foliage"], conventions()
    manifest["foliage"] = {
        **{key: want[key] for key in ("material", "pad_gap_m", "min_pad_pieces", "shades", "tones", "variation")},
        "under_tint": [round(c, 6) for c in linear_rgb(want["under_tint"])],
        "top_tint": [round(c, 6) for c in linear_rgb(want["top_tint"])],
        **{key: rules["foliage"][key] for key in ("swatch_px", "max_palette_error", "min_neighbours_differ")},
        "min_effect_share": rules["painted_shading"]["min_effect_share"],
    }
    if "core_tint" in want:
        # The cores under the leaf pieces (ADR 9 as amended): their colour, and how many a pad may have.
        # Foliage of blades has none, and the load test then asks for none.
        manifest["foliage"].update({"core_tint": [round(c, 6) for c in linear_rgb(want["core_tint"])], "lobes": want["lobes"]})
if "painted_shading" in spec:
    # What the texture must do, from the spec, and how strictly, from the conventions.
    want, rules = spec["painted_shading"], conventions()["painted_shading"]
    manifest["painted"] = {
        "texture_px": want["texture_px"],
        "base_tint": [round(c, 6) for c in linear_rgb(want["base_tint"])],
        "top_tint": [round(c, 6) for c in linear_rgb(want["top_tint"])],
        # The crevice shadow is asked only of a shape with inside corners; absent, the load test holds the shape to having none.
        **{key: want[key] for key in ("edge_light", "edge_width_m", "crevice_shadow", "crevice_width_m", "hidden_underside") if key in want},
        **{key: rules[key] for key in ("min_texels_per_m", "min_uv_coverage", "max_uv_overlap", "feature_deg", "crevice_sky_hidden", "join_sky_hidden", "colour_tolerance", "min_effect_share")},
        "texel_range": rules["texel_range_srgb"],
        # Variation the spec asks for (absent: none), and the rules tools/paint.py and the load test share.
        **{key: want[key] for key in ("growth_height_m", "growth_up", "growth_edges", "growth_darker", "growth_patch_m", "blotch", "blotch_size_m", "side_shade") if key in want},
        **({"growth": [round(c, 6) for c in linear_rgb(want["growth"])]} if "growth" in want else {}),
        **{key: rules[key] for key in ("side_shade_normal_z", "side_shade_half_band", "growth_up_normal_z", "growth_cover", "growth_patch_edges", "blotch_spread", "max_blotch_grain", "max_level_gap")},
    }
    if "grain" in want or "close_texels_per_m" in want:
        # Grain and close-range texels the spec asks for (ADR 12), and how the load test measures the grain.
        manifest["painted"].update({key: want[key] for key in ("grain", "grain_width_m", "close_height_m", "close_texels_per_m") if key in want})
        manifest["painted"].update({key: rules[key] for key in ("min_grain_step", "min_grain_along", "min_grain_patches", "grain_patch_m")})
        if want.get("grain"):
            # The two tones of grained bark, as the painter makes them: painted.colour is asked of each (tools/paint.py).
            import paint

            manifest["painted"].update(paint.grain_tones(want))
if "skeleton" in spec:
    # Where a player stands against the trunk: its middle at eye height, in glTF space (x, z). A trunk
    # leans, so this is not the origin; crates/asset_view's --stand measures its distance from here.
    import skeleton

    obj = objects[0]
    bm = bmesh.new()
    bm.from_object(obj, depsgraph)
    bm.transform(obj.matrix_world)
    slot = [s.material.name for s in obj.material_slots].index(spec["skeleton"]["material"])
    at = skeleton.stand_at(bm, slot, spec["bounds_m"]["min"][2], conventions()["metrics"]["eye_height_m"])
    bm.free()
    if at is not None:
        manifest["stand_at"] = [round(at[0], 4), round(-at[1], 4)]
with open(asset.manifest, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print(f"exported {asset.glb} ({triangles} triangles)")
