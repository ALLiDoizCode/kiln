# crag

Many leaning prisms of different heights sharing one base, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its crags share. The deliverable is three variants, each an asset of its own with its own seed, size and number of pieces: `source/crag_1`, `_2` and `_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

Built under the pieces rule of ADR 13, as the slab and the standing stone are (`source/slab/brief.md`): several closed pieces that pass into each other, each softened on its own.

## Purpose

Broken ground: cliff tops, ridges, the edge of a layer of the pit. A player walks round it, stands against it and looks up at it. It sits on flat ground; its underside is never seen. Nothing climbs, breaks or moves it yet.

## Viewing

First person (ADR 7). From as close as 0.5 m, where one prism's side fills the view and the joins between prisms are at eye height; from 3 to 10 m, where the stepped outline is read whole; and from across a layer, 40 m and more, where it is an outline against what is behind it.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Pieces | Prisms | Character |
| --- | --- | --- | --- | --- | --- | --- |
| `crag_1` | 3.2 m | 2.6 m | 3.0 m | 6 | 4 | the plain one: as tall as a wall of the building grid, a player's eye is just over half way up it |
| `crag_2` | 5.0 m | 4.0 m | 4.6 m | 8 | 5 | a ridge end: two and a half players tall, wider than a 3 m foundation |
| `crag_3` | 2.0 m | 1.7 m | 1.7 m | 5 | 3 | an outcrop: its tallest prism reaches a player's eye |

Width and depth are those of the whole asset. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Crag, and "How they are built"):

1. **Many pieces sharing one base.** Five to eight closed pieces, all standing on the ground and passing into each other, so nothing floats. They are packed closer than a slab's plates, so more of their surface is buried: no more than 40% of all of it.
2. **Prisms and blocks.** A piece at least 0.3 of the crag's height is a prism; a lower one is a block. A crag has at least three prisms (four and five in the larger variants), and two or three blocks.
3. **Different heights, stepping down.** Going out from the tallest prism, by where each prism stands on the ground, every prism is at most 0.9 of the height of the one before it: no two of one height, and no second peak further out.
4. **The tallest is off-centre.** The surface above nine tenths of the height, which is the tallest prism's cap, is centred at least a quarter of the bounds' half extents from the middle.
5. **They lean, and lean together.** The line from the middle of a prism's foot to the middle of its cap is at least 5 degrees from upright, and every prism's lean is within 45 degrees, round the compass, of the direction they lean in on average.
6. **Small blocks fill the foot.** Seen from above, at least two sides of the crag show low near-level surface that nothing stands over (the caps of the blocks): on each, at least a hundredth of the area of the crag's footprint, width times depth.
7. **A clear size order.** A piece's size is the surface it shows. With up to eight pieces a step as large as the slab's cannot hold all the way down; each piece shows at least 1.15 times what the next shows: no twins.
8. **Flat caps ringed by chamfers**, never points: each cap slants 8 to 20 degrees, all roughly the same way. Judged on the contact sheet.
9. **Long vertical edges.** A prism has four to six sides and the corners between them run unbroken from the ground to the shoulder. Judged on the contact sheet.

"Nothing is upright" is asked through 5 and not through the upright share of the side surface: a prism that leans 10 degrees has two sides the lean runs along, and those stay within 8 degrees of upright whatever the lean. `lean.max_upright_share` is therefore 1.0, which limits nothing, as on the standing stone.

## Style and colour

ADR 9 and ADR 13, as for the slab. Each piece is a prism of exact planes (`tools/stone.py`, `prism`), softened with a one-segment bevel as wide as its shortest edge has room for, and at most 0.012 of the crag's height and 0.045 m, and lit with the normals of its planes. The edge where a piece meets the ground is left hard.

A seed draws up to 40 whole crags until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_crag`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

Painted by script (ADR 9, ADR 10; `tools/paint.py`) into one texture, 1024 px unless a variant's own brief says otherwise, with the standing stone's values:

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground, the boulder's tints.
2. **Side shade.** Upright faces are darker at mid height, by up to 22%.
3. **Blotches.** The tone drifts lighter and darker by up to 12%, in soft-edged patches about 0.4 m across.
4. **Crevice shadow.** Where one piece passes into another the colour loses 45% of its light, fading to nothing 0.2 m out. This is what hides the joins (ADR 13), and a crag has more of them than any rock before it.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane.

No growth: moss is a cover, and covers are palette variants on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with one material. The mesh is five to eight closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

At most 90 triangles a piece and 1 material slot per variant. A prism of n sides is 17n - 4 triangles once softened: 64, 81 and 98 for four, five and six sides. Until the stress scene of ADR 7 exists this is an estimate; it is more than the boulder's 400 because a crag is up to eight pieces where the boulder is one skin.

## References

- Shape: `docs/style/rock-shapes.md`, Crag. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/crag_variants.png`). A boulder, not a crag: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes, LODs, mossy and snow-capped covers, other stone colours, crags as part of a cliff face (placement is the game's), a finished underside.

## Numbers

Every value the variants' `spec.json` files share. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces and prisms it has, its budget and the area of its foot; `crag_2`'s gives its own texture size.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"crag"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `materials.m_crag` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `1024` | Painted shading: one 1024 px texture |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1 |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1 |
| `painted_shading.edge_light` | `0.3` | Painted shading 5 |
| `painted_shading.edge_width_m` | `0.06` | Painted shading 5 |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 4 |
| `painted_shading.crevice_width_m` | `0.2` | Painted shading 4 |
| `painted_shading.blotch` | `0.12` | Painted shading 3 |
| `painted_shading.blotch_size_m` | `0.4` | Painted shading 3 |
| `painted_shading.side_shade` | `0.22` | Painted shading 2 |
| `painted_shading.hidden_underside` | `true` | The underside is never seen |
| `overlap.max_buried_share` | `0.4` | Silhouette 1: no more than 40% of the surface is buried |
| `overlap.min_step_ratio` | `1.15` | Silhouette 7 |
| `cluster.max_height_step` | `0.9` | Silhouette 3 |
| `cluster.min_lean_deg` | `5.0` | Silhouette 5 |
| `cluster.max_lean_spread_deg` | `45.0` | Silhouette 5 |
| `lean.max_upright_share` | `1.0` | Silhouette: no limit; the lean is held by `cluster` |
| `lean.min_summit_offset` | `0.25` | Silhouette 4 |
| `foot.min_sides` | `2` | Silhouette 6 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size, built from pieces under ADR 13, after the slab and the standing stone; the shape, from `docs/style/rock-shapes.md`; that expected values come from this brief and painted shading is asked for in the spec.

Proposed by the agent, and open to change:

- The three sizes, piece and prism counts, and seeds; every range in `generator.py`.
- **Thresholds invented for the crag.** In the spec: a buried limit of 0.4 and a size step of 1.15 (neither measured on a reference); a height step of 0.9; a lean of at least 5 degrees within 45 degrees of the common direction; a summit offset of 0.25; a foot of a hundredth of the footprint on two sides. In `conventions.toml` (`[cluster]`): a piece is a prism from 0.3 of the bounds' height, the height the foot check already calls low.
- That where a prism stands is the middle of its face on the ground, and its lean the line from there to the middle of its surface within 45 degrees of level (its cap).
- That blocks may stand anywhere round the base, behind the tallest prism too: the stepping down is asked of the prisms.
- Leaving the upright share unlimited, for the reason under Silhouette.
- The budget of 90 triangles a piece; every painted value, the standing stone's; no growth.
