# rubble_3

Variant 3 of the rubble. Everything about it is in the family's brief, `source/rubble/brief.md`, except what is here.

## Real-world size

0.44 m wide, 0.36 m deep and 0.11 m tall: four fragments, the largest about 0.2 m long and the smallest about 0.08 m. Beside a 1.8 m player the heap is a quarter of the player's height across, one boot long, and its tallest stone is one sixteenth of the player, at the ankle bone. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Group

Exactly four fragments. None lies further than 0.1 m from the rest, half the length of its largest fragment (the family's brief, Silhouette 3), and at least one pair of them touch. At 60 triangles a fragment the budget is 240 (the family's brief, Budget).

## Paint

The family's brief gives each painted band as a share of the largest fragment's length (Painted shading). At 0.2 m: edge light fading out 0.005 m into each plane (one fortieth), and blotches and crevice shadow 0.02 m across (one tenth).

## Seed

Seed 3: not picked from several. The owner picks from `benchmarks/out/rubble_1_candidates.png`, which shows seeds 1 to 12 of `rubble_1`.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["rubble_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.22, -0.18, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.22, 0.18, 0.11]` | Real-world size |
| `max_triangles` | `240` | Group: 60 a fragment |
| `scatter.min_count` | `4` | Group |
| `scatter.max_count` | `4` | Group |
| `scatter.max_gap_m` | `0.1` | Group: half the largest fragment's length |
| `scatter.min_touching` | `1` | Group |
| `painted_shading.edge_width_m` | `0.005` | Paint: one fortieth of the largest fragment |
| `painted_shading.crevice_width_m` | `0.02` | Paint: one tenth of the largest fragment |
| `painted_shading.blotch_size_m` | `0.02` | Paint: one tenth of the largest fragment |
