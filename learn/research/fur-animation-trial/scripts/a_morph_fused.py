"""Prototype A: shape keys for a model whose spikes are fused into one surface, with no hand work.

    tools/bl scripts/a_morph_fused.py <model.glb> <out.glb> <facts.json> [key=value ...]

Finds spikes either by how thin the model is at each vertex (detect=thin, the default) or by how
far each vertex sits outside a smoothed copy of the surface (detect=outside), then stores
shape keys on the same vertices (so the same vertex count and order as the base shape):

  soft_all      every vertex moved to its Laplacian-smoothed place (prototype A1, the blunt way)
  soft_masked   only spike vertices moved, onto the nearest point of the smoothed copy
  spiked_push   spike vertices pushed out along the line from the smoothed copy to the vertex
  spiked_axial  each spike (a connected group of spike vertices) stretched along its own axis

Settings (defaults in SET below): thin/thick (metres of thickness at which the mask is 1 and 0), smooth=laplace|taubin, iterations, low/high (metres outside the
smoothed copy at which the mask is 0 and 1), legs (share of the height below which nothing
moves), factor (how many times longer a spike gets), soft_iterations.
With mask=<out.glb> also writes the base shape painted with the mask (blue 0, red 1).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from mathutils.bvhtree import BVHTree
import furlib as F

a = F.args()
src, out, facts_path = a[:3]
SET = {"detect": "thin", "thin": 0.02, "thick": 0.035, "smooth": "laplace", "iterations": 30,
       "low": 0.004, "high": 0.012, "legs": 0.33, "factor": 3.0, "soft_iterations": 10, "mask": "", "tip": 0.015}
for kv in a[3:]:
    k, v = kv.split("=", 1)
    SET[k] = type(SET[k])(v)

obj = F.load_one_mesh(src)
me = obj.data
co, e, tri = F.coords(me), F.edges(me), F.triangles(me)
height = co[:, 2].max() - co[:, 2].min()

# 1. The smoothed copy, and how far outside it each vertex sits.
s = F.smooth(co, e, SET["iterations"], taubin=SET["smooth"] == "taubin")
tree = BVHTree.FromPolygons([tuple(p) for p in s], [tuple(int(i) for i in t) for t in tri], all_triangles=True)
near = np.empty_like(co); h = np.empty(len(co))
for i, p in enumerate(co):
    loc, normal, _, dist = tree.find_nearest(tuple(p))
    near[i] = loc
    h[i] = dist if (p - np.array(loc)).dot(np.array(normal)) >= 0 else -dist


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


rel = (co[:, 2] - co[:, 2].min()) / height
region = smoothstep(rel, SET["legs"], SET["legs"] + 0.08)

# The other way to find a spike: it is thin. From each vertex, look straight into the model
# (against the vertex normal) and measure how far the other side is.
normals = F.vertex_normals(co, tri)
own = BVHTree.FromPolygons([tuple(p) for p in co], [tuple(int(i) for i in t) for t in tri], all_triangles=True)
thickness = np.full(len(co), 1.0)
for i, (p, nrm) in enumerate(zip(co, normals)):
    hit = own.ray_cast(tuple(p - 1e-4 * nrm), tuple(-nrm))
    if hit[0] is not None:
        thickness[i] = hit[3]
# A single ray is noisy: take the middle value of each vertex and its neighbours.
nb = [[i] for i in range(len(co))]
for x, y in e:
    nb[x].append(y); nb[y].append(x)
thickness = np.array([np.median(thickness[n_]) for n_ in nb])

if SET["detect"] == "thin":
    mask = (1 - smoothstep(thickness, SET["thin"], SET["thick"])) * region
    keep = (thickness < SET["thick"]) & (region > 0.5)
else:
    mask = smoothstep(h, SET["low"], SET["high"]) * region
    keep = (h > SET["low"]) & (region > 0.5)

# 2. The shapes.
k = SET["factor"]
soft_all = F.smooth(co, e, SET["soft_iterations"])
soft_masked = co + mask[:, None] * (near - co)
spiked_push = co + (k - 1) * mask[:, None] * (co - near)

# Each spike on its own: a connected group of vertices outside the smoothed copy.
label, n = F.components(len(co), e, keep)
spiked_axial = co.copy()
spikes = []
for c in range(n):
    idx = np.nonzero(label == c)[0]
    if len(idx) < 3 or h[idx].max() < SET["tip"]:
        continue
    # The root is where the group touches the rest of the model; the tip is its farthest vertex.
    edge_of_group = np.array([v for v in idx if any(label[w] != c for w in nb[v])], dtype=int)
    if len(edge_of_group) == 0:
        edge_of_group = idx[h[idx] <= np.percentile(h[idx], 25)]
    root = co[edge_of_group].mean(0)
    tip = co[idx[np.argmax(np.linalg.norm(co[idx] - root, axis=1))]]
    axis = tip - root
    length = np.linalg.norm(axis)
    if length < 1e-6:
        continue
    axis /= length
    along = np.clip((co[idx] - root) @ axis, 0, None)
    spiked_axial[idx] = co[idx] + (k - 1) * along[:, None] * axis
    spikes.append({"vertices": int(len(idx)), "length_m": float(length), "tip_height_m": float(h[idx].max())})

shapes = {"soft_all": soft_all, "soft_masked": soft_masked, "spiked_push": spiked_push, "spiked_axial": spiked_axial}

# 3. What each shape does to the mesh.
facts = {"source": os.path.basename(src), "settings": SET, "vertices": len(co), "triangles": len(tri),
         "height_m": float(height),
         "thickness_m": {str(p): float(np.percentile(thickness, p)) for p in (5, 25, 50, 75, 90, 95)},
         "outside_m": {str(p): float(np.percentile(h, p)) for p in (5, 25, 50, 75, 90, 95, 99, 100)},
         "mask": {"vertices_above_0": int((mask > 0).sum()), "vertices_above_half": int((mask > 0.5).sum()),
                  "vertices_at_1": int((mask >= 0.999).sum())},
         "spike_groups": {"groups_found": int(n), "groups_used": len(spikes),
                          "vertices_in_largest": max((x["vertices"] for x in spikes), default=0),
                          "lengths_m_sorted": sorted((round(x["length_m"], 4) for x in spikes), reverse=True)[:25],
                          "sizes_sorted": sorted((x["vertices"] for x in spikes), reverse=True)[:25]},
         "base": {"self_intersecting_pairs": F.self_intersections(co, tri),
                  "box_size_m": (co.max(0) - co.min(0)).tolist()},
         "shapes": {}}
for name, sh in shapes.items():
    facts["shapes"][name] = {
        "vertices_moved_over_1mm": int((np.linalg.norm(sh - co, axis=1) > 0.001).sum()),
        "largest_move_m": float(np.linalg.norm(sh - co, axis=1).max()),
        "box_size_m": (sh.max(0) - sh.min(0)).tolist(),
        "self_intersecting_pairs": F.self_intersections(sh, tri),
        "triangles_turned_over": F.flipped(co, sh, tri),
        "edge_stretch": F.stretch(co, sh, e),
    }
    F.add_key(obj, name, sh, slider_max=2.0)
F.write_json(facts_path, facts)

os.makedirs(os.path.dirname(out), exist_ok=True)
F.export_glb(out)
print("WROTE", out, os.path.getsize(out))

if SET["mask"]:
    obj.shape_key_clear()
    F.paint(obj, "mask", mask)
    plain = __import__("bpy").data.materials.new("mask")
    plain.use_nodes = True
    nt = plain.node_tree
    attr = nt.nodes.new("ShaderNodeVertexColor"); attr.layer_name = "mask"
    nt.links.new(attr.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.clear(); me.materials.append(plain)
    F.export_glb(SET["mask"], morph=False, vertex_colour=True)
