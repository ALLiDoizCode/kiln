# block_1

Variant 1 of the block. Everything about it is in the family's brief, `source/block/brief.md`, except what is here.

## Real-world size

0.5 m wide, 0.35 m deep and 0.3 m tall: a stone two people carry. Its height is one sixth of a 1.8 m player: to the middle of the shin. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Whole: one closed skin, no crack.

## Paint

The family's brief gives each painted band as a share of the block's width (Painted shading). At 0.5 m wide: edge light fading out 0.0156 m into each plane, blotches about 0.075 m across. No crevice shadow: a whole block has no inside corner for one to lie in, so its spec leaves `crevice_shadow` and `crevice_width_m` out, as the load test asks (`painted.crevices_darker`). A 256 px texture. Chamfers are at least 0.04 m across.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py block_1 1 40`), with 68 to 80 triangles; only this one was painted and taken through the later gates. Seed 1 was not picked from several. Its first draw is the one kept. It measures: 80 triangles; square to the view from 0.531 (back) to 0.963 (front), at least 0.5; four chamfers 0.07 to 0.093 m across; 0.665 of the view from above level.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["block_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.25, -0.175, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.25, 0.175, 0.3]` | Real-world size |
| `max_triangles` | `150` | Budget (family): 150 and 100 more for each crack |
| `painted_shading.texture_px` | `256` | Paint: about 200 texels per block width |
| `painted_shading.edge_width_m` | `0.0156` | Paint: one thirty-second of the width |
| `painted_shading.blotch_size_m` | `0.075` | Paint: 0.15 of the width |
| `block.min_chamfer_m` | `0.04` | Silhouette 3 (family): 0.08 of the width |
