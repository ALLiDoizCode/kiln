#!/usr/bin/env bash
# Stage 1: the round trips of section 3. Run from learn/research/blender-stages-trial/.
# These are the loops as they were typed during the trial, gathered here afterwards; the
# script itself has not been run from start to end.
set -uo pipefail
M=../tripo-api-trial/models
for m in crate_p2_tri_req20000 crate_p1_tri_req20000 orb_p2_tri_req20000 orb_p1_tri_req20000 \
         crate_p2_tri_req20000_textured crate_p2_tri_req20000_smartuv orb_p2_tri_req20000_textured \
         orb_p1_tri_req20000_textured crate_p2_tri_req10000 crate_p2_tri_req5000 crate_p2_tri_req2000; do
  scripts/run_stage.sh rt_${m}_default roundtrip.py $M/$m.glb | tail -1
  scripts/run_stage.sh rt_${m}_nomerge roundtrip.py $M/$m.glb merge_vertices=false | tail -1
  scripts/run_stage.sh rt_${m}_smooth roundtrip.py $M/$m.glb shading=SMOOTH | tail -1
  scripts/run_stage.sh rt_${m}_clear roundtrip.py $M/$m.glb clear_custom_normals=true | tail -1
done
for s in crate orb; do
  m=${s}_h31_default
  scripts/run_stage.sh rt_${m}_default roundtrip.py $M/$m.glb | tail -1
  scripts/run_stage.sh rt_${m}_again roundtrip.py $M/$m.glb | tail -1
  scripts/run_stage.sh rt_${m}_nomerge roundtrip.py $M/$m.glb merge_vertices=false | tail -1
  scripts/run_stage.sh rt_${m}_smooth roundtrip.py $M/$m.glb shading=SMOOTH | tail -1
  scripts/run_stage.sh rt_${m}_tangents roundtrip.py $M/$m.glb tangents=true | tail -1
  scripts/run_stage.sh rt_${m}_webp roundtrip.py $M/$m.glb image_format=WEBP | tail -1
done
python3 scripts/summarise_roundtrip.py > roundtrip.csv
