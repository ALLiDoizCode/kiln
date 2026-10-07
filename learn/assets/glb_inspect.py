#!/usr/bin/env python3
"""Print what a .glb holds: each mesh primitive, its attributes, counts and material.

Usage: python3 learn/assets/glb_inspect.py <file.glb>
Reads only the JSON chunk of the file; needs nothing but the standard library.
"""
import json
import struct
import sys


def read_json_chunk(path):
    with open(path, "rb") as f:
        magic, version, _length = struct.unpack("<4sII", f.read(12))
        if magic != b"glTF":
            sys.exit(f"{path}: not a .glb file")
        chunk_length, chunk_type = struct.unpack("<I4s", f.read(8))
        if chunk_type != b"JSON":
            sys.exit(f"{path}: first chunk is not JSON")
        return version, json.loads(f.read(chunk_length))


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
