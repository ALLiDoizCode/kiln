"""Clean a model by the rules that harmed none of the models they were tried on. Runs inside
the pinned Blender, not under the system Python:

    tools/bl kiln/blender_scripts/clean.py <in.glb> <out.glb> <facts.json>

Each mesh is cleaned on its own, in this order:

  weld            vertices closer than a hundredth of a millimetre become one
  dissolve        edges shorter than a thousandth of a millimetre, and the faces left with
                  no area, are removed. Ten times that already changed the surface of the
                  trial's dense crate: a triangle standing on an edge became a hole
  loose bits      vertices on no edge and edges on no face are deleted
  hidden pieces   a separate piece of the mesh that cannot be seen from outside is deleted.
                  From up to 40 of its faces rays are sent in 26 directions; the piece is
                  hidden when every ray hits the mesh. This needs a closed shell round it: a
                  piece inside a box with a gap is kept. A piece inside another mesh is kept.
  turned faces    within each piece, faces that wind the other way from the faces round them
                  are turned to agree. A whole piece is never turned over: whichever way most
                  of its surface faces is taken as meant, so a flat card or a room seen from
                  inside stays as it was made. Where a face is turned, its stored normals are
                  turned with it.

Holes are not filled and no piece is deleted for being small: both damaged models in the
trial (learn/research/blender-stages-trial.md, section 4), where a small piece was a spike
and, once, the whole visible crate.

The input is only read. <facts.json> gets what each rule did, summed over the meshes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
import numpy as np  # noqa: E402  (bundled with Blender)
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402
import kiln_bl as lib  # noqa: E402

WELD = 1e-5        # metres: a hundredth of a millimetre
DEGENERATE = 1e-6  # metres: a thousandth of a millimetre
DIRECTIONS = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1)
              for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]


def pieces_of(bm):
    """Lists of faces, one list per piece: faces that share a vertex are in one piece."""
    bm.faces.index_update()
    seen, pieces = set(), []
    for face in bm.faces:
        if face.index in seen:
            continue
        piece, stack = [], [face]
        seen.add(face.index)
        while stack:
            current = stack.pop()
            piece.append(current)
            for vertex in current.verts:
                for other in vertex.link_faces:
                    if other.index not in seen:
                        seen.add(other.index)
                        stack.append(other)
        pieces.append(piece)
    return pieces


def hidden(piece, tree):
    for face in piece[::max(1, len(piece) // 40)]:
        centre = face.calc_center_median()
        for direction in DIRECTIONS:
            if tree.ray_cast(centre + direction * WELD, direction)[0] is None:
                return False
    return True


def turn_stored_normals(mesh, turned):
    """Turn the stored normals of the faces in `turned` (one flag per face) that now point
    into the surface. Without this a turned face is still lit from behind."""
    if not mesh.has_custom_normals:
        return
    faces = len(mesh.polygons)
    corners = np.empty(len(mesh.loops) * 3, dtype=np.float32)
    mesh.corner_normals.foreach_get("vector", corners)
    corners = corners.reshape(-1, 3)
    facing = np.empty(faces * 3, dtype=np.float32)
    mesh.polygon_normals.foreach_get("vector", facing)
    sides = np.empty(faces, dtype=np.int32)
    mesh.polygons.foreach_get("loop_total", sides)
    face_of_corner = np.repeat(np.arange(faces), sides)
    facing = facing.reshape(-1, 3)[face_of_corner]
    wrong = np.asarray(turned, dtype=bool)[face_of_corner] & ((corners * facing).sum(axis=1) < 0.0)
    corners[wrong] *= -1.0
    mesh.normals_split_custom_set(corners)


def clean(mesh, facts):
    bm = bmesh.new()
    bm.from_mesh(mesh)

    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=WELD)
    facts["vertices_joined"] += before - len(bm.verts)

    before = len(bm.faces)
    bmesh.ops.dissolve_degenerate(bm, dist=DEGENERATE, edges=bm.edges)
    facts["faces_dissolved"] += before - len(bm.faces)

    wires = [e for e in bm.edges if not e.link_faces]
    bmesh.ops.delete(bm, geom=wires, context="EDGES")
    lone = [v for v in bm.verts if not v.link_edges]
    bmesh.ops.delete(bm, geom=lone, context="VERTS")
    facts["loose_bits_deleted"] += len(wires) + len(lone)

    pieces = pieces_of(bm)
    if len(pieces) > 1:
        tree = BVHTree.FromBMesh(bm)
        doomed = [piece for piece in pieces if hidden(piece, tree)]
        if len(doomed) < len(pieces):  # never the whole mesh
            facts["hidden_pieces_deleted"] += len(doomed)
            facts["hidden_triangles_deleted"] += sum(len(f.verts) - 2 for p in doomed for f in p)
            bmesh.ops.delete(bm, geom=[f for p in doomed for f in p], context="FACES")
            pieces = pieces_of(bm)

    bm.normal_update()
    bm.faces.index_update()
    was = [face.normal.copy() for face in bm.faces]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    for piece in pieces:
        turned = sum(f.calc_area() for f in piece if f.normal.dot(was[f.index]) < 0.0)
        if 2.0 * turned > sum(f.calc_area() for f in piece):
            bmesh.ops.reverse_faces(bm, faces=piece)
    bm.normal_update()
    turned = [face.normal.dot(was[face.index]) < 0.0 for face in bm.faces]
    facts["faces_turned"] += sum(turned)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    if any(turned):
        turn_stored_normals(mesh, turned)


def main(source, target, facts_path):
    facts = {"vertices_joined": 0, "faces_dissolved": 0, "loose_bits_deleted": 0,
             "hidden_pieces_deleted": 0, "hidden_triangles_deleted": 0, "faces_turned": 0}
    for obj in lib.read(source):
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        clean(obj.data, facts)
    lib.write(target)
    lib.save_facts(facts_path, facts)


if __name__ == "__main__":
    main(*lib.arguments())
