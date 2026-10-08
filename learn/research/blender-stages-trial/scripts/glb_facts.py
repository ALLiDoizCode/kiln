#!/usr/bin/env python3
"""What one .glb holds, and how it differs from another, read from the files with kiln/glb.py.

    python3 -I scripts/glb_facts.py <model.glb> [<reference.glb>]

Prints JSON. For the one file:
  bytes, sha256, extensions, triangles, vertices stored, welded points (positions rounded to a
  millionth of a metre), which attributes it has, normals that are not unit length, each image's
  format, pixel size, bytes and SHA-256, and what the material says (factors, double sided).
  "backward_normal_corners": triangle corners whose stored normal points more than 90 degrees
  away from the side the triangle itself faces (by its winding): such a corner is lit from the
  wrong side. Triangles with no area are left out.
  "triangle_areas": how the triangles are spread over the surface -
      share_holding_99pc_of_area   the smallest share of the triangles that together make up
                                   99% of the surface (largest first). Low means most of the
                                   triangles add almost nothing.
      share_under_100th_of_mean    the share of triangles smaller than a hundredth of the mean
                                   triangle: slivers and specks.
With a reference file, "against_reference" adds:
  same_images     which images have the same bytes
  normals         for every stored vertex that the reference stores at the same position and UV
                  (both rounded to a millionth), the angle between the two normals: the share
                  matched, the largest angle and the share over one degree
Standard library only. The .glb files are untrusted data: run with -I.
"""
import hashlib
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
from kiln import glb  # noqa: E402


def primitives(model):
    for mesh in model.json.get("meshes", []):
        for prim in mesh.get("primitives", []):
            yield prim


def read(path):
    model = glb.load(path)
    doc = model.json
    out = {"file": path, "bytes": os.path.getsize(path),
           "extensions_used": doc.get("extensionsUsed", []),
           "extensions_required": doc.get("extensionsRequired", []),
           "generator": doc.get("asset", {}).get("generator")}
    with open(path, "rb") as f:
        out["sha256"] = hashlib.sha256(f.read()).hexdigest()
    triangles = vertices = bad_normals = zero_normals = backward = 0
    attributes, points, areas, keyed = set(), set(), [], {}
    for prim in primitives(model):
        attributes |= set(prim["attributes"])
        pos, _ = model.accessor(prim["attributes"]["POSITION"])
        count = len(pos) // 3
        vertices += count
        nor = model.accessor(prim["attributes"]["NORMAL"])[0] if "NORMAL" in prim["attributes"] else None
        uv = model.accessor(prim["attributes"]["TEXCOORD_0"])[0] if "TEXCOORD_0" in prim["attributes"] else None
        for i in range(count):
            p = (round(pos[3 * i], 6), round(pos[3 * i + 1], 6), round(pos[3 * i + 2], 6))
            points.add(p)
            if nor is not None:
                n = (nor[3 * i], nor[3 * i + 1], nor[3 * i + 2])
                length = math.sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
                if length < 1e-6:
                    zero_normals += 1
                elif abs(length - 1.0) > 1e-3:
                    bad_normals += 1
                key = p + ((round(uv[2 * i], 6), round(uv[2 * i + 1], 6)) if uv is not None else ())
                keyed.setdefault(key, n)
        idx = model.accessor(prim["indices"])[0] if "indices" in prim else list(range(count))
        triangles += len(idx) // 3
        for t in range(0, len(idx) - 2, 3):
            a, b, c = idx[t] * 3, idx[t + 1] * 3, idx[t + 2] * 3
            ux, uy, uz = pos[b] - pos[a], pos[b + 1] - pos[a + 1], pos[b + 2] - pos[a + 2]
            vx, vy, vz = pos[c] - pos[a], pos[c + 1] - pos[a + 1], pos[c + 2] - pos[a + 2]
            cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            areas.append(0.5 * math.sqrt(cx * cx + cy * cy + cz * cz))
            if nor is not None and areas[-1] > 1e-12:
                for k in (a, b, c):
                    if nor[k] * cx + nor[k + 1] * cy + nor[k + 2] * cz < 0.0:
                        backward += 1
    out.update(triangles=triangles, vertices_stored=vertices, welded_points=len(points),
               attributes=sorted(attributes), zero_length_normals=zero_normals,
               non_unit_normals=bad_normals,
               backward_normal_corners=backward)
    if areas:
        total, mean = sum(areas), sum(areas) / len(areas)
        running, needed = 0.0, 0
        for area in sorted(areas, reverse=True):
            running += area
            needed += 1
            if running >= 0.99 * total:
                break
        out["triangle_areas"] = {
            "surface_area": total,
            "share_holding_99pc_of_area": needed / len(areas),
            "share_under_100th_of_mean": sum(1 for a in areas if a < mean / 100) / len(areas),
            "zero_area": sum(1 for a in areas if a < 1e-12)}
    out["images"] = []
    for i, image in enumerate(doc.get("images", [])):
        data = model.image_bytes(i) or b""
        try:
            kind, width, height = glb.image_info(data)
        except Exception as error:  # an image this reader cannot size is still listed
            kind, width, height = f"unreadable: {error}", None, None
        out["images"].append({"name": image.get("name"), "mime": image.get("mimeType"), "format": kind,
                              "width": width, "height": height, "bytes": len(data),
                              "sha256": hashlib.sha256(data).hexdigest()})
    out["materials"] = []
    for material in doc.get("materials", []):
        pbr = material.get("pbrMetallicRoughness", {})
        def image_of(slot):
            if not slot:
                return None
            return doc["textures"][slot["index"]].get("source")
        out["materials"].append({
            "name": material.get("name"), "double_sided": material.get("doubleSided", False),
            "alpha_mode": material.get("alphaMode", "OPAQUE"),
            "base_colour_factor": pbr.get("baseColorFactor"), "metallic_factor": pbr.get("metallicFactor"),
            "roughness_factor": pbr.get("roughnessFactor"),
            "base_colour_image": image_of(pbr.get("baseColorTexture")),
            "metallic_roughness_image": image_of(pbr.get("metallicRoughnessTexture")),
            "normal_image": image_of(material.get("normalTexture")),
            "normal_scale": (material.get("normalTexture") or {}).get("scale"),
            "occlusion_image": image_of(material.get("occlusionTexture")),
            "extensions": sorted(material.get("extensions", {}))})
    return out, keyed


def main(path, reference=None):
    out, keyed = read(path)
    if reference:
        ref, ref_keyed = read(reference)
        ref_hashes = [i["sha256"] for i in ref["images"]]
        matched = over = 0
        worst = 0.0
        for key, n in keyed.items():
            m = ref_keyed.get(key)
            if m is None:
                continue
            matched += 1
            ln = math.sqrt(sum(v * v for v in n)) or 1.0
            lm = math.sqrt(sum(v * v for v in m)) or 1.0
            dot = max(-1.0, min(1.0, sum(a * b for a, b in zip(n, m)) / (ln * lm)))
            angle = math.degrees(math.acos(dot))
            worst = max(worst, angle)
            over += angle > 1.0
        out["against_reference"] = {
            "reference": reference, "reference_bytes": ref["bytes"],
            "reference_vertices_stored": ref["vertices_stored"], "reference_triangles": ref["triangles"],
            "reference_welded_points": ref["welded_points"],
            "reference_zero_length_normals": ref["zero_length_normals"],
            "extensions_dropped": sorted(set(ref["extensions_used"]) - set(out["extensions_used"])),
            "extensions_added": sorted(set(out["extensions_used"]) - set(ref["extensions_used"])),
            "same_images": [i["sha256"] in ref_hashes for i in out["images"]],
            "reference_images": [{k: i[k] for k in ("name", "format", "width", "height", "bytes")} for i in ref["images"]],
            "reference_materials": ref["materials"],
            "normals": {"keys_here": len(keyed), "keys_in_reference": len(ref_keyed),
                        "matched_share": matched / max(1, len(keyed)),
                        "largest_angle_degrees": worst,
                        "share_over_1_degree": over / max(1, matched)}}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:3])
