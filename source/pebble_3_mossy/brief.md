# pebble_3_mossy

`pebble_3` under moss: the same stone, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Everything about it is in the family's brief, `source/pebble/brief.md` (Covers), and in `source/pebble_3/brief.md`, except what is here. Its mesh, UVs included, is `pebble_3`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["pebble_3_mossy"]` | Parts: one object |
| `seed` | `3` | `pebble_3`'s |
| `bounds_m.min` | `[-0.25, -0.19, 0.0]` | `pebble_3`'s |
| `bounds_m.max` | `[0.25, 0.19, 0.1]` | `pebble_3`'s |
| `painted_shading.edge_width_m` | `0.016` | `pebble_3`'s |
| `painted_shading.blotch_size_m` | `0.05` | `pebble_3`'s |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"pebble_3"` | The asset whose mesh this is |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.03` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.25` | Family brief, Covers: the share of near-level faces under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_edge_m` | `0.03` | Family brief, Covers: how far in from an edge the growth along it reaches |
| `painted_shading.growth_darker` | `0.5` | Family brief, Covers: how much darker than the stone the patches are |
| `painted_shading.growth_patch_m` | `0.03` | Family brief, Covers: how large a patch is |
