# GPU acceleration for the build-and-check loop

Research date: 2026-10-05. Audience: the owner. Question as asked: "could we use CUDA or GPU acceleration to speed this up", where "this" is `tools/gate.sh` and `tests/run.sh`, run by several agents at once.

## Answer

**Yes, for exactly one step: the texture bake in `tools/paint.py`.** It is the only step that runs on the CPU and could run on the GPU, and it is the largest consumer of CPU in the loop: about 75 to 92 core-seconds per asset on the CPU against about 1 to 2 seconds on the RTX 3080 with CUDA (measured, both assets). Everything else that draws a picture (the EEVEE review tiles, the Bevy screenshots) is on the GPU already, and the rest is single-threaded Python that no GPU setting touches.

**It comes with two costs that must be handled before switching.** A GPU bake is not byte-identical from run to run (5 to 9 texels in a million differ by one level out of 255), where the CPU bake is; and eight bakes started at once ran the card out of memory, after which five of them exited 0 with a wrong texture. So: one bake on the card at a time, behind a machine-wide lock, and a decision about whether committed `.glb` files may differ by a few texels between rebuilds.

**For a tree the GPU is not the main lever.** Its slowest step is the mesh checks (L1), 44 core-seconds of Python, most of it in two lines of `tools/foliage.py`; see [section 5](#5-what-else-the-measurements-show).

**How to read the evidence labels**

- **[measured]**: I ran it on this machine on 2026-10-05 and the number is from that run. The machine was busy with other agents throughout (load average 15 to 48 on 16 threads), so wall-clock times are inflated and vary; CPU seconds (user + system) are steadier and are given where they matter.
- **[raw]**: I read the text myself: a page of Blender's manual or release notes pulled with `curl`, a file of Blender's source at tag `v5.2.2`, or a file in this repo.
- **[summarised fetch]**: a page read through a tool that summarises it.
- **[inference]**: my reasoning. Nothing was run.
- **not verified**: collected in [section 7](#7-not-verified).

Nothing tracked was changed. The gate was run on `slab_1` and `tree_1` several times and rewrote their outputs byte for byte (`git status` stayed clean after each run). The timing scripts are in `target/scratch/gpu/`, which git ignores; their outputs (textures, `.blend` files) were deleted afterwards.

---

## 1. The machine

- GPU: NVIDIA GeForce RTX 3080, 10,240 MiB, driver 610.57.04, compute mode Default. The desktop (Hyprland and others) already holds 0.8 to 1.5 GB of it. `nvidia-smi` **[measured]**
- CPU: AMD Ryzen 7 5800X, 8 cores, 16 threads. **[measured]** (Blender's device list, `nproc`)
- Blender 5.2.2 LTS in `.tools/blender`, run through `tools/bl` (`--background --factory-startup`), lists the card as both a CUDA and an OptiX device. **[measured]** (`target/scratch/gpu/devices.py`)
- Blender's requirements: CUDA "requires a NVIDIA graphics cards with compute capability 5.0 and higher"; OptiX the same "and a driver version of at least 575". This card and driver meet both. <https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html> **[raw]**

---

## 2. Where the time goes

### One gate, step by step

Wall-clock seconds, each step run by hand with the gate's own command (`target/scratch/gpu/time_gate.sh`). The range is over 4 runs of `slab_1` and 3 of `tree_1`, at load averages of 16 to 31 (slab) and 25 to 42 (tree). **[measured]**

| Step of `tools/gate.sh` | `slab_1` (s) | `tree_1` (s) | What it is |
|---|---|---|---|
| L0 spec lint | 0.04 to 0.3 | 0.06 to 0.1 | Python |
| **build** | **9.3 to 20.6** | **25 to 42** | Blender: generator, unwrap, **bake**, save (broken down below) |
| **L1 mesh checks** | 1.0 to 2.8 | **72 to 100** | Blender: single-threaded Python and bmesh |
| export | 0.6 to 2.1 | 1.7 to 2.8 | Blender: the glTF exporter (Python) |
| L2 glTF validator | 0.01 to 0.03 | 0.04 | native binary |
| L2b Bevy profile lint | 0.02 to 0.04 | 0.05 to 0.08 | Python |
| L4 Bevy load test | 0.5 to 1.3 | 3.4 to 9.2 | Rust, no renderer: CPU (2.3 CPU-s on the tree) |
| L4b Bevy screenshots | 3.3 to 8.4 (2 shots) | 13 to 17 (4 shots) | Rust: GPU already; 1.4 s each at best, nearly all start-up |
| L4c bark view | none | 2.3 to 4.3 | Blender: Python |
| L5 review renders | 3.2 to 11.5 | 7.3 to 15.6 | Blender: EEVEE on the GPU already, then ImageMagick |
| L5c, L5b image lint and baseline | 0.1 to 0.5 | 0.25 to 0.4 | Python |
| **Whole gate** | **26 to 44** | **140 to 175** | |

### Inside the build

One run of `tools/build.py`'s steps with a stopwatch round each part (`target/scratch/gpu/build_timed.py`, which calls `paint.apply` unchanged and saves under `target/scratch/`). "wall / CPU" in seconds; CPU is user + system summed over all threads. **[measured]**

| Part | `slab_1` wall / CPU | `tree_1` wall / CPU | Kind of work |
|---|---|---|---|
| Blender start to script (and exit) | about 0.5 | about 0.5 | process start-up |
| Generator (`source/<family>/...`) | 0.3 to 1.3 / 0.6 | 9.5 to 40 / 10 to 16 | single-threaded Python and bmesh |
| Unwrap and pack (`paint.unwrap`) | under 0.01 | 1.1 to 4.5 / 1.3 to 1.8 | Blender operators, CPU |
| **Bake, CPU, 16 threads** | **12 to 19 / 83 to 92** | **15 / 77 to 78** | Cycles |
| **Bake, CUDA** | **1.5 to 2.9 / 0.9 to 1.4** | **1.1 to 1.3 / 0.6 to 0.8** | Cycles on the GPU |
| Bake, OptiX (after its first run) | 1.8 to 2.0 / 1.1 to 1.4 | 0.5 to 1.1 / 0.8 to 1.1 | Cycles on the GPU |
| Leaf palette (`paint.leaf_colours`) | none | 1.4 to 7.2 / 1.4 to 2.5 | Python |
| Save `.blend` | 0.01 | 0.02 | disk |

The CPU bake by thread count, `slab_1`, same texture every time: 1 thread 90.8 s, 4 threads 18.7 s, 8 threads 12.2 s, 16 threads 12 to 19 s. **[measured]** The work is about 75 to 90 core-seconds however it is spread. `tests/run.sh` gives each Blender one thread when it runs one case per core (`tests/run.sh` line 223), which is the "minute of one core each" its header mentions.

### Inside the review renders

`tools/review_render.py` with a stopwatch on each render (`target/scratch/gpu/review_timed.py`), 3.0 to 3.8 s in all: 12 EEVEE renders take 1.8 to 2.2 s together (0.7 to 0.9 s for the first, which compiles shaders, then about 0.1 s each), and the ImageMagick montage 1.3 to 1.6 s. **[measured]**

### Start-up

- Blender, started and stopped with an empty script: 0.47 to 0.52 s, five runs. A gate starts it 4 times (5 for a tree). **[measured]**
- `asset_view --screenshot`: 1.41 to 1.44 s run directly, 1.61 to 1.64 s through `cargo run -q`; `cargo run` itself costs about 0.2 s each time. **[measured]**

---

## 3. What a GPU can and cannot speed up

### The bake: yes

- **It runs on the CPU today, by choice.** `tools/paint.py` line 557 sets the engine to Cycles and line 558 sets `scene.cycles.device = "CPU"`; the module's docstring gives the reason: "Cycles runs on the CPU with a fixed seed, so a rebuild gives the same texels". **[raw]**
- **Cycles supports CUDA and OptiX on this card.** Manual, as in section 1. **[raw]**
- **Baking on the GPU works in `--background --factory-startup`.** I baked both assets on CUDA and on OptiX through `tools/bl`. **[measured]** The manual documents GPU rendering from the command line as well: "`--cycles-device <device>` Set the device used for rendering. Valid options are: CPU CUDA OPTIX HIP ONEAPI METAL", with the example `blender -b file.blend -f 20 -- --cycles-device OPTIX`. <https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html> **[raw]**
- **How it is switched on from Python.** `--factory-startup` leaves the compute device type at none, so the script must set it every run. This is what the experiment ran, just before the bake: **[measured]**

  ```python
  prefs = bpy.context.preferences.addons["cycles"].preferences
  prefs.compute_device_type = "CUDA"
  prefs.refresh_devices()
  for d in prefs.devices:
      d.use = d.type == "CUDA"
  scene.cycles.device = "GPU"
  ```

  `compute_device_type` ("Device to use for computation (rendering with Cycles)") and `refresh_devices` are in `intern/cycles/blender/addon/properties.py` lines 1656 to 1661 and 1766 to 1773 at tag `v5.2.2`. <https://github.com/blender/blender/blob/v5.2.2/intern/cycles/blender/addon/properties.py> **[raw]**
- **CUDA needs no compile step; OptiX does, once.** "Normally users do not need to install the CUDA toolkit as Blender comes with precompiled kernels" (manual, GPU rendering page **[raw]**); the first CUDA bake took 1.95 s. The first OptiX bake took **238 s** (141 CPU-s) while it built its kernels, and 2 s after that; the result is cached in `/var/tmp/OptixCache_<user>/optix7cache.db`, which every working copy of this user shares. **[measured]**
- **Gain.** Bake wall time 12 to 19 s to about 2 s (slab), 15 s to about 1.2 s (tree): roughly **8 to 12 times** on an otherwise idle 16 threads. In CPU work, 77 to 92 core-seconds to about 1: that is what lowers the load average when four agents build at once. Four CPU bakes at once took 30 to 31 s each (load 48); four CUDA bakes at once took 3.0 to 3.2 s each. **[measured]**

### The review renders: already on the GPU

- `tools/review_render.py` line 42 sets `BLENDER_EEVEE`. **[raw]** Under `tools/bl` Blender reported its graphics backend as `OPENGL`, renderer `NVIDIA GeForce RTX 3080/PCIe/SSE2`, version `4.6.0 NVIDIA 610.57.04`. **[measured]**
- EEVEE has rendered without a display on Linux since Blender 3.4: "Headless rendering is now supported under Linux". <https://developer.blender.org/docs/release_notes/3.4/eevee/> **[raw]** It works here: every gate run produced its tiles. **[measured]**
- Nothing to gain: 0.1 s a tile. `--gpu-backend` can force `vulkan` or `opengl` (manual, command-line arguments **[raw]**); I did not try Vulkan.

### The Bevy viewer and load test

- `asset_view --screenshot` renders on the GPU already: its log names the adapter as `NVIDIA GeForce RTX 3080`, `DiscreteGpu`, `backend: Vulkan` (`source/tree_1/out/reports/L4b-bevy-view.log`). **[measured]** It adds Bevy's `DefaultPlugins` with no window and the winit plugin off (`crates/asset_view/src/main.rs` lines 158 to 171). **[raw]** Bevy picks the adapter itself: "Backends::DX12, Backends::METAL, and Backends::VULKAN are enabled by default for non-web and the best choice is automatically selected." <https://docs.rs/bevy/0.19.1/bevy/render/settings/struct.WgpuSettings.html> **[summarised fetch]**
- `asset_smoke` has no renderer at all: "The plugin set bevy_gltf's own tests use: no window, no renderer" (`crates/asset_smoke/src/main.rs` line 186). **[raw]** Its checks are CPU arithmetic on the mesh and the texture, 2.3 CPU-s for the tree. **[measured]** A GPU would not help it.
- Eight `asset_view` screenshots started at once finished in 3.96 s, raised the card's memory in use by about 3.75 GB (about 0.47 GB each), and wrote eight identical files, identical to the one the gate wrote. **[measured]**

### Generators, bmesh, unwrap, export, checks: no

- They are Python and Blender's mesh code on one CPU thread; the CPU columns above equal the wall times at low load, which is what one thread looks like. **[measured]**
- Blender's only GPU compute setting is the one above, and its own description limits it to "rendering with Cycles" (`properties.py` line 1658 **[raw]**). The manual's GPU page describes GPU use "for rendering, instead of the CPU" and nothing else. **[raw]**
- The glTF exporter is a bundled Python add-on: `.tools/blender/5.2/scripts/addons_core/io_scene_gltf2/`. **[raw]** (the folder is there; I did not read it for GPU calls)
- They are also small, except on a tree: unwrap 1.3 to 1.8 CPU-s, export under 3 s for the whole process.

---

## 4. Sharing one card between four agents

### Memory

- **One bake takes far more memory than the scene needs.** Peak memory in use on the card rose by about 2.7 GB during one CUDA bake of `slab_1` (two objects, 400 triangles, one 1024 px texture), about 2.3 GB for `tree_1`, about 1.8 GB for OptiX. **[measured]** (sampled every 0.1 to 0.2 s with `nvidia-smi`; the desktop's own use moved by a few hundred MB between samples, so these are rough)
- **Why.** Cycles sizes its working state by the card, not by the scene: `num_states = max(max_num_threads, 65536) * 16`, at least a million path states. `intern/cycles/device/cuda/queue.cpp` lines 30 to 34 at `v5.2.2`. <https://github.com/blender/blender/blob/v5.2.2/intern/cycles/device/cuda/queue.cpp> **[raw]** The same function reads an environment variable, `CYCLES_CONCURRENT_STATES_FACTOR`, that scales it (lines 36 to 41). **[raw]** With the factor at 0.25 the rise was about 1.2 GB, the bake no slower, and the texture within one level of the default's in 8 texels. **[measured]**
- **Four at once fitted; eight did not.** Four CUDA bakes of `slab_1` together peaked at 7.7 GB in use and all four were right. Eight together peaked at 9.8 GB: **two failed** with `Failed to retain CUDA context (Out of memory)` and a Python exception, and **five logged `System is out of GPU memory` or `Out of memory in CUDA queue enqueue`, returned `{'FINISHED'}` from `bpy.ops.object.bake`, exited 0, and wrote a texture in which 216,000 to 340,000 of 1,048,576 texels were wrong by 67 to 139 levels**. One of the eight was right. **[measured]**
- That is the dangerous case: `paint.py` checks the operator's return value (line 629) and it says finished. The operator reports cancelled only when `RE_bake_engine` returns false (`source/blender/editors/object/object_bake_api.cc` lines 1792 to 1805 at `v5.2.2` **[raw]**); in these runs it evidently did not. The manual says that with CUDA and OptiX "if the GPU memory is full Blender will automatically try to use system memory" (GPU rendering page **[raw]**); that did not save these runs.
- Eight builds queued behind one `flock` on a lock file finished in 33 s in all, every texture right. **[measured]**

### Contention

- Several processes on one card take turns; NVIDIA's Multi-Process Service exists to reduce that: "Enabling MPS provides the benefit of improved GPU utilization and reduced GPU context switching." <https://docs.nvidia.com/deploy/mps/index.html> **[raw]** It is not needed here: a bake is 1 to 2 s, so a queue of four is shorter than one CPU bake. **[inference]**
- The card also draws the desktop. Blender's manual warns of "issues with interactivity when using the same graphics card for display and rendering". **[raw]** With bakes this short I would expect a stutter at most; I did not watch the screen. **[inference]**

### Determinism

Baked textures compared texel by texel as 8-bit values, 1,048,576 texels each (`target/scratch/gpu/cmp.py`, `count.py`). **[measured]**

| Compared | `slab_1`: texels that differ (largest step) | `tree_1`: texels that differ (largest step) |
|---|---|---|
| CPU against CPU, second run | 0 | 0 |
| CPU at 1, 4 and 16 threads | 0 | not run |
| CUDA against CUDA, second run | 6 (1 level) | 7 (1 level) |
| OptiX against OptiX, second run | 7 (1 level) | 5 (1 level) |
| CPU against CUDA | 14 (2 levels) | 2,815 (3 levels; all but 4 by 1) |
| CPU against OptiX | 471 (26 levels) | 2,829 (2 levels) |

- **The CPU bake is exactly repeatable, and independent of thread count.** That is what `tools/bl`'s header promises, and it held.
- **The GPU bake is not exactly repeatable.** A handful of texels move by one level from run to run on the same device. The RMS difference from the CPU texture is 0.00002 (slab) to 0.00012 (tree) on a 0 to 1 scale.
- **OptiX disagrees with the CPU more than CUDA does** on the slab, whose two pieces pass through each other: 471 texels, some by 26 levels. Prefer CUDA. **[measured]**
- **What that means for the gates.** The mesh and its UVs are made before the bake, so the season check (`tools/same_mesh.py`, byte-identical meshes) is not touched. **[inference]** from `paint.apply`'s order of steps. The baseline check allows an RMSE of 0.01 over the contact sheet (`conventions.toml`, `baseline_rmse`), a hundred times the texture's difference, so it should not trip. **[inference]**, not run. What does change: a rebuilt `assets/models/<asset>.glb` would no longer be the same bytes as the committed one, so every gate run would leave it modified in `git status`.
- I found no statement in Blender's manual that CPU and GPU renders match or differ; the table above is the evidence.

---

## 5. What else the measurements show

These are not GPU matters, but they are where the rest of the time is.

- **Two lines of `tools/foliage.py` are most of a tree's Python time.** Profiled with `cProfile` (`target/scratch/gpu/validate_prof.py`, `gen_prof.py`): **[measured]**
  - `seen_first` (line 305) evaluates `max(xs)` and `max(ys)` in its loop conditions, over every point, once per ray: 17.6 of the 40 CPU-s of L1 on `tree_1`, and 5.3 of the 11.8 CPU-s of the tree's generator.
  - `pads_of` (line 73) calls `numpy.unique(..., axis=0)` on rows of four integers: 15.3 of the 40 CPU-s of L1, and 4.0 of the 11.8 of the generator.
  - Together about 33 of 40 CPU-s in L1 and 9 of 12 in the generator. Hoisting the two maxima out of the loops, and packing each row into one integer before `unique`, should remove most of both. **[inference]**, not tried: no tracked file was changed.
- **L1 on a tree builds its two siblings again every time** (`check_variants`, `tools/validate.py` line 586): 25 of the 40 CPU-s, most of it the two hot spots above. **[measured]**
- **Oversubscription.** Every Blender takes all 16 threads unless `KILN_BLENDER_THREADS` is set (`tools/bl`), so four agents' bakes ask for 64 threads on 16: each bake took 30 s instead of 12 to 19, and the single-threaded steps around them slowed in step (L1 on the tree: 44 CPU-s, 72 to 100 s on the clock). **[measured]** Moving the bake to the GPU removes the cause.
- **Start-up is small but repeated.** Per gate: 4 or 5 Blender starts (2 to 2.5 s), 2 or 4 `asset_view` starts (1.4 s each, a view apiece), about 0.2 s of `cargo run` on each of 3 to 5 Bevy calls, and 1.3 s of montage. One `asset_view` run that takes every view would save 1.4 to 4 s a gate. **[inference]** from the measured start-up times.

---

## 6. Recommendation

**Use the GPU for the bake. Use it for nothing else: there is nothing else to move.**

| Step | Recommendation | Expected gain |
|---|---|---|
| Bake in `tools/paint.py` | CUDA, one bake at a time | 8 to 12 times on the bake; 77 to 92 core-seconds saved per build |
| Whole gate, rock (`slab_1`) | follows from the bake | roughly 20 s to 8 s at low load, about 2.5 times **[inference]** |
| Whole gate, tree (`tree_1`) | follows from the bake | about 14 s off 140 to 175 s, about 10 per cent; its CPU work falls from about 150 to about 75 core-seconds **[inference]** |
| `tests/run.sh --fresh` (43 kept fixtures, most of them a bake on one thread) | follows from the bake | large: each fixture's "minute of one core" becomes about 2 s on the card, taken in turn **[inference]**, not run |
| Review renders (EEVEE) | leave | none: on the GPU already, 0.1 s a tile |
| Bevy screenshots | leave | none: on the GPU already; the time is start-up |
| Bevy load test, generators, unwrap, export, mesh checks | leave | none: CPU code with no GPU path |
| OptiX | do not use | no faster than CUDA here, 238 s to compile once, and further from the CPU result |

What the switch has to include, from the measurements:

1. **A machine-wide lock round the bake** (for example `flock` on a file outside the working copies, since the agents work in separate ones), so that one bake is on the card at a time. Without it, eight at once gave wrong textures with exit code 0.
2. **A check that the bake happened.** The operator's return value is not enough. Cycles prints `ERROR` lines to the log on running out of memory; failing on those, or falling back to the CPU, would catch it. **[inference]**: which check is most reliable was not tested.
3. **A decision on byte-identical outputs.** Either accept that a committed `.glb` differs by a few texels after each rebuild, or keep the CPU for the build whose output is committed and use the GPU while iterating and for the test suite's fixtures (an environment variable read by `paint.py`, CPU by default, would do it). The second keeps the property the docstring of `paint.py` promises.
4. Optionally `CYCLES_CONCURRENT_STATES_FACTOR=0.25` to cut a bake's memory from about 2.7 GB to about 1.2 GB.

If only one thing is done for trees, fix the two lines in `tools/foliage.py` first: that is worth more to a tree's gate than the GPU is.

---

## 7. Not verified

- **`tests/run.sh` was not run**, so the suite's 2 to 7 minutes is not broken down here. That its time is mostly one-thread bakes is from its header and the one-thread bake measured above.
- **No GPU-baked asset was taken through the gates.** That L4's texture checks, L4c and the baseline pass with a GPU texture is inferred from how small the difference is.
- **No clean-machine timings.** Other agents were running throughout; wall-clock figures at an idle machine would be lower, the rock's most of all.
- **Whether CPU and GPU Cycles results are meant to match.** Blender's issue tracker has reports on this (for example issues 89351, 40207 and 69535 on projects.blender.org), but the site refused the fetch and I did not read them. The search also turned up a description of a failed bake writing black texels and returning finished, on a page I could not open; my own runs showed wrong texels and a finished result, which agrees with it.
- **Why `RE_bake_engine` reported success after the device ran out of memory.** I read where the operator's result is set, not the path the error takes inside Cycles.
- **`-- --cycles-device CUDA` through `tools/bl`.** Documented, not tried; `tools/bl` already passes the script's own arguments after `--`, and `paint.py` sets the device to CPU afterwards.
- **That UV unwrapping and the glTF exporter contain no GPU code.** Inferred from there being no setting for it and from their running on one thread; I did not read their source.
- **Vulkan as Blender's backend**, and whether EEVEE's tiles are the same from run to run in bytes (the gate compares them with a tolerance, and `git status` stayed clean across the runs here, which suggests they are).
- **CUDA together with the CPU** (`CUDA+CPU`), NVIDIA MPS, and anything on a second GPU: not tried.
- **Memory per bake at other texture sizes.** Every asset measured used a 1024 px texture.
- **The Bevy `WgpuSettings` wording** was read through a summarising tool.
