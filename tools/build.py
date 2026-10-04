"""Build one asset from source/<asset>/build.py into source/<asset>/out/<asset>.blend.

Usage: tools/bl tools/build.py <asset>
"""

import runpy
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import Asset, script_args

asset = Asset(script_args()[0])

bpy.ops.wm.read_factory_settings(use_empty=True)
runpy.run_path(str(asset.source / "build.py"))["build"]()

asset.out.mkdir(parents=True, exist_ok=True)
result = bpy.ops.wm.save_as_mainfile(filepath=str(asset.blend), check_existing=False)
if result != {"FINISHED"}:
    raise RuntimeError(f"save failed: {result}")
print(f"built {asset.blend}")
