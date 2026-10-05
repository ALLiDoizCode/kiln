"""Arch: two unlike piers of stacked blocks bridged by one rough slab or by a knot of wedged blocks, with rubble at the feet.

docs/style/rock-shapes.md, Arch. Rock that ended up as an arch, not a door frame that was built: the
first generator here made two matched upright piers of squared blocks under a level squared lintel,
which passed every gate and was refused (tests/fixtures/arch_trilithon.py keeps it).

Every piece is a lozenge of exact planes (ADR 9; tools/stone.py, `hull`): an irregular outline at its
widest, a smaller copy of it below and another above, the whole turned and tipped as one, and cut
off level where it meets the ground. The pieces pass into each other; each is softened on its own
and they stay separate closed pieces in the one mesh (ADR 13).

The arch faces the front (-Y): its piers stand to the left and right and the opening runs through
from front to back. One pier is broad and low, the other narrower and taller, and each is a block
with a smaller one stacked on and sunk into it. A lintel arch is bridged by one thick slab lying
aslant from the low pier up to the high one. In a wedged-block arch the upper block of each pier
leans far in over the opening and a keystone is wedged between and over the two.

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order, and two sides unlike in width, height and mass.
2. Nothing upright: a lozenge's sides lean out below its widest and in above it, and every block is
   tipped; the blocks of one pier tip the same way, toward the other pier.
3. Off-centre: the opening is off the middle, and the highest part is the high end of the slab or
   the knot beside the taller pier.
4. A foot: rubble a sixth of the arch's height against the outer feet of the piers, never in the passage.
5. No level table: the slab slopes, the keystone is tipped, and so is every block's top.

A spec gives the seed, the bounds, the kind of span and the opening wanted. A seed draws whole
arches, one after another, until one meets the spec, and fails the build with the reasons when
none does.
"""

import math
import random

import bmesh
import stone
import validate
from mathutils import Matrix, Vector
from pipeline import conventions

ARCHES = 40  # how many whole arches one seed may draw before it is given up
SOFT = (0.012, 0.04)  # the least and most a soft edge eats into each plane beside it, metres
SOFT_SHARE = 0.012  # and the most as a share of the arch's height; and the least its top may be over its widest, for the span to lie on
WIDER = (1.1, 1.2)  # the stretch a player walks through, over the width the spec asks
TALLER = (1.05, 1.12)  # and over the height it asks
OUTLINE_JITTER = 0.22  # how far a corner's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.86, 1.0)  # how far out each corner stands, as a share of the block's half width that way
WAIST = (0.32, 0.5)  # how far up a block its widest outline is, as a share of its height
BENT = math.radians(13.0)  # the least the sides below and above a block's widest may differ in tilt, or it has no widest between its ends
LEANS = (13.0, 19.0)  # how far a block's sides lean out below its widest and in above it, degrees
PINCH = 0.64  # the least its top and its bottom may be, over its widest
SIDES = dict(base=(5, 6), upper=(5, 5), span=(6, 6), rubble=(5, 5))  # corners of a block's outline
NARROWER = (0.6, 0.7)  # the tall pier's width over the broad one's
SHALLOWER = (0.8, 0.92)  # and its depth
DEEP = (0.8, 0.92)  # the broad pier's depth, over the bounds'
UPPER = dict(wide=(0.85, 0.95), deep=(0.8, 0.92), bite=(0.1, 0.15), pinch=0.7)  # an upper block over the one under it: width, depth; and how far it is sunk into it, as a share of the arch's height
TIP = dict(broad=(3.0, 6.0), tall=(3.0, 6.0), knot=(3.0, 6.0), aside=0.6)  # how far each pier's blocks tip toward the other pier, degrees, and both piers' lower blocks under a knot; and how far round from straight toward it, radians
# A lintel arch: where the piers' blocks meet, as a share of the pier's height (broad, tall); how far the broad pier's upper block
# stands back from the opening, as a share of that pier's width; the slab's thickness over the arch's height; how far it lies
# into each pier's top; where its ends are, in from each pier's outer face, as a share of that pier's width (broad, tall); its
# depth over the deeper of the blocks it lies on; how far it is turned and rolled, degrees; and the slopes it may have, degrees.
SLAB = dict(joint=((0.78, 0.84), (0.43, 0.48)), back=(0.12, 0.25), thick=(0.19, 0.23), into=(0.5, 0.65), ends=((0.1, 0.3), (0.0, 0.2)), deep=(1.08, 1.2), turn=6.0, roll=4.0, slope=(13.5, 22.0))
# A wedged-block arch, whose broad pier is also the higher: how tall each pier's lower block is, over the opening's height
# (broad, tall: neither lower than the opening, so that the span rests on rock that stands from the ground); how far each upper
# block leans in over the opening, degrees (broad, tall: the tall pier's is the long leaner); the keystone's thickness over the
# arch's height; how high its top is, the same; how far the long leaner's end is into it, as a share of that thickness; how far
# past each end the keystone reaches, as a share of that block's width; its depth over the shallower upper block's; how far it
# is tipped, up toward the broad pier, degrees.
KNOT = dict(lower=((1.36, 1.44), (1.0, 1.08)), over=((10.0, 16.0), (24.0, 32.0)), thick=(0.2, 0.23), top=(0.9, 0.95), into=(0.35, 0.5), past=(0.25, 0.4), deep=(0.85, 1.0), tip=(8.0, 16.0))
# Rubble: its height over the arch's; its half width over its height; each next block's size over the last; its depth over
# its width; how far it stands out past the pier's outer face, over its half width (it lies at an outer corner of the pier, to the front or the back); how far it is tipped, degrees; and how far under the ground it goes beyond what its tip needs, over its height.
RUBBLE = dict(tall=(0.13, 0.17), radius=(0.88, 1.02), shrink=(0.78, 0.83), flat=(0.8, 1.0), out=(0.7, 1.0), tip=(13.0, 22.0), under=0.25, leans=(5.0, 9.0), pinch=0.8)


def lozenge(rng, centre, half, sides, tip, turn=None, floor=None, waist=WAIST, leans=LEANS, pinch=PINCH):
    """One piece: a block `half` (x, y, z) about `centre`, its outline of `sides` straight sides widest `waist` of the way
    up and smaller below and above (its sides lean `leans` degrees, and it is never less than `pinch` of its widest), turned `turn` radians about its own axis and tipped `tip` (the way, radians; how far,
    degrees). Cut off level at `floor` when one is given."""
    a, b, c = half
    start = rng.uniform(0, math.tau)
    # The outline's sides as lines, each square to its own direction: however long the block, no two sides are near one line.
    lines = []
    for i in range(sides):
        azimuth = start + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        lines.append((math.cos(azimuth), math.sin(azimuth), math.hypot(a * math.cos(azimuth), b * math.sin(azimuth)) * rng.uniform(*OUTLINE_IN)))
    outline = []
    for (ax, ay, ad), (bx, by, bd) in zip(lines, lines[1:] + lines[:1]):
        det = ax * by - ay * bx
        outline.append(((ad * by - ay * bd) / det, (ax * bd - ad * bx) / det))
    # Its corners stand out past the sides' middles: bring the outline back to the half widths asked.
    fit = (a / max(abs(x) for x, _ in outline), b / max(abs(y) for _, y in outline))
    outline = [(x * fit[0], y * fit[1]) for x, y in outline]
    widest = -c + 2 * c * rng.uniform(*waist)
    below = max(pinch, 1 - math.tan(math.radians(rng.uniform(*leans))) * (widest + c) / min(a, b))
    above = max(pinch, 1 - math.tan(math.radians(rng.uniform(*leans))) * (c - widest) / min(a, b))
    rings = ((below, -c), (1.0, widest), (above, c))
    # On a block much taller than it is wide the sides below and above its widest would be one bent plane (stone.MIN_ANGLE):
    # such a block is widest at its foot and tapers the whole way up.
    nearest = 0.7 * min(a, b)
    if math.atan((1 - below) * nearest / (widest + c)) + math.atan((1 - above) * nearest / (c - widest)) < BENT:
        rings = ((1.0, -c), (above, c))
    way, far = tip
    turned = Matrix.Rotation(math.radians(far), 3, Vector((-math.sin(way), math.cos(way), 0))) @ Matrix.Rotation(rng.uniform(-0.3, 0.3) if turn is None else turn, 3, "Z")
    points = [centre + turned @ Vector((x * scale, y * scale, z)) for scale, z in rings for x, y in outline]
    return stone.hull(points, floor)


def draw(rng, spec):
    """The raw pieces of one arch, or a string saying why this one will not do."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    width, depth, height = hi - lo
    want = spec["arch"]
    wedged = want["span"] == "wedged"
    rubble = spec["overlap"]["min_count"] - 5
    wide = want["min_opening_m"] * rng.uniform(*WIDER)
    clear = want["min_clear_m"] * rng.uniform(*TALLER)
    middle = (lo.y + hi.y) / 2
    pieces = []

    # The piers: the broad one on the left (index 0), the tall one on the right; `toward` is the way each faces the opening.
    toward = (1, -1)
    tips = [rng.uniform(*TIP["knot" if wedged else kind]) for kind in ("broad", "tall")]
    ways = [(0.0 if side > 0 else math.pi) + rng.uniform(-TIP["aside"], TIP["aside"]) for side in toward]
    if wedged:
        knot = KNOT
        lower = [clear * rng.uniform(*knot["lower"][index]) for index in range(2)]
        over = [rng.uniform(*knot["over"][index]) for index in range(2)]
        thick = height * rng.uniform(*knot["thick"])
        crown = height * rng.uniform(*knot["top"])
        # The broad pier's upper block ends at the top of the bounds; the long leaner's end is into the keystone, lower.
        ends = [height, crown - thick + thick * rng.uniform(*knot["into"])]
        # How far each pier comes in over the opening by the height a player needs: its lower block tips that way.
        inward = [clear * math.tan(math.radians(tips[index])) for index in range(2)]
    else:
        slab = SLAB
        thick = height * rng.uniform(*slab["thick"])
        inward = [0.6 * clear * math.tan(math.radians(tips[0])), clear * math.tan(math.radians(tips[1]))]
    gap = wide + sum(inward)

    # Along x, from the left: rubble, the broad pier, the gap between the piers at the ground, the tall pier, rubble.
    tall = height * rng.uniform(*RUBBLE["tall"])
    radii = [tall * rng.uniform(*RUBBLE["radius"])]
    for _ in range(rubble - 1):
        radii.append(radii[-1] * rng.uniform(*RUBBLE["shrink"]))
    out = [radii[index] * rng.uniform(*RUBBLE["out"]) for index in range(2)]
    narrower = rng.uniform(*NARROWER)
    broad = (width - gap - sum(out)) / (1 + narrower)
    widths = (broad, broad * narrower)
    if widths[1] < 0.14 * height:
        return f"a tall pier {widths[1]:.2f} m wide under an arch {height:.1f} m tall"
    deeps = (depth * rng.uniform(*DEEP), depth * rng.uniform(*DEEP) * rng.uniform(*SHALLOWER))
    inner = (lo.x + out[0] + broad, lo.x + out[0] + broad + gap)  # each pier's face on the opening, at the ground
    ys = [middle + rng.uniform(-1, 1) * (depth - d) / 2 for d in deeps]

    def base(index, top):
        """A pier's lower block, from the ground up to `top`. Returns where the middle of its top is, along x."""
        side, tip = toward[index], math.radians(tips[index])
        sink = max(widths[index], deeps[index]) / 2 * math.sin(tip) + 0.05
        c = (top + sink) / 2 / math.cos(tip)
        x = inner[index] - side * widths[index] / 2
        pieces.append(lozenge(rng, Vector((x, ys[index], lo.z + (top - sink) / 2)), (widths[index] / 2, deeps[index] / 2, c), rng.randint(*SIDES["base"]), (ways[index], tips[index]), floor=lo.z))
        return x + side * (top + sink) / 2 * math.tan(tip)

    def upper(index, x, bottom, top, lean, back):
        """A pier's upper block, from `bottom` to `top`, its foot `back` behind `x` and leaning `lean` degrees toward the
        opening. Returns (its half width, its half depth, where its upper end is along x)."""
        side, angle = toward[index], math.radians(lean)
        size = (widths[index] * rng.uniform(*UPPER["wide"]) / 2, deeps[index] * rng.uniform(*UPPER["deep"]) / 2)
        length = (top - bottom) / math.cos(angle)
        foot = x - side * back
        centre = Vector((foot + side * length / 2 * math.sin(angle), ys[index], lo.z + (bottom + top) / 2))
        pieces.append(lozenge(rng, centre, (*size, length / 2), rng.randint(*SIDES["upper"]), (ways[index], lean), pinch=UPPER["pinch"]))
        return (*size, foot + side * length * math.sin(angle))

    if wedged:
        tops = []
        for index in range(2):
            x = base(index, lower[index])
            bite = height * rng.uniform(*UPPER["bite"])
            tops.append(upper(index, x, lower[index] - bite, ends[index], over[index], 0.0))
        # The keystone: wedged between the two upper ends and over the long leaner's, tipped up toward the broad pier.
        reach = [tops[index][0] * 2 * rng.uniform(*knot["past"]) for index in range(2)]
        left, right = tops[0][2] - reach[0], tops[1][2] + reach[1]
        if right - left < 0.5 * widths[1]:
            return f"leaning blocks whose ends are {tops[1][2] - tops[0][2]:.2f} m apart: no room for a keystone"
        half = ((right - left) / 2, min(tops[0][1], tops[1][1]) * rng.uniform(*knot["deep"]), thick / 2)
        centre = Vector(((left + right) / 2, (ys[0] + ys[1]) / 2, lo.z + crown - thick / 2))
        pieces.append(lozenge(rng, centre, half, rng.randint(*SIDES["span"]), (rng.uniform(-0.3, 0.3), rng.uniform(*knot["tip"])), turn=math.radians(rng.uniform(-8, 8))))
    else:
        # The slab's underside passes over the broad pier's face at the height a player needs and rises to the tall pier;
        # its high end is the top of the bounds, which gives its slope.
        ends = [rng.uniform(*slab["ends"][index]) * widths[index] for index in range(2)]
        left, right = inner[0] - widths[0] + ends[0], inner[1] + widths[1] - ends[1]
        slope = math.atan((height - thick - clear) / (right - inner[0]))
        if not slab["slope"][0] <= math.degrees(slope) <= slab["slope"][1]:
            return f"a slab that would slope {math.degrees(slope):.0f} degrees"

        def under(x):
            return clear + (x - inner[0]) * math.tan(slope)

        sizes = []
        for index in range(2):
            back = rng.uniform(*slab["back"]) * widths[index] if index == 0 else rng.uniform(0.02, 0.08) * widths[index]
            # The pier's top is into the slab over its own middle.
            over_x = inner[index] - toward[index] * (widths[index] / 2 + back)
            top = under(over_x) + thick * rng.uniform(*slab["into"])
            joint = top * rng.uniform(*slab["joint"][index])
            x = base(index, joint)
            sizes.append(upper(index, x, joint - height * rng.uniform(*UPPER["bite"]), top, tips[index], back))
        half = ((right - left) / 2 / math.cos(slope), min(depth / 2, max(size[1] for size in sizes) * rng.uniform(*slab["deep"])), thick / 2)
        x = (left + right) / 2
        centre = Vector((x, sum(ys) / 2, lo.z + under(x) + thick / 2 / math.cos(slope)))
        way = math.pi + math.atan2(math.radians(rng.uniform(-slab["roll"], slab["roll"])), slope)
        pieces.append(lozenge(rng, centre, half, rng.randint(*SIDES["span"]), (way, math.degrees(slope)), turn=math.radians(rng.uniform(-slab["turn"], slab["turn"]))))

    # Rubble against the outer feet: the first at an outer corner of the broad pier, the second at the opposite outer
    # corner of the tall one, a third at the broad pier's other outer corner.
    side = rng.choice((-1, 1))
    places = [
        (lo.x + radii[0], ys[0] + side * (deeps[0] / 2 - radii[0] * rng.uniform(0.6, 1.0))),
        (hi.x - radii[1], ys[1] - side * (deeps[1] / 2 - radii[1] * rng.uniform(0.6, 1.0))),
        (lo.x + radii[-1] * rng.uniform(1.0, 1.6), ys[0] - side * (deeps[0] / 2 - radii[-1] * rng.uniform(0.6, 1.0))),
    ]
    for index, (radius, (x, y)) in enumerate(zip(radii, places)):
        high = tall * radius / radii[0]
        tip = rng.uniform(*RUBBLE["tip"])
        # Its widest is under the ground, so every side that shows leans in, and the ground cuts no corner of it short.
        sunk = radius * math.sin(math.radians(tip)) + RUBBLE["under"] * high
        half = (radius, radius * rng.uniform(*RUBBLE["flat"]), (high + sunk) / 2)
        widest = RUBBLE["under"] * high / 2 / (high + sunk)
        pieces.append(lozenge(rng, Vector((x, y, lo.z + (high - sunk) / 2)), half, rng.randint(*SIDES["rubble"]), (rng.uniform(0, math.tau), tip), floor=lo.z, waist=(widest, widest), leans=RUBBLE["leans"], pinch=RUBBLE["pinch"]))

    if rng.random() < 0.5:
        # The other way round: the broad pier on the right.
        mirror = lo.x + hi.x
        for bm in pieces:
            for vert in bm.verts:
                vert.co.x = mirror - vert.co.x
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
            bm.normal_update()
    return pieces


def lit_from_behind(pieces, normals):
    """How many triangles the softened pieces would have with a corner normal facing against them, whichever way their
    quads are cut. stone.finish asks this of each face as a whole; the strip of a soft edge between two planes far apart
    in tilt is a quad that is not flat, and the load test reads its two triangles."""
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
