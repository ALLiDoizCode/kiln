"""Build one asset from a run of seeds and say which pass gate L1, to see how reliable a generator is.

Each seed is built by the asset's own build script from its spec with only the seed changed,
and measured by tools/validate.py as the gate would. Nothing is painted, saved or exported, so
this says nothing about the later gates. An aid for writing a brief, not a gate.

Usage: tools/bl tools/try_seeds.py <asset> <first seed> <last seed>
"""

import runpy
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import Asset, Checks, conventions, script_args
from validate import check_scene

name, first, last = script_args()
asset = Asset(name)
passed = []
for seed in range(int(first), int(last) + 1):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    spec = asset.spec()
    spec["seed"] = seed
    # Flat-coloured, as the build script leaves it: painting is tools/paint.py's, and is not what a seed changes.
    spec.pop("painted_shading", None)
    spec.pop("variants", None)
    try:
        runpy.run_path(str(asset.source / "build.py"))["build"](spec)
    except RuntimeError as error:
        print(f"seed {seed}: no build: {str(error).splitlines()[0]} ({len(str(error).splitlines()) - 1} refused)")
        continue
    checks = Checks("L1-mesh", name)
    triangles = check_scene(checks, spec, conventions())
    failed = sorted(r["id"] for r in checks.failed())
    print(f"seed {seed}: {triangles} triangles, {'passes L1' if not failed else f'FAILS {failed}'}")
    if not failed:
        passed.append(seed)
print(f"{name}: {len(passed)} of {int(last) - int(first) + 1} seeds build and pass L1: {passed}")
