# standing_stone_1

Variant 1 of the standing stone. Everything about it is in the family's brief, `source/standing_stone/brief.md`, except what is here.

## Real-world size

1.4 m wide, 1.1 m deep and 2.6 m tall: the plain one, half as tall again as a player. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Two: the stone and one foot block.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py standing_stone_1 1 40`), with 136 to 190 triangles; only this one was painted and taken through the later gates. Seed 1 was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["standing_stone_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.7, -0.55, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.7, 0.55, 2.6]` | Real-world size |
| `overlap.min_count` | `2` | Pieces |
| `overlap.max_count` | `2` | Pieces |
