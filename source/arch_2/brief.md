# arch_2

Variant 2 of the arch: a lintel arch: one rough slab lying aslant across two unlike piers. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

9.4 m wide, 2.4 m deep and 6.0 m tall: a natural bridge. The opening is at least 3.0 m wide and 3.0 m tall, open from the ground up: a wall of the building grid fits in it, and a 1.8 m player has 1.2 m over the head. The slab is a sloping way across. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Eight: two piers of two stacked blocks each, the slab, and three rubble blocks.

## The opening

Seen from the front, open air right through, at least 3.0 m wide from the ground up to 3.0 m. On each side of it rock stands without a break from the ground into the span over at least 0.4 m2.

## Seed

Seed 2: not picked from several. It keeps the 39th arch of the 40 it may draw and measures: 596 triangles; one hole seen from the front; the opening 3.89 m wide up to 3.0 m, and 4.48 m tall at its tallest; rock under the slab over 0.58 and 0.56 m2; the hole 0.767 of its rectangle; the sides 0.208 of the height apart; 0.049 of the view from above level; 0.338 of the sides upright; the summit 0.496 off the middle; 0.209 of the surface buried; size steps 1.74, 1.34, 1.28, 1.56, 1.24, 1.41, 1.45; foot 0.49 m2 on the left and 1.0 on the right. Of seeds 1 to 8 at this size all 8 build and pass gate L1 (the run of 40 was stopped at 8 when the shared machine was overloaded), with 578 to 614 triangles. About one draw in twenty-four meets the spec at this size, so some seeds will use all forty and fail.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-4.7, -1.2, 0.0]` | Real-world size |
| `bounds_m.max` | `[4.7, 1.2, 6.0]` | Real-world size |
| `overlap.min_count` | `8` | Pieces |
| `overlap.max_count` | `8` | Pieces |
| `arch.span` | `"lintel"` | Pieces |
| `arch.min_opening_m` | `3.0` | The opening |
| `arch.min_clear_m` | `3.0` | The opening |
| `arch.min_bearing_m2` | `0.4` | The opening |
| `max_triangles` | `780` | Budget: eight pieces (the family brief's Budget) |
