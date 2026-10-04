---
name: review-renders
description: Look at an asset through fixed-camera renders and record what they show as measurements. Use after any geometry or material change, at the end of each phase, and before telling the user an asset is done.
---

# Review renders

Gates prove an asset is well-formed. The **contact sheet** is where you find out whether it is the right asset. The protocol is fixed so that every sheet is comparable with the last one and with the brief: same cameras, same passes, same framing from the spec's bounds.

## 1. Render

Run `tools/gate.sh <asset> <phase>`; its last two steps take a screenshot in Bevy and render the sheet in Blender. The phase names the stage being reviewed: `blockout`, `final`. Views are named from the asset's point of view: `front` looks at its front. The `scale` view and the `bevy` tile show the asset beside a player-height figure.

## 2. Read the sheet

Read `source/<asset>/review/<phase>/sheet.png` with the Read tool. When a tile needs a closer look, read that tile's own PNG beside it.

## 3. Make the aids

Detail hides the two things that decide whether an asset reads: its big light and dark shapes, and what the eye sees at a glance. Run `python tools/review_aids.py views` on the `bevy` tile and the `material_three_quarter` tile, and on the same view of the brief's reference or benchmark when there is one. Each writes an `_aids.png` beside the image with three panels:

- **as rendered**;
- **value map**: the image in five greys. A sound asset shows three to five large, distinct masses here. Many small scattered patches mean the surface is noise; one grey from top to bottom means it will read as flat.
- **squint**: the image blurred, which is how it reads from across a room. The asset should still be recognisable as what the brief names, and the eye should land where the brief's silhouette features are.

Read each aid with the Read tool.

## 4. Write observations as measurements

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
7. **Scale** (scale tiles): the asset's height as a fraction of the figure's, beside the brief's size over the player height in `conventions.toml`.
8. **In the engine** (bevy tile): what differs from the Blender material tiles in colour, contrast and shading. The game ships what Bevy shows, so where the two disagree, Bevy is right.
9. **Values** (value maps): how many distinct masses the asset shows and which parts they are, beside the reference's count and layout. Name any part that vanishes into its neighbour or into the ground.
10. **At a glance** (squint views): what the blurred asset reads as in three words, where the eye lands first, and the same two answers for the reference.
11. **Differences from the brief**: every mismatch found above, each with the number that shows it. Write "none found" only after items 1 to 10 are each written.

A mismatch that a number could have caught goes to the `asset-checks` skill as an escaped defect.

## 5. Hand over

Give the user the sheet path and the differences list. At the `blockout` phase, and before an asset is called done, the user looks at the sheet themselves: appeal and style fit are their call, and a clean observations file is the evidence they judge with, never the judgement.
