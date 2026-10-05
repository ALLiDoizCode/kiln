"""Export a plant changed one way, for tests/run.sh to load in Bevy.

Usage: tools/bl tests/plant_mutations.py <asset> <mutation> <out.glb>

  fine_texture  nothing wrong: the same plant painted on a texture twice the size a side. The load test
                samples it four times as finely, and what it finds on the surface must not change kind:
                a bush's stems are tubes that bend, convex all round, and have no inside corner at any size.
"""

import runpy
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import paint
from pipeline import Asset, conventions, script_args, share_textures

name, mutation, out = script_args()
asset = Asset(name)
spec = asset.spec()
if mutation == "fine_texture":
    spec["painted_shading"]["texture_px"] *= 2
else:
    raise RuntimeError(f"no mutation called {mutation}")
bpy.ops.wm.read_factory_settings(use_empty=True)
built = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is built)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
share_textures(out)  # the stems and the leaves read one painted texture, as tools/export.py leaves them
