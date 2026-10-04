# Nature shapes

A vocabulary of plant and scenery forms to build, and the construction habits behind them. It is a list in our own words, read off the product page and preview images of a commercial pack ([Poly Nature Pack](https://superhivemarket.com/products/poly-nature-pack-animated-stylized-pack) by Polyperfect: 824 assets, listed at $50 and up, royalty-free licence). The pack was not bought and nothing from it is used; the previews are kept locally in the git-ignored `docs/style/refs/nature-shapes/`.

Unlike the rock pack in `rock-shapes.md`, the owner offered this one as a reference for the **look** as well as the shapes.

## The shapes

**Trees**

| Shape | What it is |
| --- | --- |
| **Broadleaf** | A forked trunk carrying three to six separate rounded pads of foliage at different heights, with sky between them. |
| **Umbrella tree** | A bare leaning trunk that forks high into a wide, flat, shallow canopy (acacia). |
| **Conifer** | A straight trunk with tiers of drooping branches, widest at the bottom. |
| **Tall pine** | A long bare trunk with a small crown and a few stub branches at the top. |
| **Columnar tree** | A narrow upright flame of foliage hiding most of the trunk (poplar, cypress). |
| **Weeping tree** | A dome of long drooping strands that reaches almost to the ground. |
| **Palm** | A slender curved trunk with a fan of long fronds from one point. |
| **Bottle tree** | A fat, swollen trunk with a small crown of short branches (baobab). |
| **Jungle giant** | A very thick trunk with tall buttress roots and its crown out of view. |
| **Stilt-root tree** | A trunk standing on arching roots above water or mud (mangrove). |
| **Bare tree** | A branch skeleton with no foliage: dead, burnt or wintering. |

Each species comes in about four growth stages, from sapling to full size, and in colour variants (green, autumn, snow-covered) on the same meshes.

**Smaller plants**

| Shape | What it is |
| --- | --- |
| **Dome bush** | A low rounded mass of leaves, sometimes with flowers. |
| **Blade plant** | A rosette of long broad leaves from one point (ferns, jungle understorey). |
| **Grass tuft** | A fan of thin blades; also tall dry grass and reeds. |
| **Leaf mat** | A flat patch of small leaves lying on the ground or water. |
| **Lily pad** | A flat disc with a raised rim, from hand-sized to large enough to stand on, with flowers between. |
| **Flower scatter** | Tiny bright flowers, used as an accent. |
| **Mushroom, cactus, coral** | Small distinct props that mark a biome. |

**Climbing and hanging growth**

| Shape | What it is |
| --- | --- |
| **Hanging sheet** | A ragged curtain of leaves that hangs from an edge or drapes over a surface. |
| **Liana** | A thin vine looping between trunk and branch. |

**Dead wood**: fallen logs (some hollow, with plants growing on them), log piles, stumps, loose branches, exposed roots.

**Rocks and sky**: boulders, an arch, cliff blocks, stacked stones, ice blocks, and clouds as solid lumpy meshes in white and storm-grey.

## How they are built

- **Foliage is leaf-shaped polygons, not solid lumps and not noise.** Each visible leaf or leaf cluster is a flat, pointed, jagged-edged piece, large enough to read as a leaf from several metres. Hundreds of them overlap, pointing outward and downward, so every canopy has a serrated outline. In the previews they look like plain coloured geometry with no transparent texture; that is how it appears, and it cannot be confirmed without the files.
- **Canopies are several pads, with gaps.** A tree is a visible trunk and branches carrying separate clumps of foliage. Sky shows between the clumps.
- **Trunks are designed.** They taper, lean and bend, have five to eight flat sides, flare at the base into roots, and are darker than the foliage.
- **Colour comes from two computed effects.** The product page names shader pieces for a gradient by height and for shadow in crevices. Leaves at the top of a mass are yellow-green and lit; leaves underneath are deep green. This is the same idea as our painted shading (ADR 9).
- **Each piece is one flat colour, and neighbours differ.** The variation is between leaves, not within one.
- **Variety comes from stages and variants**, not from many unrelated models.

## How the scenes are built

From the jungle and swamp previews, which are the closest to what the pit's forested layers need:

- **A dark frame.** Trunks and large leaves close to the camera are in shadow and frame the view.
- **A lit middle.** Light falls in shafts through gaps in the canopy onto a few plants, with haze behind them.
- **Three heights of growth.** Dense ground cover at the foot of every trunk, shrubs and blade plants at waist to head height, canopy above. Bare ground is rare.
- **One accent colour**, in small amounts: magenta flowers in the jungle, pink lilies in the swamp.
- **Depth by haze.** Trunks further away are paler and bluer until they are flat silhouettes.

## What this changes for us

Two professional packs build foliage two different ways. The Quaternius benchmark uses leaf cards: flat pieces showing a painted cluster of leaves with transparent gaps, which need painted textures. This pack appears to use leaf-shaped geometry with flat colour, which needs no painted texture and no transparency, at a higher triangle count. The second suits a pipeline that generates everything by script, and research found no free painted leaf textures we could ship. Which one the tree generator uses is a decision for the tree brief.
