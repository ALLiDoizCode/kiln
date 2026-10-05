# arch_1

Variant 1 of the arch: a lintel arch: one rough slab lying aslant across two unlike piers. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

6 m wide, 2.0 m deep and 4.2 m tall: a gateway under a fallen slab. The opening is at least 1.6 m wide and 2.2 m tall, open from the ground up: a 1.8 m player walks through with 0.4 m over the head and, shoulders 0.5 m wide, 0.55 m to spare on each side. The slab slopes from the low pier up to the high one. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven: two piers of two stacked blocks each, the slab, and two rubble blocks against the piers' outer feet.

## The opening

Seen from the front, open air right through, at least 1.6 m wide from the ground up to 2.2 m. On each side of it rock stands without a break from the ground into the span over at least 0.2 m2.

## Seed

Seed 1: not picked from several; twelve seeds are in `benchmarks/out/arch_1_candidates.png` for the owner to pick from. It keeps the third arch it draws and measures: 568 triangles; one hole seen from the front; the opening 2.16 m wide up to 2.2 m, and 3.23 m tall at its tallest; rock under the slab over 0.22 and 0.33 m2; the hole 0.780 of its rectangle; the sides 0.212 of the height apart; 0.086 of the view from above level; 0.330 of the sides upright; the summit 0.458 off the middle; 0.220 of the surface buried; size steps 1.3, 1.29, 1.45, 1.39, 1.29, 1.58; foot 0.40 m2 on the left and 0.16 on the right. Of seeds 1 to 16 at this size all 16 build and pass gate L1 (`tools/bl tools/try_seeds.py arch_1 1 40`, stopped at 16 when the shared machine was overloaded), with 532 to 568 triangles.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-3.0, -1.0, 0.0]` | Real-world size |
| `bounds_m.max` | `[3.0, 1.0, 4.2]` | Real-world size |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `7` | Pieces |
| `arch.span` | `"lintel"` | Pieces |
| `arch.min_opening_m` | `1.6` | The opening |
| `arch.min_clear_m` | `2.2` | The opening |
| `arch.min_bearing_m2` | `0.2` | The opening |
