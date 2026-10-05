# spire_2

Variant 2 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

4.2 m wide, 3.7 m deep and 8.0 m tall: the great pillar, 4.4 players tall, its base wider than a 3 m foundation. The cap of the base is about 2.9 m up, the height of a wall of the building grid. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Eight or nine, by seed: four tiers, two shoulders, two blocks, and on some seeds a block on the base's ledge.

## Budget

At most 960 triangles: 132 for the base's main mass, 3 x 126 for the tiers above it, 98 and 81 for the shoulders, 2 x 81 for the blocks and 105 for a ledge block: 956.

## Foot

The footprint is 15.5 m2; a hundredth of it, 0.16 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 2. Of seeds 1 to 40 at this size 38 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_2 1 40`), with 642 to 850 triangles; seeds 30 and 38 fail the build (none of their 40 spires meets the spec). Only seed 2 was painted and taken through the later gates; it was not picked from several. It took the twenty-eighth spire it drew and measures: 716 triangles; 4 tiers, 2.88, 1.42, 0.83 and 0.54 m wide, steps 0.49, 0.59 and 0.65, differing by 1.31; tiers 0.375, 0.251 and 0.267 of their width off the middle of the one below; leaning 10.4 degrees; standing 0.984, 0.983 and 0.955; ledges 0.414, 0.234, 0.107 and 0.480 (the third is just over the 0.1 asked); 12 flutes; 0.333 buried; smallest size step 1.16 (1.15 asked); 127 texels per metre at 2048 px.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-2.1, -1.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.1, 1.85, 8.0]` | Real-world size |
| `max_triangles` | `960` | Budget |
| `overlap.min_count` | `8` | Pieces |
| `overlap.max_count` | `9` | Pieces |
| `spire.tiers` | `[4, 4]` | Pieces |
| `foot.min_side_m2` | `0.16` | Foot |
