# stack

Three to five flat stones piled off-centre, each smaller than the one below and turned from it: a cairn, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its stacks share. The deliverable is three variants, each an asset of its own with its own seed, size and number of stones: `source/stack_1`, `_2` and `_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

Built under the pieces rule of ADR 13, as the slab and the crag are (`source/slab/brief.md`): several closed pieces that pass into each other, each softened on its own. It is the first family whose pieces stand on each other and not all on the ground.

## Purpose

A marker somebody made: a cairn beside a path, at a ledge worth finding again, at the way down to the next layer. It is the one rock in the catalogue that reads as placed by a hand, so it must look balanced and not fallen. It sits on flat ground; the underside of its lowest stone is never seen. Nothing climbs, breaks or moves it yet.

## Viewing

First person (ADR 7). Looked for from 5 to 30 m, where it is an outline of stepped stones against the ground; walked up to and looked down on from 0.5 m, a player's eye 1.7 m up and every stack lower than that, so the caps, the rims and the dark lines between the stones are what is seen.

## Real-world size

| Variant | Width (x) | Depth (y) | Height | Stones | Character |
| --- | --- | --- | --- | --- | --- |
| `stack_1` | 0.9 m | 0.8 m | 0.7 m | 4 | the plain one: a cairn up to a player's knee and a little over, 0.39 of a player's height |
| `stack_2` | 1.2 m | 1.05 m | 1.1 m | 5 | a trail marker: hip to waist high, 0.61 of a player's height, seen from across a ledge |
| `stack_3` | 0.5 m | 0.44 m | 0.32 m | 3 | a small pile at a path's edge: shin high, 0.18 of a player's height |

Width and depth are those of the whole asset. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Stack, and "How they are built"):

1. **Three to five stones, one on another.** Each is a closed piece of its own. The lowest stands on the ground; the middle of every other one is over the cap of the stone below it, and there its underside is sunk into that cap by no more than 0.35 of its own thickness: it rests on the stone, neither floating over it nor swallowed by it.
2. **Flat stones.** A stone's thickness (its volume over the area it covers seen from above) is at most 0.5 of its width (the diameter of a circle of that area).
3. **Each smaller than the one below.** Seen from above, each stone covers at most 0.85 of the area the one below it covers. They are also turned: each has its own outline at its own angle. The turn is judged on the contact sheet (`top`); no check measures it.
4. **Piled off-centre.** Each stone sits 0.12 to 0.3 of the lower one's radius off its middle, and the offsets go roughly one way, so the top of the pile (the surface above nine tenths of the height) is centred at least 0.15 of the bounds' half extents from the middle, the boulder's limit.
5. **It would not topple.** At every stone, the centre of mass of all the stones above it is over its cap.
6. **A clear size order.** A piece's size is the surface it shows; each stone shows at least 1.15 times what the next shows, the crag's step: no twins.
7. **Nothing upright.** Every side leans in by 12 to 22 degrees from its own stone's upright; at most 15% of the side surface stands within 8 degrees of vertical, the boulder's limit.
8. **Flat caps ringed by chamfers.** Each cap tips 2 to 5 degrees, back against the tip of the one below, so the pile wobbles upward and does not lean over. Judged on the contact sheet.

Stones that rest on each other bury the faces they rest on. Take a stone of cap and underside area A each and sides of 0.8 A; its cap is about 0.4 A once the chamfers are taken off, and the stone above covers it. Each join then buries about 0.4 A of the lower stone and as much of the upper one, of 2.8 A a stone: about 0.3 to 0.4 of all the surface. The limit is 0.45, above the crag's 0.4.

## Style and colour

ADR 9 and ADR 13, as for the slab. Each stone is a prism of exact planes (`tools/stone.py`, `prism`): an underside, five to seven sides, a cap, and a chamfer over each side. Its edges are softened with a one-segment bevel as wide as its shortest edge has room for, between 0.006 and 0.03 m and at most 0.02 of the stack's height, and lit with the normals of its planes. The edge where the lowest stone meets the ground is left hard; the underside of every other stone has soft edges, because it shows where the stone overhangs.

A seed draws up to 40 whole stacks until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_stack`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

Painted by script (ADR 9, ADR 10; `tools/paint.py`) into one texture, 512 px unless a variant's own brief says otherwise, with the smallest slab's values (`source/slab_3`), which is the nearest rock in size:

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground, the boulder's tints.
2. **Blotches.** The tone drifts lighter and darker by up to 12%, in soft-edged patches about 0.2 m across.
3. **Crevice shadow.** Where one stone rests on another the colour loses 45% of its light, fading to nothing 0.12 m out. This is the dark line between the stones, and what hides the join (ADR 13).
4. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.04 m into each plane.

No growth and no side shade: moss is a cover (ADR 13), and a stone's side is 0.1 to 0.3 m tall, all edge and no open face, as on the slab.

## Parts

One object and one mesh per variant, with one material. The mesh is three to five closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

At most 120 triangles a stone and 1 material slot per variant. A stone of n sides whose every edge is soft is 20n - 4 triangles (116 for six sides), and 17n - 4 when it stands on the ground (115 for seven). Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Stack. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/stack_variants.png`). A boulder, not a stack: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes, LODs, mossy and snow-capped covers, other stone colours, a fallen stack, stacks of round stones, a finished underside.

## Numbers

Every value the variants' `spec.json` files share. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many stones it has and its budget; some give their own paint.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"stack"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `materials.m_stack` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `512` | Painted shading: one 512 px texture |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1 |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1 |
| `painted_shading.edge_light` | `0.3` | Painted shading 4 |
| `painted_shading.edge_width_m` | `0.04` | Painted shading 4 |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 3 |
| `painted_shading.crevice_width_m` | `0.12` | Painted shading 3 |
| `painted_shading.blotch` | `0.12` | Painted shading 2 |
| `painted_shading.blotch_size_m` | `0.2` | Painted shading 2 |
| `painted_shading.hidden_underside` | `true` | The underside of the lowest stone is never seen |
| `overlap.max_buried_share` | `0.45` | Silhouette: no more than 45% of the surface is buried |
| `overlap.min_step_ratio` | `1.15` | Silhouette 6 |
| `pile.max_sink` | `0.35` | Silhouette 1 |
| `pile.max_thickness` | `0.5` | Silhouette 2 |
| `pile.max_size_step` | `0.85` | Silhouette 3 |
| `lean.max_upright_share` | `0.15` | Silhouette 7 |
| `lean.min_summit_offset` | `0.15` | Silhouette 4 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size, built from pieces under ADR 13; the shape, from `docs/style/rock-shapes.md`; that expected values come from this brief and painted shading is asked for in the spec.

Proposed by the agent, and open to change:

- The three sizes, stone counts and seeds; every range in `generator.py`.
- **Thresholds invented for the stack.** In the spec (`pile`): a sink of at most 0.35 of a stone's thickness, a thickness of at most 0.5 of its width, a size step of 0.85; a buried limit of 0.45, from the arithmetic under Silhouette. In `conventions.toml` (`[pile]`): a stone rests on surface within 20 degrees of level, which is a cap and not a chamfer. None is measured on a reference.
- That "smaller or turned" is asked as smaller, with the turn left to the contact sheet.
- That "would not topple" is the centre of mass of the stones above being over the cap below, with no margin, and with the volume where stones pass into each other counted twice.
- The size step of 1.15, the crag's; the summit offset and upright share, the boulder's.
- The budget of 120 triangles a stone; every painted value, the smallest slab's; a 512 px texture; no growth and no side shade.
