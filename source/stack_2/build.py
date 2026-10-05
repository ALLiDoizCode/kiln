"""Stack, variant 2: one draw of the stack generator (source/stack/generator.py), from this spec's seed, bounds and stone count.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "stack"))
from generator import build_stack


def build(spec):
    return build_stack(spec)
