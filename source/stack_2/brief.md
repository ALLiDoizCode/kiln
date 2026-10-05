# stack_2

Variant 2 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

1.2 m wide, 1.05 m deep and 1.1 m tall: a trail marker, hip to waist high, 0.61 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Five.

## Budget

At most 600 triangles: 120 a stone.

## Paint

A 1024 px texture: this is the largest stack, with about four times the surface of `stack_3`, and it is the one walked up to with its upper stones nearest the eye.

## Seed

Seed 2. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (151 s), with 488 to 568 triangles; none needs more than eight stacks. Only seed 2 was painted and taken through the later gates. It was not picked from several. It measures: 528 triangles; 0.281 buried; size steps of the surface shown 2.42, 1.54, 1.64 and 1.41; each stone covers 0.61, 0.60, 0.55 and 0.59 of the one below; thickness over width 0.26 to 0.32; sunk 0.14 to 0.19; summit 0.455 off the middle. Seeds 1 to 12 are seen side by side in `benchmarks/out/stack_2_candidates.png`.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["stack_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.6, -0.525, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.6, 0.525, 1.1]` | Real-world size |
| `max_triangles` | `600` | Budget |
| `overlap.min_count` | `5` | Stones |
| `overlap.max_count` | `5` | Stones |
| `painted_shading.texture_px` | `1024` | Paint |
