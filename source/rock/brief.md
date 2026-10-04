# rock

A free-standing boulder. The first rock, and the first asset in the soft-edged style of ADR 9.

## Purpose

Set dressing and cover on a layer's ground. A player walks around it and stands beside it. Nothing climbs, breaks or moves it yet, and it is not stood on by design (the top is above head height). It sits on flat ground; its underside is never seen.

## Viewing

First person, from as close as 0.5 m (ADR 7), and typically from 3 to 20 m. At 0.5 m a single plane fills the view, so each plane has to hold up as a flat, clean surface with a soft edge around it, and the silhouette has to work from every side.

## Real-world size

3.0 m wide, 2.6 m deep and 2.0 m tall: a little taller than the 1.8 m player and about the footprint of a small car. Its lowest point is at z = 0 and the origin is on the ground under the centre of its bounding box.

## Silhouette

1. An asymmetric boulder cut from a block by a small number of large planes of clearly different sizes and tilts. A plane counts as large at 0.4 m2 or more (a 0.63 m square, which at 0.5 m fills about 60 degrees of the view). There are between 6 and 16 large planes, the largest is at least 3 times the area of the median one, and together they hold at least 75% of the visible surface. The rest is soft edge and small chamfers.
2. At least one ledge: a step where two large planes meet in an inward (concave) corner at least 0.5 m long, so the outline has a shoulder and is not one convex lump.
3. No face reads as part of a sphere: there is no patch of small faces whose tilt changes gradually. The 75% share above is the number that rules it out.

The sides lean inward toward the top, so the base is the widest part and the rock reads as sitting, not balanced.

## Style and colour

ADR 9: soft edges, and rock built from deliberate planes, never from noise displacement. Planes are made by cutting a block (`bmesh.ops.bisect_plane`), and the ledge by cutting a rectangular notch.

Edges are softened with a one-segment bevel, 0.07 m wide, and smooth shading whose normals are taken from the planes: each plane is lit as perfectly flat and the bevel strip between two planes blends from one to the other. The benchmark gets soft edges from smooth shading alone on a sculpted mesh; on a mesh of exact planes that would smear light across every plane, which is the "part of a sphere" look this brief rules out. The edge where the rock meets the ground is left hard, so no gap shows under it.

One material, one flat colour:

- `m_rock`: mid grey, `#a1a7a1`, the median of the grey (not mossy) texels of the benchmark's texture under this rock's UVs.

Painted shading (ADR 9: base-to-top gradient, light edges, dark crevices, moss) is a later step and is out of scope here.

## Parts

One object, one closed mesh. Nothing moves.

## Budget

At most 400 triangles and 1 material slot. The benchmark is 342 triangles. Until the stress scene of ADR 7 exists this is an estimate.

## References

`benchmarks/quaternius-stylized-nature/glTF/Rock_Medium_1.gltf`, seen in the Bevy viewer (`benchmarks/out/Rock_Medium_1.png`, `Rock_Medium_1_close.png`). It is a benchmark: nothing from it is copied or shipped. What we are matching:

- The read: a handful of big flat planes, the largest several times the size of the others, with soft edges between them.
- The step on top, where a raised slab sits above a lower shelf.
- Sides that lean in from a wide base.
- Size class and cost: about 3.2 by 3.0 by 2.3 m and 342 triangles.

What we are not matching: its painted texture and moss, and its sculpted, slightly uneven planes (measured at a 1 degree tolerance, only 11% of its surface lies in large planes; ours are exact).

## Out of scope

Variants, LODs, collision shapes, UVs, textures, painted shading, a finished underside.

## Numbers

Every value in `spec.json`, and the sentence above it comes from. `tools/lint_spec.py` fails if a row and the spec disagree, or if the spec has a value with no row.

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["rock"]` | Parts: one object |
| `bounds_m.min` | `[-1.5, -1.3, 0.0]` | Real-world size: 3.0 by 2.6 m in plan, lowest point at z = 0, origin under the centre |
| `bounds_m.max` | `[1.5, 1.3, 2.0]` | Real-world size: 2.0 m tall |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `400` | Budget |
| `materials.m_rock` | `"#a1a7a1"` | Style and colour: mid grey from the benchmark's texture |
| `planes.large_m2` | `0.4` | Silhouette 1: a plane counts as large at 0.4 m2 |
| `planes.min_area_share` | `0.75` | Silhouette 1 and 3: large planes hold at least 75% of the visible surface |
| `planes.min_count` | `6` | Silhouette 1: between 6 and 16 large planes |
| `planes.max_count` | `16` | Silhouette 1: between 6 and 16 large planes |
| `planes.min_size_ratio` | `3.0` | Silhouette 1: the largest is at least 3 times the median |
| `planes.min_ledges` | `1` | Silhouette 2: at least one ledge |
| `planes.ledge_m` | `0.5` | Silhouette 2: a concave corner at least 0.5 m long |
| `soft_edges` | `true` | Style and colour: every edge is soft except where the rock meets the ground |
| `watertight` | `true` | Parts: one closed mesh |
| `attributes` | `["POSITION", "NORMAL"]` | Out of scope: no UVs or textures |

## Decisions

There was no grilling session: the owner gave the decisions below in writing on 2026-10-04 and the agent proposed the rest. Every proposed item is open to change at the first review.

Given by the owner: the name; purpose and first-person viewing from 0.5 m; the benchmark; about 3.0 by 2.6 by 2.0 m with the lowest point at z = 0 and the origin under the centre; at most 400 triangles and one material; `m_rock` as one flat mid grey sampled from the benchmark's texture; painted shading out of scope; an asymmetric boulder of a small number of large planes of clearly different sizes and tilts, with at least one ledge or step and no face that reads as part of a sphere; plane cuts as the technique; a seeded build script with one fixed seed; variants, LODs, collision, UVs and textures out of scope.

Proposed by the agent: the exact bounds (centred in x and y); the hex value `#a1a7a1`; every number under `planes` (what large means, the 75% share, 6 to 16 planes, the size ratio of 3, and a ledge as a 0.5 m concave corner between two large planes); the edge treatment (0.07 m one-segment bevel with plane normals, hard edge at the ground); the flat underside at z = 0; the seed.

"Clearly different tilts" has no number and no check; it is judged on the contact sheet.
