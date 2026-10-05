# boulder

One full, heavy, weathered lump of stone, wider than tall, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its boulders share. The deliverable is a run of three sizes, each an asset of its own with its own seed and size: `source/boulder_1`, `source/boulder_2`, `source/boulder_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

The family supersedes `source/rock`, the first boulder: six pieces fused by a boolean union, which read as a stump more than a boulder and built from 2 seeds of 40. `source/rock` stays in place and passing, because many cases in `tests/` use it as their fixture.

## Purpose

Set dressing and cover on a layer's ground, everywhere: the most-used rock. A player walks round it, crouches behind it, steps onto the small one. Placed turned and mixed in size. It sits on flat ground, sunk into it; its underside is never seen. Nothing climbs, breaks or moves it yet.

## Viewing

First person, from as close as 0.5 m (ADR 7) and typically from 3 to 20 m. At 0.5 m one plane fills the view, so each plane has to hold up as a flat, clean surface with a soft edge round it. From 3 m and further what reads is the outline and the light top over darker flanks, and the outline has to be a boulder's from every side.

## Real-world size

Three sizes, each given beside the 1.8 m player.

| Variant | Width (x) | Depth (y) | Height | Beside a 1.8 m player |
| --- | --- | --- | --- | --- |
| `boulder_1` | 1.2 m | 1.0 m | 0.7 m | 0.39 of the player's height: to mid thigh, a stone to sit on or step up on |
| `boulder_2` | 2.0 m | 1.7 m | 1.2 m | two thirds: to the chest, cover for a crouching player |
| `boulder_3` | 3.2 m | 2.7 m | 1.9 m | 1.06: just over the head, hides a standing player; the benchmark rock's size |

Each is 0.58 to 0.6 times as tall as it is wide. Smaller is the pebble's work (its largest is 0.5 m across). The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, from `docs/style/rock-shapes.md` (Boulder: "one full, heavy lump made of a few large planes with broad chamfered corners. Wider than tall"), with every limit that could be measured taken from the benchmark's three rocks (References):

1. **Wider than tall.** No more than 0.65 times as tall as its wider side, measured on the mesh (`low`). The benchmark's rocks measure 0.576 to 0.617 above the ground; `source/rock` is 0.667.
2. **One convex mass.** The stone fills at least 0.89 of its own convex hull (`mass_convex`), and seen from above it covers at least 0.94 of its outline's convex hull (`mass_outline`). The benchmark's rocks fill 0.897 to 0.952 and cover 0.951 to 0.970. `source/rock` fills 0.844 and covers 0.892: the dominant piece is a trunk and the pieces at its foot stand out of it like roots, which is what made it a stump. A crag fills 0.529 and covers 0.866.
3. **Sloping flanks.** At most 0.85 of the side surface is within 20 degrees of upright (`mass_slopes`). The benchmark's rocks have 0.535 to 0.834 there; `source/rock` has 0.946, a crag 0.926 and a block 0.948: a trunk's sides are all wall.
4. **Full.** At least 0.4 of its bounding box's volume, and the level slice three quarters of the way up at least 0.28 of the footprint of the bounds (`fullness`, `crown`). The benchmark's rocks hold 0.410 to 0.532 and 0.282 to 0.396.
5. **Nothing upright.** At most 15% of the side surface stands within 8 degrees of vertical (`lean`), the first boulder's limit, from the benchmark's first rock (0.145).
6. **The tallest part is off-centre.** The surface above nine tenths of the height is centred at least 0.15 of the bounds' half extents from the middle (`summit_off_centre`). The benchmark's rocks: 0.166 to 0.384.
7. **Broad planes and chamfers.** A cap that tips, four to six shoulders round it, five to eight sides and one to three chamfers across corners: twelve to eighteen planes, each lit flat, with a soft edge between every two. Judged on the contact sheet (`clay_wire`, `three_quarter`); no check counts them.
8. **It bulges.** The stone is widest a little above the ground and some of its sides are undercut, so it reads as sunk to near its widest part and not as set down. The benchmark's rocks are widest 0.14 to 0.23 of the way up. Judged on the contact sheet (`front`, `right`).
9. **Twelve seeds are twelve boulders.** Judged on the candidates sheets (`benchmarks/out/boulder_<n>_candidates.png`).

The habits of the shapes document that a boulder does not follow here: several pieces in a size order, and a foot of small blocks. See Decisions.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement.

The stone is the space behind a set of planes (`tools/stone.py`, `solid`), each touching or cutting a little into an ellipsoid that fills the bounds and whose middle is 0.12 to 0.26 of the height above the ground. The planes that face upward are pushed 0.22 to 0.5 of the half extents to one side, so the summit is off the middle, one flank is steep and the other long. Sides face from 12 degrees below level to 24 above, shoulders 34 to 58 degrees above, and the cap is 3 to 11 degrees from level. Its edges are then softened with a one-segment bevel and lit with the normals of the planes on either side (`tools/stone.py`, `finish`). The edge where it meets the ground is left hard.

A soft edge is 0.012 to 0.02 of the stone's width (the first boulder's 0.05 m of 3.0 m is 0.017). The generator draws every boulder 3 m wide, softens it there with edges 0.035 to 0.06 m wide, and shrinks it to its size; the three sizes are one construction.

A seed draws up to 2000 whole boulders until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_boulder`: mid grey, `#a1a7a1`, the first boulder's and the pebble's colour.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one texture. The first boulder's bands, each as a share of the stone's width as the pebble's are; each variant's brief gives the metres.

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground.
2. **Side shade.** Upright faces are darker at mid height, by up to 22%.
3. **Blotches.** Lighter and darker by up to 12%, in soft patches a fifth of the stone's width across (the first boulder: 0.6 m of 3.0 m) and never more than 0.3 m. From 0.5 m, the closest a stone is seen (ADR 7), a view about 60 degrees wide shows 0.6 m of a plane: a patch 0.64 m across, as a fifth of the large boulder is, fills it with one tone, and the first large boulder was one blank tone from there (`benchmarks/out/boulder_variants.png`, first round). At 0.3 m two patches cross the view.
4. **Edge light.** Exposed edges gain up to 30%, fading out one thirty-seventh of the width into each plane (the first boulder: 0.08 m of 3.0 m).
5. **No crevice shadow.** The stone is convex and has no inside corner, so its spec asks none, as the pebble's.

No growth: moss is a cover, and covers are variants of the palette on the same mesh (ADR 13). These are the bare stone.

**Texture size.** The conventions ask 100 texels per metre of every visible face. The visible surface is about two footprints of the bounds at three quarters of their area; a layout uses at least 0.4 of its texture, and the sparsest face of an unwrap by angle gets about half the average density, so a texture needs about 2 x 10,000 / 0.4 = 50,000 texels per square metre of stone. That is 90,000 texels for the small boulder (1.8 m2), 255,000 for the medium (5.1 m2) and 650,000 for the large (13 m2): 512 px, 1024 px and 1024 px, the next powers of two.

## Parts

One object and one mesh per variant, with one material. The mesh is one closed skin. Nothing moves.

## Budget

At most 400 triangles and 1 material slot per variant, the first boulder's budget; the benchmark's rocks are 244 to 522. A softened solid of e edges above the ground is about 4e triangles, and eighteen planes have about 45 edges: about 180. Until the stress scene of ADR 7 exists this is an estimate.

## References

- Shape: `docs/style/rock-shapes.md`, Boulder. The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `Rock_Medium_1`, `Rock_Medium_2` and `Rock_Medium_3` of `benchmarks/quaternius-stylized-nature/glTF/` (the pack has no big or small rock), seen beside the three variants under Bevy (`benchmarks/out/boulder_variants.png`). Measured on 2026-10-05 with the gate's own functions (`tools/validate.py`: `check_low`, `check_fullness`, `check_lean`, `check_mass`), each rock cut off at the ground it is modelled to stand in (z = 0; they are sunk 0.05 to 0.32 m):

| Measure | Rock_Medium_1 | Rock_Medium_2 | Rock_Medium_3 | `source/rock` | Limit here |
| --- | --- | --- | --- | --- | --- |
| Height over the wider side | 0.617 | 0.606 | 0.576 | 0.667 | at most 0.65 |
| Share of its convex hull filled | 0.897 | 0.952 | 0.897 | 0.844 | at least 0.89 |
| Outline from above, share of its hull | 0.964 | 0.970 | 0.951 | 0.892 | at least 0.94 |
| Side surface within 20 degrees of upright | 0.535 | 0.834 | 0.747 | 0.946 | at most 0.85 |
| Side surface within 8 degrees of upright | 0.145 | 0.391 | 0.475 | 0.000 | at most 0.15 |
| Share of the bounding box filled | 0.412 | 0.532 | 0.410 | 0.460 | at least 0.4 |
| Slice at three quarters of the height, share of the footprint | 0.282 | 0.396 | 0.338 | 0.348 | at least 0.28 |
| Summit off the middle | 0.166 | 0.384 | 0.301 | 0.187 | at least 0.15 |
| Largest steep plane, share of the surface seen | 0.088 | 0.060 | 0.037 | 0.110 | not asked |

Nothing else from the benchmark is used: no mesh, outline or colour.

## Out of scope

Collision shapes, LODs, mossy and snow-capped covers, other stone colours, a boulder with a ledge or a second lump, a finished underside.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, its texture's size and the widths of its painted bands. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"boulder"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_boulder` | `"#a1a7a1"` | Style and colour: the first boulder's grey |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1: a cool grey at the ground |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1: a light grey at the top |
| `painted_shading.edge_light` | `0.3` | Painted shading 4: exposed edges gain up to 30% |
| `painted_shading.blotch` | `0.12` | Painted shading 3: lighter and darker by up to 12% |
| `painted_shading.side_shade` | `0.22` | Painted shading 2: upright faces darker by up to 22% |
| `painted_shading.hidden_underside` | `true` | Painted shading: the underside is never seen |
| `fullness.min_volume_share` | `0.4` | Silhouette 4: at least 0.4 of the bounding box |
| `fullness.min_crown_share` | `0.28` | Silhouette 4: the slice three quarters of the way up, at least 0.28 of the footprint |
| `lean.max_upright_share` | `0.15` | Silhouette 5: at most 15% of the side surface within 8 degrees of vertical |
| `lean.min_summit_offset` | `0.15` | Silhouette 6: the summit at least 0.15 of the half extents off the middle |
| `low.max_height_share` | `0.65` | Silhouette 1: at most 0.65 times as tall as its wider side |
| `mass.min_hull_share` | `0.89` | Silhouette 2: at least 0.89 of its convex hull |
| `mass.min_outline_share` | `0.94` | Silhouette 2: from above, at least 0.94 of its outline's hull |
| `mass.max_steep_share` | `0.85` | Silhouette 3: at most 0.85 of the side surface within 20 degrees of upright |
| `soft_edges` | `true` | Style and colour: every edge is soft except where the stone meets the ground |
| `watertight` | `true` | Parts: one closed skin |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Decisions

There was no grilling session. The owner gave the decisions below in writing on 2026-10-05, and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the boulder as a family in three sizes; that it must read as one heavy weathered lump, not a pile of prisms, a crystal or a stump, and that twelve seeds must be twelve different boulders; that "reads as a stump" is an escaped defect, to be closed with numbers measured on the benchmark's rocks; that `source/rock` stays in place.

Proposed by the agent:

- **One closed skin, not overlapping pieces.** The shapes document asks for several pieces in a size order and a foot, and `source/rock` followed it: its pieces are what made it a stump (Silhouette 2), and the owner has since rejected two families as "too constructed". The benchmark's three rocks are each one mass, 0.90 to 0.95 of their own hull. So a boulder here is one convex solid, softened on its own, as the pebble is: it needs no boolean and no `overlap` block, and `fullness` can be asked of it. The cost is that it has no ledge and no inside corner, which the benchmark's first rock has on its back; a second lump tucked into the first, kept inside the limits of Silhouette 2, is the next thing to try.
- **Planes, not a hull of points.** An earlier experiment (`git show 2b8901e`) took the hull of random points; a hull's faces are triangles, and its lumps read as crystals. Planes touching an ellipsoid give broad faces of four to seven sides. The price is that planes drawn freely often leave an edge too short to soften, so a seed draws many boulders (17 to 1,732 of the 2,000 allowed, over seeds 1 to 40; a seed draws the same stone at every size) before one is kept.
- **The checks.** `mass` (three ids) is new; each has a case in `tests/test_validate.py` seen not caught before the check existed (`stump_boulder`, `rooted_boulder`, `tall_boulder`). `low`, `fullness` and `lean` are reused. Not asked: `planes`, `pieces`, `foot`, `chamfers` (they measure ledges, a size order of pieces, a foot of small blocks and chamfers between large planes on a rock 3 m across) and `rounded` (the benchmark's largest steep plane is 0.037 to 0.088 of its surface, but its surface is not flat planes, so the number is not comparable; these boulders measure 0.09 to 0.14, and a limit of 0.1 left 5 seeds of 12 without a build).
- **Thresholds.** Each limit of Silhouette 1 to 4 is the worst of the benchmark's three rocks, rounded outward by the agent: 0.617 to 0.65, 0.897 to 0.89, 0.951 to 0.94, 0.834 to 0.85, 0.410 to 0.4, 0.282 to 0.28. The 20 degrees of `mass_slopes` is the agent's: the angle at which the three rocks and `source/rock` are furthest apart of 8, 20 and 30. 15% upright and 0.15 off-centre are the first boulder's, measured on the first benchmark rock only; the other two would fail 15% (0.391 and 0.475), and it is kept because a check is not loosened.
- The three sizes, the seeds, the budget, every range in `generator.py`, the texture sizes, and the paint (the first boulder's colour, tints and strengths, without its moss).
