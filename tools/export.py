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
from pipeline import Asset, gltf_bounds, linear_rgb, script_args

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
    export_image_format="AUTO",
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
with open(asset.manifest, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
print(f"exported {asset.glb} ({triangles} triangles)")
