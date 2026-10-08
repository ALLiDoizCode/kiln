#!/usr/bin/env bash
# Stage 5: run kiln's own scale_to_size stage function on a model, timed, and measure the result.
#
#   scripts/run_scale.sh <run name> <in.glb> [size in metres, default 0.8]
#
# The stage is called as kiln's build() calls it - kiln.run.scale_to_size(source, work, record,
# profile) - with a work folder under work/, never the store in assets/.
set -uo pipefail
name="$1"; source="$(realpath "$2")"; size="${3:-0.8}"
here="$(pwd)"; repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
work="$here/work/scale_$name"; rm -rf "$work"; mkdir -p "$work" "$here/runs" "$here/models"
out="$here/models/$name.glb"; rm -f "$out"
(cd "$repo" && python3 "$here/scripts/timed.py" "$name" "$here/runs" -- python3 -c '
import json, shutil, sys
sys.path.insert(0, ".")
from kiln.run import scale_to_size
from kiln.profile import load_profile
source, work, size, out, facts = sys.argv[1:6]
model, stage_facts = scale_to_size(source, work, {"size": float(size)}, load_profile("pit"))
shutil.copyfile(model, out)
json.dump({"stage": "scale_to_size", "source": source, "settings": {"size": float(size)}, **stage_facts,
           "script_result": json.load(open(work + "/scale_to_size.json"))}, open(facts, "w"), indent=1)
' "$source" "$work" "$size" "$out" "$here/runs/$name.facts.json")
status=$?
if [ -f "$out" ]; then
  python3 -I "$here/scripts/glb_facts.py" "$out" > "$here/runs/$name.glb.json"
  (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$out" --size "$size" --json) > "$here/runs/$name.measure.json" 2>/dev/null
fi
exit $status
