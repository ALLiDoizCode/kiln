# rubble

A handful of small broken stones lying together as they fell: what is found at the foot of an arch, a cliff or a broken block. Made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its groups share. The deliverable is three groups, each an asset of its own with its own seed, spread and number of fragments: `source/rubble_1`, `source/rubble_2`, `source/rubble_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

## Purpose

Ground scatter at the foot of bigger rock: against the piers of an arch (`source/arch`), under a crag or a cliff, beside a cracked block. Placed several to a view, turned, and mixed with pebbles. A group lies on flat ground; its undersides are never seen. Nothing picks a fragment up, throws it or breaks it yet, so a group is one mesh and not five props.

## Viewing

First person (ADR 7). A standing player's eye is 1.7 m above a group on the floor, so it is mostly seen from above and from 1.7 m or further: from there the smallest fragment is about 3 degrees across, and what reads is how many stones there are, how unlike in size, and how they lie to each other, not the planes of any one. A crouching or climbing player has it 0.5 m from the face, where the largest fragment fills a quarter of the view and its planes and soft edges have to hold up as a pebble's do.

## Real-world size

Three groups. Each is given beside the 1.8 m player; a fragment's size is its length, the greatest distance between two of its points.

| Variant | Spread (x by y) | Height | Fragments | Largest, smallest fragment | Beside a 1.8 m player |
| --- | --- | --- | --- | --- | --- |
| `rubble_1` | 0.6 m by 0.5 m | 0.14 m | 5 | about 0.25 m and 0.09 m | a third of the player's height across, as wide as two boots end to end; its tallest stone is one thirteenth of the player, just over the ankle bone |
| `rubble_2` | 1.0 m by 0.8 m | 0.2 m | 7 | about 0.36 m and 0.09 m | a spill a long stride across, more than half the player's height; its tallest stone is one ninth of the player, to the lower shin |
| `rubble_3` | 0.44 m by 0.36 m | 0.11 m | 4 | about 0.2 m and 0.08 m | a quarter of the player's height across, a tight heap one boot long; its tallest stone is one sixteenth of the player, at the ankle bone |

The largest fragment is a stone for two hands and the smallest one for the palm. Anything larger is a boulder or a block; a stone on its own is a pebble. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Rubble: "a handful of tiny fragments placed as one group", and "How they are built"):

1. **Separate stones.** Four to seven fragments, each a closed stone of its own, lying apart or just touching. None passes into another: this is not a rock built of pieces (Decisions).
2. **Clearly different sizes.** The largest fragment is at least 2.5 times as long as the smallest, and ranked by length each is at least 1.1 times the next: no two are twins ("a clear size order").
3. **One group, as it fell.** No fragment lies further than half the largest fragment's length from the rest (0.1 to 0.18 m, by variant), and at least one pair touches (two pairs in the group of seven): one fetched up against another, its high end toward it. The fragments are not in a line and not in a ring: seen from above their middles spread at least 0.3 times as far across the group as along it, and their distances from the group's middle differ (a spread of at least 0.2 of their mean), so some are near the middle and some at the edge.
4. **Broken and weathered, not dressed.** Each fragment is a shard cut by five to nine planes at its own angles, with one or two corners knocked off, and it lies tilted, 8 to 32 degrees off level, each its own way: no fragment is a cube standing square on a face. At most 15% of all the side surface is within 8 degrees of vertical. Every edge above the ground is soft.
5. **On the ground, not in it and not over it.** Every fragment reaches the ground and meets it at a hard edge with no gap, sunk a tenth to a quarter of its height, as a stone lying in dirt is. None is sunk to a cap: each stands at least 0.3 of its own length above the ground. A pebble is a plate 0.2 of its width tall; a fragment is a lump.
6. **The tallest part is off-centre.** The largest fragment is not in the middle of the group: the surface above nine tenths of the height is centred at least 0.15 of the bounds' half extents from the middle, the boulder's limit.

Judged on the contact sheet and not checked: that the fragments read as broken (item 4's planes and tilts are the generator's ranges; only the upright share is measured), and that twelve seeds are twelve different groups (`benchmarks/out/rubble_1_candidates.png`).

The habits of the shapes document that rubble does not follow: pieces pushed into each other, a foot of small blocks, flat caps ringed by chamfers, long vertical edges. Those describe a rock a player stands beside. Rubble is what lies at such a rock's foot.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes with no noise. The boulder's bare grey, `#a1a7a1`, one material. Mossy and snow-capped rubble are covers, which are palettes on the same mesh (ADR 13), and are not in this brief.

## Painted shading

Asked for in the spec and added by `tools/paint.py` during the build (ADR 10); the build script gives the one flat colour.

1. **Gradient.** The pebble's and the boulder's tints: a cool grey `#8c8c9a` at the ground to a light grey `#c8c8c8` at the top of the bounds.
2. **Blotches.** Lighter and darker by up to 12%, in patches a tenth of the largest fragment's length across.
3. **Edge light.** Exposed edges gain up to 30%, fading out over one fortieth of the largest fragment's length: a band narrow enough to fit on the smallest fragment's planes.
4. **Crevice shadow.** Up to 45% darker, the boulder's strength, reaching a tenth of the largest fragment's length: where one fragment lies against another the gap between them is an inside corner, and the dark in it is what makes the two read as touching. A single fragment is convex and has no crevice of its own.

No growth and no side shade.

**Texture size.** The narrowest band is the edge light, about 6 mm, and it needs 3 texels across: 500 texels per metre. A group shows about 1.5 times the sum of its fragments' lengths squared: 0.2 to 0.45 m2, so 50,000 to 110,000 texels used; at the 0.4 of the texture a layout must use that is 360 to 530 px a side. 512 px for each (the largest group's band is 9 mm, which needs a third fewer).

The undersides are never seen, so they get almost none of the texture.

## Parts

One object and one mesh per variant, with one material. The mesh is several closed stones, separate from each other. Nothing moves.

## Budget

At most 60 triangles a fragment and 1 material slot per variant: 300, 420 and 240 triangles for groups of five, seven and four. A pebble has 150 and is one stone seen alone; a fragment is one of several seen together and gets under half of that, and a group comes to about the 280 the reference pack spends on a rock (`docs/style/rock-shapes.md`). A softened solid of e edges above the ground is about 4e triangles (the pebble's brief), so 60 allows a fragment about 15 edges: a shard of seven or eight planes. The generator gives the largest fragment 1.3 times an even share and the next 1.15, and the small ones what is left. Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Rubble, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark, for scale and paint only: `benchmarks/quaternius-stylized-nature/glTF/Pebble_Round_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/rubble_variants.png`). The benchmark has no rubble; nothing of it is used, and no limit here was measured on it.

## Out of scope

Collision shapes, LODs, fragments that are picked up or thrown, rubble heaped more than one stone deep (a fragment lying on top of another), rubble as part of an arch's or a crag's own mesh (those have their own pieces), mossy and snow-capped covers, other stone colours, finished undersides.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, its count of fragments, its budget, how far apart its fragments may lie, how many touch, and the widths of its painted bands. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"rubble"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `materials.m_rubble` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `512` | Painted shading, texture size |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1: a cool grey at the ground |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1: a light grey at the top |
| `painted_shading.edge_light` | `0.3` | Painted shading 3: exposed edges gain up to 30% |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 4: up to 45% darker between fragments that touch |
| `painted_shading.blotch` | `0.12` | Painted shading 2: lighter and darker by up to 12% |
| `painted_shading.hidden_underside` | `true` | Painted shading: the undersides are never seen |
| `scatter.min_size_range` | `2.5` | Silhouette 2: the largest at least 2.5 times as long as the smallest |
| `scatter.min_step_ratio` | `1.1` | Silhouette 2: each at least 1.1 times as long as the next |
| `scatter.min_breadth` | `0.3` | Silhouette 3: not a line |
| `scatter.min_radial_spread` | `0.2` | Silhouette 3: not a ring |
| `scatter.min_stand_share` | `0.3` | Silhouette 5: each stands at least 0.3 of its length above the ground |
| `lean.max_upright_share` | `0.15` | Silhouette 4: at most 15% of the side surface within 8 degrees of vertical |
| `lean.min_summit_offset` | `0.15` | Silhouette 6: the summit at least 0.15 of the half extents off the middle |
| `soft_edges` | `true` | Silhouette 4: every edge is soft except where a fragment meets the ground |
| `watertight` | `true` | Parts: every fragment is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Open

Found at the first gates on 2026-10-05 and left as they are: no check was loosened and no spec value changed to pass them.

- **The Bevy load test cannot measure the crevice shadow.** `painted.crevices_darker` finds 0 samples in inside corners on `rubble_1` and `rubble_3` (96 on `rubble_2`): it looks for corners within one connected surface, or between pieces under `overlap`, and a gap of 7 mm between two separate stones is neither. The brief still asks the shadow.
- **Texture use.** `uv.coverage` reads 0.400, 0.371 and 0.336 where the conventions ask 0.4: several fragments, each unwrapped by angle into several islands, on 512 px.
- **Hard edges on `rubble_3`.** `soft_edges`: 34 of 177 vertices share a position with a differently lit vertex. The kit's soft edges leave a hard point where two planes meet at one vertex and not along an edge; the generator does not refuse such a shard, and gate L1 does not see it.
- **A seed with slivers.** `rubble_2` seed 27 builds with degenerate faces and doubled vertices (gate L1 fails it).
- **Sizes.** A layout need reach only 0.82 of the bounds before it is stretched to them, so the fragments come out up to a quarter longer than the table above: `rubble_1`'s largest is 0.315 m, not 0.25 m.

## Decisions

There was no grilling session. The owner gave the decisions below in writing on 2026-10-05, and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the family and its three variants, differing by seed, spread and count; the shape, from `docs/style/rock-shapes.md`; that rubble is cheap ground scatter seen standing and crouching; that the fragments are separate stones in one mesh, lying apart or just touching; that it is broken, weathered fragments of clearly different sizes lying as they fell, tilted, some leaning on a neighbour, and not a tidy ring of equal cubes (the arches and spires were rejected as "too constructed", and the first pebbles for being faceted blocks); that expected values come from this brief and painted shading is asked for in the spec; that a check tuned on rocks a metre across is not loosened or switched off through a spec value.

Proposed by the agent:

- **A group of separate stones is its own spec block, `scatter`, and not `overlap`.** Every rock before this is one closed skin or overlapping pieces (ADR 13). Neither fits. One skin: the whole-mesh checks would pass a group with one small stone inside out, since the volume of the rest stays positive. `overlap`: its checks ask that every piece passes into another (`overlap_touch`) and say how much may be buried, and rubble is the opposite, stones that pass into nothing. So a `scatter` block says what a group is, and its checks read the fragments back from the mesh as its connected closed parts, exactly as the overlap rule does (`pieces_in`, `Solid` and `overlaps` in `tools/validate.py`, reused), with no record from the build:
  - `scatter_count`: how many fragments (`min_count`, `max_count`);
  - `scatter_closed`: each fragment is a closed surface facing outward, asked of each one;
  - `scatter_apart`: no fragment's surface lies inside another;
  - `scatter_on_ground`: each fragment's lowest point is on the floor of the bounds, so none floats;
  - `scatter_stands`: each stands at least `min_stand_share` of its own length above the ground, so none is sunk to a cap;
  - `scatter_size_order`: `min_size_range` and `min_step_ratio`, by length;
  - `scatter_grouped`: every fragment is within `max_gap_m` of another, through to the largest;
  - `scatter_touching`: at least `min_touching` pairs are within the touching distance of each other (1 cm, `[scatter]` in `conventions.toml`);
  - `scatter_not_line` and `scatter_not_ring`: `min_breadth` and `min_radial_spread`, on the fragments' middles seen from above.
  A spec may not have both blocks (`spec.scatter_or_overlap`, gate L0; `spec.scatter` holds the block's own values). Each check has a case that was seen not caught before the check existed (`tests/test_validate.py`, the mutations of `rubble_1`).
- **Fragments do not pass into each other, even where one leans on another.** `tools/paint.py` paints a spec without `overlap` as one solid, and a fragment pushed into its neighbour would then be lit along the join as an exposed edge (the slab's `lit_joins` defect). Kept apart by a few millimetres, the two are painted rightly as they are, and the crevice shadow fills the gap. So "leaning on a neighbour" is a fragment tipped toward a bigger one and lying within a centimetre of it, and a fragment lying on top of another is out of scope. The Bevy load test asks facing outward of the whole mesh and not of each fragment (it does so only for `overlap`); gate L1's `scatter_closed` is the check that holds each one.
- **Size is length.** The greatest distance between two points of a fragment: it does not change when the stone is turned or tipped, as its width seen from above does.
- **Thresholds.** 2.5 and 1.1 for the size order: with five fragments a range of 2.5 is a mean step of 1.26, and 1.1 is the least step at which two stones side by side are told apart from 1.7 m (a tenth of 0.15 m is half a degree there). The largest gap is half the largest fragment's length. It was first the smallest fragment's length (0.08 to 0.09 m), and no layout of five stones 0.25 to 0.09 m long that close together reaches a spread of 0.6 m by 0.5 m: laid in two rows they come to about 0.5 m by 0.36 m. The spreads were kept and the gap widened; this was found at the first builds, from the layouts refused and not from a measurement of a built group. Touching at 1 cm: about a degree from 0.5 m, and inside the reach of the crevice shadow. 0.3 for breadth and 0.2 for radial spread are arithmetic: a line reads 0 on the first and a ring 0 on the second, and stones dropped at random in a circle read about 0.6 and 0.4. 0.3 of the length for standing: between the pebble's plate (0.2 of its width, 0.25 allowed) and the shards drawn here (0.35 to 0.7 before they are tipped). None was measured on a reference; the benchmark has no rubble.
- **The sizes, counts and seeds** 1, 2 and 3, and the budget of 60 triangles a fragment.
- **The construction, and every range in `generator.py`.** A fragment is the space behind planes touching a flattened ellipsoid (the boulder's construction with fewer planes cut deeper, so it is angular and not full), tipped, sunk and cut off by the ground. The group is laid out largest first; each next fragment is slid toward one already placed until it touches or lies a drawn gap away. The group is drawn eight metres wide and shrunk, as the pebble and the boulder are, because the kit's least sizes are a metre rock's.
- **The paint.** The boulder's colour, tints and strengths; band widths as shares of the largest fragment's length; a 512 px texture, by the sum under Texture size.
