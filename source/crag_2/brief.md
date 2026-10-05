# crag_2

Variant 2 of the crag. Everything about it is in the family's brief, `source/crag/brief.md`, except what is here.

## Real-world size

5.0 m wide, 4.0 m deep and 4.6 m tall: a ridge end, two and a half players tall and wider than a 3 m foundation. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Eight: five prisms and three blocks.

## Budget

At most 720 triangles: 90 a piece.

## Texture

One 2048 px texture, not the family's 1024: this crag shows about 77 m2 of surface, and at 1024 px its sparsest triangle had 72 texels per metre where `conventions.toml` asks for 100 (a texel of 1 cm seen from 0.5 m, ADR 7).

## Foot

The footprint is 20.0 m2; a hundredth of it, 0.2 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 2. Not tried over a run of seeds: `tools/bl tools/try_seeds.py crag_2 1 40` had not finished its first seed after about fifteen minutes beside two other runs and was stopped, so how many seeds build at this size is not known. Eight pieces are slow to draw: seed 2 took the sixteenth crag it drew. Only this seed was painted and taken through the gates; it was not picked from several.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["crag_2"]` | Parts: one object |
| `seed` | `2` | Seed |
| `bounds_m.min` | `[-2.5, -2.0, 0.0]` | Real-world size |
| `bounds_m.max` | `[2.5, 2.0, 4.6]` | Real-world size |
| `max_triangles` | `720` | Budget |
| `painted_shading.texture_px` | `2048` | Texture |
| `overlap.min_count` | `8` | Pieces |
| `overlap.max_count` | `8` | Pieces |
| `cluster.min_prisms` | `5` | Pieces |
| `foot.min_side_m2` | `0.2` | Foot |
