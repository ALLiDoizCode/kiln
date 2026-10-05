"""Fallen log generator: one spec, one log (source/log/brief.md, ADR 13).

Shared by the build scripts of every log asset (source/log_1, ...), which each
call `build_log(spec)`. A spec gives a seed, bounds and a `log` block (how
thick, which butt, how many stubs), and a `hollow` block when the log is
hollow. Everything else is drawn from `random.Random(seed)`, in a fixed order,
and built as plain lists of vertices and faces with the kit in tools/wood.py
(the tree's rings, strips, seams and grain), so the same spec gives the same mesh.

1. Trunk: rings of seven to nine flat sides with a narrow strip along every
   corner, along a line that bends in plan, lifts off the ground along one
   stretch on some seeds, and twists. It tapers from the butt (-x) to the top
   (+x); its section is irregular, each corner a little nearer or further.
2. Ground: every ring that reaches the ground is sunk into it a little and
   pressed flat there: its lowest corners are brought down onto the ground.
3. Ends. The top is broken: its last ring is ragged, each corner broken off
   nearer or further, with a tongue of two or three corners standing well out,
   round torn wood that falls in toward the middle. The butt is broken too,
   or sawn (a flat cut a little off square, with a narrow rim), or torn out:
   the foot flaring into root stubs round a bulging root plate.
4. Hollow: a second tube inside the first, facing inward, its floor flat, off
   the trunk's middle; the two are joined at each end by a ragged ring of wood.
5. Stubs: one to three closed tubes of unequal length, leaning toward the
   top, each with its foot in the trunk's wall and a broken end.
6. Fit: the bend is chosen so that the log fills the spec's bounds across,
   and the whole is then stretched a little to the bounds exactly.
7. Keep or redraw: the log is measured as the gate measures it
   (tools/log_checks.py), against the spec with room to spare (MARGINS). A
   log that misses is thrown away and the seed draws the next one.

Each material gets one flat colour; tools/paint.py paints them, with the
grain along each limb by the `grain` attribute written here (ADR 10, ADR 12).
"""

import contextlib
import copy
import io
import math
import random

import bmesh
import log_checks
import wood as kit
from mathutils import Quaternion, Vector
from pipeline import Checks, conventions
from wood import END, INNER, RIM, SIDE, UNDER, Wood, frames, ring, round_of, skin

Z = Vector((0, 0, 1))
BARK, WOOD = 0, 1  # the object's materials, in order
MAX_STRETCH = (0.85, 1.18)  # the fit may not change any dimension by more
LOGS = 60  # how many whole logs one seed may draw before it is given up
BEND = (0.04, 0.09)  # how far the trunk's line may stand off the straight, as a share of its length
STRIP = 0.16  # the strip along a corner, as a share of a side
PRESS = 0.34  # corners this share of the radius above the trunk's lowest point, sink included, are pressed onto the ground
# Room to spare: a log is kept only when it meets these in place of the spec's own limits (spec key -> stricter value).
MARGINS = {
    "max_triangles": lambda most: round(most * 0.95),
    "log.max_taper": lambda most: round(most - 0.03, 3),
    "log.min_bend": lambda least: round(least + 0.008, 3),
    "log.min_grounded_share": lambda least: round(least + 0.05, 3),
    "log.min_flat_share": lambda least: round(least + 0.05, 3),
    "log.min_end_wood": lambda least: round(least + 0.1, 3),
    "log.thickness_m": lambda span: [round(span[0] + 0.08 * (span[1] - span[0]), 3), round(span[1] - 0.08 * (span[1] - span[0]), 3)],
    "hollow.min_clear_m": lambda least: round(least + 0.03, 3),
    "hollow.min_wall_m": lambda least: round(least * 1.15, 3),
}


def draw_numbers(spec, rng):
    """Everything about one log that is drawn, before any of it is built."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    want, hollow = spec["log"], spec.get("hollow")
    n = {}
    low, high = want["thickness_m"]
    n["sides"] = sides = rng.choice((7, 8, 8, 9))
    n["taper"] = rng.uniform(0.24, 0.3) if hollow else rng.uniform(0.28, 0.45)
    # A hollow log is drawn thick: the hollow has to stay open where the trunk is thinnest.
    n["thick"] = rng.uniform(low + (0.6 if hollow else 0.25) * (high - low), high - 0.15 * (high - low))
    n["spin"], n["twist"] = rng.uniform(0, 2 * math.pi), rng.uniform(0.25, 0.9) * rng.choice((-1, 1))
    n["corner"] = [rng.uniform(0.9, 1.1) for _ in range(sides)]
    n["sink"] = rng.uniform(0.04, 0.07) if hollow else rng.uniform(0.1, 0.24)
    # The line in plan: one bow, a second wave on it, and a kink.
    n["bow"] = (rng.uniform(0.6, 1.0) * rng.choice((-1, 1)), rng.uniform(-0.6, 0.6), rng.uniform(0, math.pi), rng.uniform(0.3, 0.7), rng.uniform(-1.2, 1.2))
    # One stretch lifted off the ground, on about half the seeds: (where, how long, how high over the radius).
    n["lift"] = (rng.uniform(0.2, 0.8), rng.uniform(0.07, 0.12), rng.uniform(0.15, 0.45) if rng.random() < 0.5 else 0.0)
    count = rng.randint(9, 11)
    inner = sorted((k + rng.uniform(-0.3, 0.3)) / count for k in range(1, count))
    n["at"] = [0.0] + ([0.035, 0.085] if want["butt"] == "root" else []) + [s for s in inner if 0.12 < s < 0.93] + [1.0]
    n["swell"] = [rng.uniform(0.95, 1.05) for _ in n["at"]]

    def ragged():
        """A broken end: how far each corner is broken off beyond the last ring, over the radius, and the torn wood inside."""
        out = [rng.uniform(-0.12, 0.3) for _ in range(sides)]
        # A hollow log's wall is thin: a tongue of it as long as a solid log's would be a blade, lit from both sides at once.
        start, wide, far = rng.randrange(sides), rng.choice((2, 3)), rng.uniform(0.25, 0.5) if hollow else rng.uniform(0.55, 1.1)
        for k in range(wide):
            out[(start + k) % sides] += far * (1.0 if wide == 2 or k == 1 else 0.6)
        if rng.random() < 0.5:
            out[(start + sides // 2 + rng.choice((-1, 0, 1))) % sides] += rng.uniform(0.25, 0.5)
        return {"out": out, "in": [rng.uniform(0.05, 0.3) for _ in range(sides)], "middle": rng.uniform(-0.35, 0.05), "reach": [rng.uniform(0.42, 0.62) for _ in range(sides)],
                "off": (rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15))}

    n["top"] = ragged()
    n["butt"] = ragged() if want["butt"] == "broken" else None
    n["saw"] = (rng.uniform(0, 2 * math.pi), math.radians(rng.uniform(4, 13)))
    roots = rng.sample(range(sides), rng.choice((3, 4)))
    n["roots"] = {"reach": [rng.uniform(1.5, 2.1) if j in roots else rng.uniform(1.05, 1.25) for j in range(sides)], "out": [rng.uniform(-0.1, 0.12) for _ in range(sides)],
                  "plate": [rng.uniform(0.1, 0.3) for _ in range(sides)], "middle": rng.uniform(0.25, 0.5)}
    n["wall"] = (rng.uniform(0.15, 0.18), [rng.uniform(0.9, 1.15) for _ in n["at"]], rng.uniform(0, 2 * math.pi), rng.uniform(0.0, 0.2))
    stubs = []
    lengths = [rng.uniform(0.9, 1.6), rng.uniform(0.25, 0.55), rng.uniform(0.55, 0.9)]
    side = rng.choice((-1, 1))
    for k in range(rng.randint(*want["stubs"])):
        stubs.append({
            "at": rng.uniform(0.2, 0.42) + 0.22 * k + rng.uniform(-0.04, 0.04),
            "round": side * (-1) ** k * math.radians(rng.uniform(10, 95)),
            "long": lengths[k] * (0.6 if hollow else 1.0),
            "thick": rng.uniform(0.09, 0.12) if hollow else rng.uniform(0.15, 0.24),
            "lean": math.radians(rng.uniform(5, 14) if hollow else rng.uniform(20, 48)),
            "sides": rng.choice((5, 6)),
            "spin": rng.uniform(0, 2 * math.pi),
            "jag": [rng.uniform(-0.3, 0.35) for _ in range(6)],
            "tip": rng.uniform(-0.25, 0.3),
        })
    n["stubs"] = stubs
    return n


def bowed(n, share):
    """How far the trunk's line stands off the straight between its ends at a share of its length: 0 at both ends, 1 at most."""
    a1, a2, phase, kink_at, kink = n["bow"]

    def raw(s):
        return a1 * math.sin(math.pi * s) + 0.4 * a2 * math.sin(2 * math.pi * s + phase) + 0.5 * kink * max(0.0, s - kink_at)

    def off(s):
        return raw(s) - raw(0.0) - (raw(1.0) - raw(0.0)) * s

    most = max(abs(off(k / 60)) for k in range(61))
    return off(share) / most


def ray_hit(wood, faces, origin, direction):
    """The nearest point at which a ray from `origin` meets any of the faces (by index); None when it meets none."""
    best = None
    for index in faces:
        face = wood.faces[index]
        for b, c in zip(face[1:], face[2:]):
            p0, p1, p2 = wood.verts[face[0]], wood.verts[b], wood.verts[c]
            e1, e2 = p1 - p0, p2 - p0
            h = direction.cross(e2)
            det = e1.dot(h)
            if abs(det) < 1e-12:
                continue
            s = origin - p0
            u = s.dot(h) / det
            q = s.cross(e1)
            v = direction.dot(q) / det
            t = e2.dot(q) / det
            if u >= 0 and v >= 0 and u + v <= 1 and t > 1e-6 and (best is None or t < best):
                best = t
    return None if best is None else origin + direction * best


def cap(wood, rim, per, inner, centre, material, outward, grain, kind=END):
    """Close an end: from a rim ring (`per` vertices to a corner) in to a ring of one vertex to a corner, and from there to a centre vertex (None: left open, a hollow).

    `outward` is the way the end faces; `grain(vertex, corner)` gives a vertex's (across, along, limb) as a corner of the face at that corner."""
    sides = len(inner)
    made = []
    for j in range(sides):
        k = (j + 1) % sides
        if per == 2:
            made.append(((rim[2 * j], rim[2 * j + 1], inner[j]), j))
        made.append(((rim[per * j + per - 1], rim[per * k], inner[k], inner[j]), j))
        if centre is not None:
            made.append(((inner[j], inner[k], centre), j))
    for corners, j in made:
        a, b, c = (wood.verts[i] for i in corners[:3])
        if (b - a).cross(c - a).dot(outward) < 0:
            corners = tuple(reversed(corners))
        wood.face(corners, kind, material, [grain(i, j) for i in corners])


def one(spec, n, bend):
    """The log the numbers describe, bent by `bend` of its length, as lists; not yet fitted to the bounds."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    want, hollow = spec["log"], spec.get("hollow")
    sides, at = n["sides"], n["at"]
    if hollow and want["butt"] != "broken":
        raise ValueError("a hollow log is open right through: its butt is broken")
    wood = Wood()
    butt_radius = n["thick"] / 2 / (1 - n["taper"] * 0.5**0.8)
    # The line is shorter than the bounds by what stands out past its ends: a tongue of splinters, a root plate.
    beyond_top = max(0.0, *n["top"]["out"]) * butt_radius * (1 - n["taper"])
    beyond_butt = {"broken": lambda: max(0.0, *n["butt"]["out"]), "root": lambda: n["roots"]["middle"], "sawn": lambda: math.tan(n["saw"][1])}[want["butt"]]() * butt_radius
    length = (hi.x - lo.x) - beyond_top - beyond_butt

    def radius(k):
        return butt_radius * (1 - n["taper"] * at[k] ** 0.8) * n["swell"][k]

    def lifted(k):
        where, wide, high = n["lift"]
        return high * radius(k) * math.exp(-(((at[k] - where) / wide) ** 2))

    def spin(k):
        return n["spin"] + n["twist"] * at[k]

    def offsets(frame, k, reach=None):
        """A ring's corners from its middle, without strips."""
        tangent, across, along = frame
        return [(across * math.cos(spin(k) + 2 * math.pi * j / sides) + along * math.sin(spin(k) + 2 * math.pi * j / sides)) * radius(k) * n["corner"][j] * (reach[j] if reach else 1.0) for j in range(sides)]

    # The line: level at first, then each point raised so that its ring's lowest corner is sunk by its share.
    points = [Vector((-length / 2 + length * s, bend * (hi.x - lo.x) * bowed(n, s), radius(k) * (1 - n["sink"]) + lifted(k))) for k, s in enumerate(at)]
    for _ in range(2):
        frame = frames(points, Z)
        for k, point in enumerate(points):
            point.z = -min(offset.z for offset in offsets(frame[k], k)) - n["sink"] * radius(k) + lifted(k)
    frame = frames(points, Z)
    far = [0.0]
    for a, b in zip(points, points[1:]):
        far.append(far[-1] + (b - a).length)
    last = len(at) - 1

    def flare(k):
        if want["butt"] != "root" or k > 2:
            return None
        return [1.0 + (reach - 1.0) * (1.0, 0.5, 0.15)[k] for reach in n["roots"]["reach"]]

    def shifts(k):
        """How far along the limb each corner of an end ring is moved."""
        if k == last:
            return [out * radius(k) for out in n["top"]["out"]]
        if k == 0 and want["butt"] == "broken":
            return [-out * radius(k) for out in n["butt"]["out"]]
        if k == 0 and want["butt"] == "root":
            return [-out * radius(k) for out in n["roots"]["out"]]
        if k == 0:
            normal = saw_normal()
            return [-offset.dot(normal) / frame[0][0].dot(normal) for offset in offsets(frame[0], 0)]
        return None

    def saw_normal():
        """The way a sawn butt faces: back along the trunk, tipped a little."""
        turn, tip = n["saw"]
        tangent, across, along = frame[0]
        return (Quaternion(across * math.cos(turn) + along * math.sin(turn), tip) @ -tangent).normalized()

    def press(loop, k):
        """Sink a ring into the ground: the corners low enough are brought down onto it."""
        low = min(wood.verts[i].z for i in loop)
        if low >= 0.0:
            return
        # A corner goes down whole, both vertices of its strip, or the strip would be wrung between them.
        for a, b in zip(loop[::2], loop[1::2]):
            if (wood.verts[a].z + wood.verts[b].z) / 2 < (PRESS - n["sink"]) * radius(k):
                wood.verts[a].z = wood.verts[b].z = 0.0

    rings = []
    for k in range(len(at)):
        loop = ring(wood, points[k], frame[k], radius(k), sides, strip=STRIP, spin=spin(k), reach=[c * f for c, f in zip(n["corner"], flare(k) or [1.0] * sides)], shift=shifts(k))
        press(loop, k)
        rings.append(loop)
    trunk_limb = wood.limb()
    lowest = min(range(len(rings[0])), key=lambda i: wood.verts[rings[0][i]].z)
    outer_from = len(wood.faces)
    skin(wood, rings, far, BARK, trunk_limb, strips=True, seam=lowest)
    outer = range(outer_from, len(wood.faces))

    # The hollow: a tube inside, off the middle, its wall thinner and thicker along the log, its floor flat.
    inner_rings, inner = [], range(0)
    if hollow:
        share, wobble, toward, off = n["wall"]
        floor = hollow["min_wall_m"] * 1.6
        for k in range(len(at)):
            wall = share * wobble[k] * radius(k)
            tangent, across, along = frame[k]
            middle = points[k] + (across * math.cos(toward) + along * math.sin(toward)) * off * wall
            shift = None
            if k in (0, last):
                end = n["top"] if k == last else n["butt"]
                sign = 1 if k == last else -1
                shift = [sign * (out * 0.8 - back * 0.5) * radius(k) for out, back in zip(end["out"], end["in"])]
            loop = ring(wood, middle, frame[k], radius(k) - wall, sides, spin=spin(k), reach=n["corner"], shift=shift)
            for i in loop:
                wood.verts[i].z = max(wood.verts[i].z, floor)
            inner_rings.append(loop)
        inner_from = len(wood.faces)
        skin(wood, inner_rings, far, WOOD, wood.limb(), inward=True, seam=sides // 2)
        inner = range(inner_from, len(wood.faces))

    # The ends.
    for k, sign in ((0, -1), (last, 1)):
        rim, around, limb = rings[k], round_of(wood, rings[k]), wood.limb()
        tangent, across, along = frame[k]
        outward = tangent * sign
        kind = "broken" if k == last else want["butt"]
        size = radius(k)
        if hollow:
            # A ragged ring of wood between the bark and the wall of the hollow; torn fibre runs from one to the other.
            cap(wood, rim, 2, inner_rings[k], None, WOOD, outward, lambda i, j, rim=rim, around=around, size=size: (around[2 * j] if i not in rim else around[rim.index(i)], size if i in rim else 0.8 * size, limb))
            continue
        if kind == "sawn":
            # A flat cut: a narrow rim just inside the bark, then the cut, its grain running round as rings.
            normal = saw_normal()

            def on_cut(co):
                return co - tangent * ((co - points[0]).dot(normal) / tangent.dot(normal))

            edge = [wood.vert(on_cut(points[0] + (wood.verts[i] - points[0]) * 0.9)) for i in rim]
            for i in range(len(rim)):
                j = (i + 1) % len(rim)
                corners = [(rim[j], (size, around[i + 1], limb)), (rim[i], (size, around[i], limb)), (edge[i], (0.9 * size, around[i], limb)), (edge[j], (0.9 * size, around[i + 1], limb))]
                a, b, c = (wood.verts[v] for v, _ in corners[:3])
                if ((b - a).cross(c - a) + (c - a).cross(wood.verts[edge[j]] - a)).dot(normal) < 0:
                    corners.reverse()
                wood.face([v for v, _ in corners], RIM, WOOD, [g for _, g in corners])
            ring_in = [wood.vert(on_cut(points[0] + offset * 0.5)) for offset in offsets(frame[0], 0)]
            centre = wood.vert(on_cut(points[0]))
            where = {**{v: (0.9 * size, around[i]) for i, v in enumerate(edge)}, **{v: (0.5 * size, around[2 * j]) for j, v in enumerate(ring_in)}}
            cap(wood, edge, 2, ring_in, centre, WOOD, normal, lambda i, j: (*where.get(i, (0.0, around[2 * j])), limb))
            continue
        # Torn wood: a ring part of the way in, further back than the rim, and a middle further back still;
        # a root plate bulges out instead. The grain runs outward from the middle, as torn fibre.
        if kind == "root":
            back, middle_back, reach = n["roots"]["plate"], n["roots"]["middle"], [0.55 * f for f in flare(0)]
            off = (0.0, 0.0)
        else:
            end = n["top"] if k == last else n["butt"]
            back, middle_back, reach, off = [0.35 * out - inside for out, inside in zip(end["out"], end["in"])], end["middle"], end["reach"], end["off"]
        ring_in = [wood.vert(points[k] + offset * reach[j] + outward * back[j] * size) for j, offset in enumerate(offsets(frame[k], k))]
        for i in ring_in:
            wood.verts[i].z = max(wood.verts[i].z, 0.08 * size)  # torn wood stays clear of the ground the rim is pressed onto
        centre = wood.vert(points[k] + (across * off[0] + along * off[1]) * size + outward * middle_back * size)
        where = {**{v: (around[i], size) for i, v in enumerate(rim)}, **{v: (around[2 * j], 0.5 * size) for j, v in enumerate(ring_in)}}
        cap(wood, rim, 2, ring_in, centre, WOOD, outward, lambda i, j: (*where.get(i, (around[2 * j], 0.0)), limb))

    # Stubs: each a closed tube from inside the trunk's wall, out and toward the top.
    for stub in n["stubs"]:
        k = max(i for i in range(len(at)) if at[i] <= stub["at"])
        t = (stub["at"] - at[k]) / (at[k + 1] - at[k])
        origin = points[k].lerp(points[k + 1], t)
        tangent = (points[k + 1] - points[k]).normalized()
        size = radius(k) + (radius(k + 1) - radius(k)) * t
        out = (Quaternion(tangent, stub["round"]) @ (Z - tangent * tangent.z)).normalized()
        surface = ray_hit(wood, outer, origin, out)
        if surface is None:
            raise RuntimeError("a stub's place on the trunk was not found")
        depth = (surface - origin).length
        wall = ray_hit(wood, inner, origin, out)
        foot = origin + out * ((depth + (wall - origin).length) / 2 if wall is not None else depth - 0.45 * size)
        axis = (out * math.cos(stub["lean"]) + tangent * math.sin(stub["lean"])).normalized()
        thick, long = stub["thick"] * size, stub["long"] * size
        if axis.z > 0:
            # No stub stands above the bounds: one that would is broken off shorter.
            long = max(1.6 * thick, min(long, (hi.z - thick - surface.z) / axis.z))
        places = [foot, surface + axis * thick * 0.9, surface + axis * long]
        if places[-1].z - thick < 0.04:
            raise RuntimeError("a stub reaches into the ground")
        widths = [thick, thick * 1.05, thick * 0.78]
        beside = (tangent - axis * axis.dot(tangent)).normalized()
        loops = [ring(wood, place, (axis, beside, axis.cross(beside)), width, stub["sides"], spin=stub["spin"], shift=[j * thick for j in stub["jag"][: stub["sides"]]] if i == 2 else None)
                 for i, (place, width) in enumerate(zip(places, widths))]
        limb = wood.limb()
        along_stub = [0.0, (places[1] - places[0]).length, (places[2] - places[0]).length]
        skin(wood, loops, along_stub, BARK, limb)
        for loop, place, outward, material, far_at in ((loops[0], foot, -axis, BARK, 0.0), (loops[2], places[2] + axis * stub["tip"] * thick, axis, WOOD, along_stub[2])):
            centre = wood.vert(place)
            around = round_of(wood, loop)
            for i in range(len(loop)):
                j = (i + 1) % len(loop)
                corners = (loop[i], loop[j], centre)
                a, b, c = (wood.verts[v] for v in corners)
                if (b - a).cross(c - a).dot(outward) < 0:
                    corners = (loop[j], loop[i], centre)
                wood.face(corners, END, material, [(around[i if v == loop[i] else i + 1], far_at, limb) if v != centre else (around[i], far_at + thick, limb) for v in corners])

    # What lies flat on the ground faces down and is never seen; it is cut out of the painted islands round it.
    for index, face in enumerate(wood.faces):
        if all(wood.verts[i].z == 0.0 for i in face):
            wood.kinds[index] = UNDER
            wood.seams += [(a, b) for a, b in zip(face, face[1:] + face[:1])]
    return wood


def extent(wood, axis):
    values = [v[axis] for v in wood.verts]
    return min(values), max(values)


def fit(wood, lo, hi):
    """Stretch every point so the bounds are exactly lo..hi: along and across between both sides, and up from the ground."""
    scales = []
    for axis in range(2):
        low, high = extent(wood, axis)
        scale = (hi[axis] - lo[axis]) / (high - low)
        scales.append(scale)
        for v in wood.verts:
            v[axis] = lo[axis] + (v[axis] - low) * scale
    low, high = extent(wood, 2)
    scales.append(hi.z / high)
    worst = [round(s, 2) for s in scales if not MAX_STRETCH[0] <= s <= MAX_STRETCH[1]]
    if worst or abs(low) > 1e-9:
        raise RuntimeError(f"reaching the bounds would stretch the log by {[round(s, 2) for s in scales]}, outside {MAX_STRETCH}")
    for v in wood.verts:
        v.z *= scales[2]


def unmet(wood, spec):
    """What the brief asks of the shape and this log does not give with room to spare, as the gate's own failure lines."""
    strict = copy.deepcopy(spec)
    for key, value in MARGINS.items():
        *path, last = key.split(".")
        block = strict
        for part in path:
            block = block.get(part) if isinstance(block, dict) else None
        if block is not None:
            block[last] = value(block[last])
    bm = bmesh.new()
    verts = [bm.verts.new(v) for v in wood.verts]
    for face, material in zip(wood.faces, wood.materials):
        bm.faces.new([verts[i] for i in face]).material_index = material
    bm.verts.index_update()
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    checks = Checks("build", spec["objects"][0])
    with contextlib.redirect_stdout(io.StringIO()):
        log_checks.check(checks, spec["objects"][0], bm, [strict["log"]["bark"], strict["log"]["wood"]], strict, conventions())
    checks.check("budget.triangles", wood.triangles() <= strict["max_triangles"], f"{wood.triangles()} > {strict['max_triangles']}")
    bm.free()
    return [f"{r['id']}: {r['detail']}" for r in checks.failed()]


def draw(spec, tweak=None, strict=True):
    """The log for the spec's seed, as lists, fitted to the spec's bounds.

    A seed draws whole logs, one after another from the same generator, until one fills the bounds
    without being stretched out of shape, can be lit, and meets the brief's shape checks with room
    to spare (`unmet`). `tweak(numbers)` changes what was drawn before it is built, and `strict=False`
    keeps the first log that fills the bounds whatever it measures (the tests' broken logs)."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    rng = random.Random(spec["seed"])
    refused = []
    for take in range(1, LOGS + 1):
        n = draw_numbers(spec, rng)
        if tweak:
            tweak(n)
        try:
            # The bend that fills the bounds across: more bend, more width.
            low, high = n.get("bend", BEND)
            wide = hi.y - lo.y

            def across(bend):
                a, b = extent(one(spec, n, bend), 1)
                return b - a

            if across(low) < wide < across(high):
                for _ in range(14):
                    middle = (low + high) / 2
                    low, high = (middle, high) if across(middle) < wide else (low, middle)
            bend = low if across(low) >= wide else high
            wood = one(spec, n, bend)
            fit(wood, lo, hi)
            kit.corner_normals(wood, 0.0, 0.0)
        except RuntimeError as error:
            refused.append(f"log {take}: {error}")
            continue
        problems = unmet(wood, spec) if strict else []
        if problems:
            refused.append(f"log {take}: " + "; ".join(problems))
            continue
        print(f"log seed {spec['seed']}: log {take} of up to {LOGS} fills the bounds{' and meets the brief with room to spare' if strict else ''}; {n['sides']} sides, {len(n['at'])} rings, "
              f"bent {bend:.3f} of its length, {len(n['stubs'])} stubs, {wood.triangles()} triangles")
        return wood
    raise RuntimeError(f"log seed {spec['seed']}: none of its {LOGS} logs fills the bounds and meets the brief with room to spare:\n  " + "\n  ".join(refused))


def build_log(spec, tweak=None, strict=True):
    """Build the spec's one object from its seed. Its materials are the `log` block's bark and wood, in that order."""
    wood = draw(spec, tweak, strict)
    want = spec["log"]
    return kit.to_object(wood, spec["objects"][0], [(want["bark"], spec["materials"][want["bark"]]), (want["wood"], spec["materials"][want["wood"]])])
