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

Not looked at tile by tile after the change; only measured. L4d, from 1 m beside the trunk looking 78 degrees up: pale leaf samples 0.00005 of the leaf samples (at most 0.001); foliage over the limbs among it 1.55 (at least 1.25). The underside and core tints are about twice as light as when the lines above were written.
