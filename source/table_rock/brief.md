# table_rock

A wide flat slab of rock resting on one or two narrow necks, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its table rocks share. The deliverable is three variants, each an asset of its own with its own seed, size and number of necks: `source/table_rock_1`, `source/table_rock_2`, `source/table_rock_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

It is built under the pieces rule of ADR 13, after the slab, the standing stone and the crag: several closed pieces that pass into each other, each softened on its own, and left separate in the mesh. It is the first rock with a piece that does not stand on the ground, and the first whose underside is seen.

## Purpose

An overhang: shelter to stand or build under, and a platform to stand or build on (`docs/style/rock-shapes.md`, Table rock). The game is first person, players are 1.8 m tall, they climb any surface and they build from a kit of 3 m foundations and 3 m walls (ADR 7). So a table rock is used three ways: a player walks under the cap, a player climbs onto the cap and stands there, and a base is set under it or on it. It stands on flat ground. Nothing breaks or moves it yet.

## Viewing

First person, from as close as 0.5 m (ADR 7), and from three places:

- **From beside it**, at 3 m and more: the outline of a cap on its neck, with air under the cap on every side.
- **From underneath.** A player standing under the cap has its underside from 0.3 m (the smallest clearance over a 1.8 m player, 2.0 m, less the eye's 1.7 m) to 1.3 m above the eye, and the neck at arm's length. No rock before this one shows a face that points down. The underside is therefore a finished surface: it gets its share of the texture and its paint like any other.
- **From on top**, standing on the cap: the cap's top at 1.7 m below the eye, and its rim.

The faces lying on the ground, under the necks and the blocks, are never seen.

## Real-world size

The three variants differ in size on purpose.

| Variant | Width (x) | Depth (y) | Height | Under the cap, at least | Necks | Pieces | Character |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `table_rock_1` | 3.6 m | 3.0 m | 2.9 m | 2.0 m | 1 | 3 | the plain one: a player walks under it with 0.2 m over the head |
| `table_rock_2` | 6.4 m | 4.2 m | 4.2 m | 3.0 m | 2 | 5 | a shelter: a wall of the building grid (3 m) stands under it, and a 3 m foundation fits on it |
| `table_rock_3` | 2.4 m | 2.0 m | 1.5 m | 0.9 m | 1 | 3 | a low table: its top is below a player's eye and nobody stands under it; a place to climb onto, or to keep a fire or a chest dry |

The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box. The bounds are the cap's: everything else is under it.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Table rock, and "How they are built"):

1. **A cap on necks.** The dominant piece is the cap: a plate whose outline fills the bounds, held off the ground. Under it stand one or two necks, each a prism that rises from the ground into the cap's underside, and one small block against the foot of each neck. Each is a closed piece of its own; each passes into another, so nothing floats and the cap rests on its necks; and no more than 20% of all their surface is buried inside another piece.
2. **Shelter under the cap.** Seen from straight above, at least 0.6 of the table rock's outline has open air under it from the ground up to the clearance in the table above (2.0, 3.0 and 0.9 m). What has not is where the necks and blocks stand. A cap pressed down toward the ground, or a cap on a pedestal as wide as itself, fails this.
3. **The necks are narrow.** Cut level at half that clearance, the necks together fill at most 0.15 of the outline, and exactly as many pieces pass through that cut as the variant has necks. The blocks are lower than the cut.
4. **The cap overhangs its necks on every side.** Seen from above, the necks (at that cut) stand in from the rim of the outline by at least 0.6, 0.8 and 0.35 m: on the two taller variants a player's shoulders, 0.5 m, are wholly under the cap wherever they stand against a neck. The necks need not be in the middle, and are not: the generator stands a single neck up to a fifth of the way out from the middle, and two necks unequal distances from it.
5. **A top to stand on.** Seen from straight above, at least half of what shows is within 12 degrees of level, the slab's number. The cap tips 2 to 5 degrees; the rest of the view is the chamfers round it.
6. **A clear size order.** A piece's size is the surface it shows. Each piece shows at least 1.3 times what the next shows, the slab's number: the cap, then the necks (the second neck of two is the narrower), then the blocks.
7. **Nothing upright.** The cap's sides are undercut: they lean out from the underside to the rim by 18 to 38 degrees, so the cap is widest at its shoulder and the underside is smaller than the top. The necks taper: where they meet the cap they are narrower than at the ground by 0.25 to 0.4 of their radius, which on a neck as tall as these is 2 to 6 degrees a side, inside the 8 degrees the other rocks call upright. The blocks' sides lean in by 8 to 16 degrees. Judged on the contact sheet: no check asks it, because the two measures the other rocks use do not fit (see Decisions).
8. **Flat caps ringed by chamfers.** A chamfer runs between the cap's top and every side, of a different width on each. Judged on the contact sheet.
9. **A polygonal outline.** The cap has six to eight straight sides of unequal length. Judged on the contact sheet (`top`).

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. ADR 13: the pieces overlap and are not fused.

Each piece is a prism of exact planes (`tools/stone.py`, `prism`). The cap's floor is the level plane of its underside, held above the ground, and its sides lean outward going up. Every edge of the cap is softened, the underside's rim too; a neck or a block meets the ground at a hard edge, so no gap shows under it. Each piece is softened before it meets the others, so the bevel always forms. A soft edge is as wide as the piece's shortest edge has room for, at most 0.035 m and at most 0.012 of the table rock's height: narrower than the slab's 0.045 m, because the top of a neck and a block are small.

A seed draws up to 40 whole table rocks until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_table_rock`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one texture, 1024 px except where a variant's brief says otherwise. The values are the standing stone's and the crag's, so the rocks sit together:

1. **Gradient.** A cool grey `#8c8c9a` at the ground to a light grey `#c8c8c8` at the top of the bounds.
2. **Side shade.** Faces steeper than 45 degrees lose up to 22% at mid height, fading out toward the ground and the top. It goes by how far a face is from level, whichever way it points, so the level underside of the cap takes none.
3. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, in soft patches about 0.4 m across.
4. **Crevice shadow.** Where one piece passes into another the colour loses 45% of its light, fading to nothing 0.2 m out. This hides the joins (ADR 13): a ring of shadow on the underside round each neck, and on the neck under the cap.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane. The edge a piece stands on gets none.

The underside of the cap is painted by the same rules as any other face: there is no rule for a face that points down. What that gives is recorded in each variant's observations.

`hidden_underside` is true: it names the faces lying on the ground, under the necks and blocks, which get almost none of the texture. It does not touch the underside of the cap, which is above the ground.

No growth on the bare stone: moss is a cover, and covers are palette variants on the same mesh (ADR 13; Covers, below).

## Covers

A cover is what lies on the stone: `bare`, or `mossy` (`docs/style/catalogue.md`; snow is not built). The assets above are bare. A mossy one is a palette variant (ADR 13, `CONTEXT.md`): a separate asset, `<base>_mossy`, whose spec names its base as `palette_of` and its `cover`, and differs from the base's only in the growth keys of `painted_shading`. It is the base's mesh, UVs included, with another texture, and the gate holds it to that (`spec.cover`, `spec.palette_of`, `palette.same_mesh`).

Moss is growth as ADR 10 and `tools/paint.py` paint it: a wash from the ground up to a height, and small patches on faces near level and along exposed upper edges. Its colour, how dark it is and how sparse come from the first mossy rock (`source/rock/brief.md`, measured there against the benchmark): olive `#7a8a4d` at the stone's own lightness; patches 50% darker than the stone they sit on; patches over about 25% of near-level faces and along about 40% of exposed upper edges, because the benchmark's moss is sparse. How high the wash reaches and how large a patch is are shares of the stone, not that rock's metres:

- **Reach.** Three tenths of the stone's height, and at most 0.9 m, half the player's height, which is where the first rock's stops. The wash's ragged top wanders up to half its reach either way, so at three tenths it stays under half the height, where the growth along upper edges begins; the two never close into a coat.
- **Patch.** A thirteenth of the narrower side of the footprint, and at most 0.2 m, the benchmark's larger flecks (the first rock: 0.2 m on a 2.6 m side). A stone then carries about a dozen patches across whatever its size.

A table rock's cap is a broad near-level top out in the weather, and that is where its patches lie, with the wash round the foot of the neck. The underside of the cap faces down and is sheltered: nothing settles there, and the painter puts growth only on faces that look up. `table_rock_1_mossy`: 2.9 m tall, so the wash reaches 0.9 m (0.87, at the cap of 0.9), well under the cap's underside at 2.0 m; 3.0 m on its narrower side, so patches of 0.2 m (0.23, at the cap of 0.2).

## Parts

One object and one mesh per variant, with one material. The mesh is three or five closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

1 material slot per variant. A prism of n sides standing on the ground is 17n - 4 triangles once softened, and the cap, whose underside rim is softened too, is 20n - 4: 156 for eight sides. A neck has five or six sides (81 or 98) and a block four or five (64 or 81). The largest table rock of three pieces is then 335 triangles and of five 514: the budgets are 400, the boulder's, and 540, `crag_1`'s. Until the stress scene of ADR 7 exists these are estimates.

## References

- Shape: `docs/style/rock-shapes.md`, Table rock, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/table_rock_variants.png`). A boulder, not a table rock: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes and the climbable flag (ADR 7: not implemented), LODs, snow-capped covers, other stone colours, a table rock that grows out of a cliff face (placement is the game's), darkening the underside as shadow (lighting is the engine's), finished faces under the necks.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces and necks it has, its clearance and overhang, and its budget; and `table_rock_2`'s gives its own texture size.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"table_rock"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_table_rock` | `"#a1a7a1"` | Style and colour: the boulder's grey |
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
| `painted_shading.hidden_underside` | `true` | Painted shading: the faces lying on the ground are never seen |
| `overlap.max_buried_share` | `0.2` | Silhouette 1: no more than 20% of the surface is buried |
| `overlap.min_step_ratio` | `1.3` | Silhouette 6 |
| `table.min_shelter_share` | `0.6` | Silhouette 2 |
| `table.max_neck_share` | `0.15` | Silhouette 3 |
| `top.min_level_share` | `0.5` | Silhouette 5 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size and at least one on two necks, built from pieces under ADR 13; the shape, from `docs/style/rock-shapes.md`; what a table rock must be held to (the cap overhangs its necks, the necks are narrow against the cap, the top is level enough to stand on, the cap rests on its necks); that expected values come from this brief and painted shading is asked for in the spec.

Proposed by the agent, and open to change:

- The three sizes, clearances, neck and piece counts, and seeds; every range in `generator.py`.
- **Thresholds invented for the table rock.** In the spec: 0.6 of the outline sheltered; necks filling at most 0.15 of the outline; an overhang of 0.6, 0.8 and 0.35 m; a buried limit of 0.2 (the standing stone's). In `conventions.toml` (`[table]`): the necks are measured at half the clearance. None is measured on a reference: the rock reference's table rocks are known only from previews.
- That shelter is measured straight up from the ground and the overhang straight down from above, on the grid the other shape checks use (`[planes] view_rays`).
- **No `lean` and no `foot` block.** `lean` asks that the summit, the surface above nine tenths of the height, be off the middle of the bounds; a table rock's summit is its whole cap, which fills the bounds, so the measure reads near zero for every table rock and would have to be switched off by its own value. `foot` counts low level surface that nothing stands over, seen from above; everything under a cap is stood over. Nothing upright (Silhouette 7) is therefore held by the generator's ranges and the contact sheet only.
- One block against each neck, under the cap, for the foot that "How they are built" asks for; none beyond the rim, so the bounds stay the cap's.
- Enlarging the blocks after the first contact sheet, from 0.5 to 0.65 of their neck's radius to 0.7 to 0.95: at the first size one was a few pixels in every view. No spec value changed with it.
- The under-the-cap Bevy tile (`bevy_under`) looks 35 degrees up from 1 m beside the origin, not the 78 degrees used under a tree: at 78 the underside, 0.3 to 0.5 m from the eye, filled the picture with one tone.
- The budgets, from the triangle counts of softened prisms; every painted value, the crag's; a 2048 px texture for the largest.

- **Covers (2026-10-05).** Asked for by the owner through the catalogue (bare, mossy, snow-capped for rocks) and ADR 13: a cover is a palette variant of its base, as a season is of a tree. Proposed by the agent, and open to change: the `cover` field and what a cover variant's spec may change; that the reach is three tenths of the height and at most 0.9 m, and a patch a thirteenth of the narrower side and at most 0.2 m (neither share is measured on a reference: they are the first mossy rock's 0.9 m and 0.2 m turned into shares, the reach lowered from that rock's 0.45 of its height so the wash stays under half way up); the colour, darkness and the two shares of cover, which are that rock's. Which variant of the family got the cover was the coordinator's choice. Not approved.
