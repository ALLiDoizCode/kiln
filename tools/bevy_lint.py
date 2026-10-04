"""Gate L2b: a GLB uses only what bevy_gltf can load.

The Khronos validator accepts files Bevy cannot use (Draco, unnamed animated
nodes, non-triangle primitives). This closes that gap before any Rust runs.

Usage: python tools/bevy_lint.py <file.glb>
"""

import json
import struct
import sys
from collections import Counter

from pipeline import Checks, conventions

TRIANGLES = 4

path = sys.argv[1]
with open(path, "rb") as f:
    magic, version, _length = struct.unpack("<4sII", f.read(12))
    chunk_length, chunk_type = struct.unpack("<I4s", f.read(8))
    if magic != b"glTF" or version != 2 or chunk_type != b"JSON":
        sys.exit(f"{path}: not a glTF 2.0 binary file")
    gltf = json.loads(f.read(chunk_length))

profile = conventions()["gltf_profile"]
checks = Checks("L2b-bevy", path)

used = set(gltf.get("extensionsUsed", [])) | set(gltf.get("extensionsRequired", []))
unsupported = sorted(used - set(profile["allowed_extensions"]))
checks.check("extensions.supported", not unsupported, f"bevy_gltf does not load {unsupported}")

external = [b["uri"] for b in gltf.get("buffers", []) if "uri" in b] + [i["uri"] for i in gltf.get("images", []) if "uri" in i]
checks.check("self_contained", not external, f"external resources: {external}")

names = [n.get("name") for n in gltf.get("nodes", [])]
checks.check("nodes.named", all(names), f"{names.count(None)} unnamed nodes")
repeated = [n for n, count in Counter(names).items() if n and count > 1]
checks.check("nodes.unique_names", not repeated, f"repeated: {repeated}")

primitives = [p for m in gltf.get("meshes", []) for p in m["primitives"]]
checks.check("primitives.triangles", all(p.get("mode", TRIANGLES) == TRIANGLES for p in primitives), "non-triangle primitive mode")
checks.check("primitives.indexed", all("indices" in p for p in primitives), "unindexed primitive")
checks.check("primitives.have_material", all("material" in p for p in primitives), "primitive with no material")

joints = [len(s["joints"]) for s in gltf.get("skins", [])]
checks.check("skins.joint_limit", all(j <= profile["max_joints"] for j in joints), f"joint counts {joints} exceed {profile['max_joints']}")
checks.finish()
