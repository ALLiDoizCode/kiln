# spire_3

Variant 3 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

2.0 m wide, 1.7 m deep and 3.6 m tall: a stub, two players tall. The cap of its base is about 1.6 m up, at a player's eye, so this is the one whose first ledge is seen as a surface. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven or eight, by seed: three tiers, two shoulders, two blocks, and on some seeds a block on the base's ledge.

## Budget

At most 840 triangles: 132 for the base's main mass, 2 x 126 for the tiers above it, 98 and 81 for the shoulders, 2 x 81 for the blocks and 105 for a ledge block: 830.

## Texture

One 1024 px texture, not the family's 2048: about 17 m2 of surface, estimated before building, where a 1024 px texture holds about 42 m2 at 100 texels per metre.

## Foot

The footprint is 3.4 m2; a hundredth of it, 0.03 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 3. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_3 1 40`), with 584 to 774 triangles. Only seed 3 was painted and taken through the later gates; it was not picked from several. It took the twelfth spire it drew and measures: 620 triangles; 3 tiers, 1.33, 0.60 and 0.37 m wide, steps 0.45 and 0.62, differing by 1.39; tiers 0.625 and 0.278 of their width off the middle of the one below; leaning 12.3 degrees; standing 1.0 and 0.993; ledges 0.422, 0.195 and 0.409; 13 flutes; 0.332 buried; smallest size step 1.30; 120 texels per metre at 1024 px.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_3"]` | Parts: one object |
| `seed` | `3` | Seed |
| `bounds_m.min` | `[-1.0, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.0, 0.85, 3.6]` | Real-world size |
| `max_triangles` | `840` | Budget |
| `painted_shading.texture_px` | `1024` | Texture |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `8` | Pieces |
| `spire.tiers` | `[3, 3]` | Pieces |
| `foot.min_side_m2` | `0.03` | Foot |
