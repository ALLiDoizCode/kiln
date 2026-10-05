# leaf_mat_3, final: observations

From `benchmarks/out/leaf_mat_variants.png` and, for the first variant, `benchmarks/out/leaf_mat_1_candidates.png`; `sheet.png` was rendered and passed the image lint but was not opened. Numbers not read off a tile are the gate's (the L1 log, the L4 report). The gate stops at L4 on `uv.coverage` (see 11); the tiles after it were made with the gate's own commands. The aids of `tools/review_aids.py` were not made.

1. **Silhouette.** `--stand 0.5` and `--stand 1`: a ragged patch of separate pointed leaves with ground showing between them and bays in its outline; no straight edge and no round one. From 3 m (`--stand 3`) it is a small green smudge with a broken edge.
2. **Proportions.** 37 leaves 0.072 to 0.103 m long (brief 0.05 to 0.14), the steepest 16.4 degrees from level (brief at most 25); 0.97 of them lap another (brief at least 0.5). They cover 0.562 of their convex hull (brief 0.45 to 0.8) and 0.336 of the bounds' footprint (brief at least 0.3).
3. **Facing and grounding.** No front. It lies on the ground; no leaf's corner is under 4 mm.
4. **Topology.** Each leaf is 4 triangles, each runner 16; 180 (budget 200) triangles.
5. **Shading.** Each leaf is lit as one flat piece; none is black.
6. **Materials.** Leaves in two or three greens, the upper ones light yellow-green and the lower darker and bluer; a runner shows as a thin brown line between leaves where it is not covered.
7. **Scale.** standard: 0.4 m across, 0.22 of the figure's height; 3 cm tall.
8. **In the engine.** Leaves throw small shadows on the ground and on each other, which is what separates them.
9. **Values.** Not made as value maps. As rendered: light and mid green pieces over small dark shadows; no mass.
10. **At a glance.** "Fallen leaves", "leaf litter": a scatter of separate leaves more than a mat of ground cover. The benchmark's clover is three large clover leaves on stalks, a different thing.
11. **Differences from the brief.**
   - `uv.coverage` fails at L4: the runners' islands use 0.346 of the texture and the conventions want 0.4. The texture holds only two thin runners under a palette strip; left failing, as instructed.
   - "A mat": with a third of the footprint covered it reads as loose leaves lying on the ground, not as a carpet. The cover asked (0.3 of the footprint, 0.45 of the hull) was made up before anything was built, and the budget was raised once to reach it.
   - The leaves point every way; ground cover that grows (ivy, clover) would show its leaves in rows along the runners.
