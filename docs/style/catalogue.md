# Catalogue

What the pipeline is to build, as our own assets. The owner's direction (2026-10-05): the whole catalogue of the nature reference and of the rock reference is the target, not a sample of it. The shapes and how they are built are described in `rock-shapes.md` and `nature-shapes.md`; this file is the list and its state. Nothing from either pack is used: these are our own versions in our style (ADR 9).

An entry is a **family**: one generator and one brief, producing several assets from seeds and settings (ADR 13; `source/tree/` is the first). A family is done when its variants pass their gates and the owner has approved their contact sheets.

## Variants every family must cover

The owner's direction: cover all the variants the references offer, not only shapes.

| Kind | What varies | Applies to |
| --- | --- | --- |
| **Shape** | Seed: a different individual of the same kind. At least three per family. | Everything |
| **Size or growth stage** | Sapling, young, mature, old for plants; small, medium, large for rocks and dead wood. | Everything |
| **Season** | Summer green, autumn (yellow to orange to red), winter (bare branches, or snow lying on upward-facing surfaces), and dead or burnt. | Trees, bushes, ground plants, hanging growth |
| **Colour** | Other foliage and flower colours for the same shape, including unnatural ones for deep layers; stone kinds for rocks (grey, sandstone, dark, ice). | Everything |
| **Cover** | Bare, mossy, snow-capped. | Rocks, dead wood, trunks |

Season, colour and cover are meant to be changes of palette and painted shading on the same mesh wherever possible, so a variant costs a texture and not a new model. Winter-bare trees and snow that changes the outline are the exceptions.

## Rocks

| Family | To build | State |
| --- | --- | --- |
| Boulder | 3 or more variants in 3 sizes | The family `source/boulder` supersedes `source/rock` (several fused pieces, 322 triangles; reads as a stump, and is kept as a test fixture): `boulder_1` to `boulder_3`, 0.7, 1.2 and 1.9 m tall, each one convex skin of planes, 126 to 160 triangles; 40 of 40 seeds build at each size. They read as heavy lumps, but faceted, and about a third of the seeds as cut wedges. Not approved. |
| Standing stone | Slab and lozenge kinds, several heights | Three variants built from pieces (ADR 13): 2.6, 3.6 and 1.8 m tall, 172 to 204 triangles, bare stone, each with one or two foot blocks. Not approved. |
| Stepped spire | 3 or more, with foot blocks | Not started |
| Crag | 3 or more clusters | Three variants built from pieces (ADR 13): 3.0, 4.6 and 1.7 m tall, of 6, 8 and 5 pieces (4, 5 and 3 leaning prisms, the rest foot blocks), 394 to 634 triangles, bare stone. The largest needs a 2048 px texture. No covers. Not approved. |
| Arch | Lintel arch and wedged-block arch | Reworked after the owner refused the first three as constructed (trilithons). Three variants built from pieces (ADR 13), every piece a tipped lozenge: two lintel arches, a rough slab lying aslant from a low pile of blocks up to a taller pier, 6.0 and 9.4 m wide and 4.2 and 6.0 m tall, with 2.16 m by 2.2 m and 3.89 m by 3.0 m open for a player inside holes 3.23 and 4.48 m tall; and one wedged-block arch 5.8 m wide and 3.9 m tall, 1.72 m by 2.0 m open inside a hole 2.67 m tall. 7, 8 and 7 pieces, 568 to 596 triangles, 2048 px textures, bare stone. Checked for one hole right through, the opening, the span resting on both piers, and against a trilithon: the hole not a rectangle, the sides unlike in height, the top not level, little upright. Still wrong: a slab's and a keystone's outline is a pointed lozenge, `arch_2`'s slab is a long beam, the taller pier of a lintel arch is a post, and two of twelve seeds of the wedged kind do not build. Twelve seeds of each kind are in `benchmarks/out/arch_1_candidates.png` and `arch_3_candidates.png`. No covers. Not approved. |
| Rib | Single ribs and a paired arch | Not started |
| Table rock | 2 or more | Three variants built from pieces (ADR 13): 3.6, 6.4 and 2.4 m across and 2.9, 4.2 and 1.5 m tall, with 2.0, 3.0 and 0.9 m of open air under the cap; the largest on two necks and with a 2048 px texture; 288 to 500 triangles, bare stone. Under the viewer's light the underside and necks are in the cap's shadow and their paint does not read. No covers. Not approved. |
| Slab | Single and overlapped, several sizes | Three overlapped variants built from pieces (ADR 13): 2.6, 4.0 and 1.4 m across, 208 to 312 triangles, bare stone. No single slab, no covers. Not approved. |
| Stack | 3 or more | Three variants built from pieces (ADR 13), the first whose pieces stand on each other: 0.7, 1.1 and 0.32 m tall, of 4, 5 and 3 flat stones, 334 to 528 triangles, bare stone. All three pass their gates. Open: air shows in wedges at some joins, and the lowest stone reads as a plinth. No covers. Not reviewed by a second reader, not approved. |
| Block | A run of sizes, some cracked | Three sizes: 0.5, 1.0 and 2.0 m wide, 80 to 164 triangles, bare stone. The smallest is whole, one closed skin; the others are parted along one and two cracks into overlapping pieces (ADR 13). The cracks are straight slots, not wandering lines. No covers. Not approved. |
| Terrace | 2 or more | Not started |
| Pebble | A run of sizes | Three sizes, each one closed skin (not pieces): a low plate of six to eight leaning sides, a broad rim and a tipped cap, 0.12, 0.25 and 0.5 m across and a fifth as tall, 104 to 122 triangles, a 256 px texture, bare stone. Redone lower and rounder after the first review; `low` and `rounded` are checked against limits measured on the benchmark's round pebbles. Twelve seeds of each size are in `benchmarks/out/pebble_<n>_candidates.png` for the owner to pick from. No square pebbles, no covers. Not approved. |
| Rubble | 2 or more groups | Not started |

## Trees

Every tree family is wanted in four **growth stages** and in the seasons and colours above, as the reference has them.

| Family | State |
| --- | --- |
| Broadleaf | Three mature variants built (2,800 to 3,550 triangles), one sapling (stage 0.5, 3.5 m, two tufts in a row, 1,050 triangles, with its own limits for pieces in a tuft and bark seen), one young tree (1,850) and one old (5,340). One mature tree in autumn and in winter (snow on the foliage, as palettes); no bare winter tree, no snow on bark. Species is a recipe and growth stage a number in the spec. Not approved. |
| Umbrella tree | Not started |
| Conifer | Not started |
| Tall pine | Not started |
| Columnar tree | Not started |
| Weeping tree | Not started |
| Palm | Not started |
| Bottle tree | Not started |
| Jungle giant | Not started |
| Stilt-root tree | Not started |
| Bare tree | Not started |

## Smaller plants

| Family | State |
| --- | --- |
| Dome bush | Three variants built in three sizes, 0.75 to 1.5 m tall (664 to 1,432 triangles). Not approved. No flowers, seasons or colours yet. |
| Blade plant (ferns, understorey) | Three variants built in three sizes, 0.45 to 1.0 m tall (164 to 248 triangles): whole-leaf rosettes. Not approved. No fronds cut into leaflets, seasons or colours yet. |
| Grass tuft, tall grass, reeds | Grass tuft: three variants built in three sizes, 0.25 to 0.9 m tall (104 to 124 triangles). Not approved. Tall dry grass and reeds not started. |
| Leaf mat | Not started |
| Lily pad and flowers | Not started |
| Flower scatter | Not started |
| Mushroom, cactus and other biome markers | Not started |

## Climbing and hanging growth

| Family | State |
| --- | --- |
| Hanging sheet | Not started |
| Liana | Not started |

## Dead wood

| Family | State |
| --- | --- |
| Fallen and hollow logs | Not started |
| Log pile, stump, branches, roots | Not started |

## Not assets

Clouds, fog, light shafts and water are rendering, and belong to the game repo (ADR 8).
