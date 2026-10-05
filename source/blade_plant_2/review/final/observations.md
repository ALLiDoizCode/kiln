# blade_plant_2, final: observations

From `sheet.png`, its tiles, the aids and `benchmarks/out/blade_plant_variants.png`. Numbers not read off a tile are the gate's (`out/reports/` and the L1 log).

1. **Silhouette.** top: a star of 16 blades from one point, the widest gap between neighbours 45 degrees (brief: at most 100). front, right, back: an upright tuft of inner blades in the middle third of the width, with outer blades reaching the sides of the frame and drooping at their ends. The outer blades are seen nearly edge-on from the level views and show there as thin dark lines, not as leaves; they read as leaves from above and from the three-quarter view.
2. **Proportions.** Blades are 0.78 to 1.10 m foot to tip (brief 0.3 to 1.3), mean width 0.12 to 0.23 of that (brief 0.08 to 0.25), leaning 24 to 82 degrees (brief 15 to 85). The median blade stands 0.343 of its length off the straight line (brief at least 0.08). The rootstock is about a fifth of the plant's width in the top tile on variant 1, less on variant 2.
3. **Facing and grounding.** The plant has no front. The rootstock sits on the bottom edge of the frame in the level tiles, at the origin in the top tile; the bounds are off-centre about it by a few centimetres, as the spec gives them.
4. **Topology.** clay_wire: each blade is three stretches and a tip, with one line along its middle; the bends between stretches show as corners in the level tiles (two or three kinks a blade), most on the drooping outer blades. 248 triangles (budget 400).
5. **Shading.** material tiles: blades are lit smooth; the fold shows as a lighter and a darker half on the inner blades. No blade is black.
6. **Materials.** Inner, higher blades are the lightest yellow-green; outer, lower ones darker and bluer. The rootstock is dark brown and shows in the top and three-quarter tiles, and as a dark base in the level tiles.
7. **Scale.** scale: the plant is about 0.56 of the figure's height (brief 1.0 m of 1.8 m).
8. **In the engine.** bevy: lighter and more even than the Blender tiles; the undersides of the outer blades are the darkest green. The plant's shadow on the ground is as large as the plant.
9. **Values.** bevy value map: the blades are two greys (lit upper faces, shaded undersides) and the rootstock a black spot; the masses are small and thin against the ground, as the benchmark plant's are.
10. **At a glance.** bevy squint: "small green tuft"; the eye lands on the upright middle. The benchmark's `Plant_1` reads "broad-leaved plant": its leaves are about twice as wide for their length and carry a painted gradient to orange tips.
11. **Differences from the brief.**
   - The brief's "long broad leaves": at mean width 0.12 to 0.23 of their length the blades are at the narrow end of broad beside the benchmark's; from 0.5 m (`blade_plant_variants.png`, fourth column) they read as leaves, from 3 m as a tuft.
   - The bends between a blade's three stretches read as kinks from the side. Nothing measures them; one more stretch a blade would cost 4 triangles each.
   - Each blade is one flat colour; the benchmark's gradient along the leaf is what ours lacks most at 0.5 m.
