# tree_young_1, final: observations

Read from `sheet.png` and `benchmarks/out/tree_stages.png`. Written by the agent that built it; the review aids (value map, squint) were not made for this asset.

1. **Silhouette**: front, right, back: a single trunk forking at about 0.4 of the height into three limbs, each ending in one pad; three pads, sky between every pair in front and back; in `right` the two lower pads overlap into one mass. Top: the three pads lie in a crescent, not round the trunk; the left third of the bounds' footprint is empty.
2. **Proportions**: the crown pad is about 0.3 of the height and 0.45 of the width; the trunk below the fork is about 0.4 of the height (brief: fork 1.8 to 3.0 m of 5.6 m; measured 2.2 m).
3. **Facing and grounding**: the foot sits on the bottom edge of the frame; the trunk leans to the right in `front`.
4. **Topology**: clay_wire: the trunk shows five rings below the fork; leaf pieces are the dense part.
5. **Shading**: no face darker than its neighbours without a lighting reason in the material tiles.
6. **Materials**: bark brown, leaves light yellow-green on top of each pad and dark green underneath.
7. **Scale**: the figure is about 0.32 of the tree's height (1.8 / 5.6 = 0.32).
8. **In the engine**: `bevy_trunk`: the trunk fills about a fifth of the tile's width (mature: about a third) and grain shows as dark streaks along it; `bevy_under`: one limb and the underside of one pad, dark green with points against the sky.
9. **Beside the mature tree** (`tree_stages.png`): shorter by about a fifth, thinner in the trunk, three pads to five.
10. **Differences from the brief**: the crescent of pads in `top` (the brief does not ask for pads all round, and no check measures it); 1,850 triangles of 2,500.

## After the fixes of 2026-10-05

Not looked at tile by tile after the change; only measured. L4e, from 1 m beside the trunk looking 78 degrees up: pale leaf samples 0.00005 of the leaf samples (at most 0.001); foliage over the limbs among it 1.55 (at least 1.25). The underside and core tints are about twice as light as when the lines above were written.

## After the swept foot and the limbs' rings (branch `treefoot`, 2026-10-05)

Read from the rebuilt `bevy.png`, `bevy_under.png` and `bevy_trunk.png`, and the gate's reports; the Blender tiles of the sheet were opened only for `tree_young_1`. Where a line above speaks of the foot as a skirt or of elbows, this replaces it.

- Triangles: 1,934. L1: 3 roots in 3 ridges, the sharpest turn between two stretches of a limb 13.6 degrees (it was 15.4).
- `bevy`: the foot is three separate roots, thin ridges that run out over the ground from the trunk, with bare ground between them; no skirt joins their tips. Between two roots the trunk comes straight down to the ground, flat-sided: it does not widen there.
- `bevy`, the roots' flanks: fine streaks run out along each root. The grain is not seen stretched into patches at this distance.
- `bevy_under`: each limb curves in even stretches; no single stretch turns more sharply than its neighbours. A limb is still flat-sided, and its corners show as straight lines.
- L4: on open faces the grain's furrows are 1.018 of the tone the paint gives a furrow and its plates 1.005 of a plate's (0.50 of the open samples are furrow); inside corners are 0.60 times as light as open faces; the sparsest triangle has 309 texels per metre.
