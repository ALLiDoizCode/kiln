#!/usr/bin/env python3
"""The comparison table of stage 6, from the folders scripts/measure_model.sh wrote:
    python3 -I scripts/comparison.py > comparison.csv     (from learn/research/blender-stages-trial/)
One row per model: the chain's results (measurements/stages_*) and Tripo's own files."""
import csv, json, os, subprocess, sys
M = "../tripo-api-trial/measurements"; MODELS = "../tripo-api-trial/models"
ROWS = [("crate", "stages_crate_chain"), ("crate", "stages_crate_chain_fast"), ("crate", "stages_crate_chain_smart_uv"),
        ("crate", "stages_crate_baked1024"), ("crate", "stages_crate_baked4096"), ("crate", "stages_crate_reduced20k_own_uvs"),
        ("crate", "stages_crate_reduced5k_baked"), ("crate", "stages_crate_p1_rebaked"), ("crate", "stages_crate_p2_rebaked"),
        ("crate", "crate_h31_default"), ("crate", "crate_h31_req20000"), ("crate", "crate_p1_tri_req20000"),
        ("crate", "crate_p2_tri_req20000_textured"), ("crate", "crate_p2_tri_req20000_smartuv"),
        ("orb", "stages_orb_chain"), ("orb", "stages_orb_chain_fast"), ("orb", "stages_orb_baked1024"), ("orb", "stages_orb_baked4096"),
        ("orb", "stages_orb_reduced20k_own_uvs"), ("orb", "stages_orb_reduced5k_baked"), ("orb", "stages_orb_p1_rebaked"),
        ("orb", "stages_orb_p2_rebaked"), ("orb", "orb_h31_default"), ("orb", "orb_h31_req20000"), ("orb", "orb_spiked_h31_req20000"),
        ("orb", "orb_p1_tri_req20000_textured"), ("orb", "orb_p2_tri_req20000_textured")]
def load(p):
    try: return json.load(open(p))
    except (OSError, ValueError): return None
out = []
for subject, name in ROWS:
    m = load(f"{M}/{name}/measure.json"); d = load(f"{M}/{name}/defects.json")
    if not m or not d: continue
    w = d["welded"]; u = m.get("uvs") or {}; td = m.get("texel_density") or {}
    areas = load(f"runs/areas_{name}.json")
    if areas is None:
        path = m["file"]["path"]
        areas = json.loads(subprocess.run([sys.executable, "-I", "scripts/glb_facts.py", path], capture_output=True, text=True).stdout)
        json.dump({"triangle_areas": areas["triangle_areas"], "backward_normal_corners": areas["backward_normal_corners"]}, open(f"runs/areas_{name}.json", "w"))
    t = areas["triangle_areas"]
    use = {"baseColorTexture": "base colour", "metallicRoughnessTexture": "metallic-roughness", "normalTexture": "normal"}
    maps = "; ".join(f"{use.get(x['used_as'][0].split(' ')[0], '?') if x['used_as'] else 'unused'} {x['width']} {x['format']} {x['bytes'] / 1e6:.2f} MB" for x in m["textures"])
    out.append({"subject": subject, "model": name, "triangles": m["totals"]["triangles"], "vertices_stored": m["totals"]["vertices"],
                "file_mb": round(m["file"]["bytes"] / 1e6, 2), "maps": maps or "none", "uv_islands": u.get("islands", ""),
                "uv_seam_share": round(u["seam_share"], 3) if u else "", "uv_coverage": round(u["coverage"], 3) if u else "",
                "texel_px_per_m": round(td["pixels_per_metre"]) if td.get("pixels_per_metre") else "",
                "open_edges": w["boundary_edges"], "non_manifold_edges": w["non_manifold_edges"], "zero_area_faces": w["degenerate_faces"],
                "pieces": w["pieces"], "validator_errors": m["validator"]["errors"], "validator_warnings": m["validator"]["warnings"],
                "share_holding_99pc_area": round(t["share_holding_99pc_of_area"], 3), "sliver_share": round(t["share_under_100th_of_mean"], 3),
                "largest_dimension": round(m["bounding_box"]["largest_dimension"], 4), "lowest_point": round(m["bounding_box"]["min"][1], 5),
                "under_budget_20000": m["totals"]["triangles"] <= 20000 and m["validator"]["errors"] == 0})
w = csv.DictWriter(sys.stdout, list(out[0])); w.writeheader(); w.writerows(out)
