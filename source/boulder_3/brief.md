# boulder_3

Variant 3 of the boulder, the large one. Everything about it is in the family's brief, `source/boulder/brief.md`, except what is here.

## Real-world size

3.2 m wide, 2.7 m deep and 1.9 m tall. Its height is 1.06 of a 1.8 m player: just over the head, hiding a standing player. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 3.2 m wide: edge light fading out 0.086 m into each plane (one thirty-seventh), and blotches about 0.64 m across (one fifth). A 1024 px texture (the family's brief, Texture size). No crevice shadow: the stone has no inside corner.

## Seed

Seed 7, the agent's choice from the sheet and the owner's to change: `benchmarks/out/boulder_3_candidates.png` shows seeds 1 to 12.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["boulder_3"]` | Parts: one object |
| `seed` | `7` | Seed |
| `bounds_m.min` | `[-1.6, -1.35, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.6, 1.35, 1.9]` | Real-world size |
| `painted_shading.texture_px` | `1024` | Paint: the family's brief, Texture size |
| `painted_shading.edge_width_m` | `0.086` | Paint: one thirty-seventh of the width |
| `painted_shading.blotch_size_m` | `0.64` | Paint: one fifth of the width |
