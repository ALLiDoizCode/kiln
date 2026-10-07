#!/usr/bin/env python3
"""Print what a .glb holds: each mesh primitive, its attributes, counts and material.

Usage: python3 learn/assets/glb_inspect.py <file.glb>
Needs nothing but the standard library. For measurements (bounding box, UV islands,
texel density and more) use: python3 -m kiln.measure <file.glb>
"""
import os
import sys

# The file reader is kiln's own (kiln/glb.py at the repo root), so there is one parser.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from kiln.glb import GltfError, load  # noqa: E402


def read_json_chunk(path):
    try:
        model = load(path)
    except (GltfError, OSError) as error:
        sys.exit(str(error))
    return model.version, model.json


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    version, gltf = read_json_chunk(sys.argv[1])
    accessors = gltf.get("accessors", [])
    materials = gltf.get("materials", [])
    print(f"{sys.argv[1]}  (glTF {version}, generator: {gltf['asset'].get('generator', '?')})")
    for mesh in gltf.get("meshes", []):
        print(f"\nmesh \"{mesh.get('name', '')}\"")
        for i, prim in enumerate(mesh["primitives"]):
            print(f"  primitive {i}")
            vertices = 0
            for name, index in prim["attributes"].items():
                acc = accessors[index]
                vertices = acc["count"]
                print(f"    {name:<11} {acc['type']:<5} x {acc['count']}")
            if "indices" in prim:
                count = accessors[prim["indices"]]["count"]
                print(f"    indices     {count}  = {count // 3} triangles")
            else:
                print(f"    indices     none  = {vertices // 3} triangles")
            if "material" in prim:
                mat = materials[prim["material"]]
                pbr = mat.get("pbrMetallicRoughness", {})
                textures = [k for k in ("baseColorTexture", "metallicRoughnessTexture") if k in pbr]
                textures += [k for k in ("normalTexture", "occlusionTexture", "emissiveTexture") if k in mat]
                print(f"    material    \"{mat.get('name', '')}\"  textures: {', '.join(textures) or 'none'}")
            else:
                print("    material    none (the engine uses a default)")
    images = gltf.get("images", [])
    print(f"\n{len(gltf.get('meshes', []))} mesh(es), {len(materials)} material(s), {len(images)} image(s)")


if __name__ == "__main__":
    main()
