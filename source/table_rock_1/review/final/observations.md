# table_rock_1, final: observations

Tiles read: `sheet.png`, `bevy_under.png`, and the aids `bevy_aids.png`, `material_three_quarter_aids.png`, `bevy_under_aids.png`. Gate L1's measurements are quoted where a tile cannot give a number.

## 1. Silhouette

- front, right, back: a plate on one neck; air shows under the plate on both sides of the neck in all three. In `front` the neck is about one fifth of the cap's width (L1: the neck fills 0.072 of the outline 1.0 m up; brief: at most 0.15).
- front, back: the cap's sides slope out from the underside to the shoulder and its top edge is chamfered; the cap is widest about two thirds of the way up its thickness. Brief: undercut 18 to 38 degrees.
- top: an outline of seven straight sides of unequal length; nothing of the neck or block shows past it. Brief: six to eight sides.
- right, back: one block at the neck's foot, about one sixth of the neck's height and as wide as the neck is at the ground. It does not read in `top` (under the cap) and is a few pixels in `bevy`.
- three_quarter, bevy: the neck stands off the middle of the cap, toward the back left. L1: it stands 0.93 m in from the rim at the nearest (brief: at least 0.6 m).

## 2. Proportions

- scale: the underside of the cap is above the figure's head by about one tenth of the figure's height. L1: 0.841 of the outline has 2.0 m of open air under it (brief: at least 0.6 of it, 2.0 m).
- front: the cap is about one quarter of the whole height thick; the neck three quarters.
- L1: 0.590 of what is seen from above is within 12 degrees of level (brief: at least 0.5). This is the measure closest to its limit.
- L1: 3 pieces showing 19.73, 6.78 and 1.70 m2, steps 2.91 and 3.99 (brief: at least 1.3); 0.065 of the surface buried (brief: at most 0.2).

## 3. Facing and grounding

- front, scale: the neck and block stand on the bottom of the frame; the cap's bounds fill it side to side. The asset has no front of its own.

## 4. Topology (clay_wire)

- top: the cap's top is one plane fanned into triangles from two corners; long thin triangles, all coplanar. Every other edge follows a plane's border, doubled by its soft-edge strip.
- 326 triangles (budget 400).

## 5. Shading (material tiles)

- front, scale: the upper half of the neck is darker than the lower with a hard diagonal border. The same border is in `clay_wire_front`, which has no paint: it is the shadow the cap casts on the neck under the review light, not a normal.
- No face is darker or lighter than its neighbours without a light or paint reason.

## 6. Materials

- One material. top: blotches of two tones about a ninth of the cap's width across (brief: about 0.4 m of 3.6 m). The cap's rim is lighter than its top (edge light).

## 7. Scale

- scale: the asset is about 1.6 figures tall (brief: 2.9 m over 1.8 m, 1.61).

## 8. In the engine (bevy, bevy_back, bevy_under)

- bevy, bevy_back: the top of the cap is light and shows its blotches; the neck is in the cap's shadow from the top down to about a third of its height on the sunlit side and wholly on the other. The shadow on the ground is about as wide as the cap.
- bevy_under (eye 1.7 m up, 1 m from the origin, looking 35 degrees up): the neck, a darker ring on the underside round the top of the neck (the crevice shadow at the join, about half the neck's width out from it), the underside, and the rim against the sky at the lower corners. The texture's brightest channel spans 67 to 152 (8-bit sRGB) and the underside is painted at about 0.72 of the height, between the two tints; under Bevy it comes out at about 54 of 255, the join ring at about 39 to 51 and the neck beside it at about 47 (grey means of patches of the tile, by `magick`; approximate), where the sunlit top of the cap is about 170. Everything under the cap is in the cap's own cast shadow and is lit by the viewer's ambient light alone.
- bevy_under: the blotches and the edge light of the underside cannot be made out; the join ring can.

## 9. Values (bevy_aids, bevy_under_aids)

- bevy: three masses: the cap's top (lightest), the ground, and the neck together with the cast shadow (darkest). The neck and the shadow on the ground are one grey: the neck vanishes into the shadow.
- bevy_under: one mass. The neck, the join and the underside are a single grey of the five; only the sky and the ground differ.
- material_three_quarter: three masses: top, cap sides, neck.

## 10. At a glance (squint)

- bevy: "pale disc, dark stalk"; the eye lands on the cap's top. A mushroom or a table would both fit.
- bevy_under: "dark ceiling, dark post"; the eye lands on the bright sky at the lower corners.

## 11. Differences from the brief

- Viewing, from underneath: the brief asks for the underside to be a finished surface with paint like any other. It is painted, but under the viewer's light none of the paint but the join ring reads: about 54 of 255 against 170 on the top. Nothing in the gates measures this.
- Silhouette 7: the neck's sides taper 2 to 6 degrees, inside what the other rocks call upright. No check holds it.
- The block is small in every view from outside the cap, and from above it is not seen at all: the "foot" of rock-shapes.md is weaker here than on the crag.
