# Glossary

The shared vocabulary for this repo. Use these terms, with these meanings, in briefs, specs, skills and reviews. Seeded from [the research notes](docs/research/3d-asset-agent-workflow.md); project decisions are in [docs/adr](docs/adr/).

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
- **Up axis, forward axis, handedness**: the coordinate convention. They differ per tool. Ours is in [ADR 0001](docs/adr/0001-units-axes-facing.md); background in [section 6](docs/research/3d-asset-agent-workflow.md#6-interchange-formats).
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

**Pipeline**

- **Asset**: one deliverable thing, made from a brief, a spec and a build script, and shipped as one GLB. _Avoid_: model, object (an object is one Blender object inside an asset).
- **Brief**: the words that say what an asset is, what it is for, and the decisions behind it.
- **Spec**: the brief's numbers, in a form the checks read. _Avoid_: config, requirements.
- **Build script**: the code that constructs an asset's geometry and materials from nothing.
- **Check**: one measurement of an asset compared with one value from the spec or the conventions, with a stable id. _Avoid_: test (a test proves a check can fail), rule.
- **Gate**: a script that runs checks and decides, by exit code, whether the asset moves on. _Avoid_: layer, stage.
- **Mutation**: a deliberate way of breaking a known-good asset, used to prove that a check goes red.
- **Escaped defect**: something wrong with an asset that every gate passed.
- **Manifest**: what the engine must see when it loads an asset, written at export.
- **Profile**: the subset of glTF that the pinned Bevy version can load.
- **Contact sheet**: one image of an asset from the fixed review cameras and passes. _Avoid_: screenshot, preview.
- **Pass**: one way of rendering every review view, such as material or clay with wireframe.
- **Phase**: the point in an asset's life that a contact sheet records, such as blockout or final.
- **Value**: how light or dark a colour is, with hue set aside. **Value map**: a render reduced to a few greys, to show its big light and dark masses.
- **Squint view**: a render blurred until detail is gone, to show how it reads at a glance.
- **Blind comparison**: two renders shown side by side in a random order with the labels hidden, so the judge cannot favour the one they expect to be better.
- **Observation**: a statement about a contact sheet that a second reader could confirm or refute from the same tile. _Avoid_: verdict.
- **Fixture**: an asset that exists to exercise the pipeline, such as the tracer. It is never shipped in a game.
- **Margin**: how far a face's edges sit in from the sides of the asset's bounding box, measured in the face's own plane. A crate's frame width is its panels' margin.
- **Painted shading**: colour variation computed from an asset's shape and baked into it: a base-to-top gradient, light along exposed edges, shadow in crevices. Ours is baked into one texture per asset (ADR 10). _Avoid_: baked lighting (no light is involved), vertex paint.
- **Tint**: a colour the material colour is multiplied by. White leaves it as it is. The gradient of painted shading runs from a base tint at the ground to a top tint at the top of the bounds.
- **Edge light**: the part of painted shading that lightens exposed (outward, convex) edges. **Crevice shadow**: the part that darkens inside corners.
- **Growth**: moss, lichen or the like, painted from the ground up to a height, and in patches on faces near level and along upper edges. At the base it is at the material's own lightness, so it changes hue and not value; a spec may make the patches darker than the surface round them (`growth_darker`) and set their size (`growth_patch_m`), and says how far in from an edge the growth along it reaches (`growth_edge_m`).
- **Side shade**: the part of painted shading that darkens upright faces at mid height. **Blotch**: a broad, soft-edged patch of lighter or darker tone within a plane; blotches lighten as much as they darken.
- **Grain**: the part of painted shading that runs in streaks along a limb: fine streaks, **plates** of differing tone, dark **furrows** between them with a lighter **ridge** beside each, and a few knots (ADR 12). _Avoid_: noise, wood texture.
- **Close texels**: the texel density a surface gets below the height at which a player stands against it.
- **Banding**: a smooth gradient shown as flat steps. In a texture it is too few levels; in a review image it is a viewer reducing a file deeper than 8 bits per channel to a palette.
- **Open face**: surface far enough from every edge and inside corner that only the material colour and the tint reach it. The checks measure colour there.
- **Hidden underside**: faces lying on the floor of the bounds and facing down, which nobody sees; they get almost none of the texture and are not measured.
- **Leaf card**: a small flat piece of geometry showing a painted cluster of leaves with transparent gaps, as the benchmark tree builds its foliage. Not used here: our foliage is leaf pieces (ADR 9). _Avoid_: billboard (a card that turns to face the camera), leaf plane.
- **Leaf piece**: one flat, pointed, notched piece of foliage geometry in a single colour, large enough to read as a leaf; the unit foliage is built from. The checks find a piece as a connected set of faces of the foliage material with an open edge. _Avoid_: leaf card, leaf plane, confetti (pieces too small to read).
- **Core**: a closed, dark, low-triangle solid of the foliage material inside a pad, under its leaf pieces; it gives the pad depth and closes the view up into it from below (ADR 9). The checks find a core as a connected set of faces of the foliage material with no open edge. _Avoid_: blob, hull, solid foliage (a solid on its own is never foliage).
- **Lobe**: one of the two to four overlapping rounded masses a pad is built from, each with its own core. **Skirt**: the leaf pieces that hang from a lobe's rim and under it, pointing out and down.
- **Pad**: a separate clump of leaf pieces and their cores with clear air round it; a canopy is several. The checks find a pad as pieces and cores with no gap of `pad_gap_m` between them. _Avoid_: clump, blob, crown (the whole canopy, or the highest pad).
- **Seen into**: looking straight up at a pad, the share of its outline where the eye passes its underside and meets the inside of the pad, or sky through a gap.
- **Rim point**: the point of a leaf piece that, seen from straight below, has sky just past it and on either side.
- **Sky share**: seen from one direction, the part of a canopy's outline (the convex hull of its foliage) through which nothing is hit. A single mass of foliage has little; a ball has none.
- **Branch skeleton**: the trunk and branches of a tree as connected tapering tubes, before foliage is added. **Limb**: any one of those tubes.
- **Slice**: bark cut by a level plane, which gives one closed loop per limb the plane passes through. A tree's girth, flat sides, fork, taper, roots and lean are all read from slices.
- **Fork**: the lowest height at which a slice shows two limbs. **Breast height**: 1.3 m above the ground, where a trunk's girth is taken.
- **Flare**: how far the trunk reaches out at the ground, over its radius at breast height. A **root** is a corner of the ground slice that stands well out from the rest.
- **Palette**: the colours foliage may take, as a strip of swatches along the top of an asset's painted texture. A **swatch** is one square of flat colour; all of a leaf piece's UVs sit on the middle of one (ADR 11). **Shade**: a step of the palette from the underside of a pad to its top. **Tone**: one of the lighter or darker versions of a shade, so that neighbouring pieces differ.
- **Blade**: one long leaf as a single open piece of foliage geometry: a strip that tapers to a point, bends along its length and may be folded along its middle. Foliage is either leaf pieces in pads or blades from one point; a spec with a `blades` block is the second, and has no pads, lobes or cores. A blade's **foot** is its corner nearest the origin on the ground and its **tip** the sharpest corner of its outline. _Avoid_: frond (a leaf cut into leaflets, which nothing here is yet), leaf piece (flat and notched).
- **Rosette**: blades growing from one point in every direction. **Lean**: how far from upright the straight line from a blade's foot to its tip is. **Arch**: how far a blade stands off that line, as a share of its length.
- **Rootstock**: the low closed mound at the origin that a rosette grows out of; the closed surface of a plant of blades. _Avoid_: crown (the slice of a rock, and a tree's canopy).
- **Stem**: one of the short woody tubes a bush stands on; the closed surface of a bush. _Avoid_: trunk, limb (a tree's).
- **Open material**: a material whose faces are separate open pieces by design, such as leaf pieces. The closed-surface checks are asked of an asset's other materials.
- **Seam**: also, here, an edge a build script marks to say where a surface may be cut to lie flat; `tools/paint.py` unwraps along seams when a mesh has any.
- **Variant**: one of several assets drawn by the same generator from different seeds, each an asset in its own right. A **family** is the folder holding the generator and the brief they share. _Avoid_: LOD.
- **Species**: a recipe the tree generator reads (`source/tree/species/<name>.toml`): how the trunk forks, where the pads sit, the leaf shape. A spec names one. _Avoid_: tree type, kind.
- **Growth stage**: how grown a tree is, as a number in its spec: its height over a mature tree's, so 1.0 is mature. The recipe says how girth, fork, pad count and pad width follow it. _Avoid_: age, size, LOD.
- **Season**: summer, autumn or winter, as a palette on a tree's mesh. A **palette variant** is an asset whose spec names the asset it is a `palette_of`: the same mesh, UVs included, with another texture. It is a variant in its season or in its cover, and its spec differs from its base's only in what that kind may change. _Avoid_: colour variant, skin.
- **Cover**: what lies on a stone: `bare`, or `mossy` (growth painted on it, ADR 10). A mossy stone is a palette variant of the bare one, named `<base>_mossy`, whose spec differs from its base's only in its `cover` and the growth keys of `painted_shading`. An asset that names no cover and has no growth is bare. _Avoid_: overgrown, weathered (as names for it).
- **Outline difference**: between two variants, the share of what either covers, seen from a level direction, that only one of them covers.
- **Benchmark**: a professional asset run through the gates and viewer to compare ours against. It is never shipped.
- **Plane**: a connected set of faces that lie in one flat surface, however they are triangulated. A **large plane** is one at or above the area a spec's `planes.large_m2` gives. _Avoid_: facet (a plane too small to be deliberate), face (one polygon of the mesh).
- **Plane cut**: slicing a solid with one flat cut and capping the hole; how rock is shaped (ADR 9). A **notch** is two cuts that meet, removing only what is in front of both.
- **Ledge**: an inward (concave) corner between two large planes: a shelf and the wall behind it. Where a spec says so (`planes.ledge_plane_m2`), one of the two may be smaller: the corner between a wall and a piece set against it. _Avoid_: step (also a stair), crevice.
- **Soft edge**: an edge lit as if rounded, because the faces either side share normals across it. Ours is a narrow bevel strip whose normals blend from one plane to the next. The opposite of a hard edge.
- **Step, fracture, shoulder**: the three forms cut into a rock, each a ledge. A step is a raised slab above a lower shelf on top; a fracture is a V-shaped groove down a side; a shoulder is a bench part of the way up a side. _Avoid_: step for a stair.
- **Fullness**: how much of its bounding box a closed shape fills, as a share of the box's volume. **Crown**: the level slice through a shape three quarters of the way up its bounds, as a share of the bounds' footprint; it tells a boulder (broad high up) from a wedge.
- **Outline**: what a shape covers when seen from one direction with parallel rays. A plane's **view share** is the part of the outline it fills from that direction.
- **Recess**: how far a face sits below the asset's bounding box, measured along the face's normal.
- **Piece**: one of the solids a shape is pushed together from, each cut from a block by planes. Pieces are either fused into one closed skin (the boulder) or left as **overlapping pieces** (ADR 13). The **dominant piece** is the largest; **secondary pieces** are set against it. A piece's size is the surface it shows in the finished mesh, not its volume, because part of each is buried. _Avoid_: part (a separately moving object), chunk.
- **Piece record**: what a build script says a shape's pieces are, saved beside the mesh for the gate to hold against it. Never taken on trust: a piece counts only by the surface the mesh shows of it.
- **Overlapping pieces**: closed pieces left separate in one mesh, each softened on its own and passing into its neighbours (ADR 13). A spec says so with an `overlap` block; the checks then read the pieces back from the mesh as its connected closed parts, with no piece record. _Avoid_: fused, merged (a union into one skin), part.
- **Buried surface**: the part of a piece's surface that lies inside another piece, where it costs triangles and texture and is never seen. A point is buried when the space just in front of it is inside another piece. The **buried share** is buried surface over all surface.
- **Join**: where one piece passes into another. Two pieces are **joined** when enough of the smaller one's surface is buried in the other (`[overlap]` in `conventions.toml`); a piece joined to nothing **floats**. Painted crevice shadow darkens a join.
- **Size order**: the pieces of a shape ranked by size, each clearly larger than the next; two of nearly one size are **twins**.
- **Foot**: low, near-level surface that nothing stands over, reaching out past a shape's main mass, so the shape looks settled into the ground and not placed on it.
- **Chamfer**: a plane that cuts off a corner or a rim, of a middle size: smaller than a large plane, and wide enough to be lit as a face of its own. _Avoid_: bevel (the narrow strip of a soft edge).
- **Upright**: within a few degrees of vertical (`[lean]` in `conventions.toml`). A shape's **upright share** is how much of its side surface is upright.
- **Summit**: the part of a shape above nine tenths of its height. It is **off-centre** by how far its middle is from the middle of the bounds.
- **Neck**: a narrow piece that stands on the ground and holds a table rock's plate off it. **Clearance**: the open air under that plate, from the ground up; the part of the outline that has the clearance a spec asks is **sheltered**. **Overhang**: how far in from the rim of the outline, seen from above, the necks stand. _Avoid_: pillar, leg, stem (a bush's).
- **Pier**: one of the two stacks of blocks an arch stands on, each reaching the ground. **Span**: what bridges them: one rough slab lying aslant (the lintel kind), or a knot of leaning blocks and a keystone. A **trilithon** is what an arch must not be: two matched upright piers of squared blocks under a level squared lintel. **Opening**: the open air right through an arch, seen from the front, from the ground up; its width is taken where it is open up to the height a spec asks. The span **rests** on a pier where rock runs without a break from the ground up into the span. _Avoid_: neck (a table rock's), cap, doorway.
- **Log**: a trunk lying on the ground, along x. Its **butt** is the thick end, where it grew from the ground (−x): sawn, broken, or torn out with its roots (a **root plate**); its **top** is the end where the crown broke off (+x), always broken. A **stub** is a branch broken off short. _Avoid_: trunk for the whole asset (a tree's), stump (what stays in the ground).
- **Station**: a log's trunk cut by an upright plane across its length, which gives its outline there and the outline of its hollow. A log's thickness, taper, bend, hollow and wall are read from stations, as a tree's are from slices.
- **Settled**: sunk a little into the ground and flat on it there, measured as the width a station lies flat on the ground over its whole width. **Pressed**: how the generator does it, bringing a ring's lowest corners down onto the ground.
- **Hollow**: open air inside a log's trunk, with a **wall** of wood between it and the outside. The wall has thickness: the trunk stays one closed surface, its inside facing into the hollow. Its **clear** size is the lesser of how far it is open across and up. _Avoid_: open material (leaf pieces: an open surface with no thickness).

**Game**

- **Pit**: the vertical world the game takes place in, in place of an island. _Avoid_: abyss (the source of inspiration, not our name), map.
- **Layer**: one depth band of the pit, with its own biome, look, and balance of risk and reward. A player can live out a whole life on any layer. _Avoid_: level (already means a playable map, and level of detail), floor, zone.
- **Descent**: moving down to a deeper layer; risk and reward both rise.
- **Ascent**: moving up toward the rim; it triggers the curse.
- **Curse**: the harm a player takes while ascending, worse the deeper the ascent starts.
- **Life**: one character's persistent existence, from spawn to death, including what they build and keep.
