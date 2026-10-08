# A trial of Tripo's API against the videos' claims: prepared, not run

Prepared 2026-10-08 on the development machine. **No model was generated.** The API key on this machine has a balance of 0 credits, so the paid part of the trial did not start. What exists is the plan, the reference images, the measuring scripts (each proven on a file whose answer is known), the exact request bodies, and a record of what Tripo's CLI and API answer at a zero balance.

This is a research note. It sets up a measurement of the claims collected in [`videos-and-workspace-review.md`](videos-and-workspace-review.md) and reports the little that could be measured without credits. It does not choose a generator. It does not draw on the `first-attempt` tag beyond rendering pictures of the two specimens in `learn/specimens/`. Everything it produced is in [`tripo-api-trial/`](tripo-api-trial/).

## The question

Which claims in the six videos can be checked by calling Tripo's API from this machine, what does each check cost, and what do the checks show?

The third part has no answer yet. The first two do.

## How to read this

- **Measured** means it was run on this machine on 2026-10-08 and the output is in [`tripo-api-trial/`](tripo-api-trial/). Almost everything measured here is about Tripo's CLI and about kiln's own tools, not about a generated model.
- **Docs** means Tripo's API documentation ([full text](https://developers.tripo3d.com/llms-full.txt)), its [pricing page](https://developers.tripo3d.com/en/pricing), or the documentation bundled in the CLI (`tripo docs`), all read today.
- **Video** means what the creator said or showed, as recorded in the videos note. No video was opened again for this note.
- **Planned** means a request that is written down and checked by the CLI's dry run but was not sent.
- **Inference** means this note's reasoning.
- **Arithmetic** means a cost worked out from listed prices. No charge was observed, because nothing was charged.
- **One generation is an observation, not a rate.** The plan makes one model per condition. Whatever it shows when it runs will be true of that model. It will not say how often Tripo does the same.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, review pictures, store) are used as `CONTEXT.md` defines them.

### Terms used here

The earlier notes define mesh, triangle, quad, UV, UV island, PBR, base colour, normal map, roughness, decimation, retopology, credit, CLI and headless. Terms added or used heavily here:

- **Dry run:** asking the CLI to print the request it would send, without sending it.
- **Request body:** the JSON a program sends to the API. It is the exact record of what was asked for.
- **Seed:** a number that fixes the random choices a generator makes. Tripo has one for the shape (`model_seed`) and one for the texture (`texture_seed`).
- **Welded:** a mesh after every pair of points at the same position has been joined into one. A `.glb` stores a point again wherever its normal or UV changes, so defects are counted on the welded mesh.
- **Boundary edge:** an edge with a face on one side only. A ring of them is the rim of a hole or of an open sheet.
- **Non-manifold edge:** an edge shared by three or more faces. A surface that could be made of paper never has one.
- **Loose part:** a group of faces not connected to the rest of the mesh.
- **Degenerate face:** a face with no area, such as a triangle whose three corners lie on one line.
- **Delight:** Tripo's name for removing shadows and highlights from the reference image before making the texture.
- **Wallet:** the balance of credits a key can spend. Tripo's web app and its API may keep separate ones; whether they do was not established.

## Summary

### What was run, and what it cost

- **Phase B, the paid run, did not happen.** `tripo balance` returned `{"balance":0,"frozen":0}` before the preparation and again after it. **Credits spent: 0. Balance before: 0. Balance after: 0.**
- **One real task-creation request was sent, to record the answer at a zero balance.** A text-to-image request (5 credits by the pricing page; nothing paid is cheaper) straight to the API returned HTTP 403 with code 2010, "You don't have enough credit to create this task" and the suggestion "Please purchase more credit". No task was created and nothing was charged (section 4).
- **The CLI never sends a paid request at a zero balance.** It reads the balance first and stops with exit code 4 (measured, and read in its source).
- **`tripo usage` is empty.** This key has never run a task.

### What the preparation showed

Five things were learned for free. Each is about the tools, not about Tripo's models.

- **The CLI's dry run does not check parameters against the API.** It printed `"valid": true` for a made-up parameter (`smart_uv=true`) and for a list given as `face_limit`. A valid dry run shows what would be sent. It does not show that Tripo would accept it (section 4).
- **The CLI's dry run gives no cost.** `cost_notes` was empty for a request that the price list puts at 110 credits.
- **CLI 0.5.2 refuses the newest texture model on its texture step.** `texture:model=v3.5-20260815` fails locally with "texture model must be one of v3.0-20250812/v2.5-20250123". The same value passes through untouched as `texture_version` on a generation. So the cheapest way to test `delight` (texture an existing shape again, 10 credits) has to go round the CLI, by HTTP (section 4).
- **Without `--model`, a request for 20,000 faces goes to P1.** The dry run's reason: "face budget 20000 ≤ 20000 → P1". The pit profile's placeholder budget sits exactly on the CLI's switch point, so kiln must always name the model (section 5).
- **Neither Smart UV nor the four-polygon-count picker is in the API or the CLI.** Confirmed again today in the documentation's full text and in the CLI's help and bundled pages. The CLI's `-n 4` plans four separate tasks from one request body; it is not four polygon counts for one price (section 1).

### What the trial needs

- **Credits in the API wallet.** 290 runs the whole plan; 190 runs the three most informative requests. Where the owner's expected free credits are is not known (section 7).
- **A decision on the reference image.** The prepared pictures are renders of the repo's own crate. That is an easy case, and the crate looks the same from every side, so it cannot show which way Tripo turns a model (section 3).

## 1. The claims, and which can be tested through the API

"Where" gives the section of the videos note. "Request" is the planned request that answers it (section 2).

### Testable through the API

| # | Claim or question | Who says it | What would be generated and measured | Request |
|---|---|---|---|---|
| A | P2 asked for a polygon count returns a model at that count | Videos 1, 6, 7 show a slider and a face count per part (sections 1, 6, 7). Docs: `face_limit` is the "maximum polycount"; Tripo's skill text says it "does hold as an upper bound" | One P2 model at `face_limit=20000`. Triangles counted by `kiln.measure` | r1 |
| B | That model is usable as it comes: "game ready" | Video 7 (asserted) | The same model: defects counted in Blender, the glTF validator, kiln's two checks, review pictures at 0.5 m, a wireframe picture | r1 |
| C | What a raw output holds: meshes, materials, which PBR maps, texture sizes and formats, UV islands, normals | Not in any video. Docs: four PBR maps, texture size unstated. The earlier notes list it as unknown | The same model and the two cheaper ones, read with `glb_inspect.py` and `kiln.measure` | r1, r2, r3 |
| D | P2 texturing "requires two step" | Video 4. Docs disagree: `texture` defaults to true in one task | Whether r1's file has textures | r1 |
| E | Low-poly straight from P2 is better than a dense model reduced afterwards | Video 4, asserted; he names Tripo's own retopology and Hunyuan's (section 4) | r1 against the H series model on defaults reduced to 20,000 triangles by Blender's Decimate. Same counts, same pictures | r1, r2 |
| F | P1 does "smart low poly" with "really logical" mesh | Video 5 (section 5). Docs: "Strict 50-20,000 face limit control" | One P1 model at `face_limit=20000`, measured as r1 | r3 |
| G | The same seed gives the same model | Not in any video (their method is the opposite: make four, keep one). Docs: "Using the same seed with the same input will produce an identical 3D mesh" | r3 sent twice. Files compared by checksum, then by vertex positions and by stored images | r3, r4 |
| H | A strict front picture is better than a three-quarter one, also for single objects | The repository's prompt files (section 3). Tripo's guidance gives no angle | One model from each picture of the same crate, same model and seeds. Proportions against the true 1 : 1 : 1, whether the model comes out square to the axes, defects, pictures | r2, r5 |
| I | `delight` removes lighting baked into the picture | Not in any video. Docs: only texture model v3.5 reads it | One shape textured twice from a picture with a hard shadow, `delight` on and off. Brightness figures of the two base colour textures, and looking at them | r6a, r6b |
| J | Defects remain on P2: holes, stray flat pieces, stray small UV islands | Videos 4 and 7 admit them (sections 4, 7) | Counted on every model: boundary edges and rings, loose parts, UV islands | all |
| K | Orientation, up axis and size as delivered | Never mentioned in any video. Docs: faces +X, Y-up, size arbitrary unless `auto_size` | Bounding box and node transforms as stored and as Blender imports them. Limited by the crate (section 3) | all |
| L | Generation "takes like 5 to 7 seconds" | Video 7, of the web app. Docs: P1 about 10 s without texture, 60 s with | The start and finish times of each request, a by-product | all |
| M | A P2 generation costs 100 credits, or 65 | Videos 1, 4, 6, 7, of the web app. Docs: 110 through the API with standard texture | The fall in the balance across r1 | r1 |

### Testable, but cut from the budget

| Claim | Why it is cut |
|---|---|
| P2 makes clean quads (videos 1, 7) | `quad=true` forces FBX. Kiln reads `.glb` only, so the file would be measured in Blender alone. One more P2 generation, 110 credits plus an unstated quad surcharge |
| Picking the best of four polygon counts by wireframe (videos 1, 6, 7) | Through the API it is four separate generations: 440 credits |
| Generating in parts beats generating whole (videos 1, 4, 5, 6, 7) | One generation per part, and the parts are then assembled by hand in Blender, which kiln does not do. A crate is one part |
| Surface detail drawn flat gives a lighter mesh than detail drawn raised (video 1) | Needs two pictures of an object with fine relief, and two generations. No such picture exists in the repo |
| Whether the same seed holds on P2 itself | 110 more credits. The plan tests it on P1 |
| Multiview against one picture; `smart_low_poly`; Tripo's own reduce step | From the earlier notes' lists, not from the videos |

### Not testable through the API

| Claim | Why not |
|---|---|
| Smart UV unwraps in seconds with seams where an artist would put them (videos 1, 6, 7) | No endpoint. Searched today: the documentation's full text has no "Smart UV" and uses "unwrap" only to describe `export_uv`; the CLI's help, `tripo docs --llm`, and its `commands/generate`, `commands/make` and `commands/process` pages have no "Smart UV" and mention unwrapping once, also for `export_uv`; nothing in the installed package's code matches either. The CLI's dry run will pass `smart_uv=true` along, but it passes any name along (section 4) |
| Four models at four polygon counts for the price of one (videos 1, 6, 7) | No parameter takes several counts. `-n 4` in the CLI plans four tasks: the dry run shows `"candidates":4` over one request body with one `face_limit` |
| Smart UV is far better than Hunyuan's (video 7) | No Smart UV, and Hunyuan is another service |
| The web app's price of 65 or 100 credits (videos 1, 4) | The trial would measure an API charge. Whether a web app credit is the same thing was not established |
| An LLM makes normal and roughness maps from the colour texture (video 1) | Not a Tripo feature. What the trial can show is whether a raw output already carries those maps (question C) |
| Everything about rigging, animation, cloth, effects and engines | Outside kiln |

What the API can still show about UVs: the layout Tripo gives by default (`export_uv=true`). `kiln.measure` counts its islands, seam edges and coverage. Video 4 implies that layout was in very many small islands before Smart UV existed; the count on r1 to r3 would say whether that holds for these models.

## 2. The plan and the budget

### Prices used

Arithmetic from the [pricing page](https://developers.tripo3d.com/en/pricing) (H series tab, read today as plain text) and the documentation's changelog. The pricing page's P series tab is drawn in the browser and could not be read; P1 prices are carried from the earlier note.

| Request | Credits |
|---|---|
| Image to 3D, H series, standard texture | 30 |
| Image to 3D, P1, standard texture | 50 |
| Image to 3D, P2, standard texture | 110 |
| Texture an existing model again, standard | 10 |
| Text to image, `seedream_v4` | 5 |

### The ranked list

Most informative first. Every request uses the same seeds (`model_seed=1`, `texture_seed=1`) and states `texture=true`, `pbr=true`, `texture_quality=standard` in the request instead of leaning on defaults.

| Order | Name | Model | Reference image | Asks | Credits | Total | Answers |
|---|---|---|---|---|---|---|---|
| 1 | `r1_p2_three_quarter` | `P2-20260801` | Crate, three-quarter | `face_limit=20000` | 110 | 110 | A, B, C, D, J, K, L, M, and half of E |
| 2 | `r2_h31_three_quarter` | `v3.1-20260211` | Crate, three-quarter | Defaults | 30 | 140 | C, J, K, the other half of E, the base for H and I |
| 3 | `r3_p1_three_quarter` | `P1-20260311` | Crate, three-quarter | `face_limit=20000` | 50 | 190 | F, C, J |
| 4 | `r4_p1_three_quarter_repeat` | `P1-20260311` | Crate, three-quarter | r3 unchanged | 50 | 240 | G |
| 5 | `r5_h31_front` | `v3.1-20260211` | Crate, strict front | Defaults | 30 | 270 | H |
| 6a | `r6_retexture_delight_true` | Texture `v3.5-20260815` | Crate, hard light | r2's shape, `delight=true` | 10 | 280 | I |
| 6b | `r6_retexture_delight_false` | Texture `v3.5-20260815` | Crate, hard light | r2's shape, `delight=false` | 10 | 290 | I |

**290 credits, 10 spare.** The same list is in [`tripo-api-trial/plan.csv`](tripo-api-trial/plan.csv) and, as commands, in [`tripo-api-trial/scripts/run_all.sh`](tripo-api-trial/scripts/run_all.sh).

Why this order:

- **r1 first** because the videos are about P2, and one P2 file answers the most questions at once. It is also more than a third of the budget.
- **r2 second** because it is the cheapest generation, it is the dense starting point the videos argue against, and two later requests build on it.
- **r3 before the repeat** because P1 at 50 credits may do for a prop what P2 does at 110, and that is worth more than repeatability.
- **The repeat on P1, not P2.** A second P2 would cost 110. The documentation's sentence about seeds is the same for every model, so P1 tests the sentence. It does not test whether P2, a preview, keeps to it.
- **`delight` last** because it rests on a script that goes round the CLI and has never met the API (section 3).

### If there are fewer credits

- **200** (the web app's free monthly amount, by an earlier note): r1, r2, r3. 190 credits.
- **110 to 139:** r1 alone.
- **30 to 109:** r2 alone. It says what an H series raw output holds. It says nothing about P2.

### Where a cheaper model does not test the video's claim

- r3 (P1) answers video 5's remark about P1. It is not evidence about P2.
- r2 and r5 use the H series for the camera-angle question. The repository's rule is written for image-to-3D generators in general, so the H series is a fair test of the rule. It would not show whether P2 reacts to the angle the same way.
- r2 reduced in Blender is **a weaker rival than the video named.** The creator compared P2 with retopology tools (Tripo's own, Hunyuan's). Blender's Decimate is the plainest reduction there is. If P2 beats it, that supports the claim only against plain decimation.

## 3. Method

### Reference images

**What the repo has.** `learn/specimens/crate.glb` (108 triangles, two plain-coloured materials, no textures) and `learn/specimens/boulder_1.glb` (136 triangles, one 512 × 512 texture). Both were made by the first attempt's own scripts and exported from Blender, so pictures of them are the owner's own work and are fine to upload to a service that may make uploads public. There is no `assets/` store yet and no `reference_image.*` anywhere. `benchmarks/` holds a third-party pack and was not touched.

**What was made.** [`scripts/render_reference.py`](tripo-api-trial/scripts/render_reference.py), run through `tools/bl`, renders three pictures of a model. All are 2048 × 2048 PNG, on pure white, with the object spanning 78% of the frame in its wider direction, by Cycles on the CPU with a fixed seed.

| File | Camera | Light | Use |
|---|---|---|---|
| `images/crate_three_quarter.png` | Perspective, 100 mm lens (so perspective is mild), 35° round and 20° up | Even: a white sky and a weak wide sun | The main picture: r1 to r4 |
| `images/crate_front.png` | Orthographic, straight on, at mid height | The same | r5: the repository's "strict front" rule |
| `images/crate_three_quarter_hard_light.png` | As the first | One hard sun, a white ground that takes a shadow (the shadow runs off the right edge of the picture) | r6: deliberately breaks "even light, no shadow" |

The same three were rendered for the boulder, as spares. Checksums are in [`images/SHA256SUMS`](tripo-api-trial/images/SHA256SUMS), and [`images/contact_sheet.png`](tripo-api-trial/images/contact_sheet.png) shows all six small, side by side.

**Against the earlier note's checklist** (its section 3), for the main picture:

| Item | Met? |
|---|---|
| One object | Yes |
| Fills 70 to 85% of the frame, centred | Yes: the crate spans 78% of the frame |
| Plain white background | Yes |
| Even, soft light, no cast shadow | Yes; the faces differ slightly in brightness so they can be told apart |
| At least 1024 × 1024, PNG, under 20 MB | Yes: 2048 × 2048, about 3 MB |
| Nothing hidden | Three of six faces are seen; the other three are guessed, as with any single picture |
| No glass or chrome | Yes |

**Why a crate.** It is a static prop of the kind the pit game is full of, it has flat sides and sharp edges (which generators tend to round), and its panels are set back from its frame, so the result shows whether small relief becomes geometry or texture.

**What is wrong with it, plainly.**

- **A render of a 3D model is an easy case.** It has clean edges, no noise, no lens, and exactly the light the checklist asks for. A drawn or photographed reference would be harder. A good result here would not carry over.
- **The crate is the same on all six sides.** So the trial can measure whether a model comes out square to the axes, where its lowest point is and how big it is. It **cannot** say which side Tripo treats as the front. The boulder (1.2 × 0.7 × 1.0 m, different in every direction) could; no credits are budgeted for it.
- **The strict front picture of this crate is a square inside a square.** It carries no depth at all. That makes r5 an extreme test of the front-view rule, not a typical one.
- **It has no fine detail,** so nothing here tests "flat against raised".

**The alternative, if the owner prefers.** Tripo's own text-to-image step would make a less easy picture for 5 credits (`seedream_v4`), inside the 10 spare. A prompt is on record in [`requests/zero-balance/http.request.json`](tripo-api-trial/requests/zero-balance/http.request.json) (a barrel with iron hoops, three-quarter view, white background, even light). A generated picture would have to be looked at against the checklist before use, and its licence on a free plan is as uncertain as a model's.

### The requests

Each planned request was run with `--dry-run --json`, and the command, the printed plan and anything on the error channel are in [`tripo-api-trial/requests/dry-run/`](tripo-api-trial/requests/dry-run/). The body for r1, as the CLI would send it:

```json
{"input": "<upload:images/crate_three_quarter.png>", "model": "P2-20260801", "face_limit": 20000,
 "texture": true, "pbr": true, "texture_quality": "standard", "texture_seed": 1, "model_seed": 1}
```

r2 and r5 are the same without `face_limit` and with `"model": "v3.1-20260211"`. r3 and r4 are r1 with `"model": "P1-20260311"`. All five went to `POST /v3/generation/image-to-model` and came back `"valid": true` with no warnings.

r6 cannot be planned by the CLI (section 4). Its body is written by [`scripts/retexture_v35.sh`](tripo-api-trial/scripts/retexture_v35.sh) for `POST /v3/models/texture`: r2's task as `input`, `"model": "v3.5-20260815"`, the hard-light picture as `texture_prompt.image`, `delight` true or false, `texture_seed` 1. **That script has not been tested against the API**; the field names are from the reference page.

Settings left at Tripo's defaults on purpose, so the raw output is seen as it comes: `auto_size` (off), `export_orientation` (`+x`), `orientation`, `texture_alignment`, `export_uv` (on), `quad` (off), and the texture model on r1 to r5 (`v3.0-20250812`, which ignores `delight`).

### The guards on spending

[`scripts/run_request.sh`](tripo-api-trial/scripts/run_request.sh) wraps every paid CLI request. It reads the balance before and after, appends a row to `ledger.csv`, and refuses to start when the balance is below the expected cost, when credits are frozen, when the trial's total would pass 300, or when an earlier request ended with an unexpected charge or an error (it then leaves a `STOP` file for a person to remove). It blanks anything shaped like an API key in what it saves. **Measured:** at a balance of 0 it refused r1 with exit 4 and wrote nothing but the ledger's header. Its paths after a successful request have not been exercised.

### Measuring a model

[`scripts/measure_model.sh`](tripo-api-trial/scripts/measure_model.sh) runs everything on one file and writes into `measurements/<name>/`.

| What | Tool | Gives |
|---|---|---|
| Identity | `sha256sum` | The checksum and size |
| Contents | `learn/assets/glb_inspect.py` | Meshes, primitives, attributes, materials |
| Counts, box, textures, UVs, texel density, validity | `python3 -m kiln.measure --size 0.8 --json` | Triangles, vertices, bounding box, each image's pixel size and format, which material slot uses it, UV islands, seam and open edges, coverage, pixels per metre at the crate's 0.8 m, the Khronos validator's result |
| Defects | [`scripts/mesh_defects.py`](tripo-api-trial/scripts/mesh_defects.py) in Blender | As imported and welded: boundary edges and rings, non-manifold edges, loose parts and their sizes, degenerate faces, zero-length edges, faces wound the wrong way, faces of 3, 4 and more sides, node rotations and scales, the bounding box in Blender's axes and turned back to glTF's |
| Polygon layout | [`scripts/render_untextured.py`](tripo-api-trial/scripts/render_untextured.py) in Blender | Two grey pictures with every edge drawn, front three-quarter and back |
| Looks | `target/release/review_pictures --size 0.8 --closest 0.5` | Kiln's eight review pictures, one from the pit profile's closest viewing distance |

Three more scripts answer single questions: [`compare_models.py`](tripo-api-trial/scripts/compare_models.py) (same bytes, same geometry, same images: for the seed repeat), [`texture_stats.py`](tripo-api-trial/scripts/texture_stats.py) (brightness figures of each stored image and a PNG copy: for `delight`), and [`reduce_in_blender.py`](tripo-api-trial/scripts/reduce_in_blender.py) (Decimate to a triangle count: for the dense route).

**Each was run before any credit could be spent** (measured):

- `mesh_defects.py` on a file built to be broken ([`make_broken_fixture.py`](tripo-api-trial/scripts/make_broken_fixture.py): a cube with one face missing, a fin on one edge, a floating triangle and a triangle with no area). Expected after welding: 13 triangles, 3 parts, 1 non-manifold edge, 1 degenerate face, 12 boundary edges in 4 rings. It reported exactly that ([`tooling-proof/broken.defects.json`](tripo-api-trial/tooling-proof/broken.defects.json)). As imported, before welding, the same file shows 29 boundary edges and 8 parts, which is why the welded figures are the ones to read.
- On the two specimens it found no defects, and its welded edge count for the boulder (204) equals `kiln.measure`'s.
- `measure_model.sh` ran end to end on the boulder: all eight review pictures and both wireframe pictures were written. `target/release/review_pictures` is built on this machine.
- `compare_models.py` reported the boulder identical to itself and different from a reduced copy. `reduce_in_blender.py` took the boulder from 136 triangles to 60 when asked for 60.

What these tools do not measure: whether a model looks like its reference image (a person does that at the shape review), UV stretch, the quality of a normal map, or how a quad mesh deforms.

### Versions

| | |
|---|---|
| `tripo-cli` | 0.5.2, on Node.js 26.7.0 |
| API | `https://openapi.tripo3d.ai/v3` (the CLI reports region `ov`) |
| Blender | 5.2.2 LTS, through `tools/bl` |
| Khronos glTF Validator | 2.0.0-dev.3.10 |
| `review_pictures` | 0.1.0, Bevy 0.19.1, on an RTX 3080 |
| Python | 3.14.7, standard library only |
| Kiln | commit `a24508e` |

## 4. Results

### What was measured without credits

**The balance.** `tripo balance`: `{"balance":0,"frozen":0}` at the start and at the end. `tripo usage`: `[]`. `tripo doctor`: key read from the environment, API reachable, "0 credits (0 frozen)".

**The CLI at a zero balance.** A text-to-image request through the CLI ended with exit code 4 and this on standard output:

```json
{"error":"Insufficient credits","exit_code":4,"api_code":2010,"suggestion":"run \"tripo topup\" to add credits"}
```

Its source (`dist/core/task-service.js`) shows why: it reads the balance before submitting and raises 2010 itself when the balance is 0 or less. It also warns, without stopping, when the balance is under 30. So the code 2010 above is the CLI's own; the request never reached task creation.

**The API at a zero balance.** One request was therefore sent straight to `POST /v3/generation/text-to-image` (2026-10-08 16:31:40 GMT), with a prompt and `"model": "seedream_v4"`:

```
HTTP 403
{"code":2010,"status":"error","message":"You don't have enough credit to create this task",
 "suggestion":"Please purchase more credit","request_id":"0dd327fd-…"}
```

No task was created. The balance stayed 0 with nothing frozen. The files are in [`requests/zero-balance/`](tripo-api-trial/requests/zero-balance/). The documentation's error page gives the same code and the same HTTP status, with different words ("Insufficient credits", "Please top up your account"). No further paid request was attempted.

**The CLI's dry run.** Eleven extra dry runs probed what the CLI checks ([`requests/dry-run/probe_*`](tripo-api-trial/requests/dry-run/)):

| Asked | The CLI answered | Agrees with the earlier notes? |
|---|---|---|
| P2 with `quad=true` | Valid. Warning: "quad=true forces FBX output (quad topology cannot be stored in GLB)". Cost note: "quad topology: higher price tier, FBX output" | Yes |
| P1 with `quad=true` | Valid, with `quad` removed and a warning | Yes |
| P1 with `face_limit=25000` | Invalid, exit 2: "P1 face_limit must be within 50–20000" | Yes |
| `face_limit=20000` and no `--model` | Valid, model `P1-20260311`: "face budget 20000 ≤ 20000 → P1" | Yes; now seen |
| P2 with `-n 4` | Valid, `"candidates":4`, one request body | Yes: four tasks, not four counts |
| P2 with `face_limit=[5000,10000,15000,20000]` | **Valid.** The list is put in the body as it is | New |
| P2 with a made-up `smart_uv=true` | **Valid.** The name is put in the body as it is | New |
| H series with `texture_version=v3.5-20260815` and `delight=true` | Valid, passed through | As the earlier note expected |
| The texture step with `model=v3.5-20260815` | **Invalid, exit 2:** "texture model must be one of v3.0-20250812/v2.5-20250123" | New: the CLI is behind the API's changelog |
| The reduce step, `decimate:20000` | Valid | Yes |
| `--for game-mobile` | P1, `face_limit=15000`, then a convert to FBX with 2048-pixel textures | Yes |

None of these was sent. Whether the API would reject the list or the made-up name is not known. The CLI's own skill page says so in other words: "Unknown `--param key=value` pairs pass through to the API".

### The claims

Verdicts are one of: supported, contradicted, not tested, inconclusive. "Would count as" is fixed now, before any result exists.

| # | Claim | What the video or the docs said | What was measured | Verdict | Would count as support / as contradiction |
|---|---|---|---|---|---|
| A | P2 returns the count asked for | Video: a count per part matching a slider. Docs: a maximum | Nothing | Not tested | Support: 18,000 to 20,000 triangles. Over 20,000 contradicts the docs. Well under 18,000 means a ceiling, not a target |
| B | The result is usable as it comes | Video 7: "game ready" | Nothing | Not tested | Support: no validator errors, and on the welded mesh no non-manifold edges, no degenerate faces, no boundary edges, no loose part under 1% of the triangles, and nothing wrong in the 0.5 m picture. Any of those present contradicts it for this one model |
| C | What a raw output holds | Docs: four PBR maps; sizes unstated | Nothing | Not tested | A description, not a verdict |
| D | P2 texturing needs a second step | Video 4: yes. Docs: no | Nothing | Not tested | Contradicted through the API if r1's file has textures |
| E | P2 low-poly beats dense then reduced | Video 4, asserted | Nothing | Not tested | Support against plain decimation only: r1 has fewer defects than r2 reduced and looks no worse at 0.5 m |
| F | P1 gives a logical low-poly mesh | Video 5 | Nothing | Not tested | As B, plus the wireframe picture |
| G | Same seed, same model | Docs: "identical 3D mesh" | Nothing | Not tested | Support: the same vertex positions and triangles to the last bit. Different positions contradict the sentence |
| H | Strict front beats three-quarter | Repository prompts | Nothing | Not tested | Support: r5's proportions are nearer 1 : 1 : 1 than r2's and its defects no worse. One crate cannot settle it either way |
| I | `delight` removes baked lighting | Docs | Nothing | Not tested | Support: with `delight` on, the base colour has a narrower spread of brightness and the shaded side is no darker than the lit side |
| J | Defects remain on P2 | Videos 4, 7 admit them | Nothing | Not tested | Counts, per model |
| K | Orientation and size as delivered | Docs: +X forward, Y-up, size arbitrary | Nothing | Not tested | A description; front cannot be told on this crate |
| L | Generation takes 5 to 7 seconds | Video 7, web app | Nothing | Not tested | The request's wall-clock time, which includes upload, queue and download |
| M | A P2 generation costs 100 or 65 credits | Videos 1, 4, web app. Docs: 110 by API | Nothing | Not tested | The fall in the balance |
| N | Smart UV is available | Videos 1, 6, 7: in the web app | Docs and CLI searched: absent | **Not reachable through the API as documented** (measured on the documentation, not on the service) | |
| O | Four polygon counts for one price | Videos 1, 6, 7: in the web app | Docs: no such parameter. CLI: `-n 4` is four tasks | **Not reachable through the API as documented** | |
| P | P2.0 is "officially released" | Video 7 | Docs today: `P2-20260801`, "Preview". CLI 0.5.2: "Preview", never chosen by itself | **Contradicted for the API, by the documentation.** The web app was not looked at | |
| Q | `quad` output is a `.glb` like any other | Implied by nothing; an earlier note records the docs | CLI dry run: forces FBX | Docs **supported** by the CLI's own check | |

## 5. Checks against `profiles/pit.toml`

The profile holds two numbers, both marked as placeholders: `triangle_budget = 20000` and `closest_viewing_distance = 0.5`. Kiln's checks today are two: no validator errors, and triangles at or under the budget (`kiln/checks.py`).

- **No model exists to check.**
- **The plan is built on both numbers.** `face_limit=20000` on r1 and r3; the Blender reduction of r2 aims at 20,000; the review pictures are taken with `--closest 0.5`.
- **20,000 is the top of P1's range and the CLI's switch point** (measured in the dry run). One triangle more and P1 refuses the request; without `--model` the CLI picks P1 at 20,000 (measured) and, by its documentation, the H series above that. If issue #11 moves the budget, the same command would silently go to a different generator unless kiln names the model.
- **The measured budget is not this placeholder.** [`pit-budget-measurement.md`](pit-budget-measurement.md) estimates 10,000 triangles per asset. If that becomes the profile's number, r1 and r3 should ask for 10,000 instead; the cost is the same.
- **A generated model can be put through kiln's own run without touching the real store:** `python3 -m kiln run --model <file.glb> --size 0.8 --profile pit --licence "Tripo free credits: measurement specimen, no rights" --source "Tripo API trial <task id>" --store <a temporary folder>`. It must never go into `assets/`.

## 6. Corrections to earlier notes

Nothing in the other notes was edited. These are the points this trial's preparation changes or sharpens.

| Note | It says | What was found |
|---|---|---|
| `tripo-guidance-and-blender-scripting.md`, section 5, "What the CLI exposes" | `texture_version` and `delight` "would still pass through with `-p`" | True on a generation (measured in the dry run). **Not true on the texture step:** CLI 0.5.2 rejects `model=v3.5-20260815` there before sending anything |
| The same note, section 18, experiment 7 | Testing `delight` takes two generations, 60 credits | By the pricing page it can be two texture tasks on one existing shape, 20 credits. That route needs HTTP, not the CLI |
| The same note, section 18, experiment 1; `claude-tripo-blender-workflows.md`, section 13, experiment 1 | A dry run "would show the chosen model, every request body" and which parameters are stripped | It does. It should not be read as a check of the request: made-up parameters and wrong value types come back `"valid": true`. It also gives no cost |
| `claude-tripo-blender-workflows.md`, section 1 | "The CLI checks the balance first" | Confirmed, and stronger: at a balance of 0 it never sends the paid request. Exit code 4, as that note lists |
| `claude-tripo-blender-workflows.md`, section 1, Setup | "New accounts receive free credits" (docs) | This key's API balance is 0 and its usage is empty. Whether credits were never granted, were granted to a different wallet, or need claiming is not known |
| `videos-and-workspace-review.md`, section 8 | Smart UV and multi-count generation are "not in the API as documented" | Re-checked today, and in the CLI as well. Still absent |
| The same note, section 8 | P2 "still lists ... as Preview" | Still so today, in the documentation and in the CLI's model table |
| `llm-vs-3d-generators.md`, comparison table | Tripo, "Free plan through the API: Not stated" | Still not stated. One data point now exists: a key with a zero balance gets HTTP 403, code 2010 |
| All of them | API examples use `openapi.tripo3d.com` | The CLI sends this key's requests to `openapi.tripo3d.ai`. Both names are Tripo's; the earlier note already recorded that the CLI picks by key |

## 7. What is still unknown, and what the next credits should buy

**Unknown, and blocking.**

1. **Where the free credits are.** The API wallet of this key holds none. Three possibilities, none checked: the free credits belong to the web app (Tripo Studio) and cannot be spent through the API; the API console grants its own and they have not been claimed; or this key belongs to a different account from the one the owner signed up with. Looking at the billing page of the API console in a browser would settle it. `tripo topup` opens that page; it was not run, because it leads to a purchase screen.
2. **Whether free credits can create API tasks at all.** Not stated anywhere read.

**Unknown, and the reason for the trial.** Every row of section 4's table marked "not tested".

**What the first credits should buy, in order.**

1. **r1**, 110 credits. One P2 file answers claims A, B, C, D, J, K, L and M for one prop.
2. **r2**, 30 credits, and its free reduction in Blender. With r1 it gives the first look at claim E.
3. **r3**, 50 credits.
4. Then r4, r5 and r6 as the plan has them.

**What would make the trial better than planned.**

- **A harder reference image with a clear front and top.** One text-to-image request (5 credits) or a picture the owner supplies. It would let orientation be measured and would make every result less of a best case.
- **A second prop.** Every verdict above would rest on one crate.
- **P2 with quads**, once kiln has a way to read FBX or a convert step is chosen. About 115 credits.
- **The pit profile's real triangle budget.** The plan uses the placeholder.

**The licence stays as the earlier notes left it.** Models made on free credits are measurement specimens. By Tripo's terms as those notes read them, free users get no rights in outputs, and uploads and results may be public. Nothing private or third-party was prepared for upload.

## 8. How to run it again

From the repo root, with `TRIPO_API_KEY` set and `tripo` 0.5.2 on the path:

```
tripo balance
cd learn/research/tripo-api-trial
scripts/run_all.sh
```

- `run_all.sh` sends the requests in the plan's order and stops at the first refusal. To send only some, copy single lines from it. `TRIAL_LIMIT=200 scripts/run_all.sh` lowers the cap.
- Models, `preview.png` and `task.json` land in `models/<name>/`. That folder's `.gitignore` keeps `.glb` and `.fbx` files out of git. The CLI's answer, the command and a copy of `task.json` land in `requests/`; the balance before and after each request lands in `ledger.csv`.
- Then, for each model: `scripts/measure_model.sh <name> models/<name>/<file>.glb 0.8`. The comment at the foot of `run_all.sh` lists the reduce, compare and texture commands.
- To make the reference images again: `tools/bl learn/research/tripo-api-trial/scripts/render_reference.py learn/specimens/crate.glb learn/research/tripo-api-trial/images 2048`. It does not give the same bytes twice: two renders of the front picture on this machine had the same size and different checksums (probably the date Blender writes into a PNG; the pixels were not compared). The checksums in `images/SHA256SUMS` are of the files kept here, which are the ones to upload.
- To prove the defect counter again: `tools/bl .../scripts/make_broken_fixture.py /tmp/broken.glb`, then `tools/bl .../scripts/mesh_defects.py /tmp/broken.glb`, and compare with the numbers in the fixture's first comment.
- Result links expire within minutes by Tripo's documentation. The CLI downloads at once; do not use `--no-download`.

## What could not be done or verified

- **Every measurement of a generated model.** No model exists.
- **`run_request.sh` after a successful request, and the whole of `retexture_v35.sh` and `run_all.sh`.** Only the refusal at a zero balance ran. The name of the field `tripo files upload --json` returns (`file_token`) and the shape of `texture_prompt.image` are from the documentation, not from a response.
- **Whether the API rejects unknown parameters.** The CLI passes them; nothing was sent.
- **P series prices on the pricing page.** The tab is drawn in the browser. P1's 50 and P2's 110 are from the earlier note and the changelog. The surcharge for `quad` on P2 is not stated; the CLI says only "higher price tier".
- **Whether `/v3/models/texture` keeps a task's original reference image when none is given.** The reference page "strongly" recommends supplying it again; the plan supplies one.
- **Whether a web app credit and an API credit are the same thing, and where the owner's free credits are.**
- **Tripo's terms of service.** Not re-read today; the licence statements are the earlier notes'.
- **The provenance of the two specimens beyond the git history.** `crate.glb` entered the repo in commit `279fbef` ("Add the crate prop") as output of the first attempt's own scripts; that it has no third-party source is taken from that, not from a statement by the owner.
- **The further video note that arrived while this was being written** ([`video-local-trellis2-pixal3d-watertight-low-poly.md`](video-local-trellis2-pixal3d-watertight-low-poly.md)) was read at its headings and summary only. It is about generators run locally and adds no claim about Tripo's API. One of its points is already built into the method here: defects are counted after welding.

## Sources

Every item was read on 2026-10-08.

**Tripo, first party**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt): the changelog, the P series image-to-model page, the texture page, the text-to-image page, billing and error handling. Searched for "Smart UV" and "unwrap".
- [API pricing](https://developers.tripo3d.com/en/pricing), as plain text; H series tab only.
- `tripo-cli` 0.5.2 as installed: `--help` for `make`, `generate`, `model`, `mesh`, `task`, `files`, `topup`; `tripo docs --llm` and the topics `commands/generate`, `commands/make`, `commands/process`, `common-errors`; and two source files, `dist/core/requests.js` and `dist/core/task-service.js`.

**Kiln**

- `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, `profiles/pit.toml`, `kiln/checks.py`, `kiln/glb.py`, `tests/cross_check/blender_figures.py`.
- [`videos-and-workspace-review.md`](videos-and-workspace-review.md) (the claims), [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md) (parameters, the checklist, the experiments), [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md) (the CLI), [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md) (prices and licence), [`pit-budget-measurement.md`](pit-budget-measurement.md) (the form of a measurement note).

## Method

The work was done on 2026-10-08 in one sitting. The notes above were read first and the claims listed from the videos note alone. Tripo's documentation was downloaded as its full-text file and searched; the pricing page was fetched and stripped to text. The CLI was asked for its help and bundled pages, and two of its source files were read to explain what it did.

The reference images were rendered from `learn/specimens/` with a script run through `tools/bl`, looked at, and rendered three times: the first set filled only about 60% of the frame, the second fixed that by moving the camera so close that the perspective was strong, and the third, kept here, uses a longer lens from further away. The measuring scripts were written in a scratch folder, run on the two specimens and on a file built with known defects, and copied into [`tripo-api-trial/scripts/`](tripo-api-trial/scripts/) once their output matched what was expected. One script (`compare_models.py`) failed on first use and was fixed.

Every planned request was run with `--dry-run --json`. The balance was read before and after. At a balance of 0, one request was made through the CLI and one straight to the API, both for the cheapest paid task; neither created a task. Nothing was bought, no plan was changed, no terms were accepted and `tripo topup` was not run. The API key was not printed or saved; saved outputs were filtered for anything shaped like a key and then searched for one.

Only this file and the folder beside it were written. Nothing was committed.
