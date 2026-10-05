# standing_stone_2

Variant 2 of the standing stone. Everything about it is in the family's brief, `source/standing_stone/brief.md`, except what is here.

## Real-world size

1.9 m wide, 1.4 m deep and 3.6 m tall: twice a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Three: the stone and two foot blocks.

## Seed

Seed 2. Of seeds 1 to 40 at this size 28 build and pass gate L1, with 204 to 276 triangles; the other 12 fail the build and say why (two foot blocks leave less room: stretched too far to fill the bounds, a block not convex, or planes too close in tilt). Only this one was painted and taken through the later gates. Seed 2 is the first that builds.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["standing_stone_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-0.95, -0.7, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.95, 0.7, 3.6]` | Real-world size |
| `overlap.min_count` | `3` | Pieces |
| `overlap.max_count` | `3` | Pieces |
