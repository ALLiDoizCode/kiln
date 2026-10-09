"""Write tiny .glb files from Python lists, so tests can know every answer by hand."""
import base64
import json
import struct
import zlib

FLOAT, U8, U16, U32, I8, I16 = 5126, 5121, 5123, 5125, 5120, 5122
_FORMATS = {FLOAT: "f", U8: "B", U16: "H", U32: "I", I8: "b", I16: "h"}
_TYPES = {1: "SCALAR", 2: "VEC2", 3: "VEC3", 4: "VEC4"}


def png(width, height):
    """A real, plain grey PNG of the given pixel size."""
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body)))
    rows = (b"\x00" + b"\x80" * (3 * width)) * height
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def jpeg():
    """A real JPEG, 8 x 8 pixels of one brown, as Blender 5.2.2 saved it."""
    return base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/4QAMTmVvR2VvAAAAWv/bAEMAAwICAwICAwMDAwQDAwQFCAUFBAQFCgcH"
        "BggMCgwMCwoLCw0OEhANDhEOCwsQFhARExQVFRUMDxcYFhQYEhQVFP/bAEMBAwQEBQQFCQUFCRQNCw0UFBQU"
        "FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFP/AABEIAAgACAMBIgACEQED"
        "EQH/xAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEF"
        "EiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZX"
        "WFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK"
        "0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/"
        "xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXx"
        "FxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeY"
        "mZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEA"
        "AhEDEQA/AOHooor5I+oP/9k=")


class GlbBuilder:
    def __init__(self):
        self.doc = {"asset": {"version": "2.0", "generator": "kiln tests"},
                    "buffers": [{}], "bufferViews": [], "accessors": [], "meshes": [],
                    "nodes": [], "scenes": [{"nodes": []}], "scene": 0}
        self.bin = bytearray()

    def view(self, data, stride=None):
        while len(self.bin) % 4:
            self.bin.append(0)
        entry = {"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(data)}
        if stride:
            entry["byteStride"] = stride
        self.bin += data
        self.doc["bufferViews"].append(entry)
        return len(self.doc["bufferViews"]) - 1

    def accessor(self, rows, component=FLOAT, normalized=False):
        """An accessor over `rows`: a list of numbers, or of equal-length tuples."""
        rows = [r if isinstance(r, (tuple, list)) else (r,) for r in rows]
        width = len(rows[0])
        data = b"".join(struct.pack("<" + _FORMATS[component] * width, *r) for r in rows)
        entry = {"bufferView": self.view(data), "componentType": component,
                 "count": len(rows), "type": _TYPES[width]}
        if normalized:
            entry["normalized"] = True
        if width == 3 and component == FLOAT:
            entry["min"] = [min(r[i] for r in rows) for i in range(3)]
            entry["max"] = [max(r[i] for r in rows) for i in range(3)]
        self.doc["accessors"].append(entry)
        return len(self.doc["accessors"]) - 1

    def image(self, data, mime="image/png", name="picture"):
        self.doc.setdefault("images", []).append(
            {"bufferView": self.view(data), "mimeType": mime, "name": name})
        return len(self.doc["images"]) - 1

    def material(self, name="m", base_colour_image=None, **more):
        entry = {"name": name}
        if base_colour_image is not None:
            self.doc.setdefault("textures", []).append({"source": base_colour_image})
            entry["pbrMetallicRoughness"] = {
                "baseColorTexture": {"index": len(self.doc["textures"]) - 1}}
        entry.update(more)
        self.doc.setdefault("materials", []).append(entry)
        return len(self.doc["materials"]) - 1

    def primitive(self, positions, uvs=None, indices=None, material=None,
                  index_component=U16, uv_component=FLOAT, mode=None, normals=None):
        attributes = {"POSITION": self.accessor(positions)}
        if normals is not None:
            attributes["NORMAL"] = self.accessor(normals)
        if uvs is not None:
            attributes["TEXCOORD_0"] = self.accessor(uvs, uv_component,
                                                     normalized=uv_component != FLOAT)
        entry = {"attributes": attributes}
        if indices is not None:
            entry["indices"] = self.accessor(indices, index_component)
        if material is not None:
            entry["material"] = material
        if mode is not None:
            entry["mode"] = mode
        return entry

    def mesh(self, primitives, name="mesh"):
        self.doc["meshes"].append({"name": name, "primitives": primitives})
        return len(self.doc["meshes"]) - 1

    def node(self, mesh=None, children=None, root=True, **transform):
        entry = dict(transform)
        if mesh is not None:
            entry["mesh"] = mesh
        if children:
            entry["children"] = children
            for child in children:
                if child in self.doc["scenes"][0]["nodes"]:
                    self.doc["scenes"][0]["nodes"].remove(child)
        self.doc["nodes"].append(entry)
        index = len(self.doc["nodes"]) - 1
        if root:
            self.doc["scenes"][0]["nodes"].append(index)
        return index

    def write(self, path):
        self.doc["buffers"][0]["byteLength"] = len(self.bin)
        text = json.dumps(self.doc).encode()
        text += b" " * (-len(text) % 4)
        body = bytes(self.bin) + b"\x00" * (-len(self.bin) % 4)
        with open(path, "wb") as f:
            f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(text) + 8 + len(body)))
            f.write(struct.pack("<I4s", len(text), b"JSON") + text)
            f.write(struct.pack("<I4s", len(body), b"BIN\x00") + body)
        return path


# ---- shapes with answers that can be worked out by hand ------------------------------------

def quad(width=1.0, height=1.0, u=(0.0, 1.0), v=(0.0, 1.0)):
    """A flat rectangle in the XY plane, two triangles, four vertices, one UV island."""
    positions = [(0, 0, 0), (width, 0, 0), (width, height, 0), (0, height, 0)]
    uvs = [(u[0], v[0]), (u[1], v[0]), (u[1], v[1]), (u[0], v[1])]
    return positions, uvs, [0, 1, 2, 0, 2, 3]


_CUBE_FACES = [  # four corners of each face of the unit cube, in order round the face
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],  # front
    [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],  # right
    [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)],  # back
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],  # left
    [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)],  # top
    [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],  # bottom
]


def cube_six_faces():
    """A unit cube whose six faces are six separate UV islands.

    Each face has its own four vertices and its own quarter-size cell of the UV square,
    laid three across and two up with gaps between (cells that touched would be joined
    wherever the faces also touch on the cube). 24 vertices, 12 triangles. Welded, the cube has 18 edges
    (12 cube edges and 6 face diagonals); all 12 cube edges are seams.
    """
    positions, uvs, indices = [], [], []
    for n, face in enumerate(_CUBE_FACES):
        col, row = n % 3, n // 3
        base = len(positions)
        positions += face
        uvs += [(col * 3 / 8 + du / 4, row / 2 + dv / 4) for du, dv in ((0, 0), (1, 0), (1, 1), (0, 1))]
        indices += [base, base + 1, base + 2, base, base + 2, base + 3]
    return positions, uvs, indices


def cube_cross():
    """A unit cube unfolded as a cross: one UV island.

    The cross is four cells across (left, front, right, back) with the top above the front
    and the bottom below it; each cell is a quarter of the UV square. 14 vertices, 12
    triangles. Five cube edges stay joined in the cross, so 7 of the 18 edges are seams.
    """
    lattice = {  # corner of the cross, in cells -> corner of the cube
        (0, 1): (0, 0, 0), (1, 1): (0, 0, 1), (2, 1): (1, 0, 1), (3, 1): (1, 0, 0), (4, 1): (0, 0, 0),
        (0, 2): (0, 1, 0), (1, 2): (0, 1, 1), (2, 2): (1, 1, 1), (3, 2): (1, 1, 0), (4, 2): (0, 1, 0),
        (1, 3): (0, 1, 0), (2, 3): (1, 1, 0),
        (1, 0): (0, 0, 0), (2, 0): (1, 0, 0),
    }
    order = list(lattice)
    positions = [lattice[k] for k in order]
    uvs = [(k[0] / 4, k[1] / 4) for k in order]
    indices = []
    for col, row in ((0, 1), (1, 1), (2, 1), (3, 1), (1, 2), (1, 0)):
        a, b, c, d = (order.index(k) for k in
                      ((col, row), (col + 1, row), (col + 1, row + 1), (col, row + 1)))
        indices += [a, b, c, a, c, d]
    return positions, uvs, indices


def ball(rows=30, columns=60, radius=1.0):
    """A closed ball of latitude and longitude lines, with UVs in one island: the map of the
    world, cut down one line from pole to pole. Each pole is a row of `columns` vertices at
    one place, so welded the ball has (rows - 1) * columns + 2 points; it has
    2 * columns * (rows - 1) triangles, 3,480 as given.
    """
    import math
    positions, uvs, indices = [], [], []
    for row in range(rows + 1):
        across = math.pi * row / rows
        for column in range(columns + 1):
            around = 2.0 * math.pi * (column % columns) / columns
            positions.append((radius * math.sin(across) * math.cos(around),
                              radius * math.cos(across),
                              radius * math.sin(across) * math.sin(around)))
            uvs.append((column / columns, 1.0 - row / rows))
    for row in range(rows):
        for column in range(columns):
            a = row * (columns + 1) + column
            b, c, d = a + 1, a + columns + 2, a + columns + 1
            if row > 0:
                indices += [a, b, c]
            if row < rows - 1:
                indices += [a, c, d]
    return positions, uvs, indices
