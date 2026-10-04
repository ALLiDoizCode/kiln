# crate / final: observations

From `sheet.png`, rendered with the recess at 0.05 m and colours `#5a3820` / `#a87a4a`. Pixel figures are read from the 512 px tiles by eye, so treat them as good to about 2%.

## Silhouette

- three_quarter: a cube with a darker frame along all nine visible edges and a lighter recessed panel on each of the three visible faces. Both silhouette features from the brief read.
- front, top: the recess shows as a shadow band along the top and left inner edges of the panel. In clay_wire_front the band under the top frame member is about 10% of the side; at 0.03 m it was about 6%.
- right, back: the recess does not read as depth. These faces are lit only by the shadowless fill light, so frame and panel are told apart by colour alone.

## Proportions

- front: the crate fills 52% of the tile width, and the tile is framed at 1.52 m, so the crate is about 0.79 m wide. Brief: 0.8 m.
- right (no cast shadow): each frame member is 12 to 13% of the side. Brief: 0.1 m of 0.8 m, 12.5%.
- Recess depth cannot be measured from this sheet: the recess walls are edge-on in the four orthographic views, and the band visible there is cast shadow, whose length depends on the light angle. three_quarter shows the walls on all three faces, visibly narrower than the frame members. The depth is gated instead: `m_crate_panel.recess` in the L1 mesh checks compares every panel face against the spec's `recess_m` of 0.05 m.

## Facing and grounding

- front, right, back: the crate is centred in the frame built from the spec's bounds, base on the lower edge of those bounds.
- All four side faces are identical, so these renders cannot show facing. The bounds check in the Bevy load test covers axis and scale; the tracer covers facing.

## Topology (clay_wire)

- Each face has four mitred frame quads, four recess walls and one panel quad. Every edge sits on a silhouette or colour boundary; none supports nothing.
- three_quarter: the wire overlay is thicker where three frame corners meet at the near top corner. This is the review wireframe modifier overlapping itself, and is absent from the material pass.

## Shading (material)

- Each face is uniformly lit; no face is darker or lighter than a parallel neighbour. Frame quads on one face share one tone across their mitre lines, so the mitres do not show.
- front: the panel's cast shadow is close in tone to the frame, so the top and left frame members look nearly twice as wide as the bottom and right ones. In clay_wire_front the same members measure equal. This is the review light, and it is also how the crate will look under a low sun in game.

## Materials

- Frame reads as dark brown and panel as mid tan in every view; the panel is clearly the lighter of the two. Brief: dark wood `#5a3820`, lighter wood `#a87a4a`.
- The recess walls carry the frame colour, as the brief asks (front and top, under the top frame member).
- The first version of this sheet used linear RGB values from the brief and the frame rendered as mid tan, not dark wood. That mismatch led to ADR 6 and the `base_colour` check.

## Scale

- scale: the crate's top is at about 45% of the figure's height. Brief: 0.8 m beside a 1.8 m player, 44%. It reads as waist-high.

## In the engine (bevy tile)

- Lit faces are lighter than in the Blender material tiles: the frame reads as mid brown and the panel as light tan. The shaded right face is much darker, with its frame close to black. Contrast between lit and shaded faces is higher in Bevy than in Blender.
- Frame and panel stay distinguishable on all three visible faces, including the shaded one.
- The recess shows as a dark line along the inner top and left edges of the front and top panels, and the crate casts a shadow on the ground; its base sits on the ground with no gap.
- Colours in this tile depend on the viewer's own light and exposure, which are placeholders until the game's lighting exists (pit issue #1). The brief's "dark wood" holds in shade and not in direct light.

## Differences from the brief

None found in geometry, proportions or colour assignment.

For the user to judge, since no number settles them:

1. The recess still reads as depth only on faces with a cast shadow (front, top, three_quarter); the right and back views are unchanged by the deeper recess. This is a limit of the shadowless fill light, and in game it depends on the scene's lighting.
2. In Bevy the lit frame is lighter than "dark wood" suggests. Whether to darken `#5a3820` should wait for the game's real lighting.
3. With no bevels and no plank gaps the faces are flat colour fields. That matches the brief's scope, and is the first thing to revisit if the crate looks too plain beside other assets.
