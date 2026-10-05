# tree_1, tree_2, tree_3 / final: review

Two reviewers that did not build the trees, on 2026-10-05, each given only the briefs, specs, sheets and tiles, reports and exported files (the `asset-review` skill). **A** asked whether each tree matches its brief; **B** checked the skill's list of smells. This file covers all three variants; `tree_2` and `tree_3` point here.

The measurements are the reviewers'. The reconciling agent looked at `benchmarks/out/tree_stages.png` and `tree_seasons.png` and saw the plinth-like foot, the pale pieces under `tree_1` and the dark underside there; it re-measured nothing else. No finding was shown to be wrong, so every one is accepted, and nothing has been fixed yet. Approval is the owner's and has not been given.

## Findings

### To fix in the asset

| # | Finding | By | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 1 | The trunk's foot is one flat-sided ring that meets the trunk at a hard corner: a plinth on `tree_1` and `tree_3`, a four-point star on `tree_2`, not roots. | B | `bevy`: the skirt is about three trunk widths across | Fix in the generator. |
| 2 | Limbs seen from below are straight prisms with elbows; the trunk outline kinks at a ring. | B | `bevy_under`: `tree_1` main limb one hard ridge at x≈600, y 100–500; `tree_3` left limb kinks at (240,740) and (190,560). `bevy_trunk`: kinks on `tree_2` (y≈625) and `tree_3` (y≈655) | Fix in the generator: bark has 642 to 850 of 4,000 triangles, and 450 to 1,200 are unspent. |
| 3 | A few leaf pieces under the canopy are near-white among dark neighbours, lighter than any underside swatch. | A, B | `bevy_under`: `tree_1` 4,750 to 6,350 px at about RGB (160,168,148) against a leaf median of 35/255; `tree_2` 2,516 px; `tree_3` 148 px | Fix: find why (a piece lit on its sunward face and seen from behind is the likely cause, not checked). Escaped defect: see Retrospective. |
| 4 | From below, bark and leaf undersides have the same value, so limbs do not stand out from foliage. | B | `bevy_under`: leaf median luminance 0.023 to 0.025, bark 0.023 to 0.024; one grey in `bevy_under_aids` | Fix or question 1. The brief asks for "the branch skeleton against" the canopy when looking up. Escaped defect: see Retrospective. |
| 5 | Grain on `tree_1`'s foot runs about 30° off the trunk's, with a visible break at the join. | B | `bevy`, `tree_1` | Fix with finding 1. |

### To change in the brief

| # | Finding | By | Evidence | Outcome |
| --- | --- | --- | --- | --- |
| 6 | `tree_1`: "five pads at five heights" is three levels. | A | Pad mid-heights 6.28, 5.30, 5.21, 3.83, 3.82 m | Correct the sentence, or question 2. |
| 7 | `tree_3`: "the lowest two under 2 m" is wrong: the lowest pad is 2.57 × 2.72 m and the two small ones sit above it. | A | Pad boxes at 4.39, 5.32 and 5.50 m | Correct the sentence. |
| 8 | "Bark fills the view at arm's length": bark is half the trunk tile. | A | `bevy_trunk`: 58%, 51%, 50% | Reword: the sentence describes standing against the trunk, the tile is 0.5 m away. |
| 9 | "Each variant's bounds say which way" it leans: they do not. | A | L4 bounds centres are 0.05 to 0.1 m off the origin against a lean of 0.32 to 0.42 m | Drop the clause. |
| 10 | Numbers in the prose with no row in a Numbers table: the 60° piece corner and its notch, 0.6 m for seen-into, 1.3 m breast height, limb taper stations, 24-triangle core, 4-triangle piece, 0.27 m leaf spacing, the 3,800 generator ceiling, 180 texels per metre on limbs, the 16 px strip, the 4 mm step and `grain_patch_m` 0.15, the viewing distances, and every "It measures" figure in the Seed paragraphs. `grain_width_m` is 0.02 where its row cites streaks 1 cm wide. | A | Briefs against their tables | Give each a row or remove it; reconcile `grain_width_m` with its sentence. |

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

Not done: it follows the owner's verdict. Already known from this review, to hand to the `asset-checks` skill: findings 3 and 4 were caught by an eye and a number could have caught both (a leaf sample from below far lighter than the lightest underside swatch; bark and leaf value from below closer than a set ratio), so both are escaped defects. Findings 1 and 2 are a starved silhouette that the existing flare and root checks pass; whether a number can catch them is open.
