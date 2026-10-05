# lily_pad_3

Variant 3 of the lily pads. Everything about it is in the family's brief, `source/lily_pad/brief.md`, except what is here.

## Real-world size

The group with the pad to stand on: 3.0 m wide, 2.6 m deep and 0.16 m tall, of 7 to 10 pads. The widest is 1.2 to 1.7 m across, two thirds of a 1.8 m player's height or more, and its floor is level: room for both feet and a step. Two flowers 14 to 30 cm across. The origin is on the water's surface at the middle of the bounds.

## Seed

Seed 3.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["lily_pad_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.5, -1.3, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.5, 1.3, 0.16]` | Real-world size |
| `max_triangles` | `500` | Family brief, Budget |
| `painted_shading.texture_px` | `128` | Family brief, Budget |
| `foliage.piece_m` | `[0.08, 1.7]` | Real-world size: a disc's width, from hand-sized to the widest |
| `discs.count` | `[7, 10]` | Real-world size: pads |
| `discs.widest_m` | `[1.2, 1.7]` | Real-world size: the widest pad |
| `blooms.count` | `[2, 2]` | Family brief, Silhouette 6 |
| `blooms.width_m` | `[0.14, 0.3]` | Real-world size: a flower's width |
| `variants.siblings` | `["lily_pad_1", "lily_pad_2"]` | The other two variants |
| `variants.min_difference` | `0.3` | As the trees: how far its outline differs from each of the others' |
