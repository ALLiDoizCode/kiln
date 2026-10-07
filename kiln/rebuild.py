"""Rebuild assets from their kept raw outputs, without generating again.

    python3 -m kiln rebuild [NAME ...] [--store DIR] [--profiles DIR] [--check]

With no names it takes every folder of the store that holds an asset record. Each asset is
rebuilt by kiln.run.build() from its record and its raw output alone, so a changed target
profile or stage reaches every asset in one command. Nothing here calls a generator.

One line per asset says what became of it:

    rebuilt, unchanged     the finished model has the checksum its record had; anything else that
                           differs (profile checksum, tool version, a check's number) follows in
                           brackets
    rebuilt, changed       the model's checksum differs, or a check's result flipped; the
                           differences are listed
    failed a check         the check, what was measured, the limit and the overshoot follow; the
                           record says so and no finished model is left
    raw output missing     or "raw output changed since its asset record was written": that
                           asset is not rebuilt, and nothing in its folder is touched
    problem                anything else that stopped one asset: an unreadable record, a missing
                           profile, a stage that broke, a stage that wrote to the raw output

A finished model that is missing, or that differs from its record, is reported and then
rebuilt, because the raw output is the input and the model is only its result. One asset's
problem never stops the others. The exit code is 0 unless an asset failed a check or had a
problem.

Repeatability was tried on this machine and no difference was found: the same raw output, size
and profile gave byte-identical finished models in different store paths, with Blender on 1, 3
and all threads, and for models with and without a texture (tests.test_rebuild.Repeatability).
The asset record holds no time or date, so it repeats too.

With --check nothing is built or written. Each asset is reported "up to date" or "out of date"
with the reasons: a large file missing or changed, the profile's checksum no longer the one in
the record, or a last build that failed a check. Tool versions are not looked at, since that
would start Blender; a rebuild reports them. The exit code is 1 if any asset is not up to date.
"""
import argparse
import os
import sys

from kiln import KilnError, run as kiln_run
from kiln.checks import describe
from kiln.profile import PROFILES_DIR, load_profile
from kiln.record import RECORD_NAME, read_record, record_path, sha256_of


def file_state(asset_dir, entry):
    """"ok", "missing" or "changed": a large file compared with the entry in the record."""
    path = os.path.join(asset_dir, entry["path"])
    if not os.path.isfile(path):
        return "missing"
    return "ok" if sha256_of(path) == entry["sha256"] else "changed"


def asset_names(store, names):
    """The assets to look at: the names given, or every folder of the store with a record."""
    if names:
        return list(dict.fromkeys(names))
    if not os.path.isdir(store):
        return []
    return sorted(name for name in os.listdir(store)
                  if os.path.isfile(os.path.join(store, name, RECORD_NAME)))


def raw_output_problem(asset_dir, record):
    """What is wrong with the raw output a record names, as a line, or None if nothing is."""
    path = os.path.join(asset_dir, record["raw_output"]["path"])
    state = file_state(asset_dir, record["raw_output"])
    if state == "missing":
        return f"raw output missing: {path}"
    if state == "changed":
        return f"raw output changed since its asset record was written: {path}"
    return None


def problem_text(error):
    if isinstance(error, KilnError):
        return f"problem: {error}"
    return f"problem: the asset record is incomplete ({error!r})"


def what_changed(old, new):
    """The differences between two records of one asset, as short phrases."""
    reasons = []
    if old["target_profile"]["sha256"] not in (None, new["target_profile"]["sha256"]):
        reasons.append("profile checksum")
    for tool, version in (old["tools"] or {}).items():
        if version != new["tools"][tool]:
            reasons.append(f"{tool.removeprefix('gltf_')} version {version} -> {new['tools'][tool]}")
    was = {check["name"]: check for check in old["checks"] or []}
    for check in new["checks"]:
        before = was.get(check["name"])
        for field in ("measured", "limit"):
            if before and before[field] != check[field]:
                reasons.append(f"check {check['name']} {field} "
                               f"{before[field]:,} -> {check[field]:,}")
        if before and before["passed"] != check["passed"]:
            reasons.append(f"check {check['name']} {'now passes' if check['passed'] else 'now fails'}")
    if (old["model"] or {}).get("sha256") != (new["model"] or {}).get("sha256"):
        reasons.append("model checksum")
    return reasons


def rebuild_one(store, name, profiles_dir, stages):
    """Rebuild one asset: a result {"name", "status", "text", "lines"}."""
    def result(status, text, lines=()):
        return {"name": name, "status": status, "text": text, "lines": list(lines)}
    asset_dir = os.path.join(store, name)
    try:
        if os.sep in name or not os.path.isfile(record_path(asset_dir)):
            raise KilnError("there is no asset with an asset record in the store")
        old = read_record(asset_dir)
        if raw_output_problem(asset_dir, old):
            return result("problem", raw_output_problem(asset_dir, old))
        notes = []
        if old["model"]:
            model_state = file_state(asset_dir, old["model"])
            if model_state != "ok":
                notes.append("the finished model was missing" if model_state == "missing"
                             else "the finished model had changed on disk")
        new = kiln_run.build(asset_dir, profiles_dir, stages)
    except (KilnError, KeyError, TypeError) as error:
        return result("problem", problem_text(error))
    if not new["passed"]:
        return result("failed a check", "failed a check",
                      [f"  {describe(c)}" for c in new["checks"] if not c["passed"]])
    reasons = what_changed(old, new)
    changed = (old["model"] or {}).get("sha256") != new["model"]["sha256"] or not old["passed"]
    text = "rebuilt, changed" if changed else "rebuilt, unchanged"
    details = notes + reasons
    return result("changed" if changed else "unchanged",
                  text + (f" ({'; '.join(details)})" if details else ""))


def check_one(store, name, profiles_dir):
    """Look at one asset without writing: a result like rebuild_one's, "ok" or "out of date"."""
    def result(status, text):
        return {"name": name, "status": status, "text": text, "lines": []}
    asset_dir = os.path.join(store, name)
    try:
        if os.sep in name or not os.path.isfile(record_path(asset_dir)):
            raise KilnError("there is no asset with an asset record in the store")
        record = read_record(asset_dir)
        if raw_output_problem(asset_dir, record):
            return result("problem", raw_output_problem(asset_dir, record))
        reasons = []
        if record["model"] and file_state(asset_dir, record["model"]) != "ok":
            reasons.append("the finished model is missing"
                           if file_state(asset_dir, record["model"]) == "missing"
                           else "the finished model has changed on disk")
        profile = load_profile(record["target_profile"]["name"], profiles_dir)
        if record["checks"] is None:
            reasons.append("it has not been built")
        elif profile["sha256"] != record["target_profile"]["sha256"]:
            reasons.append("the profile has changed")
        if record["passed"] is False:
            reasons.append("the last build failed a check")
    except (KilnError, KeyError, TypeError) as error:
        return result("problem", problem_text(error))
    return result("out of date", "; ".join(reasons)) if reasons else result("ok", "up to date")


def rebuild(store, profiles_dir, names=None, stages=None):
    """Rebuild the named assets, or every asset with a record. Returns one result each."""
    return [rebuild_one(store, name, profiles_dir, stages) for name in asset_names(store, names)]


def check(store, profiles_dir, names=None):
    """Like rebuild(), but only look: nothing is built or written."""
    return [check_one(store, name, profiles_dir) for name in asset_names(store, names)]


SUMMARY_ORDER = ("ok", "unchanged", "changed", "out of date", "failed a check", "problem")
SUMMARY_WORDS = {"ok": "up to date", "problem": "with a problem"}


def summary(results):
    count = len(results)
    parts = [f"{sum(r['status'] == s for r in results)} {SUMMARY_WORDS.get(s, s)}"
             for s in SUMMARY_ORDER if any(r["status"] == s for r in results)]
    return f"{count} asset{'' if count == 1 else 's'}" + (": " + ", ".join(parts) if parts else "")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m kiln rebuild",
        description="Rebuild assets from their kept raw outputs, without generating again.")
    parser.add_argument("names", nargs="*", metavar="NAME",
                        help="the assets to rebuild (default: every asset with an asset record)")
    parser.add_argument("--check", action="store_true",
                        help="only report what is missing, changed or out of date; write nothing")
    parser.add_argument("--store", default=kiln_run.STORE, metavar="DIR",
                        help="where assets are kept (default: assets/ in the repo)")
    parser.add_argument("--profiles", default=PROFILES_DIR, metavar="DIR",
                        help="where target profiles are kept (default: profiles/ in the repo)")
    args = parser.parse_args(argv)
    if args.check:
        results = check(args.store, args.profiles, args.names)
    else:
        results = rebuild(args.store, args.profiles, args.names)
    for result in results:
        print(f"{result['name']}: {result['text']}")
        for line in result["lines"]:
            print(line)
    print(summary(results))
    return 0 if all(r["status"] in ("ok", "unchanged", "changed") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
