# lily_pad

A group of lily pads floating on still water: flat round leaves of clearly different sizes, each with a raised rim and a notch, all at one level, with one or two flowers standing between them. Made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its groups share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/lily_pad_1`, `source/lily_pad_2`, `source/lily_pad_3`. Their specs name this folder as their `family`. One other flower colour is drawn as a palette on the first variant's mesh: `source/lily_pad_1_pink`.

It is the **lily pad** row of the nature reference (`docs/style/nature-shapes.md`): "a flat disc with a raised rim, from hand-sized to large enough to stand on, with flowers between". The reference's swamp scene uses pink lilies as its one accent colour.

## Purpose

Dressing for still water: pools and the edges of flooded ground. The largest variant carries one pad a player can stand on, as the game has players standing on things (ADR 7: climbing on any surface). Whether a pad bears a player's weight, and its collision shape, are the game's (ADR 8); the asset only makes the pad wide enough and level.

## Viewing

First person (ADR 7). A player's eye is 1.7 m up and the pads lie on the water at the player's feet, so a group is seen two ways and never from the side: from standing height looking down, from the bank 1 to 6 m away, as light discs on dark water with a point of flower colour; and, on the largest variant, from on top of the big pad, looking straight down at its floor and rim and across at the smaller pads round it. Nothing is seen from below.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Pads | Widest pad | Beside a 1.8 m player |
| --- | --- | --- | --- | --- | --- | --- |
| `lily_pad_1` | 1.1 m | 0.9 m | 0.09 m | 5 to 7 | 0.35 to 0.6 m | a group a stride across; the widest pad a serving tray |
| `lily_pad_2` | 1.8 m | 1.5 m | 0.12 m | 6 to 9 | 0.6 to 1.0 m | a group as long as the player is tall; the widest pad a cafe table, too small to stand on with both feet apart |
| `lily_pad_3` | 3.0 m | 2.6 m | 0.16 m | 7 to 10 | 1.2 to 1.7 m | the widest pad is two thirds of the player's height across or more: room for both feet and a step |

On every variant the narrowest pad is hand-sized, 0.08 to 0.2 m across. The height is that of the taller flower; the pads themselves stand 1 to 7 cm above the water. The origin is on the water's surface at the middle of the bounds: the pads' floors float 1.2 cm above it, so they do not flicker against the water, and the middle of the largest pad dips to it.

## Silhouette

Seen from above, which is how it is seen.

1. **Discs.** Each pad is one disc: a round, level floor with a raised rim. Its rim stands 0.02 to 0.08 of the disc's width above its floor. Round, not a compass circle: the nearest point of its outline is at least 0.7 as far from its middle as the furthest.
2. **A notch.** Each disc has one notch cut from its rim in to its middle, 15 to 60 degrees wide.
3. **One level.** Every disc's floor lies within 2 cm of one height, and no part of a floor is more than 2 cm from it. No disc lies over another: seen from above no two overlap.
4. **A run of sizes.** From hand-sized to the widest, with no step of more than 2.0 times between one size and the next, and at most one pair of twins (two within a tenth of each other in width).
5. **Scattered.** Not a row and not a ring: the middles of the discs spread at least 0.3 as far across the group as along it, and their distances from the group's middle differ, the spread of those distances being at least 0.3 of their mean.
6. **Flowers between.** One flower on the smallest variant and two on the others: a closed star of pointed petals, a low open ring round a raised pointed middle, standing on the water between the pads and not on one. A flower fills at most 0.6 of its convex hull: petals, not a ball.
7. **The pad to stand on** (`lily_pad_3`). Its widest disc is at least 1.2 m across and its floor is level, as 3 asks of every disc. Seen from straight above, at least 0.6 of the whole group is within 12 degrees of level (`top`): the rest is rims and flowers.
8. **Flat.** The group is no taller than a tenth of its wider side (`low`).

## Style and colour

ADR 9: leaf-shaped geometry in flat colour, no cards and no transparency.

- **Pad** `m_lily_pad`, `#6fa04c`: the colour of the widest disc. Each disc is one flat colour from the palette in the texture (ADR 11), 4 shades in 3 tones up to 8% lighter or darker. The painter picks a piece's shade from how high it sits, and a wider disc's rim stands higher, so the wide discs are the light yellow-green and the small ones a little darker and bluer (underside tint `#b4d0c8`, a mild one: nothing here is in shadow).
- **Flower** `m_lily_flower`, `#d8d0c6`, a warm white: the closed surface, with painted shading (ADR 10): rosy toward the water (`#c9a8b4`) and plain at the petal tips, a little light on the petals' edges and shadow in the cup. White is kept under the texel range's 240, which is why it is not whiter.
- The flower's colour is far from every colour of the pads' palette: at least 0.3 apart in linear RGB.
- No plate under anything, of mud or of water: the reeds' mud plate was the first thing the eye landed on. What is between the pads is the game's water.

## Colours

Another flower colour is a palette on a variant's mesh (ADR 13). A spec names its `colour`; a colour variant names its base as `palette_of` and a colour that is not its base's, and may differ from it only in what a season may.

| Asset | Colour | Flower | Toward the water |
| --- | --- | --- | --- |
| `lily_pad_1` | white | `#d8d0c6` | `#c9a8b4` |
| `lily_pad_1_pink` | pink | `#e0709c`, the reference's swamp accent | `#b07090` |

## Parts

One object and one mesh per variant, with two materials. The pad material holds the discs, each an open piece (`open_materials`). The flower material is the closed surface: each flower is one closed piece.

## Budget

Cheap dressing, seen at the player's feet and often several groups at once: at most 320, 420 and 500 triangles, and two materials on one 128 px texture: the smallest that holds a flower at the conventions' 100 texels a metre, since the palette's strip takes 24 px of it and the gap round an island 8 px (at 64 px the first variant's 14 cm flower was painted at 11 texels a metre). A disc is three triangles a side, of 8 to 16 sides by its size: 24 to 48. A flower is 40. The benchmark's nearest things, its clover and flower groups, are flat cards.

## References

- Look: `docs/style/nature-shapes.md`, Lily pad; `docs/style/refs/nature-shapes/`.
- Comparison: `benchmarks/out/lily_pad_variants.png`; twelve seeds of the first variant in `benchmarks/out/lily_pad_1_candidates.png`.

## Out of scope

Water, ripples, stalks under the water, a pad's veins, buds, LODs, wind, collision.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives the rest.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"lily_pad"` | This brief |
| `season` | `"summer"` | Lilies flower in summer |
| `colour` | `"white"` | Colours |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `materials.m_lily_flower` | `"#d8d0c6"` | Style and colour: flower |
| `materials.m_lily_pad` | `"#6fa04c"` | Style and colour: pad |
| `painted_shading.base_tint` | `"#c9a8b4"` | Style and colour: rosy toward the water |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: plain at the tips |
| `painted_shading.edge_light` | `0.1` | Style and colour: a little light on the petals' edges, under the texel range |
| `painted_shading.edge_width_m` | `0.003` | A petal is 2 to 5 cm wide: a band wider than 3 mm leaves it no open face |
| `painted_shading.crevice_shadow` | `0.4` | Style and colour: shadow in the cup |
| `painted_shading.crevice_width_m` | `0.006` | A band 6 mm wide, for the same reason |
| `painted_shading.hidden_underside` | `true` | A flower stands on the water |
| `foliage.material` | `"m_lily_pad"` | Parts |
| `foliage.pad_gap_m` | `0.15` | Silhouette 5: the discs of one group lie close; 15 cm of clear water parts two groups |
| `foliage.min_pad_pieces` | `4` | Real-world size: a group is at least 5 discs, and a stray one may lie apart |
| `foliage.under_tint` | `"#b4d0c8"` | Style and colour: a little darker and bluer |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the pad colour itself for the widest disc |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.08` | Style and colour |
| `discs.narrowest_m` | `[0.08, 0.2]` | Real-world size: hand-sized |
| `discs.max_size_step` | `2.0` | Silhouette 4 |
| `discs.max_twins` | `1` | Silhouette 4 |
| `discs.level_m` | `0.02` | Silhouette 3 |
| `discs.rim_share` | `[0.02, 0.08]` | Silhouette 1 |
| `discs.notch_deg` | `[15.0, 60.0]` | Silhouette 2 |
| `discs.min_round` | `0.7` | Silhouette 1 |
| `discs.min_scatter` | `0.3` | Silhouette 5 |
| `blooms.max_hull_share` | `0.6` | Silhouette 6 |
| `blooms.min_colour_apart` | `0.3` | Style and colour: far from the pads' palette |
| `low.max_height_share` | `0.1` | Silhouette 8 |
| `top.min_level_share` | `0.6` | Silhouette 7 |
| `soft_edges` | `true` | Discs and flowers are lit smooth |
| `watertight` | `true` | Parts: a flower is closed |
| `open_materials` | `["m_lily_pad"]` | Parts: discs are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **A lily pad is a disc** (`CONTEXT.md`), not a pad: a pad is already a clump of leaf pieces. A disc is one open piece of the foliage material and takes one palette colour, as a blade does.
- **A flower is a bloom**: one closed piece of the closed material, as a seed head is, so that it has a colour of its own whatever the pads' palette is. It floats: no stalk is drawn.
- **A group of discs is checked by a `discs` block of its own**, not as blades, stalks or pads over cores, and its flowers by a `blooms` block. `low` and `top` are the pebble's and the slab's checks, reused as they are.
- **The colour of a disc follows its size**, through its rim's height: this is what the painter's rule (shade by height) gives a flat thing, not a choice.
- **Every variant has a flower**: an asset with open pieces needs a closed surface, and no plate is wanted.
- **Thresholds made up here, with nothing measured behind them**: every number in the `discs` and `blooms` blocks, `low.max_height_share`, `top.min_level_share`, the size ranges and `max_triangles`.

Not measured, and judged on the contact sheet and the candidates sheet: whether a group reads as scattered and not constructed, and whether twelve seeds are twelve groups.
