# grass_tuft

A tuft of grass: a fan of thin blades from one point, made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its tufts share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/grass_tuft_1`, `source/grass_tuft_2`, `source/grass_tuft_3`. Their specs name this folder as their `family`.

It is the nature reference's **grass tuft** (`docs/style/nature-shapes.md`): "a fan of thin blades; also tall dry grass and reeds". Its foliage is blades (`CONTEXT.md`), as the blade plant's is (`source/blade_plant/brief.md`), and it is held to the same checks with its own limits.

## Purpose

The lowest of the three heights of growth: ground cover at the foot of every trunk, bush and rock. It is the commonest plant there is: hundreds are on screen at once. A player walks through it. Nothing cuts it yet, and it does not move in the wind.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 1 to 10 m; beyond that a tuft is a few pixels. A player's eye is 1.7 m up, so a tuft is looked down on, and the tall one is looked across at from a few metres.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `grass_tuft_1` | 0.5 m | 0.5 m | 0.45 m | to the knee; the plain one |
| `grass_tuft_2` | 0.8 m | 0.75 m | 0.9 m | to the hip: tall grass |
| `grass_tuft_3` | 0.35 m | 0.3 m | 0.25 m | over the ankle |

The benchmark's short grass tuft is 0.6 by 0.7 m and 1.3 m tall, and its tall one 1.8 m: taller than ours, for a meadow and not a forest floor. The origin is on the ground at the middle of the rootstock.

## Silhouette

1. **A fan from one point.** Every blade's foot is within 0.1 m of the origin, at the ground. There are at least 12 blades, and they go all round: seen from above, no gap between neighbouring blades is wider than 90 degrees.
2. **Thin, pointed blades.** Each blade is one piece, 0.12 to 1.1 m from foot to tip in a straight line, ending in a point of 60 degrees or less. Its mean width is 0.02 to 0.1 of that length: clearly thinner than a blade plant's leaf (0.08 and up), and wide enough to be seen at all from 3 m (a 0.45 m blade is 1 to 4 cm wide).
3. **Blades stand and splay.** The middle of the tuft stands nearly upright and the outside leans out: every blade leans between 2 and 65 degrees from upright. None stands exactly upright and none lies down. Blades curve a little: the median blade stands off the straight line from its foot to its tip by at least 0.03 of its length.
4. **Colour by blade.** Each blade is one flat colour, neighbours differ, and the taller blades in the middle are a lighter yellow-green and the short outer ones darker and bluer.
5. **A rootstock.** A low mound at the origin, about 0.1 m across, that the blades grow out of: the tuft's closed surface, and the dark middle a player sees looking down into it.

## Style and colour

ADR 9: leaf-shaped geometry in flat colour, no leaf cards and no transparency. The benchmark's grass is cards with a painted, transparent texture; ours is one strip of geometry per blade.

- **Rootstock** `m_grass_rootstock`, `#5c5234`: a dark straw brown, with painted shading (ADR 10): darker toward the ground (`#a8a098`), light along its edges, shadow in its corners.
- **Leaf** `m_grass_leaf`, `#a4bc50`: the colour of the tallest blade, yellower than the blade plant's and the bush's. The underside tint `#6f96a6` is the tree's. 4 shades in 3 tones up to 14% lighter or darker, as the blade plant.
- Blades take their colour from a palette in the rootstock's texture (ADR 11), so dry grass, autumn or another colour is a second texture on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with two materials. The rootstock is the closed surface. The leaf material holds the blades, each an open piece (`open_materials`).

## Budget

At most 250 triangles and two materials, on one 256 px texture. A blade is 5 triangles (two quads and a tip): it bends once and does not fold. 16 to 32 blades are 80 to 160, and the rootstock is 24. The benchmark's tufts are 155 to 622 triangles. Hundreds are on screen, so this is the smallest budget of any plant; the game is expected to batch or instance them (ADR 8: that is the game's side).

## References

- Look: `docs/style/nature-shapes.md`, Grass tuft.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Grass_Common_Short.gltf` (155 triangles, cards). A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/grass_tuft_variants.png`.

## Out of scope

Tall dry grass and reeds as kinds of their own (the catalogue lists them with this family; they are later recipes of this generator), seed heads, wind, LODs, seasonal and colour variants (palette changes on these meshes, ADR 13).

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants.siblings`.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"grass_tuft"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `250` | Budget |
| `materials.m_grass_rootstock` | `"#5c5234"` | Style and colour: rootstock |
| `materials.m_grass_leaf` | `"#a4bc50"` | Style and colour: leaf, the colour of the tallest blade |
| `painted_shading.texture_px` | `256` | Budget |
| `painted_shading.base_tint` | `"#a8a098"` | Style and colour: the rootstock darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top |
| `painted_shading.edge_light` | `0.2` | Style and colour: light along the rootstock's edges |
| `painted_shading.edge_width_m` | `0.002` | The rootstock's faces are about 3 cm wide |
| `painted_shading.crevice_shadow` | `0.5` | Style and colour: shadow in its corners |
| `painted_shading.crevice_width_m` | `0.005` | A band half a centimetre wide |
| `painted_shading.hidden_underside` | `true` | The rootstock stands on the ground |
| `foliage.material` | `"m_grass_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 1: blades from one point have no clear air between their feet, on the tree's 6 cm grid |
| `foliage.min_pad_pieces` | `12` | Silhouette 1: at least 12 blades |
| `foliage.piece_m` | `[0.12, 1.1]` | Silhouette 2: a blade's length |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer for the low blades |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself for the tallest blade |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.14` | Style and colour |
| `blades.width_share` | `[0.02, 0.1]` | Silhouette 2: mean width over length |
| `blades.root_m` | `0.1` | Silhouette 1: from one point |
| `blades.max_gap_deg` | `90.0` | Silhouette 1: all round |
| `blades.lean_deg` | `[2.0, 65.0]` | Silhouette 3: standing and splayed |
| `blades.min_arch` | `0.03` | Silhouette 3: blades curve a little |
| `soft_edges` | `true` | The rootstock and the blades are lit smooth |
| `watertight` | `true` | Parts: the rootstock is a closed surface |
| `open_materials` | `["m_grass_leaf"]` | Parts: blades are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |
| `variants.min_difference` | `0.3` | As the trees |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **Grass is blades**, checked as the blade plant's are, with no new check: thinner, more of them, more upright and less arched.
- **A blade is a strip of geometry, not a card.** It costs 5 triangles where a card of many painted blades costs 2, and it needs no transparency (ADR 9).
- **The rootstock is the closed surface**, as for the blade plant.
- **Thresholds made up here, with nothing measured behind them**: every number in the `blades` block, `piece_m`, `min_pad_pieces` and `max_triangles`.

Not measured, and judged on the contact sheet: whether a tuft reads as grass or as a few spikes.
