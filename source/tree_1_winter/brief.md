# tree_1_winter

`tree_1` in winter: the same tree, drawn again from the same species, growth stage, seed and bounds, with another palette (ADR 11, ADR 13). Everything about it is in the family's brief, `source/tree/brief.md` (Seasons), and in `source/tree_1/brief.md`, except what is here. Its mesh, UVs included, is `tree_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tree_1_winter"]` | Parts: one object |
| `seed` | `1` | `tree_1`'s |
| `bounds_m.min` | `[-2.4, -2.3, 0.0]` | `tree_1`'s |
| `bounds_m.max` | `[2.5, 2.4, 7.0]` | `tree_1`'s |
| `season` | `"winter"` | Family brief, Seasons |
| `palette_of` | `"tree_1"` | The asset whose mesh this is |
| `materials.m_tree_leaf` | `"#d8dcde"` | Family brief, Seasons: the colour at the top of a pad |
| `foliage.under_tint` | `"#507359"` | Family brief, Seasons: the underside |
| `foliage.core_tint` | `"#3a5442"` | Family brief, Seasons: the core, darker than the darkest piece |
