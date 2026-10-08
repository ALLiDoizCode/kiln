"""Reduce a model to a triangle count with Blender's Decimate modifier (Collapse), the plainest
"generate dense, then reduce" route, to set beside a model the generator made at that count.

    tools/bl reduce_in_blender.py <in.glb> <out.glb> <triangles>

Every mesh gets the same ratio = target / triangles now. No repair, no new UVs, no baking: the
existing UVs are carried by the modifier and the textures are left as they are. Collapse works
to a ratio, so the result lands near the target, not exactly on it; the count reached is printed
on a line starting REDUCED. This is a comparison aid, not a kiln stage.
"""
import json
import sys

import bpy

source, target, wanted = sys.argv[sys.argv.index("--") + 1:][:3]
wanted = int(wanted)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source, merge_vertices=True)
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]


def triangles():
    total = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        total += len(obj.data.loop_triangles)
    return total


before = triangles()
ratio = min(1.0, wanted / max(1, before))
for obj in meshes:
    modifier = obj.modifiers.new("reduce", "DECIMATE")
    modifier.decimate_type = "COLLAPSE"
    modifier.ratio = ratio
    modifier.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
after = triangles()
bpy.ops.export_scene.gltf(filepath=target, export_format="GLB")
print("REDUCED " + json.dumps({"source": source, "triangles_before": before, "ratio": ratio,
                               "triangles_after": after, "wanted": wanted, "blender": bpy.app.version_string}))
