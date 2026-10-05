# table_rock_1

Variant 1 of the table rock. Everything about it is in the family's brief, `source/table_rock/brief.md`, except what is here.

## Real-world size

3.6 m wide, 3.0 m deep and 2.9 m tall: the plain one. A 1.8 m player walks under the cap, which is at least 2.0 m above the ground, with 0.2 m over the head; the top is 1.1 m above the player's head and is reached by climbing. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Three: the cap, one neck, and one block against the neck's foot.

## Under the cap

At least 2.0 m of open air under the cap, and the neck stands at least 0.6 m in from the rim on every side: wider than a player's shoulders.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py table_rock_1 1 40`), with 270 to 346 triangles; 30 keep the first table rock they draw and 10 the second. Only this one was painted and taken through the later gates. Seed 1 was not picked from several: it is the first. It measures: 326 triangles; 0.841 of the outline with 2.0 m of open air under it; the neck 0.072 of the outline and 0.93 m in from the rim; 0.590 of the view from above level; 0.065 of the surface buried; size steps 2.91 and 3.99.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["table_rock_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-1.8, -1.5, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.8, 1.5, 2.9]` | Real-world size |
| `overlap.min_count` | `3` | Pieces |
| `overlap.max_count` | `3` | Pieces |
| `table.necks` | `1` | Pieces |
| `table.min_clear_m` | `2.0` | Under the cap |
| `table.min_overhang_m` | `0.6` | Under the cap |
