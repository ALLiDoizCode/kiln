# kiln

A 3D asset pipeline for games on Bevy, with Blender as the authoring tool. The repo was reset to a clean start on 2026-10-07: the pipeline is to be designed as its owner learns the domain (`learn/`), and nothing about its stages, checks or conventions is decided yet.

The first attempt is at the git tag `first-attempt`. It was built without domain knowledge; do not restore code, decisions or vocabulary from it unless the user asks.

## What is here

- `learn/` — the owner's course on 3D asset pipelines: `MISSION.md`, `RESOURCES.md`, lessons, reference pages and learning records. `learn/specimens/` holds two models from the first attempt, kept only as files to inspect.
- `kiln/` — the Python package. `kiln/measure.py` measures one model file (`measure(path, size=None)` returns a plain dict); `kiln/glb.py` is the only glTF reader, also used by `learn/assets/glb_inspect.py`. Standard library only: system Python has no numpy.
- `tests/` — `unittest` tests; `tests/glb_fixture.py` writes tiny `.glb` files from Python lists. `tests/cross_check/blender_figures.py` counts the same figures in Blender for comparison.
- `crates/asset_view` — a Bevy window that shows a `.glb` with hot reload. It still takes the first attempt's manifest file as its second argument.
- `tools/install_tools.sh` — installs the pinned Blender and glTF validator into `.tools/`.
- `tools/bl <script.py> [args]` — runs a script in the pinned Blender, headless and with factory settings.
- `benchmarks/` — third-party asset packs for comparison; ignored by git, never committed or shipped.

## Commands

- `cargo run -p asset_view -- <asset.glb> <manifest.json>` — open an asset in the viewer.
- `python3 learn/assets/glb_inspect.py <asset.glb>` — print what a model file holds.
- `python3 -m kiln.measure <asset.glb> [--size METRES] [--json]` — measure a model file: counts, bounding box, materials, textures, UVs, texel density, validator result. Each number is defined in `learn/reference/measuring-a-model.html`.
- `python3 -m unittest` — run the tests, from the repo root.
- `tools/bl tests/cross_check/blender_figures.py <asset.glb>` — the same counts taken in Blender.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root holds the glossary; `docs/adr/` is created there when the first decision is recorded. See `docs/agents/domain.md`.
