# A trial of the Blender stages on Tripo's models: repair, reduce, UVs and baking, scale

Measured 2026-10-08 on the development machine, in kiln's pinned Blender 5.2.2 through `tools/bl`: headless, factory settings, offline. 561 Blender runs, none of which crashed. Everything it produced is in [`blender-stages-trial/`](blender-stages-trial/); measurements of the main results sit beside the Tripo trial's, in [`tripo-api-trial/measurements/stages_*`](tripo-api-trial/measurements/).

This is a research note. It tests, on the models of [`tripo-api-trial.md`](tripo-api-trial.md) sections 9 and 10, what the desk research in [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md) Part 2 said Blender's API offers. It adds no stage to kiln and does not decide the stage list. It does not draw on the `first-attempt` tag.

## The question

Tripo's H3.1 model returns the best asset of the three tried: one closed mesh with base colour, metallic-roughness and normal maps at 4096 pixels. But it has about 1.9 million triangles, against a placeholder budget of 20,000 in `profiles/pit.toml`. Tripo's low-poly models (P1.0, P2.0) fit the budget and come without texture; Tripo's paid texture step gives them base colour only, on thousands of UV islands.

**Can fixed, headless Blender scripts turn the H3.1 result into an asset inside the budget that keeps its three maps, and repair and re-texture the low-poly ones, well enough that kiln does not need Tripo's paid Smart UV and texture steps?**

## How to read this

- **Measured** means it was run on this machine on 2026-10-08 and the record is in [`blender-stages-trial/runs/`](blender-stages-trial/runs/), one set of files per run, summed up in the CSV files beside that folder.
- **Looked at** means a review picture that I opened and describe. I am not the shape review: I describe, I do not approve.
- **Desk** means what [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md) said from the documentation, before anything was run. Section 10 sets it against what was measured.
- **Inference** means this note's reasoning. Section 11 is inference from end to end and is marked so.
- **Two subjects and a handful of runs are observations, not rates.** One crate and one creature. "Did not crash in 68 runs" does not mean it cannot.
- **Times are wall-clock on a machine that was not idle.** Another program's Blender was running at times, and several of my own runs overlapped. Treat a time as good to about a fifth.
- Kiln's own words (run, size, target profile, raw output, stage, shape review, review pictures, store) are used as `CONTEXT.md` defines them.

### Terms used here

The earlier notes define mesh, triangle, UV, UV island, seam, base colour, normal map, roughness, metallic, welded, boundary edge (called an **open edge** in the tables), non-manifold edge, loose part (a **piece**) and degenerate face (a **zero-area face**). Terms added or leaned on here:

- **Round trip:** importing a file into Blender and exporting it again without changing anything.
- **Stored normals (custom normals):** the direction each corner of the surface is lit from, as the file gives it. Blender keeps them beside the mesh and uses them in place of the ones it would work out from the faces.
- **Collapse:** the Decimate modifier's main mode. It removes edges one at a time, cheapest first, until a share of the triangles is left.
- **Bake:** drawing one model's look into another model's textures. Here: the dense model's colour, roughness and surface detail are drawn into new textures laid out for the reduced model.
- **Selected to active:** the bake that does this. For every pixel of the reduced model's texture a ray is sent from its surface to find the dense surface.
- **Cage extrusion and ray distance:** how far outside the reduced surface the ray starts, and how far it may travel. Too little and the ray misses; too much and it finds the wrong part.
- **Margin:** how many pixels a baked colour is spread beyond the edge of its UV island, so that no unpainted pixel shows at a seam.
- **Texel density:** texture pixels per metre of surface, at the size the asset will have. All figures here are at 0.8 m.
- **Sliver:** a triangle smaller than a hundredth of the model's mean triangle.
- **Samples:** how many rays Cycles, Blender's renderer, sends for each pixel. More is slower and smoother; a bake of flat colour needs one.
- **Picture difference:** a number this trial uses to rank results. Two review pictures from the same camera are compared pixel by pixel; the mean difference of the colour values is given on a scale of 0 to 255. The same model rendered twice gives exactly 0. It ranks; it does not say what the eye sees.

## Summary

**Yes for the dense model, with one catch each for repeatability and for UVs. No for the creature's low-poly models.**

### Which stages work headless

Every stage ran through `tools/bl` with no display, no add-on beyond those Blender ships, and returned `FINISHED`. None needed a retry.

| Stage | Works headless? | Key numbers (crate, creature) |
|---|---|---|
| Round trip | Yes | 8 s and 9 s for the dense files, 2.0 GB. Textures copied byte for byte. It also repairs: all three of Tripo's invalid P2.0 files come out valid |
| Repair | Yes, but only four of its rules are safe to fix | 40 to 47 s on a dense model, of which 30 s is counting. Hole filling and "delete small pieces" damage these models |
| Reduce (Collapse) | Yes | 1,801,451 and 1,951,822 triangles to exactly 20,000 in 26 to 37 s, 2.3 to 2.7 GB. 68 runs, no crash. Same bytes every time |
| UVs and bake | Yes, on the GPU (OptiX) and on the CPU | Three maps at 2048 in 11 to 13 s; a whole run 19 to 25 s, 3.6 to 4.0 GB. All three maps arrive in the `.glb`, metallic and roughness in one image |
| Scale and place | Yes | Kiln's `scale_to_size` takes 1 s on a reduced model and 7 to 8 s on a dense one. Turning to Bevy's forward is one more half-turn |

### What the best chain produces

Five fixed scripts, one after another, from the raw 57 MB and 66 MB files: repair, reduce, UVs and bake, kiln's own `scale_to_size`, place.

| | Crate | Creature |
|---|---|---|
| Triangles | 19,999 | 20,000 |
| File | 4.8 MB | 8.4 MB |
| Maps | base colour, metallic-roughness, normal, each 2048 | the same |
| Open edges, non-manifold edges, pieces | 2, 1, 1 | 0, 1, 1 |
| Validator errors | 0 | 0 |
| Kiln's two checks | pass | pass |
| Time | 69 s, or 96 to 103 s for the same bytes every time | 77 to 82 s, or 107 to 110 s |
| Peak memory | 3.8 GB | 4.1 GB |

Looked at beside the dense originals at three-quarter, front and closest view, both are hard to tell from them. The crate has a few light flecks on one frame edge; the creature has lost nothing I can see at 20,000 triangles.

### How it compares with Tripo's own routes

- **Against P1.0 or P2.0 plus Tripo's texture step:** the chain's models have three maps where Tripo's have base colour alone, a twelfth to a third of the UV islands (251 against 3,105 on the crate; 1,401 against 4,208 and 4,893 on the creature), no stray pieces, and pass the validator where Tripo's textured files do not. Looked at, the chain's crate is sharp where Tripo's is blurred, and the chain's creature is the H3.1 shape, which the Tripo note already judged closest to the drawing.
- **Against H3.1 asked for 20,000 triangles directly** (two files that arrived during the trial): this is the real rival. Tripo's own file is also in budget (17,080 and 19,007 triangles) and also has all three maps, at 4096. On the crate its edges are ragged and the chain's are straight. On the creature it is a different, softer generation with fewer spikes; neither is plainly wrong.
- **The low-poly crate hides its triangles.** Tripo's P2.0 crate "at 20,000" is a 108-triangle box with 19,850 triangles of other pieces sealed inside it. A script removes them. That 108-triangle box with the H3.1 maps baked onto it looks as good as the 20,000-triangle one.
- **Baking H3.1's look onto the creature's low-poly models does not work.** They are different generations with different shapes; the colours land in the wrong places.

### The catches

1. **A file that Blender wrote is not the mesh Blender had.** Every hard edge is stored as two rows of points, and the importer does not join them. The first whole chain tore the crate into 94 pieces with 10,194 open edges this way. Every stage that edits the surface has to weld by distance when it reads a file. With that one line the chain is sound.
2. **The normal map bake is not the same bytes twice.** Between 1 and 5 pixels of 4 million come out one step different, on the GPU and on the CPU. Run with one thread it gave the same bytes in 17 of 17 runs, at about three times the bake time. Kiln's rebuild depends on this.
3. **Smart UV Project is the wrong tool for a spiky shape.** It cut the creature into 4,174 islands, as many as Tripo's texture step. Laying the reduced mesh's own islands out again gave 1,395.
4. **Collapse keeps the stored normals and leaves them wrong.** The reduced crate shows jagged shading along every edge until they are cleared.

**What the measurement cannot say:** whether any of this holds for a third subject, how the results look in the pit game, and what texture size the profile should allow. Section 13 lists these.

## 1. This machine and versions

| | |
|---|---|
| Processor, memory | AMD Ryzen 7 5800X (16 threads), 31 GB RAM, 62 GB swap |
| Graphics card | RTX 3080, 10 GB, also driving the desktop; driver 610.57.04 |
| System | Linux 7.2.5-3-omarchy |
| Blender | 5.2.2 LTS, through `tools/bl` (`--background --factory-startup --offline-mode`) |
| glTF add-on | the one bundled: "Khronos glTF Blender I/O v5.2.40" |
| Khronos glTF Validator | 2.0.0-dev.3.10 |
| `review_pictures` | 0.1.0, Bevy 0.19.1 |
| Python | 3.14.7 for the scripts outside Blender, standard library only |
| Kiln | commit `91a38b9` |

- **`/usr/bin/time` is not installed**, and nothing may be installed. [`scripts/timed.py`](blender-stages-trial/scripts/timed.py) stands in for it: it reads the peak resident memory of the process from `wait4`, which is the figure `time -v` prints. It also watches the machine's free memory twice a second and kills a run that leaves under 2 GB.
- **Memory was never short.** The largest process was 6.5 GB (a 4096 bake) and the machine never had under 4.8 GB available.
- **No core dump.** `coredumpctl` lists none since the trial began at 16:02. The four Blender crashes it lists from 13:19 to 13:43 belong to the local generator trial.

## 2. Method

### The inputs

All from [`tripo-api-trial/models/`](tripo-api-trial/models/), only read:

| File | What | Triangles |
|---|---|---|
| `crate_h31_default`, `orb_h31_default` | H3.1 on defaults: the dense, textured sources | 1,801,451 and 1,951,822 |
| `crate_p1_tri_req20000`, `crate_p2_tri_req20000` | P1.0 and P2.0 asked for 20,000, untextured | 19,796 and 19,958 |
| `orb_p1_tri_req20000`, `orb_p2_tri_req20000` | the same for the creature | 18,438 and 20,389 |
| the `_textured` and `_smartuv` versions | Tripo's own texture and Smart UV steps | |
| `crate_h31_req20000`, `orb_h31_req20000` | H3.1 asked for 20,000, made in the web app during this trial | 17,080 and 19,007 |

"The creature" is the `orb_*` models. They are made from someone else's artwork for a private test: no picture or model of it is committed (section 14).

### The scripts

Each stage is one script in [`blender-stages-trial/scripts/`](blender-stages-trial/scripts/) with the shape a kiln stage has: it reads one `.glb`, writes one `.glb`, and writes a JSON file of facts.

```
tools/bl <stage>.py <in.glb> <out.glb> <facts.json> [name=value ...]
```

| Script | Stage |
|---|---|
| `roundtrip.py` | import and export, nothing between |
| `repair.py` | weld, dissolve degenerate faces, delete loose bits, delete small or hidden pieces, turn faces outward, fill holes, clear stored normals: each optional |
| `reduce.py` | Collapse, Planar, Un-Subdivide, voxel remesh, QuadriFlow |
| `uv_bake.py` | new UVs or the old ones laid out again, then the bake of three maps |
| `place.py` | turn about the up axis, origin to the bottom centre |
| kiln's own `scale_to_size` | called as `build()` calls it, by `run_scale.sh`, with a work folder under `work/` and never the store |

Every operator's return value is checked, because an operator that cancels does not raise (desk, confirmed: QuadriFlow did exactly that).

### What was recorded

For every run: the settings, seconds, peak memory, exit status and signal (`runs/<name>.run.json`), the stage's own facts and the seconds of each step (`.facts.json`), Blender's output (`.log`), and what the output file holds (`.glb.json`, `.measure.json`, `.validator.txt`). The main results were then measured with the Tripo trial's `scripts/measure_model.sh`, unchanged, so that their numbers line up with that note's.

Four measures were added, each a short script:

- **How the triangles are spread** ([`glb_facts.py`](blender-stages-trial/scripts/glb_facts.py)): the share of triangles that holds 99% of the surface, and the share that are slivers. It gives the Tripo note's figures for the P2.0 crate (18.5% and 72.7%), so the two notes can be read together.
- **Distance to the dense surface** ([`distance.py`](blender-stages-trial/scripts/distance.py)): from 20,000 points on the reduced model to the dense one, and back. The second direction shows what was lost.
- **Whether the bake's rays will land** (inside `uv_bake.py`): 20,000 points spread evenly over the reduced surface, each sending the ray the bake would send, without Cycles.
- **Picture difference** ([`picture_diff.py`](blender-stages-trial/scripts/picture_diff.py)), defined above. `review_pictures` gave the same pixels twice for the same file, so any difference is the model's.

## 3. Round trip

Import, then export with the settings kiln's `scale_to_size` uses: join vertices on import, keep the file's normals, keep each texture's format, no tangents. 56 runs; [`roundtrip.csv`](blender-stages-trial/roundtrip.csv).

### What changes

| | Crate, H3.1 | Creature, H3.1 | Crate, P2.0, 20,000 |
|---|---|---|---|
| Seconds, peak memory | 8.3 s, 2.0 GB | 9.3 s, 2.0 GB | 0.7 s, 0.4 GB |
| File size | 56,826,900 to 57,173,032 bytes | 65,804,832 to 65,804,660 | 481,172 to 364,328 |
| Triangles | unchanged | unchanged | unchanged |
| Vertices stored | 926,464 to 937,286 | 1,034,900, unchanged | 10,021 to 10,148 |
| Points after welding | 900,728, unchanged | 975,882, unchanged | 10,021, unchanged |
| Normals | none turned by more than 0.34° | none by more than 0.52° | 4 of zero length replaced |
| Textures | three, each the same bytes | three, each the same bytes | none |
| Extensions named | `FB_ngon_encoding` and `KHR_materials_volume` dropped | the same | the same |
| Validator | 0 errors, 1 warning, before and after | the same | 4 errors to 0 |

- **The shape and the textures survive.** No point moves, and the three images are copied without being decoded: same SHA-256.
- **Stored vertices grow where shading is hard.** The crate, which has flat faces, gains 1.2%. The creature, smooth all over, gains none. This is small here and matters a great deal in section 8.
- **The two extensions Tripo names are not in use.** Its files list `KHR_materials_volume` and `FB_ngon_encoding` but no material carries the first. Dropping them changes nothing that draws.
- **The low-poly files shrink by a quarter** (481 KB to 364 KB) with the same triangles. Why was not looked into.
- **The warning that stays** is "Material requires a tangent space but the mesh primitive does not provide it." Tripo's files have it too. Bevy works tangents out itself.
- **The same file twice gives the same bytes.**

### A round trip repairs Tripo's invalid files

Three of Tripo's P2.0 crate files fail the validator (Tripo note, section 9). All three pass after a round trip:

| File | Errors before | After |
|---|---|---|
| `crate_p2_tri_req20000` | 4: normals of zero length | 0 |
| `crate_p2_tri_req20000_textured` | 2: a declared minimum that is not the real minimum | 0 |
| `crate_p2_tri_req20000_smartuv` | 1 | 0 |

So does every textured creature file. Nothing is printed when this happens: Blender replaces a zero-length normal with one of its own and the exporter writes fresh minimums. The desk note warned that the importer "repairs silently"; here that is a help.

### Other exporter settings

| Setting changed | What it did (crate H3.1; creature H3.1) |
|---|---|
| Do not join vertices on import | 944,971 vertices stored in place of 937,286; 1,035,274 in place of 1,034,900 |
| Import with smooth normals, not the file's | Vertex count stays exactly as it came, and the file is the smallest. But 6.6% and 22.5% of the normals turn by more than a degree: the look changes |
| Clear the stored normals | The same loss of the generator's shading |
| Write tangents | File grows to 99.5 MB and 82.7 MB. The crate then **fails the validator with 5 errors** (tangents of zero length, on its zero-area faces); the creature passes and loses the warning |
| Textures as WebP | All three re-encoded at the default quality of 75: the crate's 3.1 MB normal map becomes 41 KB. Lossy, and it would apply to the normal map too |

**The settings that change least are the ones kiln already uses.**

### The setting a person would choose

None for this stage. It is the cost of entering Blender at all, and it is small.

## 4. Repair

129 runs; [`repair.csv`](blender-stages-trial/repair.csv). Each rule was run alone on each model, so that what it does can be told apart from the others. Defects are counted after welding at a millionth of a metre, as the Tripo note counts them.

### The models before

| Model | Triangles | Open edges | Non-manifold | Inside-out joins | Zero-area faces | Pieces |
|---|---|---|---|---|---|---|
| Crate, H3.1 | 1,801,451 | 2 | 1 | 18 | 21 | 1 |
| Creature, H3.1 | 1,951,822 | 0 | 1 | 18 | 0 | 1 |
| Crate, P1.0 | 19,796 | 18 | 1 | 0 | 0 | 4 |
| Crate, P2.0 | 19,958 | 97 | 87 | 4 | 58 | 28 |
| Creature, P1.0 | 18,438 | 157 | 20 | 1 | 0 | 157 |
| Creature, P2.0 | 20,389 | 1,169 | 12 | 0 | 0 | 236 |

An "inside-out join" is an edge whose two faces wind opposite ways: one of them faces inward.

### What each rule does

| Rule and setting | What it fixed | What it broke |
|---|---|---|
| **Weld** at 0.01 mm | Dense crate: 3 vertices joined | Nothing |
| Weld at 0.1 mm | Dense crate: 315 joined. Low-poly: nothing to join | Nothing seen |
| Weld at 1 mm | | P2.0 crate: 4,631 vertices joined, open edges 97 to 161, non-manifold 87 to 234 |
| Weld at 10 mm | | Every low-poly model collapses: 18,438 triangles to 7,333 on the P1.0 creature, 7% of its surface gone |
| **Dissolve degenerate** at 0.01 mm | Dense crate: 46 faces, zero-area faces 21 to 0, and with the weld its 2 open edges and 1 non-manifold edge go too | Nothing |
| Dissolve at 0.1 mm | P2.0 crate: 68 faces, zero-area 58 to 2 | Dense crate: 4,664 faces removed and the open edges stay |
| Dissolve at 1 mm | | P2.0 crate: 14,413 of 19,958 faces removed |
| **Delete loose vertices and edges** | Nothing to delete in any model | Nothing |
| **Turn faces outward** | Inside-out joins to 0 in every model: 10 and 9 faces turned on the dense models, 55 to 57 on three of the low-poly ones | Stored normals no longer match (below) |
| **Fill holes** of up to 4 sides | P1.0 crate: 6 holes, open edges 18 to 0. P2.0 creature: 206 holes, open edges 1,169 to 350 | Filled faces get UVs that span the whole texture: on the textured creature the UV square "in use" jumps from 40% to 91% |
| Fill every hole | P1.0 creature: 19 holes, one of 65 sides. P2.0 creature: 235 holes, 655 triangles added | P2.0 creature goes from 20,389 to **21,044 triangles**, further over the budget. Each spike's open base gets a lid nobody sees |
| **Delete small pieces**, under 1% of the triangles | | **Deletes the crate.** On both low-poly crates the visible box is the piece with the fewest triangles: 310 triangles removed are 95% of the P2.0 crate's surface, 110 are 88% of the P1.0's |
| Delete small pieces, under 1% of the surface | P2.0 crate: 20 pieces, 17,626 triangles, 3% of the surface | Creature: 155 and 235 pieces go, a quarter of the surface. They are the spikes |
| **Delete hidden pieces** (new in this trial) | P2.0 crate: 27 pieces, **19,850 triangles**, leaving 108. P1.0 crate: 2 of 3 inner pieces, leaving 8,627 | Nothing: no piece removed from either creature or either dense model |
| **Clear stored normals**, sharp edges over 30° | Normals agree with the faces again | Vertices stored: 10,021 to 19,248 on the P2.0 crate, 9,584 to 22,024 on the P1.0 creature. The generator's shading is gone |

Times: each rule takes 1 to 2.5 seconds on a dense model and a hundredth of a second on a low-poly one. A whole repair of a dense model is 40 to 47 seconds and 3.6 to 4.6 GB, of which about 30 seconds is the two counts written into the facts; without them 22 to 28 seconds.

### Two findings worth their own paragraph

**The low-poly crates are a small box full of hidden triangles.** [`scripts/pieces.py`](blender-stages-trial/scripts/pieces.py) lists each piece with its bounding box. The P2.0 crate at 20,000 is one piece of 108 triangles holding 71% of the surface, the box you see, and 27 pieces holding the other 19,850 triangles, every one of them inside that box. The P1.0 crate is a box of 110 triangles holding 88% of the surface and three pieces of 7,437, 8,517 and 3,732 triangles inside it. The new rule finds a hidden piece by sending rays outward from points on it in 26 directions: a piece is hidden when none escapes. It removed every hidden piece of the P2.0 crate. On the P1.0 crate one inner piece stayed, because the box has 18 open edges and a ray gets out through a gap. It removed nothing from the creature, whose pieces are spikes that can be seen. The 108 triangles that remain are closed, one piece, with no defect of any kind.

**Turning faces is not enough; the stored normals have to go with them.** Blender's "recalculate outside" turns the faces and leaves the stored normals pointing the old way (desk, from the manual). Measured: on the P2.0 crate, after turning 55 faces with the stored normals kept, 174 corners of the exported file are still lit from behind; with the stored normals cleared, none are. On the dense crate the figures are 273 and 0. Clearing them has a price: 6.7% of the dense crate's normals and 22.6% of the dense creature's then differ from Tripo's by more than a degree.

### What cannot be repaired by a fixed rule

- **The creature's low-poly models are loose shells on purpose.** 157 and 236 pieces, each spike an open cone stuck into the body. Every rule that "repairs" them either does nothing (weld, dissolve, loose bits), spends triangles on lids inside the body (fill holes), or removes the spikes (small pieces). **Repair should not be attempted on them** beyond turning faces outward. A check that counts open edges or pieces will fail them however they are repaired, as the Tripo note foresaw.
- **Non-manifold edges.** No rule here removes one, apart from the single one on the dense crate that the 0.01 mm weld happened to close. Blender has no general repair for them (desk, confirmed).
- **A box with gaps hides nothing reliably.** The hidden-piece rule depends on the outer shell being closed.
- **What a small piece is.** By triangle count the crate's whole visible surface is "small". By surface the creature's spikes are. No one number separates junk from intent on both subjects.

### The settings a person or Claude would choose

| Setting | Range that worked | Trade-off |
|---|---|---|
| Weld distance | 0.001 mm to 0.1 mm did no harm; 0.01 mm closed the dense crate | 1 mm already damaged a low-poly model. It is a length, so it means something only at a known size |
| Dissolve distance | 0.01 mm on dense, up to 0.1 mm on low-poly | 0.1 mm on the dense crate removed 100 times the faces and fixed less |
| Delete hidden pieces | on | Safe on all six models. Depends on a closed outer shell |
| Turn faces outward, clear stored normals | on, together | Fixes lighting from behind; loses the generator's shading; more vertices |
| Sharp edge angle after clearing | 30° for the crate | On the creature 30° makes 22,024 vertices of 9,584 |
| Fill holes | **off** | Closes gaps on a prop; adds useless triangles and smeared texture on a subject built of open shells |
| Delete small pieces | **off** | No setting was safe on both subjects |

## 5. Reducing

56 runs on the two dense models; [`reduce.csv`](blender-stages-trial/reduce.csv). All but the last column of every table is counted by the scripts.

### Collapse, the main result

The Decimate modifier in Collapse mode, one pass, ratio = 20,000 ÷ triangles now.

| | Crate | Creature |
|---|---|---|
| Triangles reached | 20,000 exactly | 20,000 exactly |
| Seconds: whole run, the Collapse itself | 26 to 37, 20 to 23 | 27 to 38, 23 to 32 |
| Peak memory | 2.3 to 2.4 GB | 2.5 to 2.7 GB |
| Runs, crashes | 5, none | 5, none |
| Same bytes each time | yes, 5 of 5 | yes, 5 of 5 |
| Open edges, non-manifold edges, pieces | 0, 0, 1 | 0, 0, 1 |
| Zero-area faces, stray edges | 4, 1 | 0, 0 |
| Share of triangles holding 99% of the surface | 84% | 91% |
| Slivers | 2.6% | 0.01% |
| Distance to the dense surface, 95% of points within | 0.04 mm | 1.1 mm |
| Largest distance | 0.19 mm | 3.4 mm |
| From the dense surface back, largest | 0.14 mm | 2.7 mm |

- **It finishes, fast, in a fifth of the machine's memory.** The desk note guessed "seconds" from an older, smaller model; at 1.9 million triangles it is half a minute.
- **The crash of the local generator trial did not come back.** That trial saw Blender 5.2.2 die in Decimate in 3 of 13 runs on a mesh of 10.6 million triangles. Here Collapse ran 68 times on meshes of 1.8 and 1.95 million (47 in this section, 21 inside whole chains) without one. That is an observation at a fifth of the size, not a clearance.
- **It lands on the target.** The count asked for was reached to the triangle in every run but four (a weld or an Un-Subdivide first), which gave 19,999. It never went over.
- **The triangles go where the shape is.** The crate after Collapse is nothing like the P2.0 crate's 73% slivers. The creature keeps its spikes: seen from the dense model, no point of it is more than 2.7 mm from the reduced one.
- **To 5,000:** also exact, also the same bytes twice. The crate barely notices (largest distance 0.4 mm). The creature loses spike tips: up to 17 mm of the dense model is no longer there, and its picture difference doubles.

### The variations

| Variation | Crate | Creature |
|---|---|---|
| **Staged**, 3 or 6 passes in place of 1 | No faster, no nearer the shape, and slivers rise: 2.6% to 7.1% to 12.7% | No gain; slivers stay under 0.1% |
| **Vertices not joined on import** | Torn: 16,172 open edges, 8 pieces | Torn: 17,504 open edges, 943 pieces |
| **Weld at 0.1 mm first** | 316 vertices joined, 19,999 triangles, and 2 open edges and 1 non-manifold edge come back | 9 joined, 1 non-manifold edge, 2 inside-out joins |
| **Un-Subdivide** twice, then Collapse | Un-Subdivide removed under 0.1% of the triangles; the result is Collapse's | The same |
| **Planar** at 5°, not across UV seams, then Collapse | **859 s.** 12 open edges, 7 non-manifold, slivers 24%, picture difference six times Collapse's | 55 s. 68 open edges, 34 non-manifold |
| Planar at 1° | 398 s, same defects | not run |
| Planar at 5° with no limit | **Stopped by hand after 30 minutes** | not run |
| **Voxel remesh** at 4 mm, then Collapse | 20 s. Closed, 1 piece, no defect, slivers 0.5%. Up to 2.8 mm from the dense surface: corners rounded. Same bytes twice | 16 s. Closed but **6 pieces**; up to 10 mm lost |
| Voxel remesh at 2 mm | 72 s, 3.4 GB; up to 1.3 mm | 35 s; 10 pieces |
| **QuadriFlow** on the dense model | **Cancelled at once**: "The mesh needs to be manifold and have face normals that point in a consistent direction". The operator returns `CANCELLED` and raises nothing | The same |
| QuadriFlow on the repaired, the reduced or the voxel-remeshed model | Cancelled, all three | Ran in 8 s on the reduced and the remeshed model: 7,600 quads. Spikes gone: up to 125 mm of the dense model lost. **Not the same bytes twice** |

- **Collapse in one pass is the method.** Nothing else was as close to the shape, and the two that sound cleverer (Planar for a flat-sided crate, QuadriFlow for clean quads) were slower, worse or refused to run.
- **Planar is a trap on a dense model.** It took a quarter of an hour, left faces of up to 534 sides, and after triangulating them the crate still had 84,632 triangles, so Collapse had to finish the job on a worse mesh.
- **A voxel remesh keeps something it calls UVs.** The manual says "All data layers will be lost" (desk). Measured: the remeshed model still has a UV map, in one island with no seams, which is the old UVs smeared across every cut. The textures are unusable on it (picture difference eight times Collapse's on the crate). A remesh always needs new UVs and a bake.

### Protecting UV seams

Collapse has no seam option (desk, confirmed: the modifier has none). Its one handle is a vertex group that makes chosen vertices dearer to remove. `reduce.py` marks every vertex on a UV seam (25,360 on the crate, 56,829 on the creature) and tries that at five strengths from 0.01 to 100.

| | Crate, plain | Crate, seams protected | Creature, plain | Creature, seams protected |
|---|---|---|---|---|
| UV islands (dense: 190 and 1,067) | 250 | 191 to 195 | 1,395 | 1,094 to 1,101 |
| UV square in use (dense: 63% and 50%) | 56% | 61% | 39% | 47% |
| Slivers | 2.6% | 15% | 0.01% | 0.1% |
| Largest distance to the dense surface | 0.19 mm | 1.6 mm to 19 mm | 3.4 mm | 8.5 mm |
| Picture difference, closest view | 0.34 | 0.79 to 1.0 | 1.0 | 1.2 |

- **It works as a seam keeper and costs the shape.** Islands and coverage stay near the dense model's. But there are more seam vertices than the 10,000 the reduced mesh can have, so the budget goes to them and the rest of the surface is starved. Every strength gave the same result: it is a switch, not a dial.
- **The first pass overshoots.** With the group set, a ratio for 20,000 did not reach 20,000; the script had to run Collapse again.
- **Not worth it,** given what the next two subsections show.

### What Collapse does to the UVs, the textures and the normals

Collapse carries the UVs along and bends them. Islands split (190 to 250; 1,067 to 1,395), their edges are eaten (coverage 63% to 56%; 50% to 39%), and texel density, even to within a fifth across the dense crate, now runs from 870 to 1,730 pixels a metre.

Looked at, with Tripo's own three 4096 maps left on the reduced mesh:

- **With the stored normals kept, the crate is wrong at the closest view:** light and dark spikes along every edge of the frame, like torn paper. Collapse keeps the stored normals as data and they no longer fit the surface. The desk note called this undocumented; this is what happens.
- **With the stored normals cleared** (smooth, sharp over 30°) the spikes are gone and the crate is close to the dense one, with faint smudges along some edges where the old normal map meets new geometry. The picture difference is 0.28 at the closest view, the same as a bake.
- **The creature with normals cleared** keeps its colours and spikes but its nose turns into flat facets: the nose's roundness was in the geometry that Collapse removed, and the old normal map does not hold it.

So **the original UVs and textures are usable on a flat-sided prop and not on a shape with rounded detail**, and never with the stored normals left in place.

### The settings a person or Claude would choose

| Setting | Range that worked | Trade-off |
|---|---|---|
| Target triangles | the profile's budget; 5,000 also ran | The crate looks the same at 5,000 and, by section 4, at 108. The creature loses spike tips at 5,000 |
| Method | Collapse, one pass | Nothing else was better on either subject |
| Weld on reading | 0.001 mm | Needed for any file Blender wrote (section 8). 0.1 mm brought defects back |
| Normals afterwards | cleared | Kept normals are wrong |

## 6. UVs and texturing

169 runs: 75 of UVs alone, 94 with a bake; [`bake.csv`](blender-stages-trial/bake.csv).

### Does the bake run headless?

**Yes, first time, on the GPU.** Factory settings leave Cycles on the CPU with no graphics device chosen. `uv_bake.py` sets the Cycles add-on's device type to OptiX, switches the card on and sets the scene to GPU; the bake returned `FINISHED` with no display. The CPU works as well and, at one sample, is no slower:

| Three maps at | GPU (OptiX) | CPU, 16 threads | CPU, 1 thread |
|---|---|---|---|
| 1024 | 7.6 to 9.4 s | not run | 27 s |
| 2048 | 10.5 to 12.6 s | 10.0 to 11.9 s | 35 to 41 s |
| 4096 | 23 to 37 s | 23.6 to 27.4 s | not run |

- **Samples are the trap the desk note said they were.** Factory settings give 4,096 samples with denoising on. At that setting the same 2048 bake took **174 seconds on the GPU**, 17 times as long, and on the CPU had not finished the first of three maps after 400 seconds, when I stopped it. At 16 samples nothing changed that the picture difference could see. The scripts use 1.
- **Memory:** 3.1 to 3.5 GB at 1024, 3.6 to 4.1 GB at 2048, 6.0 to 6.5 GB at 4096. Most of it is the dense model, which the bake loads whole.

### How the three maps are made

- **Normal map:** Cycles' Normal bake, tangent space, with the dense model's own material in place. The result holds both the shape the reduction removed and the detail of Tripo's normal map.
- **Base colour:** the dense model's material is rewired so that its base colour texture is given off as light, and an Emit bake copies it. Blender's Diffuse bake with only its Color pass was also tried: its picture difference was three times as large on the crate (0.82 against 0.26 at the closest view), because that pass leaves out whatever the material calls metal.
- **Metallic and roughness:** Blender has no bake for metallic (desk, confirmed). Tripo stores the two in one image, as glTF wants. The same Emit bake copies that image whole, so one bake gives both.

### Does the `.glb` carry all three maps?

**Yes.** The reduced model's new material has the base colour image on Base Color, the packed image through a Separate Color node with green to Roughness and blue to Metallic, and the normal image through a Normal Map node. `kiln.measure` reads the exported file as one material with `baseColorTexture`, `metallicRoughnessTexture` (one image) and `normalTexture`. The validator finds no error. The exporter prints one warning, "More than one shader node tex image used for a texture", which is its remark on the shared image; the dense originals draw the same warning on a plain round trip.

**One thing had to be worked round.** A baked image lives in memory, and the exporter writes any such image as PNG whatever format it is marked with: the first bakes came out with three PNGs. The exporter copies an image's own bytes only when it comes from a file. So the script saves each baked image beside the output (base colour and metallic-roughness as JPEG at quality 90, the normal map as PNG), loads it back and packs it. The exported images are then the saved files, byte for byte.

### UVs: Smart UV Project is right for the crate and wrong for the creature

On the reduced meshes of 20,000 triangles (dense originals: 190 islands and 63% of the UV square for the crate, 1,067 and 50% for the creature):

| UVs | Crate: islands, square in use | Creature: islands, square in use |
|---|---|---|
| Tripo's, as Collapse left them | 250, 56% | 1,395, 39% |
| The same islands laid out again | 250, 67% | 1,395, 56% |
| Smart UV Project, 20° | 519, 55% | 11,845, 1.4% |
| 30° | 293, 55% | 9,672, 2.3% |
| 45° | 84, 56% | 7,366, 4.1% |
| 66° (Blender's default) | 74, 56% | **4,174, 12%** |
| 89° | 74, 56% | 3,694, 15% |
| 66°, island margin 0 | 74, 57% | 4,174, 46% |
| 66°, margin 0.001 added | 74, 57% | 4,174, 44% |
| 66°, margin 0.001 added, packed again | 74, 56% | 4,174, 54% |
| Seams at edges over 60°, then Unwrap | 19, 50% | 1,232, 3% with overlaps |

- **The crate is easy.** Any angle from 45° up gives 74 islands, as few as Tripo's own H3.1 at 20,000 (73) and a third of Tripo's Smart UV on the P2.0 crate (220).
- **The creature is not.** Smart UV Project cuts wherever neighbouring faces turn away from each other, and a spike is nothing but that. At the default it makes 4,174 islands, level with Tripo's texture step (4,208) which this stage was meant to beat. Blender's default margin between that many islands then leaves 12% of the texture in use.
- **Unwrapping from sharp edges** is worse on both: 19 islands on the crate with texel density from 54 to 1,581 pixels a metre, and overlapping islands on the creature.
- **Laying the old islands out again is the best found for the creature.** "Keep" means: leave Tripo's islands as Collapse left them, scale each to its share of the surface (Average Islands Scale), and pack them (Pack Islands, a margin of a thousandth of the square on each side). 1,395 islands and 56% of the square: fewer islands than Smart UV Project and more of the texture used than the dense original. The textures are then baked again into the new layout.
- **Margin method matters more than margin.** Blender's default way of reading the margin ("scaled") grows with the number of islands. The plain way ("add": this much on every side) gave 44% where the default gave 12%.

Unwrapping takes a tenth of a second to two seconds either way.

### Bake settings

At 2048 on the reduced meshes, changing one setting at a time. "Rays missing" and "wrong hits" are from the ray check; a wrong hit is a ray that lands further away than twice the distance within which 99% of the surface finds the dense one.

| Setting | Crate | Creature |
|---|---|---|
| Cage 0, no limit | 42% wrong hits. Picture difference 5.2 against 0.26: ruined | 66% wrong hits; 3.0 against 0.58 |
| Cage 1 mm, ray 2 mm | 0.2% missing; same picture as 20 mm | **8.6% missing** |
| Cage 5 mm, ray 10 mm | the same | 1.0% missing, 1.7% wrong: the best picture (0.54) |
| Cage 20 mm, ray 40 mm | the same | 0.2% missing, **11% wrong**: a ray from one spike lands on the next |
| Cage 50 mm, ray 100 mm | the same | 18% wrong; picture worse (0.67) |
| **Cage worked out** from the meshes | 1.0 mm | 5.7 mm; 0.9% missing, 2.3% wrong |
| Margin 0 | Lines at seams: picture difference 0.37 against 0.26 | 0.81 against 0.58 |
| Margin 2, 8, 32 pixels | No difference beyond 2 | No difference beyond 2 |
| Margin type "extend" in place of "adjacent faces" | Changes the two colour maps slightly, not the picture | The same |
| 16 samples | No difference | No difference |
| Sharp edges over 30° on the reduced mesh | No difference in the picture; 296 more vertices | Slightly worse; 7,519 more vertices |
| Low mesh not welded first | **4,206 islands, 7% of the square in use**; dark slashes all over the frame | No effect (all smooth, so the importer had joined it) |
| PNG for all three maps | File 5.9 MB against 3.0; picture difference 0.17 against 0.26 | 12.5 MB against 8.6 |

- **The cage is the per-asset setting, and it can be worked out.** The crate does not care. The creature needs the ray to start outside the surface but not reach the next spike: 5 mm, where 1 mm misses and 20 mm strays. `cage=auto` measures how far the reduced surface is from the dense one (99% within 0.07 mm and 1.4 mm) and takes four times that, never under a millimetre. That picked 1.0 mm and 5.7 mm, both in the range that worked.
- **Weld before unwrapping.** The reduced crate, read back from its `.glb`, arrives in 10,610 more vertices than it has points. Smart UV Project then treats each sheet as its own piece.

### Texture size: 1024, 2048, 4096

Reduced mesh of 20,000 triangles, old islands laid out again, cage worked out. "Reduced only" is the reduced mesh with Tripo's own 4096 maps and UVs, normals cleared: the no-bake route.

| Crate | 1024 | 2048 | 4096 | Reduced only, 4096 |
|---|---|---|---|---|
| File | 2.1 MB | 4.8 MB | 12.7 MB | 6.2 MB |
| Texel density at 0.8 m | 388 px/m | 804 | 1,608 | 1,471 |
| Bake seconds | 9.4 | 11.7 | 37.4 | none |
| Picture difference: three-quarter, closest | 0.20, 0.47 | 0.12, 0.28 | 0.10, 0.23 | 0.13, 0.28 |

| Creature | 1024 | 2048 | 4096 | Reduced only, 4096 |
|---|---|---|---|---|
| File | 3.3 MB | 8.4 MB | 22.8 MB | 10.5 MB |
| Texel density at 0.8 m | 525 px/m | 1,173 | 2,346 | 1,962 |
| Bake seconds | 8.2 | 12.6 | 25.1 | none |
| Picture difference: three-quarter, closest | 0.32, 0.57 | 0.26, 0.43 | 0.25, 0.40 | 0.47, 0.84 |

In video memory, by the arithmetic of [`pit-budget-measurement.md`](pit-budget-measurement.md) section 6: three maps with mipmaps take 16 MiB at 1024, 64 MiB at 2048 and 256 MiB at 4096 uncompressed, a quarter of each block compressed.

- **2048 is where the gain stops paying.** From 1024 to 2048 the picture difference falls by a fifth to two fifths; from 2048 to 4096 by a sixth at most, for four times the memory and nearly three times the file.
- **The file is mostly the normal map.** It stays PNG (3.2 MB and 5.7 MB at 2048). The two JPEGs together are 1.1 and 1.9 MB.
- **The baked 4096 file is twice the size of Tripo's 4096 file.** Tripo's normal map is a 3 to 5 MB PNG; the baked one is 9 to 15 MB, because a bake into many small islands with margins compresses worse.
- **Looked at:** the crate at 1024 and at 2048 from the closest view. Both match the dense crate; 1024 is a little softer at the inner edge of the frame. I did not open the 4096 pictures; the figures for them are the picture difference alone.
- **For the crate the bake buys nothing a picture shows.** Reduced only, at Tripo's own 4096, has the same picture difference as a bake at 2048. For the creature the bake halves it.

### Baking onto Tripo's own low-poly meshes

P1.0 and P2.0 are other generations than H3.1: other shapes. The dense model is first stretched onto the low mesh's bounding box, then baked as before at 2048. 24 runs.

| Low mesh | After repair | 99% of its surface is within this of the H3.1 surface | Rays missing at a 30 mm cage | Looked at |
|---|---|---|---|---|
| Crate, P2.0 | **108 triangles**, 36 islands | 15 mm | 1% | Clean and sharp. Hard to tell from the 20,000-triangle chain result at three-quarter |
| Crate, P1.0 | 8,630 triangles (one hidden piece left) | 55 mm | 5% | Clean; the panels of the two crates are set back by different amounts, so the inner frame is a little off |
| Creature, P1.0 | 18,538 triangles, 157 pieces | 134 mm | 73% | **Wrong.** Brown and red patches on the feet, the face slipped to one side, dark streaks along the spikes |
| Creature, P2.0 | 21,044 triangles, 236 pieces | 133 mm | 64% | Wrong in the same way |

- **Is baking across two different shapes meaningful? For the crate, yes; for the creature, no.** Two crates stretched to the same box agree to within a centimetre or two. Two creatures do not: their surfaces are 13 cm apart in places, on a model 1 m long. A wider cage finds a surface for more rays (down to 10% missing at half a metre) and finds the wrong one.
- **Against Tripo's `_textured` files.** Tripo's P2.0 crate texture, looked at, is blurred with light and dark gradients painted in. The 108-triangle box with H3.1's maps is sharper, has three maps where Tripo's has one, 36 islands where Tripo's has 3,105, and is 2.6 MB. Tripo's creature textures are flat-coloured and in the right places; the cross-shape bakes are not. **Tripo's texture step wins on the creature's low-poly models, and nothing here replaces it.**

### The settings a person or Claude would choose

| Setting | Range that worked | Trade-off |
|---|---|---|
| UVs | old islands laid out again, for both; Smart UV Project at 45° to 89° for the crate only | Smart UV gives the crate a third of the islands and a file two thirds the size. It gives the creature three times the islands |
| Island margin | 0.001 of the square, read as "add" | Under two pixels at 1024. Blender's default reading wastes the texture on a many-island model |
| Texture size | 1024 to 4096 all ran | Section above. The profile has no texture budget yet |
| Cage and ray | worked out; 1 mm to 50 mm for the crate, about 5 mm for the creature | Too small misses, too large strays, on any shape with parts near each other |
| Bake margin | 2 to 32 pixels | 0 shows lines |
| Samples | 1 | 4,096 is 17 times slower for no gain |
| Device | GPU or CPU | Same speed at one sample. One CPU thread for the same bytes every time (section 9) |
| Image formats | JPEG at 90 for colour and metallic-roughness, PNG for normal | PNG for all three doubles the file and is closer to the dense model |

## 7. Scaling and placement

Kiln's own stage function, `kiln.run.scale_to_size(source, work, record, profile)`, with size 0.8 m and a work folder under `work/`. Then `place.py`. 10 runs, besides the 21 inside whole chains.

| Model | Seconds, memory | Largest dimension after | Lowest point | Vertices stored | Textures |
|---|---|---|---|---|---|
| Crate, dense | 7.0 s, 1.9 GB | 0.8000 m | 0.0000 | 926,464 to 951,648 | same bytes |
| Creature, dense | 7.7 s, 2.0 GB | 0.8000 m | 0.0000 | unchanged | same bytes |
| Crate, reduced | 1.2 s, 0.7 GB | 0.8000 m | −0.00001 m | 23,208 to 23,212 | same bytes |
| Creature, reduced | 1.3 s, 0.7 GB | 0.8000 m | **+0.00025 m** | unchanged | same bytes |
| Creature, reduced, scaled a second time | 1.2 s | 0.8000 m; factor 0.99999996 | the same | unchanged | same bytes |

- **The size is right** to the seventh decimal, on a dense model as on a reduced one, and scaling an already scaled model changes nothing.
- **Normals and textures survive.** The count of corners lit from behind is the same before and after; no normal is off unit length; every image is copied byte for byte.
- **It does not put the model on the ground or centre it,** and does not claim to. Tripo's raw files already stand on y = 0 and are centred, so a raw file stays so. A reduced one does not: Collapse had removed the creature's lowest point, leaving it a quarter of a millimetre in the air and a tenth of a millimetre off centre.
- **`place.py` does both.** After it the creature's box is from −0.30739 to +0.30739 across, 0 to 0.8 up, and −0.39953 to +0.39953 along. One second.
- **Turning to Bevy's forward.** glTF's forward is +Z, where Tripo's models face; Bevy's is −Z. `scripts/facing.py` reads the mean z of the top 15% of the creature, which is its raised tail:

| | Tail end at |
|---|---|
| Raw H3.1 | z = −0.302 (face at +Z) |
| Reduced and scaled | −0.247 |
| Turned 180° about the up axis | **+0.246** (face at −Z) |
| Turned 90° | z = −0.070, x = −0.246: sideways |

  One call of `Mesh.transform` with a half-turn about Blender's Z (glTF's Y) does it. The stored normals turn with the mesh: after the turn the largest angle between a stored normal and the same normal turned by hand was 0.06° to 0.78°. The desk note had left that as untested.
- **Every round trip grows a hard-edged model.** The baked crate went from 12,388 vertices stored to 12,670 through `scale_to_size` and to 12,705 through `place.py`, with the same triangles. Small, and it compounds.

### The settings a person or Claude would choose

| Setting | Values | Trade-off |
|---|---|---|
| Size | metres; exists today | |
| Turn about the up axis | 180° for every Tripo model seen so far | A person has to look once to know which way a generator faces its models. A crate cannot show it |
| Origin | bottom centre | Right for a prop that stands on a floor |

## 8. The whole chain, and the comparison

### The chain

[`scripts/chain.sh`](blender-stages-trial/scripts/chain.sh), from the raw H3.1 file:

1. **Repair:** weld and dissolve at 0.01 mm, delete loose bits and hidden pieces, turn faces outward.
2. **Reduce:** weld at 0.001 mm, then Collapse in one pass to 20,000.
3. **UVs and bake:** weld; the reduced mesh's own islands laid out again; stored normals cleared, all smooth; cage worked out; three maps at 2048, one sample, margin 8 pixels.
4. **Scale:** kiln's `scale_to_size`, 0.8 m.
5. **Place:** half-turn, origin to the bottom centre.

| Stage | Crate | Creature |
|---|---|---|
| 1 Repair | 22 to 28 s | 24 to 27 s |
| 2 Reduce | 25 s | 29 to 31 s |
| 3 UVs and bake, GPU | 21 s | 21 to 22 s |
| 3 UVs and bake, one CPU thread | 47 to 48 s | 52 to 53 s |
| 4 Scale | 0.8 s | 0.9 s |
| 5 Place | 0.8 s | 0.9 s |
| **Whole chain, GPU bake** | **69 s** | **77 to 82 s** |
| **Whole chain, one-thread bake** | **96 to 103 s** | **107 to 110 s** |
| Peak memory | 3.8 GB | 4.1 GB |

Nearly half the time is reading and writing the dense file three times: once in repair, once in reduce, once as the source of the bake.

### The first chain was wrong, and why

The first version had no weld in stage 2. Its creature was sound. **Its crate came out in 94 pieces with 10,194 open edges and 752 UV islands,** and still passed both of kiln's checks.

The cause is in section 3's small print. Stage 1 exports the repaired crate. Blender's exporter stores a point twice wherever two faces meet at a hard edge, because each needs its own normal. Stage 2's importer joins doubled points only where their normals agree, so the crate arrives as flat sheets that touch but are not joined, and Collapse pulls them apart. Reducing straight from Tripo's file never showed this: Tripo stores one point with one normal. The creature escaped because it has no hard edge.

With `weld=0.000001` in stage 2 (10,824 vertices joined) the crate reduces to one piece. Everything below is from the corrected chain. The first chain's records are kept as `runs/chainv1_*`.

### The comparison

Every row measured with `scripts/measure_model.sh` at 0.8 m; [`comparison.csv`](blender-stages-trial/comparison.csv) has more rows and columns. "Slivers" is the share of triangles under a hundredth of the mean. "Islands" are UV islands. Time is the chain's; for Tripo's rows it is not known here.

**Crate**

| | Triangles | File | Maps | Islands | Open | Non-manifold | Pieces | Validator errors | Slivers | In budget and valid |
|---|---|---|---|---|---|---|---|---|---|---|
| **The chain** (`stages_crate_chain`) | 19,999 | 4.8 MB | three, 2048 | 251 | 2 | 1 | 1 | 0 | 2.6% | yes; 69 to 103 s |
| The chain with Smart UV Project | 19,999 | 3.0 MB | three, 2048 | 70 | 2 | 1 | 1 | 0 | 2.6% | yes |
| Reduced only, Tripo's maps kept | 20,000 | 6.2 MB | three, 4096 | 250 | 0 | 0 | 1 | 0 | 2.6% | yes; 26 s |
| P2.0 box with H3.1's maps baked on | 108 | 2.6 MB | three, 2048 | 36 | 0 | 0 | 1 | 0 | 0% | yes |
| Tripo: H3.1 asked for 20,000 | 17,080 | 6.2 MB | three, 4096 | 73 | 8 | 4 | 1 | 0 | 4.4% | yes |
| Tripo: P1.0 | 19,796 | 0.5 MB | none | none | 18 | 1 | 4 | 0 | 3.6% | yes, untextured |
| Tripo: P2.0 + texture step | 19,958 | 3.0 MB | base colour only, 4096 | 3,105 | 97 | 87 | 28 | 2 | 72.7% | **no** |
| Tripo: P2.0 + Smart UV | 19,958 | 0.6 MB | none | 220 | 97 | 87 | 28 | 1 | 72.7% | **no** |
| Tripo: H3.1 default | 1,801,451 | 56.8 MB | three, 4096 | 190 | 2 | 1 | 1 | 0 | 0.1% | **no** |

**Creature**

| | Triangles | File | Maps | Islands | Open | Non-manifold | Pieces | Validator errors | Slivers | In budget and valid |
|---|---|---|---|---|---|---|---|---|---|---|
| **The chain** (`stages_orb_chain`) | 20,000 | 8.4 MB | three, 2048 | 1,401 | 0 | 1 | 1 | 0 | 0% | yes; 77 to 110 s |
| Reduced only, Tripo's maps kept | 20,000 | 10.5 MB | three, 4096 | 1,395 | 0 | 0 | 1 | 0 | 0% | yes; 28 s |
| Reduced to 5,000 and baked | 5,000 | 8.1 MB | three, 2048 | 1,170 | 0 | 0 | 1 | 0 | 0.2% | yes |
| Tripo: H3.1 asked for 20,000 | 19,007 | 9.9 MB | three, 4096 | 718 | 2 | 2 | 1 | 0 | 0% | yes |
| Tripo: P1.0 + texture step | 18,438 | 4.3 MB | base colour only, 4096 | 4,893 | 157 | 20 | 157 | 2 | 0% | **no** |
| Tripo: P2.0 + texture step | 20,389 | 4.4 MB | base colour only, 4096 | 4,208 | 1,169 | 12 | 236 | 2 | 0% | **no** |
| Tripo: H3.1 default | 1,951,822 | 65.8 MB | three, 4096 | 1,067 | 0 | 1 | 1 | 0 | 0% | **no** |

A third Tripo file, `orb_spiked_h31_req20000` (19,188 triangles, 2,299 islands, 19 open edges), appeared in `models/` during the trial. I do not know what setting made it; it is in the CSV and not discussed.

Both chain results pass kiln's two checks against `profiles/pit.toml`: no validator error, and 19,999 and 20,000 triangles against a budget of 20,000.

### Looked at, side by side

Three-quarter, front and closest view of each. The chain's pictures are of its stage 4 output, before the half-turn, so that every model faces the camera the same way.

**Crate**

- **The chain:** straight edges, flat faces, the panel's shading as on the dense crate. Faults: three or four small light flecks along one upright edge of the frame in the three-quarter view, and one light speck beside the panel in the closest and front views. They sit where the reduced mesh keeps its 2 open edges.
- **Tripo's H3.1 at 20,000:** the frame's edges are ragged in every view, as if chewed, with dark smudges along them. The flat faces and colours are right. From the front the top and bottom of the frame are visibly wavy.
- **Tripo's P2.0 with its texture step:** blurred, with light and dark bands painted across the frame and a pale diagonal across each panel. No surface detail.
- **The 108-triangle box with H3.1's maps:** as clean as the chain's at three-quarter, and without the flecks.
- **Which looks better:** the chain's and the 108-triangle box, clearly, over both of Tripo's.

**Creature**

- **The chain:** the dense H3.1 creature with nothing I can see missing: the spikes on the back and sides, the dark line round each tuft, the nose with its pits. The spikes are thin and dark-edged, as they are on the dense model.
- **Tripo's H3.1 at 20,000:** a different generation of the same creature. Rounder and softer, fewer and thicker spikes on the back, a smoother nose, the tail more upright. Nothing in it is broken.
- **Tripo's P2.0 with its texture step:** a third shape, lower and wider. Flat colour, no surface detail, and a ring of small hooked pieces standing off the face below the nose.
- **Which looks better:** the chain's and Tripo's H3.1 at 20,000 are both sound and differ as two drawings of one animal differ; the chain's has more of the spikes. Both are well ahead of P2.0 with its texture step.

## 9. Repeatability

Kiln's rebuild promises the same finished model, byte for byte, from the same raw output.

| Stage | Same bytes from the same input and settings? | Runs |
|---|---|---|
| Round trip | Yes | 2 of 2 on each dense model |
| Repair | Yes | 12 of 12 on the crate, 9 of 9 on the creature, inside chains |
| Collapse, to 20,000 and to 5,000 | Yes | 5 of 5 and 2 of 2, each subject |
| Voxel remesh then Collapse | Yes | 2 of 2, each subject |
| QuadriFlow | **No** | 2 runs on one input, 2 files |
| UVs (Smart UV Project, Pack Islands) | Yes: the two colour maps depend on the UVs and were the same bytes in every repeat | |
| Bake, base colour and metallic-roughness | Yes, on one device | every repeat |
| **Bake, normal map, GPU** | **Not always**: 6 of 8 the same on the crate at 2048; 3 different files in 3 on the creature | |
| **Bake, normal map, CPU with 16 threads** | **Not always**: 3 of 5 the same on the crate; 3 different in 3 on the creature | |
| Bake, normal map, CPU with one thread | Yes | 17 of 17: 9 on the crate, 8 on the creature, each set against the others of its own input and settings |
| `scale_to_size`, `place.py` | Yes | every repeat |
| **Whole chain, bake on one CPU thread** | **Yes** | 2 of 2 on each subject |
| Whole chain, GPU bake | Crate yes, 2 of 2 (and 3 of 3 in the first chain); creature no, 2 different in 2 (and 3 in 3) | |

- **How different is "different"?** Between two normal maps of 4,194,304 pixels: 1 pixel on the crate, 2 to 5 on the creature, each by one step of 255. Nothing an eye or the picture difference can see. A checksum sees it.
- **Where it comes from.** Not from Cycles' own threads: setting Blender's render threads to one for the normal bake alone still gave 3 different files in 5. Only starting Blender itself with one thread (`KILN_BLENDER_THREADS=1`) made it stop. So it is in something Blender does around the bake with its own thread pool. I did not find what.
- **GPU and CPU do not agree with each other** either: 1,695 pixels of the normal map differ by up to 2 steps, and the JPEGs by up to 9.
- **17 of 17 is an observation.** Nothing documents that one thread gives the same bytes.

## 10. Where the desk research was right and wrong

Against [`tripo-guidance-and-blender-scripting.md`](tripo-guidance-and-blender-scripting.md), Part 2. Nothing in that note was edited.

### Right

| It said | Measured |
|---|---|
| An operator may cancel without raising; check the return value | QuadriFlow returned `{'CANCELLED'}` with only a printed warning, 5 times |
| Import without joining vertices breaks decimation | 16,172 and 17,504 open edges after Collapse |
| `merge_vertices` cannot join vertices whose normals differ; such a model "needs `bmesh.ops.remove_doubles` after import" | This is what broke the first chain (section 8), and the weld is what fixed it |
| The importer repairs silently | Zero-length normals replaced with no message; Tripo's three invalid files become valid |
| Unchanged textures are copied, not re-encoded | Same SHA-256 through round trip, repair, reduce, scale and place |
| Flip and Recalculate do not update stored normals | 174 corners still lit from behind after turning 55 faces; 0 once the stored normals are cleared |
| Collapse has no seam protection | The modifier has none; the vertex-group route works crudely (section 5) |
| Un-Subdivide is for grid-like meshes | Removed under 0.1% of the triangles |
| Factory settings bake at 4,096 samples on the CPU, with denoising | Read from the binary again: 4,096, CPU, denoising on, device type none. 17 times slower on the GPU; unfinished on the CPU |
| No metallic bake type; glTF wants metallic and roughness in one image | One Emit bake of Tripo's packed image gives both |
| A bake target left as sRGB stores numbers wrongly | The two data maps are made Non-Color; the exported maps draw correctly |
| The 3D Print Toolbox is not bundled | `bpy.ops.mesh` has no `print3d` operator. Nothing in this trial needed it: every count it gives was taken with `bmesh` |
| Smart UV Project, Pack Islands and the bake run with no editor area | All did, every time |
| "Deleting floaters deletes intent" | The creature's spikes; and the crate's whole visible box, when floaters are judged by triangle count |
| A filled hole has no texture of its own | Its UVs span the texture: coverage 40% to 91% |
| Sharp edges cost vertices | 9,584 to 22,024 on the creature at 30° |
| glTF +Z is Blender −Y; a model facing glTF's forward faces backwards in Bevy | Confirmed by `facing.py` before and after a half-turn |

### Wrong, or not as feared

| It said | Measured |
|---|---|
| **`Image.scale()` may not mark an image changed, so an export may write the full-size original** | Not in 5.2.2 with a packed image from a `.glb`. `is_dirty` became True and the exported image was 1024 pixels. It was re-encoded at the exporter's default JPEG quality of 75. Packing the image again before export, which looks like the careful thing, turned it into a 1.1 MB PNG |
| A dense H-series output "decimates in seconds" | Half a minute at 1.9 million triangles. Still cheap |
| Voxel remesh: "All data layers will be lost" | A UV map survives and is useless: one island, no seams (section 5) |
| What `Mesh.transform` does to stored normals "was not read"; a turned model might be lit wrongly | They turn with the mesh, to within 0.8° |
| What Collapse does to stored normals is undocumented | It keeps them, and they are wrong: jagged shading on the crate until cleared |
| Planar "suits forms comprised of mainly flat surfaces" and "keeps edges crisp" | On a 1.8-million-triangle crate it took 7 to 14 minutes and gave a worse mesh than Collapse in 20 seconds |
| Setting an image's `file_format` decides what the exporter writes | Only for an image that comes from a file. A baked image is written as PNG regardless |
| `material.use_nodes` is deprecated and always True | A new material's node tree was there without setting it; no warning was printed |

### Not in the desk research at all

- A file Blender wrote cannot be read back as the same mesh (section 8). The desk note's two halves of this were both there; that they meet between two stages was not.
- The normal bake is not byte-repeatable with more than one thread.
- Smart UV Project's island count explodes on a spiky shape, and Blender's default margin method then empties the texture.
- Low-poly output can be mostly hidden pieces.

## 11. What this means for kiln's stage list and checks

**Everything in this section is inference** from two subjects.

### A stage list

1. **Take in** the raw output; shape review. As today.
2. **Clean** (always): weld at 0.001 mm; dissolve degenerate faces at 0.01 mm; delete loose vertices and edges; delete hidden pieces; turn faces outward and clear the stored normals. No hole filling. No deleting by size. These five did no harm to any of the six models and fixed what they could.
3. **Reduce** (only when over the profile's triangle budget): Collapse, one pass, to the budget.
4. **UVs and bake** (only when stage 3 ran, and the raw output has UVs and textures): the reduced mesh's own islands laid out again; cage worked out; three maps at the profile's texture size; one sample; one thread.
5. **Resize textures** (only when stage 4 did not run and the textures are over the profile's size): not built here. `Image.scale()` reaches the file; the format it comes out in needs the same save-and-reload as the bake.
6. **Scale to size.** As today.
7. **Place:** origin to the bottom centre, and a turn about the up axis that is a setting of the generator, not of the asset: 180° for Tripo.

- **One Blender session for stages 2 to 4, or a weld at the start of every stage.** Each file passed between stages re-splits the hard edges, grows the vertex count and costs seconds of reading and writing a dense file. One script doing clean, reduce and bake on the mesh in memory would avoid all three and take perhaps 50 seconds in place of 70 to 110. If the stages stay separate files, "weld at 0.001 mm on reading" belongs in the one place that reads a `.glb`, not in each stage's care.
- **The bake's dense source is the raw output,** read from the asset record's folder, not the output of the stage before. A stage's signature `(source, work, record, profile)` already allows that.
- **What a person still sets per asset:** nothing in the fixed chain as run. The cage is worked out, the UV rule was the same for both subjects, the turn belongs to the generator. Smart UV Project for hard-surface props would be the first per-asset switch worth having: a third of the islands and two thirds of the file on the crate.

### Checks

- **The two checks kiln has are not enough to catch a broken chain.** The torn crate of the first chain had 19,999 triangles and no validator error. A check on **pieces and open edges against the raw output's own counts** would have caught it: 1 piece became 94. Counted against the raw output, not against zero, it also does not fail a creature built of 236 shells.
- **Distance from the reduced surface to the raw one,** as a share of the size, is cheap (a few seconds) and says whether the shape was kept: 0.02% of the size on the crate, 0.3% on the creature at 20,000, 1.7% at 5,000.
- **The bake's ray check** before baking: rays missing and wrong hits. Over a few percent means the cage is wrong or the two meshes are not the same shape; over 60%, as on the creature's low-poly models, means stop.
- **Texture count, size and which maps,** once the profile has a texture budget. `kiln.measure` already reads them.
- **UV islands and the share of the UV square in use** as figures in the record, not as pass or fail. 4,174 islands at 12% is a warning that the unwrap went wrong.
- **Same bytes on rebuild** holds only if the bake runs on one thread, on the CPU, on the same Blender. A graphics card must not be allowed to change an asset.

### Does kiln need Tripo's paid steps?

- **Tripo's Smart UV and texture steps on P1.0 and P2.0: no, if H3.1 is the generator.** The chain gives three maps and a quarter of the islands for about a minute and a half of this machine, and nothing here made the low-poly-plus-texture route look worth 20 credits.
- **But the chain is not the only way into the budget.** H3.1 asked for 20,000 triangles comes back in budget with three maps and, on the creature, fewer UV islands than the chain's (718 against 1,401). It would still need its textures brought down from 4096. On the crate its edges were visibly worse than the chain's. One crate is not grounds to say Tripo's own reduction is worse in general; it is grounds to keep the dense file as the raw output, so that either route stays open.
- **The low-poly models are not a shortcut.** On the crate they hide 99% of their triangles; on the creature nothing here could texture them.

## 12. Corrections to other notes

Nothing in the other notes was edited.

| Note | It says | What was found |
|---|---|---|
| `tripo-api-trial.md`, section 9 | "P2.0 spends most of its triangles where they do nothing": 73% slivers | They are not slivers of the visible surface. 19,850 of the 19,958 triangles are in 27 pieces sealed inside a 108-triangle box. Removing them changes nothing that can be seen |
| The same, section 9 | "P1.0 at the same count is more even: 55.7% hold 99% and 3.6% are tiny" | The P1.0 crate is a 110-triangle box holding 88% of the surface with 19,686 triangles in three pieces inside it. Its triangles are even in size and almost all hidden |
| The same, section 9 | "Not every file is valid glTF. Three of the P2.0 files fail the validator" | True of the raw files. A plain round trip through Blender makes all three valid |
| The same, sections 9 and 10 | The low-poly models at 20,000 "pass the pit profile's placeholder `triangle_budget`" | They do. The crate ones could pass a budget of 200 |
| `tripo-guidance-and-blender-scripting.md`, Part 2 | | Section 10 above |
| `local-generator-trial.md`, stage 3 | Blender 5.2.2 crashed in Decimate in 3 of 13 runs at 10.6 million triangles | 0 of 68 at 1.8 and 1.95 million. The same build; a fifth of the size |
| `pit-budget-measurement.md`, section 6 | A 2048 texture on a 1 m asset is "somewhat under one texel per pixel at the closest view" | For what it adds: the chain's 2048 textures give 804 and 1,173 pixels a metre at 0.8 m, against that note's 1,500 for one texel per pixel |

## 13. What is unknown, and the next step

**Unknown**

1. **Whether any of this holds for a third subject.** A crate is flat and a creature is spiky; a rock, a barrel, a chair and a plant are none of those. The UV rule in particular was chosen on two cases.
2. **Why the normal bake differs by a pixel between runs,** and whether one thread is a cure or thirteen lucky runs.
3. **What texture size the pit profile should allow.** Section 6 gives the cost of each; what is visible in the game at 0.5 m is a question for final review.
4. **How the baked normal maps look in Bevy under moving light.** The review pictures have one fixed light. Neither Tripo's files nor the chain's store tangents; both lean on Bevy working them out the way Blender did.
5. **Whether Tripo's own reduction is generally rougher than Collapse,** as it was on one crate.
6. **Whether a hole-free, clean-quad mesh is ever needed.** Nothing here makes one: QuadriFlow refused the crate and destroyed the creature's spikes.
7. **Compressed textures.** Every file here stores PNG and JPEG; the pit profile expects block compression, which is a stage of its own.

**The next step, in order of what it would settle**

1. **Put one more H3.1 raw output of a different kind through `chain.sh` unchanged** (a rock or a barrel). It costs one generation and two minutes, and says whether the fixed chain is fixed.
2. **Fold clean, reduce and bake into one script** and time it against the chain.
3. **Add the pieces-and-open-edges check** to kiln's checks, measured against the raw output.
4. **Run the one-thread bake 50 times overnight** and compare checksums.

## 14. How to run it again

From `learn/research/blender-stages-trial/`, with `.tools/` holding the pinned Blender and validator and `target/release/review_pictures` built:

```
scripts/run_stage.sh <run name> <stage script> <in.glb> [name=value ...]   one stage, timed and measured
scripts/chain.sh crate my_run                  the whole chain on the crate, GPU bake, 2048, 20,000 triangles
CHAIN_ONE_THREAD=1 scripts/chain.sh orb my_run the same on the creature with the bake on one CPU thread
scripts/chain.sh crate my_run 1024 5000 smart  texture size, triangles, and Smart UV Project in place of "keep"
```

The matrices behind each section. Each overwrites its own runs, except the reduction one, which skips runs already recorded. The first two were typed as loops during the trial and gathered into scripts afterwards; those two scripts have not been run from start to end.

| Section | Command | About |
|---|---|---|
| 3 | `scripts/run_roundtrip_matrix.sh` | 3 minutes |
| 4 | `scripts/run_repair_matrix.sh` | 8 minutes |
| 5 | `scripts/run_reduce_matrix.sh crate orb`, then `scripts/summarise_reduce.py > reduce.csv` | 75 minutes, most of it Planar on the crate |
| 6 | `scripts/run_uv_matrix.sh`, `scripts/run_bake_matrix.sh`, `scripts/run_tripo_lowpoly.sh`, then `scripts/diff_pictures.sh` and `scripts/summarise_bake.py > bake.csv` | 40 minutes |
| 7 | `scripts/run_scale.sh <name> <in.glb> 0.8`, then `scripts/run_stage.sh <name> place.py models/<name>.glb turn=180` | seconds |
| 8 | from `../tripo-api-trial/`: `../blender-stages-trial/scripts/measure_results.sh`; then here `python3 -I scripts/comparison.py > comparison.csv` | 15 minutes |

Where things are:

- **`runs/`**: every run's records, in git. `runs.csv` lists all 561 with seconds, memory and exit status.
- **`models/`**: every output model, 554 files and 5.7 GB, **not in git** (`models/.gitignore`). Their checksums are in `SHA256SUMS`. Any of them can be made again from the run's settings in its `.facts.json`.
- **`work/`**: review pictures of each run (`work/pics/<run>/`) and scratch, 1.4 GB, not in git.
- **`../tripo-api-trial/measurements/stages_*`**: the main results measured the Tripo trial's way.
- **The creature.** Its models are in `models/` and its pictures in `work/` and in `measurements/stages_orb_*/review/` and `wire/`. None is committed: two lines added to `tripo-api-trial/.gitignore` cover the last two. That was the only edit outside this trial's own folders.

Three things to know before running:

- **Do not wrap a run in `timeout`.** `timed.py` starts Blender in its own session so that it can kill it for memory; killing the wrapper leaves Blender running. Two runs here had to be found and stopped by hand.
- **Planar with no limit on the dense crate** does not finish in half an hour.
- **A 4096 bake wants 6.5 GB** and the dense model's import 2 GB; two at once are fine on this machine, four are not.

## What could not be done or verified

- **`/usr/bin/time -v`** as asked: not installed. `scripts/timed.py` reports the same peak-memory figure from `wait4`.
- **Clean timings.** The machine was shared, and some of my own runs overlapped (the bake matrix ran beside the reduction matrix).
- **The cause of the normal bake's one-pixel differences.** Narrowed to "outside Cycles' render threads"; not found.
- **Planar with no limit on the crate** (stopped at 30 minutes) and **a 4,096-sample bake on the CPU** (stopped at 400 seconds). Neither finished; both are recorded as stopped, not as failed.
- **QuadriFlow on the crate.** Refused on the raw, the repaired, the reduced and the voxel-remeshed mesh. I did not go further than those four inputs.
- **The 4096 pictures.** Measured by picture difference; not opened.
- **Every picture of every run.** I opened about forty: the dense originals, the main bakes at 1024 and 2048, the no-bake route with and without stored normals, the low-poly bakes, the chain results and Tripo's files at three-quarter, front and closest. The rest are ranked by picture difference alone.
- **The credits Tripo charged for H3.1 at 20,000,** and how long it took: those generations were made by the owner during the trial.
- **What made `orb_spiked_h31_req20000`.**
- **Why low-poly files shrink by a quarter on a round trip.**
- **How any result looks in the pit game,** under its lights and at its distances.
- **Whether `tools/bl` on another machine or another graphics card gives these bytes.**

## Method

The work was done on 2026-10-08 between 16:00 and 19:00 in one sitting. `CLAUDE.md`, `CONTEXT.md`, `profiles/pit.toml`, `kiln/run.py`, `kiln/blender_scripts/scale_to_size.py` and the Tripo trial's scripts were read first, then sections 9 and 10 of the Tripo note, Part 2 of the desk note and stage 3 of the local generator trial.

The stage scripts were written one at a time and each tried on a small model before a dense one. Three things were found by a result that looked wrong and were then chased:

- The first bake showed dark slashes on the crate. The reduced mesh had arrived unwelded; a weld was added to the bake script.
- The ray check said 93% of rays missed on the P1.0 crate while the baked picture was plainly right. The check was sampling triangles, not surface, and nearly all of that crate's triangles are hidden inside it. The check was changed to sample by area, and the hidden-piece rule and `pieces.py` came from following that up.
- The comparison table showed the chain's crate in 94 pieces. The chain had passed kiln's checks and I had not yet looked at its pictures. The weld in the reduce stage, the rerun of every chain and section 8's account came from that.

Two helper mistakes cost time and no results: a process search that matched its own command line and ended my shell twice, and `timeout` leaving Blender running.

The models in `tripo-api-trial/models/` and the existing folders in `tripo-api-trial/measurements/` were only read. No network was used, nothing was installed, nothing was committed. The browser, Tripo and `tripo-api-trial.md` were not touched.
