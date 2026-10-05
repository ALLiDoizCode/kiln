"""Export log_3 with its grain running the wrong way, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants, so the named check must fail.

Usage: tools/bl tests/log_mutations.py <mutation> <out.glb>

  hoops  the grain runs round the trunk and not along it: every corner's place across the grain and
         along it are exchanged before painting. `painted.grain_along` must fail it
"""

import runpy
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import paint
from pipeline import Asset, conventions, script_args, share_textures

mutation, out = script_args()
if mutation != "hoops":
    raise RuntimeError(f"no mutation called {mutation}")
asset = Asset("log_3")
spec = asset.spec()
bpy.ops.wm.read_factory_settings(use_empty=True)
log = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
for corner in log.data.attributes["grain"].data:
    across, along, limb = corner.vector
    corner.vector = (along, across, limb)
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is log)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
share_textures(out)
