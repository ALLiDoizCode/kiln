"""Stepped spire, variant 1: one draw of the spire generator (source/spire/generator.py), from this spec's seed, bounds, tiers and piece count.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "spire"))
from generator import build_spire


def build(spec):
    return build_spire(spec)
