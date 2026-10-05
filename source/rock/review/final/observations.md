# rock / final: observations

From `sheet.png`: seed 5 of the third generator (several pieces), 322 triangles, colour `#a1a7a1` under painted shading in one 1024 px texture, 551 kB. Orthographic tiles are framed at 4.90 m across 512 px (104 px per metre); pixel figures are read by eye and good to about 2%. Numbers marked L1 are printed by `tools/validate.py` for this build, and numbers marked L4 are in `out/reports/L4-bevy.json`, measured by the Bevy load test on the exported texture. The benchmark comparison uses `benchmarks/out/rock_v3_vs_benchmark.png` (both rendered by `asset_view`: standard, `--close` and `--back`); the second rock is still in `rock_vs_benchmark.png`.

## Silhouette

- Fullness (brief: at least 45% of the bounding box). L1: 46.0%. front, right, back: one mass about 2.0 m tall whose top is 1.5 to 1.9 m wide, with lower blocks against it. The second rock held 56.2%.
- Crown (brief: at least 28% of the footprint three quarters up). L1: 34.8%. top: the cap is an eight-sided area about 1.9 m by 1.6 m.
- Pieces and size order (brief: at least 5 showing 0.2 m2, the dominant at least 3 times the next, each at least 1.15 times the next). L1: six pieces showing 10.24, 1.37, 1.03, 0.83, 0.42 and 0.27 m2; steps 7.5, 1.33, 1.23, 1.98, 1.55. The record and the mesh differ over 1.0% of the space they fill, and 80.7% of the visible surface lies on a recorded piece (the rest is soft edge). top: the dominant piece is the octagon; five blocks stand out from it, two on the left edge of the tile, two on the lower edge and one at the upper right. back: the tall secondary is the slab in the middle, 0.8 m wide at the ground and about 1.35 m tall. The dominant piece is 7.5 times the next, so in every tile this is one large mass with small things against it; none of the secondary pieces reads as a second mass.
- Foot (brief: 0.15 m2 of low near-level surface on at least 2 sides). L1: right 0.30 m2, left 0.17 m2, back 0.11 m2, front 0.01 m2. front: a block 0.5 m tall at each lower corner. right: two blocks, 0.3 and 0.5 m tall, across the lower middle. bevy: the two feet at the lower right are the nearest things to the camera.
- Nothing upright (brief: at most 15% of side surface within 8 degrees of vertical). L1: 0.0%. front: the left side leans in about 0.35 m over 2.0 m (10 degrees) and the right side about 0.4 m. Every side leans by about the same amount, 9 to 12 degrees, so the outline in front, right and back is a symmetrical trapezoid.
- Summit off-centre (brief: at least 0.15 of the half extents). L1: 0.187. front: the cap's high edge is at the upper left and it falls about 0.25 m to the right. top: the pale cap sits a little above and left of the middle of the tile.
- Chamfers (brief: at least 3 of 0.1 to 0.4 m2, 0.2 m wide, between large planes). L1: 3, of 0.11, 0.18 and 0.37 m2. back, bevy: the cap's rim is cut at the right of back and toward the camera in bevy; the largest is about 0.6 m wide. Seen from 3 m they are narrow beside 2 m2 walls: they read as a broken rim, not as faces of their own.
- Planes (brief: 6 to 16 large, at least 60% of the surface, largest at least 2 times the median). L1: 11 large planes holding 62.2% of 17.56 m2; largest 1.92 m2, median 0.86 m2, ratio 2.23.
- No plane dominates (brief: at most 40% of the outline). L1: front 40%, right 18%, back 19%, left 20%, top 28%, three_quarter 22%, three_quarter_back 16%. front: one wall, about 1.6 m wide and 1.9 m tall, is most of the tile's rock. It is at the limit.
- A form on every side (brief: 0.5 m of ledge corner in sight from each of seven directions). L1: front 0.84 m, right 1.29 m, back 2.70 m, left 2.20 m, top 1.10 m, three_quarter 0.84 m, three_quarter_back 2.64 m. The corners are where the secondary pieces' flanks meet the dominant piece's walls (five of 0.57 to 1.35 m). front has the least: the tall secondary shows there only as a 0.25 m wide strip at the left edge.
- Flat caps: every piece's top is one plane; the dominant piece's tips 6 to 10 degrees. Long vertical edges: right and back each show three or four edges running from the ground to the rim, 0.5 to 1.0 m apart.
- No face reads as part of a sphere: each plane is one flat tone under its paint in every material tile.

## Proportions

- front: 61% of the tile wide and 41% tall, so 3.0 m by 2.0 m. Brief: 3.0 m, 2.0 m.
- right: 53% of the tile wide, so 2.6 m. Brief: 2.6 m.
- The tall secondary is about two thirds of the height (1.35 of 2.0 m), the low secondary under half (0.95 m), the feet a quarter or less (0.5, 0.45 and 0.3 m). Each stands out from the dominant piece by 0.3 to 0.45 m.

## Facing and grounding

- front, right, back, scale: the base is a straight line on the lower edge of the spec's frame, with no gap.
- The brief names no front. The dominant piece stands toward the back right of the bounds (top: its octagon touches the right and upper sides of the outline); the pieces gather on the left and front.

## Topology (clay_wire)

- Every plane boundary is a pair of close parallel lines, the bevel strip, now 0.05 m. They follow the silhouette everywhere.
- Inside each plane, diagonals fan from one corner (front: six across the large wall). They support nothing; they exist because the gate allows no face with more than four sides.
- The stray line above the rock that the previous sheet showed in the clay_wire tiles is not in this one.
- top: the five attached pieces have between 12 and 20 triangles each; the cap has 12.

## Shading (material)

- No plane is darker or lighter than its lighting and its paint explain. L4: no triangle has normals against its winding, and no position above the ground carries two normals.
- UV seams do not show. L4: no texel is claimed by two triangles, the islands use 44.3% of the texture, and the sparsest face has 139 texels per metre.
- No banding. L4: largest unused run of levels 0.

## Materials

- Colour and gradient (brief: `#a1a7a1`, 58% of the light at the top, 27% at the ground). L4: open faces average 0.974 times what the paint formula gives (allowed 1 +/- 0.08); the lowest quarter is 0.662 times as light as the highest, expected 0.629.
- Growth at the base (brief: olive from the ground to about 0.9 m, at the rock's lightness). front, right, back: green from the ground to between a third and a half of the height, with a soft lobed upper edge; every foot is green all over. L4: growth on 99.7% of the surface below 0.36 m and on 0.5% of upright open faces above 1.44 m.
- Growth patches (brief: about 0.2 m, broken, over about 25% of level faces and 40% of upper edges, 50% darker than the rock). top: the cap carries some forty separate dark olive flecks and clusters, 0.05 to 0.4 m across, thicker toward the rim; the bare rock between them is one pale area. L4: cover of level faces 19.9% (allowed 12.5% to 37.5%); 51.8% of the edge zone of upright faces in the top fifth; patches 48.4% darker than the bare rock beside them (0.5 +/- 0.08); growth starts or stops 1.32 times per 0.2 m (at least 0.9).
- Side shade (22% at mid height). L4: 19.4% darker, where 16.8% is due.
- Blotches. right, bevy: two or three soft lighter and darker areas on each wall above the green. L4: spread 0.234 (allowed 0.12 to 0.30), grain 3.0% of it.
- Edge light. L4: 1.231 times open faces. Crevice shadow. back, bevy_back: a dark line where each block meets the wall. L4: 0.699 times open faces.
- Range. L4: brightest channel between 67 and 154 of 255 (allowed 30 to 240).

## Scale

- scale: the rock's top is at about 1.12 times the figure's height. Brief: 2.0 m beside 1.8 m, 1.11. The tall secondary's top is at about 0.75 of the figure's height, the feet at knee height.

## In the engine (bevy, bevy_back)

- The same layers as in Blender. The cap is the lightest part, the green base the middle tone, and the wall away from the sun the darkest.
- Sampled in the `--close` view (9 px squares, linear luminance): bare cap 0.37 to 0.38 (`#a0a4a0`), moss on the cap 0.21 (`#788358`), lit side 0.20 to 0.28, base 0.15 to 0.18 (`#656f4b`). On the second rock the moss on the cap was `#b7c487`, lighter than the rock.
- bevy: the feet and the low block read at once, as separate things in front of the mass. bevy_back: the wall toward the camera is in the sun's shade and its paint is hard to read, as before.
- Soft edges survive, and the base meets the ground with a cast shadow and no gap.

## Values (value maps)

- bevy: three masses. The cap (lightest, broken into about fifteen fragments by the moss), the lit walls with the green base (one mid grey, which the value map does not separate from the ground), and the shaded wall with its cast shadow (dark). The feet on the lit side vanish into the mid grey; the two on the shaded side read as dark notches.
- Benchmark, same view: also three, but the cap is one unbroken light shape with a light rim, and the lit wall carries a dark diagonal groove.
- material_three_quarter: one dark mass on a mid ground; in Blender's light the whole rock is a single value and only the cap's flecks differ.
- The cap's moss is the one place where this rock is many small scattered patches. That is the reading the skill warns is noise.

## At a glance (squint views)

- Ours, bevy: "stump with moss". The eye lands on the dark wall at the right, then on the pale cap. The pieces at the foot blur into the base; the low block at the left survives as a green lump.
- Benchmark: "mossy rounded boulder". The eye lands on the pale cap and follows the groove down the front.
- Ours is recognisably a rock, and the brief's features that survive the blur are the off-centre tilted cap and the widening base. The pieces do not survive it.

## Beside the benchmark

Both in Bevy, same cameras and light (`benchmarks/out/rock_v3_vs_benchmark.png`).

- Mass: about level. Volume share 0.460 against the benchmark's 0.450 (tightest box) and 0.412 (axis-aligned, as ours is measured); crown 0.348 against 0.28 to 0.30.
- Lean: ours has no upright surface (0% within 8 degrees) against the benchmark's 14.5%, but ours leans evenly and inward only. The benchmark bulges: 13% of its side surface overhangs, and its widest level is above the ground. Ours is widest at the ground on every side, which is what makes it a frustum, a stump, where the benchmark is a lump.
- Foot: measured the same way, ours 0.30 and 0.17 m2 on two sides, the benchmark 0.26 and 0.15 m2. Ours is separate blocks; the benchmark's is a low collar that is part of the mass.
- Pieces: ours shows six. The benchmark is one sculpted mass with a groove and a slab; it has no pieces to count.
- Moss: now the same kind of thing. Both have dark flecks on the cap and a wash at the base. Ours has more of it (20% of level faces and half of the upper rim; the benchmark's is perhaps a tenth) and its flecks are more alike in size.
- Colour: within about 10% of the benchmark in every region sampled (brief, Painted shading).
- Cost: 322 triangles and 551 kB, against 342 triangles and a shared 2048 px texture.

## Against each habit of rock-shapes.md

1. Several pieces: met by number (six), and seen in top, back and both bevy tiles. Weak in the squint view.
2. A clear size order: met by number. The order is lopsided: one piece of 10 m2 and five of 0.3 to 1.4 m2. The reference's boulders have secondary pieces a third to a half the size of the dominant one; ours are a seventh at most.
3. Nothing upright: met (0%), but uniformly: every side 9 to 12 degrees. "Pieces in one group lean roughly the same way" is not what this is; nothing leans as a whole.
4. The tallest part off-centre: met (0.187), by the cap's tilt and chamfers more than by where the mass stands.
5. A foot: met on two sides (0.30, 0.17 m2), a third near (0.11).
6. Flat caps: met. One plane per top.
7. Long vertical edges: met; the walls are folded and every piece adds two.
8. Big chamfers: met by number (three), not by eye: the largest is 0.37 m2 beside walls of 1 to 2 m2.

## Seeds 1 to 40

Each seed was taken through the build, painting, L1, the glTF validator, the Bevy profile lint and the Bevy load test, as the gate does it.

- 2 of 40 pass the build: seeds 5 and 37, in 5 and 4 seconds. The other 38 draw their 200 rocks and fail, each with the list of why every rock was refused, in 60 to 90 seconds.
- 2 of those 2 pass every gate. The second generator passed the build on 39 of 40 and every gate on 32; the seven it lost at the load test (UV layout, growth cover, a triangle lit from behind) have no counterpart here: the build now refuses a rock lit from behind or left with a hard edge, the smaller growth patches no longer miss a cap, and UV cover was 0.443 on both.
- So the gap between the build and the gate is closed on this sample, and the generator has become a poor one: one seed in twenty. With the brief's numbers for the foot, the summit and the size steps relaxed a little (0.42 fullness, 0.1 summit, a size ratio of 1.5), 9 of 12 seeds built. What refuses most rocks, in that run's order: the foot on a second side, a ledge in sight from all seven directions, twins among the pieces, the size ratio of 2, and fullness. They pull against each other: a dominant piece big enough for 45% fullness leaves a strip of 0.3 to 0.45 m for everything else.

## Differences from the brief

None found against the brief's numbers: every value in the Numbers table measures as specified above.

Found on the sheet and not caught by any gate:

1. The dominant piece is a regular frustum: eight sides with nearly the same lean. No check measures how much the leans differ, or whether the shape is widest above the ground.
2. The secondary pieces are thin: 0.3 to 0.45 m out from the dominant piece. `pieces.min_dominant_ratio` has a floor (3.0) and no ceiling, so a dominant piece 7.5 times the next passes.
3. The moss on the cap reads as scatter in the value map. `painted.growth_up` allows 12.5% to 37.5% cover for the 25% asked; nothing limits how many separate patches there are.

Caught by number during this work:

1. The second rock, unchanged, passed every gate while having one piece, no foot, no chamfers and 46% of its sides upright. It is now the red case of four checks (`tests/fixtures/rock_single_block.json`).
2. A rock painted with moss as light as the rock, and one with patches three times too large, both passed every gate before `painted.growth_darker` and `painted.growth_patches` existed.
3. Turning a soft edge's normal toward its face to stop it being lit from behind gives that vertex two normals. Four seeds built that way then failed `soft_edges` in the load test. The build now refuses such a rock instead.

For the owner to judge, since no number in the brief settles them:

1. Whether a stump-like dominant piece with small pieces against it is the composed boulder that was asked for. It follows the habits by number; from across a room it is one mass.
2. The three existing numbers that changed (brief, Decisions): the large-plane share 0.75 to 0.6, a ledge against a plane of 0.15 m2, and the soft edge 0.07 to 0.05 m.
3. How much moss: 25% of level faces and 40% of upper edges are the agent's numbers.
