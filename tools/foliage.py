"""Foliage as the pipeline sees it (ADR 9, ADR 11): leaf pieces, the pads they form, and the palette.

A **piece** is a connected set of faces of the foliage material. A **pad** is
a set of pieces with no clear air between them: space is cut into cubes
`pad_gap_m` on a side, and two pieces belong to one pad when they touch the
same cube or two neighbouring cubes. Nothing here trusts a label from the
build script; pieces and pads are found from the mesh alone, so the paint and
the checks agree on them by construction, and crates/asset_smoke finds them
again, the same way, from the exported file.

Used by tools/paint.py (which piece gets which colour) and tools/validate.py
(what the foliage is made of). Runs under Blender's Python.
"""

import math

import numpy
from mathutils import Vector, geometry


def pieces_of(bm, material_index):
    """The foliage material's faces, grouped into pieces: sets of faces joined by shared vertices."""
    faces = [f for f in bm.faces if f.material_index == material_index]
    seen, pieces = set(), []
    for face in faces:
        if face in seen:
            continue
        piece, queue = [], [face]
        seen.add(face)
        while queue:
            current = queue.pop()
            piece.append(current)
            for vert in current.verts:
                for other in vert.link_faces:
                    if other not in seen and other.material_index == material_index:
                        seen.add(other)
                        queue.append(other)
        pieces.append(sorted(piece, key=lambda f: f.index))
    return pieces


def triangles_of(pieces):
    """(triangle corners as an N x 3 x 3 array, the piece each triangle belongs to)."""
    corners, owner = [], []
    for index, piece in enumerate(pieces):
        for face in piece:
            verts = [tuple(v.co) for v in face.verts]
            for i in range(1, len(verts) - 1):
                corners.append((verts[0], verts[i], verts[i + 1]))
                owner.append(index)
    return numpy.array(corners, dtype=numpy.float64).reshape(-1, 3, 3), numpy.array(owner, dtype=numpy.int64)


def pads_of(triangles, owner, piece_count, cell):
    """The pad each piece belongs to, as a list of pad numbers (0 is the pad with the most pieces)."""
    if not len(triangles):
        return []
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    longest = max(numpy.linalg.norm(b - a, axis=1).max(), numpy.linalg.norm(c - a, axis=1).max(), numpy.linalg.norm(c - b, axis=1).max())
    # Points over every triangle, no further apart than half a cube.
    steps = max(1, int(numpy.ceil(longest / (cell / 2))))
    weights = numpy.array([(i / steps, j / steps) for i in range(steps + 1) for j in range(steps + 1 - i)])
    points = a[:, None, :] + (b - a)[:, None, :] * weights[None, :, 0:1] + (c - a)[:, None, :] * weights[None, :, 1:2]
    cubes = numpy.floor(points / cell).astype(numpy.int64).reshape(-1, 3)
    owners = numpy.repeat(owner, len(weights))
    seen = numpy.unique(numpy.column_stack((cubes, owners)), axis=0)

    parent = list(range(piece_count))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first = {}
    for x, y, z, piece in seen.tolist():
        other = first.setdefault((x, y, z), piece)
        if other != piece:
            parent[find(piece)] = find(other)
    # Half of the 26 neighbours: each pair of cubes is met once.
    offsets = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if (dx, dy, dz) > (0, 0, 0)]
    for (x, y, z), piece in first.items():
        for dx, dy, dz in offsets:
            other = first.get((x + dx, y + dy, z + dz))
            if other is not None:
                parent[find(piece)] = find(other)

    roots = [find(i) for i in range(piece_count)]
    sizes = {}
    for root in roots:
        sizes[root] = sizes.get(root, 0) + 1
    # Largest first; ties by the lowest piece number, so the numbering never depends on chance.
    order = {root: number for number, root in enumerate(sorted(sizes, key=lambda root: (-sizes[root], root)))}
    return [order[root] for root in roots]


def heights_in_pads(pieces, pads):
    """How high each piece's middle sits among the middles of its own pad's pieces: 0 for the lowest, 1 for the highest."""
    middles = []
    for piece in pieces:
        zs = [v.co.z for face in piece for v in face.verts]
        middles.append(sum(zs) / len(zs))
    spans = {}
    for z, pad in zip(middles, pads):
        low, high = spans.get(pad, (float("inf"), float("-inf")))
        spans[pad] = (min(low, z), max(high, z))
    return [(z - spans[pad][0]) / max(spans[pad][1] - spans[pad][0], 1e-9) for z, pad in zip(middles, pads)]


def palette(material_rgb, under_tint, top_tint, shades, tones, variation):
    """The foliage colours, linear RGB, as rows of `tones` colours from the lowest shade to the highest.

    A shade is the material colour times a tint that runs from `under_tint`
    (the underside of a pad) to `top_tint` (its top). Within a shade the tones
    are evenly spaced from `variation` darker to `variation` lighter.
    """
    rows = []
    for shade in range(shades):
        share = shade / (shades - 1)
        tint = [u + (t - u) * share for u, t in zip(under_tint, top_tint)]
        row = []
        for tone in range(tones):
            lift = 1.0 + variation * (2 * tone / (tones - 1) - 1)
            row.append(tuple(min(1.0, m * t * lift) for m, t in zip(material_rgb, tint)))
        rows.append(row)
    return rows


def swatch_layout(texture_px, swatch_px, count):
    """Where the palette lies in the texture: (swatches per row, rows, height of the strip in texels).

    Swatches run in rows from the top-left corner. The strip is the rows plus
    one more swatch's height left empty under them, so that nothing painted
    beside the palette bleeds into it.
    """
    per_row = texture_px // swatch_px
    rows = -(-count // per_row)
    return per_row, rows, (rows + 1) * swatch_px


def swatch_uv(index, texture_px, swatch_px):
    """The middle of swatch `index`, as a UV with v = 1 at the top row of the image."""
    per_row = texture_px // swatch_px
    column, row = index % per_row, index // per_row
    return ((column + 0.5) * swatch_px / texture_px, 1.0 - (row + 0.5) * swatch_px / texture_px)


def piece_shape(piece):
    """One piece's shape: its length, how far from flat it is, its outline's corners, and where it points.

    Returns a dict: `length_m` (the longest distance between two corners),
    `off_plane_m` (the furthest a corner lies from the piece's plane),
    `sharpest_deg` (its most pointed corner), `notches` (corners of the outline
    that turn inward), `middle`, and `points` (unit vector from the middle to
    the sharpest corner).
    """
    verts = list({v for face in piece for v in face.verts})
    middle = sum((v.co for v in verts), Vector()) / len(verts)
    normal = sum((face.normal * face.calc_area() for face in piece), Vector()).normalized()
    shape = {
        "length_m": max((a.co - b.co).length for a in verts for b in verts),
        "off_plane_m": max(abs((v.co - middle).dot(normal)) for v in verts),
        "middle": middle,
        "sharpest_deg": 180.0,
        "notches": 0,
        "points": Vector((0, 0, 0)),
    }
    # The outline: edges with a face on one side only, walked in order.
    inside = set(piece)
    rim = [e for face in piece for e in face.edges if sum(1 for f in e.link_faces if f in inside) == 1]
    beside = {}
    for edge in rim:
        for vert in edge.verts:
            beside.setdefault(vert, []).append(edge)
    if not rim or any(len(edges) != 2 for edges in beside.values()):
        return shape  # not one simple outline: left as blunt and unnotched
    order, edge, vert = [rim[0].verts[0]], rim[0], rim[0].verts[1]
    while vert is not order[0]:
        order.append(vert)
        edge = next(e for e in beside[vert] if e is not edge)
        vert = edge.other_vert(vert)
    turns = []
    for before, at, after in zip(order[-1:] + order[:-1], order, order[1:] + order[:1]):
        a, b = before.co - at.co, after.co - at.co
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        turns.append((math.degrees(a.angle(b)), a.cross(b).dot(normal), at))
    # Most corners turn one way round; the few that turn the other way are notches.
    way = 1 if sum(1 for _, side, _ in turns if side > 0) * 2 >= len(turns) else -1
    corners = [(angle, at) for angle, side, at in turns if side * way > 0 and angle < 179]
    shape["notches"] = sum(1 for angle, side, _ in turns if side * way < 0 and angle < 179)
    if corners:
        angle, tip = min(corners, key=lambda corner: corner[0])
        shape["sharpest_deg"] = angle
        shape["points"] = (tip.co - middle).normalized()
    return shape


def view_axes(direction):
    """(toward the camera, across the view, up the view) for a view direction."""
    toward = Vector(direction).normalized()
    across = toward.cross(Vector((0, 0, 1)) if abs(toward.z) < 0.9 else Vector((0, 1, 0))).normalized()
    return toward, across, across.cross(toward)


def sky_and_bark(tree, faces, bark_index, canopy_points, direction, rays, above_z):
    """Looking from `direction` with parallel rays: (share of the canopy's outline that is sky, share of what is seen above `above_z` that is bark).

    The canopy's outline is the convex hull of the foliage as seen from there.
    A ray inside it that meets nothing shows sky. Of the rays that meet the
    tree above `above_z`, the bark share is those that meet bark first.
    """
    toward, across, up = view_axes(direction)
    flat = [(p.dot(across), p.dot(up)) for p in canopy_points]
    hull = [flat[i] for i in geometry.convex_hull_2d(flat)]
    xs, ys = [p[0] for p in hull], [p[1] for p in hull]
    cell = max(max(xs) - min(xs), max(ys) - min(ys)) / rays
    far = max(p.dot(toward) for p in canopy_points) + 10.0

    def inside(x, y):
        return all((bx - ax) * (y - ay) - (by - ay) * (x - ax) >= 0 for (ax, ay), (bx, by) in zip(hull, hull[1:] + hull[:1]))

    sky = total = bark = seen = 0
    y = min(ys) + cell / 2
    while y < max(ys):
        x = min(xs) + cell / 2
        while x < max(xs):
            if inside(x, y):
                total += 1
                point, _, index, _ = tree.ray_cast(across * x + up * y + toward * far, -toward)
                if index is None:
                    sky += 1
                elif point.z > above_z:
                    seen += 1
                    bark += faces[index].material_index == bark_index
            x += cell
        y += cell
    return sky / max(total, 1), bark / max(seen, 1)


def outline(tree, lo, hi, direction, rays):
    """What a shape covers seen from `direction`, as a grid of booleans over the box lo..hi."""
    toward, across, up = view_axes(direction)
    corners = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    xs, ys = [c.dot(across) for c in corners], [c.dot(up) for c in corners]
    cell = max(max(xs) - min(xs), max(ys) - min(ys)) / rays
    far = max(c.dot(toward) for c in corners) + 10.0
    grid = []
    y = min(ys) + cell / 2
    while y < max(ys):
        x = min(xs) + cell / 2
        row = []
        while x < max(xs):
            row.append(tree.ray_cast(across * x + up * y + toward * far, -toward)[2] is not None)
            x += cell
        grid.append(row)
        y += cell
    return numpy.array(grid, dtype=bool)


def difference(a, b):
    """How far two outlines differ: the share of what either covers that only one covers (0 the same, 1 nothing shared)."""
    either = numpy.logical_or(a, b).sum()
    return 1.0 - numpy.logical_and(a, b).sum() / max(either, 1)
