# spire

A stepped spire: a wide fluted base, then two or three narrower tiers stacked on it like a telescope, each with a flat cap, and buttresses and small blocks leaning on its foot. Made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its spires share. The deliverable is three variants, each an asset of its own with its own seed, size and number of tiers: `source/spire_1`, `_2` and `_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

Built under the pieces rule of ADR 13, as the crag is (`source/crag/brief.md`): several closed pieces that pass into each other, each softened on its own.

## Purpose

The pillars standing in the pit. A player sees one from the rim or from a ledge across the layer, walks up to it, stands against its foot and looks up it. It stands on flat ground; its underside is never seen. Nothing climbs, breaks or moves it yet (a climbable flag and collision are ADR 7's, not built).

## Viewing

First person (ADR 7), eye at 1.7 m.

- **From 0.5 m**, against the foot: one side of the base or one buttress fills the view. What is at eye height is the base's sides, the grooves where a buttress passes into the base, and the caps of the lower buttresses and blocks. Every tier above the base is seen from below, as a step in the outline overhead.
- **From 3 to 15 m**: the whole spire is in view, and this is where the tiers are counted. The caps of the upper tiers are above the eye and are not seen as surfaces; each is read as a step in the outline, and by the ring of chamfers under it.
- **From across a layer, 40 m and more**: an outline against what is behind it: a telescope, wide at the ground, stepping in.

## Real-world size

A player is 1.8 m tall. These are tall: two to four and a half players.

| Variant | Width (x) | Depth (y) | Height | Players tall | Tiers | Pieces | Character |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `spire_1` | 3.2 m | 2.8 m | 6.0 m | 3.3 | 3 | 8 | the plain one: two storeys of the building grid |
| `spire_2` | 4.2 m | 3.7 m | 8.0 m | 4.4 | 4 | 9 | the great pillar: a base wider than a 3 m foundation, and a fourth tier |
| `spire_3` | 2.0 m | 1.7 m | 3.6 m | 2.0 | 3 | 7 | a stub: the cap of its base is at a player's eye |

Width and depth are those of the whole asset, buttresses and blocks included. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Stepped spire, and "How they are built"):

1. **Tiers, stacked.** Three or four closed pieces one on another: the base stands on the ground, and each tier above stands on the cap of the one below, its bottom sunk into it. At least nine tenths of a tier's foot has the tier below under it: nothing hangs off.
2. **Each narrower by a clear step.** Taken half way up the part of it that shows, a tier is at most 0.7 as wide as the one below (its width is the square root of the area of a level cut through it). A column with a line round it is not a step.
3. **Flat caps seen as ledges.** Seen from straight above, every tier shows near-level surface (within 12 degrees, as a slab's top is) that nothing stands over: at least a tenth of the area of a level cut through that tier. On the top tier that is its cap, never a point; on the others it is the ledge round the foot of the next.
4. **Flutes on the base.** The base has seven or eight sides, and the corners between them run unbroken from the ground to its shoulder; the buttresses add their own. Measured as sides: at least six planes of the pieces that stand on the ground are tall sides, at least 0.6 of the base's height from bottom to top and at least 1.2 times as tall as wide, with at least half of each showing. Sides in level bands have none.
5. **The tallest part is off-centre.** Every tier stands off the middle of the one below, all to roughly one side, and the buttresses and blocks stand round the other; so one flank is nearly sheer and the other climbs in steps. The surface above nine tenths of the height is centred at least a tenth of the bounds' half extents from the middle.
6. **A foot.** Two or three buttresses, each a narrow prism lower than the base's shoulder that leans in against the base with a cap sloping outward, in a run of heights; and two small blocks. Seen from above, at least two sides of the spire show low near-level surface that nothing stands over, a hundredth of the footprint on each.
7. **A clear size order.** A piece's size is the surface it shows; each shows at least 1.15 times what the next shows, as on the crag: no twins.
8. **Chamfers ring every cap**, each wide enough to be a face of its own. Judged on the contact sheet.

### Light: how this differs from the crag

On the crag 91% of the side surface is within about 17 degrees of upright, so from behind, with the sun on the far side, nearly every side is in shade and it reads as one dark field. A spire is taller and would do the same. A slender stack of steps cannot lean all its sides far: every degree of lean and every ledge is taken from the same radius, and the tiers above the base keep sides 3 to 5 degrees from upright. What this family does about it:

- **The base flares.** Its sides lean in 9.5 to 12 degrees, more along its longer axis, and it holds about half of the side surface. With the buttresses' outer faces (10 to 15 degrees) that is why `lean.max_upright_share` is a real limit here, 0.45 of the side surface within 8 degrees of upright, and not the crag's 1.0.
- **Ledges and chamfer rings.** Each cap is ringed by chamfers 42 to 51 degrees from level, which face the sky from every side of the spire; with the ledge they put a light band across the outline at each step, whichever way the sun is.
- **Buttress caps slope outward** 14 to 24 degrees, at different heights round the foot: light faces low down, at and below the eye.
- **Flutes turn.** Seven or eight sides, and the buttresses' own, face different ways round the compass, so neighbours take different light; the grooves between buttress and base take crevice shadow.

It is still mostly near upright by the crag's measure (17 degrees): the upper tiers and the base alike. The share is reported in each variant's review, and the back view under Bevy is where to judge whether this is enough.

**As built, it is not enough.** The three variants have 0.33 to 0.39 of their side surface within 8 degrees of upright, and 0.94 to 0.95 within 17, more than the crag; 0.09 to 0.12 of what shows is nearer level than upright. In the back view the spire is one dark mass with light only on the chamfer rings and a buttress cap (`source/spire_1/review/final/observations.md`, items 8, 9 and 11). A real answer needs radius this shape does not have (a wider base, or fewer tiers), or light in the viewer and the game that reaches shaded sides.

## Style and colour

ADR 9 and ADR 13, as for the crag. Each piece is a prism of exact planes (`tools/stone.py`, `prism`), softened with a one-segment bevel as wide as its shortest edge has room for, at most 0.005 of the spire's height and 0.025 m (narrower than the crag's 0.045 m: the top tier and the blocks are small pieces, and one width limit serves every piece of an asset), and lit with the normals of its planes. The edge where a piece meets the ground is left hard.

A seed draws up to 40 whole spires until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_spire`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

Painted by script (ADR 9, ADR 10; `tools/paint.py`) into one texture, with the crag's values:

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground.
2. **Side shade.** Upright faces are darker at mid height, by up to 22%.
3. **Blotches.** The tone drifts lighter and darker by up to 12%, in soft-edged patches about 0.4 m across.
4. **Crevice shadow.** Where one piece passes into another the colour loses 45% of its light, fading to nothing 0.2 m out: round the foot of each tier, and down each groove between a buttress and the base.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane.

**Texture size, said before building.** `conventions.toml` asks 100 texels per metre of every face, and a 1024 px texture at the 0.4 coverage the packer reaches holds about 42 m2 at that density. Estimated from the sizes above: `spire_1` has about 47 m2 of surface and `spire_2` about 85 m2, so the family's texture is 2048 px (about 168 m2); `spire_3` has about 17 m2 and its own brief gives 1024 px.

No growth: moss is a cover, and covers are palette variants on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with one material. The mesh is seven to nine closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

One material slot. Triangles, estimated before building from the crag's count of 17n - 4 for a softened prism of n sides standing on the ground, and 21n for one whose bottom is off the ground and softened too: the base of up to 8 sides, 132; a tier of up to 6, 126; a buttress or a block of up to 5, 81. Each variant's own brief adds them up. Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Stepped spire. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/spire_variants.png`). A boulder, not a spire: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes, a climbable flag, LODs, mossy and snow-capped covers, other stone colours, a spire joined to a wall of the pit, a finished underside.

## Numbers

Every value the variants' `spec.json` files share. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces and tiers it has, its budget and the area of its foot; `spire_3`'s gives its own texture size.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"spire"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `materials.m_spire` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `2048` | Painted shading: texture size |
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
| `overlap.max_buried_share` | `0.4` | Silhouette 7: the crag's limit |
| `overlap.min_step_ratio` | `1.15` | Silhouette 7 |
| `spire.max_width_step` | `0.7` | Silhouette 2 |
| `spire.min_ledge_share` | `0.1` | Silhouette 3 |
| `spire.min_flutes` | `6` | Silhouette 4 |
| `lean.max_upright_share` | `0.45` | Light: the base and the buttresses' outer faces lean |
| `lean.min_summit_offset` | `0.1` | Silhouette 5 |
| `foot.min_sides` | `2` | Silhouette 6 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size, built from pieces under ADR 13; the shape, from `docs/style/rock-shapes.md`; that the spires are tall; that expected values come from this brief and painted shading is asked for in the spec; that `lean.max_upright_share` is not to be set to 1.0.

Proposed by the agent, and open to change:

- The three sizes, tier and piece counts, and seeds; every range in `generator.py`.
- That the flutes are the corners of a seven- or eight-sided base and of buttresses leaning on it, and not grooves cut into one piece: a piece is convex (ADR 13), so a groove is where two pieces meet.
- That the tiers step off-centre to one side and the buttresses stand round the other.
- **Thresholds invented for the spire.** In the spec: a width step of 0.7, a ledge of a tenth of a tier's level cut, six flutes; an upright share of 0.45 and a summit offset of 0.1; the crag's buried limit of 0.4 and size step of 1.15; a foot of a hundredth of the footprint on two sides. In `conventions.toml` (`[spire]`): nine tenths of a tier's foot over the tier below; a flute at least 0.6 of the base's height, 1.2 times as tall as wide and half shown. None is measured on a reference.
- The budget; every painted value, the crag's; no growth.
