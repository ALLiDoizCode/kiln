"""Block: a near-cuboid of stone with chamfered corners, whole or parted along one or two cracks.

docs/style/rock-shapes.md, Block. The block is cut from a box by planes (ADR 9): the ground, a
top that barely tips, four sides that barely lean, and three or four chamfers, each across one
rim of the top or one upright corner. A whole block is that one closed skin.

A cracked block is the same box parted along its cracks into two or three pieces, left as
overlapping pieces (ADR 13, tools/stone.py). A crack is a plane across the block's length. Each
piece beside it ends in a wall of its own, and the two walls lean apart: above the line where
they cross they leave a V-shaped groove, and below it the pieces pass into each other. Each
piece is cut from the box set in by its own amount, so one stands proud of the next along the
crack and no two show faces in one plane (source/block/brief.md, Decisions).

Every block is drawn one metre wide, softened there, and scaled to its spec's bounds, so a soft
edge, a chamfer and a crack are shares of the block's width and the run of sizes is one construction.

A spec gives the seed, the bounds and (as `overlap`) how many pieces. A seed draws whole blocks,
one after another, until one meets the spec, and fails the build with the reasons when none does.
"""

import math
import random

import bmesh
import stone
import validate
from mathutils import Vector
from pipeline import conventions

BLOCKS = 60  # how many whole blocks one seed may draw before it is given up
SOFT = (0.008, 0.02)  # the least and most a soft edge eats into each plane beside it, as a share of the block's width
TIP = (0.0, 2.0)  # how far the top tips from level, degrees
LEAN = (0.0, 3.0)  # how far a side leans in from upright, degrees
CHAMFERS = (3, 4)  # how many rims and upright corners are cut
TOP_CHAMFERS = (1, 2)  # how many of those are rims of the top; the rest are upright corners
CHAMFER_IN = (0.1, 0.15)  # how far in from the corner a chamfer meets each face beside it, as a share of the block's width
# A crack: where along the block's length it crosses, as a share of the length, for one crack and
# for two (either may be mirrored); never the middle, so the pieces differ in size.
CRACK_AT = {1: ((0.6, 0.7),), 2: ((0.42, 0.5), (0.72, 0.8))}
CRACK_SKEW = (4.0, 15.0)  # how far a crack is turned from square across the block, degrees, either way
CRACK_LEAN = (0.0, 6.0)  # how far it leans from upright, degrees, either way
CRACK_APART = (9.0, 13.0)  # how far each of its two walls leans back from it, degrees: the groove's sides
CRACK_DEEP = (0.06, 0.08)  # how far below the lower of the two tops the walls cross, as a share of the block's width: the groove's depth
SET_IN = (0.0, 0.012, 0.024)  # how far each piece's box is set in on every side, as a share of the block's width; dealt out by the seed


def carve(planes):
    """The convex solid behind every plane (normal, offset). A plane that touches nothing of it is
    left out (a piece has only the chamfers and sides its part of the block has); None when nothing is left."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=200.0)
    for normal, offset in planes:
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=normal * offset, plane_no=normal, clear_outer=True)
        rim = [g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
        if len(rim) >= 3:
            bmesh.ops.holes_fill(bm, edges=rim)
        if not bm.faces:
            bm.free()
            return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    if any(not e.is_manifold for e in bm.edges) or bm.calc_volume(signed=True) <= 0:
        bm.free()
        return None
    return bm


def either(rng, low, high):
    return rng.uniform(low, high) * rng.choice((-1, 1))


def draw(rng, lo, hi, count):
    """The raw pieces of one block filling the bounds lo..hi, in order along its length, or None when a piece came to nothing."""
    middle = (lo + hi) / 2
    top_normal = stone.leaning(rng.uniform(0, math.tau), math.radians(90 - rng.uniform(*TIP)))
    top = (top_normal, top_normal.dot(Vector((middle.x, middle.y, hi.z))))
    sides = []
    for quarter, at in enumerate((Vector((hi.x, middle.y, lo.z)), Vector((middle.x, hi.y, lo.z)), Vector((lo.x, middle.y, lo.z)), Vector((middle.x, lo.y, lo.z)))):
        normal = stone.leaning(quarter * math.tau / 4, math.radians(rng.uniform(*LEAN)))
        sides.append((normal, normal.dot(at)))

    # Chamfers: each cuts the corner between two planes of the box, meeting each a little way in from it.
    rims = [(top, side, stone.Z.cross(side[0])) for side in sides]
    corners = [(sides[i], sides[(i + 1) % 4], stone.Z) for i in range(4)]
    on_top = rng.randint(*TOP_CHAMFERS)
    cut = rng.sample(rims, on_top) + rng.sample(corners, max(1, rng.randint(*CHAMFERS) - on_top))
    chamfers = []
    for a, b, along in cut:
        on_edge = stone.meeting(a, b, (along, along.dot(middle)))
        in_a, in_b = rng.uniform(*CHAMFER_IN), rng.uniform(*CHAMFER_IN)
        raw = a[0] * in_a + b[0] * in_b
        chamfers.append((raw.normalized(), raw.normalized().dot(on_edge) - in_a * in_b / raw.length))

    # Cracks, in order along the block: for each, the wall of the piece before it and the wall of the piece after it.
    set_in = rng.sample(SET_IN, count) if count > 1 else [0.0]
    mirrored = rng.random() < 0.5
    places = sorted(1 - along if mirrored else along for along in (rng.uniform(low, high) for low, high in CRACK_AT.get(count - 1, ())))
    walls = []
    for index, along in enumerate(places):
        across = stone.leaning(math.radians(either(rng, *CRACK_SKEW)), math.radians(either(rng, *CRACK_LEAN)))
        # The walls cross below the top of the lower of the two pieces: the groove is that deep on both sides.
        lower_top = hi.z - max(set_in[index], set_in[index + 1])
        crossing = Vector((lo.x + (hi.x - lo.x) * along, middle.y, lower_top - rng.uniform(*CRACK_DEEP)))
        pair = []
        for outward in (across, -across):
            up = (stone.Z - outward * stone.Z.dot(outward)).normalized()
            apart = math.radians(rng.uniform(*CRACK_APART))
            normal = outward * math.cos(apart) + up * math.sin(apart)
            pair.append((normal, normal.dot(crossing)))
        walls.append(pair)

    pieces = []
    for index in range(count):
        planes = [(-stone.Z, -lo.z)] + [(normal, offset - set_in[index]) for normal, offset in (top, *sides, *chamfers)]
        if index > 0:
            planes.append(walls[index - 1][1])
        if index < count - 1:
            planes.append(walls[index][0])
        bm = carve(planes)
        if bm is None:
            for made in pieces:
                made.free()
            return None
        pieces.append(bm)
    return pieces


def shape(spec, strict=True):
    """The softened pieces of the block for the spec's seed, and their corner normals.

    With `strict` off the first block that can be softened is returned, whatever it measures."""
    name = spec["objects"][0]
    rng = random.Random(spec["seed"])
    conv = conventions()
    lo, hi = Vector(spec["bounds_m"]["min"]), Vector(spec["bounds_m"]["max"])
    count = spec["overlap"]["max_count"] if "overlap" in spec else 1
    # Drawn one metre wide: the kit's least sizes are a metre rock's, and every feature is a share of the width.
    scale = hi.x - lo.x
    metre = {**spec, "bounds_m": {"min": list(lo / scale), "max": list(hi / scale)}}
    extra = (("block", validate.check_block), ("cracks", validate.check_cracks))
    refused = []
    for take in range(1, BLOCKS + 1):
        pieces = draw(rng, lo / scale, hi / scale, count)
        if pieces is None:
            refused.append(f"block {take}: a piece that came to nothing")
            continue
        done = stone.finish(pieces, metre, SOFT)
        problems = [done] if isinstance(done, str) else []
        if not problems:
            for bm in pieces:
                for vert in bm.verts:
                    vert.co *= scale
                bm.normal_update()
            problems = stone.unmet(name, pieces, spec, conv, extra=extra) if strict else []
        if not problems:
            print(f"{name} seed {spec['seed']}: block {take} of up to {BLOCKS} meets the spec")
            return pieces, done[1]
        refused.append(f"block {take}: " + "; ".join(problems))
        for bm in pieces:
            bm.free()
    raise RuntimeError(f"{name} seed {spec['seed']}: none of its blocks meets the spec:\n  " + "\n  ".join(refused))


def build_block(spec, strict=True):
    pieces, normals = shape(spec, strict)
    material, colour = next(iter(spec["materials"].items()))
    return stone.join(spec["objects"][0], pieces, normals, material, colour)
