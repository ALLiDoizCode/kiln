# 9. The style is soft-edged shapes with painted shading, and foliage is leaf cards

This replaces the style line of ADR 7 ("flat-colour low-poly with bevels ... not from textures"). The rest of ADR 7 stands.

- **Shapes** have bevelled, soft edges and smooth shading, with enough geometry that facets do not read as facets.
- **Surfaces** carry painted shading computed by script from the shape and baked in: darker toward the base and lighter toward the top, light along exposed edges, shadow in crevices. Textures are allowed.
- **Foliage** is leaf cards (small flat pieces showing a painted cluster of leaves, with transparent gaps) hung on a branch skeleton, never solid shapes.
- **Rock** is built from deliberate planes, ledges and fractures, never from noise displacement.

The owner rejected the faceted references on the first style board as "too low poly", then chose bevelled and detailed shapes over faceted ones, and the painted treatment over plain colour, realistic texture and brush patches, in side-by-side throwaways (pit `look-tests/style-variants`). Nine reference scenes were then recreated by script (pit `look-tests/recreations`): composition, palette and haze worked every time, and solid-lump foliage, noise rock and untextured near surfaces failed every time. A professional stylised pack used as a benchmark builds its rocks and trees the way this record describes.

Baked into a texture, the painted treatment looked the same in Bevy as in Blender. Baked into vertex colours it came out washed pale in Bevy; ADR 10 found out why and chose the texture.

Costs accepted: UV unwrapping, a bake step, texture and transparency support in the gates, and larger files.

Generator tools under the GPL (Sapling Tree Gen, IvyGen) are pinned as downloads in the git-ignored `.tools/` folder, like Blender itself, and are never vendored into the repo. Their output is ours.

The style is still conditional on the look test in pit.
