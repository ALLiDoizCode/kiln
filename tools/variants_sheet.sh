#!/usr/bin/env bash
# Variants of one family beside a benchmark, all under Bevy from the same cameras, one row each:
# the standard view, from the back, a player standing 3 m away, standing 0.5 m away, and looking
# up from 1 m beside the trunk. Written 8 bits deep and opaque, and checked (tools/image_lint.py).
# With --low, for plants below a player's eye, which have no view from below: the last view is
# the player standing 1 m away and looking down at the plant.
# Usage: [KILN_SHEET_VIEWS='standard;--back;--stand 3;--stand 0.5;--close'] tools/variants_sheet.sh [--low] <out.png> <benchmark.gltf> <benchmark.manifest.json> <asset> [asset...]
set -euo pipefail
cd "$(dirname "$0")/.."
last="--stand 1 --pitch 78"
if [[ ${1:-} == --low ]]; then last="--stand 1"; shift; fi
out="$1"; benchmark="$2"; benchmark_manifest="$3"; shift 3
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
tiles=()
# KILN_SHEET_VIEWS: the views of a row, separated by semicolons, when the default five do not suit:
# nothing of a low rock is in the picture looking up from beside it, and the viewer then saves none.
IFS=';' read -ra views <<< "${KILN_SHEET_VIEWS:-standard;--back;--stand 3;--stand 0.5;$last}"
row() { # <label> <model> <manifest>
  local n=0
  for view in "${views[@]}"; do
    n=$((n + 1)); flags=(); [[ $view == standard ]] || read -ra flags <<< "$view"
    cargo run -q -p asset_view -- "$2" "$3" "${flags[@]}" --screenshot "$tmp/$1_$n.png" 2> /dev/null
    label="$view"; [[ $view == "--stand 1 --pitch 78" ]] && label="from below (--stand 1 --pitch 78)"
    tiles+=(-label "$1, $label" "$tmp/$1_$n.png")
  done
}
for asset in "$@"; do row "$asset" "assets/models/$asset.glb" "assets/models/$asset.manifest.json"; done
row "$(basename "$benchmark" .gltf) (benchmark)" "$benchmark" "$benchmark_manifest"
magick montage -background '#202124' -fill white -pointsize 18 "${tiles[@]}" -tile "${#views[@]}x" -geometry 640x640+4+4 -depth 8 -alpha off "PNG24:$out"
python tools/image_lint.py "$out"
