# tree_2 / final: observations

From `sheet.png`, seed 11, 2,802 triangles (642 bark, 216 core, 1,944 leaf), two materials on one 1024 px texture, 1,010 kB. Orthographic tiles are framed at 12.1 m across 512 px (42.3 px per metre); figures read off tiles are by eye and good to about 0.1 m. Numbers marked L1 are printed by `tools/validate.py` for this build, numbers marked L4 are in `out/reports/L4-bevy.json` (the Bevy load test on the exported file), and numbers marked L4c are printed by `tools/view_checks.py` for the `bevy_trunk` tile. The aids are `bevy_aids.png`, `bevy_under_aids.png` and `material_three_quarter_aids.png` beside the sheet, and `benchmarks/out/CommonTree_1_aids.png` and `CommonTree_1_under_aids.png` for the benchmark. All three variants and the benchmark from a player's eye are in `benchmarks/out/tree_variants.png`; the same sheet before the core and the grain is `tree_variants_v1.png`.

## Silhouette

- Designed trunk (brief: five to eight flat sides, leaning 0.15 to 0.8 m, at most 0.9 of its girth below the fork, flare at least 2.0 into at least three roots). L1: 7 sides, radius 0.19 m at 1.3 m, lean 0.32 m, taper 0.84, flare 3.7 in 4 roots. front: a brown column about 0.4 m wide at 1.3 m, running up and to the right, 0.3 m off its foot by the fork; limbs leave it at about 2.3 m and run 1.5 to 2 m sideways before they reach a pad. clay_wire_front: the trunk's sides are long quads between six rings, with a narrow strip between sides; the roots are triangular fins at the ground.
- Visible branch skeleton (brief: fork at 2.0 to 3.5 m, at least three limbs, tapering to at most 0.8, bark at least 2% of what is seen above the fork from six of seven views). L1: fork at 2.3 m, 6 limbs in the busiest slice (twigs included), limb taper 0.52; bark seen: front 0.041, right 0.051, back 0.038, left 0.048, three_quarter 0.045, three_quarter_back 0.044, below 0.060. front and right: every pad hangs on a limb that can be followed back to the trunk.
- Separate pads (brief: three to six, each of at least 40 pieces, sky 20% to 50% of the canopy's outline from five of six views). L1: four (190, 134, 90 and 72 pieces), none stray; sky: front 0.35, right 0.29, back 0.35, left 0.29, three_quarter 0.31, three_quarter_back 0.38. front: four pads: the widest at the top right (its middle about 5.3 m up, 3.2 m across), one at the top left about 5.0 m up, one mid left at about 4.3 m and a small one low on the right at about 4.0 m. Background shows between each pair; the widest gap, about 0.7 m, is between the top right pad and the low right one. top: four pads in an arc open to the upper right, with the fork and three limbs in plain sight in the middle: a gap about 1 m wide.
- Lumpy pads over cores (brief: two to four lobes per pad, the widest at least 1.2 times the narrowest; pads at least 1.3 times as wide as tall; the widest pad at least 1.4 times the narrowest; core at most 10% of the foliage seen from the side). L1: pads 3.15, 2.42, 2.21 and 1.94 m wide, 1.58 to 1.95 times as wide as tall, the widest 1.62 times the narrowest; cores per pad 2, 2, 2 and 3, widest over narrowest 1.30 to 1.60; core seen: front 0.049, right 0.045, back 0.053, left 0.068, three_quarter 0.045, three_quarter_back 0.047. front and right: no pad's outline is one arc; each has two or three humps along its top and a ragged lower edge hanging 0.3 to 0.5 m below its widest line. Between pieces the pads show dark green: in the bevy tile the gaps on a pad's lit side are dark, and none that I can find shows the ground or the sky through a pad.
- Leaf-shaped pieces (brief: flat, pointed, notched, 0.35 to 0.9 m, pointing out and down). L1: 486 pieces, 0.50 to 0.82 m long, all flat, all with a corner of 60 degrees or less and a notch; 0.88 point out of their pad and 0.91 below level. front and right: each pad's lower edge is a row of points hanging down, 8 to 14 across a pad.
- From below (brief: at most 15% of a pad's outline seen into; at least one point per metre of rim clear against the sky; core at most 45% of the foliage seen). L1: seen into each pad 0.056 to 0.120; points per metre of rim 2.13 to 3.64; core 0.333 of the foliage seen from straight below. bevy_under: one limb crosses the lower left of the tile and the leader runs up the middle into a pad whose whole outline, about 25 points, stands against the sky; a second pad fills the left edge.
- Bark at arm's length (brief: the typical tone step across the trunk at least 0.021 of the mean and at least 1.16 times the step along it, from 0.5 m). L4c: 0.0258 of the mean tone (floor 0.021; benchmark 0.021 to 0.023); 1.50 times the step along the trunk (floor 1.16). bevy_trunk: the trunk fills the middle of the tile, leaning right, in the canopy's shade: dark brown, with darker furrows 10 to 30 cm long running up it and lighter streaks between; no face of it is one flat tone.

## Proportions

- front, right: the tree fills the height of the spec's frame from the ground line to 6.2 m, and its width; L1 finds the bounds exact to a millimetre (5.5 m, 5.4 m, 6.2 m).
- The fork is at 2.3 m of 6.2 m; the canopy takes the rest. The trunk at 1.3 m is about 0.4 m across.
- Pads are 1.8 to 3.3 m across and 1.1 to 1.8 m tall, skirt included; a piece is a fifth to a third of a pad's width.

## Facing and grounding

- front, right, back, scale: the foot of the trunk sits on the lower edge of the spec's frame, its roots flat on it, with no gap.
- The brief names no front. The origin is at the foot of the trunk; in top the trunk is off the middle of the canopy.

## Topology (clay_wire)

- Trunk: six rings from the ground to the fork, closest together at the foot where the roots curve in. Each supports the bend or the taper.
- Limbs: five rings each; one three-sided twig runs from the end of a limb to each side lobe, and shows only from below.
- Foliage: every piece is four triangles, and in the clay tiles the pads are dense with their edges. The cores cannot be told from the pieces in any clay tile: they are under them.

## Shading (material)

- No bark face is darker or lighter than its neighbours without a lighting reason; L4 finds no position above the ground with two normals, and no triangle whose normals face against its winding.
- Leaf pieces differ in tone from their neighbours within a pad; this is their colour and their own tilt.
- The bark's texture seams do not show as lines in any material tile. In bevy_trunk the grain does not line up across the one seam that runs up the trunk; where it is in view it reads as one more furrow.

## Materials

- Bark `#7a5a44`: L4: open faces 0.973 of the material colour times the tint; the lowest quarter 0.784 times as light as the highest (the tints give 0.781); corners 1.20 times as light as open faces, junctions 0.68 times (the check allows up to 0.70). L4: mean tone step 0.31 a centimetre across the grain and 0.13 along it; 99% of 120 hand-sized patches show the step and 92% show it at least 1.16 times the step along. L4: the bark's islands use 54.2% of the texture; 253 texels per metre at the sparsest below 2.5 m and 231 above.
- Leaf `#a8b846`: the tops of pads are a light yellow-green, their sides a mid green and their skirts a dark green. L4: 24 colours in use, every piece on the palette, 0.83 of pieces with a nearest neighbour of another colour, the highest quarter of each pad at least 2.92 times as light as its lowest (the tints give 3.60), blue 0.095 of the colour below against 0.066 above.
- Core: L4: one colour, luminance 0.075 against 0.100 for the darkest leaf piece.

## Scale

- scale: the tree is 3.4 times the figure's height. Brief: 6.2 m over 1.8 m is 3.4.
- scale: the fork is above the top of the figure's head.

## In the engine (bevy)

- bevy and bevy_back: pads are light on top and dark under their skirts; the gaps between pieces on a pad's lit side are dark green. Against the Blender material tiles, Bevy's foliage is lighter and yellower on top and its shadow side is darker; the bark is the same brown. The canopy's shadow on the ground is solid blots joined by the limbs' shadows, and I can find no hole of light inside a pad's shadow at this tile's size.
- bevy_under: foliage from below is never black: green channel least 35, darkest 1% 39, median 46 of 255 (the benchmark from the same place: least 41, median 53). Ours is a step darker than the benchmark's underside.
- bevy_trunk: see Silhouette. Beside the benchmark's trunk from the same camera (`tree_variants.png`, fourth column), ours has more contrast between furrow and ridge and softer edges; the benchmark's lines are thinner and sharper.

## Values (value maps)

- bevy: four masses. The lit tops of the pads are the lightest thing in the image; the pads' skirts and undersides are a step darker than the ground; the trunk and limbs are dark lines; the cast shadow is the darkest large shape. No pad vanishes into the ground or into another pad.
- bevy_under: two masses, the canopy as one dark shape with a serrated edge and the sky; the limbs sit inside the dark shape, a little lighter where the sun reaches them. The benchmark from the same place is the same two masses, with a rounder, finer-toothed edge.
- Benchmark, standard view (`CommonTree_1_aids.png`): two masses, one dark canopy with light specks on its lit edge, and the trunk. Its canopy is darker than the ground; ours is lighter than the ground on top.

## At a glance (squint views)

- bevy: "wide, low tree". The eye lands on the top right pad, then runs down the long left limb.
- bevy_under: "dark leafy roof". The eye lands on the limbs, then on the toothed edge against the sky.
- Benchmark: "round dark tree". The eye lands on the canopy as a whole, then the trunk, which is thicker than ours (about 0.5 m against 0.4 m).

## Differences from the brief

- Junction shadow shows 0.68 of open tone where the check allows up to 0.70 (54% of the `crevice_shadow` asked for, against a floor of 50%): the thinnest margin of any check on this variant. It is the paint's, measured after the generator, so the generator's margins do not cover it.
- The taper is 0.84 against a ceiling of 0.9, and the generator's own limit of 0.85: inside both, but the nearest of this variant's shape measures to a limit.
- The bark reads as bark from 0.5 m by measurement and in the tile, but it is softer than the benchmark's: at 250 texels per metre a furrow's edge is a blur about 1 cm wide. The brief's numbers are met; whether the softness is acceptable is the owner's to judge on `tree_variants.png` and `tree_bark_study.png`.
- From straight below, 33% of the foliage seen is core (limit 45%). The pads read as dark masses with leafy rims, and pieces inside a pad's outline are dark on dark: they can be made out in the tile but do not read one by one.
- No other mismatch found in the items above.

## After the fixes of 2026-10-05 (review findings 3 and 4)

The leaf material has no gloss, the underside and core tints are about twice as light, and nothing else changed: the mesh's positions, triangle counts and every L1 figure above are as they were. Lines above that describe `bevy_under` or the underside's tone are from before; these replace them.

- L4e, from 1 m beside the trunk looking 78 degrees up: pale leaf samples (grey and light) are 0.00007 of the leaf samples, before 0.00170 (at most 0.001); foliage over the limbs among it is 1.32, before 0.92 (at least 1.25).
- bevy_under: no near-white piece. The left limb (x 0 to 600, y 620 to 900 of 1024) and the leader are darker than the leaves behind them; two lit pieces at about x 880, y 790 are light green, not grey. The left limb is still one straight prism.
- Differences from the brief still standing: the foot (finding 1), the limbs' elbows (finding 2) and the grain on the foot (finding 5) are not fixed.

## After the swept foot and the limbs' rings (branch `treefoot`, 2026-10-05)

Read from the rebuilt `bevy.png`, `bevy_under.png` and `bevy_trunk.png`, and the gate's reports; the Blender tiles of the sheet were opened only for `tree_young_1`. Where a line above speaks of the foot as a skirt or of elbows, this replaces it.

- Triangles: 2,900. L1: 4 roots in 4 ridges, the sharpest turn between two stretches of a limb 13.5 degrees (it was 14.6).
- `bevy`: the foot is four separate roots, thin ridges that run out over the ground from the trunk, with bare ground between them; no skirt joins their tips. Between two roots the trunk comes straight down to the ground, flat-sided: it does not widen there.
- `bevy`, the roots' flanks: fine streaks run out along each root. The grain is not seen stretched into patches at this distance.
- `bevy_under`: each limb curves in even stretches; no single stretch turns more sharply than its neighbours. A limb is still flat-sided, and its corners show as straight lines.
- L4: on open faces the grain's furrows are 1.013 of the tone the paint gives a furrow and its plates 0.997 of a plate's (0.45 of the open samples are furrow); inside corners are 0.58 times as light as open faces; the sparsest triangle has 234 texels per metre.
