"""Gate L5: fixed-camera review renders and a contact sheet.

Cameras are framed from the spec's bounds, not the mesh's, so an asset built
at the wrong size or place looks wrong instead of being quietly re-framed.
Views are named from the asset's point of view: "front" looks at its front.

Usage: tools/bl tools/review_render.py <asset> [phase]
"""

import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import Asset, conventions, script_args

args = script_args()
asset = Asset(args[0])
phase = args[1] if len(args) > 1 else "final"
spec = asset.spec()
review = conventions()["review"]
out_dir = asset.source / "review" / phase
out_dir.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(asset.blend))
scene = bpy.context.scene

lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
centre = (lo + hi) / 2
radius = (hi - lo).length / 2

# Where the camera sits relative to the asset, and (for the top view) which
# way is up on screen. The asset's front faces -Y.
VIEWS = {
    "front": (Vector((0, -1, 0)), "ORTHO"),
    "right": (Vector((1, 0, 0)), "ORTHO"),
    "back": (Vector((0, 1, 0)), "ORTHO"),
    "top": (Vector((0, 0, 1)), "ORTHO"),
    "three_quarter": (Vector((1, -1, 0.7)).normalized(), "PERSP"),
}

scene.render.engine = "BLENDER_EEVEE"
scene.eevee.taa_render_samples = review["eevee_samples"]
scene.render.resolution_x = scene.render.resolution_y = review["tile_px"]
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("review_world")
background = world.node_tree.nodes["Background"]
background.inputs["Color"].default_value = (0.18, 0.19, 0.21, 1)
background.inputs["Strength"].default_value = 1.0
scene.world = world

sun_data = bpy.data.lights.new("review_sun", "SUN")
sun_data.energy = 3.0
sun = bpy.data.objects.new("review_sun", sun_data)
# Light travels from the asset's front-left and above, so the front is lit.
sun.rotation_euler = Vector((0.4, 0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(sun)

# A weaker light from the opposite side, so the back and right views are readable.
fill_data = bpy.data.lights.new("review_fill", "SUN")
fill_data.energy = 1.2
fill_data.use_shadow = False
fill = bpy.data.objects.new("review_fill", fill_data)
fill.rotation_euler = Vector((-0.6, -0.5, -0.4)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(fill)

camera_data = bpy.data.cameras.new("review_camera")
camera = bpy.data.objects.new("review_camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera


def aim(view):
    direction, kind = VIEWS[view]
    camera_data.type = kind
    if kind == "ORTHO":
        camera_data.ortho_scale = radius * 2.2
        distance = radius * 4
    else:
        camera_data.lens = 50
        distance = radius * 4.2
    camera.location = centre + direction * distance
    camera.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera_data.clip_start, camera_data.clip_end = 0.01, distance + radius * 4


def render_pass(name):
    tiles = []
    for view in review["views"]:
        aim(view)
        path = out_dir / f"{name}_{view}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.is_file():
            raise RuntimeError(f"render produced no file: {path}")
        tiles.append(path)
    return tiles


def flat(name, colour):
    material = bpy.data.materials.new(name)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = colour
    bsdf.inputs["Roughness"].default_value = 0.9
    return material


tiles = render_pass("material")

# Clay with the modelled edges drawn on top: shows form and topology with no
# material to hide behind. The file is never saved, so nothing is restored.
clay, wire = flat("review_clay", (0.6, 0.6, 0.6, 1)), flat("review_wire", (0.02, 0.02, 0.02, 1))
for name in spec["objects"]:
    obj = bpy.data.objects[name]
    obj.data.materials.clear()
    obj.data.materials.append(clay)
    obj.data.materials.append(wire)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
    modifier = obj.modifiers.new("review_wire", "WIREFRAME")
    modifier.use_replace = False
    modifier.material_offset = 1
    modifier.thickness = radius * 0.012
tiles += render_pass("clay_wire")

sheet = out_dir / "sheet.png"
dims = " x ".join(f"{b - a:g}" for a, b in zip(lo, hi))
subprocess.run(
    ["magick", "montage", "-background", "#202124", "-fill", "white", "-pointsize", "18"]
    + [arg for tile in tiles for arg in ("-label", tile.stem, str(tile))]
    + ["-tile", f"{len(review['views'])}x", "-geometry", "+4+4",
       "-title", f"{asset.name} / {phase} / spec {dims} m (x, y, z)", str(sheet)],
    check=True,
)
print(f"review sheet {sheet}")
