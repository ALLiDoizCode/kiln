"""How much two pictures of the same size differ, pixel by pixel. Read-only.

    tools/bl picture_diff.py <a.png> <b.png> [<a2.png> <b2.png> ...]

Prints one line per pair starting with DIFF and JSON: the mean absolute difference of the red,
green and blue values on a scale of 0 to 255, and the share of pixels where any of the three
differs by more than 8 and by more than 32. Used on review pictures of a dense model and of a
reduced one taken from the same camera: the smaller the numbers, the closer the reduced model
looks to the dense one in that view. Runs in Blender only because Blender can read a PNG and
the system Python has no image library.
"""
import json
import sys

import bpy
import numpy as np


def pixels(path):
    image = bpy.data.images.load(path)
    image.colorspace_settings.name = "Non-Color"
    data = np.zeros(image.size[0] * image.size[1] * image.channels, dtype=np.float32)
    image.pixels.foreach_get(data)
    out = data.reshape(image.size[1], image.size[0], image.channels)[:, :, :3] * 255.0
    bpy.data.images.remove(image)
    return out


args = sys.argv[sys.argv.index("--") + 1:]
for a, b in zip(args[0::2], args[1::2]):
    pa, pb = pixels(a), pixels(b)
    if pa.shape != pb.shape:
        print("DIFF " + json.dumps({"a": a, "b": b, "error": "different sizes"}))
        continue
    diff = np.abs(pa - pb)
    worst = diff.max(axis=2)
    print("DIFF " + json.dumps({"a": a, "b": b, "mean_abs_difference": round(float(diff.mean()), 4),
                                "share_over_8": round(float((worst > 8).mean()), 5),
                                "share_over_32": round(float((worst > 32).mean()), 5)}))
