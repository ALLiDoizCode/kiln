"""Measure one model file: counts, bounding box, materials, textures, UVs, texel density
and the Khronos glTF Validator's result.

As a library:

    from kiln.measure import measure, render_text
    report = measure("raw.glb", size=0.8)      # a plain dict; json.dumps(report) works
    print(render_text(report))

As a command:

    python3 -m kiln.measure <asset.glb> [--size METRES] [--json] [--no-validator]

Needs only the standard library. What each number means, exactly, is written down in
learn/reference/measuring-a-model.html; the short form is in the text output.
"""
import argparse
import json
import math
import os
import subprocess
import sys
from collections import Counter
from itertools import compress

from kiln.glb import GltfError, image_info, is_identity, load

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VALIDATOR = os.path.join(REPO_ROOT, ".tools", "gltf_validator")

# The UV square is sampled at the centres of a COVERAGE_GRID x COVERAGE_GRID grid of cells.
COVERAGE_GRID = 1024

# Material slots that can hold a texture, in glTF's own names.
_PBR_SLOTS = ("baseColorTexture", "metallicRoughnessTexture")
_MATERIAL_SLOTS = ("normalTexture", "occlusionTexture", "emissiveTexture")

_SEVERITIES = {0: "error", 1: "warning", 2: "info", 3: "hint"}


def measure(path, size=None, validator=DEFAULT_VALIDATOR):
    """Measure the model file at `path` and return the report as a plain dict.

    size       the asset's largest dimension in metres. Texel density is worked out as if
               the model had been scaled to it. Without it, the model is measured as stored.
    validator  path of the Khronos glTF Validator, or None to leave that part out.

    Raises kiln.glb.GltfError if the file cannot be decoded.
    """
    if size is not None and not size > 0:
        raise ValueError("size must be a positive number of metres")
    model = load(path)
    doc = model.json
    notes = []

    textures = _textures(model)
    materials = _materials(doc, textures, notes)
    surface = _Surface()
    meshes, totals = _meshes(model, materials, textures, surface, notes)

    box = surface.bounding_box()
    largest = box["largest_dimension"] if box else None
    factor = (size / largest) if (size is not None and largest) else None
    if size is not None and factor is None:
        notes.append("A size was given but the model has no extent, so nothing was scaled.")

    report = {
        "file": {
            "path": str(path),
            "bytes": os.path.getsize(path),
            "gltf_version": doc.get("asset", {}).get("version", str(model.version)),
            "generator": doc.get("asset", {}).get("generator"),
            "extensions_used": doc.get("extensionsUsed", []),
        },
        "totals": {
            "meshes": len(doc.get("meshes", [])),
            "triangles": totals["triangles"],
            "vertices": totals["vertices"],
            "materials": len(materials),
            "textures": len(textures),
        },
        "meshes": meshes,
        "bounding_box": box,
        "size": {"in_file": largest, "given": size, "scale_factor": factor},
        "materials": materials,
        "textures": textures,
        "surface": surface.surface_figures(),
        "uvs": surface.uv_figures(),
        "texel_density": surface.texel_density(factor or 1.0, size if factor else largest),
        "validator": run_validator(path, validator) if validator else None,
        "notes": notes,
    }
    return report


def surface(path):
    """Only the welded surface's figures of the model file at `path` (the "surface" part of
    measure's report): quicker, for a caller that wants nothing else."""
    model = load(path)
    notes = []
    textures = _textures(model)
    gathered = _Surface()
    _meshes(model, _materials(model.json, textures, notes), textures, gathered, notes,
            with_uvs=False)
    return gathered.surface_figures()


# ---- materials and textures ----------------------------------------------------------------

def _textures(model):
    """One entry per image in the file: format, pixel size and bytes."""
    out = []
    for index, image in enumerate(model.json.get("images", [])):
        data = model.image_bytes(index)
        if data is None:
            fmt, width, height, size = "missing", None, None, None
        else:
            fmt, width, height = image_info(data)
            size = len(data)
        name = image.get("name", "")
        if not name and not image.get("uri", "data:").startswith("data:"):
            name = image["uri"]
        out.append({"index": index, "name": name, "format": fmt, "width": width, "height": height, "bytes": size,
                    "used_as": []})
    return out


def _image_of_texture(doc, texture_index):
    """The image a glTF texture points at, looking through the WebP and Basis extensions."""
    texture = doc["textures"][texture_index]
    for extension in texture.get("extensions", {}).values():
        if isinstance(extension, dict) and "source" in extension and "source" not in texture:
            return extension["source"]
    return texture.get("source")


def _materials(doc, textures, notes):
    """One entry per material: its name and the image each of its texture slots uses."""
    out = []
    transformed = False
    second_set = False
    for index, material in enumerate(doc.get("materials", [])):
        slots = {}
        pbr = material.get("pbrMetallicRoughness", {})
        found = [(slot, pbr[slot]) for slot in _PBR_SLOTS if slot in pbr]
        found += [(slot, material[slot]) for slot in _MATERIAL_SLOTS if slot in material]
        for slot, info in found:
            image = _image_of_texture(doc, info["index"])
            slots[slot] = image
            transformed |= "KHR_texture_transform" in info.get("extensions", {})
            second_set |= info.get("texCoord", 0) != 0
            if image is not None and image < len(textures):
                use = f"{slot} of {material.get('name') or 'material ' + str(index)}"
                textures[image]["used_as"].append(use)
        out.append({"index": index, "name": material.get("name", ""), "textures": slots})
    if transformed:
        notes.append("A material uses KHR_texture_transform, which is ignored here: UV and "
                     "texel density figures are for the UVs as stored.")
    if second_set:
        notes.append("A material reads a texture through a UV set other than the first; "
                     "only the first set (TEXCOORD_0) is measured.")
    return out


# ---- geometry ------------------------------------------------------------------------------

def _triangle_corners(model, primitive, vertex_count, where, notes):
    """The primitive's triangles as three lists of vertex numbers, and whether it is indexed."""
    mode = primitive.get("mode", 4)
    indexed = "indices" in primitive
    if indexed:
        order, _ = model.accessor(primitive["indices"])
        if order and max(order) >= vertex_count:
            raise GltfError(f"{where}: an index points past the last vertex")
    else:
        order = range(vertex_count)
    if mode == 4:
        usable = len(order) - len(order) % 3
        return order[0:usable:3], order[1:usable:3], order[2:usable:3], indexed
    if mode == 5:  # triangle strip
        order = list(order)
        return order[:-2], order[1:-1], order[2:], indexed
    if mode == 6:  # triangle fan
        order = list(order)
        return [order[0]] * max(len(order) - 2, 0), order[1:-1], order[2:], indexed
    notes.append(f"{where} draws points or lines, not triangles; it adds no triangles.")
    return [], [], [], indexed


def _meshes(model, materials, textures, surface, notes, with_uvs=True):
    """Walk every mesh as the scene places it, feeding `surface`; return the per-mesh table.
    With `with_uvs` off the UVs are not read, so `surface` has no UV figures to give."""
    doc = model.json
    table = []
    for index, mesh in enumerate(doc.get("meshes", [])):
        primitives = []
        for p, primitive in enumerate(mesh.get("primitives", [])):
            for name in primitive.get("extensions", {}):
                if name in ("KHR_draco_mesh_compression", "EXT_meshopt_compression"):
                    raise GltfError(f"mesh {index} primitive {p} is compressed with {name}, "
                                    "which kiln does not decode")
            material = primitive.get("material")
            primitives.append({
                "index": p,
                "material": material,
                "material_name": materials[material]["name"] if material is not None else None,
                "triangles": 0,
                "vertices": 0,
                "indexed": "indices" in primitive,
                "has_uvs": "TEXCOORD_0" in primitive.get("attributes", {}),
                "attributes": sorted(primitive.get("attributes", {})),
            })
        table.append({"index": index, "name": mesh.get("name", ""), "placed": 0,
                      "triangles": 0, "vertices": 0, "primitives": primitives})

    totals = {"triangles": 0, "vertices": 0}
    for node, mesh_index, matrix in model.placed_meshes():
        entry = table[mesh_index]
        entry["placed"] += 1
        first_placement = entry["placed"] == 1
        for p, primitive in enumerate(doc["meshes"][mesh_index].get("primitives", [])):
            where = f"mesh {mesh_index} primitive {p}"
            attributes = primitive.get("attributes", {})
            if "POSITION" not in attributes:
                notes.append(f"{where} has no positions; it adds nothing.")
                continue
            flat, per = model.accessor(attributes["POSITION"])
            if per != 3:
                raise GltfError(f"{where}: POSITION is not three numbers per vertex")
            vertex_count = len(flat) // 3
            a, b, c, _ = _triangle_corners(model, primitive, vertex_count, where, notes)
            uv = None
            if with_uvs and "TEXCOORD_0" in attributes:
                uv_flat, uv_per = model.accessor(attributes["TEXCOORD_0"])
                if uv_per != 2 or len(uv_flat) // 2 != vertex_count:
                    raise GltfError(f"{where}: TEXCOORD_0 does not match the positions")
                uv = (uv_flat[0::2], uv_flat[1::2])
            texture = None
            material = primitive.get("material")
            if material is not None:
                image = materials[material]["textures"].get("baseColorTexture")
                if image is not None and image < len(textures):
                    texture = textures[image]
            surface.add(flat, matrix, a, b, c, uv, texture,
                        {"node": node, "mesh": mesh_index, "primitive": p, "material": material})
            totals["triangles"] += len(a)
            totals["vertices"] += vertex_count
            if first_placement:
                entry["primitives"][p]["triangles"] = len(a)
                entry["primitives"][p]["vertices"] = vertex_count
                entry["triangles"] += len(a)
                entry["vertices"] += vertex_count
    unplaced = [str(e["index"]) for e in table if e["placed"] == 0]
    if unplaced:
        notes.append("Not placed in the scene, so not counted or measured: mesh "
                     + ", ".join(unplaced) + ".")
    repeated = [str(e["index"]) for e in table if e["placed"] > 1]
    if repeated:
        notes.append("Placed more than once, and counted in the totals once per placement: "
                     "mesh " + ", ".join(repeated) + ".")
    return table, totals


class _Surface:
    """Everything the scene draws, gathered primitive by primitive in world space.

    Vertices are welded by position as they arrive: two vertices at exactly the same place
    are one point. Edges, pieces and UV islands are worked out on that welded surface.
    """

    def __init__(self):
        self.low = [math.inf] * 3
        self.high = [-math.inf] * 3
        self._points = {}        # world position -> point number
        self._used = set()       # points that are a corner of some triangle
        self._all_triangles = 0  # triangles with three distinct points, with UVs or without
        self._all_edges = []     # per side of those: which edge of the welded surface
        self._joins = []         # pairs of points that a triangle ties into one piece
        self._uv_points = {}     # (point number, u, v) -> number of that point-with-a-UV
        self._triangles = 0      # triangles that have UVs and three distinct points
        self._edges = []         # per triangle side: which edge of the welded surface
        self._uv_edges = []      # per triangle side: that edge together with its UVs
        self._owners = []        # per triangle side: which triangle
        self._uv_columns = []    # per primitive with UVs: the six UV lists of its triangles
        self._uv_area = 0.0
        self._uv_triangles_all = 0
        self._outside = 0
        self._zero_area = 0
        self._textured = []      # per textured primitive: figures for texel density

    def add(self, flat, matrix, a, b, c, uv, texture, where):
        xs, ys, zs = flat[0::3], flat[1::3], flat[2::3]
        if not is_identity(matrix):
            m = matrix
            xs, ys, zs = (
                [m[0] * x + m[1] * y + m[2] * z + m[3] for x, y, z in zip(xs, ys, zs)],
                [m[4] * x + m[5] * y + m[6] * z + m[7] for x, y, z in zip(xs, ys, zs)],
                [m[8] * x + m[9] * y + m[10] * z + m[11] for x, y, z in zip(xs, ys, zs)],
            )
        if xs:
            for axis, column in enumerate((xs, ys, zs)):
                self.low[axis] = min(self.low[axis], min(column))
                self.high[axis] = max(self.high[axis], max(column))
        if not a:
            return
        # Weld: give every vertex the number of the point at its position.
        points = self._points
        point_of = [points.setdefault(k, len(points)) for k in zip(xs, ys, zs)]
        pa, pb, pc = (list(map(point_of.__getitem__, idx)) for idx in (a, b, c))
        # A triangle with two corners at the same point has no area and no three edges.
        proper = [i != j and j != k and k != i for i, j, k in zip(pa, pb, pc)]
        whole = all(proper)
        sa, sb, sc = (pa, pb, pc) if whole else (list(compress(col, proper)) for col in (pa, pb, pc))
        self._all_triangles += len(sa)
        for p, q in ((sa, sb), (sb, sc), (sc, sa)):
            self._all_edges += [(i << 32 | j) if i < j else (j << 32 | i) for i, j in zip(p, q)]
        self._joins += zip(sa, sb)
        self._joins += zip(sb, sc)
        self._used.update(sa, sb, sc)
        if uv is None:
            return
        us, vs = uv

        # Surface area of every triangle, in the scene (square metres) and in the UV square.
        corners = [list(map(col.__getitem__, idx)) for idx in (a, b, c) for col in (xs, ys, zs)]
        areas = [0.5 * math.sqrt(((by - ay) * (cz - az) - (bz - az) * (cy - ay)) ** 2
                                 + ((bz - az) * (cx - ax) - (bx - ax) * (cz - az)) ** 2
                                 + ((bx - ax) * (cy - ay) - (by - ay) * (cx - ax)) ** 2)
                 for ax, ay, az, bx, by, bz, cx, cy, cz in zip(*corners)]
        del corners
        uv_corners = [list(map(col.__getitem__, idx)) for idx in (a, b, c) for col in (us, vs)]
        uv_areas = [0.5 * abs((bu - au) * (cv - av) - (cu - au) * (bv - av))
                    for au, av, bu, bv, cu, cv in zip(*uv_corners)]
        self._uv_area += math.fsum(uv_areas)
        self._uv_triangles_all += len(a)
        outside = [not (0.0 <= u <= 1.0 and 0.0 <= v <= 1.0) for u, v in zip(us, vs)]
        if any(outside):
            self._outside += sum(1 for i, j, k in zip(a, b, c)
                                 if outside[i] or outside[j] or outside[k])
        self._uv_columns.append(uv_corners)
        if texture is not None and texture["width"] and texture["height"]:
            self._textured.append((where, texture, areas, uv_areas))

        # Give every vertex the number of its point taken together with its UV.
        uv_points = self._uv_points
        uv_point_of = [uv_points.setdefault(k, len(uv_points)) for k in zip(point_of, us, vs)]
        qa, qb, qc = (list(map(uv_point_of.__getitem__, idx)) for idx in (a, b, c))
        pa, pb, pc = sa, sb, sc
        if not whole:
            self._zero_area += proper.count(False)
            qa, qb, qc = (list(compress(col, proper)) for col in (qa, qb, qc))
        first = self._triangles
        self._triangles += len(pa)
        owners = range(first, first + len(pa))
        for (p, q), (s, t) in (((pa, pb), (qa, qb)), ((pb, pc), (qb, qc)), ((pc, pa), (qc, qa))):
            self._edges += [(i << 32 | j) if i < j else (j << 32 | i) for i, j in zip(p, q)]
            self._uv_edges += [(i << 32 | j) if i < j else (j << 32 | i) for i, j in zip(s, t)]
            self._owners += owners

    def bounding_box(self):
        if self.low[0] == math.inf:
            return None
        dimensions = [h - l for l, h in zip(self.low, self.high)]
        return {"min": list(self.low), "max": list(self.high), "dimensions": dimensions,
                "largest_dimension": max(dimensions)}

    def surface_figures(self):
        """The welded surface, whether or not it has UVs: its edges, the open ones, and how
        many pieces it is in. Triangles that touch, even at one point, are in one piece."""
        if not self._all_triangles:
            return None
        sides_per_edge = Counter(self._all_edges)
        unused = len(self._points) - len(self._used)
        return {
            "triangles": self._all_triangles,
            "points": len(self._used),
            "edges": len(sides_per_edge),
            "open_edges": sum(1 for n in sides_per_edge.values() if n == 1),
            "pieces": _count_groups(len(self._points), self._joins) - unused,
        }

    def uv_figures(self):
        if not self._uv_triangles_all:
            return None
        edges, uv_edges, owners = self._edges, self._uv_edges, self._owners
        sides_per_edge = Counter(edges)
        edge_count = len(sides_per_edge)
        open_edges = sum(1 for n in sides_per_edge.values() if n == 1)
        del sides_per_edge
        # An edge is a seam when the triangles on it carry more than one version of its UVs.
        edge_of_version = dict(zip(uv_edges, edges))
        versions_per_edge = Counter(edge_of_version.values())
        seam_edges = sum(1 for n in versions_per_edge.values() if n > 1)
        del edge_of_version, versions_per_edge
        # Triangles that share an edge and agree on its UVs are in the same island.
        last_owner = dict(zip(uv_edges, owners))
        joins = [(t, other) for t, other in zip(owners, map(last_owner.__getitem__, uv_edges))
                 if t != other]
        del last_owner
        islands = _count_groups(self._triangles, joins)
        covered = _covered_cells(self._uv_columns, COVERAGE_GRID)
        return {
            "triangles": self._uv_triangles_all,
            "islands": islands,
            "edges": edge_count,
            "seam_edges": seam_edges,
            "open_edges": open_edges,
            "seam_share": seam_edges / edge_count if edge_count else None,
            "coverage": covered / (COVERAGE_GRID * COVERAGE_GRID),
            "coverage_grid": COVERAGE_GRID,
            "triangle_area_sum": self._uv_area,
            "triangles_outside_square": self._outside,
            "triangles_without_area": self._zero_area,
        }

    def texel_density(self, factor, size):
        """Texture pixels per metre of surface once the model is `factor` times as large."""
        if not self._textured:
            return None
        by_primitive = []
        samples = []
        total_pixels = 0.0
        total_area = 0.0
        for where, texture, areas, uv_areas in self._textured:
            pixels = texture["width"] * texture["height"]
            area = math.fsum(areas) * factor * factor
            uv_area = math.fsum(uv_areas)
            total_pixels += uv_area * pixels
            total_area += area
            scale = pixels / (factor * factor)
            samples += [(math.sqrt(u * scale / w), w) for w, u in zip(areas, uv_areas) if w > 0.0]
            by_primitive.append(dict(where, texture=texture["index"],
                                     texture_pixels=[texture["width"], texture["height"]],
                                     surface_area=area,
                                     pixels_per_metre=math.sqrt(uv_area * pixels / area)
                                     if area > 0.0 else None))
        if total_area <= 0.0:
            return None
        samples.sort()
        low, median, high = _weighted_percentiles(samples, (0.05, 0.5, 0.95))
        return {
            "size": size,
            "pixels_per_metre": math.sqrt(total_pixels / total_area),
            "p05": low, "median": median, "p95": high,
            "surface_area": total_area,
            "by_primitive": by_primitive,
        }


def _weighted_percentiles(sorted_samples, shares):
    """Values below which the given shares of the total weight lie. Samples: (value, weight)."""
    total = math.fsum(w for _, w in sorted_samples)
    targets = [s * total for s in shares]
    out = []
    running = 0.0
    n = 0
    for value, weight in sorted_samples:
        running += weight
        while n < len(targets) and running >= targets[n]:
            out.append(value)
            n += 1
        if n == len(targets):
            break
    while len(out) < len(shares):
        out.append(sorted_samples[-1][0])
    return out


def _count_groups(count, joins):
    """How many groups `count` things fall into once each pair in `joins` is tied together."""
    parent = list(range(count))
    groups = count
    for a, b in joins:
        while parent[a] != a:
            parent[a] = a = parent[parent[a]]
        while parent[b] != b:
            parent[b] = b = parent[parent[b]]
        if a != b:
            parent[a] = b
            groups -= 1
    return groups


def _covered_cells(uv_columns, grid):
    """How many cells of a grid x grid raster of the UV square have their centre inside
    at least one UV triangle. A cell under several triangles counts once."""
    rows = [bytearray(grid) for _ in range(grid)]
    ones = b"\x01" * grid
    ceil, floor = math.ceil, math.floor
    top = grid - 1
    for columns in uv_columns:
        # Move to grid units with cell centres on whole numbers.
        au, av, bu, bv, cu, cv = ([x * grid - 0.5 for x in col] for col in columns)
        for ax, ay, bx, by, cx, cy in zip(au, av, bu, bv, cu, cv):
            r0 = ceil(min(ay, by, cy))
            r1 = floor(max(ay, by, cy))
            if r1 < r0:
                continue
            c0 = ceil(min(ax, bx, cx))
            c1 = floor(max(ax, bx, cx))
            if c1 < c0 or r1 < 0 or r0 > top or c1 < 0 or c0 > top:
                continue
            if r0 < 0:
                r0 = 0
            if r1 > top:
                r1 = top
            for y in range(r0, r1 + 1):
                # Where the row through these cell centres enters and leaves the triangle.
                lo = math.inf
                hi = -math.inf
                for px, py, qx, qy in ((ax, ay, bx, by), (bx, by, cx, cy), (cx, cy, ax, ay)):
                    if py == qy:
                        if py == y:
                            lo = min(lo, px, qx)
                            hi = max(hi, px, qx)
                    elif py <= y <= qy or qy <= y <= py:
                        x = px + (y - py) * (qx - px) / (qy - py)
                        if x < lo:
                            lo = x
                        if x > hi:
                            hi = x
                if hi < lo:
                    continue
                x0 = max(ceil(lo), 0)
                x1 = min(floor(hi), top)
                if x1 >= x0:
                    rows[y][x0:x1 + 1] = ones[:x1 - x0 + 1]
    return sum(row.count(1) for row in rows)


# ---- the validator -------------------------------------------------------------------------

def run_validator(path, validator=DEFAULT_VALIDATOR):
    """Run the Khronos glTF Validator on the file and return its verdict as a dict."""
    if not os.path.isfile(validator):
        return {"ran": False,
                "reason": f"The Khronos glTF Validator is not installed at {validator}. "
                          "Run tools/install_tools.sh to install it."}
    try:
        done = subprocess.run([validator, "-o", str(path)], capture_output=True, text=True)
        result = json.loads(done.stdout)
    except (OSError, ValueError) as error:
        return {"ran": False, "reason": f"The Khronos glTF Validator did not give a result: {error}"}
    issues = result.get("issues", {})
    return {
        "ran": True,
        "version": result.get("validatorVersion"),
        "errors": issues.get("numErrors", 0),
        "warnings": issues.get("numWarnings", 0),
        "infos": issues.get("numInfos", 0),
        "hints": issues.get("numHints", 0),
        "truncated": issues.get("truncated", False),
        "messages": [{"severity": _SEVERITIES.get(m.get("severity"), str(m.get("severity"))),
                      "code": m.get("code"), "message": m.get("message"),
                      "pointer": m.get("pointer")}
                     for m in issues.get("messages", [])],
    }


# ---- text for reading ----------------------------------------------------------------------

def _n(value):
    return f"{value:,}"


def _m(value):
    return f"{value:.4g}"


def _percent(value):
    return f"{100 * value:.1f}%"


def render_text(report):
    """The report as text for a person, each figure with a line saying what it is."""
    out = []
    add = out.append
    f = report["file"]
    add(f"{f['path']}")
    add(f"  {_n(f['bytes'])} bytes, glTF {f['gltf_version']}, written by {f['generator'] or '?'}")
    if f["extensions_used"]:
        add(f"  extensions used: {', '.join(f['extensions_used'])}")

    t = report["totals"]
    add("")
    add("COUNTS")
    add(f"  triangles  {_n(t['triangles']):>12}   what the graphics card draws")
    add(f"  vertices   {_n(t['vertices']):>12}   rows stored in the file; a point on the surface is "
        "stored again wherever its normal or UV changes")
    for mesh in report["meshes"]:
        placed = "" if mesh["placed"] == 1 else f", placed {mesh['placed']} times"
        add(f"  mesh {mesh['index']} \"{mesh['name']}\": {_n(mesh['triangles'])} triangles, "
            f"{_n(mesh['vertices'])} vertices{placed}")
        for p in mesh["primitives"]:
            material = f"\"{p['material_name']}\"" if p["material"] is not None else "none"
            add(f"    primitive {p['index']}: {_n(p['triangles'])} triangles, "
                f"{_n(p['vertices'])} vertices, material {material}, "
                f"{'indexed' if p['indexed'] else 'not indexed'}, "
                f"{'has UVs' if p['has_uvs'] else 'no UVs'}")

    add("")
    add("BOUNDING BOX   the smallest upright box that holds the model as the scene places it, in metres")
    box = report["bounding_box"]
    if box is None:
        add("  none: the scene draws nothing")
    else:
        for axis, name in enumerate("xyz"):
            add(f"  {name}  {_m(box['min'][axis]):>10} to {_m(box['max'][axis]):<10} "
                f"= {_m(box['dimensions'][axis])} m")
        s = report["size"]
        add(f"  size in file  {_m(s['in_file'])} m   the largest of the three dimensions")
        if s["given"] is not None and s["scale_factor"] is not None:
            add(f"  size given    {_m(s['given'])} m   so the model must be scaled by "
                f"{_m(s['scale_factor'])}")

    add("")
    add(f"MATERIALS   {len(report['materials'])}; each one is a separate draw")
    for material in report["materials"]:
        slots = ", ".join(f"{slot} = texture {image}" for slot, image in material["textures"].items())
        add(f"  {material['index']}  \"{material['name']}\"  {slots or 'no textures'}")

    add("")
    add(f"TEXTURES   {len(report['textures'])} image(s) stored in the file")
    for texture in report["textures"]:
        pixels = (f"{texture['width']} x {texture['height']} pixels"
                  if texture["width"] else "pixel size unknown")
        size = f"{_n(texture['bytes'])} bytes" if texture["bytes"] is not None else "file missing"
        add(f"  {texture['index']}  \"{texture['name']}\"  {pixels}, {texture['format']}, {size}")
        for use in texture["used_as"]:
            add(f"       used as {use}")

    add("")
    add("SURFACE   the triangles joined wherever their corners are at the same place")
    surface = report["surface"]
    if surface is None:
        add("  none: the scene draws no triangle with three separate corners")
    else:
        add(f"  pieces      {_n(surface['pieces']):>10}   parts of the surface that do not touch "
            "each other")
        add(f"  open edges  {_n(surface['open_edges']):>10}   of {_n(surface['edges'])} edges; "
            "edges with a triangle on one side only: holes or rims in the surface")

    add("")
    add("UVS   how the surface is laid flat on the texture")
    uv = report["uvs"]
    if uv is None:
        add("  none: no triangle has UVs, so no texture can be placed on this model")
    else:
        add(f"  islands     {_n(uv['islands']):>10}   separate pieces the surface is cut into")
        add(f"  seam edges  {_n(uv['seam_edges']):>10}   of {_n(uv['edges'])} edges = "
            f"{_percent(uv['seam_share'])}; an edge where the surface is joined but the UVs are cut")
        add(f"  open edges  {_n(uv['open_edges']):>10}   edges with a triangle on one side only: "
            "holes or rims in the surface, not seams")
        add(f"  coverage    {_percent(uv['coverage']):>10}   share of the UV square under at least "
            "one triangle; the rest of the texture is unused")
        add(f"  area sum    {_percent(uv['triangle_area_sum']):>10}   UV triangle areas added up; "
            "more than coverage means triangles overlap or lie outside the square")
        if uv["triangles_outside_square"]:
            add(f"  {_n(uv['triangles_outside_square'])} triangle(s) reach outside the UV square")
        if uv["triangles_without_area"]:
            add(f"  {_n(uv['triangles_without_area'])} triangle(s) have two corners at the same "
                "point and are left out of the edge and island figures")

    add("")
    add("TEXEL DENSITY   base colour texture pixels per metre of surface")
    density = report["texel_density"]
    if density is None:
        add("  none: no triangle has both UVs and a base colour texture of known size")
    else:
        add(f"  at size {_m(density['size'])} m")
        add(f"  overall  {density['pixels_per_metre']:>10.1f} px/m   over the whole textured surface")
        add(f"  spread   {density['p05']:>10.1f} to {density['p95']:.1f} px/m   the middle 90% of the "
            f"surface; median {density['median']:.1f}")
        for p in density["by_primitive"]:
            value = (f"{p['pixels_per_metre']:.1f} px/m" if p["pixels_per_metre"] is not None
                     else "no surface area")
            add(f"  mesh {p['mesh']} primitive {p['primitive']}: {value} from texture "
                f"{p['texture']} ({p['texture_pixels'][0]} x {p['texture_pixels'][1]})")

    add("")
    add("KHRONOS GLTF VALIDATOR   whether the file obeys the glTF format")
    v = report["validator"]
    if v is None:
        add("  not run")
    elif not v["ran"]:
        add(f"  not run: {v['reason']}")
    else:
        add(f"  {v['errors']} errors, {v['warnings']} warnings, {v['infos']} infos, "
            f"{v['hints']} hints   (validator {v['version']})")
        for message in v["messages"]:
            add(f"  {message['severity']}: {message['message']}  [{message['code']} at "
                f"{message['pointer']}]")
        if v["truncated"]:
            add("  the validator cut its list of messages short")

    if report["notes"]:
        add("")
        add("NOTES")
        for note in report["notes"]:
            add(f"  {note}")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m kiln.measure",
        description="Measure one model file. Definitions: learn/reference/measuring-a-model.html")
    parser.add_argument("asset", help="the .glb to measure")
    parser.add_argument("--size", type=float, metavar="METRES",
                        help="the asset's largest dimension in metres; texel density is "
                             "worked out as if the model were scaled to it")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--no-validator", action="store_true",
                        help="do not run the Khronos glTF Validator")
    args = parser.parse_args(argv)
    if args.size is not None and not args.size > 0:
        parser.error("--size must be a positive number of metres")
    try:
        report = measure(args.asset, size=args.size,
                         validator=None if args.no_validator else DEFAULT_VALIDATOR)
    except (GltfError, OSError) as error:
        print(f"kiln.measure: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2) if args.json else render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
