# spire_3

Variant 3 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

2.0 m wide, 1.7 m deep and 3.6 m tall: a stub, two players tall. The cap of its base is about 1.6 m up, at a player's eye, so this is the one whose first ledge is seen as a surface. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven: three tiers (the base and two above it), two buttresses and two blocks.

## Budget

At most 720 triangles: 132 for the base, 2 x 126 for the tiers, 4 x 81 for the buttresses and blocks: 708.

## Texture

One 1024 px texture, not the family's 2048: about 17 m2 of surface, estimated before building, where a 1024 px texture holds about 42 m2 at 100 texels per metre.

## Foot

The footprint is 3.4 m2; a hundredth of it, 0.03 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_3 1 40`), with 584 to 678 triangles. Only seed 3 was painted and taken through the later gates; it was not picked from several. It took the second spire it drew and measures: 622 triangles; tiers 1.16, 0.52 and 0.27 m wide, steps 0.45 and 0.52; ledges 0.158, 0.122 and 0.182 of each tier's level cut; 13 flutes; 0.332 of the side surface within 8 degrees of upright; summit 0.124 off the middle; 0.197 of the surface buried; smallest size step 1.40. The sparsest triangle has 151 texels per metre at 1024 px.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.0, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.0, 0.85, 3.6]` | Real-world size |
| `max_triangles` | `720` | Budget |
| `painted_shading.texture_px` | `1024` | Texture |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `7` | Pieces |
| `spire.tiers` | `3` | Pieces |
| `foot.min_side_m2` | `0.03` | Foot |
