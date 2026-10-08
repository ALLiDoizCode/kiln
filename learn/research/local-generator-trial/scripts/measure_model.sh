#!/usr/bin/env bash
# Measure one model file every way the trial uses, and take its pictures.
#
#   scripts/measure_model.sh <name> <model.glb> [size in metres, default 0.8]
#
# Run from learn/research/tripo-api-trial/, with the kiln repo three folders up. Writes into
# measurements/<name>/: sha256.txt, measure.json and measure.txt (python3 -m kiln.measure),
# inspect.txt (learn/assets/glb_inspect.py), defects.json (scripts/mesh_defects.py in the pinned
# Blender), wire/ (scripts/render_untextured.py) and review/ (target/release/review_pictures, the
# same eight views a shape review uses, at the pit profile's closest viewing distance of 0.5 m).
# Nothing is written beside the model and the model is only read. Python runs with -I because a
# downloaded file is untrusted data.
set -uo pipefail
name="$1"; model="$(realpath "$2")"; size="${3:-0.8}"
here="$(pwd)"; repo="$(cd "$(dirname "$0")/../../../.." && pwd)"
out="$here/measurements/$name"; mkdir -p "$out/wire" "$out/review"
sha256sum "$model" | cut -d' ' -f1 > "$out/sha256.txt"
stat -c %s "$model" > "$out/bytes.txt"
case "$model" in
  *.glb)
    (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$model" --size "$size" --json) > "$out/measure.json" 2> "$out/measure.stderr.txt"
    (cd "$repo" && python3 -I -c 'import sys; sys.path.insert(0, "."); from kiln.measure import main; sys.exit(main(sys.argv[1:]))' "$model" --size "$size") > "$out/measure.txt" 2>> "$out/measure.stderr.txt"
    (cd "$repo" && python3 -I -c 'import sys, runpy; sys.path.insert(0, "."); sys.argv = ["glb_inspect.py", sys.argv[1]]; runpy.run_path("learn/assets/glb_inspect.py", run_name="__main__")' "$model") > "$out/inspect.txt" 2>&1
    if [ -x "$repo/target/release/review_pictures" ]; then
      "$repo/target/release/review_pictures" "$model" --size "$size" --closest 0.5 --out "$out/review" > "$out/review/views.json" 2> "$out/review/renderer.log" || echo "review pictures failed" >&2
    else echo "review_pictures is not built: no review pictures" >&2; fi ;;
esac
"$repo/tools/bl" "$here/scripts/mesh_defects.py" "$model" "$out/defects.json" > "$out/defects.log" 2>&1 || echo "mesh_defects failed" >&2
"$repo/tools/bl" "$here/scripts/render_untextured.py" "$model" "$out/wire" 1600 > "$out/wire/render.log" 2>&1 || echo "wire render failed" >&2
echo "$name: $(cat "$out/sha256.txt")  ->  $out"
