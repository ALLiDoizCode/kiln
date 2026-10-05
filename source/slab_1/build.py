"""Slab, variant 1: one draw of the slab generator (source/slab/generator.py), from this spec's seed, bounds and piece count.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "slab"))
from generator import build_slab


def build(spec):
    return build_slab(spec)
