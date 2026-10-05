# stack_2, final: observations

From `sheet.png` in this folder, read on 2026-10-05 after the gates passed. Numbers marked L1 are the gate's own, from `out/reports`; the rest are read off the tiles.

## 1. Silhouette

- front, right, back: five stones read as five bands stepping up to the right in front; the lowest band is about 0.28 of the pile's height, the second 0.2, and the top three about 0.17 each.
- top: five outlines, each at its own angle; the top stone is over the left third of the lowest stone's outline.
- front: a dark wedge under the right half of the second stone, about a fifth of the pile's width long, and a smaller one under the third: open air between a stone and the tipped cap below it. right and back show the same under the second stone.
- front and three_quarter: the lowest stone is 1.3 times as wide as the second and shows a quarter more height; with its long leaning sides it reads as a plinth under four stones. It measures 0.255 thick over wide (limit 0.5), so the brief's number does not rule it out.
- Off-centre (Silhouette 4): reads in top and front; L1 puts the summit 0.455 of the half extents from the middle (at least 0.15).
- Would not topple (Silhouette 5): no stone's middle is past the edge of the band below it in front, right or back; L1 finds no stone tipping off.

## 2. Proportions

- L1: going up, each stone covers 0.61, 0.60, 0.55, 0.59 of the one below seen from above (at most 0.85); thickness over width 0.26 to 0.32 (at most 0.5); each is sunk 0.14 to 0.19 of its thickness into the cap below (at most 0.35); 0.281 of the surface is buried (at most 0.45).

## 3. Facing and grounding

- front, right, back: the lowest stone's bottom edge is a straight line on the bottom of the spec's frame; nothing below it. A stack has no front; none is marked.

## 4. Topology

- clay_wire tiles: every edge is a doubled line, the two sides of a soft edge; no edge crosses a plane without a corner to support. The edges round each underside are as dense as those round each cap, and most of each underside is buried. 528 triangles.

## 5. Shading

- material tiles: no face darker or lighter than its neighbours without a cause; each plane is one tone and each edge a thin lighter line.

## 6. Materials

- One grey on every stone, lighter on the caps and toward the top stone, darker on the lowest stone's sides; a dark band at every join. Brief: `#a1a7a1` between a `#8c8c9a` foot and a `#c8c8c8` top.

## 7. Scale

- scale: the pile is about 0.6 of the figure's height; brief 1.1 m of 1.8 m, 0.61.

## 8. In the engine

- bevy, bevy_back: the caps are lighter and the shadow sides darker than in the material tiles; in bevy_back the side away from the light is about the tone of the pile's own cast shadow on the ground, and the joins on that side cannot be told from the sides. L4d (`view.shade_value`) passes.

## 9. Values and 10. At a glance

- bevy value map (`bevy_aids.png`): three masses. The caps and lit sides of the upper four stones are one light grey; the lowest stone and every shadow side are the ground's own mid grey, so the lowest stone has no edge against the ground on its lit side; the cast shadow is the one dark mass, and with the slot under the second stone it is the darkest thing in the tile. No benchmark of this shape to set beside it.
- bevy squint: a pale lump on a dark shadow, about a third of the figure's height in the picture; "pale rock pile". The eye lands on the top two stones, the lightest part. The separate stones cannot be told apart at this blur.
- material_three_quarter aids were made (`material_three_quarter_aids.png`) and not read.

## 11. Differences from the brief

- Air gaps at the joins (item 1): the brief asks that each stone rests on the one below, and the check measures that under the stone's middle only. Where a stone overhangs a cap that tips away from it, a wedge of open air shows. No check covers it; a number could (the largest gap between an underside and the surface under it, round the stone's rim). Not closed: an escaped defect for the `asset-checks` skill.
- The turn of each stone (Silhouette 3) and the caps tipping back against each other (Silhouette 8) are judged here only: in top every outline is at its own angle; the tip of the caps cannot be read from these tiles.
- The lowest stone reads as a plinth (item 1). Within the brief's numbers; a look decision.
