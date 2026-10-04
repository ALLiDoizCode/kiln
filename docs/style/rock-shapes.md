# Rock shapes

A vocabulary of rock forms to build, and the construction habits behind them. It is a list of shapes in our own words, read off the preview images of a commercial pack ([Low Poly Rock Bundle](https://superhivemarket.com/products/low-poly-rock-bundle), 143 rocks, about 280 triangles each). The pack was not bought and nothing from it is used; the previews are kept locally in the git-ignored `docs/style/refs/rock-shapes/`.

Take the **shapes** from this list. Do not take the surface: the pack is faceted, hard-edged and one flat colour, which is the look ADR 9 replaced. Our rocks get soft edges and painted shading on top of these forms.

## The shapes

| Shape | What it is | Where the game needs it |
| --- | --- | --- |
| **Boulder** | One full, heavy lump made of a few large planes with broad chamfered corners. Wider than tall. | Everywhere; the first rock asset. |
| **Standing stone** | A tall slab or lozenge, two to four times as tall as wide, tapering toward the top, leaning a little. | Markers, the standing stones of the forest reference. |
| **Stepped spire** | A wide base with vertical flutes, then two or three narrower tiers stacked on it like a telescope, each with a flat cap. Small blocks and wedges lean on its foot. | Pillars standing in the pit. |
| **Crag** | Many leaning prisms of different heights sharing one base. The tallest is off-centre, the others step down from it, and small blocks fill the foot. | Cliff tops, ridges, broken ground. |
| **Arch** | Two piers of stacked blocks bridged by a lintel block or a knot of wedged blocks, with rubble at the feet. | Gateways, natural bridges between ledges. |
| **Rib** | A curved column built from short segments, alone or paired into a pointed arch. | Fossil or bone-like features of deeper layers. |
| **Table rock** | A wide flat slab resting on one or two narrow necks. | Overhangs, shelter, platforms to build on. |
| **Slab** | A wide, low plate with a polygonal outline and a nearly flat top; often two or three overlapped. | Ledges to stand and build on, stepping stones. |
| **Stack** | Three to five flat stones piled off-centre, each smaller or turned from the one below. | Cairns, trail markers. |
| **Block** | A near-cuboid with chamfered corners and one or two crack lines, in a run of sizes. | Quarried or fallen stone, building material. |
| **Terrace** | A block cut into steps that climb to one side. | Climbable steps on a wall. |
| **Pebble** | A small, low, rounded polyhedron; made as a run of sizes. | Ground scatter. |
| **Rubble** | A handful of tiny fragments placed as one group. | The foot of arches, cliffs and broken blocks. |

## How they are built

These habits show in almost every piece, and they are what separates a designed rock from a lump:

- **Several pieces, not one.** Most shapes are a few plane-cut pieces pushed together: one dominant piece, two or three secondary ones, and several small ones. A single cut block reads as a wedge.
- **A clear size order.** The pieces differ a lot in size; none are near-equal twins.
- **Nothing is upright.** Every piece tapers or leans, and pieces in one group lean roughly the same way.
- **The tallest part is off-centre.**
- **A foot.** Small blocks and wedges sit against the base, so the rock looks settled into the ground and not placed on it.
- **Flat caps.** Tops are flat or gently tilted planes, ringed by a chamfer, never points.
- **Long vertical edges.** Tall sides are broken by edges that run top to bottom, like flutes, not by horizontal bands.
- **Big chamfers.** Corners are cut by a plane wide enough to catch light as its own face.

## Not answered by pictures

The numbers behind these shapes (how full each is against its bounding box, how much of the surface the large planes hold, triangle counts per shape) cannot be read from previews. The thresholds in `conventions.toml` and in rock specs are still proposals measured against one benchmark rock.
