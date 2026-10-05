# flower_scatter_3

Variant 3 of the flower scatter. Everything about it is in the family's brief, `source/flower_scatter/brief.md`, except what is here.

## Real-world size

0.3 m wide, 0.28 m deep and 0.15 m tall, of 3 to 5 flowers: a handspan and a half across, the tallest flower at the ankle of a 1.8 m player. The origin is on the ground at the middle of the bounds.

## Seed

Seed 3.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["flower_scatter_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.15, -0.14, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.15, 0.14, 0.15]` | Real-world size |
| `max_triangles` | `300` | Family brief, Budget |
| `blooms.width_m` | `[0.07, 0.1]` | Family brief, Real-world size: each across |
| `blooms.count` | `[3, 5]` | Real-world size: flowers |
| `variants.siblings` | `["flower_scatter_1", "flower_scatter_2"]` | The other two variants |
| `variants.min_difference` | `0.3` | As the trees: how far its outline differs from each of the others' |
