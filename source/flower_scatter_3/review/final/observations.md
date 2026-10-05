# flower_scatter_3, final: observations

Read from `sheet.png` (opened 2026-10-05, after the generator of step 3) and from the gate's own measurements of this build.

## Measured by the gate

- flower_scatter_3 blooms: 4, [0.074, 0.079, 0.082, 0.087] m across, filling [0.264, 0.264, 0.264, 0.264] of their convex hulls
- flower_scatter_3 scatter: 4 blooms [0.055, 0.078, 0.111, 0.128] m up on 4 stems leaning [7, 15, 20, 25] degrees (together 0.37), the nearest two 0.102 m apart; 11 leaves (2.8 to a bloom) reaching 0.026 m, under the lowest bloom's 0.044 m
- 216 triangles; painted parts: 70 open, 1444 edge and 0 crevice samples; edges 1.100 times the open tone; the layout uses 0.594 of the texture under the palette's strip with its baked margin (0.280 of the whole texture under triangles); the sparsest triangle has 379 texels a metre on 128 px.

## Seen

1. Silhouette. material_top: four blooms, each about 0.28 of the scatter's width across; three in a loose bunch and one apart.
2. Heights. material_front: four heights from 0.055 to 0.128 m; the lowest bloom is just above its own leaves.
3. Shading. material_front: two of the four blooms show a brown underside.
4. In the engine. bevy: four yellow spots under the figure's ankle; `--stand 3` in the variants sheet: one yellow speck, found as a spot of colour, with nothing of its shape.
5. Paint. Only 70 open samples: the load test measures the colour on little more than it needs (50).
6. Differences from the brief: at 3 m this variant is a speck (4 above); the brief asks that a flower be found from there, and what is found is the scatter.
