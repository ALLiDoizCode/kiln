# pebble_1

Variant 1 of the pebble. Everything about it is in the family's brief, `source/pebble/brief.md`, except what is here.

## Real-world size

0.12 m wide, 0.09 m deep and 0.025 m tall: a flat pebble that fits in the palm, as thick as a finger. Its height is one seventy-second of a 1.8 m player: thinner than the sole of a boot. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 0.12 m wide: edge light fading out 0.004 m into each plane (one thirtieth), blotches about 0.012 m across (one tenth), and a crevice shadow that would fade out over 0.012 m (one tenth) if the stone had an inside corner, which it has not.

## Seed

Seed 12, the agent's choice and the owner's to change: `benchmarks/out/pebble_1_candidates.png` shows seeds 1 to 12. Seed 1, kept from the first pebbles, was given up: at this size its paint failed the load test (`painted.gradient`: the low quarter of its open faces came out 1.152 times as light as the high quarter, where the tints give 0.946), and it is the most lopsided of the twelve on the sheet. Of the twelve at this size all build and pass gate L1 (`tools/bl tools/try_seeds.py pebble_1 1 12`), with 104 to 140 triangles, each within 71 draws of the 120 a seed may make; only seeds 1 and 12 were taken through the later gates. Seed 12 keeps its first draw and has 122 triangles; what it measures is in `review/final/observations.md`.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_1"]` | Parts: one object |
| `seed` | `12` | Seed |
| `bounds_m.min` | `[-0.06, -0.045, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.06, 0.045, 0.025]` | Real-world size |
| `painted_shading.edge_width_m` | `0.004` | Paint: one thirtieth of the width |
| `painted_shading.crevice_width_m` | `0.012` | Paint: one tenth of the width |
| `painted_shading.blotch_size_m` | `0.012` | Paint: one tenth of the width |
