"""Export pebble_1 drawn from another seed, with or without its paint broken, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants.

Usage: tools/bl tests/pebble_mutations.py <mutation> <out.glb>

  flat_cap     seed 1 and nothing wrong: a plate whose open faces are its cap and little else, a few
               blotches across and almost all at one height. The load test must pass it
  no_gradient  that stone painted one tint from foot to cap: `painted.gradient` must fail it
"""

import runpy
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import paint
from pipeline import Asset, conventions, script_args

mutation, out = script_args()
if mutation not in ("flat_cap", "no_gradient"):
    raise RuntimeError(f"no mutation called {mutation}")
asset = Asset("pebble_1")
spec = asset.spec()
spec["seed"] = 1
bpy.ops.wm.read_factory_settings(use_empty=True)
pebble = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
if mutation == "no_gradient":
    spec["painted_shading"]["base_tint"] = spec["painted_shading"]["top_tint"]
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is pebble)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
