# What skeleton and animation a rigged model file holds, as Blender reads it.
#   tools/bl scripts/inspect_rig.py <model.glb|model.fbx> ...
import bpy, sys
for p in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if p.lower().endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=p)
    else:
        bpy.ops.import_scene.gltf(filepath=p)
    print("RESULT", p.split("/")[-1])
    for o in bpy.data.objects:
        if o.type == "ARMATURE":
            print("RESULT   armature", o.name, "bones", len(o.data.bones), [b.name for b in o.data.bones][:30])
        if o.type == "MESH":
            print("RESULT   mesh", o.name, "verts", len(o.data.vertices), "vertex groups", len(o.vertex_groups),
                  "shape keys", len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0,
                  "modifiers", [m.type for m in o.modifiers])
    print("RESULT   actions", [(a.name, tuple(round(x, 1) for x in a.frame_range)) for a in bpy.data.actions],
          "fps", bpy.context.scene.render.fps)
