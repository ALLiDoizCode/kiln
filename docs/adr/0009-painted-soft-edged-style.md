# 9. The style is soft-edged shapes with painted shading, and foliage is leaf pieces over a dark core

This replaces the style line of ADR 7 ("flat-colour low-poly with bevels ... not from textures"). The rest of ADR 7 stands.

- **Shapes** have bevelled, soft edges and smooth shading, with enough geometry that facets do not read as facets.
- **Surfaces** carry painted shading computed by script from the shape and baked in: darker toward the base and lighter toward the top, light along exposed edges, shadow in crevices. Textures are allowed.
- **Foliage** is leaf-shaped geometry on a branch skeleton: each leaf or cluster is a flat, pointed, jagged-edged piece in one colour, large enough to read as a leaf, and a canopy is several separate pads of them with sky between. A solid may sit under the leaf pieces, as long as the leaf pieces are what is seen: a dark, closed, low-triangle core inside each pad. A solid shape on its own is never foliage. (Amended twice on 2026-10-04; see below.)
- **Rock** is built from deliberate planes, ledges and fractures, never from noise displacement.

The owner rejected the faceted references on the first style board as "too low poly", then chose bevelled and detailed shapes over faceted ones, and the painted treatment over plain colour, realistic texture and brush patches, in side-by-side throwaways (pit `look-tests/style-variants`). Nine reference scenes were then recreated by script (pit `look-tests/recreations`): composition, palette and haze worked every time, and solid-lump foliage, noise rock and untextured near surfaces failed every time. A professional stylised pack used as a benchmark builds its rocks and trees the way this record describes.

Baked into a texture, the painted treatment looked the same in Bevy as in Blender. Baked into vertex colours it came out washed pale in Bevy; ADR 10 found out why and chose the texture.

Foliage was first recorded here as leaf cards: flat pieces showing a painted cluster of leaves with transparent gaps, as the Quaternius benchmark builds them. That needs painted textures with transparency, and research found no free ones we could ship. The owner then offered a second pack as a reference for the look (`docs/style/nature-shapes.md`), whose foliage appears to be plain leaf-shaped geometry with a height gradient and crevice shadow computed by shader, the same idea as painted shading. The owner chose that route: it needs no painted leaf texture and no transparency, and it suits a pipeline that builds everything by script. It costs more triangles per tree. Leaf cards are not used.

The rule for foliage was then "never solid shapes", and the first three trees were built as open shells of leaf pieces. Beside the benchmark and the reference, their pads read as thin round caps on stalks: between the pieces one saw sky or the inside of the far side of the pad, and from underneath, where a first-person player mostly sees a tree, the pieces read as overlapping flat shapes. The reference's pads look as if they have a solid faceted core under the leaves. The owner agreed to allow that: a dark core under the leaf pieces. The rule is now that a solid may sit under the leaf pieces as long as the leaf pieces are what is seen. The gates hold a tree to it: every pad has its cores, they are closed and darker than every leaf piece, and from each review direction no more than a set share of the foliage seen is core (`source/tree/brief.md`). The core is in the leaf material and takes its colour from one more swatch of the palette (ADR 11), so a tree stays two materials.

Costs accepted: UV unwrapping, a bake step, texture and transparency support in the gates, and larger files.

Generator tools under the GPL (Sapling Tree Gen, IvyGen) are pinned as downloads in the git-ignored `.tools/` folder, like Blender itself, and are never vendored into the repo. Their output is ours.

The style is still conditional on the look test in pit.
