# spire_1

Variant 1 of the stepped spire. Everything about it is in the family's brief, `source/spire/brief.md`, except what is here.

## Real-world size

3.2 m wide, 2.8 m deep and 6.0 m tall: the plain one, two storeys of the building grid and 3.3 players tall. A player's eye is below the base's shoulder; the cap of the base is about 2.7 m up, over the player's head. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Pieces

Eight: three tiers (the base and two above it), three buttresses and two blocks.

## Budget

At most 800 triangles: 132 for the base, 2 x 126 for the tiers, 5 x 81 for the buttresses and blocks: 789.

## Foot

The footprint is 9.0 m2; a hundredth of it, 0.09 m2, is the low near-level surface asked of each of two sides.

## Seed

Seed 1. Of seeds 1 to 40 at this size all 40 build and pass gate L1 (`tools/bl tools/try_seeds.py spire_1 1 40`), with 652 to 764 triangles. Seeds 1 to 12 are in `benchmarks/out/spire_1_candidates.png` for the owner to pick from; seed 1 was not picked from them: it is the first. It took the second spire it drew and measures: 688 triangles; tiers 1.82, 0.86 and 0.45 m wide, steps 0.47 and 0.52; ledges 0.123, 0.131 and 0.220 of each tier's level cut; 14 flutes; 0.392 of the side surface within 8 degrees of upright; summit 0.149 of the half extents off the middle; 0.226 of the surface buried; smallest size step 1.43.

Measured after building, and not acted on: at 2048 px the sparsest triangle has 202 texels per metre, so a 1024 px texture would give about 101 where 100 is asked. The size was set from an estimate of 47 m2 of surface at 0.4 coverage; it shows 41.8 m2 and the packer reached 0.63. The owner may prefer 1024 px and a file a quarter the size.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["spire_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-1.6, -1.4, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.6, 1.4, 6.0]` | Real-world size |
| `max_triangles` | `800` | Budget |
| `overlap.min_count` | `8` | Pieces |
| `overlap.max_count` | `8` | Pieces |
| `spire.tiers` | `3` | Pieces |
| `foot.min_side_m2` | `0.09` | Foot |
