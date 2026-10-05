"""Arch: two piers of stacked blocks bridged by a lintel block or by a knot of wedged blocks, with rubble at the feet.

docs/style/rock-shapes.md, Arch. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py): four leaning sides and up to two cut corners, a level floor, and a tipped cap
ringed by chamfers. The pieces pass into each other; each is softened on its own and they stay
separate closed pieces in the one mesh (ADR 13).

The arch faces the front (-Y): its piers stand to the left and right and the opening runs
through from front to back. A lintel arch is two piers of two stacked blocks and one block lying
across both. A wedged-block arch is two piers of a tall block with a leaning block stacked on
it, and a keystone wedged between the two leaning blocks.

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: the piers are not twins (one is about three quarters
   as wide as the other, and their blocks meet at different heights), and the rubble blocks are
   a fraction of the size of a pier block, each smaller than the last.
2. Nothing upright: every side leans in, all the pieces lean a little more one common way, and
   the leaning blocks of a knot hang far over the opening.
3. Off-centre: the opening is off the middle of the bounds, toward the narrower pier, and the
   span's top tips so that one end is the highest.
4. A foot: rubble against the outer feet of the piers, never in the passage.
5. Flat caps ringed by chamfers, and corners cut by planes.

A spec gives the seed, the bounds, the kind of span and the opening wanted. A seed draws whole
arches, one after another, until one meets the spec, and fails the build with the reasons when
none does.
"""

import math
import random

import bmesh
import stone
import validate
from mathutils import Vector
from pipeline import conventions

ARCHES = 40  # how many whole arches one seed may draw before it is given up
SOFT = (0.012, 0.04)  # the least and most a soft edge eats into each plane beside it, metres
SOFT_SHARE = 0.012  # and the most as a share of the arch's height
WIDER = (1.08, 1.18)  # the opening at the ground, over the width the spec asks
TALLER = (1.04, 1.1)  # the underside of the span, over the height the spec asks
NARROWER = (0.7, 0.78)  # the second pier's width over the first's
SHALLOWER = (0.7, 0.8)  # and its depth
DEEP = (0.94, 1.0)  # the first pier's depth, over the bounds'
SKEW = 4.0  # how far a side's direction strays from square, degrees
TAPER = (0.05, 0.12)  # how much narrower a block is at its cap than at its floor, each side, as a share of its lesser width
TAPER_MOST = 6.0  # and the most that may be, degrees: a low block is not a pyramid
LEAN = (1.0, 2.0)  # how far every piece leans one common way on top of that, degrees
SLANT = (3.0, 7.0)  # how far a block's cap slants from level, degrees
SHOULDER = (0.025, 0.035)  # how far below a block's cap its chamfers start, as a share of the arch's height
INSET = (0.6, 1.0)  # how far in from the side a chamfer meets the cap, over how far below it starts
STEEP = (0.25, 0.4)  # the same for the chamfer over a side that hangs far over: nearer upright, or the corner of the soft edges between the two is lit from behind
CUT = (0.72, 0.85)  # a cut corner: how far out its plane stands, as a share of the way to the corner
CUT_LEAN = (0.0, 3.0)  # and how far it leans in, degrees, beyond the two sides it lies between
JOINT = ((0.6, 0.66), (0.57, 0.63))  # where a lintel arch's pier blocks meet, as a share of the opening's height: the first pier, the second
SETBACK = (0.03, 0.08)  # how far a block stands in from the shoulder of the one under it, as a share of that one's width
SINK = 0.05  # how far a piece's floor is below the lowest of the shoulder it stands on, metres: no daylight under its soft rim
# The lintel: its depth over the bounds'; how far in from a pier's outer face its end is, as a share of that pier's width; how far its
# ends lean in and its long sides lean either way, degrees; its top's tilt; its chamfers; how many corners are cut.
LINTEL = dict(depth=(0.86, 0.96), end=(0.02, 0.1), ends=(4.0, 10.0), sides=(2.0, 6.0), tilt=(2.0, 5.0), shoulder=(0.08, 0.12), inset=(0.6, 1.0), cuts=(1, 2))
# A knot: how far a leaning block hangs over the opening, degrees; how far its back leans the same way, over that; how far above
# the piers the keystone's floor is, as a share of what the bounds leave above the opening; how far above that floor a leaning
# block's cap is, the same; how far below its cap its chamfers start, as a share of the arch's height; how far that cap slants, to the front or the back, and its chamfers' insets (wide, so that each is steeper than the leaning back under it); how far the keystone bites into each leaning block, as a share
# of the gap between them; how far its sides are undercut, degrees; its top's tilt; its chamfers; the least gap it may bridge, metres.
KNOT = dict(over=(22.0, 30.0), back=(0.3, 0.5), rise=(0.5, 0.6), above=(0.12, 0.2), shoulder_of=(0.035, 0.045), slant=(3.0, 7.0), chamfer=(0.9, 1.4), bite=(0.2, 0.32), undercut=(10.0, 20.0), tilt=(2.0, 5.0), shoulder=(0.18, 0.28), inset=(0.8, 1.4), gap=0.2)
# Rubble: the first block's half width over the first pier's width; how far its far side is from the pier's outer face, over that
# half width; each next block's size over the last; its depth over its width; its height over its half width; and its shape.
RUBBLE = dict(radius=(0.34, 0.42), out=(1.0, 1.3), shrink=(0.78, 0.84), flat=(0.8, 1.0), tall=(0.8, 1.1), taper=(5.0, 10.0), slant=(3.0, 8.0), shoulder=(0.3, 0.4), inset=(1.1, 1.6))


def block(rng, rect, floor, top, lifts, slant, drop, insets, cuts=0, way=None, steep=()):
    """One piece (stone.prism) on the rectangle `rect` (x0, x1, y0, y1) at `floor`, its cap `top` up over the rectangle's middle.

    `lifts` is how far the +x, +y, -x and -y sides lean in, degrees (negative: out, overhanging); `slant` the cap's
    tilt from level, degrees, down toward `way`; its chamfers start `drop` below its cap, and those of the sides in `steep` are steep (STEEP); `cuts` corners are cut off."""
    x0, x1, y0, y1 = rect
    centre = Vector(((x0 + x1) / 2, (y0 + y1) / 2, floor))
    walls = []
    for side, (x, y) in enumerate(((x1, centre.y), (centre.x, y1), (x0, centre.y), (centre.x, y0))):
        azimuth = math.radians(90 * side + rng.uniform(-SKEW, SKEW))
        normal = stone.leaning(azimuth, math.radians(lifts[side]))
        walls.append((azimuth, normal, normal.dot(Vector((x, y, floor))), drop * rng.uniform(*(STEEP if side in steep else insets))))
    for corner in rng.sample(range(4), cuts):
        azimuth = math.radians(45 + 90 * corner + rng.uniform(-8.0, 8.0))
        out = stone.leaning(azimuth, 0)
        reach = (Vector((x1 if corner in (0, 3) else x0, y1 if corner in (0, 1) else y0, floor)) - centre).dot(out) * rng.uniform(*CUT)
        normal = stone.leaning(azimuth, math.radians((lifts[corner] + lifts[(corner + 1) % 4]) / 2 + rng.uniform(*CUT_LEAN)))
        walls.append((azimuth, normal, normal.dot(centre + out * reach), drop * rng.uniform(*insets)))
    walls.sort(key=lambda wall: wall[0])
    cap = stone.leaning(rng.uniform(0, math.tau) if way is None else way, math.radians(90 - slant))
    return stone.prism([(normal, offset) for _, normal, offset, _ in walls], (cap, cap.dot(centre + stone.Z * (top - floor))), drop, [inset for *_, inset in walls], floor=floor)


def section(rect, lifts, rise):
    """The rectangle a block's sides have leaned in to, `rise` above its floor."""
    x0, x1, y0, y1 = rect
    move = [rise * math.tan(math.radians(lift)) for lift in lifts]
    return (x0 + move[2], x1 - move[0], y0 + move[3], y1 - move[1])


def within(rect, margins):
    """The rectangle `margins` (+x, +y, -x, -y) inside this one."""
    x0, x1, y0, y1 = rect
    return (x0 + margins[2], x1 - margins[0], y0 + margins[3], y1 - margins[1])


def draw(rng, spec):
    """The raw pieces of one arch, or a string saying why this one will not do."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    width, depth, height = hi - lo
    want = spec["arch"]
    wedged = want["span"] == "wedged"
    rubble = spec["overlap"]["min_count"] - 5
    wide = want["min_opening_m"] * rng.uniform(*WIDER)
    clear = want["min_clear_m"] * rng.uniform(*TALLER)

    # Along x, from the left: rubble, the first pier, the opening, the second pier, rubble. Together they are the bounds' width.
    narrower, first, shrink = rng.uniform(*NARROWER), rng.uniform(*RUBBLE["radius"]), rng.uniform(*RUBBLE["shrink"])
    out = [rng.uniform(*RUBBLE["out"]) for _ in range(2)]
    pier = (width - wide) / (1 + narrower + first * out[0] + first * shrink * out[1])
    radii = [first * pier * shrink**index for index in range(rubble)]
    left = lo.x + out[0] * radii[0]
    spans = ((left, left + pier), (left + pier + wide, left + pier + wide + narrower * pier))
    deep = (depth * rng.uniform(*DEEP), depth * rng.uniform(*SHALLOWER))
    middles = [(lo.y + hi.y) / 2 + rng.uniform(-1, 1) * (depth - d) / 2 for d in deep]
    way, lean = rng.uniform(0, math.tau), rng.uniform(*LEAN)

    def lifts(rect, tall):
        """How far each side of a block on `rect`, `tall` high, leans in, degrees: its taper, and the lean all the pieces share."""
        lesser = min(rect[1] - rect[0], rect[3] - rect[2])
        return [min(TAPER_MOST, math.degrees(math.atan(rng.uniform(*TAPER) * lesser / tall))) - lean * math.cos(math.radians(90 * side) - way) for side in range(4)]

    pieces, tops = [], []  # and, for each pier, (the rectangle the span may stand on, the height of the lowest of that shoulder)

    def stack(rect, floor, top, cuts):
        """A block on `rect`; returns what may stand on it: the rectangle of its shoulder, and how high the lowest of that shoulder is."""
        mine, slant = lifts(rect, top - floor), rng.uniform(*SLANT)
        size = (rect[1] - rect[0], rect[3] - rect[2])
        drop = height * rng.uniform(*SHOULDER)
        pieces.append(block(rng, rect, floor, top, mine, slant, drop, INSET, cuts))
        # Its chamfers are under whatever stands on it: that stands on its shoulder, the section its sides reach.
        return section(rect, mine, top - floor - drop), top - drop - math.hypot(*size) / 2 * math.tan(math.radians(slant))

    def reaching(rect, floor, level):
        """How high the cap of a block on `rect` must be over its middle, for the whole of its shoulder to pass `level`."""
        size = (rect[1] - rect[0], rect[3] - rect[2])
        return level + SINK + math.hypot(*size) / 2 * math.tan(math.radians(SLANT[1])) + height * SHOULDER[1]

    for index, ((x0, x1), d, y) in enumerate(zip(spans, deep, middles)):
        rect = (x0, x1, y - d / 2, y + d / 2)
        if wedged:
            # One tall block, whose whole shoulder passes the floor of the leaning block that stands on it.
            tops.append((stack(rect, lo.z, reaching(rect, lo.z, lo.z + clear), 1 - index)[0], lo.z + clear + SINK))
            continue
        cap, low = stack(rect, lo.z, lo.z + clear * rng.uniform(*JOINT[index]), 1 - index)
        upper = within(cap, [rng.uniform(*SETBACK) * (x1 - x0) for _ in range(4)])
        tops.append((stack(upper, low - SINK, reaching(upper, low - SINK, lo.z + clear), 0)[0], lo.z + clear + SINK))

    if wedged:
        knot = KNOT
        above = lo.z + height - (lo.z + clear)
        rise = above * rng.uniform(*knot["rise"])
        inner, deeps = [], []
        for index, (cap, _) in enumerate(tops):
            over = rng.uniform(*knot["over"])
            back = over * rng.uniform(*knot["back"])
            size = cap[1] - cap[0]
            rect = within(cap, [rng.uniform(*SETBACK) * size for _ in range(4)])
            mine = lifts(rect, rise)
            # The first pier is on the left, and its block leans to the right, over the opening; the second's to the left.
            mine[0], mine[2] = (-over, back) if index == 0 else (back, -over)
            drop = height * rng.uniform(*knot["shoulder_of"])
            top = lo.z + clear + rise + above * rng.uniform(*knot["above"])
            pieces.append(block(rng, rect, lo.z + clear, top, mine, rng.uniform(*knot["slant"]), drop, knot["chamfer"], 0, way=rng.choice((-1, 1)) * math.pi / 2 + rng.uniform(-0.5, 0.5), steep=(0 if index == 0 else 2,)))
            reach = rise * math.tan(math.radians(over))
            inner.append(rect[1] + reach if index == 0 else rect[0] - reach)
            deeps.append((rect[2], rect[3]))
        gap = inner[1] - inner[0]
        if gap < knot["gap"]:
            return f"leaning blocks that come within {gap:.2f} m of each other under the keystone"
        bite = [gap * rng.uniform(*knot["bite"]) for _ in range(2)]
        y0, y1 = max(d[0] for d in deeps), min(d[1] for d in deeps)
        rect = (inner[0] - bite[0], inner[1] + bite[1], y0 + rng.uniform(0.0, 0.08) * (y1 - y0), y1 - rng.uniform(0.0, 0.08) * (y1 - y0))
        mine = lifts(rect, above - rise)
        mine[0], mine[2] = -rng.uniform(*knot["undercut"]), -rng.uniform(*knot["undercut"])
        thick = above - rise
        tilt = rng.uniform(*knot["tilt"])
        top = lo.z + height - 0.8 * (rect[1] - rect[0]) / 2 * math.tan(math.radians(tilt))
        pieces.append(block(rng, rect, lo.z + clear + rise, top, mine, tilt, thick * rng.uniform(*knot["shoulder"]), knot["inset"], 1))
    else:
        part = LINTEL
        ends = [rng.uniform(*part["end"]) * (x1 - x0) for x0, x1 in spans]
        d = depth * rng.uniform(*part["depth"])
        # Over the middle of both piers' tops, as near as its depth lets it be.
        y = sum((cap[2] + cap[3]) / 2 for cap, _ in tops) / 2
        rect = (spans[0][0] + ends[0], spans[1][1] - ends[1], y - d / 2, y + d / 2)
        mine = [rng.uniform(*part["ends"]), rng.choice((-0.6, 1.0)) * rng.uniform(*part["sides"]), rng.uniform(*part["ends"]), rng.choice((-0.6, 1.0)) * rng.uniform(*part["sides"])]
        thick = height - clear
        tilt = rng.uniform(*part["tilt"])
        top = lo.z + height - 0.8 * (rect[1] - rect[0]) / 2 * math.tan(math.radians(tilt))
        # The top tips down toward one end, so the other end is the highest.
        pieces.append(block(rng, rect, lo.z + clear, top, mine, tilt, thick * rng.uniform(*part["shoulder"]), part["inset"], rng.randint(*part["cuts"]), way=rng.choice((0.0, math.pi)) + rng.uniform(-0.5, 0.5)))

    # Rubble against the outer feet: the first at the left of the first pier, the second at an outer corner of the second
    # pier, a third at the first pier's other outer corner.
    side = rng.choice((-1, 1))
    places = [
        (lo.x + radii[0], middles[0] + side * rng.uniform(0.2, 0.6) * deep[0] / 2),
        (hi.x - radii[1], middles[1] + rng.choice((-1, 1)) * rng.uniform(0.4, 0.8) * deep[1] / 2),
        (lo.x + radii[-1] * rng.uniform(1.0, 1.4), middles[0] - side * rng.uniform(0.5, 0.8) * deep[0] / 2),
    ]
    for radius, (x, y) in zip(radii, places):
        across = radius * rng.uniform(*RUBBLE["flat"])
        tall = radius * rng.uniform(*RUBBLE["tall"])
        pieces.append(block(rng, (x - radius, x + radius, y - across, y + across), lo.z, lo.z + tall, [rng.uniform(*RUBBLE["taper"]) for _ in range(4)], rng.uniform(*RUBBLE["slant"]), tall * rng.uniform(*RUBBLE["shoulder"]), RUBBLE["inset"], 0))

    if any(bm is None for bm in pieces):
        for bm in pieces:
            if bm is not None:
                bm.free()
        return "a piece that is not convex"
    if rng.random() < 0.5:
        # The other way round: the wider pier on the right.
        middle = lo.x + hi.x
        for bm in pieces:
            for vert in bm.verts:
                vert.co.x = middle - vert.co.x
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
            bm.normal_update()
    return pieces


def lit_from_behind(pieces, normals):
    """How many triangles the softened pieces would have with a corner normal facing against them, whichever way their
    quads are cut. stone.finish asks this of each face as a whole; the strip of a soft edge between two planes far apart
    in tilt (a leaning block of a knot) is a quad that is not flat, and the load test reads its two triangles."""
    behind = 0
    for bm, mine in zip(pieces, normals):
        at = 0
        for face in bm.faces:
            corners = [(loop.vert.co, mine[at + index]) for index, loop in enumerate(face.loops)]
            at += len(corners)
            cuts = [(0, 1, 2)] if len(corners) == 3 else [(0, 1, 2), (0, 2, 3), (1, 2, 3), (1, 3, 0)]
            for a, b, c in cuts:
                facing = (corners[b][0] - corners[a][0]).cross(corners[c][0] - corners[a][0])
                if facing.length > 1e-12 and min(corners[i][1].dot(facing.normalized()) for i in (a, b, c)) <= stone.FACING:
                    behind += 1
    return behind


def shape(spec, strict=True):
    """The softened pieces of the arch for the spec's seed, and their corner normals.

    With `strict` off the first arch that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
    soft = (SOFT[0], max(SOFT[0], min(SOFT[1], SOFT_SHARE * height)))
    refused = []
    for take in range(1, ARCHES + 1):
        pieces = draw(rng, spec)
        if isinstance(pieces, str):
            refused.append(f"arch {take}: {pieces}")
            continue
        done = stone.finish(pieces, spec, soft)
        if not isinstance(done, str) and lit_from_behind(pieces, done[1]):
            done = f"{lit_from_behind(pieces, done[1])} triangles of soft edges that would be lit from behind"
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv, (("arch", validate.check_arch),)) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: arch {take} of up to {ARCHES} meets the spec")
            return pieces, done[1]
        refused.append(f"arch {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its arches meets the spec:\n  " + "\n  ".join(refused))


def build_arch(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
