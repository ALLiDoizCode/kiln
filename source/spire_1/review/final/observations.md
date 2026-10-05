# spire_1, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/spire_variants.png`. 3.2 x 2.8 x 6.0 m. Numbers in brackets are the gate's own, from `out/reports/` and the L1 log; the shares of surface by tilt were measured on the built mesh by a scratch script and are not a check.

1. **Silhouette.** Tiers: three read in every level view and in `bevy`; each step in is a visible notch on both flanks in `front`, `right` and `back` [3 tiers; steps 0.47, 0.52; brief: at most 0.7]. Flat caps: the top tier ends in a flat about a third of its width in `clay_wire_front`, not a point; the two ledges are seen as surfaces only in `top` and `three_quarter` [ledges 0.123, 0.131, 0.220 of each level cut; brief: 0.1]. Flutes: in `clay_wire_front` three edges run unbroken from the ground to the base's shoulder, and no level edge crosses a side [14 tall sides; brief: 6]; in the material tiles the base's sides differ little in tone and the flutes read weakly: it reads as a truncated pyramid of flat faces more than a fluted column. Off-centre: the upper tiers stand right of the base's middle in `front` by about a tenth of its width [summit 0.149; brief: 0.1]. Foot: buttresses read in `front` (two, at the left and the middle) and `back` (one, right); the two blocks are specks under a twentieth of the height.
2. **Proportions.** The base is 0.45 of the height and about 2.6 m wide at the ground, 1.5 m at its shoulder; second tier 0.3 of the height, top tier 0.27. Tiers 1.82, 0.86, 0.45 m wide at mid height. The tallest buttress reaches about 0.6 of the base's height. 8 pieces, 0.226 buried [brief: at most 0.4]; shown 20.08 to 0.38 m2, smallest step 1.43 [brief: 1.15].
3. **Facing and grounding.** The base sits on the bottom edge of the frame in `front`, `right` and `back`; no gap under any piece. A spire has no front.
4. **Topology** (clay_wire). 688 triangles [budget 800]. One bevel strip per plane edge; no edges along the joins; caps are fans.
5. **Shading.** No face darker or lighter than its neighbours without a lighting reason.
6. **Materials.** One grey, mottled; edges lighter [1.26 times open faces], joins darker [0.58 times]; lighter toward the top [gradient 0.704, expected 0.698].
7. **Scale.** The figure reaches 0.3 of the spire's height [brief: 1.8 of 6.0 m], and about two thirds of the way up the base.
8. **In the engine** (`bevy`, `bevy_back`, and `benchmarks/out/spire_variants.png`). In `bevy` the lit flank is light grey and the far flank dark; the chamfer ring of the base is the lightest band. In `bevy_back` every side is dark; the base's chamfer ring, the caps' chamfers and one buttress with its sloping cap are the only light. From 0.5 m (`--stand 0.5`) the tile is one dark field with one soft edge across it.
9. **Values** (value maps of `bevy` and `bevy_back`). `bevy_back`: two masses, the whole spire in the second-darkest grey, and small light patches at the base's shoulder, the second tier's shoulder, the top and one buttress: about a tenth of the asset's area. The benchmark rock from the back shows a light top about a third of its area.
10. **At a glance** (squint). `bevy_back`: "dark stepped tower"; the eye lands on the lit buttress at the foot. The steps survive the blur as two notches.
11. **Differences from the brief.**
    - Light: 0.939 of the side surface is within 17 degrees of upright (the crag: 0.91) and 0.392 within 8; only 0.085 of the visible surface is nearer level than upright. The brief's ledges and chamfer rings are light bands a few percent of the outline; from behind the spire is still one dark field. Not solved.
    - Flutes read weakly in the material tiles (item 1).
    - The blocks at the foot are too small to read from 3 m.
    - Silhouette 8 (chamfers ring every cap) has no check; it reads in every clay_wire tile.

The owner has not looked at this sheet.
