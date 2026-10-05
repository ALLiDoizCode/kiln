"""Export rubble_1 with its paint broken one way, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants, so the named check must fail.

Usage: tools/bl tests/rubble_mutations.py <mutation> <out.glb>

  no_contact_shadow  painted as one solid with no crevice shadow, as a group of stones was before
                     stones that touch shaded each other: nothing dark lies between the two stones
                     that are within the touching distance (`[scatter] touch_m`)
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
if mutation not in ("no_contact_shadow",):
    raise RuntimeError(f"no mutation called {mutation}")
asset = Asset("rubble_1")
spec = asset.spec()
bpy.ops.wm.read_factory_settings(use_empty=True)
rubble = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
if mutation == "no_contact_shadow":
    paint.SPLIT_PIECES = False
    for key in ("crevice_shadow", "crevice_width_m"):
        spec["painted_shading"].pop(key, None)
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is rubble)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
