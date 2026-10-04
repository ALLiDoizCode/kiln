"""Export the rock with its painted shading broken one way, for tests/run.sh to load in Bevy.

Each mutation builds the rock, paints it from a changed spec or changes the
result, and exports it as tools/export.py would. The real manifest still
says what the brief wants, so the named check must fail.

Usage: tools/bl tests/paint_mutations.py <mutation> <out.glb>
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
asset = Asset("rock")
spec = asset.spec()
want = spec["painted_shading"]
bpy.ops.wm.read_factory_settings(use_empty=True)
rock = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
bsdf = rock.data.materials[0].node_tree.nodes["Principled BSDF"]
options = {}


def each_uv(change):
    for corner in rock.data.uv_layers[0].data:
        corner.uv = change(corner.uv)


# Painted from a changed spec.
if mutation == "no_gradient":
    want["base_tint"] = want["top_tint"]
elif mutation == "no_edge_light":
    want["edge_light"] = 0.0
elif mutation == "no_crevice_shadow":
    want["crevice_shadow"] = 0.0
elif mutation == "wrong_colour":
    bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
elif mutation == "burnt_out":
    # Paler than any rock, with a strong edge light on top: lit, its edges would clip to white.
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
elif mutation == "small_texture":
    want["texture_px"] = 256
elif mutation == "no_growth":
    for key in ("growth", "growth_height_m", "growth_up", "growth_edges"):
        del want[key]
elif mutation == "growth_everywhere":
    want["growth_height_m"] = 5.0
elif mutation == "no_growth_up":
    want["growth_up"] = 0.0
elif mutation == "growth_carpets_the_top":
    want["growth_up"] = 1.0
elif mutation == "no_growth_edges":
    want["growth_edges"] = 0.0
elif mutation == "no_blotches":
    want["blotch"] = 0.0
elif mutation == "harsh_blotches":
    want["blotch"] = 0.5
elif mutation == "speckle":
    # Blotches the size of a texel: grain, not broad patches.
    want["blotch_size_m"] = 0.02
elif mutation == "no_side_shade":
    want["side_shade"] = 0.0

if mutation != "unpainted":
    image = paint.apply(spec, conventions())

if mutation == "banded":
    # The gradient in a dozen flat steps per channel, as a texture saved with too few levels would be.
    import numpy

    texels = numpy.empty(len(image.pixels), dtype=numpy.float32)
    image.pixels.foreach_get(texels)
    image.pixels.foreach_set(numpy.round(texels * 12) / 12)
    image.pack()

# Changed after painting.
if mutation == "shrunk_uvs":
    each_uv(lambda uv: uv * 0.5)
elif mutation == "stacked_uvs":
    # Every face laid over the same triangle of the texture.
    for polygon in rock.data.polygons:
        for corner, uv in zip(polygon.loop_indices, ((0.1, 0.1), (0.9, 0.1), (0.5, 0.9), (0.1, 0.9))):
            rock.data.uv_layers[0].data[corner].uv = uv
elif mutation == "uvs_off_the_texture":
    each_uv(lambda uv: (uv[0] + 0.6, uv[1]))
elif mutation == "tinted_factor":
    # A multiply between the texture and the shader exports as a base colour factor.
    tree = rock.data.materials[0].node_tree
    mix = tree.nodes.new("ShaderNodeMix")
    mix.data_type, mix.blend_type = "RGBA", "MULTIPLY"
    mix.inputs["Factor"].default_value = 1.0
    mix.inputs["B"].default_value = (0.5, 0.5, 0.5, 1.0)
    tree.links.new(tree.nodes["paint"].outputs["Color"], mix.inputs["A"])
    tree.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
elif mutation == "jpeg":
    options["export_image_format"] = "JPEG"

rock.select_set(True)
result = bpy.ops.export_scene.gltf(
    filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True, **options
)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
