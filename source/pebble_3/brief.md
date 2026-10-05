# pebble_3

Variant 3 of the pebble. Everything about it is in the family's brief, `source/pebble/brief.md`, except what is here.

## Real-world size

0.5 m wide, 0.38 m deep and 0.16 m tall: a small stone, the largest of the run: two feet could stand on it, and it takes two hands to lift. Its height is about one eleventh of a 1.8 m player: it reaches the lower shin. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 0.5 m wide: edge light fading out 0.016 m into each plane (one thirtieth), blotches about 0.05 m across (one tenth), and a crevice shadow that would fade out over 0.05 m (one tenth) if the stone had an inside corner, which it has not.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py pebble_3 1 40`), with 78 to 116 triangles; only this one was painted and taken through the later gates. Seed 3 was not picked from several. Its draw number 12 is the one kept. It measures: 92 triangles; 0.438 of its bounding box (at least 0.4); a crown of 0.262 (at least 0.2); 0.022 of the side surface upright (at most 0.15); summit 0.187 off the middle (at least 0.15).

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.25, -0.19, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.25, 0.19, 0.16]` | Real-world size |
| `painted_shading.edge_width_m` | `0.016` | Paint: one thirtieth of the width |
| `painted_shading.crevice_width_m` | `0.05` | Paint: one tenth of the width |
| `painted_shading.blotch_size_m` | `0.05` | Paint: one tenth of the width |
