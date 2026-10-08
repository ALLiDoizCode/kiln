"""Write a small .glb with one known defect of each kind, to prove mesh_defects.py counts them.

    tools/bl make_broken_fixture.py <out.glb>

A 1 m cube (as 12 triangles) with: its top face removed (a hole: 4 boundary edges, 1 ring);
a fin, one triangle standing on a bottom edge (that edge then has 3 faces: 1 non-manifold edge,
and 2 more boundary edges on the same ring count +1); one triangle floating apart (a loose
piece, 3 boundary edges, 1 ring); one triangle with its three corners on a line (a degenerate
face, a loose piece, 3 boundary edges, 1 ring).
Expected after welding: triangles 13, pieces 3, small_pieces 0 (each stray piece is over 1% of 13),
non_manifold_edges 1, degenerate_faces 1, boundary_edges 12, boundary_loops 4.
"""
import sys

import bmesh
import bpy

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
top = max(bm.faces, key=lambda f: f.calc_center_median().z)
bmesh.ops.delete(bm, geom=[top], context="FACES_ONLY")
bmesh.ops.triangulate(bm, faces=bm.faces[:])
bottom = [e for e in bm.edges if all(v.co.z < 0 for v in e.verts) and len(e.link_faces) == 2
          and abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-6 and e.verts[0].co.x > 0][0]
tip = bm.verts.new((1.2, 0.0, -1.0))
bm.faces.new((bottom.verts[0], bottom.verts[1], tip))
a, b, c = (bm.verts.new(p) for p in ((3, 0, 0), (3.3, 0, 0), (3, 0.3, 0)))
bm.faces.new((a, b, c))
d, e, f = (bm.verts.new(p) for p in ((5, 0, 0), (5.5, 0, 0), (6, 0, 0)))
bm.faces.new((d, e, f))
mesh = bpy.data.meshes.new("broken")
bm.to_mesh(mesh); bm.free()
obj = bpy.data.objects.new("broken", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB")
