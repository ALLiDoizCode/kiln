# lily_pad_3, final: observations

From `sheet.png`, `benchmarks/out/lily_pad_variants.png` and `benchmarks/out/lily_pad_1_candidates.png`. Numbers not read off a tile are the gate's (the L1 log, the L4 report). The gate stops at L4 on `uv.coverage` (see 11); the tiles after it were made with the gate's own commands. The aids of `tools/review_aids.py` were not made, so items 9 and 10 are from the tiles as rendered.

1. **Silhouette.** material_top: 7 discs, each a many-sided round shape with one wedge-shaped notch to its middle, none touching; the notches open different ways. front, right, back: a line a few pixels thick with the flower as a bump on it: nothing reads from the side, as the brief expects. The rim does not read in any tile: from above a disc is one flat tone.
2. **Proportions.** Discs 1.45, 1.00, 0.73, 0.53, 0.40, 0.25 and 0.17 m (brief: widest 1.2 to 1.7, narrowest 0.08 to 0.2); notches 21 to 34 degrees (brief 15 to 60); rims 0.033 to 0.042 of the width above the floor (brief 0.02 to 0.08); floors all at one height, each within 0.012 m of level (brief 0.02). Two flowers 0.26 and 0.19 m across (brief 0.14 to 0.3), filling 0.579 of the convex hull (brief at most 0.6).
3. **Facing and grounding.** No front. Everything lies on the bottom edge of the frame in the level tiles.
4. **Topology.** clay_wire_top: each disc is a fan of triangles to its middle and one ring of quads for the rim, 8 to 16 sides by size; the flowers are the densest thing in the picture. 356 (budget 500) triangles.
5. **Shading.** material tiles: no face darker than its neighbours without reason; the discs are lit as flat plates.
6. **Materials.** The widest discs are a light yellow-green and the small ones a darker, slightly bluer green; the flower is warm white, darker and rosier at its foot.
7. **Scale.** scale: the widest disc is 1.45 m across, 0.8 of the figure's height; the group is 3.0 m long.
8. **In the engine.** bevy: as the Blender tiles, a little paler; each disc throws a thin shadow line on the ground along one side, which is the only sign that it has thickness or a rim.
9. **Values.** Not made as value maps. As rendered from above: two tones of green and one point of white; no dark anywhere.
10. **At a glance.** From standing height: "lily pads", or, for the single wide ones, "pac-men": the notch is the feature the eye lands on. The flower reads as a pale five-pointed star, nearer a starfish than a water lily.
11. **Differences from the brief.**
   - `uv.coverage` fails at L4: the flowers' islands use 0.196 of the texture and the conventions want 0.4. The texture holds only the flowers (a top and an underside island each) under a palette strip; left failing, as instructed, and not dodged with a larger texture.
   - "A raised rim" (silhouette 1) is measured (0.033 to 0.042 of the width) and does not read from above in any tile.
   - "Flowers" read as stars: five petals round a pointed middle, with no cup. A cup's inside faces are lit from behind when the bloom is lit smooth (the load test's normals check), so the bloom is convex.
   - Scatter is 0.44 and 0.53 (brief at least 0.3 each).
   - From on top of the widest disc (`asset_view --stand 0.1`, not a tile of the sheet): the disc fills the middle of the picture as one flat light green shape of 16 straight sides with a wedge cut out of it; its rim, 5 cm high, cannot be told from its floor. It reads as a paper cut-out, not as a leaf with an upturned edge.
