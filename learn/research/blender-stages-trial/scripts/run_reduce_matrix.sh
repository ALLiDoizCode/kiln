#!/usr/bin/env bash
# Stage 3: every reduction of the two dense models that the trial tried, one after another.
# Run from learn/research/blender-stages-trial/. A run whose record is already in runs/ is
# skipped, so the script can be stopped and started again. Planar takes about a quarter of an
# hour on a dense model; the rest take under a minute each.
#   scripts/run_reduce_matrix.sh [crate|orb ...]
set -uo pipefail
M=../tripo-api-trial/models
export TRIAL_NO_COMPARE=1
for s in "${@:-crate orb}"; do for s in $s; do
  in=$M/${s}_h31_default.glb
  r() { n=$1; shift; [ -f runs/red_${s}__$n.run.json ] && return; echo "== $s $n $(date +%T)"; timeout 1800 scripts/run_stage.sh red_${s}__$n reduce.py $in count_before=false "$@" | tail -1; }
  # the main configuration, three times: does it crash, and is the file the same each time?
  r collapse20k_r1
  r collapse20k_r2; r collapse20k_r3
  r collapse5k_r1 target=5000; r collapse5k_r2 target=5000
  r collapse20k_steps3 steps=3; r collapse20k_steps6 steps=6
  r collapse20k_seams1 protect_seams=1; r collapse20k_seams10 protect_seams=10; r collapse20k_seams100 protect_seams=100
  r collapse5k_seams10 target=5000 protect_seams=10
  r collapse20k_nomerge merge_vertices=false
  r collapse20k_clear30 normals=clear
  r collapse20k_weld1e-4 weld=1e-4
  r collapse20k_seams0.01 protect_seams=0.01; r collapse20k_seams0.1 protect_seams=0.1
  r collapse20k_r4; r collapse20k_r5
  r unsubdiv2 method=unsubdiv unsubdiv_iterations=2
  r voxel4mm method=voxel voxel_size=0.004
  r voxel4mm_r2 method=voxel voxel_size=0.004
  r voxel2mm method=voxel voxel_size=0.002
  r planar5_uv method=planar planar_angle=5 planar_delimit=UV
  [ $s = crate ] && r planar5_none method=planar planar_angle=5 planar_delimit=none
  [ $s = crate ] && r planar1_uv method=planar planar_angle=1 planar_delimit=UV
  r quadriflow method=quadriflow
done; done
echo "== done $(date +%T)"
