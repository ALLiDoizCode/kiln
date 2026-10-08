#!/usr/bin/env python3
"""One CSV row per reduction run in runs/red_*: python3 scripts/summarise_reduce.py > reduce.csv"""
import csv, glob, json, os, sys
def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None
rows = []
for path in sorted(glob.glob("runs/red_*.run.json")):
    name = os.path.basename(path)[:-9]
    run = json.load(open(path)); f = load(f"runs/{name}.facts.json"); g = load(f"runs/{name}.glb.json")
    m = load(f"runs/{name}.measure.json"); d = load(f"runs/{name}.distance.json")
    subject, _, variant = name[4:].partition("__")
    row = {"subject": subject, "variant": variant, "seconds": run["wall_seconds"], "peak_rss_mb": run["peak_rss_mb"],
           "exit": run["exit_status"], "signal": run["signal"] or "", "least_available_mb": run["least_available_mb"],
           "started": run["started"]}
    if f:
        a = f["after"]
        row.update({"triangles": f["triangles_reached"], "passes": len(f["passes"]), "extra_passes": f["extra_passes"],
                    "reduce_seconds": round(sum(v for k, v in f["seconds"].items() if k not in ("import", "export", "count_before", "count_after")), 2),
                    "open_edges": a["boundary_edges"], "non_manifold_edges": a["non_manifold_edges"], "flipped_edges": a["flipped_edges"],
                    "degenerate_faces": a["degenerate_faces"], "wire_edges": a["wire_edges"], "pieces": a["pieces"],
                    "custom_normals_kept": f["custom_normals_after_reduce"], "uv_layers": len(f["after_object"]["uv_layers"]),
                    "intermediate": json.dumps({k: v for k, v in f.items() if k.startswith(("triangles_after_", "faces_after_", "seam_", "weld_joined", "largest_face"))})})
    if g:
        t = g["triangle_areas"]
        row.update({"bytes": g["bytes"], "vertices_stored": g["vertices_stored"], "backward_normal_corners": g["backward_normal_corners"],
                    "share_holding_99pc_area": round(t["share_holding_99pc_of_area"], 4),
                    "share_under_100th_mean": round(t["share_under_100th_of_mean"], 4),
                    "surface_area": round(t["surface_area"], 4), "sha256": g["sha256"]})
    if m:
        u = m.get("uvs")
        if u:
            row.update({"uv_islands": u["islands"], "uv_seam_share": round(u["seam_share"], 4), "uv_coverage": round(u["coverage"], 4)})
        td = m.get("texel_density")
        if td:
            row.update({"texel_px_per_m": round(td["pixels_per_metre"], 1), "texel_p05": round(td["p05"], 1), "texel_p95": round(td["p95"], 1)})
        row["validator_errors"] = m["validator"]["errors"]
    if d:
        row.update({"to_dense_p95_mm": round(1000 * d["model_to_reference"]["p95"], 3), "to_dense_largest_mm": round(1000 * d["model_to_reference"]["largest"], 3),
                    "dense_to_it_p95_mm": round(1000 * d["reference_to_model"]["p95"], 3), "dense_to_it_largest_mm": round(1000 * d["reference_to_model"]["largest"], 3)})
    rows.append(row)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
w = csv.DictWriter(sys.stdout, keys); w.writeheader(); w.writerows(rows)
