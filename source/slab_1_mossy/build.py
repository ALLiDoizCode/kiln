"""slab_1_mossy: `slab_1` under moss; the same draw of the slab generator (source/slab/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "slab"))
from generator import build_slab


def build(spec):
    return build_slab(spec)
