# slab_1_mossy

`slab_1` under moss: the same stone, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Everything about it is in the family's brief, `source/slab/brief.md` (Covers), and in `source/slab_1/brief.md`, except what is here. Its mesh, UVs included, is `slab_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["slab_1_mossy"]` | Parts: one object |
| `seed` | `1` | `slab_1`'s |
| `bounds_m.min` | `[-1.3, -1.1, 0.0]` | `slab_1`'s |
| `bounds_m.max` | `[1.3, 1.1, 0.5]` | `slab_1`'s |
| `overlap.min_count` | `2` | `slab_1`'s |
| `overlap.max_count` | `2` | `slab_1`'s |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"slab_1"` | The asset whose mesh this is |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.15` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.25` | Family brief, Covers: the share of near-level faces under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_darker` | `0.5` | Family brief, Covers: how much darker than the stone the patches are |
| `painted_shading.growth_patch_m` | `0.17` | Family brief, Covers: how large a patch is |
