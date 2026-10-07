"""Scale a model to a size. Runs inside the pinned Blender, not under the system Python:

    tools/bl kiln/blender_scripts/scale_to_size.py <in.glb> <out.glb> <size in metres> <result.json>

The model is scaled by one factor on all three axes, about the origin of the file, so that
the largest dimension of its bounding box, as the scene places it, equals the size.

What happens to transforms and to the tree of nodes: every mesh is moved into the scene's
own space. The whole transform of its node (position, rotation, scale, and those of its
parents) and the scale factor are worked into the vertex positions; the node is then left
at the origin with no rotation and a scale of 1, with no parent. After this stage a stored
vertex position is a position in the scene, in metres. A mesh placed more than once becomes
one mesh per placement. Nodes that draw nothing (empties, cameras, lights) are dropped.

The input is only read. `result.json` gets the factor used and Blender's version.
"""
import json
import sys

import bpy
from mathutils import Matrix


def main(source, target, size, result_path):
    size = float(size)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # merge_vertices is on. glTF stores a point again wherever its normal or UV changes;
    # with the option off Blender keeps those copies as separate sheets of surface, and the
    # exporter then wrote 154 vertices for the boulder specimen's 115. With it on the
    # surface comes in joined and goes out with the vertex count it came in with.
    bpy.ops.import_scene.gltf(filepath=source, merge_vertices=True, import_shading="NORMALS")

    scene = bpy.context.scene
    meshes = sorted((o for o in scene.objects if o.type == "MESH"), key=lambda o: o.name)
    placed = {o.name: o.matrix_world.copy() for o in meshes}

    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for obj in meshes:
        world = placed[obj.name]
        for vertex in obj.data.vertices:
            point = world @ vertex.co
            for axis in range(3):
                low[axis] = min(low[axis], point[axis])
                high[axis] = max(high[axis], point[axis])
    largest = max((h - l for l, h in zip(low, high)), default=0.0)
    if not largest > 0.0:
        raise SystemExit("scale_to_size: the model has no extent, so it cannot be scaled to a size")
    factor = size / largest

    for obj in meshes:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        move = Matrix.Scale(factor, 4) @ placed[obj.name]
        obj.parent = None
        obj.data.transform(move)
        if move.determinant() < 0.0:
            obj.data.flip_normals()  # a mirrored node turns every triangle inside out
        obj.matrix_world = Matrix.Identity(4)
    for obj in [o for o in scene.objects if o.type != "MESH"]:
        bpy.data.objects.remove(obj)

    bpy.ops.export_scene.gltf(
        filepath=target,
        export_format="GLB",
        use_selection=False,
        export_yup=True,
        export_apply=False,
        export_animations=False,
        export_skins=False,
        export_morph=False,
        export_cameras=False,
        export_lights=False,
        export_extras=False,
        export_image_format="AUTO",   # each texture keeps the format it came in
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
        export_draco_mesh_compression_enable=False,
    )
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({"factor": factor, "largest_dimension_before": largest,
                   "blender": bpy.app.version_string}, f)


if __name__ == "__main__":
    main(*sys.argv[sys.argv.index("--") + 1:])
