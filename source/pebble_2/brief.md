# pebble_2

Variant 2 of the pebble. Everything about it is in the family's brief, `source/pebble/brief.md`, except what is here.

## Real-world size

0.25 m wide, 0.2 m deep and 0.05 m tall: a flat cobble, as long as a hand and as thick as three fingers. Its height is one thirty-sixth of a 1.8 m player: it reaches the top of a boot's sole. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 0.25 m wide: edge light fading out 0.008 m into each plane (one thirtieth), and blotches about 0.025 m across (one tenth). No crevice shadow: the stone has no inside corner (the family's brief, Painted shading 4).

## Seed

Seed 2, kept from the first pebbles: it was not picked from several, and the owner picks from `benchmarks/out/pebble_2_candidates.png`, which shows seeds 1 to 12. Of those twelve at this size all build and pass gate L1 (`tools/bl tools/try_seeds.py pebble_2 1 12`), with 104 to 140 triangles, each within 71 draws of the 120 a seed may make. This seed keeps its draw number 14 and has 104 triangles; what it measures is in `review/final/observations.md`.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.125, -0.1, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.125, 0.1, 0.05]` | Real-world size |
| `painted_shading.edge_width_m` | `0.008` | Paint: one thirtieth of the width |
| `painted_shading.blotch_size_m` | `0.025` | Paint: one tenth of the width |
