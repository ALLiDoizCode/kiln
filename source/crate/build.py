"""Supply crate: a cube whose six faces each have a raised frame and a recessed panel.

One closed mesh. Per face: four mitred frame quads, four recess walls, one panel.
Run through tools/build.py.
"""

import bmesh
import bpy
from mathutils import Vector
from pipeline import linear_rgb

SIDE = 0.8
FRAME = 0.1  # frame member width
RECESS = 0.05  # how far each panel sits below the frame

# Slot order; colours come from the spec.
MATERIALS = ["m_crate_frame", "m_crate_panel"]
FRAME_SLOT, PANEL_SLOT = 0, 1

X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
# (normal, u, v) per face, with u x v = normal so corners wind counter-clockwise
# when seen from outside.
FACES = [(X, Y, Z), (-X, Z, Y), (Y, Z, X), (-Y, X, Z), (Z, X, Y), (-Z, Y, X)]
CORNERS = [(-1, -1), (1, -1), (1, 1), (-1, 1)]


def build(spec):
    bm = bmesh.new()
    centre = Vector((0, 0, SIDE / 2))
    half = SIDE / 2
    verts = {}

    def vert(co):
        """Cube corners are shared by three faces; reuse them."""
        key = tuple(round(c, 6) for c in co)
        if key not in verts:
            verts[key] = bm.verts.new(co)
        return verts[key]

    def quad(points, slot):
        bm.faces.new([vert(p) for p in points]).material_index = slot

    for normal, u, v in FACES:
        face_centre = centre + normal * half
        outer = [face_centre + (u * a + v * b) * half for a, b in CORNERS]
        inner = [face_centre + (u * a + v * b) * (half - FRAME) for a, b in CORNERS]
        panel = [p - normal * RECESS for p in inner]
        for i in range(4):
            j = (i + 1) % 4
            quad((outer[i], outer[j], inner[j], inner[i]), FRAME_SLOT)
            quad((inner[i], inner[j], panel[j], panel[i]), FRAME_SLOT)
        quad(panel, PANEL_SLOT)

    mesh = bpy.data.meshes.new("crate")
    bm.to_mesh(mesh)
    bm.free()

    for name in MATERIALS:
        material = bpy.data.materials.new(name)
        bsdf = material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (*linear_rgb(spec["materials"][name]), 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
        bsdf.inputs["Metallic"].default_value = 0.0
        mesh.materials.append(material)

    obj = bpy.data.objects.new("crate", mesh)
    bpy.context.scene.collection.objects.link(obj)
