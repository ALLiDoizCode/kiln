"""Dome bush, variant 3: one draw of the generator (source/dome_bush/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dome_bush"))
from generator import build_bush


def build(spec):
    return build_bush(spec)
