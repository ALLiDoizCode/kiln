"""The tracer fixture: a boot profile in the YZ plane, extruded along X.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

import bmesh
import bpy

X_MIN, X_MAX = -0.5, 1.0

# Side profile as (y, z), counter-clockwise seen from +X. Front is -Y, so the
# toe is at y = -1.5. The points at (0.5, 0.4) and (-0.3, 0.0) exist only so
# the caps split into three quads instead of one concave n-gon.
PROFILE = [
    (-1.5, 0.0), (-0.3, 0.0), (0.5, 0.0), (0.5, 0.4),
    (0.5, 1.0), (-0.3, 1.0), (-0.3, 0.4), (-1.5, 0.4),
]
# Indices into PROFILE for the three cap quads: toe, lower leg, upper leg.
CAP_QUADS = [(0, 1, 6, 7), (1, 2, 3, 6), (6, 3, 4, 5)]


def build():
    bm = bmesh.new()
    left = [bm.verts.new((X_MIN, y, z)) for y, z in PROFILE]
    right = [bm.verts.new((X_MAX, y, z)) for y, z in PROFILE]

    n = len(PROFILE)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((left[i], left[j], right[j], right[i]))
    for quad in CAP_QUADS:
        bm.faces.new([right[i] for i in quad])
        bm.faces.new([left[i] for i in reversed(quad)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("tracer")
    bm.to_mesh(mesh)
    bm.free()

    material = bpy.data.materials.new("m_tracer")
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.80, 0.25, 0.10, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Metallic"].default_value = 0.0
    mesh.materials.append(material)

    obj = bpy.data.objects.new("tracer", mesh)
    bpy.context.scene.collection.objects.link(obj)
