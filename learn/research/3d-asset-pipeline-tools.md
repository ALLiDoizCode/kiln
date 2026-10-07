# 3D asset pipeline: stages, tools and gaps

Researched 2026-10-07. Versions, prices and licence terms in this area change within months; every such figure below is as of that date and should be checked again before it is relied on.

This is a research note. It informs choices about kiln's pipeline and makes none. It does not draw on the `first-attempt` tag.

## How to read this

- Every claim links to the source that owns it: a specification, a tool's own documentation or repository, a licence text, a pricing page, a paper.
- **Vendor claim** means the vendor says so and nobody independent has shown it.
- **Secondary source** means no first-party page could be read and the claim rests on someone else's report.
- **Unverified** means no source could be read at all; the item is listed so that it is not mistaken for a fact.
- Bevy facts were read from the Bevy 0.19.1 source, the version pinned in `Cargo.toml`. Links go to the same files at the `v0.19.1` tag on GitHub.
- The versions in this repo are Blender 5.2.2 and glTF Validator 2.0.0-dev.3.10 (`tools/install_tools.sh`) and Bevy 0.19.1 (`Cargo.lock`). All three are the latest stable releases today: [Blender download page](https://www.blender.org/download/), [validator releases](https://github.com/KhronosGroup/glTF-Validator/releases), [Bevy on crates.io](https://crates.io/crates/bevy). Bevy 0.20 is at release candidate 2 (2026-09-28).
- Section 6 is synthesis, not sourced fact, and is marked as such.

## Summary

### The stage map

No single primary source lays out one canonical list of stages. The map below is assembled from the Khronos asset creation guidelines, the Blender manual, the glTF specification and engine import documentation; section 1 gives the source for each stage.

| # | Stage | Needed for | In one line |
|---|---|---|---|
| 1 | Brief and reference | every asset | Decide what the asset is, its real size, its budgets and its look. |
| 2 | Source geometry | every asset | Get a shape: model it, generate it procedurally, generate it with AI, scan it, or buy it. |
| 3 | Game mesh (retopology or decimation) | any asset whose source is too dense | Produce a mesh with few enough triangles to draw in real time. |
| 4 | UV unwrapping | every textured asset | Flatten the surface onto a 2D square so images can be mapped onto it. |
| 5 | Baking | assets with a dense source | Transfer detail from the dense source into images the game mesh uses. |
| 6 | Texturing and materials | every asset | Produce the images and numbers that say how the surface reacts to light. |
| 7 | Rigging and skinning | characters and other deforming assets only | Add a skeleton and bind the mesh to it. |
| 8 | Animation | animated assets only | Author motion for the skeleton or for objects. |
| 9 | Levels of detail | assets seen at many distances | Make cheaper versions to show when the asset is far away. |
| 10 | Collision shapes | assets the player or physics touches | Make simple invisible shapes for physics; the render mesh is too costly. |
| 11 | Export | every asset | Write the engine's delivery format, here glTF. |
| 12 | Optimisation and compression | most shipped assets | Reorder, shrink and compress mesh and texture data. |
| 13 | Validation | every asset | Check the file against the format and against the project's own rules. |
| 14 | Engine import and integration | every asset | Load into the engine, attach game data, confirm it looks and performs as intended. |
| 15 | Automation | the pipeline as a whole | Run the above repeatably, from scripts and in CI. |

### What Bevy + Blender + Tripo3D covers, and what it leaves open

- **Covered by Blender alone, scriptably:** modelling, procedural generation, decimation, UV unwrapping, baking, material setup, rigging, animation and glTF export. Blender has a tool for every authoring stage; the limits are in quality of the automatic tools (retopology in particular) and in what its baker outputs.
- **Covered by Tripo3D, by its own description:** source geometry from text or images, with options for face count, quad output, a low-poly mode, PBR textures, retopology, rigging and format conversion. There is no independent measurement of its topology, UV or texture quality (section 2).
- **Covered by Bevy:** loading glTF, PBR rendering, skinned animation, a distance-based switch between LOD entities, an asset processor and hot reload.
- **Open, with nothing in the set filling it:**
  - **Texture compression and mipmaps.** Blender does not write GPU-compressed (KTX2) textures; Bevy 0.19 does not generate mipmaps for PNG at load and does not read the glTF extension that references KTX2 textures.
  - **Level-of-detail generation.** Bevy has no automatic LOD generation and no glTF LOD import; each LOD must be made upstream and wired up in code.
  - **Collision shapes.** Bevy has no physics. A physics crate (Avian or bevy_rapier) and a way to author or derive the shapes are both needed.
  - **Mesh optimisation and compression.** Bevy 0.19.1 fails to load files using Draco, meshopt or quantisation, so the common glTF size optimisations cannot be used without extra code.
  - **Validation beyond the format.** The Khronos validator checks the file is legal glTF. Nothing checks budgets, texel density, scale, naming or look.
  - **Game data on assets.** Getting gameplay data (components) from Blender to Bevy needs a convention or an add-on such as Skein.
  - **High-quality texture painting.** Blender can paint and bake, but the dedicated tools (Substance 3D Painter, ArmorPaint, InstaMAT) are a separate category.
- **Cross-cutting, and easy to miss:** output licences differ by plan and by territory; AI output is not reproducible bit for bit; style consistency across generated assets is not something any vendor documents a control for; the `asset_view` crate as built cannot load JPEG textures.

### Strongest alternatives to Tripo3D

- **Hosted, same category:** Meshy (current model 7.1) and Rodin by Hyper3D (Gen-2.5). Both offer face-count control, quad output, PBR textures, an API and Blender integration. Tencent's hosted Hunyuan 3D 3.x is a fourth.
- **Self-hosted, open weights:** TRELLIS.2 (Microsoft, MIT, needs a 24 GB Nvidia GPU on Linux) and Hunyuan3D 2.1 (Tencent, needs 29 GB for shape plus texture, and its licence does not apply in the EU, UK or South Korea). Both produce dense meshes that still need the game-mesh stage.
- **Not AI at all:** procedural generation in Blender (Geometry Nodes or `bpy`), and CC0 libraries (Poly Haven, ambientCG, Kenney, Quaternius) for anything generic.

## 1. The map of the pipeline

### Vocabulary used throughout

- **Mesh:** a surface made of triangles. **Topology** is how those triangles (or four-sided **quads**, used while authoring) are arranged. glTF stores triangles only; quads are split on export ([Khronos guidelines 1.0, Geometry](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec03_Geometry/Geometry.md)).
- **High-poly** and **low-poly:** a dense source mesh (hundreds of thousands to millions of triangles) and the reduced mesh the game draws.
- **UV coordinates:** a 2D position for every vertex that says which part of an image covers it. **UV unwrapping** is making those coordinates; the cut lines are **seams** and the flattened pieces are **islands** ([Khronos guidelines 1.0, UV Coordinates](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec04_UVCoordinates/UVCoordinates.md)).
- **Texel density:** how many texture pixels (texels) cover a metre of surface. It decides how sharp the asset looks up close.
- **PBR (physically based rendering) material:** a description of a surface as base colour, metallic and roughness values, usually with a normal map. glTF's core material is the metallic-roughness model ([glTF 2.0 specification, section 3.9](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)).
- **Normal map:** an image that stores surface directions so a flat triangle can be lit as if it had fine detail. The Khronos guidelines recommend it to "capture small details that may be modeled in a base asset in order to reduce the triangle count" ([Geometry](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec03_Geometry/Geometry.md)).
- **Tangents:** per-vertex vectors needed to decode a normal map. The baker and the engine must compute them the same way; glTF names the MikkTSpace algorithm as the default ([glTF 2.0 specification, section 3.7.2.1](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)).
- **Mipmaps:** pre-shrunk copies of a texture that the GPU uses at a distance; without them distant textures shimmer.
- **LOD (level of detail):** "decreasing the complexity of a 3D model representation as it moves away from the viewer" ([Khronos guidelines 1.0, Levels of Detail](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec07_LevelsofDetail/LevelsofDetail.md)).
- **Draw call:** one instruction to the GPU to draw one mesh with one material. Their count is a main performance cost.

### About the sources for the map

The Khronos Real-time Asset Creation Guidelines are the nearest thing to a tool-neutral standard. [Version 2.0](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md) (August 2025) is organised by topic: file structure, geometry, UVs, materials, textures, lighting, animation, levels of detail, publishing targets, performance, source of content. On 2026-10-07 its full chapters for levels of detail, publishing targets and source of content are stubs that say "work in progress" and point at the [1.0 text](https://github.com/KhronosGroup/3DC-Asset-Creation/tree/main/asset-creation-guidelines-1.0) from 2020, so 1.0 is cited where 2.0 is empty. The guidelines are written for product models on the web; their numbers are not game budgets. Khronos also publishes one worked example, [Optimizing a high resolution source model for real-time](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/workflow/01-Optimizing-A-High-Resolution-Model-For-Realtime/01-workflow.md), which walks the order: check scale, remove unseen geometry, lay out UVs, bake and make materials, export glTF, review in a viewer.

Collision and LOD generation are not covered by Khronos; the sources for those are engine import documents.

### The stages

**1. Brief and reference.** Writing down what the asset is, its real-world size and what it must cost, and collecting pictures of it. The Khronos guidelines put reference photos and measurements first, and require models "built to real world scale" ([Geometry, Reference](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec03_Geometry/Geometry.md)). They also say an asset should be authored with a known target in mind: "one must have an idea about the intended hardware and software where assets will ultimately be rendered" ([Publishing Targets](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec99_PublishingTargets/PublishingTargets.md)). Tools: none specific; image generators and reference boards. For AI generation, the reference image is the generator's input.

**2. Source geometry.** Getting the first shape. The routes are hand modelling or sculpting, procedural generation, AI generation, photogrammetry (reconstruction from photographs), and buying or downloading. The output is often far denser than a game can draw. Tools: Blender, Houdini (section 3); AI generators (section 2); RealityScan, Meshroom (section 3); libraries (section 3).

**3. Game mesh: retopology or decimation.** **Retopology** rebuilds a clean, lighter mesh over a dense one. The Blender manual describes it as creating "a new mesh that overlaps the original one", done by hand because "the automatic remesh tools generally don't result in topology that lends itself to deformation"; of topology for a mesh that will deform it says "no perfect automatic tools exist for this right now; it has to be done manually" ([Blender manual, Retopology](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html)). **Decimation** removes triangles automatically without regard for clean edge flow. The Khronos guidelines note that an optimised delivery mesh need not be editable and "can therefore contain highly adaptive, irregular triangle meshes (instead of quad meshes)" ([Publishing Targets](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec99_PublishingTargets/PublishingTargets.md)). So clean quad topology matters most for meshes that will deform (characters) or be edited further, and less for a static rock. This stage also includes deleting geometry nobody will see ([Khronos workflow](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/workflow/01-Optimizing-A-High-Resolution-Model-For-Realtime/01-workflow.md)). Tools: Blender Decimate, voxel and QuadriFlow remesh; Quad Remesher; Instant Meshes; meshoptimizer's simplifier; the retopology options of the AI services.

**4. UV unwrapping.** Cutting the surface along seams and flattening it. It exists because "you can't assign textures to your model effectively without having UVs" ([Khronos guidelines 1.0, UV Coordinates](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec04_UVCoordinates/UVCoordinates.md)). Decisions made here: where seams go, how much padding between islands (so colours do not bleed), and texel density. Tools: Blender's unwrap operators, xatlas, RizomUV, UVPackmaster.

**5. Baking.** Rendering information from one place into an image: most often the fine detail of the high-poly mesh into a normal map for the low-poly mesh, and ambient occlusion (how shadowed each point is by nearby geometry). It exists so the cheap mesh can look like the dense one. It applies whenever there is a denser source than the game mesh, which includes AI-generated and scanned meshes. Tools: Blender's Cycles baker, Marmoset Toolbag, Substance 3D Painter, xNormal.

**6. Texturing and materials.** Producing the base colour, metallic-roughness and other images, and the material settings. The Khronos guidelines recommend the metallic-roughness workflow and authoring lossless PNG, with "automated tools to generate the other files" ([guidelines 2.0, summary](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). glTF packs occlusion, roughness and metallic into the red, green and blue channels of images ([glTF 2.0 specification, sections 3.9 and 5.19](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)); this is called ORM packing. Tools: Substance 3D Painter and Designer, ArmorPaint, Material Maker, InstaMAT, Blender; texture libraries; AI texture generation.

**7. Rigging and skinning (deforming assets only).** A **rig** is a skeleton of bones; **skinning** assigns each vertex weights saying which bones move it. A static prop needs neither. Tools: Blender armatures and Rigify, Mixamo, AccuRig, the AI services' auto-rig options, open models such as UniRig.

**8. Animation (animated assets only).** Keyframes that move bones or objects over time; glTF stores them as samplers and channels ([guidelines 2.0, Animation summary](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Tools: Blender, Cascadeur, Mixamo's library, motion capture.

**9. Levels of detail.** Lower-cost versions (LOD1, LOD2, ...) of the full mesh (LOD0). The Khronos text gives no numbers: "these guidelines make no strict recommendations regarding LOD configuration at this time. This is a discussion that should be had with the downstream consumer" ([Levels of Detail](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec07_LevelsofDetail/LevelsofDetail.md)). Some engines generate LODs at import: Godot's importer has a "Generate LODs" option ([Godot import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)), and Unreal imports them ([Unreal FBX static mesh pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)). Bevy does not (section 5). Whether an asset needs LODs depends on how far away it is ever seen and how many triangles it has. Tools: Blender Decimate, meshoptimizer and gltfpack, glTF-Transform, Simplygon, InstaLOD.

**10. Collision shapes.** Physics engines test simple shapes (boxes, spheres, convex hulls), not the render mesh. Unreal's pipeline shows the usual practice: the artist models simplified shapes beside the render mesh and marks them by name (`UBX_`, `UCP_`, `USP_`, `UCX_` prefixes for box, capsule, sphere and convex) ([Unreal FBX static mesh pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)). The alternative is deriving shapes automatically, for example by **convex decomposition**, which splits a mesh into a set of convex pieces. Only assets that something can touch need this. Tools: hand-placed shapes in Blender, CoACD, V-HACD, the collider constructors of Avian and bevy_rapier.

**11. Export.** Writing the delivery format. The Khronos guidelines separate authoring formats (`.blend`), interchange formats (FBX, OBJ, USD) and delivery formats (glTF) ([guidelines 2.0, File Structure summary](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Bevy loads glTF. glTF fixes the conventions: right-handed, +Y up, the front of an asset faces +Z, and "the units for all linear distances are meters" ([glTF 2.0 specification, section 3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). Tools: Blender's glTF exporter.

**12. Optimisation and compression.** Changes that do not alter what the asset is but make it smaller or faster: merging duplicate data, reordering vertices for the GPU's cache, compressing mesh data, converting textures to GPU-compressed formats with mipmaps. The Khronos guidelines list polygon count, instancing, texture compression and mesh compression ("glTF has extensions for Draco and MeshOpt") ([guidelines 2.0, Performance summary](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Tools: section 4.

**13. Validation.** Checking the file. There are two different questions: is it legal glTF (the Khronos validator answers this), and does it meet the project's own rules for size, budget and look (no standard tool answers this). The Khronos workflow ends with reviewing the file in a viewer.

**14. Engine import and integration.** Loading the file, attaching physics and gameplay data, and confirming it in the game's own renderer and lighting. Section 5.

**15. Automation.** Running stages from scripts so results are repeatable. Not a stage of the asset but of the pipeline. The Khronos guidelines assume it: delivery variants are produced from one lossless "base asset" by "automated workflows" ([Publishing Targets](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec99_PublishingTargets/PublishingTargets.md)).

## 2. AI generation tools

### What the evidence does and does not show

No independent, reproducible measurement of topology, UV layout or texture seams was found for the current version of any commercial generator. What exists:

- **3D Arena** ([arXiv 2506.18787](https://arxiv.org/abs/2506.18787), June 2025) ranks 19 models from 123,243 human votes on rendered appearance. Its author states that voters favour visual impact over downstream usefulness and that topology is not measured. Its data predates every current model version listed below.
- **Hi3DEval** ([arXiv 2508.05609](https://arxiv.org/abs/2508.05609)) and **3DGen-Bench** ([arXiv 2503.21745](https://arxiv.org/abs/2503.21745)) cover open and research models, not the commercial services, and do not score topology.
- Papers from model authors compare their model against competitors; those are not neutral.

So "clean topology", "game-ready" and "production-ready" below are vendor claims throughout. The only way to know is to inspect outputs, which is what `learn/` is building the skill for.

### Hosted services

**Tripo3D** (the candidate; operated by Holymolly Ltd, per its [terms](https://www.tripo3d.ai/terms)).

- *Models.* Two families in the API: the H series for detailed meshes (current `v3.1-20260211`) and the P series for low-poly meshes (`P1-20260311`; `P2-20260801` in preview). Inputs are text, one image or four views. Source: [Tripo API documentation](https://developers.tripo3d.com/en/docs/generation-text-to-model/standard), [changelog](https://developers.tripo3d.com/en/docs/changelog). The docs disagree with themselves in places: the overview page omits P2, and model identifiers differ between pages.
- *Face-count control.* `face_limit` up to 1,500,000 triangles on H v3.1, up to 150,000 quads, and 500 to 20,000 triangles with `smart_low_poly`. P2 accepts 48 to 50,000 triangles. Tripo's own guidance for the H series is "Game-ready assets: 50,000 – 100,000" faces (same documentation).
- *Quads.* `quad: true` gives a quad mesh and "will force the output format to FBX". Bevy does not load FBX, so quad output must pass through Blender.
- *Low-poly and retopology.* `smart_low_poly` is described as "hand-crafted, clean topology style. Best suited for simple, non-complex inputs. Complex models may occasionally fail" (vendor claim). A separate retopology endpoint accepts uploaded meshes, including ones not made by Tripo, and can bake textures onto the result.
- *Textures.* PBR is on by default and gives base colour, metallic, roughness and normal maps; quality levels go up to 8K. A `delight` option removes baked-in lighting on the newest texture model. The format-conversion endpoint's texture format defaults to JPEG, which matters for this repo (section 5).
- *UVs.* An `export_uv` flag controls unwrapping. No documented statement about seam placement or texel density was found.
- *Other.* Part segmentation, auto-rigging (bipeds, and from rig model v2.5 quadrupeds and other body plans), retexturing of uploaded models, style transforms, conversion to GLTF, FBX, USDZ, OBJ, STL and 3MF.
- *API price.* Pay as you go at 1 credit = $0.01 ([pricing](https://developers.tripo3d.com/en/pricing)). Image to 3D with standard textures on the H series is 30 credits ($0.30); quad output adds 5; smart low-poly adds 10; P2 with standard textures is 110 ($1.10); retopology is 10 or 30; auto-rig 25. Failed tasks are not charged.
- *Studio price.* Free: 200 credits a month, "Public Models · Non-Commercial Use". Pro: shown as $20 a month billed annually, 3,000 credits, "Private Models · Commercial Use" ([Tripo pricing](https://www.tripo3d.ai/pricing)). The monthly (non-annual) prices are unverified; the page's own figures conflict. Whether Studio credits can be spent through the API is unverified.
- *Output licence.* [Terms](https://www.tripo3d.ai/terms), last updated 2025-07-11. For free users, "Tripo retains all rights" in inputs and outputs. For paid users, "Paid Users generally have all rights", subject to a licence back to the company for providing the service; the company "will not use Inputs and Outputs as training data". Outputs may not be used "to create models or services that directly compete". The user indemnifies the vendor; the vendor gives no intellectual-property indemnity. Whether a pay-as-you-go API customer with no subscription is a "Paid User" is not defined in the terms: unverified.
- *Integrations.* Official Blender add-on 0.7.3 for "3.0+" ([plugins page](https://developers.tripo3d.com/en/docs/plugins)); Blender 5.x is not named as tested. A CLI that can run as an MCP server, and SDKs including Rust ([CLI documentation](https://developers.tripo3d.com/en/docs/cli)). Plugins for Unity, Unreal, Godot; none for Bevy.

**Meshy** (Meshy LLC).

- *Models.* `meshy-7.1` (added 2026-09-18) and a low-poly model `meshy-t2` ("Smart Topology", 100 to 15,000 triangles, triangles only). Source: [Meshy API documentation](https://docs.meshy.ai/llms-full.txt), [changelog](https://docs.meshy.ai/api/changelog).
- *Output.* Triangles by default; a remesh step gives a "quad-dominant mesh" with a target of 100 to 300,000 faces. The docs recommend leaving remesh off "for the highest-quality model". PBR adds metallic, roughness and normal maps at 2K to 8K. Separate endpoints for remesh, UV unwrap, retexture, rigging and animation. Formats GLB, FBX, OBJ, USDZ, STL. API assets are kept at most 3 days.
- *Price.* Pro is $20 a month for 1,000 credits ([pricing](https://www.meshy.ai/pricing)); a textured Meshy 7.1 model is 30 credits ([API pricing](https://docs.meshy.ai/api/pricing)), about $0.60 at the Pro rate. The API needs Pro or above.
- *Output licence.* [Terms](https://www.meshy.ai/terms-of-use), updated 2026-09-19. Free-plan output is owned by Meshy and licensed to the user under Creative Commons Attribution 4.0. Paid users "own their Customer Output". Section 2.9 lets Meshy use inputs and outputs of non-Enterprise customers "to train, validate, test, or improve Services"; the pricing page FAQ says the opposite, and the terms govern.
- *Integrations.* A Blender plugin tested on "4.2.6, 5.0.1, 5.1.0, 5.2.0" that receives models from the web app ([Meshy Blender plugin](https://docs.meshy.ai/webapp/plugins/blender/introduction)); an official MCP server.

**Rodin by Hyper3D** (Deemos Corporation).

- *Models.* Rodin Gen-2.5 ([API specification](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5)).
- *Output.* `Raw` triangle meshes up to 2,000,000 faces or `Quad` meshes from 500 to 200,000 faces, with presets (for quads: 4,000, 8,000, 18,000, 50,000). PBR materials (base colour, metalness, normal, roughness) at 2K by default. An option bakes high-resolution detail into a normal map for the quad mesh. Formats GLB, USDZ, FBX, OBJ, STL.
- *Price.* Creator $30 a month ("about 60 models"); Business $120 a month with "Full API access"; a base generation is 0.5 credits ([pricing](https://hyper3d.ai/pricing?lang=en)). The API needs the Business plan.
- *Output licence.* [Terms](https://hyper3d.ai/legal/terms): "we will not limit your use of such Output", but export is "for private or commercial use depending on your subscription plan". The API [data policy](https://docs.hyper3d.ai/en/legal/data-retention-policy) says payloads are kept 7 days and "not used to train models".
- *Integrations.* A hosted MCP endpoint ([Hyper3D MCP](https://hyper3d.ai/features/mcp)); a Blender add-on exists, and its supported Blender versions are unverified.

**Tencent Hunyuan 3D (hosted).** Model versions 3.0 and 3.1 through Tencent Cloud; face count 3,000 to 1,500,000; a LowPoly mode with triangle or mixed quad output; PBR flag; smart topology, UV unfold and auto-rig as separate jobs ([API documentation](https://intl.cloud.tencent.com/document/product/1284/75540)). Postpaid $0.02 per credit; a normal generation is 25 credits and PBR adds 10, about $0.70 ([billing](https://www.tencentcloud.com/document/product/1284/75281)). Terms of the consumer studio are unverified.

**Other services, briefly.**

| Service | Status on 2026-10-07 | Note |
|---|---|---|
| Kaedim | Operating | AI plus human artists who clean every output; turnaround in hours per stage; offers LODs and UV presets ([Kaedim documentation](https://docs.kaedim3d.com/)). No public pricing page; price is unverified. |
| Sloyd | Operating | Plus plan $15 a month with unlimited generation ([pricing](https://www.sloyd.ai/pricing)); [terms](https://www.sloyd.ai/terms-of-use) grant a use licence, not ownership. Its pricing page and terms disagree on free-tier commercial use. |
| Hi3D (formerly Hitem3D) | Operating | Aimed at 3D printing; free tier output is CC BY 4.0 ([pricing](https://www.hi3d.ai/pricing)). |
| CSM (Common Sense Machines) | Appears offline | Acquired by Google according to a [law-firm notice](https://www.gunder.com/print/v2/content/25253/gunderson-dettmer-represents-common-sense-machines-in-acquisition-by-google.pdf) dated 2026-01-27; its sites did not resolve. No statement from Google or CSM was found. |
| Luma Genie | Appears discontinued | The Genie URL redirects to a homepage that no longer mentions it. No official notice found. |
| Roblox Cube 3D | Operating | Works only inside Roblox; no export ([Roblox documentation](https://create.roblox.com/docs/parts/model-generation)). |
| Autodesk Wonder 3D | Launched 2026-03-04 | Text and image to 3D in Flow Studio ([Autodesk announcement](https://blogs.autodesk.com/media-and-entertainment/2026/03/04/introducing-wonder-3d-text-and-image-to-3d-in-flow-studio/)). Export formats and prices are secondary-source only. |
| fal.ai, Replicate | Operating | Resell Tripo, Meshy, Rodin, Hunyuan and open models behind one API ([fal 3D models](https://fal.ai/explore/search?q=3d)). How their terms interact with each vendor's was not checked. |

### Open-weights, self-hostable models

"Open weights" means the trained model can be downloaded and run on one's own GPU. Three findings hold across the group:

1. **None produces a game mesh in one step.** Each extracts a dense triangle surface from a volumetric representation (by an algorithm such as marching cubes) and then decimates it. The game-mesh stage is still required.
2. **Licences have traps beside the headline.** Tencent's licences exclude the EU, UK and South Korea. The MIT-licensed TRELLIS models depend on Nvidia libraries ([nvdiffrast](https://github.com/NVlabs/nvdiffrast/blob/main/LICENSE.txt), [nvdiffrec](https://github.com/NVlabs/nvdiffrec/blob/main/LICENSE.txt)) whose licence says they "only may be used or intended for use non-commercially". Whether that reaches the generated assets is a legal question this note does not answer.
3. **Tencent's newest models are hosted only.** The last open full release is Hunyuan3D 2.1 (June 2025).

| Model | Output mesh | Textures | Licence of weights | Stated hardware | Source |
|---|---|---|---|---|---|
| Hunyuan3D 2.1 (Tencent) | Marching cubes surface, then decimated | PBR: albedo, roughness, metallic; no normal map mentioned | Tencent community licence: "does not apply in the European Union, United Kingdom and South Korea"; outputs covered too; cap of 1M monthly users | 10 GB shape, 21 GB texture, 29 GB both; Mac, Windows, Linux | [repository](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1), [licence](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/main/LICENSE) |
| Hunyuan3D 2.0 (Tencent) | Marching cubes; default decimation to 40,000 faces | Colour only, lighting removed | Same licence family | 6 GB shape, 16 GB with texture | [repository](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) |
| TRELLIS.2 (Microsoft) | Voxel-grid surface, remeshed and decimated; example exports 1,000,000 faces | PBR: base colour, roughness, metallic, opacity; UVs by xatlas | MIT, with the Nvidia dependencies above | Nvidia GPU with 24 GB; Linux only | [repository](https://github.com/microsoft/TRELLIS.2), [model card](https://huggingface.co/microsoft/TRELLIS.2-4B) |
| TRELLIS (Microsoft) | Iso-surface, 95% of triangles removed by default | Base colour only; UVs by xatlas | MIT, with non-commercial dependencies | Nvidia GPU with 16 GB; Linux | [repository](https://github.com/microsoft/TRELLIS) |
| Pixal3D (Tencent ARC, 2026) | As TRELLIS.2, on which it is built | PBR | MIT; inherits TRELLIS.2's dependencies | Not stated | [repository](https://github.com/TencentARC/Pixal3D) |
| Stable Fast 3D and SPAR3D (Stability AI) | Low-polygon mesh; optional triangle or quad remesh (quads split on export) | Colour map plus single roughness and metallic values | Stability Community Licence: free under US$1,000,000 annual revenue, registration required for commercial use; "You own any outputs" | About 6 GB and 10.5 GB | [SF3D](https://github.com/Stability-AI/stable-fast-3d), [SPAR3D](https://github.com/Stability-AI/stable-point-aware-3d), [licence](https://github.com/Stability-AI/stable-fast-3d/blob/main/LICENSE.md) |
| TripoSG (VAST, Tripo's company) | Iso-surface; `--faces` decimation | None; geometry only | MIT | 8 GB | [repository](https://github.com/VAST-AI-Research/TripoSG) |
| TripoSR (Stability and Tripo, 2024) | Marching cubes | Vertex colour or baked colour | MIT | About 6 GB | [repository](https://github.com/VAST-AI-Research/TripoSR) |

Tripo's current commercial models (H v3.1, P1, P2) are not open. No mesh generator from Stability newer than SPAR3D (January 2025) was found; its [core models page](https://stability.ai/core-models) lists none.

**Models that generate artist-style topology.** A separate research line takes a dense mesh or point cloud and writes out a low-poly mesh triangle by triangle, imitating how an artist would lay it out. They produce no UVs or textures and have hard size limits: MeshAnything V2 "cannot generate meshes with more than 1600 faces" and its code licence is non-commercial ([repository](https://github.com/buaacyw/MeshAnythingV2)); BPT is released only as a "lite version" under a Tencent licence ([repository](https://github.com/Tencent-Hunyuan/bpt)); Nvidia's Meshtron has no released code or weights ([project page](https://research.nvidia.com/labs/cosmos-lab/meshtron/)); DeepMesh has released its smaller model ([repository](https://github.com/zhaorw02/DeepMesh)). Tencent's PolyGen, which the hosted LowPoly mode is reported to use, has no open weights. No neutral benchmark of these exists. They are not yet a dependable self-hosted retopology step.

**Open auto-rigging models** (for the day characters are in scope): UniRig ([repository](https://github.com/VAST-AI-Research/UniRig), MIT, 8 GB) and its successor SkinTokens ([repository](https://github.com/VAST-AI-Research/SkinTokens), MIT, 14 GB), both from Tripo's company; Puppeteer from ByteDance ([repository](https://github.com/Seed3D/Puppeteer), Apache-2.0). Adobe's RigAnything is research-only by licence. All quality claims are the authors' own.

**Blender integration of open models.** Tencent ships a Blender add-on in the Hunyuan3D 2.0 repository that talks to a locally run server. A community add-on covers TRELLIS and TRELLIS.2 ([trellis_blender](https://github.com/FishWoWater/trellis_blender)). ComfyUI node packs exist for most.

## 3. Non-AI and procedural alternatives or complements

### Blender (5.2.2 LTS, the repo's pin)

Blender is free, runs on Linux, and is licensed GPL; "What you create with Blender is your sole property", including exported files ([Blender licence page](https://www.blender.org/about/license/)).

- **Headless scripting.** `--background` runs without a window and `--python` runs a script; `--python-exit-code` is needed for a failing script to return a non-zero exit code ([command-line arguments](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)). `tools/bl` already does this.
- **Geometry Nodes.** "A system for modifying the geometry of an object with node-based operations" ([manual](https://docs.blender.org/manual/en/5.2/modeling/geometry_nodes/introduction.html)): procedural modelling inside Blender. The exporter's "Apply Modifiers" option exports the evaluated result.
- **UV unwrapping.** Unwrap along seams with three methods including Minimum Stretch; Smart UV Project, which cuts automatically by angle and is "a good method for, say, mechanical objects or architecture"; Lightmap Pack ([manual, UV editing](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/uv.html)).
- **Baking.** Only the Cycles renderer bakes. "Selected to Active" bakes a high-poly object onto a low-poly one. Bake types include Normal, Ambient Occlusion, Roughness, Diffuse and Emit; there is no Metallic bake type and no packed ORM output, so those need a workaround or another tool ([manual, baking](https://docs.blender.org/manual/en/5.2/render/cycles/baking.html)).
- **Decimation and remeshing.** The Decimate modifier's Collapse mode reduces by a ratio and is the free baseline for LODs ([manual](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/decimate.html)). Voxel remesh and QuadriFlow quad remesh rebuild topology automatically ([manual, Retopology](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html)).
- **Rigging.** Armatures, and the bundled Rigify add-on for generating rigs ([manual](https://docs.blender.org/manual/en/5.2/addons/rigify/index.html)).

**The built-in glTF exporter** ([manual](https://docs.blender.org/manual/en/5.2/addons/scene_gltf2.html)):

- Quads and n-gons are triangulated. Vertices are duplicated at UV seams and hard edges, so vertex counts rise.
- Materials are read from the Principled BSDF node: base colour, metallic, roughness, normal map, emission. Shader nodes the exporter does not recognise are skipped, so procedural materials must be baked to images first.
- Ambient occlusion exports only through a custom node group named `glTF Material Output`.
- It exports "+Y Up" by converting from Blender's own axes.
- Custom properties go to the glTF `extras` field only if "Custom Properties" is ticked.
- It can write Draco and (new in 5.2) meshopt compression, and WebP images. It does not write KTX2 textures.
- In the default animation mode only active or stashed actions export.
- Area lights, world lighting, curves and animation of materials are not exported.

### Houdini (SideFX)

A node-based procedural modelling and simulation package, the industry's usual tool for procedural asset generation. Apprentice is free and non-commercial; Indie is $299 a year under a $100,000 revenue cap; Core is $1,995 perpetual ([editions](https://www.sidefx.com/products/compare/), [Indie restrictions](https://www.sidefx.com/faq/question/indie-restrictions/)). It scripts headlessly through `hython` and has a glTF output node that does not support skins or morph targets ([glTF ROP](https://www.sidefx.com/docs/houdini/nodes/out/gltf.html)). Which export formats Apprentice and Indie allow is unverified; two readings of the comparison page conflicted.

### Texturing tools

| Tool | What it is | Price and licence | Linux | Automation | Source |
|---|---|---|---|---|---|
| Substance 3D Painter | Paints PBR textures onto a mesh, with baking; the industry standard | $199.99 on Steam with updates to March 2027, or Adobe plans from $59.99 a month | Yes (Ubuntu 22.04) | Automation toolkit exists; details unverified | [Steam](https://store.steampowered.com/app/4329260/Substance_3D_Painter_2026/), [Adobe plans](https://www.adobe.com/products/substance3d/plans.html) |
| Substance 3D Designer | Builds procedural materials as node graphs | $199.99 on Steam (from a search summary, not opened) | Yes | As above | [Steam](https://store.steampowered.com/app/4329280/Substance_3D_Designer_2026/) |
| ArmorPaint | Open-source PBR texture painter | $19 for binaries; source under zlib; actively maintained | Yes | Unverified | [site](https://armorpaint.org/download), [repository](https://github.com/armory3d/armorpaint) |
| Material Maker | Open-source procedural material graphs | Free, MIT; version 1.7 | Not stated | Command-line export | [site](https://www.materialmaker.org/), [releases](https://github.com/RodZill4/material-maker/releases) |
| InstaMAT | Material authoring, painting and baking | Free under $100,000 revenue, with attribution | Yes | Pipeline CLI and SDK | [site](https://instamaterial.com/) |
| Marmoset Toolbag 5 | Baker and preview renderer | $18.99 a month or $399 perpetual | Unverified | Unverified | [shop](https://marmoset.co/shop/) |
| xNormal | Normal and occlusion baker | Free; Windows only | No | Unverified | [site](https://xnormal.net/) |
| Quixel Mixer | Material blending | Discontinued; final version 2023.1 (secondary source: [CG Channel](https://www.cgchannel.com/2026/02/quixel-mixer-has-been-discontinued-get-the-final-version-for-free/)) | — | — | — |

### Retopology and UV specialists

- **Quad Remesher** (Exoside): commercial automatic quad retopology plugin for Blender; $109.90 perpetual for the Pro licence ([site](https://exoside.com/quadremesher/quadremesher-buy/)).
- **Instant Meshes:** open-source automatic remesher; no commits since 2022 ([repository](https://github.com/wjakob/instant-meshes)).
- **xatlas:** MIT library that "generates unique texture coordinates suitable for baking lightmaps or texture painting" ([repository](https://github.com/jpcy/xatlas)); the unwrapper inside most AI generators.
- **RizomUV** and **UVPackmaster:** dedicated unwrap and packing tools. RizomUV's version and price are secondary-source only; UVPackmaster's price is unverified ([UVPackmaster](https://uvpackmaster.com/)).

### Photogrammetry and scanning

Photogrammetry reconstructs a textured mesh from many photographs of a real object. Its output is dense and has real lighting baked into the colour, so stages 3 to 6 still apply.

- **RealityScan** (Epic; the desktop product formerly named RealityCapture), version 2.2: free under $1 million annual revenue, otherwise $1,250 a seat a year ([licence](https://www.realityscan.com/en-US/license)). Linux support is unverified.
- **Meshroom / AliceVision:** open source, MPL-2.0, release 2025.1.0 ([repository](https://github.com/alicevision/Meshroom)).
- **COLMAP:** open source, BSD, 4.2.1, with a command line and Python bindings ([site](https://colmap.github.io/)).
- **Gaussian splatting** is a different kind of capture: a cloud of semi-transparent blobs, not a mesh. The Khronos extension for it stores splats as points ([KHR_gaussian_splatting](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_gaussian_splatting)). It has no triangles, UVs or PBR material, so it does not feed a mesh pipeline without a separate surface-extraction step. Bevy 0.19 does not load it.

### Asset libraries and their licences

**CC0** is a public-domain dedication: any use, no attribution.

| Library | Licence | Note | Source |
|---|---|---|---|
| Poly Haven | CC0 | Models, textures, lighting environments | [licence](https://polyhaven.com/license) |
| ambientCG | CC0 | PBR materials | [licence](https://docs.ambientcg.com/license/) |
| Kenney | CC0 | Stylised game assets | [support page](https://kenney.nl/support) |
| Quaternius | CC0 | Stylised game models; already in `benchmarks/` | [FAQ](https://quaternius.com/faq.html) |
| Fab (Epic) | Per listing; Standard licence with Personal tier up to $100,000 revenue | Some content is marked for Unreal Engine only; check each listing. The Fab licence text itself could not be read (unverified). | [Fab licences](https://dev.epicgames.com/documentation/en-us/fab/licenses-and-pricing-in-fab) |
| Quixel Megascans | Fab Standard licence; no longer free as a whole | Scanned surfaces and objects | [Quixel licence](https://quixel.com/license) |
| Sketchfab | Per model: Creative Commons variants or store licences | Present status under Epic is unverified | [licences](https://sketchfab.com/licenses) |
| OpenGameArt | CC0, CC-BY, CC-BY-SA, GPL, OGA-BY per asset | CC-BY-SA requires derivatives under the same licence | [FAQ](https://opengameart.org/content/faq) |
| Unity Asset Store | Asset Store terms | No engine restriction found in the standard licence; "Restricted Assets" carry their own terms (unverified which) | [terms](https://unity.com/legal/as-terms) |
| Synty | Synty licence | "not limited by game engine" | [licence](https://syntystore.com/pages/end-user-licence-agreement) |
| BlenderKit (now Blendkit) | Royalty Free or CC0 per asset | A Blender add-on, not built in | [pricing](https://www.blendkit.com/plans/pricing/) |

### Rigging and animation services

Out of the owner's present scope; listed for the map.

- **Mixamo** (Adobe): free auto-rigger and animation library for two-legged humanoids. Licence wording and current status come from a search summary of Adobe's FAQ; the page itself could not be read (secondary source).
- **AccuRig** (Reallusion): free auto-rig tool exporting FBX and USD ([site](https://www.reallusion.com/auto-rig/accurig/)).
- **Cascadeur** 2026.2.3: physics-assisted animation; runs on Linux; the free tier exports only its own format, and paid tiers (Indie from $8 a month billed annually) export glTF directly ([plans](https://cascadeur.com/plans)).
- FBX from any of these reaches Bevy by importing into Blender and exporting glTF. The standalone converter FBX2glTF is unmaintained ([Godot fork notice](https://github.com/godotengine/FBX2glTF)).

## 4. Processing and optimisation tools between authoring and engine

| Tool | What it does | Stage | Form and licence | Source |
|---|---|---|---|---|
| glTF Validator 2.0.0-dev.3.10 | Checks a file against the glTF specification: structure, references, accessor data, image sizes. Emits a JSON report. | 13 | CLI, npm; Apache-2.0 | [repository](https://github.com/KhronosGroup/glTF-Validator), [issue list](https://github.com/KhronosGroup/glTF-Validator/blob/main/ISSUES.md) |
| glTF-Transform 4.5.1 | A toolkit of small operations on glTF files: `inspect`, `dedup`, `prune`, `weld`, `simplify`, `join`, `instance`, `tangents`, `unwrap`, `resize`, texture conversion, Draco and meshopt compression | 9, 12, 13 | Node CLI and library; MIT | [CLI reference](https://gltf-transform.dev/cli) |
| meshoptimizer 1.3 | Library for mesh simplification, GPU-cache reordering, quantisation, compression and meshlet building | 9, 12 | C/C++ with a Rust crate; MIT | [repository](https://github.com/zeux/meshoptimizer) |
| gltfpack 1.3 | One-command glTF optimiser built on meshoptimizer: simplify (`-si`), compress (`-c`), instance (`-mi`), KTX2 textures (`-tc`) | 9, 12 | CLI; MIT | [gltfpack README](https://github.com/zeux/meshoptimizer/blob/master/gltf/README.md) |
| KTX-Software 4.4.2 | Creates and inspects KTX2 files, the Khronos container for GPU-compressed textures with mipmaps. `toktx` is removed in 5.0 in favour of `ktx create`. | 12 | CLI; Apache-2.0 | [releases](https://github.com/KhronosGroup/KTX-Software/releases) |
| Basis Universal 2.50 | The codec inside KTX2 "universal" textures: one file transcodes at load time to whatever format the GPU supports. ETC1S is small and lower quality; UASTC is larger and higher quality. | 12 | CLI and library; Apache-2.0 | [repository](https://github.com/BinomialLLC/basis_universal) |
| Draco 1.5.7 | Mesh geometry compression, used through `KHR_draco_mesh_compression` | 12 | Library; Apache-2.0 | [repository](https://github.com/google/draco) |
| CoACD 1.0.14 | Convex decomposition of a mesh into collision pieces; `pip install coacd` | 10 | Python and CLI; MIT | [repository](https://github.com/SarahWeiii/CoACD) |
| V-HACD 4.1 | Older convex decomposition; its README says deprecated and points to CoACD | 10 | Library; BSD | [repository](https://github.com/kmammou/v-hacd) |
| MikkTSpace | The reference tangent algorithm, "a common standard for tangent space used in baking tools" | 5, 11 | C file; zlib-style | [repository](https://github.com/mmikk/MikkTSpace) |
| Simplygon | Commercial automatic LOD and optimisation. $42,000 a year per title, with discounts for small studios; no free tier | 9, 12 | SDK and plugins | [site](https://www.simplygon.com/) |
| InstaLOD | Commercial LOD and optimisation. Free "Pioneer" tier under $100,000 revenue, with attribution; whether that tier includes the CLI is unverified | 9, 12 | App, CLI, SDK | [site](https://instalod.com/) |
| trimesh 5.1.1, Open3D 0.20, PyMeshLab | Python mesh-processing libraries for custom checks and operations. PyMeshLab is GPL-3.0. | 13, 15 | Python | [trimesh](https://github.com/mikedh/trimesh), [Open3D](https://github.com/isl-org/Open3D), [PyMeshLab](https://github.com/cnr-isti-vclab/PyMeshLab) |

Three points decide which of these can be used with Bevy 0.19.1 at all (section 5 has the sources):

- gltfpack quantises vertex data by default and emits `KHR_mesh_quantization`, which Bevy 0.19.1 does not support; its `-noq` flag turns that off. It also restructures the file and drops `extras` unless `-ke` is given.
- Draco and meshopt compression make the file unloadable in stock Bevy 0.19.1.
- `KHR_meshopt_compression`, which Blender 5.2 and gltfpack 1.3 can already write, is still a release candidate, not a ratified extension ([extension text](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_meshopt_compression)).

The validator checks format conformance. It does not judge triangle budgets, texel density, naming, scale or appearance; that statement is an inference from its issue list, which contains no such checks.

## 5. The Bevy end

All of this section is Bevy 0.19.1 unless marked. Source files are under [`crates/` at tag v0.19.1](https://github.com/bevyengine/bevy/tree/v0.19.1/crates).

### What `asset_view` is built with

The crate enables features `3d` and `file_watcher` with default features off. That includes the glTF loader, PBR, tangent generation, PNG, HDR and KTX2 with Zstandard. It does not include `jpeg`, `webp`, `basis-universal`, `asset_processor`, `compressed_image_saver` or `meshlet` ([Bevy cargo features](https://github.com/bevyengine/bevy/blob/v0.19.1/docs/cargo_features.md)). A `.glb` with JPEG or WebP textures fails to load in the viewer as built.

### glTF import

- **Loads:** `.gltf` and `.glb`; scenes, node hierarchy, triangle meshes, positions, normals, tangents, one vertex-colour set, two UV sets, skins, morph targets, animations, cameras and punctual lights ([`bevy_gltf` loader](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs), [`vertex_attributes.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/vertex_attributes.rs)). A third UV set or second colour set is skipped with a warning.
- **Extensions supported:** `KHR_lights_punctual`, `KHR_materials_emissive_strength`, `_ior`, `_unlit`, `_volume`, `_transmission`, `_clearcoat`, `_anisotropy`, `_specular`. For the last five, the numeric factors load but their textures need extra cargo features (`pbr_transmission_textures` and similar). `KHR_texture_transform` works on the base-colour texture only ([`bevy_gltf` extension table](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)).
- **Extensions not supported:** `KHR_draco_mesh_compression`, `EXT_meshopt_compression`, `KHR_mesh_quantization`, `KHR_texture_basisu`, `EXT_texture_webp`, `EXT_mesh_gpu_instancing`, `KHR_materials_variants`, sheen, iridescence, `KHR_animation_pointer` (same table). `MSFT_lod` is not referenced in the loader at all.
- **A file that lists an unsupported extension as required fails to load entirely,** because the loader validates by default (`GltfLoaderSettings::validate`).
- **Extension hook.** `GltfExtensionHandler` lets a crate handle extensions itself, including replacing a mesh while loading ([`loader/extensions`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/extensions/mod.rs); introduced in [Bevy 0.18](https://bevy.org/news/bevy-0-18/)). The community crate [`bevy_gltf_draco`](https://crates.io/crates/bevy_gltf_draco) uses it for Draco.
- **Blender custom properties** arrive as raw JSON strings in the components `GltfExtras`, `GltfMeshExtras`, `GltfMaterialExtras` and `GltfSceneExtras` ([`assets.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/assets.rs)).
- **Missing normals:** flat normals are computed and vertices duplicated. **Missing tangents:** generated with MikkTSpace, but only when the material has a normal map and the mesh has normals and UVs; failure is a warning (loader source above).
- **Changed in 0.19:** the asset label `Material{n}` now yields a `GltfMaterial`, and `Material{n}/std` the `StandardMaterial`; scenes are spawned with `WorldAssetRoot`. Tutorials written for 0.18 or earlier do not match ([Bevy 0.19 release notes](https://bevy.org/news/bevy-0-19/)).

### Coordinate systems

- glTF: +Y up, front of the asset faces +Z ([specification, section 3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). Bevy: +Y up, forward is −Z ([`convert_coordinates.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/convert_coordinates.rs)). Blender itself is Z up; its exporter's "+Y Up" option exports "using glTF convention, +Y up" ([exporter manual](https://docs.blender.org/manual/en/5.2/addons/scene_gltf2.html)).
- Bevy applies no conversion by default. A model whose front follows the glTF convention therefore has Bevy's `Transform::forward()` pointing out of its back.
- `GltfConvertCoordinates { rotate_scene_entity, rotate_meshes }` corrects this, globally on `GltfPlugin` or per load. Both default to false and the source marks it "an experimental feature. Behavior may change in future versions". It replaced 0.17's `use_model_forward_direction` ([0.17 to 0.18 migration guide](https://bevy.org/learn/migration-guides/0-17-to-0-18/)). It is unchanged in 0.20-rc.2.
- Units are metres on both sides; nothing is rescaled.

### Textures

- **Formats** are individual cargo features: `png`, `jpeg`, `webp`, `ktx2`, `basis-universal`, `dds` and others ([`bevy_image` manifest](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_image/Cargo.toml)).
- **GPU-compressed formats** (BCn on desktop GPUs; ASTC and ETC2 mostly on mobile) load from KTX2 or DDS if the GPU supports them, and fail otherwise. A "universal" UASTC texture is transcoded at load to ASTC, else BC7, else ETC2, else uncompressed, and needs the `basis-universal` feature. ETC1S inside KTX2 is not transcoded in 0.19.1 ([`ktx2.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_image/src/ktx2.rs), [`basis.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_image/src/basis.rs)).
- **KTX2 inside glTF:** an image with MIME type `image/ktx2` loads, but the `KHR_texture_basisu` way of referencing it does not ([Bevy issue 19104](https://github.com/bevyengine/bevy/issues/19104)). The standard tools write the extension form, so this needs checking against real files.
- **Mipmaps are not generated for PNG or JPEG at load.** They come only from files that carry them (KTX2, DDS, Basis). A GPU mip generator exists in `bevy_core_pipeline` but is not run by default ([Bevy issue 18037](https://github.com/bevyengine/bevy/issues/18037)).
- **Colour space** inside glTF is decided by which material slot uses the image: normal, occlusion and metallic-roughness maps load as linear data, base colour and emissive as sRGB ([`loader/gltf_ext`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/gltf_ext/mod.rs)).
- **0.20-rc** changes the built-in compressed image saver to write BCn or ASTC with automatic mipmaps ([Bevy PR 24223](https://github.com/bevyengine/bevy/pull/24223)).

### Asset processing

Bevy can preprocess assets: in `AssetMode::Processed` it reads `assets/`, runs processors, and writes results to `imported_assets/`, with per-asset settings in `.meta` files. Running the processor needs the `asset_processor` feature ([`bevy_asset`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_asset/src/lib.rs), [processor module](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_asset/src/processor/mod.rs)). In 0.19.1 exactly one processor is built in: PNG to a compressed Basis texture with mipmaps, behind the `compressed_image_saver` feature. There is no built-in processor for meshes, glTF files or LODs; custom ones can be written. Hot reload is the `file_watcher` feature, which the viewer enables. Bevy's new scene format (BSN) ships in 0.19 as a Rust macro only; no `.bsn` file loader exists yet ([Bevy 0.19 release notes](https://bevy.org/news/bevy-0-19/)).

### Meshlets (virtual geometry)

A renderer that splits very dense meshes into small clusters and picks detail per cluster automatically, which removes the need for hand-made LODs on meshes it supports. In 0.19.1 it is experimental and behind the `meshlet` feature. Constraints, from the [meshlet module](https://github.com/bevyengine/bevy/tree/v0.19.1/crates/bevy_pbr/src/meshlet): the mesh must have exactly positions, normals and one UV set (so no skinning, vertex colours or second UV set); materials must be opaque; the docs say "Do not use normal maps baked from higher-poly geometry"; multisample anti-aliasing must be off; it "currently works only on the Vulkan and Metal backends"; it needs several less common GPU features. Whether a GTX 1660 or RX 5600 exposes those features is unverified; running Bevy's `meshlet` example on the target machine would settle it.

### Level of detail

`VisibilityRange` shows or hides an entity by camera distance with a dithered cross-fade ([`visibility/range.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_camera/src/visibility/range.rs)). Each LOD is a separate entity with its own mesh, which the developer supplies. Bevy has no automatic LOD generation for the standard renderer and no LOD import from glTF; [issue 6868 "Mesh LOD Support"](https://github.com/bevyengine/bevy/issues/6868) has been open since 2022. No maintained Bevy LOD crate was found.

### Skinning and animation (brief)

Four bone influences per vertex; 256 joints per skin; animation clips load from glTF with linear, step and cubic interpolation; an animation graph blends clips; there is no inverse kinematics in `bevy_animation` ([`bevy_animation`](https://github.com/bevyengine/bevy/tree/v0.19.1/crates/bevy_animation), [`skin.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_pbr/src/render/skin.rs)).

### What an asset must be authored for

- Bevy's `StandardMaterial` follows glTF: roughness in the green channel and metallic in blue of one texture, occlusion in red, which may be the same image ([`pbr_material.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_pbr/src/pbr_material.rs)).
- Normal maps use the OpenGL convention (green is +Y), which is Blender's bake default and glTF's rule. Maps authored for DirectX (green is −Y) look inverted; `flip_normal_map_y` exists but the glTF loader never sets it.
- The glTF normal-map strength and occlusion strength values are not applied (marked TODO in the loader).
- Each glTF primitive (one per material on a mesh) becomes its own entity and draw. Material count per object is a direct cost.
- Vertex colours multiply the base colour.

### Ecosystem crates

Versions and Bevy requirements from crates.io on 2026-10-07.

| Crate | Purpose | Latest | Works with Bevy 0.19 |
|---|---|---|---|
| [`bevy_skein`](https://github.com/rust-adventure/skein) | Blender add-on plus crate: attach Bevy components to objects in Blender, carried in glTF extras | 0.6.0; add-on 0.1.16 supports Blender 5.2 | Yes |
| [Blenvy](https://github.com/kaosat-dev/Blenvy) (successor of Blender_bevy_components_workflow) | Same goal, older | 0.1.0-alpha.1 (2024), requires Bevy 0.14 | No; stalled |
| [`bevy_asset_loader`](https://crates.io/crates/bevy_asset_loader) | Declarative loading of asset collections with loading states | 0.27.0 | Yes |
| [`avian3d`](https://docs.rs/avian3d/0.7.0/avian3d/) | Physics. `ColliderConstructor` builds colliders from a mesh: triangle mesh, convex hull, or convex decomposition; `ColliderConstructorHierarchy` applies that to a loaded scene, with per-name overrides | 0.7.0 | Yes |
| [`bevy_rapier3d`](https://docs.rs/bevy_rapier3d/0.36.0/bevy_rapier3d/) | Physics. `AsyncSceneCollider` builds colliders for a loaded scene | 0.36.0 | Yes |
| [`bevy_gltf_draco`](https://crates.io/crates/bevy_gltf_draco) | Draco decoding through the extension hook | 0.2.1; small project | Yes |
| [`bevy_mod_mipmap_generator`](https://crates.io/crates/bevy_mod_mipmap_generator) | Generates mipmaps at runtime on the CPU | 0.2.0; its README calls it "mostly prototyping/testing" | Yes |
| [`bevy_trenchbroom`](https://github.com/Noxmore/bevy_trenchbroom) | Level route that does not use Blender: Quake-style maps from the TrenchBroom editor | 0.14.0 | Yes |
| [`meshopt`](https://crates.io/crates/meshopt) | Rust bindings to meshoptimizer | 0.6.2 | Independent of Bevy |

There is no official Bevy editor. The editor prototype repository was archived on 2026-04-14 ([bevy_editor_prototypes](https://github.com/bevyengine/bevy_editor_prototypes)).

### What a Blender to Bevy pipeline commonly trips on

Each of these follows from a source cited above.

1. Bevy cannot load `.blend` files; export is always a step.
2. The forward axis is reversed unless the experimental coordinate conversion is turned on.
3. Object transforms are carried over, not baked. Unapplied scale in Blender becomes scale on the Bevy entity, inherited by children.
4. Negative scale makes Bevy create a second copy of the material with inverted culling.
5. One Blender object becomes a parent entity with one child per material, and the mesh sits on the children, named `MeshName.MaterialName`. Code that looks for the mesh on the entity with the Blender object's name does not find it.
6. Custom properties are missing unless the exporter's "Custom Properties" box is ticked.
7. Normal maps look wrong when the mesh has no UVs or normals for tangent generation, or when the map was authored for DirectX.
8. Compression options in the exporter (Draco, meshopt) produce files Bevy rejects.
9. JPEG and WebP textures need cargo features that this repo does not enable. PNG always works.
10. PNG textures have no mipmaps in 0.19, so they shimmer at a distance unless converted to KTX2 or processed.
11. Texture transforms from Blender's Mapping node work only on base colour.
12. Only two UV maps and one colour attribute survive.
13. Procedural Blender materials do not export; they must be baked to images.
14. Animations export only if the action is active or stashed.
15. Every exported camera and light is spawned; `load_cameras` and `load_lights` turn that off.

## 6. Gaps and things to consider

**This section is synthesis.** It combines the facts above into a coverage table and a list of concerns. The judgements in it are the author's reading, not statements from a source. It names candidate tools and does not recommend among them.

### Coverage of the stage map by Bevy + Blender + Tripo3D

| Stage | Blender | Tripo3D (by its own description) | Bevy | Left open | Candidates for the gap |
|---|---|---|---|---|---|
| 1 Brief and reference | — | Takes text or image as input | — | Writing down size, budgets and style per asset class | A written brief; any image tool for reference |
| 2 Source geometry | Modelling, Geometry Nodes, `bpy` | Yes | — | Nothing structural | Alternatives: Meshy, Rodin, Hunyuan, TRELLIS.2, libraries, photogrammetry |
| 3 Game mesh | Decimate, remesh (automatic, limited quality) | `face_limit`, `smart_low_poly`, P series, retopology endpoint; quality unmeasured | — | A trusted automatic route to a clean low-poly mesh | Quad Remesher, meshoptimizer simplify, InstaLOD, manual retopology |
| 4 UVs | Unwrap, Smart UV Project | Unwraps automatically; no documented control of seams or density | — | Control and checking of texel density and seams | Re-unwrap in Blender, xatlas, RizomUV, UVPackmaster |
| 5 Baking | Cycles bake; no metallic or packed ORM output | Bakes textures onto retopologised mesh | — | Metallic and ORM packing; bake automation | Scripts in `bpy`, Marmoset Toolbag, Substance, InstaMAT |
| 6 Texturing and materials | Painting, node materials (must be baked) | PBR texture generation, retexturing | Renders glTF PBR | Hand-quality painting; consistent look across assets | Substance Painter, ArmorPaint, InstaMAT, Material Maker, CC0 material libraries |
| 7 Rigging | Armatures, Rigify | Auto-rig | Skinning | Out of present scope | Mixamo, AccuRig, UniRig |
| 8 Animation | Full | Preset animations | Animation graph | Out of present scope | Cascadeur, Mixamo |
| 9 LODs | Decimate per level, by script | Can regenerate at lower face counts | Distance switch only; no generation, no import | Generating LODs and wiring them to entities | gltfpack, glTF-Transform, `meshopt` crate, InstaLOD, a custom Bevy asset processor; meshlets (experimental) |
| 10 Collision | Shapes can be modelled by hand | — | None | Physics engine, shape authoring, a naming or tagging convention | Avian or bevy_rapier; CoACD; Skein to tag shapes |
| 11 Export | glTF exporter | GLB directly (FBX if quads) | Loads glTF | Agreed export settings; the forward-axis decision | — |
| 12 Optimisation and compression | Can write Draco and meshopt, which Bevy rejects | — | One PNG to Basis processor | Texture compression with mipmaps; mesh reordering | KTX-Software, Basis Universal, glTF-Transform, gltfpack with `-noq`, Bevy's `compressed_image_saver` |
| 13 Validation | Scriptable inspection | — | Load errors and warnings | Checks beyond format legality | Khronos validator plus custom checks (`glb_inspect.py`, trimesh, glTF-Transform `inspect`) |
| 14 Integration | — | — | Yes | Carrying gameplay data from Blender | Skein, or a convention over glTF extras |
| 15 Automation | `tools/bl` | API, CLI, Rust SDK | Asset processor | The orchestration itself | Scripts and CI; nothing off the shelf |

### Cross-cutting concerns a newcomer tends to miss

- **Licences of generated assets depend on the plan.** On Tripo's free tier the vendor retains all rights and the pricing page says non-commercial. On Meshy's free tier the output is CC BY 4.0 and owned by Meshy. Evaluation outputs made on a free tier may not be usable in a shipped game. Tripo's terms do not say whether API-only customers count as paid users.
- **Licences can depend on where one lives.** Tencent's open Hunyuan3D licences exclude the EU, UK and South Korea, for the outputs as well as the weights.
- **Training on your data differs by vendor.** Tripo's terms say paid inputs and outputs are not used for training; Meshy's terms allow it for non-Enterprise customers.
- **No vendor indemnifies the user** against intellectual-property claims on generated output, in the terms read here. Copyright in AI output is not warranted by any of them.
- **Library licences vary per asset.** CC0 libraries are the simple case. Fab listings can be Unreal-only; CC-BY needs attribution; CC-BY-SA spreads to derivatives.
- **Style consistency.** Each generation is independent. The services document a style-image input for texturing and a few style presets, but no documented mechanism guarantees that fifty generated assets look like one set. Shared materials, a fixed palette, or retexturing all assets in one tool are the usual ways to impose it.
- **Topology and UV quality of AI meshes is unmeasured.** There is no independent benchmark. Expect to judge every output, and to budget cleanup: re-decimation or retopology, re-unwrapping, re-baking. For static props irregular triangles are acceptable by the Khronos guidelines' own reasoning; for anything that deforms they are not.
- **Baked-in lighting.** Generated and scanned textures can contain highlights and shadows from the source image. Under the game's own lighting this looks wrong. Tripo and Hunyuan document "delighting" steps; their effectiveness is a vendor claim.
- **Texel density and scale.** A first-person game viewed from 0.5 m needs a known number of texels per metre, and AI generators normalise size arbitrarily. Tripo has an `auto_size` option that scales to metres; real-world scale still has to be set and checked per asset. No tool in the set checks texel density.
- **Performance budgets.** No source found gives triangle, material and texture-memory budgets for a first-person game on GTX 1660 class hardware; this remains the gap already recorded in `learn/RESOURCES.md`. Tripo's "game-ready 50,000 – 100,000" faces is a vendor's general guidance, not a budget. Measuring in Bevy on the target GPU is the available route.
- **Draw calls.** In Bevy each material on an object is a separate draw. Generated assets tend to have one material each with unique textures, which prevents sharing; modular sets usually share a few materials.
- **Reproducibility.** Hosted generation cannot be re-run to the same bytes: model versions are retired (Meshy retires `meshy-5` on 2026-10-10), and the documentation read here promises no determinism. The generated file, with its prompt, input image, model version and options, is the thing to keep under version control or in storage. Procedural generation in Blender, by contrast, is reproducible from a script and a pinned Blender.
- **Cost per asset.** On list prices a textured generation is roughly $0.30 (Tripo H), $0.60 (Meshy 7.1), $0.29 to $0.75 (Rodin, depending on plan), $0.70 (Hunyuan hosted). Several attempts per accepted asset multiply this, and retopology, rigging and conversion are charged separately. Self-hosting trades this for a 24 GB class GPU.
- **Vendor lock-in.** The outputs are ordinary GLB or FBX files and remain usable if a vendor disappears; two of the services checked (CSM, Luma Genie) appear to have gone. What does not transfer is anything built around one vendor's API, options or house style.
- **The format is not the look.** A file that passes the Khronos validator can still be the wrong size, face backwards, have inverted normal maps or miss its budget.

## What could not be verified, and where sources disagreed

**Not verified from a primary source**

- Tripo: monthly Studio prices; whether Studio credits work in the API; whether API-only customers are "Paid Users"; the Blender add-on on Blender 5.x; what image format a generated GLB embeds.
- Meshy: the visible price cards (the figures above come from the page's embedded data); the price of standalone API credits.
- Rodin: Blender add-on version support; the date of its terms.
- Kaedim pricing; Hi3D prices in dollars; Tencent's consumer studio terms; Autodesk Wonder 3D export formats and prices.
- CSM and Luma Genie: no first-party shutdown statement for either.
- Hunyuan3D 2.5 being hosted-only is inferred from the absence of a repository. No first-party page for Hunyuan3D-PolyGen was found.
- The Fab licence text; current Megascans prices; Sketchfab's present status; which Unity Asset Store assets are "Restricted".
- Mixamo's licence wording, formats and status (Adobe's help site refused direct reads); Substance automation toolkit licensing; Substance Designer's Steam price.
- Houdini export restrictions by edition; RizomUV version and price; UVPackmaster price; RealityScan and Marmoset Toolbag on Linux; InstaLOD free-tier CLI.
- Whether Bevy's meshlet renderer runs on a GTX 1660 or RX 5600.
- Whether Nvidia's non-commercial library licences reach assets generated by TRELLIS.
- Line numbers in Bevy source were read from the published 0.19.1 crates; the links here point to whole files at the tag.
- An independent benchmark of topology, UV or rigging quality for any generator: none exists that could be found.
- A primary source for game performance budgets on the target hardware: none found.

**Sources disagree**

- Tripo's documentation with itself: model identifiers, P1's minimum face count (48 or 50), concurrency limits, and an overview page that omits P2.
- Tripo's pricing page: "$20/month billed annually $240" beside "Annually 50% off".
- Meshy on training: the pricing FAQ says no training without consent; terms section 2.9 permits it.
- Sloyd on free-tier commercial use: the pricing page says personal only; the terms say commercial use is permitted.
- Rodin on commercial use: "we will not limit your use" and "depending on your subscription plan" in the same terms.
- Licence labels between GitHub and Hugging Face for MeshAnything V2 (non-commercial versus MIT), BPT (Tencent licence versus MIT) and DeepMesh (Apache-2.0 versus MIT).
- Bevy 0.19.1's `CompressedImageSaver`: its documentation says it writes KTX2; the code returns the Basis format.
- Bevy's meshlet documentation says Vulkan and Metal only, while the underlying graphics library lists the required feature on DirectX 12 as well.
- The Blender manual's glTF page describes iridescence export, but its own extension list omits it.
- V-HACD's README says deprecated and archived; the repository is not archived.
- The Khronos guidelines 2.0 table of contents lists chapters whose text is not yet written.

## Method

Research was done on 2026-10-07 by reading first-party pages, repositories, licence files, papers and the Bevy 0.19.1 source. Some pages were read only through an automatic summariser, which was caught inventing content twice (two papers described as benchmarking commercial generators that do not). The licence clauses, Tripo, Meshy and Rodin API facts and prices, and the Bevy facts were read in the raw text. Read only through the summariser, and so worth a second look before relying on them: Kaedim's documentation, Sloyd's pricing and API pages, Tencent Cloud billing, the fal.ai listings, the Autodesk announcement, and several of the tool prices in sections 3 and 4. No file from the `first-attempt` tag was used.
