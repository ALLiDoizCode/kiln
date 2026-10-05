"""standing_stone_1_mossy: `standing_stone_1` under moss; the same draw of the standing_stone generator (source/standing_stone/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "standing_stone"))
from generator import build_standing_stone


def build(spec):
    return build_standing_stone(spec)
