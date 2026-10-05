# tree_2 / final: observations

From `sheet.png`, seed 7, 3,432 triangles (768 bark, 2,664 leaf), two materials on one 1024 px texture, 666 kB. Orthographic tiles are framed at 10.87 m across 512 px (47.1 px per metre); figures read off tiles are by eye and good to about 0.1 m. Numbers marked L1 are printed by `tools/validate.py` for this build, and numbers marked L4 are in `out/reports/L4-bevy.json`, measured by the Bevy load test on the exported file. The aids are `bevy_aids.png` and `material_three_quarter_aids.png` beside the sheet, and `benchmarks/out/CommonTree_1_aids.png` for the benchmark. The benchmark beside this variant is `benchmarks/out/tree_2_vs_benchmark.png`, and all three variants from a player's eye are in `benchmarks/out/tree_variants.png`.

## Silhouette

- Designed trunk (brief: five to eight flat sides, leaning 0.15 to 0.8 m, at most 0.9 of its girth below the fork, flare at least 2.0 into at least three roots). L1: 7 sides, radius 0.20 m at 1.3 m, lean 0.28 m, taper 0.87, flare 3.6 in 4 roots. front: the trunk leans right by about 0.3 m between the ground and the fork, about 0.4 m wide at 1.3 m, with a foot about 1.1 m across. back: the lean is the other way, as it should be. clay_wire_front: the trunk's sides show as two or three long quads between each pair of rings, with a narrow strip between sides; the roots are the triangular fins at the ground.
- Visible branch skeleton (brief: fork at 2.0 to 3.5 m, at least three limbs, tapering to at most 0.8, bark at least 2% of what is seen above the fork from six of seven views). L1: fork at 2.1 m, 10 limbs in the busiest slice (twigs included), limb taper 0.64; bark seen: front 0.024, right 0.038, back 0.034, left 0.027, three_quarter 0.020, three_quarter_back 0.030, below 0.041. front: a long limb leaves low to the left at about 2 m and runs nearly level for about 1.5 m before turning up into its pad; two more rise to the right. The fork is just above the figure's head in scale.
- Separate pads (brief: three to six, each of at least 40 pieces, sky 20% to 50% of the canopy's outline from five of six views). L1: four (213, 187, 135 and 131 pieces), none stray; sky: front 0.30, right 0.32, back 0.30, left 0.32, three_quarter 0.20, three_quarter_back 0.28. front: four pads; the crown pad at the top right is the widest thing on the tree (about 2.9 m), with two smaller pads stacked under it and one out to the left at about 3.6 m. Background shows between the left pad and the others across a gap about 0.5 m wide; the two under the crown are separated from it by a band of shadow, not of sky. top: three pads show, the crown pad covering the fourth; clear gaps of about 0.3 m between them.
- Leaf-shaped pieces (brief: flat, pointed, notched, 0.35 to 0.9 m, pointing out and down). L1: 666 pieces, 0.54 to 0.81 m long, all flat, all with a corner of 60 degrees or less and a notch; 0.86 point out of their pad and 0.85 below level. front and right: every pad's lower edge is a row of points hanging down, 6 to 10 across each pad; the upper outline is smoother, broken by a few raised tips. Single pieces can be told apart in the front tile, where one is about 30 px long.
- Not measured: that pads differ visibly in size. front: the widest pad is about 1.4 times the narrowest.

## Proportions

- front, right: the tree fills the height of the spec's frame from the ground line to 6.2 m and its width; L1 finds the bounds exact to a millimetre (5.5 m, 5.4 m, 6.2 m).
- The fork is at 2.1 m of 6.2 m; the canopy takes the rest. The trunk at 1.3 m is about 0.4 m across, a twelfth of the crown's width.
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

- Bark `#7a5a44`: front and scale show a mid brown, darker toward the foot (L4: the lowest quarter of the open bark is 0.74 (the tints give 0.77) times as light as the highest). L4: corners are 1.23 times as light as open faces, junctions 0.67 times. At this tile size neither shows; see In the engine for the close view.
- Leaf `#a8b846`: the tops of pads are a light yellow-green, their sides a mid green and their lower rims a dark green. L4: 24 colours in use, every piece on the palette, 0.85 of pieces with a nearest neighbour of another colour, the highest quarter of each pad at least 2.62 times as light as its lowest (the tints give 3.60 from bottom to top), blue 0.091 of the colour below against 0.066 above.
- L4: the bark's islands use 52.0% of the texture at 232 texels per metre at their sparsest.

## Scale

- scale: the figure reaches about a quarter of the way up; the tree is 3.4 times the figure's height. Brief: 6.2 m over 1.8 m is 3.4.
- scale: the fork is above the top of the figure's head.

## In the engine (bevy)

- bevy: the crown pad hides most of the skeleton; one limb shows at its right and the trunk below. This is the variant in which the least bark shows (2.0% from the standard three-quarter direction, the brief's floor). bevy_back: all four pads separate, with the limbs between them.
- Against the Blender material tiles, Bevy's foliage is lighter and yellower on top and its shadow side is darker; the bark is the same brown. Bevy also casts the canopy's shadow on the ground: 4 joined round blots with small holes of light in them.
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

- The fork is at 2.1 m (brief: 2.0 to 3.5 m), bark seen from three_quarter is 0.020 (brief: at least 0.02) and the trunk's taper is 0.87 (brief: at most 0.9). All three pass by a small margin; this is the variant nearest the edge of the brief.
- front and right: the two pads under the crown pad read as one mass with it from those sides; the sky share there is 0.30 and 0.32 because of the gap to the left pad, not because these three separate.
- The bark's painted shading passes its checks and cannot be seen from the review distances; from 0.5 m the trunk reads as flat brown planes. The brief asks for bark that holds up at arm's length, and the benchmark's bark, with a painted texture and a normal map, holds up better there.
- Pieces seen from underneath do not read as leaves: their notch and point are lost against other pieces, and they read as overlapping flat shapes. The brief's "leaf-shaped" is met by measurement and from the side, not from below.
- The pads are regular: each is a rounded cap of about the same proportions, and from the side they read as caps on stalks more than as the lumpy masses of the reference. Nothing in the brief measures this.
- No other mismatch found in items 1 to 10.
