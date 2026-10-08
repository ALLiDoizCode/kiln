"""Prototype E: what a rigged file holds, as Blender imports it.
    tools/bl scripts/e_inspect_rig.py <rigged.glb|.fbx> <facts.json>
Lists the bones (name, parent, where the head and tail are, in glTF axes: y up, z forward),
the vertex groups and how many vertices each one moves, and the actions (clips).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import furlib as F

src, out = F.args()
bpy.ops.wm.read_factory_settings(use_empty=True)
if src.lower().endswith(".fbx"):
    bpy.ops.import_scene.fbx(filepath=src)
else:
    bpy.ops.import_scene.gltf(filepath=src, merge_vertices=True)
g = lambda v: [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]
facts = {"file": os.path.basename(src), "objects": [(o.name, o.type) for o in bpy.context.scene.objects],
         "actions": [(a.name, list(a.frame_range)) for a in bpy.data.actions], "armatures": [], "meshes": []}
for o in bpy.context.scene.objects:
    if o.type == "ARMATURE":
        facts["armatures"].append({"name": o.name, "bones": [
            {"name": b.name, "parent": b.parent.name if b.parent else None, "deform": b.use_deform,
             "head": g(o.matrix_world @ b.head_local), "tail": g(o.matrix_world @ b.tail_local)} for b in o.data.bones]})
    if o.type == "MESH":
        counts = {vg.name: 0 for vg in o.vertex_groups}
        per_vertex = {}
        for v in o.data.vertices:
            n = 0
            for ge in v.groups:
                if ge.weight > 0:
                    counts[o.vertex_groups[ge.group].name] += 1; n += 1
            per_vertex[n] = per_vertex.get(n, 0) + 1
        facts["meshes"].append({"name": o.name, "vertices": len(o.data.vertices), "parent": o.parent.name if o.parent else None,
                                "modifiers": [m.type for m in o.modifiers], "vertices_moved_by_group": counts,
                                "groups_per_vertex": per_vertex, "shape_keys": [k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []})
F.write_json(out, facts)
