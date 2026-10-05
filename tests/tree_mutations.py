"""Export tree_1 with its foliage broken one way, for tests/run.sh to load in Bevy.

Each mutation builds the tree, paints it from a changed spec or changes the
result, and exports it as tools/export.py would. The real manifest still says
what the brief wants, so the named check must fail.

Usage: tools/bl tests/tree_mutations.py <mutation> <out.glb> [painted.blend]
       tools/bl tests/tree_mutations.py painted <out.blend>

`painted` saves the tree built and painted with nothing wrong. A mutation in
AFTER_PAINT changes only what painting left, so given that file it starts from
it instead of building and baking a tree of its own; the export is the same
either way, byte for byte.
"""

import runpy
import sys
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import foliage
import paint
from pipeline import Asset, conventions, linear_rgb, script_args, share_textures

AFTER_PAINT = ("none", "single_sided", "gradient_within_piece", "no_cores", "core_open", "bark_inside_out", "two_textures", "glossy_leaves")

mutation, out, *painted = script_args()
asset = Asset("tree_1")
spec = asset.spec()
want = spec["foliage"]
conv = conventions()
if painted:
    if mutation not in AFTER_PAINT:
        raise RuntimeError(f"{mutation} is not in AFTER_PAINT: it must build and paint a tree of its own")
    result = bpy.ops.wm.open_mainfile(filepath=painted[0])
    if result != {"FINISHED"}:
        raise RuntimeError(f"open failed: {result}")
    tree = bpy.data.objects["tree_1"]
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    tree = runpy.run_path(str(asset.source / "build.py"))["build"](spec)
leaf = bpy.data.materials[want["material"]]
slot = [s.material.name for s in tree.material_slots].index(want["material"])

# Painted from a changed spec.
if mutation == "one_tone":
    # Every piece of a shade the same colour: neighbours no longer differ.
    want["variation"] = 0.0
elif mutation == "no_gradient":
    want["under_tint"] = want["top_tint"]
elif mutation == "grey_underside":
    # Darker underneath, but no bluer.
    want["under_tint"] = "#8c8c8c"
elif mutation == "wrong_leaf_colour":
    # An autumn palette, where the brief and the manifest say green.
    spec["materials"][want["material"]] = "#c8782a"
elif mutation == "light_core":
    # The solid under the leaves as light as the leaves on top of it.
    want["core_tint"] = "#ffffff"
elif mutation == "dark_underside":
    # The underside of a pad, and its core, as dark as the bark: limbs seen from below are lost against the leaves.
    want["under_tint"], want["core_tint"] = "#6f96a6", "#527a86"
elif mutation == "wrong_bark_colour":
    # Bark painted over a brown a fifth darker than the brief's and the manifest's (#6e513d for #7a5a44): grain and all, on the wrong colour.
    bark = next(s.material for s in tree.material_slots if s.material.name != want["material"])
    bark.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*linear_rgb("#6e513d"), 1.0)
elif mutation == "no_grain":
    # Bark with its gradient, edge light and blotches, and no grain: flat brown planes at arm's length.
    spec["painted_shading"]["grain"] = 0.0
elif mutation == "no_close_texels":
    # The trunk a player stands against given no more texels than a twig.
    del spec["painted_shading"]["close_height_m"], spec["painted_shading"]["close_texels_per_m"]
elif mutation == "grain_across":
    # The grain's two directions swapped: streaks run round each limb like hoops.
    values = [0.0] * (len(tree.data.loops) * 3)
    tree.data.attributes["grain"].data.foreach_get("vector", values)
    values[0::3], values[1::3] = values[1::3], values[0::3]
    tree.data.attributes["grain"].data.foreach_set("vector", values)

if not painted:
    paint.apply(spec, conv)
if mutation == "painted":
    result = bpy.ops.wm.save_as_mainfile(filepath=out, check_existing=False)
    if result != {"FINISHED"}:
        raise RuntimeError(f"save failed: {result}")
    sys.exit(0)

# Changed after painting.
if mutation == "single_sided":
    leaf.use_backface_culling = True
elif mutation == "gradient_within_piece":
    # Each piece's corners spread over the palette, so a piece is no longer one flat colour.
    size, swatch = spec["painted_shading"]["texture_px"], conv["foliage"]["swatch_px"]
    uvs = tree.data.uv_layers[0].data
    for polygon in tree.data.polygons:
        if polygon.material_index == slot:
            for step, corner in enumerate(polygon.loop_indices):
                uvs[corner].uv = foliage.swatch_uv((polygon.index + step * 7) % (want["shades"] * want["tones"]), size, swatch)
elif mutation in ("no_cores", "core_open"):
    # Every core removed (pads are open shells again), or one face missing from each core.
    bm = bmesh.new()
    bm.from_mesh(tree.data)
    cores = foliage.cores_of(bm, slot)
    bmesh.ops.delete(bm, geom=[f for core in cores for f in (core if mutation == "no_cores" else core[:1])], context="FACES")
    bm.to_mesh(tree.data)
    bm.free()
elif mutation == "glossy_leaves":
    # The leaf material with the gloss every material has unless told otherwise: a piece the sun grazes, seen
    # from under it, shows the sun's glare and none of its own colour (near-white among dark neighbours).
    leaf.node_tree.nodes["Principled BSDF"].inputs["Specular IOR Level"].default_value = 0.5
elif mutation == "bark_inside_out":
    bm = bmesh.new()
    bm.from_mesh(tree.data)
    bmesh.ops.reverse_faces(bm, faces=[f for f in bm.faces if f.material_index != slot])
    bm.to_mesh(tree.data)
    bm.free()

tree.select_set(True)
result = bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True, export_apply=True, export_normals=True, export_texcoords=True)
if result != {"FINISHED"}:
    raise RuntimeError(f"export failed: {result}")
if mutation != "two_textures":
    share_textures(out)
