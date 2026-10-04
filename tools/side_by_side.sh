#!/usr/bin/env bash
# An asset beside a benchmark, both under Bevy from the same cameras: the standard view,
# close up, and from the back. Written 8 bits deep and opaque, and checked, so that no
# viewer bands it (tools/image_lint.py).
# Usage: tools/side_by_side.sh <asset> <benchmark.gltf> <benchmark.manifest.json> <out.png>
set -euo pipefail
cd "$(dirname "$0")/.."
asset="$1"; benchmark="$2"; benchmark_manifest="$3"; out="$4"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
tiles=()
for view in standard close back; do
  flag=(); [[ $view == close ]] && flag=(--close); [[ $view == back ]] && flag=(--back)
  cargo run -q -p asset_view -- "assets/models/$asset.glb" "assets/models/$asset.manifest.json" "${flag[@]}" --screenshot "$tmp/ours_$view.png" 2> /dev/null
  cargo run -q -p asset_view -- "$benchmark" "$benchmark_manifest" "${flag[@]}" --screenshot "$tmp/theirs_$view.png" 2> /dev/null
  tiles+=(-label "$asset, $view" "$tmp/ours_$view.png" -label "$(basename "$benchmark" .gltf), $view" "$tmp/theirs_$view.png")
done
magick montage -background '#202124' -fill white -pointsize 18 "${tiles[@]}" -tile 2x -geometry 704x704+4+4 -depth 8 -alpha off "PNG24:$out"
python tools/image_lint.py "$out"
