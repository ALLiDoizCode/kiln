# kiln

Assets for Bevy, built as code by headless Blender and gated by scripts. Read `CONTEXT.md` for vocabulary and `docs/adr/` for the decisions (units, axes, facing, format) before touching an asset.

## Commands

- `tools/install_tools.sh` — install the pinned Blender and glTF validator into `.tools/`.
- `tools/gate.sh <asset>` — build the asset and run every gate, stopping at the first failure.
- `python tools/baseline.py approve <asset> [phase]` — record the current contact sheet as approved. Run it only when the user has looked at the sheet and said so in this conversation; a rebuilt sheet that drifts from it then fails the gate.
- `cargo run -p asset_view -- assets/models/<asset>.glb assets/models/<asset>.manifest.json` — open the asset in a Bevy window with hot reload.
- `python tools/review_aids.py views <image...>` / `blind <a> <b> <out>` — value map and squint view of a render, and a blind side-by-side of two renders; aids for review, not gates.
- `tests/run.sh` — prove the gates themselves can fail. Run after changing anything in `tools/` or `crates/asset_smoke`.
- `tools/bl <script.py> [args]` — the only way to run Blender here. Never call the binary directly.

## Rules

- An asset is `source/<asset>/{brief.md, spec.json, build.py}`. `out/` and `assets/models/*.glb` are outputs; never edit them by hand.
- A build script gives each material one flat colour. Painted shading is asked for in the spec (`painted_shading`) and added by `tools/paint.py` during the build (ADR 10); a build script never unwraps or bakes.
- Expected values (bounds, budgets) go in `spec.json` from the brief, never copied from what the build produced.
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
