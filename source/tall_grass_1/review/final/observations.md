# tall_grass_1, final: observations

From `sheet.png`, `benchmarks/out/tall_grass_variants.png` (rows 1 and 5) and `benchmarks/out/tall_grass_1_candidates.png`. Numbers not read off a tile are the gate's (the L1 log). The aids of `tools/review_aids.py` were not made, so items 9 and 10 are from the tiles as rendered.

1. **Silhouette.** front, right, back: a sheaf, narrow at the foot (about a sixth of its greatest width) and widest at three quarters of the leaves' height, with a ragged top of blade tips bending outward; four seed heads stand above it on thin stalks. Background shows between blades only in the outer third and at the top. top: a star of blades all round, the widest gap between neighbours 24 degrees (brief: at most 60), with the dark rootstock in the middle.
2. **Proportions.** 88 blades (84 leaves and 4 seed stalks), 0.77 to 1.13 m foot to tip (brief 0.3 to 1.8), mean width 0.01 to 0.05 of that (brief 0.008 to 0.05). 35 of 88 lean 15 degrees or less (0.40; brief at least 0.3); the most any leans is 34 degrees (brief at most 60). Sky is 0.465 of the outline on average, 0.43 to 0.52 by view (brief at most 0.5): the right and left views are over 0.5 on their own. The median blade stands 0.077 of its length off the straight line (brief at least 0.05). Seed heads are 0.12 to 0.15 m long (brief 0.06 to 0.2), their lowest points 0.81 to 0.88 of the height (brief above 0.7); the leaves' tips reach about 0.8 of it.
3. **Facing and grounding.** No front. The rootstock sits on the bottom edge of the frame in the level tiles and at the origin in the top tile.
4. **Topology.** clay_wire: each leaf is three stretches and a tip, the rows even along it; 664 triangles (budget 700).
5. **Shading.** material tiles: blades are lit smooth; those seen edge on are thin dark lines. None is black.
6. **Materials.** The tall blades are a light yellow-green, the short outer ones darker and bluer; the seed heads are pale straw; the rootstock is a brown spot seen only in the top tile.
7. **Scale.** scale: the seed heads reach about 0.63 of the figure's height (brief 1.15 m of 1.8 m, 0.64): the waist.
8. **In the engine.** bevy: colours a little paler than in Blender; the clump's shadow is a spray of thin lines as long as the clump is tall. `--stand 0.5` (variants sheet): looking down on it the clump is a star of straight, pointed blades round the seed stalks, and the arch of the blades does not show. `--stand 0.15 --pitch -60` (from inside): the same star, filling the picture, with the rootstock a dark point; no blade crosses another's direction.
9. **Values.** Not made as value maps. As rendered, from the side: one mid-dark mass with a lighter top edge and light seed heads; the benchmark's is a few broad strokes, each dark at the foot and light at the tip.
10. **At a glance.** From 3 m: "clump of grass". From above at 0.5 m: "spiky green star", as the grass tuft's review said of the tuft, though denser. The benchmark from 0.5 m is a few broad curving leaves.
11. **Differences from the brief.**
   - "Arching over at their tips" (silhouette 3) reads from the side only. From above and from inside, blades read as straight: a blade bends in one upright plane, outward, so seen along that plane it is a straight line.
   - "Soft" is not reached seen from above: every blade ends in a point 5 to 17 degrees wide and all point away from the middle.
   - Sky from the right and left is 0.52, over the brief's 0.5; the check takes the mean of six views (0.465).
   - Each blade is one flat colour; the benchmark's dark foot and light tip along each blade is still what ours lacks.
   - The twelve seeds of the candidates sheet are nearly alike: they differ in the number of seed heads (3 to 6) and in one or two outer blades.
