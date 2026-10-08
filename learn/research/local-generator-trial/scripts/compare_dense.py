"""Compare the geometry of two dense .glb files (first primitive of each). Read-only. Needs numpy and scipy.

    <venv>/bin/python -I compare_dense.py <a.glb> <b.glb>

ComfyUI writes the prompt into each file it saves, so two saves of one mesh differ as files; this
compares what matters: vertex and triangle counts, whether positions and indices are the same to the
last bit, and how far the surfaces are apart: for 200,000 vertices of each file, the distance to the
nearest vertex of the other (median, 99th percentile and largest, in the files' units).
"""
import json, struct, sys, hashlib
import numpy as np
from scipy.spatial import cKDTree
CT = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
def read(path):
    with open(path, "rb") as fh:
        fh.read(12); jlen, _ = struct.unpack("<II", fh.read(8)); doc = json.loads(fh.read(jlen)); blen, _ = struct.unpack("<II", fh.read(8)); start = fh.tell()
    buf = np.memmap(path, dtype=np.uint8, mode="r", offset=start, shape=(blen,))
    def acc(i, n):
        a = doc["accessors"][i]; v = doc["bufferViews"][a["bufferView"]]
        return np.frombuffer(buf, dtype=CT[a["componentType"]], count=a["count"] * n, offset=v.get("byteOffset", 0) + a.get("byteOffset", 0)).reshape(-1, n)
    p = doc["meshes"][0]["primitives"][0]
    return acc(p["attributes"]["POSITION"], 3), acc(p["indices"], 1).reshape(-1, 3)
(pa, ia), (pb, ib) = read(sys.argv[1]), read(sys.argv[2])
out = {"a": sys.argv[1], "b": sys.argv[2], "vertices": [len(pa), len(pb)], "triangles": [len(ia), len(ib)],
       "same_positions_bit_for_bit": pa.shape == pb.shape and bool(np.array_equal(pa, pb)),
       "same_indices_bit_for_bit": ia.shape == ib.shape and bool(np.array_equal(ia, ib)),
       "bounding_box_a": [pa.min(0).round(5).tolist(), pa.max(0).round(5).tolist()],
       "bounding_box_b": [pb.min(0).round(5).tolist(), pb.max(0).round(5).tolist()]}
rng = np.random.default_rng(0)
for name, (x, y) in {"a_to_b": (pa, pb), "b_to_a": (pb, pa)}.items():
    s = x[rng.choice(len(x), size=min(200000, len(x)), replace=False)]
    d, _ = cKDTree(y).query(s, workers=-1)
    out["nearest_vertex_distance_" + name] = {"median": float(np.median(d)), "p99": float(np.percentile(d, 99)), "max": float(d.max())}
print(json.dumps(out, indent=1))
