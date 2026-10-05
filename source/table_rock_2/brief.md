# table_rock_2

Variant 2 of the table rock. Everything about it is in the family's brief, `source/table_rock/brief.md`, except what is here.

## Real-world size

6.4 m wide, 4.2 m deep and 4.2 m tall: the shelter. The cap is at least 3.0 m above the ground, so a wall of the building grid stands under it, and a 3 m foundation fits on its top. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Five: the cap, two necks standing apart along its length (the second the narrower), and one block against the foot of each.

## Under the cap

At least 3.0 m of open air under the cap, and the necks stand at least 0.8 m in from the rim on every side.

## Budget

At most 540 triangles, `crag_1`'s budget: five pieces (family brief, Budget). One 2048 px texture: the cap and two necks are about 80 m2 of surface, and a 1024 px texture half used holds 52 m2 at the 100 texels per metre the conventions ask.

## Seed

Seed 2. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py table_rock_2 1 40`), with 424 to 518 triangles; none needed more than the fourth table rock it drew. Only this one was painted and taken through the later gates. Seed 2 was not picked from several. It keeps the third it draws and measures: 500 triangles; 0.811 of the outline with 3.0 m of open air under it; the necks 0.089 of the outline and 0.99 m in from the rim; 0.686 of the view from above level; 0.073 buried; least size step 1.67.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["table_rock_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-3.2, -2.1, 0.0]` | Real-world size |
| `bounds_m.max` | `[3.2, 2.1, 4.2]` | Real-world size |
| `overlap.min_count` | `5` | Pieces |
| `overlap.max_count` | `5` | Pieces |
| `table.necks` | `2` | Pieces |
| `table.min_clear_m` | `3.0` | Under the cap |
| `table.min_overhang_m` | `0.8` | Under the cap |
| `max_triangles` | `540` | Budget |
| `painted_shading.texture_px` | `2048` | Budget |
