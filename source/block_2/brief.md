# block_2

Variant 2 of the block. Everything about it is in the family's brief, `source/block/brief.md`, except what is here.

## Real-world size

1.0 m wide, 0.7 m deep and 0.6 m tall: a seat. Its height is one third of a 1.8 m player: to just above the knee. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

One crack: two pieces. A piece's size is the surface it shows, and each shows at least 1.3 times what the next shows, the slab's step: no crack is in the middle. A crack is a groove at least 0.025 m deep within 0.1 m (the surface 0.05 m to either side of it stands that much higher), across at least 0.7 of the block.

## Paint

The family's brief gives each painted band as a share of the block's width (Painted shading). At 1.0 m wide: edge light fading out 0.0312 m into each plane, blotches about 0.15 m across, and crevice shadow fading out over 0.06 m. A 512 px texture. Chamfers are at least 0.08 m across.

## Seed

Seed 2. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py block_2 1 40`), with 104 to 128 triangles; only this one was painted and taken through the later gates. Seed 2 was not picked from several. Its fourth draw is the one kept. It measures: 118 triangles; square to the view from 0.507 (right) to 0.911 (left), at least 0.5; three chamfers 0.101 to 0.119 m across; 0.811 of the lines across it meet its crack (at least 0.7); 0.193 of the surface buried; a size step of 1.71; 0.573 of the view from above level.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["block_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.5, -0.35, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.5, 0.35, 0.6]` | Real-world size |
| `max_triangles` | `250` | Budget (family): 150 and 100 more for each crack |
| `painted_shading.texture_px` | `512` | Paint: about 200 texels per block width |
| `painted_shading.edge_width_m` | `0.0312` | Paint: one thirty-second of the width |
| `painted_shading.crevice_width_m` | `0.06` | Paint: 0.06 of the width |
| `painted_shading.blotch_size_m` | `0.15` | Paint: 0.15 of the width |
| `block.min_chamfer_m` | `0.08` | Silhouette 3 (family): 0.08 of the width |
| `overlap.min_count` | `2` | Pieces |
| `overlap.max_count` | `2` | Pieces |
| `overlap.max_buried_share` | `0.4` | Budget (family): the crag's limit |
| `overlap.min_step_ratio` | `1.3` | Pieces: the slab's step |
| `cracks.count` | `1` | Pieces |
| `cracks.depth_m` | `0.025` | Silhouette 4 (family): 0.025 of the width |
| `cracks.width_m` | `0.1` | Silhouette 4 (family): 0.1 of the width |
| `cracks.min_span` | `0.7` | Silhouette 4 (family): across at least 0.7 of the block |
