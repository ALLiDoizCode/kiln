# block_2, final: what the sheet shows

Read from `sheet.png`, the aids of the `material_three_quarter` tile (`material_three_quarter_aids.png`; `bevy_aids.png` was made and not opened), and `benchmarks/out/block_variants.png`. Numbers in brackets are the gate's own, from `out/reports/`.

1. **Silhouette.** Near-cuboid: `front` and `back` are a rectangle 1.7 times as wide as tall with one top corner cut. Square to the view: top 0.573, front 0.872, back 0.695, right 0.507, left 0.911 [at least 0.5 each]. Chamfers: three ways, 0.101 to 0.119 m across [at least 3 of 0.08 m]. The crack reads in `front`, `back`, `top`, `three_quarter` and both Bevy tiles: a notch in the top outline about a twentieth of the width wide in `front`, a straight dark line across the whole top in `top`, turned about 12 degrees from square, and a line leaning about 12 degrees down each long side. It does not read in `right`, which looks along it.
2. **Proportions.** 1.0 x 0.7 x 0.6 m. The crack is about 0.62 of the way along; the pieces show 2.05 and 1.19 m2 [step 1.71, at least 1.3]. The smaller piece stands about 2 cm lower and further in than the larger: a step along the crack in `front` and `top`. Lines across the block that meet one groove: 0.811 [at least 0.7]. 0.193 of the surface is buried [at most 0.4]. 0.573 of the view from above is level [at least 0.5].
3. **Facing and grounding.** The base sits on the bottom edge of the frame; no gap under it. In `top` a sliver of the larger piece's foot shows past the smaller piece's front side, about 2 cm wide.
4. **Topology** (clay_wire). 118 triangles [budget 250]. Two closed pieces; each plane a fan; the walls of the crack below the groove are inside the other piece and carry about a sixth of the triangles.
5. **Shading.** Planes lit flat, strips round. The groove is dark on both walls in every tile.
6. **Materials.** One grey, top lighter than foot; blotches about 0.15 m; the crack is the darkest thing on the block, a band about 5 cm wide in `top`.
7. **Scale.** About one third of the figure's height [brief: 0.6 of 1.8 m].
8. **In the engine** (`bevy`, `bevy_back`, `block_variants.png`). The crack is a black line from `--stand 3` and a slot with a lit far rim from `--close`; darker and wider than in Blender's tiles, because the engine's shadow falls into it as well as the paint.
9. **Values** (value map of `material_three_quarter`). Two masses: the top, which has the backdrop's value and vanishes into it, and the dark sides; the crack shows as a dark line joining the sides across the top.
10. **At a glance** (squint). "Split grey block." The eye lands on the dark line across the top.
11. **Differences from the brief.**
    - Silhouette 4 asks for a crack line; what shows is a straight, even slot. It never wanders, forks or narrows, and on a block 1 m wide it is about 5 cm of darkness: closer to a saw cut or a parted joint than a crack.
    - Closest to its limit: 0.507 of the right view square to the view, where 0.5 is asked.
    - The sliver of foot in item 3 is a consequence of setting each piece in by its own amount; no check sees it.
