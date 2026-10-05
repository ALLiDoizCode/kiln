# standing_stone

A tall stone that tapers and leans, with one or two small blocks against its foot, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its stones share. The deliverable is three variants, each an asset of its own with its own seed, size and number of pieces: `source/standing_stone_1`, `_2` and `_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

Built under the pieces rule of ADR 13, as the slab is (`source/slab/brief.md`): several closed pieces that pass into each other, each softened on its own.

## Purpose

A marker: the standing stones of the forest reference, a waypoint seen from across a layer, the post of a gate. A player walks round it and stands against it. Nothing climbs, breaks or moves it yet.

## Viewing

First person, from as close as 0.5 m (ADR 7), where one side fills the view, and from 5 to 40 m, where it is an outline against what is behind it.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Pieces | Character |
| --- | --- | --- | --- | --- | --- |
| `standing_stone_1` | 1.4 m | 1.1 m | 2.6 m | 2 | the plain one: half as tall again as a player |
| `standing_stone_2` | 1.9 m | 1.4 m | 3.6 m | 3 | the tall one: twice a player, a wall and a half of the building grid, with two foot blocks |
| `standing_stone_3` | 1.0 m | 0.9 m | 1.8 m | 2 | a player's own height |

Width and depth are those of the whole asset, foot blocks included; the stone itself is narrower. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Standing stone, and "How they are built"):

1. **Tall.** The stone is two to four times as tall as it is wide. Its bounds give 1.9 times the whole asset's width; the stone alone is narrower than the bounds by its foot blocks. Judged on the contact sheet (`front`, `right`).
2. **It tapers.** Every side leans in by 3 to 5.5 degrees, so the cap is narrower than the foot. Judged on the contact sheet.
3. **It leans a little.** The whole stone leans 4 to 7 degrees one way. The surface above nine tenths of the height is centred at least 0.15 of the bounds' half extents from the middle.
4. **A slab or a lozenge.** Four to six sides; the depth of its foot is 0.55 to 1.0 of its width. Judged on the contact sheet (`top`).
5. **A slanted flat cap ringed by chamfers**, never a point: the cap slants 10 to 22 degrees. Judged on the contact sheet.
6. **A foot.** One or two low blocks, 0.1 to 0.18 of the height, stand against the base and pass into it, so the stone looks settled into the ground. Each is a closed piece of its own; each passes into the stone, so nothing floats; no more than 20% of all the surface is buried.
7. **A clear size order.** Each piece shows at least 1.5 times the surface of the next.
8. **Long vertical edges.** The corners between the sides run unbroken from the ground to the shoulder. Judged on the contact sheet.

"Nothing is upright" is the one habit of rock-shapes.md this shape is not held to by number: a standing stone's sides are within 8 degrees of upright by nature (0.58 to 0.82 of the side surface on the first ten seeds). `lean.max_upright_share` is therefore 1.0, which limits nothing; the lean is held by the summit instead (3).

## Style and colour

ADR 9 and ADR 13, as for the slab. Each piece is a prism of exact planes (`tools/stone.py`, `prism`), softened with a one-segment bevel as wide as its shortest edge has room for and at most 0.05 m, and lit with the normals of its planes. The edge where a piece meets the ground is left hard.

A seed draws up to 40 whole stones until one meets every number in this brief, and if none does the build fails and lists why each was refused.

One material:

- `m_standing_stone`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

Painted by script (ADR 9, ADR 10; `tools/paint.py`) into one 1024 px texture:

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground, the boulder's tints.
2. **Side shade.** Upright faces are darker at mid height, by up to 22%, as on the boulder.
3. **Blotches.** The tone drifts lighter and darker by up to 12%, in soft-edged patches about 0.4 m across: a side is 0.4 to 0.9 m wide.
4. **Crevice shadow.** Where a foot block passes into the stone the colour loses 45% of its light, fading to nothing 0.2 m out.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane.

No growth on the bare stone: moss is a cover, and covers are palette variants on the same mesh (ADR 13; Covers, below).

## Covers

A cover is what lies on the stone: `bare`, or `mossy` (`docs/style/catalogue.md`; snow is not built). The assets above are bare. A mossy one is a palette variant (ADR 13, `CONTEXT.md`): a separate asset, `<base>_mossy`, whose spec names its base as `palette_of` and its `cover`, and differs from the base's only in the growth keys of `painted_shading`. It is the base's mesh, UVs included, with another texture, and the gate holds it to that (`spec.cover`, `spec.palette_of`, `palette.same_mesh`).

Moss is growth as ADR 10 and `tools/paint.py` paint it: a wash from the ground up to a height, and small patches on faces near level and along exposed upper edges. Its colour, how dark it is and how sparse come from the first mossy rock (`source/rock/brief.md`, measured there against the benchmark): olive `#7a8a4d` at the stone's own lightness; patches 50% darker than the stone they sit on; patches over about 25% of near-level faces and along about 40% of exposed upper edges, because the benchmark's moss is sparse. How high the wash reaches and how large a patch is are shares of the stone, not that rock's metres:

- **Reach.** Three tenths of the stone's height, and at most 0.9 m, half the player's height, which is where the first rock's stops. The wash's ragged top wanders up to half its reach either way, so at three tenths it stays under half the height, where the growth along upper edges begins; the two never close into a coat.
- **Patch.** A thirteenth of the narrower side of the footprint, and at most 0.2 m, the benchmark's larger flecks (the first rock: 0.2 m on a 2.6 m side). A stone then carries about a dozen patches across whatever its size.

A standing stone is nearly all upright side, where nothing settles: its moss is the wash round its foot and on its foot blocks, patches along the edges of its cap, and little else. `standing_stone_1_mossy`: 2.6 m tall, so the wash reaches 0.8 m (0.78, rounded); 1.1 m on its narrower side, so patches of 0.085 m.

## Parts

One object and one mesh per variant, with one material. The mesh is two or three closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

At most 400 triangles and 1 material slot per variant, the boulder's budget. A prism of n sides is 17n - 4 triangles once softened; a six-sided stone and two five-sided blocks are 260.

## References

- Shape: `docs/style/rock-shapes.md`, Standing stone. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/standing_stone_variants.png`). A boulder, not a standing stone: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes, LODs, carvings, snow-capped covers, other stone colours, groups and circles of stones (placement is the game's), a finished underside.

## Numbers

Every value the variants' `spec.json` files share. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and how many pieces it has.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"standing_stone"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_standing_stone` | `"#a1a7a1"` | Style and colour: the boulder's grey |
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
| `overlap.max_buried_share` | `0.2` | Silhouette 6: no more than 20% of the surface is buried |
| `overlap.min_step_ratio` | `1.5` | Silhouette 7 |
| `lean.max_upright_share` | `1.0` | Silhouette: no limit; a standing stone is upright |
| `lean.min_summit_offset` | `0.15` | Silhouette 3 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants, built from pieces under ADR 13, after the slab; the shape, from `docs/style/rock-shapes.md`.

Proposed by the agent, and open to change: the three sizes, piece counts and seeds; every range in `generator.py`; the buried limit of 0.2 and the size step of 1.5 (neither measured on a reference); the summit offset of 0.15, the boulder's; leaving the upright share unlimited; the budget; every painted value; no growth.

- **Covers (2026-10-05).** Asked for by the owner through the catalogue (bare, mossy, snow-capped for rocks) and ADR 13: a cover is a palette variant of its base, as a season is of a tree. Proposed by the agent, and open to change: the `cover` field and what a cover variant's spec may change; that the reach is three tenths of the height and at most 0.9 m, and a patch a thirteenth of the narrower side and at most 0.2 m (neither share is measured on a reference: they are the first mossy rock's 0.9 m and 0.2 m turned into shares, the reach lowered from that rock's 0.45 of its height so the wash stays under half way up); the colour, darkness and the two shares of cover, which are that rock's. Which variant of the family got the cover was the coordinator's choice. Not approved.
