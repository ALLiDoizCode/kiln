# rock

A free-standing boulder. The first rock, and the first asset in the soft-edged style of ADR 9.

## Purpose

Set dressing and cover on a layer's ground. A player walks around it and stands beside it. Nothing climbs, breaks or moves it yet, and it is not stood on by design (the top is above head height). It sits on flat ground; its underside is never seen.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 3 to 20 m. At 0.5 m a single plane fills the view, so each plane has to hold up as a flat, clean surface with a soft edge around it, and the silhouette has to work from every side.

## Real-world size

3.0 m wide, 2.6 m deep and 2.0 m tall: a little taller than the 1.8 m player and about the footprint of a small car. Its lowest point is at z = 0 and the origin is on the ground under the centre of its bounding box.

## Silhouette

A full, heavy boulder built the way `docs/style/rock-shapes.md` says designed rocks are built: several pieces pushed together, in a clear size order, settled on a foot, with nothing upright. The second rock was full enough but read as a cut block, "more a stone armchair than a boulder" (Decisions, 2026-10-04, third round).

1. **Fullness.** The rock holds at least 45% of its bounding box's volume. That is the benchmark's own figure in the tightest box that can be turned about the vertical to fit it (0.450; in its axis-aligned box, where it sits at an angle, 0.412). The second rock held 56.2%; this one holds 46.0%, because its pieces and its foot reach to the bounds and its main mass leans.
2. **Crown.** The level slice three quarters of the way up is at least 28% of the footprint of the bounds: the benchmark's is 28% (30% in its tightest box), the first rock's was 19%. This is the number that tells a boulder from a wedge.
3. **Several pieces, in a size order.** One dominant piece, a tall and a low secondary piece set against it, and three small pieces at its foot, joined into one closed mesh. At least 5 pieces each show 0.2 m2 or more of surface in the finished mesh; the dominant one shows at least 3 times what the next shows, and every piece at least 1.15 times the next, so no two are twins. A piece's size is the surface it shows, which is measured on the mesh; the build's record of the pieces is held against the mesh and is not taken on trust (`CONTEXT.md`, piece record).
4. **A foot.** On at least 2 of the rock's four sides there is 0.15 m2 or more of near-level surface below 0.3 of its height that nothing stands over: the tops of the small pieces, reaching out past the main mass. The benchmark has this on two sides (0.26 and 0.15 m2, measured the same way); the second rock had none.
5. **Nothing upright.** At most 15% of the side surface stands within 8 degrees of vertical. The benchmark's share is 14.5%; the second rock's was 46.0%.
6. **The tallest part is off-centre.** The surface above nine tenths of the height is centred at least 0.15 of the bounds' half extents from the middle. The benchmark's is 0.166 away.
7. **Big chamfers.** At least 3 planes of a middle size, 0.1 m2 up to the 0.4 m2 that makes a plane large, each at least 0.2 m across at its narrowest and each cutting the corner between two or more large planes. The second rock had none: every plane of it was a large one.
8. **Planes.** A plane counts as large at 0.4 m2 or more (a 0.63 m square, which at 0.5 m fills about 60 degrees of the view). There are between 6 and 16 large planes, the largest is at least 2 times the area of the median one, and together they hold at least 60% of the visible surface. The rest is the chamfers, the small pieces of the foot and soft edge. (It was 75% when every plane had to be a large one; see Decisions.)
9. **No plane dominates a view.** From each of seven directions (front, right, back, left, top, and the two three-quarter views from the front right and the back left) the largest plane fills at most 40% of the rock's outline, the benchmark's own most.
10. **A form on every side.** A ledge is an inward (concave) corner at least 0.5 m long between a large plane and a plane of at least 0.15 m2: the corner between the dominant piece's wall and a piece set against it. There is at least one, and from each of the seven directions at least 0.5 m of ledge corner is in plain sight, so no side of the rock is a convex lump. In the second rock the forms were a step, a fracture and a shoulder cut into one block; here they are the joints between pieces.
11. No face reads as part of a sphere: there is no patch of small faces whose tilt changes gradually. The large-plane share above is the number that rules it out; a ball pushed about by noise measures 0.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. Each piece is a convex solid cut from a block by planes (`bmesh.ops.bisect_plane`), and the pieces are joined with Blender's exact boolean union.

The build script draws a rock from a seed. The dominant piece stands in one corner of the bounds, touching two of their sides, with eight sides that lean in by 9 to 12 degrees and a cap tipped 6 to 10 degrees toward the opposite corner; the two walls that face away from its corner are each folded down their length. One corner of the cap and two stretches of its rim are cut by chamfers. Every other piece stands astride one of the dominant piece's upright edges, so that piece falls away from it on both flanks, and leans on it: its hidden back tips into the dominant piece. The tall secondary and the first foot stand on one side, the second and third foot on the next, and the low secondary at the corner behind.

A piece is redrawn (up to 40 times) until it joins the rest without leaving an edge shorter than 0.15 m, a sliver of plane, or an overhanging face in sight; its flanks are placed clear of the dominant piece's upright edges by construction. A seed draws up to 200 whole rocks until one meets every number in this brief, and if none does the build fails and lists why each was refused. Nothing is left out silently. The build measures the shape with the gate's own checks, and also refuses a rock whose soft edges did not form or whose soft-edge normals would be lit from behind, which the Bevy load test would otherwise find later. Seed 5 is shipped: its tenth rock meets the brief, in about 4 seconds. Of seeds 1 to 40 only 5 and 37 give a rock that meets this brief, and both of those pass every later gate; the other 38 fail the build and say why (`review/final/observations.md`).

Edges are softened with a one-segment bevel, 0.05 m wide (0.07 m on the second rock; the small pieces have edges too short for it), and smooth shading whose normals are taken from the planes: each plane is lit as perfectly flat and the bevel strip between two planes blends from one to the other. The edge where the rock meets the ground is left hard, so no gap shows under it.

One material:

- `m_rock`: mid grey, `#a1a7a1`, the median of the grey (not mossy) texels of the benchmark's texture under this rock's UVs.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one 1024 px texture. Nothing is painted by hand. Read as a painter's layers:

1. **Growth.** Moss covers the rock from the ground up to about 0.9 m, half the player's height, and stops there with a ragged, patchy upper edge. At the base it is an olive green, `#7a8a4d`, taken at the rock's own lightness: a wash that changes the hue and not the value, as the benchmark's base is (measured below). Above that it sits where it would settle, in small broken patches about 0.2 m across: over about 25% of the faces that are near level, and along about 40% of the exposed edges in the upper part of the rock. Those patches are 50% darker than the rock they sit on.
2. **Gradient.** The rock is darker toward the base and lighter toward the top. At the top the colour is multiplied by a light grey, `#c8c8c8`, which leaves about 58% of the light; at the ground by a cool grey, `#8c8c9a`, which leaves about 27%. The tint runs evenly with height between the two.
3. **Side shade.** Upright faces are darker at mid height, by up to 22%, fading to nothing toward the ground and the top.
4. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, in broad soft-edged patches about 0.6 m across, as much lighter as darker.
5. **Crevice shadow.** Inside corners are darker: in the corner where a piece meets the dominant one the colour loses 45% of its light, fading to nothing 0.3 m out.
6. **Edge light.** Exposed edges are lighter: on the soft edge between two planes the colour gains up to 30%, fading to nothing 0.08 m into each plane. The edge the rock stands on is not exposed and gets none.

The underside is never seen, so it gets almost none of the texture.

**Measured against the benchmark.** Both rocks under Bevy in the `--close` view, same camera and light, a 9 px square averaged with ImageMagick and turned into linear luminance:

| Region | Benchmark | Ours, top tint `#ffffff`, growth at the rock's lightness | Ours as specified |
| --- | --- | --- | --- |
| Bare rock on the lit top | 0.34 to 0.36 (`#9ba2a6`) | 0.51 (`#b8bcb8`) | 0.37 to 0.38 (`#a0a4a0`) |
| Moss on the lit top | 0.25 (`#838d76`), 0.73 of the rock beside it | as light as the rock (`#b7c487` on the second rock) | 0.21 (`#788358`), 0.57 of the rock beside it |
| Moss on a lit side | 0.08 (`#48533d`), 0.41 of the rock beside it | none there | none there |
| Bare rock on a lit side | 0.18 to 0.19 (`#757972`) | 0.28 to 0.37 | 0.20 to 0.28 (`#787b7a`) |
| Growth at the base, lit side | 0.17 to 0.19 (`#697554`), 0.94 of the side above it | 0.18 to 0.22 (`#6d7850`) | 0.15 to 0.18 (`#656f4b`) |

What followed from it: `top_tint` went from `#ffffff` to `#c8c8c8`, because our top and sides were about 1.45 times as light as the benchmark's while our base already matched; `growth_darker` is 0.5, between the benchmark's 0.41 where a fleck is sharp and 0.73 where the sample blurs it with the rock round it; the base growth keeps the rock's own lightness, as the benchmark's does (0.94); `growth_patch_m` is 0.2 m, the size of the benchmark's larger flecks; and the cover fell from 45% of level faces to 25%, and from half the upper edges to 40%, because the benchmark's moss is sparse.

At 1024 px the sparsest visible face has about 139 texels per metre (the gate asks for 100; the reason is in `conventions.toml`). The texture is most of the file's 551 kB.

The patches are computed, not drawn: they have no brush marks, chips or strokes. Whether the style needs those is a separate question.

## Parts

One object, one closed mesh. Nothing moves.

## Budget

At most 400 triangles and 1 material slot. The benchmark is 342 triangles. Until the stress scene of ADR 7 exists this is an estimate.

## References

`benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen in the Bevy viewer (`benchmarks/out/Rock_Medium_1.png`, `Rock_Medium_1_close.png`). It is a benchmark: nothing from it is copied or shipped. What we are matching:

- The read: a handful of big flat planes, the largest several times the size of the others, with soft edges between them.
- Its lean and its foot: the numbers under Silhouette 4, 5 and 6 are measured on it.
- Sides that lean in from a wide base.
- Size class and cost: about 3.2 by 3.0 by 2.3 m and 342 triangles.
- Its mass: the numbers under Silhouette 1, 2 and 4 are measured on it.
- Where its paint varies, and how dark its moss is: small dark flecks on top and along upper edges, a wash at the base, blotches within planes, darker sides at mid height.

`docs/style/rock-shapes.md` describes how professional plane-built rocks are put together, and `docs/style/refs/rock-shapes/` holds the previews it was read from. This rock is built by its habits: several pieces, a size order, nothing upright, the tallest part off-centre, a foot, flat caps, long vertical edges and big chamfers. Each has a number under Silhouette except flat caps and long vertical edges, which are judged on the contact sheet.

What we are not matching: the brushwork of its hand-painted texture (ours is computed from the shape, so it has no strokes or chips), and its sculpted, slightly uneven planes (measured at a 1 degree tolerance, only 11% of its surface lies in large planes; ours are exact).

## Out of scope

Variants, LODs, collision shapes, hand-painted detail, normal maps, a finished underside.

## Numbers

Every value in `spec.json`, and the sentence above it comes from. `tools/lint_spec.py` fails if a row and the spec disagree, or if the spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["rock"]` | Parts: one object |
| `bounds_m.min` | `[-1.5, -1.3, 0.0]` | Real-world size: 3.0 by 2.6 m in plan, lowest point at z = 0, origin under the centre |
| `bounds_m.max` | `[1.5, 1.3, 2.0]` | Real-world size: 2.0 m tall |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_rock` | `"#a1a7a1"` | Style and colour: mid grey from the benchmark's texture |
| `planes.large_m2` | `0.4` | Silhouette 8: a plane counts as large at 0.4 m2 |
| `planes.min_area_share` | `0.6` | Silhouette 8 and 11: large planes hold at least 60% of the visible surface |
| `planes.min_count` | `6` | Silhouette 8: between 6 and 16 large planes |
| `planes.max_count` | `16` | Silhouette 8: between 6 and 16 large planes |
| `planes.min_size_ratio` | `2.0` | Silhouette 8: the largest is at least 2 times the median |
| `planes.min_ledges` | `1` | Silhouette 10: at least one ledge |
| `planes.ledge_m` | `0.5` | Silhouette 10: a concave corner at least 0.5 m long |
| `planes.ledge_plane_m2` | `0.15` | Silhouette 10: between a large plane and a plane of at least 0.15 m2 |
| `planes.max_view_share` | `0.4` | Silhouette 9: the largest plane fills at most 40% of the outline from each direction |
| `planes.min_ledge_views` | `7` | Silhouette 10: ledge corner in plain sight from each of the seven directions |
| `fullness.min_volume_share` | `0.45` | Silhouette 1: at least 45% of the bounding box, the benchmark's figure |
| `fullness.min_crown_share` | `0.28` | Silhouette 2: the slice three quarters of the way up is at least 28% of the footprint |
| `pieces.min_count` | `5` | Silhouette 3: at least 5 pieces show |
| `pieces.min_shown_m2` | `0.2` | Silhouette 3: a piece shows when 0.2 m2 or more of it is on the surface |
| `pieces.min_dominant_ratio` | `3.0` | Silhouette 3: the dominant piece shows at least 3 times what the next shows |
| `pieces.min_step_ratio` | `1.15` | Silhouette 3: every piece shows at least 1.15 times the next |
| `foot.min_sides` | `2` | Silhouette 4: on at least 2 of the four sides |
| `foot.min_side_m2` | `0.15` | Silhouette 4: 0.15 m2 or more of low near-level surface; the benchmark's weaker side |
| `chamfers.min_count` | `3` | Silhouette 7: at least 3 chamfers |
| `chamfers.min_m2` | `0.1` | Silhouette 7: a middle size, from 0.1 m2 |
| `chamfers.min_width_m` | `0.2` | Silhouette 7: at least 0.2 m across at its narrowest |
| `lean.max_upright_share` | `0.15` | Silhouette 5: at most 15% of the side surface within 8 degrees of vertical; the benchmark's 14.5% |
| `lean.min_summit_offset` | `0.15` | Silhouette 6: the summit at least 0.15 of the half extents off the middle; the benchmark's 0.166 |
| `painted_shading.texture_px` | `1024` | Painted shading: one 1024 px texture |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 2: at the ground the colour is multiplied by a cool grey |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 2: at the top by a light grey; measured against the benchmark |
| `painted_shading.edge_light` | `0.3` | Painted shading 6: exposed edges gain up to 30% |
| `painted_shading.edge_width_m` | `0.08` | Painted shading 6: fading to nothing 0.08 m into each plane |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 5: the corner loses 45% |
| `painted_shading.crevice_width_m` | `0.3` | Painted shading 5: fading to nothing 0.3 m out |
| `painted_shading.growth` | `"#7a8a4d"` | Painted shading 1: olive green moss |
| `painted_shading.growth_height_m` | `0.9` | Painted shading 1: from the ground up to about 0.9 m |
| `painted_shading.growth_up` | `0.25` | Painted shading 1: patches over about 25% of the faces near level |
| `painted_shading.growth_edges` | `0.4` | Painted shading 1: along about 40% of the exposed upper edges |
| `painted_shading.growth_darker` | `0.5` | Painted shading 1: the patches are 50% darker than the rock; measured against the benchmark |
| `painted_shading.growth_patch_m` | `0.2` | Painted shading 1: patches about 0.2 m across |
| `painted_shading.blotch` | `0.12` | Painted shading 4: lighter and darker by up to 12% |
| `painted_shading.blotch_size_m` | `0.6` | Painted shading 4: patches about 0.6 m across |
| `painted_shading.side_shade` | `0.22` | Painted shading 3: upright faces up to 22% darker at mid height |
| `painted_shading.hidden_underside` | `true` | Painted shading: the underside is never seen |
| `soft_edges` | `true` | Style and colour: every edge is soft except where the rock meets the ground |
| `watertight` | `true` | Parts: one closed mesh |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Decisions

There was no grilling session: the owner gave the decisions below in writing on 2026-10-04 and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the name; purpose and first-person viewing from 0.5 m; the benchmark; about 3.0 by 2.6 by 2.0 m with the lowest point at z = 0 and the origin under the centre; at most 400 triangles and one material; `m_rock` as one flat mid grey sampled from the benchmark's texture; an asymmetric boulder of a small number of large planes of clearly different sizes and tilts, with at least one ledge or step and no face that reads as part of a sphere; plane cuts as the technique; a seeded build script with one fixed seed; variants, LODs and collision out of scope. Painted shading, UVs and textures were out of scope at first; on 2026-10-04 the owner asked for painted shading generated by script from the shape and the spec, with a base-to-top gradient, edge light, crevice shadow and moss or growth toward the base, and with the rock's shape left alone.

Proposed by the agent: the exact bounds (centred in x and y); the hex value `#a1a7a1`; every number under `planes` (what large means, the 75% share, 6 to 16 planes, the size ratio of 3, and a ledge as a 0.5 m concave corner between two large planes); the edge treatment (0.07 m one-segment bevel with plane normals, hard edge at the ground); the flat underside at z = 0; the seed. For painted shading, every value: both tints, the growth colour and its height, the edge-light and crevice amounts and widths, the 1024 px texture (512 px falls below the gate's texel density; 2048 px triples the file for no difference seen at 0.5 m), and giving the underside almost none of it. The values were tuned by eye against the benchmark in the Bevy viewer and are the first thing to change at review.

On 2026-10-04 the owner looked at the rock beside the benchmark and decided it was too thin. Given by the owner then: it is to be a full, heavy boulder that fills most of its bounding box; one plane must not dominate a view; it needs secondary forms of the benchmark's kind (a top slab or step, a fracture or groove, a shoulder) that read at 3 m and from every side; the generator must either give a rock that passes or fail and say why; and the paint needs growth on upward faces and along upper edges, blotches within planes and darker sides at mid height, computed by script, with no imitation of brush marks.

Proposed by the agent in answer, and open to change:

- Fullness as two numbers, volume share (0.45) and crown (0.28), both the benchmark's measured values. Volume share alone does not separate the first rock from the benchmark (0.409 against 0.412 in their axis-aligned boxes), which is why the crown is there. The shipped rock is well above both (0.562 and 0.384): fuller than the benchmark.
- 0.4 as the most of an outline one plane may fill, from the benchmark's largest flat region; the seven directions; and "ledge corner in plain sight from all seven" as what "reads from every side" means.
- `planes.min_size_ratio` lowered from 3.0 to 2.0. The first rock reached 4.68 only through the slab that filled most of a view, which is what the owner rejected. With no plane above 40% of any outline the largest exact plane is about 2 m2, and the shipped rock measures 2.73. A faceted ball measures 1.15, so 2.0 still rules it out. The owner should confirm this one: it loosens a number.
- The other `planes` numbers are unchanged and still met (16 large planes, holding 89% of the surface).
- The construction: nine sides, the three forms placed by side number, every plane a large one, up to 40 rocks per seed; seed 2.
- Every new painted value: 0.45, 0.5, 0.12 over 0.6 m, and 0.22.

"Clearly different tilts" has no number and no check; it is judged on the contact sheet.

On 2026-10-04, third round, the owner looked at the second rock beside the benchmark and agreed with two recommendations. Given by the owner then:

- **Rebuild the shape from several pieces.** The rock was full enough but read as a cut block: near-upright walls, nine similar sides, level shelves. It is to follow the habits of `docs/style/rock-shapes.md` it ignored: several pieces (one dominant, two or three secondary, several small, pushed together), a clear size order with no near-equal twins, a foot, and big chamfers. It should also lean in more, with faces that differ more in size and tilt, and its tallest part off-centre. One closed mesh, the same bounds, the same 400 triangles; the generator stays deterministic and loud.
- **Let moss be darker than the rock.** Growth is allowed its own, darker value, with smaller and more broken patches, as a spec option any asset can use.
- The fullness, crown, view-share and ledge checks stay; a threshold that is wrong for a composed boulder may change, with its reason, and none is weakened to get a pass. Thresholds for the new checks come from the benchmark wherever it can be measured the same way.

Proposed by the agent in answer, and open to change:

- The construction: a dominant piece in one corner of the bounds, five pieces astride its upright edges, an exact boolean union, seed 5.
- Every number under Silhouette 3 to 7. From the benchmark, measured by the same check on its mesh cut off at the ground: the upright share (0.145, so 0.15), the summit's offset (0.166, so 0.15), and the foot (0.26 and 0.15 m2 on its two sides, so 0.15 on 2 sides). Not from the benchmark, because its pieces cannot be read back from a sculpted mesh and its planes are not flat: 5 pieces, the ratios 3.0 and 1.15, and the chamfer sizes. Those four are read from the style reference and from what the generator can reach.
- Three existing numbers changed, each because of what was asked for. **The owner should confirm these.** (1) `planes.min_area_share` from 0.75 to 0.6: it was set when every plane was a large one; chamfers and the pieces of a foot are below 0.4 m2 by definition, and on the shipped rock large planes hold 62%. A noise lump still measures 0. (2) A ledge may be the corner between a large plane and a plane of at least 0.15 m2 (`planes.ledge_plane_m2`): the forms are now pieces set against the dominant one, and a piece that is a fifth of its size has no face of 0.4 m2. Between two large planes the shipped rock has no ledge at all. (3) The soft edge is 0.05 m wide, not 0.07.
- Kept as they were, and met: fullness 0.45 (0.460), crown 0.28 (0.348), the size ratio of 2 (2.23), 6 to 16 large planes (11), and 40% of an outline (0.40 from the front, at the limit).
- For painted shading: the top tint, `growth_darker`, `growth_patch_m` and the two covers, each from the measurement in the table above; and that only the patches are darker, not the growth at the base.

Flat caps and long vertical edges still have no number; they are judged on the contact sheet. "Clearly different tilts" has none either.
