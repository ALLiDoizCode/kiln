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
