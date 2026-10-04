"""Gate L0: an asset's spec.json is complete and the toolchain pins agree.

Usage: python tools/lint_spec.py <asset>
"""

import re
import sys

from pipeline import ROOT, Asset, Checks, conventions

REQUIRED = {
    "asset": str,
    "class": str,
    "objects": list,
    "bounds_m": dict,
    "bounds_tolerance_m": float,
    "max_triangles": int,
    "max_materials": int,
    "watertight": bool,
    "attributes": list,
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
    checks.check("spec.brief", (asset.source / "brief.md").is_file(), "brief.md missing")

pins = conv["toolchain"]
installer = (ROOT / "tools" / "install_tools.sh").read_text()
checks.check("pins.blender", f"BLENDER_VERSION={pins['blender']}\n" in installer, "conventions.toml and install_tools.sh disagree")
checks.check("pins.gltf_validator", f"VALIDATOR_VERSION={pins['gltf_validator']}\n" in installer, "conventions.toml and install_tools.sh disagree")
checks.check("pins.bevy", f'version = "={pins["bevy"]}"' in (ROOT / "Cargo.toml").read_text(), "conventions.toml and Cargo.toml disagree")
checks.finish()
