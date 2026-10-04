# Free assets and tools for the seven recreation gaps

Research date: 2026-10-04. Audience: the owner, who has no 3D art background. Scope: the seven things that failed in every one of the nine scene recreations (rock, trees, foliage, close surfaces, clouds, brushwork, distant towns), and what free material exists to fix each.

Vocabulary follows `CONTEXT.md`. **`kiln`** is this repo (assets: build scripts, gates, GLB files). **`pit`** is the game repo (rendering: fog, clouds, light shafts, post-process). The split is [ADR 0008](../adr/0008-pipeline-and-game-are-separate.md). The style line is [ADR 0007](../adr/0007-game-target-and-metrics.md).

**How to read the evidence labels**

- **[run]**: I executed it on this machine on 2026-10-04 with `tools/bl` (Blender 5.2.2 LTS, headless, `--factory-startup`). Nothing was installed into Blender; extensions were unpacked under `benchmarks/research-samples/` and imported from there for the length of one process.
- **[raw]**: read as raw data, not through a summariser: GitHub API responses, the Blender Extensions catalogue JSON, the docs.rs item index, licence files inside downloaded archives, and one PDF converted with `pdftotext`.
- Unmarked statements with a link were read through a summarising fetch tool on 2026-10-04. Treat exact wording as one step less certain than **[raw]**.
- **[inference]**: my reasoning or recommendation.
- **unverified**: not confirmed against a primary source. Collected in [section 7](#7-unverified-items-and-things-wanted-but-not-found-free).

**Terms used, defined once**

- **Alpha / alpha mask**: a texture channel saying which pixels are see-through. A **leaf card** is a flat rectangle of mesh showing a painted picture of leaves, with everything around the leaves cut away by the alpha mask.
- **Atlas**: several pictures packed in one texture.
- **Normal**: the direction a point on a surface is treated as facing for lighting. **Custom normals** deliberately lie about it, for example making a hundred flat leaf cards light up like one smooth ball.
- **Bake**: compute something slow once (lighting, a procedural colour pattern) and store the result in a texture or in per-vertex colours.
- **Vertex colour**: a colour stored at each corner of the mesh instead of in a texture. No texture file and no UV map needed.
- **Volume / VDB**: a 3D grid of density values (how thick the cloud is at each point). OpenVDB (`.vdb`) is the standard file format for it.
- **Raymarching**: drawing a volume by stepping along each line of sight and adding up the density.
- **Post-process**: a filter run on the finished picture every frame.
- **Kuwahara filter**: a filter that replaces each pixel with the average of the calmest nearby patch. It flattens detail and keeps edges, which looks like paint. The **anisotropic** kind stretches the patch along the local direction of the picture, so the flattening follows edges like a brush would.
- **Strata**: the horizontal layers in rock. **Buttress**: a thick rib that braces a cliff or a trunk at its base.
- **Skeleton (of a tree)**: the trunk and branch lines before any thickness or leaves.
- **Signed distance field (SDF)**: a volume that stores, at each point, the distance to the nearest surface. Useful for carving and rounding shapes.

---

## 1. Summary

Five finds are worth acting on. Each was checked for licence, and the first four were run here.

| # | Find | Licence | What it unblocks |
|---|------|---------|------------------|
| 1 | **Rock from plane cuts, not noise.** Start from a block and slice it with a dozen random flat cuts (`bmesh.ops.bisect_plane`), then bevel. Core Blender, no add-on. **[run]**: a 162-triangle rock with deliberate flat planes, and a stack of six cut slabs that reads as strata with ledges (`benchmarks/research-samples/technique-probes/rock_probe.png`). | Our own code. Blender itself is GPL; the output is ours. | Failure 1. The "smeared clay" look comes from the method (noise displacement), and a different method removes it. |
| 2 | **Sapling Tree Gen** and **IvyGen**, two Blender-maintained ("Community") extensions. Both **[run]** headless on 5.2.2 without installing. Sapling gives a real trunk, forks and branch skeleton from one operator call with a preset; IvyGen grows ivy over the top of a test cube and down its side from one operator call. | GPL-3.0-or-later and GPL-2.0-or-later (tool code). Output geometry is not covered by the tool's licence in general ([GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.html#WhatCaseIsOutputGPL)). | Failures 2 and 3: branch structure, and growth that drapes over the surface it sits on. |
| 3 | **Bake to vertex colours in headless Cycles.** `bpy.ops.object.bake(..., target='VERTEX_COLORS')` returned `FINISHED` **[run]** after enabling the bundled Cycles add-on from the script. | Core Blender. | Failure 4, without breaking ADR 0007's "no textures" rule: colour variation, grime in creases and soft shadow stored per vertex. Megagon (Lonely Mountains: Downhill, board pick 6) describes the same idea: "A rough ambient occlusion pass is painted onto the vertices" ([80.lv interview](https://80.lv/articles/level-game-production-lonely-mountains-downhill)). |
| 4 | **Bevy 0.19's own volumetric fog**: `FogVolume` (a box of fog with an optional 3D density texture), `VolumetricFog` on the camera, `VolumetricLight` on lights ([docs.rs index](https://docs.rs/bevy/0.19.1/bevy/all.html) **[raw]**). Blender 5.2.2 imports `.vdb`, reads it through its bundled `openvdb` Python module, and converts it to a mesh **[run]**. CC0 cloud volumes exist (JangaFX, CGHeven). | Bevy: MIT OR Apache-2.0. JangaFX and CGHeven clouds: CC0 as stated on their pages. | Failure 5 and light shafts, first-party, with the camera able to sit beside or under the cloud (the two third-party cloud crates found cannot do this well). |
| 5 | **CC0 building kits with whole buildings and modular parts**: Kenney *Fantasy Town Kit* 2.0 (167 GLB files **[raw]**), KayKit *Medieval Hexagon Pack* (CC0 licence file in its GitHub repo **[raw]**), Quaternius *Medieval Village MegaKit*. Plus watabou's free *Medieval Fantasy City Generator*, which exports street and block layouts as JSON. | CC0 for the three kits. Generated maps: "use ... as you like ... include in your commercial rpg adventures" (watabou). | Failure 7: buildings with roofs and a street plan to place them on, in place of scattered boxes. |

Two things this research did **not** find free, and which shape the recommendations: a **CC0 brush-stroke alpha atlas**, and a **maintained Bevy crate for painterly post-processing**. Both gaps are in [section 7](#7-unverified-items-and-things-wanted-but-not-found-free).

One decision the owner has to make before most of section 2 can be used: ADR 0007 says "flat-colour low-poly ... Atmosphere comes from lighting and fog in the engine, not from textures". Leaf cards, painted rock textures and brush-stroke atlases are all textures. Each section below marks which options stay inside ADR 0007 and which need it changed.

A second, smaller decision: `tools/bl` runs Blender with `--factory-startup --offline-mode`, which loads no extensions. Using Sapling or IvyGen means pinning their zip files the way `tools/install_tools.sh` pins Blender, and importing them from the build script. I did exactly that by hand; it works **[run]**.

---

## 2. The seven failures

Column key. **Kind**: A = ingredient to ship or build from, B = tool that generates, C = reference from the people who made a look. **Repo**: where it belongs.

### Failure 1. Rock and cliff forms

What the references have and noise cannot give: flat planes meeting at hard edges, ledges, strata, overhangs.

| Option | Kind | Publisher | Licence | Works headless in 5.2.2 / format | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **Plane-cut chiselling** in the build script: `bmesh.ops.bisect_plane(..., clear_outer=True)` then `holes_fill`, then a Bevel modifier | B | Blender (core API) | Blender is GPL; output is ours | **[run]**. 14 cuts on a block gave 162 triangles with clear planes. Six cut slabs stacked with small offsets and twists gave strata and overhangs at 60 to 88 triangles each. | Best fit. Planes are placed by rule (count, tilt range, depth range), so they can be checked by a gate. Matches board picks 4, 6 and runner-up 15. Stays inside ADR 0007. | `kiln` |
| **Decimate modifier, Planar mode** (`decimate_type='DISSOLVE'`, about 25 degrees) on a noise mesh, after [Greg Zaal, "Procedural Stylized Rock Modeling", 2013](https://blog.gregzaal.com/2013/09/20/procedural-stylized-rock-modeling/) | B, C | Greg Zaal (author's own blog) | Article has no licence statement; the technique is core Blender | **[run]**, one untuned attempt: triangles fell from 5,120 to 2,014 but the rock still read as a lumpy blob. Zaal's recipe has two more steps I did not reproduce (a low-frequency displacement first, and an ordinary Decimate before the planar one). | Worth one more try with his full recipe. His cliff variant is "random vertical and horizontal cuts", which is the plane-cut idea again. | `kiln` |
| **SDF grid nodes** in Geometry Nodes: `Mesh to SDF Grid`, `SDF Grid Boolean`, `SDF Grid Fillet`, `Grid to Mesh` | B | Blender (core) | as above | Node types present in 5.2.2 **[run]** (listed from `bpy.types`). Not exercised. | For welding many chiselled blocks into one cliff without seams, then re-cutting. Try only if stacking separate slabs shows gaps up close. | `kiln` |
| **Cell Fracture** extension, v0.2.1 | B | Blender "Community" ([catalogue](https://extensions.blender.org/api/v1/extensions/) **[raw]**) | GPL-3.0-or-later (tool) | **[run]**: `bpy.ops.object.add_fracture_cell_objects` split a cube into 8 flat-faced cells. Min Blender 4.2.0, no max. | Fracture lines and blocky rubble at a cliff foot. | `kiln` |
| **Extra Mesh Objects** rock generator, v0.4.1 (`bpy.ops.mesh.add_mesh_rock`) | B | Blender "Community" | GPL-3.0-or-later | **[run]**: produces a 6,144-triangle smooth lump. | **Reject.** It is the same failure we already have (`_probe/rock.png`). | n/a |
| **A.N.T. Landscape** v0.2.0 (`mesh.landscape_add`, `mesh.eroder`) and **Erosion terrain generator** v1.0.0 | B | Blender "Community"; Lucas Furer ([repo](https://github.com/LucasFurer/my_blender_addon), Apache-2.0 on GitHub, GPL-3.0-or-later in the extension manifest **[raw]**) | GPL-2.0-or-later; see left | Both **[run]**. A.N.T. made a 128x128 terrain and ran 30 erosion iterations. The erosion extension made a 129,032-triangle terrain; it requires Blender 5.2.0 or later and is a single-author v1.0.0. | Erosion carves gullies into **height-field** terrain (a surface with one height per point). It cannot make overhangs. Use for far backdrop hills only. The pit's terrain is generated in `pit`, so this has little place in `kiln`. | `kiln` (backdrops) |
| **Stylized Rock Generator** ([mertnizamoglu/Stylized-Rock-Blender](https://github.com/mertnizamoglu/Stylized-Rock-Blender)) | B | Mert Nizamoglu | GPL-3.0 **[raw]** | Not run. One Python file that applies a modifier stack with Cliff, Boulder and Pebble presets. README says "Blender 3.0.0 or newer"; last push 2025-07-22; 20 stars. | Read it for the modifier order and preset numbers; do not depend on it. | `kiln` (reference) |
| **Kenney *Nature Kit*** 1.0: 329 glTF models including 56 cliff pieces (blocks, corners, steps, caves, waterfall tops) and 23 rocks | A | Kenney ([page](https://kenney.nl/assets/nature-kit)) | CC0 (`License.txt` in the zip **[raw]**; site-wide statement at [kenney.nl/support](https://kenney.nl/support)) | 10.5 MB zip, glTF, FBX, OBJ, DAE, STL. Downloaded; preview image viewed. Import into Blender not run. | Flat-colour low-poly cliffs built as a snapping kit. Closest free example of ADR 0007's style applied to cliffs. Use as a second benchmark beside Quaternius, and as a pattern for a cliff **modular kit**. | `kiln` |
| **Poly Haven** rock and cliff scans (37 models tagged `rocks`, for example `namaqualand_cliff_01`, `rock_face_01`, `coastal_cliff_04`) | A | Poly Haven ([API](https://api.polyhaven.com/assets?t=models) **[raw]**) | CC0 ([licence page](https://polyhaven.com/license): "You can redistribute them ... or even in a product you sell") | glTF and .blend downloads; photo-scanned, high triangle counts. Not downloaded. | Wrong style to ship. Good as a **shape reference**: where real cliffs break, how strata tilt. | `kiln` (reference) |
| **Megagon Industries on Lonely Mountains: Downhill** | C | Daniel Helbig and Jan Bubenik, interviewed by 80.lv ([article](https://80.lv/articles/level-game-production-lonely-mountains-downhill)) | reference only | n/a | Confirms the target is reachable with no textures: "We don't use classic textures, normal maps or sprites/billboards in the game". Little on how rock is modelled. | reference |

**Pick: plane-cut chiselling written into our own build scripts.** It has no dependency, it ran, it produces the planes and ledges the references have at a triangle count below Quaternius's rocks, and its parameters are numbers a spec and a gate can hold. Use Kenney's cliff kit and the Quaternius rocks as the benchmarks to beat.

### Failure 2. Tree and trunk forms

What is needed: a skeleton first (trunk, forks, branches), thickness second, foliage hung on the branch ends third, with gaps left between.

| Option | Kind | Publisher | Licence | Works headless in 5.2.2 / format | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **Sapling Tree Gen** v0.3.7 (`bpy.ops.curve.tree_add`) | B | Blender "Community" (manifest website `projects.blender.org/extensions/add_curve_sapling` **[raw]**) | GPL-3.0-or-later (tool). Preset files are GPL-2.0-or-later. | **[run]**. Default call: tree in 0.1 s. With the bundled `japanese_maple` preset passed as keyword arguments: a spreading, forked, many-branched tree in 5.2 s (`_probe/sapling_japanese_maple.png`). Nine presets ship (maples, willow, birch, fir, pine, aspen, callistemon). The `willow` preset failed with an argument type error in my loader. Min Blender 4.4.0, no max. | Best fit for the skeleton. It is the long-standing Weber and Penn style generator with about 100 parameters for forks, curvature, taper and branch levels. **Caveat:** output is curves with round bevels; the maple preset evaluated to 747,696 trunk triangles and 213,600 leaf triangles. Budget work is needed: lower `bevelRes` and `resU`, convert to mesh, decimate, and replace its leaves with our own cards. | `kiln` |
| **Generate Tree Plugin** v1.1.5 (`bpy.ops.treegen.generate`, settings on `scene.tree_generator_settings`) | B | YGForge ([repo](https://github.com/YGForge/LowPolyTreeGen)) | GPL-3.0-or-later in the extension manifest **[raw]**; the GitHub repo has no licence file | **[run]**. Makes a low-poly trunk with a bend, buttress-like roots, forked branches and faceted leaf clumps; wood totals about 5,000 triangles (`_probe/lowpolytree.png`, `lowpolytree2.png`). Min Blender 5.0.1. | Already in ADR 0007's style, and the only tool found that makes **roots**. Its foliage is faceted lumps, which is our "pom-pom" failure, so take the wood only. Maturity is low: one author, zero stars, last push 2026-09-21. | `kiln` |
| **Space colonization tree generator** v1.0.0 | B | "LS" (catalogue **[raw]**) | GPL-3.0-or-later | **[run]**: grew a 1,229-vertex skeleton (edges only) inside a sphere I supplied as the crown volume. Has a "Skin skeleton" option I did not test. Archive files dated 2025-07-18. | The algorithm grows branches toward points scattered in a shape you choose, so the **crown silhouette is designed**, not random. Good for trees that must fit a composition. Needs our own thickness step. | `kiln` |
| **Modular Tree** v5.5.2 | B | Brandyn Britton ([GoodPie/modular_tree](https://github.com/GoodPie/modular_tree), fork of [MaximeHerpin/modular_tree](https://github.com/MaximeHerpin/modular_tree)) | GPL-3.0-or-later | **Failed in my probe**: with its compiled `m_tree` wheel on the path, `mtree.quick_generate` raised "id properties not supported for this type". It may work when installed properly; **unverified on 5.2.2**. Requires 4.3.1 or later; last push 2026-08-06. | Node-based and capable, but it depends on a compiled library per platform. Not worth the risk while Sapling works. | n/a |
| **Easy Tree** v1.0.1 | B | Jacob Johnston | GPL-3.0-or-later (`LICENCE.txt` in the zip **[raw]**) | Not run. It is a Geometry Nodes group ("Simple Tree Generator") inside `assets.blend`, driven by named sockets, so it can be appended and set from Python **[inference]**. Bundles ambientCG bark and leaf textures. Min Blender 4.5.0. | Fallback if a Geometry Nodes tree is preferred over an operator. | `kiln` |
| **ez-tree** v1.1.0 | B | Daniel Greenheck ([repo](https://github.com/dgreenheck/ez-tree)) | MIT **[raw]**. Bark textures are ambientCG CC0; leaf textures (`ash`, `aspen`, `oak`, `pine` PNG) are "licensed under the project's own license" ([textures/LICENSE.md](https://github.com/dgreenheck/ez-tree/blob/main/src/app/public/textures/LICENSE.md) **[raw]**) | JavaScript and Three.js. The web app exports GLB; the library is on npm as `@dgreenheck/ez-tree`. Running it from Node with no browser is **unverified**. 1,680 stars, last push 2026-07-16. | The only MIT option, and it has twist and "gnarliness" parameters for trunks. It sits outside Blender, which breaks "one build script per asset" unless the GLB is imported and re-checked. Its four leaf textures are MIT and could be shipped. | `kiln` |
| **tree-gen** | B | Charlie Hewitt ([friggog/tree-gen](https://github.com/friggog/tree-gen)) | GPL-3.0, plus this sentence in the README: "any models generated using the tool are free for use without restriction in any context apart from direct sale as assets" | Not run; Blender add-on; last push 2025-07-11; no 5.x statement found. | Skip: no advantage over Sapling and an unusual output condition. | n/a |
| **Quaternius** tree packs beyond the benchmark: *Stylized Tree Pack*, *Ultimate Stylized Nature Pack* (63 models, includes .blend) | A | Quaternius ([site](https://quaternius.com/), [pack page](https://quaternius.com/packs/ultimatestylizednature.html)) | CC0 as stated on each pack page | FBX, OBJ, Blend, glTF. Not downloaded (the brief said not to re-research the benchmark pack). | More trunk and canopy shapes to compare against. | `kiln` (benchmark) |
| **Poly Haven** trees (20 models, for example `jacaranda_tree`, `island_tree_01`, `quiver_tree_01`), roots (`pine_roots`, `root_cluster_01`) and stumps | A | Poly Haven | CC0 | Scanned or realistic; glTF. Not downloaded. | Shape reference for forks, roots and twist. Wrong style to ship. | `kiln` (reference) |

**Pick: Sapling Tree Gen for the skeleton, with our own thickness, roots and foliage on top.** It is maintained under the Blender project, it ran here, and its presets already show forks and spreading crowns. Runner-up: Generate Tree Plugin, mainly as readable source for how to build roots.

### Failure 3. Foliage

Three separate problems: (a) clusters with a real silhouette, (b) growth that follows a surface, (c) patches of colour shaped like brush strokes.

| Option | Kind | Publisher | Licence | Works headless in 5.2.2 / format | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **IvyGen** v0.1.5 (`bpy.ops.curve.ivy_gen`, settings on `window_manager.ivy_gen_props`) | B | Blender "Community" | GPL-2.0-or-later (tool) | **[run]**. Seeded at the 3D cursor beside a subdivided cube; ivy climbed the side, spread across the top and hung over the edges in 1.5 s (`_probe/ivy2.png`). Min Blender 4.2.0. Archive files dated 2024-05-14. | Direct answer to "drapes over and follows the surface". It has weights for gravity, adhesion and branching. **Caveat:** defaults gave 2.1 million curve triangles and 370,000 leaf triangles. Use it for the **paths** only (thin the curve, drop its leaves) and hang our own cards along them. | `kiln` |
| **Core Geometry Nodes**: `Distribute Points on Faces`, `Raycast`, `Sample Nearest Surface`, `Instance on Points`, `Curve to Mesh` | B | Blender (core) | Blender GPL; output ours | Node types present in 5.2.2 **[run]**. Not exercised here; scattering already works in the recreations. | For moss and hanging vines: scatter points on down-facing or up-facing faces only (by normal), drop a curve from each, instance cards along it. No add-on. | `kiln` |
| **Bagapie** v11.0.12 (ivy generator, scattering, 50+ tools) | B | Antoine Bagattini | GPL-3.0-or-later (`LICENSE` in the zip **[raw]**) | Not run. Declares `network` permission; min Blender 5.0.0. Ships a Geometry Nodes ivy in `BagaPie_IvyGenerator.blend`. | Second ivy option if IvyGen's old algorithm proves hard to control. Larger and UI-centred. | `kiln` |
| **Atlas2Mesh** v1.1.0 | B | BHiMAX | GPL-3.0-or-later | Not run. Its operators (`spriteuv.detect_alpha_regions`, `spriteuv.build_shape_meshes`) trace alpha shapes in an atlas into mesh cards. Min Blender 4.2.0. | Turns a painted leaf-cluster picture into a card cut to the cluster's outline, which wastes fewer see-through pixels than a rectangle. Read the code; the same can be done in our script. | `kiln` |
| **"Cool Leaves Textures"**: four 1024x1024 PNGs with alpha, each one painted leaf cluster in a different colour | A | Sinestesia on OpenGameArt ([page](https://opengameart.org/content/cool-leaves-textures)) | CC0 | Downloaded and viewed: a dense hand-painted clump of pointed leaves with a ragged, readable outline, in green and in teal. About 1.3 MB each. | The only **painted cluster with a real silhouette** found under CC0. Use as the card texture for a first test beside Quaternius's leaf textures. | `kiln` |
| **ambientCG leaf and foliage atlases** (`LeafSet` series including ivy `LeafSet017` and `LeafSet029`, `Foliage001` to `008`, `PineNeedles001`) | A | ambientCG ([API](https://ambientcg.com/api/v2/full_json?q=Foliage) **[raw]**) | CC0 1.0 ([licence](https://docs.ambientcg.com/license/): "You can include the raw files in your project, for example a video game") | Downloaded `LeafSet029` (1K PNG, 9.8 MB) and `Foliage001` (1K JPG, 3.9 MB). Viewed: nine separate photographed ivy leaves with a clean black-and-white opacity mask; nine grass blades likewise. | Photographs of **single leaves**, not clusters, so the colour maps are the wrong style. The **opacity masks** are useful on their own as accurate leaf outlines to fill with flat palette colours. | `kiln` |
| **Quaternius leaf textures** (already in `benchmarks/quaternius-stylized-nature/Textures/`) | A | Quaternius | CC0 (licence file in the pack) | Already measured in the benchmark. | Baseline to build on, per the brief. | `kiln` |
| **Custom normals on leaf cards**: Data Transfer or Normal Edit modifier copying normals from a rounded hull onto the cards | B | Blender (core) | as above | `DATA_TRANSFER` and `NORMAL_EDIT` modifier types and the exporter's `export_normals` option are present in 5.2.2 **[run]**. The transfer itself and the round trip to Bevy were not run. | Removes the "polygon confetti" look: every card in a clump is lit as part of one soft shape, so the clump shows a light side and a dark side. Widely described by game artists; I found no first-party write-up I could open (see section 7). | `kiln` |
| **Megagon on foliage as geometry** | C | Megagon Industries via [80.lv](https://80.lv/articles/level-game-production-lonely-mountains-downhill) | reference only | n/a | "every leaf on a tree is actually geometry"; "several areas in the game have well over a million triangles on the screen". Shows the no-texture route is real, and what it costs. | reference |
| **`bevy_feronia`** 0.8.4 | B | Nico Zweifel ([repo](https://github.com/NicoZweifel/bevy_feronia)) | MIT OR Apache-2.0 **[raw]** | Bevy crate: scattering, wind, foliage materials, LOD. `Cargo.toml` on the `dev` branch depends on Bevy crates 0.19.0 **[raw]**; the README's table still lists 0.18. README: "I wouldn't personally use this in production quite yet". | Engine-side wind and scattering if `pit` wants them later. | `pit` |

**Pick: painted leaf-cluster cards with normals copied from a hull, hung on Sapling branch ends, plus IvyGen paths for anything that must cling or hang.** Start with the CC0 "Cool Leaves" clump and the Quaternius textures. This needs an alpha-masked texture, so it needs ADR 0007 amended for foliage. The route that stays inside ADR 0007 is Megagon's: every leaf as flat-coloured geometry cut to an ambientCG leaf outline, at a much higher triangle cost.

### Failure 4. Surfaces seen up close

| Option | Kind | Publisher | Licence | Works headless in 5.2.2 / format | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **Cycles bake to vertex colours** (`bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, target='VERTEX_COLORS')`; also `type='AO'`) | B | Blender (core; Cycles is a bundled add-on in `scripts/addons_core/cycles`) | Blender GPL; output ours | **[run]**. `--factory-startup` lists only EEVEE, so the script must call `addon_utils.enable("cycles")` first; after that both an image bake and a vertex-colour bake returned `FINISHED` on CPU. The exporter has `export_vertex_color` and `export_active_vertex_color_when_no_material` options **[run]**. | Best fit. Darken creases, lighten upward faces, add slow colour drift from a noise node, and store all of it per vertex. No UVs, no texture file, ADR 0007 intact. Detail is limited to the mesh's vertex density. | `kiln` |
| **Cycles bake to an image** from procedural shader nodes (Brick, Voronoi, Noise, Wave, Gabor textures; Bevel and Ambient Occlusion nodes) | B | Blender (core) | as above | **[run]**: a Voronoi-driven colour baked to a 256x256 PNG (`clouds/bake_test.png`). Shader node types listed from 5.2.2. | For paving, planks and masonry where vertex density is too low. Needs UVs and a texture, so it needs the spec to list them (ADR 0004) and ADR 0007 amended. | `kiln` |
| **Hand-painted rock textures** (4 tileable sets, 1K and 2K, each with normal, height and roughness maps) | A | rubberduck on OpenGameArt ([page](https://opengameart.org/content/handpainted-rock-textures)) | CC0 | Downloaded the 1K zip (16.6 MB) and viewed all four colour maps: rounded cobbles, cracked slab, small pebbles, and one banded orange set that reads as wood or sandstone. Clearly painted, with placed highlights. | A direct sample of "painted colour variation and placed highlights". Good as a look target for our own bakes and usable as shipped textures. The same author has more CC0 sets (for example "stylized hand painted stone blocks"); not checked one by one. | `kiln` |
| **3dtextures.me** stylised and hand-painted categories (stylised bark, ground, cliff rock, wood planks) | A | João Paulo / "Gendo" ([about page](https://3dtextures.me/about/)) | "All textures on this site are licensed as CC0" | Not downloaded; the site says textures are downloaded one by one. Hosting and file sizes **unverified**. | Larger stylised library for bark, ground and planks. | `kiln` |
| **Lynocs texture pack**: 464 stylised textures with seven maps each, about 3.7 GB in 49 zips | A | Lynocs on itch.io ([page](https://lynocs.itch.io/texture-pack)) | CC0 1.0, with the author's note "Just don't sell these as it is" | Not downloaded. The page says the textures are **AI-assisted**. | Wide coverage, but the extra sentence conflicts with CC0's wording, and AI-assisted origin is a provenance question for a public repo. Treat as reference until the owner decides. | reference |
| **ambientCG** and **Poly Haven** photographic materials (bark, rock, paving, moss, planks; Poly Haven has 864 textures, ambientCG 2,000+) | A | ambientCG; Poly Haven | CC0 both | Standard PBR texture sets. ambientCG atlases downloaded (above). | Wrong style as they are. Possible input to a paint filter to make stylised textures (see failure 6) **[inference]**, not tested. | `kiln` |
| **Material Maker** | B | Rodolphe Suescun ([repo](https://github.com/RodZill4/material-maker), [command-line doc](https://rodzill4.github.io/material-maker/doc/command_line.html)) | MIT **[raw]** | Standalone procedural texture tool built on Godot; 5,962 stars, last push 2026-10-03. Documents `--export-material --target <engine> -o <dir> <files>`. Whether that runs with no window is **unverified**. | A second way to author tileable painted textures as node graphs kept in git. Adds a tool outside Blender. | `kiln` |
| **Megagon: ambient occlusion in vertices** | C | Megagon via [80.lv](https://80.lv/articles/level-game-production-lonely-mountains-downhill) | reference only | n/a | "A rough ambient occlusion pass is painted onto the vertices, which often helps to define the volume a bit more." This is the manual version of the first row. | reference |

**Pick: bake ambient occlusion and procedural colour drift into vertex colours.** It ran, it needs no ADR change, and a shipped game on the style board does the same thing by hand. Move to baked image textures only for surfaces where vertices are too sparse.

### Failure 5. Clouds

Clouds are a rendering problem, so most of this belongs to `pit`. `kiln`'s part is supplying cloud **shapes**. glTF has no way to carry a volume, so a VDB must be turned into a mesh shell, a set of cards, or a 3D texture before it reaches Bevy **[inference]**.

| Option | Kind | Publisher | Licence | Format, size, verification | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **Bevy `FogVolume` + `VolumetricFog` + `VolumetricLight`** | B | Bevy ([FogVolume](https://docs.rs/bevy/0.19.1/bevy/light/struct.FogVolume.html), [VolumetricFog](https://docs.rs/bevy/0.19.1/bevy/light/struct.VolumetricFog.html)) | MIT OR Apache-2.0 | First-party in 0.19.1. `FogVolume` has `density_texture: Option<Handle<Image>>` ("Optional 3D voxel density texture"), `density_texture_offset` for scrolling, `fog_color`, `light_tint`, `absorption`, `scattering`. The `fog_volumes` example loads `volumes/bunny.ktx2` **[raw]**. | Best fit for clouds **inside the pit**: a shaped box of fog the player can stand beside, lit by the sun with visible shafts. `light_tint` and `fog_color` are the levers against "grey". Performance on a GTX 1660 is **unverified**. | `pit` |
| **JangaFX free VDB "Cloud Pack"**: 10 cloud variations, 104 MB | A | JangaFX ([page](https://jangafx.com/software/embergen/download/free-vdb-animations)) | "These free VDB simulations are licensed as CC0 (Public Domain)" | `.vdb`. Hosted on MediaFire, so not scriptable; **not downloaded**. | Source shapes for density textures or shells. CC0 means the files, or anything made from them, can live in the public repo. | `kiln` |
| **CGHeven "Free Cloud VDB Pack Vol. 1"**: 10 cumulus clouds | A | CGHeven, Ammar Khan ([post](https://cgheven.com/blog/free-cloud-vdb-pack-vol-1-10-hero-clouds), dated 2025-07-27) | "100% CC0"; "free, no signup" | `.vdb`. Sizes not stated on the page; **not downloaded**. | Second CC0 source. | `kiln` |
| **Walt Disney Animation Studios cloud data set** | A | Disney ([page](https://www.disneyanimation.com/resources/clouds/), [licence PDF](https://media.disneyanimation.com/uploads/production/data_set_asset/6/asset/License_Cloud.pdf)) | **CC BY-SA 3.0 Unported** (PDF read with `pdftotext` **[raw]**: "licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License") | One very detailed cumulus cloud in `.vdb` at several resolutions; single zip, large. Not downloaded. | Commercial use is allowed with attribution, but **share-alike** means anything derived from it must carry the same licence. Use as a reference for what a good cloud volume looks like; do not derive shipped assets from it. | reference |
| **OpenVDB sample models** (`smoke.vdb` 2 MB, `bunny_cloud.vdb` 74 MB, and others) | A | Academy Software Foundation ([downloads](https://www.openvdb.org/download/)) | No per-model licence on the page; treat as **reference-only** | Downloaded `smoke.vdb` (2.6 MB). | Test data only. Used for the run in the next row. | test data |
| **Blender volume tools**: `bpy.ops.object.volume_import`, Volume to Mesh modifier, the bundled `openvdb` Python module, Geometry Nodes `Points to Volume`, `Volume to Mesh`, `Distribute Points in Volume` | B | Blender (core) | Blender GPL; output ours | **[run]** on `smoke.vdb`: import succeeded, the `openvdb` module read the grid list (`density`, fog volume), and Volume to Mesh produced a 5,004-vertex shell. | Three uses: (1) read a CC0 cloud's density grid and write it out as a 3D texture for `FogVolume`; (2) make a low-poly shell mesh for far clouds; (3) build our own cloud volumes from scattered points with flat bottoms. The step from grid to a KTX2 3D texture Bevy loads was **not run**. | `kiln` |
| **`bevy_weather`** 0.2.0 | B | etwodev ([repo](https://github.com/etwodev/bevy_weather)) | MIT OR Apache-2.0 (`Cargo.toml` **[raw]**; GitHub's licence detector shows MIT) | Depends on Bevy 0.19.1 **[raw]**. Clouds are "raymarched through a curved planetary shell above the camera"; "Flying through the layer works but is not the case it is tuned for". 10 commits, 1 star, last push 2026-09-16. | Built for a sky seen from the ground. The pit needs cloud decks **below** the viewer. Read its shaders; do not depend on it. | `pit` |
| **`bevy-volumetric-clouds`** 0.2.0 | B | Erik Vroon ([repo](https://github.com/evroon/bevy-volumetric-clouds)) | MIT | Released 0.2.x is for Bevy 0.18 per the README; `master` depends on 0.19.0 **[raw]**. "The clouds are drawn on a skybox that does not take the depth buffer into account yet. Therefore, it's not yet possible to 'fly' into the clouds." Render resolution fixed at 1920x1080. 54 stars. | Same limit, more strongly. Useful as a working Bevy port of the Horizon technique to read. | `pit` |
| **Easy Clouds** v2.2.0 | B | LunarKitten ([Codeberg](https://codeberg.org/LunarKitten/EasyClouds)) | GPL-3.0-or-later | Blender extension that builds procedural cloud volume shaders, including one named "Colored Shadow Volume". Not run. Renders in Blender only. | For `kiln` review renders and for baking cloud cards. Look at its coloured-shadow shader for the "bright top, tinted shaded side" look. | `kiln` |
| **"The Real-time Volumetric Cloudscapes of Horizon: Zero Dawn"** | C | Andrew Schneider, Guerrilla Games, SIGGRAPH 2015 ([course page with PDF, 5 MB](https://advances.realtimerendering.com/s2015/index.html)) | reference only | Slides. | The standard write-up for raymarched clouds with shape control; what both crates above implement. Realistic, not painted. | `pit` |
| **"'Genshin Impact': Crafting an Anime-Style Open World"** (GDC 2021) | C | miHoYo ([video](https://www.youtube.com/watch?v=-JFyAdI_rO8)) | reference only | Video. A search summary says it covers stylised clouds built from artist-drawn silhouettes with light and rim-highlight maps. I could not read the page itself, so the content is **unverified**. | The nearest first-party description of anime clouds found. Watch before designing cloud cards. | `pit` |

**Pick: `FogVolume` with a 3D density texture for clouds inside the pit, shapes taken from the CC0 JangaFX or CGHeven volumes and flattened underneath.** It is first-party, and it is the only option found that puts the camera beside or below the cloud. The painted look (ragged flat footprint, bright top, coloured shadow side) will come from the tint settings and from the shape, and that part is unproven. For clouds far away in open sky, painted cards are the cheaper route, and no free painted cloud texture set was found.

### Failure 6. Brushwork

The experiment's finding stands: a filter over the whole picture cannot invent strokes. Strokes have to exist somewhere as shapes. There are three places to put them.

| Where the strokes live | Option | Kind | Publisher | Licence | Verification | Fit | Repo |
|---|---|---|---|---|---|---|---|
| In the final picture | **Anisotropic Kuwahara as a Bevy `FullscreenMaterial`** | B | Bevy trait: [FullscreenMaterial](https://docs.rs/bevy/0.19.1/bevy/core_pipeline/fullscreen_material/trait.FullscreenMaterial.html) ("A trait to define a material that will render to the entire screen"); examples `fullscreen_material.rs`, `custom_post_processing.rs` exist at tag v0.19.1 **[raw]** | MIT OR Apache-2.0 | The trait and examples exist. No Bevy implementation of the filter was found (GitHub searches for "bevy kuwahara" and "bevy painterly" returned nothing). | The anisotropic kind follows edges, so it is a step up from the uniform filter already tried. It still cannot simplify by design or lose an edge on purpose. | `pit` |
| | **Blender's Kuwahara compositor node** | B | Blender ([manual, 5.2 LTS](https://docs.blender.org/manual/en/latest/compositing/types/creative/kuwahara.html)) | Blender GPL | Node present in 5.2.2 with inputs Size, Type, Uniformity, Sharpness, Eccentricity, High Precision **[run]**. Running the compositor on an image headless was not run. | Free way to **test the idea before writing a shader**: push the nine existing recreation renders through the anisotropic mode and compare with the references. | `kiln` (review only) |
| | **Kyprianidis, Kang, Döllner, "Image and Video Abstraction by Anisotropic Kuwahara Filtering"**, Pacific Graphics 2009 | C | Authors ([page with PDF](https://www.kyprianidis.com/p/pg2009/)) | reference only | Page lists the PDF and a source link on Google Code (likely dead). | The paper to implement from. | `pit` |
| | **Maxime Heckel, "On Crafting Painterly Shaders"** (2024-10-29) | C | Author ([article](https://blog.maximeheckel.com/posts/on-crafting-painterly-shaders/)) | No licence on the code snippets: reference only | Walks from the basic filter to the anisotropic one with GLSL at each step. | The most implementable walkthrough found. Rewrite, do not copy. | `pit` |
| | **Acerola's post-processing shaders** | C | Garrett Gunnell ([repo](https://github.com/GarrettGunnell/Post-Processing)) | MIT **[raw]** | Unity shaders; last push 2024-06-30; 828 stars. That it contains Kuwahara variants is **unverified** (from memory, not checked in the tree). | MIT, so code may be ported if it does. | `pit` |
| On the surfaces | **Brush-stroke shaped colour patches baked into vertex colours or textures** | B | our own script, using the bakes from failure 4 | ours | Not run. | Cheapest way to get "brush-stroke shaped patches of colour" on rock and ground: drive the colour drift with stretched, directional noise (the Wave and Gabor texture nodes exist in 5.2.2 **[run]**). | `kiln` |
| As geometry | **Brushstroke Tools** v1.2.3 | B | Blender Studio, Simon Thommes ([docs](https://studio.blender.org/tools/addons/brushstroke_tools), [Project Gold premiere post](https://studio.blender.org/blog/project-gold-premiere/)) | GPL-3.0-or-later, copyright 2024 Blender Foundation (manifest and `LICENSE` in the zip **[raw]**) | Unpacked and read; **not run**. It builds "textured mesh strips based on curve geometry using Geometry Nodes" on a surface; the fill method takes a `method='SURFACE_FILL'` property, so it may be scriptable, **unverified**. Min Blender 4.2.0; archive files dated 2025-07-23. | The only free tool that makes real strokes on 3D objects. Output is many overlapping see-through strips, which is expensive in a game. Best used in `kiln` to render look targets and to bake stroke textures. | `kiln` |
| | **Its bundled brush atlases**: six 4K EXR sheets of scanned oil strokes (`dry_loaded`, `dry_scrumble`, `fat_loaded`, `feathery`, `grunge`, `streaky_dashes`) plus a linen canvas map | A | Blender Studio | Same GPL-3.0-or-later; no separate licence for the images in the archive | Viewed two sheets: rows of real dabs and long strokes, black on white, about 60 strokes per sheet (`_probe/bs_sheet.png`). | Exactly the ingredient wanted, under the wrong licence for shipping. GPL allows commercial use and redistribution, but an image that visibly contains these scans is arguably a derived work and would carry GPL into the game's art. Use for look development; do not ship. | `kiln` (look-dev) |
| | **Barbara Meier, "Painterly Rendering for Animation"**, SIGGRAPH 1996 | C | Walt Disney Animation Studios ([publication page with PDF](https://disneyanimation.com/publications/painterly-rendering-for-animation/)) | reference only | Abstract quoted on the page: the problem is "getting the paint to 'stick' to surfaces rather than randomly change with each frame". | The original method: scatter stroke particles on the surface and draw each as a brush image. Brushstroke Tools is a descendant. | both |

**Pick, in two steps.** First, spend an hour running the existing recreation renders through Blender's anisotropic Kuwahara node to see how far a direction-following filter gets; if it helps, `pit` implements it as a `FullscreenMaterial` from the Kyprianidis paper. Second, and more important, put strokes on the assets: directional colour patches baked into surfaces, and stroke-shaped cards along foliage and cloud silhouettes to break the outline. Designed simplification and lost edges are an art decision no tool here makes for you.

### Failure 7. Towns at a distance

Two problems: the pieces (boxes do not read as houses), and the layout (random scatter does not read as streets and terraces).

| Option | Kind | Publisher | Licence | Format, size, verification | Fit and concrete use | Repo |
|---|---|---|---|---|---|---|
| **Kenney *Fantasy Town Kit* 2.0** | A | Kenney ([page](https://kenney.nl/assets/fantasy-town-kit)) | CC0 (`License.txt`, created 2025-08-03 **[raw]**) | 3.9 MB zip; 167 GLB files plus FBX and OBJ **[raw]**. Preview viewed: walls (stone and timber), roofs in two pitches with gables and corners, stairs, chimneys, road pieces with slopes, fences, stalls, a windmill and watermills. | Modular **parts**, flat-coloured, in ADR 0007's style. Assemble 10 to 20 house variants by script, then instance those. The road pieces include slopes, which suits terraces. | `kiln` |
| **KayKit *Medieval Hexagon Pack*** | A | Kay Lousberg ([itch page](https://kaylousberg.itch.io/kaykit-medieval-hexagon), [GitHub](https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0)) | CC0 (`LICENSE.txt` in the repo **[raw]**: "License: (Creative Commons Zero, CC0)") | "over 200" models in FBX, glTF, OBJ; repo about 29 MB. Not downloaded. | **Whole small buildings** (houses, church, tavern, mill, market) made to be seen from far above, which is our case. Fastest route to a town that reads. | `kiln` |
| **Quaternius *Medieval Village MegaKit*** (free tier is 60 to 70 per cent of 300+ models) | A | Quaternius ([page](https://quaternius.com/packs/medievalvillagemegakit.html)) | CC0 as stated on the page | OBJ, FBX, glTF. Not downloaded. | Same maker and style as the existing benchmark, with modular walls, roofs, doors and vines. Best match if the benchmark's look is the target. | `kiln` |
| **Medieval Fantasy City Generator** | B | watabou ([itch page](https://watabou.itch.io/medieval-fantasy-city-generator)) | Free. "You can use maps created by the generator as you like: copy, modify, include in your commercial rpg adventures etc." | Runs in a browser; exports PNG, SVG and **JSON**. Last updated 2025-02-03. Not scriptable headless. JSON structure not inspected. | Generate a handful of layouts by hand, save the JSON under `source/`, and have the build script read street lines and block outlines and place buildings along them. A layout file is an input like any other spec. | `kiln` |
| **TownGeneratorOS** | B, C | watabou ([repo](https://github.com/watabou/TownGeneratorOS)) | GPL-3.0 **[raw]** | Haxe source of an older version of the generator; last push 2021-01-09. | Read for the algorithm (wards, walls, streets from a Voronoi diagram). Do not copy code into `kiln` unless GPL is acceptable there. | reference |
| **MapGenerator** | B | ProbableTrain ([repo](https://github.com/ProbableTrain/MapGenerator)) | LGPL-3.0 and GPL-3.0 | Browser tool; exports PNG, SVG and STL. Last push 2024-05-09; 1,437 stars. | Grid-like modern city streets. Wrong character for a ring town on a slope. | n/a |
| **Our own layout rule**: streets along height contours of the slope, terraces as flat steps, buildings placed in rows facing the street, density falling off from a few centres | B | our own script | ours | Not run. | The reference's "terraces following the slope" is a rule, and the recreations already scatter by script. Change the scatter from random points to points along contour curves, with a gap for each street. | `kiln` |
| **Parish and Müller, "Procedural Modeling of Cities"**, SIGGRAPH 2001 | C | authors ([ACM](https://dl.acm.org/doi/pdf/10.1145/1185657.1185716), [SIGGRAPH history page](https://history.siggraph.org/learning/procedural-modeling-of-cities-by-parish-and-muller/)) | reference only | Paper. Read only as a search summary: roads grown from population and terrain maps, land split into lots, buildings per lot. | The standard reference if the layout rule above needs to grow. | reference |
| **Blosm** | B | vvoovv ([repo](https://github.com/vvoovv/blosm)) | GPL | Imports real OpenStreetMap buildings and terrain; needs network. | Real-world towns, online. Not relevant to a headless, offline build. | n/a |

**Pick: KayKit's whole buildings (or houses assembled from Kenney's parts) instanced along contour-following streets generated by our own script.** Use a watabou JSON layout for the first test if writing the contour rule takes more than a day.

---

## 3. The Bevy rendering side (`pit`)

Everything in this table is first-party in Bevy 0.19.1. Names were read from the [docs.rs item index](https://docs.rs/bevy/0.19.1/bevy/all.html) **[raw]**; descriptions come from the linked pages.

| Need | Bevy 0.19.1 type | What it does | Example in the Bevy repo at v0.19.1 **[raw]** |
|---|---|---|---|
| Distance haze | [`DistanceFog`](https://docs.rs/bevy/0.19.1/bevy/pbr/struct.DistanceFog.html), `FogFalloff` | "the 'classic' computer graphics distance fog effect" | `fog.rs`, `atmospheric_fog.rs` |
| Fog with shape, clouds in the pit | [`FogVolume`](https://docs.rs/bevy/0.19.1/bevy/light/struct.FogVolume.html) | "A unit cube of fog ... Can be positioned and scaled with a Transform", optional 3D density texture, scroll offset, tint | `fog_volumes.rs`, `scrolling_fog.rs` |
| Light shafts | [`VolumetricFog`](https://docs.rs/bevy/0.19.1/bevy/light/struct.VolumetricFog.html) on the camera, `VolumetricLight` on a light | "enables volumetric fog and volumetric lighting, also known as light shafts or god rays". The `volumetric_fog.rs` example attaches `VolumetricLight` to point, spot and directional lights. | `volumetric_fog.rs` |
| Sky | [`Atmosphere`](https://docs.rs/bevy/0.19.1/bevy/light/struct.Atmosphere.html), `ScatteringMedium` (with `earth()` and `mars()` presets), `AtmosphereSettings`, `AtmosphereEnvironmentMapLight`, `Skybox` | Physically based sky for "one planet". **No clouds.** | `atmosphere.rs`, `skybox.rs` |
| Clouds | none first-party | No type with "cloud" in its name exists in the index. | none |
| Post-process, built in | `Bloom`, `DepthOfField`, `MotionBlur`, `AutoExposure`, `ChromaticAberration`, `Vignette`, `LensDistortion` ([post_process](https://docs.rs/bevy/0.19.1/bevy/post_process/index.html)); `ColorGrading`, `Tonemapping`. `Vignette` and `LensDistortion` are new in 0.19 ([release notes](https://bevy.org/news/bevy-0-19/)). No film grain. | Standard camera effects | `post_processing.rs`, `color_grading.rs`, `tonemapping.rs`, `bloom_3d.rs` |
| Post-process, custom | [`FullscreenMaterial`](https://docs.rs/bevy/0.19.1/bevy/core_pipeline/fullscreen_material/trait.FullscreenMaterial.html) | One fragment shader over the whole screen, scheduled before tonemapping by default | `shader_advanced/fullscreen_material.rs`, `shader_advanced/custom_post_processing.rs` |
| Custom surface look | [`ExtendedMaterial`](https://docs.rs/bevy/0.19.1/bevy/pbr/struct.ExtendedMaterial.html), `MaterialExtension` | "A material that extends a base Material with additional shaders and data" | `shader/extended_material.rs` |
| Leaf cards | [`AlphaMode::Mask`](https://docs.rs/bevy/0.19.1/bevy/prelude/enum.AlphaMode.html), `AlphaMode::AlphaToCoverage` | Cut-out transparency; the second needs MSAA and is described as suited to foliage | `transparency_3d.rs` |
| Contact detail | `ScreenSpaceAmbientOcclusion`, `ContactShadows` (new in 0.19) | Darkening in creases; short sharp shadows where things touch | `ssao.rs`, `contact_shadows.rs` |
| Swapping detail with distance | visibility ranges | Fade between a near and a far version of an asset | `visibility_range.rs` |

Third-party crates checked against their own repositories on 2026-10-04 **[raw]** unless noted:

| Crate | Does | Bevy version in `Cargo.toml` | Licence | Maturity | Verdict |
|---|---|---|---|---|---|
| [`bevy_weather`](https://github.com/etwodev/bevy_weather) 0.2.0 | Sky, raymarched clouds, fog, rain, snow | 0.19.1 | MIT OR Apache-2.0 | 1 star, 10 commits, pushed 2026-09-16 | Clouds tuned for viewing from below. Read, do not depend. |
| [`bevy-volumetric-clouds`](https://github.com/evroon/bevy-volumetric-clouds) 0.2.0 | Horizon-style clouds on a skybox | 0.19.0 on `master`; released 0.2.x targets 0.18 per README | MIT | 54 stars, pushed 2026-08-24 | Cannot enter clouds. Read. |
| [`bevy_stratus`](https://github.com/edgarhsanchez/bevy_stratus) 0.1.0 | Fork of the above, "half-precision" | 0.19 | MIT | 1 star, pushed 2026-08-20 | Same limit. |
| [`bevy_feronia`](https://github.com/NicoZweifel/bevy_feronia) 0.8.4 | Scattering, wind, foliage materials, LOD | bevy sub-crates 0.19.0 on `dev`; README table says 0.18 | MIT OR Apache-2.0 | 85 stars; author says not for production yet | Watch. |
| [`bevy_mod_outline`](https://github.com/komadori/bevy_mod_outline) 0.13.0 | Mesh outlines | 0.19.0 | MIT OR Apache-2.0 | 207 stars, pushed 2026-07-09 | Only if outlines are ever wanted (style board question 6). |
| [`bevy_wind_waker_shader`](https://github.com/janhohenheim/bevy_wind_waker_shader) 0.6.0 | Two-tone toon shading via `ExtendedMaterial` | **0.18.0** | MIT OR Apache-2.0 | 91 stars, pushed 2026-01-29 | Not on 0.19. A short example of a stylised `ExtendedMaterial` to read. |
| [`bevy_toon_shader`](https://github.com/tbillington/bevy_toon_shader) | Toon shading | not checked | Apache-2.0 per GitHub | pushed 2024-10-05 | Stale. |

No maintained crate for painterly or Kuwahara-style rendering in Bevy was found. *Tiny Glade* (Pounce Light) is a shipped stylised game on a customised Bevy, discussed by its two developers in an [80.lv interview](https://80.lv/articles/exclusive-tiny-glade-developers-discuss-bevy-proceduralism-publishers-cozy-games); the article was found by search and not read, so nothing is claimed from it.

---

## 4. Proposed order of adoption

Ordered by visible gain per unit of effort. Steps 1 to 3 need no licence decision and no ADR change.

1. **Rock by plane cuts** (`kiln`, about a day). Lift the function from `benchmarks/research-samples/technique-probes/rock_probe.py` into a build script, add parameters for cut count, tilt and depth, and rebuild one cliff recreation from stacked cut slabs with overhangs. Compare beside the Quaternius rocks and Kenney's cliff kit.
2. **Vertex-colour bake** (`kiln`, about a day). Add a bake step: enable Cycles from the script, bake ambient occlusion and a low-frequency colour drift into a colour attribute, export it. Apply to the new cliff and to one paving or wall asset. Confirm in the Bevy viewer that the colours arrive (not verified here).
3. **Kuwahara test on existing renders** (`kiln`, about an hour). Run the nine recreation renders through Blender's anisotropic Kuwahara node at two or three sizes. This decides whether `pit` should spend time on a `FullscreenMaterial` version.
4. **Decide the two policy questions.** (a) May foliage use alpha-masked textures (amend ADR 0007)? (b) May build scripts load pinned GPL extensions from `.tools/`?
5. **Trees** (`kiln`, a few days, needs 4b). Pin Sapling. Generate a skeleton from a preset with low curve resolution, convert to mesh, add buttress roots (borrow the approach from Generate Tree Plugin), hang leaf-cluster cards on branch ends with normals copied from a hull. Needs 4a for the cards; without it, use flat-coloured leaf geometry cut to ambientCG outlines.
6. **Draping growth** (`kiln`, a day or two, needs 4b). Pin IvyGen; use its paths for vines and moss lines over the new cliff.
7. **Clouds and shafts in the pit** (`pit`, a few days). `VolumetricFog` and `VolumetricLight` first, with a plain `FogVolume`. Then `kiln` produces one 3D density texture from a CC0 cloud volume and `pit` loads it. Measure frame time on the minimum hardware.
8. **Town** (`kiln`, a few days). Import KayKit buildings (or assemble houses from Kenney parts), then replace random scatter with placement along contour-following streets.
9. **Strokes on assets** (`kiln`, open-ended). Directional colour patches in the bake from step 2; stroke-shaped cards on foliage and cloud outlines. Use Brushstroke Tools only to render targets to aim at.

---

## 5. Licence summary

"Commercial" = may be used in a commercial game. "Public repo" = the files themselves may be committed to a public repository. "Reference only" = look, do not ship. For tools, the answers are about the **tool's files**; what a tool generates is ours, on the general rule in the [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.html#WhatCaseIsOutputGPL): "The output of a program is not, in general, covered by the copyright on the code of the program."

| Item | Licence | Commercial | Public repo | Reference only |
|---|---|---|---|---|
| Kenney Nature Kit, Fantasy Town Kit | CC0 | yes | yes | no |
| KayKit Medieval Hexagon Pack, Forest Nature Pack | CC0 | yes | yes | no |
| Quaternius packs (Medieval Village MegaKit, Ultimate Stylized Nature, Stylized Tree) | CC0 | yes | yes | no |
| Poly Haven models and textures | CC0 | yes | yes | no (wrong style; used as reference by choice) |
| ambientCG materials and atlases | CC0 1.0 | yes | yes | no |
| OpenGameArt "Cool Leaves Textures" (Sinestesia) | CC0 | yes | yes | no |
| OpenGameArt "handpainted rock textures" (rubberduck) | CC0 | yes | yes | no |
| 3dtextures.me | CC0 (site statement) | yes | yes | no |
| Lynocs texture pack | CC0 1.0 plus "don't sell these as it is"; AI-assisted | yes | unclear | treat as reference until decided |
| JangaFX free VDBs | CC0 (page statement) | yes | yes | no |
| CGHeven Cloud VDB Pack Vol. 1 | CC0 (page statement) | yes | yes | no |
| Disney cloud data set | CC BY-SA 3.0 | yes, with attribution | yes, with attribution; derivatives must be CC BY-SA | effectively yes for us |
| OpenVDB sample models | none stated | unknown | unknown | yes |
| ez-tree code and leaf textures | MIT | yes | yes, keep the notice | no |
| Bevy and `bevy_*` crates listed | MIT OR Apache-2.0 (or MIT) | yes | yes | no |
| Material Maker | MIT | yes | yes | no |
| Acerola Post-Processing | MIT | yes | yes | no |
| Blender core (bmesh, modifiers, Geometry Nodes, Cycles bake, compositor) | GPL | yes (tool) | not needed | no |
| Sapling Tree Gen, Cell Fracture, Extra Mesh Objects, Generate Tree Plugin, Space colonization, Easy Tree, Modular Tree, Atlas2Mesh, Bagapie, Easy Clouds | GPL-3.0-or-later | yes (tool) | yes, but those files stay GPL; simpler to pin the zip in git-ignored `.tools/` | no |
| IvyGen, A.N.T. Landscape | GPL-2.0-or-later | yes (tool) | as above | no |
| Erosion terrain generator | GPL-3.0-or-later (manifest); Apache-2.0 (GitHub) | yes (tool) | as above | no |
| Stylized Rock Generator (mertnizamoglu) | GPL-3.0 | yes (tool) | as above | read only by choice |
| tree-gen (friggog) | GPL-3.0; models "free for use ... apart from direct sale as assets" | yes | as above | skip |
| Brushstroke Tools code | GPL-3.0-or-later | yes (tool) | as above | no |
| Brushstroke Tools brush atlases (EXR scans) | GPL-3.0-or-later, no separate asset licence | legally yes, but would carry GPL into shipped art | yes under GPL | **treat as look-dev only** |
| watabou Medieval Fantasy City Generator (generated maps) | author's terms: use "as you like", commercial included | yes | yes (the exported layouts) | no |
| TownGeneratorOS source | GPL-3.0 | yes | as GPL | read only by choice |
| MapGenerator | LGPL-3.0 and GPL-3.0 | yes | as GPL | not used |
| Blosm | GPL | yes | as GPL | not used |
| Articles, papers and talks (Zaal 2013, Megagon interview, Heckel 2024, Kyprianidis 2009, Meier 1996, Schneider 2015, Parish and Müller 2001, Genshin GDC talk, Blender manual) | no reuse licence found | no | no | yes |

---

## 6. What was downloaded and inspected

All under `benchmarks/research-samples/` (git-ignored). Total 267 MB on disk at the end. No account or payment was needed for any of it.

| Folder | Contents | What I did and saw |
|---|---|---|
| `blender-extensions/` | Zips and unpacked copies of 15 extensions from the [Blender Extensions catalogue](https://extensions.blender.org/api/v1/extensions/): Sapling Tree Gen, IvyGen, Extra Mesh Objects, A.N.T. Landscape, Modular Tree, Space colonization tree generator, Generate Tree Plugin, Easy Tree, Erosion terrain generator, Brushstroke Tools, Easy Clouds, Cell Fracture, Atlas2Mesh, Scatter Objects, Bagapie. (A sixteenth, Leaf Gen, was downloaded and deleted unread to save space.) | Read manifests and licence files. Ran nine through `_probe/probe.py`, which imports the unpacked folder, calls `register()`, runs the generator operator, prints triangle counts and renders a grey view. |
| `blender-extensions/_probe/` | `probe.py`, renders, `sheet2.png` (contact sheet), `bs_sheet.png` | **Sapling default**: a thin straight trunk with sparse side branches and round leaves; 15,840 + 5,084 triangles. **Sapling `japanese_maple`**: a wide, forked, twiggy crown; about 960,000 triangles. **Generate Tree Plugin**: brown faceted trunk leaning slightly, four to nine roots curling out, forked branches; with leaves on, green faceted lumps on each branch. **IvyGen**: a mat of ivy over the cube's top, stems running down one face. **Rock generator**: a smooth pear-shaped lump. **A.N.T. + eroder**: a ridged mountain patch. **Erosion terrain**: a 254 m square of rolling eroded hills. **Space colonization**: edges only, hidden inside my helper sphere in the render. **Cell Fracture**: cube in eight pieces. **Modular Tree**: error, no output. **Brush atlases**: rows of black oil-paint dabs and strokes on white. |
| `technique-probes/` | `rock_probe.py`, `rock_probe.png` | Four objects side by side: noise blob (5,120 triangles); the same after planar decimate (2,014; still a blob); block after 14 plane cuts and a bevel (162; large clean planes); six cut slabs stacked (60 to 88 each; jagged shelves with overhangs, crude but readable as strata). |
| `kenney/` | `fantasy-town-kit.zip` (3.9 MB), `nature-kit.zip` (10.5 MB), unpacked | Read both `License.txt` files (CC0). Counted 167 GLB and 329 glTF files. Viewed both preview images: flat-colour parts laid out on a grid; cliffs are stepped blocks with coloured tops. Did not import into Blender. |
| `ambientcg/` | `LeafSet029_1K-PNG` (ivy, 9.8 MB), `Foliage001_1K-JPG` (grass, 3.9 MB) | Viewed colour and opacity maps: nine separate photographed leaves or blades per atlas with clean masks. Each zip also holds normal, roughness, displacement maps and a `.blend`. |
| `opengameart/` | `cool-leaves/` (four PNGs, 5 MB), `hp-rock/` (1K zip, 16.6 MB) | Viewed two leaf clumps and all four rock colour maps, as described in sections 2.3 and 2.4. |
| `clouds/` | `smoke.vdb` (2.6 MB, OpenVDB sample), `bake_test.png` | Used as test data: VDB import, `openvdb` module, Volume to Mesh, and both bake targets all succeeded in one headless run. |

Not downloaded: the JangaFX and CGHeven cloud packs (download flow not scriptable or not found), the Disney cloud (size and share-alike), KayKit and Quaternius packs (not needed to establish licence and contents), Poly Haven models.

---

## 7. Unverified items, and things wanted but not found free

**Unverified**

- **Guerrilla Games' own publication pages** (`guerrilla-games.com/read/...`) did not respond to three fetch attempts. The cloudscapes talk was verified on the SIGGRAPH course site instead. Their vegetation talk ("Between Tech and Art: The Vegetation of Horizon Zero Dawn"), which a forum thread says describes leaf normals copied from an envelope shape, was **not read**. The custom-normals technique in failure 3 therefore has no first-party citation here.
- **The Genshin Impact GDC talk's content.** Title and video link come from a search result; the page could not be read.
- **Parish and Müller 2001** and the **Tiny Glade interview** are cited from search summaries, not from reading them.
- **Acerola's repository containing Kuwahara shaders**: not checked in the file tree.
- **That Bevy 0.19's glTF loader carries vertex colours and custom normals through** to rendering. The exporter options exist **[run]**; the Bevy side was not run. `docs/research/3d-asset-agent-workflow.md` may already cover it.
- **VDB to a 3D KTX2 texture that `FogVolume` accepts.** Reading the grid in Blender's Python works **[run]**; writing a 3D texture Bevy loads was not attempted, and no tool for it was identified.
- **`FogVolume` cost on a GTX 1660**, and whether its tint controls can produce bright tops with coloured shaded sides.
- **Running Blender's compositor headless on an existing image** (the node exists; the full run was not done).
- **Brushstroke Tools' surface-fill running without a viewport.** The draw operator is interactive; the fill path looked scriptable in the source but was not run.
- **Modular Tree on Blender 5.2.2.** It failed when loaded from a folder; a proper install was out of bounds for this task.
- **ez-tree from Node with no browser**, and **Material Maker's export with no window**.
- **3dtextures.me**: download hosting, file sizes and per-texture pages were not opened.
- **Extension release dates.** The catalogue JSON gives versions and minimum Blender versions but no dates; where a date is given it is the timestamp of files inside the archive.
- **Sapling's `willow` preset** failed in my loader with an argument type error; I did not find out whether that is the preset or my loader.
- **Kenney and KayKit models loading through `tools/bl` and exporting within the glTF profile** (ADR 0004). Formats are glTF, so this is expected to work, and was not run.

**Wanted, not found free**

- **A CC0 (or similarly permissive) brush-stroke alpha atlas.** The only good one found is Blender Studio's, under GPL. Options: scan or paint our own, or generate stroke shapes procedurally.
- **A CC0 atlas of painted leaf clusters with several clusters per sheet.** Found one clump in four colours (OpenGameArt) and Quaternius's textures; everything else under CC0 is photographs of single leaves.
- **Painted, anime-style cloud textures or cards under CC0.** All free cloud material found is realistic volume data.
- **A maintained Bevy crate for painterly, Kuwahara or stroke-based rendering.** None found on GitHub.
- **A Bevy cloud solution for clouds below or around the camera.** Both crates found assume the viewer is under the cloud layer.
- **A free rock or cliff generator that produces planes, ledges and strata out of the box.** Every generator tried or read is noise displacement with a decimate on top. The plane-cut probe in this repo is the closest thing, and it is thirty lines of our own code.
- **A headless town layout generator.** The good ones (watabou, MapGenerator) run in a browser.
- **A first-party breakdown of stylised rock modelling from a shipped game.** Found only an individual artist's tutorial (Zaal 2013) and Megagon's general interview.
- **Blender Studio's Project Gold production files.** The premiere post says they are available "by subscribing to the Blender Studio website", so they are not free.

---

## 8. Sources

Local runs (all 2026-10-04, Blender 5.2.2 LTS via `tools/bl`):

- `benchmarks/research-samples/blender-extensions/_probe/probe.py` (extension probes)
- `benchmarks/research-samples/technique-probes/rock_probe.py` (rock techniques)
- Two throw-away scripts in the session scratch directory: node and operator introspection; VDB import, bake and Kuwahara node check. Their results are quoted above; the scripts were not kept in the repo.

Catalogues and APIs read raw:

- Blender Extensions catalogue: <https://extensions.blender.org/api/v1/extensions/>
- Bevy 0.19.1 item index: <https://docs.rs/bevy/0.19.1/bevy/all.html>
- Poly Haven asset API: <https://api.polyhaven.com/assets?t=models>, <https://api.polyhaven.com/assets?t=textures>
- ambientCG API: <https://ambientcg.com/api/v2/full_json>
- GitHub API (licence, last push, stars, `Cargo.toml`, README, file trees) for: [bevyengine/bevy](https://github.com/bevyengine/bevy) at tag v0.19.1, [etwodev/bevy_weather](https://github.com/etwodev/bevy_weather), [evroon/bevy-volumetric-clouds](https://github.com/evroon/bevy-volumetric-clouds), [edgarhsanchez/bevy_stratus](https://github.com/edgarhsanchez/bevy_stratus), [NicoZweifel/bevy_feronia](https://github.com/NicoZweifel/bevy_feronia), [komadori/bevy_mod_outline](https://github.com/komadori/bevy_mod_outline), [janhohenheim/bevy_wind_waker_shader](https://github.com/janhohenheim/bevy_wind_waker_shader), [tbillington/bevy_toon_shader](https://github.com/tbillington/bevy_toon_shader), [dgreenheck/ez-tree](https://github.com/dgreenheck/ez-tree), [friggog/tree-gen](https://github.com/friggog/tree-gen), [MaximeHerpin/modular_tree](https://github.com/MaximeHerpin/modular_tree), [GoodPie/modular_tree](https://github.com/GoodPie/modular_tree), [YGForge/LowPolyTreeGen](https://github.com/YGForge/LowPolyTreeGen), [LucasFurer/my_blender_addon](https://github.com/LucasFurer/my_blender_addon), [mertnizamoglu/Stylized-Rock-Blender](https://github.com/mertnizamoglu/Stylized-Rock-Blender), [RodZill4/material-maker](https://github.com/RodZill4/material-maker), [GarrettGunnell/Post-Processing](https://github.com/GarrettGunnell/Post-Processing), [ProbableTrain/MapGenerator](https://github.com/ProbableTrain/MapGenerator), [watabou/TownGeneratorOS](https://github.com/watabou/TownGeneratorOS), [vvoovv/blosm](https://github.com/vvoovv/blosm), [KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0](https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0)

Bevy documentation:

- Release notes: <https://bevy.org/news/bevy-0-19/>
- <https://docs.rs/bevy/0.19.1/bevy/light/struct.FogVolume.html>, <https://docs.rs/bevy/0.19.1/bevy/light/struct.VolumetricFog.html>, <https://docs.rs/bevy/0.19.1/bevy/light/struct.Atmosphere.html>, <https://docs.rs/bevy/0.19.1/bevy/light/atmosphere/struct.ScatteringMedium.html>
- <https://docs.rs/bevy/0.19.1/bevy/pbr/index.html>, <https://docs.rs/bevy/0.19.1/bevy/post_process/index.html>
- <https://docs.rs/bevy/0.19.1/bevy/core_pipeline/fullscreen_material/trait.FullscreenMaterial.html>, <https://docs.rs/bevy/0.19.1/bevy/prelude/enum.AlphaMode.html>
- Examples directory: <https://github.com/bevyengine/bevy/tree/v0.19.1/examples/3d>

Blender:

- Kuwahara node, 5.2 LTS manual: <https://docs.blender.org/manual/en/latest/compositing/types/creative/kuwahara.html> (the page body did not come through the fetch; the description quoted in search results is from the 4.0 manual at <https://docs.blender.org/manual/en/4.0/compositing/types/filter/kuwahara.html>)
- Brushstroke Tools: <https://studio.blender.org/tools/addons/brushstroke_tools>; Project Gold premiere: <https://studio.blender.org/blog/project-gold-premiere/>
- Easy Clouds source: <https://codeberg.org/LunarKitten/EasyClouds> (link from its manifest; not opened)

Asset publishers and licences:

- Kenney: <https://kenney.nl/assets/fantasy-town-kit>, <https://kenney.nl/assets/nature-kit>, <https://kenney.nl/support>
- KayKit: <https://kaylousberg.itch.io/kaykit-medieval-hexagon>, <https://kaylousberg.itch.io/kaykit-forest>
- Quaternius: <https://quaternius.com/>, <https://quaternius.com/packs/medievalvillagemegakit.html>, <https://quaternius.com/packs/ultimatestylizednature.html>
- Poly Haven licence: <https://polyhaven.com/license>
- ambientCG licence: <https://docs.ambientcg.com/license/>
- OpenGameArt: <https://opengameart.org/content/cool-leaves-textures>, <https://opengameart.org/content/handpainted-rock-textures>
- 3dtextures.me: <https://3dtextures.me/about/>
- Lynocs: <https://lynocs.itch.io/texture-pack>
- JangaFX: <https://jangafx.com/software/embergen/download/free-vdb-animations>
- CGHeven: <https://cgheven.com/blog/free-cloud-vdb-pack-vol-1-10-hero-clouds>
- Disney clouds: <https://www.disneyanimation.com/resources/clouds/>, licence <https://media.disneyanimation.com/uploads/production/data_set_asset/6/asset/License_Cloud.pdf>
- OpenVDB samples: <https://www.openvdb.org/download/>
- watabou: <https://watabou.itch.io/medieval-fantasy-city-generator>
- GNU GPL FAQ on program output: <https://www.gnu.org/licenses/gpl-faq.html#WhatCaseIsOutputGPL>

Write-ups, talks and papers:

- Greg Zaal, "Procedural Stylized Rock Modeling", 2013: <https://blog.gregzaal.com/2013/09/20/procedural-stylized-rock-modeling/>
- Megagon Industries interview, 80.lv: <https://80.lv/articles/level-game-production-lonely-mountains-downhill>
- Andrew Schneider, "The Real-time Volumetric Cloudscapes of Horizon: Zero Dawn", SIGGRAPH 2015 course page: <https://advances.realtimerendering.com/s2015/index.html>
- Kyprianidis, Kang, Döllner, 2009: <https://www.kyprianidis.com/p/pg2009/>
- Maxime Heckel, "On Crafting Painterly Shaders", 2024: <https://blog.maximeheckel.com/posts/on-crafting-painterly-shaders/>
- Barbara Meier, "Painterly Rendering for Animation", 1996: <https://disneyanimation.com/publications/painterly-rendering-for-animation/>
- Material Maker command line: <https://rodzill4.github.io/material-maker/doc/command_line.html>
- Sucker Punch, "Procedural Grass in 'Ghost of Tsushima'", GDC 2021 (members-only video; listed for completeness, not used): <https://gdcvault.com/play/1027033/Advanced-Graphics-Summit-Procedural-Grass>
- Found by search, not read: Genshin Impact GDC 2021 talk <https://www.youtube.com/watch?v=-JFyAdI_rO8>; Parish and Müller 2001 <https://dl.acm.org/doi/pdf/10.1145/1185657.1185716>; Tiny Glade interview <https://80.lv/articles/exclusive-tiny-glade-developers-discuss-bevy-proceduralism-publishers-cozy-games>
