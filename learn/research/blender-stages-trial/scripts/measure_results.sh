#!/usr/bin/env bash
# Measure the trial's main results with the Tripo trial's own script, unchanged, so that the
# numbers line up with that note's sections 9 and 10. Writes measurements/stages_* beside the
# other measurements. Run from learn/research/tripo-api-trial/.
set -uo pipefail
B=../blender-stages-trial/models
m() { [ -f "$B/$2.glb" ] && scripts/measure_model.sh "stages_$1" "$B/$2.glb" 0.8; }
for s in crate orb; do
  m ${s}_chain                 chain_${s}_keep1t_a_5_place          # the finished model of the chain
  m ${s}_chain_fast            chain_${s}_keep_a_5_place            # the same with the bake on every thread
  m ${s}_reduced20k_own_uvs    red_${s}__collapse20k_clear30        # reduced only: Tripo's UVs and 4096 maps kept
  m ${s}_baked1024             bake_${s}__1024_keeppack
  m ${s}_baked4096             bake_${s}__4096_keeppack
  m ${s}_reduced5k_baked       bake_${s}__5k_2048_keeppack
  m ${s}_p1_rebaked            tripo_${s}_p1_tri_req20000__repaired_bake_autocage
  m ${s}_p2_rebaked            tripo_${s}_p2_tri_req20000__repaired_bake_autocage
done
m crate_chain_smart_uv chain_crate_smart_a_5_place
