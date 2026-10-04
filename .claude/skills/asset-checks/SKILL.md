---
name: asset-checks
description: The red-before-geometry discipline for 3D asset gates. Use before modelling an asset from its spec, when adding or changing a check in tools/ or crates/asset_smoke, or when a defect reached a review render without any gate failing.
---

# Asset checks

A **gate** is a script whose exit code decides whether an asset moves on. This skill is the reference that makes a green gate mean something: what a good check is, the anti-patterns, and the loop.

## What a good check is

A check measures the built asset and compares it with a value from the spec or `conventions.toml`. It has a stable id (`crate.manifold`, `bounds.match_spec`) and its failure message carries the measurement, so a red gate says what is wrong and by how much.

Each gate reads a different thing: L1 reads the scene inside Blender, L2 and L2b read the exported bytes, L4 reads what Bevy loaded. Put a check at the latest gate that can still see the property, because a defect the exporter introduces is invisible from inside Blender.

## Anti-patterns

- **Tautological**: the expected value is derived from the build (bounds read back from the mesh, a triangle count copied from the last run). It passes by construction. Expected values come from the brief, through the spec.
- **Unproven**: a check that has never been seen red. Every check has a case in `tests/` that breaks a known-good asset one way and asserts this check's id fails.
- **Advisory**: a check that prints a warning and exits 0. A property either gates or belongs in the review render notes.
- **Eyeball-only**: a property that could be measured, left to the contact sheet. If you caught it by eye and a number could have caught it, it becomes a check.

## The loop

1. **Red on the spec.** Before modelling, run `tools/gate.sh <asset>`. It must fail, and for the right reason: no build yet, or a blockout outside the budget or bounds. A gate that is green before the asset exists is checking nothing.
2. **One slice at a time.** Build the next part of the asset, then run the gate. Fix what goes red before adding more geometry.
3. **New property, new check.** When the spec gains a property no check covers, add the check and its red case together, in that order: write the mutation in `tests/`, watch it report NOT CAUGHT, then write the check until `tests/run.sh` passes.
4. **Escaped defect, new check.** When a review render or the user finds a defect every gate passed, reproduce it as a mutation first, then close it as in step 3.

Done when `tools/gate.sh <asset>` and `tests/run.sh` both exit 0, and every property in the spec is named by at least one check id in the reports under `source/<asset>/out/reports/`.
