# pebble_1

Variant 1 of the pebble. Everything about it is in the family's brief, `source/pebble/brief.md`, except what is here.

## Real-world size

0.12 m wide, 0.09 m deep and 0.05 m tall: a pebble that fits in the hand, the size of a hen's egg laid on its side and half sunk. Its height is one thirty-sixth of a 1.8 m player: it does not reach the top of a boot's sole. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 0.12 m wide: edge light fading out 0.004 m into each plane (one thirtieth), blotches about 0.012 m across (one tenth), and a crevice shadow that would fade out over 0.012 m (one tenth) if the stone had an inside corner, which it has not.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py pebble_1 1 40`), with 78 to 116 triangles; only this one was painted and taken through the later gates. Seed 1 was not picked from several. Its draw number 51 is the one kept. It measures: 104 triangles; 0.464 of its bounding box (at least 0.4); a crown of 0.349 (at least 0.2); 0.084 of the side surface upright (at most 0.15); summit 0.154 off the middle (at least 0.15).

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.06, -0.045, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.06, 0.045, 0.05]` | Real-world size |
| `painted_shading.edge_width_m` | `0.004` | Paint: one thirtieth of the width |
| `painted_shading.crevice_width_m` | `0.012` | Paint: one tenth of the width |
| `painted_shading.blotch_size_m` | `0.012` | Paint: one tenth of the width |
