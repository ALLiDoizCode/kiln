"""Read a glTF model file (.glb, or .gltf with its buffers) with the standard library only.

This is the one place in kiln that knows the file layout. It gives back plain Python lists:

    model = load("crate.glb")
    model.json                      the file's JSON description, as a dict
    model.accessor(3)               -> (flat list of numbers, numbers per element)
    model.placed_meshes()           -> [(node index, mesh index, 3x4 matrix), ...]
    model.image_bytes(0)            -> the encoded image, or None if it is not in reach
    image_info(data)                -> (format, width, height)

Anything the reader cannot decode raises GltfError with a message that says what and where.
"""
import array
import base64
import json
import os
import struct
import sys
import urllib.parse


class GltfError(Exception):
    """The file is not a glTF file this reader can decode."""


# glTF componentType -> (array typecode, bytes, largest value when used as a normalised integer)
_COMPONENTS = {
    5120: ("b", 1, 127.0),
    5121: ("B", 1, 255.0),
    5122: ("h", 2, 32767.0),
    5123: ("H", 2, 65535.0),
    5125: ("I", 4, 4294967295.0),
    5126: ("f", 4, None),
}
_ELEMENT_SIZES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT2": 4, "MAT3": 9, "MAT4": 16}

# Extensions that store mesh data in a form this reader does not decode.
_COMPRESSED = ("KHR_draco_mesh_compression", "EXT_meshopt_compression")

IDENTITY = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)


class Gltf:
    def __init__(self, path, document, binary_chunk, version):
        self.path = path
        self.json = document
        self.version = version
        self._binary_chunk = binary_chunk
        self._buffers = {}

    # ---- bytes -------------------------------------------------------------------------

    def _uri_bytes(self, uri):
        """Bytes behind a URI: a data: URI, or a file beside the model. None if out of reach."""
        if uri.startswith("data:"):
            header, _, payload = uri.partition(",")
            if header.endswith(";base64"):
                return base64.b64decode(payload)
            return urllib.parse.unquote_to_bytes(payload)
        target = os.path.join(os.path.dirname(self.path), urllib.parse.unquote(uri))
        if not os.path.isfile(target):
            return None
        with open(target, "rb") as f:
            return f.read()

    def buffer(self, index):
        if index not in self._buffers:
            entry = self.json["buffers"][index]
            if "uri" in entry:
                data = self._uri_bytes(entry["uri"])
                if data is None:
                    raise GltfError(f"buffer {index}: cannot read {entry['uri']!r}")
            elif index == 0 and self._binary_chunk is not None:
                data = self._binary_chunk
            else:
                raise GltfError(f"buffer {index}: has no uri and the file has no binary chunk")
            self._buffers[index] = data
        return self._buffers[index]

    def view_bytes(self, index):
        view = self.json["bufferViews"][index]
        start = view.get("byteOffset", 0)
        return memoryview(self.buffer(view["buffer"]))[start:start + view["byteLength"]]

    def _read_numbers(self, view_index, byte_offset, component_type, per_element, count):
        """`count` elements of `per_element` numbers from a buffer view, as one flat list."""
        if component_type not in _COMPONENTS:
            raise GltfError(f"unknown accessor componentType {component_type}")
        typecode, size, _ = _COMPONENTS[component_type]
        element_bytes = size * per_element
        view = self.json["bufferViews"][view_index]
        stride = view.get("byteStride") or element_bytes
        data = self.view_bytes(view_index)
        if count and byte_offset + stride * (count - 1) + element_bytes > len(data):
            raise GltfError(f"bufferView {view_index}: too short for {count} elements")
        if stride == element_bytes:
            raw = data[byte_offset:byte_offset + element_bytes * count]
        else:  # interleaved: pick each element out of its row
            raw = b"".join(data[o:o + element_bytes]
                           for o in range(byte_offset, byte_offset + stride * count, stride))
        numbers = array.array(typecode)
        numbers.frombytes(raw)
        if sys.byteorder == "big":
            numbers.byteswap()
        return numbers.tolist()

    def accessor(self, index):
        """The accessor's values as (flat list, numbers per element).

        Normalised integers are turned into floats; sparse accessors are filled in.
        """
        acc = self.json["accessors"][index]
        if acc["type"] not in _ELEMENT_SIZES:
            raise GltfError(f"accessor {index}: unknown type {acc['type']!r}")
        per_element = _ELEMENT_SIZES[acc["type"]]
        count = acc["count"]
        component_type = acc["componentType"]
        if "bufferView" in acc:
            values = self._read_numbers(acc["bufferView"], acc.get("byteOffset", 0),
                                        component_type, per_element, count)
        else:
            values = [0] * (per_element * count)
        if "sparse" in acc:
            sparse = acc["sparse"]
            where = self._read_numbers(sparse["indices"]["bufferView"],
                                       sparse["indices"].get("byteOffset", 0),
                                       sparse["indices"]["componentType"], 1, sparse["count"])
            what = self._read_numbers(sparse["values"]["bufferView"],
                                      sparse["values"].get("byteOffset", 0),
                                      component_type, per_element, sparse["count"])
            for n, element in enumerate(where):
                if element >= count:
                    raise GltfError(f"accessor {index}: sparse index {element} out of range")
                values[element * per_element:(element + 1) * per_element] = \
                    what[n * per_element:(n + 1) * per_element]
        if acc.get("normalized") and component_type != 5126:
            largest = _COMPONENTS[component_type][2]
            values = [max(v / largest, -1.0) for v in values]
        return values, per_element

    def image_bytes(self, index):
        """The encoded bytes of an image, or None if it is a separate file that is missing."""
        image = self.json["images"][index]
        if "bufferView" in image:
            return bytes(self.view_bytes(image["bufferView"]))
        if "uri" in image:
            return self._uri_bytes(image["uri"])
        return None

    # ---- the scene ---------------------------------------------------------------------

    def placed_meshes(self):
        """Every mesh as the scene places it: [(node index, mesh index, matrix), ...].

        The matrix is the node's world transform as 12 numbers, three rows of four. A mesh
        used by two nodes appears twice. The scene is the file's default scene, or its
        first, or failing that every node that has no parent.
        """
        nodes = self.json.get("nodes", [])
        scenes = self.json.get("scenes", [])
        if scenes:
            roots = scenes[self.json.get("scene", 0)].get("nodes", [])
        else:
            children = {c for node in nodes for c in node.get("children", [])}
            roots = [i for i in range(len(nodes)) if i not in children]
        placed = []
        stack = [(root, IDENTITY, 0) for root in reversed(roots)]
        while stack:
            index, parent, depth = stack.pop()
            if depth > len(nodes):
                raise GltfError("the node hierarchy contains a loop")
            node = nodes[index]
            world = _multiply(parent, _local_matrix(node))
            if "mesh" in node:
                placed.append((index, node["mesh"], world))
            for child in reversed(node.get("children", [])):
                stack.append((child, world, depth + 1))
        return placed


def load(path):
    """Open a .glb (or a .gltf) and return a Gltf. Raises GltfError if it is neither."""
    with open(path, "rb") as f:
        data = f.read()
    binary_chunk = None
    if data[:4] == b"glTF":
        if len(data) < 20:
            raise GltfError(f"{path}: file is cut short")
        _, version, _length = struct.unpack_from("<4sII", data, 0)
        offset, text = 12, None
        while offset + 8 <= len(data):
            chunk_length, chunk_type = struct.unpack_from("<I4s", data, offset)
            body = data[offset + 8:offset + 8 + chunk_length]
            if chunk_type == b"JSON" and text is None:
                text = body
            elif chunk_type == b"BIN\x00" and binary_chunk is None:
                binary_chunk = body
            offset += 8 + chunk_length
        if text is None:
            raise GltfError(f"{path}: no JSON chunk")
    elif data.lstrip()[:1] == b"{":
        version, text = 2, data
    else:
        raise GltfError(f"{path}: not a glTF file")
    try:
        document = json.loads(text)
    except ValueError as error:
        raise GltfError(f"{path}: the JSON part does not parse: {error}") from None
    for name in _COMPRESSED:
        if name in document.get("extensionsRequired", []):
            raise GltfError(f"{path}: mesh data is compressed with {name}, which kiln does "
                            "not decode; export the file without mesh compression")
    return Gltf(path, document, binary_chunk, version)


# ---- transforms ----------------------------------------------------------------------------

def _local_matrix(node):
    """A node's own transform as three rows of four."""
    if "matrix" in node:
        m = node["matrix"]  # glTF stores columns first
        return (m[0], m[4], m[8], m[12], m[1], m[5], m[9], m[13], m[2], m[6], m[10], m[14])
    tx, ty, tz = node.get("translation", (0.0, 0.0, 0.0))
    x, y, z, w = node.get("rotation", (0.0, 0.0, 0.0, 1.0))
    sx, sy, sz = node.get("scale", (1.0, 1.0, 1.0))
    return (
        (1 - 2 * (y * y + z * z)) * sx, (2 * (x * y - z * w)) * sy, (2 * (x * z + y * w)) * sz, tx,
        (2 * (x * y + z * w)) * sx, (1 - 2 * (x * x + z * z)) * sy, (2 * (y * z - x * w)) * sz, ty,
        (2 * (x * z - y * w)) * sx, (2 * (y * z + x * w)) * sy, (1 - 2 * (x * x + y * y)) * sz, tz,
    )


def _multiply(a, b):
    """a then-applied-after b, both three rows of four (the fourth row is 0 0 0 1)."""
    if a is IDENTITY:
        return tuple(float(v) for v in b)
    rows = []
    for r in (0, 4, 8):
        a0, a1, a2, a3 = a[r], a[r + 1], a[r + 2], a[r + 3]
        rows += [a0 * b[0] + a1 * b[4] + a2 * b[8],
                 a0 * b[1] + a1 * b[5] + a2 * b[9],
                 a0 * b[2] + a1 * b[6] + a2 * b[10],
                 a0 * b[3] + a1 * b[7] + a2 * b[11] + a3]
    return tuple(rows)


def is_identity(matrix):
    return tuple(matrix) == IDENTITY


# ---- images --------------------------------------------------------------------------------

def image_info(data):
    """(format, width, height) read from an encoded image's header.

    Knows PNG, JPEG, WebP and KTX2. Returns ("unknown", None, None) for anything else.
    """
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        width, height = struct.unpack_from(">II", data, 16)
        return "png", width, height
    if data[:2] == b"\xff\xd8":
        size = _jpeg_size(data)
        return ("jpeg",) + (size or (None, None))
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        size = _webp_size(data)
        return ("webp",) + (size or (None, None))
    if data[:12] == b"\xabKTX 20\xbb\r\n\x1a\n" and len(data) >= 28:
        width, height = struct.unpack_from("<II", data, 20)
        return "ktx2", width, height
    return "unknown", None, None


def _jpeg_size(data):
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            return None
        marker = data[offset + 1]
        if marker == 0xFF:  # padding
            offset += 1
            continue
        if marker in (0x01,) or 0xD0 <= marker <= 0xD9:  # markers with no length
            offset += 2
            continue
        (length,) = struct.unpack_from(">H", data, offset + 2)
        # SOF0..SOF15 hold the picture size, except DHT (C4), JPG (C8) and DAC (CC).
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if offset + 9 > len(data):
                return None
            height, width = struct.unpack_from(">HH", data, offset + 5)
            return width, height
        offset += 2 + length
    return None


def _webp_size(data):
    kind = data[12:16]
    if kind == b"VP8X" and len(data) >= 30:
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if kind == b"VP8L" and len(data) >= 25:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if kind == b"VP8 " and len(data) >= 30:
        width, height = struct.unpack_from("<HH", data, 26)
        return width & 0x3FFF, height & 0x3FFF
    return None
