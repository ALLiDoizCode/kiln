# arch

Two piers of stacked blocks bridged by a lintel block or by a knot of wedged blocks, with rubble at the feet, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its arches share. The deliverable is three variants, each an asset of its own with its own seed, size and kind of span: `source/arch_1`, `source/arch_2`, `source/arch_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

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
| `arch_1` | 4.2 m | 1.7 m | 3.3 m | 1.6 m wide, 2.2 m tall | lintel | 7 | a gateway: a player walks through with 0.4 m over the head and 0.55 m beside each shoulder |
| `arch_2` | 6.6 m | 2.2 m | 4.4 m | 3.0 m wide, 3.0 m tall | lintel | 8 | a natural bridge: a wall of the building grid (3 m by 3 m) fits in the opening, and the lintel is a walkway |
| `arch_3` | 3.8 m | 1.3 m | 3.4 m | 1.2 m wide, 2.0 m tall | wedged | 7 | a narrow door under a pointed knot of leaning blocks; one player at a time, 0.2 m over the head |

The arch faces the front (-Y): the opening runs through it from front to back, and the piers stand to the left and right. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Arch, and "How they are built"):

1. **Piers, a span, rubble.** A lintel arch is two piers of two stacked blocks each, one lintel block lying across both, and rubble blocks against the piers' outer feet. A wedged-block arch is two piers, each a tall block with a leaning block stacked on it, and a keystone wedged between the two leaning blocks: the knot is those three. Each is a closed piece of its own; each passes into another, so nothing floats; and no more than 30% of all their surface is buried inside another piece.
2. **One hole right through.** Seen from the front with parallel rays, the arch and the ground enclose exactly one area of open air. A span broken in the middle, a pier that does not reach the ground, or a slit of daylight between a pier and the span each fail this.
3. **An opening a player walks through.** Inside that hole there is a stretch at least as wide as the table above says (1.6, 3.0 and 1.2 m) that is open from the ground up to at least the height it says (2.2, 3.0 and 2.0 m). Rubble lying in the passage, a span pressed down, or piers pushed together fail this. The generator makes it 8 to 18% wider and 4 to 10% taller than asked.
4. **The span rests on both piers.** On each side of the opening there is rock without a break straight up from the ground into the span, over at least 0.2, 0.4 and 0.1 m2 of ground. A span that hangs beside a pier, or behind it, fails this.
5. **A top to stand on**, on the lintel arches: seen from straight above, at least half of what shows is within 12 degrees of level, the slab's number. The lintel's top tips 2 to 5 degrees. The lintel of `arch_1` is at least 1.1 m deep and that of `arch_2` 1.5 m: judged on the contact sheet. The knot of `arch_3` is leaning blocks and is climbed over, not stood on: nothing is asked of its top.
6. **A clear size order.** A piece's size is the surface it shows. Each piece shows at least 1.15 times what the next shows, the crag's number for a shape of many pieces: the span or the larger pier first, the rubble last. The two piers are not twins: one is about three quarters as wide as the other, and their blocks meet at different heights.
7. **A foot.** Rubble blocks stand against the outer feet of the piers, never in the passage: seen from above, at least two sides of the arch have 0.08 m2 of low, near-level surface that nothing stands over, the crag's number.
8. **Nothing upright.** Every block is narrower at its cap than at its floor by 0.05 to 0.12 of its lesser width a side (1 to 6 degrees: the tall pier blocks least), all the pieces of an arch lean 1 to 2 degrees more one common way, and a leaning block of the knot leans 22 to 30 degrees over the opening (further, and the corner of its soft edges under the cap is lit from behind). Judged on the contact sheet: no check asks it (see Decisions).
9. **Flat caps ringed by chamfers**, and one or two corners of the larger blocks cut by a plane wide enough to be a face. Judged on the contact sheet.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. ADR 13: the pieces overlap and are not fused.

Each piece is a prism of exact planes (`tools/stone.py`, `prism`): four leaning sides and up to two cut corners, a level floor, and a tipped cap ringed by chamfers. A piece that stands on the ground meets it at a hard edge; every edge of a piece held off the ground is softened. Each piece is softened before it meets the others. A soft edge is as wide as the piece's shortest edge has room for, at most 0.04 m and at most 0.012 of the arch's height.

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

The texture is 2048 px: the pieces of `arch_1` have about 50 m2 of surface and those of `arch_2` about 100 m2, and at 1024 px with the packer's 0.4 coverage that is under the 100 texels a metre the conventions ask. `arch_3`, about 30 m2, was first given 1024 px, and the load test read 93 texels a metre on its sparsest triangle (`uv.texel_density`), so it takes 2048 px too.

`hidden_underside` is true: it names the faces lying on the ground, which get almost none of the texture. It does not touch the underside of the span.

No growth: moss is a cover, and covers are palette variants on the same mesh (ADR 13).

## Parts

One object and one mesh per variant, with one material. The mesh is seven or eight closed pieces that overlap (`overlap` in the spec). Nothing moves.

## Budget

1 material slot per variant. A prism of n sides standing on the ground is 17n - 4 triangles once softened, and one held off the ground 20n - 4. A lintel arch is at most two pier blocks of five sides on the ground (81 each), two of four above them (76 each), a lintel of six (116) and two rubble blocks of up to five (81 each): 592, and 673 with a third rubble block. A wedged-block arch is two pier blocks (81 each), two leaning blocks (76 each), a keystone of five (96) and two rubble blocks: 572. The budgets are 600, 680 and 600. Until the stress scene of ADR 7 exists these are estimates.

## References

- Shape: `docs/style/rock-shapes.md`, Arch, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen beside the three variants under Bevy (`benchmarks/out/arch_variants.png`). A boulder, not an arch: a comparison of paint and cost only. Nothing from it is used.

## Out of scope

Collision shapes and the climbable flag (ADR 7: not implemented), LODs, mossy and snow-capped covers, other stone colours, an arch that grows out of a cliff or joins two ledges (placement is the game's), a round arch of many voussoirs, the rib family's pointed arch, finished faces under the piers.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, how many pieces it has, its span, opening and bearing, and whatever else differs: the lintel arches' own give `top.min_level_share`, which the wedged-block arch does not have.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"arch"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `600` | Budget |
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
| `overlap.min_step_ratio` | `1.15` | Silhouette 6 |
| `foot.min_sides` | `2` | Silhouette 7 |
| `foot.min_side_m2` | `0.08` | Silhouette 7 |
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
- **No `lean` block.** `lean` asks little upright side surface, which the crag and the standing stone already switch off with a limit of 1.0, and a summit off the middle of the bounds; an arch's summit is its span, which lies across the middle. Nothing upright (Silhouette 8) is held by the generator's ranges and the contact sheet only.
- **No `top` block on the wedged-block arch**: its top is leaning blocks.
- The budgets, from the triangle counts of softened prisms; every painted value, the crag's.

Changed after the first builds, each because the first number could not be built or failed a later gate, none to pass a shape check:

- `arch_3` was 3.2 m wide. Its piers were then 0.6 to 0.85 m wide and 2.4 m tall, and by the height of the knot they had tapered to less than a leaning block needs to stand on; it is 3.8 m wide.
- `arch_3`'s texture was 1024 px and the load test read 93 texels a metre (`uv.texel_density`, 100 wanted); it is 2048 px.
- The leaning blocks of a knot were to hang 34 to 44 degrees over the opening. At that angle the corner of the soft edges under the cap is lit from behind (the load test: "3 triangles have vertex normals facing against their winding"); they hang 22 to 30 degrees, and the generator refuses any arch with such a triangle. The keystone is correspondingly wider.
- A block stands on the shoulder of the one under it, not inside its cap: inside the cap, the upper block of the narrower pier was 0.2 to 0.4 m wide.
