#!/usr/bin/env bash
# One asset drawn from a run of seeds, painted and seen under Bevy from one view, as one sheet to
# choose from: a tile per seed, labelled with it. A seed that does not build has no tile and is
# named on the last line. Each seed is built as a copy of the asset under a name of its own, so
# the asset's own outputs are not touched. An aid for a look decision, not a gate: nothing is checked.
# Written 8 bits deep and opaque (tools/image_lint.py).
# Usage: [KILN_SHEET_VIEW='--stand 3'] [KILN_JOBS=4] tools/candidates_sheet.sh <out.png> <asset> <first seed> <last seed>
set -euo pipefail
cd "$(dirname "$0")/.."
out="$1"; asset="$2"; first="$3"; last="$4"
view="${KILN_SHEET_VIEW:-standard}"
tmp="$(mktemp -d)"; run="zz_cand_$$"
trap 'rm -rf "$tmp" source/${run}_* assets/models/${run}_*' EXIT
cargo build -q -p asset_view
bin="${CARGO_TARGET_DIR:-target}/debug/asset_view"

one() { # <seed>: build, paint, export and photograph the asset drawn from that seed
  local seed="$1" name="${run}_$1" flags=()
  mkdir "source/$name"
  cp "source/$asset/build.py" "source/$name/build.py"
  python -c "
import json, sys
s = json.load(open('source/$asset/spec.json'))
s['asset'] = '$name'; s['objects'] = ['$name']; s['seed'] = $seed
s.pop('variants', None); s.pop('palette_of', None)
json.dump(s, open('source/$name/spec.json', 'w'))"
  [[ $view == standard ]] || read -ra flags <<< "$view"
  tools/bl tools/build.py "$name" > "$tmp/$seed.log" 2>&1 \
    && tools/bl tools/export.py "$name" >> "$tmp/$seed.log" 2>&1 \
    && "$bin" "assets/models/$name.glb" "assets/models/$name.manifest.json" "${flags[@]}" --screenshot "$tmp/$seed.png" >> "$tmp/$seed.log" 2>&1 \
    || true
}
export -f one; export asset run tmp view bin
seq "$first" "$last" | xargs -P "${KILN_JOBS:-4}" -I{} bash -c 'one {}'

tiles=(); missing=()
for seed in $(seq "$first" "$last"); do
  if [[ -s $tmp/$seed.png ]]; then tiles+=(-label "$asset, seed $seed" "$tmp/$seed.png"); else missing+=("$seed"); fi
done
[[ ${#tiles[@]} -gt 0 ]] || { echo "no seed from $first to $last built: see the last lines of one log"; tail -5 "$tmp/$first.log"; exit 1; }
count=$((${#tiles[@]} / 3)); columns=4; if [[ $count -le 6 ]]; then columns=3; fi
magick montage -background '#202124' -fill white -pointsize 18 "${tiles[@]}" -tile "${columns}x" -geometry 640x640+4+4 -depth 8 -alpha off "PNG24:$out"
python tools/image_lint.py "$out"
echo "$out: $count of $((last - first + 1)) seeds, view '$view'${missing[*]:+; no picture for seeds ${missing[*]}}"
