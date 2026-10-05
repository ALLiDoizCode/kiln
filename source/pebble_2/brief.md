# pebble_2

Variant 2 of the pebble. Everything about it is in the family's brief, `source/pebble/brief.md`, except what is here.

## Real-world size

0.25 m wide, 0.2 m deep and 0.09 m tall: a cobble, as long as a shoe is wide and long as a hand. Its height is one twentieth of a 1.8 m player: it reaches the ankle bone. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 0.25 m wide: edge light fading out 0.008 m into each plane (one thirtieth), blotches about 0.025 m across (one tenth), and a crevice shadow that would fade out over 0.025 m (one tenth) if the stone had an inside corner, which it has not.

## Seed

Seed 2. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py pebble_2 1 40`), with 78 to 116 triangles; only this one was painted and taken through the later gates. Seed 2 was not picked from several. Its draw number 14 is the one kept. It measures: 92 triangles; 0.522 of its bounding box (at least 0.4); a crown of 0.480 (at least 0.2); 0.045 of the side surface upright (at most 0.15); summit 0.218 off the middle (at least 0.15).

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.125, -0.1, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.125, 0.1, 0.09]` | Real-world size |
| `painted_shading.edge_width_m` | `0.008` | Paint: one thirtieth of the width |
| `painted_shading.crevice_width_m` | `0.025` | Paint: one tenth of the width |
| `painted_shading.blotch_size_m` | `0.025` | Paint: one tenth of the width |
