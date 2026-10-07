"""A run: from a model file to an asset, which is the finished model plus its asset record.

    python3 -m kiln run --model rock.glb --size 0.8 --profile pit \\
        --licence "CC0 1.0" --source "modelled by J. Green"

A run has two halves, and the second needs nothing but the asset's folder:

    take_in()   copies the model file into the store as the raw output and writes the asset
                record with what only the caller knows: name, size, profile, licence, source.
    build()     reads the asset record, takes the raw output through STAGES in a work area,
                measures the result, makes the profile's checks, and writes the finished
                model and the completed record.

The store holds one folder per asset:

    <store>/<name>/asset_record.json    the asset record               (in git)
    <store>/<name>/raw_output.glb       the raw output, never changed  (ignored by git)
    <store>/<name>/<name>.glb           the finished model             (ignored by git)

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

from kiln import KilnError
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


# ---- the two halves of a run ---------------------------------------------------------------

def take_in(model, size, profile, licence, source, name=None, store=STORE,
            profiles_dir=PROFILES_DIR):
    """Start an asset from a model file: copy it into the store as the raw output and write
    the asset record with what the caller gave. Returns the asset's folder.

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
    load_profile(profile, profiles_dir)
    require_tools()
    asset_dir = os.path.join(store, name)
    if os.path.lexists(asset_dir):
        raise KilnError(f"an asset named '{name}' is already in the store: {asset_dir}. "
                        "Kiln does not overwrite an asset; remove that folder to make it "
                        "again, or give another name with --name.")

    os.makedirs(asset_dir)
    raw = os.path.join(asset_dir, "raw_output" + extension)
    shutil.copyfile(model, raw)
    os.chmod(raw, 0o444)  # no stage may write to the raw output
    write_record(asset_dir, {
        "name": name,
        "licence": licence.strip(),
        "source": source.strip(),
        "size": float(size),
        "target_profile": {"name": profile, "sha256": None},
        "raw_output": file_entry(raw),
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

    The same raw output, size and profile give the same finished model, byte for byte.
    """
    record = read_record(asset_dir)
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
        profiles_dir=PROFILES_DIR):
    """A whole run from a model file. Returns (the asset's folder, its completed record)."""
    asset_dir = take_in(model, size, profile, licence, source, name, store, profiles_dir)
    try:
        return asset_dir, build(asset_dir, profiles_dir)
    except BaseException:
        # The run broke before any check was made: leave no half-made asset behind.
        shutil.rmtree(asset_dir, ignore_errors=True)
        raise


# ---- the command ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m kiln run",
        description="Make an asset from a model file: scale it to the size, check it against "
                    "the target profile, and write the finished model with its asset record.")
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
    parser.add_argument("--name", metavar="NAME",
                        help="the asset's name (default: the model file's name)")
    parser.add_argument("--store", default=STORE, metavar="DIR",
                        help="where assets are kept (default: assets/ in the repo)")
    parser.add_argument("--profiles", default=PROFILES_DIR, metavar="DIR",
                        help="where target profiles are kept (default: profiles/ in the repo)")
    args = parser.parse_args(argv)
    try:
        asset_dir, record = run(args.model, args.size, args.profile, args.licence, args.source,
                                name=args.name, store=args.store, profiles_dir=args.profiles)
    except KilnError as error:
        print(f"kiln run: {error}", file=sys.stderr)
        return 2

    lines = [f"  {describe(check)}" for check in record["checks"]]
    if not record["passed"]:
        failed = sum(1 for check in record["checks"] if not check["passed"])
        print(f"kiln run: stopped, {failed} check(s) of target profile "
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
