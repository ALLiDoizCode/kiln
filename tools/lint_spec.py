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
BLOTCH = {"blotch": float, "blotch_size_m": float}
SIDE_SHADE = {"side_shade": float}
# Optional; a tree's trunk and branches (source/tree/brief.md). All keys are required once it is present.
SKELETON = {
    "material": str,
    "min_sides": int,
    "max_sides": int,
    "min_flare": float,
    "min_roots": int,
    "lean_m": list,
    "fork_m": list,
    "max_taper": float,
    "min_branches": int,
    "max_branch_taper": float,
    "min_seen_share": float,
    "min_seen_views": int,
}
# Optional; foliage of leaf pieces in pads, coloured from a palette (ADR 11). All keys are required once it is present.
FOLIAGE = {
    "material": str,
    "pad_gap_m": float,
    "min_pads": int,
    "max_pads": int,
    "min_pad_pieces": int,
    "piece_m": list,
    "min_pointing_out": float,
    "min_pointing_down": float,
    "sky_share": list,
    "min_sky_views": int,
    "under_tint": str,
    "top_tint": str,
    "shades": int,
    "tones": int,
    "variation": float,
}
# Optional; the other assets made by the same generator, and how far this one must differ from each.
VARIANTS = {"siblings": list, "min_difference": float}
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
            and set(planes) == set(PLANES)
            and all(type(planes[key]) is kind and planes[key] >= 0 for key, kind in PLANES.items())
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
    checks.check("spec.soft_edges", isinstance(spec.get("soft_edges", False), bool) and (not spec.get("soft_edges") or "NORMAL" in spec["attributes"]), "optional; true or false, and true needs NORMAL in attributes")
    painted = spec.get("painted_shading")
    if painted is not None:
        keys = set(painted) if isinstance(painted, dict) else set()
        wanted = {**PAINTED, **(GROWTH if keys & set(GROWTH) else {}), **(BLOTCH if keys & set(BLOTCH) else {})}
        optional = {**SIDE_SHADE, **(GROWTH_WHERE if "growth" in keys else {})}
        wanted.update({key: kind for key, kind in optional.items() if key in keys})
        ok = keys == set(wanted) and all(type(painted[key]) is kind for key, kind in wanted.items())
        ok = ok and all(re.fullmatch(HEX, painted[key]) for key in ("base_tint", "top_tint", "growth") if key in painted)
        checks.check(
            "spec.painted_shading",
            ok,
            f"optional; needs exactly {sorted(PAINTED)}, with or without {sorted(GROWTH)} (and then {sorted(GROWTH_WHERE)}), {sorted(BLOTCH)} together, {sorted(SIDE_SHADE)}; colours as #rrggbb",
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
            checks.check(
                "spec.painted_amounts",
                amounts_ok and strengths_ok and painted.get("growth_height_m", 1.0) > 0,
                "edge_light, growth_up, growth_edges and blotch in 0..1; crevice_shadow and side_shade in 0..1 (below 1); widths, growth height and blotch size above 0",
            )
    def block(key, keys):
        """An optional block with exactly `keys`, each of its type; None when absent or malformed."""
        found = spec.get(key)
        if found is None:
            return None
        ok = isinstance(found, dict) and set(found) == set(keys) and all(type(found[k]) is kind for k, kind in keys.items())
        checks.check(f"spec.{key}", ok, f"optional; needs exactly {sorted(keys)}")
        return found if ok else None

    def span(value, low=0.0):
        return len(value) == 2 and all(type(v) is float for v in value) and low <= value[0] < value[1]

    luma = lambda colour: sum(c * w for c, w in zip(linear_rgb(colour), (0.2126, 0.7152, 0.0722)))
    open_materials = spec.get("open_materials", [])
    checks.check(
        "spec.open_materials",
        isinstance(open_materials, list) and set(open_materials) < set(spec["materials"]) and (not open_materials or spec["watertight"]),
        "optional; a list of some, not all, of the materials, on a watertight asset: their faces are open pieces and the rest is the closed surface",
    )
    checks.check("spec.seed", type(spec.get("seed", 0)) is int, "optional; a whole number")
    skeleton = block("skeleton", SKELETON)
    if skeleton:
        ok = (
            skeleton["material"] in spec["materials"]
            and 3 <= skeleton["min_sides"] <= skeleton["max_sides"]
            and span(skeleton["lean_m"])
            and span(skeleton["fork_m"])
            and 0 < skeleton["max_taper"] < 1
            and 0 < skeleton["max_branch_taper"] < 1
            and skeleton["min_flare"] > 1
            and 0 < skeleton["min_seen_share"] < 1
            and 0 < skeleton["min_seen_views"] <= len(conv["foliage"]["views"]) + 1
        )
        checks.check("spec.skeleton_amounts", ok, "material in `materials`; min_sides <= max_sides; lean_m and fork_m as [least, most]; tapers and min_seen_share in 0..1; min_flare above 1; min_seen_views at most the foliage views and the one from below")
    leaves = block("foliage", FOLIAGE)
    if leaves:
        ok = (
            leaves["material"] in open_materials
            and leaves["pad_gap_m"] > 0
            and 1 <= leaves["min_pads"] <= leaves["max_pads"]
            and span(leaves["piece_m"])
            and span(leaves["sky_share"])
            and leaves["sky_share"][1] < 1
            and 0 < leaves["min_sky_views"] <= len(conv["foliage"]["views"])
            and all(0 <= leaves[key] <= 1 for key in ("min_pointing_out", "min_pointing_down"))
            and all(re.fullmatch(HEX, leaves[key]) for key in ("under_tint", "top_tint"))
            and leaves["shades"] >= 2
            and leaves["tones"] >= 2
            and 0 < leaves["variation"] < 1
        )
        checks.check("spec.foliage_amounts", ok, "material in `open_materials`; pad_gap_m above 0; min_pads <= max_pads; piece_m and sky_share as [least, most]; shares in 0..1; tints as #rrggbb; at least 2 shades and 2 tones; variation in 0..1")
        if ok:
            checks.check(
                "spec.foliage_under_darker",
                luma(leaves["under_tint"]) < luma(leaves["top_tint"]),
                f"under_tint {leaves['under_tint']} is not darker than top_tint {leaves['top_tint']} (nature-shapes: lit above, deep green underneath)",
            )
            checks.check("spec.foliage_needs_paint", painted is not None, "foliage takes its colours from the painted texture (ADR 11): the spec needs painted_shading")
            if skeleton and skeleton["material"] != leaves["material"]:
                bark, leaf = spec["materials"][skeleton["material"]], spec["materials"][leaves["material"]]
                checks.check("spec.bark_darker", luma(bark) < luma(leaf), f"bark {bark} is not darker than leaf {leaf} (brief: the trunk is darker than the foliage)")
    variants = block("variants", VARIANTS)
    if variants:
        siblings = variants["siblings"]
        ok = siblings and asset.name not in siblings and all(isinstance(s, str) and (ROOT / "source" / s / "spec.json").is_file() for s in siblings) and 0 < variants["min_difference"] < 1
        checks.check("spec.variants_amounts", ok, "siblings are other assets with a spec.json; min_difference in 0..1")
    family = spec.get("family")
    checks.check("spec.family", family is None or (isinstance(family, str) and (ROOT / "source" / family / "brief.md").is_file()), "optional; names the folder under source/ whose brief.md this asset is a variant of")
    checks.check(
        "spec.painted_needs_uvs",
        (painted is not None) == ("TEXCOORD_0" in spec["attributes"]),
        "painted_shading needs TEXCOORD_0 in attributes, and a flat-colour asset carries no UVs (ADR 4)",
    )
    checks.check("spec.brief", (asset.source / "brief.md").is_file(), "brief.md missing")

# Traceability: every value in the spec has a row in the brief's Numbers table,
# and every row agrees with the spec. A number the brief never stated cannot
# reach a check, and a check cannot enforce a number the brief has changed.
# A variant's numbers are its family's, except the rows its own brief gives.
def numbers(path):
    return dict(re.findall(r"^\| `([^`]+)` \| `([^`]+)` \|", path.read_text(), flags=re.M)) if path.is_file() else {}


rows = numbers(asset.source / "brief.md")
if isinstance(spec.get("family"), str):
    rows = {**numbers(ROOT / "source" / spec["family"] / "brief.md"), **rows}


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
