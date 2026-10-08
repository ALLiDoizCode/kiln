#!/usr/bin/env bash
# Stage 4, UVs only: every unwrap setting the trial tried on the two reduced meshes, no baking.
# Run from learn/research/blender-stages-trial/ after the reductions exist.
set -uo pipefail
export TRIAL_NO_COMPARE=1
for s in "${@:-crate orb}"; do for s in $s; do for t in 20k 5k; do
  in=models/red_${s}__collapse${t}_r1.glb
  u() { n=$1; shift; scripts/run_stage.sh uv_${s}_${t}__$n uv_bake.py $in bake=false "$@" | tail -1; }
  for a in 20 30 45 66 80 89; do u smart${a} angle=$a; done
  u smart66_m0 island_margin=0; u smart66_m001 island_margin=0.001; u smart66_m01 island_margin=0.01; u smart66_m03 island_margin=0.03
  u smart66_concave pack=concave; u smart66_aabb pack=aabb
  u smart45_concave angle=45 pack=concave
  u sharp30 uv=sharp_unwrap seam_angle=30 pack=concave; u sharp60 uv=sharp_unwrap seam_angle=60 pack=concave
  u keep uv=keep
done; done; done
