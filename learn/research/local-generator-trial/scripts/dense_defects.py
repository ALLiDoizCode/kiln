"""Count the defects of a .glb too dense for scripts/mesh_defects.py (which builds a bmesh and needs
far more memory than this machine has for 15 million triangles). Read-only.

    <venv>/bin/python -I dense_defects.py <model.glb> [result.json]

Needs numpy and scipy (the local-gen environment has them; system Python does not). Reads the
first buffer of the .glb directly. Counts are taken twice, as mesh_defects.py does: on the vertices
as stored, and after joining vertices that sit at the same position (rounded to 1e-6 of a unit).
The numbers mean the same as in mesh_defects.py; "pieces" here are faces joined through shared
edges or vertices of the welded mesh. Degenerate faces: area under 1e-12 square units.
"""
import json, struct, sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

CT = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

def read(path):
    with open(path, "rb") as fh:
        magic, version, length = struct.unpack("<III", fh.read(12))
        jlen, jtype = struct.unpack("<II", fh.read(8)); doc = json.loads(fh.read(jlen))
        blen, btype = struct.unpack("<II", fh.read(8)); start = fh.tell()
    buf = np.memmap(path, dtype=np.uint8, mode="r", offset=start, shape=(blen,))
    def acc(i):
        a = doc["accessors"][i]; v = doc["bufferViews"][a["bufferView"]]
        dt = np.dtype(CT[a["componentType"]]); n = NC[a["type"]]
        off = v.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = v.get("byteStride", 0)
        if stride and stride != dt.itemsize * n:
            raw = np.lib.stride_tricks.as_strided(buf[off:], shape=(a["count"], dt.itemsize * n), strides=(stride, 1))
            return np.ascontiguousarray(raw).view(dt).reshape(a["count"], n)
        return np.frombuffer(buf, dtype=dt, count=a["count"] * n, offset=off).reshape(a["count"], n)
    out = []
    for m in doc["meshes"]:
        for p in m["primitives"]:
            pos = acc(p["attributes"]["POSITION"]).astype(np.float64)
            idx = acc(p["indices"]).astype(np.int64).reshape(-1, 3) if "indices" in p else np.arange(len(pos)).reshape(-1, 3)
            out.append((pos, idx, sorted(p["attributes"])))
    return doc, out

def count(pos, tri):
    nv = len(pos)
    e = np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]])
    lo, hi = e.min(1), e.max(1); keep = lo != hi
    keys = lo[keep] * nv + hi[keep]
    uniq, counts = np.unique(keys, return_counts=True)
    a, b, c = pos[tri[:, 0]], pos[tri[:, 1]], pos[tri[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    graph = coo_matrix((np.ones(len(e), dtype=np.int8), (e[:, 0], e[:, 1])), shape=(nv, nv))
    ncomp, label = connected_components(graph, directed=False)
    piece_tris = np.bincount(label[tri[:, 0]], minlength=ncomp); piece_tris = np.sort(piece_tris[piece_tris > 0])[::-1]
    used = np.zeros(nv, dtype=bool); used[tri.ravel()] = True
    # edges whose two faces wind opposite ways: a directed edge used twice in the same direction
    dkeys = e[keep][:, 0] * nv + e[keep][:, 1]
    du, dc = np.unique(dkeys, return_counts=True)
    total = max(1, len(tri))
    return {"vertices": int(nv), "vertices_used": int(used.sum()), "triangles": int(len(tri)), "edges": int(len(uniq)),
            "boundary_edges": int((counts == 1).sum()), "non_manifold_edges": int((counts > 2).sum()),
            "loose_vertices": int((~used).sum()), "edges_used_twice_the_same_way": int((dc > 1).sum()),
            "degenerate_faces": int((area < 1e-12).sum()), "zero_length_edges": int((~keep).sum()),
            "pieces": int(len(piece_tris)), "piece_triangles_largest_first": [int(x) for x in piece_tris[:20]],
            "small_pieces": int((piece_tris < 0.01 * total).sum()),
            "small_piece_triangles": int(piece_tris[piece_tris < 0.01 * total].sum()),
            "surface_area": float(area.sum()), "smallest_face_area": float(area.min()), "median_face_area": float(np.median(area))}

doc, prims = read(sys.argv[1])
report = {"file": sys.argv[1], "generator": doc.get("asset", {}).get("generator"), "primitives": []}
for pos, tri, attrs in prims:
    q = np.round(pos / 1e-6).astype(np.int64)
    _, first, inverse = np.unique(q, axis=0, return_index=True, return_inverse=True)
    wtri = inverse.reshape(-1)[tri]
    wtri = wtri[(wtri[:, 0] != wtri[:, 1]) & (wtri[:, 1] != wtri[:, 2]) & (wtri[:, 0] != wtri[:, 2])]
    report["primitives"].append({"attributes": attrs,
        "bounding_box_gltf_yup": {"min": pos.min(0).round(6).tolist(), "max": pos.max(0).round(6).tolist(),
                                  "dimensions": (pos.max(0) - pos.min(0)).round(6).tolist()},
        "as_stored": count(pos, tri), "welded": count(pos[first], wtri),
        "faces_lost_to_welding": int(len(tri) - len(wtri))})
text = json.dumps(report, indent=1)
print(text)
if len(sys.argv) > 2: open(sys.argv[2], "w").write(text + "\n")
