# 2. Bevy is pinned to an exact version

The workspace pins `bevy = "=0.19.1"`. Bevy minor releases break APIs and change what the glTF loader accepts, and the crates we expect to depend on (Skein, Avian) each target one Bevy minor.

Upgrading is a deliberate task: bump the pin in `Cargo.toml` and `conventions.toml`, re-derive `[gltf_profile]` from the new `bevy_gltf` (ADR 4), port `crates/asset_smoke`, and re-run every asset through `tools/gate.sh`.
