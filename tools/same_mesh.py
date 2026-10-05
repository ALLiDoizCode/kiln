"""Gate L2c: a palette variant's GLB carries its base asset's mesh, and only its texture differs.

A season is another palette on the same mesh (ADR 11, ADR 13), and a cover
(moss) is other growth painted on it (ADR 10): a spec with `palette_of`
names the asset it is a palette of. A variant then costs a
texture and not a model only if every vertex, normal, UV and index of the two
files is the same, byte for byte, so that the game can keep one mesh and swap
the image. This reads both exported files and says so, and that the images do
differ: a season or a cover with its base's own texture is not one.

Usage: python tools/same_mesh.py <variant.glb> <base.glb>
"""

import hashlib
import json
import struct
import sys

from pipeline import Checks


def read(path):
    """A GLB's JSON and its binary chunk."""
    with open(path, "rb") as f:
        magic, version, _length = struct.unpack("<4sII", f.read(12))
        length, kind = struct.unpack("<I4s", f.read(8))
        if magic != b"glTF" or version != 2 or kind != b"JSON":
            sys.exit(f"{path}: not a glTF 2.0 binary file")
        gltf = json.loads(f.read(length))
        length, _kind = struct.unpack("<I4s", f.read(8))
        return gltf, f.read(length)


def view(gltf, binary, index):
    found = gltf["bufferViews"][index]
    start = found.get("byteOffset", 0)
    return binary[start : start + found["byteLength"]]


def geometry(gltf, binary):
    """Every primitive as {what it holds: (its layout, a hash of its bytes)}, in the file's order."""
    primitives = []
    for mesh in gltf.get("meshes", []):
        for primitive in mesh["primitives"]:
            held = {}
            for name, index in sorted({**primitive["attributes"], "indices": primitive["indices"]}.items()):
                accessor = gltf["accessors"][index]
                layout = (accessor["componentType"], accessor["type"], accessor["count"])
                held[name] = (layout, hashlib.sha256(view(gltf, binary, accessor["bufferView"])).hexdigest())
            primitives.append(held)
    return primitives


def images(gltf, binary):
    return [hashlib.sha256(view(gltf, binary, image["bufferView"])).hexdigest() for image in gltf.get("images", []) if "bufferView" in image]


variant, base = sys.argv[1], sys.argv[2]
mine, theirs = read(variant), read(base)
checks = Checks("L2c-same-mesh", variant)
a, b = geometry(*mine), geometry(*theirs)
differing = sorted({name for one, other in zip(a, b) for name in set(one) | set(other) if one.get(name) != other.get(name)})
checks.check(
    "palette.same_mesh",
    a and len(a) == len(b) and not differing,
    f"{variant} has {len(a)} primitives and {base} has {len(b)}; they differ in {differing}: a palette variant carries its base's mesh, UVs included",
)
checks.check("palette.other_texture", images(*mine) and images(*mine) != images(*theirs), f"{variant} has no texture, or the same texture as {base}: a palette variant differs from its base in its texture")
report = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
checks.finish(report)
