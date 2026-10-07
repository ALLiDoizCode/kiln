# kiln

A 3D asset pipeline for games on Bevy, with Blender as the authoring tool. The repo was reset to a clean start on 2026-10-07: the pipeline is to be designed as its owner learns the domain (`learn/`), and nothing about its stages, checks or conventions is decided yet.

The first attempt is at the git tag `first-attempt`. It was built without domain knowledge; do not restore code, decisions or vocabulary from it unless the user asks.

## What is here

- `learn/` — the owner's course on 3D asset pipelines: `MISSION.md`, `RESOURCES.md`, lessons, reference pages and learning records. `learn/specimens/` holds two models from the first attempt, kept only as files to inspect.
- `kiln/` — the Python package. `kiln/measure.py` measures one model file (`measure(path, size=None)` returns a plain dict); `kiln/glb.py` is the only glTF reader, also used by `learn/assets/glb_inspect.py`. Standard library only: system Python has no numpy.
- `kiln/run.py` — a run. `take_in()` copies a model file into the store as the raw output and starts its asset record; `build()` makes the asset from that record alone: the stages in `STAGES`, one measurement, then the checks in `kiln/checks.py`. A stage is a function `(source, work, record, profile) -> (model path, facts)`; a check is a function `(report, profile) -> result`. Mesh stages are scripts in `kiln/blender_scripts/`, run in the pinned Blender through `tools/bl`.
- `profiles/` — target profiles, one TOML file each, in git. `pit.toml` is provisional: its fields are placeholders until issue #11.
- `assets/` — the store, one folder per asset: `asset_record.json` (in git), `raw_output.glb` and `<name>.glb` (both ignored by git; the record holds their checksums). The first run creates it.
- `tests/` — `unittest` tests; `tests/glb_fixture.py` writes tiny `.glb` files from Python lists. `tests/cross_check/blender_figures.py` counts the same figures in Blender for comparison.
- `crates/asset_view` — a Bevy window that shows a `.glb` on a ground plane under a slow turntable, framed by its bounding box, with hot reload. PNG, JPEG and WebP textures show, including WebP given through `EXT_texture_webp` (which Bevy cannot read itself: `src/webp.rs` rewrites the file's JSON as it loads).
- `tools/install_tools.sh` — installs the pinned Blender and glTF validator into `.tools/`.
- `tools/bl <script.py> [args]` — runs a script in the pinned Blender, headless and with factory settings.
- `benchmarks/` — third-party asset packs for comparison; ignored by git, never committed or shipped.

## Commands

- `cargo run -p asset_view -- <asset.glb>` — open an asset in the viewer.
- `cargo test -p asset_view` — run the viewer crate's unit tests (the WebP rewrite).
- `python3 learn/assets/glb_inspect.py <asset.glb>` — print what a model file holds.
- `python3 -m kiln.measure <asset.glb> [--size METRES] [--json]` — measure a model file: counts, bounding box, materials, textures, UVs, texel density, validator result. Each number is defined in `learn/reference/measuring-a-model.html`.
- `python3 -m kiln run --model <file.glb> --size <metres> --profile pit --licence <text> --source <text> [--name NAME] [--store DIR]` — a run from an existing model file (a bought or hand-modelled one): scales it to the size, checks it against the target profile, and writes the asset into the store. Exit 0 when every check passes; 1 when a check fails (the check, the measured value, the limit and the overshoot are printed, and no finished model is written); 2 when an input cannot be used. An asset is never overwritten: remove `assets/<name>/` to make it again.
- `python3 -m kiln measure ...` — the same as `python3 -m kiln.measure`.
- `python3 -m unittest` — run the tests, from the repo root. The tests that start Blender and the validator are skipped when `.tools/` does not hold them; every test uses a temporary store.
- `tools/bl tests/cross_check/blender_figures.py <asset.glb>` — the same counts taken in Blender.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root holds the glossary; `docs/adr/` is created there when the first decision is recorded. See `docs/agents/domain.md`.
