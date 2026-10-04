# crate

A wooden supply crate. The first real prop, and the reference for the stylised low-poly look.

## Purpose

Set dressing and cover. Characters stand beside it and behind it; nothing opens or breaks it yet. It can be stacked and tipped, so all six sides are finished, including the bottom.

## Viewing

Third-person camera, typically 3 to 10 m away and never closer than about 2 m. Detail smaller than roughly 3 cm is not visible and is left out.

## Real-world size

A 0.8 m cube: waist-high on a 1.8 m character, about the size of a washing machine. The origin is on the ground at the centre of the base.

## Silhouette

1. A cube with a raised frame running along every edge.
2. A recessed panel on each face, set back far enough to hold a shadow line at 10 m.

Frame members are 0.1 m wide (one eighth of the side). Panels are recessed 0.05 m.

## Style and colour

Flat colour, hard edges, no textures and no bevels. One material per colour:

- `m_crate_frame`: dark wood, `#5a3820`.
- `m_crate_panel`: lighter wood, `#a87a4a`.

The frame, including the walls of each recess, is frame-coloured; only the recessed panel is panel-coloured.

## Parts

One object, one closed mesh. Nothing moves.

## Budget

150 triangles and 2 material slots. A level may show dozens at once, and at 3 m the silhouette above needs no more.

## References

None. Proportions are from the numbers above.

## Out of scope

Plank gaps, diagonal braces, bevelled edges, wear, LODs, collision shapes, variants.

## Decisions

Chosen by the user on 2026-10-04: supply crate, 0.8 m at third-person distance, one material per colour, frame and inset panels at about 150 triangles. Frame width, recess depth, the two colours and the finished bottom were proposed by the agent and are open to change at the first review. After that review the user deepened the recess from 0.03 m to 0.05 m, because it only read as depth on faces with a cast shadow.
