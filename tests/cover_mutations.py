"""Export a mossy cover variant with its growth painted wrong one way, for tests/run.sh to load in Bevy.

The real manifest still says what the brief wants, so the named check must fail. These are the
rock's growth mutations (tests/paint_mutations.py) on shapes the rock is not: a slab and a pebble
with no upright open face, a stack with no open face above its wash, a standing stone with no
near-level one. The load test measures each on the surface it has.

Usage: tools/bl tests/cover_mutations.py <asset> <mutation> <out.glb>

  growth_everywhere       the wash reaches far above the asset's top
  no_growth_edges         no growth along upper edges
  no_growth_up            no growth on faces near level
  growth_carpets_the_top  growth over all of every face near level
  growth_not_darker       patches at the stone's own lightness
  growth_broad_patches    patches three times the size asked for
  growth_on_wood          a log's wood painted as its bark is: growth on the broken and sawn ends
  packed_as_boxes         nothing painted wrong: the same paint on the same surface, laid out in the texture another
                          way (Blender's box packer, as tools/paint.py packed before `pack`). A check of the surface
                          reads this file as it reads the gated one.
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
want = spec["painted_shading"]
if mutation == "growth_everywhere":
    want["growth_height_m"] = 50.0
elif mutation == "no_growth_edges":
    want["growth_edges"] = 0.0
elif mutation == "no_growth_up":
    want["growth_up"] = 0.0
elif mutation == "growth_carpets_the_top":
    want["growth_up"] = 1.0
elif mutation == "growth_not_darker":
    want["growth_darker"] = 0.0
elif mutation == "growth_broad_patches":
    want["growth_patch_m"] *= 3
elif mutation == "packed_as_boxes":
    def boxes(objects, skip, gap, height):
        """Another layout of the same islands: packed by their boxes, the margin on every side of each, shrunk under the palette strip."""
        for operator, options in ((bpy.ops.object.mode_set, {"mode": "EDIT"}), (bpy.ops.uv.pack_islands, {"rotate": True, "scale": True, "margin_method": "FRACTION", "margin": gap, "shape_method": "AABB"}), (bpy.ops.object.mode_set, {"mode": "OBJECT"})):
            if operator(**options) != {"FINISHED"}:
                raise RuntimeError(f"{operator.idname()} failed")
        if height < 1.0:
            for obj in objects:
                for corner in obj.data.uv_layers[paint.UV_LAYER].data:
                    corner.uv = corner.uv * height

    paint.pack = boxes
elif mutation != "growth_on_wood":
    raise RuntimeError(f"no mutation called {mutation}")
bpy.ops.wm.read_factory_settings(use_empty=True)
built = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
if mutation == "growth_on_wood":
    spec["log"]["wood"] = "none of its materials"  # the painter no longer knows which material is wood
paint.apply(spec, conventions())
for obj in bpy.data.objects:
    obj.select_set(obj is built)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
share_textures(out)  # two materials on one painted texture (a log's bark and wood) share it, as tools/export.py leaves them
