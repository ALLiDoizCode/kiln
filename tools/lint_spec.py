"""Gate L0: an asset's spec.json is complete and the toolchain pins agree.

Usage: python tools/lint_spec.py <asset>
"""

import json
import re
import sys

from pipeline import ROOT, Asset, Checks, conventions, linear_rgb

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
    "max_view_share": float,
    "min_ledge_views": int,
}
# Optional; how much of its bounding box a closed shape fills. Both keys are required once it is present.
FULLNESS = {"min_volume_share": float, "min_crown_share": float}
# Optional; painted shading (ADR 10). `growth` and `growth_height_m` come together or not at all.
PAINTED = {
    "texture_px": int,
    "base_tint": str,
    "top_tint": str,
    "edge_light": float,
    "edge_width_m": float,
    "crevice_shadow": float,
    "crevice_width_m": float,
    "hidden_underside": bool,
}
GROWTH = {"growth": str, "growth_height_m": float}
# Optional variation, each a strength from 0 to 1. Growth on upward faces and along upper edges
# needs `growth`; `blotch` and `blotch_size_m` come together.
GROWTH_WHERE = {"growth_up": float, "growth_edges": float}
# Optional, with `growth`: how much darker than the surface its patches are (0 to below 1), and how large they are, metres.
GROWTH_LOOK = {"growth_darker": float, "growth_patch_m": float}
# Optional; the habits of a designed rock (docs/style/rock-shapes.md). Every key of a block is required once the block is present.
PIECES = {"min_count": int, "min_shown_m2": float, "min_dominant_ratio": float, "min_step_ratio": float}
FOOT = {"min_sides": int, "min_side_m2": float}
CHAMFERS = {"min_count": int, "min_m2": float, "min_width_m": float}
LEAN = {"max_upright_share": float, "min_summit_offset": float}
BLOTCH = {"blotch": float, "blotch_size_m": float}
SIDE_SHADE = {"side_shade": float}
HEX = "#[0-9a-f]{6}"
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
        name.startswith(prefix) and pattern.match(name) and isinstance(colour, str) and re.fullmatch(HEX, colour)
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
            and set(planes) - {"ledge_plane_m2"} == set(PLANES)
            and all(type(planes[key]) is kind and planes[key] >= 0 for key, kind in PLANES.items())
            # Optional: the least area of the smaller plane of a ledge, when it need not be a large one.
            and (("ledge_plane_m2" not in planes) or (type(planes["ledge_plane_m2"]) is float and 0 < planes["ledge_plane_m2"] <= planes["large_m2"]))
            and planes["large_m2"] > 0
            and 0 < planes["min_area_share"] <= 1
            and planes["min_count"] <= planes["max_count"]
            and 0 < planes["max_view_share"] <= 1
            and planes["min_ledge_views"] <= len(conv["planes"]["views"])
        )
        checks.check("spec.planes", ok, f"optional; needs exactly {sorted(PLANES)}, shares in (0, 1], min_count <= max_count, min_ledge_views at most the {len(conv['planes']['views'])} views in conventions.toml")
    fullness = spec.get("fullness")
    if fullness is not None:
        ok = isinstance(fullness, dict) and set(fullness) == set(FULLNESS) and all(type(fullness[key]) is float and 0 < fullness[key] <= 1 for key in FULLNESS)
        checks.check("spec.fullness", ok and spec["watertight"], f"optional; needs exactly {sorted(FULLNESS)}, each a share in (0, 1], on a watertight asset")
    # The habits of a designed rock: blocks of positive numbers, with shares in (0, 1].
    for block, keys in (("pieces", PIECES), ("foot", FOOT), ("chamfers", CHAMFERS), ("lean", LEAN)):
        wanted_block = spec.get(block)
        if wanted_block is None:
            continue
        ok = isinstance(wanted_block, dict) and set(wanted_block) == set(keys) and all(type(wanted_block[key]) is kind and wanted_block[key] >= 0 for key, kind in keys.items())
        ok = ok and all(wanted_block[key] <= 1 for key in ("max_upright_share", "min_summit_offset") if key in keys)
        ok = ok and wanted_block.get("min_sides", 0) <= 4 and wanted_block.get("min_dominant_ratio", 1.0) >= 1 and wanted_block.get("min_step_ratio", 1.0) >= 1
        # Chamfers are measured against what counts as a large plane, and all four against a closed shape.
        ok = ok and spec["watertight"] and (block != "chamfers" or (isinstance(planes, dict) and wanted_block["min_m2"] < planes.get("large_m2", 0)))
        checks.check(f"spec.{block}", ok, f"optional; needs exactly {sorted(keys)}, none negative, shares at most 1, ratios at least 1, on a watertight asset (chamfers: with `planes`, and min_m2 below planes.large_m2)")
    checks.check("spec.soft_edges", isinstance(spec.get("soft_edges", False), bool) and (not spec.get("soft_edges") or "NORMAL" in spec["attributes"]), "optional; true or false, and true needs NORMAL in attributes")
    painted = spec.get("painted_shading")
    if painted is not None:
        keys = set(painted) if isinstance(painted, dict) else set()
        wanted = {**PAINTED, **(GROWTH if keys & set(GROWTH) else {}), **(BLOTCH if keys & set(BLOTCH) else {})}
        optional = {**SIDE_SHADE, **({**GROWTH_WHERE, **GROWTH_LOOK} if "growth" in keys else {})}
        wanted.update({key: kind for key, kind in optional.items() if key in keys})
        ok = keys == set(wanted) and all(type(painted[key]) is kind for key, kind in wanted.items())
        ok = ok and all(re.fullmatch(HEX, painted[key]) for key in ("base_tint", "top_tint", "growth") if key in painted)
        checks.check(
            "spec.painted_shading",
            ok,
            f"optional; needs exactly {sorted(PAINTED)}, with or without {sorted(GROWTH)} (and then {sorted(GROWTH_WHERE)}, {sorted(GROWTH_LOOK)}), {sorted(BLOTCH)} together, {sorted(SIDE_SHADE)}; colours as #rrggbb",
        )
        if ok:
            size = painted["texture_px"]
            checks.check("spec.painted_texture_px", 64 <= size <= 4096 and size & (size - 1) == 0, f"{size} is not a power of two from 64 to 4096")
            luma = lambda colour: sum(c * w for c, w in zip(linear_rgb(colour), (0.2126, 0.7152, 0.0722)))
            checks.check(
                "spec.painted_base_darker",
                luma(painted["base_tint"]) < luma(painted["top_tint"]),
                f"base_tint {painted['base_tint']} is not darker than top_tint {painted['top_tint']} (ADR 9: darker toward the base)",
            )
            amounts_ok = 0 <= painted["edge_light"] <= 1 and 0 <= painted["crevice_shadow"] < 1 and painted["edge_width_m"] > 0 and painted["crevice_width_m"] > 0
            strengths_ok = all(0 <= painted.get(key, 0.0) <= 1 for key in (*GROWTH_WHERE, "blotch")) and 0 <= painted.get("side_shade", 0.0) < 1 and painted.get("blotch_size_m", 1.0) > 0
            strengths_ok = strengths_ok and 0 <= painted.get("growth_darker", 0.0) < 1 and painted.get("growth_patch_m", 1.0) > 0
            checks.check(
                "spec.painted_amounts",
                amounts_ok and strengths_ok and painted.get("growth_height_m", 1.0) > 0,
                "edge_light, growth_up, growth_edges and blotch in 0..1; crevice_shadow, side_shade and growth_darker in 0..1 (below 1); widths, growth height, growth patch size and blotch size above 0",
            )
    checks.check(
        "spec.painted_needs_uvs",
        (painted is not None) == ("TEXCOORD_0" in spec["attributes"]),
        "painted_shading needs TEXCOORD_0 in attributes, and a flat-colour asset carries no UVs (ADR 4)",
    )
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
