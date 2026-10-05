"""tree_1_winter: one draw of the tree generator (source/tree/generator.py), from this spec's species, growth stage, seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tree"))
from generator import build_tree


def build(spec):
    return build_tree(spec)
