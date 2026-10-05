# 12. Bark grain is painted into the one texture, with more texels where a player stands

At 0.5 m the first trees' bark was flat brown planes: its painted shading (a gradient, light on corners, shadow at junctions, broad blotches) has nothing in it finer than a few centimetres, and the benchmark's textured, normal-mapped bark was clearly better there. Players stand against trunks constantly (ADR 7).

What is done, inside ADR 10's idea (computed from the shape and baked into the asset's one texture, by script, the same every build):

- **Grain** is a spec option of painted shading (`grain`, `grain_width_m`). It is tone that runs in streaks along a limb: fine streaks, plates of bark a few grain widths across that differ in tone, dark furrows that wander between the plates with a lighter lip beside them, and a few knots. A build script says which way "along" is with a face-corner attribute named `grain` (metres across the grain, metres along it, a number per limb); `tools/paint.py` reads it. The attribute stays in the `.blend` and is not exported.
- **Close texels** are a second option (`close_height_m`, `close_texels_per_m`). Islands that reach below that height are enlarged before packing until their sparsest face has that many texels per metre; the rest of the surface gives up room and keeps the conventions' least. The tree asks for 250 per metre for everything that reaches below 2.5 m (the trunk to its fork, the roots and the feet of the lowest branches), two and a half times the least; a 1024 px texture runs out just under 300.
- The gates measure the grain where it matters: on the upright faces below `close_height_m`, in hand-sized patches, as the tone step across the grain and that step over the step along it (`crates/asset_smoke/src/grain.rs`), and again in a Bevy view from 0.5 m (`tools/view_checks.py`), where the thresholds come from the benchmark tree seen from the same camera.
- An asset with grain does not also ask for blotches. The plates of bark are its broad variation, and ADR 10's blotch checks (tone spread within bounds, no fine grain) would measure the grain and fail by design. The tree's spec drops `blotch`; the grain checks take its place. The mean tone is kept: `painted.colour` still holds open faces to the material colour times the tint.

What was tried, in Bevy from 0.5 m and 3 m (`benchmarks/out/tree_bark_study.png`):

- **Grain at 1024 px, 250 to 300 texels per metre on the trunk.** Reads as furrowed bark at both distances, softer than the benchmark's at 0.5 m. Chosen.
- **The same at 2048 px, 600 per metre.** No difference that can be seen: the pattern has nothing finer than a 1024 px texture already shows. The file goes from about 1 MB to 2.9 MB. Not used.
- **A tangent-space normal map from the same furrows** (a prototype: the furrow pattern baked as a height and differenced). Where the sun reaches the trunk the bark gains real relief and is clearly better than paint alone; in the canopy's shade, where a trunk mostly is, it adds nothing, because the viewer's ambient light has no direction. It costs a second 1024 px texture (the file goes from about 1 MB to 2.5 MB), tangents on every vertex, and a second texture class in the profile, the lint and the load test. Not used; it is the owner's to decide whether sunlit trunks are worth it.
- **Ridged or fluted trunk geometry.** Not tried: the trunk's five to eight flat sides are part of the brief, and ridges fine enough to read as bark would cost more triangles than the canopy.

Costs accepted: a variant's file goes from about 0.68 MB to 1.0 to 1.1 MB, because grain compresses worse than flat tone; the paint step gains about two seconds; limbs above 2.5 m have fewer texels than before (still above the conventions' least); and a build script that wants grain must supply the attribute.

Not decided here: normal maps (above), and grain on anything but bark.
