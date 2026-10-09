---
status: accepted
---

# Kiln reduces the mesh, from the generator's dense raw output

The raw output is the generator's dense, fully textured model (Tripo's H3.1 on its defaults: about 1.9 million triangles with base colour, metallic-roughness and normal maps), and kiln brings it inside the target profile's budgets itself, in the pinned Blender: clean, reduce with one Collapse pass, lay the UV islands out again and bake the dense model's three maps onto the reduced one. Decided 2026-10-08 on the measurements in `learn/research/blender-stages-trial.md` and `learn/research/tripo-api-trial.md` sections 9 to 11.

## Considered options

- **Ask the generator for the budget directly** (H3.1 asked for 20,000 triangles). One step, in budget, three maps. On the crate its edges came back ragged where kiln's were straight; on the creature it was sound. Its textures would still need bringing down from 4096. Kept open, not chosen: a dense raw output can always be reduced again to a new budget, and a reduced one cannot be made dense.
- **The generator's low-poly models with its paid texture step** (P1.0, P2.0). Rejected: base colour only, thousands of UV islands, files that fail the glTF validator, and on the crate 99% of the triangles hidden inside a 108-triangle box.

## Consequences

- A profile's budgets can change and every asset can be rebuilt to them from its kept raw output, with no new generation.
- The store holds raw outputs of 55 to 65 MB each, and a build takes one to two minutes.
- The bake runs on the CPU with one thread. That is the only setting found that gives the same bytes every time, which `kiln rebuild` depends on; a graphics card must not be allowed to change an asset.
- The evidence is two subjects, a crate and a spiky creature, from one generator. Meshy and Rodin, which issue #4 also named, were not tried.
