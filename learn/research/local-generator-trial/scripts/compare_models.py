#!/usr/bin/env python3
"""Say how alike two .glb files are: for the question "does the same seed give the same file?".

    python3 -I scripts/compare_models.py <a.glb> <b.glb>      (from learn/research/tripo-api-trial/)

Prints JSON. Levels, strongest first:
  same_bytes       the two files have the same SHA-256
  same_geometry    every mesh primitive has the same vertex positions and the same triangle indices,
                   in the same order, to the last bit
  same_images      every stored image has the same SHA-256
When the vertex counts match but the positions do not, the largest distance between a vertex and
the vertex stored at the same place in the other file is given (in the files' own units). That
distance means something only if both files store their vertices in the same order; a file that
went through Blender does not. "same_position_set" does not depend on order: it says whether the
two files hold the same points, each rounded to a millionth of a unit, the same number of times.
Standard library only; reads the files with kiln/glb.py.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
from kiln import glb  # noqa: E402


def facts(path):
    model = glb.load(path)
    doc = model.json
    prims = []
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            flat, _ = model.accessor(prim["attributes"]["POSITION"])
            positions = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
            indices = model.accessor(prim["indices"])[0] if "indices" in prim else None
            prims.append((positions, indices))
    images = [hashlib.sha256(model.image_bytes(i) or b"").hexdigest() for i in range(len(doc.get("images", [])))]
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    return digest, prims, images


def main(a, b):
    da, pa, ia = facts(a)
    db, pb, ib = facts(b)
    out = {"a": a, "b": b, "sha256_a": da, "sha256_b": db, "same_bytes": da == db,
           "primitives": [len(pa), len(pb)],
           "vertices": [sum(len(p[0]) for p in pa), sum(len(p[0]) for p in pb)],
           "same_images": ia == ib, "images": [len(ia), len(ib)]}
    out["same_geometry"] = len(pa) == len(pb) and all(x[0] == y[0] and x[1] == y[1] for x, y in zip(pa, pb))
    def points(prims):
        return sorted(tuple(round(v, 6) for v in p) for prim in prims for p in prim[0])
    out["same_position_set"] = points(pa) == points(pb)
    if not out["same_geometry"] and len(pa) == len(pb) and all(len(x[0]) == len(y[0]) for x, y in zip(pa, pb)):
        worst = 0.0
        for x, y in zip(pa, pb):
            for p, q in zip(x[0], y[0]):
                worst = max(worst, sum((u - v) ** 2 for u, v in zip(p, q)) ** 0.5)
        out["largest_vertex_distance"] = worst
        out["same_indices"] = all(x[1] == y[1] for x, y in zip(pa, pb))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:3])
