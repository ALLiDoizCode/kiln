# tree_1_autumn

`tree_1` in autumn: the same tree, drawn again from the same species, growth stage, seed and bounds, with another palette (ADR 11, ADR 13). Everything about it is in the family's brief, `source/tree/brief.md` (Seasons), and in `source/tree_1/brief.md`, except what is here. Its mesh, UVs included, is `tree_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tree_1_autumn"]` | Parts: one object |
| `seed` | `1` | `tree_1`'s |
| `bounds_m.min` | `[-2.4, -2.3, 0.0]` | `tree_1`'s |
| `bounds_m.max` | `[2.5, 2.4, 7.0]` | `tree_1`'s |
| `season` | `"autumn"` | Family brief, Seasons |
| `palette_of` | `"tree_1"` | The asset whose mesh this is |
| `materials.m_tree_leaf` | `"#e0a23a"` | Family brief, Seasons: the colour at the top of a pad |
| `foliage.under_tint` | `"#b86a50"` | Family brief, Seasons: the underside |
| `foliage.core_tint` | `"#8a4a3c"` | Family brief, Seasons: the core, darker than the darkest piece |
