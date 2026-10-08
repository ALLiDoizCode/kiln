# One video: local generators (TRELLIS.2, Pixal3D) in ComfyUI, made watertight and reduced to a baked low-poly model with headless Blender

Researched 2026-10-08. The video, its linked repository and every page cited below were read on that date. The tools shown are weeks old (the node packs were created on 2026-09-11 and the workflow repository on 2026-09-27); check each again before relying on it.

This is a research note on one source. It builds on four earlier notes, called "the notes" below: [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md), [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md), [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md) and [`mixar-vs-tripo.md`](mixar-vs-tripo.md). It does not choose anything and does not draw on the `first-attempt` tag.

**Nothing here was tested.** The video was not watched: its automatic captions were read, 56 still frames were extracted and about 30 of them were looked at. The linked repository's files were read as text. Nothing was installed, run or signed up for.

## The question

The owner supplied [this video](https://www.youtube.com/watch?v=dmDrktqyT5o) as further material on how to get game-ready 3D models with an LLM, a generator, an image generator and Blender. What does it show, how far can it be trusted, and what does it mean for the design being considered?

## How to read this

- **Shown** means it is visible in a frame of the video. **Said** means it is in the captions only. The captions are automatic, not written by the creator, and garble names: "Tralit 2" is TRELLIS.2, "Pixel 3D", "PixArt 3D", "Pixar 3D" and "Pix A19" are Pixal3D, "QMesh" is CuMesh, "most at tech" is MostAadTech, "GAB" is GLB, "boxes size" is voxel size. Numbers that are only said are marked as such.
- **Repository** means the statement was read in the creator's published files (the README, the four workflow files, the installer). **Docs** means a tool's own page says so.
- **Inference** means the sentence is this note's reasoning.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, review pictures, asset record, static asset, production ready) are used as `CONTEXT.md` defines them. The video says "game-ready"; that is its word, not a claim that anything passed a check.
- Timestamps link to the moment in the video.

### Terms used here

The notes define mesh, triangle, UV, seam, island, PBR, normal map, decimation, baking, cage, manifold, boundary edge, headless, seed and voxel remesh. Terms added by this note:

- **Watertight:** a mesh whose surface is closed, with every edge shared by exactly two faces. No holes, no stray sheets. 3D printing requires it; a game does not, but the repair steps that produce it also remove hidden inner faces.
- **High-poly and low-poly:** the dense mesh (millions of triangles) and the reduced one (thousands). "High to low" is the trade's name for reducing the mesh and baking the dense one's detail into the low one's texture maps.
- **ComfyUI:** a free program in which a job is drawn as a graph of boxes ("nodes") joined by wires. A saved graph is a **workflow**, a JSON file. It was built for image generation and now runs 3D generators too. A **node pack** is an add-in that supplies more nodes.
- **VRAM:** the memory on the graphics card. It decides which generators can run on a machine.
- **Open weights:** a generator whose trained model can be downloaded and run on one's own machine, as opposed to a hosted service such as Tripo.
- **UV chart:** the same thing as a UV island.

## The source and its grade

| | |
|---|---|
| Title | "3D AI Models Are Finally Watertight (6GB VRAM, Free & Local)" |
| Channel | PixelArtistry (`@PixelArtistry_`), 50,400 subscribers. The presenter gives his name as Philip and says he is a professional VFX artist who has "worked on productions for Marvel and Netflix for the past 7 years" ([0:57](https://www.youtube.com/watch?v=dmDrktqyT5o&t=57s); said, not checked) |
| Uploaded | 2026-09-30 |
| Length | 26:31, 26 chapters |
| Views, likes | 55,067 and 1,170 on the day of reading |
| Captions | Automatic only (English) |
| Stated purpose | "three comfy UI workflows" that give "watertight meshes straight out of" TRELLIS.2 and Pixal3D and "a fully high-to-low poly pipeline with baked textures" ([0:20](https://www.youtube.com/watch?v=dmDrktqyT5o&t=20s)) |
| Linked files | [`pixelartistry/PixelArtistry-Watertight-Meshes`](https://github.com/pixelartistry/PixelArtistry-Watertight-Meshes), MIT, read at commit `5b3a0e9`: a README, four workflow files and a Windows installer |

**Grade: interested party; hands-on; four objects; workflows published, models not.**

- No sponsor is named in speech or in the description. But the first line of the description sells the creator's own coming product, "a Trellis2 + Pixal3D Workflow Pack — an in-depth PDF guide + ComfyUI workflows", with a waitlist for "early-bird pricing", and a later line says "I'm building a 3D AI course". The free workflows shown are the lead-in to those.
- The description carries referral links to Tripo, Meshy, 3DAIStudio and Hitem3D with the notice "Some of the links above are affiliate links". None of those four is used or mentioned in the video.
- He is the author of the workflows he demonstrates, and credits the nodes they rest on to another person, MostAadTech ([1:40](https://www.youtube.com/watch?v=dmDrktqyT5o&t=100s)).
- Four objects are generated on screen: three characters (a warrior, a fox, a monster) and one prop (an axe). No model file is published. Nothing is shown in a game engine.

**There is no LLM in this video.** No Claude, no MCP server, no agent, no skill, no text prompt of any kind. It is not the missing evidence of Claude with a generator and Blender. It bears on a different part of the design: which generator, and what the stages after it can look like.

No text addressed to an AI agent was found in the captions, the description, the README or the notes inside the workflow files.

## Summary

### What the source supports

- **A whole chain from one picture to a reduced, textured `.glb` exists as free software that calls Blender headless, and its settings are published.** The steps are: generate a dense mesh, rebuild it as a closed surface, reduce it in Blender, unwrap UVs, bake the dense mesh's maps onto the reduced one in Blender, weld vertices. Every value is in the workflow files (section 2).
- **It was shown working on one static prop.** An axe went from picture to a 4,000-face textured model ([21:25](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1285s)). No time is given for that run; the runs that are timed took 360 to 570 seconds on the creator's graphics card.
- **The raw generator output is as bad as the notes guessed, by the creator's account and the model's own card.** "There are holes, faces hidden inside the mesh, and millions of polygons" ([0:20](https://www.youtube.com/watch?v=dmDrktqyT5o&t=20s)). The logs on screen show 16 and 24 million faces before reduction.
- **Two of the four objects showed faults the automatic chain did not fix.** On the warrior: a wrong face, stray extra geometry at the higher setting, and wrong eyes in the texture. On the fox: it came out turned to one side. His remedy each time is to generate again with another seed or the other generator (section 3).
- **The topology of the low-poly result is poor by his own word**, and its UVs are in over a thousand pieces (section 3).
- **A `.glb` read without joining vertices shows its UV seams as open edges.** 23,504 "non-manifold edges" on the fox became 0 after Merge by Distance ([22:17](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1337s)). This is the same effect the notes measured on a boulder.
- **Add-ons break headless Blender.** He recommends "a clean Blender install" ([3:15](https://www.youtube.com/watch?v=dmDrktqyT5o&t=195s)); the README names the add-ons that failed. `tools/bl` already starts Blender with factory settings.

### What the source does not settle

- Whether any result is production ready for any target profile. Nothing is measured against a budget, opened in an engine or seen close.
- Whether this runs on Linux, or on a 6 GB card. Both are said; neither is shown, and one node pack's own README lists Windows only (section 5).
- How these generators compare with Tripo on the same picture. No hosted generator appears.
- Anything about an LLM's part.
- Size, pivot, the facing a game expects, baked-in lighting, repeatability of a seed, and licence. None is discussed.

### The smallest experiments

Section 9 lists them. The cheapest needs no generator at all: take any dense `.glb` kiln already has and try the video's order of stages (voxel remesh, staged decimate, unwrap, bake from the dense one) through `tools/bl`, with the video's numbers as the starting values.

## 1. Tools and versions

| Tool | Version shown or stated | Where |
|---|---|---|
| Generators | Pixal3D (Tencent ARC) and TRELLIS.2 (Microsoft), switched by one toggle. Model files `pixal3d_int8_convrot.safetensors` and `trellis_2_int8_convrot.safetensors`, repackaged for ComfyUI by Comfy-Org | Workflow files; [6:55](https://www.youtube.com/watch?v=dmDrktqyT5o&t=415s) |
| Host program | ComfyUI through "ComfyUI Easy-Install"; Python 3.12, PyTorch 2.8, CUDA 12.8 | Said at [4:35](https://www.youtube.com/watch?v=dmDrktqyT5o&t=275s); README |
| Node packs | Nine by MostAadTech, pinned by the installer to commits "tested on 2026-09-26"; VisualBruno's ComfyUI-Trellis2 | Installer text |
| Blender | 5.1.2 in the window's title bar ([10:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=645s)); he says "Blender 4.5" when pointing at the install folder ([8:55](https://www.youtube.com/watch?v=dmDrktqyT5o&t=535s)). Kiln pins 5.2.2 | Shown; said |
| Blender add-on | 3D Print Toolbox, used by hand in the window to check the result | [10:44](https://www.youtube.com/watch?v=dmDrktqyT5o&t=644s) |
| Operating system | Windows 10 or 11; NVIDIA RTX 20 series or newer; 32 GB of system memory recommended | README; [2:55](https://www.youtube.com/watch?v=dmDrktqyT5o&t=175s) |
| His graphics card | Not named in the video. The README's timings are "Measured on an RTX 5080"; a log on screen shows about 16 GB of graphics memory | README; [10:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=600s) |
| Image generator | None named. Where the four input pictures came from is not said | — |
| LLM, MCP servers, skills | None | — |

## 2. The workflow, step by step

### Who does what

- **The person** installs, pastes the path to Blender into one box, loads a picture, picks the generator with a toggle, sets two or three numbers, presses Run, and looks at the result. When the result is wrong he presses Run again.
- **The generator** makes a dense mesh and, in workflows 2 and 3, its colour and material data.
- **Fixed nodes** rebuild the mesh as a closed surface, unwrap UVs and weld vertices.
- **Blender** is started by two of those nodes with no window, as a worker, to reduce the mesh and to bake. The node pack's README gives the command: `blender --background --python decimate_only.py -- ...` ([LODTailor README](https://github.com/Mstafa-awad/LODTailor-The-Mesh-Trimmer-ComfyuiNode)).
- **Blender's window** is used by the person afterwards, only to look and to count defects.

### Setup ([1:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=105s) to [5:30](https://www.youtube.com/watch?v=dmDrktqyT5o&t=330s))

A Windows batch file is put in the ComfyUI folder and run. By the README it checks Python, PyTorch, CUDA and the graphics card, downloads the node packs at pinned commits, "Runs a quick watertight test on your GPU", installs the workflows, offers to download missing models from Hugging Face, and looks for Blender. The installer window is shown starting ([4:32](https://www.youtube.com/watch?v=dmDrktqyT5o&t=272s)); its full run is not.

### Workflow 1: picture to closed dense mesh ([6:38](https://www.youtube.com/watch?v=dmDrktqyT5o&t=398s))

1. **Load one picture.** The warrior is a full figure in a T-pose (arms straight out) on a plain background ([6:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=405s)).
2. **The workflow prepares the picture itself** (repository): it removes the background with a separate model (`birefnet`), crops to the subject at 1024 × 1024 with a 1.1 margin, and estimates the camera's field of view from the picture (`MoGe`), which Pixal3D takes as an input.
3. **Choose the generator.** Said, not shown as a comparison: Pixal3D "gives you in general more accurate results based on your image, while Trellis 2 gives more broader results, but is better in a single view, especially for the back side" ([7:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=420s)).
4. **Generate** in the model's stages: a coarse block shape, then the detailed shape. Resolution by graphics memory, shown as a table inside the workflow ([9:05](https://www.youtube.com/watch?v=dmDrktqyT5o&t=545s)): 6 GB, 1024; 8 GB and up, 1536; 16 GB and up, 2048.
5. **Make it closed and lighter**, four nodes in a row ([8:07](https://www.youtube.com/watch?v=dmDrktqyT5o&t=487s)). Values from the workflow file:

| Step | Node | Settings | What it does, by its author |
|---|---|---|---|
| 1 | Quad Reconstruct | resolution 1536 | "cleans the raw mesh and removes floating fragments". The workflow's note: it "flattens tiny surface detail" |
| 2 | WTiVo | input and final resolution 1536, `proxy_points` 12,000,000, `lambda_fill` 20, `component_mode` `largest` | Rebuilds the surface as "dense, closed, manifold" from a voxel field. `largest` "keeps only the main piece and drops loose fragments" |
| 3 | LODTailor, in headless Blender | `target_tris` 6,000,000, `relative_voxel_size` 0.001, voxel rebuild on, timeout 1,800 seconds | Voxel remesh, then Decimate in stages, then Merge by Distance |
| 4 | Fast Merge | distance 0.00001, mode `STRICT_BLENDER` | Welds duplicate vertices |

6. **Result.** "Prompt executed in 364.78 seconds" ([10:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=600s); he says 360). The same log shows WTiVo producing 23,893,588 faces in 122 seconds and the final mesh at 2,965,692 faces. No textures in this workflow: the material's colour comes from vertex colours ([15:52](https://www.youtube.com/watch?v=dmDrktqyT5o&t=952s)).
7. **Check by hand in Blender.** File, Import, glTF; then the 3D Print Toolbox's "Check All" ([11:12](https://www.youtube.com/watch?v=dmDrktqyT5o&t=672s)).

**The 2K variant** ([11:35](https://www.youtube.com/watch?v=dmDrktqyT5o&t=695s)) raises the resolution to 2048 and `proxy_points` to 25,000,000, uses 24 sampler steps in place of 12 and 20, and switches Quad Reconstruct off "because this one is causing issues". The README says why: with it on, the mesh grew "to 85M faces" and the reduce step "could no longer reduce it without breaking it". It took 540 seconds (said, [13:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=825s)).

### Workflow 2: picture to reduced, baked model ([16:24](https://www.youtube.com/watch?v=dmDrktqyT5o&t=984s))

It runs workflow 1's chain, then adds two groups. Values from the workflow file, confirmed in frames at [18:32](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1112s) and [20:48](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1248s):

1. **Textured dense mesh.** Unwrap UVs (segmenter `pec`, resolution 1536), bake the generator's colour and material data to 4096 × 4096 images, save as `PixelArtistry_highpoly`.
2. **Reduce**, in headless Blender (LODTailor): `target_tris` 30,000, 3 passes, ratios 0.5, 0.25 and 0.2, voxel rebuild on, `relative_voxel_size` 0.0015.
3. **Unwrap the reduced mesh** (same unwrapper, padding 2) and set smooth normals with a crease angle of 180 degrees.
4. **Bake dense onto reduced**, in headless Blender (Bake Forger): six maps, each 4096 × 4096: base colour, normal, roughness, metallic, emission and ambient occlusion. `tight_cage_extrusion_factor` 0.0019.
5. **Weld** (Fast Merge, distance 0.0001, mode `TEXTURE_SAFE`, which keeps the UV seams), save as `PixelArtistry_lowpoly`.

His guidance for settings, written in the workflow and said at [17:20](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1040s):

| Setting | Characters | Props and hard surfaces |
|---|---|---|
| `target_tris` | 20,000 to 30,000 | 500 to 1,000 |
| `relative_voxel_size` | 0.0015 | 0.05 in the workflow's note; "0.005" said at [20:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1245s) |
| `tight_cage_extrusion_factor` | 0.0019 | 0.019; "raise it if white patches appear" |

### Workflow 3: texture a mesh you already have ([23:01](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1381s))

A `.glb` is put in ComfyUI's input folder with the picture it was made from. TRELLIS.2 generates textures for that shape; the rest is workflow 2's reduce and bake. Meshes over 6 million faces are reduced to 6 million first. "Only use here trellis 2 for the texturing and not [Pixal3D] because [Pixal3D] will always give you black textures" ([25:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1500s)); the workflow's note gives the reason: Pixal3D "projects the image onto the model from the camera it estimated, so it can only texture shapes it generated itself".

## 3. What comes out

| Object | Kind | Workflow, generator | Faces shown | Time | Defects shown or admitted |
|---|---|---|---|---|---|
| Warrior | Character | 1, Pixal3D (the default) at 1536 | 2,965,692 | 364.78 s shown | "something went wrong in the face" ([10:38](https://www.youtube.com/watch?v=dmDrktqyT5o&t=638s)) |
| Warrior | Character | 1 at 2K | 3,246,252 reduced; 43,284,076 before reduction ([15:58](https://www.youtube.com/watch?v=dmDrktqyT5o&t=958s)) | 540 s said | "it added some geometry for some reason" ([13:10](https://www.youtube.com/watch?v=dmDrktqyT5o&t=790s)) |
| Warrior | Character | 2 | About 30,000 by the setting; not read off a frame | Not given | "the eyes are a bit not that well ... we would definitely need to fix then the eye and texturing like for example in blender or substance painter" ([18:40](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1120s)) |
| Fox | Character | 2, Pixal3D | 29,984 faces, 27,942 vertices | 477.97 s shown | Comes out turned to one side ([19:56](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1196s)); 1,199 UV charts |
| Axe | Static prop | 2 at 1536 | 4,000 ("3.8K verts / 4K faces") | Not given | None named. Seen in three frames only |
| Monster | Character | 1 with TRELLIS.2, then 3 | Not shown | 570 s said for the first step | None named |

- **Format.** `.glb` throughout, saved by ComfyUI and imported into Blender by hand.
- **Textures.** Six maps of 4096 × 4096 for every reduced model, the 4,000-face axe included ([21:25](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1285s)). The emission map for the axe is plain black.
- **One object, one material, by the look of Blender's list.** Each import is a single object (`Mesh_0`, `BakeLow`). The number of materials on the baked model was not readable.
- **Topology.** Irregular triangles of mixed size ([21:52](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1312s)). His words: "Obviously, this is not the best wireframe". He says the dense result is meant "for printing or retopologizing it later on" ([16:05](https://www.youtube.com/watch?v=dmDrktqyT5o&t=965s)).
- **UVs.** The log for the fox reads "29988 faces -> 1199 charts, atlas 1716x1709" for the reduced mesh and "4567522 faces -> 5846 charts" for the dense one ([19:46](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1186s)). About one island for every 25 triangles.
- **Pieces.** The reduce step's own check printed "watertight=False ... bodies=16" after the warrior and "bodies=25" and "bodies=9" in the fox's run, before the welding step ([10:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=600s), [19:46](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1186s)). He does not mention these lines. What "bodies" counts was not read in the node's source.
- **In Blender on import.** Upright, rotation zero, scale 1.000 ([10:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=645s)). Its size in metres is not shown. In the later line-up the objects carry scales of 1.458, 1.658 and 1.941, set by him for the shot.
- **In a game engine.** Not shown.
- **Files.** The workflows and installer are published. No model, texture or input picture is.

### What the 3D Print Toolbox reported

| | Dense warrior ([11:12](https://www.youtube.com/watch?v=dmDrktqyT5o&t=672s)) | Fox as imported ([22:28](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1348s)) | Fox after Merge by Distance ([22:48](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1368s)) |
|---|---|---|---|
| Non-manifold edges | 0 | 23,504 | 0 |
| Bad contiguous edges | 0 | 0 | 0 |
| Intersecting faces | 0 | 3,117 | 2 |
| Zero faces | 2,965,692 | 27,876 | 27,876 |
| Zero edges | 3,039 | 0 | 0 |
| Thin faces | 6,771 | 288 | 288 |
| Overhang faces | 295,528 | 4,602 | 4,602 |

He reads out the first three rows of the first column and calls the mesh clean. Two things he does not mention:

- **"Zero faces" equals the whole face count of the dense mesh** and nearly all of the fox's. The panel's threshold is on screen: "Degenerate 0.0001 m". *Inference:* on a model about a metre or two tall with millions of faces, every face is smaller than that threshold, so the count says the faces are small, not that they are broken. A zero-area check with a fixed threshold is meaningless on a dense mesh.
- **The fox's 23,504 open edges are exactly the number the welding node logged as "render_bad_edges=23504"** one step earlier. The README explains: "A GLB can't give one vertex two UV coordinates, so UV seams otherwise show up as open edges." They are seams, not holes.

## 4. Time and cost

- **Money.** The title says "Free & Local". No per-generation charge exists: the models and nodes are downloaded and run on the user's machine. The cost is the machine. No figure for electricity or hardware is given.
- **Time per run:** 364.78 s (1536, closed dense mesh), 540 s (2K), 477.97 s (picture to baked low-poly), 570 s (TRELLIS.2, closed dense mesh). All on his card; the README names an RTX 5080.
- **Time for the prop:** not given.
- **Tries per kept result:** not given. He says of the 2K fault "Luckily, I did that beforehand as well" ([13:15](https://www.youtube.com/watch?v=dmDrktqyT5o&t=795s)), so at least two for that one.
- **Setup time:** not given.

## 5. Claims, and how each stands

| Claim | Where | Standing |
|---|---|---|
| Raw output from these generators has "holes, faces hidden inside the mesh, and millions of polygons" | [0:20](https://www.youtube.com/watch?v=dmDrktqyT5o&t=20s) | Asserted; no raw mesh is opened. Docs agree on holes: TRELLIS.2's card says "the generated raw meshes may occasionally contain small holes or minor topological discontinuities". The logs show the face counts |
| The dense result is watertight | [11:12](https://www.youtube.com/watch?v=dmDrktqyT5o&t=672s) | Demonstrated for one model by the toolbox's counts (0 non-manifold edges, 0 intersecting faces). Asserted for the monster ("confirmed", [23:22](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1402s)) |
| "We don't have any floating faces there anymore" inside the mesh | [11:25](https://www.youtube.com/watch?v=dmDrktqyT5o&t=685s) | Not made out. The frame at [11:28](https://www.youtube.com/watch?v=dmDrktqyT5o&t=688s) is a view from inside that shows shapes I could not identify |
| The low-poly models "are also usually watertight" | [22:12](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1332s) | Shown for the fox only after a manual Merge by Distance. The node's own check printed "watertight=False" before welding |
| It runs on 6 GB of graphics memory | Title; [7:50](https://www.youtube.com/watch?v=dmDrktqyT5o&t=470s) | Asserted. Every run shown is on a card with about 16 GB. TRELLIS.2's own card says "at least 24GB of memory is necessary" for Microsoft's code; the files used here are a smaller repackaging by Comfy-Org, whose memory needs I found no statement of |
| "It will also work with Linux, but the installation you would need probably to do by hand" | [3:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=180s) | Asserted, and in doubt. The WTiVo node's README lists "OS: Windows 10 / 11 x64" and says it ships precompiled `.pyd` files, which are Windows binaries. The installer is a `.bat` file |
| "Game-ready, low-poly version with baked textures at around 20,000 polygons" | [0:05](https://www.youtube.com/watch?v=dmDrktqyT5o&t=5s) | The files are produced on screen (about 30,000 faces for the characters, 4,000 for the axe). "Game-ready" is not tested against anything, and he says the wireframe is poor and the texture needs fixing by hand |
| Texturing "worked never that great" in his tests | [17:35](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1055s) | Demonstrated on the warrior's eyes |
| Baked low-poly and dense model are hard to tell apart "in the render view" | [25:58](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1558s) | Shown from a distance, for the monster. No close view |
| The 2K decimated mesh has "around 4 million polies" and the undecimated "64 million" | [15:55](https://www.youtube.com/watch?v=dmDrktqyT5o&t=955s) | Contradicted by the screen: 3,246,252 and 43,284,076 triangles. The README says 43M |
| For the axe he sets the voxel size to "0.005" and the target to 1,000 | [20:45](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1245s) | Contradicted by the screen. The frame after the run shows `target_tris` 4000 and `relative_voxel_size` 0.00150, the character default ([21:32](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1292s)). He says he ended at 4,000 faces. So the hard-surface voxel setting was not demonstrated, and three different values exist for it (0.05 written, 0.005 said, 0.0015 used) |
| Pixal3D follows the picture more closely; TRELLIS.2 does the back better | [7:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=420s) | Asserted. No object is generated with both |
| Pixal3D's odd facing "is due to the camera" it chooses; fix by using TRELLIS.2 | [19:56](https://www.youtube.com/watch?v=dmDrktqyT5o&t=1196s) | The turned fox is shown. The cause and the fix are asserted. Docs fit the cause: Pixal3D's card says it "lifts pixel features into 3D through back-projection" |
| Add-ons break the headless Blender runs | [3:15](https://www.youtube.com/watch?v=dmDrktqyT5o&t=195s) | Asserted; the README names Auto-Rig Pro and PolyQuilt |
| A fault is fixed by running again with another seed | [10:40](https://www.youtube.com/watch?v=dmDrktqyT5o&t=640s), [13:25](https://www.youtube.com/watch?v=dmDrktqyT5o&t=805s) | Asserted. No before and after of the same fault is shown |

## 6. What the tools' own pages say

Read 2026-10-08.

- **TRELLIS.2** ([model card](https://huggingface.co/microsoft/TRELLIS.2-4B)): "Input: Single Image"; "Output: 3D Asset (Mesh with PBR Materials)"; resolution "from 512³ to 1536³"; "Shape-conditioned Texture Generation: Generates textures for input 3D meshes and reference images", which is what workflow 3 uses. "This model is released under the MIT License." Hardware: "An NVIDIA GPU with at least 24GB of memory is necessary."
- **Pixal3D** ([model card](https://huggingface.co/TencentARC/Pixal3D)): from Tsinghua University and Tencent ARC Lab; "released under the MIT License"; third-party parts "remain licensed under their respective original terms". Its `NOTICE` file lists dinov2 (Apache-2.0), TRELLIS.2, Direct3D-S2 and MoGe (MIT). It has a low-memory mode at 1024 resolution. The card's header carries the line `extra_gated_eu_disallowed: true`, a Hugging Face setting; what it blocks in practice was not tested.
- **The files the workflows download** ([Comfy-Org/Pixal3D](https://huggingface.co/Comfy-Org/Pixal3D)): "Repackaged model files for ComfyUI", tagged MIT. One of them is named `dino_v3_L_naf_fp32.safetensors`, while Pixal3D's notice names dinov2. The licence of that file was not read.
- **The node packs** (GitHub records): LODTailor, Bake Forger and WTiVo are GPL-3.0, each created 2026-09-11 by one person, with 1, 0 and 7 stars. The creator's README: "If you plan to use your results commercially, check the license of every node pack and model you use."
- **LODTailor** ([README](https://github.com/Mstafa-awad/LODTailor-The-Mesh-Trimmer-ComfyuiNode)): sixteen steps, among them "Apply object transforms", "Join multiple imported mesh objects into one object", an "adaptive input seal", voxel remesh, "staged Decimate / Collapse passes", a "final Merge by Distance", then "Clear custom split normals and force flat shading". Voxel size is "max_dimension * relative_voxel_size", so the setting is relative to the object's size. "The final face count can differ" from the target.
- **Bake Forger** ([README](https://github.com/Mstafa-awad/LODTailor-Bake-Forger)): takes "an existing high-poly GLB and an already-prepared low-poly GLB with UVs, runs Blender in the background". "Blender's Cycles renderer lacks a native `METALLIC` bake pass", so it "temporarily reroutes the high-poly's Metallic input into an Emission shader" and bakes that. It checks which pixels the bake missed and fills them, and widens the cage when its probe says the tight one misses. It was reworked from an MIT script, `hp_to_lp_bake.py` in `mdj128/aeon-unity-tools`.
- **3D Print Toolbox** ([extension page](https://extensions.blender.org/add-ons/print3d-toolbox/)): carried from the notes; an extension, not shipped with Blender.

## 7. Against the earlier notes

Every row from the video has the same grade: interested party, hands-on, four objects.

| Topic | What the notes have | What this source shows | Agrees, adds or contradicts |
|---|---|---|---|
| Hands-on evidence of Claude plus a generator plus Blender making a static asset | None found | No LLM at all | The gap stays open. It adds the first end-to-end run found of generator plus headless Blender on a prop, with settings |
| Whether `image-to-model` takes a text prompt | No, for Tripo's API | These generators take a picture only; no text box exists in any workflow | Agrees in kind; a different generator |
| Reference image advice | One subject, plain background, even light, 1024 pixels or more; no angle stated | All four pictures are one subject on a plain background; the characters are in a T-pose. The workflow removes the background and crops by itself. Pixal3D builds the model as the picture's camera saw it, and one result came out turned | Agrees on the basics. Adds a reason to want a square-on picture for this generator (the cause is asserted, the turned result is shown) |
| Which Blender MCP servers work with Tripo and headless | Blender Lab's has a background mode; the community one refuses it | No MCP. Blender is run as `blender --background --python` by a node, with a timeout | Adds a third pattern, the one `tools/bl` already is. Agrees that factory settings matter: add-ons broke the runs |
| What a generated mesh holds | Dense; defects conceded by vendors; pieces and materials "not documented" | 16 to 43 million faces after the rebuild; holes and inner faces conceded; several "bodies" logged after reduction; vertex colours, not textures, until a bake | Agrees, with counts, for open generators. Says nothing of Tripo |
| Baked-in lighting | Tripo's `delight` needs texture model v3.5 | Not mentioned | Nothing |
| Whether LLM cleanup helps | No measurement | All cleanup is by fixed steps with two or three settings chosen by asset kind; the faults they do not fix are handled by generating again | Adds nothing on an LLM. Adds one example of fixed steps doing the whole of the mesh work |
| Joining vertices on import | "Unwelded import breaks decimation"; 3,882 boundary edges on a closed boulder until `merge_vertices=True` | 23,504 open edges on the fox until Merge by Distance; the README says to import "with Merge Vertices ticked" | Agrees, independently |
| Closing a mesh | "The only tool the manual describes as producing a manifold mesh is the voxel remesh, which costs the UVs" | A separate rebuild (WTiVo), then Blender's voxel remesh, then new UVs and a bake to get the surface data back | Agrees, and shows the order that pays the cost: close and reduce first, unwrap after, bake last |
| Automatic UVs | Blender's Smart UV Project cut a 5,000-triangle rock into 317 and 560 islands | 1,199 charts on 29,988 faces from ComfyUI's unwrapper | Agrees: a second automatic unwrapper, the same fragmentation |
| The 3D Print Toolbox | Not shipped; its counts can be taken with `bmesh` | Used by hand as the proof. Its zero-face count flagged every face of a dense mesh | Adds a caution about fixed thresholds (inference from one frame) |
| Normals after reduction | Custom normals do not survive repair steps | LODTailor forces flat shading by design; the workflow then smooths everything at 180 degrees | Adds: a normals stage has to follow the reduce stage. A 180-degree angle leaves no sharp edge, which would suit a creature and not a crate (inference) |
| Orientation and scale on import | Tripo faces +X, size arbitrary; kiln fixes both | Upright in Blender at scale 1; facing depends on the picture for Pixal3D; size never mentioned | Agrees that size is kiln's to set. Adds that facing may vary per picture with this generator |
| Cost per asset | About $0.30 a generation on Tripo's H series; "Self-hosting trades this for a 24 GB class GPU" (an older note) | No charge; 6 to 9.5 minutes a run on a 16 GB card; 6 GB claimed | Contradicts the 24 GB figure for this route, on the creator's word and a 16 GB demonstration. Microsoft's card still says 24 GB for its own code |
| Open generators run on Linux only | An older note: TRELLIS.2 "Linux only" | Windows, through ComfyUI; the closing node lists Windows only | Adds: the ComfyUI route reverses the platform question |
| Licence | Tripo's depends on the plan | Both models MIT by their cards; node packs GPL-3.0; one bundled file's licence unread | Adds a route whose model licence does not depend on a plan. Not a full reading of terms |
| Repeatability | Seeds documented; same result a vendor claim | The structure seed is set to "randomize" on purpose; two others are fixed at 42 and 43. Re-running is the repair method | Adds: as shipped, a run is not repeatable. Kiln's kept raw output already covers this (inference) |

## 8. Workflows and techniques the notes did not find

1. **A complete high-to-low chain as published settings.** Close, voxel remesh, staged decimate, unwrap, bake six maps from the dense model, weld. The notes established that each call exists in Blender; this is someone running them in that order on generated meshes.
2. **Staged reduction.** Not one Decimate to the target, but passes at ratios 0.5, 0.25 and 0.2, with a first guard reduction above 1,000,000 faces (LODTailor README).
3. **Voxel size relative to the object's largest dimension**, so one setting carries across objects of different size.
4. **Texture an existing mesh from its picture** (workflow 3). TRELLIS.2 documents this ability. It would let a shape be kept and only its textures made again, without a paid call.
5. **Metallic baked through emission**, because Cycles has no metallic pass.
6. **A bake that inspects itself**: finds pixels the rays missed, bakes again with a wider cage, fills what is left with neutral values.
7. **Two welding modes with different purposes**: one that joins everything for a geometry check, one that leaves UV seams alone for the file that ships.
8. **A switch between two generators on the same picture** as the answer to a bad back or a turned model.
9. **An installer that pins every dependency to a commit and runs a test on the user's card.** The same idea as `tools/install_tools.sh`.

## 9. What would change the design being considered, and what would not

**Everything in this section is inference.** The design being considered: Claude helps the owner write the reference-image prompt and choose generator settings; Tripo generates from the reference image through its CLI or API; kiln keeps the `.glb` as the raw output; a person reviews the shape; fixed headless Blender scripts fit it to the target profile, with Claude proposing per-asset settings that are recorded. The evidence grade is beside each point.

### What this source would change, or put in question

1. **Whether Tripo is the only candidate for the generator.** An open generator run locally has no charge per try and an MIT model licence, which removes two of the notes' open questions (cost of retries, and whether a pay-as-you-go customer is a "Paid User"). `learn/MISSION.md` already calls Tripo "a candidate to be evaluated, not a given". Against it: it needs an NVIDIA RTX card, the closing node lists Windows only, and its raw output is far denser than Tripo's low-poly models. *Evidence: model cards (docs) for the licence; one interested party on a 16 GB card for everything else. Whether the owner's machine can run it was not looked at.* It belongs in a generator trial, not in the design, until it has run once on the owner's hardware.
2. **The order of the stages after the raw output.** The video's order is: join vertices, close and remesh, reduce, set normals, unwrap, bake from the dense model, check. That order follows from two facts the notes already hold (a voxel remesh destroys UVs; an unwelded mesh cracks when reduced). The design's "fixed headless Blender scripts" did not yet have an order. *Evidence: four objects, one prop, no measurement; the reasons are from Blender's manual via the notes.*
3. **Which settings vary per asset, and so what Claude would propose and the asset record would hold.** The creator changes exactly these between objects: target triangle count, voxel size, cage distance, which generator, and the seed. That is a short, concrete list. *Evidence: his practice on four objects. Note that the one hard-surface setting he recommends was not the one he used.*
4. **How kiln counts open edges and zero-area faces.** Count after joining vertices by position, or UV seams are reported as holes. Use a threshold that scales with the object and its density, or every face of a dense mesh is reported as degenerate. *Evidence: two frames of a toolbox panel and a log line; the first point repeats the notes' own trial.*
5. **What the shape review can answer.** Two of four objects showed faults, the warrior three separate ones, and the remedy offered was always "generate again" (or, for the eyes, repair by hand). A review with only approve and reject fits that; it also means the number of tries per kept asset is a cost to record. With Pixal3D, "which way does it face" is a review question too. *Evidence: admitted on screen.*
6. **The texture stage needs its own budget.** The chain writes six 4096 × 4096 maps for a 4,000-triangle axe. On a GTX 1660 class card the textures, not the triangles, would be the load. Each map's size is a setting. *Evidence: one frame; the budget concern is from kiln's own profile, not from the video.*

### What this source would not change

1. **Claude's part.** No LLM appears. Nothing is learned for or against Claude writing the reference-image prompt, proposing settings, or staying out of the mesh.
2. **Tripo through its CLI or API.** Not used, not compared.
3. **Keeping the raw output and replaying from it.** The video's own method (a random seed, re-run until good) makes a kept file the only way to repeat a build.
4. **A person at the shape review.** The faults shown were found by a person looking.
5. **Headless Blender with factory settings.** Supported from an unrelated direction: his runs broke until add-ons were removed.
6. **Size as an input to a run.** Never mentioned.
7. **Kiln owning the stages after the generator.** The chain shown lives inside ComfyUI and Windows binaries, rests on node packs three weeks old by one author, and the Blender parts are GPL-3.0. Reading how they work is free; taking the code into kiln would bring that licence with it.

### What it suggests overall

The video is weak evidence for a strong hint: the mesh work after generation can be a fixed sequence with a handful of recorded numbers, and somebody has written that sequence down. It shows it working roughly, on characters more than props, with a person re-rolling faults and admitting the topology and texture are not finished. It says nothing on whether the result holds at 0.5 m in a game. The smallest experiments it points to:

1. **No generator needed.** On a dense `.glb` already to hand, run the stage order above through `tools/bl` with the video's starting values (voxel size 0.0015 of the largest dimension; decimate in passes of 0.5, 0.25, 0.2 to the profile's budget; bake at the profile's texture size), take it into kiln and look at the review pictures.
2. **A check on kiln's own counting.** Measure one textured `.glb` with and without joining vertices by position and compare the open-edge counts.
3. **Only if the hardware allows.** One reference image through TRELLIS.2 or Pixal3D locally and the same image through Tripo, both taken in with `python3 -m kiln run --model` and measured the same way.

## 10. Where this overlaps `videos-and-workspace-review.md`

That note, by another agent on the same day, covers six videos and a repository by a different creator; it existed when this one was finished and was read for this paragraph only. Both creators carry Tripo referral links, publish no models, show nothing against a budget, and work mostly on characters. They recommend opposite routes: that creator says to ask the generator for a low-poly quad mesh at the final count and not to reduce a dense one; this one generates dense and reduces with a bake. Neither compares the two. Both judge a result by its wireframe, which kiln's review pictures do not show. This video is the only one of the seven that runs Blender with no window and carries one static prop from picture to reduced, textured file.

## What could not be verified, and where sources disagreed

**Not downloaded, read or made out**

- The video's sound and motion. Only automatic captions and about 30 still frames at 720p were used.
- The second automatic caption track (`en`): the download was refused with "HTTP Error 429: Too Many Requests". The `en-orig` track was read in full; they are two forms of the same automatic captions.
- The comments (168). Not read.
- Parts of the log at [10:00](https://www.youtube.com/watch?v=dmDrktqyT5o&t=600s), which is blurred in the video; only the sharper lines are quoted.
- The inside view at [11:28](https://www.youtube.com/watch?v=dmDrktqyT5o&t=688s): shapes are visible that I could not identify.
- The face count of the reduced warrior and monster, and the axe's run time.
- The creator's pages on `pixel-artistry.com` (the TRELLIS.2 installation guide, the waitlist, the newsletter). Not opened.
- The source code of the node packs. Only the READMEs of LODTailor, Bake Forger and WTiVo were read; the other six packs, VisualBruno's ComfyUI-Trellis2, ComfyUI's own template and ComfyUI Easy-Install were not opened.
- The installer beyond its header, pins and Blender check. It embeds the workflows as encoded text, which was not decoded.
- The licences of the bundled `dino_v3`, `MoGe` and `birefnet` files, and whether ComfyUI's version of TRELLIS.2 still depends on the Nvidia libraries an older note flags as non-commercial.
- What Hugging Face's `extra_gated_eu_disallowed` setting does for Pixal3D.
- The presenter's stated background.

**Not established**

- That anything shown would run on the owner's machine, on Linux, or on 6 GB.
- That the same picture and settings give the same mesh twice.
- That any output would pass a kiln check or look right at 0.5 m.

**Where sources disagree**

- **Face counts:** "around 4 million" and "64 million" said; 3,246,252 and 43,284,076 on screen; 43M in the README.
- **Voxel size for hard surfaces:** 0.05 in the workflow's note, "0.005" said, 0.0015 used.
- **Blender version:** "Blender 4.5" said of the install folder; 5.1.2 in the title bar.
- **Memory:** 6 GB in the title; 24 GB in Microsoft's card for its own code; about 16 GB on the card used.
- **Linux:** "It will also work" said; "Windows 10 / 11 x64" in WTiVo's README.
- **Watertight:** claimed for the low-poly output; the reduce node's own log says "watertight=False" before the welding step, and Blender needed a manual merge.

## Sources

All read 2026-10-08.

**The video**

- [3D AI Models Are Finally Watertight (6GB VRAM, Free & Local)](https://www.youtube.com/watch?v=dmDrktqyT5o), PixelArtistry, 2026-09-30: metadata, description, chapters, automatic captions, 56 frames extracted and about 30 looked at.

**The creator's repository**

- [`pixelartistry/PixelArtistry-Watertight-Meshes`](https://github.com/pixelartistry/PixelArtistry-Watertight-Meshes) at commit `5b3a0e9`: `README.md`, `LICENSE`, the four files under `workflows/` (every node's settings and every note), and the header, pins and Blender check of `watertightMeshes_win_installer.bat`; its commit list and GitHub record (65 stars, 12 forks).

**The node packs** (README and GitHub record only)

- [`Mstafa-awad/LODTailor-The-Mesh-Trimmer-ComfyuiNode`](https://github.com/Mstafa-awad/LODTailor-The-Mesh-Trimmer-ComfyuiNode)
- [`Mstafa-awad/LODTailor-Bake-Forger`](https://github.com/Mstafa-awad/LODTailor-Bake-Forger)
- [`Mstafa-awad/WTiVo-WatertightVoxel-ComfyuiNode`](https://github.com/Mstafa-awad/WTiVo-WatertightVoxel-ComfyuiNode)

**The models**

- [microsoft/TRELLIS.2-4B](https://huggingface.co/microsoft/TRELLIS.2-4B): model card and record
- [TencentARC/Pixal3D](https://huggingface.co/TencentARC/Pixal3D): model card, `LICENSE`, `NOTICE` and record
- [Comfy-Org/Pixal3D](https://huggingface.co/Comfy-Org/Pixal3D): model card

**This repo**

- The four notes named at the top; [`3d-asset-pipeline-tools.md`](3d-asset-pipeline-tools.md) and [`game-mesh-kiln-or-generator.md`](game-mesh-kiln-or-generator.md) for what they say of open generators and voxel remeshing; [`videos-and-workspace-review.md`](videos-and-workspace-review.md) for section 10; `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md` and `tools/bl`.

## Method

Research was done on 2026-10-08. `yt-dlp` fetched the video's metadata and its automatic English captions; the captions were turned into plain text in 20-second blocks and read in full. A 720p video-only stream was downloaded, 56 frames were extracted with `ffmpeg` at moments chosen from the captions and chapters (settings panels, logs, Blender's statistics and toolbox panels, wireframes), about 30 were looked at, some enlarged to read small text, and the video file was then deleted. The repository linked in the description was read through GitHub's API as text; the workflow files were parsed to list each node's settings, which is where the exact values in section 2 come from. Model cards and licence files were fetched as raw text from Hugging Face.

Nothing downloaded was run, installed or built, and nothing was copied into kiln. No generator was called and no account was created. Facts about kiln are from `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md` and `tools/bl`. Only this file was written.
