# arch_1

Variant 1 of the arch: a lintel arch. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

4.2 m wide, 1.7 m deep and 3.3 m tall: a gateway. The opening is at least 1.6 m wide and 2.2 m tall, open from the ground up: a 1.8 m player walks through with 0.4 m over the head and, shoulders 0.5 m wide, 0.55 m to spare on each side. The lintel's top is about 3.2 m up, reached by climbing, and is a place to stand: at least 1.1 m deep. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven: two piers of two stacked blocks each, the lintel, and two rubble blocks against the piers' outer feet.

## The opening

Seen from the front, open air right through, at least 1.6 m wide from the ground up to 2.2 m. On each side of it rock stands without a break from the ground into the span over at least 0.2 m2.

## Seed

Seed 1: not picked from several; twelve seeds are in `benchmarks/out/arch_1_candidates.png` for the owner to pick from. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py arch_1 1 40`), with 538 or 558 triangles. Only this one was painted and taken through the later gates. It keeps the first arch it draws and measures: 538 triangles; one hole seen from the front; the opening 1.67 m wide up to 2.2 m, and 2.40 m tall; rock under the span over 0.47 and 0.37 m2; 0.628 of the view from above level; 0.173 of the surface buried; size steps 1.8, 1.44, 1.38, 1.55, 2.66, 1.64; foot 0.17 m2 on the left and 0.11 on the right.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-2.1, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.1, 0.85, 3.3]` | Real-world size |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `7` | Pieces |
| `arch.span` | `"lintel"` | Pieces |
| `arch.min_opening_m` | `1.6` | The opening |
| `arch.min_clear_m` | `2.2` | The opening |
| `arch.min_bearing_m2` | `0.2` | The opening |
| `top.min_level_share` | `0.5` | A top to stand on (the family brief's Silhouette 5) |
