#!/usr/bin/env python3
"""One CSV row per repair run in runs/rep_*: python3 scripts/summarise_repair.py > repair.csv"""
import csv, glob, json, os, sys
rows = []
def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None
for path in sorted(glob.glob("runs/rep_*.run.json")):
    name = os.path.basename(path)[:-9]
    run = json.load(open(path)); f = load(f"runs/{name}.facts.json"); g = load(f"runs/{name}.glb.json")
    m = load(f"runs/{name}.measure.json"); v = load(f"runs/{name}.validator.txt")
    model, _, variant = name[4:].partition("__")
    row = {"model": model, "variant": variant, "seconds": run["wall_seconds"], "peak_rss_mb": run["peak_rss_mb"], "exit": run["exit_status"]}
    if f and "before" in f:
        b, a = f["before"], f["after"]
        for k in ("triangles", "boundary_edges", "boundary_loops", "non_manifold_edges", "flipped_edges", "degenerate_faces", "pieces"):
            row[k + "_before"] = b[k]; row[k + "_after"] = a[k]
        row["surface_area_change_pc"] = round(100 * (f["surface_area_after"] / f["surface_area_before"] - 1), 3)
        row["bounds_changed"] = max(abs(x - y) for p, q in zip(f["bounds_before"], f["bounds_after"]) for x, y in zip(p, q)) > 1e-6
        row["custom_normals_after"] = f["after_object"]["has_custom_normals"]
        extra = {}
        for step in f["steps_done"]:
            e = f.get("after_" + step, {})
            extra.update({k: e[k] for k in ("vertices_joined", "faces_removed", "pieces_removed", "triangles_removed", "share_of_surface_removed", "faces_turned", "holes_filled", "sides_of_largest", "faces_added") if k in e})
        row["step_facts"] = json.dumps(extra)
    if g:
        row["vertices_stored_out"] = g["vertices_stored"]; row["backward_normal_corners_out"] = g["backward_normal_corners"]
        a = g.get("against_reference")
        if a: row["normals_share_over_1deg"] = round(a["normals"]["share_over_1_degree"], 4)
    if m and m.get("uvs"):
        row["uv_islands_out"] = m["uvs"]["islands"]; row["uv_coverage_out"] = round(m["uvs"]["coverage"], 4)
        row["uv_triangles_without_area"] = m["uvs"]["triangles_without_area"]
    if v: row["validator_errors_out"] = v.get("errors")
    rows.append(row)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
w = csv.DictWriter(sys.stdout, keys); w.writeheader(); w.writerows(rows)
