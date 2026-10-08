"""Prototype C: what a .glb holds for animation, read with kiln's own glTF reader (kiln/glb.py).

    python3 -I scripts/c_read_back.py <repo root> <model.glb> ...   prints one JSON object per file

Counts, per mesh primitive, the morph targets and which attributes each one moves, how many
bytes the targets take in the file, whether they are stored sparsely; then skins (joints) and
animations (which properties each one drives). Nothing here is a kiln feature: kiln's reader
gives the file's JSON and its accessors, and this script walks them.
"""
import json, os, sys
sys.path.insert(0, sys.argv[1])
from kiln import glb

for path in sys.argv[2:]:
    g = glb.load(path)
    d = g.json
    acc, views = d.get("accessors", []), d.get("bufferViews", [])
    out = {"file": os.path.basename(path), "bytes": os.path.getsize(path), "meshes": [], "skins": [], "animations": []}
    morph_views = set()
    for m in d.get("meshes", []):
        entry = {"name": m.get("name"), "weights": m.get("weights"), "target_names": (m.get("extras") or {}).get("targetNames"),
                 "primitives": []}
        for p in m["primitives"]:
            targets = p.get("targets", [])
            prim = {"vertices": acc[p["attributes"]["POSITION"]]["count"], "attributes": sorted(p["attributes"]),
                    "targets": len(targets), "target_attributes": sorted({k for t in targets for k in t}),
                    "sparse_target_accessors": sum(1 for t in targets for a in t.values() if "sparse" in acc[a]),
                    "target_counts_match_base": all(acc[a]["count"] == acc[p["attributes"]["POSITION"]]["count"] for t in targets for a in t.values())}
            for t in targets:
                for a in t.values():
                    if "bufferView" in acc[a]:
                        morph_views.add(acc[a]["bufferView"])
                    if "sparse" in acc[a]:  # a sparse accessor lists only the vertices that move
                        morph_views.add(acc[a]["sparse"]["indices"]["bufferView"])
                        morph_views.add(acc[a]["sparse"]["values"]["bufferView"])
            entry["primitives"].append(prim)
        out["meshes"].append(entry)
    out["morph_target_bytes"] = sum(views[v]["byteLength"] for v in morph_views)
    for s in d.get("skins", []):
        out["skins"].append({"name": s.get("name"), "joints": len(s["joints"]), "has_inverse_bind_matrices": "inverseBindMatrices" in s})
    for a in d.get("animations", []):
        paths = {}
        for c in a["channels"]:
            paths[c["target"]["path"]] = paths.get(c["target"]["path"], 0) + 1
        times = [acc[s["input"]] for s in a["samplers"]]
        out["animations"].append({"name": a.get("name"), "channels_by_path": paths, "keyframes_max": max(t["count"] for t in times),
                                  "seconds": max(t["max"][0] for t in times),
                                  "interpolations": sorted({s.get("interpolation", "LINEAR") for s in a["samplers"]})})
    out["nodes_with_weights"] = sum(1 for n in d.get("nodes", []) if "weights" in n)
    out["nodes_with_skin"] = sum(1 for n in d.get("nodes", []) if "skin" in n)
    out["extensions_used"] = d.get("extensionsUsed", [])
    print(json.dumps(out))
