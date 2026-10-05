#!/usr/bin/env bash
# Build one asset and run every gate, cheapest first. Stops at the first failure.
# Usage: tools/gate.sh <asset> [review phase]
set -euo pipefail
cd "$(dirname "$0")/.."
asset="$1"; phase="${2:-final}"
glb="assets/models/$asset.glb"
reports="source/$asset/out/reports"

step() { printf '\n== %s\n' "$1"; }

step "L0  spec lint";            python tools/lint_spec.py "$asset"
step "    build";                tools/bl tools/build.py "$asset"
step "L1  mesh checks";          tools/bl tools/validate.py "$asset"
step "    export";               tools/bl tools/export.py "$asset"
step "L2  glTF validator";       .tools/gltf_validator -a -o "$glb" > "$reports/L2-gltf.json"
step "L2b Bevy profile lint";    python tools/bevy_lint.py "$glb"
step "L4  Bevy load test";       cargo run -q -p asset_smoke -- "$glb" "assets/models/$asset.manifest.json" \
                                   --report "$reports/L4-bevy.json" > /dev/null
step "L4b Bevy screenshot";      mkdir -p "source/$asset/review/$phase"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" \
                                   --screenshot "source/$asset/review/$phase/bevy.png" 2> "$reports/L4b-bevy-view.log"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --back \
                                   --screenshot "source/$asset/review/$phase/bevy_back.png" 2>> "$reports/L4b-bevy-view.log"
if grep -q '"skeleton"' "source/$asset/spec.json"; then
  # A tree is mostly seen from under it and from against its trunk: a player's eye 1 m from the
  # trunk looking up into the canopy, and 0.5 m from it looking straight at the bark.
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --stand 1 --pitch 78 \
                                   --screenshot "source/$asset/review/$phase/bevy_under.png" 2>> "$reports/L4b-bevy-view.log"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --stand 0.5 --pitch 0 \
                                   --screenshot "source/$asset/review/$phase/bevy_trunk.png" 2>> "$reports/L4b-bevy-view.log"
step "L4c bark seen from 0.5 m"; tools/bl tools/view_checks.py "$asset" "source/$asset/review/$phase/bevy_trunk.png"
fi
step "L5  review renders";       tools/bl tools/review_render.py "$asset" "$phase"
step "L5c review image";         python tools/image_lint.py "source/$asset/review/$phase/sheet.png"
step "L5b approval baseline";    python tools/baseline.py check "$asset" "$phase"

printf '\nall gates passed: %s\nnow look at source/%s/review/%s/sheet.png\n' "$asset" "$asset" "$phase"
