# slab_1

Variant 1 of the slab. Everything about it is in the family's brief, `source/slab/brief.md`, except what is here.

## Real-world size

2.6 m wide, 2.2 m deep and 0.5 m tall: the plain one, knee high. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Two plates: the dominant one and the taller one pushed into its side.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py slab_1 1 40`), with 190 to 226 triangles; only this one was painted and taken through the later gates. Seed 1 was not picked from several: it is the first. Its first slab is the one kept. It measures: 208 triangles; 0.158 of the surface buried (at most 0.3); a size step of 1.73 (at least 1.3); 0.565 of the view from above level (at least 0.5); no side within 8 degrees of upright; summit 0.345 off the middle (at least 0.15). The level share is the measure closest to its limit.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["slab_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-1.3, -1.1, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.3, 1.1, 0.5]` | Real-world size |
| `overlap.min_count` | `2` | Pieces |
| `overlap.max_count` | `2` | Pieces |
