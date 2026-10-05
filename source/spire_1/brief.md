# spire_1

Variant 1 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

3.2 m wide, 2.8 m deep and 6.0 m tall: the plain one, two storeys of the building grid and 3.3 players tall. A player's eye is below the base's shoulder; the cap of the base is about 2.7 m up, over the player's head. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Seven to nine, by seed: three or four tiers, two shoulders, two blocks, and on some seeds a block on the base's ledge.

## Budget

At most 960 triangles: 132 for the base's main mass, 3 x 126 for the tiers above it, 98 and 81 for the shoulders, 2 x 81 for the blocks and 105 for a ledge block: 956.

## Texture

The family's 2048 px. A 1024 px texture was asked first, because the first spire_1 measured 202 texels per metre at 2048 px; the reworked one has more surface (shoulders, larger blocks, wider tiers) and gate L4 found 74 texels per metre on its sparsest triangle at 1024 px, where 100 is asked. So it is back at 2048 px.

## Foot

The footprint is 9.0 m2; a hundredth of it, 0.09 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_1 1 40`), with 584 to 828 triangles. Seeds 1 to 12 are in `benchmarks/out/spire_1_candidates.png` for the owner to pick from; seed 1 was not picked from them: it is the first, and not the best of the twelve (a small block stands on its ledge like a headstone). It took the thirty-sixth spire it drew of the forty a seed may draw, so this seed is close to not building. It measures: 698 triangles; 3 tiers, 2.11, 1.36 and 0.62 m wide, steps 0.64 and 0.45, differing by 1.42; each tier 0.191 and 0.511 of its width off the middle of the one below; leaning 8.7 degrees; standing 0.994 and 0.966; ledges 0.168, 0.381 and 0.516 of each tier's level cut; 14 flutes; 0.356 of the surface buried; smallest size step 1.23; 155 texels per metre.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-1.6, -1.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.6, 1.4, 6.0]` | Real-world size |
| `max_triangles` | `960` | Budget |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `9` | Pieces |
| `spire.tiers` | `[3, 4]` | Pieces |
| `foot.min_side_m2` | `0.09` | Foot |
