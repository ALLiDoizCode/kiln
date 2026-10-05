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
| Boulder | 3 or more variants in 3 sizes | One built from several pieces, 322 triangles; reads as a stump more than a boulder. Not approved. |
| Standing stone | Slab and lozenge kinds, several heights | Not started |
| Stepped spire | 3 or more, with foot blocks | Not started |
| Crag | 3 or more clusters | Not started |
| Arch | Lintel arch and wedged-block arch | Not started |
| Rib | Single ribs and a paired arch | Not started |
| Table rock | 2 or more | Not started |
| Slab | Single and overlapped, several sizes | Not started |
| Stack | 3 or more | Not started |
| Block | A run of sizes, some cracked | Not started |
| Terrace | 2 or more | Not started |
| Pebble | A run of sizes | Not started |
| Rubble | 2 or more groups | Not started |

## Trees

Every tree family is wanted in four **growth stages** and in the seasons and colours above, as the reference has them.

| Family | State |
| --- | --- |
| Broadleaf | Three mature variants built (2,800 to 3,550 triangles). Not approved. No growth stages yet. |
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
| Blade plant (ferns, understorey) | Not started |
| Grass tuft, tall grass, reeds | Not started |
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
