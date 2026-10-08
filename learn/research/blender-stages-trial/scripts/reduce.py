"""Stage 3 of the trial: reduce a mesh to a triangle count.

    tools/bl reduce.py <in.glb> <out.glb> <facts.json> [name=value ...]

  method=collapse     the Decimate modifier's Collapse, to `target` triangles
         planar       Decimate's Planar (dissolve nearly flat neighbours), then Collapse if the
                      result is still over `target`
         unsubdiv     Decimate's Un-Subdivide, `unsubdiv_iterations` times, then Collapse if over
         voxel        voxel remesh at `voxel_size` metres (drops UVs and normals), then Collapse
         quadriflow   QuadriFlow remesh to target/2 quads (drops UVs and normals)
  target=20000        triangles wanted; the result is never left above it when exact=true
  steps=1             Collapse in this many passes of equal ratio instead of one
  protect_seams=0     0 = off. Otherwise the modifier's vertex-group factor (0..1000), with a
                      vertex group that marks the vertices on a UV seam or an open edge, so that
                      Collapse prefers to remove other edges. Collapse has no seam option of
                      its own; this is the only handle the modifier gives.
  planar_angle=5      degrees: Planar dissolves neighbours that meet at less than this
  planar_delimit=UV   what Planar will not dissolve across: any of NORMAL,MATERIAL,SEAM,SHARP,UV
                      joined by "+", or "none"
  merge_vertices=true join the file's doubled vertices on import (off shows what that breaks)
  weld=0              metres: also weld by distance before reducing (0 = off)
  normals=keep|clear  keep the stored normals through the reduction, or drop them afterwards and
                      work normals out again, with edges over `sharp_angle` degrees made sharp
  exact=true          if Collapse lands above `target`, run it again on the result

The facts give the triangle count reached after every pass, defects before and after (on a
copy welded at a millionth of a metre), and the seconds each step took.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import numpy as np  # noqa: E402  (bundled with Blender)
import stagelib as lib  # noqa: E402

DEFAULTS = {"method": "collapse", "target": 20000, "steps": 1, "protect_seams": 0.0,
            "planar_angle": 5.0, "planar_delimit": "UV", "unsubdiv_iterations": 2,
            "voxel_size": 0.004, "merge_vertices": True, "weld": 0.0, "normals": "keep",
            "sharp_angle": 30.0, "exact": True, "count_before": True, "quadriflow_seed": 0}


def apply_modifier(obj, modifier):
    lib.activate(obj)
    lib.finished(bpy.ops.object.modifier_apply(modifier=modifier.name), "apply " + modifier.name)


def seam_group(obj):
    """A vertex group holding the vertices on UV seams and open edges. Returns (group, count)."""
    mesh = obj.data
    lib.activate(obj)
    lib.finished(bpy.ops.object.mode_set(mode="EDIT"), "edit mode")
    lib.finished(bpy.ops.mesh.select_all(action="SELECT"), "select all")
    lib.finished(bpy.ops.uv.seams_from_islands(mark_seams=True, mark_sharp=False), "seams from islands")
    lib.finished(bpy.ops.object.mode_set(mode="OBJECT"), "object mode")
    seam = np.zeros(len(mesh.edges), dtype=bool)
    mesh.edges.foreach_get("use_seam", seam)
    ends = np.zeros(len(mesh.edges) * 2, dtype=np.int32)
    mesh.edges.foreach_get("vertices", ends)
    on_seam = np.unique(ends.reshape(-1, 2)[seam])
    group = obj.vertex_groups.new(name="seams")
    group.add(on_seam.tolist(), 1.0, "REPLACE")
    return group, int(len(on_seam)), int(seam.sum())


def collapse(obj, target, settings, passes, group=None):
    """Collapse to `target` triangles in `passes` passes. Returns the count after each."""
    reached = []
    for left in range(passes, 0, -1):
        now = lib.triangles(obj.data)
        if now <= target:
            break
        ratio = (target / now) ** (1.0 / left)
        modifier = obj.modifiers.new("reduce", "DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = ratio
        modifier.use_collapse_triangulate = True
        if group is not None:
            # A higher weight makes an edge cheaper to remove, so the group is inverted:
            # seam vertices count as 0 and everything else as 1.
            modifier.vertex_group = group.name
            modifier.invert_vertex_group = True
            modifier.vertex_group_factor = settings["protect_seams"]
        apply_modifier(obj, modifier)
        reached.append({"ratio": ratio, "triangles": lib.triangles(obj.data)})
        print(f"COLLAPSE ratio {ratio:.6f} -> {reached[-1]['triangles']}", flush=True)
    return reached


def main():
    source, target_path, facts_path, settings = lib.arguments(DEFAULTS)
    target = settings["target"]
    clock = lib.Clock()
    obj = lib.one_object(source, settings["merge_vertices"])
    mesh = obj.data
    clock.lap("import")
    facts = {"stage": "reduce", "source": source, "settings": settings, "before_object": lib.describe(obj)}
    if settings["count_before"]:
        facts["before"] = lib.defects(mesh)
        clock.lap("count_before")
    passes = []
    if settings["weld"] > 0:
        modifier = obj.modifiers.new("weld", "WELD")
        modifier.merge_threshold = settings["weld"]
        before = len(mesh.vertices)
        apply_modifier(obj, modifier)
        mesh = obj.data
        facts["weld_joined"] = before - len(mesh.vertices)
        clock.lap("weld")

    method = settings["method"]
    if method == "collapse":
        group = None
        if settings["protect_seams"] > 0:
            group, vertices, edges = seam_group(obj)
            facts["seam_vertices_protected"] = vertices
            facts["seam_edges_marked"] = edges
            clock.lap("mark_seams")
        passes += collapse(obj, target, settings, settings["steps"], group)
        clock.lap("collapse")
    elif method == "planar":
        modifier = obj.modifiers.new("planar", "DECIMATE")
        modifier.decimate_type = "DISSOLVE"
        modifier.angle_limit = math.radians(settings["planar_angle"])
        if settings["planar_delimit"].lower() != "none":
            modifier.delimit = set(settings["planar_delimit"].split("+"))
        apply_modifier(obj, modifier)
        facts["faces_after_planar"] = len(obj.data.polygons)
        facts["largest_face_sides_after_planar"] = max((len(p.vertices) for p in obj.data.polygons), default=0)
        clock.lap("planar")
        modifier = obj.modifiers.new("triangulate", "TRIANGULATE")
        apply_modifier(obj, modifier)
        facts["triangles_after_planar"] = lib.triangles(obj.data)
        clock.lap("triangulate")
        passes += collapse(obj, target, settings, settings["steps"])
        clock.lap("collapse")
    elif method == "unsubdiv":
        modifier = obj.modifiers.new("unsubdiv", "DECIMATE")
        modifier.decimate_type = "UNSUBDIV"
        modifier.iterations = settings["unsubdiv_iterations"]
        apply_modifier(obj, modifier)
        facts["triangles_after_unsubdiv"] = lib.triangles(obj.data)
        clock.lap("unsubdiv")
        passes += collapse(obj, target, settings, settings["steps"])
        clock.lap("collapse")
    elif method == "voxel":
        obj.data.remesh_voxel_size = settings["voxel_size"]
        obj.data.remesh_voxel_adaptivity = 0.0
        lib.activate(obj)
        lib.finished(bpy.ops.object.voxel_remesh(), "voxel remesh")
        facts["triangles_after_voxel"] = lib.triangles(obj.data)
        facts["faces_after_voxel"] = len(obj.data.polygons)
        clock.lap("voxel")
        passes += collapse(obj, target, settings, settings["steps"])
        clock.lap("collapse")
    elif method == "quadriflow":
        lib.activate(obj)
        lib.finished(bpy.ops.object.quadriflow_remesh(
            mode="FACES", target_faces=target // 2, seed=settings["quadriflow_seed"],
            use_mesh_symmetry=False, use_preserve_sharp=False, use_preserve_boundary=False,
            preserve_attributes=False, smooth_normals=False), "QuadriFlow")
        facts["faces_after_quadriflow"] = len(obj.data.polygons)
        clock.lap("quadriflow")
    else:
        raise SystemExit(f"unknown method {method!r}")

    extra = 0
    while settings["exact"] and method != "quadriflow" and lib.triangles(obj.data) > target and extra < 5:
        passes += collapse(obj, target, settings, 1)
        extra += 1
    if extra:
        clock.lap("collapse_again")
    mesh = obj.data
    facts["passes"] = passes
    facts["extra_passes"] = extra
    facts["triangles_reached"] = lib.triangles(mesh)
    facts["custom_normals_after_reduce"] = bool(mesh.has_custom_normals)
    if settings["normals"] == "clear":
        if mesh.has_custom_normals:
            lib.activate(obj)
            lib.finished(bpy.ops.mesh.customdata_custom_splitnormals_clear(), "clear custom normals")
        mesh.shade_smooth()
        if settings["sharp_angle"] > 0:
            mesh.set_sharp_from_angle(angle=math.radians(settings["sharp_angle"]))
        clock.lap("clear_normals")
    facts["after_object"] = lib.describe(obj)
    facts["after"] = lib.defects(mesh)
    low, high = lib.bounds(mesh)
    facts["bounds_after"] = [low, high]
    clock.lap("count_after")
    lib.write(target_path)
    clock.lap("export")
    facts["seconds"] = clock.steps
    lib.save_facts(facts_path, facts)


main()
