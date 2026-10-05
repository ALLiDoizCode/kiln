# reeds

A bed of reeds at the water's edge: stiff upright stalks standing a little apart from one another, each carrying a few long leaves that bend away from it, and some topped by a dark, sausage-shaped head (a cattail), made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its beds share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/reeds_1`, `source/reeds_2`, `source/reeds_3`. Their specs name this folder as their `family`. One season is drawn as a palette on the first variant's mesh: `source/reeds_1_winter`.

It is the "reeds" of the nature reference's **grass tuft** row (`docs/style/nature-shapes.md`): "a fan of thin blades; also tall dry grass and reeds". It is not tall grass made taller (`source/tall_grass/brief.md`). Tall grass is blades from one rootstock, three in ten of them within 15 degrees of upright, arching over. A reed bed is stalks: round, rooted across a footprint and nearly all of them within a few degrees of upright, with the leaves coming off the stalks and not out of the ground. So it is not checked as blades (`blades`); it has a block of its own (`stalks`), and shares the tall grass's `clump` and `heads`.

## Purpose

The tallest of the ground plants: a screen at the edge of water and in swamp. A player walks into it and cannot see over it. Many beds stand side by side. Nothing cuts it yet, and it does not move in the wind.

## Viewing

First person (ADR 7). A player's eye is 1.7 m up and a bed reaches from the shoulder to over the head, so it is seen three ways: from outside, across water, from 3 to 20 m, as a row of upright strokes with dark heads near the top; from inside the bed, at 0.5 m, with stalks passing up through the whole picture and leaves crossing it at every angle; and looking up from inside it, along the stalks at the heads against the sky.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `reeds_1` | 0.9 m | 0.8 m | 2.0 m | just over the head |
| `reeds_2` | 1.2 m | 1.1 m | 2.4 m | well over the head |
| `reeds_3` | 0.7 m | 0.6 m | 1.6 m | to the shoulder |

The height is that of the tallest stalk's point. The width and depth are those of the leaves; the stalks' feet take up less. The origin is on the ground at the middle of the bed. The benchmark's tall grass is 0.9 by 1.0 m and 1.84 m tall; it has no reeds.

## Silhouette

1. **Upright.** At least four stalks in five stand within 6 degrees of upright, foot to tip, and none leans more than 10 degrees. Tall grass asks three blades in ten within 15 degrees; the whole bed may lean a little one way, as if from the wind.
2. **A stalk is round.** Each stalk is a tube closed to a point at its top and open at its foot, 0.9 to 2.5 m long and 1.5 to 4 cm across at its foot, at least half as thick one way as the other. A blade is one flat strip; a stalk is seen at the same width from every side.
3. **A bed, not a point.** Six to fourteen stalks, every one standing on the ground (its foot within 3 cm of it), its foot at least 6 cm from its nearest neighbour's and less than 0.3 m from one, the feet spanning at least 0.4 of the bounds' width and of its depth.
4. **Dark heads near the top.** Two to eight of the stalks, between a fifth and seven tenths of them, carry a head: a closed dark-brown sausage 0.14 to 0.4 m long and 3 to 7 cm thick, filling at least half of the cylinder round it (a spindle pointed at both ends fills a third), with the stalk passing through it and ending in a point above it. Every head is above 0.6 of the bed's height.
5. **Leaves come off the stalks.** Every stalk carries one to four leaves, and every leaf is on a stalk: one of its corners is within a stalk's width of one. A leaf is one strip, 0.25 to 1.5 m long, ending in a point of 60 degrees or less, its mean width 0.02 to 0.1 of its length.
6. **Leaves bend out of their plane.** A leaf leaves its stalk steeply, bends outward and droops, and turns sideways as it goes: seen from above, the median leaf stands off the straight line from its foot to its tip by at least 0.05 of that line's length. The tall grass's blades each bend in one upright plane, and from above and from inside that clump is "a star of straight, pointed blades".
7. **Seen through, but a screen.** From the side at most three quarters of the bed's outline is sky.
8. **Colour by piece.** Each stalk and each leaf is one flat colour, neighbours differ, and the high ones are lighter and the low ones darker and bluer.
9. **Mud.** A low dark mound under the bed that the stalks stand in.

Seeds differ in how many stalks there are, how tall each is, which way and how far the bed leans, how the feet are laid out, and how many stalks carry heads.

## Style and colour

ADR 9: geometry in flat colour, no cards and no transparency.

- **Brown** `m_reeds_brown`, `#553a26`: the heads and the mud, one closed material with painted shading (ADR 10): darker toward the ground (`#c8c0b8`), and the plain dark brown at the top, where the heads are. No crevice shadow is asked: the mud is one convex mound and the heads lie apart and make no inside corner, the load test finds none (`painted.crevices_darker`), and the painter's shadow painted nothing on them (no texel differed by 2 levels with it and without).
- **Leaf** `m_reeds_leaf`, `#8fae52`: the colour of the tallest stalk, a duller green than the tall grass's. The underside tint `#6f96a6` is the tree's. 4 shades in 3 tones up to 14% lighter or darker.
- Stalks and leaves take their colour from a palette in the texture (ADR 11), so a season is a second texture on the same mesh (ADR 13).

## Seasons

| Asset | Season | Leaf | Underside tint | Brown |
| --- | --- | --- | --- | --- |
| `reeds_1` | summer | `#8fae52` | `#6f96a6` | `#553a26` |
| `reeds_1_winter` | winter | `#cdb88a`, dead straw | `#a48c74`, darker and browner | `#4a3222` |

Winter reeds stand dead and straw-coloured with their heads still on. No snow lies on an upright stalk, so winter is a palette and not a mesh.

## Parts

One object and one mesh per variant, with two materials. The brown material is the closed surface: the mud and each head are closed pieces of it. The leaf material holds the stalks and the leaves, each an open piece (`open_materials`): a stalk is a three-sided tube open at its foot, a leaf a strip.

## Budget

At most 800 triangles and two materials, on one 256 px texture. A stalk is 19 triangles (three lengths of three sides and a cap), a leaf 9 (four quads and a tip: it bends three ways), a head 24 and the mud 32. Thirteen stalks with three leaves each and six heads would be 774. The benchmark's tall grass is 326 triangles, as cards. An estimate, as every budget is until the stress scene exists (ADR 7).

## References

- Look: `docs/style/nature-shapes.md`, Grass tuft.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Grass_Common_Tall.gltf` (326 triangles, cards, 1.84 m tall): the nearest thing the benchmark has. A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/reeds_variants.png`; twelve seeds of the first variant in `benchmarks/out/reeds_1_candidates.png`.

## Out of scope

Wind, LODs, water, broken or bent stalks, snow, a bed of many clumps (the game places beds side by side).

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants`; a season's gives its palette.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"reeds"` | This brief |
| `season` | `"summer"` | Seasons |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `800` | Budget |
| `materials.m_reeds_brown` | `"#553a26"` | Style and colour: brown |
| `materials.m_reeds_leaf` | `"#8fae52"` | Style and colour: leaf, the colour of the tallest stalk |
| `painted_shading.texture_px` | `256` | Budget |
| `painted_shading.base_tint` | `"#c8c0b8"` | Style and colour: the mud darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top, where the heads are |
| `painted_shading.edge_light` | `0.2` | As the tall grass |
| `painted_shading.edge_width_m` | `0.002` | A head's faces are about 2.5 cm wide |
| `painted_shading.hidden_underside` | `true` | The mud lies on the ground |
| `foliage.material` | `"m_reeds_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.3` | Silhouette 3: stalks of one bed stand less than 0.3 m from a neighbour |
| `foliage.min_pad_pieces` | `18` | Silhouette 3 and 5: at least six stalks with two leaves each |
| `foliage.piece_m` | `[0.25, 1.5]` | Silhouette 5: a leaf's length |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer for the low leaves |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself for the tallest stalk |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.14` | Style and colour |
| `stalks.count` | `[6, 14]` | Silhouette 3: six to fourteen stalks |
| `stalks.length_m` | `[0.9, 2.5]` | Silhouette 2: a stalk's length, foot to tip |
| `stalks.width_m` | `[0.015, 0.04]` | Silhouette 2: across its foot |
| `stalks.min_round` | `0.5` | Silhouette 2: round-ish, at least half as thick one way as the other |
| `stalks.foot_m` | `0.03` | Silhouette 3: every stalk stands on the ground |
| `stalks.max_lean_deg` | `10.0` | Silhouette 1: none leans more than 10 degrees |
| `stalks.min_apart_m` | `0.06` | Silhouette 3: a stalk's foot is at least 6 cm from its nearest neighbour's |
| `stalks.min_bed` | `0.4` | Silhouette 3: the feet span at least 0.4 of the bounds' width and of its depth |
| `stalks.leaves` | `[1, 4]` | Silhouette 5: one to four leaves on a stalk |
| `stalks.leaf_width_share` | `[0.02, 0.1]` | Silhouette 5: a leaf's mean width over its length |
| `stalks.min_leaf_sweep` | `0.05` | Silhouette 6: seen from above, the median leaf stands off the straight line from its foot to its tip by 0.05 of that line's length |
| `stalks.head_width_m` | `[0.03, 0.07]` | Silhouette 4: a head's thickness |
| `stalks.min_head_fullness` | `0.5` | Silhouette 4: a sausage fills at least half of the cylinder round it |
| `stalks.head_share` | `[0.2, 0.7]` | Silhouette 4: a share of the stalks carry a head |
| `clump.upright_deg` | `6.0` | Silhouette 1: within 6 degrees of upright |
| `clump.min_upright_share` | `0.8` | Silhouette 1: four stalks in five |
| `clump.max_sky_share` | `0.75` | Silhouette 7: at least a quarter of the outline is reed |
| `heads.count` | `[2, 8]` | Silhouette 4: two to eight heads |
| `heads.size_m` | `[0.14, 0.4]` | Silhouette 4: a head's length |
| `heads.min_height` | `0.6` | Silhouette 4: above 0.6 of the bed's height |
| `soft_edges` | `true` | The mud, the heads, the stalks and the leaves are lit smooth |
| `watertight` | `true` | Parts: the mud and the heads are closed |
| `open_materials` | `["m_reeds_leaf"]` | Parts: stalks and leaves are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **Reeds are stalks, not blades.** The `blades` checks ask that every piece grows from one point (`root_m`), goes all round it (`max_gap_deg`) and arches (`min_arch`). A reed's leaf starts a metre up a stalk, a bed has no one point, and a stalk is stiff; passing them would mean a `root_m` as large as the plant and a `min_arch` of nothing, which is switching the checks off. The `stalks` block replaces them (`check_stalks` in `tools/validate.py`): it tells stalks from leaves by their shape in the mesh (a stalk's open edge is a small ring round its foot; a leaf's is its whole outline) and measures each as what it is.
- **`clump` is shared with the tall grass**, with the stalks standing where the blades did: the share near upright is counted over stalks, and the sky through the outline is measured over stalks and leaves.
- **`heads` is shared with the tall grass**; what a cattail needs more (thick, a sausage, on a share of the stalks) is in `stalks`.
- **A stalk is an open three-sided tube of the leaf material**, not a closed tube of the brown: it must be green in summer and take its colour from the palette, and the closed material is one colour, the heads'.
- **Thresholds made up here, with nothing measured behind them**: every number in the `stalks`, `clump` and `heads` blocks, `min_pad_pieces`, `piece_m`, `pad_gap_m` and `max_triangles`.

Not measured, and judged on the contact sheet: whether a bed reads as reeds, whether leaves droop, and that the heads are darker than the leaves (the two colours are in the spec).
