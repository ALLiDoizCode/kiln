"""Prototype E: is the skeleton from Tripo's Auto Rig usable, with Tripo's weights or Blender's?

    tools/bl scripts/e_tripo_rig.py <tripo.fbx> <model with shape keys.glb> <out folder> <facts.json>

Imports Tripo's FBX export (the only export in which the skeleton keeps its shape). Then:
 1. With Tripo's own weights: bends one leg chain, then the tail, and counts the vertices that
    move. Writes tripo_weights.glb with a two-key clip "pose_test" (rest, bent, rest).
 2. Throws Tripo's weights away, binds the model that carries prototype A's shape keys to the
    same skeleton with Blender's automatic weights, and does the same. Writes
    tripo_skeleton_auto_weights.glb: a skin, four morph targets and the clip in one file.
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
import furlib as F

fbx, morph_glb, out_dir, facts_path = F.args()
os.makedirs(out_dir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx)
arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.context.scene.objects if o.type == "MESH")
facts = {"fbx": os.path.basename(fbx), "as_imported": {
    "armature_scale": [round(x, 4) for x in arm.scale], "armature_rotation_deg": [round(math.degrees(x), 1) for x in arm.rotation_euler],
    "mesh_scale": [round(x, 4) for x in mesh.scale], "mesh_rotation_deg": [round(math.degrees(x), 1) for x in mesh.rotation_euler]}}
bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start, scene.frame_end = 1, 25


def chain(name):
    """A bone and everything below it."""
    b = arm.data.bones[name]
    return [b.name] + [c.name for c in b.children_recursive]


def world(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    co = np.array([tuple(o.matrix_world @ v.co) for v in me.vertices])
    ev.to_mesh_clear()
    return co


def reset():
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()


def bend(names, degrees):
    for n in names:
        arm.pose.bones[n].rotation_euler = (math.radians(degrees), 0, 0)
    bpy.context.view_layer.update()


bones = arm.data.bones
box = lambda co: {"min": [round(float(x), 3) for x in co.min(0)], "max": [round(float(x), 3) for x in co.max(0)]}
rest = world(mesh)
heads = np.array([tuple(arm.matrix_world @ b.head_local) for b in bones])
facts["skeleton"] = {"bones": len(bones), "deform_bones": sum(1 for b in bones if b.use_deform),
                     "box_of_bone_heads": box(heads), "box_of_mesh": box(rest),
                     "children": {b.name: [c.name for c in b.children] for b in bones if b.children}}
# The chains, read off the hierarchy: the tail is the chain that ends highest; legs end lowest.
ends = [b for b in bones if not b.children]
up = max(range(3), key=lambda i: rest.max(0)[i] - 0 if i == 2 else -1)  # z is up after import
tips = sorted(ends, key=lambda b: (arm.matrix_world @ b.tail_local)[2])
legs_ends = [b.name for b in tips[:4]]
tail_end = tips[-1].name


def top_of_chain(end, stop_children=2):
    b = bones[end]
    path = [b.name]
    while b.parent and len(b.parent.children) == 1:
        b = b.parent; path.append(b.name)
    return list(reversed(path))


leg_chains = {e: top_of_chain(e) for e in legs_ends}
tail_chain = top_of_chain(tail_end)
facts["chains"] = {"legs": leg_chains, "tail": tail_chain,
                   "leg_feet_at": {e: [round(x, 3) for x in (arm.matrix_world @ bones[e].tail_local)] for e in legs_ends}}


def test(label, target):
    groups = {vg.name: 0 for vg in target.vertex_groups}
    none = 0
    for v in target.data.vertices:
        g = [ge for ge in v.groups if ge.weight > 1e-4]
        none += not g
        for ge in g:
            groups[target.vertex_groups[ge.group].name] += 1
    reset(); base = world(target)
    res = {"vertices": len(target.data.vertices), "vertex_groups": len(groups), "groups_with_vertices": sum(1 for c in groups.values() if c),
           "vertices_in_no_group": int(none), "vertices_per_group": {k: v for k, v in groups.items() if v},
           "leg_bones_with_vertices": sum(1 for ch in leg_chains.values() for n in ch if groups.get(n)),
           "leg_bones": sum(len(ch) for ch in leg_chains.values())}
    for name, ch in list(leg_chains.items())[:1]:
        reset(); bend(ch[:1], 30)
        res["bend_one_leg_30_degrees"] = {"bone": ch[0], "vertices_moved_over_1mm": int((np.linalg.norm(world(target) - base, axis=1) > 0.001).sum())}
    reset(); bend(tail_chain[:3], 15)
    moved = np.linalg.norm(world(target) - base, axis=1)
    res["bend_tail_3_bones_15_degrees"] = {"bones": tail_chain[:3], "vertices_moved_over_1mm": int((moved > 0.001).sum()), "largest_move_m": round(float(moved.max()), 3)}
    reset()
    facts[label] = res


def clip(name):
    reset()
    if arm.animation_data:
        arm.animation_data_clear()
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    moving = [c[0] for c in leg_chains.values()] + tail_chain[:3]
    for frame, on in ((1, 0), (13, 1), (25, 0)):
        for i, n in enumerate(moving):
            sign = 1 if i % 2 == 0 else -1
            deg = 15 if n in tail_chain else 30 * sign
            arm.pose.bones[n].rotation_euler = (math.radians(deg * on), 0, 0)
            arm.pose.bones[n].keyframe_insert("rotation_euler", frame=frame)
    arm.animation_data.action.name = name


test("tripo_weights", mesh)
clip("pose_test")
p = os.path.join(out_dir, "tripo_weights.glb")
F.export_glb(p, animations=True, skins=True)
facts["tripo_weights"]["glb_bytes"] = os.path.getsize(p)

# 2. The same skeleton, Blender's weights, on the model with the shape keys.
bpy.data.objects.remove(mesh, do_unlink=True)
before = set(bpy.context.scene.objects)
bpy.ops.import_scene.gltf(filepath=morph_glb, merge_vertices=True)
new = next(o for o in set(bpy.context.scene.objects) - before if o.type == "MESH")
bpy.ops.object.select_all(action="DESELECT")
new.select_set(True); bpy.context.view_layer.objects.active = new
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
co_new = world(new)
facts["glb_mesh_against_fbx_mesh"] = {"same_vertex_count": len(co_new) == len(rest), "box_of_glb_mesh": box(co_new),
                                      "largest_distance_by_index_m": round(float(np.linalg.norm(co_new - rest, axis=1).max()), 4) if len(co_new) == len(rest) else None}
reset()
arm.select_set(True); bpy.context.view_layer.objects.active = arm
facts["auto_weights_result"] = list(bpy.ops.object.parent_set(type="ARMATURE_AUTO"))
test("blender_auto_weights_on_tripo_skeleton", new)
facts["blender_auto_weights_on_tripo_skeleton"]["shape_keys"] = [k.name for k in new.data.shape_keys.key_blocks] if new.data.shape_keys else []
clip("pose_test")
p = os.path.join(out_dir, "tripo_skeleton_auto_weights.glb")
F.export_glb(p, animations=True, skins=True)
facts["blender_auto_weights_on_tripo_skeleton"]["glb_bytes"] = os.path.getsize(p)
F.write_json(facts_path, facts)
