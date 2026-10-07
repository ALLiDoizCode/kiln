"""A run: from a model file to an asset, which is the finished model plus its asset record.

    python3 -m kiln run --model rock.glb --size 0.8 --profile pit \\
        --licence "CC0 1.0" --source "modelled by J. Green" [--reference-image rock.png]
    python3 -m kiln review rock --approve          (or --reject)

A run stops once, for the shape review, and a person's decision takes it further:

    take_in()                copies the model file into the store as the raw output and writes
                             the asset record with what only the caller knows: name, size,
                             profile, licence, source, and the reference image if there is one.
    review.take_pictures()   renders the review pictures of the raw output. The run stops here.
    review.decide()          writes the person's decision into the record. A rejected run ends:
                             the raw output and the record stay, and nothing is built.
    build()                  for an approved asset only: reads the asset record, takes the raw
                             output through STAGES in a work area, measures the result, makes
                             the profile's checks, and writes the finished model and the
                             completed record. It needs nothing but the asset's folder.

Every run stops for the shape review, whatever the model file's source: a bought or
hand-modelled model enters at the stage after generation, and that stage is the shape review.
With no reference image the person judges the raw output on its own.

The store holds one folder per asset:

    <store>/<name>/asset_record.json     the asset record               (in git)
    <store>/<name>/reference_image.png   the reference image, if given  (in git)
    <store>/<name>/raw_output.glb        the raw output, never changed  (ignored by git)
    <store>/<name>/review/shape/         the review pictures            (ignored by git)
    <store>/<name>/<name>.glb            the finished model             (ignored by git)

A failed check stops the run: the record is written with every check's result and
"passed": false, no finished model is left in the folder, and the raw output is kept.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

from kiln import KilnError, review
from kiln.checks import describe, run_checks
from kiln.glb import GltfError, load
from kiln.measure import DEFAULT_VALIDATOR, measure
from kiln.profile import PROFILES_DIR, load_profile
from kiln.record import check_file, file_entry, read_record, record_path, write_record

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(REPO_ROOT, "assets")
BLENDER = os.path.join(REPO_ROOT, ".tools", "blender", "blender")
BL = os.path.join(REPO_ROOT, "tools", "bl")
BLENDER_SCRIPTS = os.path.join(REPO_ROOT, "kiln", "blender_scripts")

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
# The kinds of picture a reference image may be: ones a browser shows.
REFERENCE_IMAGE_KINDS = (".png", ".jpg", ".jpeg", ".webp")


# ---- stages --------------------------------------------------------------------------------
# A stage is a function (source, work, record, profile) -> (path of the model it wrote, facts).
# It reads `source`, writes only inside the folder `work`, and returns a small dict of facts
# worth keeping in the asset record. STAGES is the order they run in; each one's output is
# the next one's source, and the last one's output is the finished model.

def run_blender(script, *args):
    """Run one of kiln's Blender scripts in the pinned Blender; raise with its output if it fails."""
    done = subprocess.run([BL, os.path.join(BLENDER_SCRIPTS, script), *map(str, args)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        tail = "\n".join((done.stdout + done.stderr).strip().splitlines()[-15:])
        raise KilnError(f"the Blender script {script} failed:\n{tail}")


def scale_to_size(source, work, record, profile):
    """Scale the model so its largest dimension is the run's size. See the script for how."""
    target = os.path.join(work, "scale_to_size.glb")
    result = os.path.join(work, "scale_to_size.json")
    run_blender("scale_to_size.py", source, target, repr(record["size"]), result)
    with open(result, encoding="utf-8") as f:
        return target, {"scale_factor": json.load(f)["factor"]}


STAGES = (scale_to_size,)


# ---- tools ---------------------------------------------------------------------------------

def require_tools():
    for path, what in ((BLENDER, "Blender"), (DEFAULT_VALIDATOR, "the Khronos glTF Validator")):
        if not os.path.exists(path):
            raise KilnError(f"{what} is not installed at {path}. "
                            "Run tools/install_tools.sh to install the pinned tools.")


def blender_version():
    done = subprocess.run([BLENDER, "--version"], capture_output=True, text=True)
    first = (done.stdout.strip().splitlines() or [""])[0]
    if done.returncode != 0 or not first.startswith("Blender "):
        raise KilnError(f"could not read the version of the Blender at {BLENDER}")
    return first[len("Blender "):]


# ---- the parts of a run --------------------------------------------------------------------

def take_in(model, size, profile, licence, source, name=None, store=STORE,
            profiles_dir=PROFILES_DIR, reference_image=None):
    """Start an asset from a model file: copy it into the store as the raw output and write
    the asset record with what the caller gave. Returns the asset's folder.

    A reference image, if given, is copied beside the record as reference_image.<its kind>.

    Nothing is written unless every input is usable. An asset of the same name is never
    overwritten: the caller removes its folder first if it is to be made again.
    """
    if not size > 0:  # also catches NaN
        raise KilnError(f"the size must be a positive number of metres, not {size}")
    for value, what in ((licence, "licence"), (source, "source")):
        if not value or not value.strip():
            raise KilnError(f"the {what} must be given: kiln cannot know it")
    if not os.path.isfile(model):
        raise KilnError(f"there is no model file at {model}")
    extension = os.path.splitext(model)[1].lower()
    if extension != ".glb":
        raise KilnError(f"the model file must be a .glb, a glTF model in one file: {model}")
    try:
        load(model)
    except (GltfError, OSError) as error:
        raise KilnError(f"the model file cannot be read: {error}") from None
    if name is None:
        name = os.path.splitext(os.path.basename(model))[0]
    if not _NAME.match(name):
        raise KilnError(f"'{name}' cannot be an asset's name: use letters, digits, - and _ "
                        "(give one with --name)")
    if reference_image is not None:
        if not os.path.isfile(reference_image):
            raise KilnError(f"there is no reference image at {reference_image}")
        image_kind = os.path.splitext(reference_image)[1].lower()
        if image_kind not in REFERENCE_IMAGE_KINDS:
            raise KilnError(f"the reference image must be one of {', '.join(REFERENCE_IMAGE_KINDS)}"
                            f": {reference_image}")
    load_profile(profile, profiles_dir)
    require_tools()
    review.require_renderer()
    asset_dir = os.path.join(store, name)
    if os.path.lexists(asset_dir):
        raise KilnError(f"an asset named '{name}' is already in the store: {asset_dir}. "
                        "Kiln does not overwrite an asset; remove that folder to make it "
                        "again, or give another name with --name.")

    os.makedirs(asset_dir)
    raw = os.path.join(asset_dir, "raw_output" + extension)
    shutil.copyfile(model, raw)
    os.chmod(raw, 0o444)  # no stage may write to the raw output
    kept_image = None
    if reference_image is not None:
        kept_image = os.path.join(asset_dir, "reference_image" + image_kind)
        shutil.copyfile(reference_image, kept_image)
    write_record(asset_dir, {
        "name": name,
        "licence": licence.strip(),
        "source": source.strip(),
        "size": float(size),
        "target_profile": {"name": profile, "sha256": None},
        "reference_image": file_entry(kept_image) if kept_image else None,
        "raw_output": file_entry(raw),
        "shape_review": {"decision": None, "note": None, "decided_on": None, "pictures": None},
        "tools": None,
        "stages": None,
        "checks": None,
        "passed": None,
        "model": None,
    })
    return asset_dir


def build(asset_dir, profiles_dir=PROFILES_DIR, stages=None):
    """Make the asset in `asset_dir` from its raw output, reading only its asset record and
    the target profile the record names. Returns the completed record, which is also written.

    The same raw output, size and profile give the same finished model, byte for byte. The
    record's shape review is copied as it is found, so the record repeats too.

    Only an asset whose shape review is approved is built.
    """
    record = read_record(asset_dir)
    if review.state(record) != "approved":
        raise KilnError(f"'{record['name']}' is not built: its shape review is "
                        f"{review.state(record)}")
    raw = check_file(asset_dir, record["raw_output"], "raw output")
    profile = load_profile(record["target_profile"]["name"], profiles_dir)
    require_tools()

    finished = os.path.join(asset_dir, record["name"] + ".glb")
    if os.path.lexists(finished):
        os.remove(finished)  # an earlier build's model must not outlive a build that fails
    done_stages = []
    with tempfile.TemporaryDirectory(dir=asset_dir, prefix="work-") as work:
        model = raw
        for stage in (STAGES if stages is None else stages):
            model, facts = stage(model, work, record, profile)
            if not os.path.isfile(model):
                raise KilnError(f"the stage {stage.__name__} wrote no model file")
            done_stages.append({"name": stage.__name__, **facts})
        check_file(asset_dir, record["raw_output"], "raw output")
        report = measure(model, size=record["size"])
        checks = run_checks(report, profile)
        passed = all(check["passed"] for check in checks)
        if passed:
            os.replace(model, finished)

    record["target_profile"] = {"name": profile["name"], "sha256": profile["sha256"]}
    record["tools"] = {"blender": blender_version(),
                       "gltf_validator": report["validator"]["version"]}
    record["stages"] = done_stages
    record["checks"] = checks
    record["passed"] = passed
    record["model"] = file_entry(finished) if passed else None
    write_record(asset_dir, record)
    return record


def run(model, size, profile, licence, source, name=None, store=STORE,
        profiles_dir=PROFILES_DIR, reference_image=None, renderer=None):
    """A run from a model file, as far as it goes without a person: the raw output is taken
    in and its review pictures are rendered. Returns (the asset's folder, its record), with
    the shape review waiting. `renderer` stands in for review.render_pictures in tests.
    """
    asset_dir = take_in(model, size, profile, licence, source, name, store, profiles_dir,
                        reference_image)
    try:
        return asset_dir, review.take_pictures(asset_dir, profiles_dir, renderer)
    except BaseException:
        # The run broke before there was anything to decide: leave no half-made asset behind.
        shutil.rmtree(asset_dir, ignore_errors=True)
        raise


def approve(asset_dir, profiles_dir=PROFILES_DIR, note=None, today=None, stages=None):
    """Approve an asset's shape review and build it. Returns the completed record."""
    review.decide(asset_dir, "approved", note, today)
    return build(asset_dir, profiles_dir, stages)


def reject(asset_dir, note=None, today=None):
    """Reject an asset's shape review, which ends its run. Returns the record."""
    return review.decide(asset_dir, "rejected", note, today)


# ---- the commands --------------------------------------------------------------------------

def asset_folder(store, name):
    """The folder of the asset called `name` in the store; raises if there is none."""
    asset_dir = os.path.join(store, name)
    if not _NAME.match(name) or not os.path.isfile(record_path(asset_dir)):
        raise KilnError(f"there is no asset named '{name}' with an asset record in {store}")
    return asset_dir


def how_to_decide(asset_dir, record, store):
    """The lines that say where an asset's review pictures are and how to decide on them."""
    name = record["name"]
    pictures = os.path.join(asset_dir, review.SHAPE_PICTURES)
    views = (record["shape_review"]["pictures"] or {}).get("views", [])
    elsewhere = "" if os.path.abspath(store) == os.path.abspath(STORE) else f" --store {store}"
    return [f"  review pictures  {pictures}{os.sep} ({len(views)}: "
            f"{', '.join(view['name'] for view in views)})",
            f"  beside the reference image  {os.path.join(pictures, review.PAGE_NAME)}",
            "Look at them, then decide:",
            f"  python3 -m kiln review {name} --approve{elsewhere}    build the asset",
            f"  python3 -m kiln review {name} --reject{elsewhere}     end the run; nothing is built",
            "Either takes --note TEXT."]


def report_build(asset_dir, record):
    """Print how a build came out. Returns the exit code: 0 if every check passed, else 1."""
    lines = [f"  {describe(check)}" for check in record["checks"]]
    if not record["passed"]:
        failed = sum(1 for check in record["checks"] if not check["passed"])
        print(f"kiln: stopped, {failed} check(s) of target profile "
              f"'{record['target_profile']['name']}' failed for '{record['name']}'",
              file=sys.stderr)
        print("\n".join(lines), file=sys.stderr)
        print(f"No finished model was written. The raw output and the asset record with "
              f"these results are in {asset_dir}", file=sys.stderr)
        return 1
    print(f"asset '{record['name']}' at size {record['size']:g} m, target profile "
          f"'{record['target_profile']['name']}'")
    print("\n".join(lines))
    print(f"  model         {os.path.join(asset_dir, record['model']['path'])}")
    print(f"  asset record  {record_path(asset_dir)}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m kiln run",
        description="Start an asset from a model file: keep it as the raw output, render its "
                    "review pictures and stop for the shape review. `python3 -m kiln review` "
                    "then approves, which builds the asset, or rejects.")
    parser.add_argument("--model", required=True, metavar="FILE",
                        help="the model file (.glb) to start from, taken as the raw output: "
                             "a bought or hand-modelled model")
    parser.add_argument("--size", required=True, type=float, metavar="METRES",
                        help="the asset's largest dimension in metres")
    parser.add_argument("--profile", required=True, metavar="NAME",
                        help="the target profile to check against: a file in profiles/")
    parser.add_argument("--licence", required=True, metavar="TEXT",
                        help="the licence the model is used under, e.g. \"CC0 1.0\"")
    parser.add_argument("--source", required=True, metavar="TEXT",
                        help="where the model was bought, or who modelled it")
    parser.add_argument("--reference-image", metavar="FILE",
                        help="the picture that shows what the asset should look like, kept "
                             "beside the asset record (.png, .jpg or .webp)")
    parser.add_argument("--name", metavar="NAME",
                        help="the asset's name (default: the model file's name)")
    parser.add_argument("--store", default=STORE, metavar="DIR",
                        help="where assets are kept (default: assets/ in the repo)")
    parser.add_argument("--profiles", default=PROFILES_DIR, metavar="DIR",
                        help="where target profiles are kept (default: profiles/ in the repo)")
    args = parser.parse_args(argv)
    try:
        asset_dir, record = run(args.model, args.size, args.profile, args.licence, args.source,
                                name=args.name, store=args.store, profiles_dir=args.profiles,
                                reference_image=args.reference_image)
    except KilnError as error:
        print(f"kiln run: {error}", file=sys.stderr)
        return 2
    print(f"'{record['name']}' at size {record['size']:g} m is waiting for its shape review. "
          "Nothing is built yet.")
    print("\n".join(how_to_decide(asset_dir, record, args.store)))
    return 0


def review_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m kiln review",
        description="The shape review of an asset: say where it stands, or record a person's "
                    "decision on its review pictures. Approving builds the asset; rejecting "
                    "ends the run with nothing built.")
    parser.add_argument("name", metavar="NAME", help="the asset, as it is named in the store")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--approve", action="store_true",
                        help="approve the raw output, then build the asset")
    choice.add_argument("--reject", action="store_true",
                        help="reject the raw output: the run ends and nothing is built")
    choice.add_argument("--render", action="store_true",
                        help="render the review pictures again, while the review is undecided")
    parser.add_argument("--note", metavar="TEXT", help="why, kept with the decision")
    parser.add_argument("--store", default=STORE, metavar="DIR",
                        help="where assets are kept (default: assets/ in the repo)")
    parser.add_argument("--profiles", default=PROFILES_DIR, metavar="DIR",
                        help="where target profiles are kept (default: profiles/ in the repo)")
    args = parser.parse_args(argv)
    if args.note is not None and not (args.approve or args.reject):
        parser.error("--note goes with --approve or --reject")
    decided = False
    try:
        asset_dir = asset_folder(args.store, args.name)
        if args.reject:
            record = reject(asset_dir, args.note)
            print(f"'{args.name}': shape review rejected on {record['shape_review']['decided_on']}."
                  f" The run has ended and nothing is built. The raw output and the asset "
                  f"record are kept in {asset_dir}")
            return 0
        if args.approve:
            record = review.decide(asset_dir, "approved", args.note)
            decided = True
            print(f"'{args.name}': shape review approved on "
                  f"{record['shape_review']['decided_on']}. Building.")
            return report_build(asset_dir, build(asset_dir, args.profiles))
        if args.render:
            record = review.take_pictures(asset_dir, args.profiles)
            print(f"'{args.name}': review pictures rendered.")
        else:
            record = read_record(asset_dir)
        where = review.state(record)
        if where == "pending":
            print(f"'{args.name}' is waiting for its shape review.")
            problems = review.picture_problems(asset_dir, record)
            for problem in problems:
                print(f"  {problem}")
            if problems:
                print(f"Render them with `python3 -m kiln review {args.name} --render`.")
            else:
                print("\n".join(how_to_decide(asset_dir, record, args.store)))
        else:
            was = record["shape_review"]
            print(f"'{args.name}': shape review {where} on {was['decided_on']}"
                  + (f" ({was['note']})" if was["note"] else ""))
        return 0
    except KilnError as error:
        print(f"kiln review: {error}", file=sys.stderr)
        if decided:
            print(f"The approval is recorded. Build the asset with `python3 -m kiln rebuild "
                  f"{args.name}` once that is put right.", file=sys.stderr)
        return 2
