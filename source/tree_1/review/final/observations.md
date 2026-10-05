# tree_1 / final: observations

From `sheet.png`, seed 1, 3,554 triangles (850 bark, 384 core, 2,320 leaf), two materials on one 1024 px texture, 1,111 kB. Orthographic tiles are framed at 10.76 m across 512 px (47.6 px per metre); figures read off tiles are by eye and good to about 0.1 m. Numbers marked L1 are printed by `tools/validate.py` for this build, numbers marked L4 are in `out/reports/L4-bevy.json` (the Bevy load test on the exported file), and numbers marked L4c are printed by `tools/view_checks.py` for the `bevy_trunk` tile. The aids are `bevy_aids.png`, `bevy_under_aids.png` and `material_three_quarter_aids.png` beside the sheet, and `benchmarks/out/CommonTree_1_aids.png` and `CommonTree_1_under_aids.png` for the benchmark. All three variants and the benchmark from a player's eye are in `benchmarks/out/tree_variants.png`; the same sheet before the core and the grain is `tree_variants_v1.png`.

## Silhouette

- Designed trunk (brief: five to eight flat sides, leaning 0.15 to 0.8 m, at most 0.9 of its girth below the fork, flare at least 2.0 into at least three roots). L1: 7 sides, radius 0.21 m at 1.3 m, lean 0.33 m, taper 0.80, flare 4.3 in 4 roots. front: a brown column about 0.4 m wide at 1.3 m that runs up and to the right, 0.3 m off its foot by the fork, and spreads to about 1.3 m across at the ground. clay_wire_front: the trunk's sides are long quads between six rings, with a narrow strip between sides; the roots are triangular fins at the ground.
- Visible branch skeleton (brief: fork at 2.0 to 3.5 m, at least three limbs, tapering to at most 0.8, bark at least 2% of what is seen above the fork from six of seven views). L1: fork at 2.4 m, 10 limbs in the busiest slice (twigs included), limb taper 0.62; bark seen: front 0.060, right 0.078, back 0.073, left 0.069, three_quarter 0.042, three_quarter_back 0.049, below 0.059. front and right: every pad hangs on a limb that can be followed back to the trunk.
- Separate pads (brief: three to six, each of at least 40 pieces, sky 20% to 50% of the canopy's outline from five of six views). L1: five (165, 124, 113, 110 and 68 pieces), none stray; sky: front 0.39, right 0.41, back 0.39, left 0.41, three_quarter 0.29, three_quarter_back 0.32. front: five pads: one at the top left (its middle about 6.2 m up), one right of it at about 5.6 m, one mid left at about 5.2 m, and two low, left and right, at about 4.2 m. Background shows between every neighbouring pair, most between the two low pads (about 0.6 m). top: four pads round a gap at the trunk about 0.4 m wide, the fifth under the upper ones.
- Lumpy pads over cores (brief: two to four lobes per pad, the widest at least 1.2 times the narrowest; pads at least 1.3 times as wide as tall; the widest pad at least 1.4 times the narrowest; core at most 10% of the foliage seen from the side). L1: pads 2.77, 2.54, 2.21, 2.55 and 1.81 m wide, 1.61 to 2.05 times as wide as tall, the widest 1.53 times the narrowest; cores per pad 3, 3, 4, 2 and 4, widest over narrowest 1.36 to 2.25; core seen: front 0.059, right 0.047, back 0.060, left 0.061, three_quarter 0.046, three_quarter_back 0.044. front and right: no pad's outline is one arc; each has two or three humps along its top and a ragged lower edge hanging 0.3 to 0.5 m below its widest line. Between pieces the pads show dark green: in the bevy tile the gaps on a pad's lit side are dark, and none that I can find shows the ground or the sky through a pad.
- Leaf-shaped pieces (brief: flat, pointed, notched, 0.35 to 0.9 m, pointing out and down). L1: 580 pieces, 0.48 to 0.83 m long, all flat, all with a corner of 60 degrees or less and a notch; 0.86 point out of their pad and 0.89 below level. front and right: each pad's lower edge is a row of points hanging down, 8 to 14 across a pad.
- From below (brief: at most 15% of a pad's outline seen into; at least one point per metre of rim clear against the sky; core at most 45% of the foliage seen). L1: seen into each pad 0.031 to 0.093; points per metre of rim 1.68 to 2.49; core 0.365 of the foliage seen from straight below. bevy_under: the leader and two limbs run up the middle of the tile against one dark green mass; the mass's edge against the sky is points, about 30 across the tile's left and upper sides; two pale tips of lit pieces show at the left.
- Bark at arm's length (brief: the typical tone step across the trunk at least 0.021 of the mean and at least 1.16 times the step along it, from 0.5 m). L4c: 0.0263 of the mean tone (floor 0.021; benchmark 0.021 to 0.023); 2.78 times the step along the trunk (floor 1.16). bevy_trunk: the trunk fills the middle third of the tile, lit on its left face: light streaks about 1 cm wide run up it, with darker furrows 10 to 20 cm long between them and the shadows of leaves across them.

## Proportions

- front, right: the tree fills the height of the spec's frame from the ground line to 7.0 m, and its width; L1 finds the bounds exact to a millimetre (4.9 m, 4.7 m, 7.0 m).
- The fork is at 2.4 m of 7.0 m; the canopy takes the rest. The trunk at 1.3 m is about 0.4 m across.
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

- Bark `#7a5a44`: L4: open faces 0.998 of the material colour times the tint; the lowest quarter 0.805 times as light as the highest (the tints give 0.784); corners 1.15 times as light as open faces, junctions 0.59 times. L4: mean tone step 0.31 a centimetre across the grain and 0.13 along it; all 112 hand-sized patches show the step and 98% show it at least 1.16 times the step along. L4: the bark's islands use 55.9% of the texture; 253 texels per metre at the sparsest below 2.5 m and 184 above.
- Leaf `#a8b846`: the tops of pads are a light yellow-green, their sides a mid green and their skirts a dark green. L4: 24 colours in use, every piece on the palette, 0.83 of pieces with a nearest neighbour of another colour, the highest quarter of each pad at least 3.11 times as light as its lowest (the tints give 3.60), blue 0.098 of the colour below against 0.066 above.
- Core: L4: one colour, luminance 0.075 against 0.100 for the darkest leaf piece.

## Scale

- scale: the tree is 3.9 times the figure's height. Brief: 7.0 m over 1.8 m is 3.9.
- scale: the fork is above the top of the figure's head.

## In the engine (bevy)

- bevy and bevy_back: pads are light on top and dark under their skirts; the gaps between pieces on a pad's lit side are dark green. Against the Blender material tiles, Bevy's foliage is lighter and yellower on top and its shadow side is darker; the bark is the same brown. The canopy's shadow on the ground is solid blots joined by the limbs' shadows, and I can find no hole of light inside a pad's shadow at this tile's size.
- bevy_under: foliage from below is never black: green channel least 36, darkest 1% 39, median 45 of 255 (the benchmark from the same place: least 41, median 53). Ours is a step darker than the benchmark's underside.
- bevy_trunk: see Silhouette. Beside the benchmark's trunk from the same camera (`tree_variants.png`, fourth column), ours has more contrast between furrow and ridge and softer edges; the benchmark's lines are thinner and sharper.

## Values (value maps)

- bevy: four masses. The lit tops of the pads are the lightest thing in the image; the pads' skirts and undersides are a step darker than the ground; the trunk and limbs are dark lines; the cast shadow is the darkest large shape. No pad vanishes into the ground or into another pad.
- bevy_under: two masses, the canopy as one dark shape with a serrated edge and the sky; the limbs sit inside the dark shape, a little lighter where the sun reaches them. The benchmark from the same place is the same two masses, with a rounder, finer-toothed edge.
- Benchmark, standard view (`CommonTree_1_aids.png`): two masses, one dark canopy with light specks on its lit edge, and the trunk. Its canopy is darker than the ground; ours is lighter than the ground on top.

## At a glance (squint views)

- bevy: "tree with clumps". The eye lands on the top left pad, the lightest and largest, then on the gap between the two low pads.
- bevy_under: "dark leafy roof". The eye lands on the limbs, then on the toothed edge against the sky.
- Benchmark: "round dark tree". The eye lands on the canopy as a whole, then the trunk, which is thicker than ours (about 0.5 m against 0.4 m).

## Differences from the brief

- The fork is at 2.4 m against the brief's 2.0 to 3.5 m: inside, and the measure of this variant nearest a limit (the generator refuses under 2.2 m).
- The bark reads as bark from 0.5 m by measurement and in the tile, but it is softer than the benchmark's: at 250 texels per metre a furrow's edge is a blur about 1 cm wide. The brief's numbers are met; whether the softness is acceptable is the owner's to judge on `tree_variants.png` and `tree_bark_study.png`.
- From straight below, 36% of the foliage seen is core (limit 45%). The pads read as dark masses with leafy rims, and pieces inside a pad's outline are dark on dark: they can be made out in the tile but do not read one by one.
- No other mismatch found in the items above.

## After the fixes of 2026-10-05 (review findings 3 and 4)

The leaf material has no gloss, the underside and core tints are about twice as light, and nothing else changed: the mesh's positions, triangle counts and every L1 figure above are as they were. Lines above that describe `bevy_under` or the underside's tone are from before; these replace them.

- L4d, from 1 m beside the trunk looking 78 degrees up: pale leaf samples (grey and light) are 0.00007 of the leaf samples, before 0.02393 (at most 0.001); foliage over the limbs among it is 1.63, before 1.18 (at least 1.25).
- bevy_under, read with its value map and squint view: no near-white piece; the pieces that were pale (upper left at about x 380, y 240 and left at x 150 to 280, y 600 to 680 of 1024) are now yellow-green, lighter than their neighbours and not grey. Limbs are brown against green and darker than the leaves beside them. In the five-level value map the canopy is one grey and the limbs share that grey over most of their length, with darker patches along the leader (x 560 to 680, y 100 to 450) and the right limb; only the left limb's sunlit flank is a level lighter. So the limbs separate by hue and by their dark grain, not yet by a full level of value. Squint: "trunk under leaves"; the eye lands on the leader.
- bevy, beside the picture saved before: the undersides and skirts of the pads are lighter, so the step from a pad's top to its underside is smaller (L4: 1.63 where the tints give 1.75; before 2.71 where they gave 3.60). The foot is unchanged: one flat-sided skirt about three trunk widths across.
- Differences from the brief still standing: the foot (finding 1), the limbs' elbows (finding 2) and the grain on the foot (finding 5) are not fixed.
