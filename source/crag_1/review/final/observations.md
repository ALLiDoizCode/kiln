# crag_1, final: what the sheet shows

Read from `sheet.png` and `benchmarks/out/crag_variants.png`. Numbers in brackets are the gate's own, from `out/reports/`.

1. **Silhouette.** Stepping down: reads in `right` and `back`, where four caps stand at four levels; in `front` only two prisms show, the tallest hiding the rest. Tallest off-centre: reads in `back` and `top` [summit 0.628 of the half extents from the middle; brief: at least 0.25]. Leaning: reads in `front` and `scale`, where the tallest prism's left edge is about 10 degrees off upright and its top overhangs its foot; does not read in `right`, which looks along the lean. Blocks at the foot: read in `front`, `back` and `bevy` as low wedges at both ends, each under a tenth of the height.
2. **Proportions.** 3.2 x 2.6 x 3.0 m. Prisms 3.0, 2.22, 1.65 and 1.27 m tall, steps 0.74, 0.75, 0.77 [brief: at most 0.9]. In `front` the tallest prism is about 0.45 of the asset's width: a thick block, about twice as tall as wide, and not a slender column. 6 pieces; 0.340 of the surface buried [brief: at most 0.4]; shown 10.68 to 1.77 m2, smallest step 1.32 [brief: at least 1.15]. Leans 9.0 to 11.0 degrees, within 5.6 degrees of their common way [brief: at least 5, within 45].
3. **Facing and grounding.** The base sits on the bottom edge of the frame in `front`, `right` and `back`; no gap under any piece. A crag has no front.
4. **Topology** (clay_wire). 462 triangles [budget 540]. One bevel strip per plane edge; long edges run unbroken from the ground to each shoulder; caps are fans. No edges along the joins.
5. **Shading.** No face darker or lighter than its neighbours without a lighting reason in the material tiles.
6. **Materials.** One grey, mottled in patches; edges lighter [1.23 times open faces]; joins darker [0.62 times].
7. **Scale** (scale tile). The figure reaches about 0.6 of the crag's height [brief: 1.8 of 3.0 m].
8. **In the engine** (bevy, bevy_back). The faces turned from the light are near black in `bevy_back` and in the `--stand 3` and `--stand 0.5` tiles of the variants sheet: the joins and the mottling cannot be seen there, and the `--stand 0.5` tile is one dark field.
11. **Differences from the brief.**
    - The tallest prism is about 1.4 m across, nearly half the crag's width; "many leaning prisms" reads as one block with smaller ones beside it in `front`.
    - Foot: 0.22 and 0.10 m2 on two sides [brief: 0.08 on two]; a third side shows 0.07.
    - Silhouette 8 and 9 (cap slant, long edges) have no check; both read in `clay_wire_front` and `clay_wire_back`.

Not done: the value-map and squint aids (`tools/review_aids.py views`) were not made, so items 9 and 10 of the review protocol are not written. The owner has not looked at this sheet.
