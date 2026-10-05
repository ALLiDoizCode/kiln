# kiln

Assets for Bevy, built as code by headless Blender and gated by scripts. Read `CONTEXT.md` for vocabulary and `docs/adr/` for the decisions (units, axes, facing, format) before touching an asset.

## Commands

- `tools/install_tools.sh` — install the pinned Blender and glTF validator into `.tools/`.
- `tools/gate.sh <asset>` — build the asset and run every gate, stopping at the first failure.
- `python tools/baseline.py approve <asset> [phase]` — record the current contact sheet as approved. Run it only when the user has looked at the sheet and said so in this conversation; a rebuilt sheet that drifts from it then fails the gate.
- `cargo run -p asset_view -- assets/models/<asset>.glb assets/models/<asset>.manifest.json` — open the asset in a Bevy window with hot reload. With `--screenshot <out.png>` it saves one view and exits 0, or saves nothing and exits 1 when the asset is not in the picture; `--close`, `--back`, `--stand <metres>` (a player's eye that far from the asset) and `--pitch <degrees>` (with `--stand`: how far above level to look) choose the view.
- `python tools/review_aids.py views <image...>` / `blind <a> <b> <out>` — value map and squint view of a render, and a blind side-by-side of two renders; aids for review, not gates.
- `tools/variants_sheet.sh <out.png> <benchmark.gltf> <benchmark.manifest.json> <asset...>` — variants beside a benchmark under Bevy from five views, the last from below. `KILN_SHEET_VIEWS` (views separated by semicolons) replaces them, for a rock too low to be seen from below.
- `tools/bl tools/try_seeds.py <asset> <first> <last>` — build an asset from a run of seeds and say which pass gate L1; an aid for a family's brief, not a gate.
- `tests/run.sh` — prove the gates themselves can fail, after changing anything in `tools/`, `crates/` or `tests/`. While iterating run the affected part: `tests/run.sh --changed` (what the files changed since the last commit affect), `tests/run.sh rock`, `tests/run.sh L4 rock` (an asset, a gate, or both), `tests/run.sh --only <regex>` (case names and check ids). Before reporting done run it with no selection: only a last line reading `ran ALL <n> cases` is a full run; `PARTIAL RUN` is not. `--help` lists the rest. The cases are the lines of `tests/cases.sh`.
- `tools/bl <script.py> [args]` — the only way to run Blender here. Never call the binary directly.

## Rules

- An asset is `source/<asset>/{brief.md, spec.json, build.py}`. `out/` and `assets/models/*.glb` are outputs; never edit them by hand.
- A rock of several pieces is closed pieces that overlap, left separate in one mesh; its spec says so with `overlap` and its generator builds with `tools/stone.py` (ADR 13). No boolean union.
- A build script gives each material one flat colour. Painted shading is asked for in the spec (`painted_shading`) and added by `tools/paint.py` during the build (ADR 10); a build script never unwraps or bakes.
- Expected values (bounds, budgets) go in `spec.json` from the brief, never copied from what the build produced.
- A tree's spec names a `species` (a recipe in `source/tree/species/`), a `growth_stage` and a `season`; a season of another asset names it as `palette_of` and must build the same mesh. Gate the base before its seasons.
- Variants drawn by one generator are separate assets (`source/tree_1`, ...) whose specs name a `family`: the folder holding the generator and the brief they share (`source/tree`). A family folder is not an asset and has no spec.
- Every asset is for the game described in `docs/adr/0007-game-target-and-metrics.md`; questions about how the game works belong in the `pit` repo (ADR 8).
- A gate passing means the asset is well-formed, not that it is good. After the gates pass, read `source/<asset>/review/<phase>/sheet.png` and describe what it shows as measurements before calling anything done.
- A new check is not finished until a case in `tests/` shows it failing on a broken input.
- In Blender scripts prefer the data API (`bpy.data`, `bmesh`) over `bpy.ops`; operators report failure by return value, so check it and raise.
- Project standards live in `conventions.toml`; add a value there only when a script reads it.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, through the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels, unchanged. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
