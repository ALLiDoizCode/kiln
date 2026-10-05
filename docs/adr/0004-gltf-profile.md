# 4. Delivery format is GLB in a Bevy-loadable profile

Every asset ships as one self-contained `.glb` under `assets/models/`. glTF is the only model format Bevy loads first-party, and the only one with a real validator.

Valid glTF is a superset of what `bevy_gltf` loads, so the Khronos validator is not sufficient. `conventions.toml` `[gltf_profile]` lists the extensions Bevy 0.19.1 can load, taken from the `gltf` crate features `bevy_gltf` enables; `tools/bevy_lint.py` enforces it. No Draco, no meshopt, triangles only, every node named.

`KHR_materials_clearcoat` and `anisotropy` are loadable only with extra Bevy cargo features and are left out until an asset needs them.

**Amended 2026-10-05: `KHR_materials_specular` is in the profile, for its factor only.** The trees' leaf material needs no gloss: with the default, a flat leaf piece the sun grazes shows the sun's glare to a player under the canopy (`source/tree_1/review/final/review.md`, finding 3). The exporter writes a Principled BSDF's Specular IOR Level of 0 as `specularFactor: 0`, and `bevy_gltf` 0.19.1 reads that factor into `StandardMaterial::reflectance` with no extra feature (`loader/mod.rs`: `reflectance: specular_factor * 0.5`). The extension's textures do need the feature `pbr_specular_textures` and stay out; no check refuses them yet.

Exporter options are set explicitly in `tools/export.py`. Tangents and UVs are exported only when the asset's spec lists them: flat-colour assets carry neither. Textures are PNG, the one image format the Bevy crates here decode (ADR 10).
