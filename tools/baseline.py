"""Approval baselines: record the contact sheet the user approved, and detect drift from it.

    python tools/baseline.py approve <asset> [phase]   # only on the user's say-so
    python tools/baseline.py check <asset> [phase]     # gate L5b

`check` passes when nothing was ever approved (it says so), and fails when a
rebuilt sheet differs from the approved one by more than the threshold in
conventions.toml: the asset, a shared tool or the toolchain has changed what
the user signed off, and they need to look again.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date

from pipeline import Asset, conventions

command, name = sys.argv[1:3]
phase = sys.argv[3] if len(sys.argv) > 3 else "final"
asset = Asset(name)
review = asset.source / "review" / phase
sheet, approved, record = review / "sheet.png", review / "approved.png", review / "approved.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if command == "approve":
    shutil.copyfile(sheet, approved)
    record.write_text(
        json.dumps({"approved_on": date.today().isoformat(), "spec_sha256": sha256(asset.source / "spec.json"), "glb_sha256": sha256(asset.glb)}, indent=2)
        + "\n"
    )
    print(f"approved {name}/{phase}: {approved}")
elif command == "check":
    if not record.is_file():
        print(f"L5b-baseline: {name}/{phase} has NOT been approved by the user yet")
        sys.exit(0)
    stored = json.loads(record.read_text())
    changed = [
        what
        for what, path in (("spec", asset.source / "spec.json"), ("exported GLB", asset.glb))
        if sha256(path) != stored[f"{'spec' if what == 'spec' else 'glb'}_sha256"]
    ]
    # compare prints the normalised RMSE in parentheses on stderr and exits 1 on any difference.
    result = subprocess.run(
        ["magick", "compare", "-metric", "RMSE", str(sheet), str(approved), str(review / "baseline_diff.png")],
        capture_output=True, text=True,
    )
    try:
        rmse = float(result.stderr.split("(")[1].split(")")[0])
    except (IndexError, ValueError):
        rmse = 1.0  # different sizes, or unreadable: treat as a complete mismatch
    limit = conventions()["review"]["baseline_rmse"]
    if rmse > limit:
        print(f"FAIL L5b-baseline sheet.matches_approved: RMSE {rmse:.4f} > {limit}; changed since approval: {changed or 'only the render'}")
        print(f"the user must review {sheet} again; see {review / 'baseline_diff.png'}")
        sys.exit(1)
    note = f" (changed but visually within threshold: {changed})" if changed else ""
    print(f"L5b-baseline: {name}/{phase} matches the sheet approved on {stored['approved_on']}, RMSE {rmse:.4f}{note}")
else:
    sys.exit(__doc__)
