#!/usr/bin/env python3
"""One CSV row per round-trip run in runs/rt_*: python3 scripts/summarise_roundtrip.py > roundtrip.csv"""
import csv, glob, json, os, sys
rows = []
for path in sorted(glob.glob("runs/rt_*.run.json")):
    name = os.path.basename(path)[:-9]
    run = json.load(open(path))
    row = {"run": name, "seconds": run["wall_seconds"], "peak_rss_mb": run["peak_rss_mb"], "exit": run["exit_status"]}
    try:
        g = json.load(open(f"runs/{name}.glb.json")); v = json.load(open(f"runs/{name}.validator.txt"))
        f = json.load(open(f"runs/{name}.facts.json"))
    except (OSError, ValueError):
        rows.append(row); continue
    a = g["against_reference"]
    row.update({
        "settings": " ".join(f"{k}={v}" for k, v in f["settings"].items()),
        "bytes_in": a["reference_bytes"], "bytes_out": g["bytes"],
        "triangles_in": a["reference_triangles"], "triangles_out": g["triangles"],
        "vertices_in": a["reference_vertices_stored"], "vertices_out": g["vertices_stored"],
        "welded_points_in": a["reference_welded_points"], "welded_points_out": g["welded_points"],
        "zero_normals_in": a["reference_zero_length_normals"], "zero_normals_out": g["zero_length_normals"],
        "normals_matched_share": round(a["normals"]["matched_share"], 4),
        "normals_largest_angle": round(a["normals"]["largest_angle_degrees"], 2),
        "normals_share_over_1deg": round(a["normals"]["share_over_1_degree"], 5),
        "extensions_dropped": " ".join(a["extensions_dropped"]),
        "images_in": " ".join(f"{i['format']}:{i['width']}:{i['bytes']}" for i in a["reference_images"]),
        "images_out": " ".join(f"{i['format']}:{i['width']}:{i['bytes']}" for i in g["images"]),
        "images_same_bytes": " ".join(str(x) for x in a["same_images"]),
        "validator_errors_out": v.get("errors"), "validator_warnings_out": v.get("warnings"),
        "sha256": g["sha256"]})
    rows.append(row)
keys = []
for r in rows:
    for k in r:
        if k not in keys: keys.append(k)
w = csv.DictWriter(sys.stdout, keys); w.writeheader(); w.writerows(rows)
