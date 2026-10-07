# 3D Asset Pipeline Resources

## Knowledge

- [Spec: glTF 2.0, Khronos Group](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)
  The definition of the file Bevy loads. Use for: exactly what a mesh, primitive, attribute, material and texture are (section 3.7 onward), units and axes (3.4), and what an engine must do when data is missing.
- [Tutorial: glTF Tutorial, Khronos Group](https://github.khronos.org/glTF-Tutorials/gltfTutorial/)
  The spec retold step by step with small JSON examples. Use for: a first reading of any glTF concept before the spec itself. The Meshes page is [here](https://github.khronos.org/glTF-Tutorials/gltfTutorial/gltfTutorial_009_Meshes.html).
- [Guide: Asset Creation Guidelines 2.0, Khronos 3D Commerce group](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)
  Tool-neutral practice for real-time assets, written by a standards body and kept current (2.0 announced at SIGGRAPH 2025). Chapters: file structure, geometry, UVs, materials, textures, lighting, animation, levels of detail, performance. Use for: what "good" means at each stage, and the reasons. Written for product models, so its budgets are not game budgets.
- [Docs: `Mesh`, Bevy 0.19.1](https://docs.rs/bevy/0.19.1/bevy/mesh/struct.Mesh.html)
  What Bevy needs from a mesh and which attributes it knows. Use for: anything about how the asset is consumed in the engine. Check the version against `Cargo.toml` before relying on it.
- [Docs: `bevy_gltf`, Bevy 0.19.1](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)
  The loader between the file and the engine. Use for: how primitives, materials and scenes arrive as Bevy assets, and the loader's settings.
- [Docs: Blender manual, glTF 2.0 exporter](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)
  What Blender writes and how its materials map to glTF. Use for: export settings and why something in Blender did not survive export.
- [Docs: Tripo API, model v3.1](https://developers.tripo3d.com/en/models/v3-1)
  Tripo's own description of what its generator outputs and the options that change it (`face_limit`, `quad`, `smart_low_poly`, `pbr`). Use for: evaluating Tripo against a production bar. It is a vendor page: it states capabilities, never weaknesses.
- [Tool: glTF Validator, Khronos Group](https://github.com/KhronosGroup/glTF-Validator)
  Checks a file against the spec. Use for: the first automatic check on any asset from any source.
- `git show first-attempt:docs/research/3d-asset-agent-workflow.md`
  Research gathered for the first kiln attempt, removed from the working tree on 2026-10-07, with its sources listed. Use for: finding further primary sources. Its conclusions have not been checked by the learner.

## Wisdom (Communities)

- [Polycount forum](https://polycount.com/)
  The long-standing forum of working game artists. Use for: critique of an asset's topology, bakes and textures, and "how is this done in production" questions. Its wiki (wiki.polycount.com) could not be reached on 2026-10-07; check again before citing it.
- [Bevy Discord and discussions](https://bevy.org/community/)
  Use for: how assets behave in Bevy specifically, and what other solo developers' pipelines look like.

The learner has not yet said whether they want to join communities; ask before leaning on these.

## Gaps

- No verified source yet on budgets for a first-person game on GTX 1660 class hardware (triangles, materials, texture memory). Needed before any "production ready" number is taught.
- No independent (non-vendor) assessment of Tripo3D output quality: topology, UVs, texture seams, licence terms.
- No chosen primary source yet for baking and normal maps, or for PBR materials. Candidates to vet: Marmoset's baking guides, Google Filament's material documentation.
- No source yet for collision shapes and levels of detail in Bevy.
