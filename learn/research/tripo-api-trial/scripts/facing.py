# Where the tall part of a model sits along the glTF z axis, to tell which way it faces.
#   tools/bl scripts/facing.py <model.glb> ...
# Prints, in glTF axes (y up), the mean z of the vertices in the top 15% of the height and the
# mean z of all vertices. For a creature with a raised tail, the tail end is the side the top sits on.
import bpy, sys
for p in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=p)
    pts = []
    for o in bpy.data.objects:
        if o.type == "MESH":
            m = o.matrix_world
            pts += [m @ v.co for v in o.data.vertices]
    g = [(v.x, v.z, -v.y) for v in pts]  # Blender z-up to glTF y-up
    ys = [q[1] for q in g]; lo, hi = min(ys), max(ys)
    top = [q for q in g if q[1] > lo + 0.85 * (hi - lo)]
    zs = [q[2] for q in g]
    print(f"RESULT {p.split('/')[-1]}: z from {min(zs):.3f} to {max(zs):.3f}; mean z of all {sum(zs)/len(zs):+.3f}; "
          f"mean z of top 15% {sum(q[2] for q in top)/len(top):+.3f}; mean x of top 15% {sum(q[0] for q in top)/len(top):+.3f}")
