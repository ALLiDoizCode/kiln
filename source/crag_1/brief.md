# crag_1

Variant 1 of the crag. Everything about it is in the family's brief, `source/crag/brief.md`, except what is here.

## Real-world size

3.2 m wide, 2.6 m deep and 3.0 m tall: the plain one, as tall as a wall of the building grid; a player's eye is just over half way up it. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Six: four prisms and two blocks.

## Budget

At most 540 triangles: 90 a piece.

## Foot

The footprint is 8.3 m2; a hundredth of it, 0.08 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 1. Not all forty were tried: `tools/bl tools/try_seeds.py crag_1 1 40` was stopped for time after seeds 1 to 10, of which 9 build and pass gate L1 with 444 to 498 triangles; seed 9 fails the build (none of its 40 crags meets the spec). Only seed 1 was painted and taken through the later gates; it took the seventh crag it drew. Seed 1 was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["crag_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-1.6, -1.3, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.6, 1.3, 3.0]` | Real-world size |
| `max_triangles` | `540` | Budget |
| `overlap.min_count` | `6` | Pieces |
| `overlap.max_count` | `6` | Pieces |
| `cluster.min_prisms` | `4` | Pieces |
| `foot.min_side_m2` | `0.08` | Foot |
