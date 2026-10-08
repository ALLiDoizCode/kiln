#!/usr/bin/env bash
# Stage 2: every repair rule alone on every model, of section 4. Run from
# learn/research/blender-stages-trial/. These are the loops as they were typed during the
# trial, gathered here afterwards; the script itself has not been run from start to end.
set -uo pipefail
M=../tripo-api-trial/models
for m in crate_p1_tri_req20000 crate_p2_tri_req20000 crate_p2_tri_req20000_textured orb_p1_tri_req20000 \
         orb_p2_tri_req20000 orb_p2_tri_req20000_textured orb_p1_tri_req20000_textured; do
  r() { n=$1; shift; scripts/run_stage.sh rep_${m}__$n repair.py $M/$m.glb "$@" | tail -1; }
  r weld1e-4 weld=1e-4; r weld1e-3 weld=1e-3; r weld1e-2 weld=1e-2
  r degen1e-4 degenerate=1e-4; r degen1e-3 degenerate=1e-3
  r loose loose=true
  r pieces_tri1pc small_pieces=0.01 small_pieces_by=triangles
  r pieces_area1pc small_pieces=0.01; r pieces_area01pc small_pieces=0.001
  r hidden hidden_pieces=true
  r recalc_keep recalc_normals=true; r recalc_clear recalc_normals=true normals=clear
  r clear30 normals=clear; r clear0 normals=clear sharp_angle=0
  r holes4 fill_holes=4; r holes_all fill_holes=0
  r all weld=1e-4 degenerate=1e-4 loose=true recalc_normals=true fill_holes=0 normals=clear
done
for m in crate_p2_tri_req10000 crate_p2_tri_req5000 crate_p2_tri_req2000; do
  scripts/run_stage.sh rep_${m}__hidden repair.py $M/$m.glb hidden_pieces=true | tail -1
done
for m in crate_h31_default orb_h31_default; do
  r() { n=$1; shift; TRIAL_NO_COMPARE= scripts/run_stage.sh rep_${m}__$n repair.py $M/$m.glb "$@" | tail -1; }
  r all_keep weld=1e-4 degenerate=1e-4 loose=true recalc_normals=true fill_holes=0 normals=keep
  r weld_degen1e-5 weld=1e-5 degenerate=1e-5 loose=true recalc_normals=true fill_holes=0 normals=keep count_each=false
  r recalc_clear recalc_normals=true normals=clear count_each=false
  r hidden hidden_pieces=true count=false
done
python3 scripts/summarise_repair.py > repair.csv
