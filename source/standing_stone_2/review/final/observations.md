# standing_stone_2, final: what the sheet shows

Read from `benchmarks/out/standing_stone_variants.png` (five Bevy views) and the gate's reports; the Blender tiles of `sheet.png` were not read one by one. Numbers in brackets are the brief's; the measurements beside them are the gate's own, from `out/reports/`.

1. **Silhouette.** standard and `--stand 3`: a blade about 3.5 times as tall as it is wide in that view, tapering to a narrow slanted cap; it leans toward the camera's right. One foot block shows at the base in `standard`, `--close` and `--stand 3`, about a sixth of the stone's width and a twelfth of its height; the second shows only in `--back`.
2. **Proportions.** 1.9 x 1.4 x 3.6 m, foot blocks included. 3 pieces of 14.53, 1.89 and 1.07 m2; 0.095 buried [at most 0.2]; they show 14.07, 1.11 and 0.65 m2, steps of 12.6 and 1.72 [at least 1.5].
3. **Facing and grounding.** The base sits on the ground with no gap in any view. The stone has no front; the lean and the foot block are the cues to how it is turned.
4. **Topology.** 204 triangles [budget 400]. Each side is one quad from the ground to the shoulder, with a bevel strip down each corner: long vertical edges, no horizontal bands below the shoulder.
5. **Shading.** No face lit differently from its neighbours without a lighting reason; no hard edge above the ground [load test: none].
6. **Materials.** One grey, darker toward the ground and at mid height on the sides; mottled in patches about 0.4 m across; edges lighter [exposed edges 1.22 times open faces]; a dark band where the foot block meets the stone [joins 0.57 times open faces]. No green.
7. **Scale.** The stone is twice the figure [3.6 m of 1.8 m].
8. **In the engine.** The lit side is about three values lighter than the side facing away, which is close to black in `--back`; seen from 0.5 m on that side (`--stand 0.5`) the stone is a dark field with no detail. The benchmark's shaded side from 0.5 m is as dark.
9. **Values.** Two masses in the standard view: the lit sides with the cap (light) and the shaded side with the cast shadow (dark). The aids were not made for this asset.
10. **At a glance.** "Grey standing stone"; the eye lands on the slanted cap. The benchmark reads as "mossy boulder".
11. **Differences from the brief.**
    - 0.812 of the side surface is within 8 degrees of upright; the brief sets no limit, on purpose.
    - Summit 0.312 off the middle [at least 0.15].
    - The foot block is small and hidden from about half the views; the stone reads as standing on bare ground from those. The brief asks only that it be there and joined.
    - Silhouette 1, 2, 4, 5 and 8 have no check and are as described in item 1.
    - Bare stone beside a mossy benchmark, as with the slab.
