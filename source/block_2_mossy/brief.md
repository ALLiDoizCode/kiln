# block_2_mossy

`block_2` under moss: the same stone, drawn again from the same seed and bounds, with growth painted on it (ADR 10, ADR 13). Everything about it is in the family's brief, `source/block/brief.md` (Covers), and in `source/block_2/brief.md`, except what is here. Its mesh, UVs included, is `block_2`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["block_2_mossy"]` | Parts: one object |
| `seed` | `2` | `block_2`'s |
| `bounds_m.min` | `[-0.5, -0.35, 0.0]` | `block_2`'s |
| `bounds_m.max` | `[0.5, 0.35, 0.6]` | `block_2`'s |
| `max_triangles` | `250` | `block_2`'s |
| `painted_shading.texture_px` | `512` | `block_2`'s |
| `painted_shading.edge_width_m` | `0.0312` | `block_2`'s |
| `painted_shading.crevice_width_m` | `0.06` | `block_2`'s |
| `painted_shading.crevice_shadow` | `0.45` | `block_2`'s |
| `painted_shading.blotch_size_m` | `0.15` | `block_2`'s |
| `block.min_chamfer_m` | `0.08` | `block_2`'s |
| `overlap.min_count` | `2` | `block_2`'s |
| `overlap.max_count` | `2` | `block_2`'s |
| `overlap.max_buried_share` | `0.4` | `block_2`'s |
| `overlap.min_step_ratio` | `1.3` | `block_2`'s |
| `cracks.count` | `1` | `block_2`'s |
| `cracks.depth_m` | `0.025` | `block_2`'s |
| `cracks.width_m` | `0.1` | `block_2`'s |
| `cracks.min_span` | `0.7` | `block_2`'s |
| `cover` | `"mossy"` | Family brief, Covers |
| `palette_of` | `"block_2"` | The asset whose mesh this is |
| `painted_shading.growth` | `"#7a8a4d"` | Family brief, Covers: the moss's colour |
| `painted_shading.growth_height_m` | `0.18` | Family brief, Covers: how far up from the ground the moss reaches |
| `painted_shading.growth_up` | `0.25` | Family brief, Covers: the share of near-level faces under patches |
| `painted_shading.growth_edges` | `0.4` | Family brief, Covers: the share of the exposed upper edges under patches |
| `painted_shading.growth_edge_m` | `0.055` | Family brief, Covers: how far in from an edge the growth along it reaches |
| `painted_shading.growth_darker` | `0.5` | Family brief, Covers: how much darker than the stone the patches are |
| `painted_shading.growth_patch_m` | `0.055` | Family brief, Covers: how large a patch is |
