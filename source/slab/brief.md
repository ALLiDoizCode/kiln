# slab

A wide, low plate of rock, two or three overlapped, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its slabs share. The deliverable is three variants, each an asset of its own with its own seed, size and number of pieces: `source/slab_1`, `source/slab_2`, `source/slab_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

It is the first rock built under the pieces rule of ADR 13: several closed pieces that pass into each other, each softened on its own, and left separate in the mesh.

## Purpose

Ground a player stands on: ledges, stepping stones, the flat stone at a door or a fire. Also set dressing on a layer's ground beside the boulder (`source/rock`). It sits on flat ground; its underside is never seen. Nothing climbs, breaks or moves it yet.

## Viewing

First person, from as close as 0.5 m (ADR 7), and mostly from above: a player's eye is 1.7 m up and every slab is lower than that, so the top is what is seen, then the rim and the sides.

## Real-world size

The three variants differ in size on purpose: a stepping stone, a slab and a ledge.

| Variant | Width (x) | Depth (y) | Height | Pieces | Character |
| --- | --- | --- | --- | --- | --- |
| `slab_1` | 2.6 m | 2.2 m | 0.5 m | 2 | the plain one: knee high, room for two players to stand |
| `slab_2` | 4.0 m | 3.4 m | 0.8 m | 3 | a ledge: wider than a 3 m foundation of the building grid, hip high, with a small plate at its foot |
| `slab_3` | 1.4 m | 1.2 m | 0.3 m | 2 | a stepping stone: one stride across, ankle to shin high |

The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Slab, and "How they are built"):

1. **Wide and low.** Each variant is at least four times as wide as it is tall: its bounds.
2. **A nearly flat top.** Seen from straight above, at least half of what shows is within 12 degrees of level: the caps of the plates. The rest is their chamfers and the lean of their sides.
3. **Two or three pieces, overlapped.** A dominant plate, a smaller and taller plate pushed halfway into one side of it, and in the largest variant a small low plate at its foot. Each is a closed piece of its own; each passes into another, so nothing floats; and no more than 30% of all their surface is buried inside another piece, where it spends triangles and texture and is never seen.
4. **A clear size order.** A piece's size is the surface it shows. Each piece shows at least 1.3 times what the next shows: no twins.
5. **A polygonal outline.** Each plate has five to seven straight sides of unequal length. Judged on the contact sheet (`top`); no check counts them.
6. **Nothing upright.** Every side leans in by 12 to 24 degrees. At most 15% of the side surface stands within 8 degrees of vertical, the boulder's limit.
7. **The tallest part is off-centre.** The surface above nine tenths of the height, which is part of the taller plate's cap, is centred at least 0.15 of the bounds' half extents from the middle, the boulder's limit.
8. **Flat caps ringed by chamfers.** Each cap tips 2 to 5.5 degrees, all roughly the same way, and a chamfer runs between it and every side, of a different width on each. Judged on the contact sheet.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. ADR 13: the pieces overlap and are not fused.

Each plate is a prism of exact planes (`tools/stone.py`, `prism`): the ground, the sides, the cap, and a chamfer over each side. Its edges are then softened with a one-segment bevel, as wide as its shortest edge has room for and at most 0.045 m, and lit with the normals of the planes on either side, so each plane is lit flat and each edge round. The edge where a plate meets the ground is left hard, so no gap shows under it. Because a plate is convex and softened before it meets the others, the bevel always forms; the fused boulder could keep only two seeds of forty.

A seed draws up to 40 whole slabs until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_slab`: mid grey, `#a1a7a1`, the boulder's colour, so the two sit together.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one 1024 px texture:

1. **Gradient.** Darker toward the ground and lighter toward the top, between the boulder's two tints: a light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground.
2. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, in soft-edged patches about 0.3 m across: half the size of the boulder's, because the open middle of the smallest slab's cap is only about 0.5 m across and a 0.6 m patch gave it one tone (a spread of 0.036 where the load test asks for 0.12).
3. **Crevice shadow.** Where one plate passes into another the colour loses 45% of its light, fading to nothing 0.3 m out. This is what hides the join (ADR 13).
4. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.08 m into each plane, as on the boulder; a chamfer here is 0.1 to 0.3 m wide, so most of each chamfer is lit. The edge a plate stands on gets none, and an edge that runs into a join gets none there.

No growth and no side shade. Moss is a cover, and covers are variants of the palette on the same mesh (ADR 13); these are the bare stone. A slab's sides are 0.2 to 0.5 m tall, which is all edge and no open face, so there is nothing to shade at mid height and nothing for the load test to measure a side shade on.

The underside is never seen, so it gets almost none of the texture. Surface buried inside another plate still takes its share of the texture; the limit in Silhouette 3 is what bounds that waste.

## Parts

One object and one mesh per variant, with one material. The mesh is two or three closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

At most 400 triangles and 1 material slot per variant, the boulder's budget. A plate of n sides is 17n - 4 triangles once softened (98 for six sides), so three plates of seven, six and five sides are 294. Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Slab, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, the boulder's benchmark, seen beside the three variants under Bevy (`benchmarks/out/slab_variants.png`, made with `KILN_SHEET_VIEWS='standard;--back;--stand 3;--stand 0.5;--close' tools/variants_sheet.sh`). It is a boulder and not a slab: it shows the paint and the cost we are judged beside, not the shape. Nothing from it is used.

## Out of scope

Collision shapes, LODs, a single-plate slab (one closed skin, which needs no pieces rule), mossy and snow-capped covers, other stone colours, hand-painted detail, normal maps, a finished underside.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and how many pieces it has. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"slab"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_slab` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `1024` | Painted shading: one 1024 px texture |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1: a cool grey at the ground |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1: a light grey at the top |
| `painted_shading.edge_light` | `0.3` | Painted shading 4: exposed edges gain up to 30% |
| `painted_shading.edge_width_m` | `0.08` | Painted shading 4: fading to nothing 0.05 m into each plane |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 3: the join loses 45% |
| `painted_shading.crevice_width_m` | `0.3` | Painted shading 3: fading to nothing 0.2 m out |
| `painted_shading.blotch` | `0.12` | Painted shading 2: lighter and darker by up to 12% |
| `painted_shading.blotch_size_m` | `0.3` | Painted shading 2: patches about 0.3 m across |
| `painted_shading.hidden_underside` | `true` | Painted shading: the underside is never seen |
| `overlap.max_buried_share` | `0.3` | Silhouette 3: no more than 30% of the surface is buried |
| `overlap.min_step_ratio` | `1.3` | Silhouette 4: each piece shows at least 1.3 times the next |
| `top.min_level_share` | `0.5` | Silhouette 2: at least half of what shows from above is within 12 degrees of level |
| `lean.max_upright_share` | `0.15` | Silhouette 6: at most 15% of the side surface within 8 degrees of vertical |
| `lean.min_summit_offset` | `0.15` | Silhouette 7: the summit at least 0.15 of the half extents off the middle |
| `soft_edges` | `true` | Style and colour: every edge is soft except where a plate meets the ground |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Decisions

There was no grilling session. The owner gave the decisions below in writing on 2026-10-05, and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the family and its three variants, differing by seed and size; that it is built from pieces under the pieces rule of ADR 13 (closed surface and outward normals asked of each piece, a limit on buried surface, every piece touching another); the shape, from `docs/style/rock-shapes.md`; that expected values come from this brief and painted shading is asked for in the spec.

Proposed by the agent:

- The three sizes, the number of pieces in each, and the seeds.
- **Thresholds invented for the pieces rule.** In the spec: at most 0.3 of the surface buried, and a size step of 1.3. In `conventions.toml` (`[overlap]`): two pieces are joined when at least 0.02 of the smaller one's surface lies inside the other; a point of a surface is buried when the space 0.1 mm in front of it is inside another piece; and the surface is sampled at points no further apart than a ninety-sixth of the longest side of the bounds. None is measured on a reference: the rock reference's pieces cannot be read from its previews, and the benchmark's rocks are one skin each.
- The construction: plates as prisms of exact planes, all standing on the ground, the taller one pushed 0.56 to 0.7 of the way out along the dominant one's radius; every range in `generator.py`.
- The budget of 400 triangles, the boulder's.
- The paint: the boulder's colour, tints, edge light, crevice shadow and blotch strength; blotches half the boulder's size; no growth and no side shade, for the reasons under Painted shading. An edge light of 0.05 m and a crevice of 0.2 m were tried first and showed too little for the load test (edges 1.12 times open faces where 1.15 is asked), so the boulder's 0.08 and 0.3 m are used; `slab_3` has narrower bands of its own.
- The 12 degrees that counts as level (`[top] level_deg` in `conventions.toml`) and the half of the view that must be (`top.min_level_share`): a cap tips at most 5.5 degrees, and the chamfers and leaning sides take the rest of the view. Not measured on a reference.
- How a join is painted (`tools/paint.py`): pieces are baked apart; the shadow at a join is full where another piece hides a sixteenth of the sky (`join_sky_hidden` in `conventions.toml`), against a fifth within one piece; and edge light fades out in that shadow. Before this, joins were lit as exposed edges: inside corners measured 1.06 times open faces.
- In the load test, a face of another piece near a point that is not buried counts as a join there, never as an exposed edge.
- That a plate resting on another, face to face, counts as joined to it (`overlap_touch` measures surface inside another piece, not how deep it goes).
