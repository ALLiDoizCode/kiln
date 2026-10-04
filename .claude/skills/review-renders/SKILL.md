---
name: review-renders
description: Look at an asset through fixed-camera renders and record what they show as measurements. Use after any geometry or material change, at the end of each phase, and before telling the user an asset is done.
---

# Review renders

Gates prove an asset is well-formed. The **contact sheet** is where you find out whether it is the right asset. The protocol is fixed so that every sheet is comparable with the last one and with the brief: same cameras, same passes, same framing from the spec's bounds.

## 1. Render

Run `tools/bl tools/review_render.py <asset> <phase>` (the last step of `tools/gate.sh` does this). The phase names the stage being reviewed: `blockout`, `final`. Views are named from the asset's point of view: `front` looks at its front.

## 2. Read the sheet

Read `source/<asset>/review/<phase>/sheet.png` with the Read tool. When a tile needs a closer look, read that tile's own PNG beside it.

## 3. Write observations as measurements

Write `source/<asset>/review/<phase>/observations.md`. Every line names a view and states something a second reader could confirm or refute from the same tile:

- "front: frame is about one eighth of the width on each side; brief says 0.1 m of 0.8 m" is an observation.
- "looks good" and "matches the brief" are verdicts; replace each with the measurement behind it.

Cover, in this order:

1. **Silhouette**: for each silhouette feature the brief names, the view where it reads and the view where it does not.
2. **Proportions**: each part's size as a fraction of the whole, beside the brief's number.
3. **Facing and grounding**: which way the front points in `front` and `top`, and whether the base sits on the bottom edge of the spec's frame.
4. **Topology** (clay_wire tiles): where edges are dense or sparse relative to the silhouette they support, and any edge that supports nothing.
5. **Shading** (material tiles): faces darker or lighter than their neighbours with no lighting reason, which is the sign of a flipped or split normal.
6. **Materials**: each colour against the brief's, and which parts carry it.
7. **Differences from the brief**: every mismatch found above, each with the number that shows it. Write "none found" only after items 1 to 6 are each written.

A mismatch that a number could have caught goes to the `asset-checks` skill as an escaped defect.

## 4. Hand over

Give the user the sheet path and the differences list. At the `blockout` phase, and before an asset is called done, the user looks at the sheet themselves: appeal and style fit are their call, and a clean observations file is the evidence they judge with, never the judgement.
