---
name: asset-brief
description: Turn an asset idea into an approved brief and spec, before any geometry exists.
disable-model-invocation: true
---

# Asset brief

A **brief** says what the asset is and why; a **spec** is the brief's numbers, which the gates enforce. Both are written before any geometry, so every later check compares the asset against what was asked for instead of against itself.

Read `CONTEXT.md` and `docs/adr/` first; use their terms and stay inside their decisions.

## 1. Grill

Call the Skill tool with `grilling` and work this design tree with the user. Every leaf is the user's decision; give a recommended answer for each, with the number you would put in the spec.

- **Purpose**: what the asset does in the game, and whether anything interacts with it (stood on, pushed, opened, destroyed).
- **Viewing**: the closest the camera gets, and the typical distance. This sets how much detail is visible and so the triangle budget.
- **Real-world size**: width, depth, height in metres, and where the origin sits. Name a real object of that size as a sanity check.
- **Silhouette**: the two or three features that make it read as this object from the typical distance, each with the dimension that defines it (a frame's width, a recess's depth). Everything else is optional detail.
- **Style and colour**: which existing asset it must sit beside, and each material's name and base colour as an sRGB hex value.
- **Parts**: which pieces are separate objects (anything that moves or is swapped), and which are one mesh.
- **Budget**: triangles and material slots, argued from viewing distance and how many instances appear on screen.
- **References**: images or real objects to match. Save any files under `source/<asset>/refs/`.
- **Out of scope**: what this asset deliberately leaves out (LODs, collision, rig, variants).

Done when the user confirms every leaf, with none left assumed.

## 2. Write the brief

Write `source/<asset>/brief.md`: one short section per leaf above, in the user's words where they gave them. State each recommendation the user overrode, and why, so a reviewer can tell intent from accident.

## 3. Write the spec

Write `source/<asset>/spec.json`, taking every value from the brief. `source/tracer/spec.json` is the worked example and `tools/lint_spec.py` defines the required keys. Bounds are in Blender space: +Z up, front facing −Y, origin on the ground.

Then add a `## Numbers` table to the brief with one row per spec value: the spec key, the value, and the sentence of the brief it comes from (`source/crate/brief.md` shows the format). A number that matters and has no spec key yet is a missing check: hand it to the `asset-checks` skill before modelling.

Done when `python tools/lint_spec.py <asset>` exits 0.

## 4. Approve

Show the user the Numbers table and ask for approval. Modelling starts only on an explicit yes; a changed answer returns to step 1 for that leaf.
