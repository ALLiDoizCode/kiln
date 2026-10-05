"""Rubble, variant 2: one draw of the rubble generator (source/rubble/generator.py), from this spec's seed, bounds and fragment count.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "rubble"))
from generator import build_rubble


def build(spec):
    return build_rubble(spec)
