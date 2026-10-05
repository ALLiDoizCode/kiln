# stack_1, final: observations

From `sheet.png` in this folder, read on 2026-10-05 after the gates passed. Numbers marked L1 are the gate's own, from `out/reports`; the rest are read off the tiles.

## 1. Silhouette

- front, right, back: four stones read as four bands, each narrower than the one below; the lowest is about 0.95 of the tile's pile width and the top about 0.45.
- top: four outlines, each at its own angle; the top stone is a five-sided cap toward the upper right of the lowest stone's outline, not over its middle.
- front: under the left end of the second stone and under the third there is a dark wedge about a tenth of the pile's width long: the stone overhangs the tipped cap below and open air shows between them. The same wedge shows in right (left side, between the second and third stones).
- Off-centre (Silhouette 4): reads in top and front; L1 puts the summit 0.374 of the half extents from the middle (at least 0.15).
- Would not topple (Silhouette 5): no stone's middle is past the edge of the band below it in front, right or back; L1 finds no stone tipping off.

## 2. Proportions

- L1: going up, each stone covers 0.62, 0.65, 0.52 of the one below seen from above (at most 0.85); thickness over width 0.23 to 0.26 (at most 0.5); each is sunk 0.16 to 0.18 of its thickness into the cap below (at most 0.35); 0.308 of the surface is buried (at most 0.45).

## 3. Facing and grounding

- front, right, back: the lowest stone's bottom edge is a straight line on the bottom of the spec's frame; nothing below it. A stack has no front; none is marked.

## 4. Topology

- clay_wire tiles: every edge is a doubled line, the two sides of a soft edge; no edge crosses a plane without a corner to support. The edges round each underside are as dense as those round each cap, and most of each underside is buried. 430 triangles.

## 5. Shading

- material tiles: no face darker or lighter than its neighbours without a cause; each plane is one tone and each edge a thin lighter line.

## 6. Materials

- One grey on every stone, lighter on the caps and toward the top stone, darker on the lowest stone's sides; a dark band at every join. Brief: `#a1a7a1` between a `#8c8c9a` foot and a `#c8c8c8` top.

## 7. Scale

- scale: the pile is about 0.4 of the figure's height; brief 0.7 m of 1.8 m, 0.39.

## 8. In the engine

- bevy, bevy_back: the caps are lighter and the shadow sides darker than in the material tiles; in bevy_back the side away from the light is about the tone of the pile's own cast shadow on the ground, and the joins on that side cannot be told from the sides. L4d (`view.shade_value`) passes.

## 9. Values and 10. At a glance

- No aids were made for this variant; they were made for `stack_2` only. Items 9 and 10 are not written, so item 11 is not complete.

## 11. Differences from the brief

- Air gaps at the joins (item 1): the brief asks that each stone rests on the one below, and the check measures that under the stone's middle only. Where a stone overhangs a cap that tips away from it, a wedge of open air shows. No check covers it; a number could (the largest gap between an underside and the surface under it, round the stone's rim). Not closed: an escaped defect for the `asset-checks` skill.
- The turn of each stone (Silhouette 3) and the caps tipping back against each other (Silhouette 8) are judged here only: in top every outline is at its own angle; the tip of the caps cannot be read from these tiles.
