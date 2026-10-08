"""Prototype E: the box of a skinned mesh as stored and as its armature poses it at rest, in glTF axes.
    tools/bl scripts/e_posed_box.py <rigged.glb>
"""
import bpy, sys
p = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=p)
dg = bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
    if o.type == "MESH" and o.parent:
        for label, ob in (("rest (no armature)", o), ("as posed by the armature", o.evaluated_get(dg))):
            me = ob.data if label.startswith("rest") else ob.to_mesh()
            pts = [o.matrix_world @ v.co for v in me.vertices]
            g = [(v.x, v.z, -v.y) for v in pts]
            print("BOX", label, [round(min(q[i] for q in g), 3) for i in range(3)], [round(max(q[i] for q in g), 3) for i in range(3)])
        print("mesh matrix_world", [list(map(lambda x: round(x, 3), r)) for r in o.matrix_world])
for o in bpy.context.scene.objects:
    if o.type == "ARMATURE":
        print("armature matrix_world", [list(map(lambda x: round(x, 3), r)) for r in o.matrix_world])
