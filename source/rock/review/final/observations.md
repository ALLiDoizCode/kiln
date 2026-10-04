# rock / final: observations

From `sheet.png`, seed 2, 154 triangles, colour `#a1a7a1` under painted shading in one 1024 px texture, 454 kB. Orthographic tiles are framed at 4.90 m across 512 px (104 px per metre); pixel figures are read by eye and good to about 2%. Numbers marked L1 are printed by `tools/validate.py` for this build, and numbers marked L4 are in `out/reports/L4-bevy.json`, measured by the Bevy load test on the exported texture. The benchmark comparison uses `benchmarks/out/rock_vs_benchmark.png` (both rendered by `asset_view`: standard, `--close` and `--back`). The sheet now has two Bevy tiles, `bevy` from the front right and `bevy_back` from the back left.

## Silhouette

- Fullness (brief: at least 45% of the bounding box). L1: 56.2%. front: the outline is a block about 1.9 m tall at both ends, with one corner missing at the lower right; nothing tapers to a ridge.
- Crown (brief: the slice three quarters up is at least 28% of the footprint). L1: 38.4%. top: the raised slab and the shelf together cover about two thirds of the outline.
- Planes (brief: 6 to 16 large, at least 75% of the surface, largest at least 2 times the median). L1: 16 large planes holding 89.0% of 19.63 m2; largest 2.13 m2, median 0.78 m2, ratio 2.73. There is no plane under 0.4 m2: everything that is not a large plane is soft edge.
- No plane dominates (brief: at most 40% of the outline from each of seven directions). L1: front 33%, right 38%, back 30%, left 34%, top 34%, three_quarter 30%, three_quarter_back 17%. right: the wall behind the shoulder is the largest thing in the tile, about 1.6 m wide and 0.9 m tall. bevy: the same wall is the largest plane, about a third of the rock's outline.
- Step (brief: a raised slab above a lower shelf). back: a level band about 0.4 m tall and 1.5 m long, 0.4 m below the top edge, with the shelf in front of it. top: the straight line from upper left to lower right, left of centre. bevy_back: the riser is the dark band across the upper part, the shelf the pale surface below it. It does not show in front, right or bevy: the slab hides it.
- Fracture (brief: a V-shaped groove down one side, widest at the top). front: a dark slanted band from the top edge to the ground, left of centre, about 0.35 m wide at the top and 0.25 m at the ground, with a lit wall beside it. top: the notch in the outline at the upper right. It does not show in right or back. In bevy it is the vertical dark gap at the far left edge of the rock, about one twentieth of its width: present, and easy to miss.
- Shoulder (brief: a bench at about half height). front: the missing corner at the lower right, shelf at about 1.0 m. right: a shelf across the middle two thirds of the tile at about 0.95 m with a wall behind it. back: the low block at the far left. bevy: the shelf across the lower right of the rock; it is the form that reads first.
- Every side shows a form. L1: ledge corner in plain sight from front 2.71 m, right 1.50 m, back 1.74 m, left 0.73 m, top 3.68 m, three_quarter 1.58 m, three_quarter_back 1.79 m (brief: at least 0.5 m from each). The outline has an inward corner in front, right and back. There is no left tile on the sheet; left is the weakest direction by this number.
- No face reads as part of a sphere: in every material tile each plane is one flat tone under its paint; tone changes only across the narrow strips between planes.
- Sides lean in from a wide base: front and back show the outline about 0.2 m narrower at the top than at the ground on each side. The leans are slight (L1 does not measure them; the script draws 2 to 13 degrees), so in bevy the rock reads as a block with near-upright walls.

## Proportions

- front: 61% of the tile wide and 41% tall, so 3.0 m by 2.0 m. Brief: 3.0 m, 2.0 m.
- right: 53% of the tile wide, so 2.6 m. Brief: 2.6 m.
- The step's riser is about 0.4 m of the 2.0 m height (one fifth); the shoulder's shelf is at about half height; the fracture runs the full height.

## Facing and grounding

- front, right, back, scale: the base is a straight line on the lower edge of the spec's frame, with no gap.
- The brief names no front. front shows the fracture on the left and the shoulder on the right; top shows the step's line running from upper left to lower right.

## Topology (clay_wire)

- Every plane boundary is a pair of close parallel lines, the bevel strip. They follow the silhouette everywhere.
- Inside each plane, diagonals fan from one corner (front: seven across the large plane right of the fracture). They support nothing: the plane is flat. They exist because the gate allows no face with more than four sides.
- clay_wire front, right, back and scale each show one thin line rising about 0.5 m above the top of the rock. It is not in any material tile or in either bevy tile, and L1 finds the bounds exact to a millimetre, so it is not in the mesh: it is made by the review pass's wireframe modifier. It is listed under Differences.
- The sharpest face corners are slivers of 0.5 to 2 degrees where a bevel strip runs out at the ground edge, which is left hard. They are at z = 0 and do not show.

## Shading (material)

- No plane is darker or lighter than its lighting and its paint explain.
- The UV seams do not show: no line of a different tone crosses a plane in any material tile. L4: no texel is claimed by two triangles, and the islands use 44.5% of the texture.
- There is no banding in any tile: tone changes without visible steps. L4: the open faces use every 8-bit level in the range they span (largest unused run 0; the gate allows 3).

## Materials

- Colour and gradient (brief: `#a1a7a1` at the top, about 27% of the light at the ground). front, right, back: tone falls from the top to the ground on every side. L4: open faces average 0.993 times what the tint and side shade give (allowed 1 +/- 0.08); the lowest quarter is 0.412 times as light as the highest, expected 0.397.
- Growth by height (brief: olive from the ground to about 0.9 m, ragged and patchy at its top). front, right, back: green from the ground to between a third and a half of the height; its upper edge rises and falls by about 0.3 m along each side and is lobed, not level. L4: growth shows on 100% of the surface below 0.36 m and on 0.5% of upright open faces above 1.44 m.
- Growth on level faces (brief: patches over about 45%). top: the slab and the shelf are each about half green, in five or six separate patches 0.3 to 0.9 m across with soft borders a few centimetres wide. L4: 52% (allowed 23% to 68%).
- Growth along upper edges (brief: about half of them). front, right, back: green along parts of the top edge, in stretches of 0.3 to 0.8 m with gaps between. L4: 57% of the edge zone of upright faces in the top fifth.
- Side shade (brief: upright faces up to 22% darker at mid height). front, back: each side has a darker grey band between the green and the paler top. L4: 15.3% darker than the tint alone, where 16.5% is due.
- Blotches (brief: up to 12% lighter and darker, about 0.6 m across). right, bevy: the wall behind the shoulder shows four or five soft lighter and darker patches. In front and back they are faint under the growth. L4: tone spread 0.240 between the 10th and 90th percentile (allowed 0.12 to 0.30); neighbouring samples differ by 2.6% of that, so they are broad.
- Edge light (brief: up to 30% lighter). top, front: each boundary between planes carries a light line about as wide as the strip. L4: 1.257 times open faces.
- Crevice shadow (brief: 45% in the corner, fading over 0.3 m). top, back, bevy_back: a dark line in the corner of the step and of the shoulder, widening onto the shelf; the fracture's inside is the darkest part of front. L4: 0.636 times open faces.
- Range. L4: the brightest channel of every texel is between 65 and 205 of 255 (allowed 30 to 240).

## Scale

- scale: the rock's top is at about 1.12 times the figure's height. Brief: 2.0 m beside 1.8 m, 1.11. The shoulder's shelf is at about 0.55 of the figure's height, hip level.

## In the engine (bevy, bevy_back)

- The same layers as in Blender: green at the base, grey sides, a paler top with green patches.
- Colour differs from the Blender tiles. In Bevy the growth on the lit top and shelf is a light yellow green (`#b7c487` sampled on the slab in `--close`, beside `#6a6d6b` on the wall below it), much lighter than the olive of the base in shadow; in Blender's top tile it is the same light yellow green. The brief paints growth at the rock's own lightness, so on a pale lit top it is pale. The benchmark's moss is darker than the rock it sits on (`#48533d` sampled on a fleck in its `--close`).
- bevy: the slab's notch, the wall and the shoulder's shelf read at once. The fracture is at the left edge, nearly edge-on.
- bevy_back: the step reads as a dark band with a shelf; the faces toward the camera are in the sun's shade and the paint on them is hard to read, as before.
- Soft edges survive: the load test finds no hard edge above the ground.
- The base meets the ground with a cast shadow and no gap.

## Beside the benchmark

Both in Bevy, same cameras and light (`benchmarks/out/rock_vs_benchmark.png`, three rows: standard, close, back; the earlier rock is kept as `rock_painted_v1_vs_benchmark.png`).

- Mass: ours is now the fuller of the two. Volume share 0.562 against the benchmark's 0.450 (tightest box); crown 0.384 against 0.28 to 0.30. In the standard view ours stands as tall and as wide as the benchmark in its frame; before, it was a wedge beside it.
- Largest plane: ours 30% of the standard view's outline, the benchmark's largest flat region 34% to 36%. Before: 45%.
- Secondary form: both have a slab on top and a groove. The benchmark shows both in the standard view; ours shows the shoulder and the slab's notch there and keeps the step and most of the fracture for other sides.
- Character: the benchmark's sides lean in visibly more than ours (in the standard view its outline is about two thirds as wide at the top as at the ground; ours is about nine tenths) and its faces differ more in size. Ours has near-upright walls, nine sides of similar width and level shelves, and reads as a cut block: more architectural than weathered. This is the largest remaining difference in shape.
- Growth: the benchmark has small dark-green flecks on the top and upper edges, a few centimetres to 0.2 m across, darker than the rock. Ours has patches several times larger and much lighter and yellower. Ours is present where the benchmark's is; it is not as believable.
- Blotches and sides: the benchmark's sides have soft darker and lighter areas and a darker middle; ours now has both, at lower contrast. Close up they are comparable.
- Edges: the benchmark's edges carry a thin warm highlight; ours a broader pale one. Unchanged.
- Cost: 154 triangles and 454 kB, against 342 triangles and a shared 2048 px texture.

## Differences from the brief

None found against the brief's numbers: every value in the Numbers table measures as specified above.

Found on the sheet and not caught by any gate:

1. clay_wire tiles show a thin line rising above the rock. It comes from the review pass's wireframe modifier, not from the asset. No check covers the review pass itself.

Caught by number during this work:

1. The banding reported in the previous side-by-side was in that image, not in the texture or in Bevy: it was saved 16 bits deep with alpha, and viewers reduce such a file to a palette. The sheet and the side-by-side are now 8-bit and opaque, and `image.eight_bit` and `image.opaque` gate them. The texture has its own guard, `painted.banding`.
2. A texture reduced to twelve levels, and a rock with no growth at all, both passed every gate before this work.

For the owner to judge, since no number in the brief settles them:

1. The growth's lightness on lit, level faces (above).
2. The blockiness: near-upright walls and nine similar sides. `docs/style/rock-shapes.md` asks for several pieces in a clear size order, a foot, and wide chamfers; this rock has none of those.
3. `planes.min_size_ratio` was lowered from 3.0 to 2.0 (brief, Decisions).
4. From the standard view the fracture is nearly edge-on.
5. "Clearly different tilts" still has no check.
