"""How far one model's surface lies from another's. Read-only.

    tools/bl distance.py <model.glb> <reference.glb> <result.json> [samples=20000]

Both are imported as they are (no scaling, no moving), so they must share a position and size.
Points are taken on the model's surface (the centre of each triangle, or an even pick of
`samples` of them if there are more) and the nearest point of the reference's surface is found
for each. Then the same the other way round, from `samples` triangles of the reference to the
model: that direction shows parts of the reference the model has lost, such as a spike.
Distances are in the file's units and as a share of the reference's largest dimension.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402
import stagelib as lib  # noqa: E402


def load(path):
    obj = lib.one_object(path)
    mesh = obj.data
    mesh.calc_loop_triangles()
    world = obj.matrix_world
    points = [world @ v.co for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    return points, tris


def centres(points, tris, samples):
    step = max(1, len(tris) // samples)
    return [(points[a] + points[b] + points[c]) / 3.0 for a, b, c in tris[::step]]


def spread(values, size):
    values = sorted(values)
    n = len(values)
    pick = lambda share: values[min(n - 1, int(share * n))]
    return {"samples": n, "mean": sum(values) / n, "median": pick(0.5), "p95": pick(0.95),
            "p99": pick(0.99), "largest": values[-1],
            "p95_share_of_size": pick(0.95) / size, "largest_share_of_size": values[-1] / size}


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    model, reference, result = args[:3]
    samples = 20000
    for item in args[3:]:
        if item.startswith("samples="):
            samples = int(item[8:])
    a_points, a_tris = load(model)
    b_points, b_tris = load(reference)
    size = max(max(p[i] for p in b_points) - min(p[i] for p in b_points) for i in range(3))
    tree_b = BVHTree.FromPolygons(b_points, b_tris)
    tree_a = BVHTree.FromPolygons(a_points, a_tris)
    out = {"model": model, "reference": reference, "reference_size": size,
           "model_to_reference": spread([tree_b.find_nearest(p)[3] for p in centres(a_points, a_tris, samples)], size),
           "reference_to_model": spread([tree_a.find_nearest(p)[3] for p in centres(b_points, b_tris, samples)], size)}
    with open(result, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("DISTANCE " + json.dumps(out))


main()
