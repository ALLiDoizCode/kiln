"""Shared helpers for the pipeline scripts.

Imported both by plain Python (lint scripts) and by Blender's Python, so the
module level uses the standard library only.
"""

import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
        path = self.out / "reports" / f"{gate}.json"
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
