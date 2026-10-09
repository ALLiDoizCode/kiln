"""What kiln's Blender scripts share: reading and writing a .glb and a stage's facts. Imported
by the scripts beside it, inside the pinned Blender (tools/bl); it is not a kiln module.

A script that reads a model reads the output of scale_to_size or of a stage after it: every
mesh is in the scene's own space, in metres at the asset's size, on a node with no transform.
So a length in these scripts is a length on the finished asset.
"""
import json
import sys

import bmesh
import bpy


def arguments():
    return sys.argv[sys.argv.index("--") + 1:]


def finished(result, what):
    """An operator that cancels returns {'CANCELLED'} without raising; make that an error."""
    if "FINISHED" not in result:
        raise RuntimeError(f"{what} did not finish: {result}")


def read(path):
    """Empty the scene, import the .glb, and return its mesh objects sorted by name."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    finished(bpy.ops.import_scene.gltf(filepath=path, merge_vertices=True,
                                       import_shading="NORMALS"), "glTF import")
    return sorted((o for o in bpy.context.scene.objects if o.type == "MESH"),
                  key=lambda o: o.name)


def activate(obj, selected=None):
    for other in bpy.context.scene.objects:
        other.select_set(False)
    for other in (selected or [obj]):
        other.select_set(True)
    bpy.context.view_layer.objects.active = obj


def write(path, tangents=False):
    """Export the whole scene with the settings scale_to_size.py uses.

    `tangents` stores, for every corner, the directions a normal map is read along, as
    Blender works them out. A model whose normal map kiln baked needs them: the map was drawn
    for Blender's, and Bevy's own, worked out when a file has none, differ enough to put
    pale flecks along a crate's edges. Blender gives a tangent of no length to the corners
    of a triangle too thin to have one; kiln.glb.mend_tangents puts that right afterwards."""
    finished(bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=False, export_yup=True,
        export_apply=False, export_animations=False, export_skins=False, export_morph=False,
        export_cameras=False, export_lights=False, export_extras=False,
        export_image_format="AUTO",   # each texture keeps the format it came in
        export_materials="EXPORT", export_texcoords=True, export_normals=True,
        export_tangents=tangents, export_draco_mesh_compression_enable=False), "glTF export")


def weld(mesh, distance):
    """Join the vertices of a mesh that are closer than `distance` metres; returns how many
    went. UVs and stored normals belong to the corners of faces and stay as they were.

    Every script that edits the surface does this on reading. A .glb stores a point again
    wherever its normal or UV changes, and the importer joins only the copies whose normals
    agree: a model with hard edges arrives as sheets that touch but are not joined, and
    reducing it tears them apart (10,194 open edges on a crate, in
    learn/research/blender-stages-trial.md section 8)."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
    joined = before - len(bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    return joined


def triangles(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def bounds(objects):
    """The lowest and highest corner of the box round every vertex of the objects."""
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for obj in objects:
        world = obj.matrix_world
        for vertex in obj.data.vertices:
            point = world @ vertex.co
            for axis in range(3):
                low[axis] = min(low[axis], point[axis])
                high[axis] = max(high[axis], point[axis])
    return low, high


def save_facts(path, facts):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(facts, f)
