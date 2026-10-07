"""Count the same things as kiln.measure, but with Blender, as an independent second opinion.

Usage: tools/bl tests/cross_check/blender_figures.py <asset.glb> [more.glb ...]
Prints two lines of JSON per file, each starting with FIGURES. Not part of the unittest
run: it needs the pinned Blender.

The first line is the file as Blender's importer brings it in with "Merge Vertices" on.
That option does not join vertices whose normals differ, so some edges stay doubled and
show up as open edges. The second line is after Blender's "Merge by Distance", which joins
every vertex at the same position: that is the welded surface kiln.measure works on, and
the line whose edges, seams and open edges should match it.

Blender's importer turns glTF's Y-up axes into its own Z-up ones, so the bounding box is
turned back before printing: glTF (x, y, z) is Blender (x, z, -y).
"""
import json
import sys

import bmesh
import bpy
from bpy_extras import mesh_utils
from mathutils import Vector


def figures(path, weld):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path, merge_vertices=True)
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    out = {"file": path, "welded": weld, "triangles": 0, "uv_islands": 0, "edges": 0, "seam_edges": 0,
           "open_edges": 0, "has_uvs": False}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        mesh = obj.data
        mesh.calc_loop_triangles()
        out["triangles"] += len(mesh.loop_triangles)
        for vertex in mesh.vertices:
            world = obj.matrix_world @ vertex.co
            for axis, value in enumerate((world.x, world.z, -world.y)):
                low[axis] = min(low[axis], value)
                high[axis] = max(high[axis], value)
        if not mesh.uv_layers:
            continue
        out["has_uvs"] = True
        # Let Blender mark a seam wherever its own island finder sees a border, then count.
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        if weld:
            bpy.ops.mesh.remove_doubles(threshold=1e-6)
        bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False)
        bm = bmesh.from_edit_mesh(mesh)
        out["edges"] += len(bm.edges)
        out["seam_edges"] += sum(1 for e in bm.edges if e.seam and len(e.link_faces) > 1)
        out["open_edges"] += sum(1 for e in bm.edges if len(e.link_faces) == 1)
        bpy.ops.object.mode_set(mode="OBJECT")
        out["uv_islands"] += len(mesh_utils.mesh_linked_uv_islands(mesh))
    out["min"] = [round(v, 6) for v in low]
    out["max"] = [round(v, 6) for v in high]
    return out


for asset in sys.argv[sys.argv.index("--") + 1:]:
    for weld in (False, True):
        print("FIGURES " + json.dumps(figures(asset, weld)))
