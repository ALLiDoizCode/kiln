"""What the trial's Blender scripts share: reading and writing a .glb, counting defects, and
writing the facts of a run. Imported by the stage scripts in this folder, inside the pinned
Blender (tools/bl); it is not a kiln module.

Every stage script has the same shape, so that it could become a kiln stage:

    tools/bl <stage>.py <in.glb> <out.glb> <facts.json> [name=value ...]

It only reads <in.glb>, writes <out.glb>, and writes <facts.json> with the settings it used,
the seconds each step took and what it counted.
"""
import json
import sys
import time

import bmesh
import bpy

WELD = 1e-6          # metres: the distance scripts/mesh_defects.py welds at before counting


def arguments(defaults):
    """(source, target, facts path, settings) from the command line. Settings are name=value;
    a name not in `defaults` is an error, and a value takes the type of its default."""
    args = sys.argv[sys.argv.index("--") + 1:]
    source, target, facts_path = args[:3]
    settings = dict(defaults)
    for item in args[3:]:
        name, _, value = item.partition("=")
        if name not in defaults:
            raise SystemExit(f"unknown setting {name!r}; known: {', '.join(sorted(defaults))}")
        kind = type(defaults[name])
        if kind is bool:
            settings[name] = value.lower() in ("1", "true", "yes", "on")
        elif defaults[name] is None:
            settings[name] = value
        else:
            settings[name] = kind(value)
    return source, target, facts_path, settings


class Clock:
    """Seconds per named step, in the order the steps ran."""
    def __init__(self):
        self.steps, self._last = {}, time.perf_counter()

    def lap(self, name):
        now = time.perf_counter()
        self.steps[name] = round(self.steps.get(name, 0.0) + now - self._last, 3)
        self._last = now
        print(f"STEP {name}: {self.steps[name]:.2f} s", flush=True)


def finished(result, what):
    """An operator that cancels returns {'CANCELLED'} without raising; make that an error."""
    if "FINISHED" not in result:
        raise RuntimeError(f"{what} did not finish: {result}")


def read(path, merge_vertices=True, shading="NORMALS"):
    """Empty the scene, import the .glb, and return its mesh objects sorted by name."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    finished(bpy.ops.import_scene.gltf(filepath=path, merge_vertices=merge_vertices,
                                       import_shading=shading), "glTF import")
    return sorted((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: o.name)


def one_object(path, merge_vertices=True, shading="NORMALS"):
    """Import and give back a single mesh object; several meshes are joined into one."""
    meshes = read(path, merge_vertices, shading)
    if not meshes:
        raise SystemExit("the model has no mesh")
    activate(meshes[0], meshes)
    if len(meshes) > 1:
        finished(bpy.ops.object.join(), "join")
    return bpy.context.view_layer.objects.active


def activate(obj, selected=None):
    for other in bpy.context.scene.objects:
        other.select_set(False)
    for other in (selected or [obj]):
        other.select_set(True)
    bpy.context.view_layer.objects.active = obj


def write(path, selection=False, image_format="AUTO", tangents=False, normals=True):
    """Export with the settings kiln's scale_to_size stage uses."""
    finished(bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=selection, export_yup=True,
        export_apply=False, export_animations=False, export_skins=False, export_morph=False,
        export_cameras=False, export_lights=False, export_extras=False,
        export_image_format=image_format, export_materials="EXPORT", export_texcoords=True,
        export_normals=normals, export_tangents=tangents,
        export_draco_mesh_compression_enable=False), "glTF export")


def triangles(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def count(bm):
    """Defect counts of a bmesh, the same ones scripts/mesh_defects.py reports."""
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    out = {
        "vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces),
        "triangles": sum(len(f.verts) - 2 for f in bm.faces),
        "boundary_edges": len(boundary),
        "non_manifold_edges": sum(1 for e in bm.edges if len(e.link_faces) > 2),
        "wire_edges": sum(1 for e in bm.edges if not e.link_faces),
        "loose_vertices": sum(1 for v in bm.verts if not v.link_edges),
        "flipped_edges": sum(1 for e in bm.edges if len(e.link_faces) == 2 and not e.is_contiguous),
        "degenerate_faces": sum(1 for f in bm.faces if f.calc_area() < 1e-12),
        "zero_length_edges": sum(1 for e in bm.edges if e.calc_length() < 1e-9),
    }
    seen, loops, by_vert = set(), 0, {}
    for e in boundary:
        for v in e.verts:
            by_vert.setdefault(v.index, []).append(e)
    for e in boundary:
        if e.index in seen:
            continue
        loops += 1
        stack = [e]
        while stack:
            cur = stack.pop()
            if cur.index in seen:
                continue
            seen.add(cur.index)
            for v in cur.verts:
                stack.extend(x for x in by_vert[v.index] if x.index not in seen)
    out["boundary_loops"] = loops
    piece_of, pieces = {}, []
    for f in bm.faces:
        if f.index in piece_of:
            continue
        tris, stack = 0, [f]
        piece_of[f.index] = len(pieces)
        while stack:
            cur = stack.pop()
            tris += len(cur.verts) - 2
            for v in cur.verts:
                for other in v.link_faces:
                    if other.index not in piece_of:
                        piece_of[other.index] = len(pieces)
                        stack.append(other)
        pieces.append(tris)
    pieces.sort(reverse=True)
    out["pieces"] = len(pieces)
    out["largest_pieces"] = pieces[:8]
    return out


def defects(mesh, weld=WELD):
    """Defect counts of a mesh after welding a copy of it at `weld` metres. The mesh itself
    is not changed."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if weld:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld)
    bm.verts.index_update(); bm.edges.index_update(); bm.faces.index_update()
    out = count(bm)
    bm.free()
    return out


def bounds(mesh, matrix=None):
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for vertex in mesh.vertices:
        point = matrix @ vertex.co if matrix is not None else vertex.co
        for axis in range(3):
            low[axis] = min(low[axis], point[axis])
            high[axis] = max(high[axis], point[axis])
    return low, high


def describe(obj):
    """What a mesh object holds besides its shape."""
    mesh = obj.data
    return {
        "vertices": len(mesh.vertices), "faces": len(mesh.polygons), "triangles": triangles(mesh),
        "uv_layers": [u.name for u in mesh.uv_layers],
        "has_custom_normals": bool(mesh.has_custom_normals),
        "normals_domain": mesh.normals_domain,
        "smooth_faces": sum(1 for p in mesh.polygons if p.use_smooth),
        "sharp_edges": sum(1 for e in mesh.edges if e.use_edge_sharp),
        "materials": [m.name if m else None for m in mesh.materials],
        "attributes": sorted(a.name for a in mesh.attributes if not a.is_internal),
    }


def save_facts(path, facts):
    facts.setdefault("blender", bpy.app.version_string)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=1)
        f.write("\n")
    print("FACTS " + json.dumps(facts))
