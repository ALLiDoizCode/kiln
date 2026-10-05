"""Block, variant 2: one draw of the block generator (source/block/generator.py), from this spec's seed, bounds and cracks.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "block"))
from generator import build_block


def build(spec):
    return build_block(spec)
