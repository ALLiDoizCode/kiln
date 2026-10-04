"""Write a copy of a GLB with every vertex normal negated: valid glTF that lights inside out.

Usage: python tests/flip_normals.py <in.glb> <out.glb>
"""

import json
import struct
import sys

src, dst = sys.argv[1:3]
data = bytearray(open(src, "rb").read())
json_length = struct.unpack_from("<I", data, 12)[0]
gltf = json.loads(data[20 : 20 + json_length])
bin_start = 20 + json_length + 8

for mesh in gltf["meshes"]:
    for primitive in mesh["primitives"]:
        accessor = gltf["accessors"][primitive["attributes"]["NORMAL"]]
        view = gltf["bufferViews"][accessor["bufferView"]]
        offset = bin_start + view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        count = accessor["count"] * 3
        values = struct.unpack_from(f"<{count}f", data, offset)
        struct.pack_into(f"<{count}f", data, offset, *(-v for v in values))

open(dst, "wb").write(data)
