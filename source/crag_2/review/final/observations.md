# crag_2, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/crag_variants.png`. Numbers in brackets are the gate's own, from `out/reports/`.

1. **Silhouette.** Stepping down: reads in `front` and `back`, three and four caps at different levels falling to one side. Tallest off-centre: reads in `front`, where it stands in the right third [summit 0.567; brief: at least 0.25]. Leaning: reads in `right`, where both visible prisms tilt about 10 degrees the same way; hardly in `front`. Blocks: three low plates, one large in front of the tallest prism in `three_quarter` and `bevy`, where it reads as a plinth under it.
2. **Proportions.** 5.0 x 4.0 x 4.6 m. Prisms 4.6, 3.72, 3.12, 2.54, 2.04 m, steps 0.80 to 0.84 [brief: at most 0.9]. The tallest is about a third of the width in `front`. 8 pieces; 0.297 buried [brief: at most 0.4]; smallest size step 1.17 [brief: at least 1.15]. Leans 8.3 to 10.2 degrees, within 11.4 degrees of the common way.
3. **Facing and grounding.** The base is on the bottom edge of the frame in all side views.
4. **Topology** (clay_wire). 634 triangles [budget 720].
5. **Shading.** No unexplained light or dark face in the material tiles.
6. **Materials.** One grey; edges 1.21 times open faces, joins 0.57. A 2048 px texture [154 texels per metre at the sparsest; 72 at 1024 px, which failed the load test].
7. **Scale.** The figure is about 0.4 of the height [brief: 1.8 of 4.6 m].
8. **In the engine.** As crag_1: shaded faces near black; the `--stand 0.5` tile is one dark field.
11. **Differences from the brief.**
    - The first block is large enough to read as a plinth in front of the tallest prism in `bevy`, more a step than "small blocks".
    - Foot: 0.30, 0.26 and 0.43 m2 on three sides [brief: 0.2 on two].
    - The 2048 px texture is this variant's own; the family's is 1024.

Not done: the value-map and squint aids (`tools/review_aids.py views`) were not made, so items 9 and 10 of the review protocol are not written. The owner has not looked at this sheet.
