# tree_sapling_1, final: observations

Read from `sheet.png`, `bevy_under.png`, and the aids `bevy_aids.png` and `material_three_quarter_aids.png`. Written by the agent that built it; no reference image of a sapling exists to set beside the aids.

1. **Silhouette**: front and back: one stem that forks once, at about 0.55 of the height (measured 1.9 m of 3.5 m), into a leader and one side branch, each ending in one tuft; the tufts are about 0.55 and 0.25 of the frame's width of the tree, with a gap of sky between them about as wide as the smaller tuft. Right: the smaller tuft is behind the larger and the tree reads as one tuft on a stem; the side branch shows beside the stem below it. Top: two tufts in a row along x, joined by the bare branch; the row is about three times as long as the smaller tuft is wide.
2. **Proportions**: the wider tuft is 1.73 m of the 3.1 m width (0.56) and about 0.3 of the height; the narrower 1.1 m (0.35). The stem below the fork is 0.54 of the height (brief: fork 1.5 to 2.1 m; 1.9 m). The side branch runs bare for about a quarter of the tree's height before its tuft.
3. **Facing and grounding**: the foot sits on the bottom edge of the frame in every level view; the stem leans toward the wider tuft (0.16 m at the fork) and the side branch leaves to the other side.
4. **Topology**: clay_wire: the stem's rings are about evenly spaced below the fork and the branch's along its length; leaf pieces are the dense part and each tuft's pieces radiate from its middle.
5. **Shading**: material tiles: no face darker than its neighbours without a lighting reason; pieces on top of each tuft are the lightest and those hanging under it the darkest.
6. **Materials**: bark brown with lengthwise grain (bevy_trunk); leaves light yellow-green on top, darker and bluer green underneath.
7. **Scale**: the figure is about 0.5 of the tree's height (1.8 / 3.5 = 0.51); its head is level with the fork and below both tufts.
8. **In the engine**: bevy: same colours as the material tiles, the lit side of the stem lighter; the tufts' shadows on the ground are two separate shapes. bevy_trunk: the stem fills about a fifth of the tile's width, with grain along it, and the side branch and a tuft show at the top edge. bevy_under: the eye is 1.7 m up, level with the fork, so the view is of the wider tuft's underside from beside the stem: dark green pieces with about ten points against the sky along its left edge, and three or four thin pale-green slivers between pieces near the stem (pieces seen edge-on, lit from above).
9. **Values** (bevy_aids, value map): three masses: the tufts' lit tops (lightest), their undersides and the stem (dark), and the shadows on the ground. The smaller tuft is as light as the larger and stays separate from it.
10. **At a glance** (squint): "small forked tree"; the eye lands on the wider tuft, then the smaller one above and to the left of it.
11. **Differences from the brief**: from the two views along the row (right, left) the two tufts read as one, so "two tufts with clear air between them" holds in four of the six level views' directions and not end-on (sky 0.27 there, 0.43 from front and back); in bevy_under three or four pale slivers show between the dark pieces near the stem, which no check measures; the tufts read spikier than a mature pad (points clear against the sky 4.7 to 6.1 per metre of outline, mature 1.4 to 3.6), which follows from half of each piece standing out of its lobe. 1,046 triangles of 1,200.

## After the swept foot and the limbs' rings (branch `treefoot`, 2026-10-05)

Read from the rebuilt `bevy.png`, `bevy_under.png` and `bevy_trunk.png`, and the gate's reports; the Blender tiles of the sheet were opened only for `tree_young_1`. Where a line above speaks of the foot as a skirt or of elbows, this replaces it.

- Triangles: 1,102. L1: 3 roots in 3 ridges, the sharpest turn between two stretches of a limb 14.8 degrees (it was 16.9).
- `bevy`: the foot is three separate roots, thin ridges that run out over the ground from the trunk, with bare ground between them; no skirt joins their tips. Between two roots the trunk comes straight down to the ground, flat-sided: it does not widen there.
- `bevy`, the roots' flanks: fine streaks run out along each root. The grain is not seen stretched into patches at this distance.
- `bevy_under`: each limb curves in even stretches; no single stretch turns more sharply than its neighbours. A limb is still flat-sided, and its corners show as straight lines.
- L4: on open faces the grain's furrows are 1.019 of the tone the paint gives a furrow and its plates 0.981 of a plate's (0.44 of the open samples are furrow); inside corners are 0.56 times as light as open faces; the sparsest triangle has 456 texels per metre.
