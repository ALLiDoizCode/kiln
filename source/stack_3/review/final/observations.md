# stack_3, final: observations

From `sheet.png` in this folder, read on 2026-10-05 after the gates passed. Numbers marked L1 are the gate's own, from `out/reports`; the rest are read off the tiles.

## 1. Silhouette

- front, right, back: three stones read as three bands; the lowest about 0.45 of the height, the other two about 0.3 each.
- top: three outlines at different angles; the top stone covers the upper right of the lowest one's outline and reaches its rim there.
- front: a dark triangular wedge under the middle of the second stone, a third of that stone's width, and another under the left end of the top stone; right shows the top stone standing clear of the second on the left by about a quarter of its thickness. These are air gaps over a tipped cap, and at this size they are the darkest thing in the tile.
- Off-centre (Silhouette 4): reads in top and front; L1 puts the summit 0.307 of the half extents from the middle (at least 0.15).
- Would not topple (Silhouette 5): no stone's middle is past the edge of the band below it in front, right or back; L1 finds no stone tipping off.

## 2. Proportions

- L1: going up, each stone covers 0.61, 0.59 of the one below seen from above (at most 0.85); thickness over width 0.25 to 0.26 (at most 0.5); each is sunk 0.12 to 0.15 of its thickness into the cap below (at most 0.35); 0.265 of the surface is buried (at most 0.45).

## 3. Facing and grounding

- front, right, back: the lowest stone's bottom edge is a straight line on the bottom of the spec's frame; nothing below it. A stack has no front; none is marked.

## 4. Topology

- clay_wire tiles: every edge is a doubled line, the two sides of a soft edge; no edge crosses a plane without a corner to support. The edges round each underside are as dense as those round each cap, and most of each underside is buried. 334 triangles.

## 5. Shading

- material tiles: no face darker or lighter than its neighbours without a cause; each plane is one tone and each edge a thin lighter line.

## 6. Materials

- One grey on every stone, lighter on the caps and toward the top stone, darker on the lowest stone's sides; a dark band at every join. Brief: `#a1a7a1` between a `#8c8c9a` foot and a `#c8c8c8` top.

## 7. Scale

- scale: the pile is under a fifth of the figure's height; brief 0.32 m of 1.8 m, 0.18.

## 8. In the engine

- bevy, bevy_back: the caps are lighter and the shadow sides darker than in the material tiles; in bevy_back the side away from the light is about the tone of the pile's own cast shadow on the ground, and the joins on that side cannot be told from the sides. L4d (`view.shade_value`) passes.

## 9. Values and 10. At a glance

- No aids were made for this variant; they were made for `stack_2` only. Items 9 and 10 are not written, so item 11 is not complete.

## 11. Differences from the brief

- Air gaps at the joins (item 1): the brief asks that each stone rests on the one below, and the check measures that under the stone's middle only. Where a stone overhangs a cap that tips away from it, a wedge of open air shows. No check covers it; a number could (the largest gap between an underside and the surface under it, round the stone's rim). Not closed: an escaped defect for the `asset-checks` skill.
- The turn of each stone (Silhouette 3) and the caps tipping back against each other (Silhouette 8) are judged here only: in top every outline is at its own angle; the tip of the caps cannot be read from these tiles.
