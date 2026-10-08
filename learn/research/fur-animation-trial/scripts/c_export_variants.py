"""Prototype C: write the same model with and without its shape keys, to see what they cost.

    tools/bl scripts/c_export_variants.py <model with shape keys.glb> <out folder> <stem>

Writes <stem>_plain.glb (no morph targets), _pos.glb (positions only), _pos_nrm.glb (positions
and normals, what the other scripts write), _pos_nrm_tan.glb (and tangents) and _anim.glb
(positions and normals, plus a 2-second clip that takes the first shape key from 0 to 1 and back).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import furlib as F

src, out, stem = F.args()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src, merge_vertices=True)
obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
os.makedirs(out, exist_ok=True)
for name, kw in [("plain", dict(morph=False)), ("pos", dict(normals=False)), ("pos_nrm", dict()),
                 ("pos_nrm_tan", dict(tangents=True))]:
    path = os.path.join(out, f"{stem}_{name}.glb")
    F.export_glb(path, **kw)
    print("WROTE", path, os.path.getsize(path))

# A clip on the shape key's value: Blender writes it as a glTF animation of the node's weights.
keys = obj.data.shape_keys
first = keys.key_blocks[1]
scene = bpy.context.scene
scene.render.fps = 24
for frame, value in [(1, 0.0), (25, 1.0), (49, 0.0)]:
    first.value = value
    first.keyframe_insert("value", frame=frame)
scene.frame_start, scene.frame_end = 1, 49
path = os.path.join(out, f"{stem}_anim.glb")
F.export_glb(path, animations=True)
print("WROTE", path, os.path.getsize(path))
