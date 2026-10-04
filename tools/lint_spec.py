"""Gate L0: an asset's spec.json is complete and the toolchain pins agree.

Usage: python tools/lint_spec.py <asset>
"""

import json
import re
import sys

from pipeline import ROOT, Asset, Checks, conventions

REQUIRED = {
    "asset": str,
    "objects": list,
    "bounds_m": dict,
    "bounds_tolerance_m": float,
    "max_triangles": int,
    "materials": dict,
    "watertight": bool,
    "attributes": list,
}
# Optional; all of its keys are required once it is present.
PLANES = {
    "large_m2": float,
    "min_area_share": float,
    "min_count": int,
    "max_count": int,
    "min_size_ratio": float,
    "min_ledges": int,
    "ledge_m": float,
}
ATTRIBUTES = {"POSITION", "NORMAL", "TANGENT", "TEXCOORD_0", "TEXCOORD_1", "COLOR_0"}

asset = Asset(sys.argv[1])
conv = conventions()
checks = Checks("L0-spec", asset.name)
spec = asset.spec()

for key, kind in REQUIRED.items():
    checks.check(f"spec.{key}", isinstance(spec.get(key), kind), f"missing or not {kind.__name__}")
if not checks.failed():
    checks.check("spec.asset_matches_dir", spec["asset"] == asset.name, f"{spec['asset']} != {asset.name}")
    pattern = re.compile(conv["naming"]["pattern"])
    bad = [o for o in spec["objects"] if not pattern.match(o)]
    checks.check("spec.object_names", spec["objects"] and not bad, f"{bad} do not match {pattern.pattern}")
    lo, hi = spec["bounds_m"].get("min", []), spec["bounds_m"].get("max", [])
    checks.check("spec.bounds", len(lo) == len(hi) == 3 and all(a < b for a, b in zip(lo, hi)), "need min < max on 3 axes")
    checks.check("spec.attributes", set(spec["attributes"]) <= ATTRIBUTES and "POSITION" in spec["attributes"], f"allowed: {sorted(ATTRIBUTES)}")
    checks.check("spec.tangents_need_uvs", "TANGENT" not in spec["attributes"] or "TEXCOORD_0" in spec["attributes"], "TANGENT requires TEXCOORD_0")
    prefix = conv["naming"]["material_prefix"]
    colours_ok = all(
        name.startswith(prefix) and pattern.match(name) and isinstance(colour, str) and re.fullmatch("#[0-9a-f]{6}", colour)
        for name, colour in spec["materials"].items()
    )
    checks.check("spec.materials", spec["materials"] and colours_ok, f'need "{prefix}<name>": "#rrggbb" (sRGB, lower case)')
    for key in ("recess_m", "margin_m"):
        ok = all(name in spec["materials"] and isinstance(d, float) and d > 0 for name, d in spec.get(key, {}).items())
        checks.check(f"spec.{key}", ok, "optional; maps a material in `materials` to a positive distance in metres")
    planes = spec.get("planes")
    if planes is not None:
        ok = (
            isinstance(planes, dict)
            and set(planes) == set(PLANES)
            and all(type(planes[key]) is kind and planes[key] >= 0 for key, kind in PLANES.items())
            and planes["large_m2"] > 0
            and 0 < planes["min_area_share"] <= 1
            and planes["min_count"] <= planes["max_count"]
        )
        checks.check("spec.planes", ok, f"optional; needs exactly {sorted(PLANES)}, share in (0, 1], min_count <= max_count")
    checks.check("spec.soft_edges", isinstance(spec.get("soft_edges", False), bool) and (not spec.get("soft_edges") or "NORMAL" in spec["attributes"]), "optional; true or false, and true needs NORMAL in attributes")
    checks.check("spec.brief", (asset.source / "brief.md").is_file(), "brief.md missing")

# Traceability: every value in the spec has a row in the brief's Numbers table,
# and every row agrees with the spec. A number the brief never stated cannot
# reach a check, and a check cannot enforce a number the brief has changed.
brief = (asset.source / "brief.md").read_text() if (asset.source / "brief.md").is_file() else ""
rows = dict(re.findall(r"^\| `([^`]+)` \| `([^`]+)` \|", brief, flags=re.M))


def leaves(value, path=""):
    """Dotted paths of every value in the spec; lists are values, not containers."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, f"{path}.{key}" if path else key)
    else:
        yield path, value


spec_values = {path: value for path, value in leaves(spec) if path != "asset"}
untraced = sorted(set(spec_values) - set(rows))
checks.check("brief.numbers_cover_spec", not untraced, f"no row in brief.md's Numbers table for {untraced}")
mismatched = []
for path, text in rows.items():
    try:
        if path not in spec_values or json.loads(text) != spec_values[path]:
            mismatched.append(path)
    except json.JSONDecodeError:
        mismatched.append(path)
checks.check("brief.numbers_match_spec", not mismatched, f"brief.md and spec.json disagree on {mismatched}")

pins = conv["toolchain"]
installer = (ROOT / "tools" / "install_tools.sh").read_text()
checks.check("pins.blender", f"BLENDER_VERSION={pins['blender']}\n" in installer, "conventions.toml and install_tools.sh disagree")
checks.check("pins.gltf_validator", f"VALIDATOR_VERSION={pins['gltf_validator']}\n" in installer, "conventions.toml and install_tools.sh disagree")
checks.check("pins.bevy", f'version = "={pins["bevy"]}"' in (ROOT / "Cargo.toml").read_text(), "conventions.toml and Cargo.toml disagree")
checks.finish()
