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

Seed 5, chosen by the owner's agreement from the twelve in `benchmarks/out/spire_1_candidates.png` in place of seed 1, whose ledge block read as a headstone. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_1 1 40`), with 584 to 828 triangles. Seed 5 kept the eighth spire it drew, and passes every gate with no other value of the spec changed. It measures: 656 triangles; 7 pieces, with no block on the ledge; 3 tiers, 2.11, 1.01 and 0.59 m wide, steps 0.48 and 0.59, differing by 1.23 (1.2 asked); the tiers 0.500 and 0.345 of their width off the middle of the one below; leaning 10.5 degrees; standing 1.0 and 0.909 (0.9 asked: the top tier sits at the very edge of the second's cap); ledges 0.408, 0.255 and 0.413 of each tier's level cut; 15 flutes; 0.309 of the surface buried; smallest size step 1.38; 175 texels per metre at 2048 px.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_1"]` | Parts: one object |
| `seed` | `5` | Seed |
| `bounds_m.min` | `[-1.6, -1.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.6, 1.4, 6.0]` | Real-world size |
| `max_triangles` | `960` | Budget |
| `overlap.min_count` | `7` | Pieces |
| `overlap.max_count` | `9` | Pieces |
| `spire.tiers` | `[3, 4]` | Pieces |
| `foot.min_side_m2` | `0.09` | Foot |
