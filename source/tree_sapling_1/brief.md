# tree_sapling_1

A broadleaf sapling: growth stage 0.5. Everything about it is in the family's brief, `source/tree/brief.md` (Growth stages, "The sapling has a silhouette of its own"), except what is here.

## Real-world size

3.1 m wide, 1.9 m deep and 3.5 m tall: half of `tree_1`'s height and not quite two players tall, with its two tufts in a row along x (the family brief gives the sum that makes a row 3.1 m long). A player's eye (1.7 m) is level with its fork and just under its lower tuft, so it is looked at and across, not walked under. The origin is on the ground at the middle of the foot of the trunk.

## Seed

Seed 1, the first tried under the limits in the family brief: the generator keeps its sixth tree. The five before it were refused for sky from the two views along the row (0.20 where the generator asks 0.23), bark seen (under 0.017 from two views), over 1,140 triangles, taper below the fork (0.856 for 0.85), a piece over 0.67 m after the fit, tufts too alike in width (1.36 for 1.4) and a tuft seen into from below (0.14 for 0.125), and one could not be stretched to the depth. It was not picked from several by eye, and no other seed was tried.

As built: 1,046 triangles (bark 406, cores 120, leaf pieces 520), tufts of 100 and 30 pieces, 0.88 of pieces pointing out, bark 0.020 to 0.041 of what is seen above the fork from the seven views. The narrower tuft's 30 pieces would fail a pad's floor of 40; the bark seen would pass the mature tree's 2% at the gate but not the room the generator keeps to it (2.8% from all seven).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tree_sapling_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `growth_stage` | `0.5` | Family brief, Growth stages: sapling |
| `bounds_m.min` | `[-1.45, -0.9, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.65, 1.0, 3.5]` | Real-world size |
| `max_triangles` | `1200` | Family brief, Growth stages: the budget of a sapling |
| `skeleton.fork_m` | `[1.5, 2.1]` | Family brief, Growth stages: a sapling forks at about eye height |
| `skeleton.lean_m` | `[0.08, 0.4]` | Family brief, Growth stages: the mature lean times the stage |
| `skeleton.min_branches` | `2` | Family brief, Growth stages: two tufts, a limb to each |
| `skeleton.min_seen_share` | `0.012` | Family brief, Growth stages, a sapling's own limits: 0.6 of the mature tree's 2% |
| `foliage.min_pads` | `2` | Family brief, Growth stages: two tufts |
| `foliage.max_pads` | `2` | Family brief, Growth stages: two tufts |
| `foliage.min_pad_pieces` | `24` | Family brief, Growth stages, a sapling's own limits: two lobes of twelve pieces |
| `foliage.piece_m` | `[0.35, 0.7]` | Family brief, Growth stages: shorter leaf pieces |
| `foliage.min_pad_flatness` | `1.2` | Family brief, Growth stages: small pads under large leaves |
| `foliage.min_pad_spread` | `1.3` | Family brief, Growth stages: small pads under large leaves |
| `painted_shading.edge_width_m` | `0.015` | Family brief, Growth stages: the mature tree's 3 cm times this stage's girth (0.5) |
| `painted_shading.crevice_width_m` | `0.022` | Family brief, Growth stages: the mature tree's 4.5 cm times this stage's girth (0.5) |
