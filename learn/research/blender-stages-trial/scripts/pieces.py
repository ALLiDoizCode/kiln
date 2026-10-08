"""The separate pieces of a model: triangles, surface area and bounding box of each. Read-only.

    tools/bl pieces.py <model.glb> [result.json]

The mesh is welded at a millionth of a metre first, as scripts/mesh_defects.py does. Pieces are
listed largest surface first (at most 12). "inside_largest_box" says whether a piece's whole
bounding box lies within the bounding box of the piece with the most surface: a piece that
does may be hidden inside it.
"""
import json
import sys

import bmesh
import bpy

args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0], merge_vertices=True)
out = {"file": args[0], "pieces": []}
bm = bmesh.new()
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        mesh = obj.data.copy()
        mesh.transform(obj.matrix_world)
        bm.from_mesh(mesh)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bm.faces.index_update()
seen = set()
for face in bm.faces:
    if face.index in seen:
        continue
    seen.add(face.index)
    stack, tris, area = [face], 0, 0.0
    low, high = [1e9] * 3, [-1e9] * 3
    while stack:
        cur = stack.pop()
        tris += len(cur.verts) - 2
        area += cur.calc_area()
        for v in cur.verts:
            for i in range(3):
                low[i] = min(low[i], v.co[i]); high[i] = max(high[i], v.co[i])
            for other in v.link_faces:
                if other.index not in seen:
                    seen.add(other.index)
                    stack.append(other)
    out["pieces"].append({"triangles": tris, "area": area, "min": [round(x, 4) for x in low], "max": [round(x, 4) for x in high]})
out["pieces"].sort(key=lambda p: -p["area"])
total_area = sum(p["area"] for p in out["pieces"]); total_tris = sum(p["triangles"] for p in out["pieces"])
big = out["pieces"][0]
for p in out["pieces"]:
    p["share_of_area"] = round(p["area"] / total_area, 4); p["share_of_triangles"] = round(p["triangles"] / total_tris, 4)
    p["inside_largest_box"] = p is not big and all(p["min"][i] >= big["min"][i] - 1e-6 and p["max"][i] <= big["max"][i] + 1e-6 for i in range(3))
out["piece_count"] = len(out["pieces"])
out["pieces"] = out["pieces"][:12]
print("PIECES " + json.dumps(out))
if len(args) > 1:
    json.dump(out, open(args[1], "w"), indent=1)
