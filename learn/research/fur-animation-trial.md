# Animating a generated creature whose fur turns into spikes: research and six prototypes

Done 2026-10-08 on the development machine, with the pinned Blender 5.2.2 and Bevy 0.19.1. **One route works end to end and its files exist:** a script turns the generated calm model into a model that also holds a spiked shape, Bevy 0.19 blends between the two, and the same file carries a skeleton and a clip. The walk itself is the part that is not solved.

This is a research note and a look ahead. `learn/MISSION.md` puts characters, rigging and animation out of scope until static assets are solved, and nothing here changes that: no stage, check or glossary term is added to kiln. Everything it produced is in [`fur-animation-trial/`](fur-animation-trial/). The creature is someone else's artwork, used for a private test: every model and picture made from it is in folders git ignores.

## The question

Can a generated creature (round, four-legged, furry, with a snout and a raised tail) be animated for a game on Bevy, with Blender as the authoring tool, by one person who is new to 3D? Two parts: can the body move (walk, attack), and can the fur change between a soft state with a few short spikes and a state with long hard spikes all over the back and tail, some of which are shot as projectiles?

## How to read this

- **Measured** means it was run here today and the output is in [`fur-animation-trial/`](fur-animation-trial/).
- **Looked at** means a picture was rendered in Bevy by the probe (section 5, prototype D) and read by the author of this note, an AI model. The pictures are in `fur-animation-trial/pictures/`, not in git.
- **Spec**, **Docs** and **Source** mean the glTF 2.0 specification, Blender's or Tripo's documentation, and Bevy 0.19.1's source code in `~/.cargo/registry/src/`.
- **Read in full** and **read through a summary**: the web reading was done by a second agent. Pages it downloaded and searched itself are marked "in full". Pages it could only reach through a tool that summarises are marked "summary"; a quoted phrase from those may not be exact.
- **Inference** means this note's reasoning. Every estimate of hand work is inference.
- **One model is an observation, not a rate.** Each prototype ran on one generation of one creature.
- Kiln's own words are used as `CONTEXT.md` defines them.

### Terms used here

The earlier notes define mesh, triangle, vertex, UV, normal map, base colour, loose part, open edge and the glTF validator. Terms added here:

- **Skeleton** (Blender: **armature**): a tree of **bones** (glTF: **joints**) inside the model. A bone is not drawn; it is a position and a rotation that vertices can follow.
- **Skin weights:** for each vertex, which bones it follows and how strongly. A vertex on a knee follows the upper and the lower leg bone half each, so the knee bends smoothly. A model with a skeleton and skin weights is **rigged**; making them is **rigging**.
- **Clip** (Blender: **action**; glTF: **animation**): a recorded motion, stored as the rotation of each bone at a list of times.
- **Retargeting:** playing a clip made for one skeleton on another skeleton with different bone names or proportions.
- **Morph target** (also **blend shape**; Blender: **shape key**): a second position for every vertex of the same mesh. A number called the **weight** blends from the base shape (0) to the target (1). The mesh keeps the same vertices, triangles and UVs; only positions (and normals) change.
- **Vertex shader:** the small program the graphics card runs for every vertex to decide where it is drawn. A custom one can move vertices by a formula.
- **Instancing:** drawing one small mesh (one spike) many times at different places, instead of storing every copy.
- **Thickness** (as used in prototype A): how far it is from a point on the surface, straight in through the model, to the other side. A spike is thin; a body is thick.
- **Bind:** to give a mesh skin weights for a skeleton.

## Summary

### What is possible

- **The fur change, as a morph target, works here from the calm model alone, with no hand modelling.** A script finds the spikes of `orb_h31_req20000.glb` by thickness (117 of them), stretches each along its own axis, and stores the result as a morph target. The exported `.glb` passes the glTF validator with 0 errors and is 1.0 MB larger than the same file without targets. Looked at in Bevy at weights 0, 0.25, 0.5, 0.75, 1 and 2, it reads as the fur stiffening into long straight spikes.
- **Bevy 0.19.1 plays it.** With the features `crates/asset_view` already builds (`"3d"`), Bevy loaded the morph targets, drew every weight asked for, played a clip that animates the weight, and drew a model with a skin, four morph targets and a bone clip at once. Measured with a throwaway program of 263 lines.
- **The body can be bound to a skeleton automatically.** Blender's automatic weights succeeded on the 19,007-triangle model twice: on Tripo's 27-bone skeleton and on a 13-bone skeleton placed by script. 10 of 9,486 vertices were left unbound both times. Bent 25 to 30 degrees at the legs, the skin follows; the belly is dragged along with the legs, which a person would have to correct or accept.
- **A shot spike is a separate small object.** Nothing in glTF or Bevy animates a part of a mesh leaving it. The game spawns a spike mesh at the place of a bone or of a named point and moves it. This was not built; it is confirmed from engine documentation only (section 2).

### What did not work, or is not practical for one person yet

- **No walk clip was obtained.** Tripo's Auto Rig was run by the owner in the web app (rigging type "Other", 20 credits, preset "Walk"). None of the three exports holds a clip. Both `.glb` exports hold a skin in which every vertex follows one bone, and Bevy and Blender both draw the first lying on its side. The `.fbx` export holds a skeleton that fits the creature (four legs, a tail of five bones, head bones), but its weights cover only the head and the tail: no vertex follows any of the 14 leg bones, and bending a leg bone moves nothing (measured). Why is not known.
- **A walk made by hand is the real cost.** The clip in the prototypes is a leg swing written in ten lines to test the skin. It is not a walk. A walk and an attack that look right are an animator's work; the cheap routes (Tripo's preset, a library of quadruped clips retargeted) are untested here.
- **A morph target can only lengthen spikes that exist as geometry.** On the H3.1 model most of the fur on the top of the back is drawn in the texture, not modelled. Spiked, the sides, the face ruff and the tail bristle; the top of the back stays bare.
- **Melting the spikes away on the one-surface model looks poor.** The reverse direction (prototype A1) leaves crumpled stubs. It is not needed: the generated model is already the calm state.
- **Swapping between two generations would not read as one animal.** The spiked generation that arrived during this work is a different animal in a different stance, and grey because its reference drawing was grey.

### What I would try first, and why

Morph targets on the calm model, made by `scripts/a_morph_fused.py`, with the spiked weight driven by the game. It is the only route that needed nothing but the model already chosen, it survives every step measured (Blender export, validator, Bevy, alongside a skin), and its cost is one megabyte. The next step is not about fur: it is getting one usable walk clip onto the skeleton, by asking Tripo's export again in a different way or by retargeting a ready-made quadruped walk (section 7).

If the bare back matters, try the same script idea on a loose-pieces model (prototype B). There each spike is its own piece, so it can be stretched cleanly and also shrunk to nothing inside the body. The P2.0 model has 154 such spikes, back included; it costs the cleaner mesh and the normal and roughness maps that only H3.1 returns.

## 1. The options

"Hand work" assumes someone new to 3D with Claude writing the scripts; it is inference throughout. "Tested here" points at the prototype.

| Technique | What it needs from the model | glTF 2.0 | Bevy 0.19 | Cost at run time | Hand work | Verdict |
|---|---|---|---|---|---|---|
| **Skeleton and skin for the body** | One mesh; a skeleton placed inside it; weights. A closed, single-piece mesh binds best | Core: skins, up to 4 bones per vertex in one set (Spec) | Yes: `SkinnedMesh`, at most 256 joints per skin, 4 per vertex (Source). Played here | One matrix per bone per frame; small | Binding: none, automatic. Clips: the open problem | Possible. Binding practical; clips not yet |
| **Morph targets for the fur** | The same vertices in the same order in both shapes. Nothing else | Core: positions, normals, tangents; animated through `weights` (Spec) | Yes: `MorphWeights`, at most 256 targets, with skinning (Source). Played here | Memory: 48 bytes per vertex per target on the graphics card (Source); here 0.7 MB per target. Targets at weight 0 are skipped | None once the script exists; a person chooses three numbers | **Practical. Try first** |
| **A bone per spike** | Each spike's vertices bound to its own bone | Core | Fits: 117 spikes plus 27 body bones is under 256. Not tested | 117 more matrices; small | Script as for morph targets, plus a clip or code to scale 117 bones | Possible. Worth it only if single spikes must move alone |
| **Vertex shader pushing masked vertices** | A mask per vertex (vertex colour or a second UV) and, for straight spikes, each spike's axis per vertex | Carries the mask (`COLOR_0`); not the effect | Custom `MaterialExtension` with its own vertex shader. No official example with skinning (issue #13988, summary). Not tested | Least memory | A shader to write and keep working across Bevy versions | Possible, not practical: it is one morph target done the hard way |
| **Separate spike meshes, instanced** | A spike mesh; a list of points and directions on the body | Nodes, or `EXT_mesh_gpu_instancing` (ratified extension, not core) | Entities with the same mesh and material are batched (release notes, summary). Loader support for the extension not checked. Not tested | A few hundred small draws batched; small | Script to place points; each spike must follow a bone when the body moves | Possible. The way to add spikes where none are modelled |
| **Spikes as projectiles** | One spike mesh as its own small model | A separate file or mesh | Spawn an entity at a bone's place | Negligible | Game code | Practical; the owner's assumption is right |
| **Swapping two models** | Two models that agree in size, stance and colour | Two files | Show one, hide the other. An open bug loses morph weights when an entity is hidden and shown (#25966, summary) | Both in memory | An effect to hide the change; two rigs, two sets of clips | Not with two separate generations (prototype F) |
| **Real-time fur as shells or hair cards** | A fur texture; a custom transparent material | No | Nothing built in; a custom material drawing the mesh many times | The mesh is drawn once per layer. Not measured | Not tried | Not tried. Strands, the next row, were built instead |
| **Real-time fur as strands** (every hair its own geometry) | A smooth body with UVs and a base colour picture. Nothing in the file is about fur | No: the hairs are grown when the model loads | A custom `Material` with its own vertex shader. Built here (section "Strand fur") | Measured: 80,000 hairs add about 0.3 ms to a 2.5 ms frame on the RTX 3080, and 59 MB of vertices | One program of 1,363 lines and a shader of 304. Following a skeleton is not built | **Works on a body that does not bend, and is what the owner asked for.** This row replaces an earlier "not worth considering now" |

Notes on the table:

- **Order of morphing and skinning.** The specification requires morph displacements to be applied before skinning. Bevy's shader does that: `morph_vertex` runs first, then `skin_model` (`bevy_pbr-0.19.1/src/render/mesh.wgsl`). So a spike stretched by a morph target is then carried by the tail bone it belongs to. Looked at: it is (sheet E, lower row).
- **How many targets.** The specification asks a viewer to support at least eight morphed attributes, which with positions and normals is four targets. Bevy's limit is 256 (`MAX_MORPH_WEIGHTS`, `bevy_mesh-0.19.1/src/morph.rs`).
- **Normals and tangents.** Both can morph in glTF and in Bevy. Bevy stores all three for every target whether or not the file has them.
- **Real-time fur.** Shell fur draws the surface again and again, each copy pushed a little further out and showing only dots of a fur texture, so the layers read as strands (Lengyel and others, 2001; summary). It was not built. The first version of this note said real-time fur was "not worth considering now", because the creature's inked fur already reads as fur in a still picture. That verdict was wrong for what the owner wants, which is hairs that move and turn into spikes: a texture can do neither. Strand fur was then built and measured; see the section "Strand fur".

## 2. What the sources say

### glTF 2.0 (Spec, read in full)

- Morph targets may move `POSITION`, `NORMAL` and `TANGENT`; "All primitives MUST have the same number of morph targets in the same order", and every target has the same vertex count as the base. A tangent target has no fourth component.
- Default weights are `mesh.weights`; with none, zero. Target names are a convention (`mesh.extras.targetNames`), not in the specification.
- "The number of joints that influence one vertex is limited to 4 per set". More sets are allowed but a viewer "MAY support only a single set".
- A clip can drive four things only: a node's translation, rotation, scale, and its morph weights. So a glTF clip cannot hide a spike or recolour it. `KHR_node_visibility` and `KHR_animation_pointer` are ratified extensions that would; Bevy's support for the second is an open issue (#20554, from a search listing).

### Bevy 0.19.1 (Source, read locally)

- **Features.** The `"3d"` feature that `crates/asset_view` already asks for includes `morph`, `morph_animation`, `gltf_animation` and so `bevy_animation` (`bevy-0.19.1/Cargo.toml`, lines 2605 to 2633). `default-features = false` in the workspace does not remove them. Nothing has to be added to play morph targets, skins or clips.
- **Loading.** The glTF loader puts a `MorphWeights` component on the node and `MeshMorphWeights::Reference` on each primitive (`bevy_gltf-0.19.1/src/loader/mod.rs`, lines 1688 to 1885). It copies the file's default weights. It adds an `AnimationPlayer` to the root of an animated hierarchy.
- **Limits.** 256 targets; 256 joints per skin (`bevy_pbr-0.19.1/src/render/skin.rs`); four joints per vertex (`Mesh::ATTRIBUTE_JOINT_INDEX` is four 16-bit numbers).
- **Cost.** A target is stored as position, normal and tangent, 48 bytes per vertex (`MorphAttributes`). The shader loops over the targets for every vertex and skips those at weight 0.
- **Release notes and issues (summary).** 0.19 stores morph targets in the mesh and can batch morphed meshes. Open issues the reading agent listed: morph weights lost when an entity is hidden and shown again (#25966); no example of a custom vertex shader with skinning and morphing (#13988).

### Blender 5.2 (Docs, read in full; behaviour measured)

- The glTF exporter has "Shape Keys", "Shape Key Normals" and "Shape Key Tangents" as separate options, and writes shape-key values as an animation of weights.
- Animation mode "Actions" writes one glTF animation per action, and is the mode "useful if you are exporting for game engine".
- "Bone influences": the exporter keeps 4 per vertex. Measured: it warned "There are more than 4 joint vertex influences. The 4 with highest weight will be used (and normalized)".
- Rigify, Blender's rig builder, has ready skeletons for "Basic Quadruped", "Cat", "Wolf" and "Horse". Not tried.
- The manual describes "With Automatic Weights" (the "bone heat" method) and does not list why it fails. Forum posts (search snippets only) blame overlapping vertices and non-manifold or loose parts.

### Tripo's rigging and animation (Docs, read in full; and what came back)

- **Vendor claim, API documentation.** The rig check is free and recommends a rig type: `biped`, `quadruped`, `hexapod`, `octopod`, `avian`, `serpentine` or `aquatic`. Rig model `v2.5-20260210` is the one for "non-humanoid creatures"; the default model is biped only. For a quadruped there is one preset: `preset:quadruped:walk`. No idle, run or attack. Output is `glb` or `fbx`. Price: rig 25 credits, each animation 10. Nothing about morph targets.
- **Vendor claim, weaker.** A Tripo blog snippet says the studio offers "walk, run, idle, and others" for quadrupeds. The page returned 403 and the API text contradicts it.
- **Measured.** The web app charged 20 credits for the rig, offered "Walk" only for rigging type "Other", and its exports are as prototype E describes.
- **Untested.** The web app's "Describe a motion" (20 credits) and "Multi-stage Motion".

### Other riggers and ready-made clips (graded; none tried)

| Tool | Four legs? | Cost and licence | Source and grade |
|---|---|---|---|
| Mixamo | No, "bipedal humanoids only" | Free | Adobe FAQ; page returned 403, snippet only |
| AccuRig | No | Free | Reallusion forum, vendor post from 2023 (summary) |
| Meshy | "humanoid and quadruped" rigging; no quadruped presets found | Credits | First-party docs (summary) |
| Anything World | Yes | 20 free credits a month, 5 per model | Trade press from 2024 (summary); may be stale |
| Cascadeur | Quadruped tools marked "Alpha" | Free tier is non-commercial; Indie 8 USD a month | Vendor (summary) |
| Auto-Rig Pro (Blender add-on) | Yes, bones placed by hand; has a retargeting tool | 50 USD | Vendor store page (summary) |
| Quaternius animated animals | Six farm animals with Idle, Walk, Run, Jump, Death; no attack | CC0 | Author's page (summary) |

### How games do it (graded; thin)

- Engine documentation describes each building block, not this effect. Unreal: a morph target is "a snapshot of vertex locations for a specific mesh that have been deformed in some way"; its vertex-offset material functions take a greyscale mask "that controls how much the mesh's vertices will respond"; sockets are "dedicated attach points" on a skeleton. Unity: blend shape weights are set from code; a projectile is made with `Instantiate` at a position and then given a velocity. (All summary.)
- For swapping models, the only source found is a 2010 Unity forum answer: create the new model and destroy the old, or keep both and switch which is shown.
- **Not found:** any studio post or talk on quills, bristling fur or a swap hidden by an effect. The claim that this is "how games do it" rests on the building blocks being standard, which is inference.

## 3. Prototype A: a morph target from one fused surface

`scripts/a_morph_fused.py` on `orb_h31_req20000.glb` (19,007 triangles, one piece; 9,486 points once coincident ones are merged). Headless, 3 seconds. Output: `models/a_fused_morph.glb`, facts in `facts/a_fused_morph.json`.

### Finding the spikes

Two ways were tried and looked at as a painted mask (sheet `sheet_a_masks.png`).

| Method | What it marks | Verdict |
|---|---|---|
| Distance outside a Laplacian-smoothed copy, 10 or 30 passes | Spikes, but also the ridge where the back overhangs the belly, the snout, and with 30 passes the whole tail | Too many false marks |
| The same with Taubin smoothing (does not shrink), 100 passes | Only the tips of spikes | Misses most of each spike |
| **Thickness under 2 to 3.5 cm** | Spikes, whiskers and the tail's bristles; body, snout and legs untouched | Used |

Thickness is measured by looking from each vertex straight into the model and noting where the other side is; the middle value of a vertex and its neighbours is kept. Half the vertices are thicker than 30 cm and a quarter thinner than 4 cm, so there is a wide gap to put the threshold in. 1,683 vertices are marked. Joined into connected groups they make 139 groups, of which 117 are long enough to treat as a spike (the longest 15 cm). Vertices in the lowest third of the height are left alone, so the feet do not grow.

What it misses: low, wide bumps on the back (thick at the base), and everything that is only drawn in the texture.

### The four shapes

| Shape key | How | Vertices moved | Triangle pairs cutting each other (base: 4) | Triangles turned over | Edges stretched over 3 times |
|---|---|---|---|---|---|
| `soft_all` | Every vertex to its smoothed place, 10 passes | 9,443 | 10 | 561 | 83 |
| `soft_masked` | Spike vertices only, onto the smoothed copy | 1,541 | 1,324 | 416 | 91 |
| `spiked_push` | Spike vertices pushed away from the smoothed copy, 3 times as far | 1,593 | 891 | 393 | 493 |
| **`spiked_axial`** | Each spike stretched 3 times along the line from its root to its tip | 1,012 | 162 | 41 | 67 |

### What it looks like (looked at in Bevy)

- **`spiked_axial` at 1:** long, straight, clean spikes on the sides, the face ruff and the tail. Shading is right. The model grows from 0.73 by 0.97 by 0.98 m to 0.96 by 1.17 by 1.09 m. At weight 2 (five times the length) it is dramatic and still clean. This is the shape to keep.
- **In between (0.25, 0.5, 0.75):** a steady growth; no popping.
- **`spiked_push`:** jagged. Vertices on the two sides of a spike go different ways, and the tail tears into shards. Rejected.
- **`soft_masked`:** spikes shrink to crumpled stubs; the tail keeps a ragged outline. Passable at a distance, not close up.
- **`soft_all`:** the spikes melt, and so do the legs, the snout and the tail, which get thinner. The inked fur lines stay in the texture, so it still looks hairy. Blunt.
- **Texture stretch:** a spike three times as long has its texture stretched three times. On flat-coloured spikes this is not visible.
- **What is missing:** the top of the back. Spiked, it stays as bare as before.

### Settings a person or Claude would choose

Three numbers: the thickness below which something is a spike (2 to 3.5 cm worked; it should follow the model's size), the height below which nothing moves (a third), and the stretch factor (3). The weight can go past 1 at run time, so the factor need not be final.

## 4. Prototype B: a morph target from loose pieces

`scripts/b_morph_pieces.py` on the textured P1.0 and P2.0 models. Headless, 3 seconds each. Output: `models/b_pieces_p1_morph.glb`, `models/b_pieces_p2_morph.glb`; one row per piece in `facts/b_pieces_*.csv`.

The largest piece is the body. Every other piece is measured along its longest direction; one at least 2.5 times as long as wide, above the leg zone and touching the body is a spike. Its root is the end inside or nearest the body.

| | P1.0 | P2.0 |
|---|---|---|
| Pieces | 157 | 236 |
| Body | 8,883 triangles | 9,671 |
| Called spikes | 84 (4,055 triangles) | 154 (6,721) |
| Slender but in the leg zone (claws, leg fur) | 18 | 47 |
| Not slender (hooves, snout parts, tufts) | 54 | 31 |
| Spike length, shortest / middle / longest | 4.7 / 8.8 / 21 cm | 3.2 / 7.4 / 20 cm |
| Spikes whose root is inside the body | 73 of 84 | 139 of 154 |

Three shape keys: `retracted` (each spike shrunk to a point at its root), `extended` (3 times longer along its axis), `tail_only` (the same for spikes at the back only, to show groups can have their own key).

What it looks like:

- **`retracted`:** the cleanest soft state of the whole trial. The spikes vanish into the body and leave a smooth animal, because each root is under the body's surface. No stubs.
- **`extended`:** long straight spikes, back included. No triangle turns over and no edge stretches more than exactly 3 times, because each piece is scaled as a whole.
- **The tail does not change.** In both models the tail and its bristles are part of the body piece. `tail_only` moved nothing on P1.0 and 98 vertices on P2.0. The thickness method of prototype A would be needed for the tail: the two methods combine.
- **These models start with thousands of triangle pairs cutting each other** (3,631 and 2,918), since every spike is pushed through the body. That is how they are built; morphing does not make it worse.

Classification was not checked piece by piece; the painted mask (sheets `sheet_b_p1.png`, `sheet_b_p2.png`) shows spikes marked and hooves, snout and tail left alone, with some short tufts near the face left out.

## 5. Prototypes C and D: the file, and Bevy

### C. What the exported file holds

Read with `scripts/c_read_back.py`, which walks the JSON that `kiln/glb.py` returns (`facts/c_read_back.jsonl`).

| File | Bytes | Targets | Attributes morphed | Target data |
|---|---|---|---|---|
| A, no targets | 9,743,088 | 0 | | 0 |
| A, positions only | 10,028,216 | 4 | POSITION | 283,490 |
| **A, positions and normals** (what the scripts write) | 10,746,748 | 4 | POSITION, NORMAL | 1,001,426 |
| A, and tangents | 11,346,252 | 4 | POSITION, NORMAL, TANGENT | 1,360,502 |
| A, with a 2-second clip on one weight | 10,748,192 | 4 | POSITION, NORMAL | 1,001,426 |
| B (P1.0), no targets | 4,230,264 | 0 | | 0 |
| B (P1.0), positions and normals | 5,386,272 | 3 | POSITION, NORMAL | 1,154,395 |

- **One primitive, all targets on it, counts equal to the base** (14,957 vertices as stored for A; 27,438 for B).
- **Positions are stored sparsely** for the three targets that move few vertices: only the moved vertices are listed. Normals are stored for every vertex and are most of the cost. Dropping them saves 0.7 MB and would leave the stretched spikes shaded as if short; not looked at.
- **Target names survive** in `extras.targetNames`.
- **The validator: 0 errors** on every file written here (at most two warnings: no tangents stored, and a skinned mesh under a parent node).
- **A trap, found and fixed.** A shape key made from Python starts with value 1, and the exporter writes the values as the file's default weights. The first export opened with all four shapes applied at once. `furlib.add_key` now sets 0.
- **The exporter dropped** Tripo's `KHR_materials_volume` and `FB_ngon_encoding` extensions and re-packed the textures; the picture did not visibly change.

### C. What `python3 -m kiln.measure` does with such a file

It exits 0 and **reports the base shape as if nothing else were there.** Triangles, vertices, UVs and textures are right. Morph targets, skins and animations are not mentioned, and `notes` is empty. Two consequences:

- The bounding box is the calm shape's (0.73 by 0.97 by 0.98 m) although the spiked shape is 0.96 by 1.17 by 1.09 m.
- On Tripo's rigged `.glb` it reports an upright box, while Bevy and Blender draw that file lying on its side, because the box is taken from the stored positions and the skin turns them.

Report only; kiln was not changed.

### D. Bevy playback

`bevy_probe/` is a throwaway Cargo project outside the workspace: one file of 263 lines, the pattern of `review_pictures.rs`, depending on `crates/asset_view` by path for the scene, the light and the loader. It uses the workspace's `target` folder, so Bevy was not built again: the probe compiles in 3 seconds. No new crate was needed. It was a small job; the one obstacle was Bevy's limit on how many parameters a system may take (the first version had 21 and did not compile).

`morph_probe <model.glb> --out <folder> --frames "0;0.5;1"` sets the weights and writes one PNG per entry and view; `--clip N --times "0,0.5"` plays a clip instead. It prints what Bevy found in the file.

| Asked | Result |
|---|---|
| Does Bevy load the targets? | Yes: 1 node with morph weights, 4 targets (A); 3 (B) |
| Does the weight change the picture? | Yes, at every weight tried, including 2.0 and two targets at once |
| Does a clip of weights play? | Yes: the exporter's clip, sought to 0, 0.5, 1.0 and 1.5 s, shows the shape going and coming back (`sheet_d_clip.png`) |
| Skin, morph and bone clip together? | Yes: 1 skinned mesh of 28 joints, 4 targets, clip `pose_test`; the stretched spikes follow the bent tail |
| Time | 1.6 seconds for a run of 5 weights and 2 views (10 pictures), on the RTX 3080 |

No frame times were measured. The cost figures in section 1 are from the source, not from a stopwatch.

## 6. Prototypes E and F: the skeleton, and the second generation

### E. Tripo's Auto Rig, as exported

Both files arrived while this work was under way and were used. The owner's notes on how they were made are taken as given.

| Export | Bones | Skin weights | Clips | Drawn |
|---|---|---|---|---|
| `orb_h31_req20000_rigged_walk.glb` | 27 bone nodes, all without a position; the skin names 11 | All 14,957 vertices follow joint 0 at weight 1 | 0 | Lying on its side, half in the ground, in Bevy and in Blender. 3 validator errors |
| `orb_h31_req20000_walk2.glb` | 27 bone nodes, all without a position; the skin names 9 | All but one vertex on `bone_0` | 0 | Not rendered |
| `walk2_fbx/*.fbx` | 27, placed inside the creature | 7 groups: two of the head bones and the five tail bones. 3,561 of 9,486 vertices follow no bone. **No vertex follows any of the 14 leg bones** | 0 | Upright |

The FBX skeleton is a sensible one: a root and spine, four head bones, two front legs of four bones, a pelvis with two hind legs of three, and a tail of five ending at the tail's tip.

`scripts/e_tripo_rig.py` then tested it (`facts/e_tripo_rig.json`):

| | Tripo's weights | Blender's automatic weights on Tripo's skeleton |
|---|---|---|
| Bones with vertices | 7 of 27 | 27 of 27 |
| Vertices following no bone | 3,561 | 10 |
| Bend one leg 30 degrees: vertices moved | **0** | 2,383 |
| Bend three tail bones 15 degrees: vertices moved | 1,563 | 2,259 |
| Shape keys from prototype A kept | not applicable | all four |

- **Why 27 bones and 7 groups** is not known. The skin in the `.glb` exports names the same head and tail bones, so the leg weights are missing before export, or the rig never made them. The "Walk" the owner saw in the web viewer is in none of the files.
- **Automatic weights did not fail** on this mesh, despite its 2 open edges and 2 non-manifold edges. Blender did warn that the mesh "is not valid" on export; the file passed the validator.
- **A skeleton placed by script** (`scripts/e_rig_by_script.py`, 13 bones, feet found as the four clusters of low vertices) bound as well: 10 vertices unbound.
- **What a bent pose looks like** (`sheet_e.png`): with Tripo's weights only the tail moves. With automatic weights the legs swing and the tail sways; on Tripo's skeleton the belly is pulled into a sag behind the front legs, on the simpler skeleton less so. The legs are short stubs under a round body, so any leg bone sits close to belly vertices. A person would fix this by painting weights, which is hand work in Blender.
- **Both files** (`models/e_tripo/tripo_skeleton_auto_weights.glb`, `models/e_rigged_by_script.glb`) hold a skin, four morph targets and a clip, pass the validator with 0 errors and play in Bevy.

### F. The calm and the spiked generation

`orb_spiked_h31_req20000.glb` was there and was used (`scripts/f_compare.py`, `sheet_f.png`).

| | Calm | Spiked |
|---|---|---|
| Triangles | 19,007 | 19,188 |
| Size, x by y by z | 0.735 by 0.966 by 0.983 m | 0.872 by 0.966 by 0.983 m |
| Thin (spike) vertices | 28% | 47% |
| Highest point | the tail's tip, at the back | a quill, off to one side |
| Front feet apart, back feet apart | 0.37, 0.31 m | 0.24, 0.30 m |
| Colour | pink and cream | grey (the drawing was grey) |

- **Facing:** by picture, both face glTF +z.
- **They do not read as one animal.** The spiked one is a porcupine shape: lower, with a bigger head and snout, longer legs in a different stance, a fan of quills swept back, and no separate raised tail. Both files are scaled so the longest side is about 1 m, so their sizes do not correspond either.
- **A swap would also need** a second rig and a second set of clips, since the two meshes share nothing.
- An attempt to compare the bodies with the spikes stripped off, by thickness, gave the same box as the whole model for both and told nothing.

The spiked generation is still useful: as a picture of what the spiked state should look like, to set the stretch factor and to see where spikes are expected.

## 7. What this asks of the generator, the pictures, and kiln

### Of the generator

- **For a morph target, either kind of model works, and they fail in different places.** One fused surface (H3.1): best mesh and all three maps; spikes found by thickness; stretching is clean, shrinking is not. Loose pieces (P1.0, P2.0): spikes found exactly and shrink to nothing; base colour only, and the validator errors section 10 of the Tripo note records.
- **For a skeleton, the fused single piece is the safer input** (inference: automatic weights are known to dislike loose parts; only the fused model was bound here).
- **Generate the calm state, not the spiked one.** Stretching existing spikes works; a second generation does not match the first.

### Of the reference picture

- **Draw a short stub wherever a spike must grow.** The script lengthens geometry; it cannot invent it. Fur drawn as ink lines on a smooth back gives a smooth back.
- **Keep the legs clear of the belly** if the body is to walk: the sag in prototype E comes from stub legs under a round body.
- A drawing of the spiked state is worth having as a target to compare against, not as a second model.

### Of kiln, if characters ever came into scope

Inference, and not a proposal for now.

- **Measuring** would have to say that a file holds targets, a skin or clips, and measure the largest shape, not only the base one. Today it is silent, and its bounding box can be wrong for what Bevy draws.
- **Review pictures** would need the same view at several weights and clip times; the probe shows this is a small change to the existing renderer's pattern.
- **Checks on open edges and loose pieces** would cut the other way for such an asset: the loose-pieces model is the one whose fur animates best.
- **The record** would have to name the script settings that made each target, as it names a run's other inputs.

## 8. Unknowns, and the next smallest experiment

- **Where Tripo's walk is.** Not in any export. Next: export again from the web app with other settings and read the file with `scripts/c_read_back.py`; or call the API's retarget step, which documents `bake_animation` for `.glb`, on a few credits.
- **Whether a ready-made quadruped walk can be retargeted onto this skeleton** by script. Next: one CC0 animal's walk clip, one attempt.
- **Why Tripo's leg weights are missing.**
- **How the automatic weights look in motion.** Only two still poses were looked at.
- **Whether spikes added as instances on the bare back look right** beside the morphed ones.
- **Frame cost.** Nothing was timed; one creature of 19,007 triangles is far inside what the budget measurement found affordable, but a herd was not tried.
- **Normals left out of the targets**, to save 0.7 MB: not looked at.
- **One creature, one generation each.** Whether thickness finds spikes on another animal is not known.

The next smallest experiment is the first: a `.glb` from Tripo that has an `animations` array.

## What could not be done or verified

- **No walk or attack clip.** The clips here are test poses.
- **Tripo's rig could not be judged as Tripo intends it**, only as exported. The web app's preview was not seen by this note's author.
- **`orb_h31_req20000_walk2.glb` was not rendered**; it was read and imported only.
- **A vertex shader on masked vertices, a bone per spike, instancing, projectiles and shell fur were not built.** Their rows in the table are from sources and inference. Strand fur was built afterwards (section "Strand fur").
- **Rigify, Auto-Rig Pro, Cascadeur, Meshy, Anything World and the Quaternius clips were not tried.**
- **Web pages not opened:** Tripo's blog post on quadruped rigging (403), Adobe's Mixamo FAQ (403), a Polycount thread on shell counts (403). No Tripo help-centre page on Auto Rig was found.
- **Pages read only through a summarising tool:** Bevy's release notes, migration guide and issues; the Unreal and Unity pages; every row of the riggers table. Issue numbers and quotations from them should be checked before being relied on.
- **Blender's manual does not state why automatic weights fail**; the causes given are from forum snippets.
- **A cold build of the probe was not timed.** It reused the workspace's built Bevy.
- **Whether Bevy's glTF loader reads `EXT_mesh_gpu_instancing`** was not checked.
- **The pictures were judged by an AI model**, at 1280 by 960, from 2.4 to 2.7 m. The owner has not looked at them.

## Sources

Every item was read on 2026-10-08.

**Specification**

- [glTF 2.0](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), sections on morph targets, skins and animations: read in full.
- [glTF extension registry](https://raw.githubusercontent.com/KhronosGroup/glTF/main/extensions/README.md): read in full. [`EXT_mesh_gpu_instancing`](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Vendor/EXT_mesh_gpu_instancing/README.md), [`KHR_node_visibility`](https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_node_visibility/README.md): summary.

**Bevy**

- Source, read locally under `~/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/`: `bevy-0.19.1/Cargo.toml`, `bevy_internal-0.19.1/Cargo.toml`, `bevy_mesh-0.19.1/src/morph.rs` and `mesh.rs`, `bevy_pbr-0.19.1/src/render/mesh.wgsl`, `morph.wgsl`, `skinning.wgsl`, `skin.rs` and `src/extended_material.rs`, `bevy_gltf-0.19.1/src/loader/mod.rs`, `bevy_animation-0.19.1/src/lib.rs`, `graph.rs` and `morph.rs`.
- [0.19 release notes](https://bevy.org/news/bevy-0-19/), [0.18 to 0.19 migration guide](https://bevy.org/learn/migration-guides/0-18-to-0-19/), issues [#25966](https://github.com/bevyengine/bevy/issues/25966), [#13988](https://github.com/bevyengine/bevy/issues/13988), [#20554](https://github.com/bevyengine/bevy/issues/20554): summary or search listing.

**Blender 5.2 LTS manual**, read in full

- [glTF 2.0 exporter](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html), [armature parenting and automatic weights](https://docs.blender.org/manual/en/latest/animation/armatures/skinning/parenting.html), [Rigify basics](https://docs.blender.org/manual/en/latest/addons/rigify/basics.html).
- Forum, snippets only: [Blender Artists on bone heat failing](https://blenderartists.org/t/bone-heat-weighting-failed-to-find-solution-for-one-or-more-bones/701412).

**Tripo, first party**

- [API documentation, full text](https://developers.tripo3d.com/llms-full.txt) (rig check, rig, retarget, presets), [pricing](https://developers.tripo3d.com/en/pricing), [rig model page](https://developers.tripo3d.com/en/models/rig): read in full.

**Riggers and clips**: [Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html) (not opened), [Reallusion forum](https://forum.reallusion.com/523069/Animals), [Meshy rigging](https://docs.meshy.ai/en/webapp/guides/3d-model/rigging), [CG Channel on Anything World](https://www.cgchannel.com/?p=150924), [Cascadeur plans](https://cascadeur.com/plans), [Auto-Rig Pro](https://superhivemarket.com/products/auto-rig-pro), [Quaternius animated animals](https://quaternius.itch.io/lowpoly-animated-animals): summary.

**How games do it**: Unreal Engine documentation on [morph targets](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-morph-target-pipeline-in-unreal-engine), [world position offset](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-position-offset-material-functions-in-unreal-engine) and [sockets](https://dev.epicgames.com/documentation/en-us/unreal-engine/skeletal-mesh-sockets-in-unreal-engine); Unity manual on [blend shapes](https://docs.unity3d.com/Manual/BlendShapes.html) and [projectiles](https://docs.unity3d.com/Manual/instantiating-prefabs-projectiles.html) (engine documentation, summary). [Lengyel and others, real-time fur](https://hhoppe.com/proj/fur/) (paper, summary). [80 Level on shell texturing](https://80.lv/articles/classic-video-games-trick-for-rendering-grass-fur/) (trade press, summary). [Unity forum on replacing a character](https://discussions.unity.com/t/replace-character-ingame/431061) (forum post, 2010, summary).

**Kiln**

- `CLAUDE.md`, `CONTEXT.md`, `learn/MISSION.md`, `kiln/glb.py`, `kiln/measure.py`, `crates/asset_view/src/bin/review_pictures.rs` and `src/scene.rs`, [`tripo-api-trial.md`](tripo-api-trial.md) sections 10 and 11.

## How to run it again

From the repo root, with `.tools/` installed and the Tripo models in `learn/research/tripo-api-trial/models/`:

```
(cd learn/research/fur-animation-trial/bevy_probe && CARGO_TARGET_DIR=../../../../target cargo build --release)
learn/research/fur-animation-trial/scripts/run_all.sh        # prototypes A to D, about 30 seconds
learn/research/fur-animation-trial/scripts/run_skeleton.sh   # prototypes E and F, about 20 seconds
learn/research/fur-animation-trial/scripts/sheets.sh         # the contact sheets named above (ImageMagick)
```

One model at a time:

```
tools/bl learn/research/fur-animation-trial/scripts/a_morph_fused.py <model.glb> <out.glb> <facts.json> [thin=0.02 thick=0.035 legs=0.33 factor=3]
tools/bl learn/research/fur-animation-trial/scripts/b_morph_pieces.py <model.glb> <out.glb> <facts.json> <pieces.csv> [slender=2.5 factor=3]
target/release/morph_probe <model.glb> --out <folder> --frames "0;0,0,0,0.5;0,0,0,1" [--views three_quarter,side,top,front,back_quarter]
target/release/morph_probe <model.glb> --out <folder> --clip 0 --times 0,0.5 [--frames "0,0,0,1"]
python3 -I learn/research/fur-animation-trial/scripts/c_read_back.py "$PWD" <model.glb> ...
```

`a_morph_fused.py` and `b_morph_pieces.py` need the full path of the output file. Blender runs offline through `tools/bl`. The probe needs a graphics card and no display.

## Watching it

`bevy_probe/src/bin/fur_view.rs` is a second throwaway program in the probe's project: a window that shows one model on the viewer's ground and light, under the viewer's turntable, with the fur going from calm to spiked and back by itself (1.5 seconds out, 1 second held, 1.5 seconds back, 1 second held). From the repo root:

```
(cd learn/research/fur-animation-trial/bevy_probe && CARGO_TARGET_DIR=../../../../target cargo build --release --bin fur_view --features overlay)
target/release/fur_view
```

`--features overlay` draws the keys, the model's name and the weights in the window. It needs Bevy's UI crates, which `crates/asset_view` does not build: the first build with it took 3 minutes 12 seconds here and added 0.7 GB to `target/`. Without the feature the build takes seconds, the keys are printed to the terminal once, and the state is the window's title and one line of the terminal.

| Key | What it does |
|---|---|
| Space | Pauses the loop, or resumes it from the shape on screen |
| Left, Right | While paused: less or more spiked, as long as the key is held |
| 1, 2, 3 | The model to show (those of the three whose file is in `models/`) |
| T | Stops or starts the turntable |
| R | Puts the camera back where it started |
| Escape | Quits |

What each model shows:

1. **`a_fused_morph.glb`**, the fused surface (prototype A). Calm is the model as generated; the loop takes `spiked_axial` from 0 to 1. The spikes on the sides, the face ruff and the tail grow to three times their length. The top of the back stays bare.
2. **`b_pieces_p1_morph.glb`**, loose pieces from P1.0 (prototype B). Calm is `retracted` at 1: the spikes are inside the body. Half way is the model as generated (both weights 0). Spiked is `extended` at 1. The tail does not change, and a few short tufts near the face and on the back never retract.
3. **`b_pieces_p2_morph.glb`**, loose pieces from P2.0. The same two targets; more spikes, back included.

Other uses:

```
target/release/fur_view <model.glb>                    # any file with morph targets: its first target, 0 to 1 and back
target/release/fur_view --frames 3 --out <folder>      # no window: 3 pictures of each model, calm, half way, spiked
target/release/fur_view --out <folder>                 # the window also saves a picture of itself every 2 seconds
```

Normals are morphed by Bevy when the file carries them, as these three do; the viewer does nothing for it. The camera is placed for the box of the calm, half-way and spiked shapes together, so the longest spikes stay in view.

## Strand fur

Added later on 2026-10-08, after the owner made moving fur the requirement: "it needs to have realistic fur like individual hairs that turn into spikes but the fur needs to move naturally if something like wind or movement". **It works on a body that does not bend:** about 80,000 separate hairs on the creature sway in wind, hang behind the body when it dashes or shakes, and stiffen into a coat of long quills, at about 0.3 ms a frame more than the bare body on this machine. Following a skeleton is not built.

Everything in this section is **measured** or **looked at** as the note defines them; the pictures were read by the author, an AI model.

**A second version followed the same day**, after the owner watched the first and asked for rougher fur, bristle that flows the way the creature faces, stronger wind and atmospheric lighting. It is described under "The second version" below; "What was built" describes the first version, and says where the second differs only there. The first version's pictures are kept in `pictures/fur_strands/first_version/`.

**A third version followed the same evening**, after the owner watched the second and asked for one progression from combed fur to rough fur with the spikes as the peak of roughness, and for the future spikes not to be seen through the calm fur. It is described under "The third version: one scale of agitation" below, and it is what the program does now. The second version's pictures are kept in `pictures/fur_strands/second_version/`; its roughness presets and its bristle value no longer exist.

**A fourth version followed that night**, after the owner asked to see the fur in HDR with and without ray tracing. It adds keys for how the picture is made and how the body and the ground are lit, and changes nothing about the fur. It is described under "The fourth version: an HDR key and a ray tracing key" below. The third version's pictures are kept in `pictures/fur_strands/third_version/`.

### Terms

- **Strand:** one hair drawn as its own piece of geometry, here a narrow strip of triangles that tapers to a point.
- **Shader:** a small program the graphics card runs. The **vertex shader** runs for every vertex and decides where it is drawn; the **fragment shader** runs for every pixel a triangle covers and decides its colour.
- **Vertex attribute:** a number or a few numbers stored with every vertex and handed to the vertex shader: usually position, normal and UV; here also the hair's root, its comb direction, its lengths and two random numbers.
- **Instancing:** storing one small mesh (one hair) once and drawing it many times, with a short record per copy.
- **Guard hair:** one of the longer, stiffer hairs of a coat. Here, a hair that becomes a quill.
- **LDR, HDR:** low and high dynamic range. An LDR picture holds brightness from black to white and nothing above; an HDR one holds light brighter than white. The fourth version's section says which two things "HDR" means here.
- **Tone mapper:** the step that brings an HDR picture into what a screen shows, squeezing the bright end so that it is not simply cut off.
- **Bloom:** a soft glow spread round the brightest parts of the picture.
- **Rasterized, ray traced:** two ways to light a picture. Rasterized: each triangle is drawn and lit from the lights' numbers, with shadows looked up in a picture drawn from the light (a shadow map). Ray traced: for each pixel, lines are followed through the scene to the lights and to other surfaces, and what they meet decides the light.
- **Acceleration structure:** the index of a mesh's triangles that the graphics card builds so that it can find what a ray hits. It is built from the positions stored in the mesh.
- **Deferred:** drawing in two steps: first what the surface is at each pixel (colour, normal, roughness), then one pass that lights every pixel. Bevy's ray tracer replaces that second pass.
- **MSAA, TAA:** two ways to smooth jagged edges. MSAA takes several samples of each pixel in one frame. TAA takes one, shifted a little each frame, and blends frames; it has to be told how everything moved.

### What was built

`bevy_probe/src/bin/fur_strands.rs` (1,363 lines) and `fur_strands.wgsl` (304 lines), a third throwaway program in the probe's project. No new crate. Nothing under `crates/`, `kiln/` or the root `Cargo.toml` and `Cargo.lock` was changed.

**The body.** `b_pieces_p1_morph.glb` with its `retracted` target at 1, because that is the smoothest body in the trial: the 84 modelled spikes are shrunk to points inside it. The fused model was not used: its modelled spikes would stand through the fur. The cost is the pieces model's weaker file (base colour only, no normal map). 72 pieces of that model are not spikes to the script and stay: hooves, claws, and some tufts and bristles on the back, the face and the tail. They show as bare modelled spikes among the fur.

**Growing the hairs**, when the model has loaded:

- Points are spread over the body's triangles by area, one in each equal share of the area so that no patch is bald or crowded by chance. The seed is fixed, so every run grows the same coat.
- Each hair takes the body's normal there and the colour of the base colour picture at that UV. The colour is read a fifth of the way toward the middle of the triangle, away from the edge of its patch in the picture.
- No fur where the colour is strongly red (the snout), where it is dark (hooves, claws, nostrils), or below 7 cm (the feet). No fur on any part thinner than 3 cm, measured as prototype A measures thickness: that removes the leftover modelled spikes and tufts, which otherwise grow hair in every direction. On this model the rules leave 1.48 m² furred, 0.36 m² bare by colour or height, and 0.37 m² too thin.
- Hairs are combed from head to tail and downward, up the tail, and away from the snout on the face; each is turned up to 26 degrees from that at random. Soft length is 3 to 5.5 cm on the body, up to 1.8 times that round the face, up to 2.2 times on the tail, and half on the legs.
- **Two kinds of hair.** Fine hairs are the soft coat; bristled, they only lift part of the way and get a third longer. Guard hairs (between 1,800 and 4,500 of them whatever the hair count, 3,612 at 80,000) grow on the back, the flanks and the tail and become the quills: 12 to 22 cm long on the flanks, 26 to 48 cm on top of the back, up to 16 cm more on the tail, and about 12 mm wide at the base. Keeping the number of quills about fixed means the spiked shape is the same at every hair count.

**One mesh, not instancing.** All hairs are one mesh. A fine hair is a strip of 4 pieces (9 vertices, 7 triangles); a guard hair has 6 pieces (13 vertices, 11 triangles). Every vertex carries its hair's root as its position, the body's normal, where it is along the hair and on which edge of the strip, the comb direction and soft length, two random numbers, when the bristle wave reaches it, its quill length, its colour and its width: 80 bytes. This was chosen because Bevy's `Material` then does the rest: one draw, and the shadow map for free through the same shader. Instancing would store those 80 bytes once per hair, not once per vertex (about 9 times less memory), and would need its own draw code in Bevy 0.19 as in Bevy's `custom_shader_instancing` example, or a storage buffer the shader reads by hair number. Memory was not the limit here, so that was not built.

**The vertex shader places every vertex every frame.** Nothing about the hairs is updated on the CPU.

- **Shape.** The hair leaves the body at a low angle along the comb and curls back toward it. Bending is added in proportion to the place along the hair, so the root never moves, and the direction is made one unit long again at every place, so the hair keeps its length. A hair pushed below the surface is lifted back onto it.
- **Strip.** The strip is turned to face the camera (or the light, when the shadow map is drawn), so a hair is never seen edge on. The fragment shader shades it as if it were round.
- **Wind.** A direction and a strength. A field of two summed sine waves moves across the world with the wind, so neighbouring hairs sway together and the two flanks do not. One gust (key G) is a front that crosses the body at 0.9 m/s and lasts 1.6 s at any one place. Each hair also flutters at its own rate. The side the wind comes from feels more of it.
- **Movement.** Each frame the program works out the body's acceleration and its turning acceleration and steps four damped springs with them: two for moving (2.1 and 3.3 swings a second) and two for turning. The shader bends each hair by its own mix of the two, against the acceleration, plus a steady lean against the speed. So the coat flattens back in a dash, whips forward when the body stops, swings a few times and settles; in a shake each hair is bent by how fast its own part of the body turns. This is not a simulation of each hair: all hairs share the four springs.
- **Bristle**, one number from 0 to 1. Each hair has its own amount, which starts later the further back on the body it is, so the stiffening runs from the neck to the tip of the tail (this was tried against all hairs in step and kept: half way, the back is spiked and the tail is still soft). A guard hair first stands up, then grows to its quill length, widens into a cone, stops giving way to wind and movement, and turns pale with a dark point. Stood up, it points away from the line down the middle of the body and a little toward the tail, so the quills fan out evenly.
- **Shading.** Bevy's own lighting, so the fur is lit and shadowed like the body. Soft hair uses mostly the body's normal, so the coat is not noise; it is darker at the root and lighter at the tip, and each hair is up to 16% lighter or darker than its colour. The fur casts and receives shadows.
- **Thin hairs at a distance.** A hair is drawn at least 0.75 pixels wide. Where hairs would be thinner than that, only a share of them are drawn, the same ones every frame, so the coat does not get heavier with distance. Bevy's default 4-sample MSAA is on. No transparency is used.

### The second version

`fur_strands.rs` is now 2,076 lines and `fur_strands.wgsl` 415. No new crate and no new Bevy feature: fog, bloom, HDR and tone mapping are all in the `3d` feature set the probe already had, so nothing but the probe's own program was built again (6 to 10 seconds). Nothing under `crates/`, `kiln/` or the root `Cargo.toml` and `Cargo.lock` was changed.

**Rougher fur** (the owner's "ruth" was read as "rough"). One number from 0 to 1, stepped with F: sleek 0 (the first version's coat), medium 0.4, rough 0.72 (the start), very rough 1. All of it is in the vertex shader, so stepping it grows nothing again.

- **Clumps.** When the coat is grown, hairs spread evenly about 2.6 cm apart are made the middles of clumps, the same at every hair count. Every hair stores the way to the nearest middle on its own side of the body and leans toward it, more the further along the hair, so roots stay apart and tips meet: the coat breaks into tufts. Each clump has its own turn off the comb, its own lift and its own length.
- **Length and width.** Most hairs get shorter and a few much longer (0.7 to 1.6 times); width varies from 0.7 to 1.5 times and is 30% coarser overall at very rough.
- **Strays.** A few hairs in a hundred turn up to 70 degrees off the comb and stand off the coat.
- **Kink.** Every hair wavers sideways along its length. A fine hair now has 5 pieces (was 4) and a guard hair 8 (was 6) so that a kink and a quill's curve have something to bend.
- **Shaggy places.** The ruff round the face, the lower edge of the flanks and the tail are longer, more lifted and more kinked.

**Quills that flow forward.** Two readings of "flow in the direction the creature is facing" were built, each on its own key.

- **Which way the quills lean** (Q: forward, outward, rearward; comma and full stop for how far, 0.2 to 2.0, start 1.0). Forward, a quill leans along the body's surface toward the head and a little upward, blended with the outward direction so the silhouette stays full. The lean is strongest on the back and the shoulders, 60% on the flanks, about half just behind the head so the face is not buried, and each quill bends further over toward its tip, so the coat of quills curves like a wave about to break over the head. Outward is the first version's fan. Rearward is the mirror of forward.
- **Which way the stiffening travels** (V). From the tail and rump forward to the head (the start), or from the neck back to the tail as in the first version.
- **Half stiff, a hair shivers:** a fast tremble, strongest half way up, stronger in wind.

**Stronger wind.** The start is 1.0 (was 0.45) and `[` `]` go from 0 to 4.0 in steps of 0.25; from 3.0 the window calls it a gale. The wind now blows across the creature from its right and toward its tail. It is layered: a slow swell; narrow crests about a metre apart that cross the coat at about 1 m/s, in groups, and lift the coat and swirl it as they pass; a fine ripple; the one large gust of key G; and each hair's flutter, which grows in a crest. The tail's hair feels 1.8 times the wind. A hair is only ever turned, never stretched: whatever the push, the direction is one unit long at every place along the hair, so the tip is never further from the root than the hair is long, and the push itself levels off (at 4.0 a hair lies along the wind). Wind still fades to nothing on a stiff quill.

**Lighting**, stepped with L. The lights, fog, sky and ground of each are a table at the top of the program.

| Lighting | What it is |
|---|---|
| studio | The first version: the viewer's own sun, flat grey background and ground, no fog, no bloom, the cameras high. For comparison |
| dusk (the start) | A warm sun 15 degrees up from ahead of the creature, long shadows, a cool light from behind, haze, a dark sky with an orange glow low under the sun, slow clouds that dim the sun by up to a fifth |
| cavern | No sky. A cold shaft from above and behind, a warm lamp to one side that flickers, thick dark fog |
| moonlit mist | A pale blue moon from the side and behind, thick blue mist |

- All but studio add to each camera: HDR, bloom, distance fog (denser with the square of distance, in the colour of the horizon so the ground fades into the sky), and ACES tone mapping. The sky is a large ball seen from inside with a gradient in its vertex colours. The ground is a dark picture of earth made in the program. The cameras that looked down stand half as high, so there is a horizon.
- **Light from behind in the fur shader.** Two terms added after Bevy's lighting, neither shadowed: a glow where the coat is seen edge on, stronger toward the tips and when the light is beyond the creature; and Kajiya and Kay's strand highlight, which runs along a hair and makes a quill glint. Off in studio.

**Bodies**, stepped with N or chosen with `--body`. Tripo H3.1 made two bodies without spikes for this (`../tripo-api-trial/models/`): `smooth_midpoly` (9,608 triangles, the start) and `smooth_lowpoly` (4,793). `p1_retracted` is the first version's body. Assets are now read from the root of the disk, because the bodies are in two folders. The same colour and height rules decide where fur grows on all three.

**Faults of the first version that were fixed:**

- **Quills keep the coat's colour.** A quill has its root's colour to 45% of its length, pales toward the tip and ends in a dark point. In studio light the spiked creature is pink above and cream below again. In dusk light the quills in shade are steel blue from the sky and the light behind; that is the lighting, not the quill.
- **No hair goes below the ground.** A hair that would reach below y = 0 is turned to run along the ground, keeping its length.
- **Leftover modelled spikes.** On `p1_retracted` the program now finds the model's 157 loose pieces and does not draw the 134 that are mostly thin and are not hooves, claws or snout (0.14 m² of tufts, bristles and shrunk spikes). What remains on that body is fused to it: three or four cones on the tail and one by the face. The smooth bodies have none.

**Not done:** the thin-hair trick of `bevy_openusd` (fading a hair by coverage instead of dropping some hairs) needs alpha to coverage and a fragment shader for the shadow pass; the first version's rule is unchanged.

### The third version: one scale of agitation

`fur_strands.rs` is now 2,428 lines and `fur_strands.wgsl` 478. No new crate; nothing under `crates/`, `kiln/` or the root `Cargo.toml` and `Cargo.lock` was changed.

The owner's words: "ther should be more or a combinaiton and transition of more combed fur to more ruff for using the spikes as the ruffness pinical. it should be done in a way where the smooth spikes are not seed through the fur". They were read as two requirements: one continuous progression with the spikes at its top, and guard hairs that cannot be picked out of the calm coat. A second reading is at the end of this section.

**One number, agitation, from 0 to 1, drives every hair.** It replaces the second version's roughness (a look chosen once) and bristle (a separate switch). The parts of the scale overlap, so nothing snaps:

| Agitation | Name in the window | What changes |
|---|---|---|
| 0 to about 0.12 | combed | Hairs lie almost flat along the comb (4 to 10 degrees off the body, against 17 to 33 in the second version's sleek coat), each turned at most 6 degrees from it, lengths even, no tufts, no strays, no kink. The coat has a sheen and is lit as one smooth surface |
| 0.12 to 0.40 | ruffled | Hairs lift, turn off the comb, lean into tufts, vary in length; strays appear. The coat is disturbed in patches a hand wide, here swirled and lifted, there lying. The ruff and the tail shag out first because they are longest |
| 0.40 to 0.58 | rough | The same, at full strength by 0.58: lifted to about 45 degrees, up to a fifth longer, matt, each hair plainly lighter or darker than the next |
| 0.50 to 0.84 | hackles | The fine fur stands on end. Guard hairs rise out of it toward where they will point as quills, straighten, and are half as long again and a third coarser than the fur; still fur-coloured and fur-thin. They shiver |
| 0.78 to 1.0 | spikes | Guard hairs widen at the base into cones, grow to quill length, straighten fully, pale toward a dark point, stop giving way to wind. The fine fur stays raised and rough under them |

- **Every property is a smooth function of the hair's own agitation:** lift, turn off the comb, clump pull, kink, length, width, taper, straightness, colour, shine, how broken the lighting is, and how much the hair gives way to wind. Each hair is up to 0.08 ahead of or behind its neighbours, except at the two ends of the scale.
- **A change travels along the body.** The program keeps the last 1.6 seconds of agitation and hands the shader four values: what the end the change reaches first has now, and what it had 0.53, 1.07 and 1.6 seconds ago for the places further along. A hair takes the value for its place. So while agitation is rising the tail is ahead of the head (or the neck ahead of the tail, key V), a band of ruffling and hackles runs ahead of the spikes, and when agitation stops changing the whole coat arrives at the same value. This replaces the second version's wave, which at half bristle left one end fully spiked and the other untouched whatever the speed.
- **Wind and jolts ruffle the coat for a moment.** A wind crest adds up to 0.11 of agitation where it passes, a gust up to 0.24, both times the wind strength, and a dash, a stop or a shake adds up to 0.2 to the whole coat and fades over about a second. These add to the fur's roughness only and are capped at 0.56, so wind never raises hackles or a quill.
- **Wind by stage.** Combed fur gives way a third as much as ruffled fur and keeps its tip flutter; ruffled and rough fur catch the wind most; hackles half; quills none.
- **The roughness key F is kept, with a new meaning:** how rough the coat is at agitation 0. Combed (the start), sleek or tousled. The scale runs from there to the same spikes. `--calm 0` to `2` sets it at start; `--rough` is the same option under its old name.

**Guard hairs are hidden when calm.** In the second version a guard hair was grown 1.4 times as long and 1.25 times as wide as a fine hair, so the future quills showed in the calm coat as thicker, longer strands. Now a guard hair is grown exactly as a fine hair is: length and width from the same distribution, colour from the same point of the picture, the same comb, clump and random numbers. The only difference stored is its quill length, which the shader does not use below the hackles part of the scale. At agitation 0 the two kinds run through the same code with the same inputs. Key X steps through two pictures for looking at this: each hair coloured by its own agitation, and the guard hairs tinted cyan.

**Three faults of the second version, traced:**

- **The pale jagged shards along the line between pink and cream were the body's own geometry.** The "smooth" bodies still have modelled tufts fused to them: a fringe of flaps like shingles along the colour line and round the face, nicks on the back, fins on the tail. This was seen by rendering the body alone (`02_body_with_no_coat`). They are thinner than 3 cm, the rule for a modelled spike, so they grew no hair and stood bare out of the coat. Fix: on a body that does not morph, the vertices of each small thin patch (under 0.08 m², not red, above 12 cm) are moved, 200 times over, to the middle of their neighbours while the vertices round the patch stay; the flap sinks onto the body, and then it grows fur. On `smooth_midpoly` that is 116 patches and 1,226 vertices; on `smooth_lowpoly` 9 patches and 56 vertices. A first try that also moved everything within two edges of a patch moved 2,683 vertices and deflated the whole body; it was dropped. **Mostly fixed:** two or three small dark dimples remain on the flank and one white point at the tip of the tail.
- **The bare dark patch at the root of the tail was not bare.** The second version's note blamed a dark place in the picture; the picture is pink there. In studio light from behind (`03_combed_light_0_studio_rear`) the root of the tail is furred like the rest. In dusk light that place is in the body's own shadow from a sun 15 degrees up in front, lit only by the blue light from behind, so it is dark blue-grey. Nothing was changed.
- **The small dark specks were pixels with no number in them.** The fragment shader raised to a power two values that can come out a hair below zero: the place along the hair, which between a triangle's samples is read slightly outside the triangle, and one minus the dot product of two unit vectors in the light-from-behind term. A power of a negative number is no number, and the pixel is drawn black. Both are clamped now. Counted as exactly black pixels: 172 and 199 in two of the second version's calm pictures, 262 just after a stop, 67 bristled; 0 in the same views now. Which of the two clamps removes them was not separated.

**A second reading of the owner's words** that the pictures and the code allow: "smooth spikes are not seen through the fur" may be about the top of the scale, not the bottom: that at full spikes the smooth cones should not show bare among fur but be buried in or rise out of rough fur. That is also partly built (the fine fur stays raised and rough under the quills), but at 1.0 the quills are long enough to hide most of it.

### The fourth version: an HDR key and a ray tracing key

Added later on 2026-10-08, after the owner asked to see the fur "in HDR with and without ray tracing". The fur itself is the third version's. `fur_strands.rs` is now 3,619 lines, `fur_strands.wgsl` 498, and there is a second small shader, `fur_haze.wgsl` (25 lines). Nothing under `crates/`, `kiln/` or the root `Cargo.toml` and `Cargo.lock` was changed. The probe's own `Cargo.toml` and `Cargo.lock` were: see "What it cost to build".

**In one paragraph.** K switches the camera between a plain LDR picture and Bevy's HDR pipeline, and the difference is plain to see. An HDR signal to the screen is not possible with Bevy 0.19.1 as published, although this monitor, compositor and driver are all ready for one; a second binary built against a ten-line change to Bevy does send one, and nobody has looked at it yet. P switches the lighting of the body and the ground to Bevy's ray tracer, Solari, which runs here at 77 to 80 frames a second full screen. **The ray tracer cannot see or light the fur.** The fur stays rasterized; a simplified copy of the coat, rebuilt every frame, lets it cast a ray-traced shadow. So ray tracing changes the ground and the bare parts of the body, not the coat, and it costs the fur its 4x MSAA.

**What "HDR" means here: two different things.**

- **The HDR pipeline** is how the picture is worked out. The camera draws into a picture that holds 16-bit float numbers, so light can be many times brighter than white without being cut off; bloom then spreads the brightest parts a little; and a tone mapper brings everything into the range a screen shows. The opposite, here called plain LDR, draws straight into the 8-bit picture: what is brighter than white is cut off at white, and there is no bloom. Both end as an ordinary SDR signal to the screen.
- **HDR on the screen** is what is sent to the monitor: a signal in which white is not the top, so a highlight can really be brighter than the white of the desktop. This needs the program's window surface to be opened in an HDR format.

**What the viewer did before this.** The studio lighting was LDR with Bevy's default tone mapper (TonyMcMapface), no bloom, no fog. Dusk, cavern and moonlit mist were the HDR pipeline with the ACES fitted tone mapper, bloom (0.16, 0.2, 0.2) and distance fog. Exposure was Bevy's default (EV100 9.7) everywhere. Auto exposure and colour grading were not used. Until K or M is pressed or `--hdr` is given, each lighting still does exactly that.

**The HDR key, K.** On: 16-bit float picture, the HDR tone mapper (ACES fitted at the start), the lighting's bloom. Off: 8-bit picture, no bloom, the LDR tone mapper, which starts at "none" so that the cut-off is seen. Fog stays in both: it is not part of HDR.

- **M** steps the tone mapper of the picture now shown through Bevy's eight: none, Reinhard, Reinhard luminance, ACES fitted, AgX, SomewhatBoringDisplayTransform, TonyMcMapface, Blender filmic. The LDR picture and the HDR picture each remember their own.
- **- and =** make the picture half a stop darker or brighter (the camera's `Exposure`), from -6 to +6.
- **E** turns on Bevy's auto exposure, which meters the float picture and adapts over a second or two. It needs the HDR pipeline; with K off the overlay says nothing will change.
- Colour grading (`ColorGrading`) is in Bevy 0.19.1 and was not given a key.

**HDR on the screen: ready everywhere except in Bevy.** Measured on this machine, all read-only:

| Layer | What it says |
|---|---|
| Monitor and compositor | `hyprctl monitors`: DP-1 (the 3,440 by 1,440 screen) has `colorManagementPreset: hdr`, format `XBGR2101010` (10 bits a channel), `sdrBrightness 3`. HDMI-A-1 is `srgb`, 8-bit. Hyprland 0.56.2, `render:cm_enabled` true |
| Driver | NVIDIA 610.57.04. Asked from inside the program, the window's Vulkan surface offers `Rgba8UnormSrgb, Bgra8UnormSrgb, Rgba8Unorm, Rgba16Float, Bgra8Unorm, Rgb10a2Unorm` |
| wgpu 29.0.4 | Source, `wgpu-hal/src/vulkan/swapchain/native.rs`: a surface configured as `Rgba16Float` is created in the extended linear sRGB colour space (scRGB: 1.0 is SDR white, more is brighter); every other format is created as ordinary sRGB. So scRGB is the one HDR output wgpu has. HDR10 (PQ) is not there |
| Bevy 0.19.1 | Source, `bevy_render/src/view/window/mod.rs`, `create_surfaces`: takes `Rgba8UnormSrgb` or `Bgra8UnormSrgb` whenever offered, with the comment "For future HDR output support, we'll need to request a format that supports HDR". There is no setting, and the list of surfaces is private to the crate |

- **So with Bevy 0.19.1 as published the screen gets SDR whatever K says.** Key O says so in the window, with the surface's formats and each monitor's mode.
- **What is missing is one choice of format in Bevy.** `bevy_probe/scrgb/bevy_render_scrgb.patch` is that change: 11 added lines that take `Rgba16Float` when the environment variable `BEVY_SCRGB_SURFACE` is set. `bevy_probe/scrgb/build.sh` copies `bevy_render` from cargo's registry into a scratch folder under `target/`, patches the copy, and builds a second binary, `target/release/fur_strands_scrgb`, against it. The probe's own manifest, lock file and `fur_strands` binary are not touched by it, and nothing of Bevy is copied into the repo.
- **`fur_strands_scrgb --display-hdr` runs:** Bevy logs "surface format Rgba16Float (scRGB) taken", the window draws a frame every 6.06 ms rasterized (the screen's 165 a second) and every 7.5 ms ray traced, and stderr has no warning or error. It starts with the HDR picture and the tone mapper at "none", because a tone mapper that brings everything under white would make an HDR signal look like SDR; the overlay says "the screen gets scRGB, with light over white" or "all of it under white".
- **Nobody has seen it.** The author is an AI model and cannot see the monitor, and a screenshot cannot hold what is above white. Whether the highlights are brighter than the desktop's white, whether white sits at the desktop's brightness (Hyprland's `sdrbrightness 3` applies to SDR windows; what it does to an scRGB one was not found out), and whether the colours are right are for the owner to judge.
- No system, compositor or monitor setting was changed.

**What Bevy 0.19.1 has that traces rays.** One thing: the crate `bevy_solari`, Cargo feature `bevy_solari`, which calls itself experimental. Searched in every Bevy 0.19.1 crate in cargo's registry: nothing else uses ray queries. There are no ray-traced shadows, reflections or ambient occlusion as separate features of the ordinary renderer.

- **Solari is a whole lighting method, not an extra.** Added to a camera (`SolariLighting`), it replaces Bevy's lighting pass for everything drawn deferred: direct light from directional lights and glowing meshes with ray-traced shadows (ReSTIR DI), one bounce and more of indirect light (ReSTIR GI and a cache of light in the world), and reflections for smooth surfaces. There is also a slow reference path tracer, not used here.
- **What it asks of the graphics card:** wgpu's `EXPERIMENTAL_RAY_QUERY` and four binding-array features. The RTX 3080 with this driver has all five; the program checks at start and P says which is missing if any.
- **What it asks of the camera:** the 16-bit float picture (so ray traced is always HDR underneath), one sample a pixel (no MSAA), a deferred prepass with depth and motion vectors, and a main picture its compute shaders can write to.
- **What it asks of a mesh:** triangles, 32-bit indices, and exactly four vertex attributes: position, normal, UV, tangent. It builds its acceleration structure from the stored positions, once, and again whenever the mesh asset changes.
- **What it asks of a material:** Bevy's `StandardMaterial`, of which it reads base colour, emissive, roughness, metallic, reflectance and their pictures. No custom material, no vertex colours, no transparency.
- **Lights it knows:** directional lights and glowing meshes. Not point lights, not the light from all sides (`GlobalAmbientLight`), not fog.
- **Its denoiser is DLSS Ray Reconstruction,** which Bevy's own example calls "highly recommended". That is the feature `dlss`, which needs the crate `dlss_wgpu`. This project has never resolved that crate, so by the rule for this task it was not added. Without it Solari's picture is grainy: one sample a pixel.

**What happens to the fur: the ray tracer sees none of it.** Source, `bevy_solari/src/scene/blas.rs`: a mesh with any attribute beyond the four is skipped. The coat has five more. And if it were not skipped: every vertex of a hair is stored at the hair's root, because the vertex shader is what moves it, so every triangle of the coat has no area and no ray could hit it. The fur's material is not a `StandardMaterial` either, so Solari could not shade it. Not collapsed, not unbent: absent.

**What was built, by the three options of the brief:**

- **(a) The body and the ground are ray traced, the fur is not. Reached.** With P on, the body's and the ground's materials are switched to deferred and copies of their meshes, cut down to the four attributes, are handed to Solari. The fur is drawn afterwards by Bevy's ordinary forward renderer exactly as before, lit by the same lights with the same shadow map, so it also still shadows itself. **The fur receives nothing from the ray tracer:** no ray-traced shadow, no bounce light.
- **(b) A stand-in for the coat in the ray tracer's scene. Reached.** `Shape::of` in `fur_strands.rs` is the vertex shader's `place` written again in Rust, line for line. Every frame the program works out some of the hairs on all the processor's threads, as three-sided tubes that do not turn to the camera, and replaces the positions of a mesh that is never drawn; Bevy uploads it and Solari builds its acceleration structure again. So the coat and the quills cast a ray-traced shadow on the ground and on the bare parts of the body, where they are this frame. Key J steps what the stand-in holds: nothing; the guard hairs (3,599 hairs, 75,579 triangles); the guard hairs and one fine hair in 8, each drawn 4 times as wide (13,123 hairs, 161,295 triangles; the start); every hair (79,795 hairs, 761,343 triangles).
- **(c) Ray-traced fur. Not reached, and not tried.** It would mean drawing the fur deferred so that Solari lights each hair's pixels. Reasoned from the source, two things stand in the way. Solari starts a shadow ray 1 mm off the pixel's surface; a hair's pixel lies inside or within a millimetre or two of its own stand-in, so every lit hair would shadow itself at random. Without the stand-in the fur would get shadows from the body only and lose the self-shadowing that gives the coat its depth. And one sample a pixel on hairs under a pixel wide leaves the denoising to something this build does not have.

**Four things were added so that the comparison is fair,** each because Solari leaves it out:

- **The light from all sides** is a dome of 1,000 m radius that glows with the lighting's ambient colour and brightness, with a hole toward the sun and toward the light from behind, because Solari's rays to the sun would stop at the dome. What is left of the dome glows that much more. Unlike Bevy's ambient light it is blocked by things, so the ground under the belly is darker.
- **The cavern's lamp** is a ball of 5 cm glowing as bright as a point light of the lamp's lumens.
- **Fog** on the ray-traced ground is the ground drawn once more over it with `fur_haze.wgsl`, which calls Bevy's own fog function and adds exactly what the fog would have. The bare parts of the body get no fog (3% at the creature's distance in dusk).
- **Same suns:** the sun and the light from behind are the same lights, with the same directions, colours and strengths; Solari reads them itself. It gives the sun the real sun's size (half a degree), so shadows soften with distance.

**Two things were added because ray tracing takes away 4x MSAA:**

- **I: frames are blended** (Bevy's temporal anti-aliasing, TAA), on at the start when ray tracing. It takes most of the grain away and smooths the hair edges. For it the fur's prepass now says how far each vertex moved since the last frame, by placing the hair twice, with this frame's numbers and the last frame's. Before that was added a moving coat smeared into a blur (seen in the window's own picture); after, strands stay strands.
- **Hairs are drawn at least 1.3 pixels wide** while ray tracing (0.75 otherwise), or thin hairs miss pixels and the body shows through.

**What the ray tracing key changes on screen,** from the pictures below:

- **The ground's shadow:** the same shape and as dark in the middle, with a softer edge. In the cavern, lit from above, the shadow's edge is a fringe of separate quill shadows, where the shadow map gives a rounded blob. In dusk the shadow is long and its far end is soft in both.
- **The ground itself:** grainier, and darker the further away it is (see the numbers below). Up close, with frames not blended, the grain crawls.
- **Beside the feet** the ground is about half as bright (8 and 7 of 255 against 14 and 15), which fits the sky's light being blocked by the body there; Bevy's ambient light is blocked by nothing.
- **The bare parts of the body** (snout, hooves, lower legs) are lit and shadowed by rays. In the pictures the hooves are a little lighter; nothing else of it could be made out at this size.
- **The fur: the same lighting, softer.** It is blended over frames and not 4x MSAA, so a strand is less crisp. In the combed coat a few dark flecks show along the line between pink and cream.
- **Not there:** quill shadows on the fur (the fur's own shadow map still makes them, as before); bounce light from the ground into the belly fur; reflections (the ground is rough and nothing else is ray traced and shiny).
- **Lag was not judged.** The pictures give the ray tracer 150 frames to settle before each is taken. What the ground does in the first second after P or L, and behind a dashing creature, is for the owner to see.

**What it cost to build.**

- **The feature:** `bevy_solari` was added to the probe's Bevy features. Cargo downloaded one crate, `bevy_solari` 0.19.1, and the probe's own `Cargo.lock` gained that one package; every other version is as it was. `wgpu` 29.0.4, already in the lock through Bevy, is now named in the probe's `Cargo.toml` with no features, to ask the surface for its formats. The first build took 57 seconds (seven crates: `bevy_pbr`, `bevy_gizmos_render`, `bevy_solari`, `bevy_internal`, `bevy`, `asset_view`, the probe), with another agent's Blender running. The target folder grew by 265 MB and the binary from 171.6 to 175.1 MB.
- **The feature changes rasterized pictures slightly, with ray tracing off.** Solari turns on `bevy_pbr`'s feature `dfg_lut`, with which Bevy reads part of its specular lighting from a table and not from a formula. `--check --strip` set against the third version's pictures of the same moments: 0.2 to 0.7% different (root mean square) in dusk and cavern, 1.8% in moonlit mist, 3% in studio, where the ground far away is darker. Two runs of the new program give identical rasterized pictures.
- **The scRGB binary:** `scrgb/build.sh` took 94 seconds (13 crates) and 385 MB of target folder. It starts from nothing each time it is run.

### What it looks like

**The fourth version.** `fur_strands --check` writes 64 pictures and 16 contact sheets in 38 seconds: four moments (combed 0, rough 0.5, spikes 1.0, and rough 0.5 in a gale of 3.5) in dusk and in cavern light, from the three-quarter and the close camera, each in four looks. A sheet (`00_sheet_<lighting>_<moment>_<camera>.png`) holds the four looks of one moment side by side, labelled. Every look of a moment is taken at the same instant of the program's clock, so the hairs, the clouds and the lamp's flicker are the same in all four. The pictures are 8-bit PNG files: **they show the HDR pipeline after its tone mapper, and cannot show HDR on the screen.**

| Look | File ends | What it is |
|---|---|---|
| LDR rasterized | `__1_ldr_rasterized` | 8-bit picture, tone mapper none, no bloom, shadow maps, 4x MSAA |
| HDR rasterized | `__2_hdr_rasterized` | The HDR pipeline with ACES fitted and bloom; what dusk and cavern were before |
| Ray traced, LDR look | `__3_ldr_look_ray_traced` | Body and ground ray traced; no bloom and tone mapper none, on the float picture Solari needs. There is no ray tracing on an 8-bit picture |
| HDR ray traced | `__4_hdr_ray_traced` | Body and ground ray traced, the HDR pipeline, frames blended, the start's stand-in for the coat |

**LDR against HDR, rasterized:**

- **LDR is brighter and flatter.** Mean brightness of the close dusk pictures: 86 and 90 of 255 in LDR, 57 and 62 in HDR. In the combed close picture 6.2% of the pixels have red at its limit in LDR and none in HDR: the sunlit back and the tail are patches of flat salmon orange with the strands gone, where HDR keeps pink fur with strands and a gradient from lit to shaded.
- **HDR is darker and has more contrast:** deeper shadow under the creature, a darker sky, the lit flank standing out. In the cavern the LDR picture is a grey ground under a grey sky; HDR is a lit animal in the dark.
- **Bloom is slight** at these strengths (0.16 and 0.2): a faint glow round the brightest quill tips, hard to find in a still.
- **Banding** in the sky and the fog, which 8 bits could show, was not seen in either.

**Ray traced against rasterized,** both HDR:

- **Ground in sunlight, dusk, three-quarter camera, measured as the mean of 40-pixel squares:** at the bottom of the picture, nearest the camera, 16 and 14, 18 and 18 of 255 (rasterized and ray traced); in the middle distance 40 and 29, 37 and 25. In the shadow 15 and 15, 11 and 12, 8 and 9. So the shadow is as dark and the lit ground beyond it is a quarter to a third darker, and the long shadow has less contrast ray traced. Why the far ground is darker was not found out for certain; the likeliest reason is that Bevy's ambient light adds a strong reflection at grazing angles which the dome does not.
- **Grain, in dusk.** In studio light, seen once in the window's own picture, the ray-traced shadow is speckled even with frames blended. With frames blended, the brightness within a patch of near ground varies by 1.8 of 255 ray traced against 1.5 rasterized (standard deviation), and of far ground by 3.2 against 1.9. Before blending was added it was 6 and 11: plainly speckled, and that is what key I shows when it turns blending off.
- **The cavern's shadow has a spiked fringe** ray traced and a rounded edge rasterized.
- **The fur is softer,** as said above; side by side at full size the rasterized strands are crisper.
- **In the gale** the coat is as sharp as in a breeze: no smear in the still.
- **Ray-traced pictures are not the same twice:** two runs differ by 0.8 to 1.6%, because the rays are random.

**The third version.** `fur_strands --check --strip` writes 104 pictures and 3 contact sheets in about 30 seconds, in dusk light on `smooth_midpoly` unless the name says otherwise. The strip is the same three cameras at nine agitations in a light breeze (wind 0.4); `00_strip_sheet_close.png`, `_three_quarter.png` and `_side.png` each hold the nine side by side.

| Agitation | What the strip shows |
|---|---|
| 0.00 | A sleek combed coat with a sheen, pink above and cream below, every hair lying back along the body; the tail a smooth brush; the ruff a neat fan of straight hairs round the snout. No strand stands out |
| 0.15 | Nearly the same. Hair tips have begun to lift, the edge of the back is slightly fuzzy, the tail is a little fuller. The smallest step of the strip |
| 0.30 | Plainly ruffled: the outline is soft and fuzzy all round, the tail is half as wide again and untidy, the ruff has opened and its hairs cross, lighter and darker patches show on the flank |
| 0.45 | A rough, shaggy animal: tufts, strays, a thicker outline, a big ragged tail, matt |
| 0.60 | Rougher and visibly bigger; the first hackles stand above the coat along the back and the shoulders as thin straight hairs. The largest step of the strip |
| 0.70 | Hackles up over the whole back and rump: a dense stand of thin straight fur-coloured hairs above a rough coat, leaning forward. Untidy, with hairs crossing; not yet quills |
| 0.80 | The hackles longer and straighter, beginning to line up toward the head, the first pale ones among them on the back |
| 0.90 | Quills: long pale cones sweeping forward over the back, rough fur between and under them, the tail still mostly hackles |
| 1.00 | The quill wall of the second version: dense pale quills curving toward the head, well above the body. In dusk light they are steel blue where the sun does not reach |

| Pictures | What they show |
|---|---|
| `02_combed_guard_hairs_tinted`, `02_combed_no_tint` | The same moment twice. Tinted: cyan hairs spread evenly over the back, the flanks and the tail, lying in the coat. Not tinted: no strand can be picked out by length, width, straightness or colour |
| `02_body_with_no_coat` | The body alone after flattening: smooth, with the colour line now a painted edge and a few shallow nicks left |
| `03_combed_light_*`, `04_rough_light_0_studio`, `04_hackles_light_0_studio`, `11_spikes_light_*` | The stages in the other lightings. Studio shows the coverage best: no bald skin at 0, 0.45 or 0.7, including the root of the tail |
| `04_calm_coat_tousled_at_0` | Agitation 0 with F at tousled |
| `05_combed_in_wind`, `05_ruffled_in_wind`, `06_*_gust`, `07_*_gale` | Combed, the body's coat stays sleek in wind, a gust and a gale and only the tail is thrown about; ruffled, the flank lifts in bands |
| `08_mid_dash`, `08_just_stopped` | As before, with the coat a little rougher for a second after the stop |
| `09_mid_sweep_ruffling_ahead_of_spikes`, `09_mid_sweep_agitation_as_colours` | Agitation rising from 0.1 to 1 in three seconds, caught at 0.94: the tail and the rump are quills, the middle of the back hackles, the shoulders and the ruff still rough fur. The second picture is the same with each hair coloured by its own agitation |
| `10_spikes_forward`, `_outward`, `_rearward` | The three leans at 1.0 |
| `12_mid_sweep_neck_to_tail` | The same change travelling the other way |
| `14_body_p1_retracted_*`, `15_body_smooth_lowpoly_*` | The other two bodies combed, rough and spiked |

**What looks wrong in the third version, or was not judged:**

- **Movement was again judged from stills.** How the travelling change, the ruffling in wind and the settling after a jolt look in motion needs the owner's eyes.
- **The steps of the strip are uneven.** 0 to 0.15 is slight and 0.45 to 0.60 is large; the hackles part (0.6 to 0.8) is a tangle of crossing hairs more than rows of raised hackles.
- **The combed ruff is a fan of straight spines** with dark gaps between them, less sleek than the body's coat.
- **Combed, the line between pink and cream is stepped** like the pixels of the body's picture, because every hair takes one colour from the nearest pixel and they all lie the same way.
- **In a gust a few long hairs of the tail fly out bent at sharp angles.**
- **Two or three dark dimples on the flank and a white point at the tail's tip** are what is left of the body's modelled tufts.
- **Flattening the tufts changes the body that is drawn,** slightly: the fringe round the face and the fins of the tail are gone from the bare body too.
- **Quills still pass through each other and the tail,** forward quills still cover part of the ruff, and the spiked creature is still mostly steel blue in dusk light.

**The second version.** `fur_strands --check` writes 56 pictures in about 12 seconds, in dusk light on `smooth_midpoly` unless the name says otherwise.

| Pictures | What they show |
|---|---|
| `01_calm_rough` | A shaggy coat in tufts, pink above and cream below, a long cream ruff round the bare red snout, a ragged tail, lit orange from the front with a long shadow, blue on the shaded side, a dark ground fading into haze. One creature, not a ball of static |
| `02_roughness_0_sleek`, `1_medium`, `3_very_rough` | Sleek is the first version's combed coat. Medium has visible tufts. Very rough is wiry: long strays whose straight pieces show as angles, worst on the tail |
| `03_calm_light_*`, `12_bristle_light_*` | Studio: flat grey, seen from above, the pink quills plain. Cavern: nearly black, quill tips white in the cold shaft, the near side orange from the lamp. Moonlit mist: all blue, the back and the quill tips rimmed pale |
| `04_gust`, `04_gust_a_quarter_second_later` | The tail's hair thrown to one side, and a different shape a quarter of a second on. The body's coat changes less in a still than the tail |
| `05_gale` | At 3.5: the tail streaming, the flank's coat lifted in dark and light bands, the back pressed flatter. The coat holds together |
| `06_mid_dash`, `07_just_stopped` | As the first version: pressed back in the dash, thrown forward and fluffed at the stop |
| `08_bristle_half_tail_to_head` | The tail and the rear half are quills, the front half still soft fur |
| `09_bristle_full_forward` | Every quill sweeps toward the head in a curve, the tail's quills arch over the back |
| `10_bristle_full_outward`, `11_bristle_full_rearward` | A round star of straight quills; and the mirror of forward, swept back off the rump |
| `13_bristle_half_neck_to_tail` | The front half quills, the tail still soft |
| `15_body_p1_retracted_*`, `16_body_smooth_lowpoly_*` | The other two bodies, calm and bristled |

**The bodies.** `smooth_midpoly` is the best: no modelled spikes, a clean line between pink and cream, the snout and hooves bare. `smooth_lowpoly` is nearly as good; a few hairs of the ruff cross its snout and its lower legs are bare white. `p1_retracted` has a thinner tail with cones still standing in it, and less furred area.

**What looks wrong in the second version, or was not judged:**

- **Movement was judged from stills** and from the window's own pictures. Whether the wind's bands, the shiver and the forward sweep look right in motion needs the owner's eyes.
- **Very rough hair is angular.** Five straight pieces cannot carry a kink smoothly; the tail's long hairs show it most, and after a dash at rough too.
- **A gale is quieter in a still than expected** on the body: with the wind partly along the comb the coat is pressed sleek. The tail and the lee flank show it.
- **In dusk light the bristled creature is mostly steel blue,** orange only where the sun reaches. The pink shows in studio.
- **Some quills on the lower flank hook at the tip** when leaning forward, where the lean would push them into the body and they are lifted off it.
- **Forward quills cover part of the ruff** and reach past the face from the side.
- **A row of pale jagged shards along the line between pink and cream** on `smooth_midpoly`, and small dark specks in the coat seen close. Not traced: the body's own modelled tufts, or hairs coloured from the wrong side of a UV seam.
- **A bare dark patch at the root of the tail** on `smooth_midpoly`: the picture is dark there and the colour rule grows no fur on dark.
- **The ground picture has no smaller copies of itself (mipmaps)** and may shimmer far away; the fog hides most of it. The sky is a plain gradient.
- **Quills still pass through each other and through the raised tail.**

**The first version.** `fur_strands --check` then wrote 24 pictures, 1,600 by 900: eight moments from a three-quarter, a side and a close camera, with the clock stepped a sixtieth of a second a frame so every run gives the same pictures. They are in `pictures/fur_strands/first_version/`.

| Moment | What the pictures show |
|---|---|
| `1_calm` | A soft pink back, a cream belly and a cream ruff standing round the bare red snout, dark bare feet. It reads as short fur with visible strands, combed back. A dozen bare modelled spikes stand out of it on the back, the face and the tail |
| `2_mid_gust` | The same with the coat slightly rougher and the tail hair lifted. A small change in a still picture |
| `3_mid_dash` | The coat pressed flat and sleek against the body, tail hair swept back. In the side view the creature is half out of the picture: the camera follows it late on purpose |
| `4_just_stopped` | The coat thrown forward and standing off the body, clearly fluffier than calm. Close up, some hairs show their four straight pieces |
| `5_settling` | Part of the way back to calm |
| `6_bristle_half` | The front half of the back is a fan of quills; the rear and the tail are still soft. The wave is easy to read |
| `7_bristle_full` | A porcupine: a dense fan of straight pale quills over the back, the flanks and the tail, reaching well above the body and past the tail's tip; the pink face, the ruff, the snout and the feet stay as they were. Close up the quills are separate cones with dark points, and they cast a spiky shadow |
| `8_mid_shake` | The body turned a little; the coat barely different from calm in a still |

**What looked wrong in the first version, or was not judged:**

- **Movement was judged from stills only.** Whether the sway, the lag and the settling look natural in motion needs the owner's eyes on the window.
- **The quills are pale and many, so the spiked creature loses most of its pink.** The owner's drawing was not seen by the author; quill colour, number, length and width are constants at the top of the program.
- **The leftover modelled spikes** are bare and do not move or grow.
- **Quills on the flanks point down and out** and some reach the ground or pass through it. Nothing stops a hair at the ground.
- **Quills pass through each other** and through the raised tail. Nothing stops a hair at another hair.
- **Roots.** A hair starts exactly on the surface, so no root floats. Bristled, the 12 mm base of a quill is a flat strip turned to the camera, and at its foot it cuts into the body's surface slightly.
- **The tail** is fur on the tail's modelled core with modelled bristles standing out of it.
- **Colour at UV seams:** no wrong-coloured hairs were seen in these pictures. The picture has hundreds of small patches, so some are likely.
- **Popping:** none when bristle changes, since everything is a smooth function. Changing the hair count grows a new coat and the hairs jump.
- **Shimmer** could not be judged from stills.

### Measurements

Development machine: RTX 3080, Ryzen 7 5800X. `fur_strands --bench`: a full-screen window of 3,440 by 1,440 pixels, vsync off, 4-sample MSAA, the creature filling about a third of the height, three seconds of frames per row. Another agent was running Blender on the processor at the same time (load average 6 to 13), so the slowest frames are not the fur's.

| Hairs asked | Hairs grown | Fur triangles | State | Median frame, ms | Mean, ms | Slowest 1%, ms | Mesh built in, ms |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | body only | 2.56 | 2.89 | 8.0 | |
| 10,000 | 9,972 | 76,904 | calm in a breeze | 2.44 | 2.77 | 10.7 | 8 |
| 10,000 | 9,972 | 76,904 | bristled | 2.45 | 2.61 | 4.5 | |
| 30,000 | 29,910 | 216,594 | calm | 2.42 | 2.52 | 4.2 | 27 |
| 30,000 | 29,910 | 216,594 | bristled | 2.40 | 2.47 | 3.7 | |
| 80,000 | 79,781 | 572,915 | calm | 2.72 | 2.82 | 4.6 | 58 |
| 80,000 | 79,781 | 572,915 | bristled | 2.73 | 2.84 | 4.5 | |
| 80,000 | 79,781 | 572,915 | calm, fur casts no shadow | 2.39 | 2.58 | 5.4 | |
| 200,000 | 199,465 | 1,413,915 | calm | 2.67 | 3.31 | 13.7 | 147 |
| 200,000 | 199,465 | 1,413,915 | bristled | 2.90 | 3.66 | 13.8 | |
| 500,000 | 498,596 | 3,508,164 | calm | 5.49 | 6.11 | 15.8 | 165 |
| 500,000 | 498,596 | 3,508,164 | bristled | 5.74 | 6.00 | 16.2 | |
| 1,000,000 | 997,153 | 6,997,931 | calm | 10.35 | 10.32 | 11.8 | 511 |
| 1,000,000 | 997,153 | 6,997,931 | bristled | 10.80 | 10.87 | 12.4 | |
| 2,000,000 | 1,994,459 | 13,979,217 | calm | 19.93 | 44.68 | 243.8 | 1,030 |
| 2,000,000 | 1,994,459 | 13,979,217 | bristled | 20.24 | 20.21 | 32.7 | |

- **Up to 200,000 hairs the frame time is the bare body's, within the noise of this run:** about 2.5 ms, which is the program's floor, not the fur. The fur's own cost shows from 500,000.
- **A frame passes 16.7 ms between one and two million hairs,** about 1.6 million if the cost is a straight line between those two rows. That is 20 times the default. Bristled costs about the same as calm.
- **With vsync on** (the default when watching) the window ran at 6.06 ms, the 165 Hz screen's limit, at 80,000 and at 200,000 hairs.
- **Body:** 18,438 triangles. A second full-screen run at 1,920 by 1,080 gave the same picture: 1.7 to 2.0 ms up to 80,000 hairs, 2.8 to 3.2 ms at 200,000.
- **Memory.** Vertices: 8 MB at 10,000 hairs, 22 MB at 30,000, 59 MB at 80,000, 145 MB at 200,000, 719 MB at a million. `nvidia-smi` listed the whole process at 887 MiB with the 80,000 coat and 1,191 MiB after the 200,000 coat had been grown.
- **At load:** thickness of every triangle, 0.4 s once, on 8 threads; then the coat, 58 to 80 ms at 80,000 hairs.
- **One creature, close to the camera, on a fast card.** A herd, a weaker card and the camera close enough for the fur to fill the screen were not measured.

**The second version**, same machine, same full-screen window, `fur_strands --bench` on `smooth_midpoly`. The other agent's Blender was running again (load average about 6), so the means and the slowest frames carry its noise; read the medians.

| Hairs asked | Fur triangles | State | Lighting | Median frame, ms | Mean, ms | Slowest 1%, ms |
|---|---|---|---|---|---|---|
| 0 | 0 | body only | studio | 1.60 | 1.73 | 3.0 |
| 10,000 | 100,581 | calm | studio | 1.92 | 2.18 | 11.2 |
| 10,000 | 100,581 | bristled | studio | 1.77 | 1.89 | 3.8 |
| 30,000 | 280,464 | calm | studio | 1.62 | 1.68 | 2.4 |
| 30,000 | 280,464 | bristled | studio | 1.82 | 1.96 | 3.7 |
| 80,000 | 740,169 | calm | studio | 1.94 | 2.92 | 12.9 |
| 80,000 | 740,169 | bristled | studio | 2.13 | 3.32 | 13.2 |
| 80,000 | 740,169 | calm | dusk | 2.80 | 3.65 | 13.9 |
| 80,000 | 740,169 | bristled | dusk | 3.34 | 4.22 | 14.5 |
| 80,000 | 740,169 | calm | cavern | 3.01 | 4.45 | 14.7 |
| 80,000 | 740,169 | bristled | cavern | 3.90 | 5.78 | 17.3 |
| 80,000 | 740,169 | calm | moonlit mist | 3.09 | 4.63 | 15.4 |
| 80,000 | 740,169 | bristled | moonlit mist | 2.96 | 3.77 | 14.2 |
| 80,000 | 740,169 | calm, fur casts no shadow | studio | 1.71 | 1.96 | 7.8 |
| 80,000 | 740,169 | calm, fur casts no shadow | dusk | 2.14 | 2.92 | 13.0 |
| 200,000 | 1,822,599 | calm | studio | 3.74 | 4.24 | 14.6 |
| 200,000 | 1,822,599 | bristled | studio | 4.27 | 5.03 | 15.5 |

- **The new lighting costs about 1 ms a frame** at this window size: 1.9 to 2.8 ms calm and 2.1 to 3.3 ms bristled, studio against dusk, by the median. Cavern and moonlit mist are within half a millisecond of dusk. HDR, bloom and fog are full-screen work, so the cost follows the number of pixels, not the number of hairs.
- **In the old lighting the new coat costs the same as the old** at 80,000 hairs, within this run's noise, although it has 29% more triangles (740,169 against 572,915). At 200,000 hairs it is now 3.7 ms against 2.7.
- **Memory.** A vertex is 112 bytes (was 80) and a fine hair has 11 vertices (was 9): 101 MB of vertices at 80,000 hairs, against 59. `nvidia-smi` listed the process at 1,337 MiB with that coat.
- **With vsync on** the window ran at 6.06 ms, the screen's limit, in dusk light.
- In the three new lightings the cameras stand lower, so the creature covers a slightly different share of the screen than in studio.

**The third version**, same machine and window, `fur_strands --bench --lights` on `smooth_midpoly`, 80,000 hairs asked (79,795 grown, 739,749 triangles). The other agent's Blender was running (load average 2.6 to 4.4).

| State | Lighting | Median frame, ms | Mean, ms | Slowest 1%, ms |
|---|---|---|---|---|
| body only | studio | 2.37 | 4.37 | 3.2 |
| combed 0 | studio | 2.69 | 2.76 | 4.1 |
| rough 0.5 | studio | 2.50 | 2.59 | 3.6 |
| spikes 1 | studio | 2.53 | 2.72 | 9.2 |
| combed 0 | dusk | 2.92 | 3.28 | 13.1 |
| rough 0.5 | dusk | 2.96 | 3.66 | 13.6 |
| spikes 1 | dusk | 3.18 | 3.89 | 14.3 |
| combed 0 | cavern | 2.97 | 3.42 | 13.5 |
| rough 0.5 | cavern | 3.30 | 4.36 | 14.4 |
| spikes 1 | cavern | 3.29 | 4.46 | 14.4 |
| combed 0 | moonlit mist | 2.90 | 3.08 | 13.2 |
| rough 0.5 | moonlit mist | 2.94 | 3.49 | 13.5 |
| spikes 1 | moonlit mist | 3.09 | 3.88 | 13.9 |

- **The one scale costs nothing that this run can show.** In dusk light the median is 2.92, 2.96 and 3.18 ms at 0, 0.5 and 1, against 2.80 calm and 3.34 bristled for the second version. The studio rows are about 0.6 ms above the second version's, and so is the body with no fur (2.37 against 1.60), so that difference is the machine on the day, not the fur.
- **Memory and triangles are unchanged:** the vertex is still 112 bytes; the two new values are in the block of numbers the shader gets once a frame. `nvidia-smi` listed the process at 1,401 MiB in studio light and 1,657 MiB in the others.
- **At load,** flattening the tufts is within the 0.1 to 0.5 s the thickness measurement already took; the coat grew in 104 to 150 ms.
- The hair counts other than 80,000 were not measured again.

**The fourth version**, same machine, `fur_strands --bench --looks` on `smooth_midpoly` in dusk light: a full-screen window of 3,440 by 1,440 pixels, vsync off, three seconds of frames per row after 1.5 seconds of waiting (4 seconds when ray traced). No Blender and no other `fur_strands` window was running (load average 1 to 3). Rasterized rows have 4x MSAA; ray-traced rows have one sample a pixel, frames blended, and the fur's shadow map as well as the rays. Graphics memory is the whole process as `nvidia-smi` lists it, and within one run it never goes down, so read it in the order of the rows.

| Hairs asked | State | Look | Stand-in for the coat | Median frame, ms | Mean, ms | Slowest 1%, ms | Frames a second | Graphics memory, MiB |
|---|---|---|---|---|---|---|---|---|
| 80,000 | combed 0 | LDR rasterized | | 2.45 | 3.08 | 13.2 | 324 | 1,389 |
| 80,000 | spikes 1 | LDR rasterized | | 2.97 | 3.43 | 13.7 | 291 | 1,389 |
| 80,000 | combed 0 | HDR rasterized | | 2.93 | 3.43 | 13.8 | 292 | 1,645 |
| 80,000 | spikes 1 | HDR rasterized | | 3.29 | 4.07 | 13.9 | 246 | 1,645 |
| 80,000 | combed 0 | ray traced, LDR look | guard hairs and 1 fine hair in 8 | 12.25 | 12.56 | 21.2 | 80 | 2,435 |
| 80,000 | spikes 1 | ray traced, LDR look | guard hairs and 1 fine hair in 8 | 12.52 | 12.47 | 13.5 | 80 | 2,435 |
| 80,000 | combed 0 | HDR ray traced | guard hairs and 1 fine hair in 8 | 12.69 | 12.65 | 13.8 | 79 | 2,437 |
| 80,000 | spikes 1 | HDR ray traced | guard hairs and 1 fine hair in 8 | 13.02 | 12.96 | 13.9 | 77 | 2,437 |
| 80,000 | combed 0 | HDR ray traced | nothing | 10.26 | 10.25 | 11.4 | 98 | 2,437 |
| 80,000 | spikes 1 | HDR ray traced | nothing | 10.30 | 10.28 | 11.5 | 97 | 2,437 |
| 80,000 | combed 0 | HDR ray traced | guard hairs | 11.08 | 11.05 | 11.8 | 90 | 2,437 |
| 80,000 | spikes 1 | HDR ray traced | guard hairs | 12.37 | 12.32 | 13.3 | 81 | 2,437 |
| 80,000 | combed 0 | HDR ray traced | every hair | 25.42 | 25.53 | 31.7 | 39 | 2,437 |
| 80,000 | spikes 1 | HDR ray traced | every hair | 25.18 | 25.15 | 29.2 | 40 | 2,437 |
| 0 | body only | HDR rasterized | | 1.83 | 1.90 | 3.2 | 526 | 2,437 |
| 0 | body only | HDR ray traced | | 9.18 | 9.22 | 10.4 | 108 | 2,693 |

| Stand-in for the coat | Hairs in it | Triangles | Worked out on the processor, ms a frame |
|---|---|---|---|
| guard hairs | 3,599 | 75,579 | 0.8 |
| guard hairs and 1 fine hair in 8 | 13,123 | 161,295 | 1.6 to 1.7 |
| every hair, of 80,000 | 79,795 | 761,343 | 6.4 to 6.6 |
| guard hairs and 1 fine hair in 8, of 200,000 | 28,815 | 313,416 | 2.7 to 3.0 |
| every hair, of 200,000 | 199,518 | 1,849,374 | 14.6 to 14.9 |

- **The HDR pipeline costs about 0.4 ms a frame** at this size (2.45 to 2.93 combed, 2.97 to 3.29 spiked) and 256 MiB.
- **Ray tracing costs about 10 ms a frame more,** which makes the frame four times as long, and about 800 MiB. Of that, lighting the body and the ground with rays is 7.4 ms (the body alone, 1.83 to 9.18); a stand-in of 161,295 triangles rebuilt every frame is another 2.4 to 2.7 ms.
- **It stays above 60 frames a second at 80,000 hairs full screen** with any stand-in but "every hair": 77 to 98. The LDR look ray traced costs the same as the HDR one, because it is the same float picture underneath.
- **Every hair as the stand-in is too slow:** 25 ms, 40 frames a second, of which 6.5 ms is the processor placing 580,000 vertices and most of the rest is the graphics card building the acceleration structure again. **A stand-in a fifth that size is enough:** `--check --proxy 3` and the start's stand-in give ground shadows that could not be told apart in the spiked cavern picture, and whole pictures no more different (0.5 to 1.6%) than two runs of the same one. With no stand-in (`--proxy 0`) the shadow is the bare body's: smaller, and without the fringe of quills.
- **At 200,000 hairs** (a second run, `--hairs 200000`): rasterized 4.3 to 5.2 ms; ray traced with the start's stand-in 15.7 to 16.5 ms, 61 to 64 frames a second, just above 60; with every hair 93 ms, 13 frames a second.
- **In a smaller window** (a third run, `--window 1920x1080`; Hyprland made it 1,701 by 1,390, 48% of the pixels): ray traced 7.4 to 8.3 ms, 121 to 131 frames a second; the body alone ray traced 4.8 ms. The ray tracer's cost follows the number of pixels; the stand-in's does not (every hair is still 25 ms).
- **With vsync on** a tiled window ran at 6.06 ms rasterized, LDR and HDR, and at 7.5 to 7.8 ms ray traced.
- **A dome of 4,000 m radius made a ray-traced frame about ten times slower** than one of 1,000 m or less (20 seconds against 2 for 150 frames of two cameras). Why was not found; the dome is 1,000 m.
- The hair counts other than these, the other lightings and the other bodies were not measured ray traced.

### What it would take to follow an animated body

**As built the hairs do not follow bones or morph targets.** They are a separate mesh, a child of the model, so they follow the model's position and rotation and nothing else. Bend a leg or play the `extended` target and the fur stays where the calm body was.

- **Bones.** Give every hair vertex the joint numbers and weights of the body at its root (taken from the corners of its triangle), put Bevy's `SkinnedMesh` with the body's joints on the coat, and call Bevy's `skin_model` in the fur's vertex shader before placing the hair, so that the root, the normal and the comb direction are carried by the bones. Bevy 0.19 has the pieces (`skinning.wgsl`, read in section 2), and its issue about there being no example of a custom vertex shader with skinning (#13988, summary) says nobody has written it down. Not tried; a day or two of work by inference.
- **Morph targets.** The fur mesh would need its own target holding where each root moves to. Bevy stores 48 bytes per vertex per target, about 35 MB per target at 80,000 hairs. Cheaper: one more vertex attribute with the root's offset, blended in the fur shader by the same weight.
- **Movement.** The four springs follow the whole body. On a skeleton each bone moves its own way, so the lag would have to be worked out per bone (a handful of springs per bone, passed as a small table) or a tail whipping round would not throw its own fur.
- **Shot spikes** are still separate small objects, as in the summary; a quill here is not an object and cannot leave.

### What it would take to be production-worthy

Inference.

- The skinning above. Without it this is fur on a statue that slides.
- A painted mask and length map in place of the colour and height rules, which fit this one picture of this one creature. Comb direction painted or groomed, not derived.
- A body modelled without spikes, in place of a pieces model with its spikes hidden.
- Hair that stops at the ground and at the body's other parts, at least for the quills.
- Fewer hairs on a creature that is far away or one of many; the rule that thins sub-pixel hairs still sends every vertex to the card.
- A check on a weaker card, and in the game's own lighting.
- Kiln's mission keeps characters out of scope; nothing here is a stage, a check or a term of kiln.

### Watching it

From the repo root:

```
(cd learn/research/fur-animation-trial/bevy_probe && CARGO_TARGET_DIR=../../../../target cargo build --release --bin fur_strands --features overlay)
target/release/fur_strands
```

It needs at least one of the three bodies: `models/b_pieces_p1_morph.glb` (`scripts/run_all.sh` makes it) and the two smooth ones in `../tripo-api-trial/models/`; a body that is not there is left out. The window starts a 42-second loop by itself, in dusk light: combed in a light breeze; at 3 s the wind rises to 2.0 and the coat ruffles to 0.22; a gust at 6.5 s; a dash and a stop at 9.5 s; from 14 s agitation climbs slowly to 0.76 over ten seconds, through ruffled, rough and hackles; at 24.5 s the spikes sweep forward from the tail in one second; held; from 29.5 s back down through every stage to combed over nine seconds while the wind drops; a shake at 39 s. The keys for the calm coat, lean, direction of travel, lighting and body do not stop the loop, so they can be compared while it runs. The agitation and the name of its stage, the hair count, the triangle count and the frame time averaged over 90 frames are drawn in the window with the keys. So are two lines for the fourth version: `picture:` (LDR or HDR pipeline, tone mapper, bloom, exposure, and what the screen gets) and `lighting:` (rasterized, or ray traced with what stands in for the coat and what that costs). A key that has something to say (why there is no HDR on the screen, what ray tracing does and does not light) writes it under them for 14 seconds.

**What to look at for the fourth version,** which pictures cannot settle:

- **K, in dusk light at spikes (5):** the sunlit quills and back. LDR cuts them off at white; the HDR pipeline keeps their shape. Then M through the tone mappers, and - and = for exposure.
- **P, then L through the lightings:** the ground round the feet and the shadow's edge; the grain; and with I, the grain against the softness of blended frames.
- **P with D, S and G:** whether the fur smears when it moves, and whether the ground's shadow keeps up with the coat. This is the lag no still shows.
- **J with P on, at spikes in cavern light:** the shadow with no stand-in, the guard hairs, the start's, every hair, and the frame time of each.
- **`target/release/fur_strands_scrgb --display-hdr`** after `bevy_probe/scrgb/build.sh`: whether the highlights are really brighter than the desktop's white, and whether the picture as a whole is as bright as it should be.

| Key | What it does |
|---|---|
| Up, Down | Agitation by hand, while held, 0.3 a second |
| B | Runs the scale to spikes in 5 seconds, or back to combed in 6 |
| 1 2 3 4 5 | To a stage in one second: combed 0, ruffled 0.3, rough 0.5, hackles 0.7, spikes 1.0 |
| F | The calm coat, what agitation 0 looks like: combed (the start), sleek, tousled |
| Q | Quill lean: forward (the start), outward, rearward |
| , and . | Less or more lean, 0.2 to 2.0 |
| V | The change travels from tail to head (the start), or from neck to tail |
| N | Next body: smooth mid-poly (the start), smooth low-poly, P1 with its spikes retracted |
| L | Lighting: dusk (the start), cavern, moonlit mist, studio |
| W | Wind on or off |
| [ and ] | Less or more wind, 0 to 4.0 in steps of 0.25; a gale from 3.0 |
| G | A gust |
| D | Dash forward, stop, and walk back |
| S | Shake |
| H | Hair count: 10,000, 30,000, 80,000 (the start), 200,000 |
| C | Whether the fur casts a shadow |
| X | Draws each hair's agitation as a colour (blue combed, green ruffled, yellow hackles, red spikes); again, the guard hairs in cyan; again, the coat |
| K | The picture: the HDR pipeline, or plain LDR. Until K, M or `--hdr`, each lighting has what it always had |
| M | Next tone mapper of the picture now shown: none, Reinhard, Reinhard luminance, ACES fitted, AgX, SomewhatBoringDisplayTransform, TonyMcMapface, Blender filmic |
| - and = | Exposure half a stop darker or brighter, -6 to +6 |
| E | Auto exposure on or off; it works only with the HDR pipeline, and says so |
| O | Says why the screen gets an SDR signal, with what the surface offers and what each monitor is set to. In `fur_strands_scrgb --display-hdr`: says what the screen gets |
| P | Lighting of the body and the ground: rasterized, or ray traced. Says why if ray tracing cannot run |
| J | Ray traced: what stands in for the coat: guard hairs and one fine hair in 8 (the start), every hair, nothing, guard hairs |
| I | Ray traced: frames blended (the start), or not |
| T | Turntable on or off |
| R | Camera back to where it started |
| Space | Pauses or resumes the loop. Any key that changes agitation, wind or movement pauses it |
| Escape | Quits |

No key was removed. B, Up, Down, F, V and X kept their keys and changed meaning in the third version; 1 to 5 were new then. K, M, -, =, E, O, P, J and I are new in the fourth, and none of them pauses the loop.

Other uses:

```
target/release/fur_strands --hdr 0 --rt 0             # start LDR rasterized; --hdr 1 --rt 0, --hdr 0 --rt 1 and --hdr 1 --rt 1 are the other three looks
target/release/fur_strands --rt 1 --proxy 0           # ray traced with nothing standing in for the coat; 1 guard hairs, 2 the start, 3 every hair
target/release/fur_strands --check --out learn/research/fur-animation-trial/pictures/fur_strands   # no window: the four looks, 64 pictures and 16 contact sheets, 38 seconds
target/release/fur_strands --check --strip --out <folder>   # no window: the third version's 104 pictures and 3 contact sheets, 15 seconds
target/release/fur_strands --bench --looks            # full screen for two minutes: the fourth version's table above
target/release/fur_strands --bench --looks --window 1920x1080   # the same in a window, which the compositor may resize; the size is printed
learn/research/fur-animation-trial/bevy_probe/scrgb/build.sh    # builds target/release/fur_strands_scrgb, 94 seconds
target/release/fur_strands_scrgb --display-hdr        # the same program sending scRGB to the screen
target/release/fur_strands --bench --lights           # full screen for a minute: the third table above
target/release/fur_strands --bench                    # full screen for about three minutes: every hair count as well
target/release/fur_strands --bench --hairs 1000000    # one hair count
target/release/fur_strands --keys "2,3,4,5,1,UP,DOWN,B,X,F,Q,MORE,LESS,V,L,N"   # presses the keys itself, one every 1.5 s, and prints the state; MORE and LESS are . and ,
target/release/fur_strands --keys "5,P,J,J,J,J,I,I,K,K,M,=,-,E,E,O"   # the fourth version's keys; what each has to say is printed
target/release/fur_strands --body p1_retracted --light 0 --calm 1   # another body, lighting and calm coat at the start: 0 to 2 or a name, 0 to 3, 0 to 2
target/release/fur_strands <model.glb> --hairs 40000  # another body, another count
```

### What could not be done or verified

- **The fourth version was not seen by anyone on a screen.** Its window was opened under a time limit in each of the four looks (14 seconds each) and with `--keys` for every new key; the state printed changed as it should, and stderr held no warning or error from Bevy or wgpu in any window run. The pictures were read by the author, an AI model. The only warning seen anywhere is Bevy's about `ShadowLodOrigin` in `--check`, where there is a point light and no window; it comes from the cavern's lamp and not from these keys.
- **HDR on the screen was not seen at all:** see the fourth version's section. That the surface is opened as scRGB is from Bevy's log line; what the monitor then shows is not known.
- **Ray-traced fur (option c) was not tried.** The reasons given are from reading Solari's source, not from an attempt.
- **DLSS Ray Reconstruction, Solari's denoiser, was not tried:** it needs a crate this project has never used. The grain and the softness reported here are of Solari without it.
- **Why the far ground is darker ray traced** was not pinned down.
- **Movement under ray tracing** (smear, the shadow keeping up, the first second after a change) was judged from two stills: one window picture in a wind of 2.0 with the camera turning, and the gale pictures.
- **Ray traced, dusk and cavern on `smooth_midpoly` were looked at properly;** studio on `p1_retracted` in one window picture: its shadow is the retracted body's and the coat's, as it should be, and is plainly speckled even with frames blended. Moonlit mist ran (pressed through `--keys`, no error) and was not looked at. `smooth_lowpoly` was switched to with N while ray tracing and grew its stand-in, and was not looked at.
- **The Rust copy of the vertex shader** (`Shape::of`) was checked against the shader by reading and by the stand-in's shadow lying where the coat's shadow map puts it; no vertex was compared number by number.
- **The third version was not seen moving by anyone** when this was written. Its window was opened once for 16 seconds, ran the loop at the screen's 165 frames a second and saved pictures of itself with the overlay; keys 1 to 5, Up, Down, B, X, F, Q, V, G, D and Space were pressed through `--keys` and the printed state changed as it should, including the change travelling ("0.68 to 0.36") while B ran.
- **That the guard hairs are hidden at 0 rests on two things:** the code, where a guard hair and a fine hair get the same inputs and the same arithmetic there, and one pair of pictures from two cameras. It was not checked from every side or on the other two bodies.
- **The hackles and the middle of the scale were tuned by one pair of eyes in four rounds,** an AI model's, from stills.
- **The second version was not seen moving by anyone** when this was written. Its window was opened once for 14 seconds, ran the loop at the screen's 165 frames a second and saved pictures of itself with the overlay; the new keys were pressed through `--keys` and the printed state changed as it should for roughness, lean, lean amount, wave direction, lighting, body and wind up to 4.0.
- **The first version was not seen moving by its author.** The window was opened by the author under a time limit, ran its loop at the screen's 165 frames a second, and saved pictures of itself; every key was pressed through `--keys` and the printed state changed as it should for bristle, wind, hair count, shadows, turntable and pause. That a dash, a shake and a gust look right when triggered by key was seen only in the check pictures, which use the same code.
- **The owner's drawings were not available to the author.** "A dense wall of quills well beyond body height" was aimed at from the description.
- **No skinned or morphing body** was tried.
- **Instancing and shell fur were not built**, so nothing here compares their cost.
- **Graphics memory** is the whole process as `nvidia-smi` lists it, not the fur alone.
- **The frame times were taken with Blender running** on the same machine.
- **Only the P1.0 pieces body was looked at.** The program takes any model; the fused and P2.0 bodies were not rendered with fur.

## Method

The work was done on 2026-10-08 in one sitting. The Tripo note's sections 10 and 11 and Bevy's source were read first. A second agent did the web reading in parallel and returned citations with a grade and a note of how each page was reached; its report was used as given and is marked wherever a page was not read in full.

The probe was written before the Blender scripts so that every shape could be looked at in Bevy, the only place the mission verifies output. Spike detection went through four variants, each painted on the model and looked at, before thickness was chosen. The first exports had every morph weight at 1 by default; that was found by reading the file back, fixed, and everything run again from `scripts/run_all.sh`. Tripo's rigged and spiked files appeared part-way through; an armature placed by script had already been made by then and is kept as a second data point.

Models under `learn/research/tripo-api-trial/` were only read. Only this file and the folder beside it were written; nothing under `kiln/`, `crates/` or `profiles/` was touched, and nothing was committed.
