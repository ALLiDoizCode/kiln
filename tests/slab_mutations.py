"""Export slab_1 with its paint broken one way, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants, so the named check must fail.

Usage: tools/bl tests/slab_mutations.py <mutation> <out.glb>

  none       built and painted as the gate does it
  lit_joins  painted as one solid and not piece by piece (ADR 13): where one plate passes through
             another it counts as an exposed edge and is lit, and the join gets only the shadow a
             fifth of the sky hidden would give
  dark_paint painted with tints a quarter as light as the brief's: in the viewer's picture the
             sides the sun does not reach are lost (gate L4d). The load test, which holds texels
             to the manifest's tints, fails it too; a spec that asked for such tints would not
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
if mutation not in ("none", "lit_joins", "dark_paint"):
    raise RuntimeError(f"no mutation called {mutation}")
asset = Asset("slab_1")
spec = asset.spec()
bpy.ops.wm.read_factory_settings(use_empty=True)
slab = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
if mutation == "lit_joins":
    paint.SPLIT_PIECES = False
if mutation == "dark_paint":
    spec["painted_shading"].update(base_tint="#4a4a52", top_tint="#6c6c6c")
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is slab)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
