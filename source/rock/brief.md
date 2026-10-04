# rock

A free-standing boulder. The first rock, and the first asset in the soft-edged style of ADR 9.

## Purpose

Set dressing and cover on a layer's ground. A player walks around it and stands beside it. Nothing climbs, breaks or moves it yet, and it is not stood on by design (the top is above head height). It sits on flat ground; its underside is never seen.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 3 to 20 m. At 0.5 m a single plane fills the view, so each plane has to hold up as a flat, clean surface with a soft edge around it, and the silhouette has to work from every side.

## Real-world size

3.0 m wide, 2.6 m deep and 2.0 m tall: a little taller than the 1.8 m player and about the footprint of a small car. Its lowest point is at z = 0 and the origin is on the ground under the centre of its bounding box.

## Silhouette

A full, heavy boulder: it fills most of its bounding box and is still broad high up. Seen beside the benchmark, the first rock was a wedge with a narrow ridge, and the owner asked for mass (Decisions).

1. **Fullness.** The rock holds at least 45% of its bounding box's volume. That is the benchmark's own figure in the tightest box that can be turned about the vertical to fit it (0.450; in its axis-aligned box, where it sits at an angle, 0.412). A box-filling ellipsoid holds 52%. The first rock held 40.9%.
2. **Crown.** The level slice three quarters of the way up is at least 28% of the footprint of the bounds: the benchmark's is 28% (30% in its tightest box), the first rock's was 19%. This is the number that tells a boulder from a wedge; the two have nearly the same volume share.
3. **Planes.** The rock is cut from a block by a small number of large planes of different sizes and tilts. A plane counts as large at 0.4 m2 or more (a 0.63 m square, which at 0.5 m fills about 60 degrees of the view). There are between 6 and 16 large planes, the largest is at least 2 times the area of the median one, and together they hold at least 75% of the visible surface. The rest is soft edge.
4. **No plane dominates a view.** From each of seven directions (front, right, back, left, top, and the two three-quarter views from the front right and the back left) the largest plane fills at most 40% of the rock's outline. The benchmark's largest flat region, measured as the share of its outline within 15 degrees of one direction, is 40% at most (from its right); the first rock's slab was 64% of its back and 45% of the standard three-quarter view.
5. **Three forms, one for every side.** A step on top (a raised slab above a lower shelf), a fracture (a V-shaped groove down one side, widest at the top) and a shoulder (a bench at about half height). Each is a ledge: an inward (concave) corner at least 0.5 m long between two large planes. There is at least one, and from each of the seven directions at least 0.5 m of ledge corner is in plain sight, so no side of the rock is a convex lump.
6. No face reads as part of a sphere: there is no patch of small faces whose tilt changes gradually. The 75% share above is the number that rules it out.

The sides lean inward toward the top, by 2 to 13 degrees, so the base is the widest part and the rock reads as sitting, not balanced.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. Planes are made by cutting a block (`bmesh.ops.bisect_plane`), and the step, the fracture and the shoulder each by cutting a notch between two planes.

The build script draws a rock from a seed: nine sides round a footprint between an ellipse and the bounds' rectangle, a tipped top, then the three forms, placed by side number so that they sit about a third of the way round from each other. A cut is redrawn when it would leave an edge too short to bevel or a plane too small to be a large one; a seed draws up to 40 whole rocks until one meets this brief's numbers, and if none does the build fails and says why. Nothing is left out silently. The build tests the shape only. Of seeds 1 to 40, 39 give a shape that meets this brief (seed 28 fails the build and says why), and 32 of those also pass the painted and UV checks of the Bevy load test; the other 7 fail that gate by check id (3 on UV layout, 3 on growth cover, 1 on a bevel triangle lit from behind). Seed 2 is shipped: from the standard three-quarter view it shows the fracture and the shoulder with the slab above them, the step shows from the back, the left and the back left, and its outline has an inward corner in the front, right, back and left views.

Edges are softened with a one-segment bevel, 0.07 m wide, and smooth shading whose normals are taken from the planes: each plane is lit as perfectly flat and the bevel strip between two planes blends from one to the other. The benchmark gets soft edges from smooth shading alone on a sculpted mesh; on a mesh of exact planes that would smear light across every plane, which is the "part of a sphere" look this brief rules out. The edge where the rock meets the ground is left hard, so no gap shows under it.

One material:

- `m_rock`: mid grey, `#a1a7a1`, the median of the grey (not mossy) texels of the benchmark's texture under this rock's UVs. It is the rock's own colour: what an open face at the very top shows.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one 1024 px texture. Nothing is painted by hand. Read as a painter's layers:

1. **Growth.** Moss covers the rock from the ground up to about 0.9 m, half the player's height, and stops there with a ragged, patchy upper edge. Above that it sits where it would settle: in irregular patches over about 45% of the faces that are near level (the slab and the shelf), and along about half of the exposed edges in the upper part of the rock. Its colour is an olive green, `#7a8a4d`, taken at the rock's own lightness: growth changes the hue and leaves light and dark to the other layers.
2. **Gradient.** The rock is darker toward the base and lighter toward the top. At the top the colour is untouched (a white multiply tint, `#ffffff`); at the ground it is multiplied by a cool grey, `#8c8c9a`, which leaves about 27% of the light. The tint runs evenly with height between the two.
3. **Side shade.** Upright faces are darker at mid height, by up to 22%, fading to nothing toward the ground and the top. The benchmark's sides are darker there than its top and its base.
4. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, in broad soft-edged patches about 0.6 m across, as much lighter as darker.
5. **Crevice shadow.** Inside corners are darker: in the corner of the ledge the colour loses 45% of its light, fading to nothing 0.3 m out along the shelf and up the wall.
6. **Edge light.** Exposed edges are lighter: on the soft edge between two planes the colour gains up to 30%, fading to nothing 0.08 m into each plane, about the width of the bevel. The edge the rock stands on is not exposed and gets none.

The underside is never seen, so it gets almost none of the texture.

At 1024 px the sparsest visible face has about 124 texels per metre (the gate asks for 100; the reason is in `conventions.toml`). The texture is most of the file's 454 kB.

The patches are computed, not drawn: they have no brush marks, chips or strokes. Whether the style needs those is a separate question.

## Parts

One object, one closed mesh. Nothing moves.

## Budget

At most 400 triangles and 1 material slot. The benchmark is 342 triangles. Until the stress scene of ADR 7 exists this is an estimate.

## References

`benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen in the Bevy viewer (`benchmarks/out/Rock_Medium_1.png`, `Rock_Medium_1_close.png`). It is a benchmark: nothing from it is copied or shipped. What we are matching:

- The read: a handful of big flat planes, the largest several times the size of the others, with soft edges between them.
- The step on top, where a raised slab sits above a lower shelf.
- Sides that lean in from a wide base.
- Size class and cost: about 3.2 by 3.0 by 2.3 m and 342 triangles.
- Its mass: the numbers under Silhouette 1, 2 and 4 are measured on it.
- Where its paint varies: moss on top and along upper edges, blotches within planes, darker sides at mid height.

`docs/style/rock-shapes.md` describes how professional plane-built rocks are put together. This rock was reshaped before that reference arrived; it follows some of its habits (nothing upright, a flat cap, long vertical edges) and not others (it is one piece with no foot, and has no wide chamfers).

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
| `planes.large_m2` | `0.4` | Silhouette 3: a plane counts as large at 0.4 m2 |
| `planes.min_area_share` | `0.75` | Silhouette 3 and 6: large planes hold at least 75% of the visible surface |
| `planes.min_count` | `6` | Silhouette 3: between 6 and 16 large planes |
| `planes.max_count` | `16` | Silhouette 3: between 6 and 16 large planes |
| `planes.min_size_ratio` | `2.0` | Silhouette 3: the largest is at least 2 times the median |
| `planes.min_ledges` | `1` | Silhouette 5: at least one ledge |
| `planes.ledge_m` | `0.5` | Silhouette 5: a concave corner at least 0.5 m long |
| `planes.max_view_share` | `0.4` | Silhouette 4: the largest plane fills at most 40% of the outline from each direction |
| `planes.min_ledge_views` | `7` | Silhouette 5: ledge corner in plain sight from each of the seven directions |
| `fullness.min_volume_share` | `0.45` | Silhouette 1: at least 45% of the bounding box, the benchmark's figure |
| `fullness.min_crown_share` | `0.28` | Silhouette 2: the slice three quarters of the way up is at least 28% of the footprint |
| `painted_shading.texture_px` | `1024` | Painted shading: one 1024 px texture |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 2: at the ground the colour is multiplied by a cool grey |
| `painted_shading.top_tint` | `"#ffffff"` | Painted shading 2: at the top the colour is untouched |
| `painted_shading.edge_light` | `0.3` | Painted shading 6: exposed edges gain up to 30% |
| `painted_shading.edge_width_m` | `0.08` | Painted shading 6: fading to nothing 0.08 m into each plane |
| `painted_shading.crevice_shadow` | `0.45` | Painted shading 5: the corner of the ledge loses 45% |
| `painted_shading.crevice_width_m` | `0.3` | Painted shading 5: fading to nothing 0.3 m out |
| `painted_shading.growth` | `"#7a8a4d"` | Painted shading 1: olive green moss |
| `painted_shading.growth_height_m` | `0.9` | Painted shading 1: from the ground up to about 0.9 m |
| `painted_shading.growth_up` | `0.45` | Painted shading 1: patches over about 45% of the faces near level |
| `painted_shading.growth_edges` | `0.5` | Painted shading 1: along about half of the exposed upper edges |
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
