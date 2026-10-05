"""log_1: one draw of the log generator (source/log/generator.py), from this spec's seed, bounds and `log` block.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))
from plant_parts import family_generator


def build(spec):
    return family_generator("log").build_log(spec)
