# log_2_mossy

`log_2` under moss: the same log, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Its mesh, UVs included, is `log_2`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`). Everything else about it is in the family's brief, `source/log/brief.md`.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["log_2_mossy"]` | Parts: one object |
| `seed` | `2` | The seed this variant is drawn from |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"log_2"` | The asset whose mesh this is |
| `bounds_m.min` | `[-2.2, -0.75, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.2, 0.75, 1.0]` | Real-world size |
| `max_triangles` | `900` | Budget |
| `painted_shading.texture_px` | `2048` | Painted shading 4 |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.2` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.35` | Family brief, Covers: the share of what faces up under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_edge_m` | `0.1` | Family brief, Covers: how far in from an edge |
| `painted_shading.growth_darker` | `0.3` | Family brief, Covers: how much darker than the bark |
| `painted_shading.growth_patch_m` | `0.15` | Family brief, Covers: how large a patch is |
| `painted_shading.close_texels_per_m` | `250.0` | Painted shading 4 |
| `log.butt` | `"root"` | Real-world size: the butt |
| `log.thickness_m` | `[0.5, 0.7]` | Real-world size: thick |
| `log.stubs` | `[1, 3]` | Silhouette 6 |
