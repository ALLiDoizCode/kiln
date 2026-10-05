# arch_2

Variant 2 of the arch: a lintel arch. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

6.6 m wide, 2.2 m deep and 4.4 m tall: a natural bridge. The opening is at least 3.0 m wide and 3.0 m tall, open from the ground up: a wall of the building grid fits in it, and a 1.8 m player has 1.2 m over the head. The lintel's top is about 4.3 m up and is a walkway at least 1.5 m deep. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Eight: two piers of two stacked blocks each, the lintel, and three rubble blocks, the third in front of or behind the larger pier.

## The opening

Seen from the front, open air right through, at least 3.0 m wide from the ground up to 3.0 m. On each side of it rock stands without a break from the ground into the span over at least 0.4 m2.

## Seed

Seed 2: not picked from several. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py arch_2 1 40`), with 606 or 626 triangles. Only this one was painted and taken through the later gates. It keeps the first arch it draws and measures: 626 triangles; one hole seen from the front; the opening 3.40 m wide up to 3.0 m, and 3.30 m tall; rock under the span over 0.51 and 0.98 m2; 0.691 of the view from above level; 0.153 of the surface buried; size steps 2.22, 1.38, 1.62, 1.16, 3.34, 1.49, 1.25; foot 0.21 m2 on the left and 0.47 on the right.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-3.3, -1.1, 0.0]` | Real-world size |
| `bounds_m.max` | `[3.3, 1.1, 4.4]` | Real-world size |
| `overlap.min_count` | `8` | Pieces |
| `overlap.max_count` | `8` | Pieces |
| `arch.span` | `"lintel"` | Pieces |
| `arch.min_opening_m` | `3.0` | The opening |
| `arch.min_clear_m` | `3.0` | The opening |
| `arch.min_bearing_m2` | `0.4` | The opening |
| `max_triangles` | `680` | Budget: a third rubble block (the family brief's Budget) |
| `top.min_level_share` | `0.5` | A top to stand on (the family brief's Silhouette 5) |
