# Fallen log

A family (ADR 13): one generator, `generator.py`, and this brief. Its assets are `source/log_1`, `log_2` and `log_3`, three sizes drawn from different seeds, and `log_2_mossy`, `log_2` under moss. It is the first family of dead wood in `docs/style/catalogue.md`; the shape is from `docs/style/nature-shapes.md` ("fallen logs (some hollow, with plants growing on them)") and how trunks are built there: they taper and bend, have five to eight flat sides, and are dark.

## Purpose

A trunk lying on the ground of a forested layer of the pit (ADR 7). It is scenery a first-person player meets with their body: the small one is stepped over, the middle one is climbed over or walked along, and the large one is hollow and is crawled through or hidden in. Nothing about it moves, breaks or is picked up. Whether it can be climbed and what it collides as are data the pipeline does not write yet (ADR 7).

## Viewing

From 0.5 m (ADR 7): a player steps over it, stands on it, and at the largest size is inside it, with the wall of the hollow at arm's length all round. Typically from 3 to 10 m, across a clearing, where it has to read as a fallen trunk by its outline: long, low, bent, thicker at one end, with a ragged end and a stub or two. It is seen from above more than a tree is, because a player's eye (1.7 m) is over every size of it.

## Real-world size

Against a player 1.8 m tall. The origin is on the ground under the middle of the bounds; the log lies along x, its butt (the thick end, where it grew from the ground) at −x and its top (where the crown broke off) at +x, so the front view shows its side.

| Asset | Thick | Long | Beside a player | Butt | Hollow |
| --- | --- | --- | --- | --- | --- |
| `log_1` | 0.26 to 0.36 m | 2.6 m | Below the knee (0.5 m): stepped over without breaking stride. A fence rail's thickness, a young tree. | Sawn | No |
| `log_2` | 0.5 to 0.7 m | 4.4 m | Between knee and hip (0.9 m): climbed over with a hand on it, or walked along. Its root end stands 1.0 m, to the waist. | Torn out with its roots | No |
| `log_3` | 1.2 to 1.5 m | 6.4 m | To the chest: a wall to climb, 1.55 m at its highest. Hollow right through, 0.9 m clear inside: a player 1.8 m tall crawls or crouches through, and does not walk. | Broken | Right through |

A log a player could walk upright through would be 2.6 m thick, a jungle giant's; it is not built.

Thickness is the trunk's at the middle of its length, as the width of a circle with the area of its cross-section there. The bounds are taller than that: the butt is thicker than the middle, a stub may stand above the trunk, and `log_2`'s root plate stands well above it.

## Silhouette

What makes it a fallen log and not a cylinder with caps. Each is measured (`tools/log_checks.py`); the number is the least the brief accepts, not what the generator aims at.

1. **It lies.** Long and near level: the straight line from one end of the trunk to the other is within 6 degrees of level, the trunk is at least three times as long as it is thick, and at least 0.6 of its length touches the ground.
2. **It is settled into the ground.** Where it touches, it is cut off flat by the ground, as if sunk a little: the flat is at least 0.15 of the trunk's width there. The underside is not built round and resting on a line.
3. **It tapers.** The quarter of its length nearest the top is at most 0.88 as thick as the quarter nearest the butt.
4. **It bends.** Somewhere along it, the middle of the trunk stands at least 0.025 of its length off the straight line between its ends: 6 cm on the small log, 16 cm on the large. Trunks bend in plan, lift a little off the ground along a stretch, and twist.
5. **Its ends are ends.** The top is always broken: a ragged ring of splinters of unequal length, some standing out as a tongue, round torn wood. The butt is sawn (a flat cut, a little off square), torn out (the foot of the trunk flaring into three or four root stubs round a root plate) or broken. Both ends show wood, paler than the bark: at least half the cross-section there.
6. **Stubs.** One to three branch stubs of unequal length stand out of it, broken off, each ending in wood. None on its underside.
8. **Its outline runs evenly.** A trunk thins toward its top, with a swelling or a stretch lifted off the ground; it does not step in and out ring by ring like links. Along the stations its thickness, its width in plan and the height of its top each turn from thinning to thickening or back at most three times, counting steps of more than 0.04 of the thickness (`log_even`).
9. **A break is not a cut.** Where bark meets wood, the rim of a broken end reaches along the log at least half the trunk's thickness (or, on a thick log, three tenths of the end eighth the stations leave out, which is all the room a break has there); a sawn end's rim reaches at most 0.3 of it (`log_ragged`). A trunk breaks on a slant, with splinters of unequal length on it; a third of the solid logs snapped and split, half the trunk running on past the break.
7. **Hollow** (`log_3`): open from end to end, with a wall of thickness. Measured between the end eighths of its length: at least 4.5 m of it open at least 0.9 m both across and up, and the wall nowhere thinner than 7 cm. The inside is surface like the outside: closed, facing into the hollow, painted. A log whose spec has no `hollow` must show none.

Flat sides, seven to nine, with a soft edge along every corner, as the tree's trunk has (ADR 9): the same construction, so a log sits beside a standing tree as the same kind of thing.

## Style and colour

ADR 9: soft edges, painted shading. It sits beside the broadleaf (`source/tree`), whose bark is `#7a5a44`.

- `m_log_bark` `#75604f`: the tree's bark, greyer and a little paler, as dead bark weathers.
- `m_log_wood` `#ac9068`: the wood at the broken and sawn ends, on the stubs' ends and on the wall of the hollow. Clearly paler than the bark.

**Two materials, not one with a painted end.** A build script gives each material one flat colour and never paints (CLAUDE.md, ADR 10), and `tools/paint.py` paints every face from its material's colour; there is no way to ask it for a second colour inside one material. A palette strip, as foliage has (ADR 11), would do it at the cost of a new painting mode. The price of two materials is one more draw call per log.

## Painted shading

Asked for in the spec only (ADR 10, ADR 12); the generator writes flat colours, seams and the `grain` attribute.

1. Gradient: `#b9a8a0` at the ground to white at the top of the bounds, the tree's.
2. Edge light 0.2 over 0.03 m, crevice shadow 0.6 over 0.045 m (where a stub leaves the trunk, between roots): the tree's.
3. **Grain** 0.3, 0.02 m wide, the tree's bark. On the trunk it runs along the log, following the twist of its sides; on a stub along the stub; on the wall of the hollow along the log; on a sawn end round the middle, as rings; on a broken end outward from the middle, as torn fibre. No blotches (ADR 12).
4. **Close texels.** A player stands against all of a log, so all of it is below `close_height_m` (2.5 m, the tree's). `log_1` and `log_2` ask the tree's 250 texels per metre; `log_2` needs a 2048 px texture for it (about 9 m² of surface; a 1024 px texture half used gives 240). `log_3` has about 47 m², inside and out, and on a 2048 px texture half used that is 210 per metre: it asks 150, above the conventions' least of 100 and below the tree's.
5. The underside, flat on the ground, is hidden.

## Covers

Bare, and mossy (`docs/style/catalogue.md`). A mossy log is a palette variant of the bare one, as a mossy rock is (ADR 13; `source/crag/brief.md`, Covers): `log_2_mossy` names `log_2` as `palette_of`, builds the same mesh, and differs only in its `cover` and the growth keys of `painted_shading`. Moss `#7a8a4d` (the rocks'), from the ground up 0.2 m (three tenths of the trunk's thickness), in patches 0.15 m across on about 0.35 of what faces up and along 0.4 of the exposed upper edges, reaching 0.1 m in, 0.3 darker than the bark. A log lies, so its upper edges are those of the trunk's own upper sides, all along it, and not the top of its bounds (which is the root plate or a stub): the painter puts the growth along edges on every side that faces up, and `painted.growth_edges` measures it there, above the growth at the base. Moss grows on bark: the wood laid bare at the ends, on the stubs' ends and in the hollow (`log.wood`) takes none, at any height, and `painted.growth_wood` holds it to that. Plants growing on a log, which the reference shows, are not built: they are other assets set on it. Snow is not built.

## Parts

One object, one mesh, two materials. The trunk is one closed surface: a solid log's skin and its two ends; a hollow log's outside, the wall of the hollow and the two rings of wood that join them (a closed surface with a hole through it, so `watertight` holds and no `open_materials` are needed). Each stub is a closed tube of its own, its foot buried in the trunk's wall.

## Budget

Estimates (ADR 7): 700, 900 and 1,200 triangles. A trunk of eight sides and nine rings is about 260; a hollow adds about 130 for its wall; ends 40 to 80 each; a stub about 40.

## References

`docs/style/nature-shapes.md`, and the previews in `docs/style/refs/nature-shapes/`. The benchmark pack has no log; the nearest thing in it is the trunk of a dead or twisted tree, which stands. It is compared beside ours and is not like for like.

## Out of scope

Log piles, stumps, loose branches and exposed roots (the catalogue's other dead wood). A pocket hollow, open at one end to a depth: the `hollow` check measures a depth, but the generator builds only a hollow right through. Collision, the climbable flag, LODs, snow, plants on the log, a log thick enough to walk through.

## Numbers

Shared by every variant. Each variant's own rows are in its brief.

| Spec key | Value | From |
| --- | --- | --- |
| `family` | `"log"` | This brief |
| `bounds_tolerance_m` | `0.001` | 1 mm, as every asset |
| `materials.m_log_bark` | `"#75604f"` | Style and colour |
| `materials.m_log_wood` | `"#ac9068"` | Style and colour |
| `painted_shading.base_tint` | `"#b9a8a0"` | Painted shading 1 |
| `painted_shading.top_tint` | `"#ffffff"` | Painted shading 1 |
| `painted_shading.edge_light` | `0.2` | Painted shading 2 |
| `painted_shading.edge_width_m` | `0.03` | Painted shading 2 |
| `painted_shading.crevice_shadow` | `0.6` | Painted shading 2 |
| `painted_shading.crevice_width_m` | `0.045` | Painted shading 2 |
| `painted_shading.grain` | `0.3` | Painted shading 3 |
| `painted_shading.grain_width_m` | `0.02` | Painted shading 3 |
| `painted_shading.close_height_m` | `2.5` | Painted shading 4 |
| `painted_shading.hidden_underside` | `true` | Painted shading 5 |
| `log.bark` | `"m_log_bark"` | Style and colour |
| `log.wood` | `"m_log_wood"` | Style and colour |
| `log.max_taper` | `0.88` | Silhouette 3 |
| `log.min_bend` | `0.025` | Silhouette 4 |
| `log.min_grounded_share` | `0.6` | Silhouette 1 |
| `log.min_flat_share` | `0.15` | Silhouette 2 |
| `log.min_end_wood` | `0.5` | Silhouette 5 |
| `soft_edges` | `true` | Style and colour |
| `watertight` | `true` | Parts: every surface is closed |
| `attributes` | `["POSITION", "NORMAL", "TEXCOORD_0"]` | Painted shading: one texture |

## Decisions

There was no grilling session. Given by the owner on 2026-10-05, through the coordinator: the family, three variants differing by seed and size with at least one hollow, one mossy cover as a palette variant; what a fallen log is (slightly bent, tapering, a broken end and a root or sawn end, a stub or two, sunk a little into the ground, grain along it, paler wood at the ends); that it must not read as constructed; that expected values come from this brief and painted shading and grain are asked for in the spec.

Proposed by the agent, and open to change:

- The three sizes, which butt each has, and that only the largest is hollow, right through.
- Two materials (above).
- **Thresholds invented for the log**, none measured on a reference. In the spec: a taper of at most 0.88, a bend of at least 0.025 of the length, 0.6 of the length on the ground, a flat of 0.15 of the width, wood over half of each end, the stub counts, and for the hollow 0.9 m clear, 4.5 m deep and a 7 cm wall. In `conventions.toml` (`[log]`): 24 stations, the end eighths left out, 1 cm as touching the ground, 6 degrees as near level, three times as long as thick.
- Every painted value but the texture sizes and `log_3`'s 150 texels per metre is the tree's; the moss is the rocks', with a lower reach and smaller patches.
- That the butt is at −x on every seed.
- **Thresholds invented for the outline and the ends** (`conventions.toml`, `[log]`): a step of 0.04 of the thickness, at most three turns, a break reaching half the thickness or three tenths of the end left out, a saw cut at most 0.3. The break's limit was first written as half the thickness alone; a log 1.4 m thick has 0.77 m of end outside the stations and cannot hold a break of 0.7 m there with the tilt of its end ring, so the second term was added before any log was built to it. The log_3 of the first round fails `log_even` (4 turns) and passes `log_ragged` under the second term (0.27 and 0.23 of its thickness, 0.165 asked); the log_1 of the first round fails `log_ragged` (0.45 of 0.5).
- **What a seed draws**: the line (a bow, an S, or two stretches at a kink), whether the top snapped and split (a third of solid logs), whether the first stub is a limb half as thick as the trunk (a third of solid logs), taper 0.25 to 0.5, and the roots. The butt and the stub count are the spec's, so a family of twelve seeds from one spec shares them.
- **Bounds across are filled by the bend**, 0.03 to 0.13 of the length, and the log is refused if that leaves more than 3% to stretch; along and up it may still be stretched by up to 15% and 18%, as before.
- The root end: the tree's sweep (`source/tree`, `root_curve`) on four rings, three or four corners as fins, the one nearest up torn off at the top of the bounds; the plate between them is still wood, because Silhouette 5 asks wood over half of each end.
