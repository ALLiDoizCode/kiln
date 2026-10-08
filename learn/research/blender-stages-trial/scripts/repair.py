"""Stage 2 of the trial: repair a mesh by fixed rules, each one optional and with its setting.

    tools/bl repair.py <in.glb> <out.glb> <facts.json> [name=value ...]

Steps, run in this order when their setting switches them on:
  weld=<metres>          join vertices closer than this (0 = off). bmesh.ops.remove_doubles
  degenerate=<metres>    collapse edges shorter than this and the faces that then have no area
                         (0 = off). bmesh.ops.dissolve_degenerate
  loose=true             delete vertices on no edge and edges on no face
  small_pieces=<share>   delete separate pieces holding less than this share of the whole
                         (0 = off; 0.01 is 1%). small_pieces_by=triangles|area says of what:
                         the triangle count, or the surface area
  hidden_pieces=true     delete separate pieces that cannot be seen from outside: from up to
                         40 points on a piece, rays are sent in 26 directions, and a piece is
                         hidden when every one of them hits the mesh
  recalc_normals=true    make the faces of each piece point outward. bmesh.ops.recalc_face_normals
  fill_holes=<sides>     fill holes of at most this many sides (-1 = off, 0 = every hole).
                         bmesh.ops.holes_fill, then the new faces are triangulated
  normals=keep|clear     keep the file's stored (custom) normals, or drop them so Blender works
                         normals out from the faces again
  sharp_angle=<degrees>  with normals=clear: edges whose faces meet at more than this are made
                         sharp (0 = everything smooth)
After each step the defects are counted on a copy welded at a millionth of a metre, as
scripts/mesh_defects.py does, and written to the facts as "after_<step>".
count_each=false counts only before and after (for dense meshes, where a count takes long:
about 12 seconds for 1.8 million triangles). count=false does not count at all.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import stagelib as lib  # noqa: E402

DEFAULTS = {"weld": 0.0, "degenerate": 0.0, "loose": False, "small_pieces": 0.0, "small_pieces_by": "area", "hidden_pieces": False,
            "recalc_normals": False, "fill_holes": -1, "normals": "keep", "sharp_angle": 30.0,
            "count_each": True, "count": True}


def welded_count(bm):
    copy = bm.copy()
    bmesh.ops.remove_doubles(copy, verts=copy.verts, dist=lib.WELD)
    copy.verts.index_update(); copy.edges.index_update(); copy.faces.index_update()
    out = lib.count(copy)
    copy.free()
    return out


def pieces_of(bm):
    """Lists of faces, one list per connected piece."""
    bm.faces.index_update()
    seen, pieces = set(), []
    for face in bm.faces:
        if face.index in seen:
            continue
        piece, stack = [], [face]
        seen.add(face.index)
        while stack:
            cur = stack.pop()
            piece.append(cur)
            for v in cur.verts:
                for other in v.link_faces:
                    if other.index not in seen:
                        seen.add(other.index)
                        stack.append(other)
        pieces.append(piece)
    return pieces


def main():
    source, target, facts_path, settings = lib.arguments(DEFAULTS)
    clock = lib.Clock()
    obj = lib.one_object(source)
    mesh = obj.data
    clock.lap("import")
    facts = {"stage": "repair", "source": source, "settings": settings, "before_object": lib.describe(obj)}
    low, high = lib.bounds(mesh)
    facts["bounds_before"] = [low, high]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    if not settings["count"]:
        settings["count_each"] = False
    else:
        facts["before"] = welded_count(bm)
    facts["surface_area_before"] = sum(f.calc_area() for f in bm.faces)
    clock.lap("count_before")
    done = []

    def after(step, extra=None):
        clock.lap(step)
        done.append(step)
        if settings["count_each"]:
            facts["after_" + step] = dict(welded_count(bm), **(extra or {}))
            clock.lap("count_after_" + step)
        elif extra:
            facts["after_" + step] = extra

    if settings["weld"] > 0:
        before = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=settings["weld"])
        after("weld", {"vertices_joined": before - len(bm.verts)})
    if settings["degenerate"] > 0:
        faces, verts = len(bm.faces), len(bm.verts)
        bmesh.ops.dissolve_degenerate(bm, dist=settings["degenerate"], edges=bm.edges)
        after("degenerate", {"faces_removed": faces - len(bm.faces), "vertices_removed": verts - len(bm.verts)})
    if settings["loose"]:
        wires = [e for e in bm.edges if not e.link_faces]
        bmesh.ops.delete(bm, geom=wires, context="EDGES")
        lone = [v for v in bm.verts if not v.link_edges]
        bmesh.ops.delete(bm, geom=lone, context="VERTS")
        after("loose", {"wire_edges_removed": len(wires), "vertices_removed": len(lone)})
    if settings["small_pieces"] > 0:
        pieces = pieces_of(bm)
        total = sum(len(f.verts) - 2 for f in bm.faces)
        area = sum(f.calc_area() for f in bm.faces)
        if settings["small_pieces_by"] == "triangles":
            doomed = [p for p in pieces if sum(len(f.verts) - 2 for f in p) < settings["small_pieces"] * total]
        else:
            doomed = [p for p in pieces if sum(f.calc_area() for f in p) < settings["small_pieces"] * area]
        lost_area = sum(f.calc_area() for p in doomed for f in p)
        lost = sum(len(f.verts) - 2 for p in doomed for f in p)
        bmesh.ops.delete(bm, geom=[f for p in doomed for f in p], context="FACES")
        after("small_pieces", {"pieces_removed": len(doomed), "triangles_removed": lost,
                               "share_of_surface_removed": lost_area / area if area else 0.0})
    if settings["hidden_pieces"]:
        from mathutils import Vector
        from mathutils.bvhtree import BVHTree
        tree = BVHTree.FromBMesh(bm)
        directions = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1)
                      for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]
        pieces = pieces_of(bm)
        area = sum(f.calc_area() for f in bm.faces)
        doomed = []
        for piece in pieces:
            step = max(1, len(piece) // 40)
            seen_from_outside = False
            for face in piece[::step]:
                centre = face.calc_center_median()
                for direction in directions:
                    if tree.ray_cast(centre + direction * 1e-5, direction)[0] is None:
                        seen_from_outside = True
                        break
                if seen_from_outside:
                    break
            if not seen_from_outside:
                doomed.append(piece)
        lost = sum(len(f.verts) - 2 for p in doomed for f in p)
        lost_area = sum(f.calc_area() for p in doomed for f in p)
        bmesh.ops.delete(bm, geom=[f for p in doomed for f in p], context="FACES")
        after("hidden_pieces", {"pieces_removed": len(doomed), "triangles_removed": lost,
                                "share_of_surface_removed": lost_area / area if area else 0.0})
    if settings["recalc_normals"]:
        before = [tuple(f.normal) for f in bm.faces]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.normal_update()
        turned = sum(1 for f, n in zip(bm.faces, before) if f.normal.dot(n) < 0.0)
        after("recalc_normals", {"faces_turned": turned})
    if settings["fill_holes"] >= 0:
        faces = len(bm.faces)
        result = bmesh.ops.holes_fill(bm, edges=bm.edges, sides=settings["fill_holes"])
        new = result["faces"]
        sides = sorted((len(f.verts) for f in new), reverse=True)
        bmesh.ops.triangulate(bm, faces=new)
        after("fill_holes", {"holes_filled": len(sides), "sides_of_largest": sides[:8],
                             "faces_added": len(bm.faces) - faces})
    facts["surface_area_after"] = sum(f.calc_area() for f in bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    facts["custom_normals_after_edit"] = bool(mesh.has_custom_normals)
    if settings["normals"] == "clear":
        if mesh.has_custom_normals:
            lib.activate(obj)
            lib.finished(bpy.ops.mesh.customdata_custom_splitnormals_clear(), "clear custom normals")
        if settings["sharp_angle"] > 0:
            mesh.shade_smooth()
            mesh.set_sharp_from_angle(angle=math.radians(settings["sharp_angle"]))
        else:
            mesh.shade_smooth()
        clock.lap("clear_normals")
    facts["steps_done"] = done
    facts["after_object"] = lib.describe(obj)
    if settings["count"]:
        facts["after"] = lib.defects(mesh)
    low, high = lib.bounds(mesh)
    facts["bounds_after"] = [low, high]
    clock.lap("count_after")
    lib.write(target)
    clock.lap("export")
    facts["seconds"] = clock.steps
    lib.save_facts(facts_path, facts)


main()
