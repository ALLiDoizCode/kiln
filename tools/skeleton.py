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


NOTHING = {"fork_m": None, "taper": None, "branches": 0, "branch_taper": None, "sides": None, "breast_m": None, "flare": None, "roots": 0, "lean_m": None}


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
    ground = slice_at(bark, floor + 0.02)
    if ground:
        _, middle, points = ground[0]
        reach = [(p - middle).length for p in points]
        found["flare"] = max(reach) / breast[0][0]
        # A root is a corner of the ground slice that stands well out from the trunk: further than
        # its neighbours on the loop, and at least one and a half times the girth at breast height.
        tips = [i for i, r in enumerate(reach) if r >= 1.5 * breast[0][0] and r >= reach[i - 1] and r >= reach[(i + 1) % len(reach)]]
        # Two tips close together on the loop are the two corners of one root.
        roots = []
        for i in tips:
            if not any((points[i] - points[j]).length < 0.5 * reach[i] for j in roots):
                roots.append(i)
        found["roots"] = len(roots)
    return found
