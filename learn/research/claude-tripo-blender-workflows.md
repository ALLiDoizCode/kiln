# Claude, Tripo and Blender together: which workflows exist and how each works

Researched 2026-10-08. Every page, package and repository cited below was read on that date. Tool versions, prices, model names and command names in this area change within weeks (one package cited here was republished on the day of reading); check each again before relying on it.

This is a research note. It describes the ways the three tools can be wired together and what is known about each. It does not choose one. It builds on [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md) (called "the earlier note" below), which compares an LLM alone, a generator alone and an LLM driving a generator, and does not repeat it. It does not draw on the `first-attempt` tag.

**Nothing here was tested.** No generator was called, no account was created, no MCP server was started and no package was run. Packages and repositories were downloaded and their source was read as text. Every statement about what a tool does is from its documentation, its source code, its terms, or a report by someone else, and says which.

## The question

What workflows exist that combine Claude, Tripo and Blender; how does each actually work; and what is known about how well they work?

## How to read this

- **Fact** (the default) means a first-party page or the tool's own source code says so.
- **Source** means the statement was read in the program's code, not in its README. Where the two differ, the code is given.
- **Vendor claim** means the vendor says so about its own quality and nobody independent has shown it.
- **Vendor-run**, **preprint** and **hands-on** are the grades for evidence, as the earlier note defines them: a test by a company that sells one of the things tested; a research paper with its method; one person's report.
- **Inference** means the sentence is this note's reasoning from cited facts.
- **Arithmetic** means a number worked out from list prices. No cost below was measured.
- **Unverified** means no primary source could be read.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, review pictures, asset record, store, static asset) are used as `CONTEXT.md` defines them.

### Terms used here

The earlier notes define mesh, triangle, quad, topology, UV, PBR, decimation, retopology, baking, LLM, token, `bpy`, headless, seed, API, asynchronous, polling, MCP, MCP server, MCP client and agent. Terms added by this note:

- **CLI (command-line interface):** a program run by typing a command in a terminal. A script, or Claude Code, can run it the same way.
- **stdio:** the plain text channels every program has (input, output, errors). A **stdio MCP server** is a program the MCP client starts on the same machine and talks to over those channels. Nothing is exposed to the network.
- **Tool** (in MCP): one named action a server offers, with a list of parameters. The LLM sees the name, a description and the parameters, and decides when to call it.
- **Agent Skill:** a folder with a `SKILL.md` file of instructions that a coding agent such as Claude Code loads when a task matches. It is text, not code.
- **Add-on:** a Python package installed inside Blender. Blender calls its newer packaging "extensions".
- **Socket:** a network connection between two programs, here always on the same machine (`localhost`).
- **Background mode:** Blender started with `--background` (or `-b`): no window. This is what `tools/bl` does.
- **Credit:** Tripo's billing unit. Its API pricing page says "1 credit = $0.01 USD".
- **Wire value:** the exact model name the API accepts, such as `v3.1-20260211`. It has a date in it, so it names one fixed version.
- **DCC (digital content creation) tool:** the trade's word for an authoring tool such as Blender.
- **Computer Use:** Claude operating a program by looking at screenshots and sending clicks and keys, as a person would.

## Summary

### What exists

Seven arrangements were found. Five are published by the vendors themselves.

| | Workflow | Who publishes the connecting part | Needs a Blender window |
|---|---|---|---|
| 1 | Claude Code runs Tripo's CLI as a shell command, guided by the Agent Skill bundled in the package; Blender is run headless as now | Tripo (official) | No |
| 2 | The same CLI started as an MCP server (`tripo mcp`) | Tripo (official) | No |
| 3 | `tripo-mcp` plus Tripo's Blender add-on | Tripo's company (official, "alpha", unchanged since April 2025) | Yes |
| 4 | MCP for Blender (the community `blender-mcp`) with its `generate_3d` tool | One developer | Yes |
| 5 | Blender Lab's MCP server, with Tripo reached by workflow 1 or 2 | Blender's own developers | No (it has a background mode) |
| 6 | No MCP and no CLI: a script calls Tripo's HTTP API, and `bpy` scripts run through `tools/bl` | Nobody; it is ordinary code | No |
| 7 | A person generates in Tripo Studio (the web app); Claude then works on the file in Blender | Tripo describes it in an article | Yes |

### What the evidence supports

- **Tripo's CLI is the vendor's current answer to "Claude plus Tripo", and it is headless by design.** The package (`tripo-cli` 0.5.2, MIT) turns one command into create, poll, download; writes a `task.json` beside each model with the request, the seeds and the credits; and ships its own instructions for coding agents. Run as an MCP server it offers five tools, read from its source: `tripo_make`, `tripo_task_get`, `tripo_task_wait`, `tripo_balance`, `tripo_history` (section 1).
- **Neither Tripo route touches Blender.** The CLI and its MCP mode generate and download. Anything in Blender is a separate step (sections 1 and 2).
- **The community Blender MCP has Tripo built in, but only for paying subscribers of that project, and not with the user's own Tripo key.** Its source says "Tripo is only available with MCP for Blender Premium". Its `generate_3d` tool exposes a prompt or image and a quality level, and none of Tripo's game parameters: no face limit, no seed, no quad, no texture size (section 4).
- **The earlier note's open question about background mode is now answered from source.** The community server refuses: "cannot start server in background mode (blender -b) - commands would never execute". Blender Lab's server supports it two ways: tools ending `_for_cli` that start `blender --background` for one call, and a command that runs its add-on's server inside a background Blender (sections 4 and 5).
- **Every MCP route into Blender runs LLM-written Python with no real barrier, and both projects say so.** Blender Lab: "without any guards in place to protect your data". Its own source calls its sandbox "not really a sandbox". The community project has a closed report of remote code execution through `exec()`, a closed report of hidden instructions in its tool descriptions, and a closed report of a file-write flaw (sections 4 and 5).
- **Tripo documents the things kiln would need for repeatability, with caveats.** Seeds (`model_seed`, `texture_seed`, `image_seed`), dated model versions, and task IDs are all documented. Output links are short-lived: the documentation says "temporary" and the CLI's source says "expire in ~5 minutes". The CLI picks a different model (`tripo-p1`) by itself when the face budget is 20,000 or less (section 1).
- **The Tripo article the earlier note mentions describes workflow 7, not an automated chain.** A person generated, rigged and animated a character in Tripo Studio and exported a GLB. Claude Opus 5.5 then imported it into Blender, read it through `bpy`, repaired the rig, built a stage and rendered a video. People made "the creative calls ... plus final sign-off" (section 7).

### What the evidence does not settle

- **Whether any of these produces a better static game asset than a fixed script.** No source was found that measures it. The published demonstrations are of characters and scenes, by the vendor, on one asset each.
- **Whether Tripo's seed returns the same file twice.** Still a vendor claim, as in the earlier note.
- **What a Tripo raw output for a prop looks like as a mesh.** Unchanged from the earlier note.
- **Who owns a model generated through MCP for Blender Premium.** The generation runs on that project's account with Tripo, not the user's. Its terms were not read for this point.
- **Whether a pay-as-you-go API customer is a "Paid User" under Tripo's terms.** Unchanged from the earlier notes; the clause was re-read today and still does not define it.

### The smallest experiments

In order of cost: read what the CLI would send without spending anything (`tripo make ... --dry-run --json`, which its documentation says makes "zero network calls" and "works without an API key"); then one reference image generated twice with the same seed and both files taken into kiln; then the earlier note's fixed-script-against-Claude comparison on whatever fails a check. Section 13 gives the detail.

## 1. Tripo's CLI, run by Claude Code as a shell command

### The moving parts

| Part | Maintainer | Licence | Where | State on 2026-10-08 |
|---|---|---|---|---|
| `tripo-cli` | Tripo. Its documentation says to install it; the npm package is published from two personal npm accounts | MIT (package record) | [npm registry record](https://registry.npmjs.org/tripo-cli); [documentation](https://developers.tripo3d.com/en/docs/cli) | 0.5.2, published 2026-10-08. First published 2026-07-22; ten versions since. Needs Node.js 20 or later |
| The bundled Agent Skill | Tripo | In the package | `skill/` inside the package: `SKILL.md`, seven command pages, six recipes, an error table | Same version |
| Tripo API v3 | Tripo | Terms of service | [API documentation, full text](https://developers.tripo3d.com/llms-full.txt) | H series `v3.1-20260211`; P series `P1-20260311` and `P2-20260801` (preview) |
| Claude Code | Anthropic | Commercial | [headless mode](https://code.claude.com/docs/en/headless.md) | |
| Blender | Blender Foundation | GPL | `tools/bl` in this repo | 5.2.2, pinned |

The package's record names its source repository as `github.com/vast-enterprise/Tripo-API-CLI`. That address returned "Not Found" when asked through GitHub's API, so the source is either private or moved. What was read is the published package itself: 73 files, built JavaScript that is readable, not obfuscated.

### What happens, step by step

1. **Claude reads the skill.** The package carries instructions written for an LLM. They can be printed with `tripo docs --llm` or `tripo docs --topic examples/game-asset`. The skill's first line: "You (an AI coding agent) can generate production-ready 3D assets with the `tripo` CLI" (vendor claim).
2. **Claude checks the plan without spending.** `tripo make <input> --dry-run --json` prints the request it would send for every API call, with "zero network calls and no credits". The skill tells agents to do this first.
3. **Claude runs one blocking command.** `tripo make reference.png --json --yes`. The CLI works out the route from the input (source and documentation):

| What is passed | What the CLI calls |
|---|---|
| Quoted text | `POST /v3/generation/text-to-model` |
| One image file or image URL | `POST /v3/generation/image-to-model` |
| Two to four images | `POST /v3/generation/multiview-to-model` (front is required) |
| A model file | `POST /v3/models/import` |
| A task ID, or `@last` | Further processing of that task |

4. **Tripo generates.** The CLI polls and downloads. It writes the model, a `preview.png` if the server made one, and `task.json`, into `./tripo-out/<name>-<id>/`.
5. **Optional further Tripo steps**, chained with `--then`: `refine`, `texture`, `stylize`, `convert`, `import`, `rig-check`, `rig`, `retarget`, `segment`, `complete`, `decimate`, `smartsegment`. Each is one more API call and one more charge.
6. **Claude looks at `preview.png`.** The skill says: "Look at `preview.png` to judge quality; re-roll with `tripo redo` if needed." `tripo redo` sends the same request with a new seed.
7. **Blender is not involved.** Whatever happens next (taking the file into kiln, review pictures, `tools/bl` scripts) is outside the CLI.

### The parameters that matter for a game asset

All from the API documentation unless marked. The CLI passes any of them through with `-p key=value`.

| Parameter | Where | What the documentation says |
|---|---|---|
| `face_limit` | Generation | "Maximum polycount for the output mesh." Without it, "adaptive topology". Documented guidance: "Game-ready assets: **50,000 – 100,000**. Web/mobile: **10,000 – 50,000**" |
| `smart_low_poly` | Generation, H series | "hand-crafted, clean topology style. Best suited for simple, non-complex inputs. Complex models may occasionally fail." Fixes the range to 500 to 20,000 triangles |
| `quad` | Generation, convert, retopology | Quads instead of triangles. "Enabling `quad` will force the output format to `FBX`" |
| `pbr`, `texture` | Generation | Both default true. PBR gives `base_color`, `metallic`, `roughness`, `normal` |
| `texture_quality` | Generation, texture | `fast`, `standard`, `detailed`, `extreme` ("8K textures") |
| `delight` | Generation | Default true; removes baked-in lighting; only the `v3.5-20260815` texture model reads it, and the default texture model is `v3.0-20250812`, so it does nothing unless `texture_version` is set (corrected from the [later note](tripo-guidance-and-blender-scripting.md)) |
| `model_seed`, `texture_seed`, `image_seed` | Generation | "Using the same seed with the same input will produce an identical 3D mesh" (vendor claim) |
| `auto_size` | Generation | Default **false**. When on, "the model size will be in meters" |
| `export_orientation` | Generation, convert | Default `+x` forward. The documentation warns that setting it at generation can make later steps return "a wrongly-oriented result while the task still reports `status: success`", and says to set it in the final convert instead |
| `texture_size`, `texture_format` | Convert | Defaults `4096` and `JPEG` |
| `pivot_to_center_bottom`, `scale_factor`, `pack_uv` | Convert | Off, `1`, off |
| `model`, `face_limit`, `bake`, `quad` | Retopology (`POST /v3/mesh/decimate`) | `v2.0` "smart highpoly-to-lowpoly retopology"; `v1.0` "basic decimation". `bake` default true, on v2.0 only |

Two behaviours of the CLI itself, from its source and bundled documentation:

- **It changes the model by the face budget.** "A low-poly request or face budget of 20,000 or less selects `tripo-p1`; other work defaults to `tripo-v3.1`." So two requests that differ only in `face_limit` can go to two different generators. `--model` overrides it.
- **Presets exist.** `--for game-mobile` means model P1, `face_limit` 15000, standard textures, then convert to FBX with 2048-pixel textures. `--for game-pc` means v3.1 with detailed textures, then FBX. Neither preset ends in a `.glb` as its main deliverable, and neither sets a size or orientation.

Tripo's own skill text (in its [plugin for another agent](https://github.com/VAST-AI-Research/Tripo3D-Plugin-dsh), same recipes) states a limit a pipeline has to know: "**`decimate`'s face budget is a target, not a ceiling** — a 1500-face request can come back at ~1900 triangles ... Generation's own `face_limit` does hold as an upper bound".

### Unattended and repeatable?

- **Unattended: yes, by design.** "Non-TTY runs are automatically headless (`--json --yes --no-open`)". Standard output is one line of JSON. Exit codes are fixed: 0 success, 2 bad parameters, 3 sign-in, 4 no credits, 5 content policy, 6 task failed, 7 network, 8 not found, 9 rate limited.
- **Signing in needs a person once**, in a browser, or an API key in the `TRIPO_API_KEY` environment variable.
- **`--yes` is switched on automatically when no terminal is attached.** An agent's command therefore spends credits without the confirmation a person would see. The CLI checks the balance first and prints the plan to the error channel. Tripo's skill for the other agent adds a rule in words ("Plan first, run after the user confirms"); that is an instruction to the LLM, not a lock (inference).
- **Repeatable, as far as Tripo's claim holds.** `task.json` is described as "request + seeds + credits", and the documented way to make the same shape again is to read `model_seed` from it and pass `--seed`. Model names are sent as dated wire values.
- **Links do not last.** The SDK page: "Generated model URLs are temporary" and "Do not store a temporary signed URL as a permanent asset." The CLI's source: "Output URLs expire in ~5 minutes, so downloads happen immediately". A task can later have the status `expired`: "output files are no longer available". No retention period is stated.
- **`tripo batch run manifest.yaml`** runs a list of jobs with retries and keeps a state file so a second run skips the jobs that succeeded.

### What Claude's part adds over a fixed script

- Choosing parameters from a sentence, reading `preview.png`, and deciding to `redo`. Those are the only judgement steps in this workflow.
- A fixed script can run the same command. The CLI itself needs no LLM. Its `tripo ai` planner can use one, through any OpenAI-compatible endpoint the user configures; that is optional and was not looked at further.
- No evidence was found that an LLM's choice to regenerate from `preview.png` gives a better asset than a person's at shape review.

### Cost

From Tripo's [API pricing page](https://developers.tripo3d.com/en/pricing), H series tab, in credits (one credit is $0.01):

| Step | Credits |
|---|---|
| Image to 3D, standard texture | 30 |
| Text to 3D, standard texture | 20 |
| Add-ons on a generation: HD Texture +10, 8K Ultra Texture +20, HD Geometry Quality +20, Quad Mesh +5, Smart Low-poly +10, Generate Parts +20 | |
| Texture again: fast or standard 10, HD 20, 8K 30 | |
| Convert: basic 5; "advanced" 10 when any of `quad`, `face_limit`, `flatten_bottom`, `texture_size`, `texture_format`, `pivot_to_center_bottom`, `scale_factor` is set | |
| Retopology: v2.0 Smart 30; v1.0 Basic 10 | |

- **Arithmetic:** image to 3D with smart low-poly, then a convert that sets texture size, is 30 + 10 + 10 = 50 credits, $0.50.
- **P series prices** are on a tab of that page that was not read. Tripo's own skill text says P2 "Costs 100+ credits per generation versus 30–50 for P1", and a Tripo article puts a P2.0 asset at "approximately USD 1.20".
- "Failed and cancelled tasks are not charged."
- Claude's tokens come on top, as worked in section 6 of the earlier note.

### Setup

- Node.js 20 or later; `npm install -g tripo-cli`; a Tripo account and API key. Nothing in the package is specific to an operating system except notes for Windows; Linux is not named and not excluded.
- The documentation read is on `developers.tripo3d.com` and gives the API address `openapi.tripo3d.com`. The package README says the international service is `openapi.tripo3d.ai` with its console at `developers.tripo3d.ai`, and that the CLI detects which one a key belongs to.
- No plan tier is named for the API or the CLI: "Simple, transparent pay-as-you-go pricing." The documentation says "New accounts receive free credits". Tripo's terms give free users no rights in outputs (earlier note), so a model made on free credits is not usable in a sold game (inference).

## 2. Tripo's CLI as an MCP server

The same package. `tripo mcp` starts it as a stdio MCP server. The file header in its source: "MCP (Model Context Protocol) server over stdio, exposing the CLI's capabilities as tools for Cursor / Claude Desktop / any MCP client ... Self-contained: no SDK dependency".

### The tools, from source

| Tool | Parameters | What it does |
|---|---|---|
| `tripo_make` | `input` (required: prompt, image path or URL, or task ID), `scenario` (one of the seven presets), `then` (a processing chain), `model` (`tripo-v3.1`, `tripo-p1` or `tripo-p2`), `output_dir` | "Blocks until finished; downloads artifacts locally and returns file paths" |
| `tripo_task_get` | `task_id` | Status of a task |
| `tripo_task_wait` | `task_id`, `download` | Waits, then downloads |
| `tripo_balance` | none | Credit balance |
| `tripo_history` | `limit` | Recent tasks made by this CLI |

### How it differs from workflow 1

- **Fewer controls.** `tripo_make` has no parameter for `face_limit`, a seed, `quad`, texture settings or any other API parameter, except what a preset or a `then` step carries (for example `decimate:5000`). The shell command has all of them through `-p` and `--seed`. So the MCP mode cannot ask for a fixed seed (source).
- **No dry run** in the tool list.
- **It blocks.** One call lasts as long as the generation. The community Blender MCP's source notes that MCP clients built on the TypeScript SDK "cut tool calls off at 60 s by default". Whether Claude Code or Claude Desktop cuts off a `tripo_make` call was not established (unverified).
- **It is for clients that cannot run a shell**, such as Claude Desktop. Claude Code can run the command directly (inference). Tripo's own article on Claude points at the CLI, "built for AI agents like Claude Code", and does not mention the MCP mode.

Everything else (models, cost, links, sign-in) is as in section 1.

## 3. `tripo-mcp` with Tripo's Blender add-on

### The moving parts

| Part | Maintainer | Licence | Where | State |
|---|---|---|---|---|
| `tripo-mcp` | VAST-AI-Research, Tripo's company. Repository description: "Official MCP server for Tripo" | MIT | [GitHub](https://github.com/VAST-AI-Research/tripo-mcp) | Version 0.1.2. Last commit 2025-04-14. 210 stars. Seven of its nine issues are open, most from March and April 2025 with reports of failing calls |
| Tripo 3D Blender add-on | The same | MIT | [GitHub](https://github.com/VAST-AI-Research/tripo-3d-for-blender) | Source says version 0.7.7, for Blender 3.0.0 or newer; last commit 2025-11-06. Tripo's plugins page offers 0.7.3 for "3.0+" |

The README: "This project is in alpha. Currently, it supports Tripo Blender Addon integration."

### What happens

1. A person opens Blender, enables the add-on and enters a Tripo API key in its panel. The add-on starts a socket server on port 9876 (source).
2. Claude Desktop or Cursor starts `tripo-mcp`. The server asks the add-on for the API key over the socket (`get_tripo_apikey`, source).
3. Claude calls `create_3d_model_from_text(describe_the_look_of_object, face_limit)` or `create_3d_model_from_image(image, face_limit)`. These are the only generation tools and `face_limit` is the only game parameter.
4. Claude must call `get_task_status(task_id)` again and again until it finishes. The tool's own text: "3D model generation takes 3-5 minutes. You need to repeatedly call get_task_status until completion."
5. Claude calls `import_tripo_glb_model(glb_url)` and the add-on imports the file into the open scene.
6. The server also carries a copy of the early community tools: `get_scene_info`, `get_object_info`, `create_object`, `modify_object`, `delete_object`, `set_material`, `execute_blender_code`, and five Poly Haven tools.

### Limits

- **It needs an open Blender window** with the add-on's panel (README and source).
- **It is on the older API.** It calls Tripo through the Python SDK, and Tripo's SDK page says "Python remains primarily a V2 SDK". The v3 parameters in section 1 are not reachable from it (inference from the two sources).
- **No seed, no model choice, no file kept.** The model goes from a temporary link straight into the Blender scene. Nothing is written as a raw output unless Claude is told to export it.
- **The add-on runs code sent over the socket** with Python's `exec` (source), with no check.
- **Whether the add-on works on Blender 5.2** is not stated by Tripo (the earlier notes found the same).
- Tripo's newer documentation does not mention this server at all. It describes the CLI. That suggests the CLI replaced it; Tripo does not say so (inference).

## 4. MCP for Blender (the community server) and its `generate_3d` tool

### The moving parts

| Part | Maintainer | Licence | Where | State |
|---|---|---|---|---|
| MCP for Blender, formerly `blender-mcp` | Siddharth Ahuja, one developer. "This is a third-party integration and not made by Blender" | MIT | [GitHub](https://github.com/ahujasid/mcp-for-blender) | 2.1.9 on PyPI, 2026-10-06. Last commit 2026-10-06. 30,237 stars, 38 open issues. Add-on version 1.8, for Blender 3.0 or newer |
| MCP for Blender Premium | The same developer, a paid service | Terms on its site | [Premium page](https://www.mcp-for-blender.com/premium) | Hobby $10, Pro $20, Max $100 a month |

It has two halves: an add-on that opens a socket inside a running Blender, and an MCP server the client starts with `uvx mcp-for-blender`. For Claude Code the README gives `claude mcp add blender uvx mcp-for-blender`.

### The tools

The README lists nine: `execute_blender_code`, `look`, `get_scene_info`, `generate_3d`, `search_assets`, `import_asset`, `get_addon_status`, `disable_telemetry`, `record_trajectory_feedback`.

- `execute_blender_code`: "Run Python in your live Blender".
- `look`: pictures of the result from the viewport, a camera, several angles, or frames of an animation, drawn solid, with materials, rendered, as wireframe or as x-ray.
- `generate_3d`: "One call to generate and import a model with Tripo, Hunyuan3D or Hyper3D Rodin."

### The Tripo integration, from source

- **Premium only.** `generation.py`: "Tripo is only available with MCP for Blender Premium." The Premium page: "you also get Tripo, which isn't available with your own keys". With the user's own keys only Hunyuan3D and Hyper3D Rodin are offered. This corrects the earlier note's table, which listed Tripo beside the other two without the condition.
- **Parameters of `generate_3d`:** `prompt` or `image` (a file path or URL; "Images attached in chat can't be passed"), `name`, `provider`, `quality` ("standard" or "high"), `bbox_condition` (Rodin only), `job`. For Tripo the request carries only the prompt or image and the quality. There is no face limit, seed, quad, texture size or model version.
- **What comes back** is an object in the open Blender scene, not a file. The tool's own description: "It arrives at arbitrary scale and facing."
- **It waits at most 45 seconds for each call**, then returns a job handle to call again, because of the 60-second cut-off noted in section 2.
- **Which Tripo models:** the Premium page says standard generations use "Hunyuan3D v3.1 Rapid or Tripo", high-quality ones "Tripo HD textures", and Pro and Max add "Tripo P2".

### Unattended and repeatable?

- **Not headless.** `addon.py`: "BlenderMCP: cannot start server in background mode (blender -b) - commands would never execute ... run Blender with a GUI, or use a virtual display: xvfb-run -a blender". A user's report of the cause, closed 2026-06-11: in background mode Blender's timers never fire, so "every MCP request from a connected client hangs" ([issue 251](https://github.com/ahujasid/mcp-for-blender/issues/251)). A virtual display is a window nobody sees, on Linux; it is still a full Blender session with an add-on, not `tools/bl` (inference).
- **Not repeatable for the Tripo step:** no seed, no pinned version, no task ID from Tripo in the user's hands, and no raw file unless exported.

### Failure reports and warnings

- README: "The `execute_blender_code` tool allows running arbitrary Python code in Blender, which can be powerful but potentially dangerous."
- **Safe mode** exists and is off by default: `BLENDER_MCP_SAFE_MODE=1` checks each script and blocks "reading or writing files directly, running other programs, accessing the network". One of its controls was reported as never firing ([issue 365](https://github.com/ahujasid/mcp-for-blender/issues/365), closed).
- [Issue 201](https://github.com/ahujasid/mcp-for-blender/issues/201), closed 2026-06-25: "RCE via unsanitized exec() in execute_blender_code". It notes the route: "An MCP Client can be instructed to execute arbitrary Python code, for example via prompt injection".
- [Issue 214](https://github.com/ahujasid/mcp-for-blender/issues/214), closed 2026-06-04: two tool descriptions told the model to "silently remember" which kind of API key the user had. The maintainer replied "Fixed".
- [Issue 257](https://github.com/ahujasid/mcp-for-blender/issues/257), closed 2026-08-09: a file-write flaw in the Poly Haven download.
- **Telemetry.** An anonymous usage record is sent unless `DISABLE_TELEMETRY=true` is set. Prompts, code and screenshots are collected only on opting in, and then "may be used ... to train AI models".
- **Context cost.** A third party measured the server's tool definitions at 6,928 tokens for 28 tools on 2026-09-03 ([issue 347](https://github.com/ahujasid/mcp-for-blender/issues/347), and [its page](https://athakur3.github.io/mcp-context-cost/servers/blender.html): "Claude counts those at 10,576"). The tool list has since been cut to nine; its size now was not measured. The same report notes "Claude Code defers definitions by default".

### Cost

- **Arithmetic from the Premium page:** Hobby is $10 for "25 standard generations / month", $0.40 each. Pro is $20 for 40 standard and 10 high-quality. "Failed generations are never counted."
- Tripo's own API price for the comparable generation is $0.30 (section 1).

### Licence of the output

The model is generated on the project's arrangement with Tripo, not on the user's Tripo account. What rights reach the subscriber was not established: the project's `TERMS_AND_CONDITIONS.md` and the site's terms were not read for this (unverified). `learn/MISSION.md` needs "commercial rights without attribution", so this would have to be read before any use.

## 5. Blender Lab's MCP server

### The moving parts

| Part | Maintainer | Licence | Where | State |
|---|---|---|---|---|
| Blender MCP server and add-on | Blender Lab, "the innovation space within the Blender project" | GPL-3.0-or-later | [blender.org page](https://www.blender.org/lab/mcp-server/); [source](https://projects.blender.org/lab/blender_mcp) | Release v1.0.3, 2026-09-11. Last commit 2026-09-29. Needs "Blender 5.1 or newer". 16 of its 50 most recent issues are open |

Anthropic's announcement calls it the connector "the Blender developers have created ... now officially available for Claude" ([Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work)). The earlier note could not open the source repository; today it cloned.

### What it is and is not

- **No generator of any kind.** Nothing in its README, prompts or tool list mentions Tripo or any other generator. To use Tripo with it, the model file has to arrive by workflow 1, 2 or 6.
- **Its stated purpose is inspection and scripting**, not making assets: "a natural language interface with Blender's Python API, improving access to documentation, and allowing users to explore and understand complex setups". Among the prompts its page lists as "yet to be explored": "Find objects that have meshes with bad normals" and "Verify this checklist:: meshes must be manifold, all objects must have materials, naming must follow convention".
- **It carries the Blender manual and Python API reference** for the version it was built against, as files the LLM can search (`search_api_docs`, `search_manual_docs`, `get_python_api_docs`). The commit of 2026-09-11 is "Update 5.2: manual & API". The earlier note records a benchmark finding that most outright failures of LLM-written Blender scripts were calls to the wrong version's API.

### The tools, from its generated tool list

- **Code:** `execute_blender_code` (in the connected Blender) and `execute_blender_code_for_cli` ("Execute Python code in a background Blender process").
- **File summaries**, each also in a `_for_cli` form that opens a `.blend` file in background Blender: data-blocks, missing files, linked libraries, path info, a guess at what the file is for.
- **Objects:** `get_objects_summary`, `get_object_detail_summary`.
- **Pictures:** `get_screenshot_of_window_as_image`, `get_screenshot_of_area_as_image`, `render_viewport_to_path`, `render_thumbnail_to_path`.
- **Navigation of the window:** four `jump_to_...` tools.
- **Documentation:** the three above.

### Headless?

Yes, in two ways, both from source:

- **One call, one Blender.** `execute_blender_code_for_cli(blend_file, code)` runs `blender --background <blend_file> --python-expr <code>` and returns what the code puts in a variable named `result`. It opens a `.blend` file, and the command line it builds has no `--factory-startup` and no `--offline-mode`, the two switches `tools/bl` adds.
- **A background server.** The add-on registers a command: "Started via `blender --background file.blend --command blender_mcp`". Its help text: "Deferred responses are not supported in background mode; each request must complete before returning."
- **Screenshots do not work in background mode** ("Screenshots are not available in background mode"); the render tools do.
- Open issues report the `_for_cli` tools hanging on Windows. None was found for Linux.

### Warnings

- The page: "The MCP server will execute LLM generated code in Blender without any guards in place to protect your data from removal or being sent to a remote location. To keep your data safe it is recommended to use a virtual machine, or a system without access to sensitive information."
- Its `weak_sandbox.py`: "Note that this isn't really a sandbox, more guidance that some things should not be done ... If the LLM (or its user) is motivated these can be worked around." It blocks `sys.exit()` and a short list of operators such as quitting Blender.
- An open issue asks about context growth from `get_objects_summary`.

### Cost and licence

Free. The GPL covers the server and add-on. What is made with Blender is the user's (earlier note, from Blender's licence page).

## 6. No MCP and no CLI: Tripo's HTTP API from a script, and `bpy` through `tools/bl`

### What it is

Two different things, which the earlier note already separated:

- **Claude writes the code once.** A Python module in kiln creates a Tripo task, polls it, downloads the file and takes it in as a raw output. Fixed Blender scripts do the rest, as now. Claude is the programmer, not a part of the run.
- **Claude is in the run.** Claude Code (interactively, or started by a script as `claude -p "<task>" --allowedTools "Bash,Read"`) calls the API or the CLI, runs `tools/bl` scripts, reads the review pictures, and writes a new script when a check fails.

### The API calls, by name

All under `https://openapi.tripo3d.com/v3` in the documentation read (the international address is in section 1), with `Authorization: Bearer <key>`:

1. `POST /files` uploads the reference image and returns a `file_token`. (An image URL is also accepted.)
2. `POST /generation/image-to-model` with `input`, `model` (required, a dated wire value) and the parameters in section 1. It returns a task ID.
3. `GET /tasks/{task_id}` until the status is final. A webhook is the documented alternative.
4. Download the model at once.
5. Optionally `POST /mesh/decimate`, `POST /models/texture`, `POST /models/convert`, each taking the earlier task ID as `input`.

- **Official libraries:** JavaScript, Go, Rust and Java cover v3. "Python remains primarily a V2 SDK": of the v3 routes it reaches only segmentation, task query and file upload. Kiln is "standard library only" Python, and the calls above are plain HTTP with JSON, which the standard library can make (inference).
- **Limits:** ten H-series generations at once, five P-series, and **one** image-generation task at once ([rate limits](https://developers.tripo3d.com/en/docs/rate-limits)).

### Unattended and repeatable?

- **Yes for the fixed-code form.** It is ordinary code with a key.
- **The Claude-in-the-run form runs unattended too.** `claude -p` runs "non-interactively"; the documentation notes that such a session "shows no workspace trust dialog", and that `--bare` skips MCP servers, skills and `CLAUDE.md` "for CI and scripts where you need the same result on every machine". Anthropic's hosted API cannot do this alone: its MCP connector cannot reach a local server and its code sandbox has no Blender (earlier note).
- **Repeatability is the same split the earlier note drew.** The generation is as repeatable as Tripo's seed. The Blender scripts are repeatable. An LLM choosing steps for each asset is not.

### What Claude's part adds

- In the fixed-code form: nothing at run time. This is the baseline every other workflow should be compared with.
- In the other form: reading pictures, deciding to regenerate, and writing a one-off repair. The evidence for that is in section 9.

### Cost

Tripo's credits as in section 1. For Claude in the run, the earlier note's arithmetic: about $0.13 for one look at a set of review pictures on Opus 5.5; $1.69 to $4.08 for an eight-try loop with caching.

## 7. A person generates in Tripo Studio; Claude finishes in Blender

This is the workflow of the Tripo article the earlier note cites: [How to Make 3D Models with Claude Opus 5.5](https://www.tripo3d.ai/blog/how-to-make-3d-models-with-claude-opus-5-5), published 2026-09-24. *Vendor-run*, one character.

### Exactly what was done, as the article tells it

1. **Generate** "in Tripo Studio with the P2.0 model and a reference image". The web app, by a person. P2.0 "generates native quad topology (up to 25,000 quad faces, or 50,000 triangles), separates the body, clothing and accessories into independent parts".
2. **Rig** in Tripo Studio: "choose Humanoid", preset "VRM 1.0 Humanoid".
3. **Animate** in Tripo Studio with a dance preset, "just under 13 seconds". Export as GLB "with textures and animation turned on".
4. **Inspect in Blender.** "Instead of eyeballing the viewport, Claude imported the GLB and read the file through Blender's Python API. In a couple of minutes it had checked": the skeleton and animation clip; "that every texture was linked and loaded"; "mesh health: no loose vertices or degenerate faces, and the open edges all sit on hair and clothing shells, which is normal for this style"; which bones drive which parts; "where the feet meet the floor on every frame".
5. **Fix.** The tail followed the leg bones. Claude "added a six-bone tail chain from the hips, rebuilt the weights along the tail". For clothing cutting through legs it "attached invisible collision capsules ... and let a Shrinkwrap modifier push anything inside them back out, which removed most of the visible clipping. Hands brushing the body on a few frames would still need a pass from an animator."
6. **Build a stage.** "the first attempt, a pink LED dot wall, fought with the outfit", so a second was made.
7. **Render** "with EEVEE at 1440×720 ... on a local GPU through Computer Use took about ten minutes".

"Who did what", in the article's words: "Tripo: the mesh, textures, full-body rig and dance animation. Claude Opus 5.5: inspection, rig fixes, clipping, grounding, stage, lighting, camera and rendering. Human direction: the creative calls ... plus final sign-off."

### What the article does not say

- Which connection Claude used to reach Blender. It says Claude drives tools "through Computer Use or MCP" and names no MCP server. A sister article with another LLM names the community server (below).
- Any numbers: no triangle count, no token cost, no time for the whole job, no files.
- Whether the mesh checks were reported by Claude or confirmed by a person. The article itself warns, in its own table: "A clean text report doesn't mean the model is production-ready" and "It doesn't replace real geometry checks and human review."
- It ends by pointing at the CLI ("or let Claude drive Tripo directly with the Tripo CLI"), but the walkthrough did not use it.

### Tripo's sister articles, with a different LLM

Same vendor, same pattern, GPT-6 Astra in Claude's place. They show which wiring Tripo's own writers use.

- [3D character workflow](https://www.tripo3d.ai/blog/gpt-6-astra-3d-character-workflow) (2026-09-08): Tripo Studio by hand, then the community Blender MCP: "a configured Blender MCP connection between your assistant client and Blender", with a link to `ahujasid/blender-mcp`. It advises: "Before allowing scene edits, start with a read-only check."
- [3D game scene workflow](https://www.tripo3d.ai/blog/gpt-6-astra-3d-game-scene-workflow) (2026-09-18): Tripo CLI plus Unreal Engine's MCP, no Blender. "I used it with Tripo CLI and Unreal MCP to build a playable medieval game scene".
- [Tripo P2.0 vs GPT-6 Astra](https://www.tripo3d.ai/blog/tripo-p2-vs-gpt-6-astra) (2026-09-24): the only numbers. "In the three recorded tests, Tripo P2.0 generated each textured asset in 26 seconds at approximately USD 1.20, while GPT-6 Astra took 24m 17s to 47m 46s, with estimated API-equivalent costs of USD 7.81–8.81", the LLM working "through a Blender MCP workflow". Three assets, vendor-run, and it measures the LLM building the asset alone, not the LLM finishing a generated one.

## 8. Other published pieces

None of these was read beyond its repository record and the top of its README. They are listed so the owner knows they exist, not as recommendations.

### Other ways to reach Tripo

| Repository | What it says it is | Licence, stars, last push |
|---|---|---|
| [`mordor-forge/trident-mcp`](https://github.com/mordor-forge/trident-mcp) | A stdio MCP server in Go that "currently uses the Tripo v3 API"; needs `TRIPO_API_KEY`; writes models to a folder | Apache-2.0, 5, 2026-07-09 |
| [`pavlov-net/tripo3d-rs`](https://github.com/pavlov-net/tripo3d-rs) | "Unofficial Rust tooling": an SDK, a CLI and an MCP server in which "Every Tripo operation shows up as an MCP tool" | MIT, 5, 2026-10-07 |
| [`lixmal/tripo-mcp`](https://github.com/lixmal/tripo-mcp) | "Small MCP server for the Tripo 3D generation API" | MIT, 0, 2026-10-05 |
| [`MeterLong/tripo-skills`](https://github.com/MeterLong/tripo-skills) | "AI 3D model generation skill for Claude Code, Codex CLI & ChatGPT" | No licence, 2, 2026-03-04 |
| [`theisegoria/game-development-studio`](https://github.com/theisegoria/game-development-studio) | A command-line program and skills "for Codex and Claude" that "Drives Tripo 3D ... through explicit, per-invocation spend authorization" and "normalizes meshes through Blender", with provenance records | MIT, 11, 2026-10-05 |

### Other ways to reach Blender without a window

| Repository | What it says it is | Licence, stars, last push |
|---|---|---|
| [`sandraschi/blender-mcp`](https://github.com/sandraschi/blender-mcp) | "the server runs Blender headless in the background"; a bridge add-on is optional | MIT, 55, 2026-10-02 |
| [`ellmos-ai/ellmos-blender-use-mcp`](https://github.com/ellmos-ai/ellmos-blender-use-mcp) | "No add-on. No TCP port. No background daemon ... Each call spawns `blender --background --python <script.py>`"; aimed at checking exported files | MIT, 2, 2026-10-02 |
| [`lxsolutions/studio-foundation`](https://github.com/lxsolutions/studio-foundation) | "a deterministic headless-Blender asset forge for AI agents: 138 whitelisted, typed operations"; not MIT (a source-available licence) | 29, 2026-09-14 |

### Tripo's packages for other agents

- **A plugin for OpenAI's Codex**, documented by Tripo: "this plugin only works in Codex". It shows "two capabilities: generate a 3D asset, and build game-ready assets" ([Codex plugin page](https://developers.tripo3d.com/en/docs/codex-plugin)).
- **A skills-only plugin for DeepSeek Harness**, [`Tripo3D-Plugin-dsh`](https://github.com/VAST-AI-Research/Tripo3D-Plugin-dsh), with two skills, `tripo-3d` and `tripo-game-asset`, that drive `tripo-cli` through the shell. Its README explains (in Chinese) why it registers no tools and no MCP server: the CLI holds the API contract and the skill is the operating manual.
- **No Claude Code plugin from Tripo was found.** For Claude Code, Tripo's documentation gives the CLI and a prompt to paste. The skill text inside the CLI package is in the same `SKILL.md` format Claude Code uses; whether it loads as a Claude Code skill unchanged was not checked (unverified).
- [`TripoGrowthLab/vibe-gaming-interactive-handbook`](https://github.com/TripoGrowthLab/vibe-gaming-interactive-handbook) is a prompt for a coding agent (it names Claude Code) that builds a browser game from simple shapes and then swaps in "the models you make in Tripo Studio". A person makes the models. Whether that organisation is Tripo's was not established.

### Not found

- No Agent SDK program or Claude Code subagent published for Claude plus Tripo plus Blender.
- No published pipeline that takes a Tripo model through headless Blender for Bevy.

A failed search is a gap in the search, not proof that none exists.

## 9. Where the reference image comes from

Claude "cannot generate, produce, edit, manipulate, or create images" (Anthropic's vision page, earlier note). Kiln's run is "given a reference image". The options found:

- **A person supplies it.** Every Tripo walkthrough above starts with "a reference image" and does not say where it came from.
- **Tripo's own image endpoints**, which resell other companies' image models:
  - `POST /v3/generation/text-to-image`. Models listed: `seedream_v4` (default), `seedream_v5`, `banana`, `banana_pro`, `banana2`, and a `chat_image` family. 5 to 50 credits by model, size and quality. Two of the listed models carry retirement dates (2026-10-23 and 2026-12-01).
  - `POST /v3/generation/image-to-image` edits an image from a prompt.
  - `POST /v3/generation/image-to-multiview`, 10 credits, makes four views from one image, for `multiview-to-model`.
  - `image-to-model` accepts the task ID of an image task as its `input`, so the picture never has to leave Tripo.
  - `image_seed` exists for the image stage.
  - In the CLI: `tripo generate text-to-image "..."`.
- **Skip the image: `text-to-model`.** `tripo make "a stylized barbarian axe"` goes straight from words to a model. Then there is no reference image to review the shape against, unless the preview is used as one (inference).
- **Any other image model**, called by Claude through a script. The file is then passed to Tripo by path or URL.
- **`enable_image_autofix`** (default false) lets Tripo "enhance low-resolution or low-quality images" before generating, which changes the input the shape is made from.

Not established: what rights Tripo's terms give in an image made through these endpoints, and whether the terms of the underlying image companies reach the user.

What Claude can do with a reference image is look at it: write the prompt for an image model, check that the picture shows one object on a clean background as Tripo asks ("clearly visible with a clean background and minimal occlusion"), and compare it with the review pictures (inference; its sight is documented as approximate, earlier note).

## 10. Side by side

"Source" means read in the code. "Claimed" means the vendor asserts it. "No evidence" means nothing was found either way.

| | 1. CLI in the shell | 2. `tripo mcp` | 3. `tripo-mcp` + add-on | 4. MCP for Blender | 5. Blender Lab MCP | 6. HTTP + `tools/bl` | 7. Studio by hand, Claude in Blender |
|---|---|---|---|---|---|---|---|
| Maintainer of the connecting part | Tripo | Tripo | Tripo's company | One developer | Blender's developers | The owner | None needed |
| Licence | MIT | MIT | MIT | MIT; Premium is a paid service | GPL-3.0-or-later | The owner's | n/a |
| Last release or commit | 2026-10-08 | 2026-10-08 | 2025-04-14 | 2026-10-06 | 2026-09-29 | n/a | Article 2026-09-24 |
| Reaches Tripo | Yes, API v3 | Yes, API v3 | Yes, older API | Only with Premium | No | Yes, API v3 | By hand |
| Reaches Blender | No | No | Open window | Open window | Open window or background | Background (`tools/bl`) | Open window |
| Face limit | Yes | Only through a preset or `decimate` step | Yes | No | n/a | Yes | In the web app |
| Seed | `--seed` | No | No | No | n/a | Yes | Not stated |
| Pinned model version | Yes, dated wire values; but P1 is auto-picked at 20,000 faces or fewer | Same | No | No | n/a | Yes, `model` is required | Chosen in the web app |
| Leaves a model file on disk | Yes, with `task.json` | Yes | No, imports into the scene | No, imports into the scene | n/a | Yes | Yes, exported |
| Runs with no person | Yes after sign-in | Yes after sign-in | No | No (refuses background mode) | Yes in background mode | Yes | No |
| Code-execution warning | None needed: it runs no LLM code | Same | Add-on uses `exec` (source) | README warning; three closed security reports; optional safe mode | Page warning; "not really a sandbox" | Whatever runs Claude's scripts; `tools/bl` adds factory settings and no network | As 4 or 5 |
| Evidence it works well | None found | None found | Open issues reporting failures in 2025 | Preprints and hands-on reports of an LLM building in Blender through it (section 11); none of its Tripo tool | One hands-on report of a costly session; a preprint shows it in pictures | None beyond the parts | One vendor article, one character |
| Tripo cost of one image-to-3D | $0.30 list | Same | Not on the v3 price list | $0.40 (arithmetic, Hobby) | n/a | $0.30 list | Studio credits |
| Licence of the output | Tripo's terms, by plan | Same | Same | Not established | n/a | Tripo's terms, by plan | Tripo's terms, by plan |
| Blender version | Any | Any | 3.0+ stated; 5.x not stated | 3.0+ stated | 5.1+ | Kiln's pin | Any |
| Linux | Not excluded | Same | Not stated | Install script covers "macOS / Linux" | No Linux issue found | Yes, as now | n/a |

## 11. Evidence on how well these work

Graded as the earlier note grades. Most of it is in that note's section 4 and is only pointed at here.

### On the Tripo step driven by an LLM

**None found.** No paper, vendor test or hands-on report was found that measures Claude (or any LLM) choosing Tripo parameters or deciding to regenerate, against a person or a fixed setting.

### On an LLM working in Blender through an MCP server

- *Preprint.* aDSL scored "BlenderMCP with Claude Opus 4.5" building objects alone: level with an open generator on text prompts, well behind on matching an input picture (earlier note, section 4.1). That is the community server used without a generator.
- *Preprint.* ViSculpt shows its own results beside "Blender's official MCP server with Claude Sonnet 4.6 writing scripts", in pictures only (earlier note, section 4.2).
- *Preprint.* Planner-Actor-Critic drove Blender through Blender-MCP with Hyper3D Rodin among its tools; judged mostly by eye, with no with-and-without comparison (earlier note, section 4.2).
- *Hands-on, second-hand.* The MindStudio report: "2 hours of back-and-forth, 60% of a 5x Max plan's session tokens consumed" on one scene through the Blender connector, with visible defects left (earlier note, section 4.3).
- *Vendor-run.* Tripo's three recorded tests of GPT-6 Astra building assets through "a Blender MCP workflow": 24 to 48 minutes and about $8 each, against 26 seconds and about $1.20 for Tripo (section 7 above). A different LLM, and an interested party.

### On an LLM finishing a generated asset in Blender

- *Vendor-run*, one asset: the Tripo article in section 7. A character, with rig repair; kiln handles static assets only.
- *Hands-on, by Tripo's account of others:* the GPT-6 Astra character article credits creators who assembled Tripo parts in Blender with an LLM. Their own posts were not opened.
- **No controlled measurement**, as the earlier note found.

### Failure reports from the repositories

All *hands-on*, one reporter each, with reproduction steps in most:

- Community server: background mode hangs (issue 251); remote code execution through `exec` (201); hidden instructions in tool descriptions (214); a file-write flaw (257); timeouts (243 on Windows, 279); "Hitting 40000 token/s limit on claude/anthropic way too easily" (33, from March 2025).
- Blender Lab server: large replies cut short (31, 49, fixed); `_for_cli` tools hanging on Windows (42, 58, 60, open); the server not binding when Blender's online access is off (45, open).
- `tripo-mcp`: "create_3d_model_from_text error" (3), "API Error: Received response code 403" (4), "failed to connect to cursor" (2), all open since March or April 2025.

### What it adds up to

The connecting parts are documented and, for the two vendor-maintained ones, current. What is missing is any measurement of the result on the kind of asset kiln makes. The only numbers anywhere are Tripo's own, and they are about time and cost, not about whether the asset passes a check.

## 12. Fit with kiln

**Everything in this section is inference** from the facts above and from `CLAUDE.md` and `CONTEXT.md`. It says how each workflow lines up with four properties kiln has today: the raw output is kept; a person does the shape review; `kiln rebuild` repeats a build without calling a generator; Blender runs headless, pinned, with factory settings.

| | Raw output kept | Shape review by a person | Rebuild without the generator | Headless pinned Blender |
|---|---|---|---|---|
| 1. CLI in the shell | Fits: it writes a `.glb` and a `task.json`; `kiln run --model` takes the file in | Unaffected. `preview.png` could tempt an LLM to pre-judge; kiln's review pictures remain the record | Fits: generation ends before kiln starts | Fits: Blender is not touched |
| 2. `tripo mcp` | Fits, same files | Same | Fits | Fits |
| 3. `tripo-mcp` + add-on | Does not fit: the model is imported into a scene, not kept | Bypassed unless a step is added | Does not fit as shipped | Does not fit: open window, add-on |
| 4. MCP for Blender `generate_3d` | Does not fit: same reason; and no seed or task ID to record | Bypassed unless a step is added | Does not fit as shipped | Does not fit: refuses background mode |
| 5. Blender Lab MCP | n/a (no generator) | Unaffected | Only if what Claude ran is saved as a script and becomes a stage | Partly: background mode exists, but its command line lacks `tools/bl`'s factory-settings and offline switches, and it wants a `.blend` file |
| 6. HTTP + `tools/bl` | Fits by construction | Unaffected | Fits in the fixed-code form; in the Claude-in-the-run form only if each script Claude writes is kept in the asset record | Fits |
| 7. Studio by hand, Claude in Blender | Fits for the exported file | A person is already choosing in the web app, before kiln sees anything | The Blender work is a live session, not a script | Does not fit |

Further points:

- **Workflows 1, 2 and 6 differ from each other less than they appear to.** All three end with a file on disk before kiln begins. The difference is who holds the API contract: Tripo's CLI (1 and 2) or kiln's own code (6). `learn/MISSION.md` asks that "the generator is called through one interface so it can be swapped"; a call to an external command and a call to an HTTP API can both sit behind such an interface.
- **What `task.json` holds is close to what the asset record's source text would need**: the request, the seeds, the dated model and the task ID. Kiln today records "licence" and "source" as text.
- **The CLI's automatic switch to P1** at 20,000 faces or fewer means a record of "face limit 15000" does not by itself say which generator made the shape. The dated wire value does.
- **Size and facing are kiln's to fix under every workflow.** `auto_size` is off by default, the default export faces +X, and the community tool says its result "arrives at arbitrary scale and facing".
- **An MCP server into Blender adds a second way to run Blender beside `tools/bl`.** `CLAUDE.md` calls `tools/bl` the way mesh stages run. Claude Code can already write a script and run it with `tools/bl`, and read the review pictures kiln renders, with no MCP server. What the Blender Lab server would add to that is its bundled manual and API reference for the right Blender version, and summaries of a scene.
- **Whether Claude sits in the run at all** is the earlier note's question, not this one's: a step an LLM chooses per asset is not repeated by `rebuild` unless the script it wrote is kept and replayed.

## 13. What is unknown, and the smallest experiment for each

1. **What the CLI would send for a kiln-style request.**
   Smallest experiment: install the package and run `tripo make reference.png -p face_limit=<n> --seed 1 --dry-run --json`. By its documentation this spends nothing, makes no network call and needs no key. It would show the chosen model, every request body, and whether the P1 switch happens.
2. **Whether the same seed gives the same file.**
   One reference image, the same command twice with `--seed`, both files taken in with `python3 -m kiln run --model`. Compare the checksums kiln records and what `python3 -m kiln.measure` reports. Two generations, about $0.60 at list price.
3. **What a Tripo raw output for a prop is like.**
   The same two files answer it for one asset: triangles, UVs, texel density, validator result, and the review pictures.
4. **Whether `task.json` holds enough to write the asset record's source.**
   Read the file from experiment 2.
5. **Whether `face_limit` at generation is a ceiling, as Tripo's skill text says, and `decimate` only a target.**
   Experiment 2's files give the first; one `--then decimate:<n>` gives the second, 30 more credits.
6. **Whether Claude's part improves anything.**
   The earlier note's fourth step: take a raw output that fails a check, put it through a fixed script and through Claude with `tools/bl` and the review pictures, with a fixed number of tries, and measure both.
7. **Whether the Blender Lab server runs against the pinned Blender in background mode on this machine**, and whether its answers are worth its place.
   Start `.tools/blender/blender --background <file>.blend --command blender_mcp` with the add-on installed, connect Claude Code, and ask it one inspection question about an imported raw output. No cost. Its page advises a virtual machine or a system without sensitive data.
8. **Whether a pay-as-you-go API customer is a "Paid User".**
   A question for Tripo, before any generated asset goes in a game that is sold.
9. **What rights MCP for Blender Premium passes on.**
   Read its terms. Only needed if workflow 4 is of interest.

## What could not be verified, and where sources disagreed

**Could not be opened or was not read**

- The source repository of `tripo-cli` (`github.com/vast-enterprise/Tripo-API-CLI`): "Not Found". The published package was read instead.
- The P series and Splat series tabs of Tripo's API pricing page.
- `TERMS_AND_CONDITIONS.md` of MCP for Blender and the Premium site's terms.
- Two articles returned an error: a Medium (UX Planet) piece on "3D Modeling with Claude Code: A Practical Blender Workflow" and a Level Up Coding piece on AI generators for game assets. Neither was read.
- The posts by individual creators that Tripo's articles credit (on X) were not opened.
- The community repositories in section 8 were read only at the top of their READMEs. Their tool lists and code were not read.
- The Tripo Blender add-on's behaviour in background mode was not checked in its source.
- The community server's safe-mode code (988 lines) was not read; only its README description and one issue about it.

**Not established**

- Whether Claude Code or Claude Desktop cuts off a long blocking MCP call such as `tripo_make`.
- Whether the skill folder in the CLI package loads as a Claude Code skill as it is.
- Whether any of this was tested by Tripo on Linux.
- Which MCP server, if any, the Tripo article's Claude session used.
- How long a finished Tripo task keeps its files before it becomes `expired`.
- Whether `tripo-mcp` is deprecated. Its last commit is from April 2025 and Tripo's documentation no longer mentions it; Tripo has not said.
- Whether `TripoGrowthLab` on GitHub is Tripo.
- Any hands-on report, with files, of Claude plus Tripo plus Blender producing a static game asset. Four web searches with different phrasings found none. That is a gap in the search.

**Sources disagree**

- **Tripo's CLI command names.** The documentation and the package give `tripo login`, `tripo whoami`, `tripo balance`. Tripo's own article of 2026-09-18 tells readers to run `tripo auth login`, `tripo auth whoami` and `tripo account balance`. The package read today (0.5.2) has the first set.
- **The Blender add-on's version.** Tripo's plugins page offers 0.7.3; the repository's source says 0.7.7.
- **How many tools the community server has.** Its README lists nine. A third-party measurement of 2026-09-04 counted 28 at "BlenderMCP v1.29.1". The repository has a test file named for consolidated tools, so the list appears to have been merged since; the version numbering of that measurement does not match the package's 2.1.9.
- **The Blender Lab add-on's version.** The page links release v1.0.3; the manifest in the source says 1.0.0.
- **The earlier note against this one.** It listed Tripo among the generators the community server can call, without the Premium condition; and it recorded the background-mode question as unverified. Both are settled above from source.
- **Tripo's API address.** `openapi.tripo3d.com` in the documentation read; `openapi.tripo3d.ai` for international accounts in the CLI's README.
- **`face_limit`.** The API reference calls it a "maximum". Tripo's skill text says it holds at generation and not at `decimate`. The earlier notes found hands-on counts over target on another vendor. Not tested here.

## Sources

All read 2026-10-08.

**Tripo**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt) and [index](https://developers.tripo3d.com/llms.txt), which include the [CLI](https://developers.tripo3d.com/en/docs/cli), [Codex plugin](https://developers.tripo3d.com/en/docs/codex-plugin), [plugins](https://developers.tripo3d.com/en/docs/plugins), [SDK](https://developers.tripo3d.com/en/docs/sdk), [rate limits](https://developers.tripo3d.com/en/docs/rate-limits), image-to-model, text-to-image, convert and retopology pages
- [API pricing](https://developers.tripo3d.com/en/pricing) (H series tab)
- [`tripo-cli` npm registry record](https://registry.npmjs.org/tripo-cli) and the package `tripo-cli-0.5.2.tgz`: `dist/commands/mcp.js`, `dist/commands/make.js`, `dist/commands/view.js`, `dist/core/download.js`, `dist/knowledge/scenarios.js`, `dist/ai/llm.js`, `skill/SKILL.md`, `skill/commands/make.md`, `skill/commands/batch.md`, `skill/examples/game-asset.md`, `README.md`
- [`VAST-AI-Research/tripo-mcp`](https://github.com/VAST-AI-Research/tripo-mcp): README, `src/server.py`, `pyproject.toml`, issue list
- [`VAST-AI-Research/tripo-3d-for-blender`](https://github.com/VAST-AI-Research/tripo-3d-for-blender): README, `__init__.py`, `server.py`
- [`VAST-AI-Research/Tripo3D-Plugin-dsh`](https://github.com/VAST-AI-Research/Tripo3D-Plugin-dsh): README, `plugin/skills/tripo-game-asset/SKILL.md`
- [Terms of Service](https://www.tripo3d.ai/terms), last updated 11 July 2025 (section 5.2 re-read)
- [How to Make 3D Models with Claude Opus 5.5](https://www.tripo3d.ai/blog/how-to-make-3d-models-with-claude-opus-5-5), 24 September 2026. Vendor-run.
- [Tripo P2.0 vs GPT-6 Astra](https://www.tripo3d.ai/blog/tripo-p2-vs-gpt-6-astra), 24 September 2026. Vendor-run.
- [GPT-6 Astra 3D character workflow](https://www.tripo3d.ai/blog/gpt-6-astra-3d-character-workflow), 8 September 2026. Vendor.
- [GPT-6 Astra 3D game scene workflow](https://www.tripo3d.ai/blog/gpt-6-astra-3d-game-scene-workflow), 18 September 2026. Vendor.

**MCP for Blender (community)**

- [`ahujasid/mcp-for-blender`](https://github.com/ahujasid/mcp-for-blender) at commit `7a0373e`: README, `src/blender_mcp/server.py`, `src/blender_mcp/generation.py`, `addon.py`; issues [201](https://github.com/ahujasid/mcp-for-blender/issues/201), [214](https://github.com/ahujasid/mcp-for-blender/issues/214), [248](https://github.com/ahujasid/mcp-for-blender/issues/248), [251](https://github.com/ahujasid/mcp-for-blender/issues/251), [257](https://github.com/ahujasid/mcp-for-blender/issues/257), [347](https://github.com/ahujasid/mcp-for-blender/issues/347), and the titles of the rest
- [PyPI record for `mcp-for-blender`](https://pypi.org/pypi/mcp-for-blender/json)
- [Premium page](https://www.mcp-for-blender.com/premium)
- [mcp-context-cost: blender](https://athakur3.github.io/mcp-context-cost/servers/blender.html). Third-party measurement.

**Blender**

- [MCP Server, Blender Lab](https://www.blender.org/lab/mcp-server/)
- [`lab/blender_mcp`](https://projects.blender.org/lab/blender_mcp) at commit `dbbf836`: `readme.md`, `readme_tools.rst`, `addon/blender_mcp_addon/cli.py`, `weak_sandbox.py`, `blender_manifest.toml`, `mcp/blmcp/tools/execute_blender_code.py`, `mcp/blmcp/tools_helpers/blender_cli.py`, `mcp/blmcp/data/prompts.yml`; its release list and issue titles

**Anthropic**

- [Claude Code: run programmatically](https://code.claude.com/docs/en/headless.md) and [MCP](https://code.claude.com/docs/en/mcp.md)
- [Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work), 28 April 2026, updated 1 May 2026

**Community repositories, record and top of README only**

- [`mordor-forge/trident-mcp`](https://github.com/mordor-forge/trident-mcp), [`pavlov-net/tripo3d-rs`](https://github.com/pavlov-net/tripo3d-rs), [`lixmal/tripo-mcp`](https://github.com/lixmal/tripo-mcp), [`MeterLong/tripo-skills`](https://github.com/MeterLong/tripo-skills), [`theisegoria/game-development-studio`](https://github.com/theisegoria/game-development-studio), [`sandraschi/blender-mcp`](https://github.com/sandraschi/blender-mcp), [`ellmos-ai/ellmos-blender-use-mcp`](https://github.com/ellmos-ai/ellmos-blender-use-mcp), [`lxsolutions/studio-foundation`](https://github.com/lxsolutions/studio-foundation), [`TripoGrowthLab/vibe-gaming-interactive-handbook`](https://github.com/TripoGrowthLab/vibe-gaming-interactive-handbook)

**This repo**

- [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md), for the papers, hands-on reports, licence terms and cost arithmetic it already establishes

## Method

Research was done on 2026-10-08. Tripo's documentation was downloaded as its full-text file and searched directly. The `tripo-cli` package was downloaded from the npm registry and unpacked, and its files were read as text; nothing in it was run. The four GitHub repositories and the Blender Lab repository were cloned and their source searched for tool definitions, background-mode handling, code execution and the word "tripo"; tool lists in this note come from that source, not from README summaries, except where marked. Repository records and issues were read through GitHub's API and Blender's project site API. Vendor articles, the Premium page, the pricing page and the terms were downloaded as HTML and reduced to text locally, not through a summariser; publication dates are from the pages' embedded data.

Four web searches were used to look for hands-on reports and papers; they found the pages listed as unopened above and nothing else new. The papers and hands-on reports cited in section 11 are carried from the earlier note and were not re-read. Tripo facts the earlier note marks as carried over were re-read here where this note leans on them: the generation parameters, the seed wording, the link lifetime, the pricing table, the rate limits and section 5.2 of the terms.

Facts about kiln are from `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md` and `tools/bl`. No generator API was called, no account was created, no MCP server or CLI was started, no model was asked to build anything, and no file from the `first-attempt` tag was used. Only this file was written.
