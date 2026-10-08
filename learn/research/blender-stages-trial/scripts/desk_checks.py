"""Small checks of what the desk research (tripo-guidance-and-blender-scripting.md, Part 2)
left as "not tested". Read-only except for one .glb written to the folder given.

    tools/bl desk_checks.py <textured.glb> <folder for output>

Prints lines starting CHECK:
  factory settings of the bake (Cycles samples, device, denoising, margin)
  whether the 3D Print Toolbox operators exist
  whether Image.scale() reaches the exported file, with and without packing the image again
"""
import json
import os
import sys

import bpy

source, folder = sys.argv[sys.argv.index("--") + 1:][:2]
scene = bpy.context.scene
scene.render.engine = "CYCLES"
print("CHECK " + json.dumps({"cycles_samples": scene.cycles.samples, "cycles_device": scene.cycles.device,
                             "denoising": scene.cycles.use_denoising, "adaptive_sampling": scene.cycles.use_adaptive_sampling,
                             "bake_margin": scene.render.bake.margin, "bake_margin_type": scene.render.bake.margin_type,
                             "compute_device_type": bpy.context.preferences.addons["cycles"].preferences.compute_device_type,
                             "print3d_operators": [n for n in dir(bpy.ops.mesh) if "print3d" in n],
                             "addons_enabled": sorted(a.module for a in bpy.context.preferences.addons)}))
for name, repack in (("scaled_only", False), ("scaled_and_packed_again", True)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=source, merge_vertices=True)
    report = []
    for image in bpy.data.images:
        if image.size[0] > 1024:
            before = (list(image.size), image.is_dirty, bool(image.packed_file))
            image.scale(1024, 1024)
            if repack:
                image.pack()
            report.append({"image": image.name, "before": before, "after": (list(image.size), image.is_dirty, bool(image.packed_file))})
    target = os.path.join(folder, f"desk_check_{name}.glb")
    bpy.ops.export_scene.gltf(filepath=target, export_format="GLB", export_image_format="AUTO")
    print("CHECK " + json.dumps({"case": name, "images": report, "written": target}))
