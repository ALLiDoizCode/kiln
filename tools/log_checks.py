"""A fallen log as the pipeline sees it (source/log/brief.md): upright slices across its length.

A log lies along x. Its **trunk** is the largest closed piece of the mesh; the
others are its stubs. A **station** is the trunk cut by an upright plane across
x, which gives the closed outline of the trunk there and, inside it, the
outline of a hollow when there is one. Lying, being settled into the ground,
thickness, taper, bend, the hollow and its wall are all read from stations, so
nothing trusts a label from the build script. The stations leave out the ends
of the trunk (`[log] end_share` in conventions.toml), where a broken end is
not a closed outline; the wood shown at each end is measured there instead.

Used by tools/validate.py, and by the generator to refuse a draw. Runs under Blender's Python.
"""

import math

import bmesh
from mathutils import Vector


def pieces_of(faces):
    """The pieces a set of faces is made of: its faces grouped by the vertices they share, largest surface first."""
    faces = set(faces)
    pieces, seen = [], set()
    for start in sorted(faces, key=lambda face: face.index):
        if start in seen:
            continue
        seen.add(start)
        piece, front = [], [start]
        while front:
            face = front.pop()
            piece.append(face)
            for vert in face.verts:
                for other in vert.link_faces:
                    if other in faces and other not in seen:
                        seen.add(other)
                        front.append(other)
        pieces.append(piece)
    return sorted(pieces, key=lambda piece: -sum(f.calc_area() for f in piece))


def only(bm, faces):
    """A copy of the mesh holding only these faces."""
    bm.faces.index_update()
    keep = {f.index for f in faces}
    copy = bm.copy()
    copy.faces.ensure_lookup_table()
    bmesh.ops.delete(copy, geom=[f for f in copy.faces if f.index not in keep], context="FACES")
    return copy


def station(trunk, x):
    """The closed loops an upright plane across x cuts from the trunk, largest first: (area, middle, corners), in (y, z)."""
    cut = trunk.copy()
    result = bmesh.ops.bisect_plane(cut, geom=cut.verts[:] + cut.edges[:] + cut.faces[:], dist=1e-7, plane_co=(x, 0, 0), plane_no=(1, 0, 0))
    edges = [g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
    beside = {}
    for edge in edges:
        for vert in edge.verts:
            beside.setdefault(vert, []).append(edge)
    loops, used = [], set()
    for edge in edges:
        if edge in used:
            continue
        start, vert, corners = edge.verts[0], edge.verts[1], [edge.verts[0]]
        used.add(edge)
        while vert is not start:
            corners.append(vert)
            onward = [e for e in beside[vert] if e not in used]
            if not onward:
                break
            used.add(onward[0])
            vert = onward[0].other_vert(vert)
        if vert is not start or len(corners) < 3:
            continue  # an open chain: a tear, which the manifold check reports
        points = [Vector((v.co.y, v.co.z)) for v in corners]
        area = sum(a.x * b.y - b.x * a.y for a, b in zip(points, points[1:] + points[:1])) / 2
        if abs(area) < 1e-9:
            continue
        middle = sum(((a + b) * (a.x * b.y - b.x * a.y) for a, b in zip(points, points[1:] + points[:1])), Vector((0, 0))) / (6 * area)
        loops.append((abs(area), middle, points))
    cut.free()
    return sorted(loops, key=lambda loop: -loop[0])


def within(point, outline):
    """Whether a point of the plane lies inside a closed outline."""
    inside = False
    for a, b in zip(outline, outline[1:] + outline[:1]):
        if (a.y > point.y) != (b.y > point.y) and point.x < a.x + (b.x - a.x) * (point.y - a.y) / (b.y - a.y):
            inside = not inside
    return inside


def apart(points, outline):
    """The least distance from any of the points to the outline's edges."""
    least = float("inf")
    for p in points:
        for a, b in zip(outline, outline[1:] + outline[:1]):
            along = b - a
            share = max(0.0, min(1.0, (p - a).dot(along) / max(along.length_squared, 1e-12)))
            least = min(least, (p - a - along * share).length)
    return least


def turns(values, least):
    """How often a run of numbers turns from falling to rising or back, counting only rises and falls of more than `least`."""
    count, way, high, low = 0, 0, values[0], values[0]
    for value in values[1:]:
        high, low = max(high, value), min(low, value)
        if way >= 0 and value < high - least:
            count += way == 1
            way, high, low = -1, value, value
        elif way <= 0 and value > low + least:
            count += way == -1
            way, high, low = 1, value, value
    return count


def measure(bm, slots, spec, conv):
    """What the mesh shows of a log, as numbers; `slots` are its material names by index."""
    rules, want = conv["log"], spec["log"]
    floor = spec["bounds_m"]["min"][2]
    pieces = pieces_of(bm.faces)
    found = {"stubs": len(pieces) - 1}
    xs = [v.co.x for f in pieces[0] for v in f.verts]
    x0, x1 = min(xs), max(xs)
    length = x1 - x0
    trunk = only(bm, pieces[0])
    count, end = rules["stations"], rules["end_share"]
    step = length * (1 - 2 * end) / (count - 1)
    cuts = []
    for i in range(count):
        x = x0 + length * end + step * i
        loops = station(trunk, x)
        if not loops:
            cuts.append(None)
            continue
        area, middle, outline = loops[0]
        holes = [loop for loop in loops[1:] if within(loop[1], outline)]
        ys, zs = [p.x for p in outline], [p.y for p in outline]
        on_ground = [p.x for p in outline if p.y <= floor + rules["ground_m"]]
        cut = {"x": x, "area": area, "middle": Vector((x, middle.x, middle.y)), "width": max(ys) - min(ys), "low": min(zs), "top": max(zs), "flat": max(on_ground) - min(on_ground) if on_ground else 0.0, "hole": None}
        if holes:
            hole_area, _, hole = holes[0]
            cut["hole"] = {"area": hole_area, "clear": min(max(p.x for p in hole) - min(p.x for p in hole), max(p.y for p in hole) - min(p.y for p in hole)), "wall": min(apart(hole, outline), apart(outline, hole))}
        cuts.append(cut)
    whole = [cut for cut in cuts if cut]
    found.update(length=length, stations=len(whole))
    if len(whole) < count:
        trunk.free()
        return found  # a trunk that is not there at a station is no log; every check says so
    radius = [math.sqrt(cut["area"] / math.pi) for cut in cuts]
    found["thickness"] = radius[count // 2 - 1] + radius[count // 2]
    first, last = cuts[0]["middle"], cuts[-1]["middle"]
    chord = last - first
    found["tilt_deg"] = math.degrees(math.atan2(abs(chord.z), math.hypot(chord.x, chord.y)))
    found["long"] = length / found["thickness"]
    touching = [cut for cut in cuts if cut["low"] <= floor + rules["ground_m"]]
    found["grounded"] = len(touching) / count
    found["flat_share"] = sum(cut["flat"] / cut["width"] for cut in touching) / len(touching) if touching else 0.0
    quarter = count // 4
    found["taper"] = sum(radius[-quarter:]) / sum(radius[:quarter])
    found["bend"] = max((cut["middle"] - first).cross(chord).length / chord.length for cut in cuts) / length
    # The outline, station by station: how thick, how wide in plan, how high its top. A trunk thins toward its top,
    # with a swelling or a stretch lifted off the ground; one that steps in and out ring by ring turns at every ring.
    step_m = rules["step_share"] * found["thickness"]
    found["turns"] = max(turns(values, step_m) for values in ([2 * r for r in radius], [cut["width"] for cut in cuts], [cut["top"] for cut in cuts]))
    # Each end's rim, where bark meets wood: how far along the log it reaches, over the trunk's thickness at the nearest station.
    bark = slots.index(want["bark"]) if want["bark"] in slots else -1
    rim = [v.co.x for f in pieces[0] if f.material_index == bark for e in f.edges if any(o.material_index != bark for o in e.link_faces) for v in e.verts]
    for key, cut, mine in (("butt_ragged", cuts[0], lambda x: x < (x0 + x1) / 2), ("top_ragged", cuts[-1], lambda x: x >= (x0 + x1) / 2)):
        along = [x for x in rim if mine(x)]
        found[key] = (max(along) - min(along)) / (2 * math.sqrt(cut["area"] / math.pi)) if along else 0.0
    # The hollow: the longest run of stations in a row that are open at least as far across and up as the spec asks
    # (any opening at all, when the spec asks none), and the thinnest wall at any station with an opening.
    clear = spec["hollow"]["min_clear_m"] if "hollow" in spec else 0.0
    best, run = [], []
    for cut in cuts:
        run = run + [cut] if cut["hole"] and cut["hole"]["clear"] >= clear else []
        best = run if len(run) > len(best) else best
    holed = [cut["hole"] for cut in cuts if cut["hole"]]
    found.update(holed=len(holed), hollow_m=step * (len(best) - 1) if best else 0.0, clear=min((cut["hole"]["clear"] for cut in best), default=0.0),
                 widest_hole=max((hole["clear"] for hole in holed), default=0.0), wall=min((hole["wall"] for hole in holed), default=None))
    # The wood each end shows, looking along the log, over the trunk's cross-section at the nearest station.
    wood = slots.index(want["wood"]) if want["wood"] in slots else -1
    for key, cut, at_end in (("butt_wood", cuts[0], lambda x: x <= x0 + length * end), ("top_wood", cuts[-1], lambda x: x >= x1 - length * end)):
        shown = sum(f.calc_area() * abs(f.normal.x) for f in pieces[0] if f.material_index == wood and at_end(f.calc_center_median().x))
        found[key] = shown / (cut["area"] - (cut["hole"]["area"] if cut["hole"] else 0.0))
    trunk.free()
    return found


def check(checks, name, bm, slots, spec, conv):
    """The mesh is a trunk lying on the ground: long, near level, settled, tapering, bent, with wood at its ends, stubs, and the hollow its spec asks."""
    rules, want, hollow = conv["log"], spec["log"], spec.get("hollow")
    found = measure(bm, slots, spec, conv)
    shown = {key: round(value, 3) if isinstance(value, float) else value for key, value in found.items()}
    print(f"{name} log: {shown}")
    cut = found["stations"] == rules["stations"]
    missing = f"the trunk is cut by only {found['stations']} of the {rules['stations']} stations along its length: it is not one trunk from end to end"
    checks.check(
        f"{name}.log_lies",
        cut and found["tilt_deg"] <= rules["max_tilt_deg"] and found["long"] >= rules["min_long"] and found["grounded"] >= want["min_grounded_share"],
        f"the trunk's middle line is {shown.get('tilt_deg')} degrees off level, it is {shown.get('long')} times as long as thick, and {shown.get('grounded')} of its stations touch the ground; "
        f"a log lying on the ground is within {rules['max_tilt_deg']} degrees, at least {rules['min_long']} times, and spec wants {want['min_grounded_share']} touching" if cut else missing,
    )
    checks.check(
        f"{name}.log_settled",
        cut and found["flat_share"] >= want["min_flat_share"],
        f"where the trunk touches the ground it lies flat on it over {shown.get('flat_share')} of its width; spec wants at least {want['min_flat_share']}: sunk a little, not resting on a line" if cut else missing,
    )
    low, high = want["thickness_m"]
    checks.check(
        f"{name}.log_thick",
        cut and low <= found["thickness"] <= high,
        f"at the middle of its length the trunk is {shown.get('thickness')} m thick (a circle of its cross-section's area); spec wants {low} to {high} m" if cut else missing,
    )
    checks.check(
        f"{name}.log_tapers",
        cut and found["taper"] <= want["max_taper"],
        f"the quarter of the trunk nearest its top (+x) is {shown.get('taper')} as thick as the quarter nearest its butt; spec wants at most {want['max_taper']}" if cut else missing,
    )
    checks.check(
        f"{name}.log_bends",
        cut and found["bend"] >= want["min_bend"],
        f"the trunk's middle stands at most {shown.get('bend')} of its length off the straight line between its ends; spec wants at least {want['min_bend']}: a trunk, not a cylinder" if cut else missing,
    )
    checks.check(
        f"{name}.log_ends",
        cut and min(found["butt_wood"], found["top_wood"]) >= want["min_end_wood"],
        f"seen along the log, {want['wood']} covers {shown.get('butt_wood')} of the cross-section at the butt and {shown.get('top_wood')} at the top; spec wants at least {want['min_end_wood']} at each: broken or sawn through, not capped in bark" if cut else missing,
    )
    checks.check(
        f"{name}.log_even",
        cut and found["turns"] <= rules["max_turns"],
        f"along its stations the trunk's outline (its thickness, its width in plan, the height of its top) turns from thinning to thickening or back {found.get('turns')} times, counting steps of more than {rules['step_share']} of its thickness; "
        f"conventions allow {rules['max_turns']}: a trunk that thins toward its top with a swelling or a lifted stretch, not one that steps in and out ring by ring" if cut else missing,
    )
    # A break lies within the end of the log the stations leave out, so on a thick log it cannot reach as far for its
    # thickness as on a thin one: it is asked the share of the thickness, or three tenths of that end, whichever is less.
    least = min(rules["min_ragged"], 0.3 * rules["end_share"] * found["length"] / found["thickness"]) if cut else rules["min_ragged"]
    broken = found.get("top_ragged", 0.0) >= least and (want["butt"] != "broken" or found.get("butt_ragged", 0.0) >= least)
    checks.check(
        f"{name}.log_ragged",
        cut and broken and (want["butt"] != "sawn" or found["butt_ragged"] <= rules["max_sawn"]),
        f"where bark meets wood, the rim of the top reaches {shown.get('top_ragged')} of the trunk's thickness along the log and the rim of the butt ({want['butt']}) {shown.get('butt_ragged')}; "
        f"a broken end reaches at least {round(least, 3)} (splinters of unequal length, not a ring cut square) and a sawn one at most {rules['max_sawn']}" if cut else missing,
    )
    fewest, most = want["stubs"]
    checks.check(f"{name}.log_stubs", fewest <= found["stubs"] <= most, f"{found['stubs']} closed pieces stand apart from the trunk; spec wants {fewest} to {most} stubs")
    if hollow:
        checks.check(
            f"{name}.log_hollow",
            cut and found["hollow_m"] >= hollow["min_depth_m"],
            f"the trunk is open at least {hollow['min_clear_m']} m across and up for {shown.get('hollow_m')} m of its length in one run (its widest opening anywhere is {shown.get('widest_hole')} m, at {found.get('holed')} stations); spec wants {hollow['min_depth_m']} m" if cut else missing,
        )
        checks.check(
            f"{name}.log_wall",
            cut and found["wall"] is not None and found["wall"] >= hollow["min_wall_m"],
            f"the wall between the hollow and the outside is {shown.get('wall')} m at its thinnest (None: no hollow); spec wants at least {hollow['min_wall_m']} m" if cut else missing,
        )
    else:
        checks.check(f"{name}.log_hollow", cut and found["holed"] == 0, f"{found.get('holed')} stations show an opening inside the trunk, up to {shown.get('widest_hole')} m; the spec has no `hollow`: a solid log" if cut else missing)
    return found
