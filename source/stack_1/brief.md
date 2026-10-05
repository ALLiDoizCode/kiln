# stack_1

Variant 1 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

0.9 m wide, 0.8 m deep and 0.7 m tall: the plain one, a cairn a little over a player's knee, 0.39 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Four.

## Budget

At most 480 triangles: 120 a stone.

## Paint

The family's bands are the smallest slab's, sized for a rock 1.4 m across. This stack is 0.9 m across, 0.64 of that, and its bands are scaled by the same: with the family's bands the edge light and the shadow of the joins covered every stone, and the load test found no sample of open face to measure the stone's colour on. Those bands (0.025 m of edge light, 0.08 m of crevice shadow) still failed `painted.banding`: the only open face was on the lowest stone and the top cap, 20 levels of tone apart, with every stone between covered by the shadow of its joins. The bands are now 0.02 and 0.04 m, chosen so that the sides of the middle stones keep some open face; they come from the load test's refusals and not from a reference.

## Seed

Seed 1. It was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["stack_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.45, -0.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.45, 0.4, 0.7]` | Real-world size |
| `max_triangles` | `480` | Budget |
| `overlap.min_count` | `4` | Stones |
| `overlap.max_count` | `4` | Stones |
| `painted_shading.edge_width_m` | `0.02` | Paint: narrowed until the middle stones show open face |
| `painted_shading.crevice_width_m` | `0.04` | Paint: narrowed until the middle stones show open face |
| `painted_shading.blotch_size_m` | `0.13` | Paint: 0.64 of the family's |
