# Agent skills and workflow for production 3D assets

Research date: 2026-10-04. Audience: a senior software engineer with no 3D background, driving Claude Code on Arch/Omarchy.

Revised the same day for two decisions: the target engine is **Bevy**, and Blender is driven **from the command line only**. Godot, Unreal and Unity material is kept only as comparison.

**How to read the evidence labels**

- Unmarked statements with a link are **verified**: I fetched the linked page on 2026-10-04 and the claim is on it.
- **[summarised fetch]** means the page was fetched through a summarising fetch tool, not read as raw text (mainly Epic, Unity, Meshy and VRChat pages, which render client-side). Treat exact wording and numbers as one step less certain.
- **[inference]** is my reasoning or recommendation, not a sourced fact.
- **unverified** means I could not confirm it against a primary source. These are collected in [section 11](#11-unverified-items).
- Nothing in this document was executed. Blender, the glTF validator and USD tools are not installed on this machine, and no Rust code was compiled, so every command line and every Bevy design here comes from documentation and source reading, not from a run.

---

## 1. Summary of the recommendation

Two decisions are now fixed: **the target engine is Bevy**, and **Blender is driven only through its command line, with no MCP server**.

1. **Treat an asset as code, and treat Blender as a headless compiler.** Each asset is a Python build script run with `blender --background --factory-startup --python-exit-code 1 --python …`, plus a machine-readable spec. The `.blend`, the GLB and the review renders are build outputs. [inference]
2. **Build the feedback loop before any modelling skill.** The 3D equivalent of a test suite is six layers: spec lint, mesh checks in `bmesh`, glTF validation plus a Bevy-compatibility lint, a re-import round trip, a headless Bevy load test that exits non-zero, and fixed-camera renders that the agent reads back as images. Only the last layer needs judgement, and part of that judgement has to be yours. [inference]
3. **Deliver GLB, and constrain it to what `bevy_gltf` loads.** glTF 2.0 is Bevy's only first-party 3D model format that I could find. Bevy 0.19 does not load Draco, meshopt, `KHR_mesh_quantization`, `KHR_texture_basisu`, sheen, iridescence or material variants ([bevy_gltf 0.19.1](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)). A file can pass the Khronos validator and still not load correctly in Bevy, so the pipeline needs its own lint for this.
4. **Pin Bevy and plan for churn.** Stable is 0.19.1 (2026-08-13) and 0.20.0-rc.2 is already out (2026-09-28) ([releases](https://github.com/bevyengine/bevy/releases)). Every ecosystem crate you need (Skein, Avian, bevy_rapier) is pinned to one Bevy minor version. The engine-side test is Rust code that will need porting at each upgrade.
5. **Bevy ships no editor, so Blender is also the level editor.** Use [Skein](https://github.com/rust-adventure/skein) to attach Bevy components to Blender objects through glTF extras. It supports Bevy 0.19 and Blender 5.2 and was last pushed 2026-09-20. Blenvy is stale (crate targets Bevy 0.14). The official editor is not shipped.
6. **Keep Matt Pocock's skills for everything that is not 3D-specific.** `grilling`, `domain-modeling`, `research`, `to-spec`, `to-tickets`, `writing-for-agents` and `retro` transfer unchanged. Write 3D analogues only for `tdd`, `prototype`, `code-review` and `diagnosing-bugs`.
7. **Write eighteen small skills yourself, of which the first eight are the core** ([section 9](#9-recommendation-skills-and-workflow)). Nothing published is a drop-in equivalent. The closest in spirit, [majidmanzarpour/blender-game-skills](https://github.com/majidmanzarpour/blender-game-skills), has gated phases with measured evidence but is one commit from 2026-09-24. Read it as a design reference; do not depend on it.
8. **Use generative 3D models as reference input, never as deliverables.** Their own docs describe remeshed output with a target polycount, and auto-rigging limited to clear humanoids. Licensing differs sharply between vendors ([section 7](#7-generative-ai-3d-tools)).
9. **Be realistic about what agents do well.** Hard-surface and procedural geometry, pipeline automation, validation and batch processing are tractable. Organic sculpting, appealing characters and good animation are not, and no check in this document measures appeal. [inference]

Your machine today: `cargo` and `rustc` 1.99.0 are installed. There is no `blender`, `openscad`, `f3d`, `gltf_validator` or `usdchecker` on `PATH`. Python is 3.14.7; `uv`, `node` 26.7.0 and ImageMagick 7.1.2-31 are present; the GPU is an RTX 3080. Arch `extra` offers `blender 5.2.1`, `openscad 2021.01` and `f3d 3.5.0`. (Local read-only inspection; nothing was installed.)

---

## 2. What Matt Pocock's skills are, structurally

Source: [mattpocock/skills](https://github.com/mattpocock/skills), MIT, plugin version 1.3.1, last commit 2026-10-04 ([plugin.json](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json)).

**Shape**

- Each skill is a folder with a `SKILL.md` (YAML frontmatter `name` and `description`, then prose), optional sibling reference files, and optional scripts. Example: `skills/engineering/tdd/` holds `SKILL.md`, `tests.md` and `mocking.md` ([repo tree](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd)).
- The plugin manifest lists 27 skill folders in two buckets, `engineering` and `productivity` ([plugin.json](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json)).
- Skills are short. `research/SKILL.md` is 794 bytes, `implement/SKILL.md` 433 bytes, `grill-with-docs/SKILL.md` 247 bytes. The longest of the core ones, `tdd`, is 3.5 KB.
- Two install paths: a managed Claude Code plugin, or `npx skills@latest add mattpocock/skills`, which copies editable files into your repo ([README](https://github.com/mattpocock/skills/blob/main/README.md)).

**The one structural axis: who can invoke a skill** ([.agents/invocation.md](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md))

| Kind | Frontmatter | Job | Examples |
| --- | --- | --- | --- |
| User-invoked | `disable-model-invocation: true` | Orchestrate. May call model-invoked skills, never another user-invoked one. | `grill-with-docs`, `to-spec`, `to-tickets`, `implement` |
| Model-invoked | default | Hold the reusable discipline. Description carries trigger phrasing. | `grilling`, `domain-modeling`, `tdd`, `prototype`, `code-review`, `research` |

Composition is by explicit instruction. `grill-with-docs` is one line: "Call the Skill tool twice, for "grilling" and "domain-modeling"" ([SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)).

**The four problems the skills answer** ([README](https://github.com/mattpocock/skills/blob/main/README.md))

| Problem | Fix | 3D reading [inference] |
| --- | --- | --- |
| "The Agent Didn't Do What I Want" | Grilling session before building | An asset brief with budget, target engine, scale and references |
| "The Agent Is Way Too Verbose" | Shared language in a glossary | A 3D glossary plus project conventions |
| "The Code Doesn't Work" | Feedback loops: types, tests, browser access | Mesh checks, validators, round trip, renders |
| "We Built A Ball Of Mud" | Daily design investment, deep modules | Reusable build modules, modular kits, clean scene hierarchy |

**Details worth copying**

- `tdd` insists on agreed seams, vertical slices ("one test → one implementation → repeat") and names a "tautological" anti-pattern where the assertion recomputes the expected value the way the code does ([tdd/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)). The 3D equivalent is a check that reads its threshold from the same script that built the mesh.
- `prototype` defines a prototype as "throwaway code that answers a question" ([prototype/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md)). A blockout is the same thing.
- `code-review` runs two axes, Standards and Spec, in parallel sub-agents so neither pollutes the other ([code-review/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)).
- `domain-modeling` updates the glossary inline and offers an ADR only when a decision is hard to reverse, surprising, and a real trade-off ([domain-modeling/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md)).
- `writing-for-agents` says every step should end on a checkable completion criterion and that reference material should sit behind pointers ([writing-for-agents/SKILL.md](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md)).

One naming point: upstream now calls the glossary file `GLOSSARY.md`; the README notes it was `CONTEXT.md` "from before the skills renamed the convention" ([README](https://github.com/mattpocock/skills/blob/main/README.md)). Your installed plugin's `domain-modeling` description still says `CONTEXT.md`, so check which name your installed version writes before you seed the file.

---

## 3. The production pipeline: a primer and glossary

### 3.1 Stages, what each produces, and what can be measured

"Production-level" means the asset meets a written budget and a set of conventions that the target engine needs. There is no universal standard for the numbers. The Khronos real-time asset guidelines give principles, not thresholds, and their publishing-targets section is marked "work in progress" ([Khronos 3DC guidelines](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). So the numbers live in your project's spec, and the checks enforce your spec.

| # | Stage | What it is | Measurable acceptance criteria | Machine-checkable? |
| --- | --- | --- | --- | --- |
| 1 | Reference and concept | Images and measurements that define the target | Real-world dimensions written down; views listed; unknowns marked as inferred | Partly (brief is complete) |
| 2 | Blockout | Primitive shapes at correct scale and proportion | Bounding-box dimensions within tolerance of the brief; silhouette overlap against reference | Yes |
| 3 | Modelling | The real shape. Often a high-poly version for detail and a low-poly version for delivery | Triangle count within budget; no loose geometry; no zero-area faces | Yes |
| 4 | Topology and retopology | Rebuilding the surface with deliberate edge flow | Manifold where required; no n-gons in deforming areas; consistent normals | Mostly. Edge-flow quality is a judgement |
| 5 | UV unwrapping | Flattening the surface to 2D so textures can map to it | No unintended overlap; islands inside 0 to 1; texel density within a band; padding between islands | Yes |
| 6 | Baking | Transferring high-poly detail into textures on the low-poly mesh | Normal map in tangent space with the right green-channel convention; no visible seams or skewing | Partly. Artefacts need eyes |
| 7 | Texturing and PBR | Base colour, metallic, roughness, normal, occlusion, emissive maps | Correct colour space per map; plausible value ranges; texture resolution and count within budget | Mostly |
| 8 | Rigging | Building the skeleton | Bone count within budget; naming; one root; rest pose defined | Yes |
| 9 | Skinning | Binding vertices to bones with weights | Every vertex weighted; weights normalised; at most N influences per vertex | Yes |
| 10 | Animation | Keyframed or captured motion clips | Clip names, frame ranges, loop continuity, root motion convention | Partly. Quality of motion is a judgement |
| 11 | LODs | Lower-detail versions for distance | Each LOD within its triangle budget; same pivot and bounds | Yes |
| 12 | Collision | Simplified shapes for physics | Present, convex where required, named per engine convention | Yes |
| 13 | Export | Writing the interchange file | Validator passes; units, axes, applied transforms, naming | Yes |
| 14 | Engine load | The asset loads and looks right in Bevy. Bevy has no import step; the GLB is read at run time. | The headless load test exits 0; counts, names, bounds and components match the manifest | Yes |

Concrete, sourced anchors for the criteria above:

| Criterion | What the source says |
| --- | --- |
| Triangles only at delivery | "glTF stores mesh data as triangles only and unlike authoring formats, does not support quads or ngons" ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Godot recommends triangulating before export for consistent results ([Godot: model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html)) [summarised fetch]. |
| Vertex count is not the modelling vertex count | "vertices are split on export if they contain more than one of each type of mesh data" ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Budget on the exported count. |
| Degenerate geometry | "Mesh geometry SHOULD NOT contain degenerate lines or triangles" ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). |
| Origin | "bottom center of the product to be placed at 0,0,0", with exceptions by category ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). Unreal: "best to create your meshes at the origin" ([Epic: FBX static mesh pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)) [summarised fetch]. |
| Applied transforms | Godot: "apply the object transform in the 3D modeling software" before export ([Godot: model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html)) [summarised fetch]. |
| Overlapping UVs | "In general, overlapping UVs should be avoided, but there are cases where it may be beneficial" ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). So the check must allow a declared exception. |
| Naming | Use `a-z`, `_`, `-`, `0–9`, start with a letter, no spaces ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)). |
| Skin influences | glTF: "The number of joints that influence one vertex is limited to 4 per set" ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). |
| Metallic | Unreal: treat as binary, "either 0 or 1, not anything in between" for pure surfaces ([Epic: physically based materials](https://dev.epicgames.com/documentation/en-us/unreal-engine/physically-based-materials-in-unreal-engine)) [summarised fetch]. |
| Base colour ranges | Unreal's measured non-metal intensities run from charcoal 0.02 to fresh snow 0.81; metals such as iron (0.560, 0.570, 0.580) and gold (1.000, 0.766, 0.336) (same Epic page) [summarised fetch]. A base colour of pure black or pure white on a non-metal is a defect. |
| Texture colour space | Base colour and emissive are sRGB-encoded; metallic-roughness, normal and occlusion are linear ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). |
| Channel packing | Roughness in green, metalness in blue of one texture; occlusion sampled from red ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). |
| Texture dimensions | glTF-Validator warns on non-power-of-two images ([glTF-Validator README](https://github.com/KhronosGroup/glTF-Validator)). |
| Collision naming, Unreal | `UBX_`, `UCP_`, `USP_`, `UCX_` plus the render mesh name and a two-digit index ([Epic: FBX static mesh pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)) [summarised fetch]. |
| Collision naming, Godot | Suffixes `-col`, `-convcol`, `-colonly`, `-convcolonly`; also `-navmesh`, `-occ`, `-rigid`, `-noimp`, `-loop` ([Godot: node type customization](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html)). |
| Collision in Bevy | No engine convention. Avian generates colliders for a glTF scene's descendants and can be configured per node name ([ColliderConstructorHierarchy](https://docs.rs/avian3d/0.7.0/avian3d/collision/collider/struct.ColliderConstructorHierarchy.html)). The naming rule is a project decision. |
| Skeleton size in Bevy | `MAX_JOINTS` is 256 ([bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/constant.MAX_JOINTS.html)). |
| Tangents and names in Bevy | Missing tangents are computed at load with a warning; an animation is ignored if a node in its hierarchy has no name ([bevy_gltf loader source](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs)). Export tangents and name everything. |
| Extensions Bevy cannot load | Draco, meshopt, `KHR_mesh_quantization`, `KHR_texture_basisu`, sheen, iridescence, dispersion, variants ([bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)). Their presence in a delivered file is a defect. |
| LOD alignment | Unreal: all LODs "aligned and occupying the same space with the same pivot point" ([Epic: FBX static mesh pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline-in-unreal-engine)) [summarised fetch]. Godot can generate LODs on import ([Godot: import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)). Bevy has no import step, so LODs must be authored and switched by your own code or a crate: **unverified** what Bevy 0.19 offers built in. |
| A published budget, as a worked example | VRChat avatar ranks, PC "Excellent": 32,000 triangles, 40 MB texture memory, 1 skinned mesh, 4 material slots, 75 bones. Mobile "Excellent": 7,500 triangles, 10 MB, 1 material slot ([VRChat performance ranking](https://creators.vrchat.com/avatars/avatar-performance-ranking-system/)). The PC triangle row was confirmed in raw text; the rest is [summarised fetch]. |

Triangle budgets for props, texel density targets (for example pixels per metre) and UV padding in pixels are widely used conventions, but I found no primary source that mandates specific values. They are **unverified** as numbers and must be set per project.

### 3.2 How the three use cases differ

All of this table is [inference] from the sourced facts above and general pipeline structure, except where linked.

| Stage | Game asset | Animation or film | Level and map design |
| --- | --- | --- | --- |
| Geometry | Hard triangle budget. Delivered triangulated. | Quads kept for subdivision surfaces. Budget is render time, not triangles. | Modular pieces on a fixed grid. Budget is per-scene draw calls and total triangles. |
| Retopology | Required for anything sculpted or generated. | Required for anything that deforms. | Rarely needed. Pieces are built clean. |
| UVs | One or two 0 to 1 sets. Second set for lightmaps. | UDIM tiles are common. glTF does not support UDIM ([Blender glTF manual](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)). | Tiling textures and trim sheets. Overlap is deliberate. |
| Baking | Central. Detail lives in normal maps. | Often skipped. Detail stays in geometry or displacement. | Light on baking. Heavy on reuse. |
| Materials | Metallic-roughness PBR, few material slots. | Arbitrary shader networks, renderer-specific. | Shared material library across the kit. |
| Rigging | Deform bones only, bone budget, at most 4 or 8 influences. | Complex control rigs, no bone budget. | Mostly none. Doors and props only. |
| Animation | Named clips, loops, events, root motion. | Shot-based, non-looping. | Mostly none. |
| LOD and collision | Required. | Not used. | Required, plus navigation meshes and occluders. |
| Interchange | GLB or FBX. | USD and Alembic. | GLB per piece, scene assembled in the engine. |
| What "done" means | Imports clean and meets budget. | Looks right in the final render. | Pieces snap, tile without seams, and the level plays. |

### 3.3 Glossary

Written to be seeded into `GLOSSARY.md`. Definitions are mine [inference] unless linked.

**Geometry**

- **Mesh**: vertices, edges and faces that describe a surface.
- **Vertex, edge, face**: a point, a line between two points, a filled polygon.
- **Triangle (tri), quad, n-gon**: a face with three, four, or more than four sides. Engines render triangles. Artists model in quads.
- **Tri count**: the triangle count after triangulation. The budget unit for real-time assets.
- **Topology**: how faces connect. "Good topology" means edge loops follow the form and the places where it bends.
- **Edge loop**: a continuous ring of edges. Loops around joints let a mesh bend cleanly.
- **Pole**: a vertex with three, or five or more, edges. Poles in deforming areas cause pinching.
- **Manifold**: every edge belongs to exactly two faces. Blender exposes `BMEdge.is_manifold` ([bmesh.types](https://docs.blender.org/api/current/bmesh.types.html)).
- **Watertight**: a closed manifold surface with no holes. trimesh defines it as "every edge is included in two faces" ([trimesh.base](https://trimesh.org/trimesh.base.html)).
- **Boundary edge**: an edge on the border of an open surface ([bmesh.types](https://docs.blender.org/api/current/bmesh.types.html)).
- **Normal**: the direction a face or vertex points. Lighting depends on it. A flipped normal renders dark or invisible.
- **Winding order**: the vertex order of a triangle, which decides which side is the front. trimesh checks it with `is_winding_consistent` ([trimesh.base](https://trimesh.org/trimesh.base.html)).
- **Hard edge, smooth shading, split normals**: whether lighting is interpolated across an edge. A hard edge duplicates vertices at export.
- **Degenerate face**: a face with zero area.
- **High-poly, low-poly**: the detailed source mesh and the delivery mesh.
- **Retopology (retopo)**: building a clean low-poly mesh over a messy or dense one.
- **Decimation**: automatic triangle reduction. Fast, with poor edge flow.
- **Subdivision surface (subdiv)**: smoothing a coarse quad mesh by splitting faces. A film staple.

**Transforms and scene**

- **Object transform**: location, rotation and scale of an object. **Applied transform**: the transform baked into the mesh data so the object reads rotation zero and scale one. In Blender this is `bpy.ops.object.transform_apply` ([bpy.ops.object](https://docs.blender.org/api/current/bpy.ops.object.html)).
- **Origin or pivot**: the point an object rotates and scales about.
- **Up axis, forward axis, handedness**: the coordinate convention. They differ per tool. See [section 6](#6-interchange-formats).
- **Unit scale**: what one unit means. One metre in glTF. Treated as one metre in Bevy, though I found no Bevy doc that states it.
- **Data-block**: Blender's term for a named piece of data such as a mesh, material or image.
- **Collection**: Blender's grouping of objects.
- **Modifier**: a non-destructive operation on a mesh, such as mirror, bevel or triangulate.

**UVs and textures**

- **UV coordinates, UV map**: 2D coordinates per vertex that map the surface onto an image.
- **UV island (shell)**: a connected patch in UV space. **Seam**: an edge where the surface is cut to flatten it.
- **Texel**: one texture pixel. **Texel density**: texels per unit of surface. Consistent density keeps sharpness uniform ([Khronos 3DC](https://github.com/KhronosGroup/3DC-Asset-Creation/blob/main/asset-creation-guidelines/RealtimeAssetCreationGuidelines.md)).
- **Padding (margin, bleed)**: empty pixels around each island so neighbouring colours do not leak in at lower mip levels.
- **UDIM**: a scheme of multiple UV tiles for very high resolution. Film only in practice.
- **Lightmap UVs (UV2)**: a second, non-overlapping UV set for baked lighting. Godot can generate it on import ([Godot: import configuration](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/import_configuration.html)).
- **Trim sheet**: one texture of reusable strips that many meshes map onto.
- **Tiling texture**: a texture that repeats without a visible seam.
- **Atlas**: several objects' textures packed into one image.
- **Baking**: rendering information into a texture. Blender's operator is `bpy.ops.object.bake` ([bpy.ops.object](https://docs.blender.org/api/current/bpy.ops.object.html)).
- **Cage**: an inflated copy of the low-poly mesh that controls bake ray direction.

**Materials**

- **PBR**: physically based rendering. glTF "uses the metallic-roughness material model" ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)).
- **Base colour (albedo)**: surface colour with no lighting baked in.
- **Metallic**: whether the surface is metal. **Roughness**: how blurred reflections are.
- **Normal map**: a texture that fakes small surface detail. **Tangent space**: the per-vertex frame it is defined in. glTF expects MikkTSpace tangents when none are supplied ([glTF 2.0 spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). glTF and Blender use the "+Y up" (OpenGL) green channel ([Blender glTF manual](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)).
- **Ambient occlusion (AO)**: a map of how much indirect light reaches each point.
- **ORM**: a packed texture with occlusion, roughness and metallic in R, G and B.
- **Emissive**: light the surface gives off.
- **Principled BSDF**: Blender's PBR shader node. It is what the glTF exporter reads ([Blender glTF manual](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)).
- **Material slot**: one material assignment on a mesh. Each slot usually costs a draw call.

**Rigging and animation**

- **Armature, skeleton**: the bone hierarchy. **Bone, joint**: one element of it.
- **Rest pose (bind pose, T-pose, A-pose)**: the pose the mesh was bound in. Godot wants the skeleton reset to it before export ([Godot: model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html)) [summarised fetch].
- **Skinning**: binding vertices to bones. **Weights**: how much each bone moves each vertex. **Influences**: the bones affecting one vertex.
- **Deform bone, control bone**: bones that move the mesh, and bones the animator handles. Only deform bones ship in a game.
- **IK, FK**: inverse and forward kinematics. Posing from the end of a chain, or from the root.
- **Shape key (morph target, blend shape)**: a stored alternative vertex position set, used for faces.
- **Action, clip**: a named animation. **Root motion**: movement driven by the root bone, not by game code.
- **Retargeting**: transferring animation between skeletons.

**Delivery**

- **LOD**: level of detail. LOD0 is the full mesh.
- **Collision mesh**: simplified geometry for physics. **Convex hull**: a collision shape with no dents.
- **Draw call**: one batch the GPU renders. Roughly one per mesh per material.
- **Interchange format**: a file format for moving assets between tools. glTF, FBX, USD.
- **DCC**: digital content creation tool. Blender, Maya, ZBrush.
- **Round trip**: export, re-import, and compare with what you meant to export.
- **Turntable**: a set of renders orbiting the asset. **Matcap, clay render**: a flat grey render that shows form without materials. **Wireframe render**: shows topology. **Checker render**: a checkerboard texture that shows UV stretching and density.

**Bevy**

- **ECS, entity, component, system**: Bevy's architecture. An entity is an ID, components are data attached to it, systems are functions that run over them. A loaded glTF node becomes an entity.
- **Asset server, handle**: the loader and the reference it returns. Loading is asynchronous; a handle is valid before the data arrives.
- **Asset label**: the `#Scene0`-style suffix that selects one part of a glTF file. A misspelled label is ignored without warning ([bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)).
- **Load state**: whether an asset and its dependencies have loaded, are loading, or failed ([RecursiveDependencyLoadState](https://docs.rs/bevy/0.19.1/bevy/asset/enum.RecursiveDependencyLoadState.html)).
- **glTF extras**: free-form JSON on glTF objects. Blender writes custom properties there. Bevy exposes them as `GltfExtras` components.
- **Reflection, type registry**: Bevy's run-time type information. It is what lets a tool such as Skein turn JSON into typed components.
- **Skein**: a Bevy plugin and Blender extension that stores component data in glTF extras and inserts the components on spawn ([skein](https://github.com/rust-adventure/skein)).
- **BSN**: Bevy Scene Notation, the new scene format in 0.19. No `.bsn` file loader ships yet ([Bevy 0.19 notes](https://bevy.org/news/bevy-0-19/)).
- **Asset processor, `.meta` file**: optional build step that transforms source assets into `imported_assets/`, and the per-asset settings file beside each asset ([asset processor](https://docs.rs/bevy/0.19.1/bevy/asset/processor/index.html)).
- **Hot reload**: a changed asset file is reloaded in the running app. Needs the `file_watcher` feature.
- **BRP**: Bevy Remote Protocol. JSON-RPC over HTTP for inspecting and changing a running app ([bevy_remote](https://docs.rs/bevy_remote/0.19.1/bevy_remote/)).
- **Collider constructor**: an Avian component that builds a physics shape, optionally from a mesh.
- **Plugin, cargo feature**: how Bevy functionality is switched on. glTF animation loading, hot reload and several material extensions are behind features.

**Level design**

- **Modular kit**: wall, floor, corner and door pieces built to snap together.
- **Grid**: the snapping unit the kit is built on.
- **Greybox (whitebox)**: a playable level built from blockout geometry.
- **Navmesh**: the walkable surface used for pathfinding. **Occluder**: geometry that hides things behind it from rendering.

---

## 4. Driving 3D tools programmatically

### 4.1 Blender from the command line (the chosen driver)

Current release: **Blender 5.2 LTS**, released 2026-07-14; 5.2.2 dated 2026-09-15 ([blender.org download](https://www.blender.org/download/), [5.2 release page](https://www.blender.org/download/releases/5-2/), [download.blender.org](https://download.blender.org/release/Blender5.2/)). API docs are titled "Blender 5.2 Python API Documentation" ([docs.blender.org/api/current](https://docs.blender.org/api/current/index.html)).

The agent drives Blender with shell commands only. No add-on, socket or MCP server is involved.

#### Arguments that matter

All from the [Blender manual: command line arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html).

| Flag | Meaning from the manual | Use |
| --- | --- | --- |
| `-b`, `--background` | "Run in background (often used for UI-less rendering)." | Always |
| `--factory-startup` | "Skip reading the startup.blend in the users home directory." | Always, for reproducibility |
| `-P`, `--python <filepath>` | "Run the given Python script file." | The build, check, render and export scripts |
| `--python-expr <expression>` | "may be a complete multi-line script; you are limited only by the platform's maximum argument length" | One-line probes, such as printing a version |
| `--python-exit-code <code>` | "Set the exit-code in [0..255] to exit if a Python exception is raised (only for scripts executed from the command line), zero disables." | Always. Without it an uncaught exception still exits 0 |
| `--` | "End option processing, following arguments passed unchanged. Access via Python's sys.argv." | Passing your own arguments to the script |
| `-o`, `--render-output <path>` | Sets the render path. `//` is relative to the blend file. | Renders |
| `-f`, `--render-frame <frame>` | Renders one frame. Accepts lists and `..` ranges. | Stills |
| `-a`, `--render-anim` | "Render frames from start to end (inclusive)." | Turntables |
| `-E`, `--engine <engine>` | "Specify the render engine. Use `-E help` to list available engines." | Choosing Cycles or EEVEE |
| `-t`, `--threads <threads>` | Thread count for rendering and other operations | Pinning for repeatable timing |
| `--addons <addon(s)>` | "Comma separated list (no spaces) of add-ons to enable in addition to any default add-ons." | Enabling an exporter or Skein under `--factory-startup` |
| `--offline-mode` / `--online-mode` | "Disallow internet access, overriding the preference." / "Allow internet access, overriding the preference." | `--offline-mode` always |
| `-c`, `--command <command>` | "Run a command which consumes all remaining arguments. Use `-c help` to list all other commands… This implies `--background` mode." | Your own subcommands, see below |
| `-q`, `--quiet` | "Suppress status printing (warnings & errors are still printed)." | Keeping agent context small |
| `--log-level`, `--log-file` | Logging verbosity and destination | Diagnosis |
| `--debug-exit-on-error` | "Immediately exit when internal errors are detected." | Stricter failure |
| `-y` / `-Y` | Enable or disable automatic Python script execution. Disabled is the default. | Leave disabled |

Two ordering traps from the manual. "Arguments are executed in the order they are given", so `-o` must come before `-f`, and a blend file loaded after `-o` overwrites the output path ([arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)). "Always position `-f` or `-a` as the last arguments", and "Arguments are case sensitive! `-F` and `-f` are not the same" ([rendering from the command line](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html)).

Canonical forms [inference, assembled from the flags above]:

```bash
# build, check or export: a script with its own arguments
blender --background --factory-startup --offline-mode --quiet \
  --python-exit-code 1 --python tools/validate.py -- --spec assets/crate/spec.json

# render one still from an existing file, order matters
blender --background --factory-startup assets/crate/out/crate.blend \
  --engine CYCLES --render-output //review/front_ --render-frame 1
```

#### Custom subcommands: `--command`

Blender 5.2 has a registration API for it. `bpy.utils.register_cli_command(id, execute)` registers "a command, accessible via the (`-c` / `--command`) command-line argument". The callback takes the remaining arguments as a list of strings and returns an int: "0 for success, 1 on failure" ([bpy.utils](https://docs.blender.org/api/current/bpy.utils.html)). The registration has to happen in code Blender loads at startup, which in practice means an add-on or extension [inference]. This gives a cleaner interface, such as `blender -c asset_check crate`, at the cost of installing an add-on. Start with `--python … --` and move to `--command` only if the script arguments become unwieldy [inference].

#### Exit codes and output

- An uncaught Python exception sets the process exit code only if `--python-exit-code` is non-zero ([arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)).
- A `--command` callback's return value is the documented success or failure signal ([bpy.utils](https://docs.blender.org/api/current/bpy.utils.html)).
- Operators do not raise on failure in the way functions do: "The return value from calling an operator is the success (if it finished or was canceled)" ([gotchas: using operators](https://docs.blender.org/api/current/info_gotchas_operators.html)). A script must check the returned set and raise, or a cancelled export exits 0 [inference].
- Whether calling `sys.exit(n)` inside a `--python` script propagates `n` as the process exit code is **unverified** in the docs. Raising an exception with `--python-exit-code` set is the documented route.
- The docs do not specify which messages go to stdout and which to stderr: **unverified**. Do not parse Blender's console text. Have each script write a JSON report to a path you pass in, and treat the exit code as the only signal [inference].

#### Deterministic runs

Sourced facts, then the recipe.

- `--factory-startup` skips the user's startup file ([arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)). The `bpy` module, by comparison, always ignores user preferences ([Blender as a Python module](https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html)).
- Automatic execution of scripts embedded in blend files is off by default (`-Y`).
- `BLENDER_USER_RESOURCES` replaces the "default directory of all user files"; `BLENDER_USER_CONFIG`, `BLENDER_USER_SCRIPTS` and `BLENDER_USER_EXTENSIONS` override parts of it ([arguments: environment variables](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)).
- `--python-use-system-env` is opt-in; without it Blender's Python ignores `PYTHONPATH` and user site-packages.
- The default scene contains a cube, camera and light. `bpy.ops.wm.read_factory_settings(use_empty=True)` gives an empty file ([Blender as a Python module](https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html)).
- Cycles has a `Seed` setting, and "Use Animated Seed" changes it per frame ([Cycles sampling](https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html)).

Recipe [inference]: pin one Blender version from an official tarball; always pass `--factory-startup --offline-mode`; point `BLENDER_USER_RESOURCES` at an empty project-local directory so no personal add-on or preference leaks in; start every build script from an empty file; enable needed add-ons explicitly with `--addons`; fix the Cycles seed and sample count and leave animated seed off; set every export option explicitly in the script and never rely on defaults. Geometry and exports should then be repeatable. Rendered pixels are not guaranteed identical across GPUs or versions (**unverified** either way), so compare renders with a threshold.

#### Headless rendering without a display or GPU on Linux

This was an open item. The docs resolve most of it.

| Engine | What the docs say | Consequence |
| --- | --- | --- |
| EEVEE | "Being a rasterization engine, EEVEE only uses the power of the GPU to render. There is no plan to support CPU (software) rendering". Under Headless Rendering: "not supported on headless Windows systems" ([EEVEE limitations](https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html)). Headless on Linux was added in 3.4 ([3.4 release notes](https://developer.blender.org/docs/release_notes/3.4/eevee/)). | Works without a display on Linux. Needs a GPU. |
| Cycles | GPU rendering is described as an option used "instead of the CPU", enabled per scene ([Cycles GPU rendering](https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html)). | Runs on CPU with no GPU and no display. The safe default for CI and containers. |
| Workbench | Manual page did not load. | **Unverified**. It is the viewport engine, so assume it needs a GPU until tested. |

Command-line rendering needs no display server at all: "we do not need a graphical display (no need for X server on Linux for example)" ([rendering from the command line](https://docs.blender.org/manual/en/latest/advanced/command_line/render.html)).

For this machine [inference]: the RTX 3080 means EEVEE headless should work and is the fast choice for review sheets. Use Cycles on CPU with a low sample count as the fallback and as the reference when a render differs between machines. Whether EEVEE works through a software rasteriser such as llvmpipe is **unverified**; the manual's wording suggests it is unsupported.

#### One long-lived process, if startup cost matters

The docs describe no server or daemon mode for the Blender binary: **unverified** that none exists, but none is in the argument list. Measure first; startup cost on your machine is unknown. If it matters, three options, cheapest first [inference]:

1. **Batch inside one invocation.** One `--python` script loops over many assets or many checks. Reset between items with `bpy.ops.wm.read_factory_settings(use_empty=True)` or open the next file. This removes most of the cost with no extra machinery.
2. **Combine stages.** Build, check, render and export in one process for the inner loop, with separate invocations kept for CI.
3. **Use the `bpy` module in a long-lived Python process**, such as a `pytest` session. A pre-compiled module is on pip and "for the most part… is equivalent to running a script in background-mode" ([Blender as a Python module](https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html)). Caveats from the same page: no crash log, reloading the module is unsupported, and `bpy` 5.2.2 requires Python `==3.13.*` ([PyPI bpy](https://pypi.org/project/bpy/)) while this machine has 3.14.7. `uv` can supply 3.13.

For repeated renders of the same scene, `RenderSettings.use_persistent_data` keeps "render data around for faster re-renders… at the cost of increased memory usage" ([bpy.types.RenderSettings](https://docs.blender.org/api/current/bpy.types.RenderSettings.html)).

#### API facts that matter for agents

- Operators (`bpy.ops.*`) depend on context, cannot be passed data directly, and a failing poll gives "context is incorrect" with no reason ([gotchas: using operators](https://docs.blender.org/api/current/info_gotchas_operators.html)). Prefer the data API (`bpy.data`, `bmesh`) and use `Context.temp_override` when an operator is unavoidable ([bpy.types.Context](https://docs.blender.org/api/current/bpy.types.Context.html)). This is the main source of agent-written Blender scripts that fail [inference].
- `bmesh` gives the topology predicates you need: `is_manifold`, `is_boundary`, `is_wire`, `is_contiguous` on edges, `calc_area` on faces, `calc_volume` on the mesh ([bmesh.types](https://docs.blender.org/api/current/bmesh.types.html)).
- `Mesh.validate()` returns true when invalid geometry was corrected ([bpy.types.Mesh](https://docs.blender.org/api/current/bpy.types.Mesh.html)).
- UV operators exist for overlap selection, island scale averaging and packing: `uv.select_overlap`, `uv.average_islands_scale`, `uv.pack_islands`, `uv.smart_project` ([bpy.ops.uv](https://docs.blender.org/api/current/bpy.ops.uv.html)).
- Geometry Nodes trees are scriptable as `bpy.types.GeometryNodeTree` ([API](https://docs.blender.org/api/current/bpy.types.GeometryNodeTree.html)). An agent building node graphs by script is verbose and hard to review; plain Python that builds meshes is easier to diff [inference].
- The glTF exporter's defaults are not what Bevy wants. From the operator signature: `export_yup=True`, `export_apply=False`, `export_tangents=False`, `export_extras=False`, `export_cameras=False`, Draco off ([bpy.ops.export_scene](https://docs.blender.org/api/current/bpy.ops.export_scene.html)). See [section 4.5](#45-bevy-the-target-engine) for the settings to change.

### 4.2 MCP servers: considered, not used

Decision: no MCP server. The reasons hold up [inference]: a Claude Code agent with a shell can run everything above; file-based builds are reproducible and diffable where a live session is not; and both servers execute model-written Python with no sandbox. Blender Lab says its server "will execute LLM generated code in Blender without any guards in place to protect your data from removal or being sent to a remote location" ([blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)).

For the record, what exists:

| Server | Maintainer | State on 2026-10-04 |
| --- | --- | --- |
| [Blender Lab `blender_mcp`](https://projects.blender.org/lab/blender_mcp) | Blender Lab, official | v1.0.3 on 2026-09-11, GPL-3, needs Blender 5.1+, 26 tools including `execute_blender_code`, screenshots and bundled API docs search ([readme_tools.rst](https://projects.blender.org/lab/blender_mcp/src/branch/main/readme_tools.rst)) |
| [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | One community maintainer; "not made by Blender" | About 30k stars, MIT, last push 2026-09-30 |

The one thing lost by not using MCP is the agent seeing your live viewport. The review renders replace that. Revisit only if you find yourself wanting the agent to inspect a scene you are editing by hand.

Blender Lab's own example is an argument for scripted checks over ad hoc questions: an LLM's polygon-count analysis "only considered the modifiers which influenced the viewport" and missed a Solidify modifier ([blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/)).

### 4.3 Code-CAD

| Tool | State | Fit |
| --- | --- | --- |
| [OpenSCAD](https://openscad.org/downloads.html) | Last stable release is 2021.01; development snapshots add the Manifold geometry engine ([downloads](https://openscad.org/downloads.html), [repo](https://github.com/openscad/openscad)). | CSG solids from a small language. Good for printable parts. No UVs, materials or rigs. |
| [CadQuery](https://github.com/CadQuery/cadquery) | v2.8.0, 2026-06-20, Python >= 3.11 ([PyPI](https://pypi.org/project/cadquery/)). | Python BREP modelling on OpenCASCADE. Precise mechanical parts, fillets, STEP export. |
| [build123d](https://github.com/gumyr/build123d) | v0.13.0, 2026-09-21, Apache-2.0, Python 3.11 to 3.14 ([PyPI](https://pypi.org/project/build123d/)). | Same kernel, more Pythonic API. Exports STEP, 3MF, BREP and glTF ([import/export docs](https://build123d.readthedocs.io/en/latest/import_export.html)). |

Where they fit [inference]: hard-surface source geometry with exact dimensions, such as machinery, weapons, architecture and modular kit pieces, and anything 3D-printed. They are text in, solid out, which suits an agent well. Where they do not fit: they produce tessellated triangle soup with no deliberate topology, no UVs and no PBR textures. Their output still needs the retopology, UV, material and export stages in Blender. They cannot do organic forms, rigging or animation. An existing skill in this niche is [flowful-ai/cad-skill](https://github.com/flowful-ai/cad-skill) (CadQuery, for 3D printing).

### 4.4 Mesh libraries outside Blender

- [trimesh](https://github.com/mikedh/trimesh) 5.1.1 (2026-10-02, MIT): `is_watertight`, `is_winding_consistent`, `is_volume`, `euler_number`, `body_count` ([trimesh.base](https://trimesh.org/trimesh.base.html)). Use it to check the exported file independently of Blender.
- [glTF-Transform](https://github.com/donmccurdy/glTF-Transform) CLI 4.5.1: `inspect`, `validate`, `optimize`, `dedup`, `prune`, `weld`, `simplify`, `resize`, `draco`, `meshopt`, `etc1s`, `uastc` ([CLI docs](https://gltf-transform.dev/cli)). For Bevy, use `inspect` and `validate` only: `draco` and `meshopt` produce files `bevy_gltf` cannot load, and what `optimize` enables by default is **unverified**.
- [meshoptimizer](https://github.com/zeux/meshoptimizer) v1.3 (2026-09-25, MIT): simplification and the `gltfpack` optimiser.
- [manifold](https://github.com/elalish/manifold) v3.5.4 (Apache-2.0): robust booleans on manifold meshes; Python package `manifold3d`.

### 4.5 Bevy, the target engine

Sources for this section are the `bevyengine/bevy` repository at tag `v0.19.1`, docs.rs for the 0.19.1 crates, and bevy.org. Nothing here was compiled or run.

#### Release, cadence and churn

- Latest stable is **0.19.1**, published 2026-08-13. 0.19.0 was published 2026-06-18. **0.20.0-rc.2** was published 2026-09-28, so 0.20 is close ([GitHub releases](https://github.com/bevyengine/bevy/releases)).
- The news index shows release posts dated 2026-06-19, 2026-01-13, 2025-09-30 and 2025-04-24 ([bevy.org/news](https://bevy.org/news/)). That is a minor release every three to five months. The mapping of the three older dates to 0.18, 0.17 and 0.16 is my reading of the index, not confirmed per post.
- Bevy is pre-1.0, and minor versions break APIs. A visible example in the sources I read: `bevy_gltf` 0.19.1 documents spawning a glTF with `WorldAssetRoot` ([bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)), while Skein's README still shows `SceneRoot` ([skein README](https://github.com/rust-adventure/skein)). 0.19 also introduced a new scene system, BSN ([Bevy 0.19 notes](https://bevy.org/news/bevy-0-19/)).
- The minimum supported Rust version is "the latest stable release" of Rust ([setup guide](https://bevy.org/learn/quick-start/getting-started/setup/)).
- Ecosystem crates are tied to one Bevy minor: `bevy_skein` 0.6.0, `avian3d` 0.7.0 and `bevy_rapier3d` 0.36.0 all require `bevy ^0.19.0` ([crates.io](https://crates.io/crates/avian3d)).

What this means for pinning [inference]: pin the exact Bevy version in `Cargo.toml` and commit `Cargo.lock`. Upgrade only when every crate you depend on has a matching release. Keep the smoke-test binary small, because it is the engine-side code you will port at each upgrade. Record the Bevy version in each asset manifest so a later failure can be attributed.

#### What `bevy_gltf` loads

glTF 2.0 is the format. The crate describes itself as a "Plugin providing an AssetLoader and type definitions for loading glTF 2.0… files in Bevy" ([bevy_gltf 0.19.1](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)). I found no other first-party mesh or model loader in the feature list ([cargo_features.md](https://github.com/bevyengine/bevy/blob/v0.19.1/docs/cargo_features.md)); that absence is **unverified** as a complete statement.

| Feature | Status in 0.19.1 | Source |
| --- | --- | --- |
| Scenes, nodes, meshes, materials | Loaded. Parts are addressable by label, such as `GltfAssetLabel::Scene(0)`, and by name through `Gltf.named_scenes`. | [bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/) |
| Cameras, lights | Loaded when `load_cameras` and `load_lights` are true. `KHR_lights_punctual` is supported. | [GltfLoaderSettings](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/struct.GltfLoaderSettings.html) |
| Animations | Loaded as `AnimationClip` with `AnimationPlayer` added to affected hierarchies. "Requires the `bevy_animation` feature." | same |
| Skins | `GltfSkin` with joints and inverse bind poses. `MAX_JOINTS` is 256. | [MAX_JOINTS](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/constant.MAX_JOINTS.html) |
| Morph targets | Loaded. Names come from Blender's convention of placing shape key names in mesh extras. | [bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/) |
| Extras (custom properties) | Exposed as `GltfExtras`, `GltfSceneExtras`, `GltfMeshExtras`, `GltfMaterialExtras`. Example: `examples/gltf/load_gltf_extras.rs`. | [bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/) |
| Material extensions, supported | `KHR_materials_emissive_strength`, `_ior`, `_unlit`, `_volume`. Behind cargo features: `_anisotropy`, `_clearcoat`, `_specular`, `_transmission`. | same |
| Material extensions, **not** supported | `KHR_materials_sheen`, `_iridescence`, `_dispersion`, `_variants` | same |
| Compression, **not** supported | `KHR_draco_mesh_compression`, `EXT_meshopt_compression`, `KHR_mesh_quantization` | same |
| Textures | `KHR_texture_basisu` and `EXT_texture_webp` are not supported as extensions, though "Bevy supports ktx2 and webp formats". PNG, JPEG, KTX2, WebP and others are cargo features. | same; [cargo_features.md](https://github.com/bevyengine/bevy/blob/v0.19.1/docs/cargo_features.md) |
| `KHR_texture_transform` | "only supported on base_color_texture" | [bevy_gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/) |
| `KHR_animation_pointer`, `EXT_mesh_gpu_instancing` | Not supported | same |

Loader behaviours that become pipeline rules, read from the loader source ([loader/mod.rs at v0.19.1](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs)):

| Loader behaviour | Pipeline rule [inference] |
| --- | --- |
| Missing tangents on a normal-mapped material are computed with a warning: "Consider using a tool such as Blender to pre-compute the tangents." | Export tangents. Blender's default is `export_tangents=False`. |
| Missing normals are computed as flat. | Always export normals. |
| "Animation ignored for node …: part of its hierarchy is missing a name" | Every node and bone in an animated hierarchy must be named. |
| "Sparse accessor not supported for animation sampler input" | Do not post-process with a tool that writes sparse accessors. |
| `UnsupportedPrimitive` is an error. | Export triangles only. |
| A misspelled asset label "will simply ignore it without warning". | Load by typed label and assert the result is present. |

So the Blender export must avoid Draco, and any glTF-Transform step must avoid `draco`, `meshopt` and quantisation. Materials must stay within Principled BSDF inputs that map to the supported extensions; a sheen or iridescence input will export and then be dropped by Bevy [inference from the two tables].

#### Coordinate system and units

| | Up | Forward | Right | Handedness | Unit |
| --- | --- | --- | --- | --- | --- |
| Blender | +Z | +Y ("Y Forward, Z Up", [Blender USD manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)) | | right | configurable |
| glTF | +Y | +Z | −X | right | metre ([spec 3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)) |
| Bevy | +Y | −Z | +X | right | **unverified** |

Bevy's convention is in the `Camera3d` docs: "The camera coordinate space is right-handed X-right, Y-up, Z-back. This means "forward" is -Z" ([bevy_camera source](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_camera/src/components.rs)), and in `GltfConvertCoordinates`, which lists glTF as forward +Z and Bevy as forward −Z ([docs](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/convert_coordinates/struct.GltfConvertCoordinates.html)).

How they line up:

- Blender's exporter converts Z-up to Y-up by default (`export_yup=True`). After that, glTF and Bevy agree on up and handedness. Geometry arrives the right way up and not mirrored.
- They disagree on what "forward" means. A character modelled facing glTF-forward (+Z) faces Bevy's backward. `GltfConvertCoordinates` can rotate the scene root or the meshes to fix this, but it is marked "CAUTION: This is an experimental feature. Behavior may change in future versions", and cameras and lights are exempt from it.
- Decide once, in an ADR, whether you fix facing in the asset, with the loader option, or in game code. Then check it in the smoke test with an asset that has an obvious front [inference].
- I found no Bevy documentation stating that one unit is one metre. glTF is in metres and the loader applies no scale that I saw, so treat one unit as one metre and confirm it with your physics crate's gravity default [inference]. **Unverified.**

#### The engine-side smoke test (layer L4)

Official examples to start from, all in [examples/app at v0.19.1](https://github.com/bevyengine/bevy/tree/v0.19.1/examples/app):

| Example | What it shows | Needs |
| --- | --- | --- |
| `headless.rs` | `ScheduleRunnerPlugin` running "without windowing", with `default-features = false` | No window, no GPU |
| `no_renderer.rs` | `DefaultPlugins` with `RenderPlugin` set to `backends: None`. "This can be very useful for integration tests or CI." | No GPU. It still opens a window as written. |
| `headless_renderer.rs` | Rendering from a camera to an image and saving it, with `primary_window: None` and `WinitPlugin` disabled because it "will panic in environments without a display server" | No window. A graphics adapter is needed. |
| `externally_driven_headless_renderer.rs` | The same, "pumping the update loop manually" | as above |

Building blocks, all documented:

- `AppExit::Error(NonZero<u8>)` "is roughly meant to map to a standard definition of a process exit code"; `AppExit::error()` gives code 1 ([AppExit](https://docs.rs/bevy/0.19.1/bevy/app/enum.AppExit.html)).
- `RecursiveDependencyLoadState` has `Loaded` and `Failed(Arc<AssetLoadError>)`, covering the file and everything it references ([docs](https://docs.rs/bevy/0.19.1/bevy/asset/enum.RecursiveDependencyLoadState.html)).
- `GltfLoaderSettings.load_meshes` and `load_materials` take `RenderAssetUsages`, which decides whether data is "retained in RAM/VRAM" ([docs](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/struct.GltfLoaderSettings.html)). The test must keep mesh data in main memory to measure it.
- The loaded `Gltf` asset exposes scenes, named scenes, nodes, meshes, materials, skins and animations ([Gltf](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/)).

Design for the test [inference; not compiled]:

1. A small binary crate, `asset_smoke`, in the same Cargo workspace as the game, so it uses the same Bevy version and features.
2. Plugins: `DefaultPlugins` with `WinitPlugin` disabled, `primary_window: None`, `RenderPlugin` with `backends: None`, plus `ScheduleRunnerPlugin::run_loop`. This combines `no_renderer.rs` and `headless_renderer.rs`. Whether that exact combination initialises cleanly is **unverified**; it is the first thing to spike.
3. Load the GLB as `Handle<Gltf>` with settings that retain meshes in main memory.
4. Each frame, read the recursive load state. On `Failed`, print the error and exit with `AppExit::error()`. On a frame-count timeout, exit non-zero.
5. On `Loaded`, compare against the asset's `manifest.json`: scene, node, mesh, material, skin and animation counts; the names of required nodes; each mesh's vertex and triangle counts; a bounding box computed from position attributes, within tolerance; presence of normals, tangents and UVs; presence of expected extras.
6. Spawn the scene once and run a few frames, so that scene instantiation, Skein component insertion and collider generation are exercised.
7. Write a JSON report. Exit 0 or non-zero.

Run it as `cargo run -p asset_smoke --release -- assets/crate.glb assets/crate.manifest.json`. A `cargo test` integration test can wrap the same code. The first build compiles Bevy and is slow; the setup guide suggests the `dynamic_linking` feature for faster rebuilds ([setup guide](https://bevy.org/learn/quick-start/getting-started/setup/)).

**In-engine screenshots are feasible.** Three documented routes:

- The `Screenshot` component: spawn `Screenshot::primary_window()` and observe with `save_to_disk("screenshot.png")` ([Screenshot](https://docs.rs/bevy/0.19.1/bevy/render/view/window/screenshot/struct.Screenshot.html)). It wraps a `RenderTarget`, so an image target should work without a window [inference].
- `headless_renderer.rs` for frame-by-frame capture to files with no window. Its own header says that for a single screenshot "it is simpler to use" `Screenshot`.
- The `bevy_ci_testing` cargo feature: a plugin that "reads a ron file specified with the `CI_TESTING_CONFIG` environmental variable… and executes its specified actions", and it imports the screenshot trigger ([ci_testing source](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_dev_tools/src/ci_testing/mod.rs)).

All three need a working graphics adapter. Your RTX 3080 qualifies. Whether they run on a software Vulkan adapter with no GPU is **unverified**. Treat the Bevy screenshot as an optional second visual check: it shows the asset under Bevy's renderer and materials, which the Blender renders cannot [inference].

#### Asset processing, `.meta` files, hot reload and layout

- `AssetMode::Unprocessed` loads straight from the asset source. `AssetMode::Processed` reads from the unprocessed source, which "defaults to the `assets` folder", and writes to `imported_assets/Default` ([AssetMode](https://docs.rs/bevy/0.19.1/bevy/asset/enum.AssetMode.html)).
- The processor is "a "build system" for assets" with the stated values automatic, configurable, lossless and deterministic. "Final post-processed assets should generally not be version-controlled" ([asset processor](https://docs.rs/bevy/0.19.1/bevy/asset/processor/index.html)).
- Enable the `asset_processor` cargo feature to run it at startup, and `file_watcher` for hot reload: "changes to "original/source assets" will be detected, the asset will be re-processed, and then the final processed asset will be hot-reloaded in the app" ([AssetMode](https://docs.rs/bevy/0.19.1/bevy/asset/enum.AssetMode.html)).
- Per-asset settings live in `.meta` files beside the asset; the repo's examples include `bevy_pixel_dark_with_meta.png.meta` ([examples/asset/files](https://github.com/bevyengine/bevy/tree/v0.19.1/examples/asset/files)). `GltfLoaderSettings` implements `Serialize` and `Deserialize` ([docs](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/struct.GltfLoaderSettings.html)), so loader settings such as coordinate conversion can be set per file there [inference].

Layout consequences [inference]:

- The Blender export step writes GLB files into the game's `assets/` tree, or a subfolder of it. That is the hand-off point.
- Start in `Unprocessed` mode. It is simpler, and the pipeline already controls the file. Add processing later for texture compression.
- With `file_watcher` on, a re-export appears in a running game without a restart. That is a second, human feedback loop for free.
- Commit `.meta` files if you create them. Ignore `imported_assets/`.
- Prefer one self-contained `.glb` per asset over `.gltf` plus loose textures, so an asset is one file to validate and move.

#### Blender as the level editor: components and metadata

Bevy ships no editor. The 0.19 notes speak of "the upcoming Bevy Editor", and say that 0.19 "doesn't ship with an official .bsn asset loader" ([Bevy 0.19 notes](https://bevy.org/news/bevy-0-19/)). The `bevy_editor_prototypes` repository is archived; its README says "Bevy is still actively working on an Editor" and points to the community-run [jackdaw](https://github.com/jbuehler23/jackdaw) for experimentation ([README](https://github.com/bevyengine/bevy_editor_prototypes)).

| Tool | What it does | State on 2026-10-04 | Verdict |
| --- | --- | --- | --- |
| glTF extras in `bevy_gltf` | First-party. Blender custom properties become `GltfExtras` components holding raw JSON, if exported with `export_extras=True`. | Part of Bevy 0.19.1 | The stable floor. You parse the JSON yourself. |
| [Skein](https://github.com/rust-adventure/skein) | A Bevy plugin plus a Blender extension. "Store reflected component data in glTF extras… and insert components based on those extras." The Blender side reads your game's type registry through BRP. | `bevy_skein` 0.6.0 for Bevy 0.19, 0.7.0-rc.1 published 2026-09-20; add-on 0.1.16 required for Blender 5.2 and later; 322 stars; last push 2026-09-20 | **Use this.** Current on both Bevy and Blender, and already has a release candidate tracking the next Bevy. |
| [Blenvy](https://github.com/kaosat-dev/Blenvy) | Blender add-on and Bevy crate for components and blueprints | README says "Alpha 1". The crate on crates.io is 0.1.0-alpha.1 from 2024-08-14 and requires `bevy ^0.14`. Last commits on the default branch are from 2025-02-16. | Do not use. Five Bevy versions behind. |
| [jackdaw](https://github.com/jbuehler23/jackdaw) | Community "Bevy 0.19 scene editor with hierarchy, inspector, and 3D viewport" | 531 stars, pushed 2026-10-03 | Not evaluated. Worth watching; not a dependency for this pipeline. |
| Official editor and `.bsn` files | The long-term answer | Not shipped | Do not wait for it. |

Notes for the command-line-only decision [inference]:

- Skein's registry fetch needs the game running with BRP enabled, and is normally triggered by a Blender operator. Whether that operator, and component assignment, can be driven from a `--background` script is **unverified**. If it cannot, fall back to writing the extras JSON yourself from the build script in the shape Skein expects, or use plain `GltfExtras`.
- Skein requires `export_extras=True`, and the add-on must be enabled with `--addons` when running under `--factory-startup`.
- For level design this gives a workable loop: build the level in Blender from kit pieces, tag objects with components such as spawn points, triggers and colliders, export one GLB, and the Bevy side instantiates gameplay from it.

#### Collision and physics

| Crate | Version | Asset-pipeline relevance |
| --- | --- | --- |
| [Avian](https://github.com/avianphysics/avian) | `avian3d` 0.7.0, `bevy ^0.19.0`, repo pushed 2026-09-21 | `ColliderConstructor` has 26 variants, including primitives and mesh-derived shapes. `ColliderConstructorHierarchy` "will automatically generate Colliders on its descendants at runtime" for a glTF scene, and can be configured **by node name** with `with_constructor_for_name("Tree", ColliderConstructor::ConvexHullFromMesh)` ([docs](https://docs.rs/avian3d/0.7.0/avian3d/collision/collider/struct.ColliderConstructorHierarchy.html)). |
| bevy_rapier | `bevy_rapier3d` 0.36.0, `bevy ^0.19.0` | The standalone repo is archived; the plugin "has been moved to the main Rapier repository" ([README](https://github.com/dimforge/bevy_rapier)). Its scene-collider API was not read: **unverified**. |

Consequences [inference]:

- Unlike Unreal's `UCX_` prefixes or Godot's `-col` suffixes, Bevy has no engine-level collision naming convention. The convention is yours, written in an ADR, and enforced by a check.
- Two workable patterns. **By name**: dedicated low-poly collision meshes named by rule, such as `<name>_col`, matched in Rust with Avian's per-name configuration, and hidden from rendering. **By component**: attach a collider constructor to the object in Blender through Skein, so the asset carries its own physics intent. The second scales better for levels. Whether Avian's `ColliderConstructor` round-trips through Skein is **unverified**.
- Trimesh colliders generated from render meshes are the easy default and the expensive one. Budget a separate collision mesh for anything dynamic.
- Mesh-derived colliders need the mesh data in main memory, which ties back to `RenderAssetUsages`.

#### BRP as a feedback channel, and agent tooling for Bevy

The Bevy Remote Protocol is first-party. `bevy_remote` is "an implementation of the Bevy Remote Protocol, to allow for remote control of a Bevy app", "based on the JSON-RPC 2.0 protocol" ([bevy_remote 0.19.1](https://docs.rs/bevy_remote/0.19.1/bevy_remote/)). With `RemoteHttpPlugin`, the app accepts HTTP POSTs "by default, on port 15702" ([http module](https://docs.rs/bevy_remote/0.19.1/bevy_remote/http/index.html)). Methods include `world.query`, `world.get_components`, `world.list_components`, `world.spawn_entity`, `world.mutate_components`, `world.get_resources`, `registry.schema` and `rpc.discover`.

This fits a shell-only agent: BRP is plain `curl` [inference].

```bash
curl -s -X POST http://127.0.0.1:15702 -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"world.query","params":{"data":{"components":["bevy_transform::components::transform::Transform"]}}}'
```

The `params.data.components` shape is from the `world.query` section of the same docs page; `rpc.discover` returns the full schema. Use BRP to inspect a running game after an asset loads: what entities exist, which components Skein inserted, where things are. Enable it only in development builds; the pages I read document no authentication.

| Agent tooling | State | Verdict |
| --- | --- | --- |
| [natepiano/bevy_brp](https://github.com/natepiano/bevy_brp) | MCP server over BRP. `bevy_brp_mcp` 0.22.8 requires `bevy ^0.19.1`; 72 stars; pushed 2026-09-30. A companion plugin, `bevy_brp_extras`, adds `screenshot`, `shutdown` and input-simulation methods. | Not used, per the no-MCP decision. The extras plugin's screenshot method is callable over plain BRP and may be useful on its own. |
| [chrisgliddon/bevy-skills](https://github.com/chrisgliddon/bevy-skills) | "Unofficial open source AI skills for Bevy"; 16 stars; pushed 2026-08-25 | Not read in depth. Engine-coding knowledge, not asset pipeline. |
| [smanaton/bevy-skill](https://github.com/smanaton/bevy-skill), [encetroc/bevy-skills](https://github.com/encetroc/bevy-skills) | 1 and 0 stars | Too new to judge. |

No first-party Bevy agent plugin exists in the Claude Code official marketplace (local cache, 315 plugins).

#### Other engines, for comparison only

| Engine | Headless import | Collision convention | First-party agent integration |
| --- | --- | --- | --- |
| Godot 4.7.2 | `godot --headless --import` ([CLI tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)) | Name suffixes such as `-col` ([docs](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/node_type_customization.html)) | None found |
| Unreal 5.8 | `UnrealEditor-Cmd … -run=pythonscript` ([Epic](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python)) [summarised fetch] | `UCX_` and related prefixes | Experimental built-in MCP server; Epic's Claude Code plugin |
| Unity 6.6 | `-batchmode -executeMethod` ([Unity](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html)) [summarised fetch] | Engine components | Unity CLI; Unity's Claude Code plugin |

The contrast with Bevy [inference]: those engines have an editor and an import step that does work for you. Bevy has neither. There is no import dialog, no generated LODs, no generated lightmap UVs and no collision naming rule. Everything the engine needs must already be in the GLB or in your Rust code. That makes the Blender-side pipeline carry more, and makes it more checkable, since nothing happens out of sight.

---

## 5. Feedback loops: the 3D test suite

This is the part that separates a pipeline from one-shot generation. Layers are ordered cheapest first. Run each on every build; stop at the first failure. The layering is [inference]; each tool's behaviour is sourced.

| Layer | Tool | Catches | Misses | CLI |
| --- | --- | --- | --- | --- |
| L0 Spec lint | Your own script over `spec.json` | Missing budget, missing scale, undeclared target engine | Anything about the mesh | `python tools/lint_spec.py assets/crate/spec.json` |
| L1 Mesh checks | `bmesh` inside headless Blender | Non-manifold and boundary edges, loose geometry, zero-area faces, flipped or inconsistent normals, n-gons, tri count, unapplied transforms, wrong dimensions, missing UVs, UV overlap, islands outside 0 to 1, unweighted vertices, too many influences, naming | Whether the shape is the right shape. Edge-flow quality. | `blender -b --factory-startup --python-exit-code 1 -P tools/validate.py -- --spec …` |
| L2 Format validation | Khronos glTF-Validator | Schema errors, bad references, NaN and invalid accessor values, wrong min/max, animation input/output errors, non-power-of-two images, extension misuse ([README](https://github.com/KhronosGroup/glTF-Validator)) | Anything aesthetic. Budgets. Scale. A valid file can be a bad asset. | `gltf_validator -a -o out/crate.glb`. "Shell return code will be non-zero if at least one error was found." |
| (not used for Bevy) USD validation | `usdchecker` | Compliance rules for a stage or USDZ package; "the best assurance that an asset will be properly interchangeable and renderable by Hydra" ([USD toolset](https://openusd.org/release/toolset.html)) | "Only the first sample of any relevant time-sampled attribute is checked" (same page). Not budgets or looks. | `usdchecker out/crate.usdc`; `--dumpRules` lists the rules |
| L3 Round trip | Headless Blender re-importing the export into an empty scene; trimesh as a second opinion | Export options that silently drop things: modifiers not applied, missing materials, wrong axis, wrong scale, lost shape keys, extra split vertices | Engine-specific import behaviour | `blender -b --factory-startup --python-exit-code 1 -P tools/roundtrip.py -- out/crate.glb assets/crate/manifest.json` |
| L2b Bevy compatibility lint | Your own script over the GLB's JSON: `extensionsUsed`, primitive modes, names, tangents, joint counts | Extensions `bevy_gltf` does not support; unnamed nodes in animated hierarchies; missing tangents; more than 256 joints; non-triangle primitives | Anything the loader does that the docs and source did not reveal | `python tools/bevy_lint.py out/crate.glb` |
| L4 Bevy load test | A small Rust binary using the asset server with no window and no render backend ([section 4.5](#45-bevy-the-target-engine)) | Load failure of the file or any dependency; counts, names and bounds that differ from the manifest; components Skein failed to insert; colliders not generated | Runtime look. Material and lighting differences are only visible in a render. | `cargo run -p asset_smoke --release -- assets/crate.glb assets/crate.manifest.json` |
| L4b Bevy screenshot (optional) | The same binary with rendering on, using `Screenshot` | How the asset looks under Bevy's renderer: materials, normal maps, facing, scale beside a reference | Needs a graphics adapter. Not bit-stable. | `cargo run -p asset_smoke --release --features render -- --screenshot review/bevy_front.png …` |
| L5 Review renders | Headless Blender rendering from fixed cameras | Everything a number cannot: wrong proportions, shading artefacts, bad bakes, UV stretching, floating parts, ugly silhouettes | Nothing systematically, but the reader can be wrong. Vision models miss subtle shading errors and are poor judges of appeal [inference]. | `blender -b assets/crate/out/crate.blend --python-exit-code 1 -P tools/review_render.py -- --out review/` |
| L5b Regression diff | ImageMagick `compare`, or `f3d --ref` | Unintended visual change between builds | Whether the baseline was right | `compare -metric RMSE a.png b.png diff.png` |
| L6 Human review | You, on a contact sheet and in the engine | Appeal, style fit, feel in motion | Things below your current skill level. See [section 10](#10-learning-path-for-the-human). | none |

Notes on specific layers.

**L1 is where most leverage is.** These checks are deterministic, run in seconds, and encode your conventions. Write them from the spec before modelling, so the first run fails for the right reason. That is the `tdd` red step. Take expected values from the brief and spec, never from the build script, or the check is tautological in Pocock's sense. [inference]

**L5 needs a fixed protocol** or the agent will pick flattering angles [inference]:

- Same cameras every time: front, side, back, top, three-quarter, and one at gameplay distance and pixel size.
- Same passes every time: clay, wireframe over clay, UV checker, final material, and a normals or face-orientation view.
- Composite into one contact sheet per phase, and store it with the commit.
- Render reference images from the same cameras so comparison is like for like. [majidmanzarpour/blender-game-skills](https://github.com/majidmanzarpour/blender-game-skills) does this with silhouette IoU thresholds per phase (0.85 at blockout, 0.90 at forms) and is worth reading for the technique.
- The agent reads the PNGs back with its file-reading tool and must write down what it sees as measurements, not as "looks good".

**Image diffing.** ImageMagick 7.1.2-31 is already installed here and supports the metrics AE, MAE, MSE, RMSE, PSNR, SSIM, DSSIM and PHASH (`compare -list metric`, run locally). [f3d](https://f3d.app/docs/next/user/OPTIONS) renders a file straight to PNG with `--output` and has a `--ref` option for comparison against a reference image. Render engines are not bit-stable across versions and GPUs, so diff with a threshold and pin the Blender version [inference].

**L2 is not enough for Bevy.** The Khronos validator checks conformance to glTF, which is a superset of what `bevy_gltf` loads. A Draco-compressed file with sheen materials is valid glTF and wrong for Bevy. L2b closes that gap cheaply, before any Rust compiles. Its rule list comes from the `bevy_gltf` support table and must be re-derived at each Bevy upgrade. [inference]

**L4 has a compile cost.** The first build of the smoke binary compiles Bevy. After that, running it on one asset should be quick, but this is **unverified** on your machine. Keep L4 out of the innermost loop if it is slow, and run L0 to L3 on every change. [inference]

**Second opinions matter.** L1 runs inside the tool that built the mesh. L2, L3 with trimesh, and L4 are independent readers of the exported bytes. A defect that Blender's exporter introduces is only visible from outside Blender [inference].

**What no layer catches**: whether the asset is good. Checks prove it is well-formed and within budget.

---

## 6. Interchange formats

| | glTF 2.0 | OpenUSD | FBX |
| --- | --- | --- | --- |
| Owner and status | Khronos. ISO/IEC 12113:2022 ([khronos.org/gltf](https://www.khronos.org/gltf/)). Spec version 2.0.1 ([spec](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)). | Pixar, open source; v26.08 released 2026-07-20 ([releases](https://github.com/PixarAnimationStudios/OpenUSD/releases)). AOUSD publishes a Core Specification ([aousd.org](https://aousd.org/)). | Autodesk. Godot's docs refer to the "proprietary FBX SDK" ([Godot: available formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)). No public spec found: **unverified**. |
| Handedness and up | "right-handed coordinate system. glTF defines +Y as up, +Z as forward, and -X as right" ([spec 3.4](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)) | Right-handed. `upAxis` is stage metadata, legal values "Y" and "Z"; fallback "Y" ([UsdGeom up axis](https://openusd.org/release/api/group___usd_geom_up_axis__group.html)) | Stored per file; the exporter chooses ([Blender FBX manual](https://docs.blender.org/manual/en/latest/files/import_export/fbx_legacy.html)) |
| Units | "The units for all linear distances are meters." Angles in radians. Animation time in seconds. | `metersPerUnit` stage metadata; falls back to 0.01 (centimetres) if unauthored ([UsdGeom linear units](https://openusd.org/release/api/group___usd_geom_linear_units__group.html)) | Stored per file |
| Geometry | Triangles, lines, points. No quads or n-gons. | Arbitrary polygons, subdivision surfaces | Polygons |
| Materials | Metallic-roughness PBR in core; extensions for clearcoat, transmission, sheen, volume and more ([validator's extension list](https://github.com/KhronosGroup/glTF-Validator)) | UsdPreviewSurface, MaterialX. Blender converts UsdPreviewSurface to and from Principled BSDF ([Blender USD manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)) | "a fixed pipeline-like support of materials"; Blender converts ([Blender FBX manual](https://docs.blender.org/manual/en/latest/files/import_export/fbx_legacy.html)) |
| Skinning and animation | Skins with 4 joints per set, morph targets, keyframe animation | UsdSkel skeletons and blend shapes. Blender notes "Absolute shape keys are not supported" ([Blender USD manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)) | Full. The historical default for character exchange |
| Validator | [glTF-Validator](https://github.com/KhronosGroup/glTF-Validator), Apache-2.0; npm `gltf-validator` 2.0.0-dev.3.10 | `usdchecker` ([toolset](https://openusd.org/release/toolset.html)) | None found |
| Strength | A delivery format. Compact, strictly specified, validates. | A scene-composition system: layers, references, variants. | Supported everywhere, especially for animated characters |
| Weakness | Not an authoring format. No UDIM, no area or world lights from Blender ([Blender glTF manual](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)). | Large surface area. Overkill for single game props. | Opaque. Importers differ. Unit and axis bugs are common [inference]. |

Blender's own convention is "Y Forward, Z Up" ([Blender USD manual](https://docs.blender.org/manual/en/latest/files/import_export/usd.html)), so every export converts axes. Blender's glTF exporter reads Principled BSDF materials ([Blender glTF manual](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html)). Anything built from other shader nodes will not export, so the materials skill must restrict itself to that node.

**Engine conventions**

| Engine | Coordinate system | Units | Preferred import |
| --- | --- | --- | --- |
| **Bevy (target)** | Right-handed, Y up, forward −Z ([bevy_camera source](https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_camera/src/components.rs)); glTF's forward is +Z, with an experimental loader option to convert ([GltfConvertCoordinates](https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/convert_coordinates/struct.GltfConvertCoordinates.html)) | **unverified**; treat as metres | glTF 2.0 through `bevy_gltf`, the only first-party model loader I found |
| Godot | Right-handed, Y up, −Z camera forward; assets face +Z ([model export considerations](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/model_export_considerations.html)) [summarised fetch] | "1 unit being equal to 1 meter" ([introduction to 3D](https://docs.godotengine.org/en/stable/tutorials/3d/introduction_to_3d.html)) | "glTF 2.0 (recommended)"; FBX via ufbx since 4.3 ([available formats](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html)) |
| Unreal | "left-handed and uses a Z-up axis"; X forward, Y right ([Epic: coordinate system](https://dev.epicgames.com/documentation/en-us/unreal-engine/coordinate-system-and-spaces-in-unreal-engine)) [summarised fetch] | Centimetres: **unverified** (not on the fetched page) | FBX 2020.2 pipeline ([Epic: FBX content pipeline](https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-content-pipeline)) [summarised fetch]; glTF via Interchange: **unverified** |
| Unity | **unverified** | One unit is one metre: **unverified** | "best practice to use the `.fbx` file format"; glTF is not mentioned on the formats page ([Unity: model file formats](https://docs.unity3d.com/Manual/3D-formats.html)) [summarised fetch] |

**What to standardise on for Bevy** [inference]

- **GLB, one self-contained file per asset.** It is the format Bevy loads, it matches Bevy's up axis and handedness, and it is the one format where "valid" is machine-decidable.
- **A restricted profile of glTF**, defined by what `bevy_gltf` 0.19 supports: triangles only; no Draco, meshopt or quantisation; PNG, JPEG or KTX2 textures referenced the plain way; core metallic-roughness plus only the extensions in the supported list; `KHR_texture_transform` on base colour only; normals and tangents present; every node and bone named; at most 256 joints.
- **Blender exporter settings, set explicitly in the export script**: `export_format='GLB'`, `export_yup=True`, `export_apply=True`, `export_tangents=True`, `export_extras=True`, Draco off, cameras and lights off unless the asset is a level that needs them. The defaults for tangents, extras and apply-modifiers are all `False` ([bpy.ops.export_scene](https://docs.blender.org/api/current/bpy.ops.export_scene.html)).
- **No FBX and no USD in this project.** Bevy loads neither first-party. If a bought asset arrives as FBX, import it into Blender and send it through the same export and gates.
- Keep the `.blend` and the build script as the source of truth. Never treat an interchange file as the master.

For other engines, briefly: Godot also prefers glTF; Unreal and Unity pipelines are built around FBX for characters; USD suits film-style scene assembly.

---

## 7. Generative-AI 3D tools

What first-party sources say about their output:

| Tool | Kind | Output per first-party docs | Licence |
| --- | --- | --- | --- |
| [Meshy](https://docs.meshy.ai/en/api/image-to-3d) | Commercial API | `topology`: "quad: Generate a quad-dominant mesh. triangle: Generate a decimated triangle mesh". `target_polycount` 100 to 300,000, where "the actual count may deviate". Optional PBR maps (metallic, roughness, normal). Formats glb, obj, fbx, stl, usdz, 3mf. A-pose or T-pose option. [summarised fetch] | Paid: "you own the assets". Free: CC BY 4.0 with credit ([Meshy help](https://help.meshy.ai/en/articles/9992001-can-i-use-the-assets-generated-on-meshy-for-commercial-purposes)) [summarised fetch] |
| [Meshy rigging](https://docs.meshy.ai/en/api/rigging-and-animation) | Commercial API | "not suitable for the following models: Untextured meshes, Non-humanoid assets, Humanoid assets with unclear limb and body structure". Limit of 300,000 faces. Walking and running presets. [summarised fetch] | as above |
| Tripo | Commercial API | SDK exposes `face_limit`, `generate_parts`, `rig_model`, `check_riggable`, `retarget_animation` ([tripo-python-sdk API.md](https://github.com/VAST-AI-Research/tripo-python-sdk/blob/master/docs/API.md)). Quad output and its restrictions: **unverified** (docs site is client-rendered). | **unverified** |
| Hyper3D Rodin | Commercial API | **unverified**. The documentation site would not serve content to my fetches. | **unverified** |
| [Hunyuan3D-2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) | Open weights | Image to shape plus PBR texture synthesis. 10 GB VRAM for shape, 21 GB for texture, 29 GB for both. Last push 2025-10-17. | Tencent community licence that "DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA", with extra terms above 1 million monthly active users ([LICENSE](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/main/LICENSE)) |
| [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) | Open weights, Microsoft | 4B-parameter image-to-3D. Advertises "Open Surfaces" and "Non-manifold Geometry" as supported output, with PBR materials. GLB export runs a remesh step. Last push 2026-07-10. | MIT |
| [Stable Fast 3D](https://github.com/Stability-AI/stable-fast-3d) | Open weights, Stability | Single image to UV-unwrapped GLB, about 6 GB VRAM. Remesh options `none`, `triangle`, `quad`; the vertex target "is not a hard constraint". Last push 2025-01-22. | Stability licence; terms **unverified** |
| [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | Open weights | Vertex colours by default; `--bake-texture` for a texture. | MIT |

**Assessment** [inference, grounded in the table]

- The vendors' own parameters tell you what the mesh is: a surface extracted from a learned volume, then automatically remeshed or decimated to a polygon target. "Quad-dominant" from an automatic remesher is not deliberate edge flow. It will not deform well at joints.
- TRELLIS.2 lists non-manifold output as a feature. That is the opposite of what L1 enforces.
- UVs are automatic unwraps. Expect many small islands and uneven texel density. Fine for a static background prop, poor for hand-editing textures.
- Base colour often has lighting baked in. SF3D names "illumination disentanglement" as a research contribution, which tells you it is a known problem in the class.
- Auto-rigging is limited to clear humanoids by Meshy's own statement.
- Geometry seen from a single image is invented on the unseen side.

**Where they belong**

| Use | Verdict |
| --- | --- |
| Concept exploration, shape ideation | Good. Cheap, fast, disposable. |
| Blockout or proportion reference, loaded as a non-exported reference object | Good. |
| High-poly source for a bake onto a hand-built or carefully retopologised low-poly | Workable for static props, if the licence allows. |
| Distant background props, after it passes L1 to L4 and budget | Acceptable. |
| Hero assets, anything that deforms, anything players look at closely | No. This is the slop. |
| Direct to engine with no checks | No. |

Treat a generated mesh exactly like an untrusted third-party dependency: quarantine it in `refs/`, record tool, version, prompt, input image and licence in the asset manifest, and never let it reach `out/` without passing the same gates as everything else.

---

## 8. Existing skills, plugins and MCP servers for 3D

Found by GitHub search on 2026-10-04. Stars, licence and dates are from the GitHub API. "Commits" is the count on the default branch at roughly 100 per page. I read READMEs and file trees. I did not install or run any of them.

| Repo | Stars | Last push | Licence | What is actually there | Assessment |
| --- | --- | --- | --- | --- | --- |
| [majidmanzarpour/blender-game-skills](https://github.com/majidmanzarpour/blender-game-skills) | 127 | 2026-09-24 | MIT | One skill, `blender-image-to-3d`: a 22 KB `SKILL.md`, four reference files, and eight scripts (`validate.py`, `review_render.py`, `roundtrip.py`, `export_delivery.py`, `bake_maps.py`, `world_gate.py`, `init_master.py`, `compose_review.py`). Eleven gated phases, each with stated evidence. | Closest to what you want in philosophy. But **one commit, created the day it was pushed**, tested only on Claude Code with Blender 5.2 by its own account. One large skill, not small composable ones. Read it, borrow the gate design and the script ideas, do not depend on it. |
| [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill) | 81 | 2026-05-01 | MIT | Plugin with 32 `SKILL.md` files and 28 Python files, version 1.3.0, driving Blender through the community MCP server. Has "What works (honestly)" and "What doesn't" sections. | Broad, and oriented to scenes, renders and reference reconstruction, not game-asset delivery. Dormant for five months. Useful to mine for validation ideas. |
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | 264 | 2026-07-10 | MIT | "94 Specialized Skills". 188 `SKILL.md` files and **zero Python files**. | Prompt text only, with no scripts to gate anything. This is the shape to avoid. |
| [MAX-786/claude-3d-harness](https://github.com/MAX-786/claude-3d-harness) | 6 | 2026-09-21 | MIT | 60 skill files behind a registry and MCP server; pins the official Blender Lab server. | By its own Status section: "Early, and so far used on one machine." Not ready to adopt. |
| [achimala/dream-loop](https://github.com/achimala/dream-loop) | 1,622 | 2026-09-09 | MIT | One skill: generate a target image, build, have a separate critic compare a screenshot with the target, repeat. | A good pattern for the L5 loop: a separate critic agent that did not build the thing. Aimed at impressive visuals, not production constraints. |
| [flowful-ai/cad-skill](https://github.com/flowful-ai/cad-skill) | 653 | 2026-07-14 | not recognised by GitHub; file not read | CadQuery skill for 3D-printable parts, phased build plus rendered preview. Requires Python 3.10 to 3.12. | Adoptable if you do printable parts. Out of scope for game assets. |
| [scenario-labs/skills](https://github.com/scenario-labs/skills) | 864 | 2026-10-04 | MIT | Skills for the Scenario commercial generation service, plus "expert tools" for DCC software. | Tied to a paid service. Not evaluated in depth. |
| [Impertio-Studio/…-Claude-Skill-Package](https://github.com/Impertio-Studio/Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package) | 41 | 2026-07-08 | MIT | 73 skills for Blender, Bonsai and IfcOpenShell. | Architecture and BIM. Out of scope. |
| [anthropics/skills](https://github.com/anthropics/skills) | 179,593 | 2026-10-03 | — | No Blender or 3D asset skill. Nearest is `algorithmic-art`. | Nothing to adopt for 3D. |
| Claude Code official marketplace | — | — | — | Of 315 plugins, the 3D-related ones are `unity` (Unity Technologies) and `unreal-engine-skills-for-claude-code` (Epic Games). No Blender, Bevy or Godot plugin. (Local marketplace cache, updated 2026-10-04.) | Nothing for a Bevy project. |
| [natepiano/bevy_brp](https://github.com/natepiano/bevy_brp) | 72 | 2026-09-30 | MIT/Apache per README | MCP server over the Bevy Remote Protocol, plus `bevy_brp_extras` adding screenshot and input methods. `bevy_brp_mcp` 0.22.8 requires `bevy ^0.19.1`. | Current with Bevy. Not used, per the no-MCP decision; BRP itself is reachable with `curl`. |
| [chrisgliddon/bevy-skills](https://github.com/chrisgliddon/bevy-skills) | 16 | 2026-08-25 | MIT | "Unofficial open source AI skills for Bevy". Not read in depth. | Engine-coding knowledge, not asset pipeline. Small and young. |

MCP servers are covered in [section 4.2](#42-mcp-servers-considered-not-used). Bevy tooling is covered in [section 4.5](#45-bevy-the-target-engine).

**Overall**: the ecosystem is broad and young. Most repos are months old. Star counts track novelty, not maturity. Almost all of it is oriented to "make something impressive from a prompt", which is the outcome you are trying to avoid. The pieces that are mature are not skills at all: Blender's CLI and API, the Khronos validator, trimesh and glTF-Transform. On the Bevy side, the first-party pieces (`bevy_gltf`, the headless examples, BRP) are solid but change every release, and Skein is the one bridge tool that is current. I found no published skill for a Blender-to-Bevy asset pipeline.

---

## 9. Recommendation: skills and workflow

Everything in this section is [inference].

### 9.1 Design rules

1. **Scripts gate; prose guides.** Each skill that produces geometry ships a script whose exit code decides pass or fail. A skill with no check is advice.
2. **Small and composable, split by invocation**, as in Pocock's repo. User-invoked skills orchestrate. Model-invoked skills hold one discipline each.
3. **Shared tools, not copies.** The checks live in the project's `tools/` directory, owned by one skill. Other skills call that skill; they do not link across folders.
4. **One vocabulary.** Every skill reads `GLOSSARY.md` and the project conventions before acting.
5. **Vertical slices.** One asset through every gate before the second asset. One check, then the geometry that passes it.

### 9.2 Repository layout

```
kiln/
├── GLOSSARY.md                 # seeded from section 3.3
├── docs/
│   ├── adr/                    # units, facing, naming, collision rule, Bevy version, glTF profile
│   └── research/
├── conventions.toml            # machine-readable project standards
├── Cargo.toml                  # workspace; Bevy pinned to an exact version
├── Cargo.lock                  # committed
├── tools/                      # validate.py, review_render.py, export.py, roundtrip.py, bevy_lint.py
├── tests/                      # pytest over the tools, with known-bad fixture meshes
├── source/<asset>/
│   ├── brief.md                # the grilled brief
│   ├── spec.json               # budget and acceptance numbers
│   ├── refs/                   # reference images, quarantined generated meshes
│   ├── build.py                # the asset, as code
│   ├── review/<phase>/         # contact sheets and reports, committed
│   └── out/                    # .blend (git-lfs or ignored)
├── assets/                     # Bevy's asset folder: exported .glb, manifests, .meta files
├── crates/
│   ├── asset_smoke/            # the headless load test binary
│   └── game_components/        # reflected components shared by the game and Skein
└── imported_assets/            # only if asset processing is enabled; git-ignored
```

The split between `source/` and `assets/` follows Bevy: the engine reads from `assets/` by default ([AssetMode](https://docs.rs/bevy/0.19.1/bevy/asset/enum.AssetMode.html)), so only delivered files belong there.

### 9.3 Proposed skill set

| # | Skill | Invoked by | Trigger description | What it does | Gate |
| --- | --- | --- | --- | --- | --- |
| 1 | `setup-3d-pipeline` | user | Configure this repo for 3D asset work. Run once. | Checks the toolchain and versions, asks target engine and format, writes `conventions.toml`, seeds `GLOSSARY.md`, records ADRs for units, axes and naming. | `tools/doctor.py` exits 0 |
| 2 | `asset-brief` | user | Turn an asset idea into a brief and a spec. | Calls `grilling` and `domain-modeling`. Asks purpose, viewing distance, real dimensions, style, budget, rig and animation needs, references. Writes `brief.md` and `spec.json`. | Spec lint (L0) passes; you confirm |
| 3 | `blender-headless` | model | Use when writing or running any Blender Python script. | Reference skill: the canonical command line, data API over operators, `temp_override`, `--python-exit-code`, version pinning, arguments after `--`. | Script exits non-zero on exception |
| 4 | `asset-checks` | model | Use when adding or changing an acceptance check for a 3D asset, or before modelling begins. | The `tdd` analogue. One check from the spec, proven red on a fixture, then green. Owns `tools/validate.py` and its tests. | The check fails on a known-bad fixture and passes on a known-good one |
| 5 | `review-renders` | model | Use when an asset needs to be looked at: after any geometry, UV or material change. | Fixed cameras and passes, contact sheet, reads images back, writes observations as measurements. | Sheet exists for the phase; observations recorded; optional diff against baseline |
| 6 | `blockout` | model | Use when starting an asset or testing a proportion or layout question. | The `prototype` analogue. Primitives at true scale, throwaway, answers one question. | Bounding dimensions within tolerance; silhouette comparison against reference |
| 7 | `hard-surface-modeling` | model | Use when building final geometry for rigid, man-made objects. | Builds delivery meshes by script or code-CAD, part by part. | L1 mesh checks, tri budget |
| 8 | `uv-and-bake` | model | Use when unwrapping, packing or baking maps. | Seams, unwrap, pack, texel density, optional high-to-low bake. | UV checks pass; checker render reviewed |
| 9 | `pbr-materials` | model | Use when creating or assigning materials and textures. | Principled BSDF only, colour spaces, value ranges, channel packing. | Material lint; material turntable reviewed |
| 10 | `lod-and-collision` | model | Use when an asset needs LODs or physics shapes. | LOD chain; collision meshes or collider components following the project's own rule for Avian. | Per-LOD budgets; shared pivot and bounds; convexity; naming; colliders appear in the Bevy load test |
| 11 | `export-and-roundtrip` | model | Use when exporting an asset or changing export settings. | Export GLB with explicit options to the Bevy profile, write `manifest.json`, validate, lint for Bevy, re-import and compare. | glTF-Validator exits 0; Bevy lint exits 0; round trip matches the manifest (L2, L2b, L3) |
| 12 | `bevy-load-test` | model | Use after export, when an asset misbehaves in Bevy, or when upgrading Bevy. | Owns the `asset_smoke` crate: headless load, manifest assertions, optional screenshot. Also holds the Bevy glTF profile and the upgrade checklist. | L4 exits 0 |
| 13 | `asset-review` | model | Use when reviewing a finished or in-progress asset. | The `code-review` analogue. Two parallel sub-agents: Standards (conventions plus a fixed mesh-smell baseline) and Spec (brief and budget). Neither built the asset. | Report with every finding tied to a measurement or a named render |
| 14 | `diagnosing-asset-defects` | model | Use when an asset looks wrong and the cause is unknown. | The `diagnosing-bugs` analogue: make a render or check that shows the defect, minimise, hypothesise, fix, add a regression check. | The new check is red before the fix and green after |
| 15 | `rig-and-skin` | model | Use when an asset needs a skeleton or weights. | Deform skeleton, weights, extreme-pose sheet. | Weight checks; bone budget; pose sheet reviewed by you |
| 16 | `genai-intake` | model | Use when a generated or downloaded mesh enters the project. | Quarantine in `refs/`, record provenance and licence, measure it, decide reference versus bake source. | Provenance recorded; it cannot reach `out/` unchecked |
| 17 | `modular-kit` | model | Use when building level pieces that must snap together. | Grid, pivots, tiling, piece list, test assembly. | Dimensions are grid multiples; assembled test scene has no gaps |
| 18 | `level-components` | model | Use when a Blender object needs gameplay data: spawn points, triggers, colliders, markers. | Attaches Bevy components to objects through Skein or raw extras; keeps `game_components` and the Blender side in step. | Components are present on the spawned entities in the Bevy load test, or over BRP |

A mesh-smell baseline for skill 13, in the manner of Pocock's fixed Fowler list: unapplied scale, n-gons on curved or deforming surfaces, interior faces, duplicate vertices, long thin triangles, uneven texel density, wasted UV space, mid-range metallic values, pure black or white base colour, more material slots than the spec allows, default names such as `Cube.001`.

### 9.4 Mapping to Pocock's skills

| Pocock skill | 3D counterpart | Adopt, adapt or write |
| --- | --- | --- |
| `grilling`, `grill-me` | Drives `asset-brief` | Adopt unchanged |
| `domain-modeling` | Maintains `GLOSSARY.md` and ADRs for units, axes, naming, format | Adopt unchanged; seed the glossary from section 3.3 |
| `research` | Engine or format questions | Adopt unchanged |
| `to-spec`, `to-tickets` | Brief to spec to per-phase tickets | Adopt unchanged |
| `writing-for-agents` | Writing all of the skills above | Adopt unchanged |
| `retro` | After each asset: which check would have caught what you caught by eye | Adopt unchanged |
| `tdd` | `asset-checks` | Write |
| `prototype` | `blockout` | Write |
| `code-review` | `asset-review` | Write |
| `diagnosing-bugs` | `diagnosing-asset-defects` | Write |
| `implement` | A thin user-invoked `build-asset` that runs the phases in order | Write last, once the phases are stable |
| `codebase-design` | Applies as is to `tools/` and shared build modules | Adopt unchanged |
| none | `review-renders`, `export-and-roundtrip`, `bevy-load-test`, `uv-and-bake`, `pbr-materials`, `lod-and-collision`, `rig-and-skin`, `genai-intake`, `modular-kit`, `level-components` | Write |

**Adopt off the shelf**: Pocock's skills; Blender 5.2 LTS from the command line; glTF-Validator; glTF-Transform for inspection only; trimesh; ImageMagick; Bevy 0.19.1 with `bevy_gltf` and `bevy_remote`; Skein for components; Avian for physics.
**Not used**: any MCP server; Blenvy; FBX; USD.
**Study, do not adopt**: majidmanzarpour/blender-game-skills (gates and scripts), achimala/dream-loop (separate critic).
**Write**: the eighteen skills above.

### 9.5 End-to-end workflow

| Step | Skill | Output | Gate before moving on |
| --- | --- | --- | --- |
| 0 | `setup-3d-pipeline` (once) | Conventions, glossary, ADRs, pinned Bevy workspace | Doctor passes; `asset_smoke` builds |
| 1 | `asset-brief` | `brief.md`, `spec.json` | You approve |
| 2 | `asset-checks` | Checks for this asset's spec | Red against an empty scene |
| 3 | `blockout` + `review-renders` | Primitive version | Dimensions and silhouette pass; **you look at the sheet** |
| 4 | Modelling skill + `review-renders` | Delivery mesh | L1 green; clay and wire sheet reviewed |
| 5 | `uv-and-bake` | UVs, baked maps | UV checks green; checker sheet reviewed |
| 6 | `pbr-materials` | Materials | Material lint green; turntable reviewed |
| 7 | `lod-and-collision` | LODs, collision | Budgets and naming green |
| 8 | `rig-and-skin` (if needed) | Skeleton, weights | Weight checks green; **you look at the pose sheet** |
| 8b | `level-components` (if needed) | Components on objects | Present in extras |
| 9 | `export-and-roundtrip` | GLB in `assets/`, manifest | L2, L2b and L3 green |
| 10 | `bevy-load-test` | Load report, optional Bevy screenshot | L4 green |
| 11 | `asset-review` | Two-axis report | No open findings, or accepted deviations recorded |
| 12 | You, in the running game, with hot reload on | Acceptance | Your call |
| 13 | `retro` | New checks or glossary terms | — |

Human gates are at steps 1, 3, 8 and 12. Step 3 is the cheapest place to catch a wrong asset.

### 9.6 Build order

1. **Glossary and conventions** (`setup-3d-pipeline`). Decide units, facing, naming, the collision rule and the glTF profile. Pin Blender and Bevy versions. Write the ADRs.
2. **Spike the Bevy load test first.** It is the least certain piece: confirm that `DefaultPlugins` with no window and no render backend initialises, loads a GLB and exits with a code. Use any existing GLB. If it does not work as designed, the fallback is a windowed run on your desktop, and you should know that on day one.
3. **The Blender loop**: `blender-headless`, `asset-checks`, `review-renders`. Prove them on a default cube and on deliberately broken fixtures.
4. **`export-and-roundtrip`** with the Bevy lint, joined to **`bevy-load-test`**. Now a cube goes from Python script to a loaded Bevy asset with every gate green. That is the tracer bullet.
5. **`asset-brief`** and **`blockout`**.
6. **`hard-surface-modeling`** on one real prop, a crate or barrel, end to end.
7. **`asset-review`** and **`diagnosing-asset-defects`**, written from the defects step 6 produced.
8. **`uv-and-bake`**, **`pbr-materials`**. Add the optional Bevy screenshot here, since this is where Blender's and Bevy's renderers can disagree.
9. **`lod-and-collision`** with Avian, then **`level-components`** with Skein, then **`modular-kit`**. This is the level-design path.
10. **`rig-and-skin`**, then animation. Last, and with the lowest expectations.
11. **`genai-intake`**, only if you decide to use generated meshes.

At every Bevy upgrade: re-read the `bevy_gltf` support table, update the lint rules, port `asset_smoke`, and re-run every asset through L4.

### 9.7 What agents are good and bad at

This is my assessment from the structure of the tools, not from a benchmark. No primary source quantifies it: **unverified** as fact.

| Good | Why |
| --- | --- |
| Hard-surface and parametric geometry | Describable in numbers and code |
| Procedural generation, scattering, variations | Loops and parameters |
| Pipeline automation, batch export, renaming, LOD chains | Ordinary scripting |
| Validation and reporting | Deterministic and measurable |
| Modular kits on a grid | Dimensional constraints are checkable |
| Material setup from known values | Lookup and wiring |

| Bad | Why |
| --- | --- |
| Organic sculpting | No sculpting feedback loop; form is judged by eye |
| Appealing characters and faces | Appeal is not measurable, and small errors read as wrong |
| Edge flow for deformation | Needs anatomy and animation knowledge; checks only catch gross errors |
| Hand-painted or stylised textures | Art direction |
| Good animation | Timing, weight and anticipation are perceptual. Checks confirm a clip exists and loops, not that it is good |
| Judging its own renders | A builder reviewing its own output is biased, hence the separate reviewer |

Practical consequence: plan to source characters, creatures and animation from a human artist or a purchased asset, and use the pipeline to validate and integrate them. The same gates apply to bought assets.

---

## 10. Learning path for the human

You need enough to judge output, not to produce it. Roughly in order; hours are my estimates [inference].

| # | Learn | Why the agent cannot cover it | How | Time |
| --- | --- | --- | --- | --- |
| 1 | Blender navigation and viewport modes: solid, wireframe, material preview, face orientation overlay | You must be able to open the file and look | [Blender manual](https://docs.blender.org/manual/en/latest/) | 2 h |
| 2 | Model one simple prop by hand, badly | Until you have pushed vertices you cannot read a wireframe | Any beginner tutorial | 4 h |
| 3 | Reading topology: loops, poles, n-gons, density | It is the most common hidden defect, and checks catch only the gross cases | Compare wireframes of professional and generated meshes | 3 h |
| 4 | Normals and shading: smooth versus flat, hard edges, why a face is dark | Shading bugs are visible, not numeric | Toggle the overlays on a broken mesh | 2 h |
| 5 | UVs: unwrap one object, look at a checker texture, see stretching | You must recognise a bad unwrap on a contact sheet | Do it once by hand | 3 h |
| 6 | PBR intuition: what roughness and metallic look like across their range | Material plausibility is a visual call | Build a grid of spheres | 2 h |
| 7 | Scale and silhouette: judge an asset at gameplay distance, next to a human-sized reference | This is where taste starts | Always review beside a 1.8 m reference | ongoing |
| 8 | Seeing an asset in Bevy: run the `load_gltf` example on your own GLB, with hot reload, and inspect entities over BRP | Bevy has no editor or import inspector; the running game is the only view that counts | [Bevy glTF examples](https://github.com/bevyengine/bevy/tree/v0.19.1/examples/gltf) | 3 h |
| 9 | Deformation, if you do characters: bend an elbow, watch it collapse | You cannot assess a rig otherwise | Rig a cylinder with two bones | 3 h |
| 10 | Animation principles: timing, weight, anticipation | No check exists | Study, and watch reference footage | long |

Items 1 to 8 are about twenty hours and are the minimum for the workflow in section 9 to be safe. Without them you will approve contact sheets you cannot read.

---

## 11. Unverified items

**Bevy**

| Item | Status |
| --- | --- |
| The smoke-test design: `DefaultPlugins` with `WinitPlugin` disabled, no primary window and `backends: None` together | Assembled from two separate official examples; never compiled or run |
| Whether a full glTF load works under `MinimalPlugins` plus asset plugins only | Not investigated; the design uses `DefaultPlugins` to avoid the question |
| Bevy screenshots or headless rendering on a software adapter with no GPU | Not documented in what I read |
| One Bevy unit equals one metre | No Bevy doc found stating it |
| That glTF is Bevy's only first-party model format | Based on the cargo feature list; not an explicit statement |
| Which older release each bevy.org/news date belongs to | My reading of the index |
| What built-in LOD support Bevy 0.19 has | Not researched |
| Whether Skein's registry fetch and component assignment can be driven from `blender --background` | Not documented in the README; the documented flow uses Blender operators in the UI |
| Whether Avian's `ColliderConstructor` round-trips through Skein | Not checked |
| `bevy_rapier`'s scene-collider API | Not read |
| Skein's licence | GitHub reports none detected; file not read |
| jackdaw and the community Bevy skills | Metadata only; not read |
| What changes in Bevy 0.20 for glTF loading | Release candidate notes not read |
| Running time of the smoke test and Bevy compile time on this machine | Not measured |

**Blender command line**

| Item | Status |
| --- | --- |
| Whether `sys.exit(n)` in a `--python` script sets the process exit code | Not stated in the docs read |
| Which output goes to stdout and which to stderr | Not specified in the docs read |
| Workbench engine: GPU requirement, and its engine identifier | Manual page failed to load; use `blender -E help` |
| EEVEE through a software rasteriser | Manual says EEVEE is GPU-only with no CPU rendering planned; software GL or Vulkan not addressed |
| Bit-identical renders across machines or versions | Not documented either way |
| That Blender has no server or daemon mode | Absence from the argument list only |
| Where `register_cli_command` must be called from | The API is documented; the add-on requirement is my inference |
| Blender startup time | Not measured |

**Carried over**

| Item | Status |
| --- | --- |
| Unreal units are centimetres; Unreal glTF import through Interchange | Not on the pages fetched |
| Unity coordinate system, unit scale, `-runTests`, glTF support | Not fetched |
| All Epic, Unity and Meshy quotations, and the VRChat table except the PC triangle row | Read through a summarising fetch, not raw text |
| Tripo: quad output, its format restriction, `smart_low_poly`, licence terms | Only a search snippet; docs site is client-rendered |
| Hyper3D Rodin: all parameters and licence | Docs unreachable |
| Stable Fast 3D licence terms | Repo reports no SPDX licence; file not read |
| FBX has no public specification | Only Godot's "proprietary FBX SDK" wording found |
| Typical triangle budgets, texel density targets, UV padding values | Convention only; no primary source mandates numbers |
| Blender Rigify manual page | URL returned 404 |
| The agent strengths and weaknesses in section 9.7 | My assessment; no benchmark found |
| Whether any of the third-party skills or tools work as described | None were installed or run |
| Every command line and code design in this document | Taken from docs and source; nothing was executed |

---

## 12. Open questions and decisions for you

**Decided**

- Target engine: **Bevy**.
- Blender driver: **command line only, no MCP**.
- Delivery format, as a consequence: **GLB to a Bevy-compatible glTF profile**.

**Still open**

1. **Bevy version policy.** Pin 0.19.1 now, or start on 0.20 when it lands (rc.2 is dated 2026-09-28)? Starting on 0.19.1 means one port soon. Waiting means Skein and Avian must release for 0.20 first; Skein already has a 0.7.0 release candidate.
2. **Physics crate.** Avian or bevy_rapier. It decides the collider workflow. The recommendation assumes Avian because its per-name and from-mesh collider constructors are documented and I read them; bevy_rapier's equivalent was not read.
3. **Collision convention.** Named collision meshes matched in Rust, or collider components attached in Blender through Skein. Bevy imposes neither.
4. **Facing convention.** Model assets facing glTF-forward (+Z) and convert with the experimental loader option, or model them facing Bevy-forward (−Z) and convert nothing. Decide once; it affects every character and vehicle.
5. **Skein, or raw glTF extras?** Skein is current and saves parsing code, but adds a Blender extension and a dependency that must track Bevy. Raw `GltfExtras` is first-party and you write the mapping. Also: is a UI step in Blender acceptable for fetching the type registry, if it cannot be scripted?
6. **Is the level editor Blender, or do you want to evaluate jackdaw?** The recommendation is Blender plus Skein.
7. **In-engine screenshots: required gate or optional check?** They need a GPU on whatever machine runs the gate.
8. **Asset processing.** Start `Unprocessed` (recommended), or adopt Bevy's asset processor and `.meta` files from the start for texture compression.
9. **First asset class.** The recommendation starts with static hard-surface props and modular kits. If you need characters first, you will need a human artist or purchased base meshes.
10. **Art style.** Stylised low-poly is far more tractable for an agent than realistic PBR. It also keeps you inside the material features Bevy loads.
11. **Budgets.** Triangle counts, texture sizes, material slots and texel density per asset class. There is no standard to copy; set them in `conventions.toml`.
12. **Assets as code, or `.blend` as master?** The recommendation is build scripts as the source of truth. For levels this is the hard case: a level is naturally hand-placed. A hybrid, where kit pieces are scripted and the level `.blend` that instances them is hand-edited and only checked and exported by script, is probably right.
13. **Blender install.** Arch `extra` has 5.2.1; upstream is 5.2.2. An official tarball is easier to pin than a rolling package. Skein's add-on 0.1.16 requires Blender 5.2 or later.
14. **Render engine for review sheets.** EEVEE on your GPU for speed, or Cycles on CPU for portability. Both, with Cycles as the reference, is the recommendation.
15. **`--python` scripts, or registered `--command` subcommands?** Start with scripts.
16. **`bpy` as a Python module for fast tests?** It needs Python 3.13 and you have 3.14.7. Use `uv` with 3.13, or always shell out to the binary.
17. **Generated meshes: allowed at all?** If yes, which vendors, given Meshy's free-tier CC BY 4.0, Hunyuan3D's exclusion of the EU, UK and South Korea, and the unverified terms of the others.
18. **Binary storage.** The directory is not a git repo. Decide on git plus LFS for `.blend`, textures and GLB, or keep build outputs untracked and rebuildable. Note that `assets/*.glb` is what the game ships, so it probably should be tracked.
19. **Glossary filename.** `GLOSSARY.md` (upstream now) or `CONTEXT.md` (what your installed plugin's description says).
20. **How much of section 10 will you do?** The workflow's human gates assume items 1 to 8.
21. **Skill packaging.** Project-local `.claude/skills/` in this repo, or a personal plugin you reuse across projects.

---

## 13. Sources

**Pocock skills**
- https://github.com/mattpocock/skills (README, `.claude-plugin/plugin.json`, `.agents/invocation.md`, `GLOSSARY.md`, and the `SKILL.md` files for tdd, domain-modeling, prototype, grilling, research, grill-with-docs, implement, code-review, writing-for-agents)

**Blender**
- https://www.blender.org/download/ · https://www.blender.org/download/releases/5-2/ · https://download.blender.org/release/Blender5.2/
- https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
- https://docs.blender.org/api/current/index.html
- https://docs.blender.org/api/current/info_advanced_blender_as_bpy.html
- https://docs.blender.org/api/current/info_gotchas_operators.html
- https://docs.blender.org/api/current/bmesh.types.html
- https://docs.blender.org/api/current/bpy.types.Mesh.html · https://docs.blender.org/api/current/bpy.types.Context.html · https://docs.blender.org/api/current/bpy.types.GeometryNodeTree.html · https://docs.blender.org/api/current/bpy.types.RenderSettings.html
- https://docs.blender.org/api/current/bpy.ops.uv.html · https://docs.blender.org/api/current/bpy.ops.object.html
- https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- https://docs.blender.org/manual/en/latest/files/import_export/fbx.html · https://docs.blender.org/manual/en/latest/files/import_export/fbx_legacy.html
- https://docs.blender.org/manual/en/latest/files/import_export/usd.html
- https://developer.blender.org/docs/release_notes/3.4/eevee/
- https://extensions.blender.org/add-ons/print3d-toolbox/
- https://pypi.org/project/bpy/
- https://www.blender.org/lab/mcp-server/ · https://projects.blender.org/lab/blender_mcp (README, `readme_tools.rst`, releases, LICENSE)
- https://github.com/ahujasid/mcp-for-blender

**Specs and validators**
- https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html · https://www.khronos.org/gltf/
- https://github.com/KhronosGroup/glTF-Validator · https://www.npmjs.com/package/gltf-validator
- https://github.com/KhronosGroup/3DC-Asset-Creation
- https://openusd.org/release/toolset.html
- https://openusd.org/release/api/group___usd_geom_up_axis__group.html · https://openusd.org/release/api/group___usd_geom_linear_units__group.html
- https://github.com/PixarAnimationStudios/OpenUSD/releases · https://aousd.org/

**Bevy and its ecosystem**
- https://github.com/bevyengine/bevy/releases · https://bevy.org/news/ · https://bevy.org/news/bevy-0-19/ · https://bevy.org/learn/quick-start/getting-started/setup/
- https://docs.rs/bevy_gltf/0.19.1/bevy_gltf/ (crate page, `GltfLoaderSettings`, `convert_coordinates::GltfConvertCoordinates`, `MAX_JOINTS`)
- https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_gltf/src/loader/mod.rs
- https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_camera/src/components.rs
- https://github.com/bevyengine/bevy/tree/v0.19.1/examples/app (`headless.rs`, `no_renderer.rs`, `headless_renderer.rs`, `externally_driven_headless_renderer.rs`) · https://github.com/bevyengine/bevy/tree/v0.19.1/examples/gltf · https://github.com/bevyengine/bevy/tree/v0.19.1/examples/asset
- https://github.com/bevyengine/bevy/blob/v0.19.1/docs/cargo_features.md
- https://github.com/bevyengine/bevy/blob/v0.19.1/crates/bevy_dev_tools/src/ci_testing/mod.rs
- https://docs.rs/bevy/0.19.1/bevy/app/enum.AppExit.html · https://docs.rs/bevy/0.19.1/bevy/asset/enum.RecursiveDependencyLoadState.html · https://docs.rs/bevy/0.19.1/bevy/asset/enum.AssetMode.html · https://docs.rs/bevy/0.19.1/bevy/asset/processor/index.html · https://docs.rs/bevy/0.19.1/bevy/render/view/window/screenshot/struct.Screenshot.html
- https://docs.rs/bevy_remote/0.19.1/bevy_remote/ · https://docs.rs/bevy_remote/0.19.1/bevy_remote/http/index.html
- https://github.com/bevyengine/bevy_editor_prototypes · https://github.com/jbuehler23/jackdaw
- https://github.com/rust-adventure/skein · https://crates.io/crates/bevy_skein · https://github.com/kaosat-dev/Blenvy · https://crates.io/crates/blenvy
- https://github.com/avianphysics/avian · https://crates.io/crates/avian3d · https://docs.rs/avian3d/0.7.0/avian3d/collision/collider/struct.ColliderConstructorHierarchy.html · https://docs.rs/avian3d/0.7.0/avian3d/collision/collider/enum.ColliderConstructor.html
- https://github.com/dimforge/bevy_rapier · https://crates.io/crates/bevy_rapier3d
- https://github.com/natepiano/bevy_brp · https://crates.io/crates/bevy_brp_mcp · https://github.com/chrisgliddon/bevy-skills

**Blender command line, added for this revision**
- https://docs.blender.org/api/current/bpy.utils.html (`register_cli_command`)
- https://docs.blender.org/api/current/bpy.ops.export_scene.html
- https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html
- https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html
- https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html

**Other engines (comparison only)**
- Godot: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html · …/node_type_customization.html · …/import_configuration.html · …/model_export_considerations.html · https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html · https://docs.godotengine.org/en/stable/tutorials/3d/introduction_to_3d.html · https://github.com/godotengine/godot/releases
- Unreal: https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python · …/coordinate-system-and-spaces-in-unreal-engine · …/fbx-content-pipeline · …/fbx-static-mesh-pipeline-in-unreal-engine · …/physically-based-materials-in-unreal-engine · https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor · https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin
- Unity: https://docs.unity3d.com/Manual/EditorCommandLineArguments.html · https://docs.unity3d.com/Manual/3D-formats.html · https://docs.unity3d.com/Manual/FBXImporter-Model.html · https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli · https://github.com/Unity-Technologies/unity-agent-plugin
- VRChat: https://creators.vrchat.com/avatars/avatar-performance-ranking-system/

**Libraries and tools**
- https://github.com/mikedh/trimesh · https://trimesh.org/trimesh.base.html
- https://github.com/donmccurdy/glTF-Transform · https://gltf-transform.dev/cli
- https://github.com/zeux/meshoptimizer · https://github.com/elalish/manifold
- https://f3d.app/docs/next/user/OPTIONS · https://github.com/f3d-app/f3d
- https://openscad.org/downloads.html · https://github.com/openscad/openscad
- https://github.com/CadQuery/cadquery · https://pypi.org/project/cadquery/
- https://github.com/gumyr/build123d · https://build123d.readthedocs.io/en/latest/import_export.html

**Generative 3D**
- https://docs.meshy.ai/en/api/image-to-3d · https://docs.meshy.ai/en/api/rigging-and-animation · https://help.meshy.ai/en/articles/9992001-can-i-use-the-assets-generated-on-meshy-for-commercial-purposes
- https://github.com/VAST-AI-Research/tripo-python-sdk/blob/master/docs/API.md · https://github.com/VAST-AI-Research/TripoSR
- https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1 (README, LICENSE)
- https://github.com/microsoft/TRELLIS.2
- https://github.com/Stability-AI/stable-fast-3d

**Existing skills and MCP servers**
- https://github.com/majidmanzarpour/blender-game-skills · https://github.com/RobLe3/cc-blender-skill · https://github.com/arjun988/blender-skills · https://github.com/MAX-786/claude-3d-harness · https://github.com/achimala/dream-loop · https://github.com/flowful-ai/cad-skill · https://github.com/scenario-labs/skills · https://github.com/anthropics/skills
- https://github.com/hi-godot/godot-ai · https://github.com/Coding-Solo/godot-mcp · https://github.com/CoplayDev/unity-mcp · https://github.com/ChiR24/Unreal_mcp

**Local, read-only**
- `command -v` for the tools listed in section 1, including `cargo` and `rustc --version`; `pacman -Si blender godot openscad f3d`; `compare -list metric`; the Claude Code official marketplace cache at `~/.claude/plugins/marketplaces/claude-plugins-official`.
