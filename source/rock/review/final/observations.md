# rock / final: observations

From `sheet.png`, seed 2, 126 triangles, colour `#a1a7a1`. Orthographic tiles are framed at 4.90 m across 512 px (104 px per metre); pixel figures are read by eye and good to about 2%. Numbers marked L1 are printed by `tools/validate.py` for this build. The benchmark comparison uses `benchmarks/out/rock_vs_benchmark.png` (both rendered by `asset_view`, standard and `--close`).

## Silhouette

- Large planes (brief: 6 to 16, holding at least 75% of the visible surface, largest at least 3 times the median). L1: 12 large planes holding 80.2% of 14.91 m2, largest 3.08 m2, median 0.66 m2, ratio 4.68. three_quarter and bevy: one plane (the slab) fills more than half of the rock's outline; front: the slab is the right-hand two thirds, with four smaller planes to its left.
- Ledge (brief: a concave corner of at least 0.5 m between two large planes). L1: one, 1.32 m long. It reads in front, back and scale as a notch in the outline: in front the shelf is at about 1.25 m, 0.65 m wide, with a riser about 0.6 m tall behind it, leaning back. In right it does not break the outline; it shows only as a darker upright band left of centre. In top it is the straight dark line right of centre. In bevy it is a small notch at the upper left, about one tenth of the rock's width.
- No face reads as part of a sphere: in every material tile each plane is one even tone, and tone changes only across the narrow strips between planes.
- Sides lean in from a wide base: front, right and back all show the outline widest at the ground. right: the slab runs from the peak (left third of the tile) to the ground at the far right, at about 45 degrees on screen; the left side is within 10 degrees of upright.

## Proportions

- front: 61% of the tile wide and 41% tall, so 3.0 m by 2.0 m. Brief: 3.0 m, 2.0 m.
- right: 53% of the tile wide, so 2.6 m. Brief: 2.6 m.
- The rock is much less than its bounding box: 14.91 m2 of visible surface against 30.2 m2 for the box's top and sides. The peak is a ridge about 0.6 m wide in front, not a broad top.

## Facing and grounding

- front, right, back, scale: the base is a straight line on the lower edge of the spec's frame, with no gap.
- The brief names no front. front shows the ledge on the left and the slab on the right; top shows a seven-sided outline with the ledge line running front to back.

## Topology (clay_wire)

- Every plane boundary is a pair of close parallel lines, the bevel strip, about 0.1 m apart on screen. They follow the silhouette everywhere.
- Inside each plane, diagonals fan from one corner (front: five across the slab). They support nothing: the plane is flat. They exist because the gate allows no face with more than four sides.
- No dense patch anywhere; the smallest faces are the triangles where three strips meet.

## Shading (material)

- No plane is darker or lighter than its lighting explains. front, three_quarter: plane boundaries show as soft bands of blended tone, not lines.
- back and right are lit only by the shadowless fill light: planes there differ by a few percent in tone, so the form is carried by the outline more than by shading.

## Materials

- One pale grey with a slight green cast in every tile, on every face. Brief: `m_rock` `#a1a7a1`.

## Scale

- scale: the rock's top is at about 1.12 times the figure's height. Brief: 2.0 m beside 1.8 m, 1.11. The shelf is at about two thirds of the figure's height, shoulder level.

## In the engine (bevy tile)

- Lit planes are near white-grey, lighter than in the Blender tiles; the one shaded plane on the right is near black. Contrast between lit and shaded is far higher than in Blender, as it was for the crate.
- Soft edges survive export: each boundary between lit planes is a narrow band blending one tone into the next, with no hard line. The exported file has 79 vertices at 65 positions; the only positions with two normals are the 14 on the ground edge.
- The base meets the ground with a cast shadow and no gap.
- The view is from the front right, which shows the slab almost square on. About 70% of the rock's outline is one untextured plane.

## Beside the benchmark

Both in Bevy, same camera and light (`benchmarks/out/rock_vs_benchmark.png`).

- Planes and edges: ours has flatter planes and equally soft edges. The benchmark's planes wobble (11% of its surface is in large planes at a 1 degree tolerance, ours 80%).
- Mass: the benchmark fills its box (24.3 m2 of surface, with a top more than half its width); ours is a wedge with a narrow ridge (14.9 m2). Standing beside it, ours is a smaller thing than its bounds say.
- Secondary form: the benchmark has a raised slab on top and a vertical fracture groove down its front, visible from the standard view. Ours has one ledge, and from the standard view it is a small notch; the rest of that view is one plane.
- Surface: the benchmark's texture gives a dark-to-light gradient, darker crevices and moss. Ours is one flat colour, so the slab close up is a blank pale field. This is the out-of-scope painted shading, and it is most of the visible difference.
- Cost: 126 triangles against 342.

## Differences from the brief

None found against the brief's numbers: bounds, budget, colour, plane count, share, size ratio, ledge and soft edges are each as specified.

One defect escaped the gates during the build and is now closed: the first export lit every face flat (246 vertices, bevel strips as hard bands), because plane normals were read before the mesh was restretched. Every gate passed. It is now `soft_edges` in the spec and a check in the Bevy load test, with a flat-shaded rock as its red case in `tests/run.sh`.

For the owner to judge, since no number in the brief settles them:

1. The rock is wedge-shaped and occupies about half its bounding box's surface. The brief gives bounds, not fullness.
2. "Clearly different tilts" has no check. The build script draws the slab 24 to 34 degrees off upright, the other sides 0 to 15, and the top 6 to 16 off level, before the final stretch.
3. From the front right the slab hides the ledge. Turning the rock, or a seed with the ledge beside the slab, would show both.
4. Lit faces in Bevy are close to white. As with the crate, colour should wait for the game's lighting.
5. Bevel width (0.07 m) and one segment: at `--close` the edge reads as soft, not round. A second segment would roughly double the triangle count and stay in budget.
