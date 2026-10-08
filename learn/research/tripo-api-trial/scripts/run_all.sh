#!/usr/bin/env bash
# The trial's paid requests, in the order they are worth running. Run from
# learn/research/tripo-api-trial/. Each line stops the script if its guard refuses or writes STOP.
# Total 290 credits; TRIAL_LIMIT (default 300) is enforced by run_request.sh for requests 1 to 5.
# Requests 6a and 6b go round the CLI and are guarded here by hand.
set -euo pipefail
common="-p texture=true -p pbr=true -p texture_quality=standard -p texture_seed=1 --seed 1"
run=scripts/run_request.sh
# 1. P2 at the pit profile's triangle budget: the videos' central claim.            110 -> 110
$run r1_p2_three_quarter 110 make images/crate_three_quarter.png --model tripo-p2 -p face_limit=20000 $common
# 2. H series v3.1 on its defaults: the dense model the videos say not to start from. 30 -> 140
$run r2_h31_three_quarter 30 make images/crate_three_quarter.png --model tripo-v3.1 $common
# 3. P1 at the same budget: does the cheaper P model do what P2 is credited with?     50 -> 190
$run r3_p1_three_quarter 50 make images/crate_three_quarter.png --model tripo-p1 -p face_limit=20000 $common
# 4. Request 3 again, unchanged: does the same seed give the same file?               50 -> 240
$run r4_p1_three_quarter_repeat 50 make images/crate_three_quarter.png --model tripo-p1 -p face_limit=20000 $common
# 5. H series v3.1 from the strict front picture, against request 2.                  30 -> 270
$run r5_h31_front 30 make images/crate_front.png --model tripo-v3.1 $common
# 6. Request 2's shape textured again from the hard-light picture, delight on and off. 20 -> 290
task=$(python3 -c 'import json; print(json.load(open("requests/r2_h31_three_quarter.result.json"))["task_id"])')
for setting in true false; do
  before=$(tripo balance --json | python3 -c 'import json,sys; print(float(json.load(sys.stdin)["balance"]))')
  python3 -c "import sys; sys.exit(0 if $before >= 10 else 1)" || { echo "balance $before: stopping before 6 ($setting)"; exit 4; }
  scripts/retexture_v35.sh "r6_retexture_delight_$setting" "$task" images/crate_three_quarter_hard_light.png "$setting"
  after=$(tripo balance --json | python3 -c 'import json,sys; print(float(json.load(sys.stdin)["balance"]))')
  echo "r6_retexture_delight_$setting,,,$before,$after,$(python3 -c "print($before - $after)"),10,," >> ledger.csv
  python3 -c "import sys; sys.exit(0 if abs(($before - $after) - 10) < 0.005 else 1)" || { echo "unexpected charge on 6 ($setting)" | tee STOP; exit 1; }
done
# Then, at no cost:
#   for each models/<name>/*.glb:  scripts/measure_model.sh <name> <file> 0.8
#   ../../../tools/bl scripts/reduce_in_blender.py models/r2_h31_three_quarter/<file>.glb models/r2_reduced_20000.glb 20000
#   scripts/measure_model.sh r2_reduced_20000 models/r2_reduced_20000.glb 0.8
#   python3 -I scripts/compare_models.py models/r3_p1_three_quarter/<file>.glb models/r4_p1_three_quarter_repeat/<file>.glb
#   ../../../tools/bl scripts/texture_stats.py models/r6_retexture_delight_true/<file>.glb measurements/r6_retexture_delight_true/textures   (and _false)
