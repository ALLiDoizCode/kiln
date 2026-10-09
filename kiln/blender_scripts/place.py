"""Put a model where a game expects it. Runs inside the pinned Blender, not under the system
Python:

    tools/bl kiln/blender_scripts/place.py <in.glb> <out.glb> <facts.json> <turn in degrees> \\
        <tangents: yes or no>

The model is turned about the up axis (glTF's +Y), anticlockwise seen from above, and then
moved so that its bounding box is centred on the two ground axes and its lowest point is at
height 0: the origin is at the bottom centre, right for something that stands on a floor.

The turn is for a model whose front faces the wrong way. glTF's forward is +Z and Bevy's is
-Z, so a model that faces glTF's forward, as Tripo's do, needs a half-turn: 180.

Vertex positions are changed, as scale_to_size.py changes them; stored normals turn with the
mesh. With "yes" the model is written with tangents, for a model that came with them (see
kiln_bl.write). The input is only read.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector  # noqa: E402
import kiln_bl as lib  # noqa: E402


def main(source, target, facts_path, turn, tangents):
    meshes = lib.read(source)
    turned = Matrix.Rotation(math.radians(float(turn)), 4, "Z")  # Blender's up is Z
    for obj in meshes:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.transform(turned @ obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)
    low, high = lib.bounds(meshes)
    move = Vector((-(low[0] + high[0]) / 2.0, -(low[1] + high[1]) / 2.0, -low[2]))
    for obj in meshes:
        obj.data.transform(Matrix.Translation(move))
    lib.write(target, tangents=tangents == "yes")
    lib.save_facts(facts_path, {"turn": float(turn)})


if __name__ == "__main__":
    main(*lib.arguments())
