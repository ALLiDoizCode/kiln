# stack_2

Variant 2 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

1.2 m wide, 1.05 m deep and 1.1 m tall: a trail marker, hip to waist high, 0.61 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Five.

## Budget

At most 600 triangles: 120 a stone.

## Seed

Seed 2. It was not picked from several.

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
