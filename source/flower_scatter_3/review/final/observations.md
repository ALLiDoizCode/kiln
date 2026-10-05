# flower_scatter_3, final: observations

From `benchmarks/out/flower_scatter_variants.png` and, for the first variant, `benchmarks/out/flower_scatter_1_candidates.png`; `sheet.png` was rendered and passed the image lint but was not opened. Numbers not read off a tile are the gate's (the L1 log, the L4 report). The gate stops at L4 on `uv.coverage` (see 11); the tiles after it were made with the gate's own commands. The aids of `tools/review_aids.py` were not made.

1. **Silhouette.** standard, back: 3 thin stems leaning different ways, each with a yellow point on its end and two or three small leaves at its foot. `--stand 0.5`, `--stand 1`: yellow specks a few pixels across over thin green marks and their shadows. `--stand 3`: almost nothing: a faint green-yellow smudge.
2. **Proportions.** 3 blooms 0.051 to 0.058 m across (brief 0.03 to 0.07), their middles 0.08 to 0.14 m up; stems lean 13 to 24 degrees, together 0.15 (brief at most 0.7); the nearest two blooms are 0.164 m apart (brief at least 0.04); 9 leaves (3.0 to a flower) reaching 0.039 m, under the lowest bloom's 0.065 m. A bloom fills 0.519 of its convex hull (brief at most 0.6).
3. **Facing and grounding.** No front. Every stem starts on the ground.
4. **Topology.** A bloom is 20 triangles, a stem 3, a leaf 4; 105 (budget 180) triangles.
5. **Shading.** Nothing black; a stem seen edge on is a hairline.
6. **Materials.** Yellow blooms; stems and leaves in light and darker green.
7. **Scale.** standard: 0.15 m tall, a twelfth of the figure's height, and 0.3 m across.
8. **In the engine.** The shadows of the leaves on the ground are larger and darker than the flowers are bright.
9. **Values.** Not made as value maps. As rendered: no mass at all, specks.
10. **At a glance.** "A few weeds", "sprigs": the colour is too small an area to be an accent. The benchmark's group, at 2 m tall, is "tulips": broad leaves and flowers the size of a hand.
11. **Differences from the brief.**
   - `uv.coverage` fails at L4: the blooms' islands use 0.079 of the texture and the conventions want 0.4. The texture holds only the blooms under a palette strip; left failing, as instructed.
   - "An accent of colour": not reached. A 5 cm star seen from 1.7 m up is a few pixels, and from 3 m the scatter cannot be found. The brief's own size for a flower (3 to 7 cm) is what makes it so; more flowers, or flowers in tight groups of three, would carry more colour.
   - A bloom is a flat five-pointed star with nothing in its middle; it does not turn toward the viewer.
