# tree_old_1, final: observations

Read from `benchmarks/out/tree_stages.png` (the Bevy views) and the gate's reports; the sheet's Blender tiles and the review aids were not read by the agent before reporting.

1. **Silhouette**: standard and back views: five pads at four heights with sky between them, the highest alone at the top on a long leader, which makes the top third of the tree a single small pad on a stalk.
2. **Proportions**: the trunk below the fork is about a third of the height; the crown pad is about a quarter of the width.
3. **Scale**: the figure is about a fifth of the tree's height (1.8 / 8.8 = 0.20).
4. **In the engine**: from 0.5 m the trunk fills more than half the tile's width and its roots reach both lower corners; grain reads as dark furrows. From below, five limbs spread from one point.
5. **Beside the mature tree**: taller by about a quarter and clearly thicker in the trunk; its pads are not visibly wider.
6. **Differences from the brief**: none measured by the gate; 5,340 triangles of 6,000; the file is 3.5 MB because of the 2048 px texture.

## After the fixes of 2026-10-05

Not looked at tile by tile after the change; only measured. L4e, from 1 m beside the trunk looking 78 degrees up: pale leaf samples 0.00008 of the leaf samples (at most 0.001); foliage over the limbs among it 1.78 (at least 1.25). The underside and core tints are about twice as light as when the lines above were written.

## After the swept foot and the limbs' rings (branch `treefoot`, 2026-10-05)

Read from the rebuilt `bevy.png`, `bevy_under.png` and `bevy_trunk.png`, and the gate's reports; the Blender tiles of the sheet were opened only for `tree_young_1`. Where a line above speaks of the foot as a skirt or of elbows, this replaces it.

- Triangles: 5,438. L1: 4 roots in 4 ridges, the sharpest turn between two stretches of a limb 15.0 degrees (it was 19.9).
- `bevy`: the foot is four separate roots, thin ridges that run out over the ground from the trunk, with bare ground between them; no skirt joins their tips. Between two roots the trunk comes straight down to the ground, flat-sided: it does not widen there.
- `bevy`, the roots' flanks: fine streaks run out along each root. The grain is not seen stretched into patches at this distance.
- `bevy_under`: each limb curves in even stretches; no single stretch turns more sharply than its neighbours. A limb is still flat-sided, and its corners show as straight lines.
- L4: on open faces the grain's furrows are 1.015 of the tone the paint gives a furrow and its plates 1.007 of a plate's (0.44 of the open samples are furrow); inside corners are 0.55 times as light as open faces; the sparsest triangle has 372 texels per metre.
