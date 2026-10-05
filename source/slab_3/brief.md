# slab_3

Variant 3 of the slab. Everything about it is in the family's brief, `source/slab/brief.md`, except what is here.

## Real-world size

1.4 m wide, 1.2 m deep and 0.3 m tall: a stepping stone, one stride across. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Two plates: the dominant one and the taller one pushed into its side.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1, with 190 to 226 triangles; only this one was painted and taken through the later gates. Seed 3 was not picked from several. It measures: 208 triangles; 0.157 buried; a size step of 2.73; 0.513 of the view from above level (at least 0.5, the closest to its limit); summit 0.495 off the middle.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["slab_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.7, -0.6, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.7, 0.6, 0.3]` | Real-world size |
| `overlap.min_count` | `2` | Pieces |
| `overlap.max_count` | `2` | Pieces |
| `painted_shading.edge_width_m` | `0.04` | Paint: half the family's 0.08 m |
| `painted_shading.crevice_width_m` | `0.12` | Paint: under half the family's 0.3 m |
| `painted_shading.blotch_size_m` | `0.2` | Paint: two thirds of the family's 0.3 m |

## Paint

The family's bands are sized for a slab 2.6 m across. This one is about half that, and its bands are narrower to match: with the family's 0.3 m crevice the shadow of the join reached over the whole of the lower plate's cap, and the load test found only 75 samples of open face to measure the stone's colour on.
