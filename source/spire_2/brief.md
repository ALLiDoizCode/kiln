# spire_2

Variant 2 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

4.2 m wide, 3.7 m deep and 8.0 m tall: the great pillar, 4.4 players tall, its base wider than a 3 m foundation. The cap of the base is about 2.9 m up, the height of a wall of the building grid. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Nine: four tiers (the base and three above it), three buttresses and two blocks.

## Budget

At most 920 triangles: 132 for the base, 3 x 126 for the tiers, 5 x 81 for the buttresses and blocks: 915.

## Foot

The footprint is 15.5 m2; a hundredth of it, 0.16 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 2. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_2 1 40`), with 766 to 862 triangles. Only seed 2 was painted and taken through the later gates; it was not picked from several. It took the second spire it drew and measures: 860 triangles; tiers 2.64, 1.50, 0.76 and 0.43 m wide, steps 0.57, 0.51 and 0.57; ledges 0.105, 0.222, 0.118 and 0.257 of each tier's level cut (the base's is just over the 0.1 asked); 15 flutes; 0.382 of the side surface within 8 degrees of upright; summit 0.229 off the middle; 0.201 of the surface buried; smallest size step 1.23. The sparsest triangle has 142 texels per metre at 2048 px.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-2.1, -1.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.1, 1.85, 8.0]` | Real-world size |
| `max_triangles` | `920` | Budget |
| `overlap.min_count` | `9` | Pieces |
| `overlap.max_count` | `9` | Pieces |
| `spire.tiers` | `4` | Pieces |
| `foot.min_side_m2` | `0.16` | Foot |
