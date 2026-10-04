# Built shapes: props and buildings

A vocabulary of made things to build, and the construction habits behind them. It is a list in our own words, read off the product page and preview images of a commercial pack ([Poly Fantasy Pack](https://superhivemarket.com/products/poly-fantasy-pack) by Polyperfect: 2,188 models, listed at $100 and up, royalty-free licence, Blender 4.0 to 5.0). The pack was not bought and nothing from it is used; the previews are kept locally in the git-ignored `docs/style/refs/built-shapes/`. The owner offered it as a reference for the look.

Its setting is a medieval town, which is not our game's. Take the way things are built, and the kinds of prop a lived-in place needs; the pit's own designs must be ours.

## What the pack contains

By its own asset list: 110 whole buildings; 690 modular kit pieces (castle 230, village 419, docks 24, prison 17); 185 nature pieces, including 60 mushrooms, 37 rocks, 28 trees and 19 vines; 1,167 props (crafts 313, battlefield 238, battle equipment 191, outdoor 91, furniture 87, flags 67, storage 57, statues 53, lights 42 and others); 26 people. Most props come in six colour variants.

## Props a lived-in place needs

| Kind | Examples seen | Use in our game |
| --- | --- | --- |
| **Storage** | Long plank crates with slatted lids, open trays, iron-bound chests, barrels upright and on racks, half-barrel tubs, sacks | Loot containers, base storage |
| **Work** | Workbench, anvil on a stump, grindstone, drying rack, cooking frame over a fire | Crafting stations |
| **Rest** | Rope-strung and plank beds, benches, stools, tables | Base furniture |
| **Light** | Lantern on a leaning post, hanging lantern on a bracket, brazier, campfire ring, wheel chandelier | Light sources, which matter a great deal in a pit |
| **Way-marking** | Signposts with pointed boards, flags, posts | Trails, claims |
| **Barrier** | Palisade stakes, plank fences, gates, hedges | Base defence |
| **Shelter** | Market awnings on poles, lean-to roofs, a small roofed well | Early shelter before walls |
| **Carrying and climbing** | Carts, ladders, cranes with rope | Hauling loot up the pit |

## How the props are built

- **From boards, not from boxes.** A crate is a set of separate planks with visible gaps between them, held by battens, straps and corner pieces. Our first crate was one block with a frame and recessed panels, which is why it read as plain.
- **Planks differ.** Widths vary, ends do not line up exactly, and a few sit slightly askew. Neighbouring planks are a shade lighter or darker.
- **Everything is chunky.** No part is thinner than a few centimetres; handles, straps and hinges are oversized.
- **Metal is a separate, darker piece** laid over the wood: hoops, bands, hinges, nail heads large enough to see.
- **Nothing is perfectly straight.** Posts lean, beams bow, tables sag a little. It reads as hand-made.
- **Two or three materials each**: wood, iron, and sometimes one accent (cloth, rope, a painted barrel).
- **Edges are softened**, and each part is one flat colour with a gentle gradient.
- **Sets, not singletons.** Barrels appear whole, stacked, on racks, cut into tubs and broken; one design gives many props.

## Buildings

Timber-frame houses on a stone base course, with pale plaster panels between dark beams, an upper floor that juts out over the lower, steep oversized shingle roofs with deep eaves, dormers, chimneys, outside stairs and small towers.

- **Each building has its own silhouette**, mostly from the roof: the roof is as tall as the walls or taller, and ridge lines are slightly bent.
- **The frame is the structure you see**: thick posts and beams with thinner infill between them. This is the same logic as a snapping base-building kit (ADR 7): frame members on the grid, panels between.
- **A kit builds them.** The pack's 419 village pieces are walls, roofs, windows, doors and trim that assemble into the whole buildings. Whole buildings also come as single optimised meshes for distant use.
- **From far away, towns read by roof shapes and clusters**, not by individual boxes. Our recreated towns were thousands of identical boxes and read as confetti.

## How the scene is built

From the cover image: cool fog between buildings and warm light spilling from doorways; grass tufts and scattered flat stones on the ground; props crowding the space between buildings; a rock face rising behind in haze.

## What this changes for us

- The crate should be rebuilt from planks, battens and straps when it is redone for the new style and the first-person camera.
- The base-building kit should be designed as frame members plus infill panels.
- Distant buildings need distinct roof silhouettes and clustering, and a simplified single-mesh version of each.
