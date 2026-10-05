# flower_scatter

A handful of small bright flowers on short stems, each with a few leaves at its foot: an accent of colour a few handspans across, found from across a clearing. Made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its scatters share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/flower_scatter_1`, `source/flower_scatter_2`, `source/flower_scatter_3`. Their specs name this folder as their `family`. One other flower colour is drawn as a palette on the first variant's mesh: `source/flower_scatter_1_violet`.

It is the **flower scatter** row of the nature reference (`docs/style/nature-shapes.md`): "tiny bright flowers, used as an accent". The reference's scenes use one accent colour, in small amounts.

## Purpose

The accent in a clearing or at the foot of a rock: a point of colour in the green. Scattered thinly, a few in sight at once. A player walks through it; it has no collision.

## Viewing

First person (ADR 7). A player's eye is 1.7 m up and the flowers reach the ankle to the shin, so they are seen from standing height looking down, from 0.5 to 6 m away. From 3 m a flower must be found: a spot of colour 7 to 15 cm across, which is 1.5 to 3 degrees of the view there (at 5 to 6 cm, the first size, they were specks and were not found). What must read is the colour, that the spots are at different heights and not in a pattern, and green under them.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Flowers | Each across | Beside a 1.8 m player |
| --- | --- | --- | --- | --- | --- | --- |
| `flower_scatter_1` | 0.5 m | 0.45 m | 0.22 m | 5 to 8 | 0.08 to 0.12 m | two to three handspans across; the tallest flower at the shin; a flower fills a palm |
| `flower_scatter_2` | 0.8 m | 0.7 m | 0.3 m | 7 to 11 | 0.1 to 0.15 m | a short stride across; the tallest flower below the knee; a flower a spread hand |
| `flower_scatter_3` | 0.3 m | 0.28 m | 0.15 m | 3 to 5 | 0.07 to 0.1 m | a handspan and a half across; the tallest flower at the ankle |

A flower is at least 0.14 of its scatter's wider side across. The benchmark's `Flower_3_Group`, measured, has three flowers 0.53 to 0.71 m across on a group 1.5 m wide and 2.0 m tall: 0.4 of its width. Ours were 0.11 (5.6 cm on 0.5 m).

The height is that of the tallest flower. The origin is on the ground at the middle of the bounds.

## Silhouette

1. **Flowers.** Each flower is one bloom: closed, of five rounded petals round a shallow cup, as wide as Real-world size says, filling at most 0.6 of its convex hull. Its petals open nearly flat: no fold between them is deep enough to hold a shadow.
2. **On stems.** Every bloom has a stem in it: a thin strip of the leaf material from the ground.
3. **Above their leaves.** No leaf reaches as high as the lowest point of the lowest bloom.
4. **At different heights.** The lowest bloom's middle is at most 0.75 as high as the highest's.
5. **Leaning different ways.** The typical stem leans at least 4 degrees from upright, and they do not lean together: the mean of the stems' level directions of lean is at most 0.7 of what it would be if all leaned one way.
6. **Apart, and scattered.** No two blooms' middles are nearer than 6 cm: a scatter, not a bunch. And neither a row nor a ring: seen from above the blooms' middles spread at least 0.3 as far across the scatter as along it, and their distances from its middle differ, the spread of those distances being at least 0.3 of their mean, as the lily pads' discs. (The second variant's flowers first stood on a ring, which read 0.25, and no check said so.)
7. **Leaves at the foot.** Two to four leaf pieces at the foot of each stem, each starting within 3 cm of the ground: twice to four times as many leaves as flowers.
8. **Colour.** The flowers' colour is at least 0.3 from every colour of the leaves' palette, in linear RGB.

## Style and colour

ADR 9: leaf-shaped geometry in flat colour, no cards and no transparency. The benchmark's flowers are cards.

- **Petal** `m_flower_petal`, `#d8b840`, a warm yellow: the closed surface, with painted shading (ADR 10): duller toward the ground (`#c8b8a0`), so the low flowers are a little darker than the tall ones, light on the petals' edges. Every face of a petal is lit as itself, flat, as a leaf piece is.
- **Leaf** `m_flower_leaf`, `#78a44a`: the stems and the leaves, each piece one flat colour from the palette (ADR 11), the stems light and the leaves at the foot darker and bluer (underside tint `#7fa0a8`), 4 shades in 3 tones up to 12% lighter or darker.
- No plate or mound under the flowers.

## Colours

Another flower colour is a palette on a variant's mesh (ADR 13), as the lily pads' is.

| Asset | Colour | Petal |
| --- | --- | --- |
| `flower_scatter_1` | yellow | `#d8b840` |
| `flower_scatter_1_violet` | violet | `#8a6cd0`, an unnatural one for a deep layer |

## Parts

One object and one mesh per variant, with two materials. The leaf material holds the stems and the leaves, each an open piece (`open_materials`). The petal material is the closed surface: each bloom is one closed piece.

## Budget

An accent, small on screen: a bloom is 40 triangles, a stem 3 and a leaf 4, at most 59 to a flower. At most 480, 660 and 300 triangles (first 300, 400 and 180, for a five-pointed star of 20), two materials and one 128 px texture. The benchmark's `Flower_3_Group` is 755 triangles, as cards, and 2 m tall.

## References

- Look: `docs/style/nature-shapes.md`, Flower scatter.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Flower_3_Group.gltf`. A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/flower_scatter_variants.png`; twelve seeds of the first variant in `benchmarks/out/flower_scatter_1_candidates.png`.

## Out of scope

Wind, buds, seed heads, a flower's middle in a second colour, LODs.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives the rest.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"flower_scatter"` | This brief |
| `season` | `"summer"` | In flower |
| `colour` | `"yellow"` | Colours |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `materials.m_flower_petal` | `"#d8b840"` | Style and colour: petal |
| `materials.m_flower_leaf` | `"#78a44a"` | Style and colour: leaf |
| `painted_shading.texture_px` | `128` | Budget |
| `painted_shading.base_tint` | `"#c8b8a0"` | Style and colour: duller toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour |
| `painted_shading.edge_light` | `0.1` | Style and colour: light on the petals' edges, under the texel range |
| `painted_shading.edge_width_m` | `0.002` | A petal is 3 to 5 cm wide: a band of 2 mm along each edge |
| `painted_shading.hidden_underside` | `true` | As every plant |
| `foliage.material` | `"m_flower_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.12` | Silhouette 6: flowers of one scatter stand a hand apart at most |
| `foliage.min_pad_pieces` | `8` | Real-world size: at least 3 flowers, each a stem and two leaves or more |
| `foliage.piece_m` | `[0.03, 0.35]` | A leaf at the foot is 3 cm or more; the longest stem is the scatter's height and a little more for its lean |
| `foliage.under_tint` | `"#7fa0a8"` | Style and colour |
| `foliage.top_tint` | `"#ffffff"` | Style and colour |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.12` | Style and colour |
| `blooms.max_hull_share` | `0.6` | Silhouette 1 |
| `blooms.min_colour_apart` | `0.3` | Silhouette 8 |
| `flowers.max_height_share` | `0.75` | Silhouette 4 |
| `flowers.min_lean_deg` | `4.0` | Silhouette 5 |
| `flowers.max_lean_together` | `0.7` | Silhouette 5 |
| `flowers.min_apart_m` | `0.06` | Silhouette 6 |
| `flowers.min_scatter` | `0.3` | Silhouette 6 |
| `flowers.min_bloom_share` | `0.14` | Real-world size |
| `flowers.leaves_per_bloom` | `[2.0, 4.0]` | Silhouette 7 |
| `flowers.foot_m` | `0.03` | Silhouette 7 |
| `soft_edges` | `false` | Style and colour: a petal's faces are lit flat, hard edges by design |
| `watertight` | `true` | Parts: a bloom is closed |
| `open_materials` | `["m_flower_leaf"]` | Parts: stems and leaves are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **A flower is a bloom on a stem**, as a seed head is a head on a stalk: the bloom a closed piece of the closed material, the stem an open strip of the foliage. The lily pads' `blooms` block checks the blooms; a `flowers` block checks what is this family's own. The tall grass's `heads` was not reused: its lint asks for blades from one point or stalks in a bed, and these are neither.
- **Thresholds made up here, with nothing measured behind them**: every number in the `flowers` and `blooms` blocks, `piece_m`, `min_pad_pieces` and `max_triangles`.

Not measured, and judged on the contact sheet and the candidates sheet: whether the flowers read as flowers from standing height, and whether twelve seeds are twelve scatters.
