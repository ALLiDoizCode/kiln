# flower_scatter_2

Variant 2 of the flower scatter. Everything about it is in the family's brief, `source/flower_scatter/brief.md`, except what is here.

## Real-world size

0.8 m wide, 0.7 m deep and 0.3 m tall, of 7 to 11 flowers: a short stride across, the tallest flower below the knee of a 1.8 m player. The origin is on the ground at the middle of the bounds.

## Seed

Seed 2.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["flower_scatter_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.4, -0.35, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.4, 0.35, 0.3]` | Real-world size |
| `max_triangles` | `400` | Family brief, Budget |
| `blooms.count` | `[7, 11]` | Real-world size: flowers |
| `variants.siblings` | `["flower_scatter_1", "flower_scatter_3"]` | The other two variants |
| `variants.min_difference` | `0.3` | As the trees: how far its outline differs from each of the others' |
