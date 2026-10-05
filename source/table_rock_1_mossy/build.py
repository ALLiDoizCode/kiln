"""table_rock_1_mossy: `table_rock_1` under moss; the same draw of the table_rock generator (source/table_rock/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "table_rock"))
from generator import build_table_rock


def build(spec):
    return build_table_rock(spec)
