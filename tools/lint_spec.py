"""Gate L0: an asset's spec.json is complete and the toolchain pins agree.

Usage: python tools/lint_spec.py <asset>
"""

import json
import re
import sys
import tomllib

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
    "hidden_underside": bool,
}
# Optional, both or neither: the shadow in inside corners. A shape with none (a pebble) leaves them out, and the
# load test then fails if it finds an inside corner; overlapping pieces always have them, for their joins (ADR 13).
CREVICE = {"crevice_shadow": float, "crevice_width_m": float}
GROWTH = {"growth": str, "growth_height_m": float}
# Optional variation, each a strength from 0 to 1. Growth on upward faces and along upper edges
# needs `growth`; `blotch` and `blotch_size_m` come together.
GROWTH_WHERE = {"growth_up": float, "growth_edges": float}
# With `growth_edges`, and only then: how far in from an exposed edge its growth reaches, metres.
GROWTH_EDGE = {"growth_edges": float, "growth_edge_m": float}
# Optional, with `growth`: how much darker than the surface its patches are (0 to below 1), and how large they are, metres.
GROWTH_LOOK = {"growth_darker": float, "growth_patch_m": float}
# Optional; the habits of a designed rock (docs/style/rock-shapes.md). Every key of a block is required once the block is present.
PIECES = {"min_count": int, "min_shown_m2": float, "min_dominant_ratio": float, "min_step_ratio": float}
FOOT = {"min_sides": int, "min_side_m2": float}
CHAMFERS = {"min_count": int, "min_m2": float, "min_width_m": float}
LEAN = {"max_upright_share": float, "min_summit_offset": float}
# Optional; a low, rounded stone (source/pebble): how tall it may be for its wider side, and how much of
# the surface that is seen one steep plane may hold. Each block has exactly its one key, a share in (0, 1).
LOW = {"max_height_share": float}
ROUNDED = {"max_steep_plane_share": float}
# Optional; a shape of several closed pieces that pass into each other (ADR 13). Every key is required once it is present.
OVERLAP = {"min_count": int, "max_count": int, "max_buried_share": float, "min_step_ratio": float}
# Optional, with `overlap`: a cluster of leaning prisms on one base (a crag).
CLUSTER = {"min_prisms": int, "max_height_step": float, "min_lean_deg": float, "max_lean_spread_deg": float}
# Optional, with `overlap`: flat stones piled one on another (a stack).
PILE = {"max_sink": float, "max_thickness": float, "max_size_step": float}
# Optional, with `overlap`: a cap held off the ground on narrow necks (a table rock).
TABLE = {"necks": int, "min_clear_m": float, "min_shelter_share": float, "max_neck_share": float, "min_overhang_m": float}
# Optional, with `overlap`: tiers stacked like a telescope on a fluted base (a stepped spire).
SPIRE = {"tiers": list, "max_width_step": float, "min_ledge_share": float, "min_flutes": int, "min_tier_offset": float, "min_lean_deg": float, "min_step_spread": float}
# Optional, with `overlap`: two piers that reach the ground and a span resting on both, with open air right through under it (an arch).
ARCH = {"span": str, "min_opening_m": float, "min_clear_m": float, "min_bearing_m2": float, "max_box_share": float, "min_side_step": float, "max_level_share": float}
ARCH_SPANS = ("lintel", "wedged")
# Optional; a near-cuboid with big chamfers (a block), and, with it, the cracks across it. Every key of a block is required once it is present.
BLOCK = {"min_square_share": float, "min_chamfers": int, "min_chamfer_m": float}
CRACKS = {"count": int, "depth_m": float, "width_m": float, "min_span": float}
# Optional; one convex mass with sloping flanks (a boulder, source/boulder). Every key is required once it is present.
MASS = {"min_hull_share": float, "min_outline_share": float, "max_steep_share": float}
# Optional; a group of separate closed stones lying together on the ground (rubble, source/rubble). Every key is required once it is present.
SCATTER = {"min_count": int, "max_count": int, "min_size_range": float, "min_step_ratio": float, "max_gap_m": float, "min_touching": int, "min_breadth": float, "min_radial_spread": float, "min_stand_share": float}
# Optional; a trunk lying on the ground (a fallen log, source/log), and, with it, the hollow through it. Every key of a block is required once it is present.
LOG = {"bark": str, "wood": str, "butt": str, "thickness_m": list, "max_taper": float, "min_bend": float, "min_grounded_share": float, "min_flat_share": float, "min_end_wood": float, "stubs": list}
LOG_BUTTS = ("sawn", "root", "broken")
HOLLOW = {"min_clear_m": float, "min_depth_m": float, "min_wall_m": float}
BLOTCH = {"blotch": float, "blotch_size_m": float}
SIDE_SHADE = {"side_shade": float}
# Grain (streaks along a limb: bark) and its width come together; so do the height below which a
# player stands against the surface and the texels per metre it gets there.
GRAIN = {"grain": float, "grain_width_m": float}
CLOSE = {"close_height_m": float, "close_texels_per_m": float}
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
    "min_view_tone": float,
    "min_view_grain": float,
    "min_canopy_over_limbs": float,
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
    "core_tint": str,
    "lobes": list,
    "min_lobe_ratio": float,
    "max_core_seen": float,
    "max_core_seen_below": float,
    "min_pad_flatness": float,
    "min_pad_spread": float,
    "max_seen_into": float,
    "min_rim_points_per_m": float,
}
# What foliage of blades shares with foliage of leaf pieces: the material, how pieces are found, and the palette.
# A spec with a `blades` or a `stalks` block has exactly these in its `foliage` block; one without has all of FOLIAGE.
FOLIAGE_SHARED = ("material", "pad_gap_m", "min_pad_pieces", "piece_m", "under_tint", "top_tint", "shades", "tones", "variation")
# Optional; blades from one point (source/blade_plant/brief.md), in place of pads over cores. All keys are required once it is present.
BLADES = {"width_share": list, "root_m": float, "max_gap_deg": float, "lean_deg": list, "min_arch": float}
# Optional; a conifer's crown (source/tree/species/conifer.md): tiers of foliage found as pads are, and one leader. All keys are required once it is present.
TIERS = {"widest_among_lowest": int, "min_narrowing": float, "max_top_share": float, "min_droop": float, "max_tip_width_m": float, "max_leader_bow_m": float, "tip_off_m": list}
# Optional; a bed of stalks that carry leaves (source/reeds/brief.md), in place of pads over cores and of blades from one point. All keys are required once it is present.
STALKS = {
    "count": list, "length_m": list, "width_m": list, "min_round": float, "foot_m": float, "max_lean_deg": float, "min_apart_m": float, "min_bed": float,
    "leaves": list, "leaf_width_share": list, "min_leaf_sweep": float, "head_width_m": list, "min_head_fullness": float, "head_share": list,
}
# Optional, with `blades` or `stalks`: a clump of them (source/tall_grass/brief.md): how many stand near upright, and how much sky shows through it from the side.
CLUMP = {"upright_deg": float, "min_upright_share": float, "max_sky_share": float}
# Optional, with `blades` or `stalks`: heads (seed heads, cattails), closed pieces of the closed material carried on blades or stalks. Every key is required once it is present.
HEADS = {"count": list, "size_m": list, "min_height": float}
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
    for block, keys in (("low", LOW), ("rounded", ROUNDED)):
        wanted_block = spec.get(block)
        if wanted_block is not None:
            ok = isinstance(wanted_block, dict) and set(wanted_block) == set(keys) and all(type(wanted_block[key]) is float and 0 < wanted_block[key] < 1 for key in keys)
            checks.check(f"spec.{block}", ok and spec["watertight"], f"optional; needs exactly {sorted(keys)}, a share above 0 and below 1, on a watertight asset")
    mass = spec.get("mass")
    if mass is not None:
        ok = isinstance(mass, dict) and set(mass) == set(MASS) and all(type(mass[key]) is float and 0 < mass[key] < 1 for key in MASS)
        checks.check("spec.mass", ok and spec["watertight"], f"optional; needs exactly {sorted(MASS)}, each a share above 0 and below 1, on a watertight asset")
    overlap = spec.get("overlap")
    if overlap is not None:
        ok = (
            isinstance(overlap, dict)
            and set(overlap) == set(OVERLAP)
            and all(type(overlap[key]) is kind for key, kind in OVERLAP.items())
            and 2 <= overlap["min_count"] <= overlap["max_count"]
            and 0 < overlap["max_buried_share"] < 1
            and overlap["min_step_ratio"] >= 1
        )
        checks.check("spec.overlap", ok and spec["watertight"], f"optional; needs exactly {sorted(OVERLAP)}: at least 2 pieces, min_count <= max_count, max_buried_share in 0..1 (below 1), min_step_ratio at least 1, on a watertight asset")
        # These two measure one closed skin: the volume of overlapping pieces counts their overlaps twice,
        # and a piece record is held against a surface with nothing inside it.
        one_skin = sorted(block for block in ("fullness", "pieces") if block in spec)
        checks.check("spec.one_skin_checks", not one_skin, f"{one_skin} measure one closed skin and cannot be asked of overlapping pieces (`overlap`)")
    pile = spec.get("pile")
    if pile is not None:
        ok = (
            isinstance(pile, dict)
            and set(pile) == set(PILE)
            and all(type(pile[key]) is kind for key, kind in PILE.items())
            and all(0 < pile[key] < 1 for key in PILE)
            and isinstance(overlap, dict)
        )
        checks.check("spec.pile", ok, f"optional; needs exactly {sorted(PILE)}, each in 0..1 (below 1), on an asset of overlapping pieces (`overlap`)")
    cluster = spec.get("cluster")
    if cluster is not None:
        ok = (
            isinstance(cluster, dict)
            and set(cluster) == set(CLUSTER)
            and all(type(cluster[key]) is kind for key, kind in CLUSTER.items())
            and cluster["min_prisms"] >= 2
            and 0 < cluster["max_height_step"] < 1
            and 0 < cluster["min_lean_deg"] < 90
            and 0 < cluster["max_lean_spread_deg"] <= 90
            and isinstance(overlap, dict)
            and cluster["min_prisms"] <= overlap.get("min_count", 0)
        )
        checks.check("spec.cluster", ok, f"optional; needs exactly {sorted(CLUSTER)}: at least 2 prisms and no more than `overlap.min_count`, max_height_step in 0..1 (below 1), min_lean_deg in 0..90, max_lean_spread_deg in 0..90, on an asset of overlapping pieces (`overlap`)")
    table = spec.get("table")
    if table is not None:
        size = [high - low for low, high in zip(spec["bounds_m"]["min"], spec["bounds_m"]["max"])]
        ok = (
            isinstance(table, dict)
            and set(table) == set(TABLE)
            and all(type(table[key]) is kind for key, kind in TABLE.items())
            and table["necks"] >= 1
            and 0 < table["min_clear_m"] < size[2]
            and 0 < table["max_neck_share"] < table["min_shelter_share"] <= 1
            and table["max_neck_share"] + table["min_shelter_share"] <= 1
            and 0 < table["min_overhang_m"] < min(size[0], size[1]) / 2
            and isinstance(overlap, dict)
            and table["necks"] < overlap.get("min_count", 0)
        )
        checks.check("spec.table", ok, f"optional; needs exactly {sorted(TABLE)}: at least 1 neck and fewer than `overlap.min_count` (the cap is a piece too), min_clear_m above 0 and below the bounds' height, max_neck_share above 0 and min_shelter_share at most 1 with the two together at most 1, min_overhang_m above 0 and below half the bounds' lesser side, on an asset of overlapping pieces (`overlap`)")
    spire = spec.get("spire")
    if spire is not None:
        ok = (
            isinstance(spire, dict)
            and set(spire) == set(SPIRE)
            and all(type(spire[key]) is kind for key, kind in SPIRE.items())
            and len(spire["tiers"]) == 2
            and all(type(n) is int for n in spire["tiers"])
            and 3 <= spire["tiers"][0]
            and spire["tiers"][0] <= spire["tiers"][1] <= 4
            and 0 < spire["min_tier_offset"] < 1
            and 0 < spire["min_lean_deg"] < 45
            and spire["min_step_spread"] > 1
            and 0 < spire["max_width_step"] < 1
            and 0 < spire["min_ledge_share"] < 1
            and spire["min_flutes"] >= 1
            and isinstance(overlap, dict)
            and spire["tiers"][1] < overlap.get("max_count", 0)
            and spire["tiers"][0] < overlap.get("min_count", 0)
        )
        checks.check("spec.spire", ok, f"optional; needs exactly {sorted(SPIRE)}: tiers as [least, most], 3 or 4 (a base and two or three on it) and fewer than the pieces `overlap` asks (the foot is pieces too), max_width_step, min_ledge_share and min_tier_offset in 0..1 (above 0, below 1), min_lean_deg in 0..45, min_step_spread above 1, at least 1 flute, on an asset of overlapping pieces (`overlap`)")
    arch = spec.get("arch")
    if arch is not None:
        size = [hi - lo for lo, hi in zip(spec["bounds_m"]["min"], spec["bounds_m"]["max"])]
        ok = (
            isinstance(arch, dict)
            and set(arch) == set(ARCH)
            and all(type(arch[key]) is kind for key, kind in ARCH.items())
            and arch["span"] in ARCH_SPANS
            and 0 < arch["min_opening_m"] < size[0]
            and 0 < arch["min_clear_m"] < size[2]
            and arch["min_bearing_m2"] > 0
            and 0 < arch["max_box_share"] < 1
            and 0 < arch["min_side_step"] < 1
            and 0 < arch["max_level_share"] < 1
            and isinstance(overlap, dict)
            and overlap.get("min_count", 0) >= 3
        )
        checks.check("spec.arch", ok, f"optional; needs exactly {sorted(ARCH)}: span one of {ARCH_SPANS}, min_opening_m above 0 and below the bounds' width (x), min_clear_m above 0 and below the bounds' height, min_bearing_m2 above 0, max_box_share, min_side_step and max_level_share each above 0 and below 1 (at 1, 0 and 1 they ask nothing), on an asset of at least 3 overlapping pieces (`overlap`): two piers and a span")
    box = spec.get("block")
    if box is not None:
        ok = (
            isinstance(box, dict)
            and set(box) == set(BLOCK)
            and all(type(box[key]) is kind for key, kind in BLOCK.items())
            and 0 < box["min_square_share"] <= 1
            and box["min_chamfers"] >= 0
            and box["min_chamfer_m"] > 0
        )
        checks.check("spec.block", ok and spec["watertight"], f"optional; needs exactly {sorted(BLOCK)}: min_square_share in (0, 1], min_chamfers not negative, min_chamfer_m above 0, on a watertight asset")
    cracks = spec.get("cracks")
    if cracks is not None:
        ok = (
            isinstance(cracks, dict)
            and set(cracks) == set(CRACKS)
            and all(type(cracks[key]) is kind for key, kind in CRACKS.items())
            and cracks["count"] >= 1
            and cracks["depth_m"] > 0
            and cracks["width_m"] > 0
            and 0 < cracks["min_span"] <= 1
            and isinstance(box, dict)
        )
        checks.check("spec.cracks", ok, f"optional; needs exactly {sorted(CRACKS)}: at least 1 crack, depth_m and width_m above 0, min_span in (0, 1], on a block (`block`)")
    scatter = spec.get("scatter")
    if scatter is not None:
        ok = (
            isinstance(scatter, dict)
            and set(scatter) == set(SCATTER)
            and all(type(scatter[key]) is kind for key, kind in SCATTER.items())
            and 2 <= scatter["min_count"] <= scatter["max_count"]
            and scatter["min_size_range"] > 1
            and 1 <= scatter["min_step_ratio"] <= scatter["min_size_range"]
            and scatter["max_gap_m"] > 0
            and 0 <= scatter["min_touching"] <= scatter["min_count"] - 1
            and all(0 < scatter[key] < 1 for key in ("min_breadth", "min_radial_spread", "min_stand_share"))
        )
        checks.check(
            "spec.scatter",
            ok and spec["watertight"],
            f"optional; needs exactly {sorted(SCATTER)}: at least 2 stones, min_count <= max_count, min_size_range above 1 (at 1 stones of one size pass), min_step_ratio from 1 to min_size_range, "
            "max_gap_m above 0, min_touching from 0 to one fewer than min_count, min_breadth, min_radial_spread and min_stand_share each above 0 and below 1, on a watertight asset",
        )
        # Separate stones pass into nothing, so they are not overlapping pieces; and `fullness` and `pieces` measure one closed skin.
        other = sorted(block for block in ("overlap", "fullness", "pieces") if block in spec)
        checks.check("spec.scatter_or_overlap", not other, f"{other} cannot be asked of separate stones (`scatter`): `overlap` wants every piece to pass into another, and the others measure one closed skin")
    log = spec.get("log")
    if log is not None:
        size = [high - low for low, high in zip(spec["bounds_m"]["min"], spec["bounds_m"]["max"])]
        ok = (
            isinstance(log, dict)
            and set(log) == set(LOG)
            and all(type(log[key]) is kind for key, kind in LOG.items())
            and log["bark"] in spec["materials"]
            and log["wood"] in spec["materials"]
            and log["bark"] != log["wood"]
            and log["butt"] in LOG_BUTTS
            and len(log["thickness_m"]) == 2
            and all(type(v) is float for v in log["thickness_m"])
            and 0 < log["thickness_m"][0] < log["thickness_m"][1] <= size[2]
            and 0 < log["max_taper"] < 1
            and 0 < log["min_bend"] < 1
            and all(0 < log[key] <= 1 for key in ("min_grounded_share", "min_flat_share", "min_end_wood"))
            and len(log["stubs"]) == 2
            and all(type(n) is int for n in log["stubs"])
            and 0 <= log["stubs"][0] <= log["stubs"][1]
        )
        checks.check("spec.log", ok and spec["watertight"], f"optional; needs exactly {sorted(LOG)}: bark and wood two different materials of `materials`, butt one of {LOG_BUTTS}, thickness_m as [least, most] above 0 and no more than the bounds' height, max_taper and min_bend above 0 and below 1 (at 1 and 0 they ask nothing), the shares in (0, 1], stubs as [fewest, most] whole numbers, on a watertight asset")
    hollow = spec.get("hollow")
    if hollow is not None:
        size = [high - low for low, high in zip(spec["bounds_m"]["min"], spec["bounds_m"]["max"])]
        ok = (
            isinstance(hollow, dict)
            and set(hollow) == set(HOLLOW)
            and all(type(hollow[key]) is kind for key, kind in HOLLOW.items())
            and isinstance(log, dict)
            and isinstance(log.get("thickness_m"), list)
            and len(log["thickness_m"]) == 2
            and hollow["min_wall_m"] > 0
            and 0 < hollow["min_clear_m"] + 2 * hollow["min_wall_m"] <= log["thickness_m"][0]
            and 0 < hollow["min_depth_m"] <= size[0]
        )
        checks.check("spec.hollow", ok, f"optional; needs exactly {sorted(HOLLOW)}: min_wall_m above 0, min_clear_m above 0 and, with a wall either side, no more than the log's least thickness, min_depth_m above 0 and no more than the bounds' length (x), on a log (`log`)")
    top = spec.get("top")
    if top is not None:
        ok = isinstance(top, dict) and set(top) == {"min_level_share"} and type(top["min_level_share"]) is float and 0 < top["min_level_share"] <= 1
        checks.check("spec.top", ok, "optional; needs exactly min_level_share, a share in (0, 1]: how much of what is seen from above is near level")
    checks.check("spec.soft_edges", isinstance(spec.get("soft_edges", False), bool) and (not spec.get("soft_edges") or "NORMAL" in spec["attributes"]), "optional; true or false, and true needs NORMAL in attributes")
    painted = spec.get("painted_shading")
    if painted is not None:
        keys = set(painted) if isinstance(painted, dict) else set()
        wanted = {**PAINTED, **(CREVICE if keys & set(CREVICE) else {}), **(GROWTH if keys & set(GROWTH) else {}), **(BLOTCH if keys & set(BLOTCH) else {})}
        optional = {**SIDE_SHADE, **({**GROWTH_WHERE, **GROWTH_LOOK} if "growth" in keys else {})}
        wanted.update({key: kind for key, kind in optional.items() if key in keys})
        wanted.update(GROWTH_EDGE if "growth" in keys and keys & set(GROWTH_EDGE) else {})
        wanted.update({**(GRAIN if keys & set(GRAIN) else {}), **(CLOSE if keys & set(CLOSE) else {})})
        ok = keys == set(wanted) and all(type(painted[key]) is kind for key, kind in wanted.items())
        ok = ok and all(re.fullmatch(HEX, painted[key]) for key in ("base_tint", "top_tint", "growth") if key in painted)
        checks.check(
            "spec.painted_shading",
            ok,
            f"optional; needs exactly {sorted(PAINTED)}, with or without {sorted(CREVICE)} together, {sorted(GROWTH)} (and then {sorted(GROWTH_WHERE)}, {sorted(GROWTH_LOOK)}; {sorted(GROWTH_EDGE)} together), {sorted(BLOTCH)} together, {sorted(SIDE_SHADE)}; colours as #rrggbb",
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
            amounts_ok = 0 <= painted["edge_light"] <= 1 and 0 <= painted.get("crevice_shadow", 0.0) < 1 and painted["edge_width_m"] > 0 and painted.get("crevice_width_m", 1.0) > 0
            if "overlap" in spec:
                checks.check("spec.painted_joins", "crevice_shadow" in painted, "overlapping pieces are joined by what the crevice shadow hides (ADR 13): painted_shading needs crevice_shadow and crevice_width_m")
            strengths_ok = all(0 <= painted.get(key, 0.0) <= 1 for key in (*GROWTH_WHERE, "blotch")) and 0 <= painted.get("side_shade", 0.0) < 1 and painted.get("blotch_size_m", 1.0) > 0
            strengths_ok = strengths_ok and 0 <= painted.get("growth_darker", 0.0) < 1 and painted.get("growth_patch_m", 1.0) > 0 and painted.get("growth_edge_m", 1.0) > 0
            checks.check(
                "spec.painted_amounts",
                amounts_ok and strengths_ok and painted.get("growth_height_m", 1.0) > 0,
                "edge_light, growth_up, growth_edges and blotch in 0..1; crevice_shadow, side_shade and growth_darker in 0..1 (below 1); widths, growth height, growth patch size, growth_edge_m and blotch size above 0",
            )
    if painted is not None and all(type(painted.get(key, 0.0)) is float for key in (*GRAIN, *CLOSE)):
        checks.check("spec.painted_grain", 0 <= painted.get("grain", 0.0) <= 1 and painted.get("grain_width_m", 1.0) > 0, "grain in 0..1 and grain_width_m above 0")
        least = conv["painted_shading"]["min_texels_per_m"]
        checks.check(
            "spec.painted_close",
            painted.get("close_height_m", 1.0) > 0 and painted.get("close_texels_per_m", least) >= least,
            f"close_height_m above 0, and close_texels_per_m at least the {least} every face gets (conventions.toml)",
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
    if skeleton:
        checks.check(
            "spec.skeleton_view",
            0 < skeleton["min_view_tone"] < 1 and skeleton["min_view_grain"] >= 1 and skeleton["min_canopy_over_limbs"] > 1,
            "min_view_tone in 0..1; min_view_grain at least 1: tone changes faster across the trunk than along it; min_canopy_over_limbs above 1: seen from below the foliage is the lighter of the two",
        )
    # Foliage that is not pads over cores: blades from one point, or stalks in a bed.
    bladed = "blades" in spec or "stalks" in spec
    blades = block("blades", BLADES)
    if blades:
        checks.check(
            "spec.blades_amounts",
            span(blades["width_share"]) and blades["width_share"][1] <= 1 and blades["root_m"] > 0 and 0 < blades["max_gap_deg"] <= 360
            and span(blades["lean_deg"]) and blades["lean_deg"][1] <= 180 and 0 <= blades["min_arch"] < 1,
            "width_share and lean_deg as [least, most], a width at most the length and a lean at most 180 degrees; root_m above 0; max_gap_deg in 0..360; min_arch in 0..1",
        )
    stalks = block("stalks", STALKS)
    if stalks:
        whole = lambda pair: len(pair) == 2 and all(type(n) is int for n in pair) and 1 <= pair[0] <= pair[1]
        checks.check(
            "spec.stalks_amounts",
            "blades" not in spec and "clump" in spec and whole(stalks["count"]) and whole(stalks["leaves"])
            and all(span(stalks[key]) and stalks[key][0] > 0 for key in ("length_m", "width_m", "leaf_width_share", "head_width_m", "head_share"))
            and stalks["leaf_width_share"][1] <= 1 and stalks["head_share"][1] <= 1 and 0 < stalks["min_round"] <= 1 and stalks["foot_m"] > 0
            and 0 < stalks["max_lean_deg"] < 90 and stalks["min_apart_m"] > 0 and 0 < stalks["min_bed"] <= 1 and 0 <= stalks["min_leaf_sweep"] < 1 and 0 < stalks["min_head_fullness"] <= 1,
            "not on a plant of blades (`blades`: a plant is one or the other), and with a `clump`, which says how many stalks stand upright; count and leaves as [least, most] whole numbers, at least 1; "
            "length_m, width_m, leaf_width_share, head_width_m and head_share as [least, most], above 0, the shares at most 1; min_round, min_bed and min_head_fullness in (0, 1]; "
            "foot_m and min_apart_m above 0; max_lean_deg in 0..90; min_leaf_sweep in 0..1",
        )
    clump = block("clump", CLUMP)
    if clump:
        checks.check(
            "spec.clump_amounts",
            bladed and 0 < clump["upright_deg"] < 90 and 0 < clump["min_upright_share"] <= 1 and 0 < clump["max_sky_share"] < 1,
            "on a plant of blades or of stalks (`blades`, `stalks`); upright_deg in 0..90; min_upright_share in (0, 1]; max_sky_share above 0 and below 1 (at 1 it asks nothing)",
        )
    heads = block("heads", HEADS)
    if heads:
        count = heads["count"]
        checks.check(
            "spec.heads_amounts",
            bladed and spec["watertight"] and len(count) == 2 and all(type(n) is int for n in count) and 1 <= count[0] <= count[1]
            and span(heads["size_m"]) and heads["size_m"][0] > 0 and 0 < heads["min_height"] < 1,
            "on a watertight plant of blades or of stalks (`blades`, `stalks`): a head is closed, and a blade or a stalk carries it; count as [least, most] whole numbers, at least 1; size_m as [least, most], above 0; min_height above 0 and below 1, a share of the bounds' height",
        )
    if bladed:
        checks.check("spec.blades_need_foliage", isinstance(spec.get("foliage"), dict), "blades and stalks are foliage: the spec needs a foliage block for their material, size and palette")
    leaves = block("foliage", {key: FOLIAGE[key] for key in FOLIAGE_SHARED} if bladed else FOLIAGE)
    if leaves and not bladed:
        lobes = leaves["lobes"]
        checks.check(
            "spec.foliage_core",
            len(lobes) == 2 and all(type(n) is int for n in lobes) and 1 <= lobes[0] <= lobes[1]
            and leaves["min_lobe_ratio"] >= 1 and leaves["min_pad_flatness"] > 0 and leaves["min_pad_spread"] >= 1 and leaves["min_rim_points_per_m"] >= 0
            and all(0 <= leaves[key] <= 1 for key in ("max_core_seen", "max_core_seen_below", "max_seen_into"))
            and re.fullmatch(HEX, leaves["core_tint"]) is not None,
            "lobes as [least, most] whole numbers; min_lobe_ratio and min_pad_spread at least 1; max_core_seen, max_core_seen_below and max_seen_into in 0..1; core_tint as #rrggbb",
        )
        if re.fullmatch(HEX, leaves["core_tint"]) and re.fullmatch(HEX, str(leaves["under_tint"])):
            checks.check(
                "spec.foliage_core_darker",
                luma(leaves["core_tint"]) < luma(leaves["under_tint"]),
                f"core_tint {leaves['core_tint']} is not darker than under_tint {leaves['under_tint']} (ADR 9: a dark core under the leaf pieces)",
            )
    if leaves:
        ok = (
            leaves["material"] in open_materials
            and leaves["pad_gap_m"] > 0
            and leaves["min_pad_pieces"] >= 1
            and span(leaves["piece_m"])
            and (
                bladed
                or (
                    1 <= leaves["min_pads"] <= leaves["max_pads"]
                    and span(leaves["sky_share"])
                    and leaves["sky_share"][1] < 1
                    and 0 < leaves["min_sky_views"] <= len(conv["foliage"]["views"])
                    and all(0 <= leaves[key] <= 1 for key in ("min_pointing_out", "min_pointing_down"))
                )
            )
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
    tiers = block("tiers", TIERS)
    if tiers:
        checks.check(
            "spec.tiers_amounts",
            leaves is not None and skeleton is not None and not bladed and tiers["widest_among_lowest"] >= 1
            and all(0 < tiers[key] <= 1 for key in ("min_narrowing", "max_top_share"))
            and all(tiers[key] > 0 for key in ("min_droop", "max_tip_width_m", "max_leader_bow_m")) and span(tiers["tip_off_m"]),
            "tiers are foliage in pads round a leader: the spec needs its foliage and skeleton blocks; widest_among_lowest at least 1; min_narrowing and max_top_share in 0..1; min_droop, max_tip_width_m and max_leader_bow_m above 0; tip_off_m as [least, most]",
        )
    # A tree is drawn from a species recipe at a growth stage (ADR 13): source/<family>/species/<species>.toml.
    family, species = spec.get("family"), spec.get("species")
    recipe = None
    if species is not None or skeleton:
        path = ROOT / "source" / str(family) / "species" / f"{species}.toml"
        if isinstance(species, str) and isinstance(family, str) and path.is_file():
            with open(path, "rb") as f:
                recipe = tomllib.load(f)
        checks.check("spec.species", recipe is not None, "an asset with a skeleton names its `family` and a `species` with a recipe at source/<family>/species/<species>.toml")
    # A season is one of the year's (conventions.toml), and every asset with foliage has one.
    seasons = conv["palette"]["seasons"]
    if "season" in spec or leaves:
        checks.check("spec.season", spec.get("season") in seasons, f"an asset with foliage names its season, one of {seasons}")
    # What lies on the asset (docs/style/catalogue.md): a cover other than bare is growth painted on it (ADR 10).
    covers = conv["palette"]["covers"]
    if "cover" in spec:
        grown = isinstance(spec.get("painted_shading"), dict) and "growth" in spec["painted_shading"]
        checks.check(
            "spec.cover",
            spec["cover"] in covers and grown == (spec["cover"] != "bare"),
            f"optional; one of {covers}; every cover but bare has `growth` in its painted_shading, and bare has none",
        )
    # A palette variant is its base asset drawn again with other colours (ADR 11, ADR 13): the two
    # specs agree on everything that shapes the mesh, and differ in what the variant is a variant in.
    # A season differs in its palette and its materials' colours, a cover in the growth painted on it.
    if "palette_of" in spec:
        base_path = ROOT / "source" / str(spec["palette_of"]) / "spec.json"
        ok = isinstance(spec["palette_of"], str) and spec["palette_of"] != asset.name and base_path.is_file()
        shape, colours, kinds = [], [], []
        allowed = {
            "season": set(conv["palette"]["keys"]) | {f"materials.{name}" for name in spec["materials"]},
            "cover": set(conv["palette"]["cover_keys"]),
        }
        if ok:
            base = json.loads(base_path.read_text())

            def values(of):
                found = {}

                def walk(value, path=""):
                    if isinstance(value, dict):
                        for key, child in value.items():
                            walk(child, f"{path}.{key}" if path else key)
                    else:
                        found[path] = value

                walk(of)
                return found

            mine, theirs = values(spec), values(base)
            # A base that names no cover is bare, unless it has growth of its own, and then what it is under is not known.
            theirs.setdefault("cover", None if "painted_shading.growth" in theirs else "bare")
            # What this is a variant in: what it names (its season, its cover) that is not its base's.
            kinds = [kind for kind in allowed if kind in mine and mine[kind] != theirs.get(kind)]
            free = set().union(*(allowed[kind] for kind in kinds))
            # The asset's own name, and the comparison with sibling seeds, which a palette variant does not repeat.
            apart = {"asset", "objects", "palette_of", *allowed} | {key for key in set(mine) | set(theirs) if key.startswith("variants.")}
            shape = sorted(key for key in (set(mine) | set(theirs)) - free - apart if mine.get(key) != theirs.get(key))
            colours = sorted(key for key in free if mine.get(key) != theirs.get(key))
        checks.check(
            "spec.palette_of",
            ok and kinds and not shape and colours,
            f"names another asset with a spec.json, and a season or a cover that is not that asset's (it differs in {kinds}); its spec then matches the base's in everything but what that may change "
            f"(a season: {sorted(conv['palette']['keys'])} and the material colours; a cover: {sorted(conv['palette']['cover_keys'])}), and differs from it there; "
            f"differs outside that in {shape}, and inside it in {colours}",
        )
    stage = spec.get("growth_stage")
    if stage is not None or recipe is not None:
        growth = (recipe or {}).get("growth", {})
        stages = growth.get("stage", [])
        ok = recipe is not None and type(stage) is float and bool(stages) and stages[0] <= stage <= stages[-1]
        checks.check("spec.growth_stage", ok, f"with a species: a number from {stages[0] if stages else '?'} to {stages[-1] if stages else '?'}, the stages its recipe draws (the tree's height over a mature tree's)")
        if ok:
            height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
            low, high = (round(stage * h, 3) for h in growth["mature_height_m"])
            checks.check("spec.growth_height", low <= height <= high, f"the bounds are {height:g} m tall; at growth stage {stage:g} the recipe's mature height {growth['mature_height_m']} gives {low:g} to {high:g} m")
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
    # The family's rows, then its species' where the species has a brief of its own beside its recipe, then the asset's.
    species_rows = numbers(ROOT / "source" / spec["family"] / "species" / f"{spec.get('species')}.md")
    rows = {**numbers(ROOT / "source" / spec["family"] / "brief.md"), **species_rows, **rows}


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
