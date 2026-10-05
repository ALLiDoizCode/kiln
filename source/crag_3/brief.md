# crag_3

Variant 3 of the crag. Everything about it is in the family's brief, `source/crag/brief.md`, except what is here.

## Real-world size

2.0 m wide, 1.7 m deep and 1.7 m tall: an outcrop whose tallest prism reaches a player's eye. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Five: three prisms and two blocks.

## Budget

At most 450 triangles: 90 a piece.

## Foot

The footprint is 3.4 m2; a hundredth of it, 0.03 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py crag_3 1 40`), with 376 to 448 triangles; only this one was painted and taken through the later gates. Seed 3 was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["crag_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.0, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.0, 0.85, 1.7]` | Real-world size |
| `max_triangles` | `450` | Budget |
| `overlap.min_count` | `5` | Pieces |
| `overlap.max_count` | `5` | Pieces |
| `cluster.min_prisms` | `3` | Pieces |
| `foot.min_side_m2` | `0.03` | Foot |
