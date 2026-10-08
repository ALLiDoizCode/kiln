#!/usr/bin/env python3
"""One CSV row per UV or bake run in runs/uv_* and runs/bake_*:
   python3 scripts/summarise_bake.py > bake.csv
picture_diff.csv, if there, adds how far each run's review pictures are from the dense model's."""
import csv, glob, json, os, sys
def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None
diffs = {}
if os.path.exists("picture_diff.csv"):
    for r in csv.DictReader(open("picture_diff.csv")):
        diffs.setdefault(r["run"], {})[r["view"]] = r
rows = []
for path in sorted(glob.glob("runs/uv_*.run.json") + glob.glob("runs/bake_*.run.json") + glob.glob("runs/tripo_*.run.json")):
    name = os.path.basename(path)[:-9]
    run = json.load(open(path)); f = load(f"runs/{name}.facts.json"); g = load(f"runs/{name}.glb.json"); m = load(f"runs/{name}.measure.json")
    row = {"run": name, "seconds": run["wall_seconds"], "peak_rss_mb": run["peak_rss_mb"], "exit": run["exit_status"], "signal": run["signal"] or ""}
    if f:
        s = f["settings"]
        row.update({k: s.get(k, "") for k in ("uv", "angle", "island_margin", "pack", "normals", "sharp_angle", "size", "samples", "cage_extrusion", "max_ray_distance", "margin", "margin_type", "colour", "fit", "jpeg", "weld")})
        row["device"] = f.get("device", ""); row["gpu_bake_error"] = f.get("gpu_bake_error", "")
        sec = f["seconds"]
        row["uv_seconds"] = sec.get("uvs"); row["bake_seconds"] = round(sum(v for k, v in sec.items() if k.startswith("bake_")), 2)
        row["import_high_seconds"] = sec.get("import_high")
        rc = f.get("ray_check")
        if rc:
            row["ray_missed_share"] = round(rc["missed_share"], 5)
            row["ray_hit_p99_mm"] = round(1000 * rc["hit_distance_from_low_surface"]["p99"], 3) if rc["hit_distance_from_low_surface"]["p99"] is not None else ""
            row["nearest_dense_p99_mm"] = round(1000 * rc["nearest_dense_surface"]["p99"], 3)
            row["ray_far_hit_share"] = round(rc["hits_further_than_twice_p99_nearest"], 5)
    if m:
        u = m.get("uvs") or {}
        row.update({"triangles": m["totals"]["triangles"], "vertices_stored": m["totals"]["vertices"], "bytes": m["file"]["bytes"],
                    "uv_islands": u.get("islands"), "uv_seam_share": round(u.get("seam_share", 0), 4), "uv_coverage": round(u.get("coverage", 0), 4),
                    "uv_area_sum": round(u.get("triangle_area_sum", 0), 4), "validator_errors": m["validator"]["errors"], "validator_warnings": m["validator"]["warnings"]})
        td = m.get("texel_density")
        if td:
            row.update({"texel_px_per_m": round(td["pixels_per_metre"], 1), "texel_p05": round(td["p05"], 1), "texel_p95": round(td["p95"], 1)})
        row["images"] = " ".join(f"{t['used_as'][0].split(' ')[0] if t['used_as'] else 'unused'}:{t['format']}:{t['width']}:{t['bytes']}" for t in m["textures"])
    if g:
        row["sha256"] = g["sha256"]; row["image_sha256"] = " ".join(i["sha256"][:12] for i in g["images"])
    for view, d in diffs.get(name, {}).items():
        row[f"diff_{view}_mean"] = d["mean_abs_difference"]; row[f"diff_{view}_over8"] = d["share_over_8"]
    rows.append(row)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
w = csv.DictWriter(sys.stdout, keys); w.writeheader(); w.writerows(rows)
