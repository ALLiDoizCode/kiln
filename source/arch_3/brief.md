# arch_3

Variant 3 of the arch: a wedged-block arch. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

5.8 m wide, 1.7 m deep and 3.9 m tall: a narrow door. The opening is at least 1.2 m wide and 2.0 m tall, open from the ground up, inside a hole that is wider at the ground and comes to a point under the keystone: one 1.8 m player at a time, with 0.2 m over the head and 0.35 m beside each shoulder. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven: two piers of two stacked blocks each, the upper one of each leaning in over the opening; a keystone wedged between and over the two leaning blocks; and two rubble blocks against the piers' outer feet.

## The opening

Seen from the front, open air right through, at least 1.2 m wide from the ground up to 2.0 m. On each side of it rock stands without a break from the ground into the span over at least 0.1 m2.

## Seed

Seed 3: not picked from several; twelve seeds are in `benchmarks/out/arch_3_candidates.png` for the owner to pick from. It keeps the 36th arch of the 40 it may draw and measures: 590 triangles; one hole seen from the front; the opening 1.72 m wide up to 2.0 m, and 2.67 m tall at its tallest; rock under the knot over 0.24 and 0.72 m2; the hole 0.763 of its rectangle; the sides 0.186 of the height apart; 0.292 of the view from above level; 0.268 of the sides upright; the summit 0.395 off the middle; 0.214 of the surface buried; size steps 1.49, 1.27, 1.32, 1.15, 1.92, 1.46; foot 0.22 m2 on the left and 0.23 on the right. Of seeds 1 to 10 at this size 8 build and pass gate L1 and 2 (seeds 4 and 7) draw forty arches and none meets the spec (the run of 40 was stopped at 10 when the shared machine was overloaded), with 572 to 608 triangles.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-2.9, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.9, 0.85, 3.9]` | Real-world size |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `7` | Pieces |
| `arch.span` | `"wedged"` | Pieces |
| `arch.min_opening_m` | `1.2` | The opening |
| `arch.min_clear_m` | `2.0` | The opening |
| `arch.min_bearing_m2` | `0.1` | The opening |
