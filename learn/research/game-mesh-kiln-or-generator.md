# The game mesh: should kiln reduce, or should the generator?

Researched 2026-10-07. Parameters, prices and model versions in this area change within months (one of the options below is retired on 2026-10-30); every such figure is as of that date and should be checked again before it is relied on.

This is a research note. It informs one choice about kiln's pipeline and does not make it. It builds on [`3d-asset-pipeline-tools.md`](3d-asset-pipeline-tools.md) (called "the earlier note" below) and does not repeat it. It does not draw on the `first-attempt` tag.

## How to read this

- Every claim links to the source that owns it: a vendor's API documentation, the Blender manual or Python API reference, a tool's repository, the glTF specification, the Bevy 0.19.1 source.
- **Vendor claim** means the vendor says so and nobody independent has shown it.
- **Secondary source** means the claim rests on someone else's report, not a first-party page.
- **Unverified** means no source could be read; the item is listed so that it is not mistaken for a fact.
- **Inference** means the sentence is this note's reasoning from cited facts, not a statement in a source.
- **Trial** means a number measured in the one small experiment described in section 7. It is a single trial on two files, not a general result.
- Kiln's own words (run, target profile, raw output, generator, generated asset, bought asset, hand-modelled asset, static asset, production ready, shape review, final review) are used as `CONTEXT.md` defines them.
- Section 9 is synthesis, not sourced fact, and is marked as such.

### The two designs

A hosted generator can return a **dense mesh** (hundreds of thousands of triangles or more) with textures, or its own **reduced output** (a mesh already cut to a requested face count). Kiln has to meet the triangle and texture budgets of a run's target profile either way.

1. **Kiln reduces.** The raw output is the dense mesh. Kiln, in Blender, lowers the triangle count, makes new UVs, and bakes the dense mesh's detail onto the reduced mesh.
2. **Generator reduces.** The raw output is the vendor's reduced mesh at the needed face count. Kiln uses its mesh, UVs and textures as delivered and only checks and post-processes.

### Terms used here

The earlier note defines mesh, topology, quad, UV coordinates, seam, island, texel density, PBR, normal map, tangents and LOD. Terms added by this note:

- **Decimation:** removing triangles from a mesh automatically, usually by repeatedly merging the two ends of an edge into one point (an **edge collapse**), with no regard for a tidy layout.
- **Remeshing:** throwing the triangles away and building a new surface of roughly the same shape. **Retopology** is remeshing with the aim of a clean, deliberate layout.
- **Baking:** computing an image for the reduced mesh by sampling the dense mesh. For each pixel of the reduced mesh's texture, a ray is fired at the dense mesh and what it hits (surface direction, colour, roughness) is written to that pixel.
- **Cage:** an inflated copy of the reduced mesh from which those rays start, so that they begin outside the dense surface.
- **Tangent space:** the per-vertex frame of reference in which a normal map's directions are stored. The program that bakes the map and the program that draws it must build that frame the same way, or lighting looks wrong. **MikkTSpace** is the algorithm most tools agree on.
- **Welding:** merging vertices that sit at the same position into one, so that the triangles around them are connected.
- **Boundary edge:** an edge with a triangle on only one side: a hole or an open rim in the surface.

## Summary

### What the evidence supports

- **All three vendors offer reduction, and it is three different things under similar names.** Tripo has four routes (a `face_limit` on dense generation, a `smart_low_poly` flag, separate low-poly models P1 and P2, and a retopology endpoint). Meshy has two (a remesh step with `target_polycount`, and a separate Smart Topology model `meshy-t2`). Rodin has a face-count setting on one model, in triangle or quad mode (section 1).
- **Face-count control is approximate by the vendors' own wording.** Tripo's `face_limit` is a "maximum polycount"; Meshy says "the actual count may deviate from the target"; Rodin calls its number a "target face count". None documents a tolerance. Blender's Decimate modifier in the trial hit 5,000 triangles exactly, twice (sections 1 and 7).
- **Only Rodin documents that its reduced output carries the dense mesh's detail in a normal map** (`quad_normal`, off by default). Tripo's retopology endpoint has a `bake` flag described only as "bake textures onto the low-poly model". Meshy's documentation says nothing about baking in its remesh step, and its own guide says UVs must be regenerated and that retexturing gives better results after remeshing (section 1).
- **The vendors' low-poly models are not a reduction of a dense mesh at all.** Tripo P1/P2 and Meshy T2 generate the low-poly shape directly. There is then no dense mesh whose detail could be baked; any normal map comes from the vendor's texture step (section 1). This is an inference from the documentation, which describes them as separate models.
- **No vendor documents its UVs** (seam placement, island count, padding, texel density) and no vendor offers textures below 2K at generation. A target profile with a smaller texture budget needs a resize in kiln under either design (sections 1 and 3).
- **No independent measurement of any vendor's reduced output exists** that could be found, and a 2026 survey paper says no standard evaluation of topology or UV quality exists for generated assets at all (section 1).
- **The Blender route runs headless and is fast.** In the trial, decimating a 109,114-triangle and a 771,724-triangle scan to 5,000 triangles, unwrapping, baking three 2K maps and exporting GLB took 21 and 45 seconds in background mode, with the bake running on the GPU (section 7).
- **The Blender route has documented and observed failure modes.** The manual says automatic unwrapping suits "mechanical objects or architecture" and that baking without a cage "produces glitches on the edges". In the trial, Smart UV Project cut a 5,000-triangle rock into 317 and 560 islands with a fifth to a quarter of all edges as seams; one of the two results showed a visible web of dark lines; and importing a glTF without welding produced cracks after decimation (sections 2 and 7).
- **Kiln needs a reduction path of its own whatever is decided for generated assets**, because bought and hand-modelled assets enter after generation and a dense scan from a library has no generator to reduce it (section 5).
- **Quads have no value at render time for a static asset.** glTF stores triangles, Blender's exporter triangulates, and Tripo's quad output forces FBX, which Bevy cannot load (section 4).
- **Cost points different ways per vendor.** Reduced output costs more than dense on Tripo (plus 10 credits for `smart_low_poly`; P2 is 110 credits against 30), less on Meshy (15 against 30), and the same on Rodin (section 6).

### What the evidence does not settle

- Whether any vendor's reduced output looks better or worse than a Blender decimate-and-bake of the same vendor's dense output, at the same triangle count, for the kinds of static asset kiln handles. Nothing published compares them.
- Whether the vendors' low-poly models give a cleaner **silhouette** (outline) on hard-surface props such as crates and building pieces than edge-collapse decimation does. The vendors claim "hand-crafted, clean topology"; the trial used only rocks, where this does not arise.
- What the UVs of a vendor's reduced output are like, and whether kiln could use them without unwrapping again.
- What a dense generated mesh is like as input to Blender: whether it is welded, closed, and how fragmented its UVs are. The trial's inputs were photogrammetry scans with artist-made UVs, which are kinder inputs.
- Why one of the two trial results showed visible lines, and whether a different unwrap or cage setting removes them.

### Measurements that would settle it

A trial with API access, on one reference image per asset kind (a rock, a hard-surface prop, a building piece), requesting from the same vendor both a dense output and a reduced output at the target profile's triangle budget, with the seed fixed where the vendor has one. For each pair, with the dense output reduced in Blender to the same budget:

1. **Triangle count returned against triangle count asked for**, for the vendor's output.
2. **Distance between the reduced surface and the dense surface**, in millimetres and as a share of the asset's size, in both directions (reduced to dense catches bulges; dense to reduced catches lost parts).
3. **UV figures:** island count, share of edges that are seams, share of the texture square covered, texels per metre at the profile's texture size, and the vertex count after export.
4. **What the normal map contains:** whether the vendor's normal map shows the dense mesh's surface detail or only fine texture grain, judged by rendering both under the same grazing light.
5. **Defects:** boundary edges, cracks, baked-in lighting, visible seams, judged in the viewer at the profile's viewing distance in Bevy.
6. **Repeatability:** the same request twice with the same seed; compare the files.
7. **Cost and failures:** credits per accepted asset including failed tasks, and how often a reduced-output request fails where a dense one succeeds.

Items 2, 3 and 5 are already computed by the trial script's method (section 7), so the open work is the vendor side.

## 1. What each vendor's reduction does

All facts in this section are from the vendors' API documentation, read as raw text. "Faces" below means triangles unless quads are stated.

### Tripo3D

Source for all of this subsection unless stated: [Tripo API documentation, full text](https://developers.tripo3d.com/llms-full.txt), which is the raw Markdown of pages such as [Image to 3D, H series](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard), [Retopology](https://developers.tripo3d.com/en/docs/mesh-decimate), [Convert Format](https://developers.tripo3d.com/en/docs/models-convert) and the [changelog](https://developers.tripo3d.com/en/docs/changelog). Prices are from the [API pricing page](https://developers.tripo3d.com/en/pricing), where 1 credit is $0.01.

Tripo has four ways to get fewer faces.

**1. `face_limit` on dense (H series) generation.** It is described as "Maximum polycount for the output mesh"; if omitted, "the model uses adaptive topology". The upper limit is 1,500,000 on model v3.1 (2,000,000 with detailed geometry). No lower limit is stated for this mode. The documentation does not say how the limit is reached (decimation or otherwise) and gives no tolerance. No extra charge is listed for setting it at generation.

**2. `smart_low_poly: true` on H series generation.** Described as "Whether to generate a low-poly model with hand-crafted, clean topology style. Best suited for simple, non-complex inputs. Complex models may occasionally fail" (vendor claim, and the vendor's own stated limit). The face range becomes fixed: "Triangle 500 – 20,000, Quad 500 – 10,000". It adds 10 credits to the 30 of a textured image-to-3D generation.

**3. The P series models.** `P1-20260311` and `P2-20260801` (marked "Preview") are separate models "optimized for low-poly output with clean topology" (vendor claim). `face_limit` is 50 to 20,000 on P1 and 48 to 50,000 on P2 (48 to 25,000 with quads). The page adds: "For best quality: simple models start from 150 faces, complex models start from 250 faces. Lower values may result in poor generation quality." P2 costs 110 credits with standard textures, against 30 for the H series. P1's price could not be read (unverified; the pricing page shows it only behind a tab drawn in the browser). The models-and-versions page claims "cleaner topology and more precise face-count control" for P1 (vendor claim).

**4. The retopology endpoint, `POST /v3/mesh/decimate`.** It takes a previous task or an uploaded file (GLB, glTF, FBX, OBJ or STL up to 150 MB), so it accepts meshes Tripo did not make. It has "two algorithm tiers": `model=v2.0` for "smart highpoly-to-lowpoly retopology with clean topology preservation" at 30 credits, and `model=v1.0` for "basic decimation" at 10 credits. Parameters are `face_limit` ("Target polycount", with no range stated), `quad`, and `bake` (default true, "Bake textures onto the low-poly model", not supported by v1.0). Which maps are baked, and whether a normal map is baked from the dense geometry, is not stated.

A fifth route is incidental: the format-conversion endpoint also takes `face_limit` ("If omitted, the original face count is preserved"), `texture_size` (default 4096), `texture_format` (default JPEG), `bake` ("Bake advanced materials into base textures") and `pack_uv` ("Pack all UVs into a unified layout"). Setting `face_limit`, `texture_size` or `texture_format` moves the call from 5 to 10 credits.

Other points that bear on the question:

- **Textures.** `pbr` defaults to true and gives "`base_color`, `metallic`, `roughness`, `normal`" on H and P series alike. `texture_quality` has four levels; only `extreme` is given a size ("8K textures"). The pixel size of `standard` is not stated (unverified). Nothing says that the normal map of a `smart_low_poly` or P series output is baked from a denser mesh.
- **UVs.** `export_uv` (default true) "controls UV unwrapping during generation". Nothing is said about seams, islands, padding or density.
- **Quads.** On the H series, "Enabling `quad` will force the output format to `FBX`". Whether P2's quad output is also FBX is not stated (unverified). Quad output adds 5 credits on the H series.
- **Formats.** The response examples show a `.glb` URL. Conversion gives glTF, FBX, USDZ, OBJ, STL and 3MF.
- **Repeatability.** `model_seed`: "Using the same seed with the same input will produce an identical 3D mesh." `texture_seed`: "Using the same seed will produce identical textures." These are vendor claims and the only determinism statements found among the three vendors. Whether they hold for `smart_low_poly`, across the retopology endpoint, or across model versions is not stated.
- **An observation, not a finding.** The conversion endpoint's `texture_format` values (`BMP`, `DPX`, `HDR`, `OPEN_EXR`, `TARGA`, `TIFF`) are spelled as Blender spells its image formats. That is consistent with Blender doing the conversion on Tripo's side but does not show it (inference; unverified).

### Meshy

Source for all of this subsection: [Meshy API documentation, full text](https://docs.meshy.ai/llms-full.txt), which is the raw text of pages such as [Image to 3D](https://docs.meshy.ai/api/image-to-3d), [Remesh](https://docs.meshy.ai/api/remesh), [UV Unwrap](https://docs.meshy.ai/api/uv-unwrap), [Pricing](https://docs.meshy.ai/api/pricing), [Asset Retention](https://docs.meshy.ai/api/asset-retention) and the [changelog](https://docs.meshy.ai/api/changelog). The earlier note puts a Meshy credit at about $0.02 on the Pro plan.

Meshy has two ways to get fewer faces.

**1. Remesh**, either as a phase of generation (`should_remesh: true`) or as its own endpoint, `POST /openapi/v1/remesh`, which also accepts an uploaded model (GLB, glTF, OBJ, FBX or STL).

- `topology` is `triangle` ("Generate a decimated triangle mesh") or `quad` ("Generate a quad-dominant mesh").
- `target_polycount` runs from 100 to 300,000, default 30,000, and "the actual count may deviate from the target depending on the geometry". `decimation_mode` 1 to 4 chooses an adaptive level instead and overrides the target.
- On current models `should_remesh` defaults to false, and the page says: "For the highest-quality model, we recommend setting `should_remesh` to `false`."
- `save_pre_remeshed_model` also stores "an extra GLB file before the remesh phase completes", so one call can return both dense and reduced meshes.
- The standalone endpoint costs 5 credits.
- **Textures and UVs after remesh.** The API changelog says the endpoint "now preserves textures for uploaded models" (November 2025) and the task object describes the result as "the textured 3D model file". How textures are carried over is not described, and baking is not mentioned anywhere in the remesh documentation. Meshy's own web-app guide to the same tool lists as related steps "Retexturing after Remesh produces better results" and "UV needs to be regenerated after Remesh", and answers "Will Remesh reduce my model's detail?" with "Lower targets trade some detail for performance". Its table rates detail loss below 5,000 faces as "Noticeable". Its troubleshooting list names "holes after remeshing" and "small accessories disappear" as known outcomes.

**2. Smart Topology**, `model_type: "smart-topology"` with `ai_model: "meshy-t2"`: a separate model with "cleaner topology, natively separated parts, triangle output, and a face count you can set with `target_polycount`" (vendor claim). "The model is generated directly at this face count; no remesh runs". The range is 100 to 15,000, default 4,000. Output is triangles only; asking for quads "returns an error". It costs 15 credits with 2K or 4K textures, against 30 for a dense `meshy-7.1` generation.

Other points:

- **Churn.** The older `model_type: "lowpoly"` "will be retired on October 30, 2026", after which requests "will return an error". The first Smart Topology model, `meshy-t1`, was added and then removed from the documented values within about two months (changelog, July to September 2026).
- **Textures.** `enable_pbr` (default false) adds "metallic, roughness, normal" maps. `texture_resolution` is `2k`, `4k` or `8k`; nothing smaller.
- **UVs.** A separate [UV Unwrap endpoint](https://docs.meshy.ai/api/uv-unwrap) (5 credits) returns "a 'UV white model'" with "brand-new UV coordinates and no real texture", limited to 40,000 faces, and is "gated" per account "during rollout". It discards the texture, so using it means texturing again.
- **Repeatability.** The word "seed" does not occur anywhere in Meshy's API text. No repeatability is promised.
- **Retention.** API results "will only be retained for a maximum of 3 days", so a dense result cannot be sent back for remeshing later without uploading it again.

### Rodin by Hyper3D

Source: [Rodin Gen-2.5 API specification](https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5), read as raw page text.

Rodin has one model with a face-count setting.

- `mesh_mode` is `Raw` ("Triangle face", the default for Gen-2.5) or `Quad`.
- `quality` is a "preset target face count": for `Raw`, 1,000,000, 500,000, 60,000 or 20,000; for `Quad`, 50,000, 18,000, 8,000 or 4,000.
- `quality_override` is a "custom target face count from 500 to 2000000" (1,000,000 on the lower tiers; 200,000 at most in `Quad` mode).
- `quad_normal` (default false): "Bakes high-resolution geometry detail into a normal map during mesh refinement." This is the only parameter among the three vendors that is documented as carrying dense detail onto the reduced mesh. Whether it applies in `Raw` mode is not stated; its name suggests quads only (unverified).
- **Textures.** `material: "PBR"` gives "base color texture, metallicness texture, normal texture and roughness texture". The smallest texture size is 2K.
- **Formats.** `glb`, `usdz`, `fbx`, `obj`, `stl`. Nothing says quad output forces a format. A GLB cannot hold quads (section 4), so what a `Quad` GLB contains is unverified.
- **Cost.** "Base generation costs only 0.5 credits, and parameters not listed above do not incur additional charges." `mesh_mode`, `quality` and `quad_normal` are not among the listed surcharges, so reduced output costs the same as dense.
- **Repeatability.** `seed` is "a seed value for randomization in the mesh and texture generation" (0 to 65,535). The page does not say the same seed gives the same result.
- How the lower face counts are reached (decimation, remeshing or a different generation path) is not stated. No separate endpoint for reducing an uploaded mesh was found in the API index.

### The three side by side

| | Tripo3D | Meshy | Rodin Gen-2.5 |
|---|---|---|---|
| Reduce at generation | `face_limit`; `smart_low_poly` (500 to 20,000); P1 (50 to 20,000), P2 (48 to 50,000) | `should_remesh` + `target_polycount` (100 to 300,000); `meshy-t2` (100 to 15,000) | `quality` presets; `quality_override` (500 to 2,000,000) |
| Wording of the control | "maximum polycount" | "may deviate from the target" | "target face count" |
| Reduce an uploaded mesh | Yes, `/v3/mesh/decimate` | Yes, `/openapi/v1/remesh` | Not found |
| Dense detail baked to a normal map | `bake` on retopology v2.0; maps not stated | Not documented | `quad_normal`, off by default |
| UVs of reduced output documented | No | No; guide says regenerate after remesh | No |
| Smallest texture at generation | Not stated | 2K | 2K |
| Quads | FBX only (H series) | Remesh only; `meshy-t2` refuses | `Quad` mode |
| Extra cost of reduced output | +10 (`smart_low_poly`), +5 (quad), P2 110 against 30; retopology 10 or 30 | −15 (`meshy-t2` 15 against 30); remesh 5 | None |
| Same seed, same result | Stated for mesh and texture | No seed | Seed exists; no promise |

### Published samples and third-party measurements

- **No vendor publishes downloadable sample files of its reduced output** in the API documentation read here. The galleries on the vendors' sites were not examined (unverified whether files there state their generation settings).
- **No independent measurement of reduced output was found.** The earlier note found none for topology, UVs or seams in general; that still holds.
- A survey paper, [From Visual Synthesis to Interactive Worlds: Toward Production-Ready 3D Asset Generation (arXiv 2604.23629, April 2026)](https://arxiv.org/abs/2604.23629), read in the PDF's text, states that topology quality is "essential for production but almost never quantified", that "no standardized topology evaluation suite exists", and that "a comprehensive UV benchmark against production standards does not yet exist".
- **Secondary source, independence unknown:** a HackerNoon article, ["How I stress tested 3 AI 3D generators on the same inputs"](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show), reports latency, returned face counts (13,482 to 20,054 for one prompt) and blind votes on shape for Meshy 6, Tripo v3.1 and Rodin Gen-2.5. It refers to "our internal review process" without naming the organisation, publishes no files, and does not measure UVs, normal maps or reduced output against a requested count. It is not evidence for either design.
- **What the open-weights generators do** is the nearest published evidence of what "the generator reduces" can mean. The TRELLIS.2 example code first calls `mesh.simplify(16777216)` and then exports with `decimation_target = 1000000`, `remesh = True` and `texture_size = 4096`, using a library it describes as "mesh utilities used for high-speed post-processing, remeshing, decimation, and UV-unwrapping" ([TRELLIS.2 README](https://github.com/microsoft/TRELLIS.2)). The earlier note records that TRELLIS and TRELLIS.2 unwrap with xatlas. So for that family the generator's own reduction is decimation, automatic unwrapping and a bake: the same class of steps as design 1, run by someone else. Whether the hosted vendors' `face_limit` and remesh routes work the same way is not documented (inference; unverified).

## 2. What the Blender route needs, and how it automates

Blender is 5.2.2 throughout, run as `tools/bl` runs it: `--background`, which "runs in background (often used for UI-less rendering)" ([command-line arguments](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)).

### Reducing the triangle count

**The Decimate modifier** "allows you to reduce the vertex/face count of a mesh with minimal shape changes" and is meant for meshes that are "the result of complex modeling, sculpting" ([manual, Decimate](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/decimate.html)). It has three modes:

- **Collapse** "merges vertices together progressively, taking the shape of the mesh into account". Its `ratio` is "the ratio of faces to keep", and "triangles are used when calculating the ratio". A target triangle count is therefore `ratio = target / current`. This is the general-purpose mode.
- **Un-Subdivide** reverses a subdivision and "is intended for meshes with a mainly grid-based topology". It does not suit generated or scanned meshes.
- **Planar** "reduces details on forms comprised of mainly flat surfaces" by dissolving faces that meet at less than an angle limit, and can be told not to cross UV seams, material borders or sharp edges. It is the mode aimed at flat-sided shapes such as crates and walls.

In Python the modifier is [`bpy.types.DecimateModifier`](https://docs.blender.org/api/5.2/bpy.types.DecimateModifier.html), with `decimate_type`, `ratio`, `use_collapse_triangulate`, `angle_limit`, `delimit` and a read-only `face_count`.

The manual does not say what Collapse does to UVs. Blender's source enables interpolation of per-corner data during collapse (`USE_CUSTOMDATA` in [`bmesh_decimate_collapse.cc`](https://projects.blender.org/blender/blender/src/branch/main/source/blender/bmesh/tools/bmesh_decimate_collapse.cc), read on the main branch, not the 5.2 tag). In the trial the UV map survived decimation and stayed usable (section 7). So decimation does not destroy UVs in Blender; it distorts them, by an amount the trial did not measure.

**Remeshing** is the other family ([manual, Remeshing](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html)):

- **Voxel remesh** rebuilds the surface on a 3D grid, giving "uniform topology" with "no inner (self-intersecting) geometry". The manual says it should not be used for "reducing the face count of a mesh that otherwise has no problems with its geometry. It's better to use Decimate Geometry for this." Its use here would be repair: closing holes and removing inner surfaces before decimating.
- **Quad remesh** "uses the Quadriflow algorithm, which can produce better results but is also slower" and "doesn't clean up intersecting geometry". The manual again says decimation is better for plain face reduction, and that it is not for "final topology for a mesh that will be deformed".
- Both are scriptable: [`bpy.ops.object.voxel_remesh`](https://docs.blender.org/api/5.2/bpy.ops.object.html#bpy.ops.object.voxel_remesh) and [`bpy.ops.object.quadriflow_remesh`](https://docs.blender.org/api/5.2/bpy.ops.object.html#bpy.ops.object.quadriflow_remesh) (`mode='FACES'`, `target_faces`, described as an "approximate number of faces", and a `seed`). The API says of both: "All data layers will be lost". UVs are a data layer. After either remesh the mesh has no UVs and no way to show the old textures, so a new unwrap and a bake are unavoidable.

### Making new UVs

Operators, from the [manual's UV page](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/uv.html) and the [`bpy.ops.uv` reference](https://docs.blender.org/api/5.2/bpy.ops.uv.html):

- **Smart UV Project** (`bpy.ops.uv.smart_project`) "examines the angles between the selected faces, cuts them along any sharp edges, then projects each separated group of faces along its average normal". It needs no seams marked by a person, which is why it is the usual automatic choice. The manual calls it "a good method for, say, mechanical objects or architecture", and says of its angle limit: "A low limit will create lots of small UV islands with little distortion, while a high limit will create a few large islands with potentially more distortion."
- **Unwrap** (`bpy.ops.uv.unwrap`, methods Angle Based, Conformal and Minimum Stretch) "cuts the selected faces along their seams" and is "useful for organic shapes". It depends on seams having been marked, which is the part no operator does well automatically.
- **Lightmap Pack** places every face separately, "typically resulting in a disconnected and distorted UV map that would be unsuitable for manual texturing work".
- **Pack Islands** (`bpy.ops.uv.pack_islands`) arranges islands "so that they fill up the UV/UDIM space as much as possible", with a `margin` between islands. **Average Islands Scale** (`bpy.ops.uv.average_islands_scale`) evens out texel density between islands "based on their area in 3D space".

All of these ran in background mode in the trial.

### Baking from the dense mesh to the reduced mesh

From the [manual's baking page](https://docs.blender.org/manual/en/5.2/render/cycles/baking.html) and [`bpy.ops.object.bake`](https://docs.blender.org/api/5.2/bpy.ops.object.html#bpy.ops.object.bake):

- **Only Cycles bakes**, and "baking requires a mesh to have a UV map, and either a Color Attribute or an Image Texture node with an image to be baked to".
- **Selected to Active** bakes "shading on the surface of selected objects to the active object. The rays are cast from the low-poly object inwards towards the high-poly object."
- **Where the rays start** is set by `cage_extrusion` ("Inflate the active object by the specified distance for baking"), by `max_ray_distance`, or by a separate `cage_object`, which must have "the same Topology (number of faces and face order)" as the reduced mesh.
- **Bake types** include Normal, Diffuse, Roughness, Emit, Ambient Occlusion and Combined. Diffuse with only its Color contribution selected gives "the pass color, which is a property of the surface": the base colour without lighting. There is no Metallic type and no packed occlusion-roughness-metallic output, as the earlier note records.
- **Normal maps** default to tangent space with red, green and blue as +X, +Y, +Z, which the glTF exporter's manual says to keep "when using this bake panel for glTF" ([glTF exporter manual](https://docs.blender.org/manual/en/5.2/addons/scene_gltf2.html)).
- **Margin** extends each island's pixels outward, which "is important to avoid discontinuities at UV seams, due to texture filtering and mip-mapping".
- **Memory:** "There is a CPU fixed memory footprint for every object used to bake from", and the manual advises joining dense objects first.
- **Background mode and GPU.** The manual does not state whether baking works in background mode or on the GPU. In the trial it did both: `bpy.ops.object.bake` returned `FINISHED` under `--background --factory-startup`, on the CPU and on an NVIDIA RTX 3080 through OptiX once the script had enabled the device in Cycles' preferences (section 7). GPU device types are listed in the manual's [GPU rendering page](https://docs.blender.org/manual/en/5.2/render/cycles/gpu_rendering.html).

### Known failure modes

Documented by Blender or by the tools it relies on:

1. **Rays that start in the wrong place.** Without a cage "the rays will conform to the mesh normals. This produces glitches on the edges". With the automatic cage, "hard splits (e.g. when the Edge Split Modifier is applied) should be avoided because they will lead to non-smooth normals around the edges". When the automatic cage "does not give good results", the remedy the manual offers is a hand-adjusted cage mesh, which is not automatic ([baking](https://docs.blender.org/manual/en/5.2/render/cycles/baking.html)).
2. **Rays that hit nothing, or the wrong surface.** The manual describes this only as the dense object not being "entirely involved by the low-poly object". Too small an extrusion misses protruding detail; too large an extrusion lets rays hit a neighbouring part of the dense mesh. There is one distance for the whole object.
3. **Seams from automatic unwrapping.** Smart UV Project's own description is a trade between "lots of small UV islands" and "more distortion". Every seam is a place where the exporter must duplicate vertices (earlier note, glTF exporter) and where a baked map can show a line.
4. **Remeshing loses everything but shape.** "All data layers will be lost" ([`bpy.ops.object` reference](https://docs.blender.org/api/5.2/bpy.ops.object.html#bpy.ops.object.quadriflow_remesh)).
5. **Tangent space mismatch.** glTF says that when a file has no tangents, "client implementations SHOULD calculate tangents using default MikkTSpace algorithms" ([glTF 2.0 specification, section 3.7.2.1](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). Bevy 0.19.1 does that: its loader computes missing tangents "using the mikktspace algorithm" ([`bevy_gltf` loader](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs), [`bevy_mesh/src/mikktspace.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_mesh/src/mikktspace.rs)). Blender carries the same algorithm in its source tree ([`intern/mikktspace`](https://projects.blender.org/blender/blender/src/branch/main/intern/mikktspace)) and its baker converts normals to tangent space using mesh tangents computed from the UVs ([`render/intern/bake.cc`](https://projects.blender.org/blender/blender/src/branch/main/source/blender/render/intern/bake.cc); both read on the main branch, not the 5.2 tag). So Blender and Bevy agree on the algorithm, which is the favourable case. Two conditions still apply. First, the MikkTSpace reference code warns: "beware of quad triangulations. If the normal map sampler doesn't use the same triangulation of quads as your renderer then problems will occur", and advises "triangulating before sampling/exporting" ([`mikktspace.h`](https://github.com/mmikk/MikkTSpace/blob/master/mikktspace.h)). The reduced mesh should therefore be triangles before it is baked. Second, the mesh must not change between bake and export: tangents depend on positions, normals and UVs, so welding, re-unwrapping or re-computing normals after the bake invalidates the map (inference from the definition).
6. **A normal map made for one mesh, used on another.** A vendor's tangent-space normal map was made for the vendor's mesh. Keeping it on a mesh that kiln has decimated is an approximation, because the tangent frames have moved (inference from the same definition). This applies to any route that reduces triangles but keeps the original textures, in Blender or in the tools of section 3.
7. **Unwelded input.** glTF "requires discontinuous normals, UVs, and other vertex attributes to be stored as separate vertices", and Blender's importer has a "Merge Vertices" option that "attempts to combine co-located vertices where possible" and "currently cannot combine verts with different normals" ([glTF importer manual](https://docs.blender.org/manual/en/5.2/addons/scene_gltf2.html)). It is off by default. Without it, each UV island of the imported mesh is a separate sheet, and decimation pulls the sheets apart. The trial showed this (section 7).

## 3. Other tools that could do the reduction

Two groups matter. The first keeps the existing UVs and textures, so no bake is needed. The second makes a new surface or new UVs, so a bake is needed, and none of these tools bakes.

| Tool | Licence | What it does | Keeps UVs and textures? | Source |
|---|---|---|---|---|
| meshoptimizer `meshopt_simplify` | MIT | Edge-collapse simplifier that "follows the topology of the original mesh in an attempt to preserve attribute seams, borders and overall appearance" | Yes | [README](https://github.com/zeux/meshoptimizer/blob/master/README.md) |
| gltfpack | MIT | Command-line glTF optimiser; `-si R` "simplify meshes targeting triangle/point count ratio R" | Yes | [gltfpack README](https://github.com/zeux/meshoptimizer/blob/master/gltf/README.md) |
| glTF-Transform `simplify`, `weld` | MIT | `simplify` is "based on meshoptimizer"; `weld` merges duplicate vertices first | Yes | [`simplify.ts`](https://github.com/donmccurdy/glTF-Transform/blob/main/packages/functions/src/simplify.ts), [`weld.ts`](https://github.com/donmccurdy/glTF-Transform/blob/main/packages/functions/src/weld.ts) |
| glTF-Transform `textureCompress` | MIT | "Resizes textures to given maximum width/height"; converts between PNG, JPEG, WebP, AVIF | Textures only | [`texture-compress.ts`](https://github.com/donmccurdy/glTF-Transform/blob/main/packages/functions/src/texture-compress.ts) |
| glTF-Transform `unwrap` | MIT | New UVs through the `watlas` package (understood to be a WebAssembly build of xatlas; not checked); marked experimental | No: new UVs, no bake | [`unwrap.ts`](https://github.com/donmccurdy/glTF-Transform/blob/main/packages/functions/src/unwrap.ts) |
| xatlas | MIT | "Generates unique texture coordinates suitable for baking lightmaps or texture painting" | No: new UVs, no bake | [README](https://github.com/jpcy/xatlas) |
| Instant Meshes | BSD-style | Field-aligned quad or triangle remesher from a 2015 paper | No: new surface | [README](https://github.com/wjakob/instant-meshes), [licence](https://github.com/wjakob/instant-meshes/blob/master/LICENSE.txt) |
| Quad Remesher | Commercial | Automatic quad retopology plugin | No: new surface | Earlier note, section 3 |
| InstaLOD, Simplygon | Commercial | Automatic optimisation suites | Not read in this session | Earlier note, section 4 |

Points that decide how far the UV-keeping group can go:

- **Seams limit the simplifier.** meshoptimizer's README: "For meshes with inconsistent topology or many seams, such as faceted meshes, it can result in simplifier getting 'stuck' and not being able to simplify the mesh fully." Its error limit also means "it is not guaranteed to reach the target index count and can stop earlier". glTF-Transform repeats this: "Topology, particularly split vertices, will also limit the simplifier. For best results, apply a weld operation before simplification." A dense generated mesh whose UVs are cut into very many small islands is the hard case. Whether hosted generators' dense meshes are like that is unverified. The open TRELLIS models unwrap with xatlas (earlier note); how many islands that yields on their meshes was not measured here.
- **There is a way past seams, at a price.** `meshopt_SimplifyPermissive` "allows the simplifier to collapse vertices across attribute discontinuities", and `meshopt_simplifySloppy` "doesn't follow the topology of the original mesh" but "produces meshes with worse geometric quality and poor attribute quality" (same README).
- **Texture budgets are separable from triangle budgets.** Resizing the vendor's textures to the target profile's size needs no bake under either design.
- **Bevy constraints still apply.** The earlier note records that gltfpack quantises by default and that Bevy 0.19.1 rejects quantised or compressed meshes; `-noq` is needed.
- What InstaLOD and Simplygon offer for remeshing with baking was not read from their documentation in this session (two documentation URLs returned 404); the earlier note has their licence terms.

## 4. What matters for a static asset

**Quads do not survive to the engine.** glTF stores triangles; the earlier note cites the Khronos guidelines for this, and Blender's exporter triangulates on export. The same guidelines say a delivery mesh "can therefore contain highly adaptive, irregular triangle meshes (instead of quad meshes)" ([Khronos guidelines 1.0, Publishing Targets](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines-1.0/full-version/sec99_PublishingTargets/PublishingTargets.md)).

**What quads are for** is stated by the Blender manual in the negative: the quad remesher is for "generating a mesh for applying the Subdivision Surface Modifier or the Multiresolution Modifier", and clean topology is needed for "a mesh that will be deformed (e.g. a character that will be animated)" ([manual, Remeshing](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html)). A static asset is neither subdivided nor deformed. Meshy's own description of why Smart Topology matters begins "Cleaner topology deforms more predictably, so rigging and animation behave better" ([Meshy documentation](https://docs.meshy.ai/llms-full.txt)), which is not a benefit for a static asset, and Meshy's low-poly model outputs triangles only.

**Quads carry two costs here.** Tripo's H series quad output is FBX only, which Bevy cannot load, so it must pass through Blender. And MikkTSpace warns that a quad split differently by baker and renderer breaks the normal map (section 2, failure mode 5).

**What a quad mesh could still be worth** for a static asset is indirect: a person editing it later, or an unwrap that follows its edge loops. No primary source measures either (inference; unverified).

**What does matter, and where each is decided:**

- **Silhouette**, the outline against the background. A normal map changes lighting, not the outline, so the outline is whatever the reduced triangles give. It is decided by the reduction step.
- **Shading normals**, the directions used for lighting each vertex. Decimation changes them; hard edges on a crate need them split, and each split duplicates a vertex. Decided by the reduction step and by any smoothing kiln applies.
- **UV seams.** Each seam duplicates vertices on export and is a candidate visible line. Decided by the unwrap.
- **Texel density.** Decided by the unwrap's coverage of the texture square and the texture size. Poly Haven publishes a `texel_density` figure per model through its [API](https://api.polyhaven.com/assets?t=models), which shows a library treating it as a stated property; no generator states one.
- **Vertex count after export**, not triangle count alone, is what the GPU processes. In the trial the same 5,000 triangles exported as 3,027 vertices with the original UVs and 4,121 with Smart UV Project's (section 7).

## 5. Bought and hand-modelled assets

`CONTEXT.md` says a bought asset and a hand-modelled asset each "enters kiln at the stage after generation". Neither has a generator call.

- **Under design 1** they take the same path as a generated asset: a dense scan from a library is reduced, unwrapped and baked exactly as a dense generated mesh is. The trial in section 7 is in fact this case: its inputs were CC0 library scans, not generator output.
- **Under design 2** there is nothing to ask for a reduced version. A dense bought asset needs a reducer from somewhere. The options are a reduction path in kiln after all, or sending the bought file to a vendor's upload endpoint (Tripo's `/v3/mesh/decimate`, Meshy's `/openapi/v1/remesh`; Rodin has none that was found). The second makes a non-generated asset depend on a generator vendor, costs credits per asset, and sends a bought file to a third party, which the file's licence may or may not allow (not checked).
- A bought or hand-modelled asset that is already within budget needs no reduction under either design, only checks.

So design 2 cannot be the whole answer for kiln as `CONTEXT.md` scopes it. The open question is narrower: for generated assets, is the vendor's reduced output a better starting point than kiln's own reduction of the vendor's dense output?

## 6. Cost, repeatability and lock-in

**Cost per asset, list prices** (sources in section 1):

| | Dense, textured | Reduced at generation | Reduce afterwards |
|---|---|---|---|
| Tripo3D | 30 credits ($0.30) | 40 with `smart_low_poly`; P2 110 ($1.10) | Retopology 10 (basic) or 30 (smart) |
| Meshy | 30 credits (about $0.60) | `meshy-t2` 15 (about $0.30) | Remesh 5 (about $0.10) |
| Rodin Gen-2.5 | 0.5 credits | 0.5 credits | Not offered |
| Blender in kiln | — | — | No per-asset charge; seconds of local compute in the trial |

**Retargeting.** `CONTEXT.md` defines raw output as "kept unchanged as an input so that every later stage can be repeated without generating again". Under design 1 one dense raw output can be reduced again for a second target profile at no charge. Under design 2 the raw output is specific to one face count, and a second profile means a second paid call, which is also a second roll of the dice unless the vendor's seed holds (inference from the definitions and prices).

**Repeatability.**

- *Vendors.* Tripo states that a fixed seed gives an "identical 3D mesh" and "identical textures" (vendor claim, untested). Rodin has a seed and no promise. Meshy has no seed. The earlier note records that model versions are retired, which ends repeatability regardless: Meshy's `lowpoly` mode stops working on 2026-10-30.
- *Blender.* No source states that decimation or baking is deterministic. In the trial, three runs of the same decimation gave byte-identical GLB files; two identical GPU runs gave byte-identical base-colour maps and normal maps that differed in 9 of 16.8 million bytes of pixel data (section 7).

**Lock-in.** What swapping generators would break:

- *Under design 1*, kiln depends on each vendor for one thing: a dense textured mesh in a format Blender imports. All three offer that as GLB. What still differs per vendor is the state of the dense mesh (welded or not, closed or not, how its UVs are cut, whether lighting is baked into the colour), which kiln's reduction must tolerate.
- *Under design 2*, kiln depends on each vendor's reduction: its parameter names, its face ranges (500 to 20,000, 100 to 15,000 and 500 upward do not overlap fully), its meaning of the number (a maximum, a target, a target that "may deviate"), its output format (FBX for Tripo quads), and its unstated UV and texture conventions. A target profile whose budget is outside one vendor's range cannot be served by that vendor's reduced output. A vendor retiring a mode, as Meshy is doing this month, changes kiln's output for new runs.
- Under both, the checks kiln applies to the finished asset are the same, and under both they are needed: no vendor's "target" is a guarantee.

## 7. A single trial of the Blender route

**This is one trial on two files. It shows that the route runs and what it produced here. It does not show how it behaves in general, and its inputs were not generator output.**

### What was done

- **Inputs.** Two photogrammetry scans from Poly Haven, licensed CC0 ([licence page](https://polyhaven.com/license)), downloaded as glTF with 2K textures: [Namaqualand Boulder 06](https://polyhaven.com/a/namaqualand_boulder_06) (109,114 triangles, 0.68 × 1.21 × 0.65 m, a closed rock) and [Coast Rocks 05](https://polyhaven.com/a/coast_rocks_05) (771,724 triangles, 4.0 × 3.7 × 1.3 m, a patch of ground with rocks, open underneath). Each has base colour, a normal map and a roughness map on artist-made UVs.
- **Tool.** Blender 5.2.2, the repo's pinned build with a matching checksum, installed in a scratch directory because `.tools/` was not present. Run with `--background --factory-startup --offline-mode`, as `tools/bl` does. Machine: 16 threads, NVIDIA RTX 3080.
- **Script, in order.** Import (with and without "Merge Vertices"); duplicate; Decimate in Collapse mode with `ratio = 5000 / triangle count` and triangulation; export that as GLB with the original UVs and textures (variant A, no bake). Then Smart UV Project at a 66° angle limit; Pack Islands; Selected to Active bakes of Normal (tangent space), Diffuse colour only, and Roughness to 2,048-pixel images with an 8-pixel margin, cage extrusion set to 2% of the bounding-box diagonal, 4 samples; export as GLB (variant B). Then measurements and one Cycles render of each mesh from the same camera.
- **Not done.** The results were not loaded in Bevy and not run through the glTF validator. Metallic and ambient occlusion were not baked. No setting was tuned; each was a first guess. The cause of the defect described below was not diagnosed.
- Nothing from the trial is in the repository. Downloads, scripts and outputs were kept in separate scratch directories outside it.

### What was measured

| | Boulder 06 | Coast Rocks 05 |
|---|---|---|
| Triangles before → after | 109,114 → 5,000 | 771,724 → 5,000 |
| Whole script, wall clock (GPU bake; includes two renders of about 2.5 s each) | 21 s | 45 s |
| Decimate | 0.6 s | 7.7 s |
| Smart UV Project | under 0.1 s | under 0.1 s |
| Pack Islands | 7.2 s | 10.4 s |
| Each of three bakes, GPU (OptiX) | 1.0 to 1.2 s | 1.5 to 1.7 s |
| Each of three bakes, CPU (run on the unwelded import) | 1.6 to 1.7 s | not run |
| Bakes completed in background mode | Yes, all `FINISHED` | Yes, all `FINISHED` |
| Reduced → dense distance, mean / max | 1.1 mm / 5.6 mm (0.37% of diagonal) | 4.9 mm / 34 mm (0.60%) |
| Dense → reduced distance, max | 14 mm (0.92%) | 49 mm (0.87%) |
| UV islands: original / kept through decimation / Smart UV Project | 30 / 34 / 317 | 275 / 209 / 560 |
| Edges that are UV seams: kept / Smart UV Project | 504 of 7,500 (7%) / 1,460 (19%) | 1,271 of 7,526 (17%) / 1,863 (25%) |
| Share of texture square covered: original / Smart UV Project | 75% / 57% | 77% / 51% |
| Texels per metre at 2K: original / Smart UV Project | 1,115 / 993 | 345 / 301 |
| Vertices in the exported GLB: variant A / variant B | 3,027 / 4,121 | 3,956 / 4,867 |
| Texture pixels inside islands whose ray hit nothing | 0 | 2,103 of 2.1 million (0.1%) |
| GLB size: variant A / variant B | 10.9 MB / 16.3 MB | 11.6 MB / 17.1 MB |

### What was seen

- **The bake works headless and on the GPU.** Every bake finished in background mode with factory settings, on CPU and on OptiX.
- **The boulder's result looked right** in a render beside the dense mesh: the same outline to the eye, slightly softer surface detail, no visible lines.
- **The coast rocks' result had a visible defect:** a web of thin dark lines across the surface that the dense mesh does not have. The cause was not diagnosed. It is at least consistent with the 560 islands at a low texel density (301 per metre), where an 8-pixel margin is a large share of a small island, but that is a guess.
- **Importing without welding broke the mesh.** With the importer's default, the dense boulder arrived with 3,882 boundary edges (its UV islands were separate sheets). After decimation 1,204 boundary edges remained, the render showed thin dark cracks on the surface, and 361 texture pixels got no ray hit. With "Merge Vertices" on, boundary edges were 0 before and after, and there were no cracks.
- **The decimator kept the UVs.** The original UV map was still present and usable after Collapse (variant A), with fewer seams and better coverage than the automatic unwrap. Variant A needed no bake at all, but it reuses a normal map made for the dense mesh (section 2, failure mode 6), and its appearance was not rendered or compared.
- **Triangle count is not the texture budget.** Both variants are 5,000 triangles and 11 to 17 MB, nearly all of it three 2K images.
- **Repeatability.** The decimated GLB was byte-identical across three runs. Of the baked maps in two identical GPU runs, base colour was byte-identical; the normal map differed in 9 of 16.8 million bytes of pixel data, and the roughness map's file differed too.

## 8. What remains unknown

1. **The quality of vendor reduced output**, by any measure. Section 1 has only vendor wording.
2. **Whether a vendor's normal map carries dense detail** on `smart_low_poly`, P series or `meshy-t2` output, where no dense mesh is documented to exist, and on Tripo's retopology `bake`.
3. **The state of dense generated meshes as Blender input:** welded, closed, single surface, UV fragmentation, lighting baked into colour. The trial's scans were clean inputs.
4. **Hard-surface props.** Both trial inputs were rocks, where irregular triangles and a soft outline are forgiving. Whether Collapse (or Planar) keeps a crate's edges straight at a low triangle count, and whether Smart UV Project behaves as well as the manual's "mechanical objects or architecture" suggests, was not tried.
5. **Thin and detached parts.** Meshy's guide names "small accessories disappear" for its remesh; the same is plausible for edge collapse and for a single cage distance, and was not tried.
6. **The cause and cure of the line defect** in the second trial result.
7. **How the result looks in Bevy**, with Bevy's own tangents and without mipmaps for PNG (earlier note, section 5).
8. **Whether Tripo's seeds hold** as stated.
9. **Budgets.** `CONTEXT.md` says a target profile carries triangle and texture budgets, and the earlier note found no primary source for the numbers. Which design fits depends on them: every vendor's low-poly route has a ceiling (15,000 to 50,000 faces) and no vendor's textures go below 2K.

## 9. Synthesis

**This section is synthesis.** It is the author's reading of the facts above, not statements from a source, and it is not a decision.

**The two designs are less separate than they look.** Design 2 does not remove the reduction path from kiln: bought and hand-modelled assets need one (section 5), texture budgets below 2K need a resize whichever vendor is used (section 1), and no vendor's face count is a guarantee, so kiln must check and be able to correct (section 1). What design 2 could remove is the unwrap and bake for generated assets only, and only if the vendor's UVs and textures turn out to be usable as delivered, which nothing documents.

**The evidence for design 1 is about control and coverage.** It works on every source, gives an exact triangle count, lets one raw output serve several target profiles, costs nothing per asset, and depends on vendors for the least. It ran headless in under a minute. The evidence against it is about quality and effort: Blender's manual says its automatic tools are limited, the automatic unwrap made many times more islands than the artist's UVs it replaced, one of two first attempts had a visible defect, and each failure mode in section 2 is something kiln would have to detect and handle.

**The evidence for design 2 is about shape, and it is all vendor claim.** The one thing a vendor's low-poly model could do that decimation cannot is lay out a low triangle count deliberately, as a person would, which matters most for the outline of flat-sided props. If that claim is true it is a real advantage for crates and building pieces and little advantage for rocks. The evidence against is that the control is approximate, the UVs are undocumented, the ranges and meanings differ per vendor, one vendor's mode is being retired this month, Tripo charges more for it, and it leaves non-generated assets uncovered.

**A hybrid follows from the facts without choosing a winner.** Three observations point to it:

- Kiln's own reduction is needed regardless, so it is the base path.
- A vendor's low-poly model (Tripo P series, Meshy T2) is better thought of as a different generator than as a reduction: it produces a different shape from the same reference image, with no dense counterpart. It could be offered at shape review as an alternative raw output, where a person already judges shape against the reference image, and then pass through the same checks.
- A vendor's reducer that accepts uploads (Tripo retopology, Meshy remesh) is interchangeable in principle with Blender's Decimate: mesh in, smaller mesh out. If the measurements in the summary showed one to be better for some asset kind, it could stand in for the reduction step on those assets without changing what the raw output is.

**The cheapest next evidence** is the first four measurements in the summary on one hard-surface prop, since that is where the two designs are most likely to differ and where this note has no data at all.

## What could not be verified, and where sources disagreed

**Not verified from a primary source**

- Tripo: the price of P1; the pixel size of `standard` and `detailed` textures; whether P2 quad output is FBX; which maps the retopology endpoint's `bake` produces; the face range of the retopology endpoint; how `face_limit` on dense generation is achieved; whether seeds give identical output in practice.
- Meshy: how remesh carries textures over; whether any normal map reflects dense geometry; whether `meshy-t2` output has usable UVs.
- Rodin: whether `quad_normal` applies in `Raw` mode; what a `Quad` GLB contains; whether a fixed seed repeats; how lower face counts are reached.
- All three: UV conventions of any output; any published sample file of reduced output with its settings.
- Any independent measurement of reduced output: none found.
- Blender: whether baking in background mode and on GPU is documented anywhere (the manual pages read do not say; the trial showed both working); whether Decimate and bake are deterministic by design.
- Blender source files were read on the main branch, not at the 5.2 tag.
- InstaLOD and Simplygon capabilities were not read in this session.
- The common practice of baking metallic by routing it through the Emit bake type is not in the manual pages read (secondary knowledge; unverified here).
- The observation that Tripo's conversion options resemble Blender's is not evidence of what Tripo runs.

**Sources disagree**

- Tripo on P1's lower face limit: the P series page says 50, the documentation index says 48 (already noted in the earlier note).
- Tripo on what `tripo-p1` is for: the models-and-versions page lists it under both "Highest quality" and "Low-poly / game assets".
- Tripo on what `face_limit` means: "maximum polycount" on generation pages, "target polycount" on the retopology page.
- Meshy on remesh and textures: the API changelog says remesh "preserves textures for uploaded models"; the web-app guide says to regenerate UVs and retexture after remesh.
- Poly Haven on triangle counts: its API reports `polycount` 204,584 for Namaqualand Boulder 06, while the glTF it serves holds 109,114 triangles. The figures in section 7 are counted from the files.

## Method

Research was done on 2026-10-07. Vendor API documentation was downloaded as raw text (Tripo's and Meshy's `llms-full.txt`, Rodin's page HTML stripped of tags) and read directly, not through a summariser. Blender manual and API pages, tool READMEs and source files, the MikkTSpace header, and the survey paper's PDF text were read the same way. Bevy facts were read from the 0.19.1 crates in the local cargo registry. Two web searches were used only to look for third-party measurements; the one article and one paper they led to were then read in raw text. The earlier note's facts are cited as "earlier note" and were not re-verified except where a quotation appears here.

The trial in section 7 was run once per configuration (twice for the repeatability check) in a scratch directory outside the repository. No generator API was called and no account was created. No file from the `first-attempt` tag was used.
