#!/usr/bin/env bash
# Stage 4: new UVs and the bake of the dense model's three maps onto the reduced mesh, every
# setting the trial tried. Run from learn/research/blender-stages-trial/ after the reductions.
#   scripts/run_bake_matrix.sh [crate|orb ...]
# Each run's review pictures go to work/pics/<run>/ (ignored by git).
set -uo pipefail
export TRIAL_NO_COMPARE=1
M=$(realpath ../tripo-api-trial/models)
for s in "${@:-crate orb}"; do for s in $s; do
  low=models/red_${s}__collapse20k_r1.glb; high=$M/${s}_h31_default.glb
  b() { n=$1; shift; echo "== $s $n $(date +%T)"; timeout 3600 scripts/run_stage.sh bake_${s}__$n uv_bake.py ${LOW:-$low} high=$high "$@" | tail -1
        [ -f models/bake_${s}__$n.glb ] && scripts/pictures.sh bake_${s}__$n models/bake_${s}__$n.glb; }
  b 1024 size=1024 margin=4; b 2048 size=2048 margin=8; b 4096 size=4096 margin=16
  b 2048_again size=2048 margin=8
  b 2048_cpu size=2048 margin=8 device=CPU; b 2048_cpu_again size=2048 margin=8 device=CPU
  b 4096_cpu size=4096 margin=16 device=CPU
  b 2048_s16 size=2048 margin=8 samples=16
  b 2048_cage1mm size=2048 margin=8 cage_extrusion=0.001 max_ray_distance=0.002
  b 2048_cage5mm size=2048 margin=8 cage_extrusion=0.005 max_ray_distance=0.01
  b 2048_cage50mm size=2048 margin=8 cage_extrusion=0.05 max_ray_distance=0.1
  b 2048_cage20mm_nolimit size=2048 margin=8 cage_extrusion=0.02 max_ray_distance=0
  b 2048_cage0 size=2048 margin=8 cage_extrusion=0 max_ray_distance=0
  b 2048_margin0 size=2048 margin=0; b 2048_margin2 size=2048 margin=2; b 2048_margin32 size=2048 margin=32
  b 2048_extend size=2048 margin=8 margin_type=EXTEND
  b 2048_diffuse size=2048 margin=8 colour=diffuse
  b 2048_sharp30 size=2048 margin=8 sharp_angle=30
  b 2048_png size=2048 margin=8 jpeg=false
  b 2048_noweld size=2048 margin=8 weld=0
  b 2048_keepuv size=2048 margin=8 uv=keep
  b 2048_smart30 size=2048 margin=8 angle=30
  b 2048_smart66_concave size=2048 margin=8 pack=concave
  b 2048_sharp60 size=2048 margin=8 uv=sharp_unwrap seam_angle=60 pack=concave
  LOW=models/red_${s}__collapse5k_r1.glb b 5k_2048 size=2048 margin=8
  LOW=models/red_${s}__collapse5k_r1.glb b 5k_1024 size=1024 margin=4
done; done
echo "== done $(date +%T)"
