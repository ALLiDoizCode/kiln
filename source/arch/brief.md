# arch

Two piers of stacked blocks bridged by one rough slab or by a knot of wedged blocks, with rubble at the feet: rock that ended up as an arch, not a door frame that was built. Made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its arches share. The deliverable is three variants, each an asset of its own with its own seed, size and kind of span: `source/arch_1`, `source/arch_2`, `source/arch_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

It is built under the pieces rule of ADR 13, after the slab, the standing stone, the crag and the table rock: several closed pieces that pass into each other, each softened on its own, and left separate in the mesh. It is the first rock with a hole through it.

## Purpose

A gateway and a natural bridge between ledges (`docs/style/rock-shapes.md`, Arch). The game is first person, players are 1.8 m tall, they climb any surface and they build from a kit of 3 m foundations and 3 m walls (ADR 7). So an arch is used two ways: a player walks through the opening, and a player climbs onto the span and stands on it or crosses it. It stands on flat ground. Nothing breaks or moves it yet.

## Viewing

First person, from as close as 0.5 m (ADR 7), and from three places:

- **From in front or behind**, at 3 m and more: the outline of two piers and a span, with open air between them from the ground up.
- **From inside the opening.** A player walking through has a pier at arm's length on each side and the underside of the span 0.2 to 1.3 m above the eye. The underside and the piers' inner faces are finished surfaces like any other.
- **From on top**, standing on the span: its top 1.7 m below the eye, and its rim.

The faces lying on the ground, under the piers and the rubble, are never seen.

## Real-world size

The three variants differ in size and in kind on purpose. The opening is measured from the front: open air right through, from the ground up.

| Variant | Width (x) | Depth (y) | Height | Opening, at least | Span | Pieces | Character |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `arch_1` | 6 m | 2.0 m | 4.2 m | 1.6 m wide, 2.2 m tall | lintel | 7 | a gateway under a fallen slab: a player walks through with 0.4 m over the head and 0.55 m beside each shoulder |
| `arch_2` | 9.4 m | 2.4 m | 6.0 m | 3.0 m wide, 3.0 m tall | lintel | 8 | a natural bridge: a wall of the building grid (3 m by 3 m) fits in the opening, and the slab is a sloping way across |
| `arch_3` | 5.8 m | 1.7 m | 3.9 m | 1.2 m wide, 2.0 m tall | wedged | 7 | a narrow door under a pointed knot of leaning blocks; one player at a time, 0.2 m over the head |

The opening asked is the upright rectangle a player needs; the hole itself is wider and taller than it and is not a rectangle.

The arch faces the front (-Y): the opening runs through it from front to back, and the piers stand to the left and right. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

The first arches (kept as `tests/fixtures/arch_trilithon.py`) passed every gate and were refused by the owner on 2026-10-05 as constructed: two matched upright piers of squared blocks under a level squared lintel, a door frame of dressed stone (a trilithon). What must read instead, taken from `docs/style/rock-shapes.md` (Arch, and "How they are built"):

1. **Piers, a span, rubble.** Each pier is two irregular blocks, one stacked on and sunk into the other. A lintel arch is bridged by one rough slab, thick enough to be a rock, lying aslant from the lower pier up to the higher. A wedged-block arch is bridged by a knot: the upper block of each pier leaning in over the opening, the narrower pier's far in, and a keystone wedged between them and over the far leaner's end, as deep as the blocks it sits between. Rubble blocks lie against the piers' outer feet. Each is a closed piece of its own; each passes into another, so nothing floats; and no more than 30% of all their surface is buried inside another piece.
2. **One hole right through.** Seen from the front with parallel rays, the arch and the ground enclose exactly one area of open air.
3. **An opening a player walks through.** Inside that hole there is a stretch at least as wide as the table above says (1.6, 3.0 and 1.2 m) that is open from the ground up to at least the height it says (2.2, 3.0 and 2.0 m). Rubble lying in the passage fails this.
4. **The span rests on both piers.** On each side of the opening there is rock without a break straight up from the ground into the span, over at least 0.2, 0.4 and 0.1 m2 of ground.
5. **The opening is not a rectangle.** The piers lean toward each other and their blocks step in and out, and the span slopes or comes to a point: the hole fills at most 0.8 of the upright rectangle drawn round it. The first arches' filled 0.894, 0.939 and 0.912.
6. **The two sides are unlike.** Under a slab one pier is broad and low and the other two thirds as wide and taller; under a knot the broad pier is also the higher, and the narrow one carries the long leaning block. Seen from the front, the highest rock to the left of the opening and the highest to the right differ by at least 0.12 of the arch's height. The first arches' differed by 0.040, 0.035 and 0.009.
7. **The top is not a table.** Seen from straight above, at most 0.35 of what shows is within 12 degrees of level. The first lintel arches showed 0.628 and 0.691. Whether the top can be stood on is no longer asked of any variant, and the `top` block is gone from every spec: a player climbs the slab as any other rock.
8. **Nothing upright.** At most 0.35 of the side surface is within 8 degrees of upright (the first arches: 0.818, 0.856 and 0.791; the benchmark rock 0.145). Every block is a lozenge, widest part of the way up, its sides leaning out below that and in above it by up to 13 to 19 degrees, and the whole block tipped 3 to 8 degrees (a slab 13 to 22, a leaning block of a knot 10 to 32); the blocks of one pier tip the same way, toward the other pier.
9. **The tallest part is off-centre.** The surface above nine tenths of the height is centred at least 0.2 of the bounds' half extents from the middle: it is the high end of the slab, or the knot over an opening that is itself off the middle. The first arches read 0.105, 0.030 and 0.179.
10. **A clear size order.** A piece's size is the surface it shows. Each piece shows at least 1.15 times what the next shows, the crag's number for a shape of many pieces.
11. **A foot that reads.** Rubble blocks 0.13 to 0.17 of the arch's height tall (the first were 0.08) lie against the outer feet of the piers, never in the passage: seen from above, at least two sides of the arch have 0.15 m2 of low, near-level surface that nothing stands over.
12. **No block stands out through the span's face**, and no upper block is a post: an upper block is 0.85 to 0.95 of the width of the block under it, and the span is deeper, front to back, than the blocks it lies on. Judged on the contact sheet.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. ADR 13: the pieces overlap and are not fused.

Each piece is a lozenge of exact planes (`tools/stone.py`, `hull`): an irregular outline of five to seven sides at its widest, a smaller copy of it below and another above, the whole turned and tipped as one. A piece on the ground is cut off level there and meets the ground at a hard edge; every edge of a piece held off the ground is softened. Each piece is softened before it meets the others. A soft edge is as wide as the piece's shortest edge has room for, at most 0.04 m and at most 0.012 of the arch's height.

A seed draws up to 40 whole arches until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_arch`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

The grey is painted over by script (ADR 9, ADR 10; `tools/paint.py`), into one texture. The values are the crag's and the table rock's, so the rocks sit together:

1. **Gradient.** A cool grey `#8c8c9a` at the ground to a light grey `#c8c8c8` at the top of the bounds.
2. **Side shade.** Faces steeper than 45 degrees lose up to 22% at mid height, fading out toward the ground and the top.
3. **Blotches.** Within each plane the tone drifts lighter and darker by up to 12%, in soft patches about 0.4 m across.
4. **Crevice shadow.** Where one piece passes into another the colour loses 45% of its light, fading to nothing 0.2 m out. This hides the joins (ADR 13).
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing 0.06 m into each plane.

The texture is 2048 px: the pieces of `arch_1` have about 60 m2 of surface and those of `arch_2` about 120 m2, and at 1024 px with the packer's 0.4 coverage that is under the 100 texels a metre the conventions ask. `arch_3`, about 30 m2, was first given 1024 px, and the load test read 93 texels a metre on its sparsest triangle (`uv.texel_density`), so it takes 2048 px too.

`hidden_underside` is true: it names the faces lying on the ground, which get almost none of the texture. It does not touch the underside of the span.

No growth on the bare stone: moss is a cover, and covers are palette variants on the same mesh (ADR 13; Covers, below).

## Covers

A cover is what lies on the stone: `bare`, or `mossy` (`docs/style/catalogue.md`; snow is not built). The assets above are bare. A mossy one is a palette variant (ADR 13, `CONTEXT.md`): a separate asset, `<base>_mossy`, whose spec names its base as `palette_of` and its `cover`, and differs from the base's only in the growth keys of `painted_shading`. It is the base's mesh, UVs included, with another texture, and the gate holds it to that (`spec.cover`, `spec.palette_of`, `palette.same_mesh`).

Moss is growth as ADR 10 and `tools/paint.py` paint it: a wash from the ground up to a height, and small patches on faces near level and along exposed upper edges. Its colour, how dark it is and how sparse come from the first mossy rock (`source/rock/brief.md`, measured there against the benchmark): olive `#7a8a4d` at the stone's own lightness; patches 50% darker than the stone they sit on; patches over about 25% of near-level faces and along about 40% of exposed upper edges, because the benchmark's moss is sparse. How high the wash reaches and how large a patch is are shares of the stone, not that rock's metres:

- **Reach.** Three tenths of the stone's height, and at most 0.9 m, half the player's height, which is where the first rock's stops. The wash's ragged top wanders up to half its reach either way, so at three tenths it stays under half the height, where the growth along upper edges begins; the two never close into a coat.
- **Patch.** A thirteenth of the narrower side of the footprint, and at most 0.2 m, the benchmark's larger flecks (the first rock: 0.2 m on a 2.6 m side). A stone then carries about a dozen patches across whatever its size.
- **Edge reach.** The growth along an upper edge reaches one patch in from it (`growth_edge_m`, the patch's own size; the first rock: 0.2 m). Until 2026-10-05 the painter used 0.2 m for every stone, which on a top 0.7 m wide is most of the top: `block_2_mossy` then measured growth on 0.44 of its top where 0.25 was asked.

An arch's moss is the wash round the feet of both piers and over the low blocks, and patches on the tops of the span and the piers where they are near level and along their upper edges. The underside of the span faces down and gets none. `arch_3_mossy`: 3.9 m tall, so the wash reaches 0.9 m (the cap); 1.7 m on its narrower side, so patches of 0.13 m.

## Parts

One object and one mesh per variant, with one material. The mesh is seven or eight closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

1 material slot per variant. A lozenge of n sides held off the ground is 20n - 4 triangles once softened, and one cut off at the ground about 17n - 4, or a few more where the cut passes through its lowest face. Seven pieces of five to seven sides are then at most about 700 triangles and eight about 780: those are the budgets. Until the stress scene of ADR 7 exists these are estimates.

## References

- Shape: `docs/style/rock-shapes.md`, Arch, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/arch_variants.png`). A boulder, not an arch: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes and the climbable flag (ADR 7: not implemented), LODs, snow-capped covers, other stone colours, an arch that grows out of a cliff or joins two ledges (placement is the game's), a round arch of many voussoirs, the rib family's pointed arch, finished faces under the piers.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces it has, its span, opening and bearing, and whatever else differs:

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"arch"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `700` | Budget |
| `materials.m_arch` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.texture_px` | `2048` | Painted shading |
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
| `overlap.max_buried_share` | `0.3` | Silhouette 1: no more than 30% of the surface is buried |
| `overlap.min_step_ratio` | `1.15` | Silhouette 10 |
| `foot.min_sides` | `2` | Silhouette 11 |
| `lean.max_upright_share` | `0.35` | Silhouette 8 |
| `lean.min_summit_offset` | `0.2` | Silhouette 9 |
| `arch.max_box_share` | `0.8` | Silhouette 5 |
| `arch.min_side_step` | `0.12` | Silhouette 6 |
| `arch.max_level_share` | `0.35` | Silhouette 7 |
| `foot.min_side_m2` | `0.15` | Silhouette 11 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every piece is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05: the family, with three variants differing by seed and size, covering the lintel arch and the wedged-block arch, with rubble at the feet, built from pieces under ADR 13; the shape, from `docs/style/rock-shapes.md`; that an arch is a gateway a player walks through and a bridge a player may stand on; that expected values come from this brief and painted shading is asked for in the spec.

Proposed by the agent, and open to change:

- The three sizes, openings, kinds, piece counts and seeds; every range in `generator.py`.
- **A wedged-block arch's piers are one tall block and a leaning block**, not two upright blocks under the knot: nine pieces would have to show nine clearly different sizes, and the leaning blocks are already stacked on the piers.
- **Thresholds invented for the arch.** In the spec: the opening's width and height; rock under the span over 0.2, 0.4 and 0.1 m2 on each side; a buried limit of 0.3 (the slab's, for pieces that lie on each other). None is measured on a reference: the rock reference's arches are known only from previews.
- That the opening is measured from the front with parallel rays on the grid the other shape checks use (`[planes] view_rays`), and that the ground closes the hole.
- **Thresholds for a natural arch, invented after the first arches were refused**: the hole at most 0.8 of its rectangle, the sides at least 0.12 of the height apart, at most 0.35 of the top level, at most 0.35 of the sides upright, the summit 0.2 off the middle, a foot of 0.15 m2. Each is set between what the refused arches measure (Silhouette 5 to 9) and what the shape described here should; none is measured on a reference.
- The pieces of one pier lean the same way, but the two piers lean toward each other, against "pieces in one group lean roughly the same way": an arch is two groups.
- The budgets, from the triangle counts of softened prisms; every painted value, the crag's.

Changed while the generator was reworked, each before any arch of the new kind had passed its gate, and none to pass a shape check:

- The bounds. A slab that slopes 13 to 22 degrees over the opening needs more height than first written (`arch_1` 3.8 then 4.2 m, `arch_2` 5.4 then 6.0 m), and rubble a sixth of the arch's height needs room beside piers that must stay broad enough to stand blocks on (`arch_1` 5.4 then 6.0 m wide, `arch_2` 8.0 then 9.4 m, `arch_3` 4.8 then 5.8 m).
- Under a knot the lower block of each pier stands at least as high as the opening asked: the span rests on a pier only where rock runs straight up from the ground into it (`arch_rests`), and a block leaning 24 to 32 degrees from lower down has no such rock under it.
- The piers tip 3 to 6 degrees, not 8 to 14: tipped further, the top of a tall block is no longer over its own foot, and nothing rests on it by that measure. What leans is each block's sides.

Known and not mended in this round:

- A slab's and a keystone's outline is drawn from six sides evenly turned, which on a long block gives a pointed lozenge seen from above, and a long thin beam seen from the front on `arch_2`.
- The taller pier of a lintel arch is two slender blocks, 0.6 to 0.7 of the broad pier's width: a post beside a pile.
- About one draw in six meets the spec at `arch_1`'s size and one in twenty-four at the other two; a seed that finds none in forty fails its build.

- **Covers (2026-10-05).** Asked for by the owner through the catalogue (bare, mossy, snow-capped for rocks) and ADR 13: a cover is a palette variant of its base, as a season is of a tree. Proposed by the agent, and open to change: the `cover` field and what a cover variant's spec may change; that the reach is three tenths of the height and at most 0.9 m, and a patch a thirteenth of the narrower side and at most 0.2 m (neither share is measured on a reference: they are the first mossy rock's 0.9 m and 0.2 m turned into shares, the reach lowered from that rock's 0.45 of its height so the wash stays under half way up); the colour, darkness and the two shares of cover, which are that rock's. Which variant of the family got the cover was the coordinator's choice. Not approved.
