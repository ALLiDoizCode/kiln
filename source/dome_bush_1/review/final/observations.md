# dome_bush_1, final: observations

From `sheet.png`, its tiles, the aids (`bevy_aids.png`, `material_three_quarter_aids.png`) and `benchmarks/out/dome_bush_variants.png`. Numbers not read off a tile are the gate's (`out/reports/`).

1. **Silhouette.** front, right, back: one dome with a serrated edge, tips standing out all round and along the ground; no flat or straight stretch of outline. The 2 lobes do not read as separate lumps from any level view: the outline is one arc, a little higher on one side. top: a round outline with points all round (about 6 per metre, gate), not lobed.
2. **Proportions.** front: about 1.45 times as wide as tall (brief: at least 1.2; gate 1.42). Pieces are 0.28 to 0.45 m long (brief 0.2 to 0.5), about a quarter of the dome's width each. Sky is 0.13 to 0.17 of the outline from the six directions (brief 0.03 to 0.3).
3. **Facing and grounding.** The bush has no front. front, right, back: the lowest pieces lie on the bottom edge of the frame; the stems show as two to four dark uprights under the lowest pieces in front, right and back, about a tenth of the height.
4. **Topology.** clay_wire: every piece is four triangles; the wire is evenly dense over the dome and nothing is denser than the outline it carries. 944 triangles (budget 1,500), 194 pieces.
5. **Shading.** material tiles: no piece is black or lit from behind. Dark triangles between pieces are the cores (0.04 to 0.06 of the foliage seen from the sides, limit 0.1); they read as depth, most in the right and back tiles below mid height.
6. **Materials.** Pieces run from light yellow-green on top to a darker, bluer green by the ground in every level tile; the stems are dark brown. 24 colours, all on the palette (gate).
7. **Scale.** scale: the bush is about 0.61 of the figure's height (brief 1.1 m of 1.8 m).
8. **In the engine.** bevy: paler and more yellow than the Blender tiles, and the lower pieces are less dark: the height gradient is weaker under Bevy's ambient light. Dark gaps show as in Blender.
9. **Values.** bevy value map: the bush is one light grey mass with dark specks in the gaps and one darker band at the ground; the top-to-bottom gradient does not reach a second grey level. The benchmark's bush shows two levels (lit clusters over a dark inside).
10. **At a glance.** bevy squint: "round green bush"; the eye lands on the lit top. The benchmark's reads "ragged dark bush" (it is drawn red in this viewer: see below).
11. **Differences from the brief.**
   - Silhouette 2 says "lumpy, not a ball": the lobes are there (widest core 1.56 to 1.65 times the narrowest across the variants) but the outline reads as one smooth dome. Nothing measures lumpiness of the outline.
   - From 0.5 m and 1 m looking down (`dome_bush_variants.png`, last two columns) the top of the dome is nearly one tone: all the top pieces take the highest shades, so neighbours differ less there than on the sides.
   - Stems (silhouette 6) show in the level tiles but not from a standing player's eye; from there the dome hides them.

The benchmark's bush is drawn red in `dome_bush_variants.png`: its leaf texture's colour is not what this viewer shows, so only its shape, density and size can be compared, not its colour.
