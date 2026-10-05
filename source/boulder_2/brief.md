# boulder_2

Variant 2 of the boulder, the medium one. Everything about it is in the family's brief, `source/boulder/brief.md`, except what is here.

## Real-world size

2.0 m wide, 1.7 m deep and 1.2 m tall. Its height is two thirds of a 1.8 m player: to the chest, cover for a crouching player. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 2.0 m wide: edge light fading out 0.054 m into each plane (one thirty-seventh), and blotches 0.3 m across (one fifth of the width would be wider than the 0.3 m the family's brief allows). A 1024 px texture (the family's brief, Texture size). No crevice shadow: the stone has no inside corner.

## Seed

Seed 8, the agent's choice from the sheet and the owner's to change (seed 2 reads as a cut wedge): `benchmarks/out/boulder_2_candidates.png` shows seeds 1 to 12.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["boulder_2"]` | Parts: one object |
| `seed` | `8` | Seed |
| `bounds_m.min` | `[-1.0, -0.85, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.0, 0.85, 1.2]` | Real-world size |
| `painted_shading.texture_px` | `1024` | Paint: the family's brief, Texture size |
| `painted_shading.edge_width_m` | `0.054` | Paint: one thirty-seventh of the width |
| `painted_shading.blotch_size_m` | `0.3` | Paint: 0.3 m, the most the family's brief allows |
