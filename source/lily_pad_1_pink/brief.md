# lily_pad_1_pink

`lily_pad_1` with pink flowers: the same group, drawn again from the same seed and bounds, with another flower colour (ADR 11, ADR 13). It is the reference's swamp accent. Everything about it is in the family's brief, `source/lily_pad/brief.md` (Colours), and in `source/lily_pad_1/brief.md`, except what is here. Its mesh, UVs included, is `lily_pad_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["lily_pad_1_pink"]` | Parts: one object |
| `seed` | `1` | `lily_pad_1`'s |
| `bounds_m.min` | `[-0.55, -0.45, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.55, 0.45, 0.09]` | Real-world size |
| `max_triangles` | `480` | Family brief, Budget |
| `painted_shading.texture_px` | `128` | Family brief, Budget |
| `foliage.piece_m` | `[0.08, 0.6]` | Real-world size: a disc's width, from hand-sized to the widest |
| `discs.count` | `[5, 7]` | Real-world size: pads |
| `discs.widest_m` | `[0.35, 0.6]` | Real-world size: the widest pad |
| `blooms.count` | `[1, 1]` | Family brief, Silhouette 6 |
| `blooms.width_m` | `[0.1, 0.18]` | Real-world size: a flower's width |
| `colour` | `"pink"` | Family brief, Colours |
| `palette_of` | `"lily_pad_1"` | The asset whose mesh this is |
| `materials.m_lily_flower` | `"#e0709c"` | Family brief, Colours: flower |
| `painted_shading.base_tint` | `"#b07090"` | Family brief, Colours: toward the water |
