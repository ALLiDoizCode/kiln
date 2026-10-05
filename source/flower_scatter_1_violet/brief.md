# flower_scatter_1_violet

`flower_scatter_1` with violet flowers: the same scatter, drawn again from the same seed and bounds, with another petal colour (ADR 11, ADR 13). Everything about it is in the family's brief, `source/flower_scatter/brief.md` (Colours), and in `source/flower_scatter_1/brief.md`, except what is here. Its mesh, UVs included, is `flower_scatter_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["flower_scatter_1_violet"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.25, -0.225, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.25, 0.225, 0.22]` | Real-world size |
| `max_triangles` | `300` | Family brief, Budget |
| `blooms.count` | `[5, 8]` | Real-world size: flowers |
| `colour` | `"violet"` | Family brief, Colours |
| `palette_of` | `"flower_scatter_1"` | The asset whose mesh this is |
| `materials.m_flower_petal` | `"#8a6cd0"` | Family brief, Colours: petal |
