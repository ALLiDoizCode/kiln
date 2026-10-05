# reeds_1_winter

`reeds_1` in winter: the same bed, drawn again from the same seed and bounds, with another palette (ADR 11, ADR 13): dead, straw-coloured stalks and leaves with their dark heads still on. Everything about it is in the family's brief, `source/reeds/brief.md` (Seasons), and in `source/reeds_1/brief.md`, except what is here. Its mesh, UVs included, is `reeds_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["reeds_1_winter"]` | Parts: one object |
| `seed` | `1` | `reeds_1`'s |
| `bounds_m.min` | `[-0.45, -0.4, 0.0]` | `reeds_1`'s |
| `bounds_m.max` | `[0.45, 0.4, 2.0]` | `reeds_1`'s |
| `season` | `"winter"` | Family brief, Seasons |
| `palette_of` | `"reeds_1"` | The asset whose mesh this is |
| `materials.m_reeds_leaf` | `"#cdb88a"` | Family brief, Seasons: the colour of the tallest stalk |
| `materials.m_reeds_brown` | `"#4a3222"` | Family brief, Seasons: the heads and the mud |
| `foliage.under_tint` | `"#a48c74"` | Family brief, Seasons: the low leaves |
