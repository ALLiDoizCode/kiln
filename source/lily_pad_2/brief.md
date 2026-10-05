# lily_pad_2

Variant 2 of the lily pads. Everything about it is in the family's brief, `source/lily_pad/brief.md`, except what is here.

## Real-world size

A group as long as a 1.8 m player is tall: 1.8 m wide, 1.5 m deep and 0.12 m tall, of 6 to 9 pads, the widest 0.6 to 1.0 m across (a cafe table), with two flowers 10 to 24 cm across. The origin is on the water's surface at the middle of the bounds.

## Seed

Seed 2.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["lily_pad_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.9, -0.75, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.9, 0.75, 0.12]` | Real-world size |
| `max_triangles` | `720` | Family brief, Budget |
| `painted_shading.texture_px` | `128` | Family brief, Budget |
| `foliage.piece_m` | `[0.08, 1.0]` | Real-world size: a disc's width, from hand-sized to the widest |
| `discs.count` | `[6, 9]` | Real-world size: pads |
| `discs.widest_m` | `[0.6, 1.0]` | Real-world size: the widest pad |
| `blooms.count` | `[2, 2]` | Family brief, Silhouette 6 |
| `blooms.width_m` | `[0.1, 0.24]` | Real-world size: a flower's width |
| `variants.siblings` | `["lily_pad_1", "lily_pad_3"]` | The other two variants |
| `variants.min_difference` | `0.3` | As the trees: how far its outline differs from each of the others' |
