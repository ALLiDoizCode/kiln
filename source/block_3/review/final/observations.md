# block_3, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/block_variants.png`. Numbers in brackets are the gate's own, from `out/reports/`.

1. **Silhouette.** Near-cuboid: `front` and `back` are a rectangle 1.7 times as wide as tall. Square to the view: top 0.549, front 0.647, back 0.687, right 0.701, left 0.697 [at least 0.5 each]. Chamfers: three ways, 0.278 to 0.295 m across [at least 3 of 0.16 m]; in `top` three of the four corners are cut. Two cracks read in `front`, `back`, `top`, `three_quarter` and both Bevy tiles. In `top` they are two straight dark lines that run toward each other, about a fifth of the width apart at the back and a twentieth at the front; in `front` the lines down the side meet near the ground in a V.
2. **Proportions.** 2.0 x 1.4 x 1.2 m. The pieces show 6.97, 3.91 and 2.83 m2 [steps 1.78 and 1.38, at least 1.3]. Lines across the block that meet two grooves: 0.789 [at least 0.7]. 0.307 of the surface is buried [at most 0.4]. 0.549 of the view from above is level [at least 0.5].
3. **Facing and grounding.** The base sits on the bottom edge of the frame; no gap under it.
4. **Topology** (clay_wire). 164 triangles [budget 350]. Three closed pieces; the middle one is a wedge, narrow at the front of the block.
5. **Shading.** Planes lit flat, strips round; grooves dark.
6. **Materials.** One grey, top lighter than foot; blotches about 0.3 m; the cracks are the darkest things on the block.
7. **Scale.** About two thirds of the figure's height [brief: 1.2 of 1.8 m].
8. **In the engine** (`bevy`, `bevy_back`, `block_variants.png`). From `--stand 0.5` a groove fills a third of the view: both rims are lit and the lower rim's edge shows a sawtooth of about a dozen steps along 0.5 m, texels of the 1024 px texture. From `--stand 3` the two cracks are plain.
9. **Values.** Not made for this variant.
10. **At a glance.** Not made for this variant.
11. **Differences from the brief.**
    - The two cracks nearly meet at the front (item 1): the brief says no crack crosses another, and none does on the top, but the lines down the front side meet near the ground, so the middle piece reads there as a wedge driven into the block.
    - The cracks are straight, even slots, as on `block_2`.
    - The sawtooth in item 8 at 0.5 m: the brief gives this size 200 texels per width, 100 per metre, the conventions' least.
    - Closest to its limit: the smaller size step, 1.38 where 1.3 is asked; 30 of 40 seeds build at this size.
