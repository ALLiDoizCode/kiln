# table_rock_1_mossy

`table_rock_1` under moss: the same stone, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Everything about it is in the family's brief, `source/table_rock/brief.md` (Covers), and in `source/table_rock_1/brief.md`, except what is here. Its mesh, UVs included, is `table_rock_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["table_rock_1_mossy"]` | Parts: one object |
| `seed` | `1` | `table_rock_1`'s |
| `bounds_m.min` | `[-1.8, -1.5, 0.0]` | `table_rock_1`'s |
| `bounds_m.max` | `[1.8, 1.5, 2.9]` | `table_rock_1`'s |
| `overlap.min_count` | `3` | `table_rock_1`'s |
| `overlap.max_count` | `3` | `table_rock_1`'s |
| `table.necks` | `1` | `table_rock_1`'s |
| `table.min_clear_m` | `2.0` | `table_rock_1`'s |
| `table.min_overhang_m` | `0.6` | `table_rock_1`'s |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"table_rock_1"` | The asset whose mesh this is |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.9` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.25` | Family brief, Covers: the share of near-level faces under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_darker` | `0.5` | Family brief, Covers: how much darker than the stone the patches are |
| `painted_shading.growth_patch_m` | `0.2` | Family brief, Covers: how large a patch is |
