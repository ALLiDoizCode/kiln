"""Arch, variant 2: one draw of the arch generator (source/arch/generator.py), from this spec's seed, bounds, kind of span and opening.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "arch"))
from generator import build_arch


def build(spec):
    return build_arch(spec)
