# 8. The pipeline and the game are separate repos

`kiln` is the asset pipeline: briefs, specs, build scripts, gates, review, and the exported assets. Its job ends when a checked GLB is in `assets/`. The game (terrain, climbing, the curse, persistence, networking, the look test) lives in its own repo and consumes `kiln`'s assets.

The only Bevy code in `kiln` is what verifies assets: the headless load test and a viewer for review screenshots.

The contract between the two is the `assets/` folder and the metrics in ADR 7. A question about how the game works belongs in the game repo, even when its answer changes a number here.

While grilling the pipeline's robustness, the discussion moved from "what does the pipeline need to know about the game" to designing the game. Keeping prototypes in `kiln` would have turned it into the game by accretion, and the gates would have ended up guarding game code they were never designed for.
