"""Prototype B: shape keys for a model whose spikes are loose pieces stuck into the body.

    tools/bl scripts/b_morph_pieces.py <model.glb> <out.glb> <facts.json> <pieces.csv> [key=value ...]

Splits the mesh into its connected pieces. The piece with the most triangles is the body. Every
other piece is measured (triangles, length, how many times longer than wide, where it sits) and
called a spike when it is long and thin and above the legs. For each spike the root is the end
nearest the body's surface or inside it, the tip is the vertex farthest from the root, and the
axis runs from one to the other. Three shape keys, on the same vertices:

  retracted   every spike shrunk to a point at its root, which is inside the body
  extended    every spike made `factor` times longer along its own axis
  tail_only   the same as extended, for spikes behind `tail` (a share of the body length) only:
              shows that groups of spikes can have their own key

Settings: slender (length over width needed to be a spike), legs (share of the height below
which a piece is left alone), factor, tail, mask=<out.glb> (base shape painted by class).
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from mathutils.bvhtree import BVHTree
import furlib as F

a = F.args()
src, out, facts_path, csv_path = a[:4]
SET = {"slender": 2.5, "legs": 0.3, "factor": 3.0, "tail": 0.25, "mask": ""}
for kv in a[4:]:
    k, v = kv.split("=", 1)
    SET[k] = type(SET[k])(v)

obj = F.load_one_mesh(src)
me = obj.data
co, e, tri = F.coords(me), F.edges(me), F.triangles(me)
label, n = F.components(len(co), e, np.ones(len(co), dtype=bool))
tri_label = label[tri[:, 0]]
tri_count = np.bincount(tri_label, minlength=n)
body = int(np.argmax(tri_count))
body_tri = tri[tri_label == body]
body_tree = BVHTree.FromPolygons([tuple(p) for p in co], [tuple(int(i) for i in t) for t in body_tri], all_triangles=True)
lo, hi = co.min(0), co.max(0)
height, length = hi[2] - lo[2], hi[1] - lo[1]


def depth(p):
    """Metres outside the body's surface (negative inside)."""
    loc, normal, _, dist = body_tree.find_nearest(tuple(p))
    return dist if (p - np.array(loc)).dot(np.array(normal)) >= 0 else -dist


retracted, extended, tail_only = co.copy(), co.copy(), co.copy()
klass = np.zeros(len(co))  # 0 body, 0.5 other piece, 1 spike
rows = []
k = SET["factor"]
for c in range(n):
    if c == body:
        continue
    idx = np.nonzero(label == c)[0]
    p = co[idx]
    centre = p.mean(0)
    row = {"piece": c, "triangles": int(tri_count[c]), "vertices": len(idx),
           "centre_x": round(centre[0], 4), "centre_forward": round(-centre[1], 4), "centre_up": round(centre[2], 4)}
    klass[idx] = 0.5
    if len(idx) < 4:
        rows.append({**row, "class": "too small"}); continue
    # Principal axes: the direction the piece is longest in, and its spread across it.
    w, v = np.linalg.eigh(np.cov((p - centre).T))
    main = v[:, 2]
    along = (p - centre) @ main
    long_m = along.max() - along.min()
    wide_m = 4 * np.sqrt(max(w[1], 1e-12))  # about the width across, for a round section
    slender = long_m / wide_m
    ends = [p[np.argmin(along)], p[np.argmax(along)]]
    d0, d1 = depth(ends[0]), depth(ends[1])
    root_end = ends[0] if d0 < d1 else ends[1]
    # The root: the mean of the vertices in the tenth of the length nearest the root end.
    t = np.abs((p - root_end) @ main)
    root = p[t <= 0.1 * long_m].mean(0)
    tip = p[np.argmax(np.linalg.norm(p - root, axis=1))]
    axis = tip - root
    spike_len = float(np.linalg.norm(axis))
    row.update({"length_m": round(float(long_m), 4), "width_m": round(float(wide_m), 4), "slender": round(float(slender), 2),
                "root_outside_body_m": round(min(d0, d1), 4), "tip_outside_body_m": round(max(d0, d1), 4)})
    above_legs = (centre[2] - lo[2]) / height > SET["legs"]
    if slender < SET["slender"]:
        rows.append({**row, "class": "not slender"}); continue
    if not above_legs:
        rows.append({**row, "class": "slender, in the leg zone"}); continue
    if min(d0, d1) > 0.02:
        rows.append({**row, "class": "slender, not touching the body"}); continue
    axis /= spike_len
    klass[idx] = 1.0
    proj = np.clip((p - root) @ axis, 0, None)
    extended[idx] = p + (k - 1) * proj[:, None] * axis
    retracted[idx] = root + 0.02 * (p - root)
    in_tail = (hi[1] - centre[1]) / length < SET["tail"]  # Blender +y is the back of the creature
    if in_tail:
        tail_only[idx] = extended[idx]
    rows.append({**row, "class": "spike", "in_tail": in_tail})

fields = ["piece", "class", "in_tail", "triangles", "vertices", "length_m", "width_m", "slender", "root_outside_body_m",
          "tip_outside_body_m", "centre_x", "centre_forward", "centre_up"]
with open(csv_path, "w", newline="") as f:
    wtr = csv.DictWriter(f, fieldnames=fields); wtr.writeheader(); wtr.writerows(rows)

classes = {}
for r in rows:
    classes[r["class"]] = classes.get(r["class"], 0) + 1
spike_rows = [r for r in rows if r["class"] == "spike"]
shapes = {"retracted": retracted, "extended": extended, "tail_only": tail_only}
facts = {"source": os.path.basename(src), "settings": SET, "vertices": len(co), "triangles": len(tri), "pieces": int(n),
         "body_triangles": int(tri_count[body]), "classes": classes,
         "spikes": {"count": len(spike_rows), "in_tail": sum(1 for r in spike_rows if r["in_tail"]),
                    "triangles": sum(r["triangles"] for r in spike_rows),
                    "length_m": {"min": min(r["length_m"] for r in spike_rows), "median": float(np.median([r["length_m"] for r in spike_rows])),
                                 "max": max(r["length_m"] for r in spike_rows)},
                    "roots_inside_body": sum(1 for r in spike_rows if r["root_outside_body_m"] < 0)},
         "base": {"self_intersecting_pairs": F.self_intersections(co, tri), "box_size_m": (hi - lo).tolist()},
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
    import bpy
    obj.shape_key_clear()
    F.paint(obj, "mask", klass)
    plain = bpy.data.materials.new("mask"); plain.use_nodes = True
    nt = plain.node_tree
    attr = nt.nodes.new("ShaderNodeVertexColor"); attr.layer_name = "mask"
    nt.links.new(attr.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.clear(); me.materials.append(plain)
    F.export_glb(SET["mask"], morph=False, vertex_colour=True)
