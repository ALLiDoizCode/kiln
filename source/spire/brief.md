# spire

A stepped spire of weathered rock: a base that is a broken column, a main mass with lower shoulders against it and grooves between, then two or three narrower tiers, each sitting off the middle of the one below and leaning, with tilted caps that show as ledges; big blocks at its foot. Made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its spires share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/spire_1`, `_2` and `_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

Built under the pieces rule of ADR 13, as the crag is (`source/crag/brief.md`): several closed pieces that pass into each other, each softened on its own.

**Reworked on 2026-10-05.** The first spires passed every gate and read as built: coaxial tiers on a flat-faced pyramid, a monument and not rock, and twelve seeds alike. The owner asked for it to look less constructed. That was an escaped defect, so three numbers that tell a telescope from weathered rock are now checks (Silhouette 5, 6 and 7), each of which the first `spire_1` fails.

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
| `spire_1` | 3.2 m | 2.8 m | 6.0 m | 3.3 | 3 or 4, by seed | 7 to 9 | the plain one: two storeys of the building grid |
| `spire_2` | 4.2 m | 3.7 m | 8.0 m | 4.4 | 4 | 8 or 9 | the great pillar: a base wider than a 3 m foundation |
| `spire_3` | 2.0 m | 1.7 m | 3.6 m | 2.0 | 3 | 7 or 8 | a stub: the cap of its base is near a player's eye |

Width and depth are those of the whole asset, shoulders and blocks included. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Stepped spire, and "How they are built": nothing is upright, the tallest part is off-centre, a clear size order, a foot):

1. **Tiers, stacked.** Three or four closed pieces one on another: the base stands on the ground, and each tier above stands on the cap of the one below, its bottom sunk into it. At least nine tenths of a tier's foot has the tier below under it: it sits toward one edge of the cap, and does not hang off.
2. **Each narrower by a clear step.** Taken half way up the part of it that shows, a tier is at most 0.7 as wide as the one below (its width is the square root of the area of a level cut through it).
3. **Caps seen as ledges.** Every cap is a plane tipped 4 to 9 degrees, each its own way, ringed by chamfers. Seen from straight above, every tier shows near-level surface (within 12 degrees) that nothing stands over: at least a tenth of the area of a level cut through that tier. On some spires a small block sits on the base's ledge, against the tier above.
4. **Flutes and grooves on the base.** The base is a broken column: a main mass of six to eight sides, and two shoulders against it, one about three quarters of its height and one about half, each of five or six sides; the lines where they pass into each other are grooves cut from the ground up. Measured as sides: at least six planes of the pieces that stand on the ground are tall sides, at least 0.6 of the base's height from bottom to top and at least 1.2 times as tall as wide, with at least half of each showing.
5. **Off the middle.** Where it leaves the tier below, the middle of each tier is at least 0.15 of its own width from the middle of that tier's head. The first spires read 0.07 to 0.15.
6. **It leans.** Each piece leans, each a different amount (2 to 11 degrees), all within about 45 degrees of one direction; from the middle of the base on the ground to the middle of the top tier's head the spire is at least 4 degrees from upright. The first spires read 1.1 to 1.3.
7. **Unequal steps.** The largest step in width from tier to tier is at least 1.2 times the smallest: one tier much narrower than the one below, another only a little. The first spires read 1.07 to 1.12. The tiers' heights differ as much, and no two tiers have the same outline: each has its own number of sides and is squeezed its own way.
8. **A foot that reads.** Two blocks, the larger at least a seventh of the base's height tall and a third of its radius across; with the shoulders they stand round the side the spire leans away from and beside it. Seen from above, at least two sides of the spire show low near-level surface that nothing stands over, a hundredth of the footprint on each.
9. **A clear size order.** A piece's size is the surface it shows; each shows at least 1.15 times what the next shows, as on the crag: no twins.
10. **No post on top.** The top tier is at least a quarter as wide as the base's main mass. Judged on the contact sheet.

### Light, and why `lean` is not asked

The first brief was written under a viewer whose shaded sides were near black, and flared the base 10 to 12 degrees on every side to keep the upright share of the side surface under 0.45 (`lean.max_upright_share`). That flare is what made the base a pyramid. Under the viewer's light as it now is (ambient 900) the old spire's back view is a readable mid grey (gate L4d holds the shaded sides to the benchmark's value), so the flare is gone and the pieces lean as rock does: together, one way. A piece that leans 8 degrees has two sides the lean runs along, which stay near upright whatever the lean, and one that overhangs; the upright share then says nothing about it, as the crag's brief found. So this family's specs have no `lean` block: the lean is asked through Silhouette 6, and the off-centre summit through 5 and 6, which ask more than `lean.min_summit_offset` did. The share of side surface near upright is still reported in each variant's review.

### As built

The three new checks pass on all three variants and all twelve seeds of the candidates sheet differ. Not met by eye: the foot blocks still do not read (Silhouette 8); `spire_2`'s top tier is about a fifth of its base's width (Silhouette 10); a block on the ledge reads as placed; and every piece is a plain prism, so the whole reads as stacked blocks of rock. A seed often needs many draws (`spire_1` seed 1 took the thirty-sixth of forty), mostly refused for two pieces of one size.

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
4. **Crevice shadow.** Where one piece passes into another the colour loses 45% of its light, fading to nothing 0.2 m out: round the foot of each tier, and down each groove of the base.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane.

**Texture size.** `conventions.toml` asks 100 texels per metre of every face. The family's texture is 2048 px; `spire_3` gives 1024 px in its own brief. The first `spire_1` measured 202 texels per metre at 2048 px, so 1024 px was asked of the reworked one; gate L4 found 74 there, so it stays at 2048 (its own brief).

No growth: moss is a cover, and covers are palette variants on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with one material. The mesh is seven to nine closed pieces that overlap (`overlap` in the spec): three or four tiers, two shoulders, two blocks, and on some seeds a block on the base's ledge. Nothing moves.

## Budget

One material slot. Triangles, estimated before building from the crag's count of 17n - 4 for a softened prism of n sides standing on the ground, and 21n for one whose bottom is off the ground and softened too: the base's main mass of up to 8 sides, 132; a tier of up to 6, 126; shoulders of up to 6 and 5 sides, 98 and 81; two blocks of up to 5, 81 each; a ledge block of up to 5, 105. Each variant's own brief adds them up. Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Stepped spire. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/spire_variants.png`). A boulder, not a spire: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes, a climbable flag, LODs, mossy and snow-capped covers, other stone colours, a spire joined to a wall of the pit, a finished underside.

## Numbers

Every value the variants' `spec.json` files share. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces and tiers it may have, its budget and the area of its foot; `spire_3`'s gives its own texture size.

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
| `overlap.max_buried_share` | `0.4` | Silhouette 9: the crag's limit |
| `overlap.min_step_ratio` | `1.15` | Silhouette 9 |
| `spire.max_width_step` | `0.7` | Silhouette 2 |
| `spire.min_ledge_share` | `0.1` | Silhouette 3 |
| `spire.min_flutes` | `6` | Silhouette 4 |
| `spire.min_tier_offset` | `0.15` | Silhouette 5 |
| `spire.min_lean_deg` | `4.0` | Silhouette 6 |
| `spire.min_step_spread` | `1.2` | Silhouette 7 |
| `foot.min_sides` | `2` | Silhouette 8 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size, built from pieces under ADR 13; the shape, from `docs/style/rock-shapes.md`; that the spires are tall; that expected values come from this brief and painted shading is asked for in the spec. Given after the first review: that it look less constructed (off-centre leaning tiers, unequal steps, tilted caps, a base that is a cluster with grooves, a foot that reads, no post on top, seeds that differ), and that `spire_1` take a 1024 px texture if it clears 100 texels per metre.

Proposed by the agent, and open to change:

- The three sizes, tier and piece counts, and seeds; every range in `generator.py`.
- That a groove is where two pieces meet: a piece is convex (ADR 13).
- Leaving `lean` out of the specs, for the reason under Light. This removes a limit the first specs had (0.45 of the side surface within 8 degrees of upright).
- That a tier's cap tips no more than 9 degrees, so that the ledge check's 12 degrees still finds it.
- **Thresholds invented for the spire.** In the spec: a width step of 0.7, a ledge of a tenth of a tier's level cut, six flutes; a tier 0.15 of its width off the middle of the one below, a lean of 4 degrees, steps that differ by 1.2; the crag's buried limit of 0.4 and size step of 1.15; a foot of a hundredth of the footprint on two sides. In `conventions.toml` (`[spire]`): nine tenths of a tier's foot over the tier below; a flute at least 0.6 of the base's height, 1.2 times as tall as wide and half shown; a tier's head 0.85 of the way up it. None is measured on a reference; the three new ones were set between what the first spires read and what this brief asks.
- The budget; every painted value, the crag's; no growth.
