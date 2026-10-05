# block

A near-cuboid of stone with chamfered corners and one or two crack lines, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its blocks share. The deliverable is a run of three sizes, each an asset of its own with its own seed and size: `source/block_1` (whole), `source/block_2` (one crack) and `source/block_3` (two cracks). Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

## Purpose

Quarried or fallen stone: building material lying where it was cut or where it fell, at the foot of a wall, in a ruin, beside a quarry face. A player walks round it, steps up onto the smaller ones and stands against the largest. It sits on flat ground; its underside is never seen. Nothing lifts, stacks or breaks it yet.

## Viewing

First person (ADR 7). Every block is lower than a standing player's eye (1.7 m), so its top is always seen, from above and at a slant; its sides are seen from as close as 0.5 m, where one face fills the view and a crack runs across it. From 3 to 10 m what reads is the box: a light top over darker upright sides, with a dark line across it where it is cracked.

## Real-world size

A run of sizes, each twice the last, all of one proportion: 1 wide, 0.7 deep, 0.6 tall. Each is given beside the 1.8 m player.

| Variant | Width (x) | Depth (y) | Height | Cracks | Beside a 1.8 m player |
| --- | --- | --- | --- | --- | --- |
| `block_1` | 0.5 m | 0.35 m | 0.3 m | none | one sixth of the player's height: to the middle of the shin, a stone two people carry |
| `block_2` | 1.0 m | 0.7 m | 0.6 m | one | one third: to just above the knee, a seat |
| `block_3` | 2.0 m | 1.4 m | 1.2 m | two | two thirds: to the chest; less than a 3 m foundation of the building grid in either direction |

The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Silhouette

What must read, taken from `docs/style/rock-shapes.md` (Block: "a near-cuboid with chamfered corners and one or two crack lines, in a run of sizes", and "How they are built"):

1. **A near-cuboid.** Seen with parallel rays from straight above and from each of its four sides, more than half of the block's outline is surface square to the view: within 8 degrees of facing it (`[lean] upright_deg`, the angle within which the conventions call a side upright). "Mostly right angles between its big faces" is taken as: more than half, from every side. A pebble or a boulder shows almost none from its sides; a plain box shows all of it.
2. **A flat top.** Seen from straight above, at least half of what shows is within 12 degrees of level, the slab's rule and number: a block is stood on and built with.
3. **Big chamfers.** At least 3 corners or rims are cut by a plane wide enough to be lit as a face of its own: at least 0.08 of the block's width across at its narrowest (the boulder asks 0.2 m of its 3.0 m, 0.067), and at least 30 degrees from every face of the box (`[planes] ledge_min_deg`, the least two planes differ by to make a corner). Chamfers that face the same way count once, so a chamfer a crack runs through is one chamfer.
4. **A crack that reads as a crack** (`block_2`, `block_3`). Seen from straight above, a crack is a groove across the top: a line of points with the surface standing at least 0.025 of the block's width higher on both sides of it, half of 0.1 of the block's width away. It runs across at least 0.7 of the block, from one long side toward the other. On the sides it goes on down as a line where one piece stands a little proud of the other. `block_2` has one and `block_3` two; none of them crosses another, and none is in the middle, so the pieces differ in size.
5. **Set down, not grown.** No foot, no lean, a centred top. Judged on the contact sheet (`front`, `right`).

The habits of the shapes document that a block does not follow, and the checks left out of its specs for that reason (Decisions): "nothing is upright" and "the tallest part is off-centre" (`lean`), "a foot" (`foot`), and "several pieces in a size order" for the whole block (`block_1` is one stone).

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement.

The block is cut from a box by planes (`tools/stone.py`, `solid`): the ground, a top tipped up to 2 degrees, four sides that lean in by up to 3 degrees, and three or four chamfers, each across one rim of the top or one upright corner, 0.1 to 0.15 of the block's width in from the corner it cuts.

A cracked block is two or three pieces parted along its cracks, left as overlapping pieces (ADR 13). A crack is a plane across the block's length, turned up to 15 degrees from square and leaning up to 6 degrees. Each of the two pieces beside it ends in a wall of its own, and the two walls lean apart by 9 to 13 degrees each, crossing 0.06 to 0.08 of the block's width below the top of the lower piece: above the crossing they leave a V-shaped groove, below it the pieces pass into each other. Each piece is cut from the box set in by a different amount on every side (0, 0.012 or 0.024 of the block's width), so that along a crack one piece stands proud of the next: no two pieces show faces in one plane, and the crack goes on down the sides as a small step.

Every piece is softened on its own with a one-segment bevel and lit with the normals of its planes (`tools/stone.py`, `finish`). A soft edge is 0.008 to 0.02 of the block's width wide; the generator draws every block one metre wide, softens it there, and shrinks or grows it to its size, as the pebble's does, so the three sizes are one construction. The edge where the block meets the ground is left hard.

A seed draws up to 60 whole blocks until one meets every number in this brief, as the gate's own checks measure it, and if none does the build fails and lists why each was refused.

One material:

- `m_block`: mid grey, `#a1a7a1`, the boulder's colour.

## Painted shading

Painted by script (ADR 9, ADR 10; `tools/paint.py`) into one texture. Colours and strengths are the boulder's; each band is a share of the block's width, as the pebble's are, and each variant's brief gives the metres.

1. **Gradient.** A light grey `#c8c8c8` at the top of the bounds and a cool grey `#8c8c9a` at the ground.
2. **Side shade.** Upright faces are darker at mid height, by up to 22%: a block is mostly upright faces.
3. **Blotches.** Lighter and darker by up to 12%, in soft-edged patches about 0.15 of the block's width across.
4. **Crevice shadow.** Where one piece passes into another, which is in a crack and nowhere else, the colour loses 45% of its light, fading to nothing 0.06 of the block's width out. This is what draws the crack as a dark line. `block_1` has no crack and nothing for it to paint.
5. **Edge light.** Exposed edges gain up to 30%, fading to nothing one thirty-second of the block's width into each plane (the boulder: 0.08 m of 3.0 m, one thirty-seventh).

No growth: moss is a cover, and covers are palettes on the same mesh (ADR 13).

**Texture size.** The narrowest band is the edge light, one thirty-second of the width, and it needs about 3 texels: 96 texels per block width. The surface above the ground is about 2.7 widths squared (the top, 0.7, and four sides, 2.04), so about 25,000 texels must be used; at the 0.4 of a texture a layout must use that is 250 px a side, which leaves nothing over, and `block_3` at 2 m wide must also give every face the 100 texels per metre of the conventions, which is 200 per width. So each block gets about 200 texels per width: 256 px for `block_1`, 512 px for `block_2`, 1024 px for `block_3`.

The underside is never seen, so it gets almost none of the texture.

## Parts

One object and one mesh per variant, with one material. `block_1` is one closed skin. `block_2` and `block_3` are two and three closed pieces that pass into each other. Nothing moves.

## Budget

1 material slot. Triangles: a softened solid of e edges above the ground is about 4e triangles, and a solid cut by n planes has at most 3n - 6 edges. A whole block is at most 10 planes (the box and four chamfers): 24 edges, 20 of them above the ground, 80 triangles, and corners where chamfers meet add to that: 150, the pebble's budget. Each further piece repeats the box and the chamfers its part has, and adds a wall: 100 more for each crack. So 150, 250 and 350. Until the stress scene of ADR 7 exists these are estimates.

Buried surface: both walls of a crack are inside the other piece. A block's surface is about 3.4 widths squared with its underside, and a crack adds two walls of about 0.4 each: one crack buries about 0.75 of 4.3, a sixth, and two cracks 1.5 of 5.1 and the wedges below the crossings, about a third. At most 0.4 is allowed, the crag's limit.

## References

- Shape: `docs/style/rock-shapes.md`, Block, and the previews it was read from (`docs/style/refs/rock-shapes/`, git-ignored). The shapes are taken; the faceted, flat-coloured surface is not.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, the boulder's benchmark, seen beside the three variants under Bevy (`benchmarks/out/block_variants.png`). The pack has no block; nothing from it is used.

## Out of scope

Collision shapes, LODs, a climbable flag, dressed (sawn, tooled) faces, blocks stacked into walls or stacks (their own families), rubble at the foot, cracks that branch or cross, a block broken into separated halves, mossy and snow-capped covers, other stone colours, a finished underside.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m`, budget, texture size, the widths of its painted bands, its least chamfer and, where it is cracked, its pieces and cracks. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"block"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `materials.m_block` | `"#a1a7a1"` | Style and colour: the boulder's grey |
| `painted_shading.base_tint` | `"#8c8c9a"` | Painted shading 1: a cool grey at the ground |
| `painted_shading.top_tint` | `"#c8c8c8"` | Painted shading 1: a light grey at the top |
| `painted_shading.edge_light` | `0.3` | Painted shading 5: exposed edges gain up to 30% |
| `painted_shading.blotch` | `0.12` | Painted shading 3: lighter and darker by up to 12% |
| `painted_shading.side_shade` | `0.22` | Painted shading 2: upright faces darker at mid height by up to 22% |
| `painted_shading.hidden_underside` | `true` | Painted shading: the underside is never seen |
| `block.min_square_share` | `0.5` | Silhouette 1: more than half of the outline square to the view, from above and from each side |
| `block.min_chamfers` | `3` | Silhouette 3: at least 3 chamfers |
| `top.min_level_share` | `0.5` | Silhouette 2: at least half of what is seen from above is level |
| `soft_edges` | `true` | Style and colour: every edge is soft except where the block meets the ground |
| `watertight` | `true` | Parts: closed pieces |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture, so the mesh carries UVs |

## Decisions

There was no grilling session. The owner gave the decisions below in writing on 2026-10-05, and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the family and its three variants as a run of sizes, differing by seed and size, at least one of them cracked; the shape, from `docs/style/rock-shapes.md`; that expected values come from this brief and painted shading is asked for in the spec; that a check that does not fit is not loosened or switched off through a spec value.

Proposed by the agent:

- **A whole block is one closed skin; a cracked block is overlapping pieces parted along its cracks.** Three ways to make a crack were weighed. Painted only: `tools/paint.py` has no way to draw a line that is not at an edge or a join, the crack would have no depth at 0.5 m and would not show in the outline. A groove cut into one skin: the skin is then not convex, and the kit softens convex solids only (`tools/stone.py`); cutting it with a boolean is what ADR 13 ended. Pieces parted along the crack: each piece is convex, softened on its own, the groove is real depth between two soft rims, and painted crevice shadow darkens exactly the join. That is the pieces rule doing what it was made for, at the cost of the buried walls (Budget). A whole block has no second piece, and the pieces rule asks for at least two, so `block_1` has no `overlap` block and is checked as the pebble is: one mesh closed, wound one way and facing outward.
- **Checks left out, and why.** `lean` (both of its measures): a block's sides are upright by definition and its flat top is its summit, centred; asking it with limits that allow that would switch it off through a spec value, as the crag's and the standing stone's specs do for the upright share. `foot`: a block is set down on the ground, and the small stones at a broken block's foot are Rubble, another family. `planes` and with it `chamfers`: `planes` asks for a ledge in sight from seven views and that no plane fills more than a share of any view, and a box's face fills its view; `chamfers` is measured against `planes.large_m2` and the lint does not allow it alone. `fullness`: cannot be asked of overlapping pieces, and Silhouette 1 says what it would of the whole one. The size order of `overlap` is asked of the cracked blocks.
- **New checks**, because a block's three defining properties had none: `block_square` and `block_chamfers` (spec block `block`) and `cracks` (spec block `cracks`). Their thresholds are this brief's: half the outline; 0.08 of the width; a groove 0.025 of the width deep, within 0.1 of it, over 0.7 of the way across. None was measured on a reference; the angles are ones the conventions already hold. The rock reference's previews show cracks as thin dark lines across blocks and say nothing about depth.
- The three sizes, the one proportion, and the seeds 1, 2 and 3. Which variants are cracked: the smallest whole, because a crack 1.2 cm deep on a stone 0.5 m wide is below what the texture can paint.
- The construction and every range in `generator.py`; that each piece is set in by its own amount, so no two pieces show faces in one plane, which would flicker where they overlap.
- The paint: the boulder's colour, tints and strengths, with side shade as the crag has it; band widths as shares of the width.
- The budgets, by the sums under Budget, and the buried share of 0.4.
