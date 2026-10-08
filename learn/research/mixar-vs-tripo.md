# Mixar (mixar.app) beside Tripo as the source of raw outputs

Researched 2026-10-08. Every page, repository and data file cited below was read on that date. Mixar shipped seven releases in the two weeks before this was written, and its model list and prices are set on its server, not in the app; check each fact again before relying on it.

This is a research note. It informs one choice about kiln (where raw outputs come from) and does not make it. It builds on [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md) and [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md) (called "the earlier notes" below), which hold the Tripo baseline, and does not repeat them. It does not draw on the `first-attempt` tag.

**Nothing here was tested.** No account was created, no generator was called, no app was installed or run. Mixar's public source repository was downloaded and read as text. Every statement about what a tool does is from its site, its documentation, its terms, its source code, or a report by someone else, and says which.

## The question

What is mixar.app, and how does it compare to Tripo as the source of raw outputs for kiln?

## How to read this

- **Fact** (the default) means a first-party page or the product's own published source says so.
- **Source** means the statement was read in Mixar's code, not on its site. Where the two differ, both are given.
- **Site data** means a figure read from the data the public pricing, downloads and changelog pages load when opened (they are drawn in the browser, so the page text alone is empty).
- **Vendor claim** means the vendor says so about its own quality and nobody independent has shown it.
- **Hands-on** means one person's report, with what they published.
- **Inference** means the sentence is this note's reasoning from cited facts.
- **Arithmetic** means a number worked out from list prices and stated assumptions. No cost below was measured.
- **Unverified** means no primary source could be read.
- **Carried over** means a Tripo fact taken from the earlier notes without reading it again today. Tripo facts not marked that way were re-read today.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, generator trial, shape review, asset record, store, static asset) are used as `CONTEXT.md` defines them.

### Terms used here

The earlier notes define mesh, triangle, quad, topology, UV, PBR, decimation, retopology, baking, seed, API, MCP, stdio, headless, background mode, CLI, credit, wire value and add-on. Terms added by this note:

- **Fork:** a copy of another program's source code that is then developed separately. A fork of Blender is a whole application, not something installed into Blender.
- **Orchestrator, front end:** a product that does not make 3D models with a model of its own, but sends the request to other companies' generators and brings the result back.
- **Backend:** the part of a product that runs on the vendor's servers. Mixar's desktop app is open; its backend is not.
- **BYOK (bring your own key):** using your own account with an LLM company inside someone else's app, so that company bills you directly.
- **Pass-through terms:** the conditions of the company whose generator actually made the model, which may still bind the result when it reaches you through a middleman.
- **Catalog:** Mixar's list of the generators it currently offers and the settings each accepts. It is held on Mixar's server and sent to the app.
- **Markup:** a multiplier a reseller applies to its supplier's price.
- **Gaussian splat:** a way of storing a 3D scene as a cloud of soft coloured blobs. It is not a mesh and has no triangles.

## Summary

### What the evidence supports

- **Mixar is not a generator.** It is a desktop 3D editor, a fork of Blender 5.2, with an LLM agent inside it and other companies' generators wired in. Its own site says so: "Mixar is a 3D editor built on Blender that orchestrates the generators rather than being one" ([AI 3D model generator page](https://www.mixar.app/ai-3d-model-generator)).
- **One of the generators it wraps is Tripo.** Mixar's price list has rows for "Image-to-3D - Tripo v3.1", "Image-to-3D - Tripo P2 (Quad)", "Tripo Retopology", "Tripo Texture Generation", "Tripo Auto Rig" and two Tripo segmentation services, beside Hunyuan 3D, Trellis, Rodin and Meshy V7.1 (site data, section 3). So "Mixar or Tripo" is partly "Tripo through a middleman, or Tripo directly".
- **It is made by a small company in India with a US affiliate, and it is launched and moving fast.** The terms name "Adeveda Enterprises Private Limited, trading as "Mixar""; the repository adds "Mixar Inc", incorporated in the United States, which "operates Mixar's hosted backend services". The first release in its changelog is 1.6.12 on 2026-03-08; the source was opened at 2.0.0 on 2026-05-21; the current release is 4.2.2 on 2026-10-04, the 41st (section 2).
- **The app is open source; the part that generates is not.** The desktop app is GPL-3.0-or-later on GitHub. "Mixar's hosted AI backend remains a separate, closed-source service; the app talks to it over the network" (README). Every generation goes through that backend and Mixar's credits, including when the user brings their own LLM key (section 3).
- **It has no documented public API or CLI for generation.** What it has is an MCP server that controls the open, signed-in desktop app. There are installers for macOS and Windows only (section 5).
- **The generator's file is not kept.** In the source, the downloaded `.glb` is a temporary file that is imported into the scene and then deleted; the imported model is renamed, turned, moved to the origin and its material rebuilt as paint layers. What a user can get out is a new export from the editor, not the file the generator returned (source, section 4).
- **Fewer of Tripo's controls are reachable.** The scripted route exposes `texture`, `face_limit` and `model_seed` for Tripo, and its `face_limit` is capped at 20,000 in the current source even for a model whose range is far higher (source, and an open bug report). Tripo's own API has all of the parameters the earlier notes list.
- **Mixar's terms assign output to the user on one plan-independent wording, but make it subject to the generators' own terms, which Mixar does not publish or name per model.** "we assign to you our right, title and interest (if any) in Output", "Subject to ... the terms of any third-party providers you use". Tripo's terms forbid making its service "available to any third party, including end users" without written consent; whether Mixar has that consent is not stated anywhere read (section 7).
- **No evidence was found on the quality of models that come out of Mixar.** It is on neither leaderboard the earlier notes cite, and no hands-on comparison with Tripo was found. Mixar's own article on Tripo against Hunyuan says it contains "no timings, no quality scores and no win rates" (section 9).

### What the evidence does not settle

- Whether a model generated through Mixar carries "commercial rights without attribution", as `learn/MISSION.md` requires. Mixar's own terms ask for no attribution and draw no line between plans, but they point at provider terms they do not reproduce.
- What Mixar actually charges for one generation. Its price rows say "billed = base x generation_markup" and the markup figure is not on any page read.
- Which exact Tripo version a Mixar request reaches, and whether the user can pin it. The site says the engines are "configured server-side and changes over time".
- Whether Mixar can generate with no window. It starts in background mode like Blender, but its job queue relies on timers that its own source says "do NOT fire" in that mode.
- Whether the free 1,000 credits give the same rights as paid credits.

### The smallest experiments

In order of cost: read the catalog and the tool list without spending (section 12, item 1); ask Mixar three questions in writing (items 2 to 4); only then, if still of interest, one generation through Mixar and the same reference image through Tripo's API, both taken into kiln and measured the same way (item 5).

## 1. What mixar.app is

### In its own words

- Home page: "Open source · Bring your own models · Built on Blender" and "A complete 3D editor where agents build and everything stays editable." ([mixar.app](https://www.mixar.app/))
- README: "Mixar is an AI-powered 3D content creation tool built as a custom fork of Blender 5.2. It adds an AI chat agent that can drive Blender, a layered texture-painting system, AI-assisted 3D generation, and a set of Mixar-native editor spaces" ([repository](https://github.com/Mixar-AI/mixar-app)).
- On generation: "Mixar's position is deliberate: it orchestrates generation from inside a Blender-based editor rather than being a generator itself, so the output lands in the scene and the cleanup pass is available in the same application." ([AI 3D model generator page](https://www.mixar.app/ai-3d-model-generator))
- The maker's own one-line pitch on Hacker News: "We're building Mixar, think Cursor for 3D. One access point to all generative inference, an agent to build scenes/blockouts, do boring stuff like UVs and export standard formats" ([Show HN, 2026-08-04](https://news.ycombinator.com/item?id=49171258)).

### What that makes it

Three things in one application (inference from the pages above):

1. **A Blender fork.** Everything Blender 5.2 does, with extra editors. The README: "The Blender features you already know ... are unchanged".
2. **An LLM agent that drives it**, named Mixie. It runs on Mixar's hosted models for credits, or on the user's own key: the home page lists Anthropic, OpenAI, Gemini, OpenRouter ("400+ Models") and a Codex subscription.
3. **A front end over other companies' generators**, for images, 3D models, textures, video and splats, paid for in Mixar credits.

It is not an AR or XR product, and it is not a 3D generator with a model of its own. The README credits the generation to others: "Open-source 3D-generation models from the Hunyuan and Stable Diffusion ecosystems power image and mesh generation."

### Other things with the same name

Named only to avoid confusion; none was opened. Web search results for "mixar" also return: an iOS photo-blending app called Mixar, an iOS augmented-reality model viewer called "Mixar WEB", an old open-source AR engine called mixare, and a Russian contractor. Company-data sites describe a San Jose company called Mixar offering "augmented reality solutions" founded in 2024; that may be an older description of the same company (its GitHub organisation dates from September 2024 and its US affiliate is Mixar Inc), but the profiles were not opened and the link is not established (unverified).

Mixar is also not "3D-Agent", the product ranked on the Blender AI Arena in the earlier note. Mixar publishes a [comparison page against it](https://www.mixar.app/compare/3d-agent) as a rival.

## 2. Who makes it, how old it is, how active

| | Mixar | Tripo |
|---|---|---|
| Maker | "Adeveda Enterprises Private Limited, trading as "Mixar"", India ([terms](https://www.mixar.app/legal/terms-of-service)). The repository's `NOTICE.md` adds "Mixar Inc — a company incorporated in the United States. Operates Mixar's hosted backend services and US-facing commercial operations" | Tripo's terms name "Holymolly Ltd"; its repositories are under VAST-AI-Research (carried over for the second) |
| Law of the contract | "the laws of India"; "courts located in New Delhi" (terms, section 14) | Not re-read |
| First public trace | GitHub organisation created 2024-09-23. First changelog entry 1.6.12, 2026-03-08, "Windows packaging issue fix" | Older; not researched here |
| Source opened | 2.0.0, 2026-05-21: "First open source release" (site data). Repository created 2026-05-18 | Service is closed; CLI and add-ons are MIT (carried over) |
| Current release | 4.2.2, 2026-10-04 (site data and [GitHub releases](https://github.com/Mixar-AI/mixar-app/releases)) | API v3; CLI `tripo-cli` 0.5.2, published 2026-10-08 (npm record, re-read today) |
| Pace | 41 releases in seven months; 4.0.0, 4.1.1, 4.1.2, 4.1.3, 4.1.4, 4.2.0 and 4.2.2 all between 2026-09-24 and 2026-10-04 | CLI: ten versions since July 2026 (carried over) |
| Stage | Launched. Free download, paid plans, checkout through Dodo Payments. A "Creator Circle" early-access programme also exists | Launched |
| Repository | 482 stars, 88 forks, 9 open issues, last push 2026-10-08 ([GitHub record](https://github.com/Mixar-AI/mixar-app)) | n/a |
| Who writes it | Six authors listed in `AUTHORS`, all on the company's behalf. "External pull requests are **not** open yet" (README) | n/a |
| Security claims | Home page: "ISO 27001 compliant", "SOC 2 Type II compliant", with a link to a trust page. Vendor claim; no certificate was looked at | Not researched |

Funding figures for Mixar ("$450K", an investor named All In Capital, nine employees) appeared only in search summaries of company-data sites that were not opened (unverified).

Signs that the public material trails the product, all facts:

- The README says "Project status: v2.0.0"; the `VERSION` file says 4.2.2; the home page banner says "v3.2 Out Now!".
- The README's quickstart clones `mixar-texture-painting`, which an [open issue](https://github.com/Mixar-AI/mixar-app/issues/10) reports as returning 404.
- The terms contain unfilled template text: "[USD 100 or local equivalent]", a bracketed sentence about training, and one reference to "Mixar Foundation".

## 3. What it takes in, and which generators it uses

### Inputs

From the [documentation](https://www.mixar.app/docs) and the [image-to-3D page](https://www.mixar.app/image-to-3d):

- **Text**, to the agent or to a generation tool.
- **One image**: "Choose a clear image with one complete subject, a simple background, and little occlusion."
- **Several views**: "one frontal image plus up to seven additional angles, eight images maximum: left, right, back, top, bottom, left front and right front". A turnaround sheet (one picture showing several views) is cut into views by a "detect-views step".
- **A sketch** drawn over the viewport, which the agent builds from.
- **An existing mesh**, for retopology, UV unwrapping, texturing, segmentation into parts and rigging.

### The generators behind it

Mixar does not publish one list of models. Three sources give overlapping pictures:

**The home page** shows logos under "Powered by the best models in 3D": Tripo, Trellis, Tencent Hunyuan, World Labs, Patina, Nano Banana, ByteDance Seed, and for the agent Claude, OpenAI, Gemini and Kimi.

**The price list** the pricing page loads ([`/plans/feature-credit-costs`](https://api.mixar.app/api/v1/plans/feature-credit-costs), site data, 60 rows) names these 3D services and their base cost in Mixar credits:

| Row, as shown | Base credits | Its description, as shown |
|---|---|---|
| Image-to-3D — Trellis | 10 | "Base (provider) cost; billed = base x generation_markup." |
| Image-to-3D — Rodin | 40 | Same |
| Image-to-3D - Tripo v3.1 | 40 | "Base (provider) cost for Tripo v3.1 image-to-3D; billed = base x generation_markup." |
| Image-to-3D — Tripo | 50 | Same wording as Trellis |
| Image-to-3D - Tripo P2 (Quad) | 50 | "Base (provider) cost for Tripo P2 quad image-to-3D; billed = base x generation_markup." |
| Image-to-3D — Hunyuan (model_3d) | 60 | Same wording as Trellis |
| Hunyuan 3D Rapid / Hunyuan 3D Pro | 20 / 60 | None |
| Image-to-3D - Meshy V7.1 | 120 | "Base (provider) cost for Meshy V7.1 image-to-3D (fal.ai); billed = base x generation_markup." |
| Tripo Retopology | 50 | "Tripo v2.0 retopology (mesh decimate)" |
| Hunyuan 3D Topology / Hunyuan 3D UV | 50 / 10 | None |
| Tripo Texture Generation | 50 | "Texture a mesh via Tripo /v3/models/texture" |
| Tripo Mesh Segmentation / Tripo Smart Segmentation | 40 / 85 | "Split an existing mesh into parts via Tripo /v3/mesh/segment" / "Image to auto-modelled, segmented 3D parts via Tripo /v3/mesh/smartsegment" |
| Tripo Auto Rig / Auto Rig - Meshy | 30 / 20 | "Auto-rig a mesh via Tripo /v3/animations/rig" / "(fal.ai, fal-ai/meshy/rigging)" |
| World Labs World Generation | 126 | "1580 World Labs credits = USD 1.26 = 126 Mixar credits; generation markup is applied at billing time" |

One row gives the pricing calculator's figure: "Image to 3D", 44 credits, "Estimate averaged across Trellis, Rodin, Tripo, and Hunyuan."

**The source** confirms the Tripo routes by name (`RETOPOLOGY_TRIPO_MODEL = "tripo_v2"`, "Animate capability (Tripo v3 animations API)", "Segmentation (Tripo v3 mesh APIs)") and has a comment marking three operator settings "Tripo-specific (tripo-p1)". An [open issue](https://github.com/Mixar-AI/mixar-app/issues/6) quotes the catalog as the reporter saw it on 2026-08-30: "tripo-v31 | Tripo (Pro) | provider=tripo | faces=500-2000000 (default 50000)" (hands-on, one reporter).

What follows from these (inference):

- Tripo reaches Mixar's users two ways by the look of the rows: directly from Tripo's v3 API (the rows that quote Tripo endpoint paths), and possibly through fal.ai, a company that resells many models through one API (rows named "(fal)" exist for Tripo, Trellis, Rodin and Hunyuan). Which route a given request takes is not stated.
- Meshy and Rodin are in the price list but not among the home page's logos. A row in a price list shows that the backend can bill for a model, not that the model is offered to every account today.

### Versions, and whether they can be pinned

- "Which engines are wired behind each capability is configured server-side and changes over time, which is a reason to have them behind one interface rather than seven browser tabs." (AI 3D model generator page)
- Documentation: "Model choices and settings come from the live catalog. A screenshot illustrates the workflow; your available models may differ."
- The user picks a model by Mixar's own name for it (such as `tripo-v31`). Nothing read lets the user send one of Tripo's dated wire values, and nothing says which wire value Mixar's name stands for on a given day (not established).
- **Tripo directly:** `model` is a required parameter and takes a dated wire value; `v3.1-20260211` is in the API text re-read today.

## 4. What comes out

### What the documentation says

- **A mesh in the open scene, not a file.** "The result lands in the scene, not a download folder" (image-to-3D page). The documentation's steps end with "Find the imported mesh, select it, and frame it in the viewport."
- **Triangles by default; quads by request on some engines.** Mixar's article on the two engines lists "Polygon type: Triangle or quadrilateral" for Hunyuan and "Quad option, which changes the output format" for Tripo ([Tripo vs Hunyuan 3D](https://www.mixar.app/blog/tripo-vs-hunyuan)).
- **Face count.** "Mixar's Pro path runs from 40,000 to 1,500,000 faces" (image-to-3D page; this is the Hunyuan route). For retopology: "A face target is approximate, not an exact-count guarantee" and "Tripo retopology requires at least 500 faces" (documentation).
- **Textures.** A "PBR textures" switch: "On, the result comes back with a material set rather than a single colour map". A "geometry pass returns an untextured white model". No texture size in pixels is stated on the pages read.
- **UVs.** Generated ones arrive with the mesh. "AI UV Unwrap is a generation workflow that returns a new mesh with UVs." Mixar's own description of generated UVs: "many small islands, arbitrary seams, inconsistent texel density".
- **Parts.** "Mesh Segment" on an existing mesh, and an image-to-parts workflow; both are Tripo services by the price list.
- **Rigging and animation.** "Auto Rig" exists. Out of kiln's scope.
- **Splats.** A separate workflow: "A splat is not an ordinary polygon mesh."
- **Export formats.** "Mixar exports glTF, OBJ and FBX with built-in presets for Unity, Unreal and Godot" ([batch export guide](https://www.mixar.app/blender-agent/batch-export)). As a Blender fork it has Blender's exporters (README: Blender's features "are unchanged").
- **Scale and facing.** Mixar's own statement about every generated mesh: "arbitrary scale and orientation" (image-to-3D page).

### What the source adds

Read at commit `edaeb32` (2026-10-04), in `src/scripts/mixar/modules/`:

- **The generator's file is deleted after import.** `common/job_queue/core/model_io.py`, `import_file`: the downloaded file is imported with Blender's glTF importer and then, in a `finally` block, `os.remove(filepath)`.
- **The model is changed on the way in.** `moodboard/core/generation_enqueue.py`: a Tripo result is rotated: "Tripo imports facing +X, while every other supported engine (Hunyuan, Trellis, Rodin) already imports facing -Y. Rotating +X onto -Y about world Z is -90 degrees." The import hook then renames the object, applies "origin/world-origin normalization", and calls `convert_imported_material_to_paint_layers`.
- **A copy is kept as a Blender file.** `asset_search/core/generation_library.py`: "Every completed image->3D / model-3D generation is archived into a Mixar-owned asset library". That is a `.blend` asset made after import, not the generator's `.glb`.
- **The scripted route passes few settings.** `moodboard/ui/operators/image_to_3d_ops.py` forwards only these when set: `texture_size`, `mesh_simplify`, `generate_normal`, `save_gaussian_ply` (marked Trellis), `quality`, `geometry_file_format`, `material` (marked Rodin), and `texture`, `face_limit`, `model_seed` (marked Tripo). "The backend validates them against the model's catalog schema and fills defaults for the rest."
- **`face_limit` is capped at 20,000 there**: `bpy.props.IntProperty(default=0, min=0, max=20000)`. The open issue above reports the effect on `tripo-v31`: a request for 200,000 "is submitted as 20,000, with no warning and no error". The line is unchanged in the source read today.

### Beside Tripo

| | Through Mixar | Tripo's API directly |
|---|---|---|
| What arrives | An object in the editor's scene, already turned, renamed and re-materialled; the `.glb` is deleted (source) | A `.glb` file on disk; the CLI also writes `task.json` with the request, seeds and credits (carried over) |
| Formats | Whatever Blender exports: glTF/GLB, OBJ, FBX and others | GLB; GLTF, FBX, USDZ, OBJ, STL, 3MF by conversion (carried over) |
| Face count | Per-model range from the catalog; 20,000 ceiling on the scripted route (source) | `face_limit`, "Maximum polycount for the output mesh"; 500 to 20,000 with `smart_low_poly` (second figure carried over) |
| Quads | Offered for Tripo P2 and by retopology | `quad`, which forces FBX (carried over) |
| Texture size and format | Not stated | `texture_quality` tiers; `texture_size` and `texture_format` at convert (carried over) |
| Baked-in lighting | No setting found | `delight`, default true, but without effect unless `texture_version` is set to `v3.5-20260815` ([later note](tripo-guidance-and-blender-scripting.md)) |
| Size in metres | "arbitrary scale" | `auto_size`, "Default is false" |
| Facing | Turned to Blender's front on import (source) | `export_orientation`, "`+x` — default, X-forward" |
| Parts | Tripo segmentation, resold | `generate_parts`, segmentation endpoints (carried over) |

## 5. Automation

### What Mixar offers

| Route | What it is | Runs with no person and no window |
|---|---|---|
| The desktop app | The main way in. Installers for "mac" (`dmg`) and "windows" (`msi`), both 4.2.2 (site data, [`/downloads`](https://api.mixar.app/api/v1/downloads)) | No |
| The MCP server | "Mixar includes an MCP server. It works with Claude Code, Codex, Claude Desktop, Cursor, VS Code, OpenCode, Windsurf, Cline, Gemini CLI, and any app that can run a local "stdio" MCP server." Added in 4.2.2 | No: see below |
| A public HTTP API | None documented. The terms' definition of the Service mentions "API-based services" and the privacy policy lists "APIs", but the documentation describes none. `api.mixar.app` is the app's own backend | n/a |
| A CLI for generation | None found | n/a |
| An SDK | None found | n/a |
| A Blender add-on | No. It is a separate application. Its [comparison with Blender MCP](https://www.mixar.app/compare/mixar-vs-blender-mcp) says: "The bridge is free and works with your existing Blender install. Mixar is a separate application." | n/a |
| Agent Skills | None found in the repository or on the site | n/a |

### How the MCP server works

From the [documentation](https://www.mixar.app/docs), the bridge's README in the repository and `src/scripts/mixar/mcp.py`:

- **It controls the running desktop app.** The launcher finds an open Mixar on the same machine and forwards each call to it over `127.0.0.1`. With none running it answers: "Open Mixar, sign in, then use the profile menu > Connect AI Apps (MCP) to enable MCP." The documentation adds "Your AI app can start Mixar when it needs to. You must be signed in."
- **Signing in is through a browser.** README: "The desktop app authenticates via browser SSO".
- **The tools come from the backend**, not from the open source: "Mixar's scene tools come from the backend, which needs a signed-in app" (`tool_snapshot.py`). The bridge's README describes them: "scene and geometry inspection, Blender scripting, materials and layers, UVs, generation, assets, animation through scripting, rendering and export. Tool discovery includes schemas and pricing policy." The list itself is not in the repository, so the generation tool's parameters could not be read.
- **Cost.** "Inspecting, building and editing scenes and controlling the Mixar UI are free. Only AI generation costs Mixar credits, at its usual price."
- **Timeouts.** A call may last up to 600 seconds; the documentation tells Codex users to set `tool_timeout_sec = 610`. After a timeout: "the work may still have finished. Ask the assistant to inspect the scene before repeating anything."
- **Hosted assistants cannot connect**: "apps that need a remote (OAuth) MCP connection are not supported yet".

### Headless, and Linux

- **Linux.** The marketing pages end "Windows, macOS and Linux." The downloads page is titled "Download Mixar — Mac and Windows" and its data lists only those two. An [issue of 2026-10-02](https://github.com/Mixar-AI/mixar-app/issues/8), "Any plan to support Linux in the Future?", has no reply. The repository has Linux build scripts and its README says to build Blender for "macOS / Linux / Windows" first. So on Linux the only route is building a Blender fork from source (inference); kiln's development machine runs Linux.
- **Background mode.** As a Blender fork, Mixar starts with `--background --python`. The reporter of issue 6 gives their environment as "macOS arm64, headless (`--background --python`)" and called the generation operator from a script, but intercepted the request before it was sent (hands-on).
- **Whether a generation completes there is not established.** Mixar's own `headless/headless_main.py` says "in --background, bpy.app.timers do NOT fire", and the job queue's download and import steps are scheduled with `bpy.app.timers.register` (`queue_download.py`). That file is a worker started by the desktop app for the agent, taking a token from its parent; it is not a documented entry point for users (source; the conclusion is inference).
- **The acceptable use policy** forbids using "automated means to scrape or harvest data from the Service, or to circumvent usage limits, rate limits, or access controls". It does not forbid automation as such, and the MCP server is an automation route Mixar itself ships.

### Beside Tripo

Tripo has a plain asynchronous HTTP API with a key, a CLI that is "automatically headless" when no terminal is attached, fixed exit codes, a dry run, and a batch command (carried over from the earlier note; the API text and CLI version were re-read today). It needs no window and no particular operating system. Rate limits: carried over.

## 6. Pricing

### Mixar's plans

From the data the [pricing page](https://www.mixar.app/pricing) loads (site data, [`/plans/`](https://api.mixar.app/api/v1/plans/)):

| Plan | Per month | Per year | Credits a month | Listed features | Per credit (arithmetic) |
|---|---|---|---|---|---|
| Starter | $29.99 | $299.99 | 3,000 | "All generations + Agent tools" | $0.0100 |
| Pro | $49.99 | $499.99 | 6,000 "(20% bonus)" | "Everything in Starter", "Priority processing" | $0.0083 |
| Max | $99.99 | $999.99 | 14,000 "(40% bonus)" | "Early access to new features", "Highest priority processing" | $0.0071 |
| Enterprise | "Book a call" | | "Custom credit volume" | "Custom contracts & invoicing" | |

- **Free credits.** Home page: "Start with 1,000 credits", "Download now to get free 1000 credits", "Free to download, sign in to activate". No free plan appears in the plan data. Whether the 1,000 credits are given once or monthly is not stated. The maker's Hacker News post of August says "first week is free".
- **Top-ups.** A "Buy credits" page exists for signed-in users ("Every $1 gives you ... of usage"); the rate is shown only after signing in (not read).
- **Credits and refunds.** "Credits are consumed as you use paid features and, unless stated otherwise, are non-refundable and may expire." The comparison page says "terminal failures refund the credits".
- **The agent costs credits too** unless BYOK is used: "Agent Chat" 1, "Agent Plan Generation" 2, "Agent Execution" 3 (site data). With BYOK, "Generation jobs remain separate and may still consume Mixar credits."
- **The markup.** Rows are "billed = base x generation_markup". The multiplier is not in the data read, the pages read, or the open source. The documentation declines to give prices: "Check the app's current credit information; this guide does not prescribe fixed prices or generation times."

### Tripo's prices, re-read today

- [API pricing](https://developers.tripo3d.com/en/pricing): "1 credit = $0.01 USD". "Image to 3D" 30 credits with standard texture. Add-ons: "HD Texture +10", "8K Ultra Texture +20", "HD Geometry Quality +20", "Quad Mesh +5", "Smart Low-poly +10", "Generate Parts +20". "Simple, transparent pay-as-you-go pricing."
- [Studio pricing](https://www.tripo3d.ai/pricing): free, "200 Monthly Credits", "Public Models · Non-Commercial Use"; $20.00 a month, "3000 Monthly Credits", "Private Models · Commercial Use".
- "Failed and cancelled tasks are not charged." (API text)
- Retopology v2.0 at 30 credits: carried over.

### One textured prop, worked

**Arithmetic. Nothing was measured.** Assumptions: one reference image; Tripo v3.1; standard textures; Starter-plan credit price for Mixar; the earlier note's guess of three generations for each one a person approves; **Mixar's markup taken as 1, which is the lowest it can sensibly be and is not known**.

| | Through Mixar (at least) | Tripo's API directly |
|---|---|---|
| One image-to-3D generation | 40 credits, $0.40 | 30 credits, $0.30 |
| Three generations (guess) | 120 credits, $1.20 | 90 credits, $0.90 |
| One Tripo retopology on the approved one | 50 credits, $0.50 | 30 credits, $0.30 (carried over) |
| Three generations and one retopology | $1.70 | $1.20 |
| Instead: one generation with Tripo's low-poly option | Not offered as a setting found | 40 credits, $0.40 |
| Smallest spend in a month an asset is made | $29.99, unless free or top-up credits cover it | Pay as you go; smallest purchase carried over as $10 |
| Agent messages, if Mixie drives it | 1 to 3 credits each, or the user's own LLM bill | Not applicable |

The per-asset difference is small. The differences that matter are the subscription floor, the unknown markup, and that Mixar's base figure for Tripo v3.1 (40) is already above Tripo's own list price for a standard generation (30). Whether Mixar's 40 buys a higher texture tier than Tripo's 30 is not stated (inference and gap).

## 7. Terms

### Mixar's own terms

[Terms of Service](https://www.mixar.app/legal/terms-of-service), [Privacy Policy](https://www.mixar.app/legal/privacy-policy) and [Acceptable Use & Refund Policy](https://www.mixar.app/legal/acceptable-use-and-refund-policy), each "Last updated: July 24, 2026".

- **Ownership of output.** "As between you and Mixar, and subject to your compliance with this Agreement and payment of any applicable fees, we assign to you our right, title and interest (if any) in Output generated for you through your use of the Service. This assignment does not extend to (i) our underlying models, software, or the Service itself, or (ii) any third-party materials incorporated into the Output."
- **Use of output.** "Subject to your compliance with these Terms and to the terms of any third-party providers you use, you may use Output for your lawful purposes."
- **No plan tiers in the terms.** The same wording covers every user. "payment of any applicable fees" is the only link to paying; what it means for the free credits is not said.
- **Attribution.** None is required by any of the three documents. The only disclosure duty: "You must not present Output in a way that is misleading as to its AI-generated nature where disclosure is legally required."
- **Public by default.** Nothing read says outputs are published or shown to others. No public gallery was found on the site. The licence the user gives Mixar is "solely to the extent necessary to operate, maintain, secure, and improve the Service".
- **Training.** Privacy policy, 3.1: "We do not currently use your Content (uploads, prompts, or generated outputs) to train or fine-tune Mixar's underlying AI models." It reserves the right to change this with notice. The terms carry a bracketed, apparently unfinished sentence on the same point. Neither says anything about what the generator companies do with what Mixar sends them.
- **Pass-through, in Mixar's words.** Privacy policy, 4: "Because outputs may be produced using third-party AI models (including via BYOK), your rights in a given output may also be subject to that provider's terms, and you are responsible for ensuring your use of any output complies with applicable law and third-party rights."
- **Competing models.** Not to "Use Output from the Service to develop or train a competing product or model, where we or an applicable third-party provider prohibit this."
- **No promise about copyright.** "Mixar makes no representation as to whether or to what extent any given Output is protectable by copyright".
- **Indemnity runs one way**: the user indemnifies Mixar. Liability is capped at twelve months' fees or "[USD 100 or local equivalent]".

### The generators' terms behind it

- **Tripo** ([terms](https://www.tripo3d.ai/terms), "Last updated: July 11, 2025", re-read today). Rights depend on who Tripo's customer is: "For Users who access and use the Services free of charge ("Free Users"), Tripo retains all rights"; "Paid Users generally have all rights ... of the Inputs and Outputs by the paid Users", and "Company will not use Inputs and Outputs as training data". Among the things a user must not do: "make the Generative 3D Foundation Model Service available to any third party, including end users, without the prior written authorization and consent of Holymolly."
  - When a model is made through Mixar, Tripo's customer is Mixar, not the person at the keyboard (inference from how the app works: the user holds no Tripo account or key).
  - Whether Mixar has Tripo's written consent, and what that agreement says about end users' rights, is not published by either company (not established). Tripo's logo on Mixar's home page is not evidence of the terms.
- **fal.ai** ([terms](https://fal.ai/terms), "Last Updated: September 8, 2026", searched, not read end to end). It makes no promise about rights in outputs: the company "does not represent, warrant, or covenant that any Output Content will be original, will not infringe rights of any third party ..., or otherwise entitle Company to any intellectual property rights in any Output Content", and it bars using third-party models' outputs to build competing products. Each model on fal can carry its own terms; those were not read.
- **Tencent Hunyuan, Rodin, Trellis, Meshy, World Labs:** not read for this note. The earlier note records Meshy's terms when Meshy is used directly; whether they reach a model made through fal and Mixar is not established.

### Against the mission's rule

`learn/MISSION.md`: "a generator plan or library is usable only if its licence gives commercial rights without attribution."

| | Commercial use | Attribution | Verdict against the rule |
|---|---|---|---|
| **Mixar, free credits** | Mixar's terms allow "lawful purposes" and assign Mixar's interest "subject to ... payment of any applicable fees" | None required by Mixar | **Not shown.** The fee wording is unclear for free use, and the provider's terms sit underneath |
| **Mixar, Starter, Pro, Max** | Same wording; fees paid | None required by Mixar | **Not shown.** Mixar's own grant passes; the provider's terms are incorporated and unpublished. A written answer from Mixar per generator would settle it |
| **Mixar, Enterprise** | "Custom contracts" | Not stated | Depends on the contract |
| **Tripo, free** | "Tripo retains all rights"; "Non-Commercial Use" | n/a | **Fails** |
| **Tripo Studio, paid** | "Paid Users generally have all rights"; "Private Models · Commercial Use" | None found | **Passes** on the text |
| **Tripo API, pay as you go** | Same clause if the customer is a "Paid User", which the terms do not define | None found | **Passes if** that reading holds; the earlier notes' open question, unchanged |

The earlier notes' caution applies to both: no vendor's terms can say whether copyright exists in a generated model at all.

## 8. Claude, other LLMs and Blender

- **Claude inside Mixar.** The agent can run on the user's own Anthropic key (home page; README: "plug in your own OpenAI / Anthropic / other provider API keys"). The terms: with BYOK "You authorize us to transmit your prompts, inputs, and related content to that provider on your behalf". Mixar stores the key "in encrypted form".
- **Claude outside Mixar, driving it.** The MCP server of section 5, with an "Add to Claude Code" button that runs `claude mcp add --scope user mixar -- <launcher>`.
- **A local LLM.** Since 3.4.0 the agent can run on a model on the user's machine through a bundled `llama.cpp` server, or one the user already runs. The documentation warns it is "not a promise that the entire app works offline". This is for the agent only; 3D generation stays on Mixar's backend.
- **Blender.** Mixar is Blender 5.2 with changes, under the GPL. `.blend` files and Blender's Python API are there. It is not an add-on for a stock Blender and does not connect to one.
- **Tripo, for comparison** (carried over): an official CLI with instructions for coding agents, an MCP mode of that CLI, and a Blender add-on. None of them needs a third company.

## 9. Evidence on output quality

Graded as the earlier notes grade.

**On Mixar's results: none found.**

- *Leaderboards.* The word "Mixar" does not occur on the [Blender AI Arena leaderboard](https://blenderai.org/leaderboard) or the [Top 3D AI arena](https://www.top3d.ai/) front page as downloaded today. Both pages were readable (they contain the entrants the earlier note lists).
- *Vendor.* Mixar's own article declines to give numbers: "There are no timings, no quality scores and no win rates in this piece. Publishing those without a controlled test across a matched asset set would be inventing numbers". Its position on generators in general: "Current generators produce comparable meshes on a clean reference, so the generator is rarely the deciding factor." That is a claim by a company whose product is the step after generation (interested party).
- *Hands-on, one reporter, no files.* GitHub issue 6 gives triangle counts from Tripo v3.1 through Mixar on one character: `face_limit` 20,000 returned 19,846 triangles; 300,000 returned 289,308. Both are under the limit, which agrees with Tripo's description of `face_limit` as a maximum. The same report says that at 20,000 "the hands got ~84 vertices in total and could not be skinned".
- *Forum, single comments.* On Mixar's Show HN thread (6 points): "I have tried a lot of AI 3D stuff but nothing is usable in actual games. Sometimes it makes my character rigs so weird that I am unable to animate it." The maker replied that the agent "performs bad" at "assigning the weight paints". About rigging, which kiln does not do.
- *Defect reports in the repository.* A closed issue reports that builds from the public source "crash on startup ~100% of the time on Windows" because a module was left out of the public tree (July 2026). Others: a missing GPU kernel, the README's dead clone address.
- *Second-hand.* A directory page ([agentcommunity.org](https://agentcommunity.org/m/mixar)) describes Mixar approvingly with no tests. Search summaries mention a "technical review" of the agent on baking and level-of-detail tasks, apparently a LinkedIn post; it was not opened.

**On the generators Mixar wraps:** the earlier note's section 4.4 stands, since a model made by Tripo v3.1 through Mixar is made by Tripo v3.1. Its standings (carried over): Tripo AI v3.1 third for texture, Tripo's P series first and second for low poly on the Top 3D AI arena; one counted test finding non-manifold edges and zero-area faces in Tripo's reduced output. What Mixar's import step and re-export add to or take from that is unmeasured.

Searches of Reddit returned nothing readable (the site refused the request), and no YouTube video was opened. A failed search is a gap in the search, not proof that no report exists.

## 10. Side by side

"Documented" means a first-party page says so. "Source" means read in Mixar's code. "Not found" means nothing was found either way.

| | Mixar (mixar.app) | Tripo, used directly |
|---|---|---|
| What it is | A Blender 5.2 fork with an LLM agent and resold generators | A 3D generator with its own models |
| Maker | Adeveda Enterprises Private Limited (India); Mixar Inc (US) runs the backend | Holymolly Ltd in its terms |
| Stage | Launched; 41 releases since March 2026 | Launched |
| Open source | App: GPL-3.0-or-later. Backend: closed | Service closed; CLI and add-ons MIT (carried over) |
| Its own 3D model | No | Yes: H series and P series |
| Third-party models | Tripo, Hunyuan, Trellis, Rodin, Meshy by its price list; some through fal.ai | Its image endpoints resell other companies' image models (carried over) |
| Version pinning | Mixar's model names; "configured server-side and changes over time" | Dated wire value, required |
| Inputs | Text, one image, up to eight views, sketch, existing mesh | Text, one image, up to four views, existing mesh (carried over) |
| Output reaching the user | An object in a scene; export from the editor | A `.glb` file |
| Generator's file kept | No: deleted after import (source) | Yes |
| Face-count control | Per model; 20,000 cap on the scripted route (source) | `face_limit`, a maximum |
| Seed | `model_seed` exists on the scripted route (source); in the interface, not found | `model_seed`, `texture_seed`: "will produce an identical 3D mesh" (vendor claim) |
| Editing a result | The whole of Blender, plus the agent | Re-texture, segment, convert; no shape edit by instruction (carried over) |
| Style across a set | Not found; Mixar says matching a library "has to be supplied and enforced" | Not found (carried over) |
| Public API | Not documented | Yes, asynchronous HTTP |
| CLI | No | Yes |
| MCP | Yes, driving the open desktop app | Yes, `tripo mcp` (carried over) |
| Unattended on Linux | No installer; needs the signed-in desktop app | Yes (carried over) |
| Price of one image-to-3D with Tripo v3.1 | 40 credits times an unpublished markup; from $0.40 on Starter | 30 credits, $0.30 |
| Smallest monthly spend | $29.99, or free and top-up credits | Pay as you go |
| Output rights | Mixar assigns its interest, "subject to ... the terms of any third-party providers" | Paid users "generally have all rights"; free users none |
| Attribution | None required by Mixar | None found for paid users |
| Trains on user content | "We do not currently"; providers not addressed | "will not use Inputs and Outputs as training data" (paid users' clause) |
| Quality evidence | None found for Mixar | Blind-vote rankings and a few hands-on tests (carried over) |

## 11. Fit with kiln

**Everything in this section is inference** from the facts above and from `CLAUDE.md`, `CONTEXT.md` and `learn/MISSION.md`.

- **Mixar is not a like-for-like alternative to Tripo. It is closer to an alternative to kiln.** The design being considered is: a generator makes a model, kiln keeps the file, a person reviews the shape, fixed Blender scripts fit it to a target profile. Mixar's pitch is the same sequence done inside one editor by an agent: "Convert this image to 3D, then retopologise to 8k quads, rebuild the UVs and bake the detail down." The mission asks for "a pipeline I designed and understand"; Mixar is someone else's pipeline, with an LLM choosing the steps.
- **As a source of raw outputs it fits poorly, on four of kiln's own properties:**

| Kiln property | Through Mixar | Tripo directly |
|---|---|---|
| The raw output is "the file a generator returns, kept unchanged" | The generator's file is deleted; what can be exported has been turned, renamed, re-originned and re-materialled, then written again by Blender's exporter | Fits: a `.glb` on disk |
| "The generator is called through one interface so it can be swapped", unattended | No API or CLI; an MCP server that needs the signed-in desktop app; no Linux installer | Fits: HTTP or CLI |
| The asset record holds "its licence, its source" | The source would be "Tripo v3.1 through Mixar, version unknown"; the licence rests on terms not published | A dated wire value, a task ID, seeds; Tripo's terms by plan |
| `kiln rebuild` repeats a build from the kept raw output | Possible only from the re-exported file, which is already processed | Fits |

- **It adds a second company between kiln and the generator** without adding a generator. The same Tripo model costs more, with fewer of its settings, an extra set of terms, and a version chosen on Mixar's server.
- **Where Mixar could still be of use to the owner, outside the pipeline:**
  - *As a place to look at and learn from.* It is a Blender with an agent that will explain and do things, and its documentation and guides are written plainly about the same steps kiln automates (retopology, UVs, baking, export). That is a learning aid, not a stage.
  - *As a way to try several generators on one reference image without several accounts*, before a generator trial. The results would not be clean raw outputs, so they could inform which generators to enter, not replace the trial.
  - *As reading matter.* Its source is GPL and built on the same Blender version kiln pins (5.2). How it imports generated glTF files, turns Tripo's output and guards the importer is there to read. Kiln's own licence would have to be considered before copying any of it.
- **A model exported from Mixar can already enter kiln** as an existing model file through `python3 -m kiln run --model`. In kiln's vocabulary it would be nearer a hand-modelled asset made in an authoring tool than a generated asset with a kept raw output; which it is, is the owner's call.
- **Claude's role does not need Mixar.** Helping the owner write prompts and choose settings works the same against Tripo's API. Mixar's MCP server would let Claude Code drive Mixar's editor, which is the "LLM in the run" arrangement the earlier notes set against repeatability.

## 12. What is unknown, and the smallest experiment for each

1. **Which generators and settings Mixar offers this account today, and the real prices.**
   Smallest experiment: sign in with the free credits on a Mac or Windows machine, open the 3D generation panel and the credit information, and write down the model list, each model's settings and its price. No generation needed. This also shows the markup. (Needs an account; not done here.)
2. **Whether a model made by Tripo through Mixar may be sold in a game without credit.**
   A written question to Mixar: for each 3D generator, which company's terms apply to the output, on free and on paid credits, and does Mixar hold Tripo's consent to serve end users. Before any Mixar-made asset goes in a sold game.
3. **Which Tripo version `tripo-v31` stands for, and whether it can be fixed.**
   Same letter. Or read it from the catalog in experiment 1 if it shows a dated value.
4. **Whether a generation can complete with no window.**
   A question for Mixar, or the bridge's tool list after sign-in. Not worth building the fork on Linux to find out unless items 1 to 3 come back favourably.
5. **What Mixar's import does to a Tripo model, in numbers.**
   One reference image through Tripo's API (about $0.30) and the same image and model through Mixar (about 40 credits), the Mixar result exported as `.glb`; both taken in with `python3 -m kiln run --model` and compared with `python3 -m kiln.measure`: triangles, bounding box, materials, textures, UVs, validator result. This is the only item that spends money in two places.
6. **Whether the free 1,000 credits are one-off, and what rights they carry.**
   Items 1 and 2 answer it.
7. **Whether Mixar's seed setting reaches Tripo and repeats a result.**
   Only after item 5, and only if Mixar is still of interest: the same request twice.

The earlier notes' open items for Tripo itself (the "Paid User" question, whether a seed returns the same file, what a raw output for a prop is like) are unchanged and are cheaper to settle than any of these.

## What could not be verified, and where sources disagreed

**Could not be opened or was not read**

- Mixar's signed-in pages: the dashboard, the credit top-up rate, the live model catalog, the MCP tool list with its parameters.
- Mixar's backend. It is closed; everything about what it does with a request is from the client's source or Mixar's statements.
- Mixar's Cookie Policy and its trust page beyond the two certification names; no certificate or audit report was looked at.
- The terms of Tencent Hunyuan, Rodin, Trellis and World Labs; any per-model terms on fal.ai; fal's terms beyond a keyword search.
- Company-data profiles of Mixar (Preqin, PremierAlts) and the AlternativeTo page (refused the request); a Product Hunt page (not found at the address tried); a LinkedIn post described in search results as a technical review.
- Reddit (the search request returned nothing readable) and YouTube (no video opened).
- Mixar's guides on retopology, UV unwrapping, baking and PBR textures were downloaded and not read through; its blog articles other than the two quoted were read only as titles and summaries.
- Mixar's source was searched for the passages quoted, not read end to end: 1,871 Python files. The C++ part was not read.

**Not established**

- Mixar's generation markup, and so its true price per generation.
- Whether Mixar reaches Tripo directly, through fal.ai, or both.
- Which of the generators in the price list are offered to an ordinary account today.
- Whether Mixar holds Tripo's written consent to serve end users, and what rights that arrangement passes on.
- Whether the three Tripo settings on the scripted route (`texture`, `face_limit`, `model_seed`) are also in the interface, and whether the seed is honoured.
- The pixel size and file format of textures on models generated through Mixar.
- Whether generation works in background mode.
- Whether the San Jose "Mixar" in company-data listings is this company, and its funding.
- Who is behind agentcommunity.org, which lists Mixar under the domain "mixar.ai".
- Whether outputs are ever shown publicly. Nothing read says they are; nothing read says they are private either.

**Tripo facts carried over without re-reading today**

- Everything about `tripo-cli` beyond its version: `task.json`, the dry run, exit codes, the batch command, the MCP tools, the automatic switch to P1.
- Rate limits; how long output links last; the Blender add-on; retopology prices; the conversion formats; `smart_low_poly`'s range; `delight`; the P series.
- Leaderboard standings and the hands-on tests in the earlier note's section 4.4.
- The smallest credit purchase.

Re-read today: Tripo's terms (sections on free and paid users, and the list of prohibited uses), Studio pricing, API pricing for the H series, and in the API text the seed wording, `face_limit`, `auto_size`, `export_orientation`, the failed-task rule and the presence of `v3.1-20260211`.

**Sources disagree**

- **Mixar's version.** README: "v2.0.0". `VERSION` file, downloads data and changelog: 4.2.2. Home page banner: "v3.2 Out Now!".
- **Which Blender.** README: "Blender 5.2". Third-party descriptions and one of the repository's own issues: "Blender 5.0". The fork was moved to 5.2; the older figure is out of date.
- **Linux.** Marketing pages: "Windows, macOS and Linux." Downloads page and data: Mac and Windows.
- **Who operates the service.** Terms: "owned and operated by Adeveda Enterprises Private Limited". `NOTICE.md`: Mixar Inc "Operates Mixar's hosted backend services".
- **The free offer.** Home page: 1,000 credits. The maker on Hacker News in August: "first week is free". Plan data: every plan has `trial_period_days` 0.
- **Tripo's price in Mixar.** Three rows: "Image-to-3D — Tripo" 50, "Image-to-3D - Tripo v3.1" 40, "Image-to-3D Tripo (fal)" 50. Tripo's own list: 30.
- **What Mixar's model list is.** Home page logos omit Rodin and Meshy; the price list includes both.
- **The face-count range.** The image-to-3D page gives 40,000 to 1,500,000 as "Mixar's Pro path" (Hunyuan); the catalog quoted in issue 6 gives 500 to 2,000,000 for `tripo-v31`; the operator caps any scripted request at 20,000.
- **Tripo's multi-view input.** Mixar's article says it "Varies by tier"; Tripo's API takes up to four views (carried over).
- **This note against its brief.** The brief asked how Mixar compares "as the source of raw outputs". It is not one; it is a way of reaching the sources, with an editor around it.

## Sources

All read 2026-10-08.

**Mixar: site**

- [Home page](https://www.mixar.app/), [About](https://www.mixar.app/about), [Documentation](https://www.mixar.app/docs) ("Updated October 2026"), [Blog index](https://www.mixar.app/blog), [Comparisons index](https://www.mixar.app/compare), [Creator program](https://www.mixar.app/creator-program), [sitemap](https://www.mixar.app/sitemap.xml)
- [Image to 3D](https://www.mixar.app/image-to-3d) and [AI 3D model generator](https://www.mixar.app/ai-3d-model-generator)
- [Tripo vs Hunyuan 3D](https://www.mixar.app/blog/tripo-vs-hunyuan), 1 August 2026. Vendor.
- [Mixar vs Blender MCP](https://www.mixar.app/compare/mixar-vs-blender-mcp), 16 July 2026, and [3D Agent alternative](https://www.mixar.app/compare/3d-agent). Vendor; searched, not read through.
- [Blender batch export guide](https://www.mixar.app/blender-agent/batch-export). Searched for formats.
- [Pricing](https://www.mixar.app/pricing), [Downloads](https://www.mixar.app/downloads) and [Changelog](https://www.mixar.app/changelog), and the data those pages load: [`/plans/`](https://api.mixar.app/api/v1/plans/), [`/plans/feature-credit-costs`](https://api.mixar.app/api/v1/plans/feature-credit-costs), [`/downloads`](https://api.mixar.app/api/v1/downloads), `/updates/changelog`
- [Terms of Service](https://www.mixar.app/legal/terms-of-service), [Privacy Policy](https://www.mixar.app/legal/privacy-policy), [Acceptable Use & Refund Policy](https://www.mixar.app/legal/acceptable-use-and-refund-policy), each last updated 24 July 2026
- [Trust page](https://mixar.trust.site/) (certification names only)

**Mixar: repository**

- [`Mixar-AI/mixar-app`](https://github.com/Mixar-AI/mixar-app) at commit `edaeb32`: `README.md`, `NOTICE.md`, `AUTHORS`, `MAINTAINERS.md`, `TRADEMARKS.md`, `SOURCE_CORRESPONDENCE.md`, `VERSION`; and under `src/scripts/mixar/`: `mcp.py`, `headless/headless_main.py`, `modules/mcp_bridge/README.md`, `modules/mcp_bridge/core/tool_snapshot.py`, `modules/mcp_bridge/constants.py`, `modules/hunyuan/constants.py`, `modules/moodboard/ui/operators/image_to_3d_ops.py`, `modules/moodboard/core/generation_enqueue.py`, `modules/common/job_queue/core/model_io.py`, `modules/asset_search/core/generation_library.py`, `modules/local_models/README.md`
- Repository and organisation records, [release list](https://github.com/Mixar-AI/mixar-app/releases), and issues [1](https://github.com/Mixar-AI/mixar-app/issues/1), [3](https://github.com/Mixar-AI/mixar-app/issues/3), [6](https://github.com/Mixar-AI/mixar-app/issues/6), [8](https://github.com/Mixar-AI/mixar-app/issues/8), [10](https://github.com/Mixar-AI/mixar-app/issues/10), with the titles of the rest. Issues are hands-on reports, one reporter each.

**Tripo (re-read)**

- [Terms of Service](https://www.tripo3d.ai/terms), last updated 11 July 2025
- [Studio pricing](https://www.tripo3d.ai/pricing)
- [API pricing](https://developers.tripo3d.com/en/pricing)
- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt)
- [`tripo-cli` npm registry record](https://registry.npmjs.org/tripo-cli) (version and date only)

**Other providers**

- [fal.ai Terms](https://fal.ai/terms), last updated 8 September 2026. Searched by keyword.

**Evidence and third parties**

- [Show HN: Blender for AI Agents](https://news.ycombinator.com/item?id=49171258), 4 August 2026. The maker's post and six comments. Forum.
- [Blender AI Arena leaderboard](https://blenderai.org/leaderboard) and [Top 3D AI arena](https://www.top3d.ai/). Searched for the name only.
- [agentcommunity.org: Mixar](https://agentcommunity.org/m/mixar). Directory entry, no tests.

**This repo**

- [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md) and [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md), for the Tripo baseline and the evidence grades.

## Method

Research was done on 2026-10-08. Mixar's site pages were downloaded as HTML and reduced to text locally, not through a summariser; one summarised fetch of the home page was used at the start to find out what the product was and nothing is cited from it. The pricing, downloads and changelog pages are drawn in the browser from data requests; the same public, unauthenticated requests those pages make were made directly and their JSON read. No request was made that needs an account.

Mixar's repository was cloned and its text files searched for provider names, generation parameters, the import path, MCP and background-mode handling; nothing in it was built or run. Repository records, releases and issues were read through GitHub's API. Hacker News was searched through its public search API.

Tripo's terms, pricing pages and API text were downloaded again and searched for the clauses this note leans on; the rest of the Tripo baseline is from the two earlier notes and is marked "carried over" where used. A third note, `tripo-guidance-and-blender-scripting.md`, did not exist when this was written and was not used.

Six web searches were used to find the company, reviews and comparisons; they found the Hacker News thread, the directory page and the unopened pages listed above. Nothing is cited from a search summary except where marked unverified.

Facts about kiln are from `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md` and `profiles/pit.toml`. No generator was called, no account was created, no application was installed or started, and no file from the `first-attempt` tag was used. Only this file was written.
