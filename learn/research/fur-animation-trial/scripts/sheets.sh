#!/usr/bin/env bash
# Puts the probe's frames side by side as the contact sheets the note describes (ImageMagick).
set -uo pipefail
cd "$(dirname "$0")/../pictures"
m() { out="$1"; tile="$2"; shift 2; magick montage "$@" -tile "$tile" -geometry 640x480+2+2 "$out"; }
m sheet_a_masks.png 4x2 a_mask_outside_laplace_10/side_00.png a_mask_outside_laplace_30/side_00.png a_mask_outside_taubin_100/side_00.png a_mask_thin/side_00.png \
  a_mask_outside_laplace_10/top_00.png a_mask_outside_laplace_30/top_00.png a_mask_outside_taubin_100/top_00.png a_mask_thin/top_00.png
# a_fused frames: 0 base, 1 soft_all, 2 soft_masked, 3 push 0.5, 4 push 1, 5..8 axial 0.25..1, 9 axial 2
m sheet_a_soft.png 3x2 a_fused/three_quarter_0{0,1,2}.png a_fused/side_0{0,1,2}.png
m sheet_a_spiked.png 3x2 a_fused/three_quarter_0{4,8,9}.png a_fused/side_0{4,8}.png a_fused/back_quarter_08.png
m sheet_a_sweep.png 5x1 a_fused/three_quarter_0{0,5,6,7,8}.png
for p in p1 p2; do  # b frames: 0 base, 1 retracted, 2 retracted 0.5, 3..6 extended 0.25..1, 7 extended 2
  m sheet_b_$p.png 3x2 b_mask_$p/three_quarter_00.png b_pieces_$p/three_quarter_0{0,1}.png b_mask_$p/top_00.png b_pieces_$p/three_quarter_06.png b_pieces_$p/back_quarter_06.png
done
m sheet_d_clip.png 4x1 d_clip/three_quarter_0{0,1,2,3}.png
m sheet_e.png 4x2 e_tripo_weights/side_0{0,1}.png e_auto_calm/side_0{0,1}.png e_auto_spiked/side_01.png e_auto_spiked/three_quarter_01.png e_own_rig/side_0{0,1}.png
m sheet_e_tripo_glb.png 2x1 e_tripo_rigged/{three_quarter,side}_00.png
m sheet_f.png 3x2 f_calm/{three_quarter,side,front}_00.png f_spiked/{three_quarter,side,front}_00.png
