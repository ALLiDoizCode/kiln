"""Shared helpers for the pipeline scripts.

Imported both by plain Python (lint scripts) and by Blender's Python, so the
module level uses the standard library only.
"""

import json
import os
import struct
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# Where a camera sits relative to the asset, by view name (+Z up, the asset's front faces -Y).
# The review renders and the shape checks both look from these.
VIEW_DIRECTIONS = {
    "front": (0, -1, 0),
    "right": (1, 0, 0),
    "back": (0, 1, 0),
    "left": (-1, 0, 0),
    "top": (0, 0, 1),
    "three_quarter": (1, -1, 0.7),
    "three_quarter_back": (-1, 1, 0.7),
}


def script_args():
    """Arguments after `--` when run under Blender, else all arguments."""
    argv = sys.argv
    return argv[argv.index("--") + 1 :] if "--" in argv else argv[1:]


def conventions():
    with open(ROOT / "conventions.toml", "rb") as f:
        return tomllib.load(f)


class Asset:
    """Where one asset's files live."""

    def __init__(self, name):
        self.name = name
        self.source = ROOT / "source" / name
        self.out = self.source / "out"
        self.blend = self.out / f"{name}.blend"
        self.glb = ROOT / "assets" / "models" / f"{name}.glb"
        self.manifest = ROOT / "assets" / "models" / f"{name}.manifest.json"

    def spec(self):
        with open(self.source / "spec.json") as f:
            return json.load(f)

    def report(self, gate):
        # tests/run.sh runs the tools on broken assets, and points their reports away from the gate's own.
        reports = Path(os.environ["KILN_REPORTS"]) / self.name if "KILN_REPORTS" in os.environ else self.out / "reports"
        path = reports / f"{gate}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


def gltf_bounds(bounds_m):
    """Blender bounds (+Z up, front -Y) as glTF bounds (+Y up, front +Z).

    The exporter maps (x, y, z) to (x, z, -y), so min and max swap on the
    negated axis.
    """
    (x0, y0, z0), (x1, y1, z1) = bounds_m["min"], bounds_m["max"]
    return {"min": [x0, z0, -y1], "max": [x1, z1, -y0]}


def linear_rgb(srgb_hex):
    """An sRGB hex colour ("#5a3820") as the linear RGB triple Blender and glTF store."""
    channels = (int(srgb_hex[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)


def share_textures(path):
    """Rewrite a GLB so that materials reading one image through one sampler share one texture.

    The exporter writes a texture per material even when they are the same
    image, and Bevy loads every texture as an image of its own: two materials
    on one painted texture (bark and leaf) would hold it in memory twice.
    """
    with open(path, "rb") as f:
        header = f.read(12)
        length, kind = struct.unpack("<I4s", f.read(8))
        gltf = json.loads(f.read(length))
        rest = f.read()
    textures = gltf.get("textures", [])
    first, kept, renumber = {}, [], {}
    for index, texture in enumerate(textures):
        key = json.dumps(texture, sort_keys=True)
        if key not in first:
            first[key] = len(kept)
            kept.append(texture)
        renumber[index] = first[key]
    if len(kept) == len(textures):
        return

    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                # Every reference to a texture is a textureInfo: an object with an "index", under a key ending in "Texture".
                if key.endswith("Texture") and isinstance(child, dict) and "index" in child:
                    child["index"] = renumber[child["index"]]
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(gltf.get("materials", []))
    gltf["textures"] = kept
    chunk = json.dumps(gltf, separators=(",", ":")).encode()
    chunk += b" " * (-len(chunk) % 4)
    with open(path, "wb") as f:
        f.write(header[:8] + struct.pack("<I", 12 + 8 + len(chunk) + len(rest)))
        f.write(struct.pack("<I4s", len(chunk), kind) + chunk + rest)


class Checks:
    """Collects named pass/fail results; the exit code is the gate."""

    def __init__(self, gate, subject):
        self.gate = gate
        self.subject = subject
        self.results = []

    def check(self, check_id, ok, detail=""):
        self.results.append({"id": check_id, "ok": bool(ok), "detail": "" if ok else str(detail)})
        return ok

    def failed(self):
        return [r for r in self.results if not r["ok"]]

    def finish(self, report_path=None):
        failed = self.failed()
        if report_path:
            with open(report_path, "w") as f:
                json.dump(
                    {"gate": self.gate, "subject": self.subject, "passed": not failed, "checks": self.results},
                    f,
                    indent=2,
                )
        for r in failed:
            print(f"FAIL {self.gate} {r['id']}: {r['detail']}")
        print(f"{self.gate}: {len(self.results) - len(failed)}/{len(self.results)} checks passed ({self.subject})")
        sys.exit(1 if failed else 0)
