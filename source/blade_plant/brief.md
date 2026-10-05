# blade_plant

A rosette of long broad leaves from one point: a fern or an understorey plant, made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its plants share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/blade_plant_1`, `source/blade_plant_2`, `source/blade_plant_3`. Their specs name this folder as their `family`.

It is the nature reference's **blade plant** (`docs/style/nature-shapes.md`): "a rosette of long broad leaves from one point (ferns, jungle understorey)". It is the first asset whose foliage is **blades** and not leaf pieces in pads (`CONTEXT.md`).

## Purpose

The middle and the lowest of the three heights of growth: blade plants stand at knee to waist height at the foot of every trunk and between the bushes. Dozens to hundreds are on screen at once. A player walks through them and looks down onto them. Nothing breaks them yet, and they do not move in the wind.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 1 to 15 m. A player's eye is 1.7 m up, so a blade plant is always looked down on: what is seen is the upper face of each leaf, the rosette as a star from above, and the arch of the leaves from the side.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `blade_plant_1` | 1.2 m | 1.2 m | 0.7 m | above the knee; the plain one |
| `blade_plant_2` | 1.8 m | 1.7 m | 1.0 m | to the hip, and as wide as the player is tall |
| `blade_plant_3` | 0.8 m | 0.75 m | 0.45 m | to the knee |

The benchmark's nearest plant (`Plant_1`) is 1.3 by 1.4 m and 1.0 m tall. The origin is on the ground at the middle of the rootstock the leaves grow from; the bounds are not centred on it, because a rosette reaches further one way than another.

## Silhouette

1. **A rosette from one point.** Every blade's foot is within 0.15 m of the origin, at the ground: nothing floats and nothing grows from beside the plant. There are at least 8 blades, and they go all round: seen from above, no gap between neighbouring blades is wider than 100 degrees.
2. **Long, broad, pointed blades.** Each blade is one piece, 0.3 to 1.3 m from foot to tip in a straight line, widest about two fifths of the way along and narrowing to a point of 60 degrees or less. Its mean width is 0.08 to 0.25 of that length: broad enough to read as a leaf and not as grass, narrow enough not to read as a pad.
3. **Blades arch.** A blade rises from the rootstock and bends over: it stands off the straight line from its foot to its tip by at least 0.08 of that line's length (the median blade), measured in the upright plane through the two. Blades lean out between 15 and 85 degrees from upright: the inner ones stand, the outer ones lie out and droop. None lies on the ground and none stands straight up.
4. **Colour by blade.** Each blade is one flat colour, neighbours differ, and the higher blades are a lighter yellow-green and the lower ones darker and bluer.
5. **A rootstock.** A low dark mound at the origin, about 0.25 m across and 0.07 m high, that the blades grow out of. It is the plant's closed surface, and what a player sees down the middle of the rosette.

## Style and colour

ADR 9: foliage is leaf-shaped geometry in flat colour, with no leaf cards and no transparency. A blade is one leaf, so it is not flat: it bends along its length and is folded a little along its middle. There is no core: a rosette is open, and the ground shows through it.

- **Rootstock** `m_blade_rootstock`, `#5a4a36`: dark brown, with painted shading (ADR 10): darker toward the ground (`#a8a098`), light along its edges. No crevice shadow is asked: the rootstock is one convex mound and the blades lie apart and make no inside corner, the load test finds none (`painted.crevices_darker`), and the painter's shadow painted nothing on them (no texel differed by 2 levels with it and without).
- **Leaf** `m_blade_leaf`, `#8cb24a`: the colour of the highest blade; a little deeper than the bush's. The underside tint `#6f96a6` is the tree's. Between the two there are 4 shades in 3 tones up to 14% lighter or darker: a plant of a dozen blades has no use for the tree's 24 colours.
- Blades take their colour from a palette in the rootstock's texture (ADR 11), so a season or another colour is a second texture on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with two materials. The rootstock is the closed surface. The leaf material holds the blades, each an open piece (`open_materials`).

## Budget

At most 400 triangles and two materials, on one 256 px texture. A blade is 14 triangles (three stretches of two quads and a two-triangle tip), which is the least that both bends and folds; 8 to 16 blades are 112 to 224, and the rootstock is about 30. The benchmark's `Plant_1` is 120 triangles and its fern 288. Blade plants are the commonest thing on a forest floor after grass, so the ceiling is a tenth of a tree's.

The texture holds only the rootstock and the palette strip.

## References

- Look: `docs/style/nature-shapes.md`, Blade plant, and the jungle previews it was read from (`docs/style/refs/nature-shapes/`, git-ignored).
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Plant_1.gltf` (120 triangles, leaf cards). A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/blade_plant_variants.png`.

## Out of scope

Fern fronds cut into leaflets, flowers, wind, LODs, collision, seasonal and colour variants (palette changes on these meshes, ADR 13).

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants.siblings`.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"blade_plant"` | This brief |
| `season` | `"summer"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `400` | Budget |
| `materials.m_blade_rootstock` | `"#5a4a36"` | Style and colour: rootstock |
| `materials.m_blade_leaf` | `"#8cb24a"` | Style and colour: leaf, the colour of the highest blade |
| `painted_shading.texture_px` | `256` | Budget |
| `painted_shading.base_tint` | `"#a8a098"` | Style and colour: the rootstock darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top |
| `painted_shading.edge_light` | `0.2` | Style and colour: light along the rootstock's edges |
| `painted_shading.edge_width_m` | `0.004` | The rootstock's faces are about 6 cm wide |
| `painted_shading.hidden_underside` | `true` | The rootstock stands on the ground |
| `foliage.material` | `"m_blade_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 1: blades from one point have no clear air between their feet, on the tree's 6 cm grid |
| `foliage.min_pad_pieces` | `8` | Silhouette 1: at least 8 blades |
| `foliage.piece_m` | `[0.3, 1.3]` | Silhouette 2: a blade's length |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer below |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself for the highest blade |
| `foliage.shades` | `4` | Style and colour |
| `foliage.tones` | `3` | Style and colour |
| `foliage.variation` | `0.14` | Style and colour |
| `blades.width_share` | `[0.08, 0.25]` | Silhouette 2: mean width over length |
| `blades.root_m` | `0.15` | Silhouette 1: from one point |
| `blades.max_gap_deg` | `100.0` | Silhouette 1: all round |
| `blades.lean_deg` | `[15.0, 85.0]` | Silhouette 3: neither upright nor on the ground |
| `blades.min_arch` | `0.08` | Silhouette 3: blades arch |
| `soft_edges` | `true` | The rootstock and the blades are lit smooth |
| `watertight` | `true` | Parts: the rootstock is a closed surface |
| `open_materials` | `["m_blade_leaf"]` | Parts: blades are open pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |
| `variants.min_difference` | `0.3` | As the trees |

## Decisions

All proposed by the agent, from the task the owner set, and open to change at review:

- **Blades are a second form of foliage, with their own checks.** The foliage checks written for the tree ask for flat, notched pieces in pads over cores; a blade is none of those, and bending the limits until a blade passed would have emptied them. A spec with a `blades` block is held to the blade checks instead (`tools/validate.py`, `check_blades`), and its `foliage` block keeps only what blades share with leaf pieces: the material, how pieces are found, and the palette. A spec without one is held to everything the tree is, as before.
- **No core.** ADR 9 allows a core; it does not ask for one. A rosette has no inside to close.
- **The rootstock is the closed surface**, for the reason the bush's stems are.
- **A blade is one flat colour**, as a leaf piece is (ADR 11), though a real blade is darker at its foot. The palette cannot shade within a piece.
- **Thresholds made up here, with nothing measured behind them**: every number in the `blades` block, `piece_m`, `min_pad_pieces` and `max_triangles`. The benchmark's plants are leaf cards and were not measured.

Not measured, and judged on the contact sheet: that blades do not pass through each other, and the fold along a blade's middle.
