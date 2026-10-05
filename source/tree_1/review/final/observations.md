# tree_1 / final: observations

From `sheet.png`, seed 11, 3,366 triangles (886 bark, 2,480 leaf), two materials on one 1024 px texture, 684 kB. Orthographic tiles are framed at 10.76 m across 512 px (47.6 px per metre); figures read off tiles are by eye and good to about 0.1 m. Numbers marked L1 are printed by `tools/validate.py` for this build, and numbers marked L4 are in `out/reports/L4-bevy.json`, measured by the Bevy load test on the exported file. The aids are `bevy_aids.png` and `material_three_quarter_aids.png` beside the sheet, and `benchmarks/out/CommonTree_1_aids.png` for the benchmark. The benchmark beside this variant is `benchmarks/out/tree_1_vs_benchmark.png`, and all three variants from a player's eye are in `benchmarks/out/tree_variants.png`.

## Silhouette

- Designed trunk (brief: five to eight flat sides, leaning 0.15 to 0.8 m, at most 0.9 of its girth below the fork, flare at least 2.0 into at least three roots). L1: 6 sides, radius 0.19 m at 1.3 m, lean 0.18 m, taper 0.81, flare 3.8 in 4 roots. front: the trunk is a dark brown column about 0.4 m wide at 1.3 m, widening to about 1.2 m across at the ground in a triangular foot; it bows left by about 0.2 m between the ground and the fork. right: the same column, nearly upright. clay_wire_front: the trunk's sides show as two or three long quads between each pair of rings, with a narrow strip between sides; the roots are the triangular fins at the ground.
- Visible branch skeleton (brief: fork at 2.0 to 3.5 m, at least three limbs, tapering to at most 0.8, bark at least 2% of what is seen above the fork from six of seven views). L1: fork at 2.5 m, 9 limbs in the busiest slice (twigs included), limb taper 0.53; bark seen: front 0.073, right 0.095, back 0.048, left 0.062, three_quarter 0.045, three_quarter_back 0.054, below 0.050. front: three limbs leave the trunk between about 2.2 and 2.8 m, one low to the left and two rising right of centre; bark shows between and under every pad. bevy: four limbs can be counted against the ground.
- Separate pads (brief: three to six, each of at least 40 pieces, sky 20% to 50% of the canopy's outline from five of six views). L1: five (138, 135, 128, 126 and 93 pieces), none stray; sky: front 0.37, right 0.33, back 0.37, left 0.33, three_quarter 0.25, three_quarter_back 0.29. front: five pads; two side by side at the top (centres about 5.9 m), one in the middle at about 4.6 m, one low on the left at about 3.5 m, and one behind the middle pad. Background shows between the top two pads, and between the low left pad and the rest. right: four separate pads, the top one widest. top: four pads in a ring round a gap at the trunk, about 0.3 m wide, through which bark shows; the fifth is under the upper ones.
- Leaf-shaped pieces (brief: flat, pointed, notched, 0.35 to 0.9 m, pointing out and down). L1: 620 pieces, 0.54 to 0.75 m long, all flat, all with a corner of 60 degrees or less and a notch; 0.88 point out of their pad and 0.86 below level. front and right: every pad's lower edge is a row of points hanging down, 6 to 10 across each pad; the upper outline is smoother, broken by a few raised tips. Single pieces can be told apart in the front tile, where one is about 30 px long.
- Not measured: that pads differ visibly in size. front: the widest pad is about 1.4 times the narrowest.
- The trunk leans least of the three (0.18 m against a floor of 0.15 m): in front the lean reads as a slight bow, not a lean.

## Proportions

- front, right: the tree fills the height of the spec's frame from the ground line to 7.0 m and its width; L1 finds the bounds exact to a millimetre (4.9 m, 4.7 m, 7.0 m).
- The fork is at 2.5 m of 7.0 m; the canopy takes the rest. The trunk at 1.3 m is about 0.4 m across, a twelfth of the crown's width.
- A pad is 2 to 3 m across and about 1.3 m tall; a piece is about a quarter of a pad's width.

## Facing and grounding

- front, right, back, scale: the foot of the trunk sits on the lower edge of the spec's frame, its roots flat on it, with no gap.
- The brief names no front. The origin is at the foot of the trunk: in top the trunk is off the middle of the canopy, toward the side the bounds are shorter on.

## Topology (clay_wire)

- Trunk: six rings from the ground to the fork, closest together at the foot where the roots curve in, about 0.8 m apart above. Each supports the bend or the taper.
- Limbs: five rings each; twigs are three-sided and show as single dark lines.
- Foliage: every piece is four triangles; in the clay tiles the pads are dense with edges, because every piece's outline and its three inner edges are drawn. The inner edges support nothing visible (a piece is flat); they are there because the notch makes the outline concave.

## Shading (material)

- No bark face is darker or lighter than its neighbours without a lighting reason. The trunk's sides are each one tone and the tone steps at the corners; L4 finds no position above the ground with two normals.
- Leaf pieces differ in tone from their neighbours within a pad; this is their colour and their own tilt, not a normal fault: L4 finds no triangle whose normals face against its winding.
- The seams of the bark's texture do not show as lines in any material tile.

## Materials

- Bark `#7a5a44`: front and scale show a mid brown, darker toward the foot (L4: the lowest quarter of the open bark is 0.73 (the tints give 0.75) times as light as the highest). L4: corners are 1.19 times as light as open faces, junctions 0.65 times. At this tile size neither shows; see In the engine for the close view.
- Leaf `#a8b846`: the tops of pads are a light yellow-green, their sides a mid green and their lower rims a dark green. L4: 24 colours in use, every piece on the palette, 0.87 of pieces with a nearest neighbour of another colour, the highest quarter of each pad at least 2.70 times as light as its lowest (the tints give 3.60 from bottom to top), blue 0.092 of the colour below against 0.066 above.
- L4: the bark's islands use 51.5% of the texture at 217 texels per metre at their sparsest.

## Scale

- scale: the figure reaches about a quarter of the way up; the tree is 3.9 times the figure's height. Brief: 7.0 m over 1.8 m is 3.9.
- scale: the fork is above the top of the figure's head.

## In the engine (bevy)

- bevy: three pads read at once, light on top and darker on their right and lower sides; the fork is in plain sight below them. bevy_back: four pads; the two nearest the camera show their dark undersides.
- Against the Blender material tiles, Bevy's foliage is lighter and yellower on top and its shadow side is darker; the bark is the same brown. Bevy also casts the canopy's shadow on the ground: 5 joined round blots with small holes of light in them.
- `tree_variants.png`, from 3 m: the underside of the canopy is dark green with the limbs and twigs drawn against it; pieces seen from below are flat four- and five-sided shapes, and their points show only at the pads' rims. From 0.5 m: bark fills a third or more of the view as flat brown sides with no visible grain; its edge light and blotches do not show in the canopy's shadow.
- Foliage seen from below and from behind is never black: in the four Bevy views of this variant the darkest 1% of foliage pixels are 41 to 43 of 255 in the green channel, and none is under 20. From below the median is 52 to 58, the same as the benchmark's (53).

## Values (value maps)

- bevy: four masses. The lit tops of the pads are the lightest thing in the image; the pads' shadow sides and undersides are one step darker than the ground; the trunk and limbs are a dark line; the cast shadow is the darkest large shape. No pad vanishes into the ground or into another pad.
- material_three_quarter: three masses (pad tops, pad undersides, bark); the limbs read as dark lines between light pads.
- Benchmark (`CommonTree_1_aids.png`): two masses, one dark canopy with a few light specks on its lit edge, and the trunk. Its canopy is darker than the ground; ours is lighter than the ground on top.

## At a glance (squint views)

- bevy: "tree with clumps". The eye lands on the lightest pad top, then on the gaps between pads. The trunk is thin and reads second.
- Benchmark: "round dark tree". The eye lands on the canopy as a whole, then the trunk, which is thicker than ours (about 0.5 m against 0.4 m).

## Differences from the brief

- Lean is 0.18 m against the brief's 0.15 to 0.8 m: inside the range by 3 cm. If a visible lean is wanted of this variant, it needs another seed.
- The bark's painted shading passes its checks and cannot be seen from the review distances; from 0.5 m the trunk reads as flat brown planes. The brief asks for bark that holds up at arm's length, and the benchmark's bark, with a painted texture and a normal map, holds up better there.
- Pieces seen from underneath do not read as leaves: their notch and point are lost against other pieces, and they read as overlapping flat shapes. The brief's "leaf-shaped" is met by measurement and from the side, not from below.
- The pads are regular: each is a rounded cap of about the same proportions, and from the side they read as caps on stalks more than as the lumpy masses of the reference. Nothing in the brief measures this.
- No other mismatch found in items 1 to 10.
