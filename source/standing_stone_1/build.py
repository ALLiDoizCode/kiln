"""Standing stone, variant 1: one draw of the standing stone generator (source/standing_stone/generator.py), from this spec's seed, bounds and piece count.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "standing_stone"))
from generator import build_standing_stone


def build(spec):
    return build_standing_stone(spec)
