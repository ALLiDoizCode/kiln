"""Prototype F: the calm and the spiked generation side by side, in numbers.
    tools/bl scripts/f_compare.py <facts.json> <model.glb> ...
For each model: the whole box, the box of the body alone (vertices where the model is thicker
than 3.5 cm, which leaves spikes out), where the four feet and the snout are, and how many
vertices are spike (thin). glTF axes in the output: x across, y up, z forward.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from mathutils.bvhtree import BVHTree
import furlib as F

a = F.args()
out = {}
for path in a[1:]:
    obj = F.load_one_mesh(path)
    co, e, tri = F.coords(obj.data), F.edges(obj.data), F.triangles(obj.data)
    nrm = F.vertex_normals(co, tri)
    tree = BVHTree.FromPolygons([tuple(p) for p in co], [tuple(int(i) for i in t) for t in tri], all_triangles=True)
    thick = np.full(len(co), 1.0)
    for i, (p, n) in enumerate(zip(co, nrm)):
        hit = tree.ray_cast(tuple(p - 1e-4 * n), tuple(-n))
        if hit[0] is not None:
            thick[i] = hit[3]
    body = co[thick > 0.035]
    g = lambda v: [round(float(v[0]), 3), round(float(v[2]), 3), round(float(-v[1]), 3)]
    size = lambda c: [round(float(c[:, 0].max() - c[:, 0].min()), 3), round(float(c[:, 2].max() - c[:, 2].min()), 3), round(float(c[:, 1].max() - c[:, 1].min()), 3)]
    low = body[body[:, 2] < 0.06]
    feet = {}
    for side, sx in (("left", 1), ("right", -1)):
        for end, sy in (("front", -1), ("back", 1)):
            pts = low[(np.sign(low[:, 0]) == sx) & (np.sign(low[:, 1] - np.median(low[:, 1])) == sy)]
            feet[f"{end}_{side}"] = g(pts.mean(0)) if len(pts) else None
    out[os.path.basename(path)] = {
        "vertices": len(co), "triangles": len(tri), "whole_size_xyz_m": size(co), "body_size_xyz_m": size(body),
        "body_top_y_m": round(float(body[:, 2].max()), 3), "thin_vertices": int((thick <= 0.035).sum()),
        "thin_share": round(float((thick <= 0.035).mean()), 3), "feet": feet,
        "body_front_most_z": round(float(-body[:, 1].min()), 3), "body_back_most_z": round(float(-body[:, 1].max()), 3),
        "highest_point": g(co[np.argmax(co[:, 2])])}
F.write_json(a[0], out)
