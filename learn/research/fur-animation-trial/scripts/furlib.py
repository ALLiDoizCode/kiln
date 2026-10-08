"""Shared pieces of the fur-animation trial's Blender scripts (run through tools/bl).

Axes: Blender is Z up; the glTF importer turns glTF (x, y, z) into Blender (x, -z, y). The
creature's face is at glTF +z, so at Blender -y. Blender's Python brings numpy with it.
"""
import json
import sys

import bmesh
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree


def args():
    return sys.argv[sys.argv.index("--") + 1:]


def load_one_mesh(path):
    """Import a .glb with coincident points merged; return the one mesh object, custom normals
    cleared and faces smooth, so that the base shape and every shape key get their normals the
    same way (from the faces)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path, merge_vertices=True)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        raise SystemExit(f"expected one mesh object, found {len(meshes)}")
    obj = meshes[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if obj.data.has_custom_normals:
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    return obj


def coords(mesh):
    co = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", co)
    return co.reshape(-1, 3)


def edges(mesh):
    e = np.empty(len(mesh.edges) * 2, dtype=np.int64)
    mesh.edges.foreach_get("vertices", e)
    return e.reshape(-1, 2)


def triangles(mesh):
    mesh.calc_loop_triangles()
    t = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", t)
    return t.reshape(-1, 3)


def neighbour_mean(co, e):
    """Mean of each vertex's edge neighbours (itself where it has none)."""
    total = np.zeros_like(co)
    count = np.zeros(len(co))
    np.add.at(total, e[:, 0], co[e[:, 1]]); np.add.at(total, e[:, 1], co[e[:, 0]])
    np.add.at(count, e[:, 0], 1); np.add.at(count, e[:, 1], 1)
    lone = count == 0
    count[lone] = 1
    mean = total / count[:, None]
    mean[lone] = co[lone]
    return mean


def smooth(co, e, iterations, factor=0.5, taubin=False, mu=-0.53):
    """Laplacian smoothing: each pass moves every vertex part of the way to the mean of its
    neighbours. It shrinks thin things fastest. With taubin, every pass is followed by a pass
    the other way (factor mu), which keeps the large shape from shrinking."""
    s = co.copy()
    for _ in range(iterations):
        s += factor * (neighbour_mean(s, e) - s)
        if taubin:
            s += mu * (neighbour_mean(s, e) - s)
    return s


def vertex_normals(co, tri):
    n = np.zeros_like(co)
    fn = np.cross(co[tri[:, 1]] - co[tri[:, 0]], co[tri[:, 2]] - co[tri[:, 0]])
    for k in range(3):
        np.add.at(n, tri[:, k], fn)
    length = np.linalg.norm(n, axis=1)
    length[length == 0] = 1
    return n / length[:, None]


def components(n_vertices, e, keep):
    """Groups of kept vertices joined by edges whose both ends are kept. Returns a label per
    vertex (-1 where not kept) and the number of groups."""
    parent = np.arange(n_vertices)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in e[keep[e[:, 0]] & keep[e[:, 1]]]:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    label = np.full(n_vertices, -1)
    names = {}
    for v in np.nonzero(keep)[0]:
        r = find(v)
        label[v] = names.setdefault(r, len(names))
    return label, len(names)


def self_intersections(co, tri):
    """Pairs of triangles that cut through each other and share no vertex."""
    tree = BVHTree.FromPolygons([tuple(p) for p in co], [tuple(int(i) for i in t) for t in tri], all_triangles=True)
    pairs = 0
    for a, b in tree.overlap(tree):
        if a < b and not (set(tri[a]) & set(tri[b])):
            pairs += 1
    return pairs


def stretch(co_a, co_b, e):
    """How much each edge's length changes from shape a to shape b: the ratio b/a. The texture
    on a triangle is stretched by about this much along that edge."""
    la = np.linalg.norm(co_a[e[:, 0]] - co_a[e[:, 1]], axis=1)
    lb = np.linalg.norm(co_b[e[:, 0]] - co_b[e[:, 1]], axis=1)
    ok = la > 1e-9
    r = lb[ok] / la[ok]
    return {"edges": int(ok.sum()), "over_1_5": int((r > 1.5).sum()), "over_3": int((r > 3).sum()),
            "under_0_5": int((r < 0.5).sum()), "max": float(r.max()), "p99": float(np.percentile(r, 99))}


def flipped(co_a, co_b, tri):
    """Triangles whose face normal turns by more than 90 degrees between the two shapes."""
    na = np.cross(co_a[tri[:, 1]] - co_a[tri[:, 0]], co_a[tri[:, 2]] - co_a[tri[:, 0]])
    nb = np.cross(co_b[tri[:, 1]] - co_b[tri[:, 0]], co_b[tri[:, 2]] - co_b[tri[:, 0]])
    return int((np.einsum("ij,ij->i", na, nb) < 0).sum())


def add_key(obj, name, co, slider_max=1.0):
    if obj.data.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)
    key = obj.shape_key_add(name=name, from_mix=False)
    key.data.foreach_set("co", np.asarray(co, dtype=np.float32).ravel())
    key.slider_max = slider_max
    # A key made from Python starts at 1, and the exporter writes the values as the file's
    # default weights: left alone, the file would open with every shape applied at once.
    key.value = 0.0
    return key


def paint(obj, name, values):
    """Store a 0..1 number per vertex as a grey colour attribute, to look at a mask."""
    attr = obj.data.color_attributes.new(name, "FLOAT_COLOR", "POINT")
    rgba = np.ones((len(values), 4), dtype=np.float32)
    rgba[:, 0] = values; rgba[:, 1] = 0.15 + 0.2 * (1 - values); rgba[:, 2] = 1 - values
    attr.data.foreach_set("color", rgba.ravel())
    obj.data.color_attributes.active_color = attr
    return attr


def export_glb(path, morph=True, normals=True, tangents=False, animations=False, skins=False, vertex_colour=False):
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=False,
        export_morph=morph, export_morph_normal=normals, export_morph_tangent=tangents,
        export_tangents=tangents, export_animations=animations, export_skins=skins,
        export_vertex_color="ACTIVE" if vertex_colour else "NONE",
        export_all_vertex_colors=False, export_yup=True, export_apply=False,
    )


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
