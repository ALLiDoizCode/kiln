# boulder_1

Variant 1 of the boulder, the small one. Everything about it is in the family's brief, `source/boulder/brief.md`, except what is here.

## Real-world size

1.2 m wide, 1.0 m deep and 0.7 m tall. Its height is 0.39 of a 1.8 m player: to mid thigh, a stone to sit on or step up on. The lowest point is at z = 0 and the origin is on the ground under the centre of the bounding box.

## Paint

The family's brief gives each painted band as a share of the stone's width (Painted shading). At 1.2 m wide: edge light fading out 0.032 m into each plane (one thirty-seventh), and blotches about 0.24 m across (one fifth). A 512 px texture (the family's brief, Texture size). No crevice shadow: the stone has no inside corner.

## Seed

Seed 1, the agent's placeholder and the owner's to choose: `benchmarks/out/boulder_1_candidates.png` shows seeds 1 to 12.

## Numbers

The rows that are this variant's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["boulder_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `bounds_m.min` | `[-0.6, -0.5, 0.0]` | Real-world size |
| `bounds_m.max` | `[0.6, 0.5, 0.7]` | Real-world size |
| `painted_shading.texture_px` | `512` | Paint: the family's brief, Texture size |
| `painted_shading.edge_width_m` | `0.032` | Paint: one thirty-seventh of the width |
| `painted_shading.blotch_size_m` | `0.24` | Paint: one fifth of the width |
