"""Export slab_1 with its paint broken one way, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants, so the named check must fail.

Usage: tools/bl tests/slab_mutations.py <mutation> <out.glb>

  none       built and painted as the gate does it
  lit_joins  painted as one solid and not piece by piece (ADR 13): where one plate passes through
             another it counts as an exposed edge and is lit, and the join gets only the shadow a
             fifth of the sky hidden would give
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
if mutation not in ("none", "lit_joins"):
    raise RuntimeError(f"no mutation called {mutation}")
asset = Asset("slab_1")
spec = asset.spec()
bpy.ops.wm.read_factory_settings(use_empty=True)
slab = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
if mutation == "lit_joins":
    paint.SPLIT_PIECES = False
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is slab)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
