#!/usr/bin/env bash
# Runs prototypes E and F of learn/research/fur-animation-trial.md again. Needs scripts/run_all.sh
# to have run (it uses models/a_fused_morph.glb) and Tripo's files in ../tripo-api-trial/models/.
set -uo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"; repo="$(cd "$here/../../.." && pwd)"
in="$repo/learn/research/tripo-api-trial/models"; bl="$repo/tools/bl"; probe="$repo/target/release/morph_probe"
cd "$here"
fbx="$(find "$in/orb_h31_req20000_walk2_fbx" -name '*.fbx' | head -1)"

# E: what Tripo's three exports hold.
python3 -I scripts/c_read_back.py "$repo" "$in/orb_h31_req20000_rigged_walk.glb" "$in/orb_h31_req20000_walk2.glb" "$in/orb_spiked_h31_req20000.glb" > facts/e_f_read_back.jsonl
"$bl" scripts/e_inspect_rig.py "$in/orb_h31_req20000_rigged_walk.glb" facts/e_rigged_in_blender.json > logs/e_inspect.log 2>&1
"$bl" scripts/e_inspect_rig.py "$in/orb_h31_req20000_walk2.glb" facts/e_walk2_in_blender.json > logs/e_inspect_walk2.log 2>&1
"$bl" scripts/e_inspect_rig.py "$fbx" facts/e_walk2_fbx_in_blender.json > logs/e_inspect_fbx.log 2>&1
"$bl" scripts/e_posed_box.py "$in/orb_h31_req20000_rigged_walk.glb" 2>&1 | grep -E 'BOX|matrix' > facts/e_rigged_posed_box.txt
(cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$in/orb_h31_req20000_rigged_walk.glb" --size 0.8) > facts/e_measure_rigged.txt 2> logs/e_measure_rigged.stderr.txt
"$probe" "$in/orb_h31_req20000_rigged_walk.glb" --out pictures/e_tripo_rigged --views three_quarter,side --distance 2.7 > /dev/null 2> logs/probe_e_tripo_rigged.log

# E: Tripo's skeleton with Tripo's weights, then with Blender's; and a skeleton placed by script.
"$bl" scripts/e_tripo_rig.py "$fbx" "$here/models/a_fused_morph.glb" "$here/models/e_tripo" facts/e_tripo_rig.json > logs/e_tripo_rig.log 2>&1
"$bl" scripts/e_rig_by_script.py "$here/models/a_fused_morph.glb" "$here/models/e_rigged_by_script.glb" facts/e_rig_by_script.json > logs/e_rig.log 2>&1
"$probe" models/e_tripo/tripo_weights.glb --out pictures/e_tripo_weights --views three_quarter,side --distance 2.7 --clip 0 --times 0,0.5 > /dev/null 2> logs/probe_e_tripo_weights.log
"$probe" models/e_tripo/tripo_skeleton_auto_weights.glb --out pictures/e_auto_calm --views three_quarter,side --distance 2.7 --clip 0 --times 0,0.5 > /dev/null 2> logs/probe_e_auto.log
"$probe" models/e_tripo/tripo_skeleton_auto_weights.glb --out pictures/e_auto_spiked --views three_quarter,side --distance 2.7 --clip 0 --times 0,0.5 --frames "0,0,0,1" > /dev/null 2>&1
"$probe" models/e_rigged_by_script.glb --out pictures/e_own_rig --views three_quarter,side --distance 2.7 --clip 0 --times 0,0.5 --frames "0,0,0,1" > /dev/null 2> logs/probe_e_own.log
python3 -I scripts/c_read_back.py "$repo" models/e_tripo/*.glb models/e_rigged_by_script.glb > facts/e_read_back.jsonl
for f in models/e_tripo/tripo_skeleton_auto_weights.glb models/e_rigged_by_script.glb; do
  n="$(basename "$f" .glb)"
  (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$here/$f" --size 0.8 --json) > "facts/e_measure_$n.json" 2> "logs/e_measure_$n.stderr.txt"
done

# F: the calm and the spiked generation.
"$bl" scripts/f_compare.py facts/f_compare.json "$in/orb_h31_req20000.glb" "$in/orb_spiked_h31_req20000.glb" > logs/f_compare.log 2>&1
for m in calm:orb_h31_req20000 spiked:orb_spiked_h31_req20000; do
  "$probe" "$in/${m#*:}.glb" --out "pictures/f_${m%%:*}" --views three_quarter,side,back_quarter,top,front --distance 2.7 > /dev/null 2>&1
done
