#!/usr/bin/env bash
# Stage 6: the whole chain on one dense model, from the raw output to a finished model.
#
#   scripts/chain.sh <subject: crate|orb> <tag> [texture size, default 2048] [triangles, default 20000] [uv: keep (default) | smart]
#
# Run from learn/research/blender-stages-trial/. Five stage scripts, each reading the one
# before it; the bake also reads the raw output, as a kiln stage could from the asset record:
#   1 repair        weld and dissolve at a hundredth of a millimetre, drop loose bits and pieces
#                   hidden inside, turn inside-out faces. The stored normals are kept: the next
#                   stage needs them only to survive the import
#   2 reduce        weld at a millionth of a metre, then Decimate, Collapse, one pass, to the
#                   triangle count
#   3 uv_bake       weld; UVs: "keep" lays the reduced mesh's own islands out again (Average
#                   Islands Scale, Pack Islands, a margin of a thousandth of the square), "smart"
#                   makes new ones with Smart UV Project at 66 degrees; smooth normals; bake the
#                   raw output's three maps (GPU, 1 sample, cage worked out from the two meshes)
#   4 scale_to_size kiln's own stage, to 0.8 m
#   5 place         turn 180 degrees about the up axis, origin at the bottom centre
# Outputs are models/chain_<subject>_<tag>_<n>_<stage>.glb; the last one is the finished model.
# runs/chain_<subject>_<tag>.json lists each stage's seconds, peak memory and SHA-256.
set -uo pipefail
s="$1"; tag="$2"; size="${3:-2048}"; target="${4:-20000}"; uv="${5:-keep}"
if [ "$uv" = keep ]; then uvs="uv=keep pack=concave margin_method=ADD pack_margin=0.001"; else uvs="uv=smart angle=66 island_margin=0.003"; fi
raw=$(realpath ../tripo-api-trial/models/${s}_h31_default.glb)
p=chain_${s}_${tag}; margin=$((size / 256))
export TRIAL_NO_COMPARE=1 TRIAL_NO_MEASURE=1
started=$(date +%s.%N)
scripts/run_stage.sh ${p}_1_repair repair.py "$raw" weld=1e-5 degenerate=1e-5 loose=true hidden_pieces=true recalc_normals=true normals=keep count=false || exit 1
# weld=0.000001: a file Blender wrote stores a point again wherever two faces meet at a hard
# edge, and the importer does not join those. Without the weld Collapse tears the crate along
# every hard edge (10,194 open edges in the trial's first chain).
scripts/run_stage.sh ${p}_2_reduce reduce.py models/${p}_1_repair.glb target=$target weld=0.000001 count_before=false || exit 1
# CHAIN_ONE_THREAD=1 runs the bake stage's Blender with one thread and on the CPU: slower, and
# the only way found to get the normal map out as the same bytes every time.
[ -n "${CHAIN_ONE_THREAD:-}" ] && export KILN_BLENDER_THREADS=1 && uvs="$uvs device=CPU"
scripts/run_stage.sh ${p}_3_uv_bake uv_bake.py models/${p}_2_reduce.glb high="$raw" size=$size margin=$margin cage=auto $uvs || exit 1
unset KILN_BLENDER_THREADS
scripts/run_scale.sh ${p}_4_scale models/${p}_3_uv_bake.glb 0.8 || exit 1
unset TRIAL_NO_MEASURE
scripts/run_stage.sh ${p}_5_place place.py models/${p}_4_scale.glb turn=180 origin=bottom_centre || exit 1
ended=$(date +%s.%N)
python3 - "$p" "$started" "$ended" <<'PY'
import hashlib, json, sys
p, started, ended = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
stages = []
for n in ("1_repair", "2_reduce", "3_uv_bake", "4_scale", "5_place"):
    run = json.load(open(f"runs/{p}_{n}.run.json"))
    data = open(f"models/{p}_{n}.glb", "rb").read()
    stages.append({"stage": n, "seconds": run["wall_seconds"], "peak_rss_mb": run["peak_rss_mb"],
                   "exit": run["exit_status"], "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
out = {"chain": p, "wall_seconds_with_measuring": round(ended - started, 1),
       "stage_seconds": round(sum(x["seconds"] for x in stages), 1),
       "peak_rss_mb": max(x["peak_rss_mb"] for x in stages), "stages": stages}
json.dump(out, open(f"runs/{p}.json", "w"), indent=1)
print(f"CHAIN {p}: {out['stage_seconds']} s in stages, {out['wall_seconds_with_measuring']} s in all, peak {out['peak_rss_mb']:.0f} MB")
for x in stages: print(f"  {x['stage']:10} {x['seconds']:7.1f} s  {x['bytes']:>10,} bytes  {x['sha256'][:16]}")
PY
