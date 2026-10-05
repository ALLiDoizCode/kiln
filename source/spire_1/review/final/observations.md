# spire_1, final: what the sheet shows

The reworked spire (2026-10-05, second round). 3.2 x 2.8 x 6.0 m. Numbers in brackets are the gate's own, from `out/reports/` and the L1 log; the shares of surface by tilt were measured on the built mesh by a scratch script and are not a check.

1. **Silhouette.** Tiers: three read in every level view; the steps are unequal, a small one at the base's cap and a large one under the top tier [steps 0.64, 0.45, differing by 1.42; brief: at most 0.7, differing by 1.2]. Off the middle: in `front` the second tier stands at the left of the base's cap and the top tier at the right of the second's [0.191, 0.511 of their width; brief: 0.15]. Leaning: in `right` the whole spire leans right, its top over the base's right edge [8.7 degrees; brief: 4]; in `front` it reads nearly upright, looking along the lean. Caps: tipped planes, each a different way, in the clay_wire level views; the ledges are seen as surfaces in `top` and `three_quarter` [0.168, 0.381, 0.516; brief: 0.1]. Base: a main mass with a shoulder about three quarters of its height at the right of `front` and a groove between them from the ground up [14 tall sides; brief: 6]. A block stands on the base's ledge in `front`, about a quarter of the second tier's height: it reads as a headstone set against a wall, not as a broken piece.
2. **Proportions.** Base 0.42 of the height; second tier 0.37, 1.36 m wide: a slab as wide as two thirds of the base; top tier 0.2 of the height and 0.62 m wide, about 0.3 of the base's width [brief: no post, a quarter]. 8 pieces, 0.356 buried [brief: at most 0.4]; shown 20.33 to 0.78 m2, smallest step 1.23.
3. **Facing and grounding.** The base sits on the bottom edge of the frame in the level views; no gap under any piece.
4. **Topology.** 698 triangles [budget 960]. One bevel strip per plane edge; no edges along the joins.
5. **Shading.** No face darker or lighter than its neighbours without a lighting reason.
6. **Materials.** One grey, mottled; edges 1.27 times open faces, joins 0.68 times; gradient 0.645 of 0.641 expected.
7. **Scale.** The figure reaches 0.3 of the height [brief: 1.8 of 6.0 m], about 0.7 of the way up the base.
8. **In the engine** (`bevy`, `bevy_back`, `benchmarks/out/spire_variants.png`). Under the viewer's light as it now is, `bevy_back` shows the shaded sides as a mid-dark grey in which the three tiers, the base's shoulder and the edge light can all be told apart [shaded sides' median 0.0795 linear; gate L4d asks 0.0543]. From 0.5 m the tile is two planes of slightly different grey meeting at one edge.
11. **Differences from the brief.**
    - Foot (Silhouette 8): the blocks are still low specks in `back` and `bevy_back`; in `front` they are hidden. The larger was meant to be a seventh of the base's height; against the shoulders it does not read. Not met by eye.
    - The ledge block reads as placed (item 1).
    - The pieces are still plain prisms with flat sides: it reads as stacked cut blocks of rock more than as one weathered mass.
    - 0.799 of the side surface is within 8 degrees of upright and 0.945 within 17 (no longer asked: the brief, under Light); 0.141 of what shows is nearer level than upright.
    - Silhouette 10 (no post) and the chamfers have no check.

Not done: value-map and squint aids were not remade for the reworked spire, so items 9 and 10 are not written. The blind pair `benchmarks/out/spire_blind.png` was made and not opened.

The owner has not looked at this sheet.
