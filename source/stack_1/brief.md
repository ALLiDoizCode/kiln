# stack_1

Variant 1 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

0.9 m wide, 0.8 m deep and 0.7 m tall: the plain one, a cairn a little over a player's knee, 0.39 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Four.

## Budget

At most 480 triangles: 120 a stone.

## Paint

The family's bands are the smallest slab's, whose plates are 0.3 m thick. This stack's four stones share 0.7 m, about 0.2 m each, two thirds of that, and its bands are two thirds as wide: 0.027 m of edge light, 0.08 m of crevice shadow, blotches 0.13 m across. The reason is in the sizes and needs no build: a side of a 0.2 m stone, less its chamfer, is 0.12 to 0.14 m tall, and a 0.04 m band from its upper and lower edge with a 0.12 m shadow from the join under it leaves none of it open. The build said the same: with the family's bands the load test found 0 samples of open face (`painted.open_faces`).

The family's 512 px texture. It was 1024 px while the painter packed islands as boxes: at 512 px the triangles then used 0.387 of the texture where the conventions ask 0.4 (`uv.coverage`). Packed by their outlines (`pack` in `tools/paint.py`) they use 0.550 at 512 px, with 167 texels per metre on the sparsest triangle (100 asked), and the file is 190 kB where it was 520 kB.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py stack_1 1 40`, 186 s), with 392 to 470 triangles; 26 of them keep the first stack they draw and none needs more than four. Only seed 1 was painted and taken through the later gates. It was not picked from several: it is the first. It measures: 430 triangles; 0.308 of the surface buried (at most 0.45); size steps of the surface shown 2.32, 1.25 and 1.69 (at least 1.15); seen from above each stone covers 0.62, 0.65 and 0.52 of the one below (at most 0.85); thickness over width 0.23 to 0.26 (at most 0.5); sunk 0.16 to 0.18 of its thickness (at most 0.35); summit 0.374 off the middle (at least 0.15); no side within 8 degrees of upright.

Before the soft edges were limited to 0.02 of the stack's height (they were 0.035), 39 of 40 seeds built and seed 15 did not: 29 of its 40 stacks had a chamfer the soft edges would eat, and about five stacks of six were refused for that at this size.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["stack_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.45, -0.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.45, 0.4, 0.7]` | Real-world size |
| `max_triangles` | `480` | Budget |
| `overlap.min_count` | `4` | Stones |
| `overlap.max_count` | `4` | Stones |
| `painted_shading.edge_width_m` | `0.027` | Paint: two thirds of the family's 0.04 m |
| `painted_shading.crevice_width_m` | `0.08` | Paint: two thirds of the family's 0.12 m |
| `painted_shading.blotch_size_m` | `0.13` | Paint: two thirds of the family's 0.2 m |
