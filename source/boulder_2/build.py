"""Boulder, variant 2: one draw of the boulder generator (source/boulder/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "boulder"))
from generator import build_boulder


def build(spec):
    return build_boulder(spec)
