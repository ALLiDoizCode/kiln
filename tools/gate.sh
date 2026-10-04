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
step "L5  review renders";       tools/bl tools/review_render.py "$asset" "$phase"

printf '\nall gates passed: %s\nnow look at source/%s/review/%s/sheet.png\n' "$asset" "$asset" "$phase"
