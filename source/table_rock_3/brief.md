# table_rock_3

Variant 3 of the table rock. Everything about it is in the family's brief, `source/table_rock/brief.md`, except what is here.

## Real-world size

2.4 m wide, 2.0 m deep and 1.5 m tall: a low table. Its top is 0.2 m below a player's eye, so it is seen from above; nobody stands under it. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Three: the cap, one neck, and one block against the neck's foot.

## Under the cap

At least 0.9 m of open air under the cap: room for a fire or a chest, not for a player standing. The neck stands at least 0.35 m in from the rim on every side.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py table_rock_3 1 40`), with 270 to 346 triangles; none needed more than the second table rock it drew. Only this one was painted and taken through the later gates. Seed 3 was not picked from several. It keeps the second it draws and measures: 288 triangles; 0.885 of the outline with 0.9 m of open air under it; the neck 0.067 of the outline and 0.50 m in from the rim; 0.582 of the view from above level; 0.065 buried.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["table_rock_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.2, -1.0, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.2, 1.0, 1.5]` | Real-world size |
| `overlap.min_count` | `3` | Pieces |
| `overlap.max_count` | `3` | Pieces |
| `table.necks` | `1` | Pieces |
| `table.min_clear_m` | `0.9` | Under the cap |
| `table.min_overhang_m` | `0.35` | Under the cap |
