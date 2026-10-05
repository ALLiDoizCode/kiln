# rubble_1

Variant 1 of the rubble. Everything about it is in the family's brief, `source/rubble/brief.md`, except what is here.

## Real-world size

0.6 m wide, 0.5 m deep and 0.14 m tall: five fragments, the largest about 0.3 m long and the smallest about 0.1 m. Beside a 1.8 m player the group is a third of the player's height across, two boots end to end, and its tallest stone is one thirteenth of the player, just over the ankle bone. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Group

Exactly five fragments. None lies further than 0.12 m from the rest, half the length of its largest fragment (the family's brief, Silhouette 3), and at least one pair of them touch. At 60 triangles a fragment the budget is 300 (the family's brief, Budget).

## Paint

The family's brief gives each painted band as a share of the largest fragment's length (Painted shading), taken at 0.25 m when the bands were set: edge light fading out 0.006 m into each plane (one fortieth), and blotches 0.025 m across (one tenth). Crevice shadow up to 45% darker, reaching 0.025 m (the family's brief, Painted shading 4): three of this group's stones lie apart, and its one touching pair lies 7 mm apart, inside the touching distance, so the faces of the two that stand over each other there are an inside corner and the load test measures the shadow in them.

## Seed

Seed 8, picked by the agent from `benchmarks/out/rubble_1_candidates.png` (seeds 1 to 12, remade after the generator began refusing dressed shards): its largest fragment shows five planes and no one big cut face, two fragments lie against it and one lies clear, and nothing in it reads as a block standing square. The owner's pick from the same sheet replaces it.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["rubble_1"]` | Parts: one object |
| `seed` | `8` | Seed |
| `bounds_m.min` | `[-0.3, -0.25, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.3, 0.25, 0.14]` | Real-world size |
| `max_triangles` | `300` | Group: 60 a fragment |
| `scatter.min_count` | `5` | Group |
| `scatter.max_count` | `5` | Group |
| `scatter.max_gap_m` | `0.12` | Group: half the largest fragment's length |
| `scatter.min_touching` | `1` | Group |
| `painted_shading.edge_width_m` | `0.006` | Paint: one fortieth of the largest fragment |
| `painted_shading.crevice_shadow` | `0.45` | Paint: the boulder's strength, between the pair that touches |
| `painted_shading.crevice_width_m` | `0.025` | Paint: one tenth of the largest fragment |
| `painted_shading.blotch_size_m` | `0.025` | Paint: one tenth of the largest fragment |
