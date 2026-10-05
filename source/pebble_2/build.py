"""Pebble, variant 2: one draw of the pebble generator (source/pebble/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pebble"))
from generator import build_pebble


def build(spec):
    return build_pebble(spec)
