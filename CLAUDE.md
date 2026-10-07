# kiln

A 3D asset pipeline for games on Bevy, with Blender as the authoring tool. The repo was reset to a clean start on 2026-10-07: the pipeline is to be designed as its owner learns the domain (`learn/`), and nothing about its stages, checks or conventions is decided yet.

The first attempt is at the git tag `first-attempt`. It was built without domain knowledge; do not restore code, decisions or vocabulary from it unless the user asks.

## What is here

- `learn/` — the owner's course on 3D asset pipelines: `MISSION.md`, `RESOURCES.md`, lessons, reference pages and learning records. `learn/specimens/` holds two models from the first attempt, kept only as files to inspect.
- `crates/asset_view` — a Bevy window that shows a `.glb` on a ground plane under a slow turntable, framed by its bounding box, with hot reload. PNG, JPEG and WebP textures show, including WebP given through `EXT_texture_webp` (which Bevy cannot read itself: `src/webp.rs` rewrites the file's JSON as it loads).
- `tools/install_tools.sh` — installs the pinned Blender and glTF validator into `.tools/`.
- `tools/bl <script.py> [args]` — runs a script in the pinned Blender, headless and with factory settings.
- `benchmarks/` — third-party asset packs for comparison; ignored by git, never committed or shipped.

## Commands

- `cargo run -p asset_view -- <asset.glb>` — open an asset in the viewer.
- `cargo test -p asset_view` — run the viewer crate's unit tests (the WebP rewrite).
- `python3 learn/assets/glb_inspect.py <asset.glb>` — print what a model file holds.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the repo root holds the glossary; `docs/adr/` is created there when the first decision is recorded. See `docs/agents/domain.md`.
