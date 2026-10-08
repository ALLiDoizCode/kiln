# Where a raw output comes from: an LLM alone, a 3D generator, or an LLM driving a generator

Researched 2026-10-08, in two passes on the same day. Every page cited below was read on that date. Prices, model names, plan terms and API parameters in this area change within months; check each again before relying on it.

This is a research note. It informs one choice about kiln (where raw outputs come from) and does not make it. It builds on [`3d-asset-pipeline-tools.md`](3d-asset-pipeline-tools.md) and [`game-mesh-kiln-or-generator.md`](game-mesh-kiln-or-generator.md) (called "the earlier notes" below) and does not repeat them. It does not draw on the `first-attempt` tag.

**Nothing here was tested.** No generator was called, no account was created, and no model was asked to build anything. Every statement about what a tool does is from its documentation, its terms, its source repository, a paper, or a report by someone else, and says which.

## How to read this

- **Fact** (the default) means a first-party page says so: a vendor's API reference, pricing page or terms, a tool's repository, Anthropic's or Blender's documentation.
- **Vendor claim** means the vendor says so about its own quality and nobody independent has shown it.
- **Paper** means a result from a research paper, with who wrote it. Papers measure particular models on particular tasks; the models are named each time.
- **Leaderboard**, **vendor-run** and **hands-on** are grades for the comparison data in section 4, defined there. Sections 1 to 3 were first written from first-party sources only; where section 4 changes them, they say so.
- **Inference** means the sentence is this note's reasoning from cited facts.
- **Arithmetic** means a number worked out from list prices and stated assumptions. No cost below was measured.
- **Unverified** means no primary source could be read; the item is listed so it is not mistaken for a fact.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, generator trial, shape review, review pictures, static asset, production ready) are used as `CONTEXT.md` defines them.

### The three approaches

1. **The LLM alone.** A general large language model (LLM), here Claude Fable 5.1 or Claude Opus 5.5, makes the 3D model itself. It either writes a Blender Python script that builds the shape when run, or writes the mesh out directly as text.
2. **A 3D generator used directly.** Tripo or Meshy turns a reference image or a prompt into a textured model. A person, or a plain program, calls it.
3. **The LLM driving a generator.** Claude calls Tripo or Meshy for the first shape, then cleans up, reduces, scales, checks and retries through Blender scripts and kiln.

### Terms used here

The earlier notes define mesh, triangle, quad, topology, UV coordinates, seam, texel density, PBR, normal map, decimation, retopology, baking and boundary edge. Terms added by this note:

- **LLM (large language model):** a program trained to continue text. It reads text and pictures and writes text. Code is text, so it can write programs.
- **Token:** the unit an LLM reads and writes, and is billed in. About four characters of English. **MTok** is a million tokens.
- **`bpy`:** Blender's Python library. A script that imports it can do nearly anything a person can do in Blender.
- **Headless:** running a program with no window, from a script. `tools/bl` runs Blender this way.
- **Procedural:** made by a program from rules and numbers, not drawn or sculpted. A procedural model is its script.
- **Text-to-3D, image-to-3D:** a generator's two inputs, a written prompt or a picture.
- **Seed:** the number that starts a generator's random choices. If the same seed gives the same result, a result can be made again.
- **API (application programming interface):** the way a program, not a person, uses a service. **Asynchronous** means the call returns at once with a task number, and the program asks again later (**polling**) until the task is finished.
- **MCP (Model Context Protocol):** an open standard that lets an LLM call outside tools. An **MCP server** offers the tools; an **MCP client**, such as Claude Code, connects the LLM to it.
- **Agent, agentic:** an LLM working in a loop: it acts, looks at the result, and acts again.
- **Manifold, watertight:** a mesh whose surface is closed and consistent, with no holes and no edge shared by more than two faces.
- **Albedo, base colour:** the texture that holds a surface's own colour. **Baked-in lighting** is highlights and shadows painted into it, which then look wrong under the game's own light.
- **Chamfer distance:** a number for how far apart two shapes are, used by the papers below. Lower is closer.

## Summary

### What the evidence supports

- **The three approaches are not three versions of the same thing.** Tripo and Meshy are trained on 3D data to produce a shape and its textures from a picture. An LLM writing `bpy` produces a program that assembles a shape from parts. Approach 3 uses a generator for the shape and an LLM for the work around it (section 5).
- **An LLM writing Blender scripts runs today, on this machine, with nothing new installed.** Blender runs headless from a script ([Blender manual](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)); Anthropic's current models take pictures as input and use tools ([models overview](https://platform.claude.com/docs/en/about-claude/models/overview)). `tools/bl` and the review pictures are already the two halves of the loop.
- **Code-writing LLMs and native generators have been measured on the same tests, and the result is mixed, not one-sided.** In two August 2026 preprints the best code-writing systems score about level with an open generator (TRELLIS) on how well pictures of the result match the prompt, make sharper edges on machine-like objects, and fall behind on surface quality and on matching an input picture. Neither uses Tripo or Meshy, and neither measures anything a game needs beyond shape (section 4.1).
- **Shape from an LLM is still the weak point in every source, and Claude Opus 5.5 is the best-rated LLM at it in the one public ranking that includes it.** A May 2026 benchmark from Google DeepMind found results on older models "frequently degenerating into disconnected geometric fragments ... or simplistic, floating primitives", and that retrying fixes script errors but "does not yield semantically richer or more shape-accurate geometry once a script compiles" ([3DCodeBench](https://arxiv.org/abs/2606.01057)). On the Blender AI Arena, by blind votes, Opus 5.5 rates 1847 against 1463 for Opus 5 and 1387 for Fable 5.1, with no generator entered. Tripo's own side-by-side on six reference images calls Opus 5.5's output "a blockout" (sections 1 and 4.1).
- **No measurement was found of an LLM producing UVs or texture maps for a game asset.** The benchmarks judge shape, mostly on untextured renders; the public ranking judges looks. Anthropic's documentation says Claude "cannot generate, produce, edit, manipulate, or create images" ([vision](https://platform.claude.com/docs/en/build-with-claude/vision)), so a texture from the LLM alone has to be made by code (section 1).
- **Tripo and Meshy return what kiln takes in:** a `.glb` with UVs and PBR textures, from an image, through an asynchronous API, at about $0.30 (Tripo) or $0.60 (Meshy) a generation at list price. Both document a face-count control and both document a setting to remove baked-in lighting. The vendors' quality wording is still claim (section 2).
- **Tripo and Meshy have been compared with each other, loosely.** Public blind-vote rankings put them within a few points of each other near the top, with Tripo's low-poly models leading the one low-poly ranking. One hands-on test counted non-manifold edges and zero-area faces in both vendors' reduced output. A test by Meshy's own staff ranked Tripo's untextured shape first. Nobody has published UV or texel-density measurements, or a study with a stated sample and files (section 4.4).
- **Licence is where the approaches differ most clearly, and it is decided by plan, not by tool.**
  - Tripo: free output is "Public Models · Non-Commercial Use" and "Tripo retains all rights"; paid users "generally have all rights" and Tripo "will not use Inputs and Outputs as training data" ([terms](https://www.tripo3d.ai/terms), [pricing](https://www.tripo3d.ai/pricing)).
  - Meshy: free output belongs to Meshy and is licensed to the user under CC BY 4.0, which requires credit; paid users "own their Customer Output", but Meshy "may use Customer Inputs and Customer Outputs ... from non-Enterprise Customers to train" ([terms](https://www.meshy.ai/terms-of-use)).
  - Anthropic through an API key: the customer "owns its Outputs" and "Anthropic may not train models on Customer Content from Services" ([commercial terms](https://www.anthropic.com/legal/commercial-terms)).
  - `learn/MISSION.md` requires "commercial rights without attribution". By these texts that rules out both free plans and admits both paid plans and the Anthropic API (sections 1 to 3).
- **Official ways for Claude to drive each tool exist.** Meshy publishes an MCP server; Tripo's command-line tool runs as one; Blender's own developers publish an MCP server for Blender. None of them is needed for a pipeline: both generators have a plain HTTP API that a Python program can call without any LLM (section 3).
- **No controlled measurement was found of an LLM's cleanup improving a generated asset.** What exists is a paper in which LLM agents' small edits to existing meshes were rated like artists' (7.53 against 7.20 out of 10, on 20 tasks), and a vendor demonstration of Opus 5.5 inspecting and repairing one Tripo character (sections 3 and 4.2).

### What the evidence does not settle

- How Claude Fable 5.1 or Claude Opus 5.5 does at building a prop from a reference image through `bpy`, measured against a generator on the same image. The one ranking with both models compares them only with other LLMs, from text prompts; the one side-by-side with a generator is the generator's vendor's.
- Whether an LLM can produce acceptable textures and UVs by script for the kinds of static asset kiln handles.
- What a Tripo or Meshy raw output is actually like as a mesh, on more than one model: closed or not, how its UVs are cut, whether lighting is really gone from the base colour. Section 4.4 has one counted test of reduced output and nothing on UVs.
- Whether generator output cleaned up by an LLM is better than the same output cleaned up by a fixed script, or left alone.
- Whether a pay-as-you-go Tripo API customer with no subscription is a "Paid User" under Tripo's terms. The terms do not define it.
- Whether anyone can hold copyright in a generated asset at all. That is a question of law, not of any vendor's terms; both Meshy ("to the extent possible under applicable law") and Anthropic ("its right, title and interest (if any)") word their grants to allow for it.

### The experiment that would settle most of it

A generator trial, as `CONTEXT.md` defines one, with the LLM route entered as one more generator. Two or three reference images (a rock, a flat-sided prop such as a crate, a building piece), each put through Tripo, Meshy and a Claude-writes-`bpy` loop with a fixed number of tries, every result taken in with `python3 -m kiln run --model` and judged by kiln's own measurement, checks and shape review. It would also be the first test found of all three approaches on the same reference images. Section 7 lists what to record.

## 1. The LLM alone

### What it is

Two different things go under this heading.

**Writing a script.** The LLM writes Python that uses `bpy` to build the object: add a cube, move its corners, cut a hole, bevel an edge, make a material. `tools/bl` runs it and exports a `.glb`. Optionally kiln renders pictures, the LLM looks at them, and it rewrites the script. The model is the script; the `.glb` is what the script prints.

**Writing the mesh as text.** The LLM writes the list of points and triangles itself, for example as an OBJ file, where each line is one point or one triangle.

### What the documentation says the models can do

From Anthropic's [models overview](https://platform.claude.com/docs/en/about-claude/models/overview) and [pricing page](https://platform.claude.com/docs/en/about-claude/pricing):

| | Claude Fable 5.1 | Claude Opus 5.5 |
|---|---|---|
| API ID | `claude-fable-5-1` | `claude-opus-5-5` |
| Described as | "For demanding reasoning and long-horizon agentic work" | "For long-running agentic coding and knowledge work" |
| Input / output price | $10 / $50 per MTok | $4 / $20 per MTok |
| Reading from the prompt cache | $0.25 per MTok | $0.20 per MTok |
| Most it can read at once (context window) | 1M tokens | 1M tokens |
| Most it can write in one reply | 128k tokens | 128k tokens |
| Reliable knowledge cutoff | June 2026 | June 2026 |

- **Pictures in, text out.** "All current models support text and image input, text output, multilingual capabilities, vision, and tool use." A picture costs `⌈width / 28⌉ × ⌈height / 28⌉` tokens, up to 4,784; a 1920×1080 picture, the size of kiln's review pictures, is 2,691 tokens ([vision](https://platform.claude.com/docs/en/build-with-claude/vision)).
- **Stated limits of its sight.** The same page lists: "Spatial reasoning: Claude's coordinate and localization outputs are approximate"; counting "might not always be precisely accurate"; and "Always carefully review and verify Claude's image interpretations". It also says Claude "cannot generate, produce, edit, manipulate, or create images".
- **Anthropic's hosted code sandbox cannot run Blender.** The [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) gives Claude a container with 1 CPU, 5 GiB of memory and "no internet access, so Claude can't download or install additional packages at runtime: only the pre-installed libraries are available". The listed libraries are for data and documents (pandas, numpy, matplotlib, pillow and the like); Blender is not among them. So Blender has to run on the owner's machine, with Claude reaching it through a tool that runs there (Claude Code's shell, or the Agent SDK). This repo is already set up that way (inference from the page and from `tools/bl`).
- **Nothing in the Anthropic pages read claims the models can model in 3D.** Anthropic's one statement about Blender, [Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work) (28 April 2026), describes a connector that "offers a natural-language interface to its Python API, allowing users to explore and understand complex setups", and gives as examples analysing and debugging scenes and writing scripts that "batch-apply changes to objects". It does not describe making assets.

### What Blender offers a script

- Blender runs with no window (`--background`) and runs a script (`--python`); `--python-exit-code` makes a failing script fail the command ([command-line arguments](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)). The [Python API reference](https://docs.blender.org/api/current/index.html) is published per version ("Blender 5.2 Python API Documentation" today) and has a section on running in background mode.
- The API changes between versions. This matters: the benchmark below found that most outright failures were scripts written for the wrong version's API.
- What a person makes with Blender is theirs: "What you create with Blender is your sole property" ([Blender licence page](https://www.blender.org/about/license/), quoted in the earlier note).

### Evidence that LLMs can build geometry through code

All of this is from papers. None tests Claude Fable 5.1 or Claude Opus 5.5.

Section 4 adds the sources that compare LLMs with generators, and the one public ranking that does test the two models.

- **[3DCodeBench](https://arxiv.org/abs/2606.01057)** (Google DeepMind and the University of Southern California, 31 May 2026). The closest thing to the question: 12 models write Blender 5.0 scripts for 212 kinds of object from text or image prompts.
  - Finding 1: "Failures mostly arise from API mismatches, while successful renders still suffer from disconnected or floating 3D geometric components."
  - Finding 2: retrying with the error message makes scripts run (Claude Opus 4.7 reached every script running), but the gain "results from a single failure family: Blender 5.0 API mismatches". Running the models inside their own coding tools (Claude Code for Claude) "does not yield semantically richer or more shape-accurate geometry once a script compiles".
  - On pictures of results from Gemini 3.1 Pro, Claude Opus 4.7 and GPT-5.5: "While these models capture basic silhouettes, they often struggle with structural integrity."
  - In its ranking by human votes on shape, "the Claude models fall below the frontier".
  - Its scope: geometry only. Results were rendered and voted on without textures, and the prompts told models to "Leave geometry untextured". It says nothing about UVs, textures, triangle counts or game use.
  - The authors work for a company that makes one of the model families tested.
- **[3DHarnessBench](https://arxiv.org/abs/2609.06535)** (6 September 2026). Seven models, including Claude Fable 5 and Claude Opus 5, rebuild 100 existing 3D objects as Blender scripts, with more or less access to the target. It reports that results improve "significantly with richer function call access, although the improvements are strongly model-dependent", and that "Opus 5 is strongest overall" when the model can look around the target freely. Its task is copying an object that already exists in 3D, which kiln does not have: kiln starts from one reference image. The single-picture setting is its hardest.
- **[BlenderGym](https://arxiv.org/abs/2504.01786)** (April 2025): "even the state-of-the-art VLM system struggles with tasks relatively easy for human Blender users". It tests editing scenes, on models now well out of date.
- **[LL3M](https://arxiv.org/abs/2508.08228)** (August 2025) and **[3D-GPT](https://arxiv.org/abs/2310.12945)** (2023) are systems that do this with several LLM roles and a library of Blender documentation. They show it can be done and what scaffolding their authors needed; their examples are chosen by the authors and are not a measurement.
- **Writing the mesh as text.** [LLaMA-Mesh](https://arxiv.org/abs/2411.09595) (November 2024) shows an LLM can be *trained further* to write OBJ text. That is a specially trained model, not a general one used as it comes. No source was found measuring a general frontier LLM writing game meshes as text.

### Pros

- **Exact size and exact counts.** A script places points at stated coordinates in metres, so the size is whatever the script says, and the triangle count is whatever the script builds (inference from what a script is; 3DCodeBench's abstract calls procedural output "deterministic, engine-ready, and precisely editable").
- **Sharp edges and separate parts on flat-sided objects.** Measured in one preprint: code-built machines had 95th-percentile edge angles of 90° to 105° against 33° to 73° for four native generators, whose surfaces "blur bolt heads, vents, and panel lines" (Procedura, section 4.1). Tripo's own test agrees in words: "Hard-surface objects like the backpack and the scooter translate cleanly into primitives".
- **About level with an open generator at matching a text prompt**, by picture-similarity scores in two preprints, when the LLM runs in a loop that checks its work (section 4.1).
- **Repeatable after it is written.** The script is a file. Running it again gives the same model; the earlier note's trial found Blender's decimation byte-identical over three runs. Changing one number changes one thing.
- **It can be edited by asking.** The paper authors' main argument for code: a later request ("make the legs thicker") changes the script, not a fresh roll of a generator (LL3M abstract).
- **The clearest licence.** With an API key, the customer "owns its Outputs", Anthropic "may not train models on Customer Content", and Anthropic will defend the customer against a claim that outputs infringe someone's intellectual property, with exceptions ([commercial terms](https://www.anthropic.com/legal/commercial-terms), sections B and K).
- **No new vendor.** The owner already uses Claude; no account, key or plan to add.

### Cons

- **Shape is the documented weak point.** Floating and disconnected parts, simplified forms, and no improvement in shape from retrying (3DCodeBench, on Opus 4.7 and its peers). Newer models are rated higher: by blind votes Opus 5.5 is well above Opus 5 and Fable 5 on the Blender AI Arena. But that ranks LLMs against LLMs, and Tripo's side-by-side with Opus 5.5 still shows "a blockout" (section 4.1).
- **Behind a generator at matching a reference image.** In the one preprint that measures it, the code systems' pictures were further from the input picture than TRELLIS's (FID 185 to 215 against 108, lower being better), and the authors say generators "recover smoother surfaces and richer appearance cues" (aDSL, section 4.1). Kiln starts from a reference image.
- **Organic shapes do not come from primitives.** A rock or a tree trunk is not a sum of cubes and cylinders. 3DCodeBench's examples of trouble ("Fish", "Lobster") are organic, and Tripo's test reports that "faces, hands, hair and cloth folds are approximated with spheres, lofts and shells". No source measured rocks.
- **Textures are unproven and indirect.** Claude cannot make an image. A script can build a material from Blender's procedural nodes, but the glTF exporter skips nodes it does not recognise, "so procedural materials must be baked to images first" (earlier note, from the Blender manual). No source was found measuring the result.
- **UVs are left to Blender's automatic unwrap**, with the limits the earlier note recorded (hundreds of islands on a rock in its trial).
- **It works from sight it describes as approximate.** Matching a reference image means judging proportion and position from pictures, which the vision page lists as a limitation.
- **Writing the mesh as text does not reach a game budget.** Arithmetic, with an assumed 10 tokens for each line of OBJ text: a 10,000-triangle mesh is about 5,000 point lines and 10,000 triangle lines, 150,000 tokens, more than the 128,000 a model can write in one reply. And it would carry no UVs or textures.
- **The LLM's own output is not repeatable.** Two requests for the same prop give two scripts. Whether these models accept a setting that reduces this was not checked.
- **It is outside kiln's stated scope.** `learn/MISSION.md` lists "Building assets by script" as out of scope: "Kiln's first shape comes from a generator." Whether an LLM writing a script counts as a generator under `CONTEXT.md` ("an external AI service or model that produces a first shape from a reference image and a prompt") is the owner's call.

### Cost

See section 6. As arithmetic on stated assumptions: roughly $1.70 to $9 for one asset with eight tries, depending on the model and on caching. 3DCodeBench reports $0.14 an object for Claude Opus 4.7 and $0.29 for Claude Sonnet 4.6 in its own runs, which were geometry only and at older prices. One hands-on report of a detailed, animated project gives far more: $27.86 on Opus 5.5 and $42.44 on Fable 5.1 (section 4.3).

### Licence

- **API key:** [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms), effective 17 June 2025. Customer "owns its Outputs"; no training on customer content; indemnity as above.
- **Claude.ai as an individual:** [Consumer Terms](https://www.anthropic.com/legal/consumer-terms), effective 8 October 2025. "We assign to you all of our right, title, and interest—if any—in Outputs", but "We may use Materials ... including training our models, unless you opt out of training through your account settings". Which of the two sets of terms covers Claude Code on a personal subscription was not established here (unverified).
- **Blender:** output is the user's.

## 2. Tripo and Meshy used directly

The earlier notes cover both in detail: models, face-count routes, formats, prices, terms, as read on 2026-10-07. This section restates only what bears on the comparison, re-read today, and adds what they did not cover.

### What they output

| | Tripo (API v3) | Meshy |
|---|---|---|
| Current model | H series `v3.1-20260211`; low-poly P series `P1`, `P2` (preview) | `meshy-7.1`; low-poly `meshy-t2` |
| Input | Text, one image, or four views (front required; left, back, right optional) | Text, one image, or 1 to 4 images |
| File | GLB from generation; GLTF, FBX, USDZ, OBJ, STL, 3MF by conversion | GLB, FBX, OBJ, USDZ, STL |
| Mesh | Triangles; quads only as FBX on the H series | Triangles; "quad-dominant" by remesh |
| Face count | `face_limit`, a "maximum polycount"; 500 to 20,000 with `smart_low_poly` | `target_polycount`, which "may deviate"; 100 to 15,000 on `meshy-t2` |
| UVs | `export_uv`, on by default; nothing documented about seams or density | Automatic; "you won't have control over where texture seams are placed" |
| Textures | Base colour, metallic, roughness, normal; up to 8K | Base colour, plus metallic, roughness, normal with `enable_pbr`; 2K, 4K or 8K, nothing smaller |
| Baked-in lighting | `delight`, default true: "Removes baked-in lighting from the reference image before texturing" (read only by texture model `v3.5-20260815`; the default texture model is `v3.0-20250812`, so it does nothing unless `texture_version` is set. Corrected from the [later note](tripo-guidance-and-blender-scripting.md)) | `remove_lighting`, default true: "Removes highlights and shadows from the base color texture" |
| Size in metres | `auto_size`, default **false**: scales "to real-world dimensions" | `auto_size`: "uses AI vision to estimate real-world height"; `origin_at` bottom or centre |
| Which way it faces | `export_orientation`, default `+x` forward | Not found in the text read |
| Parts | `generate_parts`; segmentation endpoints | `meshy-t2` "natively separated parts" (vendor claim) |
| Rigging, animation | Yes | Yes |

Sources: [Tripo API documentation, full text](https://developers.tripo3d.com/llms-full.txt); [Meshy API documentation, full text](https://docs.meshy.ai/llms-full.txt).

Three of these rows matter to kiln directly (inference):

- **Size.** Neither generator knows the asset's size unless asked to guess it, which is why `CONTEXT.md` gives a run a size. Kiln's scaling stage is needed with either.
- **Facing.** glTF says the front of an asset faces +Z (earlier note). Tripo's default export faces +X. Something has to turn it.
- **Lighting in the colour.** Both vendors document a switch for it and both default it on. That is an admission that the problem exists and a vendor claim that the switch fixes it.

### Control and repeatability

- **Seeds.** Tripo: "Using the same seed with the same input will produce an identical 3D mesh", with a separate `texture_seed` to change textures and keep the shape (vendor claim, untested). Meshy: the word "seed" does not occur in its API text.
- **Image or text.** Both take either. Kiln's run starts from a reference image, which is the better-controlled of the two (inference: a picture fixes more than a sentence does).
- **Several views.** Both accept up to four pictures of the same object; Tripo will also generate the four views from one picture as a separate, paid step.
- **Editing a result.** Both re-texture an existing model; Tripo documents segmenting a model into parts and working on parts. Neither documents changing the shape of one part of a finished model by instruction.
- **Style across a set.** No documented control was found for either (as the earlier note found). `learn/MISSION.md` already puts this out of scope: "It follows from giving consistent reference images."
- **Versions are retired.** Meshy retires `meshy-5` on 10 October 2026 and its `lowpoly` mode on 30 October 2026 ([changelog, in the full text](https://docs.meshy.ai/llms-full.txt)). A result cannot be made again once its model is gone. This is why `CONTEXT.md` keeps the raw output.

### API

| | Tripo | Meshy |
|---|---|---|
| Shape of a call | Asynchronous: create a task, poll `GET /v3/tasks/{id}` or receive a webhook | Asynchronous: create, poll or webhook |
| Limits | 10 tasks at once for H-series generation on the rate-limits page; "3 parallel tasks" on the model page | Pro: 20 requests a second, 10 tasks in the queue |
| Failed tasks | "Failed and cancelled tasks are not charged" | Only pending tasks are refundable on cancel |
| How long results are kept | "Generated model URLs are temporary" | "a maximum of 3 days" for non-Enterprise |
| Free plan through the API | Not stated | No: "task creation requires a paid plan" |
| Official libraries | JavaScript, Python, Go, Rust, Java (the Python one covers the older API version and only part of v3) | OpenAPI description; no SDK found in the text read |
| Blender add-on | 0.7.3, for Blender "3.0+" | Yes; tested versions in the earlier note |
| MCP | `tripo mcp` in the official command-line tool; a separate official repository marked alpha | Official server, `@meshy-ai/meshy-mcp-server` |
| Can it run unattended | Yes: plain HTTP with a key (inference from the above) | Yes (same) |

### Pros

- **It is the tool built for the job.** Shape and textures from one reference image, in the format kiln takes in, in minutes.
- **Ahead of code-writing LLMs on surface quality and on matching an input picture**, where that has been measured, with open generators standing in for the commercial ones (section 4.1).
- **Rated near the top by blind public votes.** Tripo v3.1 and Meshy 7 are in the top three for texture, Meshy 7 leads geometry and Tripo's P series leads low poly on the Top 3D AI arena, each on a few hundred votes or fewer (section 4.4).
- **Organic shapes are its home ground** (inference from what it is: trained on 3D data, not assembling primitives).
- **Textures, UVs and PBR maps come with it.**
- **Cheap per try:** $0.30 to $0.60.
- **Plain API, no LLM needed.** A stage in kiln can call it.
- **Tripo documents repeatable seeds.**

### Cons

- **The vendors' quality statements are still unproven.** "Clean topology", "game-ready" and "hand-crafted" are not measured by any study with a stated sample and published files. What exists is public blind votes on looks and a few hands-on tests (section 4.4). A 2026 survey says topology quality is "almost never quantified" (earlier note).
- **The mesh's condition is undocumented, and the little that has been counted is not clean.** Neither vendor says whether output is closed, whether points are welded, or how UVs are cut. One hands-on test of the reduction tools on one model counted 6 to 31 non-manifold edges from each vendor and thousands of zero-area faces. Meshy's own figure is that 55% of 75 figurine models were fully watertight. Tripo's own export guide says non-manifold geometry and chaotic UVs "are common" in AI output (section 4.4). Meshy sells a separate "Repair Printability" call that fixes "non-manifold edges, degenerate faces, holes, and other topology issues".
- **Soft edges on flat-sided objects.** Measured on open generators, not on Tripo or Meshy: edges come out rounded and small features "fuse into one skin" (Procedura, section 4.1). Whether the vendors' low-poly models avoid this is not measured.
- **Details that are not in the picture.** One hands-on run reports that Tripo 2.5 "invented details that are not in the photo" on the side the photo did not show (section 4.4).
- **Vendors state some limits themselves.** Tripo, of `smart_low_poly`: "Best suited for simple, non-complex inputs. Complex models may occasionally fail." Meshy's guide to its remesh: "small accessories disappear" and "holes after remeshing" (earlier note). Tripo asks for a subject "clearly visible with a clean background and minimal occlusion"; Meshy for "a single object per image".
- **Face counts are a target, not a promise** (earlier note). Kiln's check is needed regardless. One hands-on run got 30,076 triangles from Meshy 7 for a 30,000 target, and 67,416 from Meshy's remesh for the same target on another vendor's mesh (section 4.4).
- **No texture below 2K at generation** on Meshy; Tripo does not state its standard size. A smaller texture budget needs a resize in kiln.
- **Each try is a new roll** unless Tripo's seed holds. Meshy offers no seed.
- **Licence depends on the plan, and one of the two trains on paid users' work.** Below.
- **The service can change under kiln.** Models retired in weeks; documentation that disagrees with itself (the concurrency figures above; more in the earlier notes).

### Cost

List prices today:

- **Tripo API:** "1 credit = $0.01 USD". Image to 3D with standard textures, H series: 30 credits, $0.30. Add 10 for smart low-poly, 10 for HD textures, 5 for quads ([API pricing](https://developers.tripo3d.com/en/pricing)).
- **Tripo Studio** (the web app): Free, 200 credits a month; Pro shown as $20 a month for 3,000 credits. The page's monthly and yearly figures do not agree with its "50% off" annual label ([pricing](https://www.tripo3d.ai/pricing)).
- **Meshy:** Pro is $20 a month for 1,000 credits, $0.02 a credit; Premium $40 for 3,000; Ultra $100 for 8,000 ([pricing](https://www.meshy.ai/pricing), read from the page's embedded data). Image to 3D with 2K or 4K textures on `meshy-7.1`: 30 credits, about $0.60. On `meshy-t2`: 15 credits, about $0.30 ([API pricing](https://docs.meshy.ai/api/pricing)).

### Licence

| | Free plan | Paid plan |
|---|---|---|
| **Tripo** ([terms](https://www.tripo3d.ai/terms), last updated 11 July 2025) | "Tripo retains all rights" in inputs and outputs. Pricing page: "Public Models · Non-Commercial Use". | "Paid Users generally have all rights", subject to a licence back to Tripo to provide the service. "Company will not use Inputs and Outputs as training data". Pricing page: "Private Models · Commercial Use". |
| **Meshy** ([terms](https://www.meshy.ai/terms-of-use), last updated 19 September 2026) | Meshy "owns all right, title, and interest" in the output and licenses it under CC BY 4.0 "as long as the free plan customer provides appropriate credit to Meshy". | Paid customers "own their Customer Output", "to the extent possible under applicable law", and "have the option to keep their User Content private". Section 2.9: Meshy "may use Customer Inputs and Customer Outputs ... from non-Enterprise Customers to train, validate, test, or improve Services". |

- **Both:** the terms bar using the service to build a competing one (Tripo's wording covers outputs: not "to create models or services that directly compete"), and the user indemnifies the vendor. Neither gives the user an indemnity against intellectual-property claims over outputs (Tripo: earlier note; Meshy: section 8 read today lists only the user's indemnity).
- **Meshy contradicts itself.** Its pricing page FAQ says "We will NOT share your data or use it for any training purpose without your consent"; its terms say the above. The terms are the contract.
- **Meshy's public gallery is a trap for a sold game.** Anything a user posts to the Meshy Community page is licensed to everyone under CC0, which gives up all rights (terms, section 3).
- **Tripo, pay-as-you-go API with no subscription:** whether that customer is a "Paid User" is not defined (unverified).

## 3. The LLM driving a generator

### What it is

The generator makes the first shape. Claude does the rest: calls the API, waits, downloads the file, runs Blender scripts to turn, scale, reduce and re-texture, runs kiln's measurement and checks, looks at pictures, and decides whether to try again. The parts kiln has already built (take in, review pictures, build, checks) are the same parts this approach would call.

### What exists to connect them

| Tool | Who maintains it | What it is | Status today |
|---|---|---|---|
| [Meshy MCP server](https://github.com/meshy-dev/meshy-mcp-server) | Meshy (official) | Wraps the Meshy API as tools: generate, remesh, retexture, check a task, download | MIT licence; last changed 2026-10-05; "every MCP tool call maps to a single REST call and consumes credits at the exact same rate" |
| [`meshy-3d-agent`](https://github.com/meshy-dev/meshy-3d-agent) | Meshy (official) | Written instructions for Claude Code and similar tools that call the Meshy API directly | Named in Meshy's documentation; not read |
| Tripo CLI (`tripo-cli`) | Tripo (official) | A command-line tool "built for AI agents"; `tripo mcp` runs it as an MCP server; `tripo batch run` runs a list of jobs with retries | Documented in the [Tripo API text](https://developers.tripo3d.com/llms-full.txt); its package page could not be fetched |
| [`tripo-mcp`](https://github.com/VAST-AI-Research/tripo-mcp) | Tripo's company (official) | An MCP server that generates through Tripo's Blender add-on | "This project is in alpha"; last changed April 2025 |
| [Blender MCP Server](https://www.blender.org/lab/mcp-server/) | Blender's own developers (Blender Lab) | Lets an LLM run Python in an open Blender and read its documentation | Needs Blender 5.1 or newer and an add-on. "The MCP server will execute LLM generated code in Blender without any guards in place" |
| [MCP for Blender](https://github.com/ahujasid/blender-mcp) (`ahujasid/mcp-for-blender`) | One developer; "third-party integration and not made by Blender" | Runs Python in Blender, returns views of the scene, and has one call that generates through Tripo, Hunyuan3D or Rodin. Tripo is reached only through the project's paid plan, not with your own Tripo key: "Tripo is only available with MCP for Blender Premium" (corrected from the [later note](claude-tripo-blender-workflows.md)) | MIT; about 30,000 stars; last changed 2026-10-06. Sends an anonymous usage record unless turned off |

Three facts decide how these could be used with kiln:

- **Anthropic's API cannot reach a local MCP server by itself.** Its [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) requires that "the server must be publicly exposed through HTTP ... Local STDIO servers cannot be connected directly". The Meshy, Tripo and Blender servers above all run locally, so they need an MCP client such as Claude Code.
- **The Blender MCP servers talk to an open Blender session.** Kiln runs Blender headless through `tools/bl`, one script per stage, with no network (`--offline-mode`). The community server refuses that mode ("cannot start server in background mode (blender -b)"); Blender Lab's server has a background mode (`blender --background file.blend --command blender_mcp`). Both facts are from the servers' source, read for the [later note](claude-tripo-blender-workflows.md); the first version of this note had them as unverified. A Claude that writes a script and runs it with `tools/bl` needs neither (inference).
- **Calling a generator needs no LLM.** Create a task, poll, download: that is ordinary code, and `learn/MISSION.md` already asks that "the generator is called through one interface so it can be swapped". An LLM is only needed where a judgement is needed (inference).

### Pros

- **It keeps what approach 2 is good at** (shape and textures from a picture) and adds a worker for everything after.
- **Claude's documented strength is the part it would do.** Anthropic describes these models as for "long-running agentic coding"; writing and fixing Blender scripts against error messages is coding. 3DCodeBench's own result is that retrying with the error message fixes failing scripts reliably.
- **Fixing an existing mesh is a narrower task than inventing one.** Turning, scaling, welding, decimating and checking are standard operations with numeric results that kiln already measures. This is an inference. The nearest measurement is of a different kind of change: LLM agents' edits to existing meshes, rated by 48 people at 7.53 out of 10 against 7.20 for artists' edits of the same meshes (ViSculpt, section 4.2).
- **One published demonstration of the whole chain on a current model.** Tripo generated a character; Claude Opus 5.5 read the file through Blender's Python, checked it for loose points and degenerate faces, and repaired its rig (Tripo's own article, one asset, section 4.2).
- **It can retry without a person.** A failed check can lead to a second generation with a different seed, or a different reduction, before a person is asked.
- **Official integrations exist** for all three tools.

### Cons

- **No controlled measurement of it was found.** The tools exist; no source was found that compares generated assets cleaned up by an LLM with the same assets cleaned up by a fixed script or left alone. Section 4.2 has a paper on a neighbouring task and a vendor's demonstration. Anything said for this approach beyond "it can be wired up, and has been shown once" is inference.
- **Reported sessions of an LLM working in Blender are long and costly.** One project cost $27.86 on Opus 5.5 and $42.44 over 1 hour 13 minutes on Fable 5.1; another report describes two hours on one scene with visible defects left (section 4.3). These were building, not cleanup, so they bound the cost from above at best.
- **An LLM that decides is not repeatable; a script is.** Kiln's `build()` makes the asset "from that record alone" and `rebuild` repeats it. If Claude chooses the steps for each asset at run time, a rebuild is no longer the same build. If Claude instead writes the stage scripts once and kiln runs them, that is ordinary development of approach 2, not a third approach (inference from `CLAUDE.md`).
- **Its judgement of pictures is the documented weak point of approach 1, carried over.** Deciding from renders whether a seam shows or a part is missing leans on the same sight the vision page calls approximate. `CONTEXT.md` gives the shape review to a person.
- **Two bills and two sets of terms.** Generator credits plus tokens. The generator's licence still governs the asset; adding Claude does not improve it. If pictures or files of a raw output are sent to Claude, Anthropic's terms apply to those as inputs.
- **Running LLM-written code needs care.** Both Blender MCP pages warn that the code runs unguarded. `tools/bl` already narrows this for kiln by running with factory settings and no network.
- **More moving parts that change monthly:** a generator API, an MCP server, a Blender version and a model.

### Cost

Generation as in section 2, plus tokens as in section 6. If Claude only looks at one set of review pictures and writes a short verdict, that is about $0.13 on Opus 5.5 (arithmetic). If Claude runs a multi-step loop for each asset, the token cost is larger than the generation cost.

### Licence

- The asset's licence is the generator's, by plan, as in section 2.
- Scripts and text Claude writes are the customer's under Anthropic's commercial terms, as in section 1.
- Blender adds no claim.
- `kiln run --licence` records one text per asset. Under this approach that text should name the generator and the plan held on the day of generation, since the plan decides the rights (inference).

## 4. Comparison data: what exists

Added in a second pass on 2026-10-08, with the source rule widened to any source. The first version of this note said no comparison existed; that was wrong for approach 1 against generators and too strong for the generators against each other. This section lists what was found, graded. Nothing here was produced or checked by this note.

**Grades**

- **Preprint:** a research paper with its method and numbers, not yet peer reviewed unless stated.
- **Leaderboard:** a public ranking with a stated method.
- **Vendor-run:** a comparison by a company that sells one of the things compared. An interested party.
- **Hands-on:** one person's or one site's report. An anecdote; the number of assets and whether files or pictures are published is given each time.

### 4.1 Code-writing LLMs and native generators on the same test

Four sources put the two side by side. None uses Tripo or Meshy as the generator except the last, which Tripo wrote.

**aDSL** ([arXiv 2608.17975](https://arxiv.org/abs/2608.17975), 18 August 2026). *Preprint.*

- What was tested: text to shape on 200 prompts over 100 objects (60 from ShapeNet, 20 from ABO, 20 from Objaverse); image to shape on 30 objects from Toys4K, each "rendered from a random viewpoint as the input condition".
- Who was tested: code-writing systems (BlenderMCP run with Claude Opus 4.5, BlenderLLM, Scene Language and ShapeCraft on Gemini 3 Pro, and the authors' own aDSL); native generators (Trellis, Direct3D-S2, MVDream, LN3Diff); and Llama-Mesh, which writes the mesh as text.
- What was measured: how well pictures of the result match the prompt or the input picture (CLIP score, VQAScore, and FID, where lower is better), and the share of prompts that gave a usable mesh. All results were rendered "with neutral materials", so texture is not judged.

| Text to shape, Objaverse prompts | CLIP | VQA | Share that produced a mesh |
|---|---|---|---|
| aDSL (the authors' system) | 29.07 | 69.37 | 1.00 |
| BlenderMCP with Claude Opus 4.5 | 28.44 | 66.22 | 1.00 |
| Trellis (native generator) | 27.67 | 68.06 | 1.00 |
| Scene Language | 26.77 | 62.45 | 0.95 |
| ShapeCraft | 24.60 | 53.94 | 1.00 |
| Llama-Mesh (mesh as text) | 17.29 | 38.74 | 0.80 |

| Image to shape, 30 Toys4K objects | CLIP | FID (lower is better) | Share that produced a mesh |
|---|---|---|---|
| Trellis (native generator) | 84.88 | 108.20 | 1.00 |
| aDSL | 84.42 | 184.71 | 1.00 |
| BlenderMCP with Claude Opus 4.5 | 83.28 | 214.87 | 1.00 |
| Direct3D-S2 (native generator) | 82.13 | 148.62 | 1.00 |
| ShapeCraft | 79.34 | 187.62 | 1.00 |
| Scene Language | 78.68 | 206.21 | 0.93 |

- The authors' own reading: "Field-based methods still recover smoother surfaces and richer appearance cues, but they struggle with structured details such as bicycle spokes"; code baselines show "floating components and misaligned parts".
- Limits: BlenderMCP was scored "on a subset due to limited API access quotas". The authors call the generators "reference comparisons", not rivals. The measures compare pictures, not meshes: nothing about triangles, UVs or closed surfaces. Trellis is the first open TRELLIS, older than any current commercial model.
- Its cost figures for the authors' system: about 31,000 tokens read and 2,750 written for each round, 4.25 to 5.23 rounds an object, about 190 seconds a round.

**Procedura** ([arXiv 2608.26238](https://arxiv.org/abs/2608.26238), 26 August 2026). *Preprint.*

- What was tested: MechBench-36, the authors' own set of 36 prompts for hard-surface machines (a rover, an excavator, a motorcycle chassis). Every method was given "the same locked reference image".
- Who was tested: the authors' agent, which writes OpenSCAD (a programming language for solid shapes), not `bpy`; two other code agents; three LLMs asked once with no loop; four native generators.
- What was measured: a score from 0 to 1 given by an LLM judge (Gemini 3.7 Flash) looking at grey renders, and two measurements on the mesh itself of how sharp its edges are.

| MechBench-36 | Kind | Judge, overall | 95th-percentile edge angle |
|---|---|---|---|
| Procedura on Gemini 3.7 Flash | Code agent (the authors') | 0.828 | 98.0° |
| TRELLIS.2 | Native generator | 0.810 | 73.1° |
| Adam CAD on GPT-5.6-sol | Code agent | 0.799 | 90.4° |
| GPT-5.6-sol, asked once | LLM alone | 0.792 | 89.8° |
| Gemini 3.7 Flash, asked once | LLM alone | 0.763 | 91.4° |
| UltraShape | Native generator | 0.748 | 33.1° |
| Hunyuan3D | Native generator | 0.697 | 35.1° |
| Direct3D-S2 | Native generator | 0.639 | 52.8° |

- The authors' reading: "the natives reproduce the silhouette faithfully but blur bolt heads, vents, and panel lines into the surrounding body".
- A second table, on another group's benchmark of 203 assemblies (P3D-Bench), has LLMs only. Claude Opus 4.6 scores 0.448 there, against 0.563 for GPT-5.6-sol and 0.566 for Gemini 3.7 Flash. No Claude model is in the MechBench-36 table.
- Limits: the benchmark and the winning system are the authors' own; the judge is the same model their system runs on; machines only, the kind of object code suits best; no textures; no Tripo or Meshy.

**Blender AI Arena** ([blenderai.org](https://blenderai.org/leaderboard), read 2026-10-08). *Leaderboard.* The only source found that tests the two models this note asks about.

- Method, as [published](https://blenderai.org/methodology): 12 prompts (props, characters, architecture, vehicles, nature, abstract). "One generation per prompt"; "No manual cleanup, retopology, or material edits afterward"; outputs exported as GLB and rendered alike. Visitors see two unlabelled results and vote. Ratings are Glicko-2, and entrants whose ratings cannot be told apart share a place. The ballots are published.
- Season 3, opened 2026-09-23, 4,789 ballots when read:

| Entrant | Rating | Placing |
|---|---|---|
| Claude Opus 5.5 | 1847 ± 72 | shares 1st |
| GPT-6.1 Sol | 1707 ± 68 | shares 1st |
| 3D-Agent (a product that drives Blender) | 1644 ± 65 | shares 2nd |
| GPT-6 Astra | 1570 ± 65 | shares 2nd |
| Claude Opus 5 | 1463 ± 63 | shares 3rd |
| Claude Fable 5.1 | 1387 ± 64 | shares 3rd |
| Claude Fable 5 | 1113 ± 81 | 4th |

- **No native generator is entered.** The site lists Tripo, Meshy, Hunyuan3D, Rodin and Trellis as "profile only". Its method page says generators are eligible and that "Mesh generators produce meshes from the same prompt text", but no generator has outputs in any season read. So this ranks LLMs against each other, not against generators.
- What it shows: by blind votes on looks, Opus 5.5 writing one `bpy` script is rated well above Opus 5, Fable 5.1 and Fable 5 doing the same. Fable 5.1 and Opus 5 are judged on files made for an earlier season.
- Its own stated limit: "Blind voting measures perceived output quality — not workflow speed, pricing, topology quality, or editability."
- Not established: who runs the site. It says it is independent and not a Blender project.

**Tripo's article on Claude Opus 5.5** ([tripo3d.ai blog](https://www.tripo3d.ai/blog/how-to-make-3d-models-with-claude-opus-5-5), 24 September 2026). *Vendor-run.*

- What was tested: six reference images (a backpack, three characters, a scooter, a bighorn ram), each given to Tripo, GPT-6 Astra and Claude Opus 5.5. Opus wrote a Blender script for each, run in Blender 5.1.2. Pictures of each result are published as grey models with wireframe. No scores, no files.
- Tripo's conclusion: "Claude Opus 5.5 can't generate production meshes on its own." "Either way, the output is a blockout. Hard-surface objects like the backpack and the scooter translate cleanly into primitives, while faces, hands, hair and cloth folds are approximated with spheres, lofts and shells."
- Tripo sells the alternative, so this is an interested party. It is still the only side-by-side found of a current Claude model and one of the two generators on the same reference images.

**LLMs only, no generator in the test.** [3DCodeBench](https://arxiv.org/abs/2606.01057) and [3DHarnessBench](https://arxiv.org/abs/2609.06535) (section 1); [CodeGen-3D](https://scholarworks.sjsu.edu/faculty_rsca/6835) (IEEE Access, January 2026; 100 prompts; only its abstract was read); [P3D-Bench](https://arxiv.org/abs/2606.11152) (not read).

### 4.2 An LLM driving a generator, or changing an existing mesh

**No controlled comparison was found**: nothing that takes generator output and measures it with and without an LLM's cleanup. What exists is nearby.

- **ViSculpt** ([arXiv 2608.24169](https://arxiv.org/abs/2608.24169), 25 August 2026). *Preprint.* LLM agents (Gemini 3 Flash and Pro) change an existing mesh by working Blender's own interface. 20 editing tasks; 48 people (39 non-experts, 9 experts) scored each result from 0 to 10. The system averaged 7.53 and human artists' edits of the same meshes 7.20. Two comparisons are shown in pictures only: against Blender's official MCP server with Claude Sonnet 4.6 writing scripts, and against re-generating the object through Hunyuan 2.0 or Rodin, which "often drifts from the original geometry". Limits: the authors' own 20 tasks; edits such as adding or reshaping a part, not reduction, UVs or checks.
- **Tripo's article**, as above. *Vendor-run*, one asset. Tripo generated a rigged, animated character; Claude Opus 5.5 "imported the GLB and read the file through Blender's Python API", checked "mesh health: no loose vertices or degenerate faces", added tail bones and rebuilt their weights, and reduced clipping. Tripo's own caveat: "Hands brushing the body on a few frames would still need a pass from an animator." A character, which kiln does not handle.
- **aDSL**, section 4.4 of the paper. The reverse order: the LLM-built mesh "serves as a spatial constraint for a pretrained generator such as Trellis". Shown in pictures, not measured.
- **Planner-Actor-Critic** ([arXiv 2601.05016](https://arxiv.org/abs/2601.05016), January 2026). *Preprint.* Several GPT-4.1 roles driving Blender through Blender-MCP, with Hyper3D Rodin among its tools. It reports better results than one agent alone, judged mostly by eye. No comparison with or without the generator was found in it.
- **LL3M** (section 1) compares itself with BlenderMCP in pictures only.

### 4.3 What working with an LLM in Blender cost and produced, by report

All *hands-on*: one project each.

- **Better Stack** ([guide](https://betterstack.com/community/guides/ai/opus-55-vs-gpt6-blender/), updated 29 September 2026). One project of three prompts: a detailed Formula 1 car, an animation of it being built, a pit-stop animation. Claude Opus 5.5 "produced a polished, professional result" and cost $27.86, writing 329,000 output tokens. Claude Fable 5.1 "produced a competent car with some visual artifacts" and "cost $42.44 and took 1 hour 13 minutes". GPT-6 Sol cost $4.50 for a weaker result. Pictures published; no files; the judgement is the author's.
- **MindStudio** ([post](https://www.mindstudio.ai/blog/claude-blender-mcp-60-percent-tokens-donut-test-results), 1 May 2026). A second-hand account of an unnamed tester's session with Claude Desktop and the Blender connector; the model version is not given. One scene, the well-known donut tutorial: "2 hours of back-and-forth, 60% of a 5x Max plan's session tokens consumed, and the final render had sprinkles clipping through the plate, a coffee cup clipping into the donut".
- **A four-build test by Pat Simmons**, read only through [a write-up by João Queirós](https://www.ai.joaoqueiros.com/blog/claude-opus-5-5-four-builds-fable-gpt-6-astra) (22 September 2026). One Blender task among four, a running shoe: GPT-6 Astra first, Opus 5.5 second ("the shoe was less convincing"), Fable 5.1 third. The original was not opened.

### 4.4 Tripo and Meshy against each other and other generators

The first version said no independent measurement of these could be found. There are public rankings and a few hands-on tests with numbers. None measures UVs or texel density, and none is a study with a stated sample and published files.

**Top 3D AI arena** ([top3d.ai](https://www.top3d.ai/), read 2026-10-08). *Leaderboard.*

- Method as stated: "The same prompt runs through every AI 3D generator, blind community votes decide the winners"; every tool gets the same reference image. 228,439 votes from 9,804 users in total.
- Top of each category when read, with the votes behind each rating:

| Category | 1st | 2nd | 3rd |
|---|---|---|---|
| Texture | Hi3D v3.0, 1,095 (139 votes) | Meshy 7, 1,092 (222) | Tripo AI v3.1, 1,091 (172) |
| Geometry | Meshy 7, 1,071 (222) | Hi3D v3.0, 1,069 (139) | Meshy 7.1, 1,058 (136) |
| Low poly | Tripo P2.0, 1,097 (73) | Tripo P1.0, 1,062 (114) | YVO3D 2.5, 1,057 (121) |
| Smart UV | Tripo Smart UV, 1,067 (107) | Hunyuan Semantic UV, 933 (107) | (two entrants) |

- Limits: each rating rests on a few dozen to a couple of hundred votes, and the leaders are a few points apart. Votes are on how a result looks in a viewer, not on counts. The site carries sponsored placements, which it says "do not affect rankings", and a Tripo discount code in one of its articles. Who runs it was not established.
- An earlier snapshot of the same arena, reported by a vendor ranked in it ([Sloyd's blog](https://www.sloyd.ai/blog/ai-3d-model-generator-rankings), 4 August 2026; 186,939 votes): Tripo AI v3.1 first at 1042 with an 88.6% win rate, Rodin Gen 2.5 sixth at 1009, Meshy 6 eighth at 1004 with 45.6%.

**3D Arena** ([arXiv 2506.18787](https://arxiv.org/abs/2506.18787), June 2025). *Leaderboard with a paper.* 123,243 votes from 8,096 users over 19 image-to-3D models. Its findings are about what voters reward: textured models gain 144.1 Elo over untextured ones. Its author says topology has "been largely overlooked" by such evaluations. The paper's models predate every current version; the live leaderboard could not be opened.

**A retopology test** ([top3d.ai](https://www.top3d.ai/learn/retopology-comparison-2025), 2 January 2026). *Hands-on, with counts.* One ball-like model, put through the reduction tools of Hunyuan 3D, Meshy and Tripo at about 1,000 and about 2,000 faces, then checked with Blender's 3D Print Toolbox. Pictures published; tool versions not stated.

| Count at about 1,000 / about 2,000 faces | Hunyuan 3D | Meshy | Tripo |
|---|---|---|---|
| Non-manifold edges | 0 / 0 | 21 / 6 | 6 / 31 |
| Intersecting faces | 0 / 0 | 0 / 2 | 3 / 0 |
| Zero-area faces | 570 / 964 | 725 / 3,301 | 2,048 / 3,974 |

- Its verdicts: Meshy, "Even after using Merge by Distance, geometry issues remain"; Tripo, "Manual cleanup is required. After merging vertices, the mesh becomes usable."
- Limits: one model. Some zero-area counts are larger than the stated face counts, which the page does not explain. This is the page with the Tripo discount code.

**A same-photo test** ([Fuser](https://fuser.studio/articles/meshy-vs-rodin-vs-tripo), 29 September 2026). *Hands-on, by a reseller of all three.* One product photo of a retro radio, one run each at the reseller's default settings, on 28 September 2026. Renders published; no files.

- Meshy 7: "30,076 triangles, which is the 30,000 target it was given", with three 2048-pixel textures. About five and a half minutes.
- Rodin Gen-2.5: 500,000 triangles.
- Tripo 2.5 (an older model than v3.1): 501,532 triangles and one colour texture, because PBR was off by default there. "It also invented details that are not in the photo". About 90 seconds.
- Rodin's mesh sent through Meshy's remesh with a 30,000 target came back at 67,416 triangles, and "the normal map was not carried over".

**A stress test by Meshy staff** ([HackerNoon](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show), 3 June 2026). *Vendor-run.* The earlier note listed this as a secondary source of unknown independence; its author writes "I'm Marcus Chen from the Meshy team". Meshy 6, Tripo v3.1 and Rodin Gen-2.5, through their APIs, April to May 2026, over five kinds of input. The number of samples is not given and no files are published.

- Blind votes on untextured shape, single image: Tripo over Rodin 77.90%; Rodin over Meshy 55.70%. Textured: Meshy over Rodin 83.90%. So Meshy's own staff rank Tripo's shape first.
- Image to 3D, median time: Tripo 99 seconds, Rodin 190, Meshy 195.
- One prompt sent to all three: 13,482 faces from Tripo, 17,438 from Meshy, 20,054 from Rodin.
- Of Meshy 6: "breaks on highly complex structures" and "Often merges adjacent parts".

**The vendors on themselves and each other.** *Vendor-run.*

- Meshy: "In our testing across 75 models, Meshy's character/figurine models achieved a 97% slicer pass rate", with "55% of models being fully watertight" ([Meshy blog](https://www.meshy.ai/blog/best-ai-tools-for-3d-printing), 5 March 2026). By that count 45% were not closed.
- Tripo's page against Meshy says "71.3% of professional 3D artists rated Tripo as the strongest choice", with no method ([Tripo](https://www.tripo3d.ai/compare/tripo-vs-meshy)). Meshy's page against Tripo claims the opposite on most rows ([Meshy](https://www.meshy.ai/compare/meshy-vs-tripo), updated 26 August 2026).
- Tripo's own guide to checking exports: "AI generators can produce non-manifold geometry, internal faces, or stray vertices"; "AI-generated UVs can be chaotic. Overlapping shells, excessive texel density variation, and missing UVs for certain parts of the mesh are common" ([Tripo blog](https://www.tripo3d.ai/blog/explore/ai-3d-model-generator-export-validation-against-engine-importers)). A vendor saying so about its own category.

**Papers.** [Mesh-Pro](https://arxiv.org/abs/2603.00526) (February 2026) shows its results beside Tripo's and Hunyuan3D's quad meshes in pictures and judges its own better. The [survey](https://arxiv.org/abs/2604.23629) the earlier note cites shows Rodin Gen 1.5, Tripo V2.5 and Meshy 5 in a figure with no numbers. No paper was found that measures Tripo's or Meshy's output.

### 4.5 What it adds up to

- **Approach 1.** Measured against open native generators on the same inputs, the best code-writing systems come out about level on how well pictures of the result match the prompt, sharper on edges, and behind on surface quality and on matching an input picture. Claude Opus 5.5 is the highest-rated LLM in the one public ranking that includes it. The only side-by-side of Opus 5.5 with Tripo is Tripo's, which calls the result "a blockout". All of it is about shape and looks. None of it measures UVs, texture maps, triangle budgets or anything in a game engine.
- **Approach 2.** Tripo and Meshy trade places near the top of public blind-vote rankings, within a few points. Tripo's low-poly models lead the one low-poly ranking. The few counted tests find non-manifold edges and zero-area faces in both vendors' reduced output, on one model. Both vendors' own writing concedes open or defective meshes.
- **Approach 3.** Still no measurement of the thing itself. One paper shows LLM agents making small edits to existing meshes that people rated like artists' edits. One vendor demonstration shows Opus 5.5 inspecting and repairing a Tripo character.

**What could not be opened or was not found.** Two Medium articles returned an error (a visual benchmark of image-to-3D services, and a Meshy workflow review). The Hugging Face 3D Arena leaderboard page did not load. Searches for Reddit, Hacker News, Blender Artists and YouTube comparisons of Claude with Blender against Tripo or Meshy returned no thread or video to read, and none was opened; this is a gap in the search, not evidence that none exists. A claim that 1,331 artists at NetEase and Tencent preferred Meshy 6 to Tripo 3.1 in 63.8% of votes appeared only in search summaries and on no page opened (unverified).

## 5. Side by side

"Documented" means a first-party page states it. "Claimed" means the vendor asserts quality. "Measured" means a source in section 4 gives numbers, on the models it names. "No evidence" means nothing was found either way.

| | 1. LLM alone (`bpy` script) | 2. Tripo or Meshy directly | 3. Claude driving a generator |
|---|---|---|---|
| First shape comes from | Primitives assembled by code | A model trained on 3D data | As 2 |
| Works from a reference image | By looking; sight documented as approximate | Yes, the main input | As 2 |
| Flat-sided props | Sharper edges than open generators (measured, one preprint, machines); "translate cleanly into primitives" (Tripo, on Opus 5.5) | Claimed for the low-poly models, which lead one public low-poly ranking; open generators measured as soft-edged | As 2 |
| Organic shapes (rocks) | Floating parts and simplified forms on older models (measured); "approximated with spheres, lofts and shells" on Opus 5.5 (Tripo) | Claimed; open generators give "smoother surfaces" than code (one preprint) | As 2 |
| Matching a reference image | Behind an open generator (measured, one preprint, 30 objects) | Ahead, same source | As 2 |
| Exact size in metres | Yes, by construction | No; a guess if asked | Kiln scales, as now |
| Triangle count | Exact, by construction | A target | Kiln reduces or checks |
| UVs | Blender's automatic unwrap | Delivered; undocumented | Either |
| Textures | Procedural, then baked; no evidence | Delivered: PBR, 2K and up | As 2 |
| Baked-in lighting | Does not arise | A switch to remove it; claimed | As 2 |
| Repeatable | The script, yes; the LLM, no | Tripo: seed, claimed. Meshy: no | The generation as 2; the cleanup only if it is a fixed script |
| Runs unattended | Yes | Yes | Yes |
| Comparison evidence | Two preprints against open generators; one public ranking of LLMs that includes Opus 5.5 and Fable 5.1; one vendor side-by-side with Tripo. Shape and looks only | Public blind-vote rankings; a few hands-on tests, one with defect counts; vendor-run tests. No UV or texel measurements | No controlled measurement; one paper on mesh edits; one vendor demonstration |
| Cost of one try | About $0.20 to $1.20 (arithmetic); $27.86 and $42.44 reported for one detailed project | $0.30 to $0.60 at list price | As 2, plus tokens |
| Commercial use without credit | Yes (API terms) | Paid plans only | As 2 |
| Vendor trains on the work | No (API terms) | Tripo paid: no. Meshy non-Enterprise: may | As 2 for the asset |
| Within kiln's stated scope | No: "Building assets by script" is out of scope | Yes | Yes for the generation |

## 6. The cost of one asset, worked

**All arithmetic, except the last subsection. Nothing was measured by this note.** The numbers that are guesses are marked.

### Shared assumptions

- Prices as in sections 1 and 2.
- A person rejects some results at shape review. **Guess: three generations for each asset approved.** The true figure is exactly what a generator trial would find.
- One look by Claude at a set of review pictures: 8 pictures at 1920×1080 (the set in `crates/asset_view/src/views.rs`), 2,691 tokens each, 21,528 tokens, plus **a guessed 2,000 tokens** written in reply.

### Approach 1: the LLM alone

**Guesses:** 8 tries. A fixed prompt of 5,000 tokens. Each try: 4,000 tokens written (thinking and the script), then 22,000 tokens read back (the 8 pictures and a short log). Every try re-reads everything before it, so the tokens read add up to 768,000 over the 8 tries, and 32,000 are written.

| | Claude Opus 5.5 | Claude Fable 5.1 |
|---|---|---|
| Read, without caching: 768,000 tokens | $3.07 | $7.68 |
| Written: 32,000 tokens | $0.64 | $1.60 |
| **Total without caching** | **$3.71** | **$9.28** |
| With prompt caching: 187,000 tokens written to the cache, 581,000 read from it | $0.94 + $0.12 | $2.34 + $0.15 |
| **Total with caching** | **$1.69** | **$4.08** |

- Smaller pictures cut this sharply: at about 1000×560 a picture is 756 tokens, not 2,691.
- One try with no pictures (write a script, run it) is about 9,000 tokens read and 4,000 written: about $0.12 on Opus 5.5 and $0.29 on Fable 5.1. That is in line with the $0.14 an object 3DCodeBench reports for Opus 4.7.
- This buys geometry. Textures would be further work of unknown size.
- Blender's own time is free and, by the earlier note's trial, seconds.

### Approach 2: a generator directly

| | One generation | Three generations (guess) |
|---|---|---|
| Tripo API, image to 3D, standard textures | $0.30 | $0.90 |
| Tripo, the same with smart low-poly | $0.40 | $1.20 |
| Meshy `meshy-7.1`, 2K textures, at the Pro rate | $0.60 | $1.80 |
| Meshy `meshy-t2`, 2K textures | $0.30 | $0.90 |

- Meshy needs a subscription to use the API at all, so the floor is $20 in any month an asset is generated. Tripo's API is pay as you go with a $10 smallest purchase shown on its Studio page.
- A person's time at shape review is the larger cost and is the same under every approach.

### Approach 3: Claude driving a generator

| | Opus 5.5 | Fable 5.1 |
|---|---|---|
| Three Tripo generations | $0.90 | $0.90 |
| Claude looks at each of the three (21,528 read, 2,000 written, each) | $0.38 | $0.95 |
| **Total, Claude as a reviewer only** | **$1.28** | **$1.85** |
| Instead, a full loop per asset on the scale of approach 1, with caching | $0.90 + $1.69 = $2.59 | $0.90 + $4.08 = $4.98 |

At list prices and with these guesses no approach is expensive for one asset; the reported figures below show the LLM route can cost fifty times a generation when the job is large. The differences that matter are what comes out and what the licence allows, not the bill (inference).

### What others report it cost

These are the only real figures found, and they sit well apart from the arithmetic above.

| Source | What was built | Reported |
|---|---|---|
| 3DCodeBench (preprint) | One object, geometry only, one script | $0.14 on Claude Opus 4.7; $0.29 on Claude Sonnet 4.6 |
| aDSL (preprint) | One object in a checking loop | About 31,000 tokens read and 2,750 written a round, 4.25 to 5.23 rounds, about 190 seconds a round |
| Better Stack (hands-on) | A detailed car and two animations of it, three prompts | $27.86 on Opus 5.5 (329,000 tokens written); $42.44 and 1 hour 13 minutes on Fable 5.1 |
| HackerNoon, by Meshy staff (vendor-run) | One prompt, one generation | $0.18 Tripo v3.1, $0.20 Meshy 6, $0.25 Rodin Gen-2.5 |

The arithmetic for approach 1 assumed 32,000 tokens written for one asset. The one reported project wrote ten times that. A simple static prop is a smaller job than an animated racing car, so the truth for kiln is somewhere between and is not known (inference).

## 7. What remains unknown, and the experiment in kiln

### Unknown

1. **How the two named models do against a generator, from a reference image.** They have been ranked against other LLMs from text prompts (Opus 5.5 first, Fable 5.1 lower), and Opus 5.5 has been set beside Tripo once, by Tripo.
2. **UVs and texture maps from an LLM's script.** No measurement of any model.
3. **The condition of a real Tripo or Meshy raw output.** One counted test of reduced output on one model, and the vendors' own admissions; nothing on UVs, texel density or baked-in lighting, and nothing on the kinds of asset kiln handles.
4. **Whether an LLM's cleanup beats a fixed script's, or beats leaving the output alone.** No measurement by anyone.
5. **Whether Tripo's seed gives the same file twice.**
6. **How many generations it takes to get one a person approves**, per kind of asset. Every cost above turns on it.
7. **Tripo's API-only customer and "Paid User".** A question for Tripo.
8. **Whether any of the published comparisons carries over to games.** Every one of them judges pictures or votes on looks. None loads a result in an engine, checks it against a triangle or texture budget, or looks at it from a player's distance.

### The experiment

Everything it needs except the generator accounts is already in the repo. It is a generator trial with three entrants and, after the second pass, an optional fourth step. No published source has put all three approaches through one test, so this would be the first such comparison found, not a repeat of one.

- **Inputs.** Two or three reference images made for the purpose, one per kind of asset: a rock, a flat-sided prop such as a crate, a building piece on the 3 m grid. Each with a size in metres. (`learn/specimens/` holds a boulder and a crate from the first attempt; they are files to inspect, not inputs to reuse.)
- **Entrants.**
  - Tripo, image to 3D, once dense and once with its low-poly route, seed fixed.
  - Meshy, the same two ways.
  - Claude writing a `bpy` script run by `tools/bl`, with a fixed limit of tries and kiln's review pictures as its only feedback. Once with Opus 5.5 and once with Fable 5.1 if the cost is acceptable.
- **The same treatment for every result.** `python3 -m kiln run --model <file> --size <m> --profile pit --licence <text> --source <text>`, then the review pictures, then `python3 -m kiln review <name> --approve` on those that pass the eye, which builds and checks.
- **Record, for each result:**
  1. Whether the shape review approved it, and after how many tries.
  2. What `python3 -m kiln.measure` reports: triangles, bounding box, materials, textures, UVs, texel density, validator result.
  3. Which checks of the target profile failed, and by how much.
  4. Anything seen in the pictures at the closest viewing distance: floating parts, holes, lighting painted into the colour, visible seams, edges that should be sharp and are rounded, details that are not in the reference image.
  4a. Defect counts on the mesh, the kind the one published counted test used: non-manifold edges, zero-area faces, intersecting faces, boundary edges. Blender's 3D Print Toolbox reports the first three; whether `kiln.measure` already does was not checked.
  4b. A second set of review pictures with textures off, since every published comparison of shape was made that way and textures raise votes (144 Elo in one arena).
  5. Cost: credits or tokens, including the tries thrown away. Wall-clock time.
  6. For Tripo: the same request twice with the same seed, and whether the two files are the same.
  7. The licence text that would go in the asset record, with the plan held.
- **The optional fourth step, for approach 3.** Take the generator results that failed a check or were rejected for a fixable reason. Put each through (a) a fixed Blender script and (b) Claude with `tools/bl`, the same pictures and a fixed number of tries, and measure both again. This is the comparison section 4.2 could not find anywhere.
- **What it would show.** Items 1 to 4b answer whether approach 1 is usable at all for each kind of asset, and what state generator output arrives in. Item 5 replaces section 6's guesses. Item 6 settles the seed. For approach 3, the first question is whether the fixes found necessary in items 3 to 4a are the same every time (then they are a script in `kiln/blender_scripts/`) or different every time (then something has to decide); the fourth step measures whether an LLM deciding does better.

It can be run in two parts. The Claude entrant costs no new account and can be run first; by itself it answers unknowns 1 and 2 for kiln's kinds of asset. The published evidence suggests where to look hardest: flat-sided props are where code did best, and matching a reference image and organic shapes are where it did worst.

## What could not be verified, and where sources disagreed

**Not verified from a primary source**

- Any capability of Claude Fable 5.1 or Claude Opus 5.5 at 3D modelling, beyond one public ranking by blind votes, one vendor side-by-side and two hands-on reports (section 4). The papers test Opus 4.5, 4.6 and 4.7, Sonnet 4.6, Fable 5 and Opus 5.
- Whether these two models accept a setting that makes their output more repeatable.
- Which of Anthropic's two sets of terms covers Claude Code used on a personal subscription.
- Anthropic's rate limits; the page was not read.
- Tripo: whether a pay-as-you-go API customer is a "Paid User"; the pixel size of standard textures; the true monthly Studio prices; how long output links last ("temporary", with no figure); anything about the `tripo-cli` package beyond Tripo's own documentation, because its package page refused the request.
- Meshy: whether subscription credits and API credits are the same pool at the same price (the API pricing page says "Purchase API credits from your subscription settings"; the playground page says requests use "your plan credits"); which way its output faces; the `meshy-3d-agent` repository's contents.
- The Blender MCP servers in background mode: since settled by the [later note](claude-tripo-blender-workflows.md). The community server refuses it; Blender Lab's supports it. Neither was run.
- A study of Tripo or Meshy output with a stated sample and published files: none found. Section 4.4 lists the rankings and hands-on tests that do exist. Who runs the Top 3D AI arena and the Blender AI Arena was not established.
- Any controlled measurement of an LLM cleaning up generated meshes: none found.
- Pages that could not be opened in the second pass, and the search that came up empty for forum threads and videos, are listed at the end of section 4.5. The claim of a 1,331-vote artist study favouring Meshy 6 is unverified.
- In section 4, papers were searched for the passages quoted, not read end to end. Affiliations are given only for 3DCodeBench.
- The law on copyright in generated output. The US Copyright Office published a report on it on 29 January 2025 ([Copyright and Artificial Intelligence, Part 2](https://www.copyright.gov/ai/)); only its index page was read, not its conclusions. This note gives no view on the law.
- The earlier notes' facts about Tripo's and Meshy's Blender add-ons, quad output and remesh behaviour are cited from those notes and were not all re-read.

**Sources disagree**

- **Tripo on how many tasks run at once:** the [rate limits page](https://developers.tripo3d.com/en/docs/rate-limits) says 10 for H-series generation; the [model page](https://developers.tripo3d.com/en/models/v3-1) says "3 parallel tasks".
- **Tripo's Studio prices:** the page labels annual billing "50% off" while showing the same $20 for Pro both ways.
- **Meshy on training:** pricing FAQ says no training "without your consent"; terms section 2.9 says it may train on non-Enterprise customers' inputs and outputs.
- **Meshy's rate-limit tiers:** one table in its documentation lists Pro, Studio and Enterprise; another on the rate-limits page adds Premium and Ultra and gives Enterprise a different queue size.
- **The two benchmarks on Claude:** 3DCodeBench puts Claude Opus 4.7 below the leaders by human vote; 3DHarnessBench finds Claude Opus 5 "strongest overall" in its interactive settings. They test different models on different tasks (making from a prompt against copying a 3D object), so this is not a contradiction, but neither should be read as "Claude is good" or "Claude is bad" at this.
- **The vendors on each other:** Meshy's and Tripo's comparison pages each claim to be preferred. A test by Meshy staff ranks Tripo's untextured shape first; the Top 3D AI arena puts Meshy 7 first for geometry.
- **Fable 5.1 against Opus 5.5:** Anthropic describes Fable 5.1 as the model for the most demanding work; in the Blender AI Arena and in both hands-on reports Opus 5.5 did as well or better at Blender tasks for less. Small samples in every case.
- **This note against the earlier note:** the earlier note called the HackerNoon stress test a secondary source of unknown independence. Its author states he works for Meshy.

## Sources

All read 2026-10-08.

**Anthropic**

- [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Vision](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)
- [MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
- [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms), effective 17 June 2025
- [Consumer Terms of Service](https://www.anthropic.com/legal/consumer-terms), effective 8 October 2025
- [Claude for Creative Work](https://www.anthropic.com/news/claude-for-creative-work), 28 April 2026, updated 1 May 2026

**Blender**

- [Command-line arguments, Blender 5.2 manual](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html)
- [Blender 5.2 Python API documentation](https://docs.blender.org/api/current/index.html) and its [tips and tricks page](https://docs.blender.org/api/current/info_tips_and_tricks.html)
- [MCP Server, Blender Lab](https://www.blender.org/lab/mcp-server/)
- [`ahujasid/blender-mcp`](https://github.com/ahujasid/blender-mcp) README and repository record (the community server)

**Tripo**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt) and [index](https://developers.tripo3d.com/llms.txt)
- [API pricing](https://developers.tripo3d.com/en/pricing)
- [Model v3.1 page](https://developers.tripo3d.com/en/models/v3-1)
- [Studio pricing](https://www.tripo3d.ai/pricing)
- [Terms of Service](https://www.tripo3d.ai/terms), last updated 11 July 2025
- [`VAST-AI-Research/tripo-mcp`](https://github.com/VAST-AI-Research/tripo-mcp) README and repository record

**Meshy**

- [API documentation, full text](https://docs.meshy.ai/llms-full.txt), which includes the [API pricing](https://docs.meshy.ai/api/pricing), [rate limits](https://docs.meshy.ai/api/rate-limits), [asset retention](https://docs.meshy.ai/api/asset-retention), [AI integration](https://docs.meshy.ai/api/ai) and [changelog](https://docs.meshy.ai/api/changelog) pages
- [Pricing](https://www.meshy.ai/pricing)
- [Terms of Use](https://www.meshy.ai/terms-of-use), last updated 19 September 2026
- [`meshy-dev/meshy-mcp-server`](https://github.com/meshy-dev/meshy-mcp-server) repository record

**Papers**

- [3DCodeBench: Benchmarking Agentic Procedural 3D Modeling Via Code](https://arxiv.org/abs/2606.01057), Gao et al., 31 May 2026
- [3DHarnessBench: Probing Agentic 3D-to-Code Capabilities of Frontier Vision-Language Models](https://arxiv.org/abs/2609.06535), Liu et al., 6 September 2026
- [BlenderGym: Benchmarking Foundational Model Systems for Graphics Editing](https://arxiv.org/abs/2504.01786), Gu et al., 2 April 2025
- [LL3M: Large Language 3D Modelers](https://arxiv.org/abs/2508.08228), Lu et al., 11 August 2025
- [3D-GPT: Procedural 3D Modeling with Large Language Models](https://arxiv.org/abs/2310.12945), Sun et al., 19 October 2023
- [LLaMA-Mesh: Unifying 3D Mesh Generation with Language Models](https://arxiv.org/abs/2411.09595), Wang et al., 14 November 2024

**Comparison data (second pass)**

- [aDSL: Agentic 3D Creation via Joint Agent-Program Design](https://arxiv.org/abs/2608.17975), Wang et al., 18 August 2026. Preprint.
- [Procedura: Agentic 3D Modeling with Procedural Control](https://arxiv.org/abs/2608.26238), Lin et al., 26 August 2026. Preprint.
- [ViSculpt: Visual-Centric Agentic Geometry Editing](https://arxiv.org/abs/2608.24169), Pang et al., 25 August 2026. Preprint.
- [From Idea to Co-Creation: A Planner-Actor-Critic Framework for Agent Augmented 3D Modeling](https://arxiv.org/abs/2601.05016), Gao and Juluri, 8 January 2026. Preprint.
- [3D Arena: An Open Platform for Generative 3D Evaluation](https://arxiv.org/abs/2506.18787), Ebert, 23 June 2025. Leaderboard with a paper.
- [Mesh-Pro](https://arxiv.org/abs/2603.00526), 28 February 2026. Preprint.
- [CodeGen-3D](https://scholarworks.sjsu.edu/faculty_rsca/6835), Ji et al., IEEE Access, 15 January 2026. Abstract only.
- [Blender AI Arena](https://blenderai.org/leaderboard): leaderboard, [methodology](https://blenderai.org/methodology), [about](https://blenderai.org/about), and its [Claude page](https://blenderai.org/models/claude). Leaderboard.
- [Top 3D AI arena](https://www.top3d.ai/) and its [retopology comparison](https://www.top3d.ai/learn/retopology-comparison-2025), 2 January 2026. Leaderboard; hands-on.
- [Sloyd: Best AI 3D Model Generator 2026: ELO Arena Rankings](https://www.sloyd.ai/blog/ai-3d-model-generator-rankings), 4 August 2026. Vendor reporting a leaderboard.
- [Tripo: How to Make 3D Models with Claude Opus 5.5](https://www.tripo3d.ai/blog/how-to-make-3d-models-with-claude-opus-5-5), 24 September 2026. Vendor-run.
- [Tripo vs Meshy](https://www.tripo3d.ai/compare/tripo-vs-meshy) and [Meshy vs Tripo](https://www.meshy.ai/compare/meshy-vs-tripo). Vendor-run.
- [Meshy: Best AI Tools for 3D Printing](https://www.meshy.ai/blog/best-ai-tools-for-3d-printing), 5 March 2026. Vendor-run.
- [Tripo: Validating AI-Generated 3D Models for Game Engine Import](https://www.tripo3d.ai/blog/explore/ai-3d-model-generator-export-validation-against-engine-importers). Vendor.
- [HackerNoon: How I Stress-Tested 3 AI 3D Generators on the Same Inputs](https://hackernoon.com/how-i-stress-tested-3-ai-3d-generators-on-the-same-inputs-what-the-numbers-actually-show), 3 June 2026. Vendor-run (Meshy staff).
- [Fuser: Meshy 7 vs Rodin Gen-2.5 vs Tripo 2.5: Same-Photo 3D Test](https://fuser.studio/articles/meshy-vs-rodin-vs-tripo), 29 September 2026. Hands-on by a reseller.
- [Better Stack: Claude Opus 5.5 vs GPT-6 Sol: Creating a Ferrari F1 Car in Blender](https://betterstack.com/community/guides/ai/opus-55-vs-gpt6-blender/), updated 29 September 2026. Hands-on.
- [MindStudio: Claude's Blender MCP Burned 60% of a $200/Month Plan on One Donut](https://www.mindstudio.ai/blog/claude-blender-mcp-60-percent-tokens-donut-test-results), 1 May 2026. Hands-on, second-hand.
- [João Queirós: Claude Opus 5.5 Tested: Four Builds Against Fable 5.1 and GPT-6 Astra](https://www.ai.joaoqueiros.com/blog/claude-opus-5-5-four-builds-fable-gpt-6-astra), 22 September 2026. Hands-on, second-hand.

**Other**

- [US Copyright Office, Copyright and Artificial Intelligence](https://www.copyright.gov/ai/) (index page only)

## Method

Research was done on 2026-10-08. Tripo's and Meshy's API documentation, terms and pricing pages, the Blender manual and API pages, the Blender Lab page, the repository READMEs, Anthropic's two sets of terms and its Blender announcement were downloaded as raw text or HTML and searched directly, not through a summariser. Meshy's plan prices are drawn in the browser; they were read from the structured data embedded in the page. Anthropic's documentation pages were fetched through a tool that returned their Markdown source. The six papers' abstracts were read from arXiv's own pages, and the full text of 3DCodeBench and 3DHarnessBench from arXiv's HTML versions. Web searches were used only to find primary sources; nothing is cited from a search result, a blog or a comparison article.

Pages that refused the request: Tripo's pricing page through the fetch tool (it loaded by direct download), the Blender Lab source repository, and the npm page for `tripo-cli`.

The second pass, the same day, lifted the first-party rule to look for comparison data. It used about fifteen web searches with different phrasings across papers, leaderboards, vendor pages and hands-on reports, then downloaded each candidate page and searched its text directly. Papers were searched for their comparison tables and the passages quoted; they were not read end to end. Section 4.5 lists what could not be opened and where the search found nothing. Each source in section 4 carries a grade, and nothing from a vendor-run or hands-on source is stated as a finding without that label.

Facts about kiln are from `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, `tools/bl` and `crates/asset_view/src/views.rs`. Facts marked "earlier note" are from the two notes named at the top and were re-read only where a quotation appears here. No generator API was called, no account was created, no model was asked to build anything, and no file from the `first-attempt` tag was used. Only this file was written.
