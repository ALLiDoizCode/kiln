# The pit profile's budgets: a measurement in Bevy

Measured 2026-10-07 on the development machine, for [issue #8](https://github.com/ALLiDoizCode/kiln/issues/8). Every frame time below is from an RTX 3080. Every figure for GTX 1660 class hardware is an **estimate** made by scaling, to be replaced when that hardware is available.

This note gives numbers for the pit **target profile** and the measurement behind them. It does not edit any profile file. It does not draw on the `first-attempt` tag.

## How to read this

- **Measured** means a number from the raw files in [`pit-budget-measurement/`](pit-budget-measurement/). Frame times are the middle of three repeats, with the lowest and highest beside them.
- **Arithmetic** means a number worked out from sizes, such as the bytes in a texture.
- **Estimate** means a measured number multiplied by a scaling factor for slower hardware. No estimate here has been checked on that hardware.
- **Assumption** means a figure this note had to choose because nothing in the repo states it. Each one is listed in section 2 for the owner to confirm, and the budgets are given as tables so a different choice can be read off.
- Kiln's own words (target profile, asset, size, static asset, production ready) are used as `CONTEXT.md` defines them.

### Terms used here

Earlier notes define mesh, triangle, vertex, UV, normal map, tangent, PBR, mipmaps and LOD. Terms added by this note:

- **Frame time:** how long one picture takes to make, in milliseconds (ms). 60 frames per second leaves 16.7 ms for each frame.
- **Median, 95th and 99th percentile:** of the recorded frames, the time that half, 95% and 99% of them came in under. The percentiles show the slow frames a mean would hide.
- **Vsync:** making the program wait for the monitor before showing each frame. It caps the frame rate at the monitor's, so it is off here.
- **GPU-bound and CPU-bound:** which of the two a frame is waiting for. A scaling factor for a slower GPU only applies to a frame that is GPU-bound.
- **Shadow map:** a picture of the scene drawn from the light, used to tell which surfaces are in shadow. Every triangle that casts a shadow is drawn again into it.
- **Shadow cascade:** one of several shadow maps for the sun, each covering a band of distance from the camera. Bevy uses four by default, so a triangle can be drawn up to five times: once for the screen and once for each cascade it falls in.
- **MSAA (multisample anti-aliasing):** smoothing jagged edges by storing several samples for each pixel. Bevy's default is four.
- **Video memory (VRAM):** the GPU's own memory, where textures and meshes must fit. The RTX 3080 has 10 GB, a GTX 1660 has 6 GB.
- **Block compression:** texture formats the GPU reads directly while they stay compressed in video memory. BC7, used here, takes 1 byte per pixel where an uncompressed texture takes 4.
- **Level of detail (LOD):** a version of a mesh with fewer triangles, shown in place of the full one when the asset is far away.

## Summary

All of this is for 1920×1080, 60 frames per second, Bevy 0.19.1 with its default renderer settings, and the assumptions in section 2.

**Triangle budget (estimate).** About **4 million triangles on screen** in total, with shadows on. As a number for each asset: **10,000 triangles**, which holds while no more than about 400 assets are in view at once.

- The scaling: frame time on a GTX 1660 is taken as **3 times** the RTX 3080's. Published figures put that factor between 2.2 and 4.3, which moves the total between about 8 million and 2.5 million triangles (section 5).
- The estimate gives static assets half the frame, 8.3 ms. That share is an assumption.
- Shadows decide this number more than anything else. Each triangle cost 2.8 to 4.8 times as much with Bevy's default shadows as without. With shadows off the same reasoning gives about 22 million triangles.

**Texture budget (estimate).** **2048×2048 for each of an asset's three textures, block compressed, with mipmaps**: 16 MiB of video memory for each asset. Without block compression the same memory buys **1024×1024**.

- Texture size did not change frame time when textures had mipmaps (256 to 4096, within 8%, with no trend). It is a memory budget, not a frame-time budget.
- The arithmetic assumes 2 GiB of a 6 GB card for static asset textures, which holds 128 different assets at 16 MiB each. That 2 GiB is an assumption.
- Mipmaps are needed for frame time as well as for looks: 4096 textures without them cost 44% more frame time.

**Levels of detail.** **Not needed up to about 400 assets of 10,000 triangles in view** (4 million triangles). **Needed beyond that**, unless shadows are made cheaper instead.

- 1,000 assets of 10,000 triangles took 4.37 ms on the RTX 3080, an estimated 13 ms on a GTX 1660: over the 8.3 ms share.
- The same scene with three levels of detail took 1.27 ms, an estimated 4 ms. With them, 3,000 assets of 20,000 triangles fit as well.
- Whether the pit game ever shows more than 400 assets at once is not known from this repo. Until it is, the spec's "levels of detail off" stands for small scenes and fails for large ones.

**What the measurement cannot say:** how a GTX 1660 really behaves, how the pit game's real scenes are laid out, or how many triangles an asset needs to look right at 0.5 m. Section 8 lists these.

## 1. What was built

`crates/budget_bench` is a Bevy program that draws procedural scenes and times them. One command runs everything and overwrites the raw files:

```
cargo run --release -p budget_bench -- --out learn/research/pit-budget-measurement
```

It takes about **16 minutes** (953 seconds measured) and the whole screen. It opens a full-screen window on the GPU, draws 66 scenes three times over, closes the window and exits. `--only <name prefix>` runs some of the scenes and `--repeats N` changes the three repeats.

It writes four files:

| File | Holds |
|---|---|
| `results.csv` | One row per scene per repeat: the scene's settings and every measured figure. |
| `summary.csv` | One row per scene: the middle repeat, and the lowest and highest median frame time. |
| `memory.csv` | Video memory of eight scenes, each run alone in its own process. |
| `environment.json` | Versions, hardware, settings, the commit, and what else was using the GPU. |

## 2. Assumptions to confirm

| Assumption | Value used | Where it comes from | What changes if it is wrong |
|---|---|---|---|
| Closest view | 0.5 m | `learn/MISSION.md` | The nearest asset fills more or less of the screen. |
| Eye height | 1.7 m | A 1.8 m player (`learn/MISSION.md`) | Little. |
| Field of view | 72° vertical | A look test in the `pit` repo (`look-tests/voxel-pit/src/main.rs`); not a stated decision | A wider view holds more assets, each smaller. |
| Resolution | 1920×1080 | Not stated anywhere; the commonest for this class of hardware | Per-pixel cost scales with pixel count. Triangle cost does not. |
| Frame rate | 60 per second, 16.7 ms | `learn/MISSION.md` | Budgets scale with the time allowed. |
| Share of the frame for static assets | 50%, 8.3 ms | **Chosen here.** The rest is for terrain, characters, effects, interface and the game's own logic | See the tables in section 5. |
| Asset **size** | 1 m | Chosen here as a middle prop | Smaller assets cover fewer pixels each. |
| How assets stand | One every 2 m on the ground, as far as needed | Chosen here; the pit game's real density is unknown | Decides how many assets are in view and how far the farthest is. |
| Shadows | Bevy's default: four cascades of 2048 pixels reaching 150 m | Bevy 0.19.1 defaults | The largest lever on the triangle budget (section 4). |
| Video memory for static asset textures | 2 GiB of 6 GB | **Chosen here** | See the table in section 6. |
| GTX 1660 is 3 times slower | ×3, range ×2.2 to ×4.3 | Published figures (section 5) | Every estimate scales with it. |

The pit game's scene is the weakest of these. The pit is a vertical world with climbing and building on a 3 m grid, and this measurement used flat ground with rocks on it. It answers "what does a scene of N assets of T triangles cost", not "what do the pit game's scenes look like".

## 3. Method

### The scenes

- **Camera.** First person at 1.7 m, looking 8° below the horizon, 72° vertical field of view.
- **Assets.** Each is a rock-like closed shape 1 m across: a sphere grid pushed in and out by a few waves, built at an exact triangle count with UVs, normals and tangents. A unit test checks the counts.
- **Material.** Bevy's lit PBR `StandardMaterial` with three textures: base colour, normal map, and metallic-roughness. The textures are noise at three scales, so no part is flat.
- **Where assets stand.** The nearest asset's surface is 0.5 m from the camera, to the right of centre, where it covers a large part of the screen. The rest stand on the ground in the wedge the camera sees, on a jittered 2 m grid, nearest first. More assets therefore reach further: 100 assets reach 22 m, 300 reach 37 m, 1,000 reach 68 m and 3,000 reach 118 m.
- **Light.** One directional light (a sun) with shadows, and ambient light. A ground plane.
- **Different assets, not copies.** A real scene has many different assets, and an engine can draw copies of one asset more cheaply. So each sweep says how many *different* assets (own mesh, own material, own three textures) its instances are drawn from. The triangle sweep uses 100 different assets. The count sweep uses 64, with contrast runs of one asset repeated and of every asset different.

### What was varied

Each variable was swept while the others were held at a middle: 100 assets, 10,000 triangles, 1024 textures.

| Sweep | Values | Held |
|---|---|---|
| Triangles per asset | 1,000 to 1,000,000 in ten steps | 100 different assets |
| Texture size | 256 to 4096; also without mipmaps; also block compressed | 300 assets from 12 different ones (so 4096 fits in memory) |
| Assets on screen | 1 to 3,000 in seven steps | 10,000 triangles; 64 different assets |
| Combined points | 300, 1,000 and 3,000 assets at 20,000 and 50,000 triangles | 64 different assets |
| Levels of detail | The combined points and two counts again, with far assets reduced | |
| Contrasts | Shadows off; one and two cascades; MSAA off | |

With levels of detail on, an asset keeps all its triangles nearer than 10 m, a quarter from 10 m, a sixteenth from 20 m and a sixty-fourth from 40 m. Those distances keep roughly one triangle per pixel for a 10,000-triangle asset (section 7).

### How frames were timed

- **Release build, vsync off** (`PresentMode::AutoNoVsync`), full screen at **1920×1080**. Every row of `results.csv` records the window as 1920×1080. The frame rate was not capped: the empty scene ran at about 880 frames per second on a 240 Hz monitor.
- **Warm-up, then sample.** The first 1.2 seconds and 40 frames of each scene are thrown away. Frames are then recorded for 2 seconds, or until 200 are recorded. A scene at 1 ms a frame gives about 1,500 frames; the slowest gives 200.
- **Reported:** median, 95th and 99th percentile frame time, taken from the time between frames in Bevy's main loop.
- **GPU-bound or not.** Two extra readings tell them apart. `nvidia-smi` reports how busy the GPU was; 95% or more is treated as GPU-bound. Bevy's render diagnostics give the GPU time of the main pass. **Bevy 0.19.1 does not time its shadow passes**, so with shadows on there is no direct reading of the GPU's whole frame, and frame time while GPU-bound stands in for it.
- **Three repeats**, each running every scene, so that anything drifting during the run is spread over all scenes.
- **Settings left at Bevy's defaults and recorded:** MSAA 4 samples, no depth prepass, trilinear texture filtering with no anisotropic filtering, shadows as in section 2.

### Two things found while building it

- **Scenes in one process affect each other.** After a scene with 3,000 different assets, a light scene that took 1.31 ms fresh took 1.58 to 1.72 ms. Bevy keeps some per-frame work sized to the largest scene it has drawn. So the scenes run in six groups, each a fresh process, with the heaviest kind last and alone. Every group ends by drawing the same light scene again as a check. Five of six checks match the fresh scene to within 0.01 ms (section 4, last table). The sixth follows the 3,000 different assets and shows the effect; nothing is measured after it.
- **Video memory cannot be read between scenes in one process**, because the process does not hand memory back. Eight scenes are therefore run alone, one process each, for `memory.csv`.

### Hardware and software

| | |
|---|---|
| GPU | NVIDIA GeForce RTX 3080, 10 GB, driver 610.57.04, Vulkan |
| CPU | AMD Ryzen 7 5800X, 8 cores |
| System | Linux 7.2.5, Hyprland 0.56.2 on Wayland, one 1920×1080 monitor at 240 Hz |
| Engine | Bevy 0.19.1 (wgpu 29.0.4), release build |
| Commit | `2da41dc`, with no uncommitted changes |
| Also on the GPU | The desktop only: Hyprland 236 MiB, quickshell 306 MiB, a browser's GPU process 91 to 99 MiB, two small helpers. About 980 MiB in use before each scene. No other 3D program. |

## 4. What was measured

Frame times are in milliseconds on the RTX 3080. "Median" is the middle repeat's median with the lowest and highest repeat in brackets. "Main pass GPU ms" is the GPU time of the pass that draws the scene to the screen, without the shadow passes.

### Noise

- Across the three repeats, a scene's median frame time moved by 0.7% at the middle scene and 3.7% at the worst.
- An earlier full run of 16 minutes the same day agreed with this one to within 2.4% on every scene, and to within 0.4% on half of them. The one exception is `check-distinct`, the scene that shows the carry-over effect, at 5%. That run's files were not kept.
- Within a sample, the second half's median differed from the first half's by 0.3% at the middle and 2.7% at the worst.
- **Differences under about 5% are treated as noise below.** One exception is noted under textures.

### Fixed cost

| scene | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- |
| `empty` | 1.14 (1.13–1.15) | 1.28 | 1.40 | 39% | 0.08 |
| `empty-noshadow` | 1.01 (1.00–1.02) | 1.11 | 1.21 | 40% | 0.07 |

An empty scene takes about 1 ms and the GPU is idle for most of it. That 1 ms is the CPU's share of a frame on this machine. **Frame times under about 1.6 ms here are CPU-bound** and say little about the GPU.

### Triangles per asset

100 different assets, the farthest 22 m away, shadows on:

| scene | triangles per asset | million triangles on screen | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tris-1k` | 1,000 | 0.10 | 1.31 (1.29–1.31) | 1.46 | 1.62 | 49% | 0.24 |
| `tris-2k` | 2,000 | 0.20 | 1.31 (1.29–1.31) | 1.45 | 1.56 | 49% | 0.23 |
| `tris-5k` | 5,000 | 0.50 | 1.31 (1.30–1.32) | 1.45 | 1.56 | 61% | 0.32 |
| `tris-10k` | 10,000 | 1.00 | 1.31 (1.30–1.31) | 1.45 | 1.55 | 84% | 0.45 |
| `tris-20k` | 20,000 | 2.00 | 1.71 (1.70–1.72) | 1.95 | 2.14 | 96% | 0.73 |
| `tris-50k` | 50,000 | 5.00 | 3.16 (3.16–3.16) | 3.44 | 3.66 | 98% | 1.08 |
| `tris-100k` | 100,000 | 10.00 | 5.54 (5.52–5.55) | 5.82 | 6.38 | 99% | 1.65 |
| `tris-200k` | 200,000 | 20.00 | 9.40 (9.38–9.41) | 9.86 | 10.82 | 99% | 2.27 |
| `tris-500k` | 500,000 | 50.00 | 21.76 (21.72–21.77) | 23.05 | 24.12 | 100% | 4.63 |
| `tris-1m` | 1,000,000 | 100.00 | 43.91 (43.78–43.94) | 45.95 | 46.61 | 100% | 8.94 |

The same with shadows off:

| scene | triangles per asset | million triangles on screen | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tris-noshadow-1k` | 1,000 | 0.10 | 1.07 (1.07–1.08) | 1.18 | 1.29 | 39% | 0.15 |
| `tris-noshadow-10k` | 10,000 | 1.00 | 1.07 (1.07–1.08) | 1.18 | 1.27 | 56% | 0.32 |
| `tris-noshadow-50k` | 50,000 | 5.00 | 1.23 (1.22–1.23) | 1.47 | 1.62 | 95% | 0.91 |
| `tris-noshadow-100k` | 100,000 | 10.00 | 1.75 (1.74–1.78) | 2.01 | 2.24 | 97% | 1.46 |
| `tris-noshadow-500k` | 500,000 | 50.00 | 5.41 (5.40–5.42) | 5.84 | 6.09 | 99% | 5.11 |
| `tris-noshadow-1m` | 1,000,000 | 100.00 | 9.67 (9.66–9.67) | 10.41 | 10.70 | 99% | 9.40 |

What this shows:

- **Below about 2 million triangles the frame is CPU-bound** and triangle count does not show. Above it, frame time rises in a straight line with the total.
- A straight line through the GPU-bound points fits to within 6%:
  - shadows on: **0.93 ms + 0.427 ms for each million triangles**;
  - shadows off: **0.85 ms + 0.089 ms for each million triangles**.
- **Shadows multiplied the cost of a triangle by 4.8** in this scene. With shadows off, the main pass's GPU time is nearly the whole frame (9.40 of 9.67 ms). With shadows on, the main pass is a fifth of it (8.94 of 43.91 ms); the rest is the shadow passes, which Bevy does not time. All 100 assets stand within 22 m, where every one of the four cascades covers them.

### Assets on screen

10,000 triangles each, drawn from 64 different assets, shadows on:

| scene | assets | different assets | million triangles | farthest asset m | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `count-1` | 1 | 1 | 0.01 | 1 | 1.18 (1.17–1.21) | 1.35 | 1.47 | 40% | 0.11 |
| `count-10` | 10 | 10 | 0.10 | 6 | 1.19 (1.19–1.21) | 1.31 | 1.42 | 47% | 0.18 |
| `count-30` | 30 | 30 | 0.30 | 12 | 1.22 (1.21–1.22) | 1.37 | 1.69 | 56% | 0.26 |
| `count-100` | 100 | 64 | 1.00 | 22 | 1.26 (1.26–1.27) | 1.41 | 1.51 | 84% | 0.41 |
| `count-300` | 300 | 64 | 3.00 | 37 | 2.00 (1.99–2.02) | 2.23 | 2.45 | 97% | 0.71 |
| `count-1k` | 1000 | 64 | 10.00 | 68 | 4.37 (4.30–4.39) | 4.66 | 5.08 | 99% | 1.39 |
| `count-3k` | 3000 | 64 | 30.00 | 118 | 9.14 (9.14–9.15) | 9.61 | 10.54 | 99% | 2.92 |

Shadows off:

| scene | assets | different assets | million triangles | farthest asset m | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `count-noshadow-100` | 100 | 64 | 1.00 | 22 | 1.06 (1.06–1.06) | 1.18 | 1.29 | 51% | 0.26 |
| `count-noshadow-1k` | 1000 | 64 | 10.00 | 68 | 1.58 (1.58–1.60) | 1.83 | 1.99 | 96% | 1.29 |
| `count-noshadow-3k` | 3000 | 64 | 30.00 | 118 | 3.33 (3.31–3.35) | 3.55 | 3.84 | 98% | 3.00 |

One asset repeated, the best case for the engine:

| scene | assets | different assets | million triangles | farthest asset m | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `count-shared-100` | 100 | 1 | 1.00 | 22 | 1.23 (1.23–1.24) | 1.35 | 1.47 | 76% | 0.30 |
| `count-shared-1k` | 1000 | 1 | 10.00 | 68 | 4.31 (4.31–4.33) | 4.61 | 4.85 | 99% | 1.38 |
| `count-shared-3k` | 3000 | 1 | 30.00 | 118 | 9.16 (9.15–9.17) | 9.70 | 10.01 | 99% | 2.97 |

Every asset different, with 256 textures so that 3,000 sets fit in memory:

| scene | assets | different assets | million triangles | farthest asset m | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `count-distinct-100` | 100 | 100 | 1.00 | 22 | 1.30 (1.28–1.31) | 1.45 | 1.56 | 82% | 0.39 |
| `count-distinct-1k` | 1000 | 1000 | 10.00 | 68 | 4.62 (4.61–4.63) | 4.99 | 5.46 | 99% | 1.56 |
| `count-distinct-3k` | 3000 | 3000 | 30.00 | 118 | 9.90 (9.88–9.92) | 11.34 | 12.39 | 99% | 3.33 |

What this shows:

- **The number of assets costs almost nothing by itself; their triangles do.** With shadows off, 3,000 assets holding 30 million triangles took 3.33 ms. The triangle sweep's line predicts 3.5 ms for 30 million triangles in 100 assets.
- **Different assets cost little more than copies.** One asset repeated 3,000 times and 64 different assets took the same time (9.16 and 9.14 ms). 3,000 different assets took 8% more (9.90 ms), with a worse 99th percentile (12.39 against 10.54 ms). Bevy 0.19.1 batches draws on the GPU on this hardware, and the measurement bears that out. This is a CPU and driver matter, so it may not carry to a weaker CPU.
- **Shadows cost less per triangle when assets are spread out.** From 1,000 to 3,000 assets each extra million triangles cost 0.24 ms with shadows, against 0.087 ms without: 2.8 times. In the triangle sweep, where everything is near, it was 4.8 times. Far assets fall in fewer cascades.

### Combined points

Shadows on, 64 different assets:

| scene | assets | triangles per asset | million triangles | farthest asset m | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `mix-300x20k` | 300 | 20,000 | 6.00 | 37 | 3.30 (3.27–3.33) | 3.60 | 3.83 | 98% | 1.18 |
| `mix-300x50k` | 300 | 50,000 | 15.00 | 37 | 6.69 (6.63–6.72) | 7.09 | 7.66 | 99% | 1.89 |
| `mix-1kx20k` | 1000 | 20,000 | 20.00 | 68 | 7.78 (7.73–7.81) | 8.09 | 8.85 | 99% | 2.37 |
| `mix-1kx50k` | 1000 | 50,000 | 50.00 | 68 | 17.08 (17.07–17.11) | 18.09 | 19.11 | 100% | 4.46 |
| `mix-3kx20k` | 3000 | 20,000 | 60.00 | 118 | 17.16 (17.14–17.17) | 18.33 | 18.90 | 100% | 5.27 |

No single line fits these and the count sweep together (the best is 29% out), because the cost of a triangle with shadows depends on how far away it is. The near line from the triangle sweep, 0.427 ms per million, is the worst case measured and is the one the budget uses.

### Shadow cascades and anti-aliasing

| scene | cascades | MSAA samples | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `mix-1kx20k` | 4 | 4 | 7.78 (7.73–7.81) | 8.09 | 8.85 | 99% | 2.37 |
| `cascades-2-1kx20k` | 2 | 4 | 4.75 (4.70–4.76) | 5.01 | 5.37 | 99% | 2.35 |
| `cascades-1-1kx20k` | 1 | 4 | 4.29 (4.29–4.35) | 4.56 | 4.85 | 98% | 2.21 |
| `msaa-off-1kx20k` | 4 | 1 | 7.06 (7.06–7.06) | 7.55 | 8.04 | 99% | 1.73 |
| `tris-10k` | 4 | 4 | 1.31 (1.30–1.31) | 1.45 | 1.55 | 84% | 0.45 |
| `msaa-off-100x10k` | 4 | 1 | 1.31 (1.30–1.31) | 1.46 | 1.59 | 69% | 0.27 |

- **Two cascades in place of four cut the frame by 39%** (7.78 to 4.75 ms) at 1,000 assets of 20,000 triangles. Fewer cascades give coarser shadows; how much coarser was not looked at.
- **Turning MSAA off saved 9%** in the heavy scene. These scenes are dominated by triangle work, not per-pixel work.

### Texture size

300 assets drawn from 12 different ones, 10,000 triangles each, shadows on:

| scene | texture size | format | mipmaps | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tex-256` | 256 | rgba8 | yes | 1.93 (1.92–1.93) | 2.14 | 2.44 | 97% | 0.67 |
| `tex-512` | 512 | rgba8 | yes | 1.93 (1.93–1.93) | 2.15 | 2.34 | 97% | 0.68 |
| `tex-1024` | 1024 | rgba8 | yes | 1.93 (1.93–1.94) | 2.17 | 2.63 | 97% | 0.68 |
| `tex-2048` | 2048 | rgba8 | yes | 1.79 (1.79–1.80) | 2.01 | 2.20 | 97% | 0.57 |
| `tex-4096` | 4096 | rgba8 | yes | 1.95 (1.95–1.96) | 2.22 | 2.62 | 97% | 0.72 |
| `tex-nomips-1024` | 1024 | rgba8 | no | 1.94 (1.94–1.95) | 2.15 | 2.30 | 97% | 0.70 |
| `tex-nomips-4096` | 4096 | rgba8 | no | 2.80 (2.80–2.81) | 3.04 | 3.23 | 98% | 1.47 |
| `tex-bc7-1024` | 1024 | bc7 | yes | 1.78 (1.75–1.78) | 1.98 | 2.15 | 96% | 0.54 |
| `tex-bc7-2048` | 2048 | bc7 | yes | 1.93 (1.93–1.93) | 2.16 | 2.37 | 97% | 0.68 |
| `tex-bc7-4096` | 4096 | bc7 | yes | 1.83 (1.83–1.83) | 2.03 | 2.14 | 97% | 0.59 |

- **With mipmaps, texture size from 256 to 4096 made no difference that follows size.** The scenes fall at two levels, about 1.93 ms and about 1.80 ms. The gap of 7% repeats in every run, so it is not noise, but it does not follow size or format: 2048 is at the low level uncompressed and at the high level compressed. Its cause is unknown. It is not evidence that any size is cheaper.
- **Without mipmaps, 4096 textures cost 44% more frame time** (2.80 against 1.95 ms); 1024 textures cost the same as with them. A far asset reading a large texture at full size jumps across memory with every pixel. Bevy 0.19 gives PNG textures no mipmaps (earlier note, section 5), so this is the case a plain glTF file is in.
- **Block compression made no difference to frame time.** The BC7 textures here were random blocks, not compressed pictures; the cost of storing and reading a block does not depend on what it shows.

### Video memory

Each scene alone in a process. "Process MiB" is what the driver counts against the measuring process. "Arithmetic" is bytes of textures (every mip level) plus bytes of meshes (48 bytes a vertex, 4 an index).

| scene | different assets | texture size | format | texture MiB by arithmetic | mesh MiB by arithmetic | process MiB measured | less the empty scene | measured ÷ arithmetic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `empty` | 0 | — | — | 0 | 0 | 531 | 0 | — |
| `tex-1024` | 12 | 1024 | rgba8 | 192 | 4 | 595 | 64 | 0.33 |
| `tex-bc7-2048` | 12 | 2048 | bc7 | 192 | 4 | 595 | 64 | 0.33 |
| `tex-2048` | 12 | 2048 | rgba8 | 768 | 4 | 1301 | 770 | 1.00 |
| `tex-bc7-4096` | 12 | 4096 | bc7 | 768 | 4 | 1301 | 770 | 1.00 |
| `tris-10k` | 100 | 1024 | rgba8 | 1600 | 35 | 2071 | 1540 | 0.94 |
| `tex-4096` | 12 | 4096 | rgba8 | 3072 | 4 | 4949 | 4418 | 1.44 |
| `tris-1m` | 100 | 1024 | rgba8 | 1600 | 3445 | 5807 | 5276 | 1.05 |

- **An empty Bevy window holds 531 MiB** before any asset is loaded. What it is made of was not looked into.
- **Block compression holds memory to a quarter**, as the arithmetic says: BC7 textures at 2048 measured the same as uncompressed ones at 1024, and BC7 at 4096 the same as uncompressed at 2048.
- **Arithmetic matched measurement to within 6%** between 770 MiB and 5.3 GiB, with two exceptions. The smallest scenes measured a third of the arithmetic, which suggests the first couple of hundred MiB go into memory the empty window had already reserved. Twelve sets of uncompressed 4096 textures measured 44% over. The cause was not found; these are the only 64 MiB textures in the run.
- **24 sets of uncompressed 4096 textures (6 GiB) would not load at all** on the 10 GB card in an early trial; the renderer stopped with an out-of-memory error. That trial is not in the raw files.
- **Meshes are small beside textures.** A 10,000-triangle asset's mesh is 0.35 MiB; its three 1024 textures are 16 MiB.

### Check scenes

The `tris-10k` scene drawn again as the last scene of each process:

| scene | median ms (lowest–highest of 3) | p95 ms | p99 ms | GPU busy | main pass GPU ms |
| --- | --- | --- | --- | --- | --- |
| `tris-10k` | 1.31 (1.30–1.31) | 1.45 | 1.55 | 84% | 0.45 |
| `check-triangles` | 1.32 (1.31–1.32) | 1.45 | 1.55 | 79% | 0.41 |
| `check-textures` | 1.31 (1.30–1.32) | 1.44 | 1.56 | 81% | 0.43 |
| `check-counts` | 1.31 (1.31–1.31) | 1.45 | 1.62 | 75% | 0.35 |
| `check-mixes` | 1.31 (1.30–1.31) | 1.47 | 1.64 | 82% | 0.42 |
| `check-lods` | 1.31 (1.30–1.31) | 1.44 | 1.54 | 85% | 0.43 |
| `check-distinct` | 1.58 (1.58–1.59) | 1.76 | 1.93 | 63% | 0.31 |

## 5. The triangle budget

### The scaling factor

The GTX 1660's frame time is estimated as the RTX 3080's multiplied by a factor. **This note uses 3, with a range of 2.2 to 4.3.**

No test was found that puts an RTX 3080 and a GTX 1660 class card through the same games at 1080p on a page that could be read. TechPowerUp's database and reviews, the usual source, refused the request. The factor therefore rests on synthetic tests:

| Source | What it measures | RTX 3080 ÷ GTX 1660 | ÷ 1660 Super | ÷ 1660 Ti | ÷ RX 5600 XT |
|---|---|---|---|---|---|
| [3DMark Time Spy graphics score, ComputerBase](https://www.computerbase.de/2024-07/3dmark-time-spy-benchmark/) | One test bench, a GPU-bound test at 1440p | not listed | 2.93 | 2.87 | not listed |
| [3DMark Steel Nomad graphics score, UL](https://benchmarks.ul.com/compare/best-gpus) | Users' results, a heavy modern test | 4.25 | 3.57 | 3.40 | 2.67 |
| [PassMark G3D Mark](https://www.videocardbenchmark.net/high_end_gpus.html) | Users' results, a mix that includes CPU-bound tests | 2.15 | 1.97 | 1.99 | 1.87 |
| [3DMark Fire Strike graphics, technical.city](https://technical.city/en/gpu/GeForce-GTX-1660-Super-vs-GeForce-RTX-3080) | An aggregator; method not disclosed | 2.77 | 2.45 | 2.45 | 1.78 |

- **Why 3:** Time Spy is the one GPU-bound test from a single known bench, and gives 2.9 for the 1660 Super and Ti. The plain GTX 1660 scores 8 to 19% below the Super where both are listed, which puts it a little over 3.
- **Why 2.2 to 4.3:** PassMark is a floor, because some of its tests are held back by the CPU. Steel Nomad is a ceiling, for the heaviest shading. The RX 5600 XT, the mission's other named card, is the fastest of the four: about 2.4, range 1.8 to 2.7.
- **Why the factor is soft for this workload.** These figures average over whole tests or games. The scenes here are bound by triangle work, mostly in shadow passes. Nothing found says how triangle throughput alone compares between the two cards. The cards' pixel rates differ by 1.9 and their memory bandwidth by 2.3 to 4.0 (from a mirror of specification data that does not name its source), so a load of a different kind could scale differently.
- **Memory does not scale.** A GTX 1660 has 6 GB against 10 GB. Section 6 budgets in absolute bytes.
- **The CPU does not scale with the GPU.** The 1 ms floor here is a Ryzen 7 5800X. A slower CPU raises it, and no GPU factor says by how much.

### From measurement to budget

The estimate multiplies the whole RTX 3080 frame time by the factor and asks what fits in the share of the frame allowed. With the near, shadows-on line from section 4:

> million triangles on screen = (16.7 ms × share ÷ factor − 0.93) ÷ 0.427

Million triangles on screen that fit, **shadows on**, by that line:

| share of frame for static assets | ms on the GTX 1660 | factor 2.2 | factor 3 | factor 4.3 |
| --- | --- | --- | --- | --- |
| 25% | 4.2 | 2.3 | 1.1 | 0.1 |
| **50%** | **8.3** | 6.7 | **4.3** | 2.4 |
| 75% | 12.5 | 11.1 | 7.6 | 4.6 |
| 100% | 16.7 | 15.6 | 10.8 | 6.9 |

**Shadows off** (0.85 ms + 0.089 ms per million):

| share of frame for static assets | ms on the GTX 1660 | factor 2.2 | factor 3 | factor 4.3 |
| --- | --- | --- | --- | --- |
| 25% | 4.2 | 11.7 | 6.1 | 1.3 |
| **50%** | **8.3** | 33.1 | **21.7** | 12.2 |
| 75% | 12.5 | 54.4 | 37.4 | 23.2 |
| 100% | 16.7 | 75.8 | 53.0 | 34.1 |

The measured scenes agree with the line. At factor 3 and a 50% share the RTX 3080 has 2.78 ms:

| Fits (under 2.78 ms) | Does not fit |
|---|---|
| 100 assets × 20,000 triangles: 1.71 ms | 100 assets × 50,000: 3.16 ms |
| 300 assets × 10,000: 2.00 ms | 300 assets × 20,000: 3.30 ms |
| | 1,000 assets × 10,000: 4.37 ms |

Reading between those points gives 4.2 million triangles in the near scene and 5.3 million in the spread one.

**The triangle budget, as an estimate: about 4 million triangles on screen with shadows on, at factor 3 and a 50% share.** Across the factor's range it is about 2.5 to 8 million.

How soft it is:

- The factor alone moves it by a factor of three end to end.
- The line multiplies the 0.93 ms fixed part by the factor too. Part of that is the CPU's time, which a slower GPU does not lengthen. This makes the estimate cautious by up to about 1.5 ms of the GTX 1660's frame.
- It uses the near scene's cost per triangle, the highest measured. A scene spread to 68 m or more cost 44% less per extra triangle.
- It assumes Bevy's default shadows. Fewer cascades would raise it (two in place of four cut one heavy scene's frame by 39%); no shadows from static assets would raise it five times.

### For each asset

A target profile carries a triangle budget for one asset. The total divides among the assets in view:

| assets in view at once | triangles each, shadows on (4 million) | shadows off (22 million) |
|---|---|---|
| 100 | 40,000 | 220,000 |
| 200 | 20,000 | 110,000 |
| **400** | **10,000** | 55,000 |
| 1,000 | 4,000 | 22,000 |
| 3,000 | 1,300 | 7,000 |

**Suggested for the pit profile: 10,000 triangles for an asset, as an estimate**, good for about 400 assets in view without levels of detail. It is a round number inside every vendor's low-poly range found by the earlier note (15,000 to 50,000 faces at most), and twice the 5,000 the Blender trial reduced to.

Two cautions:

- This is what the frame can afford, **not what an asset needs to look right**. Whether 10,000 triangles hold a 1 m prop's outline at 0.5 m is a question for the generator trial and shape review, not for this measurement.
- The budget is for a 1 m asset. A building piece on the 3 m grid covers nine times the area. Whether the budget should grow with **size** is not settled here.

## 6. The texture budget

Frame time does not set it (section 4). Video memory does.

Bytes for one asset's three textures (base colour, normal, metallic-roughness), with the full mip chain, which adds a third:

| texture size | uncompressed, 4 bytes a pixel | block compressed (BC7), 1 byte a pixel |
|---|---|---|
| 512 | 4 MiB | 1 MiB |
| 1024 | 16 MiB | 4 MiB |
| **2048** | 64 MiB | **16 MiB** |
| 4096 | 256 MiB | 64 MiB |

How many different assets fit depends on the memory given to them. On a 6 GB card, by arithmetic:

- 6,144 MiB on the card;
- less about 530 MiB for an empty Bevy window (measured on the RTX 3080; not known for a GTX 1660);
- less the desktop and other programs (about 980 MiB on this machine during the run, 675 MiB earlier in the day);
- leaves about 4.5 GiB for the whole game.

**Assumption: 2 GiB of that for static asset textures.** Different assets loaded at once that fit in it:

| texture size | uncompressed | block compressed |
|---|---|---|
| 1024 | 128 | 512 |
| **2048** | 32 | **128** |
| 4096 | 8 | 32 |

For another allowance, divide it by the bytes in the first table.

**The texture budget, as an estimate: 2048×2048 for each of the three textures, block compressed, with mipmaps.** That is 16 MiB for an asset and 128 different assets in 2 GiB. The spec already switches compression and mipmaps on for the pit profile. Until that stage exists, **1024×1024 uncompressed** costs the same memory.

How soft it is:

- It is arithmetic checked against measurement on the 10 GB card, not a test on a 6 GB card. It rests on the 2 GiB allowance and on how many different assets the pit game loads at once, which is not known.
- Measured memory ran up to 44% over arithmetic for the largest textures (section 4). Leave room.
- Not every texture needs the same size or format. A normal map can use a two-channel block format and a metallic-roughness map a smaller size. This note budgets all three alike.
- **It says nothing about sharpness.** At 0.5 m and 1080p one screen pixel covers about 0.7 mm of a surface straight ahead, which is about 1,500 pixels a metre. The earlier note's Blender trial measured 1,115 texels a metre on a 1.2 m boulder with 2048 textures. So a 2048 texture on a 1 m asset is somewhat under one texel per pixel at the closest view: a little soft, by arithmetic. Whether that is visible is a question for final review.

## 7. Levels of detail

**How small assets get.** A 1 m asset d metres away is about 743 ÷ d pixels tall at 1080p with this field of view:

| distance | height on screen | pixels covered, about | triangles facing the camera, of 10,000 |
|---|---|---|---|
| 0.5 m | fills the screen | all it can | 5,000 |
| 10 m | 74 pixels | 4,300 | 5,000 |
| 22 m (100 assets) | 34 pixels | 900 | 5,000 |
| 37 m (300 assets) | 20 pixels | 320 | 5,000 |
| 68 m (1,000 assets) | 11 pixels | 94 | 5,000 |
| 118 m (3,000 assets) | 6 pixels | 31 | 5,000 |

Beyond about 10 m a 10,000-triangle asset has more triangles than pixels. Past that, triangles are paid for and cannot be seen.

**What levels of detail bought**, measured. Far assets used a quarter of their triangles from 10 m, a sixteenth from 20 m and a sixty-fourth from 40 m:

| assets | triangles per asset at full detail | farthest asset m | million triangles, no LOD | median ms, no LOD | GPU busy | million triangles, LOD | median ms, LOD | GPU busy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | 10,000 | 68 | 10.00 | 4.37 (4.30–4.39) | 99% | 0.64 | 1.27 (1.26–1.28) | 71% |
| 3000 | 10,000 | 118 | 30.00 | 9.14 (9.14–9.15) | 99% | 0.95 | 1.31 (1.31–1.32) | 74% |
| 300 | 20,000 | 37 | 6.00 | 3.30 (3.27–3.33) | 98% | 1.02 | 1.26 (1.26–1.27) | 78% |
| 300 | 50,000 | 37 | 15.00 | 6.69 (6.63–6.72) | 99% | 2.54 | 2.03 (2.02–2.03) | 97% |
| 1000 | 20,000 | 68 | 20.00 | 7.78 (7.73–7.81) | 99% | 1.27 | 1.33 (1.33–1.33) | 95% |
| 1000 | 50,000 | 68 | 50.00 | 17.08 (17.07–17.11) | 100% | 3.18 | 2.34 (2.33–2.36) | 97% |
| 3000 | 20,000 | 118 | 60.00 | 17.16 (17.14–17.17) | 100% | 1.90 | 1.52 (1.50–1.52) | 95% |

With levels of detail, every one of these scenes is under the 2.78 ms the RTX 3080 has at factor 3 and a 50% share. Without them, none is.

**The answer.**

- **Not needed** while the triangles in view stay under the budget: up to about **400 assets of 10,000 triangles**, or 200 of 20,000. As an estimate, that is 2.00 ms on the RTX 3080 for 300 assets, about 6 ms on a GTX 1660.
- **Needed beyond that.** 1,000 assets of 10,000 triangles is an estimated 13 ms on a GTX 1660, over the 8.3 ms share. With levels of detail it is an estimated 4 ms.
- **Cheaper shadows do part of the same job.** Most of what far triangles cost here is shadow passes. Two cascades, a shorter shadow distance, or no shadows from small far assets would each move the limit, at some cost in looks. That was measured only for the cascade count.
- The spec's provisional setting for the pit profile, "levels of detail off until measurement shows they are needed", **holds if the pit game shows a few hundred assets at once and fails if it shows a thousand**. This repo does not say which. A vertical pit seen across or downwards could show many.

What this did not measure: the switch between levels as the camera moves, which can be seen as a pop; the cost of making the levels; and Bevy's own `VisibilityRange`, which the earlier note describes. Here each far asset was simply given a smaller mesh.

## 8. Limits and unknowns

1. **No GTX 1660 was measured.** Every figure for it is the RTX 3080's multiplied by 3, and the factor's published range is 2.2 to 4.3. Triangle-bound load may scale differently from the tests the factor comes from.
2. **The scene is not the pit game.** Flat ground, 1 m rocks every 2 m, a fixed camera. Real scenes have terrain, large building pieces, small props, and views up and down the pit.
3. **One asset shape and one material.** No transparency, no second UV set, no emissive or occlusion textures. Triangles in a real asset are less even than a sphere grid's.
4. **Shadow passes are not timed by Bevy 0.19.1.** Their cost is known only as the difference between runs with and without shadows.
5. **Low frame times are CPU-bound on this machine.** Below about 1.6 ms the numbers describe a Ryzen 7 5800X, not the GPU. The target's CPU is not specified anywhere.
6. **Bevy's defaults were kept.** No depth prepass, no anisotropic filtering, 4-sample MSAA, no bloom or other effects. Each would change the fixed cost or the per-pixel cost.
7. **Block-compressed textures were random blocks.** Memory and frame time are real; how compressed textures look, and how they reach Bevy 0.19, is the spec's open decision and was not touched.
8. **Unexplained:** the 7% step between texture scenes that does not follow size; the 44% excess memory for uncompressed 4096 textures; what the empty window's 531 MiB is made of.
9. **Frame-time spikes during play** (loading an asset, compiling a shader) were excluded by the warm-up and are not measured.
10. **The scaling sources could not be read first-hand in full.** The figures in section 5 were gathered by a search of the public pages named; TechPowerUp, Tom's Hardware, TechSpot and Notebookcheck could not be fetched. Check them before the factor is relied on.

## What would replace these estimates

- Running the same command on a GTX 1660 or RX 5600 XT replaces every scaled figure with a measured one. The tool reads video memory through `nvidia-smi`, so on an AMD card the memory columns come out empty.
- The pit game's real numbers: assets in view, view distance, different assets loaded at once, shadow settings, and the share of the frame it gives to static assets.

## Method

The measurement was run twice in full on 2026-10-07; the committed files are the second run, made on commit `2da41dc` with a clean working tree. The tables in this note were produced from `summary.csv` and `memory.csv` by a script that is not in the repository; the straight lines are least-squares fits through the scenes where the GPU was at least 95% busy. The scaling figures were collected by a web search on the same day and are quoted as that search reported them. The pit game's facts come from `learn/MISSION.md`, except the field of view, which was read from a look test in the `pit` repository. Nothing was taken from the `first-attempt` tag.
