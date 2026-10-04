# 7. The game target, and the metrics that follow from it

Assets are made for one game: a first-person survival and extraction game set in a vertical pit, divided into layers that each have their own biome and can be a player's permanent home. Climbing is a core action, on any surface, with ropes, pitons and ladders as placeable aids. Players build bases from a snapping kit. The terrain is procedural and cannot be dug.

From that target:

- **Camera**: first-person. Assets are seen from as close as 0.5 m, so briefs assume close viewing unless they say otherwise.
- **Player**: 1.8 m tall. Every contact sheet shows the asset beside a figure of that height.
- **Building grid**: 3 m square foundations and 3 m wall height. Every building kit piece is a multiple of the grid. This is the hardest number here to change: once kit pieces exist, changing it means rebuilding all of them.
- **Style**: superseded by ADR 9 (soft-edged shapes with painted shading; leaf-card foliage). Still true from the original: a strict palette per layer, and atmosphere from lighting and fog in the engine.
- **Minimum hardware**: a GTX 1660 or RX 5600 class GPU at 60 frames per second. Triangle and material budgets per asset class are to be derived from this with a stress scene; until then budgets in specs are estimates.
- **Data assets carry**: a climbable flag and collision shapes. Neither is implemented yet.
- **Out of scope for the pipeline** for now: first-person arms, player bodies and creatures. Held items are rigid props and are in scope.

The style was chosen because it is the one this pipeline can produce for a whole game's static assets. It is conditional: the game project's look test must show that beauty, atmosphere and scale survive it. Until that passes, no more than four assets are built.

This supersedes the third-person viewing distance assumed in the crate's first brief.
