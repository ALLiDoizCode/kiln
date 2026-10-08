"""Count the defects of a model file that kiln.measure does not count. Read-only.

    tools/bl mesh_defects.py <model.glb|.fbx> [result.json]

Runs inside the pinned Blender. Prints one line starting with DEFECTS followed by JSON, and
writes the same JSON to result.json when given. Nothing is changed or exported.

Two passes are reported:
  "as_imported"  the mesh as the importer brings it in (glTF: "Merge Vertices" on, which joins
                 points only where position, normal and UV all agree).
  "welded"       after joining every pair of vertices closer than 1e-6 of a metre. This is the
                 surface a person means by "the mesh"; holes and non-manifold edges are read here.

What each number means:
  boundary_edges      edges with a face on one side only: the rim of a hole or of an open sheet
  boundary_loops      closed rings of boundary edges: roughly "how many holes or open rims"
  non_manifold_edges  edges shared by three or more faces
  wire_edges          edges with no face
  loose_vertices      vertices on no edge
  flipped_edges       edges whose two faces wind opposite ways (one of them is inside out)
  degenerate_faces    faces whose area is below 1e-12 square metres
  zero_length_edges   edges shorter than 1e-9 metres
  pieces              groups of faces not connected to each other ("loose parts"); the triangle
                      count of each, largest first (at most 20 listed)
  small_pieces        pieces holding under 1% of the triangles: candidates for stray bits
  face_sides          how many faces have 3, 4 and more sides
Axes: Blender is Z-up. The glTF importer turns glTF (x, y, z) into Blender (x, -z, y); the
bounding box is printed both as Blender holds it and turned back to glTF axes. FBX files are
imported with the importer's defaults and only the Blender box is meaningful.
"""
import json
import sys

import bmesh
import bpy


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    low = path.lower()
    if low.endswith((".glb", ".gltf")):
        bpy.ops.import_scene.gltf(filepath=path, merge_vertices=True)
        return "gltf"
    if low.endswith(".fbx"):
        bpy.ops.import_scene.fbx(filepath=path)
        return "fbx"
    raise SystemExit("mesh_defects: only .glb, .gltf and .fbx are read")


def count(bm):
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    boundary = [e for e in bm.edges if len(e.link_faces) == 1]
    out = {
        "vertices": len(bm.verts), "edges": len(bm.edges), "faces": len(bm.faces),
        "triangles": sum(len(f.verts) - 2 for f in bm.faces),
        "face_sides": {"3": sum(1 for f in bm.faces if len(f.verts) == 3),
                       "4": sum(1 for f in bm.faces if len(f.verts) == 4),
                       "5_or_more": sum(1 for f in bm.faces if len(f.verts) > 4)},
        "boundary_edges": len(boundary),
        "non_manifold_edges": sum(1 for e in bm.edges if len(e.link_faces) > 2),
        "wire_edges": sum(1 for e in bm.edges if not e.link_faces),
        "loose_vertices": sum(1 for v in bm.verts if not v.link_edges),
        "flipped_edges": sum(1 for e in bm.edges if len(e.link_faces) == 2 and not e.is_contiguous),
        "degenerate_faces": sum(1 for f in bm.faces if f.calc_area() < 1e-12),
        "zero_length_edges": sum(1 for e in bm.edges if e.calc_length() < 1e-9),
    }
    # rings of boundary edges
    seen, loops = set(), 0
    by_vert = {}
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
    # connected pieces, by faces joined through shared vertices
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
    total = max(1, out["triangles"])
    out["pieces"] = len(pieces)
    out["piece_triangles_largest_first"] = pieces[:20]
    out["small_pieces"] = sum(1 for p in pieces if p < 0.01 * total)
    out["small_piece_triangles"] = sum(p for p in pieces if p < 0.01 * total)
    return out


def add(total, part):
    for key, value in part.items():
        if isinstance(value, dict):
            add(total.setdefault(key, {}), value)
        elif isinstance(value, list):
            total[key] = sorted(total.get(key, []) + value, reverse=True)[:20]
        else:
            total[key] = total.get(key, 0) + value


def main(path, result_path=None):
    kind = load(path)
    report = {"file": path, "importer": kind, "blender": bpy.app.version_string, "objects": [],
              "as_imported": {}, "welded": {}}
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
        entry = {"name": obj.name, "type": obj.type, "parent": obj.parent.name if obj.parent else None,
                 "location": [round(v, 6) for v in obj.matrix_world.translation],
                 "rotation_euler_deg": [round(v * 57.29577951, 4) for v in obj.matrix_world.to_euler()],
                 "scale": [round(v, 6) for v in obj.matrix_world.to_scale()]}
        if obj.type == "MESH":
            mesh = obj.data
            entry["mesh"] = mesh.name
            entry["materials"] = [m.name if m else None for m in mesh.materials]
            entry["uv_layers"] = [u.name for u in mesh.uv_layers]
            entry["colour_attributes"] = [c.name for c in mesh.color_attributes]
            entry["has_custom_normals"] = bool(getattr(mesh, "has_custom_normals", False))
            entry["smooth_faces"] = sum(1 for p in mesh.polygons if p.use_smooth)
            entry["flat_faces"] = sum(1 for p in mesh.polygons if not p.use_smooth)
            for vertex in mesh.vertices:
                world = obj.matrix_world @ vertex.co
                for axis in range(3):
                    low[axis] = min(low[axis], world[axis]); high[axis] = max(high[axis], world[axis])
            bm = bmesh.new(); bm.from_mesh(mesh)
            entry["as_imported"] = count(bm)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
            entry["welded"] = count(bm)
            bm.free()
            add(report["as_imported"], entry["as_imported"]); add(report["welded"], entry["welded"])
        report["objects"].append(entry)
    if low[0] != float("inf"):
        report["bounding_box_blender_zup"] = {"min": [round(v, 6) for v in low], "max": [round(v, 6) for v in high],
                                              "dimensions": [round(h - l, 6) for l, h in zip(low, high)]}
        if kind == "gltf":  # Blender (x, y, z) is glTF (x, z, -y)
            report["bounding_box_gltf_yup"] = {
                "min": [round(low[0], 6), round(low[2], 6), round(-high[1], 6)],
                "max": [round(high[0], 6), round(high[2], 6), round(-low[1], 6)],
                "dimensions": [round(high[0] - low[0], 6), round(high[2] - low[2], 6), round(high[1] - low[1], 6)]}
        centre = [(l + h) / 2 for l, h in zip(low, high)]
        report["bounding_box_centre_blender"] = [round(v, 6) for v in centre]
        report["lowest_point_blender_z"] = round(low[2], 6)
    report["materials"] = [m.name for m in bpy.data.materials]
    report["images"] = [{"name": i.name, "size": list(i.size), "channels": i.channels,
                         "file_format": i.file_format, "colorspace": i.colorspace_settings.name}
                        for i in bpy.data.images if i.size[0]]
    text = json.dumps(report, indent=2)
    print("DEFECTS " + json.dumps(report))
    if result_path:
        with open(result_path, "w") as handle:
            handle.write(text + "\n")


args = sys.argv[sys.argv.index("--") + 1:]
main(*args[:2])
