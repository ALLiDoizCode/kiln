# Evaluation: Cloudflare Clef, for look decisions in `kiln`

Research date: 2026-10-05. Audience: the owner. Question as asked: "would clef from cloudflare speed up and help us given that there is a lot of decisions being made about how the asset looks".

## Answer

**No, not for the bottleneck the question points at; at most try one small, bounded experiment.** Clef is real and the name is right: two open-weight "decision models" Cloudflare released on 2026-10-01 that take some text, up to four images and a list of typed questions, and return a probability for each allowed answer in well under a second, with no words. What it makes fast (the answer to a yes/no or pick-one question) is not what is slow here: our time goes into 30 to 90 minute agent runs, a one-minute gate, and the owner looking at one comparison at a time, and a bare probability is exactly the "verdict with no evidence" that `review-renders` and `asset-review` forbid. Nothing Cloudflare has published shows it can judge whether a render looks good.

Confidence that this is the product meant: **high**. It is a Cloudflare product with that exact name, four days old on the day of the question, and "decision model" matches the wording "a lot of decisions being made".

**How to read the evidence labels**

- **[raw]**: I read the bytes myself on 2026-10-05: the raw model card, the licence file, the Hugging Face API, the published JSON schema, or the blog's own text pulled with `curl`.
- **[summarised fetch]**: a Cloudflare page read through a tool that summarises it. The figures are Cloudflare's, but I did not see the page's raw text.
- **[inference]**: my reasoning. Nothing was run: no model was downloaded, no account was made, no image left this machine.
- **not verified**: collected in [section 7](#7-not-verified).

---

## 1. Which product this is

Searching for "Cloudflare clef" finds it directly; there was no need to guess at a misspelling.

- Launch post: "Introducing Clef: our open-source decision models, and new RL fine-tuning platform". <https://blog.cloudflare.com/clef-decision-models/> **[raw]**
- Changelog entry dated 2026-10-01. <https://developers.cloudflare.com/changelog/post/2026-10-01-clef-workers-ai/> **[summarised fetch]**
- Model pages: <https://developers.cloudflare.com/workers-ai/models/clef/> and <https://developers.cloudflare.com/workers-ai/models/clef-flash/> **[summarised fetch]**
- Weights: <https://huggingface.co/Cloudflare/clef> and <https://huggingface.co/Cloudflare/clef-flash>, both created 2026-09-30, public and not gated. **[raw]** (Hugging Face API)

Other things called Clef that are *not* meant: the old Clef two-factor login company (not Cloudflare; recalled from memory, not looked up), and Cloudflare's unrelated products with nearby names. None of them has anything to do with decisions or images, so I did not research them.

---

## 2. What it is

**A classifier you configure with questions, not a chat model.** You send a "state" (text or JSON), optionally images, and 1 to 64 questions. Each question is one of three types, and the reply is numbers only:

| Type | You give | You get back |
|---|---|---|
| `noul` | a yes/no question | the probability that the answer is yes |
| `choice` | 2 to 255 named options, each with a description | a probability per option, the chosen one, a confidence |
| `score` | 2 to 10 ordered levels of a rubric, lowest first | a probability per level and a probability-weighted score |

Source: the published input schema, <https://developers.cloudflare.com/workers-ai/models/clef/schema-input.json> **[raw]**

- **It writes no text.** "There is no free-form text generation and no output parsing." <https://huggingface.co/Cloudflare/clef/raw/main/README.md> **[raw]** It cannot say *why* it answered as it did, or point at a part of an image.
- **Two sizes.** Clef is 27 billion parameters, post-trained from Qwen3.8-27B; Clef-flash is 9 billion, from Qwen3.5-9B. Each is the Qwen model plus a small extra "joint schema head" that scores every option of every question in one pass. Same model card **[raw]**
- **Images.** "it has a vision encoder so it's able to take in images and classify visual content." <https://blog.cloudflare.com/clef-decision-models/> **[raw]** The hosted API takes at most 4 images, PNG, JPEG or WebP, 4 MiB and 16 megapixels each, 8 MiB decoded in total, embedded in the request; "Remote URLs are not accepted." Schema, as above **[raw]**
- **Speed.** Cloudflare reports a median of 209.3 ms for Clef and 38.8 ms for Clef-flash. Changelog, as above **[summarised fetch]**. These are Cloudflare's own measurements on its own benchmark run.
- **Input size.** 65,536 tokens hosted (model pages **[summarised fetch]**); the local code defaults to 16,384 (model card **[raw]**).

### Status, licence and price

- **Status: released.** The model pages and changelog describe it as generally available on Workers AI. **[summarised fetch]** It is four days old.
- **Licence: Apache-2.0**, for both models. `LICENSE` file at <https://huggingface.co/Cloudflare/clef/blob/main/LICENSE> and the `license: apache-2.0` field of both model cards **[raw]**. That allows running it locally, for any purpose, at no charge.
- **Hosted price:** Clef $0.240 per million input tokens (21,818 neurons); Clef-flash $0.090 per million (8,182 neurons). Workers AI gives 10,000 neurons a day free and charges $0.011 per 1,000 after that. <https://developers.cloudflare.com/workers-ai/platform/pricing/> **[summarised fetch]** By my arithmetic the free allowance is about 0.46 million input tokens a day on Clef and about 1.2 million on Clef-flash **[inference]**. At our volume the hosted price is effectively nothing; price is not what decides this.
- **Fine-tuning is not a product you can sign up for yet.** "we are also offering fine-tuning services — first as a hands-on partner with our forward-deployed engineer (FDE) team, and then later as a self-serve fine-tuning platform for customers to train and redeploy the model onto Cloudflare." Blog, as above **[raw]** It is an interest form (<https://www.cloudflare.com/resource/clef-rl-interest>), it learns from traffic you route through Cloudflare's AI Gateway, and no price is given. Blog **[summarised fetch]**

### What it has been shown to be good at

The model card's results table has 37 rows: tool calling, intent routing, retrieval, contract and medical text inference, multiple-choice knowledge tests, forecasting, phishing detection. <https://huggingface.co/Cloudflare/clef/raw/main/README.md> **[raw]** The worked examples are an invoice, a support ticket and "Is the receipt total legible?".

**No row measures judging the quality, style or appeal of a picture, or comparing two pictures.** The blog's summary of benchmarks names no image benchmark either **[summarised fetch]**. So the image ability is announced, not demonstrated, for anything like our use **[inference]**.

It also loses on the harder reasoning rows to the model it is compared with (GPQA Diamond 48.0 against 78.3, BBH 73.7 against 92.9, MMLU-Pro 65.9 against 82.7). Model card **[raw]** It is a fast sorter, not a careful thinker.

---

## 3. Would it help this project

The stated bottleneck: many decisions about how an asset should look are made slowly, one comparison image at a time, by agents and by the owner. Taking each place a decision is made:

| Where time goes now | Would Clef change it | Why |
|---|---|---|
| An agent run, 30 to 90 minutes | No | That time is an agent writing and re-running build scripts. Clef writes nothing. **[inference]** |
| A gate, up to a minute; the suite, 2 to 5 minutes | No | That is Blender, Bevy and the checks. No model call is involved. **[inference]** |
| A reviewer agent reading a contact sheet | No, and it would break the rule | `review-renders` requires every line to be an **observation**: something "a second reader could confirm or refute from the same tile", and says "looks good" is a verdict to be replaced by the measurement behind it. `asset-review` drops "a finding with no evidence". A probability of 0.73 is a verdict with no evidence and no tile. |
| The blind comparison (`review_aids.py blind`) | In form yes, in substance unproven | "Which side serves the brief better, left or right" is a `choice` question over one image. But the skill asks the reviewer for the reason "with evidence from the image", which Clef cannot give, and we have no sign its pick would match the owner's. |
| The owner looking at a sheet and saying yes or no | No | "Appeal and style fit are their call" (`review-renders`). A model that agreed with the owner would have to be trained on the owner's choices, and the fine-tuning service is not open (section 2). |
| Choosing among many seeds of a generator | **Possibly** | This is the one place the shape fits: many candidates, the same question of each, an answer that only needs to rank. See below. |

**The one plausible use: sorting candidates before a human or an agent looks.** `tools/try_seeds.py` already builds an asset from a run of seeds and says which pass gate L1. A cheap ranker could order the survivors' thumbnails by "reads as a boulder / a wedge / a lump" so that only the best few go on a sheet. That would cut how many comparisons are looked at, which is the real cost. It is a pre-sort, never a gate: CLAUDE.md's rule is that a new check is not finished until a test shows it failing on a broken input, and a model's probability that drifts with image size or wording does not meet that bar. **[inference]**

**The mismatch in one sentence:** Clef's selling points are milliseconds and cents per decision at high volume; `kiln` makes perhaps tens of look decisions a day, and each is slow because a picture has to be built and someone has to look, not because the answer takes long to compute. **[inference]**

---

## 4. What it would cost

**Running it here (nothing leaves the machine).** This is what the copyright rule requires for anything touching a benchmark pack or a reference image.

- The weights are 55.0 GB for Clef and 19.1 GB for Clef-flash, in 16-bit form. Hugging Face API file sizes **[raw]** The model card says only "Tested with `torch` 2.11 and `transformers` 5.10.2 on a single H200", a data-centre card. **[raw]**
- This machine has an RTX 3080 with 10 GB of video memory and 31 GB of RAM (`nvidia-smi`, `free`, 2026-10-05) **[raw]**. Neither model fits as published. Clef will not fit at any usual compression; Clef-flash might at 4-bit **[inference]**.
- Compressed community builds exist: 17 listed for Clef and 27 for Clef-flash, including GGUF builds from `ggml-org` and `bartowski`. Hugging Face API **[raw]** Whether those builds carry the extra scoring head, and so give the same answers as the real model, I did not check (section 7).
- The same card renders the Bevy tiles. A model held in video memory competes with every gate run in every worktree. **[inference]**
- Setup: a Python environment with torch and transformers pinned beside `.tools/`, a 19 GB download, and code loaded from the model repository (`joint_schema_model.py`, tagged `custom-code`), which is running someone else's Python and wants reading first. Model card **[raw]**

**Running it on Cloudflare.**

- Needs a Cloudflare account and an API token; then it is one HTTPS call from this machine. It does **not** need our work to move onto Cloudflare's platform: Blender, Bevy and the gates stay here. Model page example **[summarised fetch]**
- Images go to Cloudflare, embedded in the request. Cloudflare's statement: "our guarantee that we don't read, store, or train on your requests or responses (unless you want to use our fine-tuning product...)". Blog **[raw]** That is a promise in a blog post; I did not find or read the contract terms behind it (section 7).
- **The rule that decides it:** reference images and third-party benchmark packs must stay local. Our whole method of judging is ours *beside* a benchmark. Hosted Clef could therefore only be shown our own renders alone, which removes the comparison that the judgement rests on. Renders of our own assets are fine to send; the repo is public. **[inference]**

**Lock-in: low.** Apache-2.0 weights, and a request format shared with a competing product ("The Clef API is fully compatible with Jev and SystemOne", model card **[raw]**). The lock-in is in fine-tuning, which captures data through Cloudflare's gateway and redeploys onto Cloudflare. Blog **[raw]**

**A cost that is easy to miss:** a number that looks like a measurement. A probability from a model nobody here has calibrated against the owner's eye would sit in reports beside real measurements and be read as one. **[inference]**

---

## 5. Recommendation

**Do not adopt it. If curious, one experiment of about an hour, hosted, with our own renders only.**

The experiment, and what would change my mind:

1. Take pairs the owner has already ruled on (an approved sheet and the rejected build before it, rebuilt from the earlier commit; I did not count how many such pairs the history holds), rendering the same view of each. Our renders only, no benchmark, no reference image.
2. For each pair, make the blind side-by-side with `tools/review_aids.py blind` and ask hosted Clef one `choice` question: which side serves this brief better, left or right, with the brief's own sentences as the state. Twenty pairs is well inside the free daily allowance **[inference]**.
3. Count how often its pick is the owner's. Run each pair twice with the sides swapped: a model that picks "left" both times is guessing.

If it agrees with the owner on fewer than about 17 of 20, or flips with the side, stop: it is no better than what we have. If it agrees, the next step is only the seed pre-sort of section 3, and only with a local build so that benchmark views can be included. Either way it stays out of the gates. **[inference]**

Reasons not to do even this now: the product is four days old, the result decides nothing we are blocked on, and the same hour spent on the things below attacks the bottleneck directly.

## 6. What would address the bottleneck instead

All **[inference]**; none of this was tried.

- **Look at many at once, not one at a time.** `tools/variants_sheet.sh` already puts variants beside a benchmark. A sheet of a dozen seeds or a dozen values of one threshold, from which the owner picks two or three, settles in one look what now takes a dozen. The slow thing is comparisons per decision.
- **Decide a parameter once per family, not once per asset.** ADR 13 already puts the generator and the brief in the family. Each look decision the owner makes should land as a number in the family's brief and a check, which is what the retrospective in `asset-review` is for; the measure of progress is how few decisions the next variant needs.
- **Cheaper pictures while exploring.** A flat-coloured thumbnail of each candidate straight from Blender, without painting, export or the Bevy tile, as `try_seeds.py` builds them, is enough to throw out most seeds before the full gate is spent on any.
- **If a model is to rank pictures, a local image-similarity score against the benchmark** (an embedding distance from a small vision model that fits in 10 GB) is closer to the real question, "is ours near the benchmark", keeps every copyrighted image on this machine, and gives the same number every time. It would still be an aid, not a gate.

---

## 7. Not verified

- **That Clef can judge how good a render looks at all.** Nothing was run. No published benchmark covers it.
- **What the `cfcolor` row of the results table measures** (Clef 66.0%). The name suggests colour; I found no definition.
- **How an image is counted in input tokens**, and so the exact price of a call with four images. The model page does not say.
- **Whether the compressed community builds include the joint schema head** and reproduce the real model's answers, and whether Clef-flash at 4-bit fits in 10 GB with images. The memory figures in section 4 are estimates from file sizes.
- **"Generally available"** as a status: from a summarised reading of the changelog and model pages, not from raw text.
- **The contract behind "we don't read, store, or train"**: I read the blog sentence, not Cloudflare's terms of service or data-processing terms.
- **Cloudflare's benchmark numbers**: "our internal run", by the model card's own description. No independent run was looked for; news write-ups were not used.
- **Who the comparison model's maker is and what "SystemOne" specifies**: taken from Cloudflare's description only.
- **Whether the vLLM, SGLang and Docker commands shown on the Hugging Face page work for this model.** Those are the site's generic snippets; the model needs its own custom code and the blog links an open vLLM pull request, so I would not assume it.

## 8. Sources

- Cloudflare blog, launch post: <https://blog.cloudflare.com/clef-decision-models/> **[raw]** for the sentences quoted, **[summarised fetch]** otherwise
- Cloudflare changelog, 2026-10-01: <https://developers.cloudflare.com/changelog/post/2026-10-01-clef-workers-ai/> **[summarised fetch]**
- Workers AI model pages: <https://developers.cloudflare.com/workers-ai/models/clef/>, <https://developers.cloudflare.com/workers-ai/models/clef-flash/> **[summarised fetch]**
- Input schema: <https://developers.cloudflare.com/workers-ai/models/clef/schema-input.json> **[raw]**
- Workers AI pricing: <https://developers.cloudflare.com/workers-ai/platform/pricing/> **[summarised fetch]**
- Model cards: <https://huggingface.co/Cloudflare/clef/raw/main/README.md> **[raw]**; <https://huggingface.co/Cloudflare/clef-flash> **[summarised fetch]**
- Licence file: <https://huggingface.co/Cloudflare/clef/blob/main/LICENSE> **[raw]**
- Hugging Face API, 2026-10-05: `api/models/Cloudflare/clef`, `api/models/Cloudflare/clef-flash` (dates, licence, file sizes), and `api/models?filter=base_model:quantized:Cloudflare/<model>` (compressed builds) **[raw]**
- Fine-tuning interest form: <https://www.cloudflare.com/resource/clef-rl-interest> (linked from the blog; not opened)
- This project: `CLAUDE.md`, `CONTEXT.md`, `docs/adr/0003-assets-as-code-via-blender-cli.md`, `docs/adr/0009-painted-soft-edged-style.md`, `docs/adr/0013-families-pieces-and-variants.md`, `.claude/skills/asset-review/SKILL.md`, `.claude/skills/review-renders/SKILL.md`, `tools/try_seeds.py`
