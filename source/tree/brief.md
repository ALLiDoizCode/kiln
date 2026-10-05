# tree

A plain broadleaf tree, made by a generator that reads a spec. This is the brief for the family: the generator (`generator.py`, beside this file), its species recipes (`species/`) and everything its trees share. Every tree is an asset of its own whose spec names this folder as its `family` and gives a `species`, a `growth_stage`, a `season`, a `seed` and bounds (ADR 13): a new tree is a new spec, not new code. `tools/lint_spec.py` holds each of them to the Numbers table below, except for the rows an asset's own brief gives. The trees so far: three mature ones (`source/tree_1`, `tree_2`, `tree_3`), a sapling, a young and an old one (`tree_sapling_1`, `tree_young_1`, `tree_old_1`), and `tree_1` in autumn and winter (`tree_1_autumn`, `tree_1_winter`).

It is the first tree, and the first asset with foliage in the style of ADR 9 as amended: leaf-shaped pieces on a branch skeleton, over a dark core.

## Purpose

Set dressing on a forested layer's ground, and the thing a forest is made of: many are on screen at once. A player walks under it and round it and stands against the trunk. Nothing climbs it, breaks it or moves it yet, and it does not move in the wind.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 3 to 40 m. Two views decide what it must hold up to:

- **From 3 m**, looking up at it: the trunk, the fork, the underside of the nearest pads and the branches going into them fill the view.
- **From 0.5 m**, against the trunk: looking straight at it, bark is about half of what is seen, at arm's length; looking up, the rest is the underside of the canopy with the branch skeleton against it. This is how a tree is mostly seen, and each variant's contact sheet shows both (`bevy_trunk`, `bevy_under`).

From further off it is an outline: a trunk, and several rounded pads with sky between them.

## Real-world size

About 7 m tall with a crown 4 to 6 m across: a small street tree, or four players standing on each other's shoulders. The three variants differ in size on purpose, so that a group of them does not have one height:

| Variant | Width (x) | Depth (y) | Height | Character |
| --- | --- | --- | --- | --- |
| `tree_1` | 4.9 m | 4.7 m | 7.0 m | the plain one, the benchmark's size (4.3 by 4.6 by 7.3 m) |
| `tree_2` | 5.5 m | 5.4 m | 6.2 m | lower and wider |
| `tree_3` | 4.3 m | 4.3 m | 7.8 m | taller and narrower |

The origin is on the ground at the middle of the foot of the trunk, so a tree is planted, and turned, about its trunk. The crown is not centred on it: a tree leans.

## Species

A species is a recipe the one generator reads: `species/<name>.toml`, named by a spec's `species`. It holds every number that says how the trunk leans, flares and forks, where the pads sit and how they are built, and the shape of a leaf piece; the generator has none of its own besides how hard it tries (`TREES`, `MAX_STRETCH`) and the room it keeps to each limit (`MARGINS`). The broadleaf (`species/broadleaf.toml`) is the only one. The checks below are this family's, and a species that needs others (a conifer has no pads) will need its own rows.

## Growth stages

A spec's `growth_stage` is a number: the tree's height over a mature tree's, so 1.0 is mature. The recipe's `[growth]` table says what follows it, as multipliers at the stages it names with straight lines between: the trunk's girth, its lean, how low it forks, how many pads it carries, how wide they are and how long and how close its leaf pieces are. From young to old, leaf pieces do not grow: a young tree has fewer, smaller pads of full-size leaves. A sapling's are shorter (below). `tools/lint_spec.py` holds a spec's height to its stage: the stage times the recipe's mature height, 6 to 8 m.

| Stage | `growth_stage` | Height | Crown | Trunk at 1.3 m | Pads | Forks at | Triangles, at most |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sapling | 0.5 | 3.0 to 4.0 m | about 3.1 by 1.9 m | about 0.2 m through | 2 | 1.5 to 2.1 m | 1,200 |
| Young | 0.8 | 4.8 to 6.4 m | about 4 m | about 0.3 m through | 3 or 4 | 1.8 to 3.0 m | 2,500 |
| Mature | 1.0 | 6 to 8 m | 4 to 6 m | about 0.43 m through | 3 to 5 | 2.0 to 3.5 m | 4,000 |
| Old | 1.25 | 7.5 to 10 m | about 6.4 m | about 0.55 m through | 5 or 6 | 2.5 to 4.5 m | 6,000 |

What a stage changes in the Numbers, and why (each stage asset's own brief gives the rows):

- **Budget.** Leaf pieces are the cost and they follow the canopy's surface: a young tree's three or four pads at 0.8 of the width are about half the mature surface, an old tree's five or six at 1.15 about one and three quarter times. With the bark and cores that gives 2,500 and 6,000 beside the mature 4,000; 6,000 is the ceiling the owner first proposed, from the benchmark's 6,265. They are estimates until the stress scene (ADR 7).
- **Fork.** A young tree forks lower and an old one higher than a mature one; every stage still forks above a player's head (1.8 m).
- **Young pads.** A pad under full-size leaves cannot be as flat or as different from its neighbours as a mature one: 0.5 m leaves and a 0.45 m skirt are a larger part of a 1.4 m pad than of a 2.5 m one. A young tree's pads are asked to be 1.2 times as wide as tall (mature 1.3) and its widest 1.3 times its narrowest (mature 1.4).
- **Young crevice shadow.** The band of shadow round a junction is the mature tree's 4.5 cm times the stage's girth (0.7): 3.2 cm. At 4.5 cm the young tree's thinner limbs showed inside corners 0.71 as light as open faces where `painted.crevices_darker` allows 0.70, the same thinning the mature tree showed at 6 cm.
- **Old texture.** 1024 px, as a mature tree's. It was 2048 px while the painter packed islands as boxes: a 1024 px texture then gave the old trunk 231 texels per metre below 2.5 m, where this brief asks for 250. Packed by their outlines (`pack` in `tools/paint.py`) the islands use 0.65 of a 1024 px texture, the trunk below 2.5 m gets 261 texels per metre and the sparsest limb 156 (100 asked); the old tree's file is 1.3 MB where it was 3.4 MB.

**The sapling has a silhouette of its own.** At stage 0.6, drawn as a small young tree (three pads under full-size leaves), the generator kept no tree in 32 tries over four seeds: three pads small enough for a 3 m crown, under 0.5 to 0.75 m leaves, do not keep clear air between them, and their limbs show too little bark. So a sapling is not a young tree made smaller. It is stage 0.5, 3 to 4 m tall, a tree a player looks at and across rather than up into, and these are its rules, each a row of a sapling's own brief where it changes a number:

- **Two tufts.** One stem that forks once: the leader carries the higher, wider tuft and one side branch the lower, narrower one, with clear air between them. Two tufts are a row, not a ring, so a sapling's crown is longer one way than the other, and its bounds say which. Silhouette 2's "at least three limbs" is two for a sapling, and Silhouette 3's "three to six pads" is exactly two. Everything else Silhouette 3 asks of a pad (lobes, a core in each, a skirt) is asked of a tuft, except the number of its pieces (below).
- **The crown is a row's size: about 3.1 by 1.9 m.** Tufts are half as wide as a mature tree's pads: the wider 1.5 to 1.75 m, the narrower 0.8 to 0.92 m. End to end with the recipe's 0.15 m of clear air between them, and leaf tips standing 0.13 m off each side of each, the row is 1.62 + 0.86 + 0.15 + 4 x 0.13 = 3.1 m long, and as deep as the wider tuft with its tips: 1.9 m. The first bounds were 2.6 m long, which is the two tufts with nothing between or round them: the generator shrank the tufts to fit the length, and they then could not be stretched to the depth (19 refusals of 36).
- **Shorter leaf pieces, standing out like a shoot's**: 0.84 of the length, 0.42 to 0.63 m. A piece stands for a spray of leaves, and a sapling's shoots are short; pieces 0.5 to 0.75 m long on a tuft about 1 m wide would be a handful of cards. They are 0.84 of the spacing apart as well, so that a piece overlaps its neighbours as a mature tree's does. Silhouette 4's floor of 0.35 m stands (it is what a piece must be to show at 20 m); its ceiling for a sapling is 0.7 m, so that a sapling drawn with full-size pieces fails. And half of a piece's length lies behind the point where it crosses its lobe's surface, where a mature tree's piece has four fifths: see "Pointing out" below.
- **Fork.** At about a player's eye height (1.7 m), between 1.5 and 2.1 m: the player looks across the fork into the lower tuft, where every older stage forks overhead. Not lower, because the trunk's girth is taken 1.3 m up (`conventions.toml`) and the checks need one stem there and one slice above it.
- **A thin stem.** Half the mature girth: about 0.2 m through at 1.3 m, with five to eight flat sides about 10 cm wide. The bands of painted light and shadow follow the girth, as the young tree's shadow does: light along the corners 1.5 cm wide (3 cm times 0.5), shadow round a junction 2.2 cm (4.5 cm times 0.5).
- **Lean.** The fork stands 0.08 to 0.4 m to one side of the foot: the mature range times the stage (0.5), since the stem is half as long.
- **Small pads under large leaves**, as for the young tree and more so (a 0.5 m piece on a tuft 1 to 1.5 m wide): tufts are asked to be 1.2 times as wide as tall and the wider 1.3 times the narrower, the young tree's numbers.
- **Budget.** Leaf pieces follow the surface of the pads, which goes as the square of their half-widths: a sapling's two tufts (0.81 and 0.43 m) have 0.16 of the surface of a mature tree's four pads (`tree_1`: 1.63, 0.95, 0.92 and 0.87 m), and at 0.84 of the spacing carry 1.42 times the pieces on it: 0.23 of the mature 2,100 leaf triangles, about 480. With five or six cores (about 140) and the bark of one stem, one branch and a few twigs (about 420) that is about 1,040. The ceiling is 1,200, as first written; it leaves a sapling less room over its estimate (0.15) than the young tree has (0.35), because the first estimate (900) took the tufts' surface for a tenth of a mature canopy's.

**A sapling's own limits for three checks** (decided by the owner on 2026-10-05: a tuft may be held to other numbers than a pad, each with a reason that does not come from a build, and none switched off). They were written after the tries above and fourteen more trees drawn to diagnose them, and before any tree was built under them:

- **Pieces in a tuft: at least 24** (`foliage.min_pad_pieces`; a pad's is 40). The floor is what tells a tuft from a stray clump and from a cap on a stalk. A tuft is at least two lobes, and a lobe reads as a rounded mass with no fewer than a ring of five pieces hanging from its rim (the recipe's least), a ring of five or six lying on it above them and one or two under it: twelve. Two lobes of twelve are 24. By surface the number would be lower: the narrower tuft is half as wide as a mature tree's narrowest pad, a quarter of its surface, and carries 1.42 times the pieces on it, 0.35 of 40, which is 14; the larger of the two numbers is the limit. A tuft of one lobe, or of two with gaps in their rings, fails.
- **Pointing out: at least 0.8, a pad's number** (`foliage.min_pointing_out`), and the generator changed instead. Diagnosis, on six sapling trees and two mature ones drawn for it: every piece hanging from a rim or under a lobe counts as pointing out (338 of 338 on the sapling), so the measure's use of the pad's middle is not what fails a tuft; measured from each lobe's own middle the tufts score lower still. What fails is the shell. A shell piece lies along its lobe's surface with four fifths of its length behind the point where it crosses it, so its middle sits a third of its length uphill of that point, and it points away from the middle only where the lobe's radius is larger than the piece is long: 0.89 of shell pieces where the radius is over 1.4 times the length (a mature main lobe), 0.80 from 0.9 to 1.4, 0.77 from 0.6 to 0.9 and 0.51 under 0.6. A tuft's lobes are 0.15 to 0.65 m in radius under pieces 0.42 to 0.63 m long, so a shingle laid on one passes through the lobe and out of its far side. The check is right about that: such a tuft is cards crossing, not leaves pointing out. So a sapling's piece has half its length behind the surface (`leaf_foot` in the recipe's `[growth]`), which puts its foot near the middle of a small lobe, like the leaves of a shoot, and the limit stays 0.8.
- **Bark seen above the fork: 1.2% of what is seen, from six of seven views** (`skeleton.min_seen_share`; a mature tree's is 2%). Bark seen goes as the number of limbs, their thickness and their length, over the outline they are seen against. A sapling has two limbs above its fork where a mature tree has four (0.5), each between 0.5 and 0.71 as thick (the girth at the fork, its square root at the tips; 0.6), half as long (0.5), against an outline half as wide and half as tall (0.25): 0.5 x 0.6 x 0.5 / 0.25 = 0.6 of the mature share, and 0.6 of 2% is 1.2%. The number of views stays six: a sapling whose tufts swallow its fork, or whose limbs are no thicker than twigs, shows less than 1% from most sides and fails. The generator keeps the same room to this limit as to the mature one (1.4 times it, from all seven views).

Not changed for a sapling, and so asked of it as of a mature tree: sky between the tufts (20 to 50% from five of six directions), pieces pointing out of their tuft and downward, the view from below, the bark's grain and its 250 texels per metre, and the 1024 px texture.

## Seasons

A season is a palette on the same mesh (ADR 11, ADR 13). A season asset is a spec of its own that names its `season` and the asset it is a `palette_of`; it is drawn again from the same species, stage, seed and bounds, so its mesh, UVs included, is its base's, and only its texture differs. `tools/lint_spec.py` holds the two specs to agree on everything but the palette (`spec.palette_of`), and `tools/same_mesh.py` holds the two exported files to the same geometry byte for byte, with different images (gate L2c). The game can then keep one mesh and swap the image.

| Season | Leaf, top of a pad | Underside tint | Core tint | What it shows |
| --- | --- | --- | --- | --- |
| Summer | `#a8b846` | `#9ad0e6` | `#71a9b9` | Light yellow-green above, darker and bluer below (Style and colour) |
| Autumn | `#e0a23a` | `#ff936f` | `#bf6653` | Golden yellow at the top of a pad through orange to deep red underneath |
| Winter | `#d8dcde` | `#6f9f7b` | `#51755c` | Snow lying on the pads: near-white on top, through pale grey-green, to dark green underneath |

Winter here is snow on the foliage only, and it is a ramp of six shades, not a snow line. Snow on the bark's upward faces is not done: painted growth keeps the bark's own lightness and the load test finds it by hue (ADR 10), and snow is a change of lightness with no hue, so it needs a growth that lightens and checks that measure it by lightness. A bare winter tree is a separate mesh (ADR 13): the generator without leaf pieces and cores, with the twigs the cores now hide put back, and a spec without the `foliage` block, whose sky and bark-seen checks would need other limits.

## Silhouette

What must read, taken from the nature reference (`docs/style/nature-shapes.md`, Broadleaf, and "How they are built"):

1. **A designed trunk.** Five to eight flat sides with a soft edge between each pair, darker than the foliage. It leans: the fork stands 0.15 to 0.8 m to one side of the foot. It tapers: just below the fork it is at most 0.9 of its girth at breast height (1.3 m). At the ground it flares to at least 2 times its breast-height radius, into at least three roots.
2. **A visible branch skeleton.** The trunk forks between 2.0 and 3.5 m up, above a player's head, into at least three limbs, and each tapers: four fifths of the way from the fork to the top of the bark the limbs are at most 0.8 of their thickness one fifth of the way. The skeleton shows: from each level view and from underneath, bark is at least 2% of what is seen of the tree above the fork, in at least six of those seven views.
3. **Three to six separate pads of foliage**, at different heights, each of at least 40 pieces, with clear air between every pair. A pad is a dense, lumpy mass, not a cap on a stalk:
   - it is built from two to four overlapping lobes of different sizes (in every pad the widest lobe is at least 1.2 times the narrowest);
   - it is wider than tall (at least 1.3 times), with a skirt of pieces drooping from its lower edge;
   - pads differ in size within one tree (the widest at least 1.4 times the narrowest);
   - under the pieces of each lobe sits a closed, dark, low-triangle core (ADR 9 as amended), so the gaps between pieces show dark foliage and not sky or the far side of the pad. The pieces are what is seen: from each level and three-quarter view no more than 10% of the foliage seen is core.

   Sky shows **between** pads: seen from the side, between 20% and 50% of the canopy's outline (the convex hull of its foliage) is sky, from at least five of six directions. A single mass scores 10 to 19% on this measure (the benchmark tree and its four siblings), and a ball scores none.
4. **Leaf-shaped pieces.** Every piece is flat, pointed (its sharpest corner is 60 degrees or less), jagged (its outline has at least one notch) and between 0.35 and 0.9 m long. Pieces lie like shingles, overlapping, pointing out of their pad and downward, so a pad's outline is serrated.
5. **Colour by piece.** Each piece is one flat colour. Pieces differ from their neighbours, and they run from a light yellow-green at the top of a pad to a darker, bluer green underneath. The core is darker than any piece.
6. **Bark that reads as bark at arm's length.** Grain runs along every limb: fine streaks, plates of bark, dark furrows wandering between them and a few knots. Seen from 0.5 m in Bevy, in a hand-sized patch of trunk, the typical step in tone 4 mm across the trunk is at least 1.4% of the mean tone, and at least 1.25 times the step the same distance along it; both numbers are the least of the benchmark's five trees from the same camera under the viewer's light (ambient 900), and are measured again when that light changes. The trunk to its fork, the roots and the feet of the lowest branches (everything that reaches below 2.5 m) get at least 250 texels per metre.
7. **A canopy that reads as foliage from below.** Looking straight up at a pad: its underside is closed (no more than 15% of its outline shows the inside of the pad, a piece more than 0.6 m above its underside, or sky through a gap); its rim is leaves (at least one point of a piece stands clear against the sky per metre of its outline); and although the core closes the view, pieces hanging under it keep it to no more than 45% of the foliage seen.
8. **Limbs that stand out, and no glare, from below.** Looking up from 1 m beside the trunk, in Bevy: foliage seen from the side the sun does not reach is at least 1.25 times as light as the limbs among it, so the branch skeleton reads against the canopy; and no leaf piece shows the sun's glare, a near-white piece among dark ones (`tools/under_checks.py`, gate L4e).

## Style and colour

ADR 9 as amended: foliage is leaf-shaped pieces, never leaf cards, with no transparency; a solid may sit under the pieces as long as the pieces are what is seen. The tree stands beside the rock (`source/rock`) and is judged beside the benchmark tree.

- **Bark** `m_tree_bark`, `#7a5a44`: a warm mid brown, with painted shading (ADR 10): darker toward the ground (`#b9a8a0` tint at the foot, none at the top), light along the corners between its flat sides, shadow where a branch leaves the trunk and between the roots, and grain (ADR 12). The grain is its variation: no blotches are painted, and no growth.
- **Leaf** `m_tree_leaf`, `#a8b846`: the light yellow-green of a piece at the top of a pad. The underside tint `#9ad0e6` takes most of the red out, less of the green and least of the blue, which gives the darker, bluer green underneath. Between the two there are 6 shades, and each shade comes in 4 tones up to 16% lighter or darker, so that neighbouring pieces differ. A piece's shade comes from how high it sits within its own pad; its tone is drawn from a fixed shuffle.
- **Core**: in the leaf material, the leaf colour times the tint `#71a9b9`: about three quarters as light as the darkest piece, so that it is dark and not black.
- Leaf pieces and cores take their colour from a palette, not from a bake (ADR 11): a strip of swatches along the top of the bark's texture, with all of a piece's UVs on one swatch and all of every core's on the one after the leaves'. The leaf material is two-sided and has no gloss (exported as `KHR_materials_specular` with a factor of 0, ADR 4 as amended): with the default gloss a flat piece the sun grazes shows the sun and none of its own colour to a player under the canopy.

Bevy lights the back of a two-sided face with its normal turned round, so the underside of a pad is lit only by the ambient light: dark green under the viewer's light, never black, which is the reference's "deep green underneath". Each piece's normal is part its own and part the direction out of its lobe and upward, so a lobe is lit as one round mass and its pieces still differ.

## Parts

One object and one mesh per variant, with two materials: bark and leaf. Nothing moves and nothing is swapped. The bark is a closed surface (the trunk and each limb is a closed tube, pushed into its parent). The leaf material holds the leaf pieces, which are open, separate, flat pieces (what `open_materials` records), and the cores, each a closed dome of 24 triangles inside one lobe. The checks tell the two apart by shape alone: a connected set of the leaf material's faces with an open edge is a piece, and one with none is a core.

## Budget

At most 4,000 triangles and two materials per variant, on one 1024 px texture. The ceiling is unchanged; the split inside it is new.

With a core under them the pieces no longer have to hide the sky, only the core. The generator's one tree for `tree_1` was built at four leaf spacings (the same pads and skeleton each time) and looked at under Bevy from the standard view, from 3 m and from under it (`benchmarks/out/tree_budget_study_v2.png`; the first study, without cores, is `tree_budget_study.png`):

| Spacing between pieces | Triangles (bark, core, leaf) | Core, of the foliage seen from the side | What it shows |
| --- | --- | --- | --- |
| 0.36 m | 2,890 (850, 384, 1,656) | 0.08 to 0.13 | Pads hold together from every view, but dark gaps a piece wide show in the standard view; two views are over the 10% limit. |
| 0.31 m | 3,210 (850, 384, 1,976) | 0.06 to 0.08 | No gaps a piece wide. Passes the limit; too close to it for the generator's margin (0.085). |
| 0.27 m | 3,554 (850, 384, 2,320) | 0.04 to 0.06 | No difference from 0.31 m that can be seen from 3 m or from below; a little more even in the standard view. Chosen. |
| 0.23 m | 4,086 (850, 384, 2,852) | 0.01 to 0.04 | No difference from 0.27 m in any view. Over the ceiling. |

Without cores, 0.24 m was the least at which a pad read as a mass; with them 0.31 m reads as one, and 0.27 m is used for its margin on the core limit. At that spacing the three variants are 3,554, 2,802 and 3,364 triangles: bark 642 to 850, cores 216 to 384 (24 a lobe), leaf pieces 1,944 to 2,320. Of the 25 trees the generator kept while choosing seeds, the largest was 3,758. 4,000 stays the ceiling, and the generator keeps no tree over 3,800. A piece costs four triangles: three would lose the notch that makes its edge jagged. Twigs inside the pads, which the cores now hide, were taken out (about 270 triangles a tree); one twig runs from each limb's end into each side lobe.

The texture is 1024 px. The palette takes a strip 16 px tall along the top. The bark below 2.5 m gets 250 texels per metre. The limbs above are asked only the 100 the conventions ask of every face (the load test's `min_texels_per_m`): an eye at 1.7 m is at least 0.8 m from a limb above 2.5 m, where the 1 degree texel the conventions reason from 0.5 m is 1.6 cm, 63 texels per metre, so 100 already has room and no number of the limbs' own is kept here; at 2048 px the grain looks no different (ADR 12). A variant's GLB is 1.0 to 1.1 MB, most of it this texture; grain compresses worse than the flat tone it replaced (0.65 to 0.68 MB before).

## References

- Look: `docs/style/nature-shapes.md` and the previews it was read from (`docs/style/refs/nature-shapes/`, git-ignored): the asset overview (`img11.png`) for the broadleaf trees' outlines and the lumpy, solid look of their pads, the biome tiles (`img10.jpg`) for pads at close range, and the jungle scene (`img6.jpg`) for foliage seen from underneath.
- Benchmark: `benchmarks/quaternius-stylized-nature/glTF/CommonTree_1.gltf` (6,265 triangles, 7.3 m tall, leaf cards, a tiling bark texture with a normal map). A comparison only; nothing from it is used. Its four sibling trees were measured with it for the sky, variant and bark thresholds.
- Comparisons: `benchmarks/out/tree_variants.png` (the three variants and the benchmark from five views; `tree_variants_v1.png` is the same before the core and the grain), `tree_bark_study.png` (the bark by three means, ADR 12).

## Out of scope

Wind animation, LODs, collision shapes, a climbable flag, other species, a bare winter tree, snow on bark.

## Numbers

Every value the trees' `spec.json` files share, and the sentence above it comes from: the mature summer tree's. Each asset's own brief gives its `objects`, `seed` and `bounds_m`; the mature variants' give their `variants` rows, a stage's the rows Growth stages names, and a season's its `season`, `palette_of` and colours. `tools/lint_spec.py` fails if a row and a spec disagree, or if a spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"tree"` | This brief |
| `species` | `"broadleaf"` | Species: the recipe `species/broadleaf.toml` |
| `growth_stage` | `1.0` | Growth stages: mature |
| `season` | `"summer"` | Seasons |
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
| `painted_shading.crevice_width_m` | `0.045` | A band 4.5 cm wide round each junction. At 0.06 the shadow was spread thin over limbs not much wider than the band, and showed 51% of `crevice_shadow` where the check asks for 50%; at 0.045 it shows 54 to 68% |
| `painted_shading.hidden_underside` | `true` | The foot of the trunk stands on the ground |
| `painted_shading.grain` | `0.3` | Style and colour: grain; chosen by eye beside the benchmark at 0.5 m and 3 m |
| `painted_shading.grain_width_m` | `0.02` | Style and colour: fine streaks 1 cm wide, plates of bark about 6 cm |
| `painted_shading.close_height_m` | `2.5` | Viewing: a player stands against the trunk below the fork |
| `painted_shading.close_texels_per_m` | `250.0` | Budget: two and a half times the conventions' least; a 1024 px texture cannot give this much surface 300 |
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
| `skeleton.min_view_tone` | `0.014` | Silhouette 6: the typical step in tone across a hand-sized patch of trunk seen from 0.5 m |
| `skeleton.min_view_grain` | `1.25` | Silhouette 6: and faster across the trunk than along it |
| `skeleton.min_canopy_over_limbs` | `1.25` | Silhouette 8: seen from below, foliage is lighter than the limbs among it |
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
| `foliage.under_tint` | `"#9ad0e6"` | Style and colour: darker and bluer underneath |
| `foliage.top_tint` | `"#ffffff"` | Style and colour: the leaf colour itself at the top |
| `foliage.shades` | `6` | Style and colour |
| `foliage.tones` | `4` | Style and colour |
| `foliage.variation` | `0.16` | Style and colour: tones up to 16% lighter or darker |
| `foliage.core_tint` | `"#71a9b9"` | Style and colour: the core, darker than the darkest piece |
| `foliage.lobes` | `[2, 4]` | Silhouette 3: two to four lobes, a core in each |
| `foliage.min_lobe_ratio` | `1.2` | Silhouette 3: lobes of different sizes |
| `foliage.max_core_seen` | `0.1` | Silhouette 3: the pieces are what is seen from the side |
| `foliage.max_core_seen_below` | `0.45` | Silhouette 7: and most of what is seen from below |
| `foliage.min_pad_flatness` | `1.3` | Silhouette 3: wider than tall |
| `foliage.min_pad_spread` | `1.4` | Silhouette 3: pads of different sizes |
| `foliage.max_seen_into` | `0.15` | Silhouette 7: the core closes the view up into a pad |
| `foliage.min_rim_points_per_m` | `1.0` | Silhouette 7: points against the sky at a pad's rim |
| `soft_edges` | `true` | Silhouette 1: soft edges between the trunk's sides |
| `watertight` | `true` | Parts: the bark is a closed surface |
| `open_materials` | `["m_tree_leaf"]` | Parts: leaf pieces are open and separate |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Style and colour: one texture, so UVs; no tangents |

## Decisions

**Decided by the owner** on 2026-10-04, each by accepting a recommendation:

- **Subject**: a plain broadleaf tree about 7 m tall. It is chosen because it has a direct benchmark; trees specific to the pit come after it.
- **Form**: a generator that takes a seed, with three variants as the deliverable.
- **Foliage**: leaf-shaped geometry in flat colour, on a visible branch skeleton, in several separate pads with sky between them. No leaf cards, no transparency.
- **Surface**: painted shading (ADR 10).
- **Budget**: proposed as at most 6,000 triangles and two materials, from the benchmark tree's 6,265; the brief was to state the number it settles on and why. For this pass: 4,000 stands unless the look needs more, with evidence.
- **Judgement**: our tree and the benchmark tree side by side in Bevy on one sheet. The owner approves when ours is not clearly worse.
- **Reference for the look**: the nature pack described in `docs/style/nature-shapes.md`.
- **Out of scope**: wind, LODs, collision, seasonal variants, growth stages.

And, after looking at the first three trees beside the benchmark:

- **A dark core is allowed under the leaf pieces** (ADR 9 amended): pads are to read as dense masses with depth.
- **Pads are fuller and irregular**: two to four overlapping lobes of different sizes, wider than tall, with a drooping lower skirt, clearly different in size within one tree, and sky still visible between pads.
- **The canopy reads as foliage from below**: points and notches against the sky at pad rims and in the skirt, and the core closing the view up into the pad.
- **Bark reads as bark at 0.5 m and at 3 m**, generated by script and the same every build; the means to be chosen by trying and looking.
- **The generator meets the brief**: it redraws until the shape checks are met, fails loudly if it cannot, and seeds are chosen with margin.
- **A view from below** is on every tree's contact sheet.

And on 2026-10-05, after two attempts at a sapling kept no tree:

- **The sapling stage has its own limits for three checks** tuned on large pads (`foliage.min_pad_pieces`, `foliage.min_pointing_out`, `skeleton.min_seen_share`), written here with their reasons before it is built; none is switched off, and each must still fail a bad sapling (Growth stages).

And on 2026-10-05, after the review of the three mature trees (`source/tree_1/review/final/review.md`):

- **Limbs stand out from the leaves when looking up into the tree**, by lightening the leaf undersides, not by changing the bark. The underside and core tints were lightened for it (summer `#6f96a6` to `#9ad0e6` and `#527a86` to `#71a9b9`; autumn and winter by the same share); how far is the agent's, see below.

**Proposed by the agent**, and open to change at review:

- **Three assets, one generator.** Each variant is an asset (`tree_1`, `tree_2`, `tree_3`) with its own spec, build script, GLB and contact sheet, because the pipeline's unit is one asset, one GLB, and the game places trees one at a time. The generator and this brief live here, in `source/tree`, which is not an asset and has no spec. A variant's spec carries its `seed`.
- **The skeleton is our own generator, not Sapling Tree Gen**: Sapling's limbs are round curves, it has no roots, and its pads would have to go where its branches happen to end. The generator here places the pads first, inside the bounds, and grows a limb to each.
- **The budget stays 4,000 triangles** (Budget). At a leaf spacing of 0.31 m the variants would be about a tenth smaller and still pass; 0.27 m was kept for its margin on how much core shows.
- **The core is in the leaf material**, not a third material: a tree stays two draws. The cost is that the checks find cores by shape (closed) and not by name. It is one dome of 24 triangles per lobe, lit round, coloured from one more palette swatch (`core_tint`).
- **Bark is painted grain with more texels on the trunk** (ADR 12), inside ADR 10: no second texture. A normal map baked from the same furrows was prototyped and is clearly better where the sun reaches the trunk; it was left out for its cost (a second texture, tangents, a second texture class through the gates). **The owner should look at `benchmarks/out/tree_bark_study.png` and say whether sunlit trunks are worth it.**
- **No blotches on the bark.** The grain's plates are its broad variation, and ADR 10's blotch checks cannot be met by a surface with grain. `blotch` and `blotch_size_m` left the spec.
- **A leaning trunk is stood beside where it is at eye height.** The manifest gives that place (`stand_at`), and the `--stand` views measure their distance from it; before, they stood 0.5 m from the foot and often looked past the trunk.
- **Lean is measured from just above the roots.** The check `lean` took the trunk's foot as the middle of its slice at the ground. Roots reach further on one side than another, so that middle sits up to 0.2 m off the trunk's, and with the new seed a trunk drawn with no lean at all measured 0.15 m and passed: the test's upright trunk was no longer caught. The foot is now the trunk's middle 0.4 m up (`conventions.toml`), where the roots have joined it. The limits are unchanged; the variants measure 0.32 to 0.42 m.
- **The generator refuses, and so does the gate.** A seed draws trees until one fills the bounds and meets the brief's shape checks, as the gate measures them, with room to spare: `MARGINS` in `generator.py` gives the stricter value used for each limit (a fork between 2.2 and 3.3 m where the brief says 2.0 to 3.5, taper 0.85 for 0.9, bark seen 0.028 from all seven views for 0.02 from six, and so on). A seed none of whose 40 trees passes fails the build with every tree's reasons. Of seeds 1 to 12, given 8 trees each, 7 are kept at `tree_1`'s size, 8 at `tree_2`'s and 10 at `tree_3`'s. What the generator cannot measure, because it happens after it (the painted bark, the outline against the other variants), stays the gate's alone.
- **Sizes**: the three variants' bounds; the origin at the foot of the trunk.
- **Every number in the Numbers table** not named in the owner's list. Where each threshold came from:
  - `foliage.sky_share`: the benchmark tree and its four siblings, each one mass of leaf cards, score 0.10 to 0.19 from the six directions. The floor is set just above that, at 0.2; the three variants now score 0.28 to 0.41. The ceiling of 0.5 is half the outline: more sky than foliage is a bare tree.
  - `variants.min_difference`: between the benchmark pack's three trees of this height, outlines differ by 0.19, 0.27 and 0.30. 0.3 asks our variants to differ at least as much as its most different pair; they differ by 0.62 to 0.73.
  - `foliage.piece_m`: the benchmark's leaf cards are 0.85 to 2.4 m long, each showing a cluster of many leaves, so 0.9 m is where a piece stops being a leaf and becomes a card. 0.35 m is a piece that still covers a degree of the view at 20 m.
  - `skeleton.*` shape numbers: the benchmark's bark is not a closed surface and could not be sliced, so these come from the reference's words and from ADR 7's player height for the fork. `min_seen_share` 0.02 is what the benchmark shows of its own branches at best (0.00 to 0.05); the variants show 0.03 to 0.08.
  - `skeleton.min_view_tone`, `min_view_grain`: measured on the benchmark's five trees (`CommonTree_1` to `_5`) with `tools/view_checks.py --measure` from the same camera (`asset_view --stand 0.5 --pitch 0`) under the viewer's light: tone 0.0144 to 0.0163, grain 1.25 to 1.44. The floors are the least of each, 0.014 and 1.25. They follow the light: under the viewer's first light (ambient 300) the same trees read 0.021 to 0.023 and 1.16 to 1.27, and the floors were 0.021 and 1.16 (our own bark fell with them, `tree_1` from 0.026 to 0.021; why a lighter shade lessens the step as a share of the mean was not looked into). Measure them again when the light changes. Bark with no grain scores 0.0085 on tone (0.6 of the floor) and 1.22 on grain; the eight trees score 0.019 to 0.045 and 1.7 to 3.4. So the tone floor is what catches flat bark. The grain floor does not: the light on a trunk's corners already runs along it. It catches grain that runs round the trunk (0.49). A first version of the measure took the spread of tone in a window and passed grainless bark, because the line between a lit and a shaded side of the trunk is a spread; the red case caught that, and the measure is now the median step.
  - `painted_shading.close_texels_per_m`: not from the benchmark, whose bark is a tiling texture. 250 is what a 1024 px texture can give everything below 2.5 m (it runs out just under 300), and at twice that the grain looks no different.
  - `foliage.max_core_seen` 0.1: not measurable on the benchmark, which has no core. Set from the density study: at 0.1 and above, dark gaps a piece wide show in the standard view. The variants show 0.04 to 0.07.
  - `foliage.max_core_seen_below` 0.45: from straight below the core is meant to be seen, closing the pad; under half keeps pieces the larger part. The variants show 0.33 to 0.37. This is the weakest of the new numbers: nothing but our own look at the sheets stands behind it.
  - `foliage.max_seen_into` 0.15: the first three trees, open shells, score 0.29 to 0.46 in their worst pad; these score 0.07 to 0.12. The limit sits between.
  - `foliage.min_rim_points_per_m` 1.0: the first trees already scored 1.0 to 4.3 here (their rims were leafy; their insides were the trouble), and these score 1.4 to 3.6. The limit holds what was already good, and fails rounded pieces.
  - `foliage.min_pad_flatness` 1.3: the first trees' pads were already 1.6 to 2.0 times as wide as tall by this measure, and these are 1.6 to 2.1. It guards against ball pads; it is not what tells the new pads from the old.
  - `foliage.min_pad_spread` 1.4: the first trees scored 1.23 to 1.33, and the eye took their pads for one size. These score 1.53 to 1.80.
  - `foliage.lobes`, `min_lobe_ratio`: the owner's "two to four overlapping lobes of different sizes"; 1.2 is the least difference in width that reads as a difference.
  - Leaf, bark, core and tint colours: chosen by eye against the reference's previews under the Bevy viewer's light. They are the first thing to change at review.
- **Species, stage and season are spec fields; each tree is still one asset** (ADR 13, agreed by the owner on 2026-10-05; how it is written is the agent's). `species` names a recipe file, so a species is data the generator reads. `growth_stage` is the height over a mature tree's, because a spec's bounds already give the height and the lint can then hold the two together (`spec.growth_height`).
- **A season is a separate asset that shares its base's mesh**, not a second texture inside one asset: the pipeline's unit is one spec, one GLB, one contact sheet, and every gate already reads a palette from the spec, so an autumn tree is gated exactly as a summer one is. The cost is that each season's GLB repeats the mesh (about 0.15 MB of a 1 MB file); the gate proves the copies are identical, so the game may load one. Exporting the texture alone was not done: it needs images outside the GLB, which the profile (ADR 4) forbids.
- **Asset names**: `tree_<n>` stays the mature summer tree, a stage is `tree_<stage>_<n>` and a season `<base>_<season>`. The three mature trees were not renamed `tree_mature_<n>`: the tests, baselines and the game's look tests name them, and the default stage needs no word.
- **`variants.min_difference` moved** from this table to the mature variants' own briefs: it compares seeds of one stage, and a stage or season with one seed has no sibling to compare with.
- **Stage and season numbers** (Growth stages, Seasons): every one is the agent's. The stage curves in the recipe were set so that the generator keeps trees; the autumn and winter colours were chosen without the owner seeing them.
- **How far the undersides were lightened, and the two limits of gate L4e.** Measured under the viewer's ambient light of 900, on all eight trees, each built as it was before the fix (glossy leaves, the old tints) and as it is now. `skeleton.min_canopy_over_limbs` 1.25: foliage over the limbs among it was 0.94 to 1.22 before (the review called it one dark mass) and is 1.29 to 1.70 now, and the limit sits between; `tree_old_1` before (1.22) and `tree_2` now (1.29) are each within 0.04 of it. The lighter ambient does not separate limbs from leaves by itself: the ratio is the two colours', and it measured the same under 300. The tints are 1.39 times their old values in each sRGB channel, about twice as light: more than "a little", because taking the gloss off the leaf material (below) also took away the underside's reflected light (without the gloss and with the old tints the foliage is 0.67 to 0.88 of the limbs). It is about the least that passes: at 1.35 times `tree_2` measures 1.23. The pale limit (`conventions.toml`, `under_view`): at most 0.0002 of the leaf samples may be nearer grey than halfway from the palette's greyest swatch to white and twice as light as the typical unlit piece. With glossy leaves the trees measure 0.0009 to 0.022, and without, under 0.00001. It cannot see glare on the winter palette, whose own swatches are near white (0.00035 with gloss).
- **The leaf material has no gloss, and leaf normals are not lifted on pieces that face the ground.** The near-white pieces under `tree_1` were the sun's glare: Bevy's default reflectance on a flat piece the sun grazes, seen from the other side of the sun. `KHR_materials_specular` with a factor of 0 removes it and needs no cargo feature (ADR 4 as amended); it is a change to the glTF profile that **the owner should confirm**. Bark keeps its gloss. Separately, a piece's normal is no longer tipped toward the sky when its face is level or faces down (`corner_normals`), which lit a few pieces the sun could not reach; no check measures that.
- **Seams.** The generator marks seams on the bark (round every ring, and once along each stretch of a limb) and `tools/paint.py` unwraps along them. The grain does not match across the one seam that runs along each limb; it reads as one more furrow.
- **Seeds**: see each variant's brief.

Not measured, and judged on the contact sheet: that a pad's outline is serrated from the side, and that the skirt droops.
