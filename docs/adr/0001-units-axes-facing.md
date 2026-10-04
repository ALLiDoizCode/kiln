# 1. Units, axes and facing

One unit is one metre everywhere. Assets are authored in Blender's own convention: +Z up, front facing −Y (what Blender's Front view looks at). The glTF exporter converts to +Y up, which puts the asset's front on glTF +Z, the glTF standard. Origins sit on the ground plane (z = 0), and rotation and scale are applied before export.

Bevy treats −Z as forward, so a glTF-conventional asset faces "backward" by Bevy's definition. We do not model assets backward to compensate: they would look wrong in Blender, in the validator and in every other viewer. Facing is handled on the Bevy side, when the first asset that cares about forward (a character or vehicle) needs it. `GltfConvertCoordinates` is the candidate but is marked experimental in 0.19.

`tools/pipeline.py` (`gltf_bounds`) encodes the axis mapping, and the tracer fixture exists to break loudly if any of this drifts.
