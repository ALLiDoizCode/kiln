"""How many pixels of two images of the same size differ at all, and by how much at most.
    tools/bl count_different_pixels.py <a> <b> [<a2> <b2> ...]
Prints a line starting PIXELS per pair. For asking whether two bakes that are not the same
bytes differ in a handful of pixels or all over."""
import json
import sys

import bpy
import numpy as np


def pixels(path):
    image = bpy.data.images.load(path)
    image.colorspace_settings.name = "Non-Color"
    data = np.zeros(image.size[0] * image.size[1] * image.channels, dtype=np.float32)
    image.pixels.foreach_get(data)
    out = np.rint(data.reshape(image.size[1], image.size[0], image.channels) * 255.0)
    bpy.data.images.remove(image)
    return out


args = sys.argv[sys.argv.index("--") + 1:]
for a, b in zip(args[0::2], args[1::2]):
    diff = np.abs(pixels(a) - pixels(b)).max(axis=2)
    ys, xs = np.nonzero(diff)
    print("PIXELS " + json.dumps({"a": a, "b": b, "pixels": int(diff.size), "different": int(len(ys)),
                                  "largest_difference_of_255": float(diff.max()),
                                  "where": [[int(x), int(y)] for x, y in list(zip(xs, ys))[:10]]}))
