# tall_grass_1_dry

`tall_grass_1` dried out: the same clump, drawn again from the same seed and bounds, with another palette (ADR 11, ADR 13). It is the reference's "tall dry grass". Everything about it is in the family's brief, `source/tall_grass/brief.md` (Seasons), and in `source/tall_grass_1/brief.md`, except what is here. Its mesh, UVs included, is `tall_grass_1`'s; only its texture differs, and the gate holds it to that (`spec.palette_of`, `palette.same_mesh`).

Its season is `dry`: a season of its own in `conventions.toml`, beside the year's three.

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tall_grass_1_dry"]` | Parts: one object |
| `seed` | `1` | `tall_grass_1`'s |
| `bounds_m.min` | `[-0.5, -0.5, 0.0]` | `tall_grass_1`'s |
| `bounds_m.max` | `[0.5, 0.5, 1.15]` | `tall_grass_1`'s |
| `season` | `"dry"` | Family brief, Seasons |
| `palette_of` | `"tall_grass_1"` | The asset whose mesh this is |
| `materials.m_tall_grass_leaf` | `"#d8bf62"` | Family brief, Seasons: the colour of the tallest blade |
| `materials.m_tall_grass_straw` | `"#c2a468"` | Family brief, Seasons: the seed heads and the rootstock |
| `foliage.under_tint` | `"#b08a6a"` | Family brief, Seasons: the low blades |
