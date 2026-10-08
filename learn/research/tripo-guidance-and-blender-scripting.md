# What Tripo says makes a good request, and what Blender's API offers the stages after it

Researched 2026-10-08. Every page, package and source file cited below was read on that date. Tripo's parameters, prices and model names change within weeks; Blender's API changes between versions. Check each again before relying on it.

This is a research note. It supplies knowledge for a design that is being considered and is not decided: Tripo makes a model from a reference image; kiln keeps the file as the raw output; a person does the shape review; fixed Blender scripts, run through `tools/bl`, make the model fit the target profile. It builds on [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md), [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md) and [`game-mesh-kiln-or-generator.md`](game-mesh-kiln-or-generator.md) (called "the earlier notes" below) and does not repeat them. It does not draw on the `first-attempt` tag.

**Almost nothing here was tested.** No generator was called and no account was created. The pinned Blender was started twice through `tools/bl`, only to print what its API holds: operator properties and defaults, which add-ons ship, what a factory-settings session contains. No operator was run on a mesh. Every statement about what a tool does to a model is from documentation, source code or someone else's report, and says which.

## The question

Two linked questions, for the two points where Claude would help the owner:

1. Before generation: what does Tripo itself say produces a good result, in the prompt, the reference image and the settings?
2. After the shape review: for each stage kiln might need, what does the pinned Blender's API offer, what would have to be chosen per asset, and what do the docs say can go wrong?

## How to read this

- **Fact** (the default) means a first-party page, a published package or a tool's own source says so.
- **Read from the binary** means the pinned Blender printed it when asked (a property name, a default, a list). It is a fact about this build, not about what the property does.
- **Source** means the statement was read in a program's code, not its documentation.
- **Vendor claim** means the vendor says so about its own quality and nobody independent has shown it.
- **Vendor blog** is an interested party. **Hands-on** is one person's report; the number of assets and whether files are shown is given. **Single report** is one issue on a tracker.
- **Inference** means the sentence is this note's reasoning from cited facts.
- **Arithmetic** means a number worked out from list prices.
- **Unverified** means no primary source could be read.
- Kiln's own words (run, size, reference image, target profile, raw output, generator, shape review, asset record, store, static asset) are used as `CONTEXT.md` defines them.

### Versions

- **Blender 5.2.2 LTS**, build date 2026-09-15, the version `tools/install_tools.sh` pins. Its bundled glTF add-on reports version 5.2.40. Every Blender fact below is for this version.
- **Bevy 0.19.1**, the version `Cargo.toml` pins.
- **Tripo API v3**, as documented on 2026-10-08. **`tripo-cli` 0.5.2**, published 2026-10-08.

### Terms used here

The earlier notes define mesh, triangle, quad, topology, UV, seam, texel density, PBR, normal map, decimation, retopology, baking, boundary edge, manifold, `bpy`, headless, seed, credit, wire value and CLI. Terms added by this note:

- **Normal:** the direction a piece of surface faces. A renderer uses it to work out how light falls. A **flipped normal** points into the object, so the face looks dark or vanishes.
- **Custom normals (custom split normals):** normals stored in the file instead of worked out from the shape. A glTF file always stores them.
- **Smooth and flat shading:** whether the normal blends across neighbouring faces (a round look) or is constant on each face (a faceted look). A **sharp edge** is an edge across which it does not blend.
- **Tangent:** a second direction stored per vertex, which a normal map needs. If a file has none, the engine computes them.
- **Origin (pivot):** the point of the model that sits at the position the game gives it. For a prop on the floor this is usually the middle of its underside.
- **Operator:** a Blender tool called from Python as `bpy.ops.<group>.<name>()`. It acts on whatever is selected or active, not on something passed to it.
- **Context:** Blender's record of what is active and selected and which editor is in use. An operator refuses to run (its **poll** fails) when the context is wrong.
- **`bmesh`:** Blender's Python module for editing a mesh directly as vertices, edges and faces, with no operator and no context.
- **Modifier:** a step attached to an object that changes its mesh when applied, such as Decimate.
- **Edit Mode, Object Mode:** two states of Blender. Mesh operators (`bpy.ops.mesh.*`) need Edit Mode.
- **Extension:** Blender's name, since version 4.2, for an add-on installed from its online repository instead of shipped in the download.
- **Principled BSDF:** Blender's standard material node. The glTF exporter reads a material's numbers and textures from it.
- **Extras:** free-form data a glTF file may carry on any object. Blender calls them custom properties.
- **Multiview:** giving a generator several pictures of the same object from set directions instead of one.
- **Delighting:** removing the light and shadow of a photograph from a colour texture.

## Summary

### Part 1: what the evidence supports

- **Tripo's written guidance on reference images is one short help-centre page, and it is specific.** The subject should fill "70-85% of the image", centred, on "a plain, solid-color background (white or light gray works best)", in "even, diffused lighting", at "at least 1024x1024". It says to avoid "reflective or transparent surfaces", "heavy occlusion" and "multiple subjects in one image" (section 3).
- **The API reference says much less and gives a lower number:** "at least 256 × 256 px", "clean background and minimal occlusion", PNG, JPEG or WebP up to 20 MB (section 3).
- **Nothing Tripo publishes states a camera angle, a preference for perspective or orthographic pictures, or whether a transparent background is better than a white one.** These were looked for in the API reference, the help centre, three tutorials and the CLI package (section 3).
- **For prompts, the API reference gives a limit and one example.** "up to 1024 characters. Describe shape, material, style, and scale." A negative prompt is "up to 255 characters". Tripo's own blog posts disagree with each other on whether to describe materials (section 2).
- **`image-to-model` takes no prompt.** The API has no `prompt` parameter on that endpoint. A Tripo tutorial tells users to add one; that can only be about the Studio web app (sections 2 and 8).
- **Multiview is four fixed directions: front, left, back, right.** Front is required, at least two pictures, "the same object under consistent lighting". The help centre recommends it when the back or the thickness comes out wrong (section 4).
- **`delight`, the switch that removes baked-in lighting, does nothing on default settings.** It defaults to true, but "only the `v3.5-20260815` texture model reads this", and the default texture model is `v3.0-20250812`. A request has to set `texture_version` to get it (section 5).
- **For game assets Tripo's documentation recommends the P series:** "Low-poly / game assets: Use `tripo-p1`: cleaner topology and more precise face-count control". It costs more than the H series: 50 credits against 30 for an image with standard textures (sections 5 and 7).
- **Several steps can fix a result without generating again,** each a paid call: new textures on the same shape, reduction with a bake, conversion with a texture size and a bottom-centre pivot, splitting into parts, filling holes in parts. The reduction and conversion steps accept an uploaded file, not only a Tripo task (section 6).

### Part 2: what the evidence supports

- **Everything kiln's candidate stages need exists in Blender 5.2.2's API, and the import, export, decimate, unwrap and bake steps have been shown to run headless** (the earlier note's trial). The repair calls were not run by anyone cited here.
- **A glTF file does not survive a trip through Blender unchanged, by design.** Vertices are joined or split, textures may be re-encoded at JPEG quality 75, extras are dropped unless asked for, and the stored normals become custom normals that later repair steps do not update (section 10).
- **`bmesh` reaches every defect check without operators or context:** `BMEdge.is_manifold`, `is_boundary`, `is_wire`, `BMFace.calc_area()`, `bmesh.ops.remove_doubles`, `recalc_face_normals`, `dissolve_degenerate`, `holes_fill`. This is the route that does not depend on Edit Mode (section 13).
- **The 3D Print Toolbox does not ship with Blender 5.2.2.** It is an extension that has to be downloaded; `tools/bl` runs offline with factory settings (section 13).
- **Two documented traps for a texture stage.** Resizing an image with `Image.scale()` does not mark it as changed, and the exporter writes the original bytes of an unchanged image. And a factory-settings Cycles bake would run at 4,096 samples on the CPU unless the script says otherwise (section 14).
- **"Auto smooth" is gone.** It was removed in Blender 4.1. In 5.2.2 a script sets sharp edges with `Mesh.set_sharp_from_angle()` or `bpy.ops.object.shade_smooth_by_angle()` (section 15).
- **Bevy's forward is the opposite of glTF's.** glTF: "+Y as up, +Z as forward". Bevy 0.19.1: forward is −Z, and its conversion option is marked experimental and is off by default. Tripo's default export faces +X (section 11).

### What the evidence does not settle

- What a Tripo raw output for a prop actually holds: how many materials, whether metallic and roughness share one image, texture size at each quality level, whether normals are smooth, how many separate pieces. Still unknown, as in the earlier notes.
- Whether following Tripo's image checklist measurably improves results. It is the vendor's advice with no numbers behind it.
- Whether each repair call does what its description says on a generated mesh in background mode. Only the introspection was done here.
- Which way Blender's importer turns a glTF file's +Z forward. The usual answer is Blender's −Y; no page was read that says so.

### The smallest experiments

In order of cost: print one request without spending (`tripo make reference.png --dry-run --json`); inspect one existing `.glb` with `python3 learn/assets/glb_inspect.py` to see what a stage would meet; run a one-triangle file through import and export to settle the axes; then one paid generation with and without `texture_version=v3.5-20260815`. Section 18 lists them all.

# Part 1: Tripo's guidance

## 1. Where Tripo's guidance lives

Five places, of very different weight. This matters because they disagree (section 8).

| Source | What it is | Grade |
|---|---|---|
| [API reference](https://developers.tripo3d.com/llms-full.txt) (`developers.tripo3d.com`, v3) | Parameter names, values, defaults, limits | Fact, for parameters. Its quality wording is vendor claim |
| [Help Center](https://www.tripo3d.ai/help) (`tripo3d.ai/help`) | Short articles for Studio users. Most carry a modified date of 2026-08-25 | Vendor guidance |
| `tripo-cli` 0.5.2, [npm package](https://registry.npmjs.org/tripo-cli) | The CLI and its bundled skill: `skill/SKILL.md`, seven command pages, six recipes | Fact for what the CLI does; it restates the API reference |
| [Tutorials](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tips) and [blog](https://www.tripo3d.ai/blog/text-to-3d-prompt-engineering) on `tripo3d.ai` | Long marketing articles. One tutorial is tagged "Auto Generation" | Vendor blog. Several figures in them contradict the API reference |
| [Legacy API v2 documentation](https://docs.tripo3d.ai/) | The older API | Being switched off: "From November 1, 2026 ... all V2 endpoints will stop serving requests" |

The CLI package contains no advice on prompts or pictures beyond parameter limits. Its text was searched for "background", "occlusion", "centred" and "A-pose" and has none.

## 2. Text prompts

### For `text-to-model`

From the [API reference](https://developers.tripo3d.com/en/docs/generation-text-to-model/standard), the same for the H and P series:

- `prompt`: "Text prompt, up to 1024 characters. Describe shape, material, style, and scale."
  - "Good: \"A low-poly medieval wooden treasure chest with iron hinges and a rusty lock.\""
  - "Bad: \"A box.\""
  - "Include material and style hints for better PBR results."
- `negative_prompt`: "up to 255 characters. Describe what you do NOT want in the generated model. For example: \"blurry, low quality, broken mesh\"."
- `image_seed`: "Random seed for the internal text-to-image stage. Controls the reference image generated from your text prompt before 3D conversion." So text-to-model makes a picture first and builds from that (fact). A person never sees that picture before the model exists (inference).
- **Language** is not stated for this endpoint. The CLI's own planner, when it uses an LLM, is told to "translate to English, keep it concrete, <= 200 chars" (source: `dist/ai/experts.js`). That is what Tripo's own tool sends, not a documented rule.
- **Refusals:** error 2008 is "content policy violation", 2009 "prompt contains invalid characters" (CLI error table).

From the [Help Center](https://www.tripo3d.ai/help/features/how-to-use-the-text-to-3d-feature):

- "Use clear, specific descriptions with details about style, material, and structure".
- Its example: "Dark battle axe, spiked skull, cracked blade, wooden handle with dark cloth wrap and spikes, dark fantasy barbarian style".
- "AI generation involves randomness — if the first result isn't ideal, retry for different variations".
- "For more control over the output, consider generating an image first, then converting it to 3D".

That last line is Tripo's own advice to use a reference image, which is what a kiln run starts from.

### What the vendor's articles add

All *vendor blog*. None shows a measured comparison.

- [How to Master Prompt Engineering for Text to 3D Models](https://www.tripo3d.ai/blog/text-to-3d-prompt-engineering) (published 2025-04-20, modified 2026-01-27):
  - A template: `[Main Subject], [Key Descriptors/Features], [Material/Texture], [Style/Genre], [Quality/Technical Hints]`.
  - "Put crucial info like subject and key adjectives early."
  - Negative prompts it shows: "no visible text, logos, brand marking, no unrealistic proportions or colors".
  - It names "Tripo AI Version (2.5)" as the best model, which dates it.
- [5 Professional Tips](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tips) gives "a five-element formula: \"Subject + Form + Material + Key Details + Style.\""
- [Prompt Engineering for Better 3D Shapes: A Practitioner's Guide](https://www.tripo3d.ai/blog/explore/prompt-engineering-for-better-3d-shapes) (2026-03-10), written in the first person by an unnamed author, with no assets shown. It says the opposite about materials:
  - "Prompts heavy on \"rusty,\" \"glossy,\" or \"worn\" often produce baked-in, non-removable texture details on the geometry itself."
  - Use "explicit scale references like \"human-scale,\"" and shape words: "cylindrical helmet form with a tapered crest".
  - For flat-sided objects: "\"beveled edges,\" \"chamfered corners,\" ... \"sharp creases.\"" For organic ones: "\"tapered limbs,\" \"sinuous curves\"".
  - "if edges are too soft, I add \"sharp, defined edges.\""

### Style

- **The v3 generation endpoints have no `style` parameter.** The word appears in the API reference only as part of free text ("material and style hints").
- **Stylize is a separate step** on a finished model: `lego`, `voxel`, `voronoi`, `minecraft` (CLI `commands/process.md`; the ComfyUI page calls it "Apply a geometric style").
- **The Studio web app has style presets** the API does not: "Cartoon, Steampunk, Alien, Clay, Barbie, Gold" (vendor blog, above).

### For `text-to-image`, which makes a reference image

From the [API reference](https://developers.tripo3d.com/en/docs/generation-text-to-image):

- `prompt`: "Supports Chinese and English. Recommended: ≤ 300 Chinese characters or ≤ 600 English words. Put the most important elements first. Negative prompts: append after `--no`." There is no separate negative-prompt field here.
- `model` default `seedream_v4`. Others: `seedream_v5`, `banana`, `banana_pro`, `banana2`, `chat_image_2`, `chat_image_2.5_flare`, `chat_image_2.5_sunburst`, and two being retired (`chat_image_1` on 2026-10-23, `chat_image_1.5` on 2026-12-01).
- `size` default `2048x2048`. `output_format` default `png`.
- `background`: `auto`, `opaque` or `transparent`, on the two `chat_image_2.5` models only. "`transparent` requires `output_format=png`."
- `template`: `asset_extraction` ("extract a subject from a scene"), `character_completion`, `t_pose`, `variants`, `figure`. The image-to-image endpoint adds `3d_enhance` ("enhance for 3D generation"); the CLI's page says it "cleans a photo before image-to-model".
- Cost: 5 credits for the default model at any size, up to 50 for the most expensive model and quality ([pricing](https://developers.tripo3d.com/en/pricing)).
- One image task at a time per account (earlier note).

No Tripo page gives an example prompt for making a reference image of a prop. The CLI's one example is for a character: `"front view of a knight, T-pose"`.

## 3. Reference images for `image-to-model`

### What the API reference requires

From the [image-to-model page](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard):

- "Supported formats: `PNG`, `JPEG`, `WebP`". "Max file size: **20 MB**".
- "Recommended resolution: at least **256 × 256 px**. Subject should be clearly visible with a clean background and minimal occlusion."
- The input is a `file_token` from an upload, a public URL, or the task ID of a Tripo image task.
- No maximum resolution is given on this page. The image-to-image page gives one for its own input: "Max total pixels: 6000 × 6000 = 36 MP", "Min width/height: 14 px", "Aspect ratio (W/H): [1/3, 3]". Whether the same limits apply to `image-to-model` is not stated.

### What the Help Center recommends

From [How to Get Better Image-to-3D Results](https://www.tripo3d.ai/help/features/how-to-get-better-image-to-3d-results) (no date on the page). This is the most specific guidance Tripo publishes, quoted in full where it bears on a prop:

- "The subject should occupy 70-85% of the image. Center the subject with a clean margin on all sides."
- "Use a plain, solid-color background (white or light gray works best)."
- "Even, diffused lighting produces the best results. Avoid harsh directional light."
- Avoid: "Reflective or transparent surfaces (glass, chrome)."
- Avoid: "Heavy occlusion — if a limb or part is hidden behind another object, the back side will be guessed."
- Avoid: "Low resolution — aim for at least 1024x1024; below 512px the geometry gets muddy."
- Avoid: "Multiple subjects in one image — the model will try to merge them into one mesh."

Its table of problems and causes:

| Problem | "Likely cause" | "Fix" |
|---|---|---|
| "Model looks blurry / low detail" | "Low-res input or small subject" | "Use higher resolution image, ensure subject fills 70–85% of frame" |
| "Model is thicker than expected" | "Side profile information missing" | "Provide side-view reference or use multi-view input" |
| "Local distortion (hands, thin parts)" | "Occluded or ambiguous geometry" | "Use a cleaner reference angle; for characters, T-pose or A-pose works best" |
| "Extra structures on back" | "AI hallucination from missing back info" | "Provide back-view image via multi-view input" |
| "Color/texture mismatch" | "Strong shadows or reflections baked in" | "Use flat, even lighting; avoid glossy surfaces in the photo" |

### What Tripo does not say

Looked for in the API reference, the Help Center, three tutorials and the CLI package, and not found:

- **Camera angle.** Front, three-quarter or from above: no recommendation. `orientation=align_image` exists ("align the model to the input image viewpoint"), which implies the picture's viewpoint is otherwise not kept (inference).
- **Perspective or orthographic.** Not mentioned anywhere.
- **Transparent background.** The image generator can make one, and PNG is accepted, but no page says how `image-to-model` treats transparency or whether it removes a background itself. The search summary of a third-party page said "PNG files with transparency are ideal"; that page was not opened (unverified).
- **Thin parts** beyond the table's one row. Nothing on wires, chains, railings or cloth.
- **A maximum useful resolution.**

### What the tutorials say, and where they differ

- [5 Professional Tips](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tips): "use images with a resolution above 2048x2048 pixels"; "solid color backgrounds"; "high contrast between the subject and the background".
- [Beginner tutorial](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tutorial): "file size must be kept under 10MB, supporting common image formats like JPEG, PNG, and TIFF"; "minimal reflections".

Three different minimum sizes and two different size limits, from one vendor (section 8).

### What the docs say causes failures

- **A task can fail outright.** "Generation may fail due to complex prompts or temporary server load"; credits come back "within 1 hour" ([Help Center](https://www.tripo3d.ai/help/features/why-did-my-generation-fail-or-get-stuck)). Through the API, "Failed and cancelled tasks are not charged."
- **Input rejected:** 2003 empty file or unreachable URL, 2004 unsupported type, 2020 to 2022 bad URL or too large, 2008 content policy (CLI error table).
- **`smart_low_poly`:** "Best suited for simple, non-complex inputs. Complex models may occasionally fail."
- **Reduction:** error 2018, "too complex to remesh".
- **Low face limits on the P series:** "simple models start from **150** faces, complex models start from **250** faces. Lower values may result in poor generation quality."

### A checklist for a reference image

Each line is Tripo's guidance unless marked. It is a list of what the vendor asks for, not a tested recipe.

1. **One object.** Not a scene, not two props side by side.
2. **Fills 70 to 85% of the frame**, centred, with a margin all round.
3. **Plain white or light grey background.**
4. **Even, soft light.** No hard shadow on the object and none cast on the ground. Shadows and highlights in the picture end up in the colour texture.
5. **At least 1024 × 1024 pixels.** PNG or JPEG, under 20 MB. (Inference: a square 2048 × 2048 PNG, the image generator's default, meets every figure Tripo gives anywhere.)
6. **Nothing hidden.** Every part that matters is visible and not behind another part.
7. **No glass, chrome or other mirror-like or see-through surface.**
8. **If the back or the depth matters, plan for multiview** (section 4) instead of hoping.
9. **Inference, not Tripo's:** the picture shows the object's proportions and colours only. It carries no size. Kiln's run takes the size separately, and `auto_size` is a guess.
10. **Inference:** keep the picture; it is the record the shape review compares against, and Tripo's links to its own copies expire.

Claude can check items 1 to 7 by looking, with the limits Anthropic documents for its sight (earlier note): counting and proportion are approximate.

## 4. Multiview input

From the [multiview-to-model page](https://developers.tripo3d.com/en/docs/generation-multiview-to-model/standard):

- **Views:** `front`, `left`, `back`, `right`. No top or bottom view exists.
- **How many:** "The front view **cannot be omitted**. You may omit other views, but at least 2 images are required."
- **Order:** with the recommended form, an array of one-key objects such as `{"front": ...}`, "Order does not matter; the server canonicalizes to **[front, left, back, right]**". The older form is exactly four strings in that order, with `""` for a missing view.
- **Consistency:** "All images should depict the same object under consistent lighting."
- **Size:** "at least **256 × 256 px**". PNG, JPEG, WebP.
- **Parameters:** the same as `image-to-model`, including `texture_alignment` and `orientation`.
- **Cost:** the same as one image, 30 credits with standard texture on the H series.

Making the views from one picture:

- `POST /v3/generation/image-to-multiview` takes one image ("Subject should be clearly visible against a clean background") and returns four. 10 credits.
- `POST /v3/generation/edit-multiview` changes one view by instruction, for example `{"view": "front", "prompt": "..."}`. 5 credits per edited image.
- `multiview-to-model` accepts that task's ID directly: `[{"task_id": "<uuid>"}]`.

When Tripo recommends it:

- Help Center: "If a single image is not giving you accurate back or side geometry, consider using multi-view input instead — feed the model front, side, and back views so it stops guessing what it cannot see."
- The text-to-3D help page: "Try converting your reference to multi-view images for more accurate 3D structure".
- A tutorial claims "Providing 2-4 images from different angles can improve model integrity by over 40%" (vendor claim; no method, no definition of "integrity"). The same tutorial asks for "front, sides, back, and top" and "30%-60% overlapping area" between photos, which describes photographing a real object, not the API's four fixed slots.

Not stated anywhere: which way "left" is (the object's left or the viewer's), how exactly the views must line up, or whether generated views do better than a single picture. The CLI assigns files by name: "filename hints (`front|back|left|right`...) win; otherwise positional order front, left, back, right".

**Inference:** four views made by an image model are four separate inventions of the hidden sides. The shape review would then have five pictures to compare against, not one.

## 5. Generation settings

All from the API reference pages for `image-to-model` ([H series](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard), [P series](https://developers.tripo3d.com/en/docs/generation-image-to-model/p)) unless marked. Credits from the [pricing page](https://developers.tripo3d.com/en/pricing) and the [P1](https://developers.tripo3d.com/en/models/p1) and [v3.1](https://developers.tripo3d.com/en/models/v3-1) model pages; one credit is $0.01.

"H" means `v3.1-20260211`, `v3.0-20250812`, `v2.5-20250123`. "P" means `P1-20260311`, `P2-20260801`.

### Base cost of one generation, in credits

| | No texture | Standard texture | Detailed texture | Extreme texture |
|---|---|---|---|---|
| H series, from an image or multiview | 20 | 30 | 40 | 50 |
| H series, from text | 10 | 20 | 30 | 40 |
| P1, from an image or multiview | 40 | 50 | 60 | not shown |
| P1, from text | 30 | 40 | 50 | not shown |
| P2 (preview) | 100 | 110 | 120 | 130 |

The P2 row is from the changelog, which does not split it by input. The H-series "detailed" column is on the v3.1 model page; its "extreme" column is arithmetic, the standard price plus the pricing page's "8K Ultra Texture +20".

### The settings

| Parameter | Values | Default | Applies to | Extra credits |
|---|---|---|---|---|
| `model` | The dated values above | None: "Required" | All | See the table above |
| `face_limit` | H: up to 1,500,000 (v3.1), 1,000,000 (v3.0), 500,000 (v2.5); 2,000,000 with detailed geometry; 150,000 with `quad`. P1: 50 to 20,000. P2: 48 to 50,000, or 48 to 25,000 with `quad` | Omitted: "adaptive topology" | All | None |
| `smart_low_poly` | true, false. Fixes the range to 500 to 20,000 triangles, or 500 to 10,000 quads | false | H, v3.0 and later | +10 |
| `quad` | true, false. "Enabling `quad` will force the output format to `FBX`"; face count 10,000 if no limit is given | false | H v3.0 and later; P2 | +5 |
| `geometry_quality` | `standard`, `detailed` ("Ultra mode, finer geometry detail") | `standard` | H, v3.0 and later | +20 |
| `texture` | true, false | true | All | See base cost |
| `pbr` | true, false. Adds "`base_color`, `metallic`, `roughness`, `normal`"; forces `texture` on | true | All | None stated |
| `texture_quality` | `fast`, `standard`, `detailed`, `extreme` ("8K textures") | `standard` | v3.0 and later; `fast` only with texture `v3.5-20260815` | `detailed` +10, `extreme` +20 |
| `texture_version` | `v3.5-20260815`, `v3.0-20250812`, `v2.5-20250123` | Derived: `v3.0-20250812` for v3.x and P geometry | All | None stated |
| `delight` | true, false. "Removes baked-in lighting from the reference image before texturing" | true, but "only the `v3.5-20260815` texture model reads this" | Texture v3.5 only | None stated |
| `texture_alignment` | `original_image` ("prioritize matching the input image colors"), `geometry` ("prioritize matching the generated geometry") | `original_image` | Image and multiview | None |
| `orientation` | `default` ("automatic orientation"), `align_image`. "Only effective when `texture` is `true`" | `default` | Image and multiview | None |
| `auto_size` | true, false. "the model size will be in meters" | false | v3.0 and later | None |
| `export_orientation` | `+x`, `-x`, `-y`, `+y` (the forward axis) | `+x` | All | None |
| `export_uv` | true, false. "Set `false` for faster generation and smaller file size" | true | All, by the API pages | None |
| `model_seed` | Integer | Random | All | None |
| `texture_seed` | Integer | Random | All | None |
| `image_seed` | Integer | Random | Text only | None |
| `generate_parts` | true, false. Needs `texture=false` and `pbr=false` | false | H, v3.0 and later | +20 |
| `compress` | `geometry` ("meshopt compression") | Not set | v3.0 and later | None |
| `enable_image_autofix` | true, false. "enhance low-resolution or low-quality images" | false | Image | None stated |

Points a pipeline has to know:

- **The pixel size of `standard` and `detailed` textures is not stated.** Only `extreme` has a number ("8K"). The convert step's `texture_size` defaults to `4096`. A tutorial says the high-definition mode makes "4K resolution PBR material textures".
- **`delight` needs `texture_version=v3.5-20260815`.** On defaults the texture model is `v3.0-20250812`, which "ignore[s] it". So a default request keeps whatever lighting is in the picture (inference from the two quoted sentences).
- **`export_orientation` is a trap if any Tripo step follows.** "post-processing the model may produce a wrongly-oriented result while the task still reports `status: success`". Tripo says to set it in the final convert instead.
- **`compress=geometry` gives a meshopt-compressed file.** Blender 5.2.2's importer lists `EXT_meshopt_compression` among the extensions it handles (source: `io/imp/gltf2_io_gltf.py` in the pinned build). Whether Bevy 0.19.1 and kiln's own `kiln/glb.py` read it was not checked.
- **There is no setting for the number of materials, the UV layout, or smooth against flat shading.**

### What the CLI exposes

From the package's `skill/commands/generate.md` and `make.md`:

- **Every parameter above passes through** as `-p key=value`, for example `-p face_limit=8000 -p texture_version=v3.5-20260815`. The skill warns: "Unknown `--param key=value` pairs pass through to the API; stick to documented ones."
- **First-class flags:** `--model` (aliases `tripo-v3.1`, `tripo-p1`, `tripo-p2`, which the CLI turns into the dated values), `--seed` (`model_seed` only), `-n` (up to four candidates with different seeds), `--for <scenario>`, `--then <steps>`, `--dry-run`.
- **Exact endpoint control:** `tripo generate image-to-model photo.png`, `tripo generate multiview-to-model front.png back.png`, `tripo generate text-to-image "..."`.
- **It changes requests locally.** It picks P1 when the face budget is 20,000 or less (earlier note), strips parameters P1 does not support "with a warning", and turns texture off for `generate_parts`. The dry run shows the result.
- **Its parameter table differs from the API reference** in two places: it lists `texture_quality` as `standard` / `detailed` / `extreme` with no `fast`, and gives `export_uv` as "P series only". It does not list `texture_version` or `delight` at all; they would still pass through with `-p`.

## 6. Fixing a result without starting over

Each is one more task and one more charge. "Input" says what the step accepts.

| Step | Endpoint | Input | What it takes | What it returns | Credits |
|---|---|---|---|---|---|
| New textures, same shape | `POST /v3/models/texture` | A Tripo task, an uploaded file or a URL (GLB, GLTF, FBX, OBJ, STL, up to 150 MB) | `texture_prompt` (one of `text`, `image`, or four `images` in the order front, left, back, right; `style_image` with text), `model` (the texture version), `texture_quality`, `texture_alignment`, `pbr`, `texture_seed`, `delight`, `bake`, `part_names` | The model with new texture maps | 10 fast or standard, 20 HD, 30 8K |
| Same shape, other textures by seed | A new generation with the same `model_seed` and a different `texture_seed` | | "keep model_seed unchanged and vary texture_seed" | A full new generation | Full price |
| Reduce | `POST /v3/mesh/decimate` | Task, file or URL | `model` (`v2.0` default, "smart highpoly-to-lowpoly retopology"; `v1.0`, "basic decimation"), `face_limit` ("Target polycount"), `quad`, `bake` (default true, v2.0 only: "Bake textures onto the low-poly model"), `part_names` | A reduced model | 30 for v2.0, 10 for v1.0 |
| Convert | `POST /v3/models/convert` | Task, file or URL | `format` (`GLTF`, `FBX`, `USDZ`, `OBJ`, `STL`, `3MF`), `face_limit`, `texture_size` (default `4096`), `texture_format` (default `JPEG`; `PNG`, `WEBP` and others), `pack_uv`, `pivot_to_center_bottom`, `scale_factor`, `flatten_bottom`, `export_orientation`, `bake`, `export_vertex_colors`, `part_names` | The converted file | 5; 10 if any of `quad`, `face_limit`, `flatten_bottom`, `flatten_bottom_threshold`, `texture_size`, `texture_format`, `pivot_to_center_bottom`, `scale_factor` is set |
| Split into parts | `POST /v3/mesh/segment` | Task, file or URL | `model` (`v1.0-20250506` default, by geometry; `v2.0-20260430` beta, with labels), and for v2 `segmentation_granularity`, `split_by_connectivity`, `ref_image` | A model in named parts | 40 |
| Fill holes in parts | `POST /v3/mesh/complete` | A segment task only | `completion_mode`: `ai_completion` (default, "Generates realistic geometry to fill missing regions") or `quick_cap` ("Fast sealing of open boundaries without AI generation"); `part_names` | Completed parts | 50, or 30 for quick cap |
| Refine | `POST /v3/models/refine` | "only accepts text_to_model tasks" (CLI) | `model` | A refined model | Not on the pricing page |
| Stylize | `POST /v3/models/stylize` | Task or file | `style`: `lego`, `voxel`, `voronoi`, `minecraft` | A restyled model | Not on the pricing page |
| Import | `POST /v3/models/import` | File or URL | Nothing else | A task other steps can use | Not on the pricing page |

- **Refine and stylize have no reference page** in the v3 documentation. They appear only in the migration table, the SDK table and the CLI's pages. What refine does to a model is not described anywhere read.
- **Refine does not apply to kiln's route.** It takes text-to-model tasks only (CLI source and its "frequent local validations").
- **The reduce and convert steps would work on a file kiln already holds**, since they accept an upload (inference from the input list). That would make Tripo a paid alternative to a Blender stage, with the limits the earlier note recorded: "`decimate`'s face budget is a target, not a ceiling".
- **Nothing changes the shape of one region by instruction.** The nearest are segment, then complete or re-generate a part.

## 7. Model versions

| Wire value | Tripo's description | Face limit | Stated speed | Status |
|---|---|---|---|---|
| `v3.1-20260211` | "latest, best quality"; "AAA production pipelines / 3D printing & flexible manufacturing" | Up to 2,000,000 | About 40 s without texture, 120 s with | Default |
| `v3.0-20250812` | "stable, advanced features"; "Backward compatibility" | Up to 2,000,000 | | Legacy (CLI) |
| `v2.5-20250123` | "balanced"; "Historical project compatibility" | Up to 500,000 | | Legacy (CLI). Lacks `texture_quality`, `geometry_quality`, `auto_size`, `quad`, `smart_low_poly`, `generate_parts`, `compress` |
| `P1-20260311` | "optimized for low-poly generation"; "Game pipelines / UGC generative gameplay / Mobile 3D assets" | 50 to 20,000 | About 10 s without texture, 60 s with | Current. No `quad`, `smart_low_poly`, `generate_parts`, `geometry_quality` |
| `P2-20260801` | "next-gen P Series with quad output support" | 48 to 50,000; 25,000 quads | | Preview. The CLI never picks it by itself |

Texture models are versioned separately: `v3.5-20260815` (added September 2026), `v3.0-20250812`, `v2.5-20250123`.

What the documentation recommends, from [Models and Versions](https://developers.tripo3d.com/en/docs/models-and-versions):

- "**Low-poly / game assets**: Use `tripo-p1` for 3D — cleaner topology and more precise face-count control".
- "**Production environments**: Pin a specific model version to avoid output inconsistencies caused by model updates".
- The P1 page: "Strict 50-20,000 face limit control", "Game-asset ready topology" (vendor claims).
- **Hard-surface objects:** no recommendation was found in any Tripo documentation page. One blog post suggests prompt words for them (section 2).
- The Help Center describes a Studio feature, "Smart Mesh", with "~5,000 (default)" polygons, "Best For: Game assets, real-time apps, Web3D". Which API setting it corresponds to (the P series or `smart_low_poly`) is not stated.

So for a prop under a triangle budget there are three documented routes, and nothing measured between them:

| Route | Credits for one image, standard texture | Triangle control |
|---|---|---|
| H series with `face_limit` | 30 | "Maximum polycount" |
| H series with `smart_low_poly` | 40 | 500 to 20,000; "Complex models may occasionally fail" |
| P1 with `face_limit` | 50 | 50 to 20,000; "strict" |

## 8. How Tripo's own sources differ

| Topic | API reference | Help Center | Tutorials and blog | CLI package |
|---|---|---|---|---|
| Minimum picture size | "at least 256 × 256 px" | "at least 1024x1024; below 512px the geometry gets muddy" | "above 2048x2048 pixels" | Restates 256 (for splats) |
| Largest file | 20 MB | Not stated | "under 10MB" | 20 MB |
| Formats | PNG, JPEG, WebP on the generation page; "Images: `JPEG`, `PNG`" on the upload page | Not stated | "JPEG, PNG, and TIFF" in one; "JPEG, PNG, and WebP" in another | "PNG/JPEG/WebP/BMP/TIFF" in the error table |
| A prompt with a picture | No `prompt` on `image-to-model` | Not mentioned | "first upload a reference image, and then combine it with a well-constructed prompt" | No such option |
| Materials in a prompt | "Include material and style hints for better PBR results" | "details about style, material, and structure" | One post gives a material slot in its template; another says such words "produce baked-in, non-removable texture details" | Nothing |
| Views | front, left, back, right | "front, side, and back" | "front, sides, back, and top" | front, left, back, right |
| Model names | Generation pages require dated values; the Models page lists `tripo-p1`, `tripo-v3.1` and calls `tripo-v3.1` "(default)" though `model` is "Required" | | "Tripo AI Version (2.5)" as best | "the API rejects the alias itself with 1004" |
| Image model names | `banana`, `banana_pro`, `banana2` on the endpoint page; `gemini-2.5-flash`, `gemini-3-pro`, `gemini-3.1-flash` on the Models page | | | Both: "Backend aliases `banana` ... are also accepted" |
| `export_uv` | Listed for H and P | | | "P series only" |
| P1 face limit | "50 – 20,000" on the endpoint page; "48 - 20,000" on the model page and the index | | | "48–20000 (CLI enforces ≥50)" |
| Reduce face limit | No range given | | "10,000-50,000 range usually meets visual needs" for games | "docs quote 1000–20000; CLI accepts 500–20000" |
| Game face counts | "Game-ready assets: 50,000 – 100,000" | "Smart Mesh ~5,000 (default)" | "10,000-50,000" | `game-mobile` preset: 15,000 |
| Which model for quality | "Highest quality: Use `tripo-p1` for 3D" on the Models page, which also calls `tripo-v3.1` the "Latest high-precision model" | | | "`tripo-v3.1` (high fidelity)" |
| Free credits | | | "300 credits per month" | The earlier note read 200 on the pricing page |
| Blender add-on | | "Blender 4.1.0+" | | The earlier note read "3.0+" on the plugins page |
| Up axis | `export_orientation` sets a forward axis only | "Tripo exports Y-up" | | |

Where they conflict, the API reference is the contract for what a request may contain, and the Help Center is the only place with reasons. The tutorials are the least reliable: they are the source of every figure that contradicts the API.

# Part 2: Blender 5.2.2 scripting for the stages

How the facts in this part were obtained: property names, value lists and defaults are **read from the binary** (two scripts run through `tools/bl`, which printed `bpy.ops.<x>.get_rna_type().properties` and the like). What a property does is quoted from the [Blender 5.2 manual](https://docs.blender.org/manual/en/5.2/), the release notes, or the add-on's source in the pinned build. The [Python API reference](https://docs.blender.org/api/5.2/) describes the same properties; its per-operator pages were not opened one by one.

The earlier note [`game-mesh-kiln-or-generator.md`](game-mesh-kiln-or-generator.md), sections 2 and 7, already covers the Decimate modes, the unwrap operators, baking and their failure modes, and reports a trial of that route on two scanned rocks. This part adds what that note lacks and points back to it for the rest.

## 9. Running headless

### What `tools/bl` gives a script

`tools/bl` starts Blender with `--background --factory-startup --offline-mode --quiet --python-exit-code 1 --python <script> -- <args>`. From the [command-line page](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html):

- `--background`: "Run in background (often used for UI-less rendering)."
- `--factory-startup`: "Skip reading the startup.blend in the users home directory."
- `--offline-mode`: "Disallow internet access, overriding the preference."
- `--python-exit-code <code>`: "Set the exit-code in [0..255] to exit if a Python exception is raised (only for scripts executed from the command line), zero disables."
- `--`: "End option processing, following arguments passed unchanged. Access via Python's `sys.argv`."
- `-t, --threads <threads>`: "Use amount of `<threads>` for rendering and other operations".
- "Arguments are executed in the order they are given."

Read from the binary in that session:

- `bpy.app.background` is True, `bpy.app.factory_startup` is True, `bpy.app.online_access` is False.
- **The scene is not empty.** It holds `Cube`, `Light` and `Camera`. `scale_to_size.py` already clears it with `bpy.ops.wm.read_factory_settings(use_empty=True)`.
- **A window and a screen exist, but no editor area.** `bpy.context.window` is a Window, `bpy.context.screen` is "Layout", `bpy.context.area` is None.
- **Add-ons enabled by default:** `io_scene_gltf2`, `io_scene_fbx`, `cycles`, `io_anim_bvh`, `io_curve_svg`, `io_mesh_uv_layout`, `pose_library`, `bl_pkg`. Shipped but off: `node_wrangler`, `rigify`, `hydra_storm`, `ui_translate`, `viewport_vr_preview`. Nothing else ships.
- **Units** are metric with a scale of 1.0.
- **Render engine** defaults to `BLENDER_EEVEE`; it can be set to `CYCLES`. Cycles' device is `CPU` and its preferences have no GPU type selected.

### Operators, context and `bmesh`

From the API reference's [operators page](https://docs.blender.org/api/5.2/bpy.ops.html) and [gotchas page](https://docs.blender.org/api/5.2/info_gotchas_operators.html):

- **An operator acts on the context, not on an argument.** "Can't pass data such as objects, meshes or materials to operate on (operators use the context instead)."
- **It returns a set, not a result:** "Common return values are `{'FINISHED'}` and `{'CANCELLED'}`".
- **A cancel may be silent.** "If operator was cancelled but there wasn't any reports from it with `{'ERROR'}` type, it will just return `{'CANCELLED'}` without raising any exceptions. However, if there are error reports, a `RuntimeError` will be raised".
- **A wrong context raises:** "Calling an operator in the wrong context will raise a `RuntimeError`, there is a `poll()` method to avoid this problem."
- **Why a poll fails is often not said.** "the only way to eventually know what is causing the error is to read the source code for the poll function".
- **`bpy.context.temp_override(...)`** is the way to hand an operator a chosen object or selection: "to override `bpy.context.active_object`, you would pass `active_object=object`".

What follows for a kiln stage (inference):

- **`--python-exit-code 1` catches exceptions only.** A stage must check each operator's return value itself and raise when it is not `{'FINISHED'}`, or a silent cancel becomes a stage that did nothing and reported success.
- **Mesh operators need Edit Mode.** Every `bpy.ops.mesh.*` operator probed (`remove_doubles`, `normals_make_consistent`, `delete_loose`, `dissolve_degenerate`, `fill_holes`, `select_non_manifold`, `quads_convert_to_tris`, `decimate`) and every `bpy.ops.uv.*` one probed except `lightmap_pack` reported `poll()` False in Object Mode with the default cube active (read from the binary). A script enters Edit Mode with `bpy.ops.object.mode_set(mode='EDIT')` first.
- **`bmesh` needs none of this.** `bm = bmesh.new(); bm.from_mesh(mesh)`, work, `bm.to_mesh(mesh); bm.free()`. It has no context and no selection. Where both exist, `bmesh` is the more predictable choice in a headless script.
- **Operators with no area.** `bpy.context.area` is None in background mode. Operators that insist on a particular editor will fail their poll. Which of the ones kiln needs do so was not tested here; the earlier note's trial ran Smart UV Project, Pack Islands and the bake this way.

### Add-ons and extensions

- Since 4.2, most add-ons are extensions installed from an online repository ([release notes, 4.2](https://developer.blender.org/docs/release_notes/4.2/extensions/)). `--offline-mode` forbids the download.
- `--addons <addon(s)>` enables shipped add-ons by name "in addition to any default add-ons".
- `tools/bl` sets `BLENDER_USER_RESOURCES` to `.blender-user/` in the repo, so anything installed would land there and not in the home directory.
- The release notes describe "a set of extensions to all users ... served from the default read-only System repository" for offline use. Whether an extension placed there loads under `--factory-startup` was not established.

### Determinism and threads

- `tools/bl` says of its thread setting: "what a script builds, bakes or measures does not depend on it." That is the repo's own statement.
- The earlier note's trial found the decimated GLB "byte-identical across three runs", and baked maps identical or differing in a handful of bytes on the GPU.
- QuadriFlow takes a `seed` (default 0): "Different seeds will cause the remesher to come up with different quad layouts".
- No Blender page was found that promises the same output from the same input. It is observed, not documented.

### API changes that reach these calls

| Version | Change | Source |
|---|---|---|
| 4.1 | "`use_auto_smooth` is removed"; "`auto_smooth_angle` is removed. Replaced by a modifier (or operator) controlling the \"sharp_edge\" attribute"; `calc_normals_split` removed in favour of `Mesh.corner_normals`; "Meshes now always use custom normals if they exist" | [4.1 Python API](https://developer.blender.org/docs/release_notes/4.1/python_api/) |
| 4.2 | Add-ons become extensions: "an archive (.zip) containing the files and a manifest", installed from a repository | [4.2 extensions](https://developer.blender.org/docs/release_notes/4.2/extensions/) |
| 5.0 | "`ImageFormatSettings` now has a `media_type` member that needs to be set to an appropriate type before setting the actual `file_format` member"; "`material.use_nodes` is deprecated and will be removed in 6.0. Currently it always returns `True`"; EEVEE's identifier becomes `BLENDER_EEVEE` | [5.0 Python API](https://developer.blender.org/docs/release_notes/5.0/python_api/) |
| 5.1 | "Python has been upgraded to version 3.13"; `mesh.validate()` fixes more | [5.1 Python API](https://developer.blender.org/docs/release_notes/5.1/python_api/) |
| 5.2 | "Added `gpu.init()` to initialize gpu backend when running Blender in background mode"; the `imbuf` module "can now be used to convert between different file formats" with "access to image quality and compression" | [5.2 Python API](https://developer.blender.org/docs/release_notes/5.2/python_api/) |

The earlier note records the finding that most failed LLM-written Blender scripts were written for the wrong version's API. Scripts and advice found on the web that set `mesh.use_auto_smooth` or `material.use_nodes` are from before these changes. In the pinned build the first does not exist (read from the binary) and setting the second prints a deprecation warning.

### Settings for the asset record

None. These are properties of `tools/bl`, the same for every asset.

## 10. Importing and exporting glTF

### The calls

`bpy.ops.import_scene.gltf(filepath=...)` and `bpy.ops.export_scene.gltf(filepath=...)`, from the bundled add-on `io_scene_gltf2`. Both report `poll()` True in background mode. The options that matter, **read from the binary**, with the [manual's](https://docs.blender.org/manual/en/5.2/addons/import_export/scene_gltf2.html) words:

| Import option | Default | What it does |
|---|---|---|
| `merge_vertices` | False | "attempts to combine co-located vertices where possible. Currently cannot combine verts with different normals" |
| `import_shading` | `NORMALS` | `NORMALS` ("Use Normal Data"), `FLAT`, `SMOOTH`: "How normals are computed during import" |
| `import_pack_images` | True | "Pack all images into .blend file" |
| `import_webp_texture` | False | "If a texture exists in WebP format, loads the WebP texture instead of the fallback PNG/JPEG one" |
| `import_unused_materials` | False | "Import materials & Images not assigned to any mesh" |
| `import_merge_material_slots` | True | "Merge material slots when possible" |
| `import_scene_extras` | True | "Import scene extras as custom properties" |

| Export option | Default | What it does |
|---|---|---|
| `export_format` | Set by the script; `GLB` in `scale_to_size.py` | "Binary is most efficient" |
| `export_yup` | True | "Export using glTF convention, +Y up" |
| `export_apply` | False | "Apply modifiers (excluding Armatures) to mesh objects" |
| `export_texcoords`, `export_normals` | True, True | Write UVs and normals |
| `export_tangents` | False | "Export vertex tangents with meshes" |
| `export_materials` | `EXPORT` | `EXPORT`, `PLACEHOLDER`, `VIEWPORT`, `NONE` |
| `export_image_format` | `AUTO` | `AUTO`, `JPEG`, `WEBP`, `NONE` |
| `export_image_quality` | 75 | "Quality of image export", for JPEG and WebP |
| `export_keep_originals` | False | "Keep original textures files if possible"; the manual says "For glTF Separate file format only" |
| `export_extras` | False | "Export custom properties as glTF extras" |
| `export_vertex_color` | `MATERIAL` | `MATERIAL`, `ACTIVE`, `NAME`, `NONE` |
| `export_draco_mesh_compression_enable` | False | Draco compression |
| `export_meshopt_compression_enable` | False | Meshopt compression |
| `use_selection`, `use_visible`, `use_renderable` | False | Limit what is exported |
| `export_cameras`, `export_lights` | False, False | |

### What a round trip changes

Import followed by export is not a copy. In the order a stage would meet them:

1. **Axes.** glTF is +Y up; Blender is +Z up. The importer converts and the exporter converts back when `export_yup` is on. Section 11.
2. **Vertex count.** glTF "requires discontinuous normals, UVs, and other vertex attributes to be stored as separate vertices". With `merge_vertices` off, Blender keeps the copies and each UV island is a separate sheet. With it on, copies are joined when position and normal match; the importer rounds normals to one part in 50,000 before comparing (source: `blender/imp/mesh.py`, `merge_duplicate_verts`). On export, "Discontinuous UVs and flat-shaded edges may result in moderately higher vertex counts in glTF compared to Blender, as such vertices are separated for export." The count in the output need not equal the count in the input either way. `scale_to_size.py` records one case: 154 vertices written for 115 with the option off.
3. **Normals become custom normals.** With `import_shading='NORMALS'` the importer calls `mesh.normals_split_custom_set_from_vertices(vert_normals)` (source, same file). The manual's mesh-structure page says "only the FBX Importer and Alembic Importer are capable of importing custom normals", which the add-on's code contradicts. What this means for later stages is in section 15.
4. **The importer repairs silently.** It calls `mesh.validate()` (source), which the API describes as "Validate geometry, return True when the mesh has had invalid geometry corrected/removed". A raw output with invalid faces may arrive already altered, and nothing reports it (inference).
5. **Faces.** "quads and n-gons are automatically converted to triangles when exporting to glTF."
6. **Textures may be re-encoded.** The exporter writes an image's original bytes only when the image comes from a file, has no unsaved change, and its bytes match the format being written (source: `blender/exp/material/encode_image.py`, `__encode_from_image`). Otherwise it copies the pixels and encodes again, at `export_image_quality` for JPEG and WebP. With `AUTO`, a JPEG stays JPEG and a WebP stays WebP. Each re-encode of a JPEG loses a little.
7. **Metallic and roughness.** "glTF expects the metallic values to be encoded in the blue (B) channel, and roughness to be encoded in the green (G) channel of the same image." An imported material is wired that way, which lets the exporter "simply copy the image texture into the glTF file". If a script rewires it differently, "the add-on may attempt to adapt the image to the correct form during exporting".
8. **Occlusion** has no Blender equivalent. It is carried on "a custom node group by the name of glTF Material Output".
9. **Extras.** "Custom properties are always imported, and will be exported from most objects if the Include ‣ Custom Properties option is selected". The option is off by default and `scale_to_size.py` sets it off, so anything a generator put in extras is dropped.
10. **Tangents** are dropped unless `export_tangents` is on. When it is on and the mesh is not triangles, the exporter warns "Could not calculate tangents. Please try to triangulate the mesh first" (source: `blender/exp/primitive_extract.py`). Bevy 0.19.1 computes missing tangents itself (earlier note).
11. **Extensions.** A file that *requires* an extension the add-on does not handle fails to import: "Extension %s is not available on this addon version" (source). The handled list includes `KHR_draco_mesh_compression`, `EXT_meshopt_compression`, `KHR_mesh_quantization`, `EXT_texture_webp` and `KHR_texture_transform`. It does not include `KHR_texture_basisu`.
12. **Node tree.** Empty nodes, names and the hierarchy come through as Blender objects. `scale_to_size.py` already flattens them.

### What can go wrong

- **Unwelded import breaks decimation.** The earlier note's trial: 3,882 boundary edges on a closed boulder with the default, cracks after decimating, none with `merge_vertices=True`.
- **`merge_vertices` cannot join vertices whose normals differ.** A model stored with flat shading, where every face has its own normal, stays in pieces. Importing with `import_shading='SMOOTH'` does not change which vertices merge; the merge happens before shading is set (source order in `mesh.py`). Such a model needs `bmesh.ops.remove_doubles` after import (inference).
- **Old reports of doubled vertices and wrong normals** exist on Blender's tracker ([74721](https://projects.blender.org/blender/blender-addons/issues/74721), 2020; [71313](https://projects.blender.org/blender/blender/issues/71313), 2019). Both are closed and predate the pinned version; single reports.
- **WebP textures.** `import_webp_texture` is off by default and described as choosing between a WebP and its "fallback". What the importer does with a file that has only WebP was not established. `CLAUDE.md` records that kiln's viewer needed a rewrite step for exactly that case in Bevy.

### How Tripo output interacts

- Tripo returns a GLB from generation; `quad` forces FBX, which this stage would not take.
- `compress=geometry` would give a meshopt file. Blender reads it; kiln's own reader was not checked.
- Convert's default texture format is JPEG. A JPEG that passes through Blender unchanged is copied; one a stage has resized is encoded again.
- How many materials, images and meshes a Tripo GLB holds is not documented.

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Join vertices on import | on, off | On is needed for any stage that edits the surface. Off keeps the file's own vertex list |
| Join distance for vertices the importer could not merge | 0, or a length in metres | Larger closes more cracks and can also close thin gaps that should be there |
| Normals on import | keep the file's, smooth, flat | Keeping them preserves the generator's look and makes later repair steps harder (section 15) |
| Texture format on export | keep each, JPEG, WebP | JPEG is smaller and loses detail on each save; keeping the original is lossless when nothing changed |
| Image quality | 0 to 100 | Only applies when an image is re-encoded |
| Write tangents | on, off | On fixes the tangents at build time; off leaves Bevy to compute them |

## 11. Scale, orientation and origin

### Which way is forward and up

| | Up | Forward (front faces) | Right | Units | Source |
|---|---|---|---|---|---|
| glTF 2.0 | +Y | +Z | −X | "meters" | [Specification, section 3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#coordinate-system-and-units): "glTF defines +Y as up, +Z as forward, and -X as right; the front of a glTF asset faces +Z" |
| Bevy 0.19.1 | +Y | −Z | +X | | [`bevy_gltf/src/convert_coordinates.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/convert_coordinates.rs): "Bevy: forward: -Z, up: +Y, right: +X". [`Transform::forward`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_transform/src/components/transform.rs): "Equivalent to `-local_z()`" |
| Blender | +Z | Not read from a page | | Metric, scale 1.0 (read from the binary) | Exporter: "Export using glTF convention, +Y up" |
| Tripo | "Tripo exports Y-up" (Help Center) | `export_orientation`, default `+x` | | Arbitrary unless `auto_size` | API reference |

- **Bevy does not turn a glTF file to its own forward by default.** `GltfConvertCoordinates` has two switches, `rotate_scene_entity` and `rotate_meshes`, both false unless set, and its documentation says: "_CAUTION: This is an experimental feature. Behavior may change in future versions._" (source read in the 0.19.1 crate). So a model whose front faces glTF's +Z faces *backwards* by Bevy's `Transform::forward` unless the game or the file accounts for it (inference).
- **A default Tripo model faces +X**, which is neither.
- **Blender's side of the mapping was not read from documentation.** The common statement is that glTF +Z corresponds to Blender −Y. A one-triangle test file would settle it (section 18).

### The calls

- **Scale and move without operators:** `Mesh.transform(matrix)`, which `scale_to_size.py` uses. The API warns it "inverts normals if matrix is negative"; `Mesh.flip_normals()` "does not handle custom normals".
- **`bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)`** does the same through the context. It has `corrective_flip_normals` (default True, "Invert normals for negative scaled objects") and `isolate_users`. The manual: "The object's origin is moved to the global origin (for location). Rotation values are cleared to zero. Scale values are reset to 1.0."
- **`bpy.ops.object.origin_set(type=..., center=...)`**: types `GEOMETRY_ORIGIN`, `ORIGIN_GEOMETRY`, `ORIGIN_CURSOR`, `ORIGIN_CENTER_OF_MASS`, `ORIGIN_CENTER_OF_VOLUME`; centre `MEDIAN` or `BOUNDS`. **None of them is "bottom centre".** The route through this operator is to place the 3D cursor there and use `ORIGIN_CURSOR`.
- **Simpler for kiln:** after `scale_to_size`, a stored vertex position is already a position in the scene. Moving the origin to the bottom centre is one more `Mesh.transform(Matrix.Translation(...))` by minus the bounding box's centre on the two ground axes and minus its lowest point on the up axis (inference from the script's own docstring).
- **Turning:** `Mesh.transform(Matrix.Rotation(angle, 4, axis))`.

### What can go wrong

- **A mirror turns faces inside out.** `scale_to_size.py` already flips normals when the matrix's determinant is negative.
- **Custom normals are directions too.** `Mesh.transform` is documented for vertices; whether it also turns custom normals was not read. A rotated model with unrotated normals would be lit wrongly (inference; to test).
- **"Bottom" depends on up being right.** If a generator returns a model lying on its side, the lowest point is the wrong one. Nothing automatic knows which way is up for a prop.
- **Tripo's own pivot option costs 10 credits** (`pivot_to_center_bottom` triggers the advanced convert price) and its orientation option has the silent-failure warning in section 5.

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Size | Metres (exists today) | |
| Turn about the up axis | 0°, 90°, 180°, 270°, or an angle | Fixes which side is the front. A person has to look to choose it |
| Stand upright | none, or a 90° turn about a ground axis | Only when the raw output lies on its side |
| Origin | bottom centre, centre, keep the file's | Bottom centre suits a prop that stands on a floor; a wall piece on a grid may want a corner |
| Sink into the ground | 0, or a small length | A rock looks placed when a little of it is below the floor |

## 12. Reducing triangles

The earlier note covers the three Decimate modes, remeshing and what the manual says of each. This adds the exact properties and what the documents say about UVs, seams and normals.

### The calls

**`bpy.types.DecimateModifier`**, added with `obj.modifiers.new(name, 'DECIMATE')`. Read from the binary:

| Property | Values | Default | Mode |
|---|---|---|---|
| `decimate_type` | `COLLAPSE`, `UNSUBDIV`, `DISSOLVE` | `COLLAPSE` | |
| `ratio` | 0 to 1 | 1.0 | Collapse: "Ratio of triangles to reduce to" |
| `use_collapse_triangulate` | bool | False | Collapse: "Keep triangulated faces resulting from decimation" |
| `use_symmetry`, `symmetry_axis` | bool; `X`, `Y`, `Z` | False, `X` | Collapse |
| `vertex_group`, `vertex_group_factor`, `invert_vertex_group` | | | Collapse: protect or favour parts |
| `iterations` | 0 to 100 | 0 | Un-Subdivide |
| `angle_limit` | 0 to π radians | 0.0873 (5°) | Planar: "Only dissolve angles below this" |
| `delimit` | any of `NORMAL`, `MATERIAL`, `SEAM`, `SHARP`, `UV` | empty | Planar |
| `use_dissolve_boundaries` | bool | False | Planar |
| `face_count` | read-only | | "The current number of faces in the decimated mesh" |

- **Applying it:** `bpy.ops.object.modifier_apply(modifier=name)` (it has `merge_customdata`, default True: "merge UV coordinates that share a vertex to account for imprecision in some modifiers"), or export with `export_apply=True`.
- **The same collapse as an Edit Mode operator:** `bpy.ops.mesh.decimate(ratio=...)`.
- **Target count to ratio:** "triangles are used when calculating the ratio", so `ratio = target / current triangles` (earlier note).
- **Triangulating:** `bpy.types.TriangulateModifier` (`quad_method` default `SHORTEST_DIAGONAL`, `ngon_method` default `BEAUTY`, `keep_custom_normals` default False), `bpy.ops.mesh.quads_convert_to_tris` (default `BEAUTY`), or `bmesh.ops.triangulate`. The exporter triangulates anyway.
- **Remeshing:** `bpy.ops.object.voxel_remesh()` reads its settings from the mesh (`remesh_voxel_size`, `remesh_voxel_adaptivity`, `use_remesh_fix_poles`, `use_remesh_preserve_volume`, `use_remesh_preserve_attributes`). `bpy.ops.object.quadriflow_remesh(mode='FACES', target_faces=4000, seed=0, use_preserve_sharp=False, ...)`. Both: "All data layers will be lost."

### What the documents say about UVs, seams and normals

- **Collapse has no seam protection.** `delimit` is listed by the manual under Planar only: "Seam: Does not dissolve edges marked as UV Seams", "UVs: Does not dissolve edges that are part of a UV map".
- **Collapse keeps UVs and bends them.** The manual is silent; the earlier note read the source and saw it in a trial.
- **An old report** says "Decimate eliminates vertices which have multiple UV mappings" ([35042](https://projects.blender.org/blender/blender/issues/35042), 2013, closed; single report, far older than the pinned version).
- **Custom normals after a collapse:** no document read says what happens to them.
- **Un-Subdivide** "is intended for meshes with a mainly grid-based topology". A generated triangle mesh is not that.
- **Planar** suits "forms comprised of mainly flat surfaces". Its angle limit is the one number: a higher limit merges faces that are less nearly flat.

### What can go wrong

Section 2 of the earlier note lists seven failure modes. The ones a setting can affect:

- Too low a ratio destroys the outline. There is no documented measure of how low is too low; the earlier trial measured distance to the original afterwards.
- Thin parts go first (inference from how collapse works; the manual says only "minimal shape changes").
- Reusing a normal map made for the dense mesh on the reduced one is an approximation.

### How Tripo output interacts

- **Asking Tripo for the count avoids this stage.** `face_limit` at generation is documented as a maximum; the P series as "strict". Then the stage is a check, not a reduction (inference).
- **Tripo's reduce step bakes** the old textures onto the new mesh by default. Blender's Collapse keeps the old UVs; any Blender remesh needs section 14's bake.
- **A dense H-series output** (hundreds of thousands of triangles; one hands-on run got 501,532 from an older model, earlier note) decimates in seconds by the earlier trial's timings.

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Method | none, collapse, planar | Collapse for any shape; planar only for flat-sided props, where it keeps edges crisp |
| Target triangles | A count, at most the profile's budget | Fewer is cheaper to draw and loses outline and small parts |
| Planar angle limit | 0° to 180°, default 5° | Higher removes more and flattens gentle curves |
| Planar: stop at | UV seams, sharp edges, material borders | Stopping at seams keeps the texture lined up and removes less |
| Symmetry | off, or an axis | Keeps a symmetric prop symmetric; wrong for anything that is not |

## 13. Finding and repairing defects

### The calls

Both routes exist for each defect. The `bmesh` names and operator defaults are **read from the binary**; the descriptions are from the manual's [Clean Up](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/mesh/cleanup.html), [Select All by Trait](https://docs.blender.org/manual/en/5.2/modeling/meshes/selecting/all_by_trait.html) and [Normals](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/mesh/normals.html) pages.

| Defect | Find | Repair | What the manual says |
|---|---|---|---|
| Duplicate vertices | `bmesh.ops.find_doubles(bm, verts=..., dist=...)` returns a map | `bmesh.ops.remove_doubles(bm, verts=..., dist=...)`; or `bpy.ops.mesh.remove_doubles(threshold=0.0001, use_centroid=True, use_sharp_edge_from_normals=False)`; or `WeldModifier` (`merge_threshold` default 0.001) | "Merges the selected vertices that are closer to each other than a certain distance." Sharp Edges option: "will add edge marks where needed so that sharp edges will remain sharp after merging" |
| Non-manifold edges | `BMEdge.is_manifold`, `is_boundary`, `is_wire`, `is_contiguous`; `BMVert.is_manifold`; or `bpy.ops.mesh.select_non_manifold(use_wire, use_boundary, use_multi_face, use_non_contiguous, use_verts)` | No single repair | "Boundaries: Selects edges at boundaries and holes. Multiple Faces: Selects edges that belong to three or more faces. Non Contiguous: Selects edges that belong to exactly two faces with opposite normals." |
| Loose vertices and edges | `BMVert.link_edges` empty; `BMEdge.is_wire`; `bpy.ops.mesh.select_loose()` | `bmesh.ops.delete(bm, geom=..., context='VERTS')`; or `bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=False)` | "Deletes the selected vertices, edges, and optionally faces that aren't connected to anything." |
| Floating parts | Walk connected pieces in `bmesh`; or `bpy.ops.mesh.separate(type='LOOSE')` and count the objects | Delete the pieces below a size | The manual describes the operator only. `RemeshModifier` has `use_remove_disconnected` with a `threshold` |
| Flipped faces | `BMEdge.is_contiguous` False marks a disagreement between neighbours | `bmesh.ops.recalc_face_normals(bm, faces=bm.faces)`; or `bpy.ops.mesh.normals_make_consistent(inside=False)` | "Flips the orientation of the selected faces where necessary, making them all point outward ... The mesh does not need to be a closed volume for this." "this operation does not affect custom split normals" |
| Zero-area faces, zero-length edges | `BMFace.calc_area()`, `BMEdge.calc_length()` | `bmesh.ops.dissolve_degenerate(bm, dist=..., edges=bm.edges)`; or `bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)` | "Collapses any selected edges that are shorter than a certain length. This also results in the removal of small faces. If two vertices are near to each other but are not connected by an edge, they will not be merged" |
| Holes | Loops of boundary edges | `bmesh.ops.holes_fill(bm, edges=..., sides=0)`; or `bpy.ops.mesh.fill_holes(sides=4)` | "Fills each hole in the selected geometry with a face." "Sides: ... if a hole has more edges than this number, it will not be filled. Set to 0 to fill all holes." |
| Faces inside the object | `bpy.ops.mesh.select_interior_faces()` | Delete them | "Selects faces that may have been accidentally created inside the mesh ... faces with \"abnormal\" neighbors (multiple neighbors connected to the same edge)" |
| Faces passing through each other | `mathutils.bvhtree.BVHTree.FromBMesh(bm)` then `tree.overlap(tree)`: "Find overlapping indices between 2 trees" | `bpy.ops.mesh.intersect(...)` cuts them; a voxel remesh removes them and the UVs with them | Voxel remesh gives a mesh with "no inner (self-intersecting) geometry" |
| Anything invalid | | `Mesh.validate()` | "return True when the mesh has had invalid geometry corrected/removed" |

Operator defaults worth noticing: the merge and dissolve thresholds default to 0.0001 (a tenth of a millimetre once the model is in metres) and range from 0.00001 to 10; `fill_holes` defaults to holes of at most 4 sides, not all holes.

### The 3D Print Toolbox

- **It does not ship with Blender 5.2.2.** The bundled add-on folder holds thirteen add-ons and it is not one; `bpy.ops.mesh` has no `print3d` operator (read from the binary).
- **It is an extension:** [3D Print Toolbox](https://extensions.blender.org/add-ons/print3d-toolbox/), version 1.4.1 of 2026-08-05, GPL, for "Blender 4.2 LTS and newer". Its page: "Check for bad geometry and fix it with Make Manifold."
- Tripo's cleanup article and the one published counted test of Tripo output (earlier note) both use it.
- Its counts (non-manifold edges, zero-area faces, intersecting faces) can each be taken with the `bmesh` properties in the table above, with no extension (inference from what those properties are; the toolbox's source was not read to confirm it counts the same way).

### What can go wrong

- **Order matters.** Tripo's article gives "merge duplicate vertices, delete floaters, fill holes, recalculate normals", and reduction after that. Merging first is what turns separate sheets into one surface; before it, every sheet edge counts as a boundary (earlier trial).
- **A merge distance that is too large** joins vertices across a thin gap or collapses a thin part. It is a length, so it only means something after the model has been scaled to its size (inference: run this after `scale_to_size`, or scale the threshold).
- **"Outside" is ambiguous on a broken mesh.** The operator works without a closed volume, but on separate sheets or pieces inside the body the result may differ piece by piece (inference; not tested).
- **Recalculated faces and stored normals disagree.** The operator "does not affect custom split normals", and the importer has stored custom normals (section 10). After flipping faces the stored normals still point the old way. A repair stage has to clear them (`bpy.ops.mesh.customdata_custom_splitnormals_clear()`, poll True) or import without them (inference from the two documented facts).
- **Deleting floaters deletes intent.** A prop may properly consist of separate pieces. A size threshold cannot tell a stray fragment from a small real part; a person at the shape review can.
- **A filled hole has no texture of its own.** The manual does not say what UVs a fill face gets. On a prop with one large open underside, the fill is one many-sided face.
- **Nothing here closes a mesh in general.** The only tool the manual describes as producing a manifold mesh is the voxel remesh, which costs the UVs.

### How Tripo output interacts

- **Tripo's own description of the category** (vendor blog, [2026-07-07](https://www.tripo3d.ai/blog/how-to-clean-up-ai-generated-3d-models-in-blender)): "AI 3D outputs are messy by nature: dense triangle soup, loose bits, holes, flipped normals, and bad topology." It is written about AI output in general and aimed at printing; it shows no counts for Tripo's own files.
- **Counted, once:** 6 and 31 non-manifold edges, and thousands of zero-area faces, in Tripo's reduced output of one model (hands-on, earlier note). Its verdict: "After merging vertices, the mesh becomes usable."
- **A game asset need not be closed.** A boundary edge under a rock that sits on the ground is never seen. Which of these defects a target profile should check is the owner's decision; this section says only how each can be counted.
- **Tripo's paid route for holes** is segment (40 credits) then complete (30 or 50).

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Merge distance | 0 (off), or metres; Blender's default is 0.0001 | Larger closes more cracks and risks thin detail |
| Remove loose vertices and edges | on, off | Safe: they draw nothing |
| Remove small separate pieces | off, or a threshold (share of the largest piece's faces, or a size in metres) | Removes fragments; can remove a real small part |
| Make faces point outward | on, off | Fixes dark faces; needs stored normals cleared |
| Remove zero-area faces | off, or a length; default 0.0001 | Safe at small lengths |
| Fill holes | off, up to N sides, all | Closes gaps; filled faces are untextured and a large one is ugly |
| Remove interior faces | on, off | Saves triangles nobody sees; the test is a guess by the manual's own wording ("may have been") |

## 14. UVs and textures

The earlier note covers Smart UV Project, Unwrap, Pack Islands, the bake types, the cage and the margin, and timed them. This adds detection, the operator defaults, and images.

### Detecting missing or overlapping UVs

- **Missing:** `len(mesh.uv_layers) == 0`, or in the file itself no `TEXCOORD_0` (which `kiln/glb.py` can see without Blender).
- **Overlapping:** `bpy.ops.uv.select_overlap()`, "Select all UV faces which overlap each other", then count the selection. It is an Edit Mode operator; whether it runs with no UV editor open was not tested. The alternative is to test UV triangles against each other in Python.
- **Outside the 0 to 1 square, or wasted space:** read `mesh.uv_layers[0].data` directly. `python3 -m kiln.measure` already reports UVs and texel density.
- Overlap is not always a defect: mirrored halves that share texture space overlap on purpose. It is a defect for baking.

### Making new UVs

`bpy.ops.uv.smart_project`, read from the binary:

| Property | Default | Meaning |
|---|---|---|
| `angle_limit` | 1.15192 radians (66°), up to 89° | "Lower for more projection groups, higher for less distortion" |
| `island_margin` | 0.0 | "Margin to reduce bleed from adjacent islands" |
| `margin_method` | `SCALED` | `SCALED`, `ADD`, `FRACTION` |
| `area_weight` | 0.0 | "Weight projection's vector by faces with larger areas" |
| `rotate_method` | `AXIS_ALIGNED_Y` | |
| `correct_aspect` | True | |
| `scale_to_bounds` | False | |

Others: `bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001, ...)` with methods `ANGLE_BASED`, `CONFORMAL`, `MINIMUM_STRETCH`; `bpy.ops.uv.pack_islands(margin=0.001, rotate=True, shape_method='CONCAVE', ...)`; `bpy.ops.uv.average_islands_scale()`.

**The consequence for existing textures:** a new unwrap replaces where every face looks in the image. The old textures then show the wrong pixels everywhere. New UVs always mean a bake from the old layout to the new (inference from what a UV map is; Tripo's article says the same: "Cleaning destroys textures: re-unwrap and bake if you need the look back").

### Baking

`bpy.ops.object.bake`, read from the binary:

| Property | Default | Note |
|---|---|---|
| `type` | `COMBINED` | Also `DIFFUSE`, `NORMAL`, `ROUGHNESS`, `EMIT`, `AO` and others. No metallic type (earlier note) |
| `pass_filter` | empty | For `DIFFUSE`, `{'COLOR'}` gives the surface colour without lighting |
| `margin` | 16 | Pixels. `margin_type`: `EXTEND` on the operator, `ADJACENT_FACES` in the scene's bake settings |
| `use_selected_to_active` | False | True to bake one object onto another |
| `cage_extrusion`, `max_ray_distance` | 0.0, 0.0 | |
| `normal_space` | `TANGENT` | With `normal_r='POS_X'`, `normal_g='POS_Y'`, `normal_b='POS_Z'`, as the glTF manual asks |
| `target` | `IMAGE_TEXTURES` | "Bake to the image data-block associated with the active and selected Image Texture node" |
| `save_mode` | `INTERNAL` | |
| `width`, `height` | 512 | "external only"; an internal bake uses the size of the target image |
| `uv_layer` | empty | "UV layer to override active" |

What a headless bake needs:

- **Cycles:** `scene.render.engine = 'CYCLES'`. With that set, `bpy.ops.object.bake.poll()` is True in background mode (read from the binary). The earlier trial's bakes all returned `FINISHED`.
- **No display and no GPU are needed.** The device defaults to `CPU`. A GPU has to be switched on in Cycles' preferences by the script, which factory settings leave empty; the earlier trial did so.
- **A target:** "Baking requires a mesh to have a UV map, and either a Color Attribute or an Image Texture node with an image to be baked to." The image node must be the active one in the material.
- **A sample count.** "Cycles uses the render settings (samples, bounces, …) for baking." Under factory settings `scene.cycles.samples` is **4096** and denoising is on (read from the binary). The earlier trial used 4. A script that does not set it will be very slow for no gain on a colour pass (inference).
- **Memory:** "There is a CPU fixed memory footprint for every object used to bake from."

### Resizing and re-encoding images

Through `bpy.data.images`, read from the binary:

- `Image.size`, `channels`, `depth`, `is_float`, `file_format`, `packed_file`, `is_dirty`, `colorspace_settings`, `alpha_mode`.
- `Image.scale(width, height)`: "Scale the buffer of the image, in pixels".
- `Image.save(filepath='', quality=0, save_copy=False)`, `Image.save_render(filepath, scene=None, quality=0)`, `Image.pack()`.
- `file_format` values include `PNG`, `JPEG`, `WEBP`, `OPEN_EXR`, `TARGA`, `TIFF`, `AVIF`. The build has WebP support compiled in.
- New in 5.2: the `imbuf` module converts between formats with "access to image quality and compression" (release notes; not explored further).

**The trap.** The exporter writes an unchanged image's original bytes (section 10). Its own source carries the comment "Warning, img size change doesn't make it dirty, see T95616", and the tracker report it names ([95616](https://projects.blender.org/blender/blender/issues/95616), closed 2022-05-03) describes a rescaled image whose copy "has wrong size (the original image size, not the current one)". So `Image.scale()` followed by an export may write the full-size original. Whether it does in 5.2.2 for a packed image from a GLB was not tested. A resize stage has to be checked by measuring the output file, which `kiln.measure` does (inference).

### What can go wrong

- Everything in the earlier note's section 2: ray misses, seams from automatic unwrapping, hundreds of small islands (317 and 560 in its trial), lines at low texel density.
- **Colour space.** The manual says images for metallic, roughness and normals "should have its Color Space set to Non-Color". A new bake target that is left as sRGB stores those numbers wrongly (inference from the quoted rule).
- **Shrinking a normal map** averages directions; nothing documented renormalises them.
- **Format for alpha.** JPEG has no alpha channel. `MISSION.md` puts transparent plants out of scope for now.

### How Tripo output interacts

- **Tripo can do the resize at a price:** convert with `texture_size` and `texture_format` is 10 credits, default `4096` and `JPEG`.
- **Tripo's UVs:** `export_uv` is on by default; convert has `pack_uv` ("Pack all UVs into a unified layout"). Nothing is documented about seams or islands. Tripo's own article on engine import says of AI output in general that "overlapping shells, excessive texel density variation, and missing UVs for certain parts of the mesh are common" (earlier note).
- **Baked-in lighting** is the generator's to fix (`delight`, section 5). Blender has no operator that removes light from a colour texture.
- **`extreme` is 8K.** Four 8K maps are far beyond anything the pit profile's budget measurement considered (inference from `learn/research/pit-budget-measurement.md`'s texture sizes).

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Texture size | A power of two up to the profile's budget, per map or for all | Smaller saves memory and blurs up close; the profile's closest viewing distance sets the need |
| Format and quality | keep, JPEG at a quality, WebP at a quality, PNG | PNG is exact and large; JPEG and WebP are small and lossy |
| New UVs | keep, Smart UV Project | Keeping avoids a bake; new UVs fix overlaps and bad layouts and cost a bake |
| Smart UV angle limit | 1° to 89°, default 66° | Lower: more, smaller islands with less stretch, and more seams |
| Island margin | 0 to 1 | More margin wastes texture space and stops colours bleeding between islands |
| Bake margin | 0 to 64 pixels, default 16 | Too small shows lines at seams; too large overruns small islands |
| Cage extrusion | A length in metres | Too small misses detail; too large hits the wrong surface |
| Bake samples | A count; the trial used 4 | More is slower; colour and roughness passes do not need many |

## 15. Normals and shading

### What exists in 5.2.2

- **No auto smooth.** `Mesh.use_auto_smooth` and `Mesh.auto_smooth_angle` do not exist (read from the binary). The 4.1 release notes: "The base state of meshes is now the same as having \"Auto Smooth\" on with an angle of 180 degrees in older versions: Face corner \"split\" normals are calculated when there is a mix of sharp and smooth elements. Custom normals are used if available."
- **Sharpness is data on edges and faces.** Set it with:
  - `Mesh.set_sharp_from_angle(angle=...)`: "Reset and fill the \"sharp_edge\" attribute based on the angle of faces neighboring manifold edges". No operator, no context.
  - `bpy.ops.object.shade_smooth_by_angle(angle=0.5236, keep_sharp_edges=True)`: default 30°.
  - `bpy.ops.mesh.set_sharpness_by_angle(angle=0.5236, extend=False)` in Edit Mode.
  - `Mesh.shade_smooth()` and `Mesh.shade_flat()`; `bpy.ops.object.shade_smooth(keep_sharp_edges=True)`, `shade_flat`.
- **`bpy.ops.object.shade_auto_smooth(angle=0.5236)`** adds a modifier instead. The manual: "This is a geometry nodes asset that is included in the bundled \"Essentials\" asset library." Whether that asset loads in a factory-settings background session was not tested. The calls above do not need it.
- **Reading normals:** `Mesh.corner_normals`, `Mesh.vertex_normals`, `Mesh.polygon_normals`, `Mesh.normals_domain` (`POINT`, `FACE`, `CORNER`), `Mesh.has_custom_normals`.
- **Custom normals:** `Mesh.normals_split_custom_set(normals)`, `Mesh.normals_split_custom_set_from_vertices(normals)`; remove with `bpy.ops.mesh.customdata_custom_splitnormals_clear()`. The manual: stored "as the `custom_normal` Attribute on the face corner Domain".
- **Weighted Normal modifier**, `bpy.types.WeightedNormalModifier`: `mode` (`FACE_AREA` default, `CORNER_ANGLE`, `FACE_AREA_WITH_ANGLE`), `weight` (1 to 100, default 50: "A value of 50 means all faces are weighted uniformly"), `thresh` (0.01), `keep_sharp` (False), `use_face_influence` (False). It "changes the custom normals of a mesh" and "can be useful to make some faces appear very flat during shading". The manual's mesh page says custom normals are "mostly used in game development, where it helps counterbalance some issues generated by low-poly objects".

### What can go wrong

- **Stored normals outlive the shape they were made for.** The importer stores the file's normals as custom normals (section 10). Flip and Recalculate do "not affect custom split normals". Merging has an option to "add edge marks where needed so that sharp edges will remain sharp". What Collapse does to them is undocumented. A pipeline that edits the surface and keeps the generator's normals is leaning on behaviour nobody has written down (inference).
- **The clean alternative costs the generator's shading.** Clearing custom normals and setting sharpness by angle gives normals that match the edited mesh, and throws away whatever smoothing the generator intended.
- **Sharp edges cost vertices.** The exporter splits a vertex wherever its normal differs between faces: "flat-shaded edges may result in moderately higher vertex counts". A fully flat-shaded model has about three vertices per triangle.
- **The angle is one number for the whole object.** 30° suits a crate; a rock at 30° gets faceted wherever the generator made a crease.
- **Tangents depend on normals and UVs.** Change either after a normal map was made and the map is slightly wrong (earlier note, failure modes 5 and 6).

### How Tripo output interacts

Nothing in Tripo's documentation says whether its models arrive smooth-shaded, flat-shaded or with deliberate hard edges. The earlier note records one preprint measuring that open generators round off hard edges on machine-like objects. If Tripo does the same, sharpening by angle in Blender marks shading and cannot restore a rounded corner's shape (inference).

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Shading | keep the file's normals, smooth by angle, all smooth, all flat | Keeping is faithful to the generator and fragile under editing; by angle is predictable |
| Angle | 0° to 180°, Blender's default 30° | Lower gives more hard edges and more vertices |
| Weighted normals | off, face area, corner angle, both | Makes large flat faces of a low-poly prop look flat; no use on a rock |

## 16. Materials

### What the exporter reads

From the [glTF manual](https://docs.blender.org/manual/en/5.2/addons/import_export/scene_gltf2.html), "Exported Materials":

- "The exporter supports Metal/Rough PBR (core glTF) and Shadeless (`KHR_materials_unlit`) materials. It will construct a glTF material based on the nodes it recognizes in the Blender material."
- **Base colour:** "determined by looking for a Base Color input on a Principled BSDF node. If the input is unconnected, the input's default color ... is used". An Image Texture node connected there becomes the base colour texture.
- **Metallic and roughness:** "read from the Principled BSDF node"; as an image, blue and green of one image through a Separate Color node, colour space Non-Color.
- **Normal map:** Image Texture into a Normal Map node into the Normal input. "The Normal Map node must remain on its default property of Tangent Space". Its strength is exported.
- **Emission:** an image or colour on the Emission input. "If any component of emissiveFactor is > 1.0, `KHR_materials_emissive_strength` extension will be used."
- **Occlusion:** only through the `glTF Material Output` node group.
- **Double-sided:** "For materials where only the front faces will be visible, turn on Backface Culling ... The inverse of this setting controls glTF's `DoubleSided` flag."
- **Alpha mode:** "The exporter determines the alpha mode automatically from the nodes connected to the Alpha socket." Opaque when alpha is always 1; mask when a Math node rounds it; blend otherwise.
- **Factors:** a Math multiply node or a Mix multiply node after a texture becomes a glTF factor.
- **UV transforms:** a Mapping node exports as `KHR_texture_transform`. "Not all glTF readers support multiple UV maps or texture transforms."
- **What it ignores:** any node arrangement it does not recognise. The earlier note recorded the consequence: procedural materials have to be baked to images first.

### Reading and setting values from a script

- Find the node: `[n for n in mat.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled']`.
- Read or set an unconnected value: `node.inputs['Roughness'].default_value`. Check `node.inputs['Roughness'].is_linked` first; a linked input ignores its default value.
- The Principled BSDF's inputs in 5.2.2 (read from the binary), with defaults: `Base Color` (0.8, 0.8, 0.8, 1), `Metallic` 0.0, `Roughness` 0.5, `IOR` 1.5, `Alpha` 1.0, `Normal`, `Emission Color` (1, 1, 1, 1), `Emission Strength` 0.0, `Specular IOR Level` 0.5, `Coat Weight` 0.0, `Sheen Weight` 0.0, `Transmission Weight` 0.0, and others. Scripts written for older versions may use other names for some of these; which, and since when, was not looked up.
- Material flags: `mat.use_backface_culling`, `mat.surface_render_method`, `mat.alpha_threshold`.
- `mat.use_nodes` is deprecated: "Currently it always returns `True` and setting it has no effect."

### What can go wrong

- **Rewiring breaks the copy-through.** A material left exactly as imported lets the exporter copy its images. Change the wiring and the exporter may rebuild and re-encode an image (section 10).
- **A value hidden behind a texture.** Setting `default_value` on a linked input changes nothing in the output.
- **Extensions Bevy may not draw.** Blender exports clearcoat, sheen, transmission and others as glTF extensions. Which of them Bevy 0.19.1 renders was not checked. A generated prop is unlikely to use them; a bought asset may.
- **Double-sided is a cost and a cover-up.** It hides flipped faces by drawing both sides.

### How Tripo output interacts

- With `pbr` on, Tripo documents four maps: "`base_color`, `metallic`, `roughness`, `normal`". No occlusion, no emission.
- **Not documented:** how many materials one model has; whether metallic and roughness come as one image in glTF's layout or as two; whether the material is marked double-sided; what the metallic and roughness factors are. One existing Tripo GLB and `python3 learn/assets/glb_inspect.py` would answer all four.
- One hands-on run found an older Tripo model returned "one colour texture" only, because PBR was off by default in that reseller's settings (earlier note). The v3 API defaults `pbr` to true.

### Settings for the asset record

| Setting | Values | Trade-off |
|---|---|---|
| Metallic override | none, or 0 to 1 | A generator may mark a painted prop as metal; forcing 0 fixes its look and discards the map |
| Roughness override | none, or 0 to 1 | A flat value replaces the map and saves a texture |
| Drop the normal map | on, off | Saves a texture; loses fine surface detail at 0.5 m |
| Double-sided | keep, on, off | On hides inside-out faces and draws more; off shows them |
| Merge materials | keep, one | One material is one draw call; merging several needs a bake to one image |

## 17. What is known of a Tripo mesh, against the stages

| Characteristic | Source and grade | Stage it meets |
|---|---|---|
| Dense by default: "adaptive topology" up to 1.5 million triangles; 501,532 in one run of an older model | API reference (fact); hands-on, one asset (earlier note) | Reduce, unless `face_limit` or the P series is used |
| "dense triangle soup, loose bits, holes, flipped normals, and bad topology" | Tripo's blog, about AI output in general (vendor blog) | Repair |
| Non-manifold edges (6 and 31) and thousands of zero-area faces after Tripo's own reduction | Hands-on, one model, counts shown (earlier note) | Repair |
| "AI-generated UVs can be chaotic. Overlapping shells, excessive texel density variation, and missing UVs" | Tripo's blog, about the category (earlier note) | UVs and textures |
| Vertices stored separately wherever a UV or normal changes | glTF itself (fact) | Import: join vertices |
| Lighting from the picture in the colour texture unless texture v3.5 is used | API reference (fact, by inference from two sentences) | None in Blender; set at generation |
| Faces +X; up is +Y; size arbitrary | API reference, Help Center (fact) | Scale, orientation, origin |
| Four PBR maps; texture size unstated below 8K | API reference (fact) | Textures |
| Number of materials, meshes and images; smooth or flat shading; packed or separate metallic and roughness | Not documented | Import, materials, normals |
| Details invented on the unseen side | Hands-on, one asset, older model (earlier note); the Help Center's "AI hallucination from missing back info" (vendor) | None; a shape review matter, or multiview |

## 18. What is unknown, and the smallest experiment for each

Nothing below needs a decision first. The first six cost nothing.

1. **What kiln's request would look like.** `tripo make reference.png -p face_limit=<n> -p texture_version=v3.5-20260815 --seed 1 --dry-run --json`. By the CLI's documentation this makes "zero network calls" and "works without an API key". It shows the model chosen and which parameters the CLI strips.
2. **Which way Blender turns glTF's axes.** Write a one-triangle GLB with `tests/glb_fixture.py` whose point sits on +Z, import it through `tools/bl`, print the vertex. Then export and compare with the input.
3. **Whether `Image.scale()` reaches the exported file.** Import a textured GLB, scale one image, export, and read the image size with `python3 -m kiln.measure`. Repeat with a save and reload in between.
4. **Whether each repair call runs in background mode and returns `FINISHED`.** A `tests/glb_fixture.py` mesh with one known defect of each kind (a duplicated vertex, a flipped face, a zero-area triangle, a missing face, a loose piece), each `bmesh` call in turn, and a count before and after.
5. **What `Mesh.transform` and Collapse do to custom normals.** Import with stored normals, rotate or decimate, and compare `mesh.corner_normals` with freshly computed ones.
6. **What a raw output holds.** `python3 learn/assets/glb_inspect.py` and `python3 -m kiln.measure` on any Tripo GLB: materials, images and their sizes, whether metallic and roughness share an image, vertex count against triangle count (which shows flat or smooth storage), separate pieces. `learn/specimens/` holds two models from the first attempt, kept "only as files to inspect"; whether they came from Tripo is for the owner to say.
7. **Whether `delight` changes anything.** One reference image with a visible shadow, generated twice with the same `model_seed`: once on defaults, once with `texture_version=v3.5-20260815`. Compare the base colour textures. Two generations, 60 credits at H-series list price.
8. **Whether the image checklist matters.** The same object as two pictures, one that meets section 3's checklist and one that breaks two items (a hard shadow, the object small in the frame), same seed, both taken into kiln and put through the shape review. Two generations.
9. **Whether multiview fixes the back.** One picture alone against the same picture plus a back view. Two generations, plus 10 credits if the back view is made by `image-to-multiview`.
10. **H series with `face_limit`, H series with `smart_low_poly`, or P1**, for one prop at the profile's budget. Three generations, 120 credits. Measure triangles, defects from experiment 4's counts, and look.
11. **Whether an extension can be used offline.** Only if the 3D Print Toolbox is wanted: download it once by hand, install it into `.blender-user/` from the file, and see whether `tools/bl` loads it under `--factory-startup`.

## What could not be verified, and where sources disagreed

**Could not be opened or was not read**

- Tripo Studio itself. It needs an account. Everything about Studio is from the Help Center and the vendor's articles.
- A Help Center article the checklist page refers to, "How to Use Image Generation Templates". No link to it was found on the page.
- The P Series and Splat Series tabs of the API pricing page, which are drawn in the browser. P1 prices are from the P1 model page; P2 prices from the changelog. The P2 model page returned no content.
- Reference pages for `POST /v3/models/refine` and `POST /v3/models/stylize`. None exists in the v3 documentation's full text.
- A third-party cleanup guide (Neural4D, a competitor of Tripo) whose search summary said Tripo output has "inverted normals on interior cavities and detached geometry fragments". The page was not opened; the claim is unverified.
- A third-party page whose search summary said "PNG files with transparency are ideal" for Tripo. Not opened.
- Individual operator pages of the Blender Python API reference. Property names and defaults were read from the pinned binary instead; descriptions are the binary's own.
- The glTF add-on's GitHub issue tracker. Only Blender's own tracker was read, four issues by number.
- The source of the 3D Print Toolbox.
- Bevy's rendered documentation on docs.rs. The same doc comments were read in the 0.19.1 crate source on this machine; links are to the matching files on GitHub.
- Tripo's terms of service were not re-read. The Help Center's summary of them matches the earlier notes.

**Not established**

- Camera angle, perspective against orthographic, and transparent backgrounds for `image-to-model`. Tripo publishes nothing on any of them.
- Maximum resolution for an `image-to-model` input.
- The pixel size of `standard` and `detailed` textures.
- Which API setting the Studio's "Smart Mesh" is.
- What `refine` does, and what it costs.
- Whether Tripo's `image-to-model` removes a background by itself.
- Which way "left" and "right" are in multiview.
- Blender's forward axis for an imported glTF file, from documentation.
- Whether any `bpy.ops` call named in sections 11 to 16 runs in background mode with no editor area, beyond those the earlier note's trial ran (import, export, Decimate, Smart UV Project, Pack Islands, bake).
- Whether the "Smooth by Angle" modifier asset loads under factory settings.
- What Collapse, `Mesh.transform` and merging do to custom normals.
- What UVs a filled hole gets.
- Whether Bevy 0.19.1 and `kiln/glb.py` read meshopt-compressed or Draco-compressed files, and which material extensions Bevy draws.
- What the importer does with a file whose textures are WebP only.
- Whether an installed extension loads under `--factory-startup`.
- Any measurement that Tripo's image or prompt advice improves results.

**Sources disagree**

Tripo against itself is in section 8. Beyond that:

- **Blender's manual against its own add-on.** The mesh-structure page says only the FBX and Alembic importers bring in custom normals. The glTF importer in the same download calls `normals_split_custom_set_from_vertices`.
- **The bake margin's default.** `EXTEND` on the operator, `ADJACENT_FACES` in the scene's bake settings (both read from the binary).
- **Triangulation defaults.** `SHORTEST_DIAGONAL` on the modifier, `BEAUTY` on the operator.
- **"Keep original" textures.** The manual says the option is for the separate-file format only; the exporter's code reuses original bytes for a GLB whenever the image is unchanged, without the option.
- **Tripo's blog against Tripo's API on prompts with pictures and on materials in prompts** (section 8).
- **Game face counts.** Tripo's API reference says "Game-ready assets: 50,000 – 100,000"; `profiles/pit.toml` holds a placeholder of 20,000, and Tripo's own low-poly models stop at 20,000. These are different meanings of "game-ready", not a factual conflict.
- **The earlier note against this one.** It listed `delight` as "default true; removes baked-in lighting". That is the parameter's text, but on default settings the texture model that reads it is not the one used.

## Sources

All read 2026-10-08.

**Tripo, API and CLI**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt) and [index](https://developers.tripo3d.com/llms.txt): text-to-model, image-to-model and multiview-to-model (H and P series), text-to-image, image-to-image, image-to-multiview, edit-multiview, texture, convert, retopology, segmentation, completion, import, files, models and versions, changelog, billing
- [API pricing](https://developers.tripo3d.com/en/pricing) (H series tab and the tables below it)
- [Model page, v3.1](https://developers.tripo3d.com/en/models/v3-1) and [model page, P1](https://developers.tripo3d.com/en/models/p1)
- [`tripo-cli` npm registry record](https://registry.npmjs.org/tripo-cli) and the package `tripo-cli-0.5.2.tgz`: `skill/SKILL.md`, `skill/commands/generate.md`, `skill/commands/process.md`, `skill/commands/make.md`, `skill/examples/game-asset.md`, `skill/common-errors.md`, `dist/ai/experts.js`, `dist/knowledge/scenarios.js`, `dist/knowledge/models.js`, `dist/knowledge/params.js`
- [Legacy API v2 documentation](https://docs.tripo3d.ai/): the retirement notice, the image-to-model page and the upload page

**Tripo, Help Center**

- [Help Center index](https://www.tripo3d.ai/help)
- [How to Get Better Image-to-3D Results](https://www.tripo3d.ai/help/features/how-to-get-better-image-to-3d-results)
- [How to use the Image to 3D feature?](https://www.tripo3d.ai/help/features/how-to-use-the-image-to-3d-feature), modified 2026-08-25
- [How to use the Text to 3D feature?](https://www.tripo3d.ai/help/features/how-to-use-the-text-to-3d-feature), modified 2026-08-25
- [What is Smart Mesh?](https://www.tripo3d.ai/help/features/what-is-smart-mesh), modified 2026-08-25
- [Why did my generation fail or get stuck?](https://www.tripo3d.ai/help/features/why-did-my-generation-fail-or-get-stuck)
- [Can Tripo generate high-quality textures for 3D models?](https://www.tripo3d.ai/help/features/can-tripo-generate-high-quality-textures-for-3d-models)
- [How to Export and Import to DCC Tools](https://www.tripo3d.ai/help/features/how-to-export-and-import-to-dcc-tools)
- [I have subscribed to Tripo Studio paid membership. Can I use the Tripo API?](https://www.tripo3d.ai/help/api-plugins/tripo-studiotripo-api)
- [Can I use the model for commercial purposes?](https://www.tripo3d.ai/help/privacy-policy/can-i-use-models-commercially) and [How to Use Tripo Models Commercially](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)

**Tripo, tutorials and blog (vendor blog)**

- [5 Professional Tips to Generate High-Quality 3D Models from Images with Tripo AI](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tips)
- [Tripo AI Tutorial: A Complete Guide on How to Convert Images to 3D Models for Beginners](https://www.tripo3d.ai/tutorials/tripo-ai-image-to-3d-tutorial)
- [How to Master Prompt Engineering for Text to 3D Models](https://www.tripo3d.ai/blog/text-to-3d-prompt-engineering), 2025-04-20, modified 2026-01-27
- [Prompt Engineering for Better 3D Shapes: A Practitioner's Guide](https://www.tripo3d.ai/blog/explore/prompt-engineering-for-better-3d-shapes), 2026-03-10
- [How to Clean Up AI-Generated 3D Models in Blender (Step by Step)](https://www.tripo3d.ai/blog/how-to-clean-up-ai-generated-3d-models-in-blender), 2026-07-07, modified 2026-08-04

**Blender**

- The pinned Blender 5.2.2 binary, through `tools/bl`: operator and type properties, add-on list, session state
- The pinned build's glTF add-on source, `5.2/scripts/addons_core/io_scene_gltf2`: `__init__.py`, `io/imp/gltf2_io_gltf.py`, `blender/imp/mesh.py`, `blender/exp/material/encode_image.py`, `blender/exp/material/image.py`, `blender/exp/primitive_extract.py`
- Manual, 5.2: [glTF 2.0](https://docs.blender.org/manual/en/5.2/addons/import_export/scene_gltf2.html), [command-line arguments](https://docs.blender.org/manual/en/5.2/advanced/command_line/arguments.html), [Decimate modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/decimate.html), [Remesh modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/remesh.html), [Remeshing](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html), [Triangulate modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/triangulate.html), [Clean Up](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/mesh/cleanup.html), [Merge](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/mesh/merge.html), [Select All by Trait](https://docs.blender.org/manual/en/5.2/modeling/meshes/selecting/all_by_trait.html), [Normals](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/mesh/normals.html), [mesh structure](https://docs.blender.org/manual/en/5.2/modeling/meshes/structure.html), [Smooth by Angle modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/normals/smooth_by_angle.html), [Weighted Normal modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/normals/weighted_normal.html), [UV editing](https://docs.blender.org/manual/en/5.2/modeling/meshes/editing/uv.html), [render baking](https://docs.blender.org/manual/en/5.2/render/cycles/baking.html), [object origin](https://docs.blender.org/manual/en/5.2/scene_layout/object/origin.html), [apply](https://docs.blender.org/manual/en/5.2/scene_layout/object/editing/apply.html)
- Python API reference, 5.2: [operators](https://docs.blender.org/api/5.2/bpy.ops.html), [using operators (gotchas)](https://docs.blender.org/api/5.2/info_gotchas_operators.html)
- Release notes: [4.1 modeling](https://developer.blender.org/docs/release_notes/4.1/modeling/), [4.1 Python API](https://developer.blender.org/docs/release_notes/4.1/python_api/), [4.2 extensions](https://developer.blender.org/docs/release_notes/4.2/extensions/), [5.0 Python API](https://developer.blender.org/docs/release_notes/5.0/python_api/), [5.1 Python API](https://developer.blender.org/docs/release_notes/5.1/python_api/), [5.2 Python API](https://developer.blender.org/docs/release_notes/5.2/python_api/)
- [3D Print Toolbox on Blender Extensions](https://extensions.blender.org/add-ons/print3d-toolbox/)
- Tracker, single reports: [95616](https://projects.blender.org/blender/blender/issues/95616), [35042](https://projects.blender.org/blender/blender/issues/35042), [71313](https://projects.blender.org/blender/blender/issues/71313), [blender-addons 74721](https://projects.blender.org/blender/blender-addons/issues/74721)

**Khronos and Bevy**

- [glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), sections 3.4 and 3.7.2.1
- Bevy 0.19.1, read in the crate source on this machine: [`bevy_gltf/src/convert_coordinates.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/convert_coordinates.rs), [`bevy_gltf/src/loader/mod.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs), [`bevy_transform/src/components/transform.rs`](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_transform/src/components/transform.rs)

**This repo**

- [`game-mesh-kiln-or-generator.md`](game-mesh-kiln-or-generator.md), sections 2 and 7, for the Decimate modes, unwrap operators, baking, failure modes and the trial
- [`llm-vs-3d-generators.md`](llm-vs-3d-generators.md) and [`claude-tripo-blender-workflows.md`](claude-tripo-blender-workflows.md), for Tripo's prices, terms, seeds, CLI behaviour and the hands-on reports of its output
- `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, `profiles/pit.toml`, `kiln/run.py`, `kiln/blender_scripts/scale_to_size.py`, `tools/bl`, `tools/install_tools.sh`, `Cargo.toml`

## Method

Research was done on 2026-10-08. Tripo's API documentation was downloaded as its full-text file and searched directly. The `tripo-cli` package was downloaded from the npm registry into its own directory and its files were read as text; nothing in it was run. Help Center pages, tutorials, blog posts, the pricing page and the model pages were downloaded as HTML and reduced to text locally, not through a summariser; dates are from the pages' embedded data where present. Seven web searches were used to find pages; nothing is cited from a search summary, and two claims that appeared only in summaries are listed as unverified.

The pinned Blender was started twice through `tools/bl` with scripts kept outside the repo. They printed properties of operators, modifiers and data types, the list of shipped add-ons, the state of a factory-settings background session and the docstrings of `bmesh` functions. They made one material in memory and set the render engine in memory to read a default; nothing was saved and no model file was opened. `tools/bl` writes Blender's own bookkeeping into `.blender-user/`, as it does on every run. The glTF add-on's Python source inside the pinned download was searched for the behaviours quoted. Manual and release-note pages were downloaded and searched for the passages quoted; they were not read end to end. Four tracker issues were read through the tracker's API. Bevy's statements were read in the 0.19.1 crate source already present in the local Cargo registry.

No generator API was called, no account was created, no credit was spent, no operator was run on a mesh, and no file from the `first-attempt` tag was used. Only this file was written.
