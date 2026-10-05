# arch_3

Variant 3 of the arch: a wedged-block arch. Everything about it is in the family's brief, `source/arch/brief.md`, except what is here.

## Real-world size

3.8 m wide, 1.3 m deep and 3.4 m tall: a narrow door. The opening is at least 1.2 m wide and 2.0 m tall, open from the ground up, and above that it narrows to a point under the keystone: one 1.8 m player at a time, with 0.2 m over the head and 0.35 m beside each shoulder. Its top is leaning blocks: climbed over, not stood on. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven: two piers, each a tall block with a leaning block stacked on it; a keystone wedged between the two leaning blocks; and two rubble blocks against the piers' outer feet.

## The opening

Seen from the front, open air right through, at least 1.2 m wide from the ground up to 2.0 m. On each side of it rock stands without a break from the ground into the span over at least 0.1 m2.

## Seed

Seed 3: not picked from several. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py arch_3 1 40`), each with 538 triangles. Only this one was painted and taken through the later gates. It keeps the first arch it draws and measures: 538 triangles; one hole seen from the front; the opening 1.31 m wide up to 2.0 m, and 2.82 m tall under the keystone; rock under the knot over 0.28 and 0.24 m2; 0.173 of the surface buried; size steps 1.4, 2.43, 1.15, 1.39, 1.57, 1.42; foot 0.11 m2 on the left and 0.16 on the right.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["arch_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.9, -0.65, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.9, 0.65, 3.4]` | Real-world size |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `7` | Pieces |
| `arch.span` | `"wedged"` | Pieces |
| `arch.min_opening_m` | `1.2` | The opening |
| `arch.min_clear_m` | `2.0` | The opening |
| `arch.min_bearing_m2` | `0.1` | The opening |
