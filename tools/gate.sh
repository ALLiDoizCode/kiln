#!/usr/bin/env bash
# Build one asset and run every gate, cheapest first. Stops at the first failure.
# Usage: tools/gate.sh <asset> [review phase]
set -euo pipefail
cd "$(dirname "$0")/.."
asset="$1"; phase="${2:-final}"
# What is gated is baked on the CPU, whatever the caller's environment asks: only that bake gives
# the same texels every time (tools/paint.py), and a gated asset is what gets committed.
if [[ ${KILN_BAKE:-cpu} != cpu ]]; then echo "tools/gate.sh: ignoring KILN_BAKE=$KILN_BAKE; a gated asset is baked on the CPU"; fi
unset KILN_BAKE
glb="assets/models/$asset.glb"
reports="source/$asset/out/reports"

step() { printf '\n== %s\n' "$1"; }

step "L0  spec lint";            python tools/lint_spec.py "$asset"
step "    build";                tools/bl tools/build.py "$asset"
step "L1  mesh checks";          tools/bl tools/validate.py "$asset"
step "    export";               tools/bl tools/export.py "$asset"
step "L2  glTF validator";       .tools/gltf_validator -a -o "$glb" > "$reports/L2-gltf.json"
step "L2b Bevy profile lint";    python tools/bevy_lint.py "$glb"
base="$(python -c "import json,sys; print(json.load(open(sys.argv[1])).get('palette_of', ''))" "source/$asset/spec.json")"
if [[ -n $base ]]; then
  # A palette variant (a season): its base's mesh with another texture. The base's gate comes first.
step "L2c same mesh as $base";   python tools/same_mesh.py "$glb" "assets/models/$base.glb" --report "$reports/L2c-same-mesh.json"
fi
step "L4  Bevy load test";       cargo run -q -p asset_smoke -- "$glb" "assets/models/$asset.manifest.json" \
                                   --report "$reports/L4-bevy.json" > /dev/null
step "L4b Bevy screenshot";      mkdir -p "source/$asset/review/$phase"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" \
                                   --screenshot "source/$asset/review/$phase/bevy.png" 2> "$reports/L4b-bevy-view.log"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --back \
                                   --screenshot "source/$asset/review/$phase/bevy_back.png" 2>> "$reports/L4b-bevy-view.log"
if grep -q '"painted_shading"' "source/$asset/spec.json" && ! grep -q '"foliage"' "source/$asset/spec.json"; then
  # A painted solid (a rock): the sides the sun does not reach, seen close from the back, where
  # only the viewer's ambient light and the paint decide whether anything can be read.
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --back --close \
                                   --screenshot "source/$asset/out/bevy_shade.png" --shade "source/$asset/out/bevy_shade.json" 2>> "$reports/L4b-bevy-view.log"
step "L4d shaded sides";         python tools/shade_check.py "$asset" "source/$asset/out/bevy_shade.json" --report "$reports/L4d-shade.json"
fi
if grep -q '"skeleton"' "source/$asset/spec.json"; then
  # A tree is mostly seen from under it and from against its trunk: a player's eye 1 m from the
  # trunk looking up into the canopy, and 0.5 m from it looking straight at the bark.
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --stand 1 --pitch 78 \
                                   --screenshot "source/$asset/review/$phase/bevy_under.png" 2>> "$reports/L4b-bevy-view.log"
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --stand 0.5 --pitch 0 \
                                   --screenshot "source/$asset/review/$phase/bevy_trunk.png" 2>> "$reports/L4b-bevy-view.log"
step "L4c bark seen from 0.5 m"; tools/bl tools/view_checks.py "$asset" "source/$asset/review/$phase/bevy_trunk.png"
step "L4e canopy seen from below"; tools/bl tools/under_checks.py "$asset" "source/$asset/review/$phase/bevy_under.png"
fi
stood_under="$(python -c "import json,sys,tomllib; t=json.load(open(sys.argv[1])).get('table'); print('yes' if t and t['min_clear_m'] >= tomllib.load(open('conventions.toml','rb'))['metrics']['player_height_m'] else '')" "source/$asset/spec.json")"
if [[ -n $stood_under ]]; then
  # A table rock a player can stand under is also seen from there: the eye 1 m from the origin, looking up past the neck at the underside of the cap and its rim (straight up, 0.3 m from the eye, the underside fills the picture with one tone).
                                 cargo run -q -p asset_view -- "$glb" "assets/models/$asset.manifest.json" --stand 1 --pitch 35 \
                                   --screenshot "source/$asset/review/$phase/bevy_under.png" 2>> "$reports/L4b-bevy-view.log"
fi
step "L5  review renders";       tools/bl tools/review_render.py "$asset" "$phase"
step "L5c review image";         python tools/image_lint.py "source/$asset/review/$phase/sheet.png"
step "L5b approval baseline";    python tools/baseline.py check "$asset" "$phase"

printf '\nall gates passed: %s\nnow look at source/%s/review/%s/sheet.png\n' "$asset" "$asset" "$phase"
