# tree

A plain broadleaf tree, made by a generator that takes a seed. This is the brief for the family: the generator (`generator.py`, beside this file) and everything its trees share. The deliverable is three variants, each an asset of its own with its own seed and size: `source/tree_1`, `source/tree_2`, `source/tree_3`. Their specs name this folder as their `family`, and `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows a variant's own brief gives.

It is the first tree, and the first asset with foliage in the style of ADR 9 as amended: leaf-shaped geometry on a branch skeleton.

## Purpose

Set dressing on a forested layer's ground, and the thing a forest is made of: many are on screen at once. A player walks under it and round it and stands against the trunk. Nothing climbs it, breaks it or moves it yet, and it does not move in the wind.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 3 to 40 m. Two views decide what it must hold up to:

- **From 3 m**, looking up at it: the trunk, the fork, the underside of the nearest pads and the branches going into them fill the view.
- **From 0.5 m**, against the trunk, looking up: bark fills a third of the view at arm's length, and the rest is the underside of the canopy with the branch skeleton against it.

From further off it is an outline: a trunk, and several rounded pads with sky between them.

## Real-world size

About 7 m tall with a crown 4 to 6 m across: a small street tree, or four players standing on each other's shoulders. The three variants differ in size on purpose, so that a group of them does not have one height:

| Variant | Width (x) | Depth (y) | Height | Character |
| --- | --- | --- | --- | --- |
| `tree_1` | 4.9 m | 4.7 m | 7.0 m | the plain one, the benchmark's size (4.3 by 4.6 by 7.3 m) |
| `tree_2` | 5.5 m | 5.4 m | 6.2 m | lower and wider |
| `tree_3` | 4.3 m | 4.3 m | 7.8 m | taller and narrower |

The origin is on the ground at the middle of the foot of the trunk, so a tree is planted, and turned, about its trunk. The crown is not centred on it: a tree leans, and each variant's bounds say which way.

## Silhouette

What must read, taken from the nature reference (`docs/style/nature-shapes.md`, Broadleaf, and "How they are built"):

1. **A designed trunk.** Five to eight flat sides with a soft edge between each pair, darker than the foliage. It leans: the fork stands 0.15 to 0.8 m to one side of the foot. It tapers: just below the fork it is at most 0.9 of its girth at breast height (1.3 m). At the ground it flares to at least 2 times its breast-height radius, into at least three roots.
2. **A visible branch skeleton.** The trunk forks between 2.0 and 3.5 m up, above a player's head, into at least three limbs, and each tapers: four fifths of the way from the fork to the top of the bark the limbs are at most 0.8 of their thickness one fifth of the way. The skeleton shows: from each level view and from underneath, bark is at least 2% of what is seen of the tree above the fork, in at least six of those seven views.
3. **Three to six separate pads of foliage**, at different heights and of different sizes, each of at least 40 pieces, with clear air between every pair. Sky shows through the canopy: seen from the side, between 20% and 50% of the canopy's outline (the convex hull of its foliage) is sky, from at least five of six directions. A single mass scores 10 to 19% on this measure (the benchmark tree and its four siblings), and a ball scores none.
4. **Leaf-shaped pieces.** Every piece is flat, pointed (its sharpest corner is 60 degrees or less), jagged (its outline has at least one notch) and between 0.35 and 0.9 m long. Pieces lie like shingles, overlapping, pointing out of their pad and downward, so a pad's outline is serrated.
5. **Colour by piece.** Each piece is one flat colour. Pieces differ from their neighbours, and they run from a light yellow-green at the top of a pad to a darker, bluer green underneath.

## Style and colour

ADR 9 as amended: foliage is leaf-shaped geometry, never solid shapes, never leaf cards; no transparency. The tree stands beside the rock (`source/rock`) and is judged beside the benchmark tree.

- **Bark** `m_tree_bark`, `#7a5a44`: a warm mid brown, with painted shading (ADR 10): darker toward the ground (`#b9a8a0` tint at the foot, none at the top), light along the corners between its flat sides, shadow where a branch leaves the trunk and between the roots, and broad soft blotches. No growth is painted on it.
- **Leaf** `m_tree_leaf`, `#a8b846`: the light yellow-green of a piece at the top of a pad. The underside tint `#6f96a6` takes most of the red out, less of the green and least of the blue, which gives the darker, bluer green underneath. Between the two there are 6 shades, and each shade comes in 4 tones up to 16% lighter or darker, so that neighbouring pieces differ. A piece's shade comes from how high it sits within its own pad; its tone is drawn from a fixed shuffle.
- Leaf pieces take their colour from a palette, not from a bake (ADR 11): a strip of swatches along the top of the bark's texture, with all of a piece's UVs on one swatch. The leaf material is two-sided.

Bevy lights the back of a two-sided face with its normal turned round, so the underside of a pad is lit only by the ambient light: dark green under the viewer's light, never black, which is the reference's "deep green underneath". Each piece's normal is part its own and part the direction out of its pad and upward, so a pad is lit as one round mass and its pieces still differ.

## Parts

One object and one mesh per variant, with two materials: bark and leaf. Nothing moves and nothing is swapped. The bark is a closed surface (the trunk and each limb is a closed tube, pushed into its parent); the leaf pieces are open, separate, flat pieces, which is what `open_materials` records.

## Budget

At most 4,000 triangles and two materials per variant, on one 1024 px texture.

The owner proposed at most 6,000, from the benchmark's 6,265, and accepted that leaf-shaped geometry might need more. It needs fewer. The same generator was built at four leaf spacings and looked at under Bevy from the standard view, from 3 m and from 0.5 m (`benchmarks/out/tree_budget_study.png`):

| Spacing between pieces | Triangles | What it shows |
| --- | --- | --- |
| 0.34 m | 2,146 | From 3 m the pads are scattered pieces with the far side of the pad showing between most of them. |
| 0.28 m | 2,822 | Pads hold together from the standard view; from 3 m each has several holes a piece wide. |
| 0.24 m | 3,574 | Pads read as masses from 3 m and from 0.5 m, with a few small gaps. |
| 0.20 m | 4,874 | No gaps; no difference from 0.24 m in the standard view. |

0.24 m is the least at which a pad reads as a mass from 3 m. (Each row is a different draw, because the spacing changes how many random numbers a tree uses; the rows compare density, not one tree at four densities.) At that spacing the three variants are 3,366, 3,432 and 2,864 triangles, of which the bark is 730 to 890. Of the 36 trees drawn while choosing seeds, the largest was 4,062. 4,000 is the ceiling: a seed that draws more fails the gate. A piece costs four triangles: three would lose the notch that makes its edge jagged.

The texture is 1024 px. At 512 px the bark's sparsest triangle has 87 texels per metre and its islands use 33% of the texture, both under the conventions (100 and 40%); at 1024 px they are 214 and 51%. The palette takes a strip 16 px tall along the top. A variant's GLB is about 700 kB, most of it this texture.

## References

- Look: `docs/style/nature-shapes.md` and the previews it was read from (`docs/style/refs/nature-shapes/`, git-ignored): the asset overview (`img11.png`) for the broadleaf trees' outlines, the biome tiles (`img10.jpg`) for pads at close range, and the jungle scene (`img6.jpg`) for foliage seen from underneath.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/CommonTree_1.gltf` (6,265 triangles, 7.3 m tall, leaf cards). A comparison only; nothing from it is used. Its four sibling trees were measured with it for the sky and variant thresholds.

## Out of scope

Wind animation, LODs, collision shapes, a climbable flag, seasonal colour variants, growth stages, other species.

## Numbers

Every value the variants' `spec.json` files share, and the sentence above it comes from. Each variant's own brief gives its `objects`, `seed`, `bounds_m` and `variants.siblings`. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"tree"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm, far below anything seen |
| `max_triangles` | `4000` | Budget |
| `materials.m_tree_bark` | `"#7a5a44"` | Style and colour: bark |
| `materials.m_tree_leaf` | `"#a8b846"` | Style and colour: leaf, the colour at the top of a pad |
| `painted_shading.texture_px` | `1024` | Budget: 512 px gives the bark 87 texels per metre, under the conventions' 100 |
| `painted_shading.base_tint` | `"#b9a8a0"` | Style and colour: bark darker toward the ground |
| `painted_shading.top_tint` | `"#ffffff"` | Style and colour: no tint at the top |
| `painted_shading.edge_light` | `0.2` | Style and colour: light along the corners; less than the rock's 0.3, because on a limb every point is near a corner |
| `painted_shading.edge_width_m` | `0.03` | A trunk side is about 0.2 m wide; the light is a seventh of it |
| `painted_shading.crevice_shadow` | `0.6` | Style and colour: shadow where a branch leaves and between roots |
| `painted_shading.crevice_width_m` | `0.06` | A band a few centimetres wide round each junction; wider, and whole thin limbs count as crevice |
| `painted_shading.blotch` | `0.1` | Style and colour: broad soft blotches; a little under the rock's 0.12 |
| `painted_shading.blotch_size_m` | `0.4` | Two blotches across a trunk side's height at eye level |
| `painted_shading.hidden_underside` | `true` | The foot of the trunk stands on the ground |
| `skeleton.material` | `"m_tree_bark"` | Parts |
| `skeleton.min_sides` | `5` | Silhouette 1: five to eight flat sides |
| `skeleton.max_sides` | `8` | Silhouette 1 |
| `skeleton.min_flare` | `2.0` | Silhouette 1: flares to at least 2 times its radius |
| `skeleton.min_roots` | `3` | Silhouette 1: at least three roots |
| `skeleton.lean_m` | `[0.15, 0.8]` | Silhouette 1: the fork stands to one side of the foot |
| `skeleton.fork_m` | `[2.0, 3.5]` | Silhouette 2: forks above a player's head |
| `skeleton.max_taper` | `0.9` | Silhouette 1: thinner below the fork than at breast height |
| `skeleton.min_branches` | `3` | Silhouette 2: at least three limbs |
| `skeleton.max_branch_taper` | `0.8` | Silhouette 2: limbs taper |
| `skeleton.min_seen_share` | `0.02` | Silhouette 2: bark is 2% of what is seen above the fork |
| `skeleton.min_seen_views` | `6` | Silhouette 2: in six of seven views |
| `foliage.material` | `"m_tree_leaf"` | Parts |
| `foliage.pad_gap_m` | `0.06` | Silhouette 3: clear air between pads, measured on a 6 cm grid |
| `foliage.min_pads` | `3` | Silhouette 3 |
| `foliage.max_pads` | `6` | Silhouette 3 |
| `foliage.min_pad_pieces` | `40` | Silhouette 3: a pad is at least 40 pieces |
| `foliage.piece_m` | `[0.35, 0.9]` | Silhouette 4: piece length |
| `foliage.min_pointing_out` | `0.8` | Silhouette 4: pieces point out of their pad |
| `foliage.min_pointing_down` | `0.7` | Silhouette 4: and downward |
| `foliage.sky_share` | `[0.2, 0.5]` | Silhouette 3: sky through the canopy |
| `foliage.min_sky_views` | `5` | Silhouette 3: from five of six directions |
| `foliage.under_tint` | `"#6f96a6"` | Style and colour: darker and bluer underneath |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself at the top |
| `foliage.shades` | `6` | Style and colour |
| `foliage.tones` | `4` | Style and colour |
| `foliage.variation` | `0.16` | Style and colour: tones up to 16% lighter or darker |
| `soft_edges` | `true` | Silhouette 1: soft edges between the trunk's sides |
| `watertight` | `true` | Parts: the bark is a closed surface |
| `open_materials` | `["m_tree_leaf"]` | Parts: leaf pieces are open and separate |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs; no tangents |
| `variants.min_difference` | `0.3` | Decisions: how far two variants' outlines must differ |

## Decisions

**Decided by the owner** on 2026-10-04, each by accepting a recommendation:

- **Subject**: a plain broadleaf tree about 7 m tall. It is chosen because it has a direct benchmark; trees specific to the pit come after it.
- **Form**: a generator that takes a seed, with three variants as the deliverable.
- **Foliage**: leaf-shaped geometry in flat colour, on a visible branch skeleton, in several separate pads with sky between them (ADR 9 as amended). No leaf cards, no transparency.
- **Surface**: painted shading (ADR 10).
- **Budget**: proposed as at most 6,000 triangles and two materials, from the benchmark tree's 6,265, with more accepted if leaf-shaped geometry needed it; the brief was to state the number it settles on and why.
- **Judgement**: our tree and the benchmark tree side by side in Bevy on one sheet. The owner approves when ours is not clearly worse.
- **Reference for the look**: the nature pack described in `docs/style/nature-shapes.md`.
- **Out of scope**: wind, LODs, collision, seasonal variants, growth stages.

**Proposed by the agent**, and open to change at review:

- **Three assets, one generator.** Each variant is an asset (`tree_1`, `tree_2`, `tree_3`) with its own spec, build script, GLB and contact sheet, because the pipeline's unit is one asset, one GLB, and the game places trees one at a time. The generator and this brief live here, in `source/tree`, which is not an asset and has no spec. A variant's spec carries its `seed`.
- **The skeleton is our own generator, not Sapling Tree Gen.** Sapling ran headless from its unpacked folder, gave the same mesh for the same seed in two separate runs, and came down to 648 triangles with low curve and bevel resolution. It was not used because its limbs are round curves with four or eight sides (not five to eight flat sides with soft edges), it has no roots, its height and spread follow from about a hundred parameters instead of from the spec's bounds, and the pads have to be placed where its branches happen to end. The generator here places the pads first, inside the bounds, and grows a limb to each. It is about 590 lines and needs no download, and draws a tree in 0.05 s.
- **The budget is 4,000 triangles**, not 6,000 (Budget).
- **Leaf colour is a palette strip in the bark's texture** (ADR 11), not a bake and not vertex colours.
- **A pad is a shell, open underneath.** Pieces cover the top and sides of a flattened, lumpy ellipsoid and stop short of its underside, so the limb that carries it and its twigs show from below. The reference's pads appear to have a solid faceted core under their leaves; ADR 9 rules out solid shapes, and a shell needs no core. The owner should know the reference probably does it the cheaper way.
- **Sizes**: the three variants' bounds; the origin at the foot of the trunk.
- **Every number in the Numbers table** not named in the owner's list. Where each threshold came from:
  - `foliage.sky_share`: the benchmark tree and its four siblings, each one mass of leaf cards, score 0.10 to 0.19 from the six directions. The floor is set just above that, at 0.2; the three variants score 0.20 to 0.39. The ceiling of 0.5 is half the outline: more sky than foliage is a bare tree.
  - `variants.min_difference`: between the benchmark pack's three trees of this height (`CommonTree_1`, `_2`, `_5`), outlines differ by 0.19, 0.27 and 0.30. 0.3 asks our variants to differ at least as much as its most different pair.
  - `foliage.piece_m`: the benchmark's leaf cards are 0.85 to 2.4 m long, each showing a cluster of many leaves, so 0.9 m is where a piece stops being a leaf and becomes a card. 0.35 m is a piece that still covers a degree of the view at 20 m.
  - `skeleton.*`: the benchmark's bark is not a closed surface and could not be sliced, so these come from the reference's words (five to eight sides, flares into roots, tapers, leans) and from ADR 7's player height for the fork. `min_seen_share` 0.02 is what the benchmark shows of its own branches at best (0.00 to 0.05); the three variants show 0.02 to 0.10.
  - Leaf, bark and tint colours: chosen by eye against the reference's previews under the Bevy viewer's light. They are the first thing to change at review.
- **Seams.** The generator marks seams on the bark (round every ring, and once along each stretch of a limb) and `tools/paint.py` unwraps along them. Unwrapped by angle, as the rock is, a limb comes out as strips as long as the trunk and the bark used 10% of the texture.
- **The gate refuses, not the generator.** A seed draws trees until one fills the bounds and its pads come out separate; whether that tree meets the rest of this brief is the gate's to say, by check id. Of seeds 1 to 12, 11 pass at `tree_1`'s size, 5 at `tree_2`'s and 7 at `tree_3`'s. The rock's generator instead redraws until the brief is met; doing the same here would add the gate's measurements (about 3 s) to every draw.
- **Seeds**: see each variant's brief. `tree_2` passes three checks by small margins (fork at 2.1 m, taper 0.87, bark seen 0.020 from one view); it is the variant to look at first.

Not measured, and judged on the contact sheet: that a pad's outline is serrated, and that pads are of visibly different sizes.
