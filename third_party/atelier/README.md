# atelier (third-party, kept for later use)

The oil-paint engine from [bosphorify/claude-painting-skill](https://github.com/bosphorify/claude-painting-skill), copied at commit `1af61f3` (2026-10-02) under its MIT licence (`LICENSE`). It is a numpy paint simulator: bristle strokes, pigment mixing, and a pass that paints a plan image from big brush to small.

Nothing in the pipeline uses it. It is kept because research found no free brush-stroke textures we could ship, and this engine drew stroke shapes and a leaf-cluster atlas with transparency in about a second each, identically on a second run. The source repository was five days old with one author when it was copied, so it is copied, not pinned.

Only the engine is here: `oil/atelier/` and its dependency files. The skill's instructions, its tests, its pencil-and-watercolour half (which needs npm packages that were not reviewed) and its example pictures are left out.

`kiln-trial/` holds the scripts from the evaluation that produced stroke alpha shapes, a leaf atlas, a rock texture, a sky and a repaint. They were single attempts and are not held to any standard. The owner looked at the results on 2026-10-04 and preferred our own renders to the engine's look, so this stays unused until a need for painted strokes comes back.

The evaluation is in `docs/research/claude-painting-skill-evaluation.md`. To run the engine it needs numpy, pillow and scipy in a virtual environment (`uv sync` in `oil/`).
