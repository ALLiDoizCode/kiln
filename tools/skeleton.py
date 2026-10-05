"""A tree's bark as the pipeline sees it: level slices through the trunk and branches.

A **slice** is the bark cut by a level plane; it comes out as closed loops,
one for every limb the plane passes through. Everything the checks say about
a skeleton (girth, flat sides, fork, taper, roots, lean) is read from slices,
so nothing trusts a label from the build script.

Used by tools/validate.py. Runs under Blender's Python.
"""

import math

import bmesh
from mathutils import Vector


def only(bm, material_index):
    """A copy of the mesh holding only one material's faces."""
    copy = bm.copy()
    bmesh.ops.delete(copy, geom=[f for f in copy.faces if f.material_index != material_index], context="FACES")
    return copy


def slice_at(bark, z):
    """The closed loops a level plane at `z` cuts from the bark, largest first.

    Each is (radius of the circle with the loop's area, middle, corners in order), in the plane.
    """
    cut = bark.copy()
    result = bmesh.ops.bisect_plane(cut, geom=cut.verts[:] + cut.edges[:] + cut.faces[:], dist=1e-7, plane_co=(0, 0, z), plane_no=(0, 0, 1))
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
            continue  # an open chain: a tear in the bark, which the manifold check reports
        points = [Vector((v.co.x, v.co.y)) for v in corners]
        area = sum(a.x * b.y - b.x * a.y for a, b in zip(points, points[1:] + points[:1])) / 2
        if abs(area) < 1e-9:
            continue
        middle = sum(((a + b) * (a.x * b.y - b.x * a.y) for a, b in zip(points, points[1:] + points[:1])), Vector((0, 0))) / (6 * area)
        loops.append((math.sqrt(abs(area) / math.pi), middle, points))
    cut.free()
    return sorted(loops, key=lambda loop: -loop[0])


def flat_sides(points, min_share):
    """How many straight runs of a loop are at least `min_share` of the way round it."""
    edges = [b - a for a, b in zip(points, points[1:] + points[:1])]
    edges = [e for e in edges if e.length > 1e-7]
    # Join pieces of one straight run (a side cut across two faces).
    runs = []
    for edge in edges:
        if runs and runs[-1].angle(edge) < math.radians(3):
            runs[-1] = runs[-1] + edge
        else:
            runs.append(edge.copy())
    if len(runs) > 1 and runs[0].angle(runs[-1]) < math.radians(3):
        runs[0] = runs[0] + runs.pop()
    around = sum(run.length for run in runs)
    return sum(1 for run in runs if run.length >= min_share * around)


def stand_at(bm, material_index, floor, eye_height):
    """Where a trunk is at a player's eye height: the middle (x, y) of the widest loop of its slice there, or None."""
    bark = only(bm, material_index)
    loops = slice_at(bark, floor + eye_height)
    bark.free()
    return tuple(loops[0][1]) if loops else None


NOTHING = {"fork_m": None, "taper": None, "branches": 0, "branch_taper": None, "sides": None, "breast_m": None, "flare": None, "roots": 0, "lean_m": None, "root_fill": None, "root_ridges": 0, "root_curve": None, "limb_bend": None, "limbs": 0}


def inside(points, at):
    """Whether a point lies inside a closed loop, both in the plane."""
    within = False
    for a, b in zip(points, points[1:] + points[:1]):
        if (a.y > at.y) != (b.y > at.y) and at.x < a.x + (b.x - a.x) * (at.y - a.y) / (b.y - a.y):
            within = not within
    return within


def limb_bends(bark, floor):
    """The largest bend, in degrees, between successive stretches of each limb: one number per limb.

    The trunk and every limb is a closed tube of its own: rings of vertices, with one vertex closing each
    end. Counting edges from an end vertex gives the rings in order, and the line through their middles is
    the limb's path. The tube that stands on the ground is the trunk, and a tube of fewer than four sides is a twig.
    """
    found, seen = [], set()
    for start in bark.verts:
        if start in seen:
            continue
        piece, front = [start], [start]
        seen.add(start)
        while front:
            for edge in front.pop().link_edges:
                for other in edge.verts:
                    if other not in seen:
                        seen.add(other)
                        piece.append(other)
                        front.append(other)
        if min(v.co.z for v in piece) <= floor + 1e-4:
            continue
        end = max(piece, key=lambda v: len(v.link_edges))
        depth, layer, rings = {end: 0}, [end], []
        while layer:
            rings.append(layer)
            onward = []
            for vert in layer:
                for edge in vert.link_edges:
                    other = edge.other_vert(vert)
                    if other not in depth:
                        depth[other] = len(rings)
                        onward.append(other)
            layer = onward
        rings = [ring for ring in rings if len(ring) > 1]
        if len(rings) < 3 or min(len(ring) for ring in rings) < 4:
            continue
        middles = [sum((v.co for v in ring), Vector()) / len(ring) for ring in rings]
        stretches = [b - a for a, b in zip(middles, middles[1:])]
        found.append(max(math.degrees(a.angle(b)) for a, b in zip(stretches, stretches[1:])))
    return found


def measure(bark, conv):
    """What the slices say about a skeleton, as a dict; an entry is None when it cannot be measured."""
    rules = conv["skeleton"]
    if not bark.verts:
        return dict(NOTHING)
    top = max(v.co.z for v in bark.verts)
    floor = min(v.co.z for v in bark.verts)
    found = dict(NOTHING)
    breast = slice_at(bark, floor + rules["breast_height_m"])
    if not breast:
        return found
    found["breast_m"] = breast[0][0]
    found["sides"] = flat_sides(breast[0][2], rules["side_min_share"])

    step = rules["slice_step_m"]
    levels = [floor + rules["breast_height_m"] + step * i for i in range(1, int((top - floor - rules["breast_height_m"]) / step))]
    slices = [(z, slice_at(bark, z)) for z in levels]
    forked = [i for i, (_, loops) in enumerate(slices) if len(loops) >= 2]
    found["branches"] = max((len(loops) for _, loops in slices), default=0)
    if forked and forked[0] > 0:
        fork = slices[forked[0]][0]
        below = slices[forked[0] - 1][1]
        found["fork_m"] = fork - floor
        found["taper"] = below[0][0] / breast[0][0]

        def mean_radius(share):
            loops = slice_at(bark, fork + (top - fork) * share)
            return sum(radius for radius, _, _ in loops) / len(loops) if loops else None

        low, high = mean_radius(0.2), mean_radius(0.8)
        if low and high:
            found["branch_taper"] = high / low

        # Lean: from the trunk's middle just above its roots to its middle below the fork. The slice at
        # the ground will not do for the foot: roots reach further on one side than another, and its
        # middle sits up to 0.2 m off the trunk's, which made an upright trunk measure as leaning.
        foot = slice_at(bark, floor + rules["foot_height_m"])
        if foot:
            found["lean_m"] = (below[0][1] - foot[0][1]).length
    bends = limb_bends(bark, floor)
    found["limbs"], found["limb_bend"] = len(bends), max(bends, default=None)
    ground = slice_at(bark, floor + 0.02)
    if ground:
        _, middle, points = ground[0]
        reach = [(p - middle).length for p in points]
        found["flare"] = max(reach) / breast[0][0]
        # A root is a corner of the ground slice that stands well out from the trunk: further than
        # its neighbours on the loop, at least one and a half times the girth at breast height, and as
        # far as the circle the roots are told from a plinth on (below). A corner of the trunk that is
        # no root stands out from the ground either side of it too, now that the foot comes back to the
        # trunk between corners, and it is thick enough at the ground to pass the first two alone.
        ring = breast[0][0] + (max(reach) - breast[0][0]) * rules["root_ring_share"]
        tips = [i for i, r in enumerate(reach) if r >= max(1.5 * breast[0][0], ring) and r >= reach[i - 1] and r >= reach[(i + 1) % len(reach)]]
        # Two tips close together on the loop are the two corners of one root.
        roots = []
        for i in tips:
            if not any((points[i] - points[j]).length < 0.5 * reach[i] for j in roots):
                roots.append(i)
        found["roots"] = len(roots)
        # Roots or a plinth: walk a circle part of the way out from the trunk to the furthest tip. Roots are
        # ridges with ground between them, so little of the circle is inside the slice, in as many runs as there
        # are roots that reach it; a skirt with flat sides from tip to tip holds most of the circle, in one run.
        steps = 720
        radius = ring
        within = [inside(points, middle + Vector((math.cos(2 * math.pi * i / steps), math.sin(2 * math.pi * i / steps))) * radius) for i in range(steps)]
        found["root_fill"] = sum(within) / steps
        found["root_ridges"] = sum(1 for i in range(steps) if within[i] and not within[i - 1])
        # A curve into the ground, or a straight slope: how much of its reach beyond the trunk the foot
        # still has a little way up. A root that sweeps out into the ground has lost most of it by there.
        above = slice_at(bark, floor + 0.02 + rules["root_curve_height"] * breast[0][0])
        if above and max(reach) > breast[0][0]:
            found["root_curve"] = (max((p - above[0][1]).length for p in above[0][2]) - breast[0][0]) / (max(reach) - breast[0][0])
    return found
