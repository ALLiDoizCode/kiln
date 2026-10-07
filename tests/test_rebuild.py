"""Tests for `kiln rebuild`: rebuilding assets from their kept raw outputs, and what is
reported when a large file is missing or has changed.

Most classes stand in for Blender and the validator (see tests.test_run.without_tools);
the last one starts the pinned Blender and is skipped when .tools/ does not hold it.
Every test uses a store in a temporary folder.

Run from the repo root:  python3 -m unittest
"""
import os
import shutil
import unittest
from unittest import mock

from kiln import review, run as kiln_run
from kiln.rebuild import rebuild
from kiln.record import RECORD_NAME, read_record, sha256_of, write_record
from tests.glb_fixture import GlbBuilder, cube_cross, png
from tests.test_run import (RunCase, SPECIMENS, TODAY, copy_stage, needs_tools,
                            without_renderer, without_tools)


class RebuildCase(RunCase):
    def rebuild(self, *argv):
        return self.command("rebuild", "--store", self.store, "--profiles", self.profiles, *argv)

    def sums(self, asset_dir):
        return self.files(asset_dir)


class StoodIn(RebuildCase):
    """Blender, the validator and the real stages are replaced: only rebuild's logic is tested."""

    def setUp(self):
        super().setUp()
        without_tools(self)
        patch = mock.patch.object(kiln_run, "STAGES", (copy_stage,))
        patch.start()
        self.addCleanup(patch.stop)

    def made(self, name, **more):
        """An asset run, approved at its shape review and built."""
        return self.run_and_approve(self.cube(name + ".glb"), **more)[0]

    def waiting(self, name):
        """An asset whose shape review nobody has decided."""
        return self.run_asset(self.cube(name + ".glb"))[0]

    def rejected(self, name, note=None):
        asset_dir = self.waiting(name)
        kiln_run.reject(asset_dir, note, today=TODAY)
        return asset_dir


class Rebuilding(StoodIn):
    def test_no_names_rebuilds_every_asset_with_a_record_and_nothing_else(self):
        a, b = self.made("a"), self.made("b")
        os.mkdir(os.path.join(self.store, "no_record"))
        before = [self.sums(a), self.sums(b)]
        code, out, err = self.rebuild()
        self.assertEqual(code, 0, err)
        self.assertEqual([self.sums(a), self.sums(b)], before)
        self.assertEqual(out.splitlines()[:2], ["a: rebuilt, unchanged", "b: rebuilt, unchanged"])
        self.assertIn("2 assets: 2 unchanged", out)
        self.assertEqual(os.listdir(os.path.join(self.store, "no_record")), [])

    def test_names_choose_the_assets_and_an_unknown_name_is_a_problem(self):
        self.made("a"), self.made("b")
        code, out, _ = self.rebuild("b", "nope")
        self.assertEqual(code, 1)
        self.assertIn("b: rebuilt, unchanged", out)
        self.assertNotIn("a:", out)
        self.assertIn("nope: problem: there is no asset with an asset record in the store", out)

    def test_nothing_is_taken_in_again(self):
        # There is no generator yet; this holds the rule for when there is one: rebuilding
        # reads the store and calls build(), nothing that makes a new raw output.
        self.made("a")
        with mock.patch.object(kiln_run, "take_in", side_effect=AssertionError("took in")):
            self.assertEqual(self.rebuild()[0], 0)

    def test_a_changed_profile_is_applied_and_says_what_changed(self):
        asset_dir = self.made("a")
        self.profile("pit", "triangle_budget = 30000\n")
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: rebuilt, unchanged (profile checksum; check triangle_count limit "
                      "20,000 -> 30,000)", out)
        self.assertEqual(read_record(asset_dir)["checks"][1]["limit"], 30000)

    def test_a_changed_tool_version_is_named(self):
        self.made("a")
        with mock.patch.object(kiln_run, "blender_version", lambda: "9.9"):
            code, out, _ = self.rebuild()
        self.assertIn("a: rebuilt, unchanged (blender version stand-in -> 9.9)", out)

    def test_a_changed_stage_changes_the_model_and_the_report_says_so(self):
        asset_dir = self.made("a")
        old = read_record(asset_dir)["model"]["sha256"]

        def bigger(source, work, record, profile):
            target = os.path.join(work, "bigger.glb")
            shutil.copyfile(source, target)
            with open(target, "ab") as f:
                f.write(b"\0\0\0\0")
            return target, {}
        (result,) = rebuild(self.store, self.profiles, stages=(bigger,))
        self.assertEqual(result["status"], "changed")
        self.assertIn("model checksum", result["text"])
        self.assertNotEqual(read_record(asset_dir)["model"]["sha256"], old)

    def test_an_asset_that_fails_a_check_is_named_with_the_check_and_exits_1(self):
        a = self.made("a")
        self.made("b")
        self.profile("pit", "triangle_budget = 10\n")
        code, out, _ = self.rebuild()
        self.assertEqual(code, 1)
        self.assertIn("a: failed a check", out)
        self.assertIn("  triangle_count: measured 12 triangles, limit 10, over by 2 (20.0%), "
                      "FAILED", out)
        self.assertIn("b: failed a check", out)  # one asset's failure does not stop the next
        self.assertFalse(os.path.exists(os.path.join(a, "a.glb")))
        self.assertFalse(read_record(a)["passed"])
        self.assertIn("2 assets: 2 failed a check", out)

    def test_an_asset_whose_last_build_failed_is_rebuilt_when_the_profile_is_fixed(self):
        self.profile("pit", "triangle_budget = 10\n")
        a = self.made("a")
        self.assertIsNone(read_record(a)["model"])
        self.profile("pit", "triangle_budget = 20000\n")
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: rebuilt, changed (", out)
        self.assertTrue(read_record(a)["passed"])
        self.assertTrue(os.path.exists(os.path.join(a, "a.glb")))


class MissingAndChangedFiles(StoodIn):
    def test_a_missing_raw_output_is_reported_by_name_and_path_and_others_go_on(self):
        a, b = self.made("a"), self.made("b")
        os.remove(os.path.join(a, "raw_output.glb"))
        record = read_record(a)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 1)
        self.assertIn(f"a: raw output missing: {os.path.join(a, 'raw_output.glb')}", out)
        self.assertIn("b: rebuilt, unchanged", out)
        self.assertEqual(read_record(a), record)
        self.assertTrue(os.path.exists(os.path.join(a, "a.glb")))  # nothing was touched

    def test_a_changed_raw_output_is_reported_not_built_from_and_the_record_is_left(self):
        a = self.made("a")
        raw = os.path.join(a, "raw_output.glb")
        os.chmod(raw, 0o644)
        with open(raw, "ab") as f:
            f.write(b"\0")
        self.profile("pit", "triangle_budget = 30000\n")  # a rebuild would change the record
        before = self.sums(a)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 1)
        self.assertIn(f"a: raw output changed since its asset record was written: {raw}", out)
        self.assertEqual(self.sums(a), before)

    def test_a_missing_finished_model_is_reported_then_rebuilt(self):
        a = self.made("a")
        model = os.path.join(a, "a.glb")
        old = sha256_of(model)
        os.remove(model)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: rebuilt, unchanged (the finished model was missing)", out)
        self.assertEqual(sha256_of(model), old)

    def test_a_finished_model_that_differs_from_its_record_is_reported_then_rebuilt(self):
        a = self.made("a")
        model = os.path.join(a, "a.glb")
        old = sha256_of(model)
        with open(model, "ab") as f:
            f.write(b"\0")
        code, out, _ = self.rebuild()
        self.assertIn("a: rebuilt, unchanged (the finished model had changed on disk)", out)
        self.assertEqual(sha256_of(model), old)

    def test_an_unusable_record_or_profile_is_one_assets_problem_only(self):
        a, b, c = self.made("a"), self.made("b"), self.made("c")
        with open(os.path.join(a, RECORD_NAME), "w") as f:
            f.write("{not json")
        record = read_record(b)
        record["target_profile"]["name"] = "nowhere"
        write_record(b, record)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 1)
        self.assertIn("a: problem: the asset record", out)
        self.assertIn("b: problem: there is no target profile 'nowhere'", out)
        self.assertIn("c: rebuilt, unchanged", out)


class Checking(StoodIn):
    def test_check_reports_without_writing_anything(self):
        a, b, c = self.made("a"), self.made("b"), self.made("c")
        os.remove(os.path.join(a, "raw_output.glb"))
        os.remove(os.path.join(b, "b.glb"))
        self.profile("pit", "triangle_budget = 30000\n")
        before = {d: self.sums(d) for d in (b, c)}
        code, out, _ = self.rebuild("--check")
        self.assertEqual(code, 1)
        self.assertIn(f"a: raw output missing: {os.path.join(a, 'raw_output.glb')}", out)
        self.assertIn("b: the finished model is missing; the profile has changed", out)
        self.assertIn("c: the profile has changed", out)
        self.assertEqual({d: self.sums(d) for d in (b, c)}, before)

    def test_check_exits_0_when_everything_is_as_the_record_says(self):
        self.made("a")
        code, out, _ = self.rebuild("--check")
        self.assertEqual((code, out.splitlines()[0]), (0, "a: up to date"))

    def test_check_names_an_asset_whose_last_build_failed(self):
        self.profile("pit", "triangle_budget = 10\n")
        self.made("a")
        code, out, _ = self.rebuild("--check")
        self.assertEqual(code, 1)
        self.assertIn("a: the last build failed a check", out)


class ShapeReviews(StoodIn):
    """An asset is rebuilt only when its shape review is approved, and is never asked again."""

    def test_an_asset_waiting_for_its_shape_review_is_not_built_and_is_not_a_failure(self):
        a, b = self.made("a"), self.waiting("b")
        before = self.sums(b)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: rebuilt, unchanged", out)
        self.assertIn("b: waiting for shape review (decide with `python3 -m kiln review b "
                      "--approve` or `--reject`)", out)
        self.assertIn("2 assets: 1 unchanged, 1 waiting for shape review", out)
        self.assertEqual(self.sums(b), before)
        self.assertFalse(os.path.exists(os.path.join(b, "b.glb")))

    def test_a_rejected_asset_is_not_built_and_is_not_a_failure(self):
        a = self.rejected("a", note="two legs short")
        before = self.sums(a)
        with mock.patch.object(kiln_run, "build", side_effect=AssertionError("built")):
            code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn(f"a: rejected at shape review on {TODAY} (two legs short)", out)
        self.assertIn("1 asset: 1 rejected at shape review", out)
        self.assertEqual(self.sums(a), before)
        # Not by name either.
        self.assertIn("a: rejected at shape review", self.rebuild("a")[1])
        self.assertFalse(os.path.exists(os.path.join(a, "a.glb")))

    def test_check_reports_waiting_and_rejected_assets_without_failing(self):
        self.made("a"), self.waiting("b"), self.rejected("c")
        code, out, _ = self.rebuild("--check")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "a: up to date")
        self.assertIn("b: waiting for shape review", out)
        self.assertIn(f"c: rejected at shape review on {TODAY}", out)
        self.assertIn("3 assets: 1 up to date, 1 waiting for shape review, 1 rejected at shape "
                      "review", out)

    def test_a_waiting_asset_with_no_raw_output_is_still_a_problem(self):
        b = self.waiting("b")
        os.remove(os.path.join(b, "raw_output.glb"))
        for arguments in ((), ("--check",)):
            code, out, _ = self.rebuild(*arguments)
            self.assertEqual(code, 1)
            self.assertIn("b: raw output missing", out)

    def test_an_approved_asset_is_rebuilt_without_rendering_or_deciding_again(self):
        a = self.made("a")
        approved = read_record(a)["shape_review"]
        shutil.rmtree(os.path.join(a, "review"))  # the pictures are not needed to rebuild
        self.profile("pit", "triangle_budget = 30000\n")
        with mock.patch.object(review, "render_pictures", side_effect=AssertionError("rendered")), \
                mock.patch.object(review, "decide", side_effect=AssertionError("decided")):
            code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: rebuilt, unchanged (profile checksum", out)
        self.assertEqual(read_record(a)["shape_review"], approved)

    def test_a_record_with_no_shape_review_counts_as_waiting(self):
        a = self.made("a")
        record = read_record(a)
        del record["shape_review"]
        write_record(a, record)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0)
        self.assertIn("a: waiting for shape review", out)


class StagesAndTheRawOutput(StoodIn):
    def rebuild_with(self, stage):
        return rebuild(self.store, self.profiles, stages=(stage,))

    def test_a_stage_that_writes_to_the_raw_output_is_reported_and_no_asset_results(self):
        def scribbling(source, work, record, profile):
            os.chmod(source, 0o644)  # a chmod proves nothing: the checksum is the guard
            with open(source, "ab") as f:
                f.write(b"\0")
            return copy_stage(source, work, record, profile)

        def replacing(source, work, record, profile):
            target = os.path.join(work, "other.glb")
            with open(target, "wb") as f:
                f.write(b"a different file")
            os.replace(target, source)  # a new file under the raw output's name
            return source, {}

        def deleting(source, work, record, profile):
            target, facts = copy_stage(source, work, record, profile)
            os.remove(source)
            return target, facts
        for stage in (scribbling, replacing, deleting):
            with self.subTest(stage.__name__):
                shutil.rmtree(self.store, ignore_errors=True)
                a = self.made("a")
                (result,) = self.rebuild_with(stage)
                self.assertEqual(result["status"], "problem")
                self.assertRegex(result["text"], "raw output (has changed|is missing)")
                self.assertFalse(os.path.exists(os.path.join(a, "a.glb")))

    def test_the_raw_output_is_read_only_while_the_stages_run(self):
        modes = []

        def looking(source, work, record, profile):
            modes.append(os.stat(source).st_mode & 0o222)
            return copy_stage(source, work, record, profile)
        self.made("a")
        self.rebuild_with(looking)
        self.assertEqual(modes, [0])


@needs_tools
class Repeatability(RebuildCase):
    """The same raw output, size and profile give the same bytes, with the real Blender.

    The review pictures are stood in for, and the day of the decision is fixed: neither is
    made by a build. Whether the real pictures repeat is measured in tests.test_review.
    """

    def setUp(self):
        super().setUp()
        without_renderer(self)

    def textured(self):
        b = GlbBuilder()
        material = b.material("m", b.image(png(16, 16)))
        b.node(b.mesh([b.primitive(*cube_cross(), material=material)]))
        return b.write(self.path("textured.glb"))

    def build_in(self, model, store, threads=None):
        env = dict(os.environ)
        env.pop("KILN_BLENDER_THREADS", None)
        if threads:
            env["KILN_BLENDER_THREADS"] = threads
        with mock.patch.dict(os.environ, env, clear=True):
            asset_dir, _ = kiln_run.run(model, 0.8, "pit", "CC0 1.0", "a test", store=store,
                                        profiles_dir=self.profiles)
            kiln_run.approve(asset_dir, self.profiles, today=TODAY)
        return self.sums(asset_dir)

    def test_other_store_paths_and_thread_counts_give_the_same_bytes(self):
        for model in (SPECIMENS[0], SPECIMENS[1], self.textured()):
            with self.subTest(os.path.basename(model)):
                name = os.path.splitext(os.path.basename(model))[0]
                runs = [self.build_in(model, self.path("s1"), None),
                        self.build_in(model, self.path("s2", "a", "deeper"), None),
                        self.build_in(model, self.path("s3"), "1"),
                        self.build_in(model, self.path("s4"), "3")]
                for other in runs[1:]:
                    self.assertEqual(other, runs[0])
                for large in ("asset_record.json", name + ".glb", "raw_output.glb"):
                    self.assertIn(large, runs[0])
                for store in ("s1", "s2", "s3", "s4"):
                    shutil.rmtree(self.path(store))

    def test_rebuilding_in_place_gives_the_same_bytes_and_says_unchanged(self):
        asset_dir, _ = self.run_and_approve(self.textured())
        before = self.sums(asset_dir)
        code, out, _ = self.rebuild()
        self.assertEqual(code, 0, out)
        self.assertIn("textured: rebuilt, unchanged", out)
        self.assertEqual(self.sums(asset_dir), before)


if __name__ == "__main__":
    unittest.main()
