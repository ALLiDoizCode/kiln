# rubble_2

Variant 2 of the rubble. Everything about it is in the family's brief, `source/rubble/brief.md`, except what is here.

## Real-world size

1.0 m wide, 0.8 m deep and 0.2 m tall: seven fragments, the largest about 0.4 m long and the smallest about 0.11 m. Beside a 1.8 m player the spill is a long stride across, more than half the player's height, and its tallest stone is one ninth of the player, to the lower shin. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Group

Exactly seven fragments. None lies further than 0.18 m from the rest, half the length of its largest fragment (the family's brief, Silhouette 3), and at least two pairs of them touch. At 60 triangles a fragment the budget is 420 (the family's brief, Budget).

## Paint

The family's brief gives each painted band as a share of the largest fragment's length (Painted shading), taken at 0.36 m when the bands were set: edge light fading out 0.009 m into each plane (one fortieth), and blotches 0.036 m across (one tenth). Crevice shadow up to 45% darker, reaching 0.036 m (the family's brief, Painted shading 4): in this group fragments lie against each other closely enough to make inside corners, and the load test measures the shadow in them.

## Seed

Seed 2: not picked from several. The owner picks from `benchmarks/out/rubble_1_candidates.png`, which shows seeds 1 to 12 of `rubble_1`.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["rubble_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.5, -0.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.5, 0.4, 0.2]` | Real-world size |
| `max_triangles` | `420` | Group: 60 a fragment |
| `scatter.min_count` | `7` | Group |
| `scatter.max_count` | `7` | Group |
| `scatter.max_gap_m` | `0.18` | Group: half the largest fragment's length |
| `scatter.min_touching` | `2` | Group |
| `painted_shading.edge_width_m` | `0.009` | Paint: one fortieth of the largest fragment |
| `painted_shading.crevice_shadow` | `0.45` | Paint: the boulder's strength, in this group's inside corners |
| `painted_shading.crevice_width_m` | `0.036` | Paint: one tenth of the largest fragment |
| `painted_shading.blotch_size_m` | `0.036` | Paint: one tenth of the largest fragment |
