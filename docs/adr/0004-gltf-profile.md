# 4. Delivery format is GLB in a Bevy-loadable profile

Every asset ships as one self-contained `.glb` under `assets/models/`. glTF is the only model format Bevy loads first-party, and the only one with a real validator.

Valid glTF is a superset of what `bevy_gltf` loads, so the Khronos validator is not sufficient. `conventions.toml` `[gltf_profile]` lists the extensions Bevy 0.19.1 can load, taken from the `gltf` crate features `bevy_gltf` enables; `tools/bevy_lint.py` enforces it. No Draco, no meshopt, triangles only, every node named.

`KHR_materials_clearcoat`, `anisotropy` and `specular` are loadable only with extra Bevy cargo features and are left out until an asset needs them.

Exporter options are set explicitly in `tools/export.py`. Tangents and UVs are exported only when the asset's spec lists them: flat-colour assets carry neither.
