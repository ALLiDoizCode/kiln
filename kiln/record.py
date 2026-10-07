"""The asset record: the file beside the model, as JSON.

Its keys are written in the order kiln put them in. What a build writes into it holds no time
or date, so building again from the same record writes the same bytes. The one date in it is
the day a person decided a review, which is a fact about the review: a build copies the review
as it finds it. Paths in it are relative to the record's own folder.
"""
import hashlib
import json
import os

from kiln import KilnError

RECORD_NAME = "asset_record.json"


def sha256_of(path):
    """The SHA-256 checksum of a file, as hexadecimal text."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def file_entry(path):
    """How a large file is written in a record: its file name and its checksum."""
    return {"path": os.path.basename(path), "sha256": sha256_of(path)}


def record_path(asset_dir):
    return os.path.join(asset_dir, RECORD_NAME)


def write_record(asset_dir, record):
    path = record_path(asset_dir)
    scratch = path + ".part"
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    os.replace(scratch, path)
    return path


def read_record(asset_dir):
    path = record_path(asset_dir)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise KilnError(f"there is no asset record at {path}") from None
    except ValueError as error:
        raise KilnError(f"the asset record {path} is not valid JSON: {error}") from None


def check_file(asset_dir, entry, what):
    """The path of a large file a record names; raises unless it is there with its checksum."""
    path = os.path.join(asset_dir, entry["path"])
    if not os.path.isfile(path):
        raise KilnError(f"the {what} is missing: {path}")
    if sha256_of(path) != entry["sha256"]:
        raise KilnError(f"the {what} has changed since its asset record was written: {path}")
    return path
