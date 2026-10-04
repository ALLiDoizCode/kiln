# rock / final: observations

From `sheet.png`, seed 2, 126 triangles, colour `#a1a7a1` under painted shading in one 1024 px texture. Orthographic tiles are framed at 4.90 m across 512 px (104 px per metre); pixel figures are read by eye and good to about 2%. Numbers marked L1 are printed by `tools/validate.py` for this build, and numbers marked L4 are in `out/reports/L4-bevy.json`, measured by the Bevy load test on the exported texture. The benchmark comparison uses `benchmarks/out/rock_vs_benchmark.png` (both rendered by `asset_view`, standard and `--close`).

## Silhouette

- Large planes (brief: 6 to 16, holding at least 75% of the visible surface, largest at least 3 times the median). L1: 12 large planes holding 80.2% of 14.91 m2, largest 3.08 m2, median 0.66 m2, ratio 4.68. three_quarter and bevy: one plane (the slab) fills more than half of the rock's outline; front: the slab is the right-hand two thirds, with four smaller planes to its left.
- Ledge (brief: a concave corner of at least 0.5 m between two large planes). L1: one, 1.32 m long. It reads in front, back and scale as a notch in the outline: in front the shelf is at about 1.25 m, 0.65 m wide, with a riser about 0.6 m tall behind it, leaning back. In right it does not break the outline; it shows only as a darker upright band left of centre. In top it is the straight dark line right of centre. In bevy it is a small notch at the upper left, about one tenth of the rock's width.
- No face reads as part of a sphere: in every material tile each plane's tone changes only with height (the painted gradient), in level bands, and across the narrow strips between planes. No plane's tone curves.
- Sides lean in from a wide base: front, right and back all show the outline widest at the ground. right: the slab runs from the peak (left third of the tile) to the ground at the far right, at about 45 degrees on screen; the left side is within 10 degrees of upright.

## Proportions

- front: 61% of the tile wide and 41% tall, so 3.0 m by 2.0 m. Brief: 3.0 m, 2.0 m.
- right: 53% of the tile wide, so 2.6 m. Brief: 2.6 m.
- The rock is much less than its bounding box: 14.91 m2 of visible surface against 30.2 m2 for the box's top and sides. The peak is a ridge about 0.6 m wide in front, not a broad top.

## Facing and grounding

- front, right, back, scale: the base is a straight line on the lower edge of the spec's frame, with no gap.
- The brief names no front. front shows the ledge on the left and the slab on the right; top shows a seven-sided outline with the ledge line running front to back.

## Topology (clay_wire)

- Every plane boundary is a pair of close parallel lines, the bevel strip, about 0.1 m apart on screen. They follow the silhouette everywhere.
- Inside each plane, diagonals fan from one corner (front: five across the slab). They support nothing: the plane is flat. They exist because the gate allows no face with more than four sides.
- No dense patch anywhere; the smallest faces are the triangles where three strips meet.

## Shading (material)

- No plane is darker or lighter than its lighting and its paint explain. The paint is the same at the same height on every plane: front, right and back all show the green band ending at the same level.
- The UV seams do not show: no line of a different tone crosses a plane or runs along a strip in any material tile. L4: no texel is claimed by two triangles, and the islands use 43% of the texture.
- back and right are lit only by the shadowless fill light. With flat colour those tiles were carried by the outline alone; now each has three bands (green, dark grey, pale grey) and light lines along the edges, so the planes separate.

## Materials

- Colour (brief: `#a1a7a1`, untouched at the top). top, front: the summit plane and the upper third of every side are a pale grey with a slight green cast. L4: open faces are 0.997 times the material colour times the tint at their height (allowed 1 +/- 0.08).
- Gradient (brief: darker toward the base; the ground tint leaves about 27% of the light). front, right, back: tone falls steadily from the summit to the ground, and the lowest quarter of the rock's height is the darkest part of every tile. L4: the lowest quarter of the open faces is 0.458 times as light as the highest; the tints give 0.461.
- Growth (brief: olive `#7a8a4d` from the ground to about 0.9 m, thinning above, ragged upper edge). front, right, back, scale: an olive green band from the ground to a little under half the rock's height (0.9 m of 2.0 m is 45%), strongest in the bottom fifth and fading out over roughly another fifth. Its upper edge rises and falls by about a tenth of the rock's height along the front; it is soft everywhere, with no hard outline. top: green shows only round the rim of the outline, where the sides reach the ground.
- Edge light (brief: exposed edges up to 30% lighter, fading 0.08 m into each plane). top, front, three_quarter: every boundary between planes carries a light line about as wide as the bevel strip, brightest on the sharpest corners (the summit's rim and the ledge's outer corner) and faint on the shallow ones low on the slab. There is none along the ground. L4: exposed edges average 1.21 times as light as open faces at the same height (the gate wants at least 1.15).
- Crevice shadow (brief: the corner of the ledge loses 45%, fading over 0.3 m). top: a dark line down the ledge's inside corner, right of centre, with a soft dark band either side of it, wider on the shelf than on the wall. front: the shelf is darker toward the wall behind it. L4: within 0.075 m of the corner the colour averages 0.72 times an open face's (the gate wants at most 0.775).
- Range. L4: the brightest channel of every texel is between 93 and 188 of 255 (allowed 30 to 240).

## Scale

- scale: the rock's top is at about 1.12 times the figure's height. Brief: 2.0 m beside 1.8 m, 1.11. The shelf is at about two thirds of the figure's height, shoulder level.

## In the engine (bevy tile)

- The same three bands as in Blender: olive at the base, grey above it, pale at the top, with the green ending at the same height on the slab and on the planes to its left.
- Colour differs from the Blender tiles. In Bevy the lit slab's upper half is a pale grey close to the flat-coloured rock's, and the green band is a light olive; in Blender's front tile the same band is a dark, saturated olive (about `#545f3f` at the ground against about `#69734c` on the lit slab in Bevy). Bevy's light is stronger, as it was for the crate and the flat rock. Bevy is right; the paint's darkest values are lifted by it.
- The one plane in shadow on the right is near black, and no paint can be read on it.
- Edge light survives: each boundary between lit planes is a light band, and the summit's rim is the lightest line in the tile. Soft edges survive as before: the load test still finds no hard edge above the ground.
- The ledge is a small notch at the upper left, about one tenth of the rock's width, and its crevice shadow is too small to pick out at this distance.
- The base meets the ground with a cast shadow and no gap, and no light line.

## Beside the benchmark

Both in Bevy, same camera and light (`benchmarks/out/rock_vs_benchmark.png`; the flat-coloured rock is kept beside it as `rock_flat_vs_benchmark.png`).

- Read at a glance: both are now a pale-topped grey rock standing in a green base, with light edges. Before, ours was one pale shape and the benchmark a painted one; that difference is gone at the standard distance.
- Base: sampled low on the lit face, ours is about `#767d6d` going to `#69734c` at the ground, the benchmark about `#6b725f` going to `#6b7656`. The greens are within a few percent of each other; ours is a little more yellow.
- Middle: the benchmark's sides are a darker grey than ours between the green and the top (its lit side face is roughly a third darker than ours at mid height). Ours stays pale down to the green. Its gradient is steeper high up; ours is an even ramp.
- Brushwork: the benchmark's texture has patches of moss on the top and along upper edges, darker blotches on the faces, and chipped light marks along edges, each with a hard, hand-drawn outline. Ours has none: every transition is a smooth ramp. Close up (`--close`), the benchmark's slab shows about a dozen separate marks; ours shows a clean gradient and one soft-edged green band. This is the largest remaining difference in the surface.
- Growth on top: the benchmark has moss where it would settle, on the top and the ledge. Ours has it only by height from the ground.
- Planes, mass, secondary form: unchanged from the flat-coloured review. Ours has flatter planes; it is a wedge with a narrow ridge (14.9 m2 of surface against 24.3 m2), and from the standard view one plane is about 70% of its outline, which the paint now divides into bands but does not break up.
- Cost: 126 triangles and a 380 kB file (3.7 kB before painting), against 342 triangles and a shared 2048 px texture for the benchmark.

## Differences from the brief

None found against the brief's numbers: bounds, budget, plane count, share, size ratio, ledge and soft edges are as before, and the material colour, gradient, edge light, crevice shadow, texture size and texel range each measure as specified (Materials, above).

Two things were caught by number during this work, and neither by eye:

1. A rebuild did not give the same file. The rock's build script returned its faces in a different order on every run (the triangulation step), so the index buffer changed while the shape did not. The faces are now sorted; three rebuilds give one hash.
2. An export of a stale build under a changed spec was caught by `painted.colour` and `painted.gradient` at L4 (the texture was painted for the old tints).

One defect escaped the gates during the first build and stays closed: the first export lit every face flat. It is `soft_edges` in the spec and a check in the Bevy load test.

For the owner to judge, since no number in the brief settles them:

1. Every painted value is a first proposal: the tints, the green and its height, and the edge and crevice amounts. In Bevy the top third still reads pale; a darker `top_tint` or material colour would bring the middle toward the benchmark's.
2. There is no brushwork. The paint is smooth ramps computed from the shape. Whether the style needs hand-drawn-looking marks is a style question for the look test.
3. Growth follows height only. Moss on upward-facing shelves would need a term for which way a face points.
4. The rock is wedge-shaped and occupies about half its bounding box's surface. The brief gives bounds, not fullness. Known, and handled separately.
5. "Clearly different tilts" has no check.
6. From the front right the slab hides the ledge.
7. Bevel width (0.07 m) and one segment: at `--close` the edge reads as soft, not round.
