"""Tests for a run: target profiles, checks, the asset record, and the run itself.

The first classes need no tools. The classes under "with the pinned tools" start the pinned
Blender and the glTF validator, and are skipped when .tools/ does not hold them. Every test
uses a store in a temporary folder, never the repo's.

Run from the repo root:  python3 -m unittest
"""
import contextlib
import io
import json
import math
import os
import shutil
import tempfile
import unittest
from unittest import mock

from kiln import KilnError, __main__ as kiln_command, review, run as kiln_run
from kiln.checks import describe, run_checks, triangle_count, validator_errors
from kiln.glb import load
from kiln.measure import DEFAULT_VALIDATOR, measure
from kiln.profile import load_profile
from kiln.record import (RECORD_NAME, check_file, file_entry, read_record, sha256_of,
                         write_record)
from tests.glb_fixture import GlbBuilder, cube_cross, cube_six_faces, jpeg, png, quad

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECIMENS = [os.path.join(REPO, "learn", "specimens", name)
             for name in ("crate.glb", "boulder_1.glb")]
HAVE_TOOLS = os.path.exists(kiln_run.BLENDER) and os.path.exists(DEFAULT_VALIDATOR)
needs_tools = unittest.skipUnless(HAVE_TOOLS, "the pinned Blender and glTF validator are not "
                                              "installed (tools/install_tools.sh)")

# The size every finished model is held to: its largest dimension may differ from the size
# given by this share of it. Positions are stored as 32-bit floats, good to about 1 in 10^7.
SIZE_TOLERANCE = 1e-5

# The day every test's shape review is decided on, so that records repeat.
TODAY = "2026-10-07"
CLOSEST = "closest_viewing_distance = 0.5\n"


def stand_in_renderer(model, size, closest, out_dir):
    """Stands in for review.render_pictures: two tiny pictures, written at once, with the
    report the real renderer gives. The pictures are the same bytes every time."""
    views = []
    for name in ("front", "closest"):
        with open(os.path.join(out_dir, name + ".png"), "wb") as f:
            f.write(png(4, 3))
        views.append({"name": name, "file": name + ".png", "shows": f"the {name} <view>"})
    return {"view_set": 1, "picture_size": [4, 3], "views": views,
            "renderer": {"name": "stand-in", "version": "0"}}


class RunCase(unittest.TestCase):
    """A temporary folder holding a store, a folder of target profiles and model files."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.store = self.path("store")
        self.profiles = self.path("profiles")
        os.mkdir(self.profiles)
        self.profile("pit", "triangle_budget = 20000\n")

    def path(self, *parts):
        return os.path.join(self._dir.name, *parts)

    def profile(self, name, text, closest=CLOSEST):
        """Write a target profile: `text`, and the closest viewing distance unless told not to."""
        with open(os.path.join(self.profiles, name + ".toml"), "w", encoding="utf-8") as f:
            f.write(text + closest)

    def cube(self, name="cube.glb"):
        """A unit cube of 12 triangles."""
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(*cube_six_faces())]))
        return b.write(self.path(name))

    def take_in(self, model=None, size=0.8, profile="pit", licence="CC0 1.0",
                source="modelled by a test", **more):
        return kiln_run.take_in(model or self.cube(), size, profile, licence, source,
                                store=self.store, profiles_dir=self.profiles, **more)

    def run_asset(self, model=None, size=0.8, profile="pit", **more):
        """A run as far as the shape review: (the asset's folder, its record)."""
        more.setdefault("renderer", stand_in_renderer)
        return kiln_run.run(model or self.cube(), size, profile, "CC0 1.0", "modelled by a test",
                            store=self.store, profiles_dir=self.profiles, **more)

    def approved(self, model=None, **more):
        """An asset whose shape review is approved and that is not built yet: its folder."""
        asset_dir, _ = self.run_asset(model, **more)
        review.decide(asset_dir, "approved", today=TODAY)
        return asset_dir

    def run_and_approve(self, model=None, **more):
        """A whole run with an approval: (the asset's folder, its completed record)."""
        asset_dir = self.approved(model, **more)
        return asset_dir, kiln_run.build(asset_dir, self.profiles)

    def files(self, asset_dir):
        """Every file in an asset's folder with its checksum, by its path within the folder."""
        return {os.path.relpath(os.path.join(folder, name), asset_dir):
                sha256_of(os.path.join(folder, name))
                for folder, _, names in os.walk(asset_dir) for name in names}

    def command(self, *argv):
        """Run `python3 -m kiln <argv>` in this process: (exit code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = kiln_command.main(list(argv))
            except SystemExit as stop:
                code = stop.code
        return code, out.getvalue(), err.getvalue()


def without_tools(test):
    """Stand in for Blender and the validator, so the run's own logic is tested alone:
    the tools count as installed, and the validator always reports no errors."""
    def measured(path, size=None):
        report = measure(path, size=size, validator=None)
        report["validator"] = {"ran": True, "version": "stand-in", "errors": 0}
        return report
    for name, stand_in in (("require_tools", lambda: None),
                           ("blender_version", lambda: "stand-in"), ("measure", measured)):
        patch = mock.patch.object(kiln_run, name, stand_in)
        patch.start()
        test.addCleanup(patch.stop)
    without_renderer(test)


def without_renderer(test):
    """Stand in for the program that renders the review pictures: it counts as built, and
    the pictures are stand_in_renderer's."""
    for name, stand_in in (("require_renderer", lambda: "stand-in"),
                           ("render_pictures", stand_in_renderer)):
        patch = mock.patch.object(review, name, stand_in)
        patch.start()
        test.addCleanup(patch.stop)


REAL_REQUIRE_TOOLS = kiln_run.require_tools
REAL_REQUIRE_RENDERER = review.require_renderer
REAL_RENDER_PICTURES = review.render_pictures


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def copy_stage(source, work, record, profile):
    """A stage that passes the model on unchanged."""
    target = os.path.join(work, "copy.glb")
    shutil.copyfile(source, target)
    return target, {}


# ---- target profiles -----------------------------------------------------------------------

class Profiles(RunCase):
    def test_the_pit_profile_in_the_repo_loads(self):
        profile = load_profile("pit")
        self.assertEqual(profile["name"], "pit")
        self.assertIsInstance(profile["triangle_budget"], int)
        self.assertEqual(profile["closest_viewing_distance"], 0.5)
        self.assertEqual(profile["sha256"], sha256_of(os.path.join(REPO, "profiles", "pit.toml")))

    def test_the_checksum_follows_the_file(self):
        before = load_profile("pit", self.profiles)
        self.profile("pit", "triangle_budget = 500\n")
        after = load_profile("pit", self.profiles)
        self.assertEqual(after["triangle_budget"], 500)
        self.assertNotEqual(before["sha256"], after["sha256"])

    def test_a_missing_profile_is_named_with_those_that_exist(self):
        with self.assertRaises(KilnError) as caught:
            load_profile("desert", self.profiles)
        self.assertIn("desert", str(caught.exception))
        self.assertIn("pit", str(caught.exception))

    def test_a_profile_that_cannot_be_used_is_refused(self):
        for text, expected in (("triangle_budget = 0\n" + CLOSEST, "triangle_budget"),
                               ("triangle_budget = 2.5\n" + CLOSEST, "triangle_budget"),
                               (CLOSEST, "triangle_budget must be a whole number above zero, "
                                         "but it is missing"),
                               ("triangle_budget = 5\n", "closest_viewing_distance must be a "
                                                         "number of metres above zero, but it "
                                                         "is missing"),
                               ("triangle_budget = 5\nclosest_viewing_distance = 0\n",
                                "closest_viewing_distance"),
                               ("triangle_budget = 5\nclosest_viewing_distance = -0.5\n",
                                "closest_viewing_distance"),
                               ("triangle_budget = 5\nclosest_viewing_distance = inf\n",
                                "closest_viewing_distance"),
                               ("triangle_budget = 5\nclosest_viewing_distance = \"near\"\n",
                                "closest_viewing_distance"),
                               ("triangle_budget = 5\nviewing_distance = 2\n" + CLOSEST,
                                "viewing_distance"),
                               ("triangle_budget = \n", "not valid TOML")):
            self.profile("odd", text, closest="")
            with self.assertRaises(KilnError, msg=text) as caught:
                load_profile("odd", self.profiles)
            self.assertIn(expected, str(caught.exception))

    def test_a_name_that_could_leave_the_folder_is_refused(self):
        with self.assertRaises(KilnError):
            load_profile("../pit", self.profiles)

    def test_the_closest_viewing_distance_may_be_a_whole_number_of_metres(self):
        self.profile("far", "triangle_budget = 5\nclosest_viewing_distance = 2\n", closest="")
        self.assertEqual(load_profile("far", self.profiles)["closest_viewing_distance"], 2)


# ---- checks --------------------------------------------------------------------------------

def report_with(triangles=12, errors=0):
    return {"totals": {"triangles": triangles},
            "validator": {"ran": True, "version": "x", "errors": errors}}


class Checks(unittest.TestCase):
    profile = {"name": "pit", "triangle_budget": 100}

    def test_a_model_within_budget_with_no_errors_passes_both(self):
        results = run_checks(report_with(triangles=100), self.profile)
        self.assertEqual(results, [
            {"name": "validator_errors", "measured": 0, "limit": 0, "unit": "errors",
             "passed": True},
            {"name": "triangle_count", "measured": 100, "limit": 100, "unit": "triangles",
             "passed": True}])

    def test_a_model_over_the_triangle_budget_fails_that_check(self):
        result = triangle_count(report_with(triangles=136), self.profile)
        self.assertEqual((result["measured"], result["limit"], result["passed"]),
                         (136, 100, False))

    def test_validator_errors_fail_the_check(self):
        result = validator_errors(report_with(errors=3), self.profile)
        self.assertEqual((result["measured"], result["limit"], result["passed"]), (3, 0, False))

    def test_every_check_is_made_even_after_one_fails(self):
        results = run_checks(report_with(triangles=101, errors=1), self.profile)
        self.assertEqual([r["passed"] for r in results], [False, False])

    def test_a_validator_that_did_not_run_is_not_a_pass(self):
        for verdict in (None, {"ran": False, "reason": "not installed"}):
            with self.assertRaises(KilnError):
                validator_errors({"validator": verdict}, self.profile)

    def test_a_failure_is_described_by_name_value_limit_and_overshoot(self):
        line = describe(triangle_count(report_with(triangles=25000), {"triangle_budget": 20000}))
        for part in ("triangle_count", "25,000", "20,000", "over by 5,000", "25.0%", "FAILED"):
            self.assertIn(part, line)
        line = describe(validator_errors(report_with(errors=2), {}))
        for part in ("validator_errors", "measured 2", "limit 0", "over by 2"):
            self.assertIn(part, line)


# ---- the asset record ----------------------------------------------------------------------

class Records(RunCase):
    def test_a_checksum_is_the_sha256_of_the_bytes(self):
        path = self.path("abc")
        with open(path, "wb") as f:
            f.write(b"abc")
        self.assertEqual(sha256_of(path),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(file_entry(path), {"path": "abc", "sha256": sha256_of(path)})

    def test_a_record_is_written_the_same_way_every_time_in_the_order_given(self):
        record = {"name": "b", "licence": "a", "size": 0.8, "checks": [{"zz": 1, "aa": 2}]}
        os.mkdir(self.store)
        first = read_bytes(write_record(self.store, record))
        second = read_bytes(write_record(self.store, dict(record)))
        self.assertEqual(first, second)
        self.assertEqual(list(json.loads(first)), ["name", "licence", "size", "checks"])
        self.assertLess(first.index(b'"zz"'), first.index(b'"aa"'))
        self.assertEqual(read_record(self.store), record)

    def test_a_missing_or_changed_large_file_is_reported_by_path(self):
        os.mkdir(self.store)
        path = os.path.join(self.store, "raw_output.glb")
        with open(path, "wb") as f:
            f.write(b"one")
        entry = file_entry(path)
        self.assertEqual(check_file(self.store, entry, "raw output"), path)
        with open(path, "wb") as f:
            f.write(b"two")
        with self.assertRaisesRegex(KilnError, "raw output has changed.*raw_output.glb"):
            check_file(self.store, entry, "raw output")
        os.remove(path)
        with self.assertRaisesRegex(KilnError, "raw output is missing.*raw_output.glb"):
            check_file(self.store, entry, "raw output")

    def test_a_missing_record_is_reported(self):
        with self.assertRaisesRegex(KilnError, RECORD_NAME):
            read_record(self.store)


# ---- taking a model file in ----------------------------------------------------------------

class TakingIn(RunCase):
    def setUp(self):
        super().setUp()
        without_tools(self)

    def test_the_model_is_copied_unchanged_as_the_raw_output_with_its_record(self):
        model = self.cube("rock.glb")
        asset_dir = self.take_in(model, size=2, licence=" CC0 1.0 ", source="bought at a shop")
        self.assertEqual(asset_dir, os.path.join(self.store, "rock"))
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb"])
        raw = os.path.join(asset_dir, "raw_output.glb")
        self.assertEqual(read_bytes(raw), read_bytes(model))
        self.assertFalse(os.stat(raw).st_mode & 0o222, "the raw output can be written to")
        record = read_record(asset_dir)
        self.assertEqual(list(record), ["name", "licence", "source", "size", "target_profile",
                                        "reference_image", "raw_output", "shape_review",
                                        "tools", "stages", "checks", "passed", "model"])
        self.assertIsNone(record["reference_image"])
        self.assertEqual(record["shape_review"], {"decision": None, "note": None,
                                                  "decided_on": None, "pictures": None})
        self.assertEqual((record["name"], record["licence"], record["source"], record["size"]),
                         ("rock", "CC0 1.0", "bought at a shop", 2.0))
        self.assertEqual(record["target_profile"]["name"], "pit")
        self.assertEqual(record["raw_output"],
                         {"path": "raw_output.glb", "sha256": sha256_of(model)})

    def test_the_name_can_be_given(self):
        self.assertTrue(self.take_in(name="big-rock_2").endswith("big-rock_2"))

    def test_a_reference_image_is_copied_beside_the_record_with_its_checksum(self):
        for kind in (".png", ".JPG", ".webp"):
            picture = self.path("what it should look like" + kind)
            with open(picture, "wb") as f:
                f.write(png(2, 2) + kind.encode())
            asset_dir = self.take_in(reference_image=picture, name="rock" + kind[1:].lower())
            kept = os.path.join(asset_dir, "reference_image" + kind.lower())
            self.assertEqual(read_bytes(kept), read_bytes(picture))
            self.assertEqual(read_record(asset_dir)["reference_image"],
                             {"path": "reference_image" + kind.lower(),
                              "sha256": sha256_of(picture)})

    def refused(self, expected, **inputs):
        with self.assertRaises(KilnError) as caught:
            self.take_in(**inputs)
        self.assertIn(expected, str(caught.exception))
        self.assertFalse(os.path.exists(self.store), "a refused run wrote into the store")

    def test_inputs_that_cannot_be_used_are_refused_and_nothing_is_written(self):
        self.refused("no model file", model=self.path("missing.glb"))
        self.refused("positive number of metres", size=0)
        self.refused("positive number of metres", size=-0.8)
        self.refused("positive number of metres", size=math.nan)
        self.refused("positive number of metres", size=math.inf)
        self.refused("no target profile 'desert'", profile="desert")
        self.refused("licence must be given", licence="  ")
        self.refused("source must be given", source="")
        self.refused("cannot be an asset's name", name="../rock")
        self.refused("cannot be an asset's name", model=self.cube("my rock.glb"))
        text = self.path("notes.txt")
        with open(text, "w") as f:
            f.write("not a model")
        self.refused("must be a .glb", model=text)
        broken = self.path("broken.glb")
        with open(broken, "wb") as f:
            f.write(b"not a model")
        self.refused("cannot be read", model=broken)
        self.refused("no reference image", reference_image=self.path("missing.png"))
        self.refused("reference image must be one of", reference_image=text)

    def test_missing_tools_are_refused_with_how_to_install_them(self):
        with mock.patch.object(kiln_run, "require_tools", REAL_REQUIRE_TOOLS), \
                mock.patch.object(kiln_run, "BLENDER", self.path("no-blender")):
            self.refused("tools/install_tools.sh")

    def test_a_renderer_that_is_not_built_is_refused_with_how_to_build_it(self):
        with mock.patch.object(review, "require_renderer", REAL_REQUIRE_RENDERER), \
                mock.patch.dict(os.environ, {"KILN_REVIEW_RENDERER": self.path("no-renderer")}):
            self.refused("cargo build --release -p asset_view --bin review_pictures")

    def test_an_asset_that_exists_is_not_overwritten(self):
        asset_dir = self.take_in()
        before = read_bytes(os.path.join(asset_dir, RECORD_NAME))
        with self.assertRaisesRegex(KilnError, "already in the store"):
            self.take_in(licence="another")
        self.assertEqual(read_bytes(os.path.join(asset_dir, RECORD_NAME)), before)


# ---- building, with stand-ins for the tools ------------------------------------------------

class Building(RunCase):
    def setUp(self):
        super().setUp()
        without_tools(self)

    def build(self, asset_dir, stages=(copy_stage,)):
        return kiln_run.build(asset_dir, profiles_dir=self.profiles, stages=stages)

    def test_a_passing_build_writes_the_model_and_completes_the_record(self):
        asset_dir = self.approved(self.cube())
        record = self.build(asset_dir)
        self.assertEqual(sorted(os.listdir(asset_dir)),
                         [RECORD_NAME, "cube.glb", "raw_output.glb", "review"])
        self.assertEqual(record, read_record(asset_dir))
        self.assertTrue(record["passed"])
        self.assertEqual(record["model"], file_entry(os.path.join(asset_dir, "cube.glb")))
        self.assertEqual(record["target_profile"],
                         {"name": "pit", "sha256": sha256_of(os.path.join(self.profiles, "pit.toml"))})
        self.assertEqual(record["tools"], {"blender": "stand-in", "gltf_validator": "stand-in"})
        self.assertEqual(record["stages"], [{"name": "copy_stage"}])
        self.assertEqual([c["name"] for c in record["checks"]],
                         ["validator_errors", "triangle_count"])
        self.assertEqual(record["checks"][1]["measured"], 12)

    def test_a_failed_check_leaves_the_record_and_the_raw_output_but_no_model(self):
        self.profile("pit", "triangle_budget = 10\n")
        asset_dir = self.approved(self.cube())
        record = self.build(asset_dir)
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        self.assertFalse(record["passed"])
        self.assertIsNone(record["model"])
        self.assertEqual(record["checks"][1], {"name": "triangle_count", "measured": 12,
                                               "limit": 10, "unit": "triangles", "passed": False})
        self.assertEqual(read_record(asset_dir), record)

    def test_a_model_from_an_earlier_build_does_not_outlive_a_build_that_fails(self):
        asset_dir = self.approved(self.cube())
        self.build(asset_dir)
        self.profile("pit", "triangle_budget = 10\n")
        record = self.build(asset_dir)
        self.assertFalse(record["passed"])
        self.assertFalse(os.path.exists(os.path.join(asset_dir, "cube.glb")))

    def test_building_again_gives_the_same_record_and_model(self):
        asset_dir = self.approved(self.cube())
        self.build(asset_dir)
        first = self.files(asset_dir)
        self.build(asset_dir)
        self.assertEqual(self.files(asset_dir), first)

    def test_a_build_copies_the_shape_review_as_it_finds_it(self):
        asset_dir = self.approved(self.cube())
        before = read_record(asset_dir)["shape_review"]
        self.assertEqual(self.build(asset_dir)["shape_review"], before)
        self.assertEqual(before["decided_on"], TODAY)

    def test_a_missing_or_changed_raw_output_is_not_built_from(self):
        asset_dir = self.approved(self.cube())
        raw = os.path.join(asset_dir, "raw_output.glb")
        os.chmod(raw, 0o644)
        with open(raw, "ab") as f:
            f.write(b"\0\0\0\0")
        with self.assertRaisesRegex(KilnError, "raw output has changed"):
            self.build(asset_dir)
        os.remove(raw)
        with self.assertRaisesRegex(KilnError, "raw output is missing"):
            self.build(asset_dir)
        self.assertIsNone(read_record(asset_dir)["checks"])

    def test_a_stage_that_writes_to_the_raw_output_is_caught(self):
        def scribbling_stage(source, work, record, profile):
            os.chmod(source, 0o644)
            with open(source, "ab") as f:
                f.write(b"\0\0\0\0")
            return copy_stage(source, work, record, profile)
        asset_dir = self.approved(self.cube())
        with self.assertRaisesRegex(KilnError, "raw output has changed"):
            self.build(asset_dir, stages=(scribbling_stage,))
        self.assertFalse(os.path.exists(os.path.join(asset_dir, "cube.glb")))

    def test_stages_run_in_order_each_on_the_one_before_and_the_work_area_is_cleared(self):
        seen = []

        def first(source, work, record, profile):
            seen.append(("first", os.path.basename(source), record["size"], profile["name"]))
            return copy_stage(source, work, record, profile)[0], {"note": 1}

        def second(source, work, record, profile):
            seen.append(("second", os.path.basename(source)))
            target = os.path.join(work, "second.glb")
            shutil.copyfile(source, target)
            return target, {}
        asset_dir = self.approved(self.cube())
        record = self.build(asset_dir, stages=(first, second))
        self.assertEqual(seen, [("first", "raw_output.glb", 0.8, "pit"), ("second", "copy.glb")])
        self.assertEqual(record["stages"], [{"name": "first", "note": 1}, {"name": "second"}])
        self.assertEqual(sorted(os.listdir(asset_dir)),
                         [RECORD_NAME, "cube.glb", "raw_output.glb", "review"])

    def test_a_stage_that_breaks_leaves_the_approval_and_the_raw_output_but_no_model(self):
        def broken(source, work, record, profile):
            raise KilnError("the stage broke")
        asset_dir = self.approved(self.cube())
        with self.assertRaisesRegex(KilnError, "the stage broke"):
            self.build(asset_dir, stages=(broken,))
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        self.assertEqual(review.state(read_record(asset_dir)), "approved")

    def test_a_stage_that_breaks_on_a_built_asset_leaves_its_model_and_record_as_they_were(self):
        def broken(source, work, record, profile):
            raise KilnError("the stage broke")
        asset_dir = self.approved(self.cube())
        built = self.build(asset_dir, stages=(copy_stage,))
        with self.assertRaisesRegex(KilnError, "the stage broke"):
            self.build(asset_dir, stages=(broken,))
        self.assertEqual(read_record(asset_dir), built)
        self.assertEqual(sha256_of(os.path.join(asset_dir, "cube.glb")), built["model"]["sha256"])
        self.assertEqual(sorted(os.listdir(asset_dir)),
                         [RECORD_NAME, "cube.glb", "raw_output.glb", "review"])


# ---- the command line ----------------------------------------------------------------------

class CommandLine(RunCase):
    def setUp(self):
        super().setUp()
        without_tools(self)
        patch = mock.patch.object(kiln_run, "STAGES", (copy_stage,))
        patch.start()
        self.addCleanup(patch.stop)

    def arguments(self, **changed):
        given = {"--model": self.cube(), "--size": "0.8", "--profile": "pit",
                 "--licence": "CC0 1.0", "--source": "modelled by a test", "--store": self.store,
                 "--profiles": self.profiles}
        given.update(changed)
        return ["run"] + [part for pair in given.items() if pair[1] is not None for part in pair]

    def review(self, *argv):
        return self.command("review", "--store", self.store, "--profiles", self.profiles, *argv)

    def test_a_run_stops_for_the_shape_review_saying_where_the_pictures_are_and_how_to_decide(self):
        code, out, err = self.command(*self.arguments())
        self.assertEqual((code, err), (0, ""))
        asset_dir = os.path.join(self.store, "cube")
        for part in ("waiting for its shape review", "Nothing is built yet",
                     os.path.join(asset_dir, "review", "shape"), "front, closest", "index.html",
                     f"python3 -m kiln review cube --approve --store {self.store}",
                     f"python3 -m kiln review cube --reject --store {self.store}"):
            self.assertIn(part, out)
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        self.assertIsNone(read_record(asset_dir)["checks"])

    def test_approving_builds_the_asset_and_prints_each_check_and_where_it_is(self):
        self.command(*self.arguments())
        code, out, err = self.review("cube", "--approve", "--note", "the right shape")
        self.assertEqual((code, err), (0, ""))
        for part in ("shape review approved", "validator_errors", "triangle_count",
                     "measured 12 triangles", "limit 20,000",
                     os.path.join(self.store, "cube", "cube.glb"), RECORD_NAME):
            self.assertIn(part, out)
        record = read_record(os.path.join(self.store, "cube"))
        self.assertTrue(record["passed"])
        self.assertEqual((record["shape_review"]["decision"], record["shape_review"]["note"]),
                         ("approved", "the right shape"))

    def test_rejecting_ends_the_run_with_no_finished_asset(self):
        self.command(*self.arguments())
        asset_dir = os.path.join(self.store, "cube")
        with mock.patch.object(kiln_run, "build", side_effect=AssertionError("built")):
            code, out, err = self.review("cube", "--reject", "--note", "two legs short")
        self.assertEqual((code, err), (0, ""))
        for part in ("shape review rejected", "nothing is built", asset_dir):
            self.assertIn(part, out)
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        record = read_record(asset_dir)
        self.assertEqual((record["shape_review"]["decision"], record["shape_review"]["note"]),
                         ("rejected", "two legs short"))
        self.assertEqual((record["checks"], record["passed"], record["model"]),
                         (None, None, None))
        # And it stays ended: it cannot be approved afterwards.
        code, out, err = self.review("cube", "--approve")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("already decided: rejected", err)
        self.assertFalse(os.path.exists(os.path.join(asset_dir, "cube.glb")))

    def test_review_with_no_decision_says_where_the_review_stands(self):
        self.command(*self.arguments())
        code, out, _ = self.review("cube")
        self.assertEqual(code, 0)
        self.assertIn("waiting for its shape review", out)
        self.assertIn("--approve", out)
        self.review("cube", "--reject", "--note", "too tall")
        code, out, _ = self.review("cube")
        self.assertEqual(code, 0)
        self.assertRegex(out, r"shape review rejected on \d{4}-\d\d-\d\d \(too tall\)")

    def test_a_failed_check_after_approval_exits_1_naming_the_check_the_value_the_limit_and_the_overshoot(self):
        self.profile("pit", "triangle_budget = 10\n")
        self.command(*self.arguments())
        code, out, err = self.review("cube", "--approve")
        self.assertEqual(code, 1)
        self.assertIn("shape review approved", out)
        for part in ("stopped", "triangle_count", "measured 12 triangles", "limit 10",
                     "over by 2", "No finished model"):
            self.assertIn(part, err)

    def test_a_review_that_cannot_be_made_exits_2_with_one_plain_line(self):
        code, out, err = self.review("nothing")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("no asset named 'nothing'", err)
        self.command(*self.arguments())
        shutil.rmtree(os.path.join(self.store, "cube", "review"))
        for decision in ("--approve", "--reject"):
            code, out, err = self.review("cube", decision)
            self.assertEqual((code, out), (2, ""))
            self.assertIn("the review picture 'front' is missing", err)
            self.assertIn("kiln review cube --render", err)
            self.assertNotIn("Traceback", err)
        self.assertEqual(review.state(read_record(os.path.join(self.store, "cube"))), "pending")
        code, _, err = self.review("cube", "--approve", "--reject")
        self.assertEqual(code, 2)
        code, _, err = self.review("cube", "--note", "no decision")
        self.assertEqual(code, 2)
        self.assertIn("--note goes with", err)

    def test_the_pictures_can_be_rendered_again_while_the_review_waits(self):
        self.command(*self.arguments())
        asset_dir = os.path.join(self.store, "cube")
        shutil.rmtree(os.path.join(asset_dir, "review"))
        code, out, _ = self.review("cube")
        self.assertEqual(code, 0)
        self.assertIn("the review picture 'front' is missing", out)
        code, out, err = self.review("cube", "--render")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("review pictures rendered", out)
        self.assertTrue(os.path.isfile(os.path.join(asset_dir, "review", "shape", "front.png")))
        self.assertEqual(self.review("cube", "--approve")[0], 0)
        code, _, err = self.review("cube", "--render")
        self.assertEqual(code, 2)
        self.assertIn("already decided (approved)", err)

    def test_an_approval_stands_when_the_build_cannot_run_and_says_how_to_build_later(self):
        self.command(*self.arguments())

        def broken(source, work, record, profile):
            raise KilnError("the stage broke")
        with mock.patch.object(kiln_run, "STAGES", (broken,)):
            code, _, err = self.review("cube", "--approve")
        self.assertEqual(code, 2)
        self.assertIn("the stage broke", err)
        self.assertIn("python3 -m kiln rebuild cube", err)
        self.assertEqual(review.state(read_record(os.path.join(self.store, "cube"))), "approved")
        code, out, _ = self.command("rebuild", "--store", self.store, "--profiles", self.profiles)
        self.assertEqual(code, 0, out)
        self.assertIn("cube: rebuilt, changed", out)

    def test_the_licence_the_source_the_size_and_the_profile_must_be_given(self):
        for missing in ("--licence", "--source", "--size", "--profile", "--model"):
            code, _, err = self.command(*self.arguments(**{missing: None}))
            self.assertEqual(code, 2, missing)
            self.assertIn(missing, err)
        self.assertFalse(os.path.exists(self.store))

    def test_an_input_that_cannot_be_used_exits_2_with_one_plain_line(self):
        for changed, expected in (({"--model": self.path("missing.glb")}, "no model file"),
                                  ({"--size": "0"}, "positive number of metres"),
                                  ({"--profile": "desert"}, "no target profile")):
            code, out, err = self.command(*self.arguments(**changed))
            self.assertEqual((code, out), (2, ""))
            self.assertIn(expected, err)
            self.assertTrue(err.startswith("kiln run: "))
            self.assertNotIn("Traceback", err)

    def test_the_kiln_command_knows_its_commands(self):
        code, out, _ = self.command("measure", self.cube(), "--no-validator")
        self.assertEqual(code, 0)
        self.assertIn("COUNTS", out)
        code, _, err = self.command("fire")
        self.assertEqual(code, 2)
        self.assertIn("no command 'fire'", err)
        self.assertEqual(self.command()[0], 2)


# ---- with the pinned tools -----------------------------------------------------------------

def figures(report):
    """The figures of a measurement report that scaling must leave as they were."""
    uv = report["uvs"] or {}
    return {"triangles": report["totals"]["triangles"],
            "vertices": report["totals"]["vertices"],
            "meshes": report["totals"]["meshes"],
            "materials": [m["name"] for m in report["materials"]],
            "textures": [(t["format"], t["width"], t["height"], t["bytes"])
                         for t in report["textures"]],
            "islands": uv.get("islands"), "edges": uv.get("edges"),
            "seam_edges": uv.get("seam_edges"), "open_edges": uv.get("open_edges"),
            "coverage": uv.get("coverage")}


@needs_tools
class ScalingToSize(RunCase):
    def setUp(self):
        super().setUp()
        without_renderer(self)

    def finished(self, model, size=0.8, **more):
        asset_dir, record = self.run_and_approve(model, size=size, **more)
        self.assertTrue(record["passed"], record["checks"])
        return os.path.join(asset_dir, record["model"]["path"]), record

    def assert_size(self, path, size):
        largest = measure(path, validator=None)["bounding_box"]["largest_dimension"]
        self.assertLessEqual(abs(largest - size), SIZE_TOLERANCE * size,
                             f"largest dimension {largest}, size {size}")

    def test_the_largest_dimension_of_the_finished_model_is_the_size(self):
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(*quad(width=3.0, height=5.0))]))
        model = b.write(self.path("slab.glb"))
        for size in (0.8, 12.5, 0.01):
            path, record = self.finished(model, size=size, name=f"slab_{str(size).replace('.', '_')}")
            self.assert_size(path, size)
            self.assertAlmostEqual(record["stages"][0]["scale_factor"], size / 5.0, places=9)
            self.assertEqual(record["stages"][0]["name"], "scale_to_size")

    def test_the_size_is_met_as_the_scene_places_the_model_and_nodes_are_left_plain(self):
        # One mesh under a moved, turned and stretched node inside a scaled parent, and the
        # same mesh placed a second time elsewhere: the size is that of the whole scene.
        b = GlbBuilder()
        mesh = b.mesh([b.primitive(*cube_cross(), material=b.material("m", b.image(png(8, 8))))])
        half = math.sqrt(0.5)
        child = b.node(mesh, root=False, rotation=[0, 0, half, half], translation=[1, 2, 3],
                       scale=[1, 2, 1])
        b.node(children=[child], scale=[2, 2, 2], translation=[0, 1, 0])
        b.node(mesh, translation=[-5, 0, 0])
        model = b.write(self.path("tree.glb"))
        before = measure(model, validator=None)
        path, record = self.finished(model, size=0.8)
        after = measure(path, validator=None)
        self.assert_size(path, 0.8)
        factor = 0.8 / before["bounding_box"]["largest_dimension"]
        for key in ("min", "max"):
            for was, now in zip(before["bounding_box"][key], after["bounding_box"][key]):
                self.assertAlmostEqual(was * factor, now, places=6)
        self.assertEqual(after["totals"]["triangles"], before["totals"]["triangles"])
        self.assertEqual(after["uvs"]["islands"], before["uvs"]["islands"])
        self.assertEqual(after["uvs"]["seam_edges"], before["uvs"]["seam_edges"])
        nodes = load(path).json["nodes"]
        self.assertEqual(len(nodes), 2)  # one per placement; the parent that drew nothing is gone
        for node in nodes:
            self.assertFalse({"translation", "rotation", "scale", "matrix", "children"} & set(node))

    def test_normals_and_facing_follow_a_turned_and_a_mirrored_node(self):
        # A square facing +Z, once turned a quarter turn about X (so it faces -Y) and once
        # mirrored in Z (so it faces -Z). Stored normals must point the new way, and the
        # triangles must still wind the way their normals point.
        positions, uvs, indices = quad()
        b = GlbBuilder()
        for name, transform in (("turned", {"rotation": [math.sqrt(0.5), 0, 0, math.sqrt(0.5)]}),
                                ("mirrored", {"scale": [1, 1, -1], "translation": [3, 0, 0]})):
            b.node(b.mesh([b.primitive(positions, uvs, indices, normals=[(0, 0, 1)] * 4)],
                          name=name), **transform)
        path, _ = self.finished(b.write(self.path("facing.glb")), size=4.0)
        model = load(path)
        expected = {"turned": (0.0, -1.0, 0.0), "mirrored": (0.0, 0.0, -1.0)}
        self.assertEqual(sorted(m["name"] for m in model.json["meshes"]), sorted(expected))
        for mesh in model.json["meshes"]:
            primitive = mesh["primitives"][0]
            flat, _ = model.accessor(primitive["attributes"]["POSITION"])
            normals, _ = model.accessor(primitive["attributes"]["NORMAL"])
            order, _ = model.accessor(primitive["indices"])
            points = [flat[i:i + 3] for i in range(0, len(flat), 3)]
            for i in range(0, len(normals), 3):
                for got, want in zip(normals[i:i + 3], expected[mesh["name"]]):
                    self.assertAlmostEqual(got, want, places=5, msg=mesh["name"])
            for t in range(0, len(order), 3):
                a, b_, c = (points[order[t + k]] for k in range(3))
                u = [b_[k] - a[k] for k in range(3)]
                v = [c[k] - a[k] for k in range(3)]
                facing = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2],
                          u[0] * v[1] - u[1] * v[0])
                dot = sum(f * w for f, w in zip(facing, expected[mesh["name"]]))
                self.assertGreater(dot, 0, f"{mesh['name']}: a triangle faces away from its normal")

    def test_a_jpeg_texture_comes_out_as_the_same_jpeg(self):
        positions, uvs, indices = cube_cross()
        b = GlbBuilder()
        picture = jpeg()
        material = b.material("painted", b.image(picture, mime="image/jpeg", name="paint"))
        b.node(b.mesh([b.primitive(positions, uvs, indices, material)]))
        path, _ = self.finished(b.write(self.path("painted.glb")))
        model = load(path)
        self.assertEqual([image["mimeType"] for image in model.json["images"]], ["image/jpeg"])
        self.assertEqual(model.image_bytes(0), picture)

    def test_a_model_with_no_extent_stops_the_run_and_leaves_nothing(self):
        b = GlbBuilder()
        b.node(b.mesh([b.primitive([(1, 1, 1)] * 3, None, [0, 1, 2])]))
        with self.assertRaisesRegex(KilnError, "no extent"):
            self.run_and_approve(b.write(self.path("dot.glb")))
        self.assertFalse(os.path.exists(os.path.join(self.store, "dot", "dot.glb")))


@needs_tools
class WholeRuns(RunCase):
    """Whole runs with the real Blender and validator. The review pictures are stood in for:
    ReviewPicturesForReal renders them."""

    def setUp(self):
        super().setUp()
        without_renderer(self)

    def run_then_approve(self, *run_arguments):
        """`kiln run` then `kiln review --approve`: the approval's (exit code, stdout, stderr)."""
        code, out, err = self.command("run", *run_arguments, "--store", self.store,
                                      "--profiles", self.profiles)
        self.assertEqual((code, err), (0, ""))
        name = out.split("'")[1]
        return self.command("review", name, "--approve", "--store", self.store,
                            "--profiles", self.profiles)

    def test_a_model_over_the_triangle_budget_stops_the_run(self):
        self.profile("tight", "triangle_budget = 10\n")
        code, out, err = self.run_then_approve(
            "--model", self.cube(), "--size", "0.8", "--profile", "tight",
            "--licence", "CC0 1.0", "--source", "modelled by a test")
        self.assertEqual(code, 1)
        for part in ("triangle_count", "measured 12 triangles", "limit 10", "over by 2"):
            self.assertIn(part, err)
        asset_dir = os.path.join(self.store, "cube")
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        record = read_record(asset_dir)
        self.assertFalse(record["passed"])
        self.assertIsNone(record["model"])
        self.assertEqual(record["checks"][0]["passed"], True)
        self.assertEqual(record["checks"][1], {"name": "triangle_count", "measured": 12,
                                               "limit": 10, "unit": "triangles", "passed": False})

    def test_both_specimens_run_and_come_out_as_they_went_in_but_for_their_size(self):
        for specimen in SPECIMENS:
            name = os.path.splitext(os.path.basename(specimen))[0]
            before_sum = sha256_of(specimen)
            code, out, err = self.run_then_approve(
                "--model", specimen, "--size", "0.8", "--profile", "pit",
                "--licence", "CC0 1.0", "--source", "kiln's first attempt")
            self.assertEqual((code, err), (0, ""), name)
            asset_dir = os.path.join(self.store, name)
            self.assertEqual(sorted(os.listdir(asset_dir)),
                             sorted([RECORD_NAME, "raw_output.glb", name + ".glb", "review"]))
            record = read_record(asset_dir)
            self.assertTrue(record["passed"])
            self.assertEqual((record["licence"], record["source"]),
                             ("CC0 1.0", "kiln's first attempt"))
            self.assertEqual(record["target_profile"]["name"], "pit")
            self.assertEqual(record["tools"]["blender"].split()[0], "5.2.2")
            self.assertTrue(record["tools"]["gltf_validator"])
            # The large files are where the record says, with its checksums.
            raw = check_file(asset_dir, record["raw_output"], "raw output")
            model = check_file(asset_dir, record["model"], "finished model")
            # The raw output is the specimen, byte for byte, and the specimen was not touched.
            self.assertEqual(record["raw_output"]["sha256"], before_sum)
            self.assertEqual(sha256_of(specimen), before_sum)
            # Scaling changed the size and nothing else that is measured.
            before, after = measure(raw, size=0.8), measure(model, size=0.8)
            self.assertEqual(figures(after), figures(before), name)
            self.assertLessEqual(abs(after["bounding_box"]["largest_dimension"] - 0.8),
                                 SIZE_TOLERANCE * 0.8)
            self.assertEqual(after["validator"]["errors"], 0)
            if before["texel_density"]:
                self.assertAlmostEqual(after["texel_density"]["pixels_per_metre"],
                                       before["texel_density"]["pixels_per_metre"], places=2)

    def test_the_same_run_twice_gives_the_same_bytes(self):
        sums = []
        for store in (self.path("one"), self.path("two", "deeper")):
            asset_dir, record = kiln_run.run(SPECIMENS[1], 0.8, "pit", "CC0 1.0", "a test",
                                             store=store, profiles_dir=self.profiles)
            kiln_run.approve(asset_dir, self.profiles, today=TODAY)
            sums.append(self.files(asset_dir))
            for large in (RECORD_NAME, "boulder_1.glb", "raw_output.glb"):
                self.assertIn(large, sums[-1])
        self.assertEqual(sums[0], sums[1])
        # And building again in place, from the asset record alone, changes nothing.
        kiln_run.build(asset_dir, profiles_dir=self.profiles)
        self.assertEqual(self.files(asset_dir), sums[1])


class Housekeeping(unittest.TestCase):
    def test_git_ignores_the_large_files_of_the_store_but_not_the_asset_record(self):
        import subprocess
        if not shutil.which("git"):
            self.skipTest("git is not installed")

        def ignored(path):
            return subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO).returncode == 0
        self.assertTrue(ignored("assets/rock/raw_output.glb"))
        self.assertTrue(ignored("assets/rock/rock.glb"))
        self.assertTrue(ignored("assets/rock/work-abc/scale_to_size.glb"))
        self.assertTrue(ignored("assets/rock/review/shape/front.png"))
        self.assertTrue(ignored("assets/rock/review/shape/index.html"))
        self.assertFalse(ignored("assets/rock/asset_record.json"))
        for kind in ("png", "jpg", "jpeg", "webp"):
            self.assertFalse(ignored("assets/rock/reference_image." + kind))
        self.assertFalse(ignored("profiles/pit.toml"))


if __name__ == "__main__":
    unittest.main()
