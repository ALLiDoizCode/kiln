#!/usr/bin/env bash
# Compare the review pictures of every run in work/pics/ with those of the dense model it came
# from, and write picture_diff.csv. Run from learn/research/blender-stages-trial/.
set -uo pipefail
repo="$(cd "$(dirname "$0")/../../../.." && pwd)"; ref=../tripo-api-trial/measurements
pairs=(); names=()
for d in work/pics/*/; do
  n=$(basename "$d"); case "$n" in *crate*) s=crate;; *orb*) s=orb;; *) continue;; esac
  for v in three_quarter closest front back top; do
    [ -f "$d/$v.png" ] && pairs+=("$(realpath "$d/$v.png")" "$(realpath "$ref/${s}_h31_default/review/$v.png")") && names+=("$n,$v")
  done
done
"$repo/tools/bl" "$(pwd)/scripts/picture_diff.py" "${pairs[@]}" 2>/dev/null | grep '^DIFF ' > work/picture_diff.raw
python3 - "${names[@]}" <<'PY' > picture_diff.csv
import json, sys
print("run,view,mean_abs_difference,share_over_8,share_over_32")
for name, line in zip(sys.argv[1:], open("work/picture_diff.raw")):
    d = json.loads(line[5:])
    if "error" in d: continue
    print(f"{name},{d['mean_abs_difference']},{d['share_over_8']},{d['share_over_32']}")
PY
