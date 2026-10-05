"""crag_1_mossy: `crag_1` under moss; the same draw of the crag generator (source/crag/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "crag"))
from generator import build_crag


def build(spec):
    return build_crag(spec)
