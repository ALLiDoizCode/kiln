"""Stage 5 of the trial, the part kiln's scale_to_size does not do: turn the model about the
up axis and put its origin at the bottom centre.

    tools/bl place.py <in.glb> <out.glb> <facts.json> [turn=180] [origin=bottom_centre|keep]

  turn=<degrees>   about the up axis (glTF +Y, Blender +Z), anticlockwise seen from above.
                   180 takes a model whose front faces glTF's forward (+Z) to Bevy's (-Z).
  origin           bottom_centre moves the model so that its bounding box is centred on the two
                   ground axes and its lowest point is at height 0
Vertex positions are changed with Mesh.transform, as scale_to_size.py does. The facts say what
that did to the stored (custom) normals: the largest angle between each normal after the turn
and the same normal turned by hand.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
import stagelib as lib  # noqa: E402

DEFAULTS = {"turn": 180.0, "origin": "bottom_centre"}


def corner_normals(mesh):
    out = np.zeros(len(mesh.loops) * 3, dtype=np.float32)
    mesh.corner_normals.foreach_get("vector", out)
    return out.reshape(-1, 3)


def main():
    source, target, facts_path, settings = lib.arguments(DEFAULTS)
    clock = lib.Clock()
    meshes = lib.read(source)
    clock.lap("import")
    facts = {"stage": "place", "source": source, "settings": settings, "objects": []}
    turn = Matrix.Rotation(math.radians(settings["turn"]), 4, "Z")
    low, high = [float("inf")] * 3, [float("-inf")] * 3
    for obj in meshes:
        l, h = lib.bounds(obj.data, turn @ obj.matrix_world)
        low = [min(a, b) for a, b in zip(low, l)]
        high = [max(a, b) for a, b in zip(high, h)]
    move = Matrix.Identity(4)
    if settings["origin"] == "bottom_centre":
        move = Matrix.Translation(Vector((-(low[0] + high[0]) / 2, -(low[1] + high[1]) / 2, -low[2])))
    facts["bounds_before_move_blender_zup"] = [low, high]
    for obj in meshes:
        mesh = obj.data
        before = corner_normals(mesh)
        had_custom = bool(mesh.has_custom_normals)
        whole = move @ turn @ obj.matrix_world
        obj.parent = None
        mesh.transform(whole)
        obj.matrix_world = Matrix.Identity(4)
        mesh.update()
        after = corner_normals(mesh)
        rotation = np.array(whole.to_3x3().normalized(), dtype=np.float32)
        expected = before @ rotation.T
        dots = np.clip((expected * after).sum(axis=1), -1.0, 1.0)
        l, h = lib.bounds(mesh)
        facts["objects"].append({
            "name": obj.name, "had_custom_normals": had_custom,
            "has_custom_normals_after": bool(mesh.has_custom_normals),
            "normals_largest_angle_from_turned_degrees": float(np.degrees(np.arccos(dots.min()))),
            "bounds_after_blender_zup": [l, h]})
    clock.lap("place")
    lib.write(target)
    clock.lap("export")
    facts["seconds"] = clock.steps
    lib.save_facts(facts_path, facts)


main()
