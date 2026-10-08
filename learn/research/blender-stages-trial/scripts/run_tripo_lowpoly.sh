#!/usr/bin/env bash
# Stage 4, second half: Tripo's own low-poly meshes (P1.0 and P2.0, which come without UVs or
# textures) given new UVs and the H3.1 model's three maps. The dense model is first stretched
# onto the low mesh's bounding box (fit=bbox), because the two are different generations.
# Run from learn/research/blender-stages-trial/. Pictures go to work/pics/<run>/.
set -uo pipefail
export TRIAL_NO_COMPARE=1
M=$(realpath ../tripo-api-trial/models)
for s in crate orb; do for g in p1 p2; do
  m=${s}_${g}_tri_req20000; high=$M/${s}_h31_default.glb
  b() { n=$1; low=$2; shift 2; echo "== $m $n $(date +%T)"; scripts/run_stage.sh tripo_${m}__$n uv_bake.py $low high=$high fit=bbox size=2048 margin=8 "$@" | tail -1
        [ -f models/tripo_${m}__$n.glb ] && scripts/pictures.sh tripo_${m}__$n models/tripo_${m}__$n.glb; }
  b raw_bake_cage30mm $M/$m.glb cage_extrusion=0.03 max_ray_distance=0.06
  b raw_bake_autocage $M/$m.glb cage=auto
  scripts/run_stage.sh tripo_${m}__repaired repair.py $M/$m.glb weld=1e-4 degenerate=1e-4 loose=true hidden_pieces=true recalc_normals=true fill_holes=0 normals=clear | tail -1
  b repaired_bake_cage30mm models/tripo_${m}__repaired.glb cage_extrusion=0.03 max_ray_distance=0.06
  b repaired_bake_autocage models/tripo_${m}__repaired.glb cage=auto
  b repaired_bake_autocage_sharp30 models/tripo_${m}__repaired.glb cage=auto sharp_angle=30
done; done
echo "== done $(date +%T)"
