"""Tests for the shape review: the review pictures, the decision, and what the record keeps.

The first classes stand in for the renderer (tests.test_run.stand_in_renderer), so only kiln's
own logic is tested. ReviewPicturesForReal starts the real one, `review_pictures` from
crates/asset_view, and reads the pictures it writes; it is skipped, saying why, when that
program is not built or there is no graphics card to run it on. Nothing here builds it: see
kiln.review.require_renderer for the command.

Run from the repo root:  python3 -m unittest
"""
import json
import os
import shutil
import stat
import struct
import unittest
import zlib
from unittest import mock

from kiln import KilnError, review, run as kiln_run
from kiln.record import RECORD_NAME, read_record, sha256_of
from tests.glb_fixture import GlbBuilder, cube_cross, jpeg, png
from tests.test_run import (REAL_RENDER_PICTURES, REAL_REQUIRE_RENDERER, RunCase, SPECIMENS,
                            TODAY, copy_stage, needs_tools, stand_in_renderer, without_tools)


class Reviewing(RunCase):
    def setUp(self):
        super().setUp()
        without_tools(self)
        patch = mock.patch.object(kiln_run, "STAGES", (copy_stage,))
        patch.start()
        self.addCleanup(patch.stop)


# ---- taking the pictures -------------------------------------------------------------------

class TakingPictures(Reviewing):
    def test_a_run_renders_the_pictures_of_the_raw_output_at_its_size_and_the_profiles_distance(self):
        asked = []

        def renderer(model, size, closest, out_dir):
            asked.append((model, size, closest, out_dir))
            return stand_in_renderer(model, size, closest, out_dir)
        self.profile("near", "triangle_budget = 20000\n", closest="closest_viewing_distance = 0.25\n")
        asset_dir, record = self.run_asset(self.cube("rock.glb"), size=2.5, profile="near",
                                           renderer=renderer)
        self.assertEqual(asked, [(os.path.join(asset_dir, "raw_output.glb"), 2.5, 0.25,
                                  os.path.join(asset_dir, "review", "shape"))])
        self.assertEqual(sorted(os.listdir(os.path.join(asset_dir, "review", "shape"))),
                         ["closest.png", "front.png", "index.html"])
        self.assertEqual(record, read_record(asset_dir))

    def test_the_record_names_the_pictures_with_checksums_and_how_they_were_taken(self):
        asset_dir, record = self.run_asset()
        picture = sha256_of(os.path.join(asset_dir, "review", "shape", "front.png"))
        self.assertEqual(record["shape_review"], {
            "decision": None, "note": None, "decided_on": None,
            "pictures": {"view_set": 1, "closest_viewing_distance": 0.5, "picture_size": [4, 3],
                         "renderer": {"name": "stand-in", "version": "0"},
                         "views": [{"name": "front", "path": "review/shape/front.png",
                                    "sha256": picture},
                                   {"name": "closest", "path": "review/shape/closest.png",
                                    "sha256": picture}]}})
        self.assertEqual(review.state(record), "pending")
        self.assertEqual((record["checks"], record["model"]), (None, None))

    def test_the_run_stops_there_and_builds_nothing(self):
        with mock.patch.object(kiln_run, "build", side_effect=AssertionError("built")):
            asset_dir, _ = self.run_asset()
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])

    def test_the_raw_output_is_only_read(self):
        asset_dir, record = self.run_asset()
        raw = os.path.join(asset_dir, "raw_output.glb")
        self.assertEqual(sha256_of(raw), record["raw_output"]["sha256"])
        self.assertFalse(os.stat(raw).st_mode & 0o222)

        def scribbling(model, size, closest, out_dir):
            os.chmod(model, 0o644)
            with open(model, "ab") as f:
                f.write(b"\0\0\0\0")
            return stand_in_renderer(model, size, closest, out_dir)
        with self.assertRaisesRegex(KilnError, "raw output has changed"):
            self.run_asset(self.cube("other.glb"), renderer=scribbling)

    def test_a_run_whose_pictures_cannot_be_rendered_leaves_nothing_in_the_store(self):
        def broken(model, size, closest, out_dir):
            raise KilnError("the review pictures could not be rendered")

        def one_missing(model, size, closest, out_dir):
            report = stand_in_renderer(model, size, closest, out_dir)
            os.remove(os.path.join(out_dir, "closest.png"))
            return report

        def wrong_size(model, size, closest, out_dir):
            report = stand_in_renderer(model, size, closest, out_dir)
            report["picture_size"] = [1920, 1080]
            return report

        def not_a_picture(model, size, closest, out_dir):
            report = stand_in_renderer(model, size, closest, out_dir)
            with open(os.path.join(out_dir, "front.png"), "wb") as f:
                f.write(b"")
            return report

        def none(model, size, closest, out_dir):
            return {**stand_in_renderer(model, size, closest, out_dir), "views": []}
        for renderer, expected in ((broken, "could not be rendered"),
                                   (one_missing, "review picture 'closest' was not written"),
                                   (wrong_size, "1920 x 1080"),
                                   (not_a_picture, "review picture 'front' was not written"),
                                   (none, "wrote no review pictures")):
            with self.assertRaisesRegex(KilnError, expected):
                self.run_asset(renderer=renderer)
            self.assertEqual(os.listdir(self.store), [], renderer.__name__)

    def test_rendering_again_replaces_the_pictures_while_the_review_waits(self):
        asset_dir, record = self.run_asset()
        stray = os.path.join(asset_dir, "review", "shape", "old_view.png")
        with open(stray, "wb") as f:
            f.write(png(4, 3))
        again = review.take_pictures(asset_dir, self.profiles)
        self.assertEqual(again["shape_review"], record["shape_review"])
        self.assertFalse(os.path.exists(stray))

    def test_pictures_are_not_rendered_again_once_the_review_is_decided(self):
        for decision in review.DECISIONS:
            asset_dir, _ = self.run_asset(name=decision)
            review.decide(asset_dir, decision, today=TODAY)
            before = self.files(asset_dir)
            with self.assertRaisesRegex(KilnError, f"already decided \\({decision}\\)"):
                review.take_pictures(asset_dir, self.profiles)
            self.assertEqual(self.files(asset_dir), before)

    def test_the_page_shows_the_reference_image_beside_every_picture(self):
        picture = self.path("goal.png")
        with open(picture, "wb") as f:
            f.write(png(2, 2))
        asset_dir, _ = self.run_asset(reference_image=picture)
        with open(os.path.join(asset_dir, "review", "shape", "index.html"), encoding="utf-8") as f:
            page = f.read()
        for part in ('src="../../reference_image.png"', 'src="front.png"', 'src="closest.png"',
                     "the front &lt;view&gt;", "Shape review: cube", "size 0.8 m",
                     "closest viewing distance 0.5 m", "kiln review cube --approve"):
            self.assertIn(part, page)
        self.assertTrue(os.path.isfile(os.path.join(asset_dir, "reference_image.png")))

    def test_the_page_says_so_when_there_is_no_reference_image(self):
        asset_dir, _ = self.run_asset()
        with open(os.path.join(asset_dir, "review", "shape", "index.html"), encoding="utf-8") as f:
            self.assertIn("No reference image was given", f.read())


# ---- the decision --------------------------------------------------------------------------

class Deciding(Reviewing):
    def test_approval_is_written_with_the_note_the_day_and_the_pictures_it_was_made_on(self):
        asset_dir, waiting = self.run_asset()
        record = review.decide(asset_dir, "approved", note="  matches the picture ", today=TODAY)
        self.assertEqual(record, read_record(asset_dir))
        made = record["shape_review"]
        self.assertEqual((made["decision"], made["note"], made["decided_on"]),
                         ("approved", "matches the picture", TODAY))
        self.assertEqual(made["pictures"], waiting["shape_review"]["pictures"])
        self.assertEqual(review.state(record), "approved")
        self.assertEqual(list(made), ["decision", "note", "decided_on", "pictures"])

    def test_rejection_is_written_the_same_way_and_nothing_is_built(self):
        asset_dir, _ = self.run_asset()
        record = kiln_run.reject(asset_dir, today=TODAY)
        self.assertEqual((record["shape_review"]["decision"], record["shape_review"]["note"]),
                         ("rejected", None))
        self.assertEqual(review.state(read_record(asset_dir)), "rejected")
        self.assertEqual(sorted(os.listdir(asset_dir)), [RECORD_NAME, "raw_output.glb", "review"])
        self.assertEqual((record["checks"], record["passed"], record["model"]), (None, None, None))

    def test_the_day_is_today_unless_given(self):
        asset_dir, _ = self.run_asset()
        day = review.decide(asset_dir, "rejected")["shape_review"]["decided_on"]
        self.assertRegex(day, r"\A\d{4}-\d\d-\d\d\Z")

    def test_a_decision_is_made_once(self):
        for first in review.DECISIONS:
            asset_dir, _ = self.run_asset(name="made_" + first)
            review.decide(asset_dir, first, today=TODAY)
            before = self.files(asset_dir)
            for second in review.DECISIONS:
                with self.assertRaisesRegex(KilnError, f"already decided: {first} on {TODAY}"):
                    review.decide(asset_dir, second)
            self.assertEqual(self.files(asset_dir), before)

    def test_only_approved_or_rejected_can_be_decided(self):
        asset_dir, _ = self.run_asset()
        with self.assertRaisesRegex(KilnError, "approved or rejected"):
            review.decide(asset_dir, "maybe")

    def test_a_decision_needs_the_pictures_the_record_names(self):
        asset_dir, _ = self.run_asset()
        front = os.path.join(asset_dir, "review", "shape", "front.png")
        with open(front, "wb") as f:
            f.write(png(5, 5))
        with self.assertRaisesRegex(KilnError, "review picture 'front' is not the one that was "
                                               "rendered"):
            review.decide(asset_dir, "approved")
        os.remove(front)
        with self.assertRaisesRegex(KilnError, "review picture 'front' is missing"):
            review.decide(asset_dir, "rejected")
        self.assertEqual(review.state(read_record(asset_dir)), "pending")
        # An asset taken in whose pictures were never rendered cannot be decided either.
        bare = self.take_in(self.cube("bare.glb"))
        with self.assertRaisesRegex(KilnError, "no review pictures have been rendered"):
            review.decide(bare, "approved")

    def test_an_asset_is_built_only_once_approved(self):
        asset_dir, _ = self.run_asset()
        with self.assertRaisesRegex(KilnError, "not built: its shape review is pending"):
            kiln_run.build(asset_dir, self.profiles)
        rejected, _ = self.run_asset(name="other")
        kiln_run.reject(rejected, today=TODAY)
        with self.assertRaisesRegex(KilnError, "not built: its shape review is rejected"):
            kiln_run.build(rejected, self.profiles)
        for folder in (asset_dir, rejected):
            self.assertEqual(sorted(os.listdir(folder)), [RECORD_NAME, "raw_output.glb", "review"])
        record = kiln_run.approve(asset_dir, self.profiles, today=TODAY)
        self.assertTrue(record["passed"])
        self.assertTrue(os.path.isfile(os.path.join(asset_dir, "cube.glb")))


# ---- finding and starting the renderer -----------------------------------------------------

class TheRenderer(RunCase):
    """kiln.review's own dealings with the renderer, with small scripts in its place."""

    def setUp(self):
        super().setUp()
        self.out = self.path("pictures")
        os.mkdir(self.out)

    def program(self, script):
        """A program at a path of its own that runs this shell script."""
        path = self.path("renderer")
        with open(path, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n" + script)
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
        return mock.patch.dict(os.environ, {"KILN_REVIEW_RENDERER": path})

    def test_it_is_started_with_the_model_the_size_the_distance_and_the_folder(self):
        with self.program('echo "some chatter"\necho "{\\"arguments\\": \\"$*\\"}"\n'):
            report = review.render_pictures("rock.glb", 0.8, 2, self.out)
        self.assertEqual(report, {"arguments": f"rock.glb --size 0.8 --closest 2.0 --out {self.out}"})

    def test_a_renderer_that_fails_is_reported_with_what_it_said(self):
        with self.program('echo "2026 INFO bevy: starting" >&2\n'
                          'echo "review_pictures: the model holds no mesh" >&2\nexit 1\n'):
            with self.assertRaises(KilnError) as caught:
                review.render_pictures("rock.glb", 0.8, 0.5, self.out)
        self.assertIn("could not be rendered (exit status 1)", str(caught.exception))
        self.assertIn("the model holds no mesh", str(caught.exception))
        self.assertNotIn("starting", str(caught.exception))

    def test_a_renderer_that_says_nothing_is_not_taken_as_success(self):
        for script in ("exit 0\n", 'echo "not json"\n'):
            with self.program(script), self.assertRaisesRegex(KilnError, "did not say what it wrote"):
                review.render_pictures("rock.glb", 0.8, 0.5, self.out)

    def test_a_renderer_that_never_ends_is_given_up_on(self):
        with self.program("sleep 30\n"), mock.patch.object(review, "RENDER_LIMIT", 0.2):
            with self.assertRaisesRegex(KilnError, "not rendered in 0.2 seconds"):
                review.render_pictures("rock.glb", 0.8, 0.5, self.out)

    def test_it_is_looked_for_in_cargos_release_folder(self):
        with mock.patch.dict(os.environ, {"CARGO_TARGET_DIR": self.path("built")}):
            os.environ.pop("KILN_REVIEW_RENDERER", None)
            self.assertEqual(review.renderer_path(),
                             self.path("built", "release", "review_pictures"))
            with self.assertRaisesRegex(KilnError, "is not built.*cargo build --release"):
                review.require_renderer()

    def test_a_renderer_older_than_its_source_is_refused(self):
        source = self.path("src")
        os.makedirs(os.path.join(source, "bin"))
        os.makedirs(self.path("built", "release"))
        binary = self.path("built", "release", "review_pictures")
        for path in (binary, os.path.join(source, "views.rs"), os.path.join(source, "main.rs"),
                     os.path.join(source, "bin", "review_pictures.rs")):
            with open(path, "w") as f:
                f.write("")
            os.utime(path, (1000, 1000))
        with mock.patch.dict(os.environ, {"CARGO_TARGET_DIR": self.path("built")}), \
                mock.patch.object(review, "RENDERER_SOURCE", source):
            os.environ.pop("KILN_REVIEW_RENDERER", None)
            self.assertEqual(review.require_renderer(), binary)
            os.utime(os.path.join(source, "main.rs"), (2000, 2000))  # the viewer, not the renderer
            self.assertEqual(review.require_renderer(), binary)
            os.utime(os.path.join(source, "bin", "review_pictures.rs"), (2000, 2000))
            with self.assertRaisesRegex(KilnError, "older than its source.*cargo build --release"):
                review.require_renderer()

    def test_the_size_of_a_png_is_read_from_its_header(self):
        path = self.path("p.png")
        with open(path, "wb") as f:
            f.write(png(7, 5))
        self.assertEqual(review.png_size(path), (7, 5))
        with open(path, "wb") as f:
            f.write(b"\x89PNG and then nothing a picture has")
        self.assertIsNone(review.png_size(path))
        self.assertIsNone(review.png_size(self.path("missing.png")))


# ---- with the real renderer ----------------------------------------------------------------

def read_png(path, rows=None):
    """Decode an 8-bit RGB PNG with the standard library: (width, height, the first `rows`
    rows, each as bytes of r, g, b per pixel). All rows if `rows` is None."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    at, packed = 8, []
    while at < len(data):
        length, kind = struct.unpack(">I4s", data[at:at + 8])
        body = data[at + 8:at + 8 + length]
        at += 12 + length
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if (depth, colour, interlace) != (8, 2, 0):
                raise ValueError(f"{path} is not a plain 8-bit RGB PNG")
        elif kind == b"IDAT":
            packed.append(body)
    raw = zlib.decompress(b"".join(packed))
    stride = width * 3
    out, above = [], bytes(stride)
    for y in range(height if rows is None else min(rows, height)):
        start = y * (stride + 1)
        kind, line = raw[start], bytearray(raw[start + 1:start + 1 + stride])
        if kind == 1:
            for i in range(3, stride):
                line[i] = (line[i] + line[i - 3]) & 255
        elif kind == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, above))
        elif kind == 3:
            for i in range(stride):
                left = line[i - 3] if i >= 3 else 0
                line[i] = (line[i] + ((left + above[i]) >> 1)) & 255
        elif kind == 4:
            for i in range(stride):
                left = line[i - 3] if i >= 3 else 0
                up = above[i]
                corner = above[i - 3] if i >= 3 else 0
                guess = left + up - corner
                to_left, to_up, to_corner = abs(guess - left), abs(guess - up), abs(guess - corner)
                near = left if to_left <= to_up and to_left <= to_corner else (
                    up if to_up <= to_corner else corner)
                line[i] = (line[i] + near) & 255
        out.append(bytes(line))
        above = line
    return width, height, out


def pixel(rows, x, y):
    return tuple(rows[y][3 * x:3 * x + 3])


def strongest(colour):
    """Which of red, green and blue a colour is most: the names of its channels above half
    of its brightest, e.g. "r" for red and "gb" for cyan."""
    return "".join(name for name, value in zip("rgb", colour) if value > max(colour) * 0.6)


# The faces of the test cube, each in a colour of its own: glTF's front is +Z, up is +Y.
FACE_COLOURS = {"front": (1, 0, 0), "right": (0, 1, 0), "back": (0, 1, 1), "left": (1, 0, 1),
                "top": (0, 0, 1), "bottom": (1, 1, 0)}
FACES = {"front": [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
         "right": [(1, 0, 1), (1, 0, 0), (1, 1, 0), (1, 1, 1)],
         "back": [(1, 0, 0), (0, 0, 0), (0, 1, 0), (1, 1, 0)],
         "left": [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
         "top": [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)],
         "bottom": [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]}
NORMALS = {"front": (0, 0, 1), "right": (1, 0, 0), "back": (0, 0, -1), "left": (-1, 0, 0),
           "top": (0, 1, 0), "bottom": (0, -1, 0)}


def renderer_or_reason():
    """(the renderer's path, None), or (None, why the real renderer cannot be used here)."""
    try:
        return REAL_REQUIRE_RENDERER(), None
    except KilnError as error:
        return None, str(error)


RENDERER, NO_RENDERER = renderer_or_reason()


@unittest.skipUnless(RENDERER, f"the review pictures are not rendered for real: {NO_RENDERER}")
class ReviewPicturesForReal(RunCase):
    """Starts the real renderer. Each render takes a few seconds and needs a graphics card."""

    def painted_cube(self):
        """A cube with each face a colour of its own, three times too large, off to one side
        and above the ground in its file: the pictures must show it at its size all the same."""
        b = GlbBuilder()
        primitives = []
        for face, corners in FACES.items():
            material = b.material(face, pbrMetallicRoughness={
                "baseColorFactor": [*FACE_COLOURS[face], 1], "metallicFactor": 0,
                "roughnessFactor": 1})
            primitives.append(b.primitive(corners, None, [0, 1, 2, 0, 2, 3], material,
                                          normals=[NORMALS[face]] * 4))
        b.node(b.mesh(primitives), scale=[3, 3, 3], translation=[40, 7, -20])
        return b.write(self.path("painted.glb"))

    def render(self, model, out="pictures", size=0.8, closest=0.5):
        out_dir = self.path(out)
        os.makedirs(out_dir, exist_ok=True)
        try:
            return out_dir, REAL_RENDER_PICTURES(model, size, closest, out_dir)
        except KilnError as error:
            if "Unable to find a GPU" in str(error):
                self.skipTest("there is no graphics card to render on")
            raise

    def test_every_picture_shows_the_side_it_is_named_for(self):
        out_dir, report = self.render(self.painted_cube())
        names = [view["name"] for view in report["views"]]
        self.assertEqual(names, ["front", "right", "back", "left", "top", "three_quarter",
                                 "standing", "closest"])
        self.assertEqual(sorted(os.listdir(out_dir)), sorted(name + ".png" for name in names))
        self.assertEqual(report["picture_size"], [1920, 1080])
        self.assertEqual(report["view_set"], 1)
        self.assertEqual(report["meshes"], 6)  # Bevy makes one mesh of each primitive
        self.assertAlmostEqual(report["scale_factor"], 0.8 / 3, places=5)
        for part in ("name", "version", "bevy", "graphics_card"):
            self.assertTrue(report["renderer"][part], part)

        middle = {}
        for name in names:
            # Up to the middle row is enough to read the middle of the picture.
            width, height, rows = read_png(os.path.join(out_dir, name + ".png"), rows=541)
            self.assertEqual((width, height), (1920, 1080), name)
            middle[name] = pixel(rows, 960, 540)
            self.assertGreater(len({pixel(rows, x, y) for y in range(0, 541, 20)
                                    for x in range(0, 1920, 20)}), 3, f"{name} is one flat colour")
        # The face each picture looks straight at, by its colour in the middle of the picture.
        for name, face in (("front", "front"), ("right", "right"), ("back", "back"),
                           ("left", "left"), ("top", "top"), ("closest", "front")):
            self.assertEqual(strongest(middle[name]), strongest(FACE_COLOURS[face]),
                             f"{name}: the middle of the picture is {middle[name]}")

        # The corner picture holds the front, the right and the top at once, and the ground.
        _, _, rows = read_png(os.path.join(out_dir, "three_quarter.png"))
        seen = {strongest(pixel(rows, x, y)) for y in range(0, 1080, 6) for x in range(0, 1920, 6)}
        for face in ("front", "right", "top"):
            self.assertIn(strongest(FACE_COLOURS[face]), seen, face)
        # The top picture has the front at the bottom: no red anywhere, the cube in the middle.
        self.assertEqual(strongest(middle["top"]), "b")

    def test_the_asset_is_as_large_in_the_picture_whatever_scale_its_file_has(self):
        # The same cube, in a file where it is 1 across and in one where it is 250 across.
        widths = []
        for n, scale in enumerate((1, 250)):
            b = GlbBuilder()
            material = b.material("red", pbrMetallicRoughness={"baseColorFactor": [1, 0, 0, 1]})
            b.node(b.mesh([b.primitive(*cube_cross(), material=material)]),
                   scale=[scale] * 3, translation=[5 * scale, 0, 0])
            out_dir, _ = self.render(b.write(self.path(f"cube{n}.glb")), out=f"scale{n}")
            _, _, rows = read_png(os.path.join(out_dir, "front.png"), rows=541)
            row = rows[540]
            widths.append(sum(1 for x in range(1920) if strongest(row[3 * x:3 * x + 3]) == "r"))
        self.assertEqual(widths[0], widths[1])
        # 0.8 m wide, its front face 1.6 m from the eye, 30 degrees of view up and down.
        self.assertAlmostEqual(widths[0], 0.8 / 1.6 / (2 * 0.26795) * 1080, delta=4)

    def test_png_and_jpeg_textures_are_drawn(self):
        for kind, picture, mime in (("png", png(8, 8), "image/png"), ("jpeg", jpeg(), "image/jpeg")):
            b = GlbBuilder()
            material = b.material("m", b.image(picture, mime=mime))
            b.node(b.mesh([b.primitive(*cube_cross(), material=material)]))
            out_dir, _ = self.render(b.write(self.path(kind + ".glb")), out=kind)
            _, _, rows = read_png(os.path.join(out_dir, "closest.png"), rows=541)
            colour = pixel(rows, 960, 540)
            # The PNG is grey and the JPEG brown: neither is the white of a missing texture.
            self.assertLess(max(colour), 200, f"{kind}: {colour}")
            if kind == "jpeg":
                self.assertGreater(colour[0], colour[2] + 20, f"the brown came out {colour}")

    def test_a_model_that_cannot_be_shown_fails_and_leaves_no_picture(self):
        broken = self.path("broken.glb")
        with open(broken, "wb") as f:
            f.write(b"not a model")
        b = GlbBuilder()
        b.node(b.mesh([b.primitive([(1, 1, 1)] * 3, None, [0, 1, 2])]))
        dot = b.write(self.path("dot.glb"))
        b = GlbBuilder()
        b.node()
        empty = b.write(self.path("empty.glb"))
        for model, expected in ((broken, "could not be loaded"), (dot, "no extent"),
                                (empty, "holds no mesh"),
                                (self.path("missing.glb"), "cannot open")):
            with self.assertRaisesRegex(KilnError, expected):
                self.render(model, out="failed")
            self.assertEqual(os.listdir(self.path("failed")), [], model)

    def test_two_renders_of_one_model_differ_by_nothing_a_person_could_see(self):
        # Measured on the development machine (RTX 3080, Vulkan): byte for byte the same.
        # Another graphics card may round differently, so the test allows what no eye sees
        # and still catches a picture that depends on the time or on how fast frames came.
        model = SPECIMENS[1]
        first, _ = self.render(model, out="first")
        second, _ = self.render(model, out="second")
        for name in sorted(os.listdir(first)):
            if sha256_of(os.path.join(first, name)) == sha256_of(os.path.join(second, name)):
                continue
            _, _, one = read_png(os.path.join(first, name))
            _, _, two = read_png(os.path.join(second, name))
            worst = max(abs(a - b) for row_one, row_two in zip(one, two)
                        for a, b in zip(row_one, row_two))
            self.assertLessEqual(worst, 2, f"{name} differs by {worst} levels of 255")

    @needs_tools
    def test_a_whole_run_of_a_specimen_with_nothing_stood_in_for(self):
        reference = self.path("goal.png")
        with open(reference, "wb") as f:
            f.write(png(64, 64))
        code, out, err = self.command(
            "run", "--model", SPECIMENS[1], "--size", "0.8", "--profile", "pit",
            "--licence", "CC0 1.0", "--source", "kiln's first attempt",
            "--reference-image", reference, "--store", self.store, "--profiles", self.profiles)
        self.assertEqual((code, err), (0, ""))
        asset_dir = os.path.join(self.store, "boulder_1")
        record = read_record(asset_dir)
        pictures = record["shape_review"]["pictures"]
        self.assertEqual(len(pictures["views"]), 8)
        self.assertEqual(pictures["closest_viewing_distance"], 0.5)
        self.assertEqual(pictures["renderer"]["name"], "review_pictures")
        for view in pictures["views"]:
            path = os.path.join(asset_dir, *view["path"].split("/"))
            self.assertEqual(review.png_size(path), (1920, 1080))
            self.assertEqual(sha256_of(path), view["sha256"])
        self.assertEqual(sha256_of(os.path.join(asset_dir, "raw_output.glb")), sha256_of(SPECIMENS[1]))
        self.assertFalse(os.path.exists(os.path.join(asset_dir, "boulder_1.glb")))

        code, out, err = self.command("review", "boulder_1", "--approve", "--store", self.store,
                                      "--profiles", self.profiles)
        self.assertEqual((code, err), (0, ""))
        built = read_record(asset_dir)
        self.assertTrue(built["passed"])
        self.assertEqual(built["shape_review"]["pictures"], pictures)
        self.assertTrue(os.path.isfile(os.path.join(asset_dir, "boulder_1.glb")))
        # A rebuild leaves the record, review and all, byte for byte as it was.
        before = self.files(asset_dir)
        code, out, _ = self.command("rebuild", "--store", self.store, "--profiles", self.profiles)
        self.assertEqual(code, 0, out)
        self.assertIn("boulder_1: rebuilt, unchanged", out)
        self.assertEqual(self.files(asset_dir), before)
        self.assertEqual(json.dumps(read_record(asset_dir)), json.dumps(built))
        shutil.rmtree(asset_dir)


if __name__ == "__main__":
    unittest.main()
