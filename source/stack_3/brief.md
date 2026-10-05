# stack_3

Variant 3 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

0.5 m wide, 0.44 m deep and 0.32 m tall: a small pile at a path's edge, shin high, 0.18 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Three.

## Budget

At most 360 triangles: 120 a stone.

## Paint

A 512 px texture, and the bands of the largest pebble (`source/pebble_3`), which is as wide as this stack, 0.5 m. Bands half the family's were tried first: they left 804 samples of open face in two tones with nothing between, which the load test refuses as banding. Those bands (0.016 m of edge light, 0.05 m of crevice shadow) still failed `painted.banding`: the only open face was on the lowest stone and the top cap, 20 levels of tone apart, with every stone between covered by the shadow of its joins. The bands are now 0.012 and 0.025 m, chosen so that the sides of the middle stones keep some open face; they come from the load test's refusals and not from a reference.

## Seed

Seed 3. It was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["stack_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.25, -0.22, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.25, 0.22, 0.32]` | Real-world size |
| `max_triangles` | `360` | Budget |
| `overlap.min_count` | `3` | Stones |
| `overlap.max_count` | `3` | Stones |
| `painted_shading.texture_px` | `512` | Paint: 512 px |
| `painted_shading.edge_width_m` | `0.012` | Paint: narrowed until the middle stones show open face |
| `painted_shading.crevice_width_m` | `0.025` | Paint: narrowed until the middle stones show open face |
| `painted_shading.blotch_size_m` | `0.05` | Paint: the largest pebble's |
