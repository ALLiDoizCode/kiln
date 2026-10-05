# conifer

The second species of the tree family: the brief for `species/conifer.toml`, the recipe beside this file. The family brief (`source/tree/brief.md`) says what every tree shares: the purpose, the viewing distances, the trunk and its foot, the bark and its grain, leaf pieces over dark cores, the palette, the seasons rule, the parts and the texture. This file says only what a conifer changes, and gives the rows of the Numbers table that are a conifer's own. It was written before any conifer was built.

**Where a species' brief lives, and why.** Beside its recipe, as `species/<name>.md`. The family brief is the generator's and the broadleaf's at once, because the broadleaf was the only species when it was written; a second species written into it would double its length and leave no one place to read what a conifer is. `tools/lint_spec.py` reads a spec's numbers from the family brief, then from its species' brief where there is one, then from the asset's own, each overriding the one before. The broadleaf's rows were left where they are, in the family brief, which so stays the default a species departs from: moving them would touch nine assets for no change in what is built.

## State

**One mature conifer built and through its gates: `conifer_1`** (seed 7, its 7th tree; 9.5 m, five tiers and a top, 4,892 triangles, a 1024 px texture, 1.3 MB). Of seeds 1 to 12 at its size, each given 40 trees, the generator keeps a tree from nine (not 1, 4 or 9); before the form was changed (Decisions: the top, the hub, the under view) it kept one from three. A seed that keeps a tree takes 7 to 184 seconds to find it (half of them under 50), and one that keeps nothing about four minutes to say so. Trees are refused, in this order, for the budget (over 5,225: half of them), a tier seen into from below, no sky in the view from under the tree, bark seen from the level views, and sky from the level views. No second or third seed, no growth stages and no winter are written. Open, from its contact sheet (`source/conifer_1/review/final/observations.md`): from 1 m under the tree only the lowest tier is seen; from above eye height the tiers merge into one mass; and its pieces are the broadleaf's leaves, not sprays of needles.

## What it is

`docs/style/nature-shapes.md`: "a straight trunk with tiers of drooping branches, widest at the bottom". One **leader**, the trunk carried on to the tip, with **tiers** of **boughs** round it: each tier a whorl of three to seven boughs leaving the leader at about one height, each bough hanging lower the further out it goes, the tiers narrowing from the lowest to a pointed top. The outline is a cone, and an uneven one.

It must not be a stack of identical cones or a diagram of a Christmas tree (the owner's refusals of constructed rocks this week apply). So, in every tree: the tiers differ in width by more than their place in the cone asks, and in how steeply they droop; the boughs of one tier are of unequal length, so a tier seen from below is a ragged star and not a disc; the tiers are not evenly spaced, and between some of them the leader shows bare; a tier has as few as three boughs, which leaves a side of the leader open; and the top stands a little to one side of the foot.

## Viewing

First person, from 0.5 m (ADR 7), under and beside the tree.

- **Looking up the trunk from 1 m beside it**: the leader runs straight up the middle of the picture to a point, and each tier is a star of boughs round it, the lowest largest and each above it smaller and nearer the middle, like rings seen up a well. The boughs are bark spokes running out under their foliage; the foliage above each spoke is the dark underside of a bough, with a fringe of pointed pieces round it against the sky. Sky shows between the boughs of a tier and between one tier's fringe and the next. This is the view a conifer is for, and the one a broadleaf's checks from below were written to protect.
- **From 0.5 m against the bark**: the same trunk as a broadleaf's, bark with grain filling half the view, and above it the first whorl about a metre overhead, its boughs hanging down toward the eye to about head height at their tips.
- **From 3 m**: the bare trunk to above head height, then the first two tiers as drooping skirts with the trunk seen between them.
- **From 20 m and more**: a ragged cone, widest in its lowest two tiers, with notches between tiers down each side and a point at the top, off true.

## Size

Taller and narrower than the broadleaf, so a mixed wood has two heights: 8 to 11 m tall and 3.6 to 5 m across. The benchmark's five pines (below) are 7.3 to 10.2 m tall and 3.6 to 6.4 m across.

| Variant | Width (x) | Depth (y) | Height | Character |
| --- | --- | --- | --- | --- |
| `conifer_1` | 4.4 m | 4.2 m | 9.5 m | the plain one |
| `conifer_2` | 5.0 m | 4.8 m | 8.4 m | lower and wider |
| `conifer_3` | 3.8 m | 3.9 m | 10.6 m | taller and narrower |

## What the benchmark's pines measure

`benchmarks/quaternius-stylized-nature/glTF/Pine_1` to `Pine_5`, read with a scratch script (bounds, triangles, and the widest radius of foliage in each 24th of the height). A comparison only; nothing from them is used.

| | Triangles | Size (m) | Lowest foliage | Top 24th over the widest 24th | Widest band (of the crown's) | Tip off the foot |
| --- | --- | --- | --- | --- | --- | --- |
| `Pine_1` | 3,947 | 4.9 x 4.5 x 7.3 | 2.16 m | 0.29 | 1st of 17 | 0.38 m |
| `Pine_2` | 3,648 | 5.7 x 5.2 x 7.4 | 1.12 m | 0.15 | 2nd of 21 | 0.34 m |
| `Pine_3` | 4,964 | 3.6 x 4.0 x 7.4 | 3.19 m | 0.25 | 2nd of 14 | 0.44 m |
| `Pine_4` | 3,370 | 5.8 x 5.4 x 10.2 | 2.44 m | 0.26 | 2nd of 19 | 0.50 m |
| `Pine_5` | 1,646 | 6.4 x 6.2 x 8.7 | 1.45 m | 0.41 | 3rd of 20 | 1.26 m |

Their profiles rise and fall four to six times between the lowest foliage and the tip: five or six tiers, by this crude count.

## Silhouette

What must read, beside the family brief's Silhouette, whose items 1 (a designed trunk), 4 (leaf-shaped pieces), 5 (colour by piece), 6 (bark at arm's length), 7 (foliage from below) and 8 (limbs that stand out, no glare) are asked of a conifer as they are written, a tier standing where they say pad. Items 2 and 3 are the broadleaf's; a conifer's are:

2. **One leader, straight, to the tip.** The trunk does not fork: it runs on as the leader through every tier. Its lowest whorl leaves it between 2.0 and 3.5 m up, above a player's head, as a broadleaf's fork does (the checks find a fork as the lowest height at which a slice shows two limbs, and a whorl is that). It does not lean as a broadleaf does: at the lowest whorl it stands no more than 0.2 m to one side of its foot. From foot to tip its middle is never more than 0.25 m from the straight line between them. And it is off true: the tip stands 0.1 to 0.6 m to one side of the foot.
3. **Four to eight tiers and a top**, each a separate mass of foliage with clear air above and below it, found as a pad is (`foliage.pad_gap_m`), so five to nine in all. The number is what the height holds: the tiers stand between the lowest whorl (3.0 to 3.4 m, so that its wood, which hangs, is still overhead) and the top's own whorl about 1.1 m under the tip, and a tier with its skirt and clear air over it takes 0.65 to 0.95 m, less the higher and narrower it is. That is 3.9 to 5.4 m and four to seven tiers for a tree 8.4 to 9.5 m tall, and up to eight at 10.6 m. (First written as five to eight tiers before anything was drawn; the arithmetic was not done then.)
   - **A tier is a whorl of three to seven boughs**, each a lobe with its own dark core; in every tier the widest is at least 1.2 times the narrowest (boughs of unequal length).
   - **Tiers narrow upward.** The widest is the lowest or the one above it; at no fewer than three quarters of the steps from one tier to the next above, the upper is the narrower (not all of them: a tree whose every tier is narrower by the same step is the diagram); and the top is at most 0.4 of the widest.
   - **Tiers droop.** In every tier below the top, foliage further from the leader hangs lower: at least 0.15 m lower per metre out.
   - **Every tier below the top is wider than tall** (at least 1.3 times, the family's number). The top is not: it is the point.
   - **A pointed top.** The highest half metre of foliage is no more than 0.9 m across.
   - Sky shows between tiers and between the boughs of a tier, and bark shows above the lowest whorl, by the family's numbers.

## The family's checks, for a conifer

Decided here, before a build; the report of the first build says what each measured.

| Check | For a conifer | Why |
| --- | --- | --- |
| `trunk_sides`, `roots`, `roots_apart`, `roots_curve`, `trunk_tapers`, the bark view (L4c), texels | As they are | The trunk, its foot and its bark are the family's |
| `fork` | As it is, 2.0 to 3.5 m | The lowest whorl is what the slices find; it is overhead for the same reason |
| `lean` | Its own number: 0.0 to 0.2 m | A leader stands straight where a broadleaf's trunk leans; `leader_straight` says the rest |
| `branches`, `limbs_bend` | As they are | A whorl shows the leader and its boughs in one slice; a bough is a limb and may not show an elbow |
| `branches_taper` | Measured on the leader | The check is for limbs that thin toward their ends. It takes the mean thickness of whatever a slice cuts one fifth and four fifths of the way up, which on a forked tree is its limbs; on a leader with whorls it is the leader and however many boughs the slice happens to pass through, and the number turns on that (0.45 to 1.09 on one recipe). A conifer's limb above the lowest whorl is its leader, so the leader's own thickness is compared, by the family's number. The leader is the loop that carries on from the trunk, followed up slice by slice; it is not the thickest loop in a slice, which near a whorl is a bough cut on the slant (first written as the thickest, and then a leader 0.14 m thick from whorl to tip measured 0.70: Decisions) |
| `branches_seen` | The views that look down are not counted; 2% from four of the five that are | Bark showing between tiers is what "gaps where the trunk shows" asks. Tiers cover the leader from above as tiles cover a roof: a view from above the tree's own height looks onto the upper faces of drooping boughs and cannot see the leader under them, whatever the gaps between tiers, and no player sees a tree from there (ADR 7: the eye is 1.7 m up). So the two three-quarter views, which look down, are left out for a tree of tiers, and the family's rule (every view but one) is asked of the four level views and the one from below. First written as six of seven; see Decisions |
| `pads` | Its own numbers: 5 to 9, of at least 24 pieces | A tier is found as a pad is. The top is a tuft the size of a sapling's, and the sapling's floor and reason are its own: two lobes of twelve pieces |
| `cores`, `lobes_differ` | `lobes` 3 to 7; the ratio as it is | A bough is a lobe |
| `pads_wide` | As it is, of every tier below the top | The top is asked to be pointed (`top_pointed`), which is the opposite |
| `pads_differ` | As it is | True of any cone; `tiers_narrow` is what asks for the cone |
| `leaves_point_out`, `leaf_size`, `leaf_shape`, `sky`, `core_hidden`, `under_rim`, L4e | As they are | Pieces point out from the leader and down; the rest are about pieces, cores and what shows |
| `under_closed` | Each tier looked up at alone; and a piece met from behind, more than 0.3 m in from the tier's edge, is the inside of the tier | The defect is the same: an eye under a tier sees up through it, to the backs of the pieces lying on top or to the sky. A pad's measure of it (a piece met 0.6 m above the underside) cannot find it in a bough 0.3 m thick, and the tiers below hide a tier from straight under the tree, where a player sees it at a slant. The edge is the tier's outline with its small holes closed: its fringe overhangs there and is asked for by `under_rim` |
| `variants.differ` | As it is, 0.3 | The three differ in height and width on purpose |

New, because nothing asked for what makes a conifer one: `tiers_narrow`, `tiers_droop`, `top_pointed`, `leader_straight` (the `tiers` block of the spec).

## Colour and seasons

- **Leaf** `m_tree_leaf`, `#8fb65e`: a bluer, less yellow green than the broadleaf's `#a8b846`, at the top of a tier. Underside tint `#a4d6e6`, a little lighter than the broadleaf's `#9ad0e6`: the leaf colour is darker, and Silhouette 8 asks the underside to stay lighter than the limbs seen against it; with this tint the underside's lightness (0.25) is the broadleaf's. Core tint `#71a9b9`, the family's.
- **Evergreen.** Autumn does not turn it; there is no autumn conifer. **Winter is snow on the boughs**, done as the broadleaf's is: the winter palette on the same mesh (`#d8dcde`, underside `#6f9f7b`, core `#51755c`), white on top of each tier through to dark green underneath.

## Budget

At most 5,500 triangles for a mature conifer, on the family's 1024 px texture (Decisions). Estimated before the build: about 29 boughs in six tiers and a top; bark about 1,050 (the trunk 420, boughs of four sides in the lowest two tiers and three above, 630), cores about 600 (20 a bough), leaf pieces about 3,300 (the tiers' upper surface, about 31 m2, and about 80 m of rim). That is about 4,950; the ceiling leaves a tenth over it and is under the 6,000 the owner first proposed for a tree. The benchmark's pines are 1,646 to 4,964.

## Growth stages

As the family's: `growth_stage` is the height over a mature tree's, 8 to 11 m.

| Stage | `growth_stage` | Height | Tiers and top | Lowest whorl | Triangles, at most |
| --- | --- | --- | --- | --- | --- |
| Sapling | 0.5 | 4.0 to 5.5 m | 4 or 5 | 1.5 to 2.1 m | 2,200 |
| Young | 0.8 | 6.4 to 8.8 m | 5 to 7 | 1.8 to 3.0 m | 4,000 |
| Mature | 1.0 | 8 to 11 m | 6 to 9 | 2.0 to 3.5 m | 5,500 |
| Old | 1.25 | 10 to 13.75 m | 8 to 11 | 2.5 to 4.5 m | 8,000 |

The lowest whorl follows the broadleaf's fork at each stage, for its reasons (a sapling's at eye height, every other overhead). Budgets follow the tiers' surface, which goes as the number of tiers times the square of the width: young 0.7, sapling 0.35, old 1.45 of the mature 5,500, rounded. They are estimates.

## Numbers

The rows that are a conifer's own; every other value is the family brief's. Each asset's brief gives its `objects`, `seed`, `bounds_m` and `variants`.

| Spec key | Value | From |
| --- | --- | --- |
| `species` | `"conifer"` | The recipe `species/conifer.toml` |
| `max_triangles` | `5500` | Budget |
| `painted_shading.texture_px` | `1024` | Budget: the texture, the family's. It was 2048 px under the painter's first packing; see Decisions |
| `materials.m_tree_leaf` | `"#8fb65e"` | Colour: the top of a tier |
| `skeleton.lean_m` | `[0.0, 0.2]` | Silhouette 2: the leader does not lean at its lowest whorl |
| `skeleton.min_seen_views` | `4` | The family's checks, `branches_seen`: every view counted but one, of the five that do not look down |
| `foliage.min_pads` | `5` | Silhouette 3: four tiers and a top |
| `foliage.max_pads` | `9` | Silhouette 3: eight tiers and a top |
| `foliage.min_pad_pieces` | `24` | The family's checks: the top is a tuft |
| `foliage.under_tint` | `"#a4d6e6"` | Colour: the underside |
| `foliage.lobes` | `[3, 7]` | Silhouette 3: three to seven boughs in a whorl |
| `tiers.widest_among_lowest` | `2` | Silhouette 3: the widest tier is the lowest or the next. The benchmark's widest band is the 1st to 3rd of 14 to 21 |
| `tiers.min_narrowing` | `0.75` | Silhouette 3: the share of steps upward at which the upper tier is narrower |
| `tiers.max_top_share` | `0.4` | Silhouette 3: the top over the widest. The benchmark's top 24th over its widest is 0.15 to 0.41 |
| `tiers.min_droop` | `0.15` | Silhouette 3: metres lower per metre out from the leader |
| `tiers.max_tip_width_m` | `0.9` | Silhouette 3: the highest half metre of foliage |
| `tiers.max_leader_bow_m` | `0.25` | Silhouette 2: the leader's middle from the line foot to tip |
| `tiers.tip_off_m` | `[0.1, 0.6]` | Silhouette 2: off true. The benchmark's tips stand 0.34 to 0.50 m off (one 1.26 m) |

## Decisions

All the agent's, and open to change at review.

- **A tier is a second crown form in the generator, beside the pad** (code), read from the recipe's `[crown]`, `[tiers]`, `[boughs]` and `[top]` tables (data). The trunk and its foot, the bark's grain and seams, the leaf piece, the core, the fit to the bounds, the keep-or-redraw loop and the palette are the broadleaf's code, unchanged.
- **A tier is measured as a pad**, so the family's foliage checks run on a conifer; what a pad's checks cannot say of a tier is in the `tiers` block.
- **Invented, not measured**: `tiers.min_narrowing` 0.75, `tiers.min_droop` 0.15, `tiers.max_tip_width_m` 0.9 (the benchmark's leaf cards are 1.0 to 1.7 m across in their top 24th: ours asks for a sharper point than theirs), `tiers.max_leader_bow_m` 0.25, the lean of 0.2 m, the lower end of `tip_off_m`, the budgets, the colours.
- **`branches_seen` does not count the views that look down on a tree of tiers, and asks four of the remaining five.** The brief first said six of seven, as the family's. The first conifers drawn showed bark as 2.7 to 6.7% of what is seen from the level views, 2.2 to 4.0% from below and 1.0 to 2.4% from the two views that look down. The reason in the table is geometry and holds without a build, but a build is what pointed at it; the check was changed for every tree with tiers, with a case, and no spec value was moved to pass. **The owner should confirm it.**
- **`branches_taper` measures the leader on a tree of tiers**, for the reason in the table; a case holds it to a leader that does not thin (`stout_leader`: 0.14 m from whorl to tip measures 0.94 against 0.8; `conifer_1` measures 0.48). The case was not caught while the check took the thickest loop of a slice: one fifth of the way up that was a bough.
- **`under_closed` on a tier is held by a case** (`no_cores`: with every plate gone five of `conifer_1`'s six tiers measure 0.22 to 0.27 against 0.15, and with them 0.10 to 0.12). It was not caught while the interior was shrunk from an outline with the tier's small holes in it: the more open a tier, the less interior it had left to be looked at.
- **The texture is 1024 px, the family's.** The brief first kept 1024 px; after the first export it was changed to 2048 px, because under the painter's first packing the surface below 2.5 m could only just be given its 250 texels per metre and the sparsest triangle above it then had 90 where the conventions ask 100. The painter now packs islands by their outlines: at 1024 px `conifer_1` has 254 texels per metre below 2.5 m and 158 at its sparsest, and the file is 1.3 MB where it was 3.9 MB at 2048 px. Changed back after a build, on that measurement.
- **The form was changed so that most seeds keep a tree** (nine of twelve where three did), with no limit or margin moved. What refused the trees of twelve seeds, and what was changed for each:
  - *A tier seen into from below* (three trees in four, and in most of them the top alone, which measured 0.16 against 0.125). The top's spire is slimmer (0.12 to 0.15 m where it was 0.17 to 0.22) and its whorl narrower (0.15 to 0.2 of the widest tier, from 0.24 to 0.3): the pieces hanging round a stout spire over a wide whorl were seen from behind from under it. A whorl of short boughs has one plate more, the **hub**, round the leader, where the slits between its boughs are narrower than a piece. And a narrow tier's skirt is closer set (`skirt.tight`).
  - *The top wider than 0.37 of the widest tier* (one tree in three): the narrower whorl.
  - *Sky over 0.46 of the outline from the level views* (four in ten; the typical tree had 0.44): a bough's foliage stands 0.26 m above its middle line, from 0.2. A tier seen from the side is a band, and the sky is what is left between bands.
  - *Bark under 0.028 of what is seen from a level view* (one in three): the leader's tip is 0.06 m, from 0.045.
  - *Two tiers touching* (one in eight): 0.2 m of clear air between tiers before the fit, from 0.14.
  - *The budget* (half; the typical tree had 5,230 triangles against 5,225): a bough is a little narrower (half its width 0.33 to 0.40 of its length, from 0.34 to 0.42). It is still what refuses most trees.
- **A conifer is kept only when the view from under it holds sky** (`UNDER_SKY_SPARE` in the generator). Gate L4e reads a picture from 1 m beside the trunk and needs 300 samples of sky in it to know it is the right picture; a conifer's lowest tier can close that view altogether, and of the first ten trees kept on the new form five did. The generator now asks, of a tree of tiers, twice the gate's share of sky in that view, measured from the geometry. This is the brief's own Viewing ("sky shows between the boughs of a tier") held where a seed is drawn, not a new gate.
- **Pieces hang closer under a bough** (`skirt.under_spacing` 0.25, from 0.27). On the new form the first `conifer_1` drawn failed L4e's `view.under_limbs` by a hair (foliage 1.24 times the limbs' luminance from below, against 1.25): the typical thing seen from under it was a plate, which is darker than any piece. With the pieces closer the plate is 0.30 of the foliage seen from below (from 0.37) and the same measure is 1.96. A form change made after a failed build; the limit was not touched.
- **A bough's core is a plate along its underside**, not the dome a pad's lobe has: a dome under a thin bough showed between its pieces from above and round its rim (core 12 to 19% of the foliage seen, against 10%), and made small enough to hide left the tier open from below. The plate closes the underside and lies under the whole depth of the pieces. A bough's pieces are spread evenly over its plan and are the broadleaf's size.
- **No autumn conifer.** The season rule (a season is a palette on the base's mesh) is used for winter only.
