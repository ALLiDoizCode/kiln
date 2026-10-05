# tree_sapling_1

A broadleaf sapling: growth stage 0.5. Everything about it is in the family's brief, `source/tree/brief.md` (Growth stages, "The sapling has a silhouette of its own"), except what is here.

## Real-world size

2.6 m wide, 1.9 m deep and 3.5 m tall: half of `tree_1`'s height and not quite two players tall, with its two tufts in a row along x. A player's eye (1.7 m) is level with its fork and just under its lower tuft, so it is looked at and across, not walked under. The origin is on the ground at the middle of the foot of the trunk.

## Seed

None yet: the asset does not build. With the recipe as it stands the generator kept none of 36 trees over seeds 1 to 3 (12 each; a build tries 40). Trees refused, by reason, a tree counting once for each: 19 could not be stretched to the bounds (a row of two tufts stands off-centre from the foot); 15 showed too little bark above the fork (0.01 to 0.05 a view, where the generator asks 0.028 from all seven views and the spec 0.02 from six); 13 had too few pieces pointing out of their tuft (0.76 to 0.84; generator 0.84, spec 0.8); 10 had a piece under 0.38 m after the fit; 8 had a lower tuft under 40 pieces (28 to 39), which then counts as strays; 6 were over 1,140 triangles; 5 showed too little or too much sky from one view too many; 4 tapered too little below the fork (0.853 to 0.86 for 0.85).

Three of these look like checks that do not fit a tuft rather than numbers to tune, and none of them was loosened: `foliage.min_pad_pieces` (40 pieces is half a small mature pad; a tuft about 1 m wide carries 28 to 39 at any spacing the budget allows), `foliage.min_pointing_out` (measured from a pad's middle, which a 0.5 m piece on a 1 m tuft often lies across) and `skeleton.min_seen_share` (limbs 7 to 9 cm through beside tufts that hang to the fork).

## Numbers

The rows that are this asset's own. Every other value in `spec.json` is in the family brief's Numbers table.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tree_sapling_1"]` | Parts: one object |
| `seed` | `1` | Seed |
| `growth_stage` | `0.5` | Family brief, Growth stages: sapling |
| `bounds_m.min` | `[-1.2, -0.9, 0.0]` | Real-world size |
| `bounds_m.max` | `[1.4, 1.0, 3.5]` | Real-world size |
| `max_triangles` | `1200` | Family brief, Growth stages: the budget of a sapling |
| `skeleton.fork_m` | `[1.5, 2.1]` | Family brief, Growth stages: a sapling forks at about eye height |
| `skeleton.lean_m` | `[0.08, 0.4]` | Family brief, Growth stages: the mature lean times the stage |
| `skeleton.min_branches` | `2` | Family brief, Growth stages: two tufts, a limb to each |
| `foliage.min_pads` | `2` | Family brief, Growth stages: two tufts |
| `foliage.max_pads` | `2` | Family brief, Growth stages: two tufts |
| `foliage.piece_m` | `[0.35, 0.7]` | Family brief, Growth stages: shorter leaf pieces |
| `foliage.min_pad_flatness` | `1.2` | Family brief, Growth stages: small pads under large leaves |
| `foliage.min_pad_spread` | `1.3` | Family brief, Growth stages: small pads under large leaves |
| `painted_shading.edge_width_m` | `0.015` | Family brief, Growth stages: the mature tree's 3 cm times this stage's girth (0.5) |
| `painted_shading.crevice_width_m` | `0.022` | Family brief, Growth stages: the mature tree's 4.5 cm times this stage's girth (0.5) |
