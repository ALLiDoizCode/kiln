# stack_3

Variant 3 of the stack. Everything about it is in the family's brief, `source/stack/brief.md`, except what is here.

## Real-world size

0.5 m wide, 0.44 m deep and 0.32 m tall: a small pile at a path's edge, shin high, 0.18 of a player's height. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Stones

Three.

## Budget

At most 360 triangles: 120 a stone.

## Paint

The family's bands are sized for a stack 0.9 m across. This one is about half that, and its bands are half as wide to match, as the smallest slab's are against its family's.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1, with 296 to 354 triangles. Only seed 3 was painted and taken through the later gates. It was not picked from several. It measures: 334 triangles; 0.265 buried; size steps of the surface shown 2.36 and 1.31; each stone covers 0.61 and 0.59 of the one below; thickness over width 0.25 to 0.26; sunk 0.12 to 0.15; summit 0.307 off the middle.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["stack_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-0.25, -0.22, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.25, 0.22, 0.32]` | Real-world size |
| `max_triangles` | `360` | Budget |
| `overlap.min_count` | `3` | Stones |
| `overlap.max_count` | `3` | Stones |
| `painted_shading.edge_width_m` | `0.02` | Paint: half the family's 0.04 m |
| `painted_shading.crevice_width_m` | `0.06` | Paint: half the family's 0.12 m |
| `painted_shading.blotch_size_m` | `0.1` | Paint: half the family's 0.2 m |
