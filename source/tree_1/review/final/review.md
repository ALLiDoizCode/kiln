# tree_1, tree_2, tree_3 / final: review

Two reviewers that did not build the trees, on 2026-10-05, each given only the briefs, specs, sheets and tiles, reports and exported files (the `asset-review` skill). **A** asked whether each tree matches its brief; **B** checked the skill's list of smells. This file covers all three variants; `tree_2` and `tree_3` point here.

The measurements are the reviewers'. The reconciling agent looked at `benchmarks/out/tree_stages.png` and `tree_seasons.png` and saw the plinth-like foot, the pale pieces under `tree_1` and the dark underside there; it re-measured nothing else. No finding was shown to be wrong, so every one is accepted. Approval is the owner's and has not been given.

**Outcomes, 2026-10-05 (branch `treefix`).** The owner answered both questions: limbs are to stand out from the leaves, by lightening the leaf undersides and not the bark; `tree_1` keeps its shape and its sentence is corrected. Findings 3, 4 and 6 to 9 are closed. Findings 1, 2, 5 and 10 are **not done**: what was tried and what is known is in their rows. The Outcome column below says where each stands.

## Findings

### To fix in the asset

| # | Finding | By | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 1 | The trunk's foot is one flat-sided ring that meets the trunk at a hard corner: a plinth on `tree_1` and `tree_3`, a four-point star on `tree_2`, not roots. | B | `bevy`: the skirt is about three trunk widths across | **Not done.** Tried in a scratch copy of the generator, not committed: four rings through the flare instead of one, each root's reach falling off toward the trunk as a power (3.5 to 5) of the height, so it sweeps out and is not a straight slope. On a leaning trunk the second ring tipped with the trunk and its low side went 1 cm under the ground; `fit` refuses a tree that does not stand on z = 0, so `tree_1`'s first tree was refused and the seed went on to another, which would have changed `tree_1`'s shape. The foot's rings must be made level before this can be tried again. Whether a number can tell a plinth from roots is still open; a candidate was worked out and not built: the roots' reach beyond the trunk halfway up the flare, over their reach at the ground (a straight slope gives 0.63, the swept foot about 0.53: not far apart). |
| 2 | Limbs seen from below are straight prisms with elbows; the trunk outline kinks at a ring. | B | `bevy_under`: `tree_1` main limb one hard ridge at x≈600, y 100–500; `tree_3` left limb kinks at (240,740) and (190,560). `bevy_trunk`: kinks on `tree_2` (y≈625) and `tree_3` (y≈655) | **Not done.** In the same scratch copy the trunk had ten rings to the fork for six, the leader four for three and each limb six for five, with no more sides. The tree the scratch copy kept for seed 1 had 950 triangles of bark, but it is not `tree_1`'s tree (850), so the two do not compare. `tree_1` has 246 triangles left under the 3,800 the generator keeps, not 446, so rounder limbs (more sides) do not fit it without changing that room. Measured on trees the scratch foot had already changed, so not a result: `tree_old_1` missed its limb-taper room (0.725 against 0.72). |
| 3 | A few leaf pieces under the canopy are near-white among dark neighbours, lighter than any underside swatch. | A, B | `bevy_under`: `tree_1` 4,750 to 6,350 px at about RGB (160,168,148) against a leaf median of 35/255; `tree_2` 2,516 px; `tree_3` 148 px | **Fixed.** The cause was not a piece seen from behind. It is the sun's glare: Bevy's default reflectance on a flat piece the sun grazes, seen from under it, shows the sun and none of the leaf's colour (the pale pixels are grey, greyness 0.77, where the palette's swatches are 0.13 to 0.16). The leaf material now has no gloss (`KHR_materials_specular`, factor 0; ADR 4 amended, for the owner to confirm). New check `view.under_pale` (gate L4d): pale leaf samples were 0.024, 0.0017 and 0.0020 of the three trees' and are 0.00007, 0.00007 and 0.00004; at most 0.001 is allowed. A second, smaller cause was also removed and is not checked: a leaf normal tipped toward the sky on a piece that faces the ground. |
| 4 | From below, bark and leaf undersides have the same value, so limbs do not stand out from foliage. | B | `bevy_under`: leaf median luminance 0.023 to 0.025, bark 0.023 to 0.024; one grey in `bevy_under_aids` | **Fixed**, as the owner decided: undersides lighter, bark unchanged. Underside and core tints are 1.4 times their old values per channel (about twice as light) in every season: more than a little, because removing the gloss also removed a quarter of the underside's light. New check `view.under_limbs` (gate L4d), measured by rays and not by colour, so its numbers are not the reviewer's: foliage over the limbs among it was 1.18, 0.92 and 1.16 and is 1.63, 1.32 and 1.69; at least 1.25 is asked. `tree_2` passes with little room. |
| 5 | Grain on `tree_1`'s foot runs about 30° off the trunk's, with a visible break at the join. | B | `bevy`, `tree_1` | **Not done**, with finding 1. Cause found: the grain's measure round the trunk is metres round each ring, and the ring at the ground is far longer than the one above it, so streaks slant across the flare by the difference. The scratch foot gave every ring of the flare the measure of the ring it ends at; not seen rendered. |

### To change in the brief

| # | Finding | By | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 6 | `tree_1`: "five pads at five heights" is three levels. | A | Pad mid-heights 6.28, 5.30, 5.21, 3.83, 3.82 m | **Corrected**: "five pads on three levels". The shape stays. |
| 7 | `tree_3`: "the lowest two under 2 m" is wrong: the lowest pad is 2.57 × 2.72 m and the two small ones sit above it. | A | Pad boxes at 4.39, 5.32 and 5.50 m | **Corrected**: "the lowest the widest, with two small ones above it". |
| 8 | "Bark fills the view at arm's length": bark is half the trunk tile. | A | `bevy_trunk`: 58%, 51%, 50% | **Reworded**: "bark is about half of what is seen". |
| 9 | "Each variant's bounds say which way" it leans: they do not. | A | L4 bounds centres are 0.05 to 0.1 m off the origin against a lean of 0.32 to 0.42 m | **Dropped.** |
| 10 | Numbers in the prose with no row in a Numbers table: the 60° piece corner and its notch, 0.6 m for seen-into, 1.3 m breast height, limb taper stations, 24-triangle core, 4-triangle piece, 0.27 m leaf spacing, the 3,800 generator ceiling, 180 texels per metre on limbs, the 16 px strip, the 4 mm step and `grain_patch_m` 0.15, the viewing distances, and every "It measures" figure in the Seed paragraphs. `grain_width_m` is 0.02 where its row cites streaks 1 cm wide. | A | Briefs against their tables | **Not done.** |

### Pipeline, not the asset

| # | Finding | By | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 11 | The L1 and L4c reports say `ok: true` with no measurement, so fork, taper, lean, flare, roots, sky share, bark seen, core seen, seen-into and outline difference cannot be confirmed from the record. | A | `L1-mesh.json` (43 checks), `L4c-view.json` (3 checks), all with empty `detail` | Make the reports carry the measured value. |
| 12 | `tree_2`'s trunk tile shows its shadow side: the grain it is there to show is barely legible. | A, B | `bevy_trunk`: value 30 to 42 of 255 on `tree_2`, against 30 to 98 and 30 to 116 | Light or aim that view so the trunk is seen lit. |
| 13 | Wasted triangles and hidden faces cannot be judged: the canopy is solid line in the 512 px wireframe tiles. | B | `clay_wire_*` | A larger or closer wireframe tile for foliage. |
| 14 | `lighter_above` is 2.71 to 3.11 where 3.60 is expected; `tree_3` shows 75% of the ramp asked for. `min_texels_per_m` on `tree_1` is 183.9 against 180. | A | `L4-bevy.json` | Passing with little margin; no action unless the foot and limbs change the numbers. |

### Clean

Scale (7.0, 6.1, 7.7 m read off the figure against 7.0, 6.2, 7.8 m asked), engine match (leaf colour within 5 levels per channel between Blender and Bevy), floating or sunk, material sprawl (2 materials, 2 draw calls), naming, budget (3,554, 2,802, 3,364 of 4,000), pieces, cores, pads, palette, bark texel density at 0.5 m and the file itself. Reviewer A also listed the figure and ground shadow in the scale tiles as unasked-for; they are the pipeline's, not the asset's.

## Questions for the owner

1. Looking up into a tree, should the limbs stand out from the leaves (lighter bark underneath, or lighter leaf undersides), or is one dark mass under the canopy acceptable?
2. Should `tree_1` have pads at five distinct heights, as its brief says, or is three levels with two pairs acceptable and the sentence wrong?

## Retrospective

Not done in full: it follows the owner's verdict. Already known from this review, to hand to the `asset-checks` skill: findings 3 and 4 were caught by an eye and a number could have caught both (a leaf sample from below far lighter than the lightest underside swatch; bark and leaf value from below closer than a set ratio), so both are escaped defects. Findings 1 and 2 are a starved silhouette that the existing flare and root checks pass; whether a number can catch them is open.

Added with the outcomes of 2026-10-05:

- Finding 3's check was written before its red case was run, against the `asset-checks` loop. Its first form counted leaf samples lighter than the palette allows on the side the sun cannot reach. When the case ran (the leaf material with its gloss back), it was NOT CAUGHT: 0.00055 against 0.00030 on the fixed tree, and its limit had by then been raised from 0.0002 to 0.001 to let the fixed trees through. The check was rebuilt on what the defect is (grey, not a leaf's colour) and then separated the two by a factor of 200. A limit moved until the asset passes is the tautology the skill warns of; the red case is what showed it.
- The likely cause the review named for finding 3 was wrong, and so was the first fix made on it. Tracing the pale pixels back to their faces showed most of them on faces the sun does reach.
- Findings 1 and 2: still open whether a number can catch them.
