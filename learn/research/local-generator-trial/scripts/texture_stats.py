"""Describe the images stored in a .glb, and save each as a PNG to look at. Read-only on the model.

    tools/bl texture_stats.py <model.glb> <out folder>

For the question "is lighting baked into the base colour?". For every image: pixel size, and the
mean and the spread (standard deviation) of its brightness over the pixels that some triangle
actually uses is NOT attempted: the figures are over the whole image, padding included. Brightness
is 0.2126 R + 0.7152 G + 0.0722 B of the stored values (sRGB values as stored, not made linear).
Also the share of pixels darker than 0.15 and brighter than 0.85. A shadow baked into a base colour
shows as more dark pixels and a wider spread than the same texture made without it; two textures
are only comparable when they are of the same shape and the same picture. Prints one line starting
TEXTURES followed by JSON and writes textures.json into the folder.
"""
import json
import os
import sys

import bpy
import numpy as np

source, out = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
used = {}
for mat in bpy.data.materials:
    if not mat.use_nodes:
        continue
    for link in mat.node_tree.links:
        node = link.from_node
        if node.type == "TEX_IMAGE" and node.image:
            used.setdefault(node.image.name, set()).add(f"{mat.name}: {link.to_node.name} / {link.to_socket.name}")
report = []
for image in bpy.data.images:
    w, h = image.size
    if not w:
        continue
    px = np.empty(w * h * image.channels, dtype=np.float32)
    image.pixels.foreach_get(px)
    px = px.reshape(-1, image.channels)
    lum = px[:, 0] * 0.2126 + px[:, 1] * 0.7152 + px[:, 2] * 0.0722 if image.channels >= 3 else px[:, 0]
    entry = {"name": image.name, "size": [w, h], "channels": image.channels,
             "colorspace": image.colorspace_settings.name, "used_by": sorted(used.get(image.name, [])),
             "mean_rgb": [round(float(v), 4) for v in px[:, :3].mean(axis=0)],
             "brightness_mean": round(float(lum.mean()), 4), "brightness_spread": round(float(lum.std()), 4),
             "share_darker_than_0.15": round(float((lum < 0.15).mean()), 4),
             "share_brighter_than_0.85": round(float((lum > 0.85).mean()), 4)}
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in image.name)
    image.filepath_raw = os.path.join(out, safe + ".png")
    image.file_format = "PNG"
    image.save()
    entry["saved_as"] = safe + ".png"
    report.append(entry)
with open(os.path.join(out, "textures.json"), "w") as handle:
    json.dump(report, handle, indent=2)
print("TEXTURES " + json.dumps(report))
