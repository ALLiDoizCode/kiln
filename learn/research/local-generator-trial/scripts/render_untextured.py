"""Render a model without its textures, with its edges drawn, so the layout of its polygons
can be judged the way the videos' author judges it. Read-only.

    tools/bl render_untextured.py <model.glb|.fbx> <out folder> [pixels, default 1600]

Writes <name>_wire_three_quarter.png and <name>_wire_back.png: every material replaced by one
grey with dark lines along every edge (Cycles' Wireframe node, lines about a pixel and a half
wide, triangles as stored: a quad in a .glb is already two triangles). Cycles on the CPU.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
pixels = int(args[2]) if len(args) > 2 else 1600
name = os.path.splitext(os.path.basename(source))[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
if source.lower().endswith(".fbx"):
    bpy.ops.import_scene.fbx(filepath=source)
else:
    bpy.ops.import_scene.gltf(filepath=source, merge_vertices=True)
scene = bpy.context.scene

clay = bpy.data.materials.new("clay_wire")
clay.use_nodes = True
nodes, links = clay.node_tree.nodes, clay.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.9
wire = nodes.new("ShaderNodeWireframe")
wire.use_pixel_size = True
wire.inputs["Size"].default_value = 1.5
mix = nodes.new("ShaderNodeMix")
mix.data_type = "RGBA"
mix.inputs["A"].default_value = (0.72, 0.72, 0.72, 1)
mix.inputs["B"].default_value = (0.03, 0.03, 0.03, 1)
links.new(wire.outputs["Fac"], mix.inputs["Factor"])
links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])

low, high = Vector((1e9,) * 3), Vector((-1e9,) * 3)
for obj in scene.objects:
    if obj.type != "MESH":
        continue
    obj.data.materials.clear()
    obj.data.materials.append(clay)
    for poly in obj.data.polygons:
        poly.use_smooth = False  # flat faces show the true polygons, not the stored normals
    for v in obj.data.vertices:
        p = obj.matrix_world @ v.co
        for i in range(3):
            low[i] = min(low[i], p[i]); high[i] = max(high[i], p[i])
centre, radius = (low + high) / 2, (high - low).length / 2

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 48
scene.cycles.seed = 1
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = pixels
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("white")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 50
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = radius * 200
os.makedirs(out, exist_ok=True)
for suffix, azimuth in (("three_quarter", 35), ("back", 215)):
    az, el = math.radians(azimuth), math.radians(20)
    direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = centre + direction * (radius / math.sin(math.atan(18 / 50)) / 0.8)
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(out, f"{name}_wire_{suffix}.png")
    bpy.ops.render.render(write_still=True)
    print("WIRE " + scene.render.filepath)
