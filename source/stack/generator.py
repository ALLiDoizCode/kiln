"""Stack: three to five flat stones piled off-centre, each smaller than the one below and turned from it.

docs/style/rock-shapes.md, Stack. Every stone is a prism cut by exact planes (ADR 9,
tools/stone.py): an underside, five to seven sides that lean in, a gently tipped cap and a
chamfer between the cap and each side. The lowest stands on the ground; every other one lies
on the cap of the stone below, tipped as that cap is and sunk a little into it. Each is
softened on its own and they stay separate closed pieces in the one mesh (ADR 13).

The habits of rock-shapes.md, as the generator applies them:

1. Several pieces with a clear size order: each stone is narrower and thinner than the one below.
2. Off-centre: each stone sits off the middle of the one below, all roughly one way, so the
   top of the pile is to one side; never so far that the stones above would tip off.
3. Turned: each stone has its own outline, at its own angle.
4. Nothing upright: every side leans in by its own amount.
5. Flat caps ringed by chamfers: each cap tips a few degrees, back against the one below.

A spec gives the seed, the bounds and how many stones. A seed draws whole stacks, one after
another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import stone
import validate
from mathutils import Matrix, Vector
from pipeline import conventions

STACKS = 40  # how many whole stacks one seed may draw before it is given up
SOFT = (0.006, 0.03)  # the least and most a soft edge eats into each plane beside it, metres
SOFT_SHARE = 0.02  # and the most as a share of the stack's height: a small stack has small chamfers for it to eat
SIDES = ((6, 7), (5, 6))  # how many sides the lowest stone's outline has, and the others'
LEAN = (12.0, 22.0)  # how far a side leans in from its stone's upright, degrees
TILT = (2.0, 5.0)  # how far a cap tips from its stone's level, degrees
TILT_BACK = 0.7  # a cap tips within this of straight back against the one below, radians
OUTLINE_JITTER = 0.3  # how far a side's direction strays from an even spacing, as a share of that spacing
OUTLINE_IN = (0.86, 1.0)  # how far out each side stands, as a share of the stone's radius that way
CHAMFER_DROP = (0.3, 0.42)  # how far below the cap its chamfers start, as a share of the stone's thickness
CHAMFER_INSET = (0.8, 1.4)  # how far in from the side a chamfer meets the cap, over how far below the cap it starts
NARROWER = (0.72, 0.82)  # each stone's radius over that of the one below
THINNER = 0.7  # a stone's thickness goes as its radius to this power: the small stones are a little stouter
THICK_JITTER = 0.12  # how far a stone's thickness strays from that, as a share of it
OFF = (0.12, 0.3)  # how far off the middle of the stone below a stone sits, as a share of that stone's radius
OFF_TOGETHER = 1.2  # the stones sit off within this of one direction, radians
SINK = (0.1, 0.2)  # how far a stone is sunk into the cap below, as a share of its own thickness


def flat_stone(rng, sides, radii, thick, tip):
    """One stone (stone.prism) lying on z = 0 with its middle at the origin, and the plane of its cap.

    Its cap tips down toward `tip` (radians round the compass)."""
    cap = stone.leaning(tip, math.radians(90 - rng.uniform(*TILT)))
    top = (cap, cap.dot(stone.Z * thick))
    turn = rng.uniform(0, math.tau)
    walls = []
    for i in range(sides):
        azimuth = turn + (i + rng.uniform(-OUTLINE_JITTER, OUTLINE_JITTER)) * math.tau / sides
        out = stone.leaning(azimuth, 0)
        reach = math.hypot(radii[0] * out.x, radii[1] * out.y) * rng.uniform(*OUTLINE_IN)
        normal = stone.leaning(azimuth, math.radians(rng.uniform(*LEAN)))
        walls.append((normal, normal.dot(out * reach)))
    drop = thick * rng.uniform(*CHAMFER_DROP)
    return stone.prism(walls, top, drop, [drop * rng.uniform(*CHAMFER_INSET) for _ in walls]), top


def draw(rng, spec):
    """The raw stones of one stack, lowest first, or None when one did not come out convex."""
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    count = rng.randint(spec["overlap"]["min_count"], spec["overlap"]["max_count"])
    toward = rng.uniform(0, math.tau)  # the way the pile steps off its middle
    tip = rng.uniform(0, math.tau)  # the way the lowest cap tips; each next one tips back
    # Laid out seen from above round a lowest stone of radius 1, then scaled so the outlines fill the bounds.
    plans = [(Vector((0, 0)), 1.0)]
    for _ in range(count - 1):
        centre, radius = plans[-1]
        way = stone.leaning(toward + rng.uniform(-OFF_TOGETHER, OFF_TOGETHER), 0).to_2d()
        plans.append((centre + way * (radius * rng.uniform(*OFF)), radius * rng.uniform(*NARROWER)))
    low = [min(centre[i] - radius for centre, radius in plans) for i in range(2)]
    high = [max(centre[i] + radius for centre, radius in plans) for i in range(2)]
    scale = [(hi[i] - lo[i]) / (high[i] - low[i]) for i in range(2)]
    # Thicknesses that add up to the height, less what each stone is sunk into the one below.
    sinks = [0.0] + [rng.uniform(*SINK) for _ in range(count - 1)]
    shares = [radius**THINNER * (1 + rng.uniform(-THICK_JITTER, THICK_JITTER)) for _, radius in plans]
    unit = (hi.z - lo.z) / sum(share * (1 - sink) for share, sink in zip(shares, sinks))
    pieces = []
    place = Matrix.Translation(Vector((lo.x - low[0] * scale[0], lo.y - low[1] * scale[1], lo.z)))
    below = None  # the plane of the cap below, in that stone's own space, and where on it this stone sits
    for index, ((centre, radius), share, sink) in enumerate(zip(plans, shares, sinks)):
        thick = share * unit
        if below is not None:
            (normal, offset), seat = below
            at = Vector((seat.x, seat.y, (offset - normal.x * seat.x - normal.y * seat.y) / normal.z))
            # Lying on the cap below: tipped as it is, and sunk into it.
            place = place @ Matrix.Translation(at - normal * (sink * thick)) @ stone.Z.rotation_difference(normal).to_matrix().to_4x4()
        bm, top = flat_stone(rng, rng.randint(*SIDES[min(index, 1)]), (radius * scale[0], radius * scale[1]), thick, tip + rng.uniform(-TILT_BACK, TILT_BACK))
        if bm is None:
            for made in pieces:
                made.free()
            return None
        bm.transform(place)
        bm.normal_update()
        pieces.append(bm)
        tip += math.pi
        if index + 1 < count:
            step = plans[index + 1][0] - centre
            below = (top, Vector((step.x * scale[0], step.y * scale[1])))
    return pieces


def shape(spec, strict=True):
    """The softened stones of the stack for the spec's seed, and their corner normals.

    With `strict` off the first stack that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    extra = (("pile", validate.check_pile),) if hasattr(validate, "check_pile") else ()
    refused = []
    for take in range(1, STACKS + 1):
        pieces = draw(rng, spec)
        if pieces is None:
            refused.append(f"stack {take}: a stone that is not convex")
            continue
        height = spec["bounds_m"]["max"][2] - spec["bounds_m"]["min"][2]
        done = stone.finish(pieces, spec, (SOFT[0], max(SOFT[0], min(SOFT[1], SOFT_SHARE * height))))
        problems = [done] if isinstance(done, str) else (stone.unmet(name, pieces, spec, conv, extra) if strict else [])
        if not problems:
            print(f"{name} seed {spec['seed']}: stack {take} of up to {STACKS} meets the spec")
            return pieces, done[1]
        refused.append(f"stack {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its stacks meets the spec:\n  " + "\n  ".join(refused))


def build_stack(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
