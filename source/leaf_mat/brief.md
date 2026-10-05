# leaf_mat

A flat, irregular patch of small overlapping leaves growing on the ground or on water: ground cover, a few centimetres thick, creeping out from its middle along thin runners, its leaves in pairs along them, with a ragged outline and gaps in it. Made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its mats share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/leaf_mat_1`, `source/leaf_mat_2`, `source/leaf_mat_3`. Their specs name this folder as their `family`.

It is the **leaf mat** row of the nature reference (`docs/style/nature-shapes.md`): "a flat patch of small leaves lying on the ground or water".

## Purpose

The lowest of the three heights of growth: what covers bare ground at the foot of trunks and rocks, and floats at the edge of still water. Many mats lie side by side and over each other's edges. A player walks over it; it has no collision.

## Viewing

First person (ADR 7). A player's eye is 1.7 m up and a mat lies at the player's feet, so it is seen from standing height looking down, from 0.5 to 5 m away, and never from the side or from below. From there it must read as a plant that grows there, not as a green plate and not as leaves that fell there: its leaves in rows along its runners, its outline ragged, ground showing through it.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `leaf_mat_1` | 0.7 m | 0.6 m | 0.04 m | a doormat: one stride across |
| `leaf_mat_2` | 1.2 m | 1.0 m | 0.05 m | two thirds of the player's height across: two strides |
| `leaf_mat_3` | 0.4 m | 0.35 m | 0.03 m | a dinner plate and a half: under one foot and round it |

The origin is on the ground at the middle of the bounds.

## Silhouette

Seen from above, which is how it is seen.

1. **Small leaves.** Each leaf is one flat, pointed, notched leaf piece 0.05 to 0.14 m long: a hand's breadth. At least 20 of them, with no clear air of 6 cm between neighbours: one mat.
2. **Lying.** Every leaf lies within 25 degrees of level.
3. **Flat.** The mat is no taller than 0.08 of its wider side (`low`).
4. **Overlapping.** Seen from above, at least half of the leaves lie partly over or under another.
5. **Ragged, with gaps.** Seen from above, the leaves cover 0.45 to 0.8 of the convex hull of what they cover: a disc or a rectangle of leaves covers all of its own, and a few scattered leaves almost none.
6. **A patch.** The leaves cover at least 0.3 of the bounds' footprint.
7. **Runners.** Four to six runners creep out from the middle of the mat, each in two or more straight lengths a hand or so long with a turn between them and here and there a side length at a turn, each length a thin closed spindle. They are what the closed surface is; no plate lies under the mat.
8. **Growing.** The leaves stand along the runners in pairs, one either side, pointing away from the runner and toward its end, with a leaf at the end: at least 0.8 of the leaves start within 2 cm of a runner and point away from it. Denser at the middle, where the runners are close, and ragged at the edge, where each ends on its own. (First: leaves at chance places pointing every way, which read as leaves that had fallen there.)

## Style and colour

ADR 9: leaf-shaped geometry in flat colour, no cards and no transparency.

- **Leaf** `m_mat_leaf`, `#7da348`: the colour of the uppermost leaves. Each leaf is one flat colour from the palette in the texture (ADR 11): the leaves on top light, those under them darker and bluer (underside tint `#7fa0a8`), 4 shades in 3 tones up to 12% lighter or darker.
- **Runner** `m_mat_runner`, `#7a6a48`, a dull olive brown: the closed surface, with painted shading (ADR 10), darker toward the ground (`#a8a098`).
- Another leaf colour (autumn, a deep layer's blue) would be a palette on the same mesh (ADR 13); none is built.

## Parts

One object and one mesh per variant, with two materials. The leaf material holds the leaves, each an open piece (`open_materials`). The runner material is the closed surface.

## Budget

The cheapest foliage there is, laid by the dozen: a leaf is 4 triangles and a length of runner 12. Leaves 9 to 14 cm long that cover a third of the footprint are about 170 to the square metre, and a length of runner, at 12 triangles, costs as much as the three leaves it carries, so at most 420, 880 and 280 triangles, with two materials and one 128 px texture. (First set at 320, 560 and 180, before the leaves were counted, and then at 340, 720 and 200 with two runners.)

## References

- Look: `docs/style/nature-shapes.md`, Leaf mat.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Clover_1.gltf` (379 triangles): the nearest thing in the pack, and it stands up on stalks. A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/leaf_mat_variants.png`; twelve seeds of the first variant in `benchmarks/out/leaf_mat_1_candidates.png`.

## Out of scope

Leaves that move, a mat that follows uneven ground, flowers, other colours, LODs.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives the rest.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"leaf_mat"` | This brief |
| `season` | `"summer"` | Style and colour: green |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `materials.m_mat_runner` | `"#7a6a48"` | Style and colour: runner |
| `materials.m_mat_leaf` | `"#7da348"` | Style and colour: leaf |
| `painted_shading.texture_px` | `128` | Budget |
| `painted_shading.base_tint` | `"#a8a098"` | Style and colour: darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour |
| `painted_shading.edge_light` | `0.2` | As the tall grass |
| `painted_shading.edge_width_m` | `0.002` | A runner is 1.4 cm thick |
| `painted_shading.hidden_underside` | `true` | The mat lies on the ground |
| `foliage.material` | `"m_mat_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 1 |
| `foliage.min_pad_pieces` | `20` | Silhouette 1 |
| `foliage.piece_m` | `[0.05, 0.14]` | Silhouette 1 |
| `foliage.under_tint` | `"#7fa0a8"` | Style and colour |
| `foliage.top_tint` | `"#ffffff"` | Style and colour |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.12` | Style and colour |
| `mat.max_tilt_deg` | `25.0` | Silhouette 2 |
| `mat.min_overlap_share` | `0.5` | Silhouette 4 |
| `mat.hull_cover` | `[0.45, 0.8]` | Silhouette 5 |
| `mat.min_footprint_cover` | `0.3` | Silhouette 6 |
| `mat.runner_reach_m` | `0.02` | Silhouette 8 |
| `mat.min_growing_share` | `0.8` | Silhouette 8 |
| `low.max_height_share` | `0.08` | Silhouette 3 |
| `soft_edges` | `true` | The runners are lit smooth |
| `watertight` | `true` | Parts: a runner is closed |
| `open_materials` | `["m_mat_leaf"]` | Parts: leaves are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **A mat is leaf pieces lying down**, the tree's own leaf piece, checked by a `mat` block of its own and not as pads over cores: it has no core, no lobes and nothing to see from below. `low` is the pebble's check, reused as it is.
- **The closed surface is the runners**, which are what the leaves grow from; a plate under the leaves is what the owner refused under the reeds.
- **No crevice shadow is asked**: a runner is a convex spindle.
- **Thresholds made up here, with nothing measured behind them**: every number in the `mat` block, `low.max_height_share`, `piece_m`, `min_pad_pieces` and `max_triangles`.

Not measured, and judged on the contact sheet and the candidates sheet: whether it reads as leaves on the ground from standing height.
