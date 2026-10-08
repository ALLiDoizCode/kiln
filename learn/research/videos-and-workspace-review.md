# Six videos and one repository by one creator: what they show about an LLM, Tripo and Blender making game assets

Researched 2026-10-08. Every video, repository and page cited below was read on that date. The tools shown change within weeks (one feature here was released the day its video was uploaded); check each again before relying on it.

This is a research note. It reports what seven sources supplied by the owner show, and sets them against the earlier notes: [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md), [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md), [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md) and [`mixar-vs-tripo.md`](mixar-vs-tripo.md) (called "the earlier notes" below). It does not choose anything. It does not draw on the `first-attempt` tag.

**Nothing here was tested, and no video was watched.** The videos were read as captions and as still frames pulled at chosen moments. The repository was cloned and read as text; nothing in it was run. No generator was called and no account was created.

## The question

What do these six videos and one repository show about getting game-ready 3D models with an LLM, a 3D generator, an image generator and Blender; and are they the hands-on evidence, with files, of Claude plus a generator plus Blender producing a static game asset that the earlier notes could not find?

## How to read this

- **Shown** means it is visible in a frame that was looked at. **Said** means it is in the captions. Where it matters, each statement says which.
- **Demonstrated on screen**, **asserted without showing** and **contradicted by what is shown** are the three marks put on each claim a video makes.
- **Docs** means Tripo's own API documentation, read today, says so.
- **Inference** means the sentence is this note's reasoning from what is cited.
- **Arithmetic** means a number worked out from prices shown or listed. No cost was measured.
- **Grades** are the earlier notes' grades with one addition. *Interested party*: the source is a vendor, is sponsored, or earns from referrals to a tool it shows. *Hands-on*: one person's report, with the number of assets and whether files are published. *Tutorial without results*: it explains a tool and produces no asset. A video is one person's report, not a measurement.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, review pictures, asset record, static asset) are used as `CONTEXT.md` defines them.
- Quotations from videos are the captions' wording, which is machine-made and rough; the speaker is not a native English speaker. A timestamp is the start of the half-minute of captions the words fall in, or the second of the frame read; the words may come up to 30 seconds after it.

### Terms used here

The earlier notes define mesh, triangle, quad, topology, UV, UV island, seam, PBR, base colour, normal map, roughness, metallic, decimation, retopology, baking, texel density, LLM, MCP, CLI, Agent Skill, add-on, credit and headless. Terms added by this note:

- **Low-poly:** a mesh made with few polygons from the start, as opposed to a dense one reduced afterwards. **High-poly** is the dense kind.
- **Wireframe:** a picture of a mesh that draws its edges, so the layout of its polygons can be judged.
- **Part:** one separately generated piece of an object (a head, a belt, a wing), later put together with the others.
- **Rig:** a skeleton inside a mesh that lets it be posed. Rigging, animation and visual effects (**VFX**) are outside what kiln handles; they are named only to say what a video spent its time on.
- **A-pose, T-pose:** standing poses with the arms held away from the body, used so a character's parts do not hide each other.
- **Affiliate or referral link:** a link that pays the person who posted it when a viewer signs up or buys.
- **Tripo Studio:** Tripo's web app, used by hand in a browser. It is not the API or the CLI the earlier notes describe, and what it offers is not always what they offer.
- **Bypass mode:** starting a coding agent with its permission prompts switched off, so it runs any command without asking.

## Summary

### The sources

All seven are by one person. The repository belongs to video 2, whose description links it; video 6 links it too.

| | Source | What it is | Grade |
|---|---|---|---|
| 1 | [Video, 2026-10-05](https://www.youtube.com/watch?v=CgslUZIAl4s): "From Idea to Game in ONE Day with AI" | A winged character made in parts with Tripo P2.0, assembled by hand in Blender, with an LLM making texture maps, animations and effects | Interested party (Tripo referral link); hands-on, one character, no files |
| 2 | [Video, 2026-09-21](https://www.youtube.com/watch?v=gV23ON8BgwU): "My Full AI Workspace" | A tour of his desktop program for running coding agents | Sponsored (Higgsfield, spoken); tutorial without results |
| 3 | [Repository](https://github.com/witnesstodark/mr-mak-workspace) `witnesstodark/mr-mak-workspace` at `1e0c7c3` | That program, MIT licence, with twenty instruction files ("skills") for agents | Interested party's tool; instructions without results |
| 4 | [Video, 2026-09-19](https://www.youtube.com/watch?v=VeOU0FnTjjc): "1 Min vs 1 H vs 10 H" | One character made three times with more time each | Interested party (Tripo referral link); hands-on, one character, no files. No LLM in it |
| 5 | [Video, 2026-07-22](https://www.youtube.com/watch?v=gSHON893CCI): "Easy Clothing with AI" | Generated clothing fitted to a character; mostly Unreal Engine cloth physics | Interested party (Lychee Studio referral links); hands-on, one costume, no files. No LLM in it |
| 6 | [Video, 2026-09-30](https://www.youtube.com/watch?v=ZksPNRPupWs): "AI Can Now Create VFX" | Game effects and one character made with an LLM | Interested party (Tripo referral link); hands-on, one character, no files |
| 7 | [Video, 2026-09-18](https://www.youtube.com/watch?v=1vw39QCcQjg): "AI Just Solved UV Unwrapping" | First look at Tripo's Smart UV and P2.0; two characters | Interested party (Tripo referral link, early access); hands-on, about ten objects unwrapped, no files. No LLM in it |

### What the sources support

- **They are not the missing evidence.** None shows Claude, a generator's API or CLI, and headless Blender producing a static game asset. No file is published by any of them, and nothing is measured against a budget.
- **The workflow they show is a different one from the design being considered.** A person works Tripo's web app by hand, generating an object as several parts; a person assembles and repairs the parts in Blender by hand; an LLM is brought in afterwards, for texture maps, rigging help, animation, effects and engine code. The LLM named most often is OpenAI's GPT-6 Astra through Codex CLI. Claude Code appears as one of the agents the workspace runs.
- **One step shows an LLM improving a generated asset, on screen, with the prompt and the report.** In video 1 an agent reads the colour texture of one Tripo part in Blender, writes a normal map and a roughness map computed from it, and connects them to the material (section 1). One object; no close view of the result; no comparison.
- **Tripo P2.0 in the web app makes quad low-poly meshes at a chosen polygon count, four counts at a time, and a person picks one.** Shown in videos 1, 6 and 7. The creator's method is to pick by looking at the wireframe.
- **Tripo's web app now unwraps UVs ("Smart UV"), for 20 credits, in about five seconds, with free retries.** Shown on about ten objects in video 7, four of them static. The layouts have few, large islands on simple objects and hundreds on a robot generated whole. Tripo's API documentation, read today, has no such endpoint (section 8).
- **Every mesh-level defect in these videos is fixed by a person, by hand.** Holes, stray flat pieces, bent parts, a double-sided cloth, weak texture detail and stray UV islands are all admitted (sections 4 and 7).
- **The creator's own view is that an LLM is the slower and dearer way to do the Blender mesh work.** "You're going to wait like for one hour, two hours, spend a lot of tokens and still most likely going to need to fix some stuff" (video 1; asserted, not shown).
- **The repository is a place to run agents, not a pipeline.** It has no Blender script, no call to Tripo, no MCP server configured and no hooks. It can start every agent with permission prompts off, which is how its author runs it (section 3).

### What the sources do not settle

- Anything about a static prop beyond what its UV layout looks like in Tripo's own panel. No prop is exported, measured, textured on screen or shown in an engine.
- Whether P2.0 at a low polygon count is better for a prop than a dense generation reduced in Blender. The creator says so for stylised characters and says he tested it; the test is not shown.
- Whether Smart UV, the four-variant generation, or anything else seen in the web app can be reached through the API or the CLI.
- Orientation, scale, seeds, repeatability, baked-in lighting, licence, and the number of materials and images in a raw output. None is discussed in any of the seven.
- Cost. One video promises "the real cost of creating one complete character" and does not give it.

### The smallest experiments

Unchanged from the earlier notes, with two additions that these sources make worth the credits: put P2 at the target profile's triangle budget into the generator trial beside the dense route; and, on whichever raw output has a flat-looking surface, run a fixed script that derives a normal map from the base colour and look at it in the review pictures at 0.5 m. Section 11 gives the reasoning.

## 1. Video: "From Idea to Game in ONE Day with AI - Fastest Character Workflow"

[youtube.com/watch?v=CgslUZIAl4s](https://www.youtube.com/watch?v=CgslUZIAl4s). Stefan 3D AI, uploaded 2026-10-05, 13 minutes 15 seconds, 63,594 views when read.

### What it is

- **Stated purpose:** "create game-ready character with AI in just one day", with animations and effects, running in his game ([0:00](https://www.youtube.com/watch?v=CgslUZIAl4s&t=0s)). The asset is a winged character (a harpy) for a strategy game.
- **Interest:** the description's first link is a Tripo referral link with a discount code ("Use code TRIPOCREW for 60% off your first month of Pro"). No sponsorship is spoken. The Tripo account on screen holds 1,176,995 credits ([2:02](https://www.youtube.com/watch?v=CgslUZIAl4s&t=122s)); at Tripo's API rate of $0.01 a credit that is about $11,770 (arithmetic), which an ordinary customer would be unlikely to hold. Where the credits came from is not said (inference: the creator is not an arm's-length customer of Tripo). He also sells a course, linked in the description and advertised in the video ([4:34](https://www.youtube.com/watch?v=CgslUZIAl4s&t=274s)).
- **Grade:** interested party (affiliate), individual hands-on report, one asset, a character. No files published.

### The workflow shown

| Step | Who does it | What is shown | Where |
|---|---|---|---|
| 1. Put the character concept into an A-pose and cut it into separate pictures, one per part | "You can just do that with your agent", using the skills in his repository (section 3). Not shown being done | Eight part pictures on screen: head, torso with arms, legs, chest armour, bracer, cloth pieces, hair braid, one wing | [0:31](https://www.youtube.com/watch?v=CgslUZIAl4s&t=31s), [0:50](https://www.youtube.com/watch?v=CgslUZIAl4s&t=50s) |
| 2. Generate a model from each part picture | A person, in Tripo Studio (the web app) | Settings panel, below | [1:20](https://www.youtube.com/watch?v=CgslUZIAl4s&t=80s) |
| 3. Unwrap each low-poly part with "Smart UV" | A person, in Tripo Studio | Panel shows "Utilization 72.4%", a "Free Retry (x3)" button, "Topology Quad, Faces 1786, Vertices 1547" for the hair braid | [2:02](https://www.youtube.com/watch?v=CgslUZIAl4s&t=122s) |
| 4. Texture each part in Tripo | A person, in Tripo Studio | Not shown in detail | [3:03](https://www.youtube.com/watch?v=CgslUZIAl4s&t=183s) |
| 5. Assemble the parts in Blender | A person, by hand: move parts, "remove few polygons", sculpt mode with the Elastic Grab brush | Blender viewport | [3:33](https://www.youtube.com/watch?v=CgslUZIAl4s&t=213s) |
| 6. Make normal and roughness maps from the colour texture | An LLM agent working in the open Blender scene | The prompt and the agent's report, below | [5:05](https://www.youtube.com/watch?v=CgslUZIAl4s&t=305s) |
| 7. Rig the body | A person, in Mixamo's auto-rigger; wings left for later | Mixamo "AUTO-RIGGER" marker screen | [7:40](https://www.youtube.com/watch?v=CgslUZIAl4s&t=460s) |
| 8. Animate | An LLM (he names "GPT-6 Astra") in a Codex CLI session called "Overlord Animations", with his review | Blender timeline; a small Blender add-on the LLM wrote, "Harpy Animation Review", with buttons to switch clip and "Set Pose" | [8:41](https://www.youtube.com/watch?v=CgslUZIAl4s&t=521s), [10:00](https://www.youtube.com/watch?v=CgslUZIAl4s&t=600s) |
| 9. Effects and putting it in the game | A second LLM session, "Overlord Unity" | The character flying and attacking in a Unity scene | [10:42](https://www.youtube.com/watch?v=CgslUZIAl4s&t=642s), [11:42](https://www.youtube.com/watch?v=CgslUZIAl4s&t=702s) |

Steps 7 to 9 are rigging, animation and effects, which kiln does not handle. They are recorded here only so the whole of what the video claims is on the page.

**The Tripo settings panel** ([1:30](https://www.youtube.com/watch?v=CgslUZIAl4s&t=90s), read from a frame):

- "AI Model: P2.0".
- "Topology": "Quad" (marked "New") or "Triangle". Quad is selected.
- "Number of Generation": 1, 2 or 4. Four is selected, and "Customize Poly Counts" opens four sliders, each from 500 to 25,000. The values typed for the hair braid are 753, 1010, 7639 and 8822.
- The button reads "Generate 100" with the credit symbol: 100 credits for the four.
- Spoken: "for one generation you basically can generate four with different poly counts ... figure out the right range and within that range set like four different numbers", then pick the one "where the wireframe is most accurate" ([1:02](https://www.youtube.com/watch?v=CgslUZIAl4s&t=62s) to [1:33](https://www.youtube.com/watch?v=CgslUZIAl4s&t=93s)).

**The wing reference image** ([2:56](https://www.youtube.com/watch?v=CgslUZIAl4s&t=176s), read from a frame). Inside Tripo Studio's image tool, model label "Nano Banana 2", dated 2026.09.26, the prompt on screen is:

> The feathers lie very tightly against the wing, as if they were a feather texture rather than actual geometry.

His reason, spoken: a wing picture with strongly raised feathers makes the generator "try to generate every feather like as a geometry". So he makes a flatter picture for the shape, and textures the result from the detailed picture ([2:33](https://www.youtube.com/watch?v=CgslUZIAl4s&t=153s) to [3:03](https://www.youtube.com/watch?v=CgslUZIAl4s&t=183s)).

**The texture-map prompt** ([5:31](https://www.youtube.com/watch?v=CgslUZIAl4s&t=331s), read from a frame). A chat panel beside Blender. The interface looks like Claude Code's (its spinner and "Type / for commands"); the model's name is not on screen (inference). The Blender outliner shows nine objects: `body_top`, `bracers_hand`, `bracers_leg`, `cloth_bottom`, `cloth_top`, `hair`, `head`, `legs`, `wings`. The mesh under `cloth_top` is named `tripo_mesh_8c9f5996-...`. The prompt:

> There is a character model in the open Blender scene. The model consists of several objects, each with its own material. I need to generate normal and roughness maps from the color map. Let's start with just one of the objects: `cloth_top`. The object's material is worn leather, but there is an orange area on the texture representing a gemstone. Using the existing texture, generate a normal map and a roughness map at 4K resolution, then connect them to the material. Also, save these generated textures into a new folder named "textures".

**The agent's report** ([5:41](https://www.youtube.com/watch?v=CgslUZIAl4s&t=341s), read from a frame):

- Two files, `cloth_top_normal.png` and `cloth_top_roughness.png`, "Both are set to Non-Color".
- "Normal: a height map built from the colour texture's brightness at fine, medium and large detail sizes. Very large brightness changes are ignored so they don't turn into fake bumps. It's OpenGL format (green = up), which is what Blender expects."
- "Gem: I picked out the orange area by colour, filled in its white highlight spots, and replaced the leather detail there with a smooth dome".
- "Roughness: Leather is about 0.74 on average (range 0.5–0.92) ... The ring around the gem is about 0.45. The gem itself is about 0.12."
- "The stretched, smeared areas of the texture (probably unused padding between UV islands) also get some faint normal detail."
- The next message typed is "Do the same for the rest of the objects".

### What comes out

- A rigged, animated character in nine separate objects, each with its own material, with colour, normal and roughness maps, shown in a Unity scene from a strategy-game camera high above ([11:42](https://www.youtube.com/watch?v=CgslUZIAl4s&t=702s)).
- **Triangle count of the whole character: not stated or shown.** The only counts visible are per part in Tripo (1,786 quad faces for the braid).
- **Texture size:** the prompt asks for 4K maps. The size of the colour textures from Tripo is not shown.
- **Files:** none published.
- **Defects admitted:** generated maps "might take few iterations ... it might be too shiny, too reflective" ([6:07](https://www.youtube.com/watch?v=CgslUZIAl4s&t=367s)); Tripo's colour texture can "leave some artifacts", which he fixes in another texturing tool whose name the captions give as "Moondiff" (not confirmed) ([7:09](https://www.youtube.com/watch?v=CgslUZIAl4s&t=429s)); the first glow effect "was too glowing" ([12:12](https://www.youtube.com/watch?v=CgslUZIAl4s&t=732s)).

### Time and cost stated

- Assembly in Blender: "12 minutes exactly" ([4:34](https://www.youtube.com/watch?v=CgslUZIAl4s&t=274s)).
- Model with textures: "I only spent few hours" ([7:40](https://www.youtube.com/watch?v=CgslUZIAl4s&t=460s)).
- Animations: "Approximately two hours later" ([9:41](https://www.youtube.com/watch?v=CgslUZIAl4s&t=581s)).
- **Cost: not given.** The description says "At the end I also show the real cost of creating one complete character with this workflow." No cost is spoken in either caption track, and none appears in the frames looked at, including one frame a second for the last twelve seconds. The only price on screen is "Generate 100" for one part in four variants.

### Claims

| Claim | Where | Status |
|---|---|---|
| One Tripo P2.0 generation gives four models at four chosen polygon counts | [1:30](https://www.youtube.com/watch?v=CgslUZIAl4s&t=90s) | Demonstrated on screen (the panel and four results in the asset list) |
| Smart UV gives a usable UV layout with free retries | [2:02](https://www.youtube.com/watch?v=CgslUZIAl4s&t=122s) | Demonstrated on screen for several parts; "usable" is his judgement |
| An LLM agent can make normal and roughness maps from the colour texture and wire them into the material | [5:31](https://www.youtube.com/watch?v=CgslUZIAl4s&t=331s) | Demonstrated on screen for one object, with the prompt and the report |
| The agent makes these maps through an image generator ("my agent ... is connected to APIs such as [fal.ai] where it can access [GPT image] generation") | [5:36](https://www.youtube.com/watch?v=CgslUZIAl4s&t=336s) | Contradicted by what is shown for the one case on screen: the report says the normal map was computed from the colour texture's brightness. Whether other objects used an image generator is not shown |
| "You will not be able to get something like this if the UV will suck": clean UV islands are what make generated maps work | [6:07](https://www.youtube.com/watch?v=CgslUZIAl4s&t=367s) | Asserted without showing. No comparison with a poor layout is made |
| Baking detail from a high-poly model "can take up to four, five, six hours" and this replaces it | [6:38](https://www.youtube.com/watch?v=CgslUZIAl4s&t=398s) | Asserted without showing |
| LLM agents could do the Blender assembly but it would take "one hour, two hours, spend a lot of tokens and still most likely going to need to fix some stuff" | [4:03](https://www.youtube.com/watch?v=CgslUZIAl4s&t=243s) | Asserted without showing |
| A flatter wing picture gives "better optimized wireframe" | [3:03](https://www.youtube.com/watch?v=CgslUZIAl4s&t=183s) | Asserted; the two wireframes are not shown side by side in the frames looked at |
| The whole character in one day | Title | Not checkable; the times stated add to "few hours" plus two hours of animation, with effects and integration not timed |

### What could not be made out

- Both caption tracks are machine-made (see Method). Model and tool names come out differently in each: "3POPP2" and "tripod P2" for Tripo P2; "full AI" for what is probably fal.ai; "GPT 2.5 image generation" for an image model; "Moondiff"; "religion" in a list of animation reference sources. Only "P2.0" and "Nano Banana 2" were confirmed from the screen.
- Which LLM made the texture maps. He names "GPT 6 Astra or Opus 5.5" as the "frontier models" the workflow benefits from ([2:33](https://www.youtube.com/watch?v=CgslUZIAl4s&t=153s)); the panel does not show a model name.
- The Blender version.

## 2. Video: "My Full AI Workspace - A Year in the Making, Now Yours for Free"

[youtube.com/watch?v=gV23ON8BgwU](https://www.youtube.com/watch?v=gV23ON8BgwU). Stefan 3D AI, uploaded 2026-09-21, 13 minutes 23 seconds, 72,951 views when read.

### What it is

- **Stated purpose:** a tour of the desktop program he works in, released on GitHub. The description links the repository in section 3, so **the repository belongs to this video**. Video 6's description links it too ("My Workspace & Skills").
- **Interest:** sponsored. Spoken: "thanks Higgsfield to sponsor this video" ([6:40](https://www.youtube.com/watch?v=gV23ON8BgwU&t=400s)); the description's first link is a Higgsfield referral link. Higgsfield is a company that resells image, video and 3D generators under one subscription.
- **Grade:** sponsored; a tutorial about a tool, without asset results. It makes no 3D asset.

### What is shown

- **Two windows:** a chat window that starts and keeps terminal sessions of coding agents, and a "Workspace" window that shows projects as HTML reports ([1:33](https://www.youtube.com/watch?v=gV23ON8BgwU&t=93s)).
- **Which agents:** "Codex CLI, Claude Code, or even Kimi" ([2:04](https://www.youtube.com/watch?v=gV23ON8BgwU&t=124s)). The session on screen is "OpenAI Codex (v0.154.0)", "model: gpt-6-astra medium", "permissions: YOLO mode" ([5:45](https://www.youtube.com/watch?v=gV23ON8BgwU&t=345s), read from a frame).
- **No permission prompts.** "I really like how CLI and bypass permission mode works ... here there's a setting like that it will be bypassed" ([4:05](https://www.youtube.com/watch?v=gV23ON8BgwU&t=245s)); "both Claude's and GPT or Codex are running like bypass permission modes through CLI in this project folder, so they can do pretty much anything" ([12:21](https://www.youtube.com/watch?v=gV23ON8BgwU&t=741s)). The install advice is to open a CLI, "allow all permission" and "tell him like to install everything" ([1:03](https://www.youtube.com/watch?v=gV23ON8BgwU&t=63s)).
- **An "image gen workflow" example** ([5:08](https://www.youtube.com/watch?v=gV23ON8BgwU&t=308s)): a report in which each creature concept is shown as three pictures, one each from "Nano Banana Pro", "GPT-Image-2" and "Seedream v5 Pro", with the prompts kept under each ([5:45](https://www.youtube.com/watch?v=gV23ON8BgwU&t=345s), read from a frame). He describes it as how he makes characters: a session with Claude Code or Codex, "I have all the API and stuff connected", "iteration one", and so on to the one he picks.
- **Skills and MCP:** a list of skills ("how to generate models, how to generate character sheets, how to generate animations") and a tab showing which agent has which MCP connections, with "Blender MCP" connected ([8:42](https://www.youtube.com/watch?v=gV23ON8BgwU&t=522s), [9:44](https://www.youtube.com/watch?v=gV23ON8BgwU&t=584s)). Which Blender MCP server is not said.
- **His setup:** Blender and Unity open beside chats named "Overlord Unity" and "Overlord animation" ([12:51](https://www.youtube.com/watch?v=gV23ON8BgwU&t=771s)).

### Claims

| Claim | Where | Status |
|---|---|---|
| Sessions are restored in the same state after closing | [3:35](https://www.youtube.com/watch?v=gV23ON8BgwU&t=215s) | Demonstrated on screen |
| "CLI works much better than chats" | [1:03](https://www.youtube.com/watch?v=gV23ON8BgwU&t=63s) | Asserted |
| Higgsfield's MCP gives access to "Tripo, Meshy, [Hunyuan]" on "one subscription", with an API "soon" | [6:10](https://www.youtube.com/watch?v=gV23ON8BgwU&t=370s) | Asserted in the sponsor's segment; not shown |

Nothing in this video is evidence about the quality of any asset.

## 3. Repository: `witnesstodark/mr-mak-workspace`

[github.com/witnesstodark/mr-mak-workspace](https://github.com/witnesstodark/mr-mak-workspace), read at commit `1e0c7c3219f4a5430563b31b3c9c85db412af900` (2026-10-05, "Prepare 0.4.19"). Cloned and read as text. Nothing in it was run, installed or built.

### Who, when, licence, activity

- **Who:** the account `witnesstodark`. One merge commit carries the name "Stefan Vaskevich" on the same account, and the sample pages credit "Stefan Vaskevich's published 3D setup article" (`workspace/2026-09-15_creative-mcp/report.html`). It is the video creator's own repository.
- **When:** created 2026-09-15; 21 commits; last push 2026-10-05. Three people: the owner (13 commits under two names) and two outside contributors (Linux packaging and project adapters, 7 commits; asset manifests, 1 commit).
- **Licence:** MIT for the program and the owner's documents (`LICENSE`). One bundled skill, `img2threejs`, is someone else's project under Apache-2.0 (`THIRD_PARTY_NOTICES.md`).
- **Activity (GitHub API, read 2026-10-08):** 338 stars, 95 forks, 4 open issues; latest release `v0.4.19` on 2026-10-05 with installers for Windows, Linux and macOS.

### What it is for

A desktop program (Tauri, with a local Node.js service) that keeps terminal sessions of Codex CLI, Claude Code, Kimi or OpenCode in tabs, beside a viewer for project reports written as HTML. With it come twenty "skills": instruction files for coding agents. It is a place to work, not a pipeline. It contains **no asset pipeline code, no Blender script and no call to Tripo's API**.

### Structure

| Path | What is there |
|---|---|
| `src/`, `src-tauri/`, `desktop/` | The program: a React front end, a Tauri shell, a Node service that starts the CLIs |
| `.agents/skills/` | The twenty skills, the maintained copy |
| `.claude/skills/` | The same skills copied for Claude Code (`npm run skills:sync` keeps them alike) |
| `CLAUDE.md`, `AGENTS.md` | Agent instructions. `CLAUDE.md` is nine lines pointing to `AGENTS.md` |
| `.mcp.json`, `.codex/config.toml` | MCP configuration, both empty: `{"mcpServers": {}}` |
| `.env.example` | Names of four optional keys with empty values: `OPENAI_API_KEY`, `FAL_KEY`, `MRMAK_COORDINATOR_MODEL`, `OPENROUTER_API_KEY` |
| `workspace/` | Four sample projects as HTML reports, among them a character concept study with 158 generated images |
| `scripts/asset-delivery/` | A small tool that writes and checks a list of files with their SHA-256 checksums |
| `processes/`, `knowledge/`, `context/` | Short Markdown notes and placeholders |

### Claude Code configuration

- **Skills:** yes, twenty, under `.claude/skills/`.
- **Hooks, settings files, agents, slash commands:** none. `.claude/` holds only `skills/`.
- **MCP servers:** none configured. The README says "MCP configuration starts empty."
- **No Blender add-on and no `bpy` script** anywhere in the repository (searched for `import bpy`).

### The skills that bear on a static asset

Of the twenty, most are about characters, animation, effects, user interface, levels and sound. Four touch what kiln does.

**`3d-production-routing`** (`.claude/skills/3d-production-routing/SKILL.md`): a table sending a task to another skill. Its closing rule:

> For a game asset, separate concept acceptance from mesh acceptance. Verify topology, scale, materials, rig, root motion and engine import as applicable. A successful API request or attractive render is not an engine handoff.

**`image-reference-workflow`** (`.claude/skills/image-reference-workflow/SKILL.md`): how an agent should make and edit reference images.

> For an edit, identify what remains unchanged and the exact delta. Use the accepted image as input, not a reconstruction of it from text.

> Choose the camera for the deliverable. A hero concept can use dramatic framing; a modeling sheet needs readable parts and neutral light.

> Keep prompt, endpoint, seed when available, request ID and downloaded outputs together.

**`character-sheet-pipeline`** (`.claude/skills/character-sheet-pipeline/`): nine prompt files for turning one character picture into a front view and separate part pictures. This is step 1 of video 1. It is the most specific material in the repository on reference images for an image-to-3D generator, and it takes a firm position on camera angle:

> STRICT FRONT VIEW — the character faces the camera directly, dead-on, NO three-quarter angle ... Camera at eye-level, perfectly orthographic-style framing, zero perspective distortion ... Pure white background (#FFFFFF), no shadow on the ground, no ground plane visible. Neutral diffuse studio lighting (`prompts/01a_apose_front.md`)

The same rule is applied to single objects (hats, weapons, bags), with a reason:

> Older versions of this skill allowed 3/4 angles for accessories on the theory that "the user can re-orient in 3D anyway". This was wrong — it forced the user to manually rotate the reference back to front before feeding it to image-to-3D models (`prompts/04_parts_accessory.md`)

It names image models: "Nano Banana Pro (primary) | Nano Banana 2 (fallback). NEVER GPT-Image-2/2.5 here", at "2K (2048×2048 or closest 1:1)". And it has the agent inspect each generated picture against six yes-or-no checks (dead front, no three-quarter turn, no twist, no dramatic angle, no back showing, clean framing) and answer `pass`, `soft_fail` or `hard_fail`, retrying a failure "within the task budget" (`prompts/08_3q_classifier.md`). The file says of itself that it "supplies the rubric, not a deployed classifier service" and "does not establish API cost or guaranteed accuracy". No results of using it are given.

**`materials-to-game`** (`.claude/skills/materials-to-game/SKILL.md`): six steps for reducing a textured dense model to a game model by baking, in words only. The step that matters for kiln's budgets:

> Decimate or retopologize into a separate low-poly. Inspect thin parts, hard edges and the silhouette. A fixed face count is not suitable for every asset.

and for checks: "Unwrap the low-poly, check texel density, seams, overlap and padding"; "Check normal orientation in the target renderer"; "Reimport from another directory and check material links, scale, silhouette and texture resolution."

**`fal-ai-generation`** (`.claude/skills/fal-ai-generation/`): how to call fal.ai, a service that resells many image, video and 3D generators through one API. It includes a Python helper, `scripts/fal_job.py`, that uploads a file, submits a job and downloads the result. Tripo appears once in the whole repository outside the bundled third-party skill, as a fal.ai route:

> `tripo3d/h3.1/image-to-3d`: `image_url` is required. Geometry/texture quality, PBR, orientation and face limit are separate controls. (`references/mcp-workflow.md`, "Read-only schema checks on September 15, 2026")

Rules in this skill that match what kiln already does: download outputs "before relying on a CDN link"; keep "the prompt, source filenames or hashes, model ID, request ID, local outputs and review verdict together"; "Record technical completion separately from visual acceptance"; "A wait timeout does not authorize a duplicate submission."

### What the repository does not hold

- **The workflow of videos 1, 4, 6 and 7 is not in it as code.** In those videos Tripo is used by hand in its web app. The repository's only route to Tripo is through fal.ai, described in one sentence.
- **Nothing on Smart UV, P2.0, polygon counts per part, or generating normal and roughness maps from a colour texture.** The video 1 texture step is a prompt typed into a chat, not a skill.
- **No results.** No mesh, no measurement, no before and after. The sample project is concept pictures and motion studies.

### External tools and services it depends on

Codex CLI, Claude Code, Kimi or OpenCode (at least one, installed separately); Node.js 22.20 or later; Rust and Tauri to build; optionally an OpenAI API key (voice), a fal.ai key, a Higgsfield account. The sample "Creative MCP Connections" page lists, without installing any: Blender Lab MCP, Higgsfield's Blender add-on and CLI, a Unity MCP, a Godot MCP, VibeUE (Unreal), fal.ai's hosted MCP and a community fal server. That page says of itself: "Blender's project pages were not fully retrievable during this export, so no exact server command or tool count is asserted here."

### Risks

- **It can start every agent with its safety prompts off.** `desktop/service/agents.mjs`, lines 66 to 75, adds `--dangerously-bypass-approvals-and-sandbox` (Codex), `--dangerously-skip-permissions` (Claude Code), `--yolo` (Kimi) or `--auto` (OpenCode) when the bypass setting is on. `SECURITY.md` and the README say bypass "is an explicit choice and is off by default". The creator runs with it on and recommends it (section 2).
- **The recommended install is to have an agent set it up** from a pasted prompt, on a machine where the agent may already have all permissions.
- **A local service** listens on the loopback address; `SECURITY.md` warns not to expose it.
- **Scripts that reach the network or run programs:** `fal_job.py` (calls fal.ai with the user's key); `scripts/video-watch/extract.py` (runs an external program through `subprocess`); `Setup.ps1` (Windows setup).
- **The bundled `img2threejs` skill is 336 files of another project's Python and instructions,** copied twice. It was not read beyond its file list and notices.
- **Embedded keys:** none found. One string shaped like a key is a test fixture (`scripts/asset-delivery/test/manifest.test.mjs`).
- **Text addressed to an AI agent:** the skills and `AGENTS.md` are, by purpose, instructions to an agent, and `prompts/08_3q_classifier.md` contains a prompt beginning "You are a strict orthographic-reference verifier". These are the product, reported here as content. A search for phrases that try to override a reader's instructions found none. Nothing in them was followed.

### Grade

A tool and a set of written instructions from an interested party. Not evidence that any workflow produces a good asset: it holds no asset and no measurement.

## 4. Video: "Creating 3D Character with AI in 1 Min vs 1 H vs 10 H"

[youtube.com/watch?v=VeOU0FnTjjc](https://www.youtube.com/watch?v=VeOU0FnTjjc). Stefan 3D AI, uploaded 2026-09-19, 14 minutes 24 seconds, 129,956 views when read. Only a 360-pixel-high copy could be downloaded (the larger streams returned "HTTP Error 403: Forbidden"), so small text on screen is read with less certainty than in the other videos.

### What it is

- **Stated purpose:** the same stylised character (a fox-like warrior) made three times, with one minute, one hour and ten hours allowed, to show "what quality we can actually reach" ([0:00](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=0s)). The third run took about six and a half hours.
- **Interest:** Tripo referral link and discount code in the description; spoken: "you can try it for free and by my link in the description. You're going to get 500 credits if you are a new user" ([6:10](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=370s)). His course is advertised at [11:50](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=710s). The Tripo balance on screen is 707,235 credits ([0:44](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=44s)).
- **Grade:** interested party (affiliate), individual hands-on report, one character made three ways. No files published.
- **No LLM appears in this video.** No Claude, no Codex, no agent. Every step is a person in Tripo Studio, Blender, AccuRIG, Substance Painter and Unreal Engine.

### The three runs

| | One minute | One hour | "Ten hours" |
|---|---|---|---|
| Generation | One Tripo P2 generation of the whole character from one picture, then texturing as a second step ("When you do it with P2, it requires two step") | Seven part pictures (body, tail, sandals, head, trousers, waist sash, sword), each generated separately with P2 | The same, with "few more parts" and "few retries" |
| Time generating | "approximately 3 minutes" | "more than 30 minutes" | Not stated separately |
| Blender | None | 20 minutes by hand: "Cut some duplicating parts and assemble things carefully together with Blender sculpting modes or Blender proportional editing" | About 40 minutes assembling and repairing; 30 minutes unwrapping UVs by hand; colour re-baked into one texture |
| Textures | Tripo's | Tripo's | Texture repair with Blender's clone brush or another tool; materials in Substance Painter; eyes made as spheres with a texture from "Nano Banana" |
| Rig and engine | None. In Unreal it is a rigid statue | AccuRIG, then Unreal with animations retargeted | AccuRIG with extra bones; cloth and tail physics in Unreal |
| Total stated | About 3 minutes | "a little bit more than an hour" | 5.5 hours, plus "another hour in Unreal Engine" |
| Where | [0:32](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=32s) | [1:33](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=93s) to [4:38](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=278s) | [5:08](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=308s) to [13:24](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=804s) |

On screen in Tripo Studio ([0:44](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=44s), [2:22](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=142s)): two tabs, "HD Model" and "Smart Mesh", with Smart Mesh chosen; "AI Model: P2.0 - Preview"; a "Generate" button with 100 struck through and 65 beside it.

### What he says about the mesh

- **Generating in parts is where the time goes and what raises quality:** "Most important thing where I going to invest my time is to generate my model in parts ... and set different settings for the mesh" ([1:33](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=93s)).
- **How finely to split:** "you don't need to go like crazy splitting every single detail. I would say like think about like some detail that fit like within 500 to 1,000 polygons" ([2:05](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=125s)).
- **Retries:** "usually it takes like one two max retries with the different poly count settings to get the right poly counts" ([1:33](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=93s)).
- **Where it fails:** "it can break and there are some edge cases. I would say like with some realistic garment etc. it might not work that well" ([2:35](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=155s)).
- **Defects admitted in the careful run:** "it still can produce some artifacts. There might be some issues with the mesh"; "somewhere it was a bit bent. I had to straighten that"; "I also had to fix some holes caps and polygons or optimize mesh a little bit"; a scarf came out double-sided and he cut it to a single sheet ([6:40](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=400s) to [7:12](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=432s)).
- **One-shot generation of the whole character:** "we can definitely spot some blurry spots like eyes" ([1:02](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=62s)).
- **UVs:** unwrapped by hand in Blender in 30 minutes. A caption burned into the picture at about [7:40](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=460s) reads: "This video recorded before Smart UV release. I reccomend to do UV in Tripo now". His reasons for wanting few, large UV islands: "you can do nice baking pack texture nicer in lower resolution ... When you have like thousand of islands, it's very difficult to avoid small artifacts" ([8:12](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=492s)). The implication, not stated outright, is that the UVs Tripo gave before Smart UV were in very many small islands (inference).

### What comes out

- A rigged character in Unreal Engine, running with retargeted animations, with cloth and tail physics in the third run ([13:24](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=804s)).
- **Triangle count:** AccuRIG's window shows a "Total tris" figure of about 22,000 for the body without accessories ([11:02](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=662s), read from a 360-pixel frame; the digits are not certain).
- **Texture sizes, formats:** not stated. **Files:** none published.

### Claims

| Claim | Where | Status |
|---|---|---|
| A whole character from one P2 generation in about three minutes has visibly weak areas | [1:02](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=62s) | Demonstrated on screen |
| Generating in parts gives a better mesh than generating whole | [1:33](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=93s) | Shown as two results side by side in the video; no count or measurement |
| "Triple P2 produces much better low poly, especially with quads, than any [retopology]", naming Tripo's own and Hunyuan's | [5:39](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=339s) | Asserted here without showing. He says he tested it ([13:24](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=804s)); the test is not in this video |
| P2 meshes are "logical", which makes seams easy to place by hand | [7:42](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=462s) | Shown being done; "easy" is his judgement |
| Generate dense and bake down only "if you have like really detailed high poly that you want to ... preserve"; otherwise "go with P2 like low poly right away" | [13:56](https://www.youtube.com/watch?v=VeOU0FnTjjc&t=836s) | Asserted, as advice |

### What could not be made out

- Face counts in the Tripo panels, at 360 pixels.
- The name of the second texture-repair tool (captions: "modiference", "motive").
- No cost is stated anywhere.

## 5. Video: "Easy Clothing with AI for Any Character — Best Workflow"

[youtube.com/watch?v=gSHON893CCI](https://www.youtube.com/watch?v=gSHON893CCI). Stefan 3D AI, uploaded 2026-07-22, 18 minutes 35 seconds, 56,356 views when read. The oldest of the six.

### What it is

- **Stated purpose:** clothing for game characters without cloth-design software, in three routes: clothing with a new character, static clothing on an existing character, and clothing with physics on an existing character ([0:00](https://www.youtube.com/watch?v=gSHON893CCI&t=0s)).
- **Interest:** the description's two first links are referral links to "Lychee Studio", a node-based tool that chains image and 3D generators. Spoken: "they give crazy amount of free credits to start with" ([1:30](https://www.youtube.com/watch?v=gSHON893CCI&t=90s)). No sponsorship is spoken. (The captions write the tool's name as "DC Studio"; the name used here is from the description and the screen.) His course is advertised at [5:03](https://www.youtube.com/watch?v=gSHON893CCI&t=303s).
- **Grade:** interested party (affiliate), individual hands-on report, one costume. No files published.
- **About two thirds of it is Unreal Engine 5.8's cloth physics** ([7:06](https://www.youtube.com/watch?v=gSHON893CCI&t=426s) onwards): rigging, retargeting and weight painting. None of that is in kiln's scope and it is not summarised here.
- **No LLM takes part.** The only mention is advice to ask ChatGPT or Claude which physics settings to change ([13:11](https://www.youtube.com/watch?v=gSHON893CCI&t=791s)).

### The part that bears on generation

1. **Reference image made on top of a picture of the body it must fit.** He takes a render of the mannequin the clothes are for and has the image generator dress it: "you basically need an accurate screenshot or render of your character ... wear the garments on top of her ... that will helps a lot with the proportion, pose and many things" ([0:50](https://www.youtube.com/watch?v=gSHON893CCI&t=50s)).
2. **Split the picture into parts before generating.** "Generating all these parts such as head, boots, cloak, dress, all at once, that's not going to end well" ([1:30](https://www.youtube.com/watch?v=gSHON893CCI&t=90s)). A "prop extraction" node lists the parts it found (head, body, boots, cloak and so on) with a switch beside each ([1:40](https://www.youtube.com/watch?v=gSHON893CCI&t=100s), read from a frame).
3. **Generate each part.** The "Image to 3D" node shows "Provider: Lychee 3D", two modes "HD Model" and "Smart Mesh" (Smart Mesh chosen), "Polycount 5,000", and switches for "Texture" and "PBR" ([3:10](https://www.youtube.com/watch?v=gSHON893CCI&t=190s), read from a frame). Spoken: "I'm really in love with [Tripo P1] that can do smart low poly. The mesh is really logical" ([2:48](https://www.youtube.com/watch?v=gSHON893CCI&t=168s)). The node does not show the name Tripo; that the node calls Tripo is his statement.
4. **Fit in Blender by hand, against the real body.** He imports the mannequin's mesh as "a size and shape reference" and moves and reshapes each generated part to fit it, in sculpt mode with the Elastic Grab brush or by moving vertices ([3:31](https://www.youtube.com/watch?v=gSHON893CCI&t=211s) to [5:03](https://www.youtube.com/watch?v=gSHON893CCI&t=303s)). This is how scale is settled in every one of his videos: by eye against another object, never from the generator.

### Claims

| Claim | Where | Status |
|---|---|---|
| A whole costume generated as one model "is not going to end well" | [1:30](https://www.youtube.com/watch?v=gSHON893CCI&t=90s) | Asserted without showing |
| Low-poly generation can be the starting point, with detail added by texture; high-poly then baking is the "more professional approach" | [2:48](https://www.youtube.com/watch?v=gSHON893CCI&t=168s) | Asserted, as advice |
| Adjusting generated meshes in Blender "is ridiculously simple" | [4:32](https://www.youtube.com/watch?v=gSHON893CCI&t=272s) | Shown being done by someone practised; "simple" is his judgement |
| The clothing works with physics in Unreal | [17:45](https://www.youtube.com/watch?v=gSHON893CCI&t=1065s) | Demonstrated on screen |

Time and cost: none stated beyond "5 minutes" for rigging in AccuRIG. Triangle counts and texture sizes: none stated.

## 6. Video: "AI Can Now Create VFX Fro YouR Game & Characters"

[youtube.com/watch?v=ZksPNRPupWs](https://www.youtube.com/watch?v=ZksPNRPupWs). Stefan 3D AI, uploaded 2026-09-30, 19 minutes 27 seconds, 86,898 views when read. (The title's misspelling is the uploader's.)

### What it is

- **Stated purpose:** how he made the visual effects (VFX: sparks, auras, trails and the like) for his strategy game, and one character, a tree spirit, with its animations and effects ([0:00](https://www.youtube.com/watch?v=ZksPNRPupWs&t=0s)).
- **Interest:** Tripo referral link and discount code in the description; his course at [11:16](https://www.youtube.com/watch?v=ZksPNRPupWs&t=676s).
- **Grade:** interested party (affiliate), individual hands-on report, one character plus a set of effects. No asset files published; the skills he mentions are in the repository (section 3).
- **Most of it is outside kiln's scope:** effect concepts, animation, rigging and Unity. The method there is the same each time: have the LLM draw the idea first as an interactive HTML page, approve it, then hand it to a second LLM session to build in the engine ([2:33](https://www.youtube.com/watch?v=ZksPNRPupWs&t=153s), [14:50](https://www.youtube.com/watch?v=ZksPNRPupWs&t=890s)).

### The part that bears on generation ([7:10](https://www.youtube.com/watch?v=ZksPNRPupWs&t=430s) to [10:45](https://www.youtube.com/watch?v=ZksPNRPupWs&t=645s))

- **Tripo P2.0, four at once, in parts.** "now you can generate four meshes at once ... I split the mesh in some parts ... I set different poly counts and then I can choose which one works the best" ([7:41](https://www.youtube.com/watch?v=ZksPNRPupWs&t=461s)). On screen: "Number of Generation" with 4 chosen, "AI Model P2.0", "Generate 100" ([8:00](https://www.youtube.com/watch?v=ZksPNRPupWs&t=480s)). The parts shown are the body with roots, the head with antlers, and loose branches.
- **Smart UV, and why.** The head is unwrapped on screen, with the message "Auto UV unwrapping in progress" and then a layout with a "Free Retry" button ([8:30](https://www.youtube.com/watch?v=ZksPNRPupWs&t=510s)). His reason: "if it's clear what's actually going on with UV, you can drop that color map to AI and do color correction or you can add metallic and roughness" ([8:44](https://www.youtube.com/watch?v=ZksPNRPupWs&t=524s)).
- **A clean mesh in separate pieces is what lets the LLM work on it later.** "Astra actually helped me to rig all these roots ... but it only was able to made it because I kept it all optimized and roots mesh was logically separated" ([7:10](https://www.youtube.com/watch?v=ZksPNRPupWs&t=430s) to [7:41](https://www.youtube.com/watch?v=ZksPNRPupWs&t=461s)). "Astra" is GPT-6 Astra, OpenAI's model, not Claude.
- **Tripo's texture is repaired by hand.** "AI texturing is good, but it can fail on some important details", so he paints over areas in a separate texturing tool using an image as reference ([9:14](https://www.youtube.com/watch?v=ZksPNRPupWs&t=554s) to [9:44](https://www.youtube.com/watch?v=ZksPNRPupWs&t=584s)). The tool's name could not be read; the captions give "Modive".
- **Leaves are not generated as 3D.** Flat rectangles with leaf pictures from "Nano Banana Pro", placed by hand, and kept as a separate object with its own material because "it has transparency" ([9:44](https://www.youtube.com/watch?v=ZksPNRPupWs&t=584s) to [10:45](https://www.youtube.com/watch?v=ZksPNRPupWs&t=645s)). Placing them by LLM "is a little bit tricky still".

### Time and cost stated

"All that I created something around one and a half day" ([18:23](https://www.youtube.com/watch?v=ZksPNRPupWs&t=1103s)), for the character with its animations and effects. No cost.

### Claims

| Claim | Where | Status |
|---|---|---|
| Four meshes at four polygon counts from one generation | [8:00](https://www.youtube.com/watch?v=ZksPNRPupWs&t=480s) | Demonstrated on screen |
| The LLM could rig the roots only because the mesh was clean and in logical pieces | [7:41](https://www.youtube.com/watch?v=ZksPNRPupWs&t=461s) | Asserted without showing; no attempt on a messier mesh is shown |
| With a clear UV layout an image model can recolour the colour map or add metallic and roughness | [8:44](https://www.youtube.com/watch?v=ZksPNRPupWs&t=524s) | Asserted here; video 1 shows one case of the second half |
| An LLM animated a non-human run that two video generators could not produce as reference | [13:47](https://www.youtube.com/watch?v=ZksPNRPupWs&t=827s) | The animation is shown; the failed video-generator attempts are not |
| The character and effects work in the game | [16:15](https://www.youtube.com/watch?v=ZksPNRPupWs&t=975s) | Demonstrated on screen, in Unity |

Triangle counts, texture sizes: none stated. An unfinished effect is admitted: "I'm still not happy with this fire" ([2:03](https://www.youtube.com/watch?v=ZksPNRPupWs&t=123s)).

## 7. Video: "AI Just Solved UV Unwrapping and It's Crazy Good - Smart UV"

[youtube.com/watch?v=1vw39QCcQjg](https://www.youtube.com/watch?v=1vw39QCcQjg). Stefan 3D AI, uploaded 2026-09-18, 14 minutes 6 seconds, 82,227 views when read. Of the six videos this is the one closest to kiln: it is the only one that shows static objects (a house, a metal panel, a ship's wheel, a shield).

### What it is

- **Stated purpose:** a first look at "Smart UV", Tripo's automatic UV unwrapping, on the day it went live ("it's only going live today", [5:41](https://www.youtube.com/watch?v=1vw39QCcQjg&t=341s)), and at Tripo P2.0 leaving beta; then two characters built with it.
- **Interest:** Tripo referral link and discount code in the description and on screen ([5:50](https://www.youtube.com/watch?v=1vw39QCcQjg&t=350s)); spoken: "if you want to try by my link in the description, you're going to get extra 500 free credits". He had access before release ("I already tested it before this video", [2:04](https://www.youtube.com/watch?v=1vw39QCcQjg&t=124s)) and knows unreleased plans ("from what I know, later you will be able actually choose some parts"). He also runs the ranking site top3d.ai, to which he says the model will be added.
- **Grade:** interested party (affiliate with early access), individual hands-on report. About ten objects unwrapped on screen, two characters built. No files published. No measurement beyond what Tripo's own panel displays.
- **No LLM appears in this video.**

### What is shown

**Generation settings** ([0:52](https://www.youtube.com/watch?v=1vw39QCcQjg&t=52s), read from a frame). "AI Model: P2.0" marked "New". "Topology": "Quad" (marked "New") or "Triangle". "Number of Generation": 1, 2 or 4. "Customize Each Model" opens a "Polycount" panel with a switch "Use Same Polygon Count" and four sliders from 500 to 25,000; the values shown are 4592, 7404, 5000, 5000. Spoken: "for same price. You get four generation and you're able to choose the best one", and "generation still takes like 5 to 7 seconds" ([0:32](https://www.youtube.com/watch?v=1vw39QCcQjg&t=32s) to [1:04](https://www.youtube.com/watch?v=1vw39QCcQjg&t=64s)).

**Smart UV** ([1:44](https://www.youtube.com/watch?v=1vw39QCcQjg&t=104s)). A tab in Tripo Studio. Spoken: "It cost 20 credits but it is extremely fast and they give you free retries ... each retry takes around 5 seconds". On screen the button reads "Free Retry (3)", counting down. Spoken limits: "it only works with smart mesh or low poly mesh. You can actually upload any of your mesh and unwrap here" ([0:30](https://www.youtube.com/watch?v=1vw39QCcQjg&t=30s)).

**The objects unwrapped on screen**, with what Tripo's panel displays for each (read from frames):

| Object | Kind | Panel | Where |
|---|---|---|---|
| Jester head | Character part | Seams down the middle of the head; several retries shown | [1:50](https://www.youtube.com/watch?v=1vw39QCcQjg&t=110s) |
| Human head with eyes | Character part | Each eyeball its own island | [2:40](https://www.youtube.com/watch?v=1vw39QCcQjg&t=160s) |
| Whole human body | Character | About ten large islands | [3:10](https://www.youtube.com/watch?v=1vw39QCcQjg&t=190s) |
| Robot, generated whole | Hard-surface, many pieces | Several hundred small islands | [3:40](https://www.youtube.com/watch?v=1vw39QCcQjg&t=220s) |
| **House** | **Static, building** | "Topology Quad, Faces 7814, Vertices 7185", "Utilization 82.1%" | [4:22](https://www.youtube.com/watch?v=1vw39QCcQjg&t=262s) |
| **Metal panel with cut-outs** | **Static, hard-surface** | Front and back as two large islands, edges as strips | [4:50](https://www.youtube.com/watch?v=1vw39QCcQjg&t=290s) |
| **Ship's wheel** | **Static prop** | The rim as one ring-shaped island | [5:30](https://www.youtube.com/watch?v=1vw39QCcQjg&t=330s) |
| **Round shield** (part of a character) | **Static prop** | "Topology Quad, Faces 731, Vertices 741", "Utilization 73.9%" | [10:32](https://www.youtube.com/watch?v=1vw39QCcQjg&t=632s) |

"Utilization" is the share of the texture square that the UV islands cover; the rest is wasted pixels.

**A comparison with Hunyuan** ([6:12](https://www.youtube.com/watch?v=1vw39QCcQjg&t=372s)). One frame of another product's "3D Studio" (its interface is in Chinese) showing a triangle mesh of 11,483 faces whose UV layout is a carpet of hundreds of tiny islands. Spoken: "it is not even close ... this UV here takes like 10 minutes or more". It is a different object from any unwrapped in Tripo, so it is not a like-for-like test.

**Building a character** ([6:37](https://www.youtube.com/watch?v=1vw39QCcQjg&t=397s) onwards). The same method as videos 1 and 4: part pictures, four polygon counts each, pick one, Smart UV, texture in Tripo, assemble in Blender by hand in "15 minutes exactly" ([10:48](https://www.youtube.com/watch?v=1vw39QCcQjg&t=648s)), rig in Mixamo.

### Defects visible or admitted

- **Stray small islands.** "sometimes for whatever reason it defines like small areas into separate islands" ([3:08](https://www.youtube.com/watch?v=1vw39QCcQjg&t=188s)); "It was unwrapping like small squares randomly on some parts. I think that's more like a bug" ([8:15](https://www.youtube.com/watch?v=1vw39QCcQjg&t=495s)).
- **Geometry not asked for.** One of the four body variants "created like fur with planes. I don't really need that. I going to delete it" ([7:12](https://www.youtube.com/watch?v=1vw39QCcQjg&t=432s)).
- **A hole.** "when I was reviewing this mesh I spot like some hole you know obviously this hole shouldn't be there" ([12:19](https://www.youtube.com/watch?v=1vw39QCcQjg&t=739s)).
- **Whole-object generation is still worse than parts.** "there are some issues and again for more control you just generate it like and texture it like in separate [parts]" ([3:08](https://www.youtube.com/watch?v=1vw39QCcQjg&t=188s)).
- **Materials.** "I might only spend a little bit more time on the materials like PBR materials" ([13:21](https://www.youtube.com/watch?v=1vw39QCcQjg&t=801s)).
- **A hidden face left out on purpose,** which he counts as a virtue: the belt has no inner side where it sits against the body ([8:45](https://www.youtube.com/watch?v=1vw39QCcQjg&t=525s)). For a part used alone it would be an open mesh (inference).

### Time and cost stated

- Smart UV: 20 credits, about 5 seconds, three free retries.
- Four low-poly models, choosing one and unwrapping: "less than a minute" ([5:41](https://www.youtube.com/watch?v=1vw39QCcQjg&t=341s)).
- One character: "all at once 20 minutes game ready" before rigging ([13:21](https://www.youtube.com/watch?v=1vw39QCcQjg&t=801s)); the description says "two full game-ready Ursa characters ... in just few hours".
- No total in credits or money.

### Claims

| Claim | Where | Status |
|---|---|---|
| Smart UV puts seams where an artist would and returns in seconds | [1:44](https://www.youtube.com/watch?v=1vw39QCcQjg&t=104s) | Layouts and seams are demonstrated on screen for about ten objects; "like an artist" is his judgement. No stretch or texel-density figure is shown |
| Four models at four polygon counts for the price of one | [0:52](https://www.youtube.com/watch?v=1vw39QCcQjg&t=52s) | The panel is demonstrated on screen; the price is spoken, not shown in this video (video 1 shows "Generate 100" with four selected) |
| P2.0 "is finally officially released" and has fewer flaws than the beta | [0:32](https://www.youtube.com/watch?v=1vw39QCcQjg&t=32s), [4:10](https://www.youtube.com/watch?v=1vw39QCcQjg&t=250s) | "New" badge shown; "fewer flaws" asserted. Video 4, uploaded a day later, still shows "P2.0 - Preview", and its on-screen note says it was recorded earlier |
| Smart UV is far better than Hunyuan's | [6:12](https://www.youtube.com/watch?v=1vw39QCcQjg&t=372s) | One frame of one different object. Not a comparison |
| The result is "game ready" | [13:21](https://www.youtube.com/watch?v=1vw39QCcQjg&t=801s) | Asserted. Not shown in an engine in this video; no check against any budget |
| "next year [3D] will be handled by AI much better than ... any [3D] junior or middle artist" | [12:51](https://www.youtube.com/watch?v=1vw39QCcQjg&t=771s) | Opinion |

### What could not be made out

- Whether the house, panel and wheel were textured or exported; they are shown only untextured in the UV panel.
- The exact wording of the credit price on the Smart UV button (a button reading "Generate" with a number, possibly 20, is visible at [5:12](https://www.youtube.com/watch?v=1vw39QCcQjg&t=312s) at thumbnail size only).

## 8. What Tripo's own documentation says about what the videos show

Tripo's API documentation ([full text](https://developers.tripo3d.com/llms-full.txt), downloaded and searched 2026-10-08) is the only vendor source that could be read today. Tripo's website pages on these features exist (a search returned the titles "Smart UV: AI-Native UV Unwrapping in One Click", "Tripo P2.0 Official" and a Smart Mesh page) but each returned "403 Forbidden" behind a browser check and was not read.

| What a video shows or says | What the API documentation says | Result |
|---|---|---|
| P2.0 makes quads or triangles; quad slider 500 to 25,000 (videos 1, 7) | `P2-20260801`: "`face_limit`: triangle 48–50,000; with `quad=true`, 48–25,000" (changelog, 2026-08) | Agrees, apart from the web app's floor of 500 |
| P2.0 "is finally officially released" (video 7, 2026-09-18) | The image-to-model page still lists `P2-20260801` as "Preview" | Disagrees, or the API lags the web app. A third-party article dates a release to 2026-09-21 ([aicybr.com](https://aicybr.com/blog/tripo-p2-native-quad-mesh-ai-3d-generation), citing a press release that was not opened) |
| Four models at four polygon counts "for same price"; "Generate 100" with four selected (videos 1, 6, 7) | No parameter for a number of results or a list of face limits on any generation endpoint. The CLI's `-n` (earlier note) gives up to four candidates with different seeds, not different face counts | Not in the API as documented. A web app feature |
| Smart UV: 20 credits, about 5 seconds, free retries, works on uploaded meshes (video 7) | The words "Smart UV" do not occur. The only UV control is `export_uv` ("Controls UV unwrapping. Set `false` for faster generation and smaller file size") | Not in the API as documented. A web app feature |
| P2 texturing "requires two step" (video 4) | P series image-to-model has `texture`, default `true`, and `pbr` | Differs: by the documentation an API request textures in the same task |
| The web app's "Smart Mesh" tab runs model "P2.0" (videos 1, 4, 7); "[Tripo P1] that can do smart low poly" (video 5) | The P series is "Optimized for low-poly output with clean topology" | The earlier note could not tell whether Studio's "Smart Mesh" was the P series or `smart_low_poly`. The videos show it is the P series (shown) |
| Generation from a picture takes a picture and settings; the only prompts typed are for the image tool (videos 1, 4, 6, 7, in the frames read) | No `prompt` among the P series image-to-model parameters: `input`, `model`, `enable_image_autofix`, `texture_alignment`, `orientation`, `model_seed`, `face_limit`, `texture`, `pbr`, `texture_seed`, `texture_quality`, `texture_version`, `delight`, `auto_size`, `export_uv`, `export_orientation`, `quad` | Agrees with the earlier note: `image-to-model` takes no text prompt |
| Reference pictures made with "Nano Banana 2" inside Tripo (video 1); an image model the captions call "GPT 2.5" (video 1) | Image endpoints list `banana2` (earlier note) and, since 2026-09, `chat_image_2.5_flare` and `chat_image_2.5_sunburst`, with a `background` setting that can be `transparent` | Agrees; and the documentation now says transparent backgrounds can be produced, which the earlier note had as open |
| P2 costs 100 credits in the web app, or 65 with 100 struck through (videos 1, 4) | "Credits: 100 without texture; `standard` / `detailed` / `extreme` = 110 / 120 / 130" for P2 through the API | The same base number. Whether a web app credit and an API credit cost the same money was not established |

## 9. Against the earlier notes

"Notes" means the four earlier notes. The grade of every row from the videos is the same: interested party, hands-on, one person.

| Topic | What the notes have | What these sources show | Agrees, adds or contradicts |
|---|---|---|---|
| Hands-on evidence, with files, of Claude plus a generator plus Blender making a static asset | None found; "a gap in the search" | Still none. Characters, by hand in the web app, no files, GPT-6 Astra more than Claude | Agrees: the gap stays open. The notes' "no YouTube video was opened" is now six opened |
| Whether `image-to-model` takes a text prompt | No, by the API reference; a Tripo tutorial says to add one | No prompt field in the generation panels read; documentation re-read | Agrees |
| Reference image: one object | Tripo: avoid "multiple subjects in one image" | Stronger: split one object into parts and generate each from its own picture (videos 1, 4, 5, 6, 7). "all at once, that's not going to end well" | Adds a technique. Asserted; video 4 shows whole against parts for one character |
| Reference image: camera angle | Tripo states none | The repository's prompts demand "STRICT FRONT", "orthographic-style framing, zero perspective distortion", for characters and for single objects, with the reason that a three-quarter picture had to be turned to the front before use | Adds a position where the notes had none. Asserted in a prompt file; no test, no results |
| Reference image: background and light | Plain white or light grey; even light; at least 1024 pixels | The repository's prompts: "Pure white background (#FFFFFF), no shadow on the ground", "Neutral diffuse studio lighting", 2K square | Agrees |
| Reference image: how much surface detail to draw | Nothing | A picture with strongly raised detail makes the generator build the detail as geometry; draw it flatter for the shape and use the detailed picture for texture (video 1, wing) | Adds. Asserted; the two meshes are not compared on screen |
| Which image generator | Tripo's endpoints resell several | Nano Banana Pro first, Nano Banana 2 second, "NEVER GPT-Image-2/2.5" for the front sheet (repository); three models side by side per concept (video 2) | Adds one person's preference, without evidence |
| Which Blender MCP servers work with Tripo, and headless | Tripo's CLI is headless and does not touch Blender; the community server refuses background mode; Blender Lab's has one | A "Blender MCP" is connected in the workspace, unnamed, with Blender's window open (video 2). The repository's shortlist names Blender Lab MCP and installs nothing. Tripo is used only by hand in the browser | Adds nothing. No source here uses Tripo's CLI or API, or Blender without a window |
| What a generated mesh holds | Dense by default; defects conceded by vendors; number of materials and pieces "not documented" | P2 parts as shown: quad, 731 to 7,814 faces per part; a mesh named `tripo_mesh_<id>`; one material per part. In video 1's node graph the material of a Tripo part has a single image connected before the agent adds two more | Adds, for P2 in the web app. That the web app's texture step gave colour only is an inference from one frame; the API's `pbr` default says four maps |
| UVs of a generated mesh | "AI-generated UVs can be chaotic" (Tripo's blog); kiln's own trial of Blender's Smart UV Project cut a 5,000-triangle rock into 317 and 560 islands | Tripo's Smart UV on a 7,814-face house: 82.1% of the square used, islands that follow the walls and roof; on a robot generated whole, hundreds of islands. Stray tiny islands admitted | Adds: a route the notes did not have, with on-screen layouts. Web app only as far as documented |
| Defects | Non-manifold edges and zero-area faces counted once on reduced output | Holes, stray flat pieces, a bent part, double-sided cloth, an inner face left out, blurred texture on eyes (videos 4 and 7). Described, not counted | Agrees in kind. Adds that defects remain on P2.0 by an admirer's own account |
| Baked-in lighting | `delight` needs texture model v3.5 | Not mentioned in any video | Nothing |
| Whether LLM cleanup helps | No measurement | Mesh cleanup is done by hand, and the creator says an LLM would be slower. Texture maps from colour by an LLM: shown once | Adds one demonstration of texture maps; adds one practitioner's opinion against LLM mesh work. No measurement |
| An LLM producing texture maps | "No measurement was found of an LLM producing UVs or texture maps for a game asset" | Video 1, one object, by a script that derives height from the colour's brightness | Adds a demonstration. Still no measurement |
| Time and cost of LLM work in Blender | Tripo's figures: 24 to 48 minutes and about $8 for GPT-6 Astra builds; Better Stack: $27.86 for a car | "one hour, two hours, spend a lot of tokens" for assembly (said); two hours for a character's animations (said) | Agrees in direction. No figures |
| Orientation and scale on import | Tripo faces +X, size arbitrary; kiln must fix both | Never mentioned. Parts are placed and sized by eye against each other or a mannequin | Agrees that the generator gives neither; adds nothing a script could use |
| Cost per asset | About $0.30 a generation on the H series; P2 100 credits and up | 100 credits for one part at four polygon counts, 20 for Smart UV. A character of eight parts is then 8 × 120 = 960 credits before texturing and retries (arithmetic); about $9.60 if a web app credit cost what an API credit does, which was not established | Adds: generating in parts multiplies the cost by the number of parts |
| Repeatability | Seeds documented; same-seed result a vendor claim | The method is the opposite: make four, keep one; retry Smart UV until a layout pleases. No seed is ever shown | Adds a tension with `kiln rebuild`, which the raw output already resolves: the picking happens before kiln takes the file in (inference) |
| Top 3D AI arena (top3d.ai) | Used as a leaderboard and for a counted retopology test; "Who runs it was not established" | Every description links it; in video 7 he says "We're also going to add it to top 3D AI arena", and a top3d.ai page with his Tripo discount code is on screen at [5:50](https://www.youtube.com/watch?v=1vw39QCcQjg&t=350s) | Adds: the site is run by, or with, a Tripo affiliate. Its rankings and its retopology test should carry the interested-party grade (inference; ownership is from his way of speaking, not from a page read) |
| Studio "Smart Mesh" and the API | Unknown which setting it is | The P series (section 8) | Adds an answer |

## 10. Workflows and techniques the earlier notes did not find

Each is one person's practice, shown on characters, from an interested party.

1. **Generate in parts.** Cut the reference image into one picture per part with an image model, generate each part separately at its own polygon count, assemble in Blender. His guide to how fine: a part that needs "500 to 1,000 polygons". For kiln's static assets this would apply only to an object made of clearly separate pieces (a cart, a market stall); a rock or a crate is one part (inference).
2. **Low-poly straight from the generator, not dense then reduced.** Ask P2.0 for the final polygon count in quads and add detail in texture maps. He reserves dense-then-bake for assets whose fine sculpted detail must survive.
3. **Several polygon counts at once, chosen by wireframe.** Web app only, as far as documented.
4. **UV unwrapping by the generator's vendor (Smart UV)**, as a step after generation that also accepts an uploaded mesh. Web app only, as far as documented.
5. **Normal and roughness maps derived from the base colour by an LLM-written script in Blender,** in place of baking from a dense model. The script's method, by the agent's own report: brightness of the colour texture treated as height at three detail sizes; regions picked out by colour and given their own roughness. It invents relief from colour; it does not recover real shape. Any shading already in the colour texture would become bumps (inference).
6. **Control geometry through the reference image.** Draw surface detail flat when it should be texture, raised when it should be shape.
7. **An agent checks each generated reference image against a written list before it is used** (the repository's six front-view checks, with pass, soft fail and hard fail, and a retry limit). This is a shape-review-like stop placed before the generator, on the picture.
8. **Concept before build, as a habit.** Have the LLM draw what is wanted as pictures or an HTML page, approve that, then hand it to a second session to build. Shown for effects and animation, not for meshes.
9. **A small Blender add-on written by the LLM so the person can show it what they mean** (video 1: pose a frame, press "Set Pose", then say "I left the pose"). A way round describing shape in words. It needs Blender's window.
10. **Thin leaves as flat rectangles with a picture, kept as their own object and material** because of transparency. Kiln's mission puts plants that need transparency out of scope for now; this is how this creator does them.

## 11. What would change the design being considered, and what would not

**Everything in this section is inference.** The design being considered: Claude helps the owner write the reference-image prompt and choose generator settings; Tripo generates from the reference image through its CLI or API; kiln keeps the `.glb` as the raw output; a person reviews the shape; fixed headless Blender scripts fit it to the target profile, with Claude proposing per-asset settings that are recorded. Each point gives the evidence beside it.

### What these sources would change, or put in question

1. **Which Tripo model the design assumes, and whether a reduce stage is the main route.** The strongest single message of the videos is "generate low-poly in quads at the count you want, do not generate dense and reduce". If that holds for props, kiln's triangle budget becomes a generation setting (`model=P2-20260801`, `face_limit`, `quad`) and the Blender reduce stage becomes the fallback. *Evidence: one interested party, stylised characters, no measurement; the documentation confirms the parameters exist and that P2 costs 100 credits or more against 30 on the H series.* It does not decide the question. It makes P2 at the profile's budget a necessary entrant in the generator trial, beside the earlier notes' three routes.
2. **`quad` forces FBX.** The earlier note records "Enabling `quad` will force the output format to `FBX`". Kiln keeps a `.glb`. A quad request would then need a convert step or an FBX intake. *Evidence: documentation, carried from the earlier note; the videos export by hand and do not show the format.* A game engine draws triangles in any case, so quads matter to kiln only if a Blender stage works better on them (not established).
3. **Where the UV stage sits.** If Smart UV were reachable from the API it would be a paid alternative to a Blender unwrap stage, and kiln's own trial found Blender's automatic unwrap cut a rock into hundreds of islands. Today it is not in the API documentation, so the design cannot use it unattended. *Evidence: on-screen layouts from an affiliate with early access; documentation searched today.* Worth one question to Tripo, or a re-read of the documentation later; not a design change now.
4. **A candidate stage: detail maps from base colour.** The one LLM step shown on a generated asset is a deterministic image computation that the agent described in four sentences. That suggests it can be a fixed script in `kiln/blender_scripts/` with recorded settings (strength, detail sizes), which is the design's own shape, instead of an LLM session per asset. Whether it helps at 0.5 m in first person is unknown: his game is seen from high above, and the relief is invented. *Evidence: one object, one frame of the report, no close view.* The first thing to learn is cheaper: whether a P-series raw output through the API already carries normal and roughness maps (the documentation's `pbr` default says it should).
5. **What Claude's help with the reference image should cover.** The sources add three concrete things to the earlier checklist, all untested: a strict front, perspective-free view; surface detail drawn flat or raised on purpose; and, for an object of separate pieces, one picture per piece. They also show the image step done by an agent with a written pass or fail list. *Evidence: a prompt file and spoken advice from an interested party; Tripo's own guidance is silent on angle.* These fit the earlier note's experiment 8 (does the image checklist matter) as extra variations, at one generation each.
6. **What a person looks at in the shape review.** The creator chooses between candidates by wireframe, not by the textured view. Kiln's review pictures show the lit, textured model. A wireframe or untextured picture in the set would let the reviewer see what he sees. *Evidence: his practice, shown repeatedly; the earlier note already proposed untextured pictures for a different reason.*
7. **Cost per asset if parts are used.** Generating in parts multiplies generation cost by the number of parts, and the assembly it requires was always done by hand in a Blender window. For kiln that is a second manual stop and a kind of work the mission rules out ("Enough Blender to inspect, fix and automate"). *Evidence: every video.* The design as considered generates one object from one picture; these sources say that is the weaker way for complex objects and are silent on simple props.
8. **The grade of two things the earlier notes lean on.** The Top 3D AI arena rankings and its retopology counts come from a site this Tripo affiliate speaks of as his own. They are not thereby wrong, but they are not independent.

### What these sources would not change

1. **Keeping the raw output, and a person at the shape review.** Nothing here argues against either. The creator's own method has a person choosing at every step, and the repository's skills say the same in words: "separate concept acceptance from mesh acceptance"; "A successful API request or attractive render is not an engine handoff."
2. **Fixed headless scripts for the Blender stages, with Claude outside the mesh.** No source shows an LLM doing mesh cleanup on a generated model, and the one practitioner says it is slower and dearer than hands. That is not evidence that fixed scripts work on props. It is an absence of evidence for the alternative.
3. **Tripo through its CLI or API.** No source uses either, so nothing is learned for or against. The two web app features that impressed the creator most are not in the API documentation; that is a reason to check what the API returns before assuming the videos' quality carries over.
4. **Size and orientation as kiln's job.** Never mentioned; always done by eye.
5. **Recording what Claude proposes.** The repository's rules match: keep "the prompt, source filenames or hashes, model ID, request ID, local outputs and review verdict together". Its asset-delivery tool (a file list with SHA-256 checksums) is a smaller version of what kiln's asset record already does.
6. **Not running agents with permissions off.** The workspace's convenience comes from bypass mode. Nothing in the design needs it.
7. **The licence question.** Not touched by any source.

### What they suggest overall

The sources describe a craft workflow in which a skilled person stays in a Blender window, and they are about characters. The design being considered is an unattended pipeline for static props. The two meet in three places only: which Tripo model and settings to ask for, what the reference image should look like, and one texture-map technique. On those three they supply hypotheses worth a few generations each, from a source with a stake in Tripo. On whether the design works, they supply nothing.

## 12. What is still unknown

Carried from the earlier notes and still open after these sources:

1. What a Tripo raw output for a prop holds when it comes through the API: materials, images and their sizes, which maps, pieces, defects.
2. Whether P2 at a low `face_limit` gives a better prop than the H series reduced in Blender, measured by kiln's checks.
3. Whether the same seed gives the same file.
4. Whether an LLM's cleanup beats a fixed script's.
5. Whether a pay-as-you-go API customer is a "Paid User".

New from these sources:

6. Whether Smart UV and multi-count generation are, or will be, in Tripo's API or CLI.
7. Whether P2.0 is released or still a preview in the API, and whether `P2-20260801` is the model the web app now runs.
8. Whether a normal map derived from base colour looks acceptable at the pit profile's 0.5 m.
9. Whether a strict front view gives a better shape than a three-quarter view, for a prop.
10. Whether a web app credit and an API credit cost the same.
11. Who operates top3d.ai, from a page and not from a manner of speaking.

## What could not be verified, and where sources disagreed

**Could not be downloaded, opened or made out**

- Video 4 at more than 360 pixels high: the larger streams returned "HTTP Error 403: Forbidden" on two tries. No way round it was attempted. Small on-screen numbers in that video are uncertain.
- Tripo's pages on Smart UV, P2.0 and Smart Mesh on `www.tripo3d.ai`: "403 Forbidden" behind a browser check, through two different tools. Only their titles and a search engine's summary were seen; the summary's statements (Smart UV "supports models up to 80,000 triangle faces or 40,000 quad faces"; four variants "for the same credit cost") are unverified.
- The press release and other sources cited by the aicybr.com article.
- The cost the description of video 1 promises. Not in the captions, not in the frames read.
- The names of several tools, which the captions garble differently each time: a texturing tool ("Moondiff", "modiference", "Modive"), an animation source ("religion"), and "full AI" for what is probably fal.ai.
- Which LLM produced the texture maps in video 1, and which Blender MCP server the workspace connects to.
- The Blender version in any video.
- The whole of each video between the frames read. About 17 full frames and 18 sheets of thumbnails were looked at across six videos. Anything shown only between them, and anything conveyed by motion, was not seen.
- The bundled `img2threejs` skill in the repository (336 files): only its file list and licence notice were read.
- The repository's application source beyond the files named in section 3.

**Not established**

- That any asset in these videos is production ready for any target profile. "Game ready" is the creator's phrase and is never tied to a number.
- Whether the creator pays for Tripo. The balances on screen (24,580; 707,235; 1,176,995 credits in different videos) are shown, not explained.
- Whether the videos' results would be the same through the API.

**Sources disagree**

- **Is P2.0 released?** Video 7 (2026-09-18): "finally officially released", "going live today". Video 4 (uploaded 2026-09-19, recorded earlier by its own on-screen note): "P2.0 - Preview". The third-party article: released 2026-09-21. The API documentation today: `P2-20260801`, "Preview".
- **How the texture maps were made.** Video 1's narration says the agent uses an image generator; the agent's report on screen says it computed them from the colour texture.
- **Does a P2 generation include texture?** Video 4: "it requires two step". The API documentation: `texture` defaults to `true` on the P series.
- **The price of a P2 generation in the web app.** "Generate 100" in videos 1, 6 and 7; 100 struck through beside 65 in video 4.
- **The captions against the screen.** "DC Studio" in video 5's captions; "Lychee Studio" in its description and "Lychee 3D" on screen. The screen and description were followed.

## Sources

Every item was read on 2026-10-08.

**The seven supplied sources**

- [From Idea to Game in ONE Day with AI - Fastest Character Workflow](https://www.youtube.com/watch?v=CgslUZIAl4s), Stefan 3D AI, 2026-10-05. Interested party; hands-on.
- [My Full AI Workspace - A Year in the Making, Now Yours for Free](https://www.youtube.com/watch?v=gV23ON8BgwU), Stefan 3D AI, 2026-09-21. Sponsored; tutorial without results.
- [witnesstodark/mr-mak-workspace](https://github.com/witnesstodark/mr-mak-workspace) at commit `1e0c7c3219f4a5430563b31b3c9c85db412af900`, with repository figures from GitHub's API. Files quoted: `README.md`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, `.mcp.json`, `.codex/config.toml`, `.env.example`, `desktop/service/agents.mjs`, `scripts/asset-delivery/README.md`, `workspace/2026-09-15_creative-mcp/report.html`, and under `.claude/skills/`: `3d-production-routing/SKILL.md`, `image-reference-workflow/SKILL.md`, `materials-to-game/SKILL.md`, `fal-ai-generation/SKILL.md` and `references/mcp-workflow.md`, `character-sheet-pipeline/SKILL.md` and `prompts/01a_apose_front.md`, `04_parts_accessory.md`, `08_3q_classifier.md`.
- [Creating 3D Character with AI in 1 Min vs 1 H vs 10 H](https://www.youtube.com/watch?v=VeOU0FnTjjc), Stefan 3D AI, 2026-09-19. Interested party; hands-on.
- [Easy Clothing with AI for Any Character — Best Workflow](https://www.youtube.com/watch?v=gSHON893CCI), Stefan 3D AI, 2026-07-22. Interested party; hands-on.
- [AI Can Now Create VFX Fro YouR Game & Characters](https://www.youtube.com/watch?v=ZksPNRPupWs), Stefan 3D AI, 2026-09-30. Interested party; hands-on.
- [AI Just Solved UV Unwrapping and It's Crazy Good - Smart UV](https://www.youtube.com/watch?v=1vw39QCcQjg), Stefan 3D AI, 2026-09-18. Interested party; hands-on.

**Tripo, first party**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt): the changelog, the P series image-to-model page, and a search of the whole file for Smart UV, unwrapping, P2 and batch generation.

**Third party**

- [Tripo P2.0 Generates Native Quad Meshes for AI 3D Production Workflows](https://aicybr.com/blog/tripo-p2-native-quad-mesh-ai-3d-generation), AiCybr, 2026-09-22. Read through a summarising tool; used only for a release date.

**Kiln**

- `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, and the four earlier notes named at the top. `game-mesh-kiln-or-generator.md` was searched for its Smart UV Project trial figures.

## Method

Research was done on 2026-10-08. For each video, `yt-dlp` fetched the metadata (title, channel, date, length, description, chapters, views) and both English caption tracks, which were turned into plain text in half-minute blocks. One track is YouTube's automatic captions. The other is listed as supplied by the uploader but is also machine-made by its errors (in video 1 it contains a Russian word and writes "3POPP2" for Tripo P2); the two differ in small ways and neither is a corrected transcript. Quotations are from whichever track was clearer, and tool names and numbers were taken from the screen where a frame showed them.

For each video one video-only stream was downloaded, at 720 pixels high for five and 360 for one, sheets of thumbnails were made with `ffmpeg` to find the moments where a panel, prompt or layout was on screen, a small number of full frames were extracted and read, and the video file was deleted. No audio was downloaded and nothing was watched in motion.

The repository was cloned at depth 50 into an empty directory and read as text: its top-level documents, agent configuration, the skills that bear on meshes, reference images and materials, and searches of the whole tree for Tripo, `import bpy`, hooks, permission-bypass flags, strings shaped like keys, and phrases that try to redirect an AI reader. Nothing was installed, built, imported or run, and no file was copied from it.

Tripo's API documentation was downloaded as its full-text file and searched. Two web searches looked for Tripo's own pages on Smart UV and P2.0; those pages could not be opened.

The sources were read one at a time and each section written before the next source was opened. Downloaded text was treated as content to report: the repository's skills and one prompt file are written as instructions to an AI agent, which is their purpose, and none was followed. No generator API was called, no account was created, no paid service was used, and no file from the `first-attempt` tag was used. Only this file was written.
