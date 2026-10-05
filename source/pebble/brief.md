# pebble

A small, low, rounded stone for ground scatter: a flat plate with a broad rim, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its pebbles share. The deliverable is a run of three sizes, each an asset of its own with its own seed and size: `source/pebble_1`, `source/pebble_2`, `source/pebble_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

## Purpose

Ground scatter: loose stones on a layer's floor, on ledges, at the foot of the boulder (`source/rock`) and the slabs. Placed by the dozen, turned and mixed in size. A pebble sits on flat ground, a little sunk into it; its underside is never seen. Nothing picks it up, throws it or breaks it yet.

## Viewing

First person. A standing player's eye is 1.7 m above a pebble on the floor, so it is mostly seen from above and from 1.7 m or further. A player climbing has a ledge in front of the face, so the brief keeps the 0.5 m of ADR 7 as the closest it is seen. At 1.7 m the smallest pebble is about 4 degrees across; what reads from there is its outline on the ground and a light top over a darker foot, not its planes. At 0.5 m the largest one fills a third of the view, and its planes and soft edges have to hold up as the boulder's do.

## Real-world size

A run of sizes, each about twice the last, from a pebble for the hand to a stone that takes two hands. Each is given beside the 1.8 m player.

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `pebble_1` | 0.12 m | 0.09 m | 0.025 m | one seventy-second of the player's height: thinner than the sole of a boot |
| `pebble_2` | 0.25 m | 0.20 m | 0.05 m | one thirty-sixth: to the top of a boot's sole |
| `pebble_3` | 0.50 m | 0.38 m | 0.10 m | one eighteenth: to the ankle bone |

Anything larger is the boulder's or the slab's work: the smallest slab is 1.4 m across. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Pebble: "a small, low, rounded polyhedron", and "How they are built"):

1. **Low.** A pebble is a plate: no more than 0.25 times as tall as its wider side, measured on the mesh (`low`). The benchmark's five round pebbles measure 0.19 to 0.24 (References); the three variants are each given 0.2. The first pebbles were 0.32 to 0.42 and read as blocks.
2. **Rounded.** No one steep plane holds more than 0.07 of the surface that is seen (`rounded`): a plane is steep when it is more than 45 degrees from level, whichever way it leans. A rounded stone goes round by many short sides under a broad rim; a cut block shows one big face. On the benchmark's round pebbles the largest steep plane is 0.04 to 0.07 of the surface; on its square pebbles, and on the first pebbles here, 0.10 to 0.16.
3. **Full.** The stone is neither a shard nor a brick. It holds at least 0.4 of its bounding box's volume: a pyramid on the same footprint holds 0.333 and a half ellipsoid 0.524, and a pebble has to be on the ellipsoid's side of the middle between them. And the level slice three quarters of the way up is at least 0.2 of the footprint of the bounds: a pyramid's is 0.063 and a half ellipsoid's 0.344, and 0.2 is the middle between them.
4. **Nothing upright.** Every side leans in. At most 15% of the side surface stands within 8 degrees of vertical, the boulder's limit.
5. **The tallest part is off-centre.** The surface above nine tenths of the height is centred at least 0.15 of the bounds' half extents from the middle, the boulder's limit, so that a pebble is not a dome turned on a lathe. The cap tips to give it.
6. **A plate of deliberate planes.** Six to eight short sides round an uneven outline, a broad plane of the rim over each, and one cap: thirteen to seventeen planes, each lit flat, with a soft edge between every two. Seen from above, the cap and the rim are most of the stone and the sides a narrow border. The count is judged on the contact sheet (`clay_wire`, `top`); no check counts planes. The boulder's `planes` rule is not asked: it wants a ledge, an inside corner between large planes, and a pebble has none.
7. **Settled into the ground.** The sides meet the ground at 55 to 70 degrees from level, with a hard edge and no gap, so the stone reads as sunk to its widest part and not as set down. No side is undercut: on the first pebbles the undercut sides were the big dark faces. Judged on the contact sheet (`front`, `right`).

The habits of the shapes document that a pebble does not follow: several pieces in a size order, a foot of small blocks, a flat cap ringed by chamfers, long vertical edges. Those describe rocks a player stands beside. A pebble is one piece (Decisions).

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement.

The stone is a plate made of exact planes (`tools/stone.py`, `prism`): six to eight sides that lean in, spaced unevenly round the footprint and each standing a little inside it or on it, so the outline is an uneven polygon; they stop at one level, about half way up, and from the top edge of each a plane of the rim rises to the cap at 24 to 36 degrees from level; the cap tips a few degrees, falling a fifth to a third of the stone's height across its width. Its edges are then softened with a one-segment bevel and lit with the normals of the planes on either side, so each plane is lit flat and each edge round (`tools/stone.py`, `finish`). The edge where it meets the ground is left hard, so no gap shows under it.

A soft edge is 0.012 to 0.03 of the stone's width wide: 1.4 to 3.6 mm on the smallest and 6 to 15 mm on the largest. The slab's 12 to 45 mm on plates 1.4 to 4 m across would swallow a pebble's planes whole. The generator therefore draws every pebble one metre wide, softens it there, and shrinks it to its size; the three sizes are one construction.

A seed draws up to 120 whole pebbles until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_pebble`: mid grey, `#a1a7a1`, the boulder's colour, so a pebble at a boulder's foot is the same stone.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one 256 px texture. The boulder's bands are given in metres and were sized for a rock 3 m across; laid on a stone 0.12 m across, its 0.08 m edge light would cover every plane and leave no open face. A band is a feature of the stone, so here each is a share of the stone's width, about the share the boulder's are of its own, and each variant's brief gives the metres.

1. **Gradient.** Darker toward the ground and lighter toward the top, between the boulder's two tints: a light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground. This is the part that reads from a standing eye.
2. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, the boulder's strength, in soft-edged patches about one tenth of the stone's width across. The boulder's are a fifth of its width; a pebble's planes are at most about a third of its width across, and the slab found that a patch as wide as the open middle of a plane gives it one tone.
3. **Edge light.** Exposed edges gain up to 30%, the boulder's strength, fading to nothing one thirtieth of the stone's width into each plane (the boulder: 0.08 m of 3.0 m, one thirty-seventh). The edge it stands on gets none.
4. **No crevice shadow.** A pebble is convex: it has no inside corner for a shadow to lie in, so its spec asks none (`crevice_shadow` and `crevice_width_m` are left out), and the load test fails a pebble on which it finds an inside corner (`painted.crevices_darker`). A later pebble with a notch asks for the boulder's 45%, over one tenth of its width.

No growth and no side shade. Moss is a cover, and covers are variants of the palette on the same mesh (ADR 13); these are the bare stone. A pebble's sides are all edge and no open face, as the slab's are.

**Texture size.** The narrowest thing painted is the edge light, one thirtieth of the width, and it needs about 3 texels across to be a band and not one row: 90 texels per stone width, whatever the size (750 per metre on the smallest, 180 on the largest; the conventions ask 100 of everything). The visible surface is about one and a half footprints, 0.9 of a width squared at these proportions, so about 7,300 texels must be used; at the 0.4 of the texture a layout must use, that is a texture of 135 px, and the next power of two is 256. The boulder's 1024 px would be 380 kB a pebble, for scatter.

The underside is never seen, so it gets almost none of the texture.

## Covers

A cover is what lies on the stone: `bare`, or `mossy` (`docs/style/catalogue.md`; snow is not built). The assets above are bare. A mossy one is a palette variant (ADR 13, `CONTEXT.md`): a separate asset, `<base>_mossy`, whose spec names its base as `palette_of` and its `cover`, and differs from the base's only in the growth keys of `painted_shading`. It is the base's mesh, UVs included, with another texture, and the gate holds it to that (`spec.cover`, `spec.palette_of`, `palette.same_mesh`).

Moss is growth as ADR 10 and `tools/paint.py` paint it: a wash from the ground up to a height, and small patches on faces near level and along exposed upper edges. Its colour, how dark it is and how sparse come from the first mossy rock (`source/rock/brief.md`, measured there against the benchmark): olive `#7a8a4d` at the stone's own lightness; patches 50% darker than the stone they sit on; patches over about 25% of near-level faces and along about 40% of exposed upper edges, because the benchmark's moss is sparse. How high the wash reaches and how large a patch is are shares of the stone, not that rock's metres:

- **Reach.** Three tenths of the stone's height, and at most 0.9 m, half the player's height, which is where the first rock's stops. The wash's ragged top wanders up to half its reach either way, so at three tenths it stays under half the height, where the growth along upper edges begins; the two never close into a coat.
- **Patch.** A thirteenth of the narrower side of the footprint, and at most 0.2 m, the benchmark's larger flecks (the first rock: 0.2 m on a 2.6 m side). A stone then carries about a dozen patches across whatever its size.
- **Edge reach.** The growth along an upper edge reaches one patch in from it (`growth_edge_m`, the patch's own size; the first rock: 0.2 m). Until 2026-10-05 the painter used 0.2 m for every stone, which on a top 0.7 m wide is most of the top: `block_2_mossy` then measured growth on 0.44 of its top where 0.25 was asked.

A pebble is a low plate: its cap is all the level surface it has and nearly all a player sees of it, so the patches on the cap carry the cover, with a thin wash at the ground and growth along the rim of the cap. `pebble_3_mossy`: 0.1 m tall, so the wash reaches 0.03 m; 0.38 m on its narrower side, so patches of 0.03 m (0.029, rounded), and edge growth reaching 0.03 m.

## Parts

One object and one mesh per variant, with one material. The mesh is one closed skin. Nothing moves.

## Budget

At most 150 triangles and 1 material slot per variant. Scatter is placed by the dozen in one view, so it gets under half the boulder's 400; the benchmark's eleven pebbles are 48 to 136 triangles each, its round ones 114 to 136. A softened solid of e edges above the ground is about 4e triangles (two for each soft edge, and as many again for the planes and corners), and a plate of n sides has 4n edges above the ground, so 150 allows about 36 edges: eight sides at most, and fewer if that estimate is low (the build refuses a draw over the budget). Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Pebble, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Pebble_Round_1.gltf` (0.50 m by 0.37 m by 0.10 m, 136 triangles), seen beside the three variants under Bevy (`benchmarks/out/pebble_variants.png`, made with `tools/variants_sheet.sh --low`). Its size and triangle count were read from the file. The two limits of Silhouette 1 and 2 were measured on the benchmark's eleven pebbles with the gate's own measures, on 2026-10-05: the five `Pebble_Round` are 0.191, 0.210, 0.203, 0.220 and 0.241 as tall as their wider side, and their largest steep plane is 0.051, 0.041, 0.067, 0.043 and 0.043 of the surface seen; the six `Pebble_Square` are 0.30 to 0.50 as tall and 0.10 to 0.13. The limits are the round pebbles' worst values, rounded up: 0.25 and 0.07. Nothing else from the benchmark is used: no mesh, outline or colour.

## Out of scope

Collision shapes, LODs, rubble (several fragments placed as one group: its own family), square pebbles, snow-capped covers, other stone colours, a pebble that is picked up or thrown, a finished underside.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and the widths of its painted bands. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"pebble"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `150` | Budget |
| `materials.m_pebble` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `256` | Painted shading, texture size |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1: a cool grey at the ground |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1: a light grey at the top |
| `painted_shading.edge_light` | `0.3` | Painted shading 3: exposed edges gain up to 30% |
| `painted_shading.blotch` | `0.12` | Painted shading 2: lighter and darker by up to 12% |
| `painted_shading.hidden_underside` | `true` | Painted shading: the underside is never seen |
| `fullness.min_volume_share` | `0.4` | Silhouette 3: at least 0.4 of the bounding box |
| `fullness.min_crown_share` | `0.2` | Silhouette 3: the slice three quarters of the way up, at least 0.2 of the footprint |
| `low.max_height_share` | `0.25` | Silhouette 1: at most 0.25 times as tall as its wider side |
| `rounded.max_steep_plane_share` | `0.07` | Silhouette 2: no steep plane above 0.07 of the surface seen |
| `lean.max_upright_share` | `0.15` | Silhouette 4: at most 15% of the side surface within 8 degrees of vertical |
| `lean.min_summit_offset` | `0.15` | Silhouette 5: the summit at least 0.15 of the half extents off the middle |
| `soft_edges` | `true` | Style and colour: every edge is soft except where the stone meets the ground |
| `watertight` | `true` | Parts: one closed skin |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Decisions

There was no grilling session. The owner gave the decisions below in writing on 2026-10-05, and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner on the first review (2026-10-05), after seeing twelve seeds beside the benchmark: the first pebbles passed their gates and did not look like pebbles, most being faceted blocks with one big dark cut face; redo them lower and rounder, nearer the benchmark's flat plate, in our style and with nothing copied from it. The heights, the two limits and the plate construction below are the agent's answer to that.

Given by the owner at the start: the family and its three variants as a run of sizes, differing by seed and size; the shape, from `docs/style/rock-shapes.md`; that expected values come from this brief and painted shading is asked for in the spec; that a check tuned on rocks a metre across is not loosened or switched off through a spec value.

Proposed by the agent:

- **One closed skin, not overlapping pieces.** A pebble is one stone. The pieces rule of ADR 13 exists for shapes that are several blocks (arches, stacks, crags), and its checks ask for at least two pieces, a size order between them and a join. A second piece on a pebble 0.12 m across would be a crumb a few millimetres wide, buried surface and triangles spent on something nobody sees from 1.7 m, and a group of small fragments is the shapes document's Rubble, a family of its own. So a pebble has no `overlap` block and is checked as the boulder is: the whole mesh closed, wound one way and facing outward, and `fullness` asked of it (which cannot be asked of overlapping pieces). It needs no boolean, so the boulder's trouble with fused pieces does not arise: one convex solid, softened on its own.
- **Low and rounded are measured.** The first brief said "small, low, rounded" and no check measured either word: a pebble 0.42 as tall as wide, with a cut face holding 0.16 of its surface, passed. `low` and `rounded` are the two checks; each has a case in `tests/test_validate.py` that was seen not caught before the check existed (`tall_pebble`, `cut_block`), and all 36 of the first generator's pebbles from seeds 1 to 12 failed both. The limits are the worst of the benchmark's five round pebbles, rounded up (References): the rounding, from 0.241 to 0.25 and from 0.067 to 0.07, is the agent's. Steep is 45 degrees, the angle at which `lean` already calls a face a side.
- **The heights.** 0.2 of the width for each size (0.208 for the smallest, to a whole half millimetre), the benchmark pebble's proportion and inside the limit of 0.25.
- **Which of the boulder's rules are asked.** `fullness` and `lean`, for Silhouette 3 to 5. Not `planes`, `pieces`, `foot` or `chamfers`: they measure ledges, a size order of pieces, a foot of small blocks and chamfers 0.2 m wide, none of which a pebble has.
- The three sizes and the seeds 1, 2 and 3.
- **Thresholds.** 0.4 of the box and 0.2 at the crown are each the middle between a pyramid and a half ellipsoid, rounded; they are arithmetic and not measured on a reference. The benchmark's pebbles were not measured for them. 15% upright and 0.15 off-centre are the boulder's.
- The construction, and every range in `generator.py`. The first generator cut the stone by nine to twelve planes touching a tipped ellipsoid; at 0.36 of its width tall, with sides allowed to face down, it gave blocks. Tried first for the plate: planes in three free rings (sides, shoulders, a cap), which was refused 480 times in 480, mostly for an edge too short to soften, because four or five shoulders let the sides between them rise almost to the cap. The kit's `prism` (sides, a chamfer over each, a cap, with every corner computed) is the same plate with no short edges; with these ranges all twelve seeds built at each size, within 14 draws of the 120 allowed. Its rim starts at one level all the way round, as the benchmark pebble's does.
- **One island of texture.** The generator marks the edge round the ground as the only seam, so the visible stone is unwrapped as one dome (`tools/paint.py` unwraps along seams a build script marks, as for a tree's limbs). Unwrapped by angle instead, into several islands, `pebble_2` used 0.344 of its texture where the conventions ask 0.4: the 8 px kept between islands is four times as large a share of a 256 px texture as of the boulder's 1024 px. As one island the three use 0.575 to 0.596. The texture's size was not changed.
- That the generator draws at one metre wide and shrinks: the kit's least sizes (`tools/stone.py`: a plane must keep 4 cm2 inside its soft edges) are for metre rocks, and drawing at one metre leaves the kit untouched.
- The budget of 150 triangles.
- **The paint.** The boulder's colour, tints and strengths. Band widths as shares of the stone's width (a thirtieth for the edge light, a tenth for the blotches), for the reason under Painted shading, which holds for any stone this size whatever the build looks like. A 256 px texture, by the sum under Texture size.

- **Covers (2026-10-05).** Asked for by the owner through the catalogue (bare, mossy, snow-capped for rocks) and ADR 13: a cover is a palette variant of its base, as a season is of a tree. Proposed by the agent, and open to change: the `cover` field and what a cover variant's spec may change; that the reach is three tenths of the height and at most 0.9 m, and a patch a thirteenth of the narrower side and at most 0.2 m (neither share is measured on a reference: they are the first mossy rock's 0.9 m and 0.2 m turned into shares, the reach lowered from that rock's 0.45 of its height so the wash stays under half way up); the colour, darkness and the two shares of cover, which are that rock's. Which variant of the family got the cover was the coordinator's choice. Not approved.
