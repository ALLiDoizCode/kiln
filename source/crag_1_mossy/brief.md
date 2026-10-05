# crag_1_mossy

`crag_1` under moss: the same stone, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Everything about it is in the family's brief, `source/crag/brief.md` (Covers), and in `source/crag_1/brief.md`, except what is here. Its mesh, UVs included, is `crag_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["crag_1_mossy"]` | Parts: one object |
| `seed` | `1` | `crag_1`'s |
| `bounds_m.min` | `[-1.6, -1.3, 0.0]` | `crag_1`'s |
| `bounds_m.max` | `[1.6, 1.3, 3.0]` | `crag_1`'s |
| `max_triangles` | `540` | `crag_1`'s |
| `overlap.min_count` | `6` | `crag_1`'s |
| `overlap.max_count` | `6` | `crag_1`'s |
| `cluster.min_prisms` | `4` | `crag_1`'s |
| `foot.min_side_m2` | `0.08` | `crag_1`'s |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"crag_1"` | The asset whose mesh this is |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.9` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.25` | Family brief, Covers: the share of near-level faces under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_darker` | `0.5` | Family brief, Covers: how much darker than the stone the patches are |
| `painted_shading.growth_patch_m` | `0.2` | Family brief, Covers: how large a patch is |
