# Fur and hair in Rust and Bevy: what already exists

Researched 2026-10-08. Every repository, crate page and source file cited below was read on that date. Kiln pins Bevy 0.19.1; Bevy 0.20.0-rc.2 was published on 2026-09-28, so the version each crate supports will move again within weeks.

This is a research note. It surveys existing Rust code for drawing and moving fur or hair in real time, and says how each piece would or would not serve the creature of [`fur-animation-trial.md`](fur-animation-trial.md): a body covered in individual hairs that sway in wind and when the body moves, and that can stiffen into long hard spikes. It adds no stage, check or glossary term to kiln. `learn/MISSION.md` keeps characters and animation out of scope until static assets are solved; this note does not change that.

**Almost nothing here was run.** Repositories were cloned and read as text. Two crates were compiled (not run) against Bevy 0.19.1 in a scratch project, [`rust-fur-crates-scratch/`](rust-fur-crates-scratch/). No example or binary of any candidate was started, and no picture was produced or looked at.

## The question

Is there a Rust crate or a Rust/Bevy project that renders and animates fur or hair in real time, or a part of that job, well enough that the owner should use it in place of writing strand fur by hand?

## How to read this

- **Fact** (the default) means the project's own repository, `Cargo.toml`, source code or crates.io record says so. Version numbers and dates are from those, not from a README's compatibility table.
- **Source** means the statement was read in the code. Where code and README differ, the code is given.
- **Claim** means the project's README says so and nothing here checked it.
- **Compiled here** means `cargo check` finished without error in the scratch project against `bevy = "=0.19.1"` with kiln's `"3d"` feature. It says the crate builds. It says nothing about whether it works.
- **Inference** means this note's reasoning. Every "would it serve this creature" verdict and every estimate of porting work is inference.
- **Evidence grades** for whether a thing works: *demonstrated in repo* (pictures or video are in the repository; they were not opened here, only seen to exist), *claimed* (text only), *unknown*.
- **A failed search is a gap in the search, not proof of absence.** The searches run are listed under Method.
- Kiln's own words are used as `CONTEXT.md` defines them.

### Terms used here

[`fur-animation-trial.md`](fur-animation-trial.md) defines skeleton, bone, skin weights, clip, morph target, vertex shader and instancing. Terms added here:

- **Strand:** one hair, stored as a short chain of points from root to tip. **Strand rendering** draws every hair as its own thin geometry.
- **Groom:** the whole set of strands on a character, with their lengths and directions. Blender calls the object that holds one **Curves** (older files: a **particle hair** system).
- **Shell texturing:** drawing the body's surface many times, each copy pushed a little further out and showing only dots of a noise texture, so the stacked layers read as hairs. Cheap to write; the hairs are not separate things and cannot be bent one by one.
- **Fins:** extra upright strips added along the silhouette to hide the layered look of shells seen from the side. "Shell and fin" is the two together.
- **Hair cards:** flat strips of triangles, each textured with a picture of several hairs. The usual way games draw human hair.
- **Ribbon:** one strand drawn as a narrow strip that turns to face the camera. A **tube** is the same strand with a round cross-section.
- **Compute shader:** a program the graphics card runs that is not tied to drawing: it reads and writes plain buffers of numbers. Used to simulate, or to build geometry, on the graphics card.
- **Software rasterizer** (as used by two projects below): a compute shader that decides by itself which pixels each hair covers, in place of the graphics card's normal triangle drawing. It handles hairs thinner than a pixel better and needs graphics-card features that are not available everywhere.
- **Verlet integration:** a simple way to move a point under forces by remembering where it was last frame: the next place is the current place plus (current minus previous) plus the forces. A chain of such points held at fixed distances behaves like a rope or a hair.
- **Position-based dynamics (PBD, and its refinement XPBD):** simulate by moving points and then repeatedly correcting their positions until the rules hold (this link has this length, this point is outside that ball).
- **Spring bone** (also **jiggle bone**, **dynamic bone**, **secondary motion**): a chain of skeleton bones that is not animated by a clip but simulated each frame, usually with Verlet, so a tail, an ear or a lock of hair lags and swings behind the body. The mesh follows the bones through its ordinary skin weights.
- **Wind field:** a formula or a scrolling noise texture that gives a wind direction and strength at every place and time. A vertex shader samples it to bend each blade or hair.
- **Vertex animation texture (VAT):** a motion recorded in an authoring tool and stored as a picture, one row per frame and one pixel per vertex; a vertex shader plays it back.
- **Material extension:** Bevy's way to add your own vertex or pixel shader to its standard material and keep its lighting and shadows (`MaterialExtension`).
- **MSAA, TAA, alpha to coverage:** ways to smooth jagged edges. MSAA samples each pixel several times at geometry edges. TAA blends each frame with earlier ones. Alpha to coverage turns partial transparency into "this many of the MSAA samples", which smooths thin things without sorting them.
- **Order-independent transparency (OIT):** drawing see-through things correctly without sorting them back to front.

## Summary

### Is there something to use?

**No crate does the job, and none does the central part of it.** Nothing was found, on crates.io or as a repository, that draws a body's worth of separate hairs in Bevy 0.19, moves them with wind and with the body, and lets a game drive each hair's stiffness. There is no fur or hair crate on crates.io at all: the searches for fur, hair, strand, groom and shell texturing returned no rendering crate, and the Bevy Assets listing has none.

What does exist, closest first:

- **Three hair or fur renderers for Bevy, all one-person repositories, none published as a crate.** `MrInformatic/bevy-fur` (MIT, Bevy 0.18, two commits) is a demonstration that builds tufts from a mesh's triangles in a compute shader; it ignores the entity's transform, has no lighting and no wind. `mate-h/bevy_hair` (Bevy 0.19.1, three days old) and `RostigerDagmer/bevy_strand_rasterizer` (Bevy 0.19) are research-grade software rasterizers for static human grooms; neither has a licence file a sold game could rely on, and neither moves the hair.
- **One maintained wind system for instanced blades:** `bevy_feronia` with its instancing crate `bevy_eidolon`. Its wind shader (layered noise, an S-shaped bend, a bob, a twist) is the best worked example found of the technique the prototype uses. The released `bevy_feronia` 0.8.4 needs Bevy 0.18; the Bevy 0.19 port is on its `dev` branch, unreleased. It scatters things on terrain and has no notion of a moving or skinned body (its own open issue #28 asks for that).
- **One maintained spring-bone implementation:** `bevy_vrm1` 0.10.0 (Bevy 0.19, compiled here). It simulates chains of skeleton bones with Verlet integration, as the VRM avatar format specifies. That suits a tail, ears or a few thick tufts with bones in them. It is not a way to move thousands of hairs.
- **One way to bring a groom authored in Blender into Bevy 0.19.1:** `openusd-rs/bevy_openusd` reads USD curves and draws them as ribbons with its own strand material. Blender 5.2's glTF exporter does not export hair at all (source); its USD and Alembic exporters do.
- **Outside Bevy:** a complete port of AMD's TressFX hair simulation and rendering to Rust on Vulkan (`Scthe/Rust-Vulkan-TressFX`, MIT, last commit 2024-01-14), as a standalone program, not a library; and a handful of shell-texturing toys.

### What would still have to be written by hand

Whichever of these is borrowed from, the following has no ready-made answer (inference from the survey):

- Growing hairs on this creature's surface and giving each one its data (root, direction, length, colour).
- Making hairs follow a **skinned** body. No candidate does it. Bevy's issue asking for an example of skinning inside a custom vertex shader (#13988) has been open since 2024-06-23.
- The stiffen-into-spikes change, per hair.
- Lag behind the body's movement. The only strand simulations found are for a few thick strands on the CPU (`bevy_carnage::viscera`), for cloth sheets on the graphics card (`bevy_softbody`), or are six Bevy versions old (`Erizeez/realtime_hair_wgpu`).

### Recommendation in one line

Keep writing it by hand, as the prototype in `fur-animation-trial/bevy_probe/` does; borrow the wind shader's ideas from `bevy_feronia` and the thin-hair coverage trick from `bevy_openusd`'s strand material; and consider `bevy_vrm1`'s spring bones only for the tail. The reasoning is in the Recommendation section and is inference.

## The candidates

"Bevy" is the version the crate's own `Cargo.toml` asks for. "Last activity" is the last commit, or the last release where the crate is published. "Serves this creature" is inference.

| Name | Technique | Renders / simulates | Bevy | Last activity | Licence | Serves this creature |
|---|---|---|---|---|---|---|
| `MrInformatic/bevy-fur` | Compute shader turns each triangle into a tuft or shell layers | Renders; a fixed sway | 0.18 | 2026-03-28 (2 commits) | MIT | No: demonstration only |
| `mate-h/bevy_hair` | Compute-shader software rasterizer for strands | Renders | 0.19.1 | 2026-10-06 (11 commits) | `MIT OR Apache-2.0` in `Cargo.toml`; no licence file | No: static human groom, special GPU features |
| `RostigerDagmer/bevy_strand_rasterizer` | Compute-shader software rasterizer for strands | Renders; simulation is a stub | 0.19 | 2026-09-14 | None | No: no licence, missing local dependencies |
| `Erizeez/realtime_hair_wgpu` | Elastic-rod strand simulation, instanced drawing | Both | 0.13.2 | 2024-07-12 | None | No: stale, no licence |
| `openusd-rs/bevy_openusd` (`usd_bevy`) | Reads USD curves; ribbons through a material extension | Renders | 0.19.1 | 2026-10-08 | MIT | Part: a route for a Blender groom; static |
| `bevy_symbios_avatar` 0.12.0 | Procedural hair cards on human heads | Renders | 0.19 | 2026-10-07 | MIT | No: human avatars only |
| `bevy_feronia` 0.8.4 | Wind bending in a vertex shader; scattering on terrain | Renders | 0.18 released; 0.19 on `dev` | 2026-08-20 | MIT OR Apache-2.0 | Part: the wind technique |
| `bevy_eidolon` 0.5.0 | GPU-driven instanced material | Renders | 0.19 (compiled here) | 2026-08-19 | MIT OR Apache-2.0 | Part: instancing; no transparency |
| `pavlov-net/bevy_meadow` | Grass built and culled in compute shaders | Renders | Bevy `main` by git | 2026-10-06 | MIT | No: not on 0.19.1; terrain grass |
| `julien-blanchon/saddle-rendering-grass` | Vertex-shader wind and an interaction map | Renders | 0.18 | 2026-04-09 | MIT-0 | Part: the interaction idea |
| `warbler_grass` 0.6.1 | Instanced grass | Renders | 0.13 | 2024-06-21 | MIT OR Apache-2.0 | No: stale |
| `bevy_procedural_grass` 0.2.0 | Instanced grass with wind | Renders | 0.12.1 | 2024-07-22 | MIT OR Apache-2.0 | No: stale |
| `bevy_open_vat` 0.19.0 | Vertex animation textures | Plays baked motion | 0.19 | 2026-06-21 | MIT OR Apache-2.0 | Part: only for motion baked in Blender |
| `bevy_vrm1` 0.10.0 | Spring bones (Verlet) on skeleton chains | Simulates | 0.19 (compiled here) | 2026-10-03 | MIT OR Apache-2.0 | Part: tail or tufts with bones |
| `bevy_vrm` 0.4.0 | Spring bones for VRM avatars | Simulates | 0.19.0 | 2026-07-28 | MIT OR Apache-2.0 | Part: as above |
| `bevy_verlet` 0.10.0 | Verlet points and sticks, one entity per point | Simulates | 0.17 released; 0.18 in repo | 2026-05-04 | MIT | No: behind, and one entity per point |
| `bevy_silk` 0.10.0 | Verlet cloth with wind | Simulates | 0.17 | 2025-12-08 | MIT | No: cloth, behind |
| `bevy_softbody` 0.1.0 | XPBD cloth in compute shaders | Both | 0.19.0 | 2026-07-23 | MIT | No: cloth sheets only |
| `bevy_carnage` 0.5.0 (`viscera`) | XPBD strands on the CPU | Simulates; builds tube meshes | 0.19.0 | 2026-09-04 | MIT OR Apache-2.0 | No: a few thick strands; self-labelled unaudited |
| `avian3d` 0.7.0 | Physics engine; chains of bodies and joints | Simulates | 0.19.0 | 2026-06-20 | MIT OR Apache-2.0 | Part: a tail; not hairs |
| `Scthe/Rust-Vulkan-TressFX` | TressFX port: strand simulation and rendering | Both | none (Vulkan through `ash`) | 2024-01-14 | MIT | No: a program, not a library; a reference |
| `gre-v-el/Shell-Texturing` | Shell texturing with wind and motion response | Both | none (macroquad) | 2023-11-13 | None | No: no licence; a reference |
| `ogawa-rs` 0.4.0 | Reads Alembic files, curves partly | File reader | none | 2025-04-06 | MIT OR Apache-2.0 | Part: a route for a Blender groom |
| `openusd` 0.7.0 | Reads USD files, curves included | File reader | none | 2026-09-05 | MIT | Part: a route for a Blender groom |

## 1. Fur or hair rendering for Bevy

### `MrInformatic/bevy-fur`

- **What it is.** A package named `bevy_fur`, version 0.1.0, described as "A real-time fur rendering library for Bevy, demonstrating four geometry-expansion techniques". Not on crates.io. About 1,180 lines, of which 440 are shaders. Dependencies: `bevy = "0.18"` (the lock file has 0.18.1) and `bytemuck`.
- **Technique (source).** The mesh's triangles are copied into a buffer on the graphics card. Each frame a compute shader writes new triangles for every input triangle: 75, 21, 9 or 279 vertices depending on the mode (`src/mode.rs`). The four modes are named "layer shells", "edge ridges", "centre cone" and "animated fur" in the README. The shader comments say they are ports of geometry shaders (`fur_compute_4.wgsl`: "GPU port of Fur_gs_4.glsl"). Mode 4 builds one pointed tuft of 16 segments over each triangle and swings it with a cosine of the clock.
- **What it does not do (source).** The drawing shader multiplies the stored positions by the camera matrix only, so the entity's position, rotation and scale are ignored: the fur stays at the mesh's own origin. There is no lighting: the colour written is the surface normal times a brightness. There is no skinning, no wind direction, no response to movement. Length (0.5) and every other setting is a constant in the shader. One tuft per triangle is not one hair per root.
- **Bevy 0.19.** It would not build. It wires its two passes in with `add_render_graph_node`, `ViewNodeRunner` and `add_render_graph_edge`. Bevy 0.19.1's `bevy_render` has no `render_graph` module (checked in the local source; `Core3d` is a schedule there). The port is to rewrite that wiring; the shaders would carry over (inference).
- **Maintenance.** Created 2026-03-28; two commits, both that day; one contributor; 1 star; 0 issues.
- **Licence.** MIT (file present). The example model `Fur.glb` has no stated terms.
- **Evidence.** The README has no picture. One example, not run. Grade: claimed.
- **Per-strand control, wind, moving body:** no, no, no.

### `mate-h/bevy_hair`

- **What it is.** "Real-time strand hair with deferred software rasterization on hair meshes", an implementation of a 2026 paper (Lipp, Jarabo, Wimmer and Bode, cited in its README). About 6,200 lines. `bevy = { version = "0.19.1", features = ["3d"] }`, `publish = false`.
- **Technique (claim, with the module list as support).** Strands are baked into bundles the paper calls hair meshes; a compute shader generates the strands, rasterizes them into its own buffer, shades them with a hair lighting model and a 16-layer opacity map for self-shadowing, and filters the result.
- **What it needs.** The README: "Native wgpu is required", with 64-bit integers and atomic operations on them in shaders (`SHADER_INT64`, `SHADER_INT64_ATOMIC_MIN_MAX`) and subgroup operations. "Browser WebGPU is out of scope." Whether the development machine's card offers these was not checked.
- **What it does not do (source).** The groom is rigid: the render code reads the entity's `GlobalTransform` and nothing else. A search of the source for wind, skin, simulation and animation found nothing. Its input is Cem Yuksel's `.hair` file format, a research format for human hairstyles.
- **Maintenance.** Created 2026-10-05, last commit 2026-10-06, 11 commits, one contributor, 0 stars. It is three days old.
- **Licence.** `Cargo.toml` says `MIT OR Apache-2.0`. The repository has no licence file and GitHub reports none. The 92 MB of hair models in `assets/hair/` are Cem Yuksel's and carry their own terms; the README says "Public material that shows them should link that page".
- **Evidence.** One picture in the repository (`assets/groom.webp`). Grade: demonstrated in repo, for a static human groom.
- **Per-strand control, wind, moving body:** no, no, rigid only.

### `RostigerDagmer/bevy_strand_rasterizer`

- **What it is.** A Bevy plugin its README titles "Fiber": "a compute-based software rasterizer for strand geometry". About 16,700 lines. `bevy = { version = "0.19", features = ["experimental_pbr_pcss"] }`, `wgpu = "29.0.4"`.
- **It cannot be built from the repository alone (source).** `Cargo.toml` depends on `../bevy_gpu_paging_allocator` and `../bevy_vsms` by path, and its examples on `../bevy_dson`; none is in the repository.
- **Simulation is a stub (source).** `src/pipelines/sim.rs` declares one buffer binding followed by `// TODO`, and loads a `strand_simulation.wgsl` that is not among the shaders in `src/shaders/`.
- **Licence.** None. Without one, nobody else may use the code. The repository also holds two hair files in Daz Studio's format, one named `dForce Pixie Cut_708408.dsf`; their terms are not stated and Daz content is normally sold.
- **Maintenance.** Created 2025-03-29; 161 commits; last 2026-09-14; one contributor; 0 stars.
- **Evidence.** Five screenshots in the repository. Grade: demonstrated in repo.
- **Useful part.** `tools/alembic_to_strands.py` converts Alembic hair curves to the project's own strand file. It shows one person chose Alembic as the way to get a groom out of an authoring tool.

### `Erizeez/realtime_hair_wgpu`

A Bevy 0.13.2 program of about 2,260 lines with a hair simulation whose folders are named `der` with `stretch`, `bend` and `twist` methods (discrete elastic rods, a physically based model of a bending, twisting strand) and an instanced-mesh plugin to draw it. The README holds only setup steps. 34 commits, the last on 2024-07-12; no licence. Six Bevy versions behind. Grade: unknown.

### `openusd-rs/bevy_openusd`

Covered in section 7, since its place is the authoring route. For this section: its `usd_bevy` crate has a strand material (`route/strand_material.rs`, 122 lines, plus two shaders of 161 lines) written as a material extension for Bevy 0.19.1. Source comment: each point of a strand's centre line carries a pair of vertices that the vertex shader spreads apart by the strand's width, facing the view; "A strand narrower than a pixel is drawn one pixel wide, and each pixel sample keeps it with a probability equal to its projected width". That is a compact answer to thin hairs flickering, in the same Bevy version kiln pins, under the MIT licence.

### `bevy_symbios_avatar` and `symbios-avatar`

Procedural human avatars. Hair is "five regions of the head" in two families, one of them flat cards "each cut out of one shared strand mask so its end frays into strands", coloured by vertex colour. Bevy 0.19, MIT, 0.12.0 released 2026-10-07, 428 downloads, one author. It grows hair on a human head it built itself; nothing in its README describes fur on an arbitrary mesh or hair that moves. Not read beyond the README.

### Not found

- Any crate or repository doing shell texturing in Bevy. `bevy_eidolon`'s README says the material "could be used for fur", as a possibility, not a feature.
- Any hair-card tool for Bevy other than the avatar crate above.
- Anything in Bevy's own repository: no fur, hair or grass example among the examples of tag `v0.19.1`, and the only match for "hair" in `bevy_pbr`'s source is a comment on the anisotropy setting of the standard material.

## 2. Grass, foliage and wind for Bevy

A blade of grass and a hair are the same problem at different sizes: a thin strip fixed at its root, bent by wind in the vertex shader. What differs is the ground. Grass stands on terrain that does not move; fur stands on a body that walks and bends.

### `bevy_feronia` and `bevy_eidolon`

- **Versions.** `bevy_feronia` 0.8.4 on crates.io (released 2026-06-22) depends on the Bevy 0.18 crates and on `bevy_eidolon` 0.4.1. The repository's `dev` branch asks for Bevy 0.19.0 and `bevy_eidolon` 0.5.0; its last commits (2026-08-20) are "Update to bevy 0.19 (#104)" and "chore!: bump to 0.9.0 / bevy 0.19", and a pull request "chore: release v0.8.5" has been open since 2026-08-17. So the Bevy 0.19 version exists and is not released. `bevy_eidolon` 0.5.0 (2026-08-19) is released for Bevy 0.19 and was **compiled here**.
- **Technique (source).** The wind is a struct of twelve settings (direction, strength, noise scale, scroll speed, "micro" strength, an S-curve's speed, strength and frequency, a "bop" speed and strength, a twist) and a noise texture. The vertex shader samples the noise at the instance's place, bends the blade along a curve, adds small detail and recomputes the normal. The header of `src/wind/displace.wgsl` credits the method to the talk on procedural grass in "Ghost of Tsushima". It is offered two ways: as an extension of Bevy's standard material (`ExtendedWindAffectedMaterial`) and as an instanced material built on `bevy_eidolon`.
- **`bevy_eidolon`** is the instancing part alone. Its README: for "Drawing a lot of instances (millions) that require GPU-driven rendering with no transparency/alpha masking".
- **What it does not do.** Nothing bends a blade because a body pushed it or moved: issue #28, "Allow Physics based entites to affect displacement and vice versa / skeletons", is open since 2025-11-03. The crate is built round scattering items over a landscape with a height map. Wind settings are per material, not per blade (issue #9, "Individual tweaking of wind/shader properties on foliage", open).
- **Maintenance.** 275 commits, 3 contributors, 85 stars, 31 open issues, 3,010 downloads. The README: "In the current stage this is mostly for tinkerers and learners" and "I wouldn't personally use this in production quite yet".
- **Licence.** Code MIT OR Apache-2.0. The example assets are not all free: `assets/LICENSE` lists "Foliage assets by Graswald - Free License non commercial" and three tree packs under "CC Attribution". The README says the grass assets may be copied. None of the assets would be needed to borrow the shader.
- **Size.** About 12,300 lines; optional `avian3d` 0.7.0.
- **Evidence.** A screenshot linked from the README and an examples list. Grade: demonstrated in repo.
- **Per-strand control, wind, moving body:** per material only; yes; no.

### `pavlov-net/bevy_meadow`

"GPU-driven, patch-based grass for Bevy": a compute pass builds, culls and thins every blade each frame, with wind as "a shared gust direction ... plus dynamics -- speed, gustiness, and traveling gust crests". MIT; 18 commits; last 2026-10-06; 2 contributors; 6 stars. Its `Cargo.toml` depends on Bevy by git with no version: "`bevy_meadow` tracks Bevy's `main`, so it depends on Bevy by git and is not published to crates.io". It therefore does not fit a project pinned to 0.19.1 (inference; not tried). Terrain grass only. Grade: claimed.

### `julien-blanchon/saddle-rendering-grass`

Bevy 0.18, MIT-0, 16 commits, last 2026-04-09, one author, 0 stars. Wind in the vertex shader, and one idea worth noting: an **interaction map**, "World-space CPU texture that actors stamp into; sampled by shader per-vertex", so any number of moving things can bend or flatten grass and leave a trail that recovers. On a creature the same idea would be a small texture over the body's surface that a hand or a hit stamps into (inference). Grade: claimed.

### Older grass crates

- `warbler_grass` 0.6.1: Bevy 0.13, released 2024-06-21, 41,632 downloads, 140 stars, 11 open issues. The most used, and six versions behind.
- `bevy_procedural_grass` 0.2.0: Bevy 0.12.1, last commit 2024-07-22. Wind is a listed feature; "Grass Interaction, allow grass to move out of the way of other entites" is on its to-do list.
- `frosty_grass` 0.0.1: Bevy 0.12.1, 2024-01-31, "rendering grass on 3D meshes using GPU instancing". The only one that names arbitrary meshes; one release, then nothing.
- `bevy_foliage_tool` 0.16.2: Bevy 0.16, a painting tool.

`bevy_wind_waker_shader` appears in every search for "wind"; it is a cartoon lighting shader named after a game, and has nothing to do with wind.

### `bevy_open_vat`

Vertex animation textures for Bevy 0.19 (0.19.0, 2026-06-21, MIT OR Apache-2.0, 146 downloads, one author). It plays a motion baked in Blender with the OpenVAT add-on: "Decodes position and normal offsets directly in the vertex shader". A hair simulation run in Blender could be baked and replayed this way (inference), but a recording cannot react to the game: no wind that changes, no lag behind a movement the player chose. It fits a fixed bristle animation, not live fur.

## 3. Strand and secondary-motion simulation

### Spring bones: `bevy_vrm1`, `bevy_vrm`, `vrm-runtime`

VRM is a file format for humanoid avatars, built on glTF. Its `VRMC_springBone` extension marks chains of bones (hair locks, skirts, tails) to be simulated.

- **`bevy_vrm1` 0.10.0** (released 2026-10-03; `bevy = "0.19"`; MIT OR Apache-2.0; 38 stars, 10 contributors, 7,304 downloads, 2 open issues). **Compiled here** against 0.19.1. The spring-bone code is 633 lines. Source (`src/vrm/spring_bone/update.rs`): for each joint, the next tail position is the current one plus inertia (current minus previous, damped by a drag number), plus a pull back to the rest direction (stiffness), plus gravity; the result is put back at the bone's length from its head, pushed out of any collider, and turned into the bone's rotation. That is Verlet integration with a length constraint. Settings per joint: `drag_force`, `gravity_dir`, `gravity_power`, `hit_radius`, `stiffness`.
- **Can it be used without a VRM file?** The crate is written to load VRM humanoids, and its setup is driven by the file. `SpringRoot` and `SpringJointProps` are public components with public fields, and the system that prepares the state runs for any newly added `SpringRoot` (source). So a game could probably add them to its own bone chains by hand. That is inference from reading; it was not tried, and the crate documents no such use.
- **Stiffening.** `stiffness` is a plain number per joint that a game may change each frame, so "soft to rigid" is expressible on a chain (inference).
- **Wind.** Only through `gravity_dir` and `gravity_power`, a constant push per joint.
- **`bevy_vrm` 0.4.0** (2026-07-28; Bevy 0.19.0; MIT OR Apache-2.0; 66 stars, 7 contributors, 9 open issues) has its own `spring_bones.rs`. Not read in detail.
- **`vrm-runtime` 0.1.0** (2026-08-18; depends on `glam` 0.29 and no engine; one release) offers "SpringBone simulation in independent" modules. One day of history. Not read in detail.
- **Limits for fur (inference).** Every simulated joint is a Bevy entity and a bone. Bevy allows 256 joints per skin, and `fur-animation-trial.md` counts 27 body bones. That leaves room for a tail of five bones and perhaps a few dozen tufts, not for a coat.
- The `bevy_vrm1` repository holds `CLAUDE.md` and `AGENTS.md`, files of instructions for AI coding agents working on that project. They were not followed.

No crate named for jiggle bones, dynamic bones or secondary motion was found on crates.io or GitHub.

### Verlet and cloth: `bevy_verlet`, `bevy_silk`, `bevy_softbody`

- **`bevy_verlet`**: "Simple Verlet points and sticks". crates.io has 0.10.0 (2025-12-08) for Bevy 0.17; the repository's `Cargo.toml` asks for 0.18 (last commit 2026-05-04). MIT. Every point is an entity with a `Transform`. For 30,000 hairs of four points that is 120,000 entities moved on the CPU each frame; not designed for it (inference).
- **`bevy_silk`** 0.10.0: cloth on Bevy 0.17 with `Wind::Constant` and `Wind::SinWave` forces and "experimental" collisions with Rapier or Avian. MIT, 118 stars. Cloth, and two versions behind.
- **`bevy_softbody`** 0.1.0 (2026-07-14; Bevy 0.19.0; MIT; 28 downloads; same author as `bevy_hair`): "GPU cloth simulation ... using WebGPU compute shaders", XPBD, with "Extended PBR material that reads simulated positions from GPU buffers". It simulates a sheet. It is the nearest working example in Bevy 0.19 of the pattern a strand simulation on the graphics card would follow: a compute shader moves points, a material extension reads them (inference).

### XPBD strands: `bevy_carnage::viscera`

`bevy_viscera` was archived on 2026-09-04 and became a module of `bevy_carnage` (0.5.0, 2026-09-04, Bevy 0.19.0, MIT OR Apache-2.0, 119 downloads). It simulates strands as chains solved by XPBD on the CPU, deterministic, and returns a tube mesh; the solver functions take plain data and do not need Bevy's renderer. It is built for a handful of thick strands (it is part of a gore system). Its README opens: "Vibe Coded — written by an AI agent working from a human's direction ... it has had no line-by-line human audit. Read it before you trust it." Not read beyond the README and manifest.

### Physics engines: Avian and Rapier

- **`avian3d` 0.7.0** (2026-06-20; Bevy 0.19.0; MIT OR Apache-2.0; 389,461 downloads). Its `chain_3d` example builds a chain of 100 spheres joined by `SphericalJoint` and sets `SubstepCount(80)` to keep it stable. Every link is a rigid body.
- **`bevy_rapier3d` 0.36.0** (2026-08-08; Bevy 0.19.0; Apache-2.0). `rapier-rope` 0.1.0 (2026-10-01, MIT, 35 downloads) builds ropes for Rapier; not opened.
- **For hair (inference).** A physics engine's chain is right for one tail, where collision with the world matters. It is the wrong tool for a coat: thousands of bodies and joints, each solved in full, for something that only has to look plausible. No project was found that uses Avian or Rapier joints for hair.

## 4. Engine-independent Rust

### `Scthe/Rust-Vulkan-TressFX`

"An implementation of AMD's TressFX hair rendering and simulation technology using Rust and Vulkan." TressFX is AMD's open-source hair system, used in the Tomb Raider games. This port has both halves: the simulation (the README shows a video captioned "TressFX simulation: adjusting the wind strength") and rendering with per-pixel linked lists for transparency and Kajiya-Kay shading. MIT. 169 commits, the last on 2024-01-14; one author; 5 stars. It talks to Vulkan directly through `ash` 0.37, needs the `glslc` shader compiler installed, and is a program with its own window, not a library. Grade: demonstrated in repo (videos linked from the README).

Its value here is as a readable Rust reference for how a real strand simulation is laid out (inference). Bringing it into Bevy would mean rewriting every shader from GLSL to WGSL and replacing all of the Vulkan code.

### Shell-texturing toys

- `gre-v-el/Shell-Texturing`: a program on macroquad (a small game library) with "Fur physics in response to mesh movement", wind, presets and GIFs. No licence; last commit 2023-11-13.
- `rowanfr/shell-texturing` (wgpu 0.18, two commits), `CmrCrabs/fur-shader` (wgpu 0.18, archived, shaders written in Rust and compiled by a `build.rs`), `pengiie/shell-texturing` (Vulkan), `Klohger/shell-texturing`: none has a licence; all date from late 2023 or 2024, and one says it follows a video on the technique.

They confirm shell texturing is a weekend-sized job. None is a library.

### File readers for grooms

- **`ogawa-rs`** 0.4.0 (crates.io 2023-04-14; last commit 2025-04-06; MIT OR Apache-2.0; 8 contributors; 10,231 downloads). "a work in progress crate for loading Ogawa Alembic Cache files in Rust. It currently only supports basic parsing of files and partially reading curves schemas." Alembic is a film-industry file format for baked geometry; curves are how it stores hair. The crate is from Traverse Research, who also reserved the crate names `breda-hair`, `breda-hair-asset`, `breda-hair-runtime` and `breda-pipeline-hair` on 2022-10-22; each is an empty version 0.0.0 described as "Reserved". Nothing was published under them.
- **`openusd`** 0.7.0 (2026-09-05; MIT; 26,038 downloads) is a USD reader written in Rust, with `openusd-schemas` 0.7.0 giving typed access to `BasisCurves`, the USD type for hair.
- `usd` 0.0.9 (2020) and `alembic` 0.1.0 (2020, "placeholder") are abandoned bindings to the C++ libraries.

### Not found

- A Rust binding or port of NVIDIA HairWorks. A crates.io search for "tressfx" and for "hairworks" returned nothing.
- A hair-simulation library as a crate.
- A reader for Cem Yuksel's `.hair` format as a crate (`bevy_hair` has one inside it).
- Any glTF extension for hair, curves or strands: the Khronos extension registry lists none (its index was searched for hair, curve, strand and spline).

Seen in search results and not opened: `threers`, `nightshade-renderer`, `oxihuman-physics`, `gizmo-physics-soft`, and `viewport-lib-wind` 0.1.0, a wind-field plugin for another viewer library whose licence is `GPL-3.0-only`, which a sold game could not link without publishing its own source.

## 5. What Bevy 0.19.1 gives to build on

Read in the local source under `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/`. Everything in this section is available with the `"3d"` feature `crates/asset_view` already builds: `"3d"` includes `bevy_pbr`, `bevy_anti_alias`, `bevy_post_process`, `bevy_gltf`, `morph` and `gltf_animation` (`bevy-0.19.1/Cargo.toml`, lines 2605 to 2633).

| Need | What Bevy has | Where | Caveat |
|---|---|---|---|
| A custom vertex shader that keeps Bevy's lighting | `MaterialExtension`: `vertex_shader`, `prepass_vertex_shader`, `specialize` | `bevy_pbr-0.19.1/src/extended_material.rs`; example `shader/extended_material.rs` | Issue #16970, "Need an example of a simple material extension as a vertex shader", is open |
| Extra data per vertex (root, place along the hair, length) | `MeshVertexAttribute::new(name, id, format)` and `specialize` to map it to a shader input | example `shader_advanced/custom_vertex_attribute.rs` | The prototype and `bevy_openusd` both do this |
| Many copies of one mesh in one draw | Automatic batching and instancing for entities sharing a mesh and a material | `bevy_pbr-0.19.1/src/render/mesh.rs`; example `shader/automatic_instancing.rs` | One entity per copy. Skinned meshes are kept out of batches where skins use uniform buffers (`no_automatic_skin_batching`) |
| One number per instance for the shader | `MeshTag(u32)`, read in WGSL with `get_tag` | `bevy_mesh-0.19.1/src/components.rs`, `mesh_functions.wgsl` | An index into your own buffer; no more than that |
| Instancing by hand | A custom draw with an instance buffer | example `shader_advanced/custom_shader_instancing.rs` | The example calls itself "intended for advanced users" |
| Compute shaders | Pipelines and buffers; reading results back | examples `shader/compute_shader_game_of_life.rs`, `shader_advanced/compute_mesh.rs`, `shader/gpu_readback.rs`, `shader/storage_buffer.rs` | No render graph: `bevy_render` 0.19.1 has no `render_graph` module, so code written for 0.18's graph nodes must be rewired |
| Skinning in a custom vertex shader | `bevy_pbr::skinning::skin_model`, `bevy_pbr::morph`; the standard shader applies morph, then skin | `bevy_pbr-0.19.1/src/render/mesh.wgsl`, `skinning.wgsl`; example `animation/custom_skinned_mesh.rs` | Issue #13988, an example of "skinning and morph with custom vertex shaders", open since 2024-06-23. 256 joints per skin |
| Smoothing thin hairs | `Msaa` (default 4 samples); `AlphaMode::AlphaToCoverage`; `TemporalAntiAliasing`; SMAA, FXAA, sharpening | `bevy_render-0.19.1/src/view/mod.rs`, `bevy_material-0.19.1/src/alpha.rs`, `bevy_anti_alias-0.19.1/src/` | TAA "must also disable Msaa", needs motion vectors for everything drawn, and "does not work well with alpha-blended meshes" (source comments). Alpha to coverage "requires multisample antialiasing" |
| See-through hair without sorting | `OrderIndependentTransparencySettings` | `bevy_core_pipeline-0.19.1/src/oit/`; example `3d/order_independent_transparency.rs` | Costs memory per pixel; not needed if hairs are opaque |
| Hair-like highlights | `StandardMaterial::anisotropy_strength`, whose comment names hair as a use | `bevy_pbr-0.19.1/src/pbr_material.rs` | Stretches the highlight along one direction; not a hair lighting model |
| Reading lines and custom attributes from glTF | The loader reads `LINES` and `LINE_STRIP` primitives and attributes registered with `GltfPlugin::add_custom_vertex_attribute` | `bevy_gltf-0.19.1/src/loader/gltf_ext/mesh.rs`, `src/lib.rs`; example `gltf/custom_gltf_vertex_attribute.rs` | `EXT_mesh_gpu_instancing` is marked unsupported in the loader's own table (`src/lib.rs`, line 120) |

What Bevy does not have: any fur, hair, grass or wind feature, example or open proposal. Searches of its issues and discussions for fur, shell texturing, strand hair, spring bone and foliage wind found nothing on the subject; "Character Attachments" (#17114, open) is the nearest topic.

## 6. Other Rust engines

A pointer only. A code search of Fyrox's repository for "hair" matched user-interface files and nothing about rendering; for "grass", the terrain module and the changelog. No sign of a hair or fur system. Ambient's repository was searched for "fur" and rend3's for "hair", with no relevant match. Nothing was read beyond the search listings, so this is weak evidence.

## 7. Growing and authoring the hairs

There are two ways to get the hairs: grow them by code on the body's surface (what the prototype does), or comb a groom in Blender and carry it across.

### What Blender 5.2 exports

- **glTF: no hair.** The manual: "curves and other non-mesh data are not preserved, and must be converted to meshes prior to export". The exporter's source at tag `v5.2.2` (`io_scene_gltf2/blender/exp/nodes.py`) converts objects of type `CURVE`, `SURFACE` and `FONT` to meshes, and for any other object "`if blender_object.type not in ["MESH", "POINTCLOUD"]: return None`". A hair Curves object has type `CURVES`, which is in neither list, so it is written as an empty node (inference from that source; not run). A code search of the exporter for "hair" and for "particle" found nothing.
- **glTF can still carry strands that were turned into a mesh first.** The exporter has "Loose Edges: Export loose edges as lines", and "Attributes: Export Attributes with meshes, when the name starts with underscore". So a groom converted to a mesh of edges or ribbons in Blender (by a script through `tools/bl`, or Geometry Nodes), with attributes such as `_ROOT` or `_ALONG` per vertex, would export, and Bevy's loader reads both lines and such attributes (section 5). Nobody was found doing this; it is a route this note infers.
- **USD: hair as curves.** The manual lists "Hair (exported as curves, and limited to parent strands)" and adds "Only the parent strands are exported, and only with a constant color. No UV coordinates, and no information about the normals." Curves objects are exported as curves.
- **Alembic: hair as curves.** "Hair is exported as animated zero-width curves."

### Reading it in Rust

- **`openusd-rs/bevy_openusd`** (MIT; Bevy 0.19.1; 711 commits; last 2026-10-08; one contributor; 9 stars; not on crates.io). Its `usd_bevy` crate maps USD `BasisCurves` to line meshes or "opt-in width-aware tubes and ribbons" (`route/curves.rs`, 2,506 lines) and draws them with the strand material of section 1. The README shows a film studio's test scene with "the stoat's knitted sweater and fur ... as curves textured from UDIM tiles". Grade: demonstrated in repo (a picture). Costs: it must be taken by git; it requires replacing Bevy's own `bevy_asset` crate with the project's modified copy (`[patch.crates-io] bevy_asset = { git = ... }`); the checkout is 1.3 GB; and it is a whole scene system with a live editor, far more than a groom reader. The curves are static: a search of the curves code for skin, skeleton and wind found nothing.
- **`openusd`** by itself would read the curve points and leave drawing to the game.
- **`ogawa-rs`** reads Alembic curves "partially".

### Which way (inference)

For a creature that comes out of a generator as a mesh with no groom, growing hairs by code needs no extra file, no extra exporter and no hand work, and the hairs are built already knowing which point of the body they stand on. A Blender groom earns its cost when a person wants to comb the fur by hand. If that day comes, the glTF route with a mesh of strands keeps kiln on the one format it already measures and checks; USD brings a second format and a patched Bevy crate.

## 8. How the hand-built prototype compares

`fur-animation-trial.md` had no "Strand fur" section when this note was finished, so that section was not used. The prototype's source was read instead, without changing it: `fur-animation-trial/bevy_probe/src/bin/fur_strands.rs` (1,363 lines) and `fur_strands.wgsl` (304 lines) as they stood on 2026-10-08. What follows describes that snapshot and may be out of date.

What the prototype does, from its own comments: it grows points evenly over the body's surface, builds every hair as a short strip (four pieces for a fine hair, six for a guard hair) and puts all of them in one mesh. Each vertex carries its hair's root, the surface normal, its place along the hair, a combing direction and length, two random numbers, the time a "bristle wave" reaches it, a quill length, and a colour taken from the body. A vertex shader places every vertex each frame from a small block of numbers: wind direction and strength, a gust front crossing the world, two springs for how far the hair hangs behind the body's movement and two for its turning (computed on the CPU for the whole body, not per hair), and a bristle amount from 0 to 1. Hairs are kept at least 0.75 pixels wide. The same shader serves the shadow pass.

| | The prototype | Nearest existing thing | Difference |
|---|---|---|---|
| Hairs as geometry | Strips in one mesh, custom vertex attributes | `bevy_openusd`'s ribbons (same idea, same Bevy) | The same technique. The prototype grows its own hairs; `bevy_openusd` reads them from a file |
| Thin hairs | A least width in pixels | `bevy_openusd`: least width of one pixel, and each pixel sample kept with probability equal to the true width | The second half is worth borrowing: without it a coat of widened hairs looks denser than it is |
| Wind | Direction, strength and a travelling gust | `bevy_feronia`: scrolling noise texture, S-curve, bob, twist, normals recomputed | `bevy_feronia`'s is richer and its normal handling is worked out; the prototype's gust front has no counterpart there |
| Movement lag | Four springs for the whole body, on the CPU | `bevy_vrm1` spring bones (per bone chain); `bevy_softbody` (per point, on the graphics card, cloth) | The prototype's is the cheapest possible. Per-hair lag would need a compute shader in the manner of `bevy_softbody`. Nobody has it for hair on Bevy 0.19 |
| Spikes | A bristle amount with a wave across the body, per-hair quill length | Nothing | No candidate has any per-strand state a game can drive |
| Skinned body | Not seen in the snapshot (it uses the model's morph weights) | Nothing | No candidate has it either. `bevy_pbr::skinning::skin_model` is there to call |
| Drawing method | Bevy's ordinary triangles through a material | `bevy_hair` and the strand rasterizer: a compute-shader rasterizer | Theirs is built for a human head seen close, with a hundred thousand strands thinner than a pixel, and needs 64-bit atomics. For short fur on a creature seen from metres away it is the heavier answer to a problem the creature may not have |

In short: the prototype is the same family of technique as the best of what exists (strips, custom attributes, a wind shader), and it already contains the three things no existing project offers: growth on an arbitrary body, lag behind movement, and a per-hair spike state.

## Recommendation

All of this section is inference.

**Write it by hand. Do not adopt a crate.** The reasons, in order of weight:

1. **Nothing covers the middle of the job.** The parts that exist are the outside of it: a wind formula, an instancing material, a file reader, a bone simulation. Hairs on a moving body with a per-hair state is the part that would have to be written anyway, and it decides the data layout everything else must fit.
2. **Every candidate is one person's work.** Of the two hair renderers on Bevy 0.19, one was created three days ago and the other last changed on 2026-09-14; both have 0 stars and neither has a licence file. Bevy breaks its rendering interfaces every release (the render graph that `bevy-fur` was written against in March is gone in 0.19), and 0.20 is at its second release candidate. A dependency here is a port the owner would do alone, in code the owner did not write.
3. **The hand-written version is small.** `bevy_openusd`'s strand material is 283 lines; the prototype is about 1,700 with its test harness. That is within what one person and Claude can read and keep working across Bevy versions.

**Borrow, with the source open beside the prototype:**

- From `bevy_openusd` (`crates/usd_bevy/src/route/strand_material.wgsl`, `strand_functions.wgsl`; MIT): the coverage trick for hairs thinner than a pixel.
- From `bevy_feronia` (`src/wind/displace.wgsl`, `noise.wgsl`; MIT OR Apache-2.0): the layered wind and how it bends the normal with the blade.
- From `saddle-rendering-grass` (MIT-0): the interaction map, if something should ever press the fur down.
- From Bevy's own `skinning.wgsl`: `skin_model`, when the creature gets a skeleton. Each hair's vertices would carry the joint indices and weights of the body point they grew on.

**What to try first:** the skinned body, because it is the one requirement no source shows working and the one most likely to force a change in how hairs are stored. Give the prototype's hair mesh the joint attributes of the body point under each root, call `skin_model` in its vertex shader, and look at the hairs on the bent poses `fur-animation-trial.md` already has (prototype E).

**Where a crate could come in later:** `bevy_vrm1`'s spring bones for the tail, if the tail should swing by itself. It compiles against 0.19.1; whether its components work on a skeleton that is not a VRM humanoid is the first thing to test. Its algorithm is about 230 lines and could be copied under its licence if the crate turns out too tied to VRM.

**Shell texturing is not recommended for this creature.** It cannot give separate hairs that become spikes, which is the requirement.

## What is unknown

- **Whether any of the three Bevy fur and hair renderers works.** None was run. `bevy_hair` was not even compiled, and whether the development machine's graphics card has the features it asks for was not checked.
- **Whether `bevy_vrm1`'s spring bones can be driven without a VRM file.** Read from source as likely; untested.
- **Whether `bevy_feronia`'s `dev` branch builds against 0.19.1.** Its `Cargo.toml` asks for 0.19.0; it was not compiled.
- **Whether a hair Curves object really exports as an empty glTF node** from Blender 5.2.2. Read from the exporter's source; not run through `tools/bl`.
- **How Blender's USD export of a hair Curves object looks to `openusd`**, and whether `bevy_openusd` draws it. Not tried.
- **Frame cost of any of this.** No candidate publishes timings that were read here, and the prototype's `--bench` results were not available to this note.
- **How the prototype handles a skinned body.** Not seen in the snapshot read.
- **Projects that are not public or not indexed.** Bevy's Discord showcases were not searched; nothing from Discord was found through public pages.

## What could not be opened or verified

- **No picture or video in any repository was opened.** "Demonstrated in repo" means the files or links are there.
- **Web search found nothing useful.** Three searches returned no Rust or Bevy fur project that the direct searches had not already found, and one wrong lead (a procedural-texture crate, `alkyd`, with no fur feature in its description).
- **Bevy's release notes and migration guide for 0.19 were not read.** Statements about 0.19 are from the source of 0.19.1, and release dates from GitHub's release list.
- **GitHub's code search runs on default branches**, so "no match for hair in Blender's glTF exporter" is about Blender's main branch; the object-type lines quoted are from the file at tag `v5.2.2`.
- **Not read beyond README and manifest:** `bevy_vrm`, `vrm-runtime`, `bevy_carnage`, `bevy_symbios_avatar`, `bevy_meadow`, `saddle-rendering-grass`, `bevy_open_vat`, `bevy_softbody`, `bevy_silk`, `bevy_verlet`, `Erizeez/realtime_hair_wgpu`, `Scthe/Rust-Vulkan-TressFX` and the shell-texturing toys.
- **Not opened at all:** `rapier-rope`, `threers`, `nightshade-renderer`, `oxihuman-physics`, `gizmo-physics-soft`, `viewport-lib-wind`, `frosty_grass`'s repository, `pengiie/shell-texturing`, `Klohger/shell-texturing`, and lib.rs (crates.io was searched directly, which holds the same crates).
- **Contributor counts** are GitHub's, including anonymous commit authors, capped at 100. **Download counts** are crates.io's all-time figures on the day.
- **Licences were read from manifests and licence files, not audited.** Where a repository has none, that is what GitHub's record and the file listing show.
- **Other engines** were checked by code search only.

## Sources

Every item was read on 2026-10-08.

**Fur and hair for Bevy** (repository cloned at the commit given; source read)

- [`MrInformatic/bevy-fur`](https://github.com/MrInformatic/bevy-fur) at `ac523a0`: `README.md`, `Cargo.toml`, `Cargo.lock`, `LICENSE`, all of `src/`
- [`mate-h/bevy_hair`](https://github.com/mate-h/bevy_hair) at `ae65102`: `README.md`, `Cargo.toml`, `src/lib.rs`, `src/render/mod.rs`; the rest searched
- [`RostigerDagmer/bevy_strand_rasterizer`](https://github.com/RostigerDagmer/bevy_strand_rasterizer) at `c29665e`: `README.md`, `Cargo.toml`, `src/pipelines/sim.rs`, `tools/alembic_to_strands.py` (top); the rest searched
- [`Erizeez/realtime_hair_wgpu`](https://github.com/Erizeez/realtime_hair_wgpu): `README.md`, `Cargo.toml`, file listing
- [`openusd-rs/bevy_openusd`](https://github.com/openusd-rs/bevy_openusd): `README.md`, root and `crates/usd_bevy` `Cargo.toml`, `crates/usd_bevy/src/route/strand_material.rs`, top of `route/curves.rs`; the curves code searched
- [`TheJanusStream/bevy_symbios_avatar`](https://github.com/TheJanusStream/bevy_symbios_avatar) and [`symbios-avatar`](https://github.com/TheJanusStream/symbios-avatar): README sections on hair

**Grass, foliage, wind, baked motion**

- [`NicoZweifel/bevy_feronia`](https://github.com/NicoZweifel/bevy_feronia) (`dev` branch): `README.md`, `Cargo.toml`, `CHANGELOG.md`, `assets/LICENSE`, `src/wind/wind.wgsl`, `src/wind/displace.wgsl`, `src/extension/vertex.wgsl`; open issues and last commits through GitHub's API
- [`NicoZweifel/bevy_eidolon`](https://github.com/NicoZweifel/bevy_eidolon): `README.md` and `Cargo.toml` of the 0.5.0 crate file
- [`pavlov-net/bevy_meadow`](https://github.com/pavlov-net/bevy_meadow), [`julien-blanchon/saddle-rendering-grass`](https://github.com/julien-blanchon/saddle-rendering-grass), [`EmiOnGit/warbler_grass`](https://github.com/EmiOnGit/warbler_grass), [`jadedbay/bevy_procedural_grass`](https://github.com/jadedbay/bevy_procedural_grass), [`HK416/bevy_open_vat`](https://github.com/HK416/bevy_open_vat): `README.md` and `Cargo.toml`

**Simulation**

- [`not-elm/bevy_vrm1`](https://github.com/not-elm/bevy_vrm1): `README.md`, `Cargo.toml`, `src/vrm/spring_bone.rs`, `spring_bone/update.rs`, `spring_bone/initialize.rs`; the 0.10.0 crate file
- [`unavi-xyz/bevy_vrm`](https://github.com/unavi-xyz/bevy_vrm), [`nanowater/vrm-runtime-rs`](https://github.com/nanowater/vrm-runtime-rs), [`ManevilleF/bevy_verlet`](https://github.com/ManevilleF/bevy_verlet), [`ManevilleF/bevy_silk`](https://github.com/ManevilleF/bevy_silk), [`mate-h/bevy_softbody`](https://github.com/mate-h/bevy_softbody), [`Ladvien/bevy_viscera`](https://github.com/Ladvien/bevy_viscera): `README.md` and `Cargo.toml`
- [`avianphysics/avian`](https://github.com/avianphysics/avian): `crates/avian3d/examples/chain_3d.rs`

**Engine-independent**

- [`Scthe/Rust-Vulkan-TressFX`](https://github.com/Scthe/Rust-Vulkan-TressFX), [`gre-v-el/Shell-Texturing`](https://github.com/gre-v-el/Shell-Texturing), [`rowanfr/shell-texturing`](https://github.com/rowanfr/shell-texturing), [`CmrCrabs/fur-shader`](https://github.com/CmrCrabs/fur-shader): `README.md` where there is one, `Cargo.toml`
- [`Traverse-Research/ogawa-rs`](https://github.com/Traverse-Research/ogawa-rs): `README.md`, `Cargo.toml`; [`mxpv/openusd`](https://github.com/mxpv/openusd): crates.io record and a code search for `BasisCurves`

**crates.io records** (`https://crates.io/api/v1/crates/<name>` and `/<name>/<version>/dependencies`): `bevy_feronia`, `bevy_eidolon`, `bevy_open_vat`, `bevy_softbody`, `bevy_verlet`, `bevy_silk`, `bevy_vrm1`, `bevy_vrm`, `vrm-runtime`, `warbler_grass`, `bevy_procedural_grass`, `frosty_grass`, `bevy_symbios_avatar`, `bevy_carnage`, `avian3d`, `bevy_rapier3d`, `rapier-rope`, `ogawa-rs`, `openusd`, `openusd-schemas`, `usd`, `breda-hair`, `viewport-lib-wind`, `bevy_foliage_tool`, `bevy_wind_waker_shader`, `alkyd`. Repository records (dates, stars, licence, contributors, commit counts) are from `https://api.github.com/repos/<owner>/<name>`.

**Bevy**

- Source read locally under `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/`: `bevy-0.19.1/Cargo.toml`, `bevy_pbr-0.19.1/src/extended_material.rs`, `material.rs`, `pbr_material.rs`, `render/mesh.rs`, `render/mesh.wgsl`, `render/skinning.wgsl`, `render/skin.rs`, `render/mesh_functions.wgsl`; `bevy_render-0.19.1/src/lib.rs`, `view/mod.rs`; `bevy_mesh-0.19.1/src/components.rs`; `bevy_material-0.19.1/src/alpha.rs`; `bevy_anti_alias-0.19.1/src/taa/mod.rs`; `bevy_core_pipeline-0.19.1/src/oit/mod.rs`, `core_3d/mod.rs`; `bevy_gltf-0.19.1/src/lib.rs`, `loader/gltf_ext/mesh.rs`; `bevy-0.19.1/examples/shader/automatic_instancing.rs`, `shader_advanced/custom_shader_instancing.rs`
- [`bevyengine/bevy`](https://github.com/bevyengine/bevy): the file list of tag `v0.19.1`; the release list; issues [#13988](https://github.com/bevyengine/bevy/issues/13988), [#16970](https://github.com/bevyengine/bevy/issues/16970), [#17114](https://github.com/bevyengine/bevy/issues/17114) (title, state and dates only)
- [`bevyengine/bevy-assets`](https://github.com/bevyengine/bevy-assets): the file list of `main`, which is what the Bevy Assets page shows

**Blender 5.2 and glTF**

- Blender 5.2 LTS manual: [glTF 2.0](https://docs.blender.org/manual/en/5.2/addons/scene_gltf2.html), [Universal Scene Description](https://docs.blender.org/manual/en/5.2/files/import_export/usd.html), [Alembic](https://docs.blender.org/manual/en/5.2/files/import_export/alembic.html). Downloaded as HTML and searched locally.
- The glTF exporter's source at tag `v5.2.2`: [`io_scene_gltf2/blender/exp/nodes.py`](https://github.com/blender/blender/blob/v5.2.2/scripts/addons_core/io_scene_gltf2/blender/exp/nodes.py), `exp/pointcloud.py`
- [glTF extension registry](https://raw.githubusercontent.com/KhronosGroup/glTF/main/extensions/README.md)

**Secondary, as pointers only**: three web searches (Method); they added nothing that is cited.

**Kiln**: `CLAUDE.md`, the root `Cargo.toml` and `Cargo.lock`, `crates/asset_view/Cargo.toml`, [`fur-animation-trial.md`](fur-animation-trial.md), and, read only, `fur-animation-trial/bevy_probe/src/bin/fur_strands.rs` and `fur_strands.wgsl`.

## Method

Research was done on 2026-10-08 in one sitting.

**Searching.** crates.io's search API was queried with about sixty phrases (fur, hair, strand, groom, shell texturing, grass, foliage, wind, verlet, rope, cloth, jiggle, spring bone, secondary motion, tressfx, hairworks, alembic, usd curves, position based dynamics, xpbd, soft body, vertex animation texture, and each again with "bevy" in front, among others) and the results read as lists. GitHub's repository search was queried with about seventy phrases of the same kind, and its code search inside Bevy, Blender, Fyrox, Ambient, rend3, Avian, `openusd` and `ogawa-rs`. Codeberg's and GitLab's search APIs were queried with seven phrases each and returned one unrelated project. Bevy's issues and discussions were searched for nine phrases. The Bevy Assets listing was read as the file list of its repository.

**Reading.** Twenty-seven repositories were cloned without history, each into its own directory under `/tmp`, and read as text; nothing in them was run. Dates, stars, licences, contributor and commit counts came from GitHub's API; versions, release dates, licences, download counts and the Bevy version each release asks for came from crates.io's API. Blender's manual pages were downloaded as HTML and reduced to text locally, not through a summariser. Bevy facts are from the source of 0.19.1 on this machine.

**The one build.** [`rust-fur-crates-scratch/`](rust-fur-crates-scratch/) is a package of its own, outside the kiln workspace, with `bevy = "=0.19.1"` (`default-features = false`, feature `"3d"`), `bevy_vrm1 = "=0.10.0"` and `bevy_eidolon = "=0.5.0"`. Both crates were chosen because they are published, claim Bevy 0.19 and are the two that a hand-written fur might call. Both declare `build = false`; their crate files were unpacked and checked for a `build.rs` first. `cargo check` with `CARGO_TARGET_DIR` set to the scratch folder's own `target/` finished in 1 minute 29 seconds with no error; `target/` is 931 MB and is ignored by a `.gitignore` in that folder. The resolved versions were `bevy` 0.19.1 and `wgpu` 29.0.4. No binary or example was built or run. The workspace's `target/`, root `Cargo.toml` and root `Cargo.lock` were not used or changed.

**Text addressed to AI agents.** Two cloned repositories contain files of instructions for coding agents (`CLAUDE.md` and `AGENTS.md` in `bevy_vrm1`; `CLAUDE.md` in `bevy_viscera`). They are development guidance for those projects. They were treated as data and not followed. Nothing that tried to direct this research was found.

Only this file and the scratch folder were written. `fur-animation-trial.md` and everything under `fur-animation-trial/` were only read. Nothing under `kiln/`, `crates/` or `profiles/` was touched, and nothing was committed.
