# kiln

A 3D asset pipeline for games on Bevy, with Blender as the authoring tool. The repo was reset to a clean start on 2026-10-07: the pipeline is to be designed as its owner learns the domain (`learn/`), and nothing about its stages, checks or conventions is decided yet.

The first attempt is at the git tag `first-attempt`. It was built without domain knowledge; do not restore code, decisions or vocabulary from it unless the user asks.

## What is here

- `learn/` — the owner's course on 3D asset pipelines: `MISSION.md`, `RESOURCES.md`, lessons, reference pages and learning records. `learn/specimens/` holds two models from the first attempt, kept only as files to inspect.
- `kiln/` — the Python package. `kiln/measure.py` measures one model file (`measure(path, size=None)` returns a plain dict); `kiln/glb.py` is the only glTF reader, also used by `learn/assets/glb_inspect.py`. Standard library only: system Python has no numpy.
- `kiln/run.py` — a run (`kiln/rebuild.py` repeats `build()` over the store). `take_in()` copies a model file into the store as the raw output and starts its asset record; `review.take_pictures()` renders the review pictures and the run stops for the shape review; `build()`, for an approved asset only, makes the asset from that record alone: the stages in `STAGES`, one measurement, then the checks in `kiln/checks.py`. A stage is a function `(source, work, record, profile) -> (model path, facts)`; a check is a function `(report, profile) -> result`. Mesh stages are scripts in `kiln/blender_scripts/`, run in the pinned Blender through `tools/bl`.
- `kiln/review.py` — the shape review: takes the review pictures of a raw output by starting `review_pictures` (below), and writes a person's decision into the asset record with the pictures it was made on. The renderer is a function argument, so tests stand in for it. Kiln looks for the renderer at `target/release/review_pictures` (or under `$CARGO_TARGET_DIR`, or the path in `$KILN_REVIEW_RENDERER`). If it is missing kiln says how to build it (the first build takes minutes); if it is older than its source kiln builds it again with cargo.
- `profiles/` — target profiles, one TOML file each, in git. `pit.toml` is provisional: its fields are placeholders until issue #11.
- `assets/` — the store, one folder per asset: `asset_record.json` and `reference_image.*` (in git), `raw_output.glb`, `<name>.glb` and `review/` (ignored by git; the record holds their checksums). The first run creates it.
- `tests/` — `unittest` tests; `tests/glb_fixture.py` writes tiny `.glb` files from Python lists. `tests/cross_check/blender_figures.py` counts the same figures in Blender for comparison.
- `crates/asset_view` — two programs. `asset_view` is a Bevy window that shows a `.glb` on a ground plane under a slow turntable, framed by its bounding box, with hot reload. `review_pictures` (`src/bin/`) writes the review pictures of a `.glb` as PNG files, in Bevy with no window: the fixed set of views is data in `src/views.rs`, described in `learn/reference/review-pictures.html`; change a camera there and `VIEW_SET` goes up. Both share the scene and light in `src/scene.rs`. PNG, JPEG and WebP textures show, including WebP given through `EXT_texture_webp` (which Bevy cannot read itself: `src/webp.rs` rewrites the file's JSON as it loads).
- `crates/budget_bench` — the measurement behind the pit target profile's budgets: draws procedural scenes in a full-screen Bevy window with vsync off and times the frames against triangles per asset, texture size and assets on screen. It needs the development machine's GPU and display. The scene list is `src/case.rs`; results and the write-up are `learn/research/pit-budget-measurement.md` and the directory of the same name.
- `tools/install_tools.sh` — installs the pinned Blender and glTF validator into `.tools/`.
- `tools/bl <script.py> [args]` — runs a script in the pinned Blender, headless and with factory settings.
- `benchmarks/` — third-party asset packs for comparison; ignored by git, never committed or shipped.

## Commands

- `cargo run -p asset_view -- <asset.glb>` — open an asset in the viewer.
- `cargo build --release -p asset_view --bin review_pictures` — build the program that renders the review pictures. `kiln run` needs it and does not build it; the first build takes several minutes.
- `target/release/review_pictures <model.glb> --size <metres> --closest <metres> --out <folder>` — render the review pictures of any model file by hand.
- `cargo test -p asset_view` — run the viewer crate's unit tests (the WebP rewrite, where the review pictures' cameras stand).
- `cargo run --release -p budget_bench -- --out learn/research/pit-budget-measurement` — run the whole budget measurement again and overwrite its CSV files. Takes about 16 minutes and the whole screen; leave the machine alone while it runs. `--only <name prefix>` runs some scenes, `--repeats N` changes the three repeats.
- `cargo test -p budget_bench` — unit tests of the scene generators (triangle counts, texture bytes, layout).
- `python3 learn/assets/glb_inspect.py <asset.glb>` — print what a model file holds.
- `python3 -m kiln.measure <asset.glb> [--size METRES] [--json]` — measure a model file: counts, bounding box, materials, textures, UVs, texel density, validator result. Each number is defined in `learn/reference/measuring-a-model.html`.
- `python3 -m kiln run --model <file.glb> --size <metres> --profile pit --licence <text> --source <text> [--reference-image FILE] [--name NAME] [--store DIR]` — start a run from an existing model file (a bought or hand-modelled one): keeps it as the raw output, renders its review pictures into `assets/<name>/review/shape/` and stops for the shape review, printing where the pictures are and how to decide. Nothing is built. Exit 0 when it is waiting for the review; 2 when an input cannot be used or the pictures cannot be rendered (nothing is left in the store). An asset is never overwritten: remove `assets/<name>/` to make it again.
- `python3 -m kiln review <name> [--approve | --reject | --render] [--note TEXT] [--store DIR]` — the shape review of an asset. With no choice it says where the review stands. `--approve` records the approval and builds the asset: scales it to the size and checks it against the target profile; exit 0 when every check passes, 1 when a check fails (the check, the measured value, the limit and the overshoot are printed, and no finished model is written). `--reject` records the rejection and ends the run: the raw output and the record stay, nothing is built, exit 0. A decision is made once, and only while the pictures the record names are there; `--render` renders them again while the review waits. Exit 2 when it cannot be done.
- `python3 -m kiln rebuild [NAME ...] [--check] [--store DIR] [--profiles DIR]` — rebuilds every asset in the store that has an asset record (or the named ones) from its kept raw output, never calling a generator and never asking for a review again, and reports one line per asset: unchanged, changed (and what), failed a check, raw output missing or changed (not rebuilt from, record untouched), finished model missing or changed (reported, then rebuilt), waiting for shape review or rejected at shape review (not built, record untouched). Exit 1 if any asset failed a check or had a problem; waiting and rejected assets are neither. `--check` only looks and writes nothing: missing or changed files, a profile changed since the record, a last build that failed. Code in `kiln/rebuild.py`.
- `python3 -m kiln measure ...` — the same as `python3 -m kiln.measure`.
- `python3 -m unittest` — run the tests, from the repo root. The tests that start Blender and the validator are skipped when `.tools/` does not hold them, and those that render review pictures for real (`tests.test_review.ReviewPicturesForReal`, about 15 seconds, needs a graphics card) when `review_pictures` is not built; every test uses a temporary store.
- `tools/bl tests/cross_check/blender_figures.py <asset.glb>` — the same counts taken in Blender.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root holds the glossary; `docs/adr/` is created there when the first decision is recorded. See `docs/agents/domain.md`.
