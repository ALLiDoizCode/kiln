# standing_stone_1, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/standing_stone_variants.png`. Numbers in brackets are the brief's; the measurements beside them are the gate's own, from `out/reports/`.

1. **Silhouette.** front and back: a slab about 0.95 m wide at the ground narrowing to about 0.6 m at the shoulder, 2.7 times as tall as wide; right: about 0.45 m thick, leaning to the right by about a tenth of its height. The slanted cap and its chamfer ring read in `front`, `back` and `bevy`, taking the top eighth of the height. The foot block shows in `back` (a third of the stone's width, a tenth of its height) and `right` (a nub at the base); from `front`, `three_quarter` and `bevy` it is hidden behind the stone.
2. **Proportions.** 1.4 x 1.1 x 2.6 m, foot blocks included. 2 pieces of 8.62 and 0.80 m2; 0.042 of the surface buried [at most 0.2]; they show 8.48 and 0.55 m2, a step of 15.5 [at least 1.5].
3. **Facing and grounding.** The base sits on the ground with no gap in any view. The stone has no front; the lean and the foot block are the cues to how it is turned.
4. **Topology.** 190 triangles [budget 400]. Each side is one quad from the ground to the shoulder, with a bevel strip down each corner: long vertical edges, no horizontal bands below the shoulder.
5. **Shading.** No face lit differently from its neighbours without a lighting reason; no hard edge above the ground [load test: none].
6. **Materials.** One grey, darker toward the ground and at mid height on the sides; mottled in patches about 0.4 m across; edges lighter [exposed edges 1.25 times open faces]; a dark band where the foot block meets the stone [joins 0.53 times open faces]. No green.
7. **Scale.** The stone is about 1.45 times the figure [2.6 m of 1.8 m: 1.44].
8. **In the engine.** The lit side is about three values lighter than the side facing away, which is close to black in `--back`; seen from 0.5 m on that side (`--stand 0.5`) the stone is a dark field with no detail. The benchmark's shaded side from 0.5 m is as dark.
9. **Values.** Two masses in the standard view: the lit sides with the cap (light) and the shaded side with the cast shadow (dark). The aids were not made for this asset.
10. **At a glance.** "Grey standing stone"; the eye lands on the slanted cap. The benchmark reads as "mossy boulder".
11. **Differences from the brief.**
    - 0.738 of the side surface is within 8 degrees of upright; the brief sets no limit, on purpose.
    - Summit 0.430 off the middle [at least 0.15].
    - The foot block is small and hidden from about half the views; the stone reads as standing on bare ground from those. The brief asks only that it be there and joined.
    - Silhouette 1, 2, 4, 5 and 8 have no check and are as described in item 1.
    - Bare stone beside a mossy benchmark, as with the slab.
