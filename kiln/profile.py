"""Target profiles: one TOML file per profile, kept in git under profiles/.

    profile = load_profile("pit")
    profile["triangle_budget"]             a field of the profile
    profile["name"], profile["sha256"]     which profile, and the checksum of its file

The fields are placeholders until issue #11 settles what a target profile holds.
"""
import os
import re
import tomllib

from kiln import KilnError
from kiln.record import sha256_of

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(REPO_ROOT, "profiles")

# Every field a profile must hold, and no other: field name -> what it must be.
FIELDS = {"triangle_budget": "a whole number above zero"}

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


def load_profile(name, profiles_dir=PROFILES_DIR):
    """The target profile called `name`, as a dict of its fields plus "name" and "sha256"."""
    if not _NAME.match(name):
        raise KilnError(f"'{name}' is not a target profile name: use letters, digits, - and _")
    path = os.path.join(profiles_dir, name + ".toml")
    if not os.path.isfile(path):
        have = (sorted(f[:-5] for f in os.listdir(profiles_dir) if f.endswith(".toml"))
                if os.path.isdir(profiles_dir) else [])
        raise KilnError(f"there is no target profile '{name}': {path} does not exist"
                        + (f" (profiles there: {', '.join(have)})" if have else ""))
    try:
        with open(path, "rb") as f:
            fields = tomllib.load(f)
    except tomllib.TOMLDecodeError as error:
        raise KilnError(f"target profile {path} is not valid TOML: {error}") from None
    for field in fields:
        if field not in FIELDS:
            raise KilnError(f"target profile {path} has a field kiln does not know: {field}")
    for field, must_be in FIELDS.items():
        value = fields.get(field)
        if type(value) is not int or value <= 0:
            raise KilnError(f"target profile {path}: {field} must be {must_be}"
                            + (", but it is missing" if value is None else f", not {value!r}"))
    return {"name": name, "sha256": sha256_of(path), **fields}
