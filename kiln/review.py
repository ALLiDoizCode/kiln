"""The shape review: the review pictures of a raw output, and a person's decision on them.

A run stops here, before the costly stages. Kiln renders the review pictures of the raw output
and waits; a person looks at them beside the reference image and approves or rejects:

    take_pictures()   renders the review pictures of the raw output into the asset's folder and
                      writes them into the asset record, with the decision still to be made.
    decide()          writes the decision into the asset record, with the pictures it was made on.
    state()           "pending", "approved" or "rejected", from an asset record.

Only an approved asset is built (kiln.run.build() asks state()). A rejected one stays as its
raw output and its record. Nothing here builds, and nothing generates again.

The pictures are rendered by `review_pictures`, the second program of crates/asset_view, in
Bevy and without a window. The set of views is data in that crate (src/views.rs) and is
described in learn/reference/review-pictures.html. The asset is shown at its size; the raw
output is only read. In the asset's folder:

    review/shape/<view>.png     one picture per view            (ignored by git)
    review/shape/index.html     the reference image beside them (ignored by git)

The final review will use the same view names under review/final/, so the two sets can be put
side by side, picture for picture.

In the asset record:

    "shape_review": {
      "decision": null, "approved" or "rejected"     null while it waits
      "note": text given with the decision, or null
      "decided_on": the day it was decided, as 2026-10-07, or null
      "pictures": {
        "view_set": the number of the set of views
        "closest_viewing_distance": metres, from the target profile when they were taken
        "picture_size": [width, height] in pixels
        "renderer": the program, its version, Bevy's version and the graphics card
        "views": [{"name", "path", "sha256"}, ...]
      }
    }

The checksums say which pictures a decision was made on: decide() refuses if a picture is
missing or is no longer the file that was rendered. They are checksums of pictures, not of
anything a build makes, and a build never renders: `kiln rebuild` copies this whole section.
"""
import datetime
import html
import json
import os
import shutil
import struct
import subprocess
import sys

from kiln import KilnError
from kiln.profile import PROFILES_DIR, load_profile
from kiln.record import check_file, read_record, sha256_of, write_record

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERER_SOURCE = os.path.join(REPO_ROOT, "crates", "asset_view", "src")
BUILD_RENDERER = "cargo build --release -p asset_view --bin review_pictures"
# How long the renderer may take, in seconds. It gives up by itself after 120 without a model.
RENDER_LIMIT = 300

SHAPE_PICTURES = os.path.join("review", "shape")
PAGE_NAME = "index.html"
DECISIONS = ("approved", "rejected")


# ---- the renderer --------------------------------------------------------------------------

def renderer_path():
    """Where the renderer is looked for: $KILN_REVIEW_RENDERER, or cargo's release folder."""
    given = os.environ.get("KILN_REVIEW_RENDERER")
    if given:
        return given
    target = os.environ.get("CARGO_TARGET_DIR") or os.path.join(REPO_ROOT, "target")
    return os.path.join(target, "release", "review_pictures")


def build_renderer():
    """Build the renderer with cargo; raises with cargo's last lines if that fails."""
    print(f"kiln: the review picture renderer is older than its source; building it "
          f"(`{BUILD_RENDERER}`)", file=sys.stderr)
    try:
        done = subprocess.run(BUILD_RENDERER.split(), cwd=REPO_ROOT, capture_output=True,
                              text=True)
    except OSError as error:
        raise KilnError(f"could not start `{BUILD_RENDERER}`: {error}") from None
    if done.returncode != 0:
        tail = "\n".join(done.stderr.strip().splitlines()[-8:])
        raise KilnError(f"`{BUILD_RENDERER}` failed:\n{tail}")


def require_renderer():
    """The path of the built renderer.

    A renderer that was never built is refused, with how to build it: the first build takes
    several minutes, and kiln does not start that by itself. One that is older than its source
    is built again here, which takes seconds; cargo goes by the same file times, so after a
    checkout that touched the source this is what `cargo build` would do anyway.
    """
    path = renderer_path()
    if not os.path.isfile(path):
        raise KilnError(f"the program that renders the review pictures is not built: {path} "
                        f"does not exist. Build it with `{BUILD_RENDERER}` (the first build "
                        "takes several minutes).")
    if not os.environ.get("KILN_REVIEW_RENDERER"):
        built = os.path.getmtime(path)
        sources = [os.path.join(folder, name) for folder, _, names in os.walk(RENDERER_SOURCE)
                   for name in names if name.endswith(".rs") and name != "main.rs"]
        if any(os.path.getmtime(source) > built for source in sources):
            build_renderer()
            os.utime(path)  # cargo leaves the file alone when only a time changed
    return path


def render_pictures(model, size, closest, out_dir):
    """Render the review pictures of a model file into `out_dir`: the real renderer.

    Returns what the renderer reports: {"view_set", "picture_size", "renderer", "views": [{"name",
    "file", "shows", ...}], ...}. Anything standing in for this in a test takes the same
    arguments, writes the files and returns the same.
    """
    command = [require_renderer(), model, "--size", repr(float(size)),
               "--closest", repr(float(closest)), "--out", out_dir]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=RENDER_LIMIT)
    except subprocess.TimeoutExpired:
        raise KilnError(f"the review pictures were not rendered in {RENDER_LIMIT} seconds") from None
    if done.returncode != 0:
        lines = [line for line in done.stderr.strip().splitlines() if " INFO " not in line]
        tail = "\n".join(lines[-8:])
        raise KilnError(f"the review pictures could not be rendered (exit status "
                        f"{done.returncode}):\n{tail}")
    try:
        return json.loads(done.stdout.strip().splitlines()[-1])
    except (IndexError, ValueError):
        raise KilnError("the renderer did not say what it wrote") from None


def png_size(path):
    """The (width, height) in pixels of a PNG file, or None if the file is not a PNG."""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", head[16:24])


# ---- taking the pictures -------------------------------------------------------------------

def state(record):
    """Where an asset's shape review stands: "pending", "approved" or "rejected"."""
    decision = (record.get("shape_review") or {}).get("decision")
    return decision if decision in DECISIONS else "pending"


def take_pictures(asset_dir, profiles_dir=PROFILES_DIR, renderer=None):
    """Render the review pictures of the asset's raw output and write them into its record,
    with the decision still to be made. Returns the record.

    Pictures already there are replaced. Once the shape review is decided this refuses: the
    decision was made on the pictures the record names.
    """
    record = read_record(asset_dir)
    if state(record) != "pending":
        raise KilnError(f"the shape review of '{record['name']}' is already decided "
                        f"({state(record)}): its review pictures are not rendered again")
    raw = check_file(asset_dir, record["raw_output"], "raw output")
    profile = load_profile(record["target_profile"]["name"], profiles_dir)
    closest = profile["closest_viewing_distance"]

    out_dir = os.path.join(asset_dir, SHAPE_PICTURES)
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)
    report = (renderer or render_pictures)(raw, record["size"], closest, out_dir)
    check_file(asset_dir, record["raw_output"], "raw output")  # the renderer only reads it

    views = []
    for view in report["views"]:
        path = os.path.join(out_dir, view["file"])
        if png_size(path) != tuple(report["picture_size"]):
            raise KilnError(f"the review picture '{view['name']}' was not written as a PNG of "
                            f"{report['picture_size'][0]} x {report['picture_size'][1]} "
                            f"pixels: {path}")
        views.append({"name": view["name"],
                      "path": "/".join((*SHAPE_PICTURES.split(os.sep), view["file"])),
                      "sha256": sha256_of(path)})
    if not views:
        raise KilnError("the renderer wrote no review pictures")
    record["shape_review"] = {
        "decision": None,
        "note": None,
        "decided_on": None,
        "pictures": {"view_set": report["view_set"],
                     "closest_viewing_distance": closest,
                     "picture_size": list(report["picture_size"]),
                     "renderer": report["renderer"],
                     "views": views},
    }
    write_page(asset_dir, record, report)
    write_record(asset_dir, record)
    return record


def write_page(asset_dir, record, report):
    """Write review/shape/index.html: the reference image beside the review pictures.

    A plain page a person opens in a browser. It is made from the record and can be thrown away.
    """
    text = html.escape
    reference = record.get("reference_image")
    if reference:
        beside = (f'<img src="../../{text(reference["path"], quote=True)}" alt="reference image">'
                  f'<p>{text(reference["path"])}</p>')
    else:
        beside = "<p>No reference image was given to this run.</p>"
    pictures = "\n".join(
        f'<figure id="{text(view["name"], quote=True)}"><img src="{text(view["file"], quote=True)}" '
        f'alt="{text(view["name"], quote=True)}"><figcaption><b>{text(view["name"])}</b> '
        f'{text(view.get("shows", ""))}</figcaption></figure>'
        for view in report["views"])
    name = text(record["name"])
    closest = record["shape_review"]["pictures"]["closest_viewing_distance"]
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Shape review: {name}</title>
<style>
  body {{ margin: 0; font: 15px/1.4 system-ui, sans-serif; background: #1d1f22; color: #ddd; }}
  header {{ padding: 12px 20px; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  code {{ background: #2c2f33; padding: 1px 5px; border-radius: 3px; }}
  main {{ display: grid; grid-template-columns: minmax(240px, 1fr) 2fr; gap: 20px; padding: 0 20px 20px; }}
  aside {{ position: sticky; top: 12px; align-self: start; }}
  img {{ max-width: 100%; display: block; }}
  figure {{ margin: 0 0 18px; }}
  figcaption {{ padding: 4px 0; }}
</style>
</head>
<body>
<header>
  <h1>Shape review: {name}</h1>
  <p>Raw output shown at size {record["size"]:g} m, target profile
  {text(record["target_profile"]["name"])}, closest viewing distance {closest:g} m.
  Decide with <code>python3 -m kiln review {name} --approve</code> or
  <code>python3 -m kiln review {name} --reject</code>.</p>
</header>
<main>
<aside>
<h2>Reference image</h2>
{beside}
</aside>
<section>
{pictures}
</section>
</main>
</body>
</html>
"""
    with open(os.path.join(asset_dir, SHAPE_PICTURES, PAGE_NAME), "w", encoding="utf-8") as f:
        f.write(page)


# ---- the decision --------------------------------------------------------------------------

def picture_problems(asset_dir, record):
    """What is wrong with the review pictures a record names, as lines; empty if nothing is."""
    pictures = (record.get("shape_review") or {}).get("pictures")
    if not pictures:
        return ["no review pictures have been rendered"]
    problems = []
    for view in pictures["views"]:
        path = os.path.join(asset_dir, *view["path"].split("/"))
        if not os.path.isfile(path):
            problems.append(f"the review picture '{view['name']}' is missing: {path}")
        elif sha256_of(path) != view["sha256"]:
            problems.append(f"the review picture '{view['name']}' is not the one that was "
                            f"rendered: {path}")
    return problems


def decide(asset_dir, decision, note=None, today=None):
    """Write a person's decision on the shape review into the asset record. Returns the record.

    The decision is made once, on pictures that are there to look at: it is refused when the
    review is already decided, or when a picture the record names is missing or has changed.
    `today` is the day written down, as text; it defaults to today's date here.
    """
    if decision not in DECISIONS:
        raise KilnError(f"a shape review is decided as {' or '.join(DECISIONS)}, not '{decision}'")
    record = read_record(asset_dir)
    if state(record) != "pending":
        was = record["shape_review"]
        raise KilnError(f"the shape review of '{record['name']}' was already decided: "
                        f"{was['decision']} on {was['decided_on']}")
    problems = picture_problems(asset_dir, record)
    if problems:
        raise KilnError(f"the shape review of '{record['name']}' cannot be decided: "
                        + "; ".join(problems) + f". Render them with `python3 -m kiln review "
                        f"{record['name']} --render`.")
    review = record["shape_review"]
    review["decision"] = decision
    review["note"] = note.strip() if note and note.strip() else None
    review["decided_on"] = today or datetime.date.today().isoformat()
    write_record(asset_dir, record)
    return record
