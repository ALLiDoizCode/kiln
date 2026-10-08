"""Prototype E: a skeleton placed by script, Blender's automatic weights, and a walk-like clip.

    tools/bl scripts/e_rig_by_script.py <model.glb> <out.glb> <facts.json>

The model may already carry shape keys (the output of a_morph_fused.py): they are kept, so the
file written has a skin, morph targets and two animations at once.

Where the bones go is worked out from the mesh alone: the four feet are the four clusters of
low vertices (left/right, front/back), the snout is the vertex farthest forward, the tail tip
is the highest vertex. 13 bones: root, body, head, two for the tail, and for each leg an upper
bone and a lower bone. Weights: Blender's "With Automatic Weights" (bone heat).
The clip is not an animator's walk: each leg swings 25 degrees, diagonal pairs together, and
the tail sways. It is there to see the skin bend, not to be kept.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
import furlib as F

src, out, facts_path = F.args()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src, merge_vertices=True)
obj = next(o for o in bpy.context.scene.objects if o.type == "MESH")
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
co = F.coords(obj.data)
lo, hi = co.min(0), co.max(0)
height = hi[2] - lo[2]

# Landmarks. Blender axes: +z up, -y the creature's front.
low = co[co[:, 2] < lo[2] + 0.06 * height]
feet = {}
for side, sx in (("L", 1), ("R", -1)):
    for end, sy in (("front", -1), ("back", 1)):
        pts = low[(np.sign(low[:, 0]) == sx) & (np.sign(low[:, 1] - np.median(low[:, 1])) == sy)]
        feet[f"{end}_{side}"] = pts.mean(0)
snout = co[np.argmin(co[:, 1])]
tail_tip = co[np.argmax(co[:, 2])]
mid_z = lo[2] + 0.48 * height
hip_z = lo[2] + 0.36 * height
knee_z = lo[2] + 0.18 * height
back_y = max(f[1] for f in feet.values())
front_y = min(f[1] for f in feet.values())
tail_root = Vector((0, back_y + 0.02, lo[2] + 0.62 * height))

arm_data = bpy.data.armatures.new("rig")
arm = bpy.data.objects.new("rig", arm_data)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")


def bone(name, head, tail, parent=None, connect=False):
    b = arm_data.edit_bones.new(name)
    b.head, b.tail = Vector(head), Vector(tail)
    if parent:
        b.parent = arm_data.edit_bones[parent]
        b.use_connect = connect
    return b


bone("root", (0, 0, 0), (0, 0, 0.15))
bone("body", (0, back_y, mid_z), (0, front_y, mid_z), "root")
bone("head", (0, front_y, mid_z), (0, snout[1], snout[2]), "body", True)
tail_mid = (tail_root + Vector(tail_tip)) / 2
bone("tail_1", tail_root, tail_mid, "body")
bone("tail_2", tail_mid, tail_tip, "tail_1", True)
for name, f in feet.items():
    bone(f"upper_{name}", (f[0], f[1], hip_z), (f[0], f[1], knee_z), "body")
    bone(f"lower_{name}", (f[0], f[1], knee_z), (f[0], f[1], lo[2]), f"upper_{name}", True)
arm_data.edit_bones["root"].use_deform = False
bpy.ops.object.mode_set(mode="OBJECT")

# Automatic weights.
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
result = bpy.ops.object.parent_set(type="ARMATURE_AUTO")
counts = {vg.name: 0 for vg in obj.vertex_groups}
per_vertex = {}
for v in obj.data.vertices:
    n = 0
    for ge in v.groups:
        if ge.weight > 1e-4:
            counts[obj.vertex_groups[ge.group].name] += 1; n += 1
    per_vertex[n] = per_vertex.get(n, 0) + 1

# Two clips: a leg swing, and one bent pose held (to look at the skin under a strong bend).
for pb in arm.pose.bones:
    pb.rotation_mode = "XYZ"
scene = bpy.context.scene
scene.render.fps = 24


def key(frame, angles):
    for name, (rx, rz) in angles.items():
        pb = arm.pose.bones[name]
        pb.rotation_euler = (math.radians(rx), 0, math.radians(rz))
        pb.keyframe_insert("rotation_euler", frame=frame)


swing = 25
a_pose = {"upper_front_L": (swing, 0), "upper_back_R": (swing, 0), "upper_front_R": (-swing, 0), "upper_back_L": (-swing, 0),
          "lower_front_L": (-15, 0), "lower_back_R": (-15, 0), "lower_front_R": (15, 0), "lower_back_L": (15, 0),
          "tail_1": (0, 12), "tail_2": (0, 12), "head": (0, -6)}
b_pose = {k: (-rx, -rz) for k, (rx, rz) in a_pose.items()}
key(1, a_pose); key(13, b_pose); key(25, a_pose)
walk = arm.animation_data.action
walk.name = "walk_like"
scene.frame_start, scene.frame_end = 1, 25

facts = {"source": os.path.basename(src), "blender": bpy.app.version_string, "parent_set_result": list(result),
         "bones": [{"name": b.name, "parent": b.parent.name if b.parent else None, "deform": b.use_deform,
                    "head": [round(x, 3) for x in b.head_local], "tail": [round(x, 3) for x in b.tail_local]} for b in arm_data.bones],
         "landmarks": {"feet": {k: [round(float(x), 3) for x in v] for k, v in feet.items()},
                       "snout": [round(float(x), 3) for x in snout], "tail_tip": [round(float(x), 3) for x in tail_tip]},
         "vertices": len(obj.data.vertices), "vertices_moved_by_bone": counts, "bones_per_vertex": per_vertex,
         "vertices_with_no_bone": per_vertex.get(0, 0),
         "shape_keys_kept": [k.name for k in obj.data.shape_keys.key_blocks] if obj.data.shape_keys else [],
         "actions": [a.name for a in bpy.data.actions]}
F.write_json(facts_path, facts)
os.makedirs(os.path.dirname(out), exist_ok=True)
F.export_glb(out, animations=True, skins=True)
print("WROTE", out, os.path.getsize(out))
