# 11. Leaf pieces take their colour from a palette in the painted texture, not from a bake

Foliage is leaf pieces (ADR 9): several hundred separate flat pieces per tree, each one flat colour, lighter and yellower at the top of its pad and darker and bluer underneath, with neighbours differing. ADR 10 says painted shading is one baked texture per asset. For leaf pieces a bake is the wrong tool, and this is what is done instead.

- The asset keeps one texture. The bark is unwrapped and baked into it as ADR 10 describes. A strip along the top of the same texture, 16 px tall on the tree, holds a **palette**: 8 px swatches of flat colour.
- Every corner of a leaf piece has the same UV, the middle of one swatch. A piece is therefore one colour exactly, however the texture is filtered.
- The palette is computed from the spec alone: the leaf material's colour times a tint running from `under_tint` to `top_tint` in `shades` steps, each in `tones` tones up to `variation` lighter or darker. `tools/paint.py` picks a piece's shade from how high it sits among the pieces of its own pad and its tone from a fixed shuffle. Pieces and pads are found from the mesh (`tools/foliage.py`), not from labels the build script leaves.
- Bark and leaf are two materials on the one texture: the leaf material is two-sided and the bark is not. `tools/export.py` merges the two texture entries the exporter writes, because Bevy loads each entry as an image of its own.
- The gates measure it as loaded by Bevy (`crates/asset_smoke/src/foliage.rs`): one colour per piece, every colour on the palette the manifest gives, neighbours differing, each pad lighter above than below and bluer below than above.

Why not a bake. It was not tried; the numbers ruled it out. The tree's 620 pieces are about 60 m2 of surface against the bark's 8 m2. At the conventions' 100 texels per metre that is 600,000 texels, plus an 8 px gap round each of 620 islands: a 1024 px texture for the leaves alone, to hold 24 colours. Bilinear filtering and the bake's own margin would also put a gradient across the edge of every piece, which the style does not want, and there is nothing in a flat piece for edge light or crevice shadow to find.

Why not vertex colours. They would work: a colour that is the same at every corner of a piece has none of the sampling trouble ADR 10 found. They were not chosen because the bark needs the texture anyway, `COLOR_0` would then have to be carried by the bark's vertices too (white), and a palette can be swapped without touching the mesh, which is how the reference pack gets its autumn and snow trees. A seasonal variant becomes a second texture, not a second mesh.

Lighting. Bevy lights the back of a two-sided face with the normal turned round, so the underside of a pad gets only ambient light. Measured in the viewer, that is dark green and not black. The pieces' normals are part their own and part the direction out of their pad and upward, set by the generator. Light passing through leaves (diffuse transmission) cannot be carried by a GLB that Bevy 0.19 loads; if the game wants it, it sets it on the leaf material when it spawns a tree.

Costs accepted: the leaves carry UVs (8 bytes a vertex) that all point at a handful of texels; `tools/paint.py` and the load test each have a second path, for foliage; an asset with foliage must have painted shading, because the palette lives in its texture; and the colour steps are the palette's, 24 colours on the tree.

Added with ADR 9's second amendment: the cores under the leaf pieces are in the leaf material and take one more swatch, after the leaves' (the leaf colour times the spec's `core_tint`), with every corner of every core on it. The load test finds cores as closed sets of the leaf material's triangles and holds them to that one colour, darker than any piece.

Not decided here: palettes shared between assets (each tree variant carries the same strip in its own texture), and how a seasonal palette would be named and chosen.
