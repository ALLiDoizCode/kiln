# tracer

Not a game asset. A pipeline fixture: the smallest shape that makes every
axis, facing, scale and winding mistake visible, pushed through every gate.

- Shape: a boot. Flat sole on the ground, toe pointing to the asset's front,
  leg rising at the back.
- Deliberately asymmetric: the three extents differ (1.5 m wide, 2.0 m long,
  1.0 m tall) and the origin is off-centre on every axis, so any axis swap,
  mirror or rescale changes the bounding box.
- One flat-colour material. No UVs, no textures.

If the toe does not point at the viewer in the "front" render, or the load
test reports different bounds, a convention is broken somewhere.

## Numbers

| Spec key | Value | From |
| --- | --- | --- |
| `objects` | `["tracer"]` | One object |
| `bounds_m.min` | `[-0.5, -1.5, 0.0]` | Off-centre origin; toe at the front, y = -1.5 |
| `bounds_m.max` | `[1.0, 0.5, 1.0]` | 1.5 m wide, 2.0 m long, 1.0 m tall |
| `bounds_tolerance_m` | `0.001` | 1 mm |
| `max_triangles` | `40` | The boot is 28 triangles; room for none more than a small change |
| `materials.m_tracer` | `"#d9662e"` | One flat-colour material |
| `watertight` | `true` | A closed solid |
| `attributes` | `["POSITION", "NORMAL"]` | No UVs, no textures |
