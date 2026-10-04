# 10. Painted shading is one baked texture per asset, not vertex colours

An asset that wants painted shading (ADR 9) says so in its spec (`painted_shading`). `tools/paint.py` then unwraps it by script, bakes the painted colour into one PNG with Cycles, and puts that texture on the material in place of its flat colour; `tools/build.py` calls it after the asset's own build script, which stays a few lines of flat colour. The texture is embedded in the GLB. Assets without the block stay flat-coloured, with no UVs.

Vertex colours were the cheaper candidate: no UVs, no image, about 1 kB. They were tried first, on the rock (126 triangles).

- **Why they washed out.** Not colour space: a constant linear 0.2 written to a colour attribute came out of the exporter as `COLOR_0` 0.2, for float and byte attributes, per corner and per vertex, and glTF defines `COLOR_0` as linear. The cause is where a vertex bake samples. Baked term by term, the gradient and the crevice shadow gave the same mean as a texture bake (ratios 1.01 and 1.00). The edge light gave 1.30 times the texture's mean: 69% of face corners carried it, against 11% of texels, because on a low-triangle mesh every vertex sits on an edge and each face then spreads its corners' light across itself. All three together came to 1.42 times, which is the pale wash.
- **Why fixing that is not enough.** With the edge light left out, the rock's 79 vertices can hold the height gradient and nothing else: no light on edges, no shadow confined to the ledge, and the growth's edge becomes a straight blur. Adding vertices to carry them costs more than the texture does: at 15 cm spacing the rock is 6,348 triangles and 157 kB, sixteen times its triangle budget, for detail about twenty times coarser than a 1024 px texture gives at 380 kB (30 cm: 1,734 triangles; 8 cm: 22,778).

Costs accepted: the rock's file goes from 3.7 kB to 380 kB; the build gains about 4 seconds; the gates gain UV and texel checks; `crates/asset_smoke` now loads images (PNG only, so `[gltf_profile]` allows only PNG).

The texture's size comes from the spec, and `conventions.toml` sets the least texel density, 100 per metre: a 1 cm texel seen from 0.5 m (ADR 7). Sharper than that would need thousands per metre, and painted shading has nothing that fine in it.

The edge light and crevice shadow both come from Cycles' ambient occlusion node, cast outward for crevices and into the solid for edges. The Bevel node used in the look test lit the middle of every soft-edge strip darker than its sides.

Not decided here: several materials sharing one texture, normal maps, and hand-drawn-looking brushwork. Vertex colours stay allowed in a spec's `attributes` for an asset that wants only a gradient; nothing uses them.
