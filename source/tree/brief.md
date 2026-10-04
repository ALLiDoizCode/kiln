# tree

**Draft: decisions only.** The spec, build script and the rest of this brief are still to be written, and no gate has been run.

## Decisions

Made by the owner on 2026-10-04, each by accepting a recommendation:

- **Subject**: a plain broadleaf tree about 7 m tall. It is chosen because it has a direct benchmark; trees specific to the pit come after it.
- **Form**: a generator that takes a seed, with three variants as the deliverable.
- **Foliage**: leaf-shaped geometry in flat colour, on a visible branch skeleton, in several separate pads with sky between them (ADR 9 as amended). No leaf cards, no transparency.
- **Surface**: painted shading (ADR 10).
- **Budget**: proposed as at most 6,000 triangles and two materials, from the benchmark tree's 6,265. The owner accepted that leaf-shaped geometry may need more; the brief must state the number it settles on and why.
- **Judgement**: our tree and the benchmark tree side by side in Bevy on one sheet. The owner approves when ours is not clearly worse.

## References

- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/CommonTree_1.gltf` (6,265 triangles, 7.3 m tall, leaf cards). A benchmark only; nothing from it is used.
- Shapes and construction habits: `docs/style/nature-shapes.md`, the Broadleaf row and "How they are built".
- Branch skeleton tool: Sapling Tree Gen, to be pinned in `.tools/` (see `docs/research/free-assets-for-recreation-gaps.md`). Its default output is far over budget and must be reduced.
