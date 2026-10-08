#!/usr/bin/env bash
# Run one stage script of the trial on one model, timed, and measure what it wrote.
#
#   scripts/run_stage.sh <run name> <stage script> <in.glb> [name=value ...]
#
# Run from learn/research/blender-stages-trial/. Writes:
#   models/<run name>.glb            the stage's output (ignored by git)
#   runs/<run name>.facts.json       what the stage says it did
#   runs/<run name>.run.json         seconds, peak memory, exit status (scripts/timed.py)
#   runs/<run name>.log              Blender's output
#   runs/<run name>.glb.json         what the output file holds, against the input (scripts/glb_facts.py)
#   runs/<run name>.validator.txt    the Khronos validator's counts
#   runs/<run name>.measure.json     kiln's measurement at 0.8 m (python3 -m kiln.measure --json)
# TRIAL_NO_MEASURE=1 leaves kiln's measurement out. TRIAL_REFERENCE=<file.glb> compares against that file instead of the stage's input.
# TRIAL_NO_COMPARE=1 leaves the comparison out (it is slow on a dense model).
set -uo pipefail
name="$1"; script="$2"; source="$(realpath "$3")"; shift 3
here="$(pwd)"; repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
mkdir -p "$here/models" "$here/runs"
out="$here/models/$name.glb"; rm -f "$out" "$here/runs/$name.facts.json"
python3 "$here/scripts/timed.py" "$name" "$here/runs" -- \
  "$repo/tools/bl" "$here/scripts/$script" "$source" "$out" "$here/runs/$name.facts.json" "$@"
status=$?
if [ -f "$out" ]; then
  reference="${TRIAL_REFERENCE:-$source}"
  if [ -n "${TRIAL_NO_COMPARE:-}" ]; then reference=""; fi
  python3 -I "$here/scripts/glb_facts.py" "$out" $reference > "$here/runs/$name.glb.json" 2> "$here/runs/$name.glb.stderr.txt"
  (cd "$repo" && python3 -I -c 'import sys, json; sys.path.insert(0, "."); from kiln.measure import run_validator; v = run_validator(sys.argv[1]); print(json.dumps(v, indent=1))' "$out") > "$here/runs/$name.validator.txt" 2>&1
  if [ -z "${TRIAL_NO_MEASURE:-}" ]; then
    (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$out" --size 0.8 --json) > "$here/runs/$name.measure.json" 2>/dev/null
  fi
  [ -s "$here/runs/$name.glb.stderr.txt" ] || rm -f "$here/runs/$name.glb.stderr.txt"
else
  echo "$name: no model written (exit $status)"
fi
exit $status
