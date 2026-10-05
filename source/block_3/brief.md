# block_3

Variant 3 of the block. Everything about it is in the family's brief, `source/block/brief.md`, except what is here.

## Real-world size

2.0 m wide, 1.4 m deep and 1.2 m tall: fallen from a wall, or not yet split for building. Its height is two thirds of a 1.8 m player: to the chest. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Two cracks: three pieces. A piece's size is the surface it shows, and each shows at least 1.3 times what the next shows, the slab's step: no crack is in the middle. A crack is a groove at least 0.05 m deep within 0.2 m (the surface 0.1 m to either side of it stands that much higher), across at least 0.7 of the block.

## Paint

The family's brief gives each painted band as a share of the block's width (Painted shading). At 2.0 m wide: edge light fading out 0.0625 m into each plane, blotches about 0.3 m across, and crevice shadow fading out over 0.12 m. A 1024 px texture. Chamfers are at least 0.16 m across.

## Seed

Seed 3. Of seeds 1 to 40 at this size 30 build and pass gate L1 (`tools/bl tools/try_seeds.py block_3 1 40`), with 140 to 176 triangles; the other 10 draw 60 blocks and none meets the spec. Only this one was painted and taken through the later gates. Seed 3 was not picked from several. Its tenth draw is the one kept. It measures: 164 triangles; square to the view from 0.549 (top) to 0.701 (right), at least 0.5; three chamfers 0.278 to 0.295 m across; 0.789 of the lines across it meet both cracks (at least 0.7); 0.307 of the surface buried; size steps of 1.78 and 1.38; 0.549 of the view from above level.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["block_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.0, -0.7, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.0, 0.7, 1.2]` | Real-world size |
| `max_triangles` | `350` | Budget (family): 150 and 100 more for each crack |
| `painted_shading.texture_px` | `1024` | Paint: about 200 texels per block width |
| `painted_shading.edge_width_m` | `0.0625` | Paint: one thirty-second of the width |
| `painted_shading.crevice_width_m` | `0.12` | Paint: 0.06 of the width |
| `painted_shading.blotch_size_m` | `0.3` | Paint: 0.15 of the width |
| `block.min_chamfer_m` | `0.16` | Silhouette 3 (family): 0.08 of the width |
| `overlap.min_count` | `3` | Pieces |
| `overlap.max_count` | `3` | Pieces |
| `overlap.max_buried_share` | `0.4` | Budget (family): the crag's limit |
| `overlap.min_step_ratio` | `1.3` | Pieces: the slab's step |
| `cracks.count` | `2` | Pieces |
| `cracks.depth_m` | `0.05` | Silhouette 4 (family): 0.025 of the width |
| `cracks.width_m` | `0.2` | Silhouette 4 (family): 0.1 of the width |
| `cracks.min_span` | `0.7` | Silhouette 4 (family): across at least 0.7 of the block |
