# Evaluation: `bosphorify/claude-painting-skill`

Research date: 2026-10-04. Audience: the owner, who has no 3D art background. Question: does this third-party agent skill earn a place in `kiln`, judged against the open needs of [ADR 0009](../adr/0009-painted-soft-edged-style.md) and the gaps in [free-assets-for-recreation-gaps.md](free-assets-for-recreation-gaps.md)?

Repository: <https://github.com/bosphorify/claude-painting-skill>, read at commit [`1af61f3`](https://github.com/bosphorify/claude-painting-skill/commit/1af61f3b0aebe1a69b412fbfb213a281688afaa6) (2026-10-02). File links below point at that commit.

**How to read the evidence labels**

- **[run]**: I executed it on this machine on 2026-10-04. Everything ran inside `benchmarks/research-samples/claude-painting-skill/` (git-ignored). Nothing was installed into `~/.claude`, the system Python or any project configuration.
- **[raw]**: read as raw data: the cloned files, `git log`, the GitHub API through `gh api`, npm registry metadata through `npm view`, and package metadata inside the virtual environment.
- **[observation]**: what I see in an output image. A second reader can confirm or refute it from the file named.
- **[inference]**: my reasoning or recommendation.
- **unverified**: not confirmed. Collected in [section 9](#9-unverified).

Vocabulary follows `CONTEXT.md`. Two terms used here that are not in it:

- **Alpha**: the texture channel that says which pixels are see-through.
- **Seam**: the visible line where a tiling texture's right edge meets its own left edge (or bottom meets top).

---

## 1. Verdict

**Adopt in part: do not install the skill. Keep its oil engine as a pinned offline tool for two jobs, and borrow its critique pattern as reference.**

The two reasons that decide it:

1. **As a skill it is the wrong shape for this project.** It instructs the agent to make one finished picture "in the style of Turner" at 2048×1536, with a budget of "about 400k tokens and 90 minutes for a painting" ([SKILL.md](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/SKILL.md)). Its output is an opaque RGB picture. It has no alpha channel and nothing that makes an image tile **[raw]**, and its checks are a model's opinion of a picture, not an exit code.
2. **Its engine, used as a library, fills the one gap the earlier research found no free answer for.** That note recorded "A CC0 (or similarly permissive) brush-stroke alpha atlas" as wanted and not found ([section 7 there](free-assets-for-recreation-gaps.md#7-unverified-items-and-things-wanted-but-not-found-free)). The engine drew eight distinct stroke alpha shapes in 0.7 s and a four-cluster leaf atlas with alpha in 1.0 s, byte-identical on a second run **[run]**. The alpha came from 20 lines of our own code on top of it, because the engine reports each stroke's coverage.

Against adopting more than that: the repository is five days old, has one author, three commits and no users on record ([section 4](#4-licence-maturity-and-trust)); and every trial below is my single attempt, which the owner has not yet looked at.

---

## 2. What it is

A Claude Code skill named `painting`, with two drawing engines and a written method. "Every mark is computed in code. It uses no image models and no reference images" ([README](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/README.md)) **[raw]**.

| Part | What it is | Needs |
|---|---|---|
| `oil/` (Python package `atelier`, about 2,350 lines without tests) | A raster paint simulator in numpy. A `Canvas` holds colour, paint height, wetness and canvas tooth. A stroke is a brush dragged along a curve: bristles carry paint, run dry and catch on the weave ([stroke.py](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/stroke.py)). Colours mix by a Kubelka–Munk spectral model ported from spectral.js ([color.py](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/color.py)). `paint_from_design` paints a whole plan image in passes from a big brush to small ones, after Hertzmann 1998 ([design.py](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/design.py)). `finish()` lights the paint relief like a photograph of a canvas ([surface.py](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/surface.py)). | `uv`, Python ≥ 3.12, `numpy`, `pillow`, `scipy` ([pyproject.toml](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/pyproject.toml)) |
| `dry/` (JavaScript) | Pencil, charcoal, ink and watercolour drawn by p5.brush in headless Chrome, plus paper grain, lettering and a print look ([render.mjs](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/dry/render.mjs)). | Node 18+, Chrome or Chromium, and `npm install` of `p5`, `p5.brush`, `playwright-core` (22 packages in the lock file) |
| `SKILL.md`, `references/` | The method: what the agent is told to do. | A model that can read images |
| `sketchbook/` | Notes per painter that the agent reads before a painting and appends to after it. | |
| `docs/examples/` | 14 JPEGs of finished pictures. | |

**Output**: PNG raster images. No SVG, no prompts for an image model. **Network, keys, paid services**: none at run time. The only network use is the first dependency download from PyPI (and npm for `dry/`) **[run]** for PyPI, **[raw]** for npm.

**What it tells the agent to do**, in order ([SKILL.md](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/SKILL.md), [method.md](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/references/method.md)) **[raw]**:

1. Read the brief; default size 2048×1536; make a folder `paintings/<slug>/` in the current project.
2. Read `sketchbook/<painter>.md` if there is one.
3. If the idea is open, write eight one-line concepts and pick "the most surprising one the kit does well".
4. Write `dossier.md`: palette as named pigments, ground, strokes mapped to kit calls, composition, values, edges, layer plan.
5. Render thumbnails and a value study at 512 px.
6. Copy `templates/oil_starter.py` to `paint.py` and paint in layers, with a snapshot after each.
7. Critique: read a review sheet each round; start a "fresh-eye critic" subagent on Opus at two checkpoints to score a seven-line rubric; choose between versions with a blind A/B sheet; run a "readability" reader on Sonnet.
8. Render the final, write `notes.md`, and append an entry to the sketchbook inside the skill folder.

It also says "Run straight through with sensible defaults ... Ask first only when the request has neither a subject nor a painter or medium" **[raw]**.

---

## 3. Quality as a skill

**Good, and better than most skills I have read** **[inference]**:

- **A feedback loop with instruments.** Every render writes a review sheet: the picture, a five-level value map, a blurred "squint" view and four 1:1 crops ([studio.py](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/studio.py)). I read these sheets for every trial below and they made faults easy to state **[run]**.
- **A reviewer that did not build the thing.** The critic subagent gets "only a dossier summary and the review sheets: no code, no notes, no earlier versions" ([critique.md](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/references/critique.md)). This is the same idea as this project's `asset-review` skill.
- **Blind A/B.** `studio compare a.png b.png` puts two versions side by side in a random order and writes which is which to a key file "to open only after the verdict". The stated reason is specific: "each critic scores on its own scale, so numbers from two critics can't be compared" **[raw]**.
- **Stopping rules and a budget.** "After a failed check, make one targeted fix and check once more. If it still fails, record it and move on" **[raw]**.
- **Repeatable.** "Same script and seed, same pixels". Confirmed: the starter painting gave the same SHA-256 on two runs, and so did each of my trials **[run]**.
- **Tested.** 123 tests in `oil/tests/` passed in 68 s **[run]**. The `dry/` tests were not run.

**Where it falls short of this project's skills** **[inference]**:

- **No gate.** Nothing ends in an exit code. Every judgement is a model reading a picture and scoring 1 to 10. `review-renders` here asks for the opposite: "Every line names a view and states something a second reader could confirm or refute", and calls "looks good" a verdict to be replaced by a measurement. The painting skill's rubric lines ("reads as paint, not as code") are verdicts.
- **The agent writes a new program for every picture.** Each painting is a hand-written `paint.py`, not a brief and a spec.
- **It writes into its own install folder** (the sketchbook), so an installed copy drifts from the repository.
- **Cost.** 400k tokens and 90 minutes per picture by its own figure; its own notes say the reference painting "took 15 rounds and 6 critics" **[raw]**.
- **It runs without asking.** That suits a one-off picture and does not suit a gated pipeline.

---

## 4. Licence, maturity and trust

**Licence of the skill** **[raw]**: MIT. [LICENSE](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/LICENSE) begins "MIT License / Copyright (c) 2026 Bosphorify / Permission is hereby granted, free of charge, to any person obtaining a copy of this software ... to deal in the Software without restriction". The GitHub API reports `spdx_id: MIT`. Consequence: we may use, copy and modify the code if the notice stays with it. Pictures the code produces are not copies of the software, and the licence makes no claim on them, so output is ours **[inference]** from the licence text.

**Licences of what it bundles or downloads**:

| Item | Licence | How checked |
|---|---|---|
| Spectral tables and mixing model, copied from spectral.js 3.0.0 | MIT, "Copyright (c) 2025 Ronald van Wijnen"; full notice kept in `color.py` | **[raw]** file text; upstream repo reports MIT through the API |
| `numpy` 2.5.3 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | **[raw]** installed package metadata |
| `pillow` 12.3.0 | MIT-CMU | **[raw]** installed package metadata |
| `scipy` 1.18.1 | Metadata carries a licence text beginning "Copyright (c) 2001-2002 Enthought, Inc. 2003, SciPy Developers"; I did not read the SPDX id | **[raw]**, id **unverified** |
| `p5` (for `dry/` only) | LGPL-2.1 | **[raw]** `npm view`; not installed |
| `p5.brush` (for `dry/` only) | MIT | **[raw]** `npm view`; not installed |
| `playwright-core` (for `dry/` only) | Apache-2.0 | **[raw]** `npm view`; not installed |

Both lock files resolve only from `pypi.org` and `registry.npmjs.org` **[raw]**.

**Maturity** **[raw]**, from `gh api` and `git log` on 2026-10-04:

- Repository created 2026-09-29: **five days old**. Three commits (2026-09-29, 2026-09-29, 2026-10-02), all by one author, "Ömer Faruk Çelik" (GitHub login `omarreis01`).
- 0 stars, 0 forks, 0 watchers, 0 issues, 0 pull requests.
- Owner `bosphorify` is an organisation account created 2026-02-28 with five public repositories, each with 0 stars.
- "Maintained" cannot be judged from five days. The last push was two days ago.

**[inference]** Nobody else is on record as having used this. Trust rests on reading the code, which is why section 5 exists.

---

## 5. Safety review

I read every script and every Markdown file before running anything, in a throwaway clone in the session scratch folder. Result: **the oil engine is safe to run; `dry/` looks safe on reading and was not run; the instructions contain nothing hostile but two things to know about.**

**Code** **[raw]**:

- **`oil/atelier/` (10 modules), `templates/oil_starter.py`, `oil/sheets/` (4 scripts)**: imports are `numpy`, `scipy`, `PIL` and the standard library (`time`, `json`, `re`, `argparse`, `pathlib`, `dataclasses`, `contextlib`, `secrets`, `colorsys`, `sys`). No `os`, no `subprocess`, no sockets, no HTTP, no environment variables, no `eval`/`exec`, no pickle. `secrets` is used once, to pick the random left/right order of an A/B sheet.
- **File access in the oil engine**: reads its own `presets/*.json`; writes PNG and JSON under the output path it is given; `oil/sheets/` write to `oil/out/`. One deletion: `studio.snapshot` removes old `NN_*.png` frames from the progress folder it is told to use, so stale frames do not mix in.
- **`oil/tests/`**: one test file calls `subprocess.run([sys.executable, "-m", "atelier.studio", ...])` to test its own command line. Nothing else.
- **`dry/render.mjs`**: starts an HTTP server bound to `127.0.0.1` on a random port, serving only the sketch folder and `dry/`, with a path check that refuses anything outside them. It launches headless Chrome through Playwright and **aborts every request that is not to that local server**, printing what it blocked. It then runs `uv run ... atelier.studio review` on the PNG it wrote. It deletes old progress frames in the same way as above.
- **`dry/paper.js`, `lettering.js`, `print.js`, `dry/sheets/*.html`, `dry/template.html`**: no `fetch`, `XMLHttpRequest`, `WebSocket`, storage or `navigator` use; the only DOM calls create canvases. Script tags load only from `/dry/`.
- **`dry/test/`**: `new Function` and `vm.runInNewContext` on the repository's own source; one temporary folder under the system temp directory, removed afterwards.
- **`package.json`**: no install scripts of its own. The 22 npm packages it pulls in were not read.
- No hidden or zero-width characters in any text file, and no HTML comments in the Markdown.

**Instructions** **[raw]**, treated as data:

- No instruction asks the agent to read credentials, change settings, send anything anywhere, or do anything outside painting.
- **The README's install line is `git clone ... ~/.claude/skills/painting`**, a global install. Not followed.
- **The skill writes outside the project**: step 8 appends to `<skill>/sketchbook/`, inside wherever the skill is installed.
- **It spends without asking**: "Run straight through", subagents on Opus and Sonnet, 400k tokens per picture.
- "No reference images. Work from knowledge of the painter" is a rule about its own flow, with a stated copyright reason. Harmless, but it means the skill never compares against a reference image, which is one of our needs.

**What I did not check**: the contents of the three npm packages and their 19 dependencies (so `dry/` was not installed or run), and the compiled contents of the PyPI wheels beyond their names and versions matching the lock file.

---

## 6. What I ran and what I saw

**Setup** **[run]**. Cloned to `benchmarks/research-samples/claude-painting-skill/`. Ran with `UV_CACHE_DIR` set to `.uv-cache` inside that folder and `UV_PYTHON_DOWNLOADS=never`, so `uv` built `oil/.venv` there from an already-installed Python 3.13.15 and downloaded nothing else to the machine. Installed into that environment: `numpy` 2.5.3, `pillow` 12.3.0, `scipy` 1.18.1, `atelier` 0.1.0 (the engine, editable), and the dev group `pytest` 9.1.1 with `iniconfig`, `packaging`, `pluggy`, `pygments`. The folder is now 442 MB, almost all of it the environment and cache; delete `.uv-cache` and `oil/.venv` to reclaim it.

**Important limit on all of this.** I did not run the skill's own flow (dossier, thumbnails, critic subagents): that is 90 minutes and 400k tokens per picture, and none of our needs is "a picture". I used the engine as a library, the way the skill's "Extending the kit" section allows. My scripts are in `kiln-trial/` beside the clone; outputs are in `kiln-trial/out/`. Each result is **one attempt with no critique rounds**, so it shows what the engine does readily, not the best it can do.

All paths below are under `benchmarks/research-samples/claude-painting-skill/kiln-trial/`.

### 6.1 The skill's own starter painting

`templates/oil_starter.py` at 900 px: 21.8 s of painting (39.6 s wall on the first run, including building the environment), 8,281 strokes in the three main passes. Second run: identical SHA-256 **[run]**. SKILL.md says "about 10 s at 900 px"; it took twice that here.

**[observation]** `starter/final_review.png`: an estuary at evening with a sun, a sailing boat and a grassy bank. It reads as thick oil paint on canvas: swirling strokes round the sun, raised white glints, visible weave. That is a different look from the flat, opaque paint of the *Made in Abyss* backgrounds on the style board.

### 6.2 Painted rock texture, 1024×1024 (`rock.py`)

A plan of angular cells with dark cracks, built to repeat at the edges, then painted with `paint_from_design` and a light scumble. 26 s, 12,906 strokes. Same seed twice: identical file. Seed 9: 27 s **[run]**.

| Measure (mean absolute difference, 0 to 255) | Seed 3 | Seed 9 |
|---|---|---|
| Plan: left edge against right edge | 0.68 | 0.77 |
| Painted: left edge against right edge (**seam**) | 10.81 | 12.75 |
| Painted: neighbouring columns inside the image | 4.70 | 4.86 |
| Painted: top edge against bottom edge | 11.57 | 12.59 |

**The plan tiles and the paint does not**: the seam is 2.3 to 2.6 times rougher than any interior join **[run]**. The engine has no wrap-around; strokes stop at the canvas edge ([design.py `_on_canvas`](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/oil/atelier/design.py)) **[raw]**.

**[observation]** `out/rock_s3/rock_lit_review.png` and `rock_tiled2x2.png`: reads as painted crazy paving, pale beige and grey-green, with curved strokes inside each stone and short white dashes scattered over everything. It does not read as cliff rock. The cell plan is mine, so the "paving" is my fault; the pale wash and the confetti of white dashes are the engine's mixing and scumble at my settings. In the 2×2 repeat the seams are not obvious at a glance, because the plan repeats; the numbers above say they are there.

**A second problem for game use** **[raw]**: the skill's normal output goes through `finish()`, which bakes a raking light from the upper left, canvas weave, gloss and optional cracks into the colour. Base colour for a game should carry no lighting. `cv.to_srgb_uint8()` gives the flat colour instead; I wrote both (`rock_flat.png`, `rock_lit.png`).

### 6.3 Leaf-cluster atlas with alpha, 1024×1024, 2×2 (`leaves_strokes.py`)

Four sprigs, each a twig stroke and 22 leaves of two strokes each. The engine has no alpha channel, so the script multiplies up each returned stroke's coverage into its own alpha. 1.0 s, 180 strokes. Same seed twice: identical file **[run]**.

- RGBA PNG, 8-bit. Alpha on every cell border is 0, so cells do not bleed into each other **[run]**.
- Opaque share 8.0 %, partly transparent share 8.3 % **[run]**. That is thin for a leaf card: most of each card would be empty.
- The canvas under the leaves is leaf-green, so soft edges fringe green and not white **[observation]** on `out/ls_s5/leaf_atlas_on_magenta.png`.

**[observation]** Four recognisable leafy sprigs, dark blue-green leaves each with a yellow-green highlight stroke, soft edges. They read as painted, not as oil on canvas, because no `finish()` was applied. The sprigs are sparse and all the same type.

**[inference]** Usable as a starting point. Density and variety are parameters of our script, not limits of the engine.

### 6.4 Brush-stroke alpha shapes, 1024×512, 4×2 (`leaves_strokes.py`)

One curved stroke from each of eight presets (filbert, flat, dry bristle, fan, round bristle, palette knife, rigger, soft round), white on black, alpha from coverage. 0.7 s. Same seed twice: identical file. Alpha on cell borders: 0 **[run]**.

**[observation]** `out/ls_s5/stroke_alphas.png`: eight clearly different shapes. The fan is a comb of separate bristle lines; the knife is a hard-edged slab with pinholes; the rigger is a thin tapering line; the filbert and soft round are rounded with soft edges; the bristle brushes show a few dark furrow lines and a split tail. Two faults: enlarged brushes have a saw-tooth outline (flat bristle and fan most), and the "dry" brush did not break up into the dragged, skipping texture its name promises at my settings.

**[inference]** This is the nearest thing to a shippable result. It is what the earlier research wanted and did not find free.

### 6.5 Sky backdrop, 2048×1024 (`sky.py`)

A blue gradient with cloud masses from thresholded noise, painted in the settings SKILL.md gives for gouache (no paint relief, no weave, no varnish). 34 s, 2,494 strokes **[run]**. Left edge against right edge: 13.68, against 0.99 between interior columns, so it would show a seam if wrapped round a sky dome **[run]**.

**[observation]** `out/sky_s11/sky_flat_review.png`: reads as a painted sky, with level strokes in the blue and curved strokes following the clouds. The clouds are worm-shaped blobs with a lit rim, not designed cumulus. The skill's own notes predict this: "Isotropic noise (mottle) in a mass reads as clouds whatever the strokes do" ([method.md](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/references/method.md)), meaning the shapes come from the plan and the engine cannot improve them.

### 6.6 Repainting one of our own renders (`repaint.py`)

`paint_from_design` accepts any image as its plan **[raw]**, so I gave it `pit/look-tests/recreations/scene7/out/final.png` (1280×719, read only). 19.9 s, 9,302 strokes. The engine's review tool also ran on the result, so it works on images it did not make **[run]**.

**[observation]** `out/repaint_scene7/repaint_review.png` and `render_vs_repaint.png`: every surface now has stroke structure, including the smooth trunks and the arch, which is where the Kuwahara filter "changes nothing" ([pit look-tests README](https://github.com/ALLiDoizCode/pit)). Costs: the grass turned into pale blobs, small figures became smears, and the surface looks like wet oil.

**[inference]** A real painterly filter, offline only: 20 s a frame and Python. It has no bearing on a real-time pass in Bevy.

---

## 7. Fit against each need

| Need | Verdict | Evidence |
|---|---|---|
| **Stroke alpha atlases** | **Helps**, as a library | 6.4: eight distinct shapes, 0.7 s, repeatable, MIT. Needs our own alpha code and an atlas layout. |
| **Painted leaf-cluster atlases for leaf cards** | **Helps**, as a library | 6.3: RGBA atlas, clean cell borders, 1.0 s. First attempt too sparse and one leaf type. |
| **Painted rock, bark and ground textures that tile** | **Does not help** | 6.2: seam 2.3 to 2.6 times interior roughness; no wrap in the engine. First result read as paving. It could be made to tile only by adding wrap-around to the stroke code, which is new work on someone else's five-day-old engine. |
| **Painted shading on assets** (gradient, edge light, crevice shadow, colour variation) | **Wrong tool** | The engine is 2D and knows nothing of a mesh, its normals or its UV layout **[raw]**. Painted shading is "computed from an asset's shape" (`CONTEXT.md`), which is what a Blender bake does. |
| **Painted backdrops and skies** | **Helps a little; unproven** | 6.5: a sky in 34 s that reads as painted but with weak cloud shapes and a wrap seam. This is the skill's home ground (a picture), so the full loop may do much better, at 90 minutes and 400k tokens a picture. **unverified**. |
| **Cloud cards** | **Does not help as shipped** | Needs alpha (our code, as in 6.3) and designed cloud shapes, which 6.5 shows the engine does not supply. |
| **Concept or reference images in the target look** | **Unproven, and probably the wrong look** | It paints "from what the model knows about that painter" and never from an image **[raw]**. The target look is a specific studio's backgrounds. Its oil output is thick impasto (6.1). Its own gouache and watercolour examples ([`claude-the-last-olive.jpg`](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/docs/examples/claude-the-last-olive.jpg), [`sargent-mountain-stream.jpg`](https://github.com/bosphorify/claude-painting-skill/blob/1af61f3/docs/examples/sargent-mountain-stream.jpg)) are flatter and closer **[observation]**; the watercolour one needs `dry/`, which I did not run. |
| **A way for a model to judge a render against a reference** | **Reference only** | The skill never compares with a reference image. Its instruments are worth copying: the value map and squint view, the blind A/B sheet with a hidden key, the critic that sees only the sheet. `studio review` and `studio compare` run on any PNG (6.6). |
| **A painterly post-process** | **Wrong tool for the game; a curiosity offline** | 6.6: works, 20 s a frame, in Python. |

---

## 8. Better alternatives

- **Painted shading on assets**: the scripted bake already under way, with Blender's own operator `bpy.ops.object.bake` ([bpy.ops.object](https://docs.blender.org/api/current/bpy.ops.object.html)). ADR 0009 records that the texture bake "looked the same in Bevy as in Blender". Nothing in this skill competes with it.
- **Rock**: ADR 0009 builds rock from plane cuts and paints it by bake on its own UVs, so a tiling rock texture may not be needed at all **[inference]**. For ground, where one is needed, generate the plan in a repeating domain with numpy (as `rock.py`'s plan does: its edge difference is 0.68) and keep brush strokes out of it, or check any candidate by rolling it half its size with ImageMagick's `-roll` and looking at the middle ([ImageMagick options](https://imagemagick.org/script/command-line-options.php#roll)).
- **Stroke alphas, the other route**: Blender Studio's brush-stroke assets are GPL (recorded in [the earlier note](free-assets-for-recreation-gaps.md#7-unverified-items-and-things-wanted-but-not-found-free)); this engine is MIT and scriptable. I know of no better first-party source.
- **Judging a render against a reference**: extend `review-renders`, which already demands measurements. The look-test README found that "Checking region colours by number caught casts the eye missed"; that is a check with a number, and ImageMagick is already used for it in [style-reference-board.md](style-reference-board.md). Take from this skill only the sheet layout (value map, squint) and the blind A/B rule.
- **Painterly post-process in the game**: unchanged from the earlier note: an anisotropic Kuwahara pass as a Bevy `FullscreenMaterial` ([docs.rs](https://docs.rs/bevy/0.19.1/bevy/core_pipeline/fullscreen_material/trait.FullscreenMaterial.html)), low priority.
- **Skies and clouds**: unchanged from the earlier note: Bevy's own `FogVolume` and volumetric fog for clouds, and a backdrop colour chosen by view direction (`backdrop_haze` in pit scene 3).

---

## 9. Unverified

- **The full skill flow was not run.** No dossier, no critic subagents, no multi-round painting. Claims about what the loop achieves rest on the repository's own example images and notes.
- **`dry/` was not installed or run**, so pencil, ink, watercolour, papers, lettering and the print look are judged from source and from the example JPEGs only. Whether `dry/` output can carry alpha is unknown.
- **The npm dependency tree was not read.**
- **The owner has not looked at any trial output.** Whether the strokes and leaves suit the target look is their call.
- **How the leaf atlas and stroke alphas look in Bevy** was not tested: no GLB was built and no gate was run.
- **scipy's SPDX licence id** was not read from the metadata.
- **Whether the example pictures in `docs/examples/` were produced exactly as described** cannot be checked: the repository does not include their `paint.py` scripts.
- **Repainting a baked texture in UV space** with `paint_from_design`, to put brush strokes on an asset's own texture, is an idea from 6.6 that I did not try. Strokes would break at UV island edges.

---

## 10. What the owner has to decide

1. **Look at four files** and say whether any of it is the look: `kiln-trial/out/ls_s5/stroke_alphas.png`, `kiln-trial/out/ls_s5/leaf_atlas_on_magenta.png`, `kiln-trial/out/sky_s11/sky_flat_review.png`, `kiln-trial/out/repaint_scene7/render_vs_repaint.png`. If the strokes and leaves are not close, the answer becomes "skip" and nothing below matters.
2. **If yes: pin or copy?** Pin the repository at commit `1af61f3` as a download under `.tools/`, the way ADR 0009 treats Sapling Tree Gen, and keep a generator script of ours that writes the atlases. Or copy the engine modules we use into the repo with the MIT notice. Pinning is less to own; copying survives the repository vanishing, which a five-day-old single-author project might.
3. **Who owns the missing parts?** Alpha, atlas layout, and any wrap-around are ours to write and to gate (alpha present, cell borders empty, size a power of two, same seed gives the same file). The numbers in section 6 are the start of those checks.
4. **Whether to spend one full run of the real skill** (about 90 minutes and 400k tokens) on a single backdrop or concept image in a scratch folder, to settle the two "unproven" rows in section 7. I would not until item 1 is answered.
5. **Whether to copy the critique instruments** (value map, squint, blind A/B with a hidden key) into `review-renders` or `asset-review`. That needs no code from this repository.

## 11. Sources

- Repository: <https://github.com/bosphorify/claude-painting-skill> at `1af61f3b0aebe1a69b412fbfb213a281688afaa6` **[raw]**
- GitHub API, 2026-10-04: `repos/bosphorify/claude-painting-skill`, its `contributors`, `issues`, `pulls`; `orgs/bosphorify`; `users/bosphorify/repos`; `repos/rvanwijnen/spectral.js` **[raw]**
- npm registry metadata for `p5`, `p5.brush`, `playwright-core` through `npm view` **[raw]**
- spectral.js: <https://github.com/rvanwijnen/spectral.js>
- p5.brush: <https://github.com/acamposuribe/p5.brush>
- Hertzmann, "Painterly Rendering with Curved Brush Strokes of Multiple Sizes", SIGGRAPH 1998, as cited in the skill's README and `design.py`; the paper itself was not fetched.
- This project: `CONTEXT.md`, `docs/adr/0009-painted-soft-edged-style.md`, `docs/research/free-assets-for-recreation-gaps.md`, `.claude/skills/review-renders/SKILL.md`, and pit's `look-tests/README.md`.
