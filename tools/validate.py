"""Gate L1: mesh checks on a built asset, against its spec and conventions.toml.

Expected values come from the spec, never from the build script.

Usage: tools/bl tools/validate.py <asset>
"""

import json
import math
import re
import runpy
import statistics
import sys
from pathlib import Path

import bmesh
import bpy
import numpy
from mathutils import Matrix, Vector, geometry
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foliage
import skeleton
from pipeline import VIEW_DIRECTIONS, Asset, Checks, conventions, linear_rgb, script_args


def evaluated_bmesh(obj):
    """The object's mesh with modifiers applied, in world space."""
    bm = bmesh.new()
    bm.from_object(obj, bpy.context.evaluated_depsgraph_get())
    bm.transform(obj.matrix_world)
    return bm


def planes_of(bm, floor_z, tol, conv):
    """Group a mesh's faces into planes, and find the ledges between large ones.

    A plane is a connected set of faces whose normals all lie within
    `coplanar_deg` of their area-weighted mean: flat to the eye, however it is
    triangulated. Faces resting on the ground (facing straight down at
    floor_z) are left out, because nobody sees them. Returns (areas of the
    planes, area of everything visible, a function giving the ledges for a
    given large-plane area and ledge length, a function giving the plane a
    face belongs to).
    """
    cos_flat = math.cos(math.radians(conv["planes"]["coplanar_deg"]))
    cos_ledge = math.cos(math.radians(conv["planes"]["ledge_min_deg"]))
    visible = [f for f in bm.faces if not (f.normal.z < -cos_flat and all(abs(v.co.z - floor_z) <= tol for v in f.verts))]
    group = {f: f for f in visible}

    def find(face):
        while group[face] is not face:
            group[face] = group[group[face]]
            face = group[face]
        return face

    for edge in bm.edges:
        faces = [f for f in edge.link_faces if f in group]
        if len(faces) == 2 and faces[0].normal.dot(faces[1].normal) >= cos_flat:
            group[find(faces[0])] = find(faces[1])
    members = {}
    for face in visible:
        members.setdefault(find(face), []).append(face)

    # region root -> (area, normal), only for regions that are flat as a whole:
    # a finely tessellated curve chains neighbour to neighbour and is not a plane.
    planes = {}
    for root, faces in members.items():
        normal = sum((f.normal * f.calc_area() for f in faces), Vector()).normalized()
        if all(f.normal.dot(normal) >= cos_flat for f in faces):
            planes[root] = (sum(f.calc_area() for f in faces), normal)

    def ledges(large_m2, ledge_m):
        """Pairs of large planes meeting in a concave corner at least ledge_m long.

        The corner is either an edge the two planes share, or one soft-edge
        face (a bevel strip) with an edge on each. Returns, per pair, the
        corner's length and the stretches of it: (one end, the other end, the
        direction out of the corner into the open).
        """
        large = {root for root, (area, _) in planes.items() if area >= large_m2}
        runs = {}

        def add(a, b, length, ends):
            if a is not b and planes[a][1].dot(planes[b][1]) <= cos_ledge:
                key = tuple(sorted((a.index, b.index)))
                total, stretches = runs.get(key, (0.0, []))
                runs[key] = (total + length, stretches + [(*ends, (planes[a][1] + planes[b][1]).normalized())])

        def midpoint(edge):
            return (edge.verts[0].co + edge.verts[1].co) / 2

        for edge in bm.edges:
            roots = [find(f) for f in edge.link_faces if f in group]
            if len(roots) == 2 and all(r in large for r in roots) and not edge.is_convex:
                add(roots[0], roots[1], edge.calc_length(), (edge.verts[0].co.copy(), edge.verts[1].co.copy()))
        for face in visible:
            if find(face) in large:
                continue
            # (large plane across this edge, the edge) for each side of the strip
            sides = [(find(other), e) for e in face.edges for other in e.link_faces if other is not face and other in group and find(other) in large]
            for i, (a, edge_a) in enumerate(sides):
                for b, edge_b in sides[i + 1 :]:
                    across = midpoint(edge_b) - midpoint(edge_a)
                    # Concave: each plane's edge sits in front of the other plane.
                    if a is not b and across.dot(planes[a][1]) > tol and -across.dot(planes[b][1]) > tol:
                        shorter = min(edge_a, edge_b, key=lambda e: e.calc_length())
                        # The strip's own middle line, as long as its shorter side.
                        ends = tuple(v.co + across * (0.5 if shorter is edge_a else -0.5) for v in shorter.verts)
                        add(a, b, shorter.calc_length(), ends)
        return {pair: run for pair, run in runs.items() if run[0] >= ledge_m}

    def plane_of(face):
        """The root face of the plane `face` lies in, or None for hidden faces and curved regions."""
        root = find(face) if face in group else None
        return root if root in planes else None

    return [area for area, _ in planes.values()], sum(f.calc_area() for f in visible), ledges, plane_of


def check_planes(checks, name, bm, spec, conv):
    """The shape is a few large planes with a ledge (ADR 9), not a lump of small faces."""
    want = spec["planes"]
    areas, visible, ledges, plane_of = planes_of(bm, spec["bounds_m"]["min"][2], spec["bounds_tolerance_m"], conv)
    large = sorted((a for a in areas if a >= want["large_m2"]), reverse=True)
    share = sum(large) / visible if visible else 0.0
    ratio = large[0] / statistics.median(large) if large else 0.0
    found = ledges(want["large_m2"], want["ledge_m"])
    print(
        f"{name} planes: {len(large)} large (>= {want['large_m2']} m2) holding {share:.3f} of {visible:.2f} m2 visible, "
        f"largest/median {ratio:.2f}, ledges {sorted(round(length, 2) for length, _ in found.values())} m, areas {[round(a, 2) for a in large]}"
    )
    checks.check(
        f"{name}.planes_area_share",
        share >= want["min_area_share"],
        f"planes of at least {want['large_m2']} m2 hold {share:.3f} of the visible surface ({sum(large):.2f} of {visible:.2f} m2); spec wants {want['min_area_share']}",
    )
    checks.check(
        f"{name}.planes_count",
        want["min_count"] <= len(large) <= want["max_count"],
        f"{len(large)} planes of at least {want['large_m2']} m2; spec wants {want['min_count']} to {want['max_count']}",
    )
    checks.check(
        f"{name}.planes_size_ratio",
        ratio >= want["min_size_ratio"],
        f"largest large plane is {ratio:.2f} times the median one; spec wants {want['min_size_ratio']}",
    )
    checks.check(
        f"{name}.planes_ledges",
        len(found) >= want["min_ledges"],
        f"{len(found)} concave corners of at least {want['ledge_m']} m between large planes; spec wants {want['min_ledges']}",
    )

    # What each view shows: the share of the outline its largest plane fills, and how much
    # ledge corner can be seen. A view is parallel rays from far off, as the review tiles are.
    tree = BVHTree.FromBMesh(bm)
    bm.faces.ensure_lookup_table()
    views = conv["planes"]["views"]
    shares, lengths = {}, {}
    for view in views:
        toward = Vector(VIEW_DIRECTIONS[view]).normalized()
        across = toward.cross(Vector((0, 0, 1)) if abs(toward.z) < 0.9 else Vector((0, 1, 0))).normalized()
        up = across.cross(toward)
        spans = [[v.co.dot(axis) for v in bm.verts] for axis in (across, up, toward)]
        cell = max(max(span) - min(span) for span in spans[:2]) / conv["planes"]["view_rays"]
        hits = {}
        x = min(spans[0]) + cell / 2
        while x < max(spans[0]):
            y = min(spans[1]) + cell / 2
            while y < max(spans[1]):
                index = tree.ray_cast(across * x + up * y + toward * (max(spans[2]) + 1.0), -toward)[2]
                if index is not None:
                    plane = plane_of(bm.faces[index])
                    hits[plane] = hits.get(plane, 0) + 1
                y += cell
            x += cell
        shares[view] = max((count for plane, count in hits.items() if plane is not None), default=0) / max(1, sum(hits.values()))
        seen = 0.0
        for _, stretches in found.values():
            for start, end, out in stretches:
                along = end - start
                for step in range(8):
                    # Seen when nothing lies between this piece of the corner and the camera.
                    piece = start + along * ((step + 0.5) / 8) + out * 0.02
                    if tree.ray_cast(piece, toward)[2] is None:
                        seen += along.cross(toward).length / 8
        lengths[view] = seen
    print(f"{name} views: largest plane's share of the outline {({v: round(s, 2) for v, s in shares.items()})}; ledge corner seen, m {({v: round(l, 2) for v, l in lengths.items()})}")
    worst = max(shares, key=shares.get)
    checks.check(
        f"{name}.planes_view_share",
        shares[worst] <= want["max_view_share"],
        f"from {worst} one plane fills {shares[worst]:.2f} of the outline; spec wants at most {want['max_view_share']} from each of {views}; all {({v: round(s, 2) for v, s in shares.items()})}",
    )
    reading = [view for view in views if lengths[view] >= want["ledge_m"]]
    checks.check(
        f"{name}.planes_ledge_views",
        len(reading) >= want["min_ledge_views"],
        f"at least {want['ledge_m']} m of ledge corner is seen from {len(reading)} of {len(views)} views; spec wants {want['min_ledge_views']}; "
        f"not from {[v for v in views if v not in reading]}; metres seen {({v: round(l, 2) for v, l in lengths.items()})}",
    )


def check_fullness(checks, name, bm, spec, conv):
    """The shape fills its bounding box, and is still broad high up: a boulder, not a wedge."""
    want = spec["fullness"]
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    size = hi - lo
    share = bm.calc_volume(signed=True) / (size.x * size.y * size.z)
    # The crown: the level slice through the shape, as a share of the bounds' footprint.
    level = lo.z + conv["fullness"]["crown_height"] * size.z
    lower = bm.copy()
    cut = bmesh.ops.bisect_plane(lower, geom=lower.verts[:] + lower.edges[:] + lower.faces[:], dist=1e-7, plane_co=(0, 0, level), plane_no=(0, 0, 1), clear_outer=True)
    before = set(lower.faces)
    bmesh.ops.holes_fill(lower, edges=[g for g in cut["geom_cut"] if isinstance(g, bmesh.types.BMEdge)])
    crown = sum(f.calc_area() for f in lower.faces if f not in before) / (size.x * size.y)
    lower.free()
    print(f"{name} fullness: {share:.3f} of its bounding box; crown (slice at {conv['fullness']['crown_height']} of the height) {crown:.3f} of the footprint")
    checks.check(
        f"{name}.fullness",
        share >= want["min_volume_share"],
        f"the shape holds {share:.3f} of its bounding box's volume; spec wants at least {want['min_volume_share']}",
    )
    checks.check(
        f"{name}.crown",
        crown >= want["min_crown_share"],
        f"the slice {conv['fullness']['crown_height']} of the way up is {crown:.3f} of the footprint; spec wants at least {want['min_crown_share']}",
    )


def check_skeleton(checks, name, bm, slots, spec, conv):
    """The bark is a designed trunk that forks into tapering limbs (source/tree/brief.md). Returns the fork's height, or None."""
    want = spec["skeleton"]
    bark = skeleton.only(bm, slots.index(want["material"]))
    found = skeleton.measure(bark, conv)
    bark.free()
    breast = conv["skeleton"]["breast_height_m"]
    shown = {key: round(value, 3) if isinstance(value, float) else value for key, value in found.items()}
    print(f"{name} skeleton: {shown}")
    checks.check(
        f"{name}.trunk_sides",
        found["sides"] is not None and want["min_sides"] <= found["sides"] <= want["max_sides"],
        f"the trunk's slice {breast} m up has {found['sides']} flat sides; spec wants {want['min_sides']} to {want['max_sides']}",
    )
    low, high = want["fork_m"]
    checks.check(
        f"{name}.fork",
        found["fork_m"] is not None and low <= found["fork_m"] <= high,
        f"the bark first shows two limbs in one slice at {shown['fork_m']} m (None: never); spec wants a fork between {low} and {high} m",
    )
    checks.check(
        f"{name}.trunk_tapers",
        found["taper"] is not None and found["taper"] <= want["max_taper"],
        f"just below the fork the trunk is {shown['taper']} of its radius {breast} m up ({shown['breast_m']} m); spec wants at most {want['max_taper']}",
    )
    checks.check(
        f"{name}.branches",
        found["branches"] >= want["min_branches"],
        f"no slice through the bark shows more than {found['branches']} limbs; spec wants at least {want['min_branches']}",
    )
    checks.check(
        f"{name}.branches_taper",
        found["branch_taper"] is not None and found["branch_taper"] <= want["max_branch_taper"],
        f"four fifths of the way from the fork to the top, limbs are {shown['branch_taper']} as thick as one fifth of the way; spec wants at most {want['max_branch_taper']}",
    )
    checks.check(
        f"{name}.roots",
        found["flare"] is not None and found["flare"] >= want["min_flare"] and found["roots"] >= want["min_roots"],
        f"at the ground the trunk reaches {shown['flare']} times its radius {breast} m up, in {found['roots']} roots; spec wants at least {want['min_flare']} times and {want['min_roots']} roots",
    )
    low, high = want["lean_m"]
    checks.check(
        f"{name}.lean",
        found["lean_m"] is not None and low <= found["lean_m"] <= high,
        f"the trunk below the fork stands {shown['lean_m']} m to the side of its foot; spec wants {low} to {high} m",
    )
    return found["fork_m"]


def check_foliage(checks, name, bm, slots, spec, conv, fork_m):
    """The foliage is leaf-shaped pieces in separate pads with sky between (ADR 9), and the skeleton shows through it."""
    want = spec["foliage"]
    rules = conv["foliage"]
    leaf = slots.index(want["material"])
    pieces = foliage.pieces_of(bm, leaf)
    shapes = [foliage.piece_shape(piece) for piece in pieces]
    lengths = sorted(shape["length_m"] for shape in shapes)
    low, high = want["piece_m"]
    odd = [length for length in lengths if not low <= length <= high]
    checks.check(
        f"{name}.leaf_size",
        pieces and not odd,
        f"{len(odd)} of {len(pieces)} leaf pieces are not {low} to {high} m long; lengths run from {lengths[0] if lengths else 0:.2f} to {lengths[-1] if lengths else 0:.2f} m",
    )
    bent = sum(1 for shape in shapes if shape["off_plane_m"] > rules["flat_m"])
    blunt = sum(1 for shape in shapes if shape["sharpest_deg"] > rules["pointed_deg"])
    smooth = sum(1 for shape in shapes if shape["notches"] < 1)
    checks.check(
        f"{name}.leaf_shape",
        pieces and not (bent or blunt or smooth),
        f"of {len(pieces)} leaf pieces, {bent} are not flat (within {rules['flat_m']} m), {blunt} have no corner of {rules['pointed_deg']} degrees or less, {smooth} have no notch in their outline",
    )

    # Cores (ADR 9 as amended) join the pieces lying on them into one pad; check_canopy measures the cores themselves.
    cores = foliage.cores_of(bm, leaf)
    pads, _ = foliage.pads_with_cores(pieces, cores, want["pad_gap_m"])
    sizes = [pads.count(pad) for pad in range(max(pads, default=-1) + 1)]
    whole = [size for size in sizes if size >= want["min_pad_pieces"]]
    strays = sum(size for size in sizes if size < want["min_pad_pieces"])
    checks.check(
        f"{name}.pads",
        want["min_pads"] <= len(whole) <= want["max_pads"] and not strays,
        f"{len(whole)} pads of at least {want['min_pad_pieces']} pieces with {want['pad_gap_m']} m of clear air between them (sizes {whole[:8]}), and {strays} pieces in "
        f"{len(sizes) - len(whole)} smaller clumps; spec wants {want['min_pads']} to {want['max_pads']} pads and no strays",
    )
    middles = {}
    for shape, pad in zip(shapes, pads):
        middles.setdefault(pad, []).append(shape["middle"])
    middles = {pad: sum(points, Vector()) / len(points) for pad, points in middles.items()}
    out = sum(1 for shape, pad in zip(shapes, pads) if (shape["middle"] - middles[pad]).dot(shape["points"]) > 0) / max(len(shapes), 1)
    down = sum(1 for shape in shapes if shape["points"].z < 0) / max(len(shapes), 1)
    checks.check(
        f"{name}.leaves_point_out",
        out >= want["min_pointing_out"] and down >= want["min_pointing_down"],
        f"{out:.2f} of the leaf pieces point out of their pad and {down:.2f} point below level; spec wants at least {want['min_pointing_out']} and {want['min_pointing_down']}",
    )

    # What each view shows: sky through the canopy, and bark among what is seen above the fork.
    if not pieces and not cores:
        return
    tree = BVHTree.FromBMesh(bm)
    bm.faces.ensure_lookup_table()
    canopy = [v.co.copy() for part in pieces + cores for face in part for v in face.verts]
    floor = spec["bounds_m"]["min"][2]
    above = floor + (fork_m if fork_m is not None else spec.get("skeleton", {}).get("fork_m", [0.0])[0])
    bark = slots.index(spec["skeleton"]["material"]) if "skeleton" in spec else -1
    views = {view: VIEW_DIRECTIONS[view] for view in rules["views"]}
    seen = {view: foliage.sky_and_bark(tree, bm.faces, bark, canopy, direction, rules["view_rays"], above) for view, direction in {**views, "below": (0, 0, -1)}.items()}
    sky = {view: round(seen[view][0], 3) for view in views}
    low, high = want["sky_share"]
    open_views = [view for view in views if low <= sky[view] <= high]
    print(f"{name} foliage: {len(pieces)} pieces {lengths[0] if lengths else 0:.2f} to {lengths[-1] if lengths else 0:.2f} m, pads {sizes}, pointing out {out:.2f} and down {down:.2f}, sky {sky}")
    checks.check(
        f"{name}.sky",
        len(open_views) >= want["min_sky_views"],
        f"sky is {low} to {high} of the canopy's outline from {len(open_views)} of {len(views)} views; spec wants {want['min_sky_views']}; shares {sky}",
    )
    if "skeleton" in spec:
        share = {view: round(seen[view][1], 3) for view in seen}
        showing = [view for view in seen if share[view] >= spec["skeleton"]["min_seen_share"]]
        print(f"{name} skeleton seen above the fork: {share}")
        checks.check(
            f"{name}.branches_seen",
            len(showing) >= spec["skeleton"]["min_seen_views"],
            f"bark is at least {spec['skeleton']['min_seen_share']} of what is seen above the fork from {len(showing)} of {len(seen)} views; "
            f"spec wants {spec['skeleton']['min_seen_views']}; shares {share}",
        )


def check_canopy(checks, name, bm, slots, spec, conv):
    """Pads are lumpy masses of leaf pieces over dark cores, wider than tall and of different sizes, and read as foliage from below (ADR 9 as amended)."""
    want, rules = spec["foliage"], conv["foliage"]
    leaf = slots.index(want["material"])
    pieces, cores = foliage.pieces_of(bm, leaf), foliage.cores_of(bm, leaf)
    piece_pads, core_pads = foliage.pads_with_cores(pieces, cores, want["pad_gap_m"])
    whole = sorted(pad for pad in set(piece_pads) if piece_pads.count(pad) >= want["min_pad_pieces"])

    def box(parts):
        points = [v.co for part in parts for face in part for v in face.verts]
        return [max(p[i] for p in points) - min(p[i] for p in points) for i in range(3)]

    def width(parts):
        x, y, _ = box(parts)
        return math.sqrt(x * y)

    # Cores: each pad has its lobes, each a closed solid facing outward.
    low, high = want["lobes"]
    in_pad = {pad: [core for core, at in zip(cores, core_pads) if at == pad] for pad in whole}
    counts = [len(in_pad[pad]) for pad in whole]
    stray = sum(1 for at in core_pads if at not in whole)
    volumes = [sum(f.verts[0].co.dot(a.co.cross(b.co)) for f in core for a, b in zip(f.verts[1:], f.verts[2:])) / 6 for core in cores]
    inside_out = sum(1 for volume in volumes if volume <= 0)
    # A part too large to be a leaf piece, and not closed, is a core with a hole in it.
    holed = sum(1 for piece in pieces if sum(len(f.verts) - 2 for f in piece) >= rules["core_min_triangles"])
    checks.check(
        f"{name}.cores",
        whole and all(low <= count <= high for count in counts) and not stray and not inside_out and not holed,
        f"the {len(whole)} pads have {counts} cores (closed solids of the foliage material), {stray} cores lie outside any pad, {inside_out} are inside out and {holed} are not closed; spec wants {low} to {high} closed cores in every pad",
    )
    ratios = [round(max(map(lambda core: width([core]), found)) / min(map(lambda core: width([core]), found)), 2) if len(found) > 1 else 1.0 for found in in_pad.values()]
    checks.check(
        f"{name}.lobes_differ",
        ratios and min(ratios) >= want["min_lobe_ratio"],
        f"in each pad the widest core over the narrowest is {ratios}; spec wants at least {want['min_lobe_ratio']} in every pad: lobes of different sizes",
    )

    # Pads: wider than tall, and of different widths within the tree.
    of_pad = {pad: [piece for piece, at in zip(pieces, piece_pads) if at == pad] for pad in whole}
    widths = [round(width(found), 2) for found in of_pad.values()]
    flatness = [round(width(found) / box(found)[2], 2) for found in of_pad.values()]
    spread = max(widths) / min(widths) if widths else 0.0
    print(f"{name} canopy: pads {widths} m wide, {flatness} times as wide as tall; cores per pad {counts}, widest core over narrowest {ratios}")
    checks.check(
        f"{name}.pads_wide",
        flatness and min(flatness) >= want["min_pad_flatness"],
        f"the pads are {flatness} times as wide as they are tall (widths {widths} m); spec wants at least {want['min_pad_flatness']} of every pad",
    )
    checks.check(
        f"{name}.pads_differ",
        spread >= want["min_pad_spread"],
        f"the widest pad is {spread:.2f} times the narrowest (widths {widths} m); spec wants at least {want['min_pad_spread']}",
    )
    if not pieces and not cores:
        return

    # How much core each view shows, of the foliage it shows.
    tree = BVHTree.FromBMesh(bm)
    bm.faces.ensure_lookup_table()
    canopy = [v.co.copy() for part in pieces + cores for face in part for v in face.verts]
    is_core = {face.index for core in cores for face in core}
    is_piece = {face.index for piece in pieces for face in piece}
    shown = {}
    for view, direction in {**{view: VIEW_DIRECTIONS[view] for view in rules["views"]}, "below": (0, 0, -1)}.items():
        hits = foliage.seen_first(tree, canopy, direction, rules["view_rays"])
        core, leaves = sum(1 for index in hits if index in is_core), sum(1 for index in hits if index in is_piece)
        shown[view] = round(core / max(core + leaves, 1), 3)
    print(f"{name} core seen, as a share of the foliage seen: {shown}")
    over = {view: share for view, share in shown.items() if share > (want["max_core_seen_below"] if view == "below" else want["max_core_seen"])}
    checks.check(
        f"{name}.core_hidden",
        not over,
        f"core is {over} of the foliage seen; spec wants at most {want['max_core_seen']} from each side and {want['max_core_seen_below']} from below: the leaf pieces are what is seen; all {shown}",
    )

    # From below: what a pad's outline shows. A ray straight up inside it must stop at the pad's
    # underside (a core, or pieces hanging there), not pass up into the pad or through it to the sky.
    lo, hi = [min(p[i] for p in canopy) for i in range(3)], [max(p[i] for p in canopy) for i in range(3)]
    cell = rules["below_cell_m"]
    first, height, above = foliage.from_below(tree, lo, hi, cell)
    pad_of_face = {face.index: pad for part, pad in zip(pieces + cores, piece_pads + core_pads) for face in part}
    pad_first = numpy.vectorize(lambda index: pad_of_face.get(index, -1))(first)
    pad_above = numpy.vectorize(lambda index: pad_of_face.get(index, -1))(above)
    piece_first = numpy.isin(first, list(is_piece))
    into = {}
    for pad in whole:
        mine = pad_first == pad
        outline = numpy.logical_or(mine, pad_above == pad)
        if not mine.any():
            into[pad] = 1.0
            continue
        underside = numpy.percentile(height[mine], 20)
        deep = numpy.logical_and(numpy.logical_and(mine, piece_first), height > underside + rules["seen_into_m"])
        holes = numpy.logical_and(foliage.closing(outline, max(1, round(rules["hole_m"] / cell))), first < 0)
        into[pad] = round(float((deep.sum() + holes.sum()) / (outline.sum() + holes.sum())), 3)
    worst = max(into.values(), default=1.0)
    checks.check(
        f"{name}.under_closed",
        whole and worst <= want["max_seen_into"],
        f"looking straight up, {worst:.3f} of the worst pad's outline shows the inside of the pad (a piece more than {rules['seen_into_m']} m above its underside) or sky through a gap; "
        f"spec wants at most {want['max_seen_into']} of every pad; pads {list(into.values())}",
    )

    # And its rim reads as leaves: points of pieces stand clear against the sky.
    def clear(x, y):
        return tree.ray_cast(Vector((x, y, lo[2] - 1.0)), Vector((0, 0, 1)))[2] is None

    points = {pad: 0 for pad in whole}
    for piece, pad in zip(pieces, piece_pads):
        shape = foliage.piece_shape(piece)
        out = Vector((shape["points"].x, shape["points"].y))
        if pad not in points or shape["tip"] is None or out.length < 0.2:
            continue
        out.normalize()
        tip = Vector((shape["tip"].x, shape["tip"].y))
        mine = {face.index for face in piece}
        # The tip itself is seen from below, and there is sky just past it and either side of it.
        seen = tree.ray_cast(Vector((*(tip - out * rules["rim_step_m"]), lo[2] - 1.0)), Vector((0, 0, 1)))[2] in mine
        around = [tip + Matrix.Rotation(math.radians(turn), 2) @ out * rules["rim_step_m"] for turn in (-70, 0, 70)]
        if seen and all(clear(*at) for at in around):
            points[pad] += 1
    rim = {}
    for pad in whole:
        flat = [(v.co.x, v.co.y) for piece in of_pad[pad] for face in piece for v in face.verts]
        hull = [Vector(flat[i]) for i in geometry.convex_hull_2d(flat)]
        rim[pad] = round(points[pad] / sum((b - a).length for a, b in zip(hull, hull[1:] + hull[:1])), 2)
    print(f"{name} from below: seen into each pad {list(into.values())}; points clear against the sky per metre of outline {list(rim.values())}")
    checks.check(
        f"{name}.under_rim",
        whole and min(rim.values()) >= want["min_rim_points_per_m"],
        f"looking straight up, the pads show {list(rim.values())} points of leaf pieces clear against the sky per metre of their outline; spec wants at least {want['min_rim_points_per_m']} of every pad",
    )


def check_variants(checks, name, bm, spec, conv):
    """This asset's outline differs from each of its sibling variants' (source/tree/brief.md)."""
    want = spec["variants"]
    rules = conv["variants"]
    apart = {}
    for sibling in want["siblings"]:
        other_spec = Asset(sibling).spec()
        before = {kind: set(getattr(bpy.data, kind)) for kind in ("objects", "meshes", "materials")}
        # The sibling as its own build script draws it; shape only, so it is not painted.
        built = runpy.run_path(str(Asset(sibling).source / "build.py"))["build"](other_spec)
        bpy.context.view_layer.update()
        other = evaluated_bmesh(built)
        for kind, had in before.items():
            for block in set(getattr(bpy.data, kind)) - had:
                getattr(bpy.data, kind).remove(block)
        lo = [min(a, b) for a, b in zip(spec["bounds_m"]["min"], other_spec["bounds_m"]["min"])]
        hi = [max(a, b) for a, b in zip(spec["bounds_m"]["max"], other_spec["bounds_m"]["max"])]
        mine, theirs = BVHTree.FromBMesh(bm), BVHTree.FromBMesh(other)
        differences = [
            foliage.difference(foliage.outline(mine, lo, hi, VIEW_DIRECTIONS[view], rules["view_rays"]), foliage.outline(theirs, lo, hi, VIEW_DIRECTIONS[view], rules["view_rays"]))
            for view in rules["views"]
        ]
        other.free()
        apart[sibling] = round(float(sum(differences) / len(differences)), 3)
    print(f"{name} variants: outline differs from {apart}")
    close = {sibling: share for sibling, share in apart.items() if share < want["min_difference"]}
    checks.check(
        "variants.differ",
        apart and not close,
        f"seen from {rules['views']}, this asset's outline differs from {close} by less than {want['min_difference']} (the share of what either covers that only one covers); all {apart}",
    )


def check_scene(checks, spec, conv):
    """Run every L1 check against the scene currently open in Blender."""
    # matrix_world is stale until the depsgraph has been evaluated.
    bpy.context.view_layer.update()
    name_re = re.compile(conv["naming"]["pattern"])
    tolerance = conv["transform"]["tolerance"]
    mesh_objects = {o.name: o for o in bpy.data.objects if o.type == "MESH"}

    wanted = set(spec["objects"])
    checks.check("objects.present", wanted <= set(mesh_objects), f"missing {sorted(wanted - set(mesh_objects))}")
    checks.check("objects.unexpected", set(mesh_objects) <= wanted, f"not in spec: {sorted(set(mesh_objects) - wanted)}")

    triangles = 0
    lo, hi = Vector((float("inf"),) * 3), Vector((float("-inf"),) * 3)
    materials = {}
    want_lo, want_hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    tol = spec["bounds_tolerance_m"]
    # material name -> depths of its faces below the spec's bounding box
    recess_depths = {name: [] for name in spec.get("recess_m", {})}
    # material name -> each face's smallest in-plane distance to the box's sides
    margins = {name: [] for name in spec.get("margin_m", {})}

    for name in sorted(wanted & set(mesh_objects)):
        obj = mesh_objects[name]
        names = [obj.name, obj.data.name] + [s.material.name for s in obj.material_slots if s.material]
        bad = [n for n in names if not name_re.match(n)]
        checks.check(f"{name}.naming", not bad, f"{bad} do not match {name_re.pattern}")

        rotation = obj.matrix_world.to_euler()
        scale = obj.matrix_world.to_scale()
        applied = all(abs(a) <= tolerance for a in rotation) and all(abs(s - 1) <= tolerance for s in scale)
        checks.check(f"{name}.transform_applied", applied, f"rotation {tuple(rotation)}, scale {tuple(scale)}")

        bm = evaluated_bmesh(obj)
        slot_names = [s.material.name if s.material else "" for s in obj.material_slots]
        # A spec's `open_materials` are made of separate open pieces by design (leaf pieces: ADR 9).
        # Being closed, wound one way, facing outward and free of doubled vertices is asked of
        # everything else: for a tree, the bark. Pieces may touch each other and the bark.
        opened = {i for i, material in enumerate(slot_names) if material in spec.get("open_materials", [])}
        closed = [f for f in bm.faces if f.material_index not in opened]
        closed_edges = {e for f in closed for e in f.edges}
        non_manifold = [e.index for e in closed_edges if not e.is_manifold]
        if spec["watertight"]:
            checks.check(f"{name}.manifold", closed and not non_manifold, f"{len(non_manifold)} non-manifold edges on the {len(closed)} faces that must form a closed surface")
            flipped = [e.index for e in closed_edges if e.is_manifold and not e.is_contiguous]
            checks.check(f"{name}.winding_consistent", not flipped, f"{len(flipped)} edges join faces with opposite winding")
            volume = sum(f.verts[0].co.dot(a.co.cross(b.co)) for f in closed for a, b in zip(f.verts[1:], f.verts[2:])) / 6
            checks.check(f"{name}.normals_outward", volume > 0, f"signed volume {volume:.6f}")
        loose = [v.index for v in bm.verts if not v.link_faces]
        checks.check(f"{name}.no_loose_vertices", not loose, f"{len(loose)} vertices belong to no face")
        tiny = [f.index for f in bm.faces if f.calc_area() < conv["mesh"]["min_face_area_m2"]]
        checks.check(f"{name}.no_degenerate_faces", not tiny, f"{len(tiny)} zero-area faces")
        ngons = [f.index for f in bm.faces if len(f.verts) > conv["mesh"]["max_face_sides"]]
        checks.check(f"{name}.no_ngons", not ngons, f"{len(ngons)} faces with more than {conv['mesh']['max_face_sides']} sides")
        welded = list({v for f in closed for v in f.verts}) if opened else bm.verts
        doubles = bmesh.ops.find_doubles(bm, verts=welded, dist=conv["mesh"]["merge_distance_m"])["targetmap"]
        checks.check(f"{name}.no_duplicate_vertices", not doubles, f"{len(doubles)} duplicate vertices")

        slots = [s.material for s in obj.material_slots]
        checks.check(f"{name}.materials_assigned", slots and all(slots), "empty or missing material slot")
        used = {f.material_index for f in bm.faces}
        checks.check(f"{name}.material_indices_valid", all(i < len(slots) for i in used), f"faces use slots {sorted(used)}")
        for material in filter(None, slots):
            materials[material.name] = material
            # The glTF exporter only reads Principled BSDF.
            out = material.node_tree and next(
                (n for n in material.node_tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output), None
            )
            surface = out and out.inputs["Surface"].links and out.inputs["Surface"].links[0].from_node
            principled = checks.check(f"{material.name}.principled", surface and surface.type == "BSDF_PRINCIPLED", "surface is not a Principled BSDF")
            want = spec["materials"].get(material.name)
            if principled and want:
                # Flat: the socket's own value is the colour. Painted: it is the colour the
                # texture was painted from, kept on the socket under the link (tools/paint.py).
                socket = surface.inputs["Base Color"]
                got = tuple(socket.default_value)[:3]
                close = all(abs(a - b) <= 0.005 for a, b in zip(got, linear_rgb(want)))
                painted = spec.get("painted_shading")
                if painted:
                    source = socket.links[0].from_node if socket.links else None
                    image = source.image if source and source.type == "TEX_IMAGE" else None
                    checks.check(
                        f"{material.name}.painted",
                        image is not None and tuple(image.size) == (painted["texture_px"],) * 2 and image.packed_file is not None and len(obj.data.uv_layers) == 1,
                        f"base colour is fed by {source.bl_idname if source else 'nothing'}, image {tuple(image.size) if image else None}, "
                        f"{len(obj.data.uv_layers)} UV layers; spec wants one packed {painted['texture_px']} px texture and one UV layer",
                    )
                else:
                    close = close and not socket.links
                checks.check(f"{material.name}.base_colour", close, f"linear {tuple(round(c, 3) for c in got)} != spec {want}, or a flat colour has something linked to it")

        for face in bm.faces:
            slot = slots[face.material_index] if face.material_index < len(slots) else None
            if slot and slot.name in recess_depths:
                # Distance from the face to the bounding-box plane it faces.
                box_plane = sum(max(n * a, n * b) for n, a, b in zip(face.normal, want_lo, want_hi))
                recess_depths[slot.name].append(box_plane - face.normal.dot(face.calc_center_median()))
            if slot and slot.name in margins:
                # Only meaningful for faces parallel to a side of the box.
                axis = max(range(3), key=lambda i: abs(face.normal[i]))
                if abs(face.normal[axis]) < 0.999:
                    margins[slot.name].append(None)
                else:
                    margins[slot.name].append(
                        min(min(v.co[i] - want_lo[i], want_hi[i] - v.co[i]) for v in face.verts for i in range(3) if i != axis)
                    )

        if "planes" in spec:
            check_planes(checks, name, bm, spec, conv)
        if "fullness" in spec and spec["watertight"]:
            check_fullness(checks, name, bm, spec, conv)
        bm.normal_update()
        fork_m = check_skeleton(checks, name, bm, slot_names, spec, conv) if "skeleton" in spec and spec["skeleton"]["material"] in slot_names else None
        if "foliage" in spec and spec["foliage"]["material"] in slot_names:
            check_foliage(checks, name, bm, slot_names, spec, conv, fork_m)
            check_canopy(checks, name, bm, slot_names, spec, conv)
        if "variants" in spec:
            check_variants(checks, name, bm, spec, conv)

        triangles += sum(len(f.verts) - 2 for f in bm.faces)
        for v in bm.verts:
            lo = Vector(map(min, lo, v.co))
            hi = Vector(map(max, hi, v.co))
        bm.free()

    checks.check("budget.triangles", triangles <= spec["max_triangles"], f"{triangles} > {spec['max_triangles']}")
    checks.check("materials.match_spec", set(materials) == set(spec["materials"]), f"{sorted(materials)} != spec {sorted(spec['materials'])}")
    for name, depths in recess_depths.items():
        want = spec["recess_m"][name]
        off = [round(d, 4) for d in depths if abs(d - want) > tol]
        checks.check(
            f"{name}.recess",
            depths and not off,
            f"{len(off)} of {len(depths)} faces are not {want} m below the bounds; depths {sorted(set(off))}",
        )
    for name, found in margins.items():
        want = spec["margin_m"][name]
        off = [m if m is None else round(m, 4) for m in found if m is None or abs(m - want) > tol]
        checks.check(
            f"{name}.margin",
            found and not off,
            f"{len(off)} of {len(found)} faces are not {want} m in from the bounds' sides; found {off[:6]} (None: face not axis-aligned)",
        )
    in_bounds = triangles > 0 and (lo - want_lo).length <= tol and (hi - want_hi).length <= tol
    checks.check("bounds.match_spec", in_bounds, f"{tuple(lo)}..{tuple(hi)} != {tuple(want_lo)}..{tuple(want_hi)}")
    return triangles


if __name__ == "__main__":
    asset = Asset(script_args()[0])
    bpy.ops.wm.open_mainfile(filepath=str(asset.blend))
    checks = Checks("L1-mesh", asset.name)
    check_scene(checks, asset.spec(), conventions())
    checks.finish(asset.report("L1-mesh"))
