# A trial of a local generator on the development machine: TRELLIS.2 and Pixal3D in ComfyUI, and the video's chain to a low-poly model

Measured 2026-10-08 on the development machine (an RTX 3080 with 10 GB). Everything it produced is in [`local-generator-trial/`](local-generator-trial/). The software tried is weeks old and one piece of it changed on the day; a second run next month may not behave the same.

This is a research note. It tests the workflow described in [`video-local-trellis2-pixal3d-watertight-low-poly.md`](video-local-trellis2-pixal3d-watertight-low-poly.md), called "the video note" below. It does not choose a generator and does not draw on the `first-attempt` tag beyond using pictures of the two specimens in `learn/specimens/` that the Tripo trial rendered.

## The question

Can the local workflow shown in [the video](https://www.youtube.com/watch?v=dmDrktqyT5o) be run and measured on this machine? If so: how long does it take, how much memory does it need, what comes out, and could what comes out go into a game that is sold?

## How to read this

- **Measured** means it was run on this machine on 2026-10-08 and the record is in [`local-generator-trial/`](local-generator-trial/).
- **Docs** means a tool's own page or source file says so. **Video** means the creator said or showed it, as the video note records. **Inference** means this note's reasoning.
- **One or two generations per condition is an observation, not a rate.** Two objects were generated. What is said of the crate is true of that crate. Nothing here says how often these generators make a good shape.
- **The video's tools and my substitutes are kept apart.** Two of the video's steps could not run on Linux here. Another node stood in for them. A substitute tests the idea of the step, not the video's claim about its own tool. Section 3 says which is which.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, review pictures) are used as `CONTEXT.md` defines them. No shape review was held: the owner is the reviewer, and the faults listed in section 5 are only what I saw.

### Terms used here

The earlier notes define mesh, triangle, UV, UV island, seam, normal map, decimation, baking, cage, watertight, boundary edge, non-manifold edge, welded, voxel remesh, ComfyUI, node pack, workflow, VRAM and seed. Terms added here:

- **Out of memory:** a step asked the graphics card (or the machine) for more memory than was free, and stopped with an error.
- **Sampler:** the part of a generator that turns noise into a result over a set number of steps. TRELLIS.2 runs four in a row: a coarse block shape, the shape at 512, the shape at the chosen resolution, and the colours.
- **Decode:** turning a sampler's compact result into the actual mesh or colours.
- **Resolution** (of the generator): the size of the 3D grid the shape is built on: 1024 means 1024 steps along each side. Not a picture size.
- **Quantised weights (`int8`):** a model file stored with fewer bits per number to make it smaller: 5.3 GB in place of 10.3 GB for TRELLIS.2. This is what the video uses and what was run here.
- **Segmentation fault:** a program stopped by the operating system for touching memory it should not. A crash, with no error message of its own.
- **Cold run:** a run on a freshly started ComfyUI, with nothing kept from an earlier run.
- **Peak resident memory:** the most ordinary memory (RAM) a program held at once.

## Summary

- **It runs, with changes.** TRELLIS.2 and Pixal3D both generated a mesh on this machine, on Linux, through ComfyUI's own built-in nodes. **The video's chain did not run as published**: two of its node packs have no Linux build, and three of its settings ran out of memory here. With one substitute step and four changed settings the chain produced a reduced, textured `.glb` from a picture.
- **Resolution 1536 does not fit on this 10 GB card.** The shape decode stopped, out of memory, twice. Resolution 1024 fits. The video's table gives 1536 for "8 GB and up".
- **Time, from a cold start, one picture to a 20,000-triangle textured model:** 439 seconds for the crate and 310 for the boulder with TRELLIS.2, 251 for the crate with Pixal3D. Of that the generator itself took 175, 115 and 88 seconds; the rest was the chain.
- **Memory:** the ComfyUI process peaked at 8.3 to 9.1 GB of the card's 10 (the desktop held 1.1 to 1.3 GB more), and at 12 to 16 GB of RAM. One of the video's settings, tried as published, took the machine to 1.4 GB of free RAM before I stopped it.
- **What the generator returns** is a mesh of 8.6 to 14.9 million triangles with a colour at every vertex, no UVs, no textures and no normals, 200 to 360 MB as a `.glb`. It is open: 12,000 to 38,000 edges on the rim of a hole.
- **What the chain returns** is one object, one material, 4,000 or 20,000 triangles, four 4096 × 4096 textures, 17 to 49 MB. After welding it has no open edge and is one piece, for all four finished models. The glTF validator found no error in any.
- **The shapes have plain faults.** The crate came out hollow with two of its six panels missing. The Pixal3D crate came out tilted. The boulder has dark specks in its texture and a ragged lower edge. None was put right by the chain.
- **The same seeds gave the same mesh, bit for bit, four times,** across restarts of ComfyUI. The chain after it is not repeatable: Blender's reduction gave slightly different meshes on each run.
- **Three things broke at random or by design.** Blender 5.2.2 crashed with a segmentation fault in 3 of 13 runs of the reduce step on the crate. ComfyUI's unwrap node failed once with an index error on a mesh it had unwrapped minutes before. And the video's welding node, given a mesh that was not closed, widened its merge distance 73 times until 18,551 triangles had become 10, then reported success.
- **Could it ship?** Not on what was read today. The TRELLIS.2 and Pixal3D weights are MIT. But both generators, as ComfyUI packages them, read the picture with **DINOv3**, a Meta model under its own licence, which is not MIT, is gated at its source, and whose reach over outputs is unclear. That is one open licence question in place of the Nvidia one the older note raised (the Nvidia libraries are not used on this route). Verdict in section 8: **unclear, not cleared.**

## 1. This machine

| | |
|---|---|
| Graphics card | NVIDIA GeForce RTX 3080, 10,240 MiB, driver 610.57.04. It also drives the display |
| Card memory held by the desktop | 695 to 1,566 MiB over the day; 1,116 to 1,325 MiB at the start of the runs reported below |
| Memory, processor | 31 GB RAM, 62 GB swap, 16 cores |
| System | Linux 7.2.5 (Omarchy, Arch-based). System Python 3.14.7, not used |
| Blender | 5.2.2, the pinned one in `.tools/blender` |
| Docker | Installed, but with no NVIDIA runtime (`docker info` lists only `runc`). Not used; nothing was done to change that |

## 2. What was installed, from where

Everything is under `.tools/local-gen/`, which `.gitignore` already ignores (`/.tools`). Nothing was installed system-wide and no `sudo` was used. Caches (`HF_HOME`, `TORCH_HOME`, `UV_CACHE_DIR`, the pip cache, `XDG_CACHE_HOME`, `TMPDIR`) point into the same directory.

### Programs

| What | Source | Version |
|---|---|---|
| Python 3.12.15 | fetched by `uv` into `.tools/local-gen/python` | — |
| ComfyUI | `https://github.com/comfyanonymous/ComfyUI.git` | commit `46493d824fd7eac25a741e505159e4c9e0ef0ebd`, version 0.39.0, committed 2026-10-08 |
| Its Python packages | PyPI, from ComfyUI's `requirements.txt`, by `uv pip install` | torch 2.14.1 with CUDA 13.0, numpy 2.5.3, scipy 1.18.1, transformers 5.19.0, comfy-kitchen 0.2.37, comfy-aimdo 0.5.6 |
| trimesh 5.1.1 | PyPI; LODTailor imports it | — |
| LODTailor (reduce, in Blender) | `github.com/Mstafa-awad/LODTailor-The-Mesh-Trimmer-ComfyuiNode` | `3d25b7d4aa382fa5dac210eb5d8d0eadc4a4f183` |
| Bake Forger (bake, in Blender) | `github.com/Mstafa-awad/LODTailor-Bake-Forger` | `f13589c22558e3ca49dfa87dce709233eb3cc86b` |
| Fast Merge (weld) | `github.com/Mstafa-awad/WTiVo-FastMergeByDistance` | `5392949165ceed1e74448b1949d6e0dc9b34dd92`, with its `build/` folder of Windows binaries and every `__pycache__` removed |
| Memory Cleaner | `github.com/Mstafa-awad/ComfyUI-Memory-Cleaner` | `3357282290278c96ffa0da180d43bc5eac5f2286` |

The four node packs are at the commits the video's installer pins. Each was read before it was loaded: they are plain Python, they start Blender as a separate program, and none reaches the network. They run on Linux.

**The generators need no node pack.** The video note took the generation to rest on VisualBruno's ComfyUI-Trellis2. It does not: every generation node in the video's workflow (`Trellis2ShapeStage`, `VaeDecodeShapeTrellis`, `UnwrapMesh`, `BakeTextureFromVoxel` and the rest) is in ComfyUI itself, in `comfy_extras/nodes_trellis2.py` and `nodes_mesh_postprocess.py`. The video's workflow 2 is ComfyUI's own template `3d_pixal3d_trellis2_image_to_model` with the node packs' steps added.

### Model files

All from Comfy-Org's repackagings on Hugging Face, none gated, downloaded with `curl` at a fixed revision. No account, token or terms were involved. Each file's SHA-256 matched the one Hugging Face lists.

| File | From (`huggingface.co/…`) | Bytes | SHA-256 |
|---|---|---|---|
| `trellis_2_int8_convrot.safetensors` | `Comfy-Org/TRELLIS.2` @ `430a9d0` | 5,253,048,192 | `d01952ad137213f6a868f86b6b877026276f84af5eec23069217475a0bad3a31` |
| `trellis_2_shape_vae_bf16.safetensors` | same | 1,095,844,024 | `de0cb4949a76c59ee5c091a995a69bcc8c51d5aeda939f0c641a50d2a72341f4` |
| `trellis_2_texture_vae_bf16.safetensors` | same | 948,461,364 | `714e5ebf094a610e12a8e3b5175c18a62f37f6ea4218acb6073644456b73ab0e` |
| `dino_v3_vit_l.safetensors` (downloaded, not used) | same | 1,212,559,776 | `5cb785e458de7c460579082418af81f5c62380c181599344bdc60898c63468ee` |
| `dino_v3_L_naf_fp32.safetensors` | `Comfy-Org/Pixal3D` @ `f37641b` | 1,215,214,176 | `4ad2ec4e0879a5b5b04cd97325cc37da954a7b6edca5170b86510f17f2b2290f` |
| `pixal3d_int8_convrot.safetensors` | same | 5,584,555,824 | `4621eac3b715484f79303c7152af641fe0b2b14f4d0e3d394fd6922d00f955ec` |
| `birefnet.safetensors` | `Comfy-Org/BiRefNet` @ `25511f8` | 444,473,596 | `9ab37426bf4de0567af6b5d21b16151357149139362e6e8992021b8ce356a154` |
| `moge_2_vitl_normal_fp16.safetensors` | `Comfy-Org/MoGe` @ `1484985` | 661,859,924 | `cb1a692d03235671e959e81360d7b4d9f44aefadb1f852d6ca6aa17799d5e31f` |

### What was refused, and why

- **The video creator's installer** (`watertightMeshes_win_installer.bat`). Not run: it is a Windows batch file, and it carries encoded content. Its list of pinned commits and model addresses was read as text, and those were followed by hand.
- **WTiVo**, the video's step that closes the mesh. Its repository at the pinned commit `fb9e9ea` holds its working part only as Windows binaries (`cellocut_gpupr_fast.pyd`, `cellocut_vdb_watertight.pyd`, `cppmodules.cp312-win_amd64.pyd`, three `.dll` files and a `.rar`). There is no Linux build and no source for them in the repository. Not installed.
- **Quad Reconstruct**, the video's first cleaning step (commit `74048b3`). It is readable Python, but it needs a library, VisualBruno's fork of CuMesh, that has to be compiled against NVIDIA's CUDA toolkit. This machine has no `nvcc` and no `cmake`. Its `install.py` would otherwise take a prebuilt wheel out of another person's repository. I did not install a compiler toolchain (a system package) and did not install a prebuilt binary I could not match to its source. **If the owner wants this step tested: it needs the `cuda` and `cmake` system packages.**
- **Microsoft's own TRELLIS.2 code.** Not tried. It needs several compiled CUDA extensions and its card says 24 GB. ComfyUI's built-in version is what the video uses and needs neither.

### One thing found too late

The `dino_v3` files come from a model that is **gated at its source**: Meta's `facebook/dinov3-vitl16-pretrain-lvd1689m` asks for a form and manual approval, under the "DINOv3 License". Comfy-Org's copy is not gated and its page is tagged MIT, so the download needed no acceptance and I gave none. I learned of the gate only when reading licences after the runs. The owner may want to read section 8 and decide whether to keep the file.

## 3. Method

### Why ComfyUI, and how it was driven

ComfyUI's built-in route was chosen over Microsoft's repository because it is what the video uses, it is the only route with a claim of running on a small card, and it needs no compiled extension. ComfyUI was started bound to `127.0.0.1:8189`, with no browser. Each run is one request to its HTTP API: [`scripts/make_prompt.py`](local-generator-trial/scripts/make_prompt.py) writes the graph as JSON, taking every node and value of the generation from the video's workflow 2, and [`scripts/run_prompt.py`](local-generator-trial/scripts/run_prompt.py) sends it and listens. ComfyUI was shut down when the runs were done; nothing is left running.

### What was timed and how

- **Time per step** is from ComfyUI's own "now executing node X" messages.
- **Card memory** is `nvidia-smi`, read twice a second: the whole card (desktop included) and the ComfyUI process alone, with Blender when a node starts it. A peak shorter than half a second can be missed.
- **RAM** is the resident memory of ComfyUI and its children, and the machine's least free memory during the run.
- ComfyUI takes as much card memory as is free and moves model parts in and out as it needs ("dynamic VRAM"). **So a peak of 8 GB shows what it used here, not the least it needs.**

### Reference images

The same pictures the Tripo trial prepared, unchanged: [`crate_three_quarter.png`](local-generator-trial/images/crate_three_quarter.png) and [`boulder_1_three_quarter.png`](local-generator-trial/images/boulder_1_three_quarter.png), 2048 × 2048, on white, even light. They are renders of `learn/specimens/crate.glb` and `boulder_1.glb`. [`tripo-api-trial.md`](tripo-api-trial.md) says what is wrong with them as test pictures; the main point is that a clean render is an easy case. Their checksums are in [`images/SHA256SUMS`](local-generator-trial/images/SHA256SUMS) and match the Tripo trial's.

### Settings of the generation

As in the video's workflow 2, for both generators:

| Step | Setting |
|---|---|
| Background removal | BiRefNet, on |
| Crop | 1024 × 1024, margin 1.1 |
| Picture encoder | `dino_v3_L_naf_fp32` |
| Coarse shape | seed 56, 12 steps, guidance 7.5 |
| Shape at 512 | seed 42, 20 steps, guidance 7.5 |
| Shape at full resolution | seed 42, 12 steps, guidance 7.5 |
| Colours | seed 43, 12 steps, guidance 1 |
| Pixal3D only | field of view estimated from the picture by MoGe |

Two differences from the video's file. **The first seed is fixed at 56**, where the video's file has it on "randomize": a fixed seed is the only way to test repeatability. **Resolution is 1024, not 1536**, because 1536 did not fit (section 4).

### The chain, step by step: whose tool ran

| Video's step | Video's tool and setting | What ran here | Whose |
|---|---|---|---|
| 1. Clean the raw mesh | Quad Reconstruct, 1536 | **Left out.** Needs a CUDA build | — |
| 2. Close the mesh | WTiVo, 1536, 12,000,000 points, largest piece | ComfyUI's `RemeshMesh`: grid 512, unsigned distance, inner shell and enclosed pieces dropped | **Substitute** |
| 3. Lighter dense mesh | LODTailor in Blender: voxel remesh at 0.001, reduce to 6,000,000 | LODTailor in Blender: **no voxel remesh, reduce to 1,000,000** | Video's tool, changed settings |
| 4. Unwrap the dense mesh | ComfyUI `UnwrapMesh`, `pec`, 1536, padding 1 | The same | Video's |
| 5. Bake the generator's colours onto it | ComfyUI `BakeTextureFromVoxel`, 4096, checked against the closed mesh | The same at 4096, **checked against the dense mesh**; memory freed first | Video's tool, one input changed |
| 6. Reduce | LODTailor in Blender: voxel remesh at 0.0015, three passes (0.5, 0.25, 0.2), target 30,000 | The same, target **20,000** (the profile) or **4,000** (the video's axe) | Video's |
| 7. Unwrap the reduced mesh, smooth normals | `UnwrapMesh` padding 2; crease angle 180° | The same | Video's |
| 8. Bake dense onto reduced | Bake Forger in Blender: six maps at 4096, 1 sample, graphics card preferred, cage 0.0019 | The same | Video's |
| 9. Weld | Fast Merge, 0.0001, `TEXTURE_SAFE` | The same code. On Linux it runs its slower Python path: its fast path is a Windows `.dll` | Video's |

Blender was the pinned 5.2.2, started through a small wrapper, [`scripts/setup/blender-factory`](local-generator-trial/scripts/setup/blender-factory), that adds what `tools/bl` adds: factory settings, no network, its own empty user folder. LODTailor by itself starts Blender without factory settings. Bake Forger sets Cycles' samples itself (1) and asks for the graphics card; the Blender pitfall of 4,096 samples on the processor does not arise in its script.

### Measuring a model

The Tripo trial's scripts, copied unchanged into [`scripts/`](local-generator-trial/scripts/) (their checksums are in `SHARED_FROM_TRIPO_TRIAL.sha256`): `measure_model.sh` runs `python3 -m kiln.measure`, `learn/assets/glb_inspect.py`, `mesh_defects.py` in the pinned Blender (defects counted on the mesh as imported and again after welding by position), `render_untextured.py` (wireframe pictures) and `target/release/review_pictures` (the eight review pictures, closest view at 0.5 m). The size given was **0.8 m** for every model, that script's default. Neither picture says how big its object is.

Two scripts are mine, because the shared ones cannot read a mesh of 15 million triangles in this machine's memory: [`dense_defects.py`](local-generator-trial/scripts/dense_defects.py) counts the same defects with numpy, and [`compare_dense.py`](local-generator-trial/scripts/compare_dense.py) compares two dense meshes. On the raw crate `dense_defects.py` counts 12,316 boundary edges and no non-manifold edge, and LODTailor's own check of the same file printed `boundary=12,316 nonmanifold=0`.

## 4. Results, stage by stage

### Stage 1: does it install and load?

**Yes.** Nothing in the documented install had to be changed for Linux: clone ComfyUI, install its requirements, put eight files in `models/`. The install took about 25 minutes, nearly all of it downloads. ComfyUI started, found the card ("Total VRAM 9852 MB") and enabled its dynamic memory handling by itself. No low-memory flag was set.

### Stage 2: generation

**At 1536, the video's setting, it does not finish on this card.**

| Attempt | Where it stopped | Time | Peak, ComfyUI process |
|---|---|---|---|
| Crate, 1536, cold | Shape decode: "Allocation on device 0 would exceed allowed memory. Currently allocated: 7.27 GiB. Requested: 1001.00 MiB. Device limit: 9.62 GiB" | 462 s, of which the full-resolution shape sampler took 419 s | 8,416 MiB |
| The same prompt again; only the decode ran, on a card ComfyUI had just emptied | The same error at the same place | 6 s | 8,576 MiB |

A crate that fills its box has about as much surface as an object can have, and the memory of the decode grows with the surface. A thinner object might fit at 1536. That was not tried.

**At 1024 it finishes.** Cold runs, whole card to itself apart from the desktop:

| | Crate, TRELLIS.2 | Boulder, TRELLIS.2 | Crate, Pixal3D |
|---|---|---|---|
| Background, crop, picture encoding | 3 s | 3 s | 18 s (includes MoGe) |
| Coarse shape | 5 s | 5 s | 5 s |
| Shape at 512 | 15 s | 9 s | 8 s |
| Shape at 1024 | 92 s | 60 s | 33 s |
| Shape decode | 4 s | 3 s | 3 s |
| Colours | 49 s | 31 s | 18 s |
| Colour decode | 4 s | 3 s | 2 s |
| **Generation, total** | **175 s** | **115 s** | **88 s** |
| Peak card memory, ComfyUI process | 8,256 MiB | 9,062 MiB | 8,660 MiB |
| Peak card memory, whole card | 9,229 MiB | 9,754 MiB | 9,406 MiB |
| Desktop's share before the run | 1,150 MiB | 1,116 MiB | 1,191 MiB |

Per-step times and peaks for every run are in [`measurements/stages.csv`](local-generator-trial/measurements/stages.csv).

**What the generator returns** (saved straight after the decode, with the colours painted on the vertices):

| | Crate, TRELLIS.2 | Boulder, TRELLIS.2 | Crate, Pixal3D |
|---|---|---|---|
| Format | `.glb`, written by ComfyUI | same | same |
| File size | 358 MB | 274 MB | 206 MB |
| Triangles | 14,916,218 | 11,437,876 | 8,611,542 |
| Vertices | 7,464,611 | 5,717,386 | 4,296,388 |
| Objects, materials | 1, 1 | 1, 1 | 1, 1 |
| Textures, UVs, normals | none, none, none | none | none |
| Colour | one per vertex | same | same |
| Boundary edges (after welding) | 12,316 | 36,648 | 38,304 |
| Non-manifold edges | 0 | 37,842 | 61,375 |
| Separate pieces | 3 | 5 (3 of them under 1% of the triangles) | 1 |
| Degenerate faces | 0 | 0 | 0 |
| Bounding box (x, y, z) | 1.000 × 1.000 × 1.000 | 0.999 × 0.563 × 0.873 | 0.870 × 0.884 × 0.975 |
| Where it sits | centred on the origin, lowest point y = −0.5 | centred, lowest point y = −0.28 | centred, lowest point y = −0.40 |

- **Axes.** The file is glTF, so y is up. The crate and the boulder stand upright. Which way each faces was not worked out: the crate is the same on every side.
- **Size.** The longest side is always about 1 unit. The generator scales every object to fill a unit box. Size is kiln's to set, as the notes already hold.
- **The origin is at the middle of the object,** not at its base. A model placed as delivered would be half sunk in the floor.
- **Welding joins nothing.** The stored and welded vertex counts are the same, so these boundary edges are real rims, not seams.

**Repeatability.** The crate was generated four times with the same seeds, each on a ComfyUI that had been restarted in between (once with part of the card held back, below). **All four meshes are the same to the last bit**: the same 7,464,611 positions and the same 14,916,218 triangles in the same order, and the whole data block of each file has the same SHA-256 (`d93031d9…`). The four files still differ as files, because ComfyUI writes the request into each file's header. Comparisons are in [`measurements/repeat/`](local-generator-trial/measurements/repeat/). This is one object on one machine with one version of the software.

**A probe at the 6 GB claim.** ComfyUI was started with `--reserve-vram 4.0`, which asks it to leave 4 GB of the card alone. The crate generated in 182 seconds, the same mesh, and the process peaked at **6,848 MiB**, at the shape decode. So the flag is a request, not a wall, and this is not a test of a 6 GB card. It shows only that this object's generation at 1024 can be done in under 7 GB.

### Stage 3: the chain

**The chain as published, less the two steps that cannot run, destroys the model.** With Quad Reconstruct and WTiVo left out, the raw crate went straight to LODTailor. Every step reported success and the run took 379 seconds. What came out:

- LODTailor's voxel remesh turned 14,916,218 triangles into 71,954 faces. Blender's voxel remesh needs a closed shape to tell inside from outside; given an open one it kept only thin strips along the edges. [The picture](local-generator-trial/runs/crate_t2_1024_b/lodtailor_dense_on_open_mesh.png) shows a faint outline of a box and nothing else.
- The reduced mesh from that was 18,551 triangles of fragments in 39 pieces, not closed.
- **Fast Merge then welded it away.** Its log shows 73 tries, each with a wider merge distance, from 0.0001 to 0.0073, until the test it calls `geometric_watertight` passed. By then 18,551 triangles had become **10**. Its last line reads "SUCCESS | vertices 20,216->20,216 | faces 18,551->10". The saved file is 38 MB of textures on ten triangles.

So the closing step is not optional, and the video's own tool for it does not exist for Linux.

**Finding a chain that runs took a dozen failed runs.** Each kind is a folder in [`runs/`](local-generator-trial/runs/) with the error.

| What was tried | What happened |
|---|---|
| `RemeshMesh` at 1024, to close the mesh | Out of card memory |
| The same at 768, ComfyUI's template value | Out of card memory |
| The same with memory freed first, and with its input thinned to 3 million vertices | Out of card memory, both times |
| The same at 512 | **Passed**, 6 s. Crate: 6,251,612 triangles, no boundary edge, no non-manifold edge, one piece |
| LODTailor's dense step as the video sets it (voxel 0.001, target 6,000,000) on that | The voxel remesh made 11,951,778 faces, 23,903,556 triangles. Inside ComfyUI Blender then crashed with the machine at 2.2 GB of free RAM. Run by hand, Blender alone reached 19.4 GB and I stopped it at 1.4 GB free |
| `BakeTextureFromVoxel` at 4096 on the 6.25-million-triangle closed mesh | Out of card memory: "Currently allocated: 5.18 GiB. Requested: 4.30 GiB" |
| The same with memory freed first | The same error |
| The same at 2048 | Out of card memory: "Currently allocated: 8.32 GiB. Requested: 7.67 GiB". The node's memory follows the mesh's triangle count, not the texture's size (read in its source) |
| Dense mesh reduced to 1,000,000 first, bake at 4096 against it | **Passed** |

The chain that ran is the right-hand column of the table in section 3. Its changes from the video, each of which changes what is measured: **generator at 1024 not 1536; closing by a different tool at a grid of 512 not 1536; no first cleaning step; dense mesh of 1,000,000 triangles not 6,000,000 and without its voxel remesh; colours baked against that dense mesh, not the closed one.**

**Times of the chain,** from the same cold runs:

| Step | Crate, TRELLIS.2 | Boulder, TRELLIS.2 | Crate, Pixal3D |
|---|---|---|---|
| Close (substitute) | 6 s | 6 s | 4 s |
| Dense reduce, Blender | 54 s | 104 s | 37 s |
| Unwrap dense | 32 s | 3 s | 6 s |
| Bake generator's colours | 13 s | 10 s | 9 s |
| Reduce to 20,000, Blender | 104 s | 23 s | 45 s |
| Unwrap reduced, normals | 1 s | 0 s | 0 s |
| Bake dense onto reduced, Blender | 48 s | 42 s | 56 s |
| Weld | 0 s | 0 s | 0 s |
| Saving and passing files | 6 s | 7 s | 6 s |
| **Chain, total** | **264 s** | **195 s** | **163 s** |
| **Whole run** | **439 s** | **310 s** | **251 s** |
| Peak RAM, ComfyUI and Blender | 15.8 GB | 11.9 GB | 16.1 GB |
| Least free RAM on the machine | 8.6 GB | 12.1 GB | 5.7 GB |

The 4,000-triangle crate took 246 seconds of chain on a mesh already generated; the time does not depend on the target.

**What each step did to the mesh:**

| | Crate, TRELLIS.2 | Boulder, TRELLIS.2 | Crate, Pixal3D |
|---|---|---|---|
| Raw | 14,916,218 triangles; 12,316 boundary edges | 11,437,876; 36,648 boundary, 37,842 non-manifold | 8,611,542; 38,304 boundary, 61,375 non-manifold |
| Closed (substitute) | 6,251,612; 0 and 0; 1 piece | 3,316,512; **2,686 boundary, 155 non-manifold**; 2 pieces | 2,120,244; 0 boundary, **124 non-manifold** |
| Dense | 999,996; 0 and 0 | **43,849**; 320 boundary, 2,513 non-manifold | 993,490; 0 and 0 |
| Reduced, after bake and weld | 19,996; 0 and 0; 1 piece | 20,000; 0 and 0; 1 piece | 20,000; 0 and 0; 1 piece |
| UV islands, dense | 21,433 | 1,830 | 278 |
| UV islands, reduced | 116 | 27 | 99 |

Three things in that table are worth a sentence each.

- **The substitute did not close the boulder.** `RemeshMesh` left 2,686 boundary edges. It is not a watertight guarantee.
- **LODTailor's "seal" shrank the boulder's dense mesh from the 1,000,000 asked for to 43,849.** Its final step welds at a growing distance until the mesh is closed. The boulder's was not, so it kept welding up to its cap. Its own check printed `watertight=False winding_consistent=False bodies=2`. The node did not fail; the run went on with a 44,000-triangle "dense" mesh as the source of the bake. This is the same design as Fast Merge's, stopped by a cap.
- **The reduced mesh is closed in all three cases anyway,** because the reduce step begins with a voxel remesh at 0.0015, which rebuilds the surface. It worked on the boulder's damaged dense mesh; it kept only strips of the raw crate. Whether it works depends on how open its input is.

**Three failures that were not about memory:**

1. **Blender 5.2.2 crashed with a segmentation fault in the Decimate modifier.** It happened in 3 of 13 runs of the reduce step on the same closed crate (10.6 million triangles after the voxel remesh), each time straight after "Triangulate: 10,621,508 faces" and before the first reduction, with 9 to 11 GB of RAM free. The same command run again passed. The backtrace ends in Blender's threading library ([`runs/blender_crash/`](local-generator-trial/runs/blender_crash/)). I then made the wrapper run Blender again after a crash; in the six chain runs after that it was not needed once. The boulder and the Pixal3D crate did not crash, in one run each.
2. **ComfyUI's `UnwrapMesh` failed once** with "IndexError: index 536897894 is out of bounds for axis 0 with size 500000", on a dense crate made by the same steps that it unwrapped without complaint before and after. The dense mesh differs slightly from run to run (21,430, 21,432 and 21,433 islands in three runs), so the input was not identical.
3. **Fast Merge's widening weld,** described above.

### Stage 4: the finished models

| | Crate 20,000 | Crate 4,000 | Boulder 20,000 | Crate, Pixal3D, 20,000 |
|---|---|---|---|---|
| File | `crate_r2_lowpoly.glb` | `crate_c_lowpoly_4k.glb` | `boulder_r1_lowpoly.glb` | `crate_px_lowpoly.glb` |
| File size | 17.8 MB | 16.8 MB | 34.0 MB | 48.5 MB |
| Triangles | 19,996 | 4,000 | 20,000 | 20,000 |
| Vertices stored | 13,956 | 3,352 | 12,639 | 14,654 |
| Vertices after welding | 9,998 | 2,000 | 10,002 | 10,002 |
| Objects, materials | 1, 1 | 1, 1 | 1, 1 | 1, 1 |
| Textures in the file | 4, each 4096 × 4096 PNG | same | same | same |
| Boundary edges as imported | 7,292 | 2,236 | 4,226 | 7,634 |
| Boundary edges after welding | 0 | 0 | 0 | 0 |
| Non-manifold, flipped, degenerate, loose | 0, 0, 0, 0 | 0, 0, 0, 0 | 0, 0, 0, 0 | 0, 0, 0, 0 |
| Pieces | 1 | 1 | 1 | 1 |
| UV islands | 116 | 123 | 27 | 99 |
| Seam edges | 3,245 of 29,994 (10.8%) | 1,243 of 6,000 (20.7%) | 2,603 of 30,000 (8.7%) | 4,562 of 30,000 (15.2%) |
| UV square used | 51.6% | 49.5% | 63.9% | 56.1% |
| Texel density at 0.8 m | 1,070 px/m | 1,050 px/m | 2,811 px/m | 2,291 px/m |
| glTF validator | 0 errors, 0 warnings | same | same | same |

- **The four textures** are base colour, normal, a combined metallic and roughness map, and an emission map. Bake Forger also wrote an ambient occlusion picture, but it is not in the `.glb`. **The emission map is a 4096 × 4096 picture of nothing** (304,633 bytes, the same size in every model): nothing here glows.
- **Open edges as imported are UV seams.** 7,292 on the crate become 0 after welding by position, as the video's fox went from 23,504 to 0, and as the notes found on a boulder.
- **The normal map is the bulk of each file:** 11 MB for the crate, 24 MB for the boulder, 39 MB for the Pixal3D crate.
- **The vertices carry leftovers:** two colour sets and tangents on every vertex, which a game with one textured material does not need.
- Full figures are in [`measurements/`](local-generator-trial/measurements/), one folder per model, and [`measurements/defects.csv`](local-generator-trial/measurements/defects.csv) has every model in one table. SHA-256 of every model is in [`models.sha256`](local-generator-trial/models.sha256); the models themselves are in `models/`, which git ignores.

## 5. What the pictures show

Review pictures (the eight views, from `review_pictures`) and two wireframe pictures of each finished model are under `measurements/<model>/review/` and `measurements/<model>/wire/`. I looked at the three-quarter and closest views and one wireframe. **I am not the shape review.** These are the faults I could see:

**Crate, TRELLIS.2** ([three-quarter](local-generator-trial/measurements/crate_r2_lowpoly/review/three_quarter.png), [closest](local-generator-trial/measurements/crate_r2_lowpoly/review/closest.png), [wireframe](local-generator-trial/measurements/crate_r2_lowpoly/wire/crate_r2_lowpoly_wire_three_quarter.png))

- **Two of the six panels are missing.** The crate is a hollow box with openings on two opposite sides; the closest view looks straight through it. The specimen has a panel on every side. The reference image shows three sides, and those three have their panels.
- **It is hollow, with an inside.** The inner walls are modelled and textured. A real crate model is one solid shape, and those inside faces cost triangles and texture.
- The frame and the set-back panels are there and square. Edges are sharp. Colours are close to the picture, a little redder.
- Thin light scratches run along some frame edges in the texture.
- **The triangles are badly spread.** The wireframe shows dense bands of slivers along every edge and a handful of huge triangles across each flat face. A crate of this shape needs a few hundred triangles; 20,000 are spent on it and 4,000 give nearly the same picture.

**Boulder, TRELLIS.2** ([three-quarter](local-generator-trial/measurements/boulder_r1_lowpoly/review/three_quarter.png), [closest](local-generator-trial/measurements/boulder_r1_lowpoly/review/closest.png))

- The shape is the reference's: a blocky rock with flat facets and paler ridges where they meet.
- **About a dozen small dark specks** sit on the facets, each the shape of a sliver triangle. They are faults of the bake, not of the picture.
- **The bottom edge is ragged,** a row of small teeth where the rock meets the ground.
- The surface is smooth and waxy at 0.5 m. The reference is too; it is a render of a 136-triangle specimen.

**Crate, Pixal3D** ([three-quarter](local-generator-trial/measurements/crate_px_lowpoly/review/three_quarter.png))

- **It is tilted.** The crate stands on one edge, leaning, as the reference image's camera saw it. Its bounding box is 0.870 × 0.884 × 0.975 where the TRELLIS.2 crate's is a cube. This is the fault the video shows on its fox.
- The panels seen are present and the colours are nearer the reference than TRELLIS.2's. The other views were not looked at.

**The crate with nothing closing it** is ten triangles; there is nothing to look at.

## 6. The video's claims on this machine

Each claim is from the video note's section 5. "Not tested" means nothing here bears on it.

| Claim | Standing here | The number |
|---|---|---|
| Raw output has "holes, faces hidden inside the mesh, and millions of polygons" | **Supported** for holes and millions, on three meshes. Inner faces: seen on the crate, not counted | 8.6 to 14.9 million triangles; 12,316 to 38,304 boundary edges |
| The dense result is watertight | **Not tested** as claimed: WTiVo does not run on Linux. With the substitute: closed for the crate, **not** for the boulder | Crate 0 boundary edges; boulder 2,686 |
| No floating faces left inside | **Inconclusive.** One piece after the substitute on the crate, but its inside walls remain, by design of the object | 1 piece |
| The low-poly models "are also usually watertight" | **Supported** on four models, counted after welding; "usually" cannot be judged from four | 0 boundary, 0 non-manifold edges, 1 piece, each |
| It runs on 6 GB | **Inconclusive.** Not testable on a 10 GB card. At 1024, with ComfyUI asked to leave 4 GB free, the generation peaked at 6.8 GB. The chain peaked higher | 6,848 MiB generation; 8,256 MiB with the chain |
| Resolution table: 1536 for "8 GB and up" | **Contradicted** for this object on this card | Out of memory at the shape decode, twice, with 9.62 GiB usable |
| 32 GB of RAM recommended | **Supported,** and not enough for the video's dense setting on a crate | 15.8 GB peak on the chain that ran; 19.4 GB and rising in Blender alone at the video's setting |
| "It will also work with Linux, but the installation you would need probably to do by hand" | **Contradicted** for the workflow as published; **supported** for the generators and for three of the five node packs used | WTiVo: Windows binaries only. Quad Reconstruct: needs a CUDA build. Generation, LODTailor, Bake Forger, Fast Merge: ran |
| "Game-ready, low-poly version with baked textures" | The files are produced. **Game-ready is contradicted by the pictures** for both crates | Two panels missing; one model tilted |
| A 4,000-face prop | **Supported:** the chain reaches the count | 4,000 triangles, 0 open edges after welding |
| Runs take 360 to 570 s on an RTX 5080 at 1536 | **Not comparable.** Here at 1024 on an RTX 3080 | 251 to 439 s |
| Texturing "worked never that great" | **Inconclusive.** Plain-coloured objects; specks on the boulder | — |
| Baked low-poly and dense model hard to tell apart | **Not tested.** No side-by-side was made | — |
| Pixal3D follows the picture more closely; TRELLIS.2 does the back better | **Inconclusive,** one object. Pixal3D's colours were closer; TRELLIS.2's unseen sides lost their panels. Pixal3D's unseen sides were not looked at | — |
| Pixal3D's odd facing is due to the camera; the fix is TRELLIS.2 | **Supported** on one object | Pixal3D crate tilted; TRELLIS.2 crate square to the axes |
| Add-ons break headless Blender | **Not tested.** Blender ran with factory settings throughout | — |
| A fault is fixed by running again with another seed | **Not tested.** Seeds were fixed on purpose | — |
| As shipped, a run is not repeatable (the video note's inference) | **Supported in part.** With the seed fixed the generator repeats exactly. The chain does not | Four identical meshes; three different island counts on the dense mesh |
| Voxel size for hard surfaces (0.05, 0.005 or 0.0015) | **Not tested** beyond 0.0015, the value the video used | — |
| The 2K figures | **Not tested.** 1536 already fails | — |

## 7. Checks against `profiles/pit.toml`

The profile is provisional and holds two numbers.

| Field | Value | Result |
|---|---|---|
| `triangle_budget` | 20,000 | **Pass:** 19,996, 20,000 and 20,000 triangles; 4,000 for the fourth. The target was set to the budget, so this shows the chain hits a count, nothing more. LODTailor allows itself 5% over a target; here it did not use it |
| `closest_viewing_distance` | 0.5 m | The closest review picture was taken at 0.5 m for each model. Faults at that distance are in section 5 |

What the profile does not hold yet but [`pit-budget-measurement.md`](pit-budget-measurement.md) reasons about, for when issue #11 fills it in:

- **Textures.** That note's section 6 puts three 4096 × 4096 textures at 256 MiB of card memory uncompressed (64 MiB block-compressed) and marks 2048 as its working size, at a quarter of that. These models carry four such maps each, at 1,050 to 2,811 pixels per metre for a 0.8 m object. The texture size is one number in the chain; this is a setting to turn down, not a fault of the method. Whether a smaller map still looks right at 0.5 m was not tried.
- **Wasted texture.** 36 to 50% of each UV square is empty, and one of the four maps is blank.
- **Size and origin.** Every model is 1 unit long and centred on the origin. Kiln's scale stage already sets size; nothing yet moves the origin to the base.

## 8. Licences

The mission's rule: a generator is usable only if its licence gives commercial rights without attribution. For each piece **used in these runs**. Texts are saved in [`licences/`](local-generator-trial/licences/). I am not a lawyer and this is a reading, not advice.

| Piece | Licence, and where it says so | Commercial use of outputs, no attribution? |
|---|---|---|
| TRELLIS.2 weights | MIT. [Microsoft's card](https://huggingface.co/microsoft/TRELLIS.2-4B): "This model is released under the MIT License." Comfy-Org's repackaging is tagged `license: mit` | **Yes.** MIT asks that its notice travel with copies of the software, not with what the software makes |
| Pixal3D weights | MIT, by [Tencent ARC's `LICENSE`](https://huggingface.co/TencentARC/Pixal3D). Its `NOTICE`: third-party parts "remain licensed under their respective original terms". The card carries `extra_gated_eu_disallowed: true` but the repository is not gated (`gated: false` from Hugging Face's API today) | **Yes** for the weights. The EU flag's meaning was not established |
| **DINOv3** picture encoder (`dino_v3_L_naf_fp32`), used by **both** generators here | **Not MIT.** Meta's ["DINOv3 License"](https://github.com/facebookresearch/dinov3/blob/main/LICENSE.md), last updated 2025-08-19. Comfy-Org's page is tagged MIT and says nothing of this file's origin. Meta's own repository is gated (`gated: manual`) | **Unclear.** See below |
| The "naf" part of that file | Not identified. ComfyUI's source calls it "bundled NAF weights". No licence found | **Unclear** |
| BiRefNet background removal | MIT, by [its card](https://huggingface.co/ZhengPeng7/BiRefNet) | **Yes.** It only cuts the picture out. The licences of the pictures it was trained on were not read |
| MoGe (Pixal3D only) | MIT, Microsoft: the `LICENSE` in Comfy-Org's repository and [the model's record](https://huggingface.co/Ruicheng/moge-2-vitl-normal) | **Yes** |
| ComfyUI | GPL-3.0 | **Yes.** A licence on a program does not reach what the program outputs. It would matter only if kiln shipped ComfyUI's code |
| LODTailor, Bake Forger | GPL-3.0 | **Yes,** the same way. As the video note says: reading how they work is free, copying their code into kiln brings the GPL with it |
| Fast Merge | MIT | **Yes** |
| Blender | GPL; its outputs belong to the user (carried from the notes) | **Yes** |
| PyTorch, numpy, scipy, trimesh, comfy-kitchen and ComfyUI's other Python packages | Permissive where I looked (BSD for the first three, MIT for trimesh, Apache-2.0 for comfy-kitchen). Not read one by one; comfy-aimdo's was not read | **Yes** for those read; they are tools, and none is a model |

**The Nvidia question from the older note does not arise on this route.** [`3d-asset-pipeline-tools.md`](3d-asset-pipeline-tools.md) flags `nvdiffrast` and `nvdiffrec`, which Microsoft's TRELLIS code depends on and whose licence is for research and evaluation only. ComfyUI's version does not use them: no file in `comfy/` or `comfy_extras/` names them, and neither is installed in the environment. ComfyUI has its own code for those jobs.

**The DINOv3 question replaces it.** What the licence says:

- It grants "a non-exclusive, worldwide, non-transferable and royalty-free limited license ... to use, reproduce, distribute, copy, create derivative works of, and make modifications to the DINO Materials."
- It does not restrict commercial use in words. It has no attribution duty for products; the one acknowledgment duty is for research publications.
- It forbids use for "military or warfare purposes, nuclear industries or applications, espionage", and requires anyone passing the model on to do so under the same agreement and with a copy of it.
- It says nothing about who owns outputs. It mentions outputs twice, to disclaim warranty on them and to end the licence of anyone who sues Meta over them.
- "By clicking 'I Accept' below or by using or distributing any portion or element of the DINO Materials, you agree to be bound by this Agreement."

So: a game asset made with it is probably not barred, but the encoder is not under the MIT label on the page it was downloaded from, its use binds the user to Meta's agreement, and Meta gates it at the source where Comfy-Org does not. Pixal3D's own `NOTICE` lists **DINOv2** (Apache-2.0), not DINOv3, so ComfyUI's packaging differs from what Tencent ARC describes. Microsoft's card does not name its encoder; I did not read Microsoft's code to see which it uses.

**Verdict.** The weights of both generators permit commercial use of outputs without attribution. **The route as a whole is unclear, not cleared,** on one file. It is a narrower and more readable question than the Nvidia one, and it might be settled by reading one licence with care or by finding that an Apache-licensed encoder can be used in its place. Neither was done.

## 9. Against the Tripo trial

[`tripo-api-trial.md`](tripo-api-trial.md) was prepared the same day and **generated nothing**: the API key has no credits. So there is no Tripo model to compare with.

What is ready for the day it runs:

- **The same pictures.** This trial's two reference images are that trial's files, byte for byte.
- **The same scripts.** Every finished model here was measured by that trial's `measure_model.sh`, with the same size (0.8 m) and the same closest distance (0.5 m). Its numbers will sit in the same files under the same names.
- **The rows to put side by side:** the raw output table in section 4 (triangles, file size, textures, UVs, boundary and non-manifold edges, pieces, bounding box, where the origin is), the finished-model table, and the faults in section 5. For the crate the questions are already sharp: does Tripo give all six panels, a solid box or a hollow one, and is it square to the axes?
- **What will not compare directly.** Tripo can be asked for 20,000 faces and textures in one request; here the raw output is 15 million triangles with no UVs, and a 264-second chain of other people's tools sits between it and anything usable. Time and cost per kept asset would have to include that chain on this side, and the retries on both.

A folder `local-generator-trial/claude-opus-5-5/` appeared in this trial's directory while it ran. It is another agent's work and not part of this note; I did not open or change it.

## 10. What this would mean for kiln

**Everything in this section is inference.**

1. **A local generator is possible on the owner's machine, at 1024.** That was unknown this morning. It costs nothing per try and about two to three minutes of the graphics card. It is a real candidate for a generator trial, behind the licence question.
2. **Its raw output is far from a model file kiln can take in.** 15 million triangles, no UVs, colours on vertices, open. `kiln run --model` would keep a 358 MB file as the raw output and every stage after it would have to work at that scale. Tripo's raw output, by its documentation, is already reduced and textured. With a local generator, kiln would own the close, reduce, unwrap and bake stages; with Tripo it may own only a scale and a check.
3. **The video's stage order holds up, but its tools are not a foundation.** Close, reduce, unwrap, bake, weld produced four clean meshes. The tools did it with two crashes of three kinds, one silent destruction of a model, a "seal" that quietly shrank a mesh to 4% of its target, and settings that have to change with the object's surface area. They are three to four weeks old and by one author.
4. **"Weld until it is closed" is a rule kiln should never copy.** Two of the video's tools widen a merge distance until a watertight test passes. A mesh of ten triangles passes. A repair step needs a limit on how much it may change and a check after it on what is left: triangle count, bounding box, area. Kiln's checks-after-build are the right shape for this.
5. **Blender's Decimate on ten million triangles is not dependable in 5.2.2.** Three crashes in thirteen runs on one mesh. A kiln stage that reduces a dense mesh in the pinned Blender should expect a crash, run again, and record that it did. Or reduce in steps that keep each mesh smaller.
6. **The shape review would have rejected both crates,** on the faults in section 5, and nothing in the chain would have saved them. That matches the video note: the remedy is another seed or another picture. A crate seen from one corner has three unseen sides, and this generator did not invent panels for two of them. A second reference image from behind, or a generator that takes several views (ComfyUI ships a multi-view Pixal3D file, not tried), is the obvious thing to test.
7. **Twenty thousand triangles is the wrong target for a crate, and the chain cannot know that.** Automatic reduction spent them on slivers along the edges. The budget is a ceiling; what a shape needs is a judgement the profile does not hold.
8. **The asset record would need the whole recipe.** Generator, resolution, four seeds, the closing tool and its grid, both reduce targets, voxel size, texture size, cage distance, the versions of ComfyUI and each node pack, and how many tries the Blender steps took. With those and a kept raw output, the generation need never be repeated; the chain can be, but will not give the same bytes.

## 11. What is unknown, and the next step

**Unknown**

- Whether any thinner object fits at 1536 on this card.
- What a 6 GB or 8 GB card does. Only a card of that size can say.
- Whether WTiVo or Quad Reconstruct would give a better closed mesh than the substitute. Neither ran.
- How often either generator gives a sound shape. Two objects, one seed each.
- Whether the Blender crash is in 5.2.2 only, and what triggers it. It was not reported upstream.
- Whether the missing panels come from the generator at 1024, from the picture, or from the seed.
- What the DINOv3 licence means for a sold game, and whether another encoder can stand in.
- How these results compare with Tripo's on the same pictures.

**The next step,** if the owner wants to go on with this route: settle the DINOv3 question first, since it decides whether the rest is worth doing. Then the cheapest informative run is the crate again with two changes, one at a time: another seed, and a second picture from the opposite corner. Each is three minutes.

## 12. How to run it again, and how to remove it

All paths are from the repo root. The setup scripts are copied in [`scripts/setup/`](local-generator-trial/scripts/setup/); they hold absolute paths to this checkout.

**Install** (about 25 minutes, 29 GB):

```
mkdir -p .tools/local-gen/src && cd .tools/local-gen
cp ../../learn/research/local-generator-trial/scripts/setup/* . && . ./env.sh
git clone https://github.com/comfyanonymous/ComfyUI.git src/ComfyUI
git -C src/ComfyUI checkout 46493d824fd7eac25a741e505159e4c9e0ef0ebd
uv venv --python 3.12 venv
uv pip install --python venv/bin/python -r src/ComfyUI/requirements.txt trimesh
./dl.sh                      # the eight model files, 16.4 GB
```

Then clone the four node packs of section 2 at their commits into `src/ComfyUI/custom_nodes/`, and delete `build/` and every `__pycache__` from them.

**Run** (from `learn/research/local-generator-trial/`):

```
../../../.tools/local-gen/start_comfy.sh > comfy.log 2>&1 &     # 127.0.0.1:8189 only
cp images/*.png ../../../.tools/local-gen/input/
scripts/run_chain.sh crate_r2   crate_three_quarter.png     trellis2 20000
scripts/run_chain.sh boulder_r1 boulder_1_three_quarter.png trellis2 20000
scripts/run_chain.sh crate_px   crate_three_quarter.png     pixal3d  20000
scripts/measure_model.sh crate_r2_lowpoly models/crate_r2_lowpoly.glb 0.8
pkill -f "[m]ain.py --listen 127.0.0.1 --port 8189"            # stop ComfyUI
```

`run_chain.sh` tries up to three times and copies the results into `models/` and `runs/`. Generation only, with no chain: `python3 scripts/make_prompt.py out.json --image crate_three_quarter.png --name x --resolution 1024`, then `venv/bin/python scripts/run_prompt.py out.json runs/x`. Every request that was sent is kept as `runs/*.prompt.json`; `crate_t2_1024_video20k.prompt.json` is the chain with nothing closing the mesh, and `crate_t2_1536_raw.prompt.json` the run that does not fit.

**Disk.** `.tools/local-gen/` holds 29 GB: 16.4 GB of model files, 6.7 GB of Python environment, 6.6 GB of `uv` download cache (safe to delete alone: `rm -rf .tools/local-gen/cache`), 113 MB of Python. The results folder holds 1.5 GB of models, which git ignores, and about 56 MB of measurements, pictures and logs.

**Remove everything:**

```
rm -rf .tools/local-gen
rm -rf learn/research/local-generator-trial/models      # or the whole folder
```

Nothing was installed anywhere else. One thing outside those folders is not mine to delete: **two core dumps of the pinned Blender, 3.3 GB and 1.2 GB, are in the system's crash store** (`coredumpctl list` shows them at 13:19 and 13:29). They were written by the first two crashes, before I set the wrapper to leave none. They are owned by the system and will expire by its own rules, or the owner can clear them.

## Corrections to earlier notes

Listed here, not made there.

- [`video-local-trellis2-pixal3d-watertight-low-poly.md`](video-local-trellis2-pixal3d-watertight-low-poly.md), section 1 and the README it quotes: the generation does not rest on VisualBruno's ComfyUI-Trellis2. The generation nodes are ComfyUI's own. That pack is needed only for the CuMesh library behind Quad Reconstruct.
- The same note, section 6: the file `dino_v3_L_naf_fp32.safetensors`, whose licence it left unread, is Meta's DINOv3 under the DINOv3 License, and it is used by TRELLIS.2 as well as Pixal3D in this workflow.
- The same note, "What could not be verified": ComfyUI's version of TRELLIS.2 does **not** depend on the Nvidia libraries the older note flags.
- The same note, section 7, "Open generators run on Linux only … the ComfyUI route reverses the platform question": the generators run on Linux through ComfyUI. It is two of the video's node packs that are Windows-only.
- [`3d-asset-pipeline-tools.md`](3d-asset-pipeline-tools.md), the TRELLIS.2 row, "Nvidia GPU with 24 GB; Linux only": true of Microsoft's code by its card. Through ComfyUI with quantised weights it generated at 1024 on a 10 GB card.
- The same note, "UVs by xatlas" and "MIT, with the Nvidia dependencies above" for TRELLIS.2: neither holds on the ComfyUI route, which has its own unwrapper and does not use those libraries. It has the DINOv3 question in their place.

## What could not be done or verified

- **The video's chain as published.** WTiVo and Quad Reconstruct did not run. Every result after the raw output rests on a substitute for the step the video is named after.
- **Resolution 1536, and the 2K workflow.**
- **The 6 GB claim.** No such card.
- **Docker isolation.** No GPU runtime is set up, so the stack ran in a `uv` environment as the owner's user, with third-party Python code. The node packs were read first; ComfyUI and its 100-odd Python packages were not.
- **Fast Merge's fast path,** a Windows `.dll`. Its widening weld is in the Python that did run, so the fault is not the fallback's alone, but the native path was not seen.
- **A second seed, a second picture, a third object.** The axe in the video was not reproduced; its picture is not published.
- **Which way the models face.**
- **A side-by-side of dense and reduced models,** and any look at the dense textured models at all.
- **The other six review pictures** of each model, and all pictures of the 4,000-triangle crate, were made but not looked at.
- **A run through `kiln run`** with a temporary store. The models were measured with kiln's measurement and never taken in.
- **The texture maps one by one.** Only what the review pictures show.
- **Whether ComfyUI contacted any host while running.** It was started with `--disable-api-nodes` (which this version treats as `--offline`) and with Hugging Face's offline switches set; its traffic was not watched.
- **Licences of training data** for any model, and the licence of the "naf" weights.

## Sources

Read 2026-10-08.

- ComfyUI at commit `46493d8`: `comfy_extras/nodes_trellis2.py`, `nodes_mesh_postprocess.py`, `nodes_save_3d.py`, `requirements.txt`, `LICENSE`, and the template `3d_pixal3d_trellis2_image_to_model.json` in the `comfyui-workflow-templates` package.
- The six node packs named in section 2 at their pinned commits: file lists, licences, and the Python of LODTailor (`decimate_only.py` in full), Bake Forger, Fast Merge, Memory Cleaner and Quad Reconstruct (`install.py`).
- The video's workflow 2 and installer, as text, from the files the video note's research saved.
- Hugging Face: the cards and API records of `Comfy-Org/TRELLIS.2`, `Comfy-Org/Pixal3D`, `Comfy-Org/MoGe`, `Comfy-Org/BiRefNet`, `microsoft/TRELLIS.2-4B`, `TencentARC/Pixal3D` (with `LICENSE` and `NOTICE`), `ZhengPeng7/BiRefNet`, `Ruicheng/moge-2-vitl-normal`, and the API record of `facebook/dinov3-vitl16-pretrain-lvd1689m`.
- [The DINOv3 License](https://github.com/facebookresearch/dinov3/blob/main/LICENSE.md).
- This repo: `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, `profiles/pit.toml`, the notes named above, and the Tripo trial's scripts and images.

No text addressed to an AI agent was found in any file read.

## Method

The work was done on 2026-10-08 between about 12:30 and 15:00. The install went into `.tools/local-gen/` with `uv`; model files came by `curl` from fixed revisions and were checksummed. Node packs were cloned to a side folder, read, and only then copied into ComfyUI without their binaries. ComfyUI ran on `127.0.0.1` and was driven by two scripts over its HTTP API; the server's logs are in `runs/comfy-server-*.log`. Twenty-three requests were sent in all: nine finished and fourteen stopped with an error. Twelve of the fourteen are kept with their error; two repeats of one failure were overwritten. Where a step failed, the next attempt changed one thing, and the table in section 4 lists them in order. Blender steps that failed inside ComfyUI were run again by hand to read their logs. Models were measured with the Tripo trial's scripts and two of my own, and the pictures were looked at once.

Only this file and the folder `local-generator-trial/` were written in the repo. No other note was edited, nothing was put in `assets/`, `kiln run` was not used, and nothing was committed.
