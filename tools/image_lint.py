"""Gate L5c: a review image is saved the way image viewers show faithfully.

A contact sheet or side-by-side saved with 16 bits per channel, or with an
alpha channel, is reduced to a small palette by some viewers (the one agents
read images through among them). Smooth gradients then show as flat bands and
soft patches gain hard outlines, neither of which is in the asset. An image
that is 8 bits per channel and opaque is shown as saved.

Usage: python tools/image_lint.py <image.png> [more.png ...]
"""

import subprocess
import sys

from pipeline import Checks

checks = Checks("L5c-image", " ".join(sys.argv[1:]))
for path in sys.argv[1:]:
    described = subprocess.run(["magick", "identify", "-format", "%z %[channels]", path], capture_output=True, text=True)
    depth, channels = (described.stdout.split() + ["?", "?"])[:2] if described.returncode == 0 else ("unreadable", "unreadable")
    checks.check(f"image.eight_bit: {path}", depth == "8", f"{depth} bits per channel; viewers reduce anything deeper to a palette, which shows as banding")
    checks.check(f"image.opaque: {path}", channels in ("srgb", "gray"), f"channels are {channels}; a review image is opaque colour")
checks.finish()
