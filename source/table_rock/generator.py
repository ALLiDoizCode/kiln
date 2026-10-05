"""Table rock: a wide flat cap of rock resting on one or two narrow necks, with a small block at the foot of each.

docs/style/rock-shapes.md, Table rock. Every piece is a prism cut by exact planes (ADR 9,
tools/stone.py). The cap is a plate held off the ground: a level underside, sides that lean
out from it to a shoulder, and a gently tipped top ringed by chamfers. A neck is a prism that
tapers from the ground up into the cap's underside; a block is a low plate against a neck's
foot. The pieces pass into each other; each is softened on its own and they stay separate
closed pieces in the one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: the cap, the necks (the second narrower than the
   first), and a block a fraction of the size of the neck it stands against.
2. Nothing upright: the cap's sides are undercut, the necks taper, the blocks' sides lean in.
3. Off-centre: a single neck stands off the middle of the cap; two stand apart along its
   length, unequal, and neither on its middle line.
4. A foot: one block against each neck, under the cap, on the side away from the other neck.
5. A flat cap ringed by chamfers, with a polygonal outline of six to eight sides.

A spec gives the seed, the bounds, how many necks, and the open air wanted under the cap. A
seed draws whole table rocks, one after another, until one meets the spec, and fails the build
with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Vector
from pipeline import conventions

TABLES = 40  # how many whole table rocks one seed may draw before it is given up
SOFT = (0.012, 0.035)  # the least and most a soft edge eats into each plane beside it, metres: a neck's top and a block are too small for wider
SOFT_SHARE = 0.012  # and the most as a share of the height: a low table rock has small chamfers for it to eat
OUTLINE_JITTER = 0.25  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.88, 1.0)  # how far out each side stands, as a share of the piece's radius that way
# The cap: its sides; how far above the clearance the spec asks its underside is, as a share of that clearance;
# how far its sides lean out going up and its top tips, degrees; how far below the top its chamfers start, as a
# share of its thickness; and how far in from the side a chamfer meets the top, over how far below it starts.
CAP = dict(sides=(6, 8), above=(0.05, 0.12), undercut=(18.0, 38.0), tilt=(2.0, 5.0), shoulder=(0.25, 0.38), inset=(0.9, 1.8))
# A neck: its sides; its radius at the ground as a share of the cap's lesser half width; its depth over its width;
# how much narrower it is where it meets the cap, as a share of that radius; how far up into the cap it goes, as a
# share of the cap's thickness; its own top, inside the cap: slant in degrees, and where its chamfers start, as a share of how far it goes in
# and at most `shoulder_most` of its radius there.
NECK = dict(sides=(5, 6), radius=(0.3, 0.36), flat=(0.8, 1.0), narrower=(0.25, 0.4), into=(0.2, 0.35), slant=(3.0, 8.0), shoulder=(0.4, 0.6), shoulder_most=0.2, inset=(0.5, 1.0))
ALONE = 0.2  # a single neck stands up to this share of the cap's half widths off its middle
# Two necks: how far along the cap's longer half width each stands from the middle, how far across the shorter, and the second's radius over the first's.
PAIR = dict(along=(0.3, 0.4), across=(-0.12, 0.12), second=(0.62, 0.72))
# A block: how far round from straight away from the other neck it stands, degrees (anywhere round a single neck); how far
# out along its neck's radius its middle is; its radius over its neck's; its height over its own radius; and its shape.
BLOCK = dict(turn=(-70.0, 70.0), out=(0.85, 1.1), radius=(0.7, 0.95), tall=(0.7, 1.1), sides=(4, 5), lean=(8.0, 16.0), slant=(3.0, 9.0), shoulder=(0.15, 0.25), inset=(0.9, 1.4))


def outline(rng, sides, centre, radii, lean):
    """The sides of a piece as planes round `centre`: `lean` gives each side's lift above horizontal, degrees, from its azimuth."""
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        normal = stone.leaning(azimuth, math.radians(lean(azimuth)))
        walls.append((normal, normal.dot(centre + out * reach)))
    return walls


def cap(rng, centre, radii, underside, height):
    """The cap (stone.prism): a level underside at `underside`, sides leaning out from it to the shoulder,
    where it is `radii` wide, and a tipped top ringed by chamfers, its highest corner about `height` up."""
    thick = height - underside
    tilt = math.radians(rng.uniform(*CAP["tilt"]))
    normal = stone.leaning(rng.uniform(0, math.tau), math.pi / 2 - tilt)
    # The top passes under `height` at the middle by about what it rises to its highest corner.
    top = (normal, normal.dot(centre + stone.Z * (height - 0.8 * max(radii) * math.tan(tilt))))
    drop = thick * rng.uniform(*CAP["shoulder"])
    shoulder = Vector((centre.x, centre.y, height - drop))
    walls = outline(rng, rng.randint(*CAP["sides"]), shoulder, radii, lambda _: -rng.uniform(*CAP["undercut"]))
    return stone.prism(walls, top, drop, [drop * rng.uniform(*CAP["inset"]) for _ in walls], floor=underside)


def draw(rng, spec):
    """The raw pieces of one table rock, the cap first, then the necks, then the blocks, or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    height = hi.z - lo.z
    half = ((hi.x - lo.x) / 2, (hi.y - lo.y) / 2)
    middle = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    necks = spec["table"]["necks"]
    blocks = spec["overlap"]["min_count"] - 1 - necks
    clear = spec["table"]["min_clear_m"]
    underside = clear * (1 + rng.uniform(*CAP["above"]))
    thick = height - underside
    pieces = [cap(rng, middle, half, lo.z + underside, lo.z + height)]

    # Where the necks stand, and how wide each is at the ground.
    long = 0 if half[0] >= half[1] else 1
    radius = min(half) * rng.uniform(*NECK["radius"])
    if necks == 1:
        at = stone.leaning(rng.uniform(0, math.tau), 0) * rng.uniform(0, ALONE)
        plans = [(Vector((at.x * half[0], at.y * half[1], 0)), radius)]
    else:
        plans = []
        for side in rng.sample((-1, 1), 2)[:necks]:
            at = [0.0, 0.0, 0.0]
            at[long] = side * half[long] * rng.uniform(*PAIR["along"])
            at[1 - long] = half[1 - long] * rng.uniform(*PAIR["across"])
            plans.append((Vector(at), radius))
            radius *= rng.uniform(*PAIR["second"])
    for at, radius in plans:
        tall = underside + thick * rng.uniform(*NECK["into"])
        narrower = rng.uniform(*NECK["narrower"])
        radii = (radius, radius * rng.uniform(*NECK["flat"]))
        if rng.random() < 0.5:
            radii = radii[::-1]
        into = tall - underside
        slant = stone.leaning(rng.uniform(0, math.tau), math.radians(90 - rng.uniform(*NECK["slant"])))
        centre = middle + at
        taper = math.degrees(math.atan(min(radii) * narrower / tall))
        walls = outline(rng, rng.randint(*NECK["sides"]), centre, radii, lambda _: taper * rng.uniform(0.8, 1.2))
        drop = min(into * rng.uniform(*NECK["shoulder"]), min(radii) * (1 - narrower) * NECK["shoulder_most"])
        pieces.append(stone.prism(walls, (slant, slant.dot(centre + stone.Z * tall)), drop, [drop * rng.uniform(*NECK["inset"]) for _ in walls], floor=lo.z))

    # One block against the foot of each neck, on the side away from the other neck.
    for index, (at, radius) in enumerate(plans[:blocks]):
        if necks == 1:
            way = rng.uniform(0, math.tau)
        else:
            away = at - plans[1 - index][0]
            way = math.atan2(away.y, away.x) + math.radians(rng.uniform(*BLOCK["turn"]))
        centre = middle + at + stone.leaning(way, 0) * (radius * rng.uniform(*BLOCK["out"]))
        size = radius * rng.uniform(*BLOCK["radius"])
        tall = size * rng.uniform(*BLOCK["tall"])
        slant = stone.leaning(rng.uniform(0, math.tau), math.radians(90 - rng.uniform(*BLOCK["slant"])))
        walls = outline(rng, rng.randint(*BLOCK["sides"]), centre, (size, size), lambda _: rng.uniform(*BLOCK["lean"]))
        drop = tall * rng.uniform(*BLOCK["shoulder"])
        pieces.append(stone.prism(walls, (slant, slant.dot(centre + stone.Z * tall)), drop, [drop * rng.uniform(*BLOCK["inset"]) for _ in walls], floor=lo.z))
    if any(bm is None for bm in pieces):
        for bm in pieces:
            if bm is not None:
                bm.free()
        return None
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the table rock for the spec's seed, and their corner normals.

    With `strict` off the first table rock that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
    soft = (SOFT[0], max(SOFT[0], min(SOFT[1], SOFT_SHARE * height)))
    refused = []
    for take in range(1, TABLES + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"table rock {take}: a piece that is not convex")
            continue
        done = stone.finish(pieces, spec, soft)
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv, (("table", validate.check_table),)) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: table rock {take} of up to {TABLES} meets the spec")
            return pieces, done[1]
        refused.append(f"table rock {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its table rocks meets the spec:\n  " + "\n  ".join(refused))


def build_table_rock(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
