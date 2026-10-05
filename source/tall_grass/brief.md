# tall_grass

A clump of tall grass: many long thin blades standing close together and arching over at their tips, with a few seed heads above them, made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its clumps share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/tall_grass_1`, `source/tall_grass_2`, `source/tall_grass_3`. Their specs name this folder as their `family`. One season is drawn as a palette on the first variant's mesh: `source/tall_grass_1_dry`.

It is the "tall dry grass" of the nature reference's **grass tuft** row (`docs/style/nature-shapes.md`): "a fan of thin blades; also tall dry grass and reeds". Its foliage is blades (`CONTEXT.md`), checked as the grass tuft's are (`source/grass_tuft/brief.md`), and it is asked two things more that the grass tuft was not, because the tuft's own review found it "a spiky green tuft; nearer a yucca or a sedge than a soft clump of grass": that it is dense, and that part of it stands upright.

## Purpose

The middle of the three heights of growth: the grass a player wades through, in clearings and at the edge of water. Many clumps stand side by side. Nothing cuts it yet, and it does not move in the wind.

## Viewing

First person (ADR 7). A player's eye is 1.7 m up and a clump reaches the waist to the chest, so it is seen three ways: across a clearing, from 3 to 15 m, as a soft mass with a broken top; from 0.5 m, standing against it and looking down and across at its blades; and from inside it, standing on the clump and looking down past the seed heads into the blades and at the rootstock.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `tall_grass_1` | 1.0 m | 1.0 m | 1.15 m | to the waist |
| `tall_grass_2` | 1.3 m | 1.2 m | 1.4 m | to the chest |
| `tall_grass_3` | 0.8 m | 0.75 m | 1.0 m | to the hip |

The height is that of the seed heads; the leaves stop lower. The benchmark's tall grass is 0.9 by 1.0 m and 1.84 m tall: over a player's head, for a meadow. The origin is on the ground at the middle of the rootstock.

## Silhouette

1. **A dense clump.** At least 40 blades, their feet within 0.25 m of the origin at the ground, going all round: seen from above no gap between neighbouring blades is wider than 60 degrees. Seen from the side, at most half of the clump's outline is sky. The grass tufts show 0.68 to 0.80 of theirs (measured with the same rays), and that is what made them spikes.
2. **Long, thin, pointed blades.** Each blade is one piece, 0.3 to 1.8 m from foot to tip in a straight line, ending in a point of 60 degrees or less. Its mean width is 0.008 to 0.05 of that length: a blade a metre long is 1 to 5 cm wide.
3. **Standing, and arching over.** At least three blades in ten stand within 15 degrees of upright, foot to tip; the grass tufts have at most one in twenty there. None leans more than 60 degrees. Blades leave the rootstock nearly upright and bend outward toward the tip: the median blade stands off the straight line from its foot to its tip by at least 0.05 of its length.
4. **Seed heads.** Three to six thin upright stalks rise above the leaves, each carrying a seed head: a closed spindle 0.06 to 0.2 m long, pointed at both ends. Every head is above 0.7 of the clump's height, and each has a stalk in it.
5. **Colour by blade.** Each blade is one flat colour, neighbours differ, and the tall blades are a lighter yellow-green and the short ones darker and bluer.
6. **A rootstock.** A low mound at the origin that the blades grow out of: the dark middle a player sees looking down into the clump.

## Style and colour

ADR 9: leaf-shaped geometry in flat colour, no leaf cards and no transparency. The benchmark's grass is cards with a painted, transparent texture; ours is one strip of geometry per blade.

- **Straw** `m_tall_grass_straw`, `#b09a5e`: the rootstock and the seed heads, one closed material with painted shading (ADR 10): dark toward the ground (`#8a8278`), so the rootstock is a dull brown, and the plain pale straw at the top, where the seed heads are.
- **Leaf** `m_tall_grass_leaf`, `#9cb64e`: the colour of the tallest blade. The underside tint `#6f96a6` is the tree's. 4 shades in 3 tones up to 14% lighter or darker, as the grass tuft.
- Blades take their colour from a palette in the texture (ADR 11), so dry grass or another colour is a second texture on the same mesh (ADR 13).

## Seasons

The dry grass of the reference is a palette on a variant's mesh. The year's seasons in `conventions.toml` are summer, autumn and winter, and "dry" is not one, so the dry clump names its season as `autumn`: the season grass dries in.

| Asset | Season | Leaf | Underside tint | Straw |
| --- | --- | --- | --- | --- |
| `tall_grass_1` | summer | `#9cb64e` | `#6f96a6` | `#b09a5e` |
| `tall_grass_1_dry` | autumn | `#d8bf62`, a dry gold | `#b08a6a`, darker and browner | `#c2a468` |

## Parts

One object and one mesh per variant, with two materials. The straw material is the closed surface: the rootstock and each seed head are closed pieces of it. The leaf material holds the blades and the seed stalks, each an open piece (`open_materials`).

## Budget

At most 700 triangles and two materials, on one 512 px texture (at 256 px the gaps round the seed heads' small islands leave 0.39 of the texture used, under the 0.4 the conventions ask). A blade is 7 triangles (three quads and a tip): it bends twice. 72 to 84 blades are 504 to 588; a seed stalk is 5 and its head 8; the rootstock is 24. The benchmark's tall grass is 326 and 622 triangles, as cards. Several times a grass tuft's budget, for a plant that is larger, nearer the eye and rarer.

## References

- Look: `docs/style/nature-shapes.md`, Grass tuft.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Grass_Common_Tall.gltf` (326 triangles, cards). A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/tall_grass_variants.png`; twelve seeds of the first variant in `benchmarks/out/tall_grass_1_candidates.png`.

## Out of scope

Wind, LODs, a trampled or cut clump, flowers, other colours than the two here.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants`; a season's gives its palette.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"tall_grass"` | This brief |
| `season` | `"summer"` | Seasons |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `700` | Budget |
| `materials.m_tall_grass_straw` | `"#b09a5e"` | Style and colour: straw |
| `materials.m_tall_grass_leaf` | `"#9cb64e"` | Style and colour: leaf, the colour of the tallest blade |
| `painted_shading.texture_px` | `512` | Budget |
| `painted_shading.base_tint` | `"#8a8278"` | Style and colour: the rootstock dark toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top |
| `painted_shading.edge_light` | `0.2` | As the grass tuft |
| `painted_shading.edge_width_m` | `0.002` | The seed heads' faces are about 1 cm wide |
| `painted_shading.crevice_shadow` | `0.5` | As the grass tuft |
| `painted_shading.crevice_width_m` | `0.005` | A band half a centimetre wide |
| `painted_shading.hidden_underside` | `true` | The rootstock stands on the ground |
| `foliage.material` | `"m_tall_grass_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 1: blades from one clump have no clear air between their feet, on the tree's 6 cm grid |
| `foliage.min_pad_pieces` | `40` | Silhouette 1: at least 40 blades |
| `foliage.piece_m` | `[0.3, 1.8]` | Silhouette 2: a blade's length |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer for the low blades |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself for the tallest blade |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.14` | Style and colour |
| `blades.width_share` | `[0.008, 0.05]` | Silhouette 2: mean width over length |
| `blades.root_m` | `0.25` | Silhouette 1: feet within 0.25 m of the origin |
| `blades.max_gap_deg` | `60.0` | Silhouette 1: all round |
| `blades.lean_deg` | `[0.0, 60.0]` | Silhouette 3: none leans more than 60 degrees |
| `blades.min_arch` | `0.05` | Silhouette 3: arching over |
| `clump.upright_deg` | `15.0` | Silhouette 3: within 15 degrees of upright |
| `clump.min_upright_share` | `0.3` | Silhouette 3: three blades in ten |
| `clump.max_sky_share` | `0.5` | Silhouette 1: at most half of the outline is sky |
| `heads.count` | `[3, 6]` | Silhouette 4: three to six seed heads |
| `heads.size_m` | `[0.06, 0.2]` | Silhouette 4: a head's length |
| `heads.min_height` | `0.7` | Silhouette 4: above 0.7 of the clump's height |
| `soft_edges` | `true` | The rootstock, the heads and the blades are lit smooth |
| `watertight` | `true` | Parts: the rootstock and the heads are closed |
| `open_materials` | `["m_tall_grass_leaf"]` | Parts: blades are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **Tall grass is blades**, checked as the grass tuft's are, and two things more are measured (`clump`): the share of blades near upright and the share of the outline that is sky. Both are numbers the grass tuft fails, taken from its review.
- **A seed head is a closed spindle of the straw material**, not a blade and not foliage: a blade is an open strip that takes a leaf colour from the palette by its height, and a seed head must be straw whatever the leaves are. The checks (`heads`) find a head as a closed piece of the closed material that does not stand on the ground.
- **A blade is a strip of geometry, not a card** (ADR 9).
- **Thresholds made up here, with nothing measured behind them**: `min_pad_pieces`, `piece_m`, every number in the `blades` and `heads` blocks, `clump.upright_deg`, `clump.min_upright_share` and `max_triangles`. `clump.max_sky_share` is set below what the grass tufts measure (0.68 to 0.80), and how far below is made up.

Not measured, and judged on the contact sheet: whether a clump reads as soft.
