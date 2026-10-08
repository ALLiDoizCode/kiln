#!/usr/bin/env bash
# Runs prototypes A to D of learn/research/fur-animation-trial.md again, from the repo root or
# anywhere: reads the Tripo models in ../tripo-api-trial/models/ and writes models/, pictures/,
# facts/ and logs/ here. Needs .tools/ (tools/install_tools.sh) and the probe built:
#   (cd bevy_probe && CARGO_TARGET_DIR=../../../../target cargo build --release)
# Prototype E (the skeleton) is scripts/run_skeleton.sh.
set -uo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"; repo="$(cd "$here/../../.." && pwd)"
in="$repo/learn/research/tripo-api-trial/models"; bl="$repo/tools/bl"; probe="$repo/target/release/morph_probe"
cd "$here"; mkdir -p models pictures facts logs work

# A: one fused surface.
"$bl" scripts/a_morph_fused.py "$in/orb_h31_req20000.glb" "$here/models/a_fused_morph.glb" facts/a_fused_morph.json \
  mask="$here/work/a_fused_mask.glb" > logs/a_fused.log 2>&1 || echo "A failed, see logs/a_fused.log"
# A, the other detection method, for the comparison of masks only.
for v in "laplace 10" "laplace 30" "taubin 100"; do set -- $v
  "$bl" scripts/a_morph_fused.py "$in/orb_h31_req20000.glb" "$here/work/a_outside_$1_$2.glb" "facts/a_outside_$1_$2.json" \
    detect=outside smooth="$1" iterations="$2" mask="$here/work/a_outside_$1_$2_mask.glb" > "logs/a_outside_$1_$2.log" 2>&1
  "$probe" "work/a_outside_$1_$2_mask.glb" --out "pictures/a_mask_outside_$1_$2" --views side,top,three_quarter --distance 2.4 > /dev/null 2>&1
done
"$probe" work/a_fused_mask.glb --out pictures/a_mask_thin --views side,top,three_quarter --distance 2.4 > /dev/null 2>&1
# Targets: 0 soft_all, 1 soft_masked, 2 spiked_push, 3 spiked_axial.
"$probe" models/a_fused_morph.glb --out pictures/a_fused --views three_quarter,side,back_quarter --distance 2.7 \
  --frames "0;1;0,1;0,0,0.5;0,0,1;0,0,0,0.25;0,0,0,0.5;0,0,0,0.75;0,0,0,1;0,0,0,2" > /dev/null 2> logs/probe_a_fused.log

# B: loose pieces. Targets: 0 retracted, 1 extended, 2 tail_only.
for m in p1 p2; do
  "$bl" scripts/b_morph_pieces.py "$in/orb_${m}_tri_req20000_textured.glb" "$here/models/b_pieces_${m}_morph.glb" \
    "facts/b_pieces_$m.json" "facts/b_pieces_$m.csv" mask="$here/work/b_${m}_mask.glb" > "logs/b_$m.log" 2>&1 || echo "B $m failed"
  "$probe" "work/b_${m}_mask.glb" --out "pictures/b_mask_$m" --views side,top,three_quarter --distance 2.4 > /dev/null 2>&1
  "$probe" "models/b_pieces_${m}_morph.glb" --out "pictures/b_pieces_$m" --views three_quarter,back_quarter,side --distance 2.7 \
    --frames "0;1;0.5;0,0.25;0,0.5;0,0.75;0,1;0,2" > /dev/null 2> "logs/probe_b_$m.log"
done

# C: the same models with fewer and more attributes morphed, and one with a clip; read back.
"$bl" scripts/c_export_variants.py "$here/models/a_fused_morph.glb" "$here/models/c_variants" a_fused > logs/c_a.log 2>&1
"$bl" scripts/c_export_variants.py "$here/models/b_pieces_p1_morph.glb" "$here/models/c_variants" b_pieces_p1 > logs/c_b.log 2>&1
python3 -I scripts/c_read_back.py "$repo" "$in/orb_h31_req20000.glb" "$in/orb_p1_tri_req20000_textured.glb" \
  models/a_fused_morph.glb models/b_pieces_p1_morph.glb models/b_pieces_p2_morph.glb models/c_variants/*.glb > facts/c_read_back.jsonl
: > facts/c_validator.txt
for f in models/a_fused_morph.glb models/b_pieces_p1_morph.glb models/b_pieces_p2_morph.glb models/c_variants/a_fused_anim.glb models/c_variants/a_fused_pos_nrm_tan.glb; do
  n="$(basename "$f" .glb)"
  (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$here/$f" --size 0.8 --json) \
    > "facts/c_measure_$n.json" 2> "logs/c_measure_$n.stderr.txt"; echo "$n: kiln.measure exit $?" >> facts/c_validator.txt
done

# D: Bevy plays the clip the exporter wrote (a glTF animation of the node's weights).
"$probe" models/c_variants/a_fused_anim.glb --out pictures/d_clip --views three_quarter --distance 2.7 --clip 0 --times 0,0.5,1.0,1.5 \
  > /dev/null 2> logs/probe_d_clip.log
