# dome_bush

A low rounded bush, made by a generator that takes a seed. This is the brief for the family (ADR 13): the generator (`generator.py`, beside this file) and everything its bushes share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/dome_bush_1`, `source/dome_bush_2`, `source/dome_bush_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

It is the nature reference's **dome bush** (`docs/style/nature-shapes.md`): "a low rounded mass of leaves". It is built as one pad of a tree's canopy is built (`source/tree/brief.md`), set on the ground on a few short stems.

## Purpose

The middle of the three heights of growth a forested layer has: ground cover, then shrubs at waist to head height, then canopy. Dozens are on screen at once, at the foot of trunks and between them. A player walks round it and looks down onto it. Nothing breaks it or moves it yet, and it does not move in the wind.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 2 to 20 m. A player's eye is 1.7 m up, so the bush is looked **down on** or across at, never up into: at 0.5 m its top fills the lower half of the view. From further off it is an outline: a low dome with a serrated edge.

## Real-world size

Waist high and wider than it is tall. Beside a 1.8 m player the three variants reach the thigh, the waist and the shoulder:

| Variant | Width (x) | Depth (y) | Height | Beside a player |
| --- | --- | --- | --- | --- |
| `dome_bush_1` | 1.6 m | 1.5 m | 1.1 m | to the waist; the plain one |
| `dome_bush_2` | 2.2 m | 2.0 m | 1.5 m | to the shoulder; as wide as a player's arms held out |
| `dome_bush_3` | 1.1 m | 1.0 m | 0.75 m | to the thigh |

The benchmark's bush is 1.9 by 2.0 m and 1.35 m above the ground: between the first two. The origin is on the ground in the middle of the bounds, among the feet of the stems.

## Silhouette

1. **A low dome.** One mass of foliage, with no clear air inside it (one pad, and no piece outside it), at least 1.2 times as wide as it is tall, reaching down to the ground.
2. **Lumpy, not a ball.** The dome is two or three overlapping lobes of different sizes (the widest at least 1.2 times the narrowest), each with a closed, dark, low-triangle core under its pieces (ADR 9 as amended). The pieces are what is seen: from each level and three-quarter view no more than 10% of the foliage seen is core.
3. **Leaf-shaped pieces.** Every piece is flat, pointed (its sharpest corner is 60 degrees or less), jagged (at least one notch in its outline) and 0.2 to 0.5 m long: a bush is seen from nearer its leaves than a tree is, and they are about half the size of a tree's. Pieces lie like shingles, at least 80% of them pointing out of the dome and at least 50% below level; the crown of a dome has no downhill, and the pieces beside the ground are held up by it, so fewer point down than on a tree's pad (70%).
4. **A serrated outline with little sky in it.** Seen from the side, between 3% and 30% of the outline (the convex hull of the foliage) is sky, from at least five of six directions: more than a ball (none), because tips stand out all round, and less than a canopy of separate pads. Seen from straight above, as a player standing over it does, at least one point of a piece stands clear per metre of the outline.
5. **Colour by piece.** Each piece is one flat colour, neighbours differ, and they run from a light yellow-green at the top of the dome to a darker, bluer green by the ground. The core is darker than any piece.
6. **Stems.** Four to six short woody stems rise from the ground at the origin into the lobes, darker than the foliage. They are what shows in the gaps under the lowest pieces from 0.5 m, and they are the bush's closed surface.

## Style and colour

ADR 9 as amended: leaf-shaped pieces over a dark core, no leaf cards, no transparency. The bush stands beside the trees (`source/tree_1`) and is judged beside the benchmark's bush.

- **Stem** `m_bush_stem`, `#6b5540`: a mid brown a little greyer than the tree's bark, with painted shading (ADR 10): darker toward the ground (`#a89c94` at the foot), light along its corners, shadow where stems meet. No grain: a stem is 3 to 4 cm thick and mostly hidden.
- **Leaf** `m_bush_leaf`, `#9ab552`: the colour of a piece at the top of the dome, a little greener and deeper than the tree's `#a8b846`, so a bush under a tree is not the tree's colour. The underside tint `#6f96a6`, the 6 shades, 4 tones and 16% variation are the tree's.
- **Core**: in the leaf material, the leaf colour times `#527a86`, as the tree's.
- Leaf pieces and cores take their colour from a palette in the stems' texture (ADR 11), so a season or another colour is a second texture on the same mesh (ADR 13). Nothing here blocks that: no colour is in the mesh.

## Parts

One object and one mesh per variant, with two materials. The stems are the closed surface: each a closed tube standing on the ground. The leaf material holds the leaf pieces, which are open, separate and flat (`open_materials`), and the cores.

## Budget

At most 1,500 triangles and two materials, on one 512 px texture. The benchmark's bush is 900 triangles of leaf cards (1,368 with flowers); ours pays four triangles a piece, as the tree does, and the tree came to a little over half its benchmark's count. Bushes are commoner on screen than trees, so the ceiling is well under half a tree's 4,000. As built the variants are 944, 1,432 and 664 triangles; the largest is close to the ceiling.

The texture holds only the stems (about 0.4 m2) and the palette strip, 16 px tall. It is 512 px for the layout's sake, not for sharpness: the stems unroll into about twenty small islands with an 8 px gap round each, and at 256 px the gaps left the islands 0.25 of the texture, where the conventions ask for 0.4. At 512 px they take a little over 0.4, at about 500 texels per metre. A variant's file is 105 to 140 kB.

## References

- Look: `docs/style/nature-shapes.md`, Dome bush, and the previews it was read from (`docs/style/refs/nature-shapes/`, git-ignored).
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Bush_Common.gltf` (900 triangles, leaf cards). A comparison only; nothing from it is used.
- Comparison: `benchmarks/out/dome_bush_variants.png`.

## Out of scope

Flowers and berries, wind, LODs, collision, seasonal and colour variants (palette changes on these meshes, ADR 13), growth stages beyond the three sizes.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants.siblings`.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"dome_bush"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `1500` | Budget |
| `materials.m_bush_stem` | `"#6b5540"` | Style and colour: stem |
| `materials.m_bush_leaf` | `"#9ab552"` | Style and colour: leaf, the colour at the top of the dome |
| `painted_shading.texture_px` | `512` | Budget |
| `painted_shading.base_tint` | `"#a89c94"` | Style and colour: stems darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top |
| `painted_shading.edge_light` | `0.2` | Style and colour: light along the corners, as the tree's bark |
| `painted_shading.edge_width_m` | `0.004` | A stem's side is about 3 cm wide; the light is an eighth of it |
| `painted_shading.crevice_shadow` | `0.5` | Style and colour: shadow where stems meet |
| `painted_shading.crevice_width_m` | `0.01` | A band 1 cm wide, a third of a stem's thickness |
| `painted_shading.hidden_underside` | `true` | The feet of the stems stand on the ground |
| `foliage.material` | `"m_bush_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 1: clear air is measured on a 6 cm grid, as on the tree |
| `foliage.min_pads` | `1` | Silhouette 1: one mass |
| `foliage.max_pads` | `1` | Silhouette 1 |
| `foliage.min_pad_pieces` | `40` | Silhouette 1: a mass, as a tree's pad is |
| `foliage.piece_m` | `[0.2, 0.5]` | Silhouette 3: piece length |
| `foliage.min_pointing_out` | `0.8` | Silhouette 3 |
| `foliage.min_pointing_down` | `0.5` | Silhouette 3 |
| `foliage.sky_share` | `[0.03, 0.3]` | Silhouette 4 |
| `foliage.min_sky_views` | `5` | Silhouette 4: from five of six directions |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer by the ground |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself at the top |
| `foliage.shades` | `6` | Style and colour |
| `foliage.tones` | `4` | Style and colour |
| `foliage.variation` | `0.16` | Style and colour |
| `foliage.core_tint` | `"#527a86"` | Style and colour: the core |
| `foliage.lobes` | `[2, 3]` | Silhouette 2 |
| `foliage.min_lobe_ratio` | `1.2` | Silhouette 2: lobes of different sizes |
| `foliage.max_core_seen` | `0.1` | Silhouette 2: the pieces are what is seen |
| `foliage.max_core_seen_below` | `1.0` | Viewing: a bush stands on the ground and is never seen from below, so nothing is asked of that view |
| `foliage.min_pad_flatness` | `1.2` | Silhouette 1: wider than tall |
| `foliage.min_pad_spread` | `1.0` | Silhouette 1: one pad, so there is no second to differ from |
| `foliage.max_seen_into` | `1.0` | Viewing: measured looking straight up from under the pad, a view a bush on the ground does not have, so nothing is asked of it |
| `foliage.min_rim_points_per_m` | `1.0` | Silhouette 4: points round the outline, which is the same from above as from below |
| `soft_edges` | `true` | Stems are lit round |
| `watertight` | `true` | Parts: the stems are a closed surface |
| `open_materials` | `["m_bush_leaf"]` | Parts: leaf pieces are open and separate |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs |
| `variants.min_difference` | `0.3` | As the trees: outlines differ at least as much as the benchmark's most different pair of trees |

## Decisions

All proposed by the agent, from the task the owner set (three small-plant families, each in three variants that differ by seed and size) and open to change at review:

- **A bush is a tree's pad on the ground.** The same pieces, lobes, cores, palette and checks; no new check was written for it. The limits that differ from the tree's are the rows above that say why: one pad, fewer pieces pointing down, less sky, and nothing asked of the view from below.
- **Stems are the closed surface.** The pipeline asks every asset for a closed surface in a material that is not the open one, and a texture to carry the palette. A bush has woody stems, so they are that surface, rather than a third kind of asset with none.
- **Sizes and seeds**: the three variants' bounds, and each variant's brief.
- **Thresholds made up here, with nothing measured behind them**: `sky_share` 0.03 to 0.3, `min_pointing_down` 0.5, `min_pad_flatness` 1.2, `piece_m` 0.2 to 0.5 m, `max_triangles` 1,500. The benchmark's bush could not be measured for sky: it is leaf cards with transparent texels, which the outline rays take as solid.
- **Colours**: by eye beside the tree's.

Not measured, and judged on the contact sheet: the view from straight above (no check looks from there; the three-quarter views look down at 35 degrees), and that the stems show under the lowest pieces.
