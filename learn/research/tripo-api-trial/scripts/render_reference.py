"""Render reference images of a model file, for use as the input of an image-to-3D generator.

    tools/bl render_reference.py <model.glb> <out folder> [pixels, default 2048]

Writes three square PNG files of the same object, with the object spanning 78% of the frame in its wider direction, on white:
  <name>_front.png                     strict front (the object's -Y side in Blender, glTF +Z),
                                       orthographic camera at mid height, even light, no ground
  <name>_three_quarter.png             perspective camera (100 mm, to keep perspective mild) 35 degrees round and 20 degrees
                                       up, even light, no ground, no cast shadow
  <name>_three_quarter_hard_light.png  the same camera, one hard sun, a white ground that takes the
                                       shadow: deliberately breaks "even light, no shadow"
Even light is a uniform white sky plus a weak sun from over the camera's shoulder so that faces
can be told apart. Cycles on the CPU, 96 samples, Standard view transform, fixed seed. Two runs
do not give the same bytes (the checksums differ; the pixels were not compared), so keep the files. A render of a 3D model is an easy case for a generator: clean edges,
no noise, no perspective surprises.
"""
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
source, out = args[0], args[1]
pixels = int(args[2]) if len(args) > 2 else 2048
name = os.path.splitext(os.path.basename(source))[0]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source, merge_vertices=True)
scene = bpy.context.scene
low, high = Vector((1e9,) * 3), Vector((-1e9,) * 3)
for obj in scene.objects:
    if obj.type == "MESH":
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            for i in range(3):
                low[i] = min(low[i], p[i]); high[i] = max(high[i], p[i])
centre, dims = (low + high) / 2, high - low
points = [obj.matrix_world @ v.co for obj in scene.objects if obj.type == "MESH" for v in obj.data.vertices]
points = points[::max(1, len(points) // 5000)]  # a dense mesh does not need every point for framing
radius = dims.length / 2

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 96
scene.cycles.seed = 1
scene.cycles.use_denoising = False
scene.render.resolution_x = scene.render.resolution_y = pixels
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"

world = bpy.data.worlds.new("white")
scene.world = world
world.use_nodes = True
background = world.node_tree.nodes["Background"]
background.inputs["Color"].default_value = (1, 1, 1, 1)
# The camera always sees a pure white sky; only the light the sky gives is turned down for the
# hard-light picture.
tree = world.node_tree
light_path = tree.nodes.new("ShaderNodeLightPath")
mix = tree.nodes.new("ShaderNodeMix")
mix.data_type = "FLOAT"
mix.inputs["B"].default_value = 1.0
tree.links.new(light_path.outputs["Is Camera Ray"], mix.inputs["Factor"])
tree.links.new(mix.outputs["Result"], background.inputs["Strength"])

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
sun_data = bpy.data.lights.new("sun", "SUN")
sun = bpy.data.objects.new("sun", sun_data)
scene.collection.objects.link(sun)

ground_mesh = bpy.data.meshes.new("ground")
s = radius * 40
ground_mesh.from_pydata([(-s, -s, low.z), (s, -s, low.z), (s, s, low.z), (-s, s, low.z)], [], [(0, 1, 2, 3)])
ground = bpy.data.objects.new("ground", ground_mesh)
scene.collection.objects.link(ground)
white = bpy.data.materials.new("ground_white")
white.use_nodes = True
white.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 1, 1, 1)
white.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
ground_mesh.materials.append(white)


def aim(obj, origin, target):
    obj.location = origin
    obj.rotation_euler = (Vector(target) - Vector(origin)).to_track_quat("-Z", "Y").to_euler()


def shot(suffix, azimuth, elevation, ortho, hard):
    az, el = math.radians(azimuth), math.radians(elevation)
    direction = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    fill = 0.78
    def extent():
        # the larger of the width and height the object's points take up, as a share of the frame
        bpy.context.view_layer.update()
        seen = [world_to_camera_view(scene, cam, c) for c in points]
        return max(max(s.x for s in seen) - min(s.x for s in seen), max(s.y for s in seen) - min(s.y for s in seen))

    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = 1.0
        aim(cam, centre + direction * radius * 10, centre)
        cam_data.ortho_scale = extent() / fill
    else:
        cam_data.type = "PERSP"
        cam_data.lens = 100
        cam_data.sensor_width = 36
        near, far = radius * 1.05, radius * 100
        for _ in range(40):  # halve the range until the box takes up `fill` of the frame
            middle = (near + far) / 2
            aim(cam, centre + direction * middle, centre)
            if extent() > fill:
                near = middle
            else:
                far = middle
    cam_data.clip_end = radius * 200
    ground.hide_render = not hard
    if hard:
        mix.inputs["A"].default_value = 0.35
        sun_data.energy = 5.0
        sun_data.angle = math.radians(0.5)
        aim(sun, centre + Vector((-1.0, -0.6, 1.2)) * radius * 10, centre)
    else:
        mix.inputs["A"].default_value = 1.0
        sun_data.energy = 1.0
        sun_data.angle = math.radians(40)
        aim(sun, centre + (direction + Vector((-0.5, 0, 0.7))) * radius * 10, centre)
    scene.render.filepath = os.path.join(out, f"{name}_{suffix}.png")
    bpy.ops.render.render(write_still=True)
    print("REFERENCE " + scene.render.filepath)


os.makedirs(out, exist_ok=True)
shot("front", 0, 0, True, False)
shot("three_quarter", 35, 20, False, False)
shot("three_quarter_hard_light", 35, 20, False, True)
