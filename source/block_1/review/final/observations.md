# block_1, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/block_variants.png`. Numbers in brackets are the gate's own, from `out/reports/`.

1. **Silhouette.** Near-cuboid: `front` is a rectangle 1.7 times as wide as tall with one top corner cut at about 45 degrees; `right` and `back` the same box with one or two cut corners; `top` a rectangle with its two front corners cut. Square to the view: top 0.665, front 0.963, back 0.531, right 0.597, left 0.763 [at least 0.5 each]. Chamfers: four, 0.07 to 0.093 m across [at least 3 of 0.04 m]; in `front` only one shows, in `top` two. No crack, as the brief says.
2. **Proportions.** 0.5 x 0.35 x 0.3 m. The largest chamfer is about a fifth of the width in `top`. 0.665 of the view from above is level [at least 0.5].
3. **Facing and grounding.** The base sits on the bottom edge of the frame in `front`, `right` and `back`; sides lean in by a few degrees at most. A block has no front.
4. **Topology** (clay_wire). 80 triangles [budget 150]. Each face of the box is one fan of two to four triangles; every edge carries one bevel strip. No edge supports nothing.
5. **Shading.** Each plane is lit flat and the strips as round edges; no face darker or lighter than its neighbours without a lighting reason.
6. **Materials.** One grey, lighter on top than at the foot in every side view; blotches about a sixth of the width across; a pale line on the upper edges.
7. **Scale.** About one sixth of the figure's height [brief: 0.3 of 1.8 m].
8. **In the engine** (`bevy`, `block_variants.png`). The same planes and tones; the side away from the light is two values darker than the top. From `--stand 3` it is a small light box with a dark side; its chamfers cannot be told from there.
9. **Values.** Not made for this variant (aids were made for `block_2`).
10. **At a glance.** Not made for this variant.
11. **Differences from the brief.**
    - Closest to its limit: 0.531 of the back view square to the view, where 0.5 is asked.
    - From 3 m the chamfers do not read (item 8); the block reads as a plain brick.
    - The pack has no block to compare with; beside `Rock_Medium_1` it is plain: no moss, no drawn rim.
