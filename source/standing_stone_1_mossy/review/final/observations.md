# standing_stone_1_mossy, final: observations

Read from the material tiles of `sheet.png` (front, right, back, top, three-quarter, scale) and the standard view in `benchmarks/out/covers_mossy.png`. The clay and Bevy tiles of the sheet were not read one by one; the mesh is `standing_stone_1`'s byte for byte (L2c). The review aids were not made; no second reader. Not approved.

1. **Where the moss is**: an olive wash on the lowest 0.8 m with a soft, nearly level top, covering the foot block; dark olive flecks down the upper third of the upright edges and round the tipped cap; the faces between are bare.
2. **Amounts**: 0.29 of the asset's pixels in the standard view are green. Load test: growth on 1.00 of the surface below 0.32 m; 0.00 of upright open faces above 1.28 m; 0.59 of the level faces there are (280 samples, the bevel round the cap, none clear of an edge; 0.12 to 0.82 allowed); 0.41 of upper edges; patches 0.51 darker, measured between neighbouring samples; 2.10 patch edges per 0.085 m.
3. **Differences from the brief**: none seen. The stone has no face near level, so `growth_up` is measured on a strip of bevel only; the brief expects little there.
