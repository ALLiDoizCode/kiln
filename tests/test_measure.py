"""Tests for kiln.measure, on tiny model files whose every figure can be worked out by hand.

Run from the repo root:  python3 -m unittest
"""
import contextlib
import io
import json
import math
import os
import struct
import tempfile
import unittest

from kiln import glb
from kiln.measure import DEFAULT_VALIDATOR, main, measure, render_text, run_validator
from tests.glb_fixture import (FLOAT, U8, U16, U32, GlbBuilder, cube_cross, cube_six_faces,
                               png, quad)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECIMENS = [os.path.join(REPO, "learn", "specimens", name)
             for name in ("crate.glb", "boulder_1.glb")]


class MeasureCase(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)

    def path(self, name="model.glb"):
        return os.path.join(self._dir.name, name)

    def one_mesh(self, positions, uvs, indices, material=None, builder=None, **node):
        """Write a model with one mesh of one primitive, and return its path."""
        b = builder or GlbBuilder()
        b.node(b.mesh([b.primitive(positions, uvs, indices, material)]), **node)
        return b.write(self.path())

    def measured(self, *args, size=None, **kwargs):
        return measure(self.one_mesh(*args, **kwargs), size=size, validator=None)


class Counts(MeasureCase):
    def test_a_quad_is_two_triangles_and_four_vertices(self):
        report = self.measured(*quad())
        self.assertEqual(report["totals"]["triangles"], 2)
        self.assertEqual(report["totals"]["vertices"], 4)
        mesh = report["meshes"][0]
        self.assertEqual((mesh["triangles"], mesh["vertices"], mesh["placed"]), (2, 4, 1))
        self.assertEqual(mesh["primitives"][0]["triangles"], 2)
        self.assertTrue(mesh["primitives"][0]["indexed"])
        self.assertTrue(mesh["primitives"][0]["has_uvs"])

    def test_counts_are_given_per_mesh_and_per_primitive(self):
        b = GlbBuilder()
        positions, uvs, indices = quad()
        cube = cube_six_faces()
        b.node(b.mesh([b.primitive(positions, uvs, indices), b.primitive(*cube)], name="two"))
        b.node(b.mesh([b.primitive(positions, None, indices)], name="one"))
        report = measure(b.write(self.path()), validator=None)
        self.assertEqual(report["totals"]["meshes"], 2)
        self.assertEqual(report["totals"]["triangles"], 2 + 12 + 2)
        self.assertEqual(report["totals"]["vertices"], 4 + 24 + 4)
        self.assertEqual([m["triangles"] for m in report["meshes"]], [14, 2])
        self.assertEqual([p["vertices"] for p in report["meshes"][0]["primitives"]], [4, 24])
        self.assertFalse(report["meshes"][1]["primitives"][0]["has_uvs"])

    def test_a_primitive_without_indices_uses_its_vertices_three_at_a_time(self):
        positions, uvs, indices = quad()
        report = self.measured([positions[i] for i in indices], [uvs[i] for i in indices], None)
        self.assertEqual(report["totals"]["triangles"], 2)
        self.assertEqual(report["totals"]["vertices"], 6)
        self.assertFalse(report["meshes"][0]["primitives"][0]["indexed"])
        self.assertEqual(report["uvs"]["islands"], 1)
        self.assertEqual(report["uvs"]["edges"], 5)

    def test_every_index_width_reads_the_same(self):
        for component in (U8, U16, U32):
            b = GlbBuilder()
            positions, uvs, indices = cube_cross()
            b.node(b.mesh([b.primitive(positions, uvs, indices, index_component=component)]))
            report = measure(b.write(self.path()), validator=None)
            self.assertEqual(report["totals"]["triangles"], 12, component)
            self.assertEqual(report["uvs"]["islands"], 1, component)

    def test_strips_and_fans_are_counted_as_the_triangles_they_draw(self):
        positions, uvs, _ = quad()
        for mode, order in ((5, [0, 1, 3, 2]), (6, [0, 1, 2, 3])):
            b = GlbBuilder()
            b.node(b.mesh([b.primitive(positions, uvs, order, mode=mode)]))
            report = measure(b.write(self.path()), validator=None)
            self.assertEqual(report["totals"]["triangles"], 2, mode)
            self.assertEqual(report["uvs"]["edges"], 5, mode)

    def test_a_mesh_placed_twice_counts_twice_in_the_totals(self):
        b = GlbBuilder()
        mesh = b.mesh([b.primitive(*quad())])
        b.node(mesh)
        b.node(mesh, translation=[5, 0, 0])
        report = measure(b.write(self.path()), validator=None)
        self.assertEqual(report["totals"]["triangles"], 4)
        self.assertEqual(report["meshes"][0]["triangles"], 2)
        self.assertEqual(report["meshes"][0]["placed"], 2)
        self.assertEqual(report["bounding_box"]["dimensions"], [6.0, 1.0, 0.0])
        self.assertTrue(any("more than once" in note for note in report["notes"]))

    def test_a_mesh_no_node_places_is_noted_and_not_counted(self):
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(*quad())]))
        b.mesh([b.primitive(*cube_cross())])
        report = measure(b.write(self.path()), validator=None)
        self.assertEqual(report["totals"]["triangles"], 2)
        self.assertEqual(report["meshes"][1]["placed"], 0)
        self.assertTrue(any("Not placed" in note for note in report["notes"]))


class BoundingBox(MeasureCase):
    def test_box_of_a_quad(self):
        report = self.measured(*quad(2.0, 0.5))
        box = report["bounding_box"]
        self.assertEqual(box["min"], [0.0, 0.0, 0.0])
        self.assertEqual(box["max"], [2.0, 0.5, 0.0])
        self.assertEqual(box["dimensions"], [2.0, 0.5, 0.0])
        self.assertEqual(box["largest_dimension"], 2.0)
        self.assertEqual(report["size"], {"in_file": 2.0, "given": None, "scale_factor": None})

    def test_a_given_size_gives_the_factor_to_scale_by(self):
        report = self.measured(*quad(2.0, 0.5), size=0.5)
        self.assertEqual(report["size"], {"in_file": 2.0, "given": 0.5, "scale_factor": 0.25})

    def test_node_scale_and_translation_are_applied(self):
        report = self.measured(*quad(), scale=[2, 3, 1], translation=[10, 0, -1])
        self.assertEqual(report["bounding_box"]["min"], [10.0, 0.0, -1.0])
        self.assertEqual(report["bounding_box"]["max"], [12.0, 3.0, -1.0])

    def test_transforms_of_parent_nodes_are_applied(self):
        # The child is scaled by 2; its parent turns it a quarter turn about Z and moves it.
        b = GlbBuilder()
        child = b.node(b.mesh([b.primitive(*quad())]), scale=[2, 2, 2])
        half = math.sqrt(0.5)
        b.node(children=[child], rotation=[0, 0, half, half], translation=[0, 0, 4])
        report = measure(b.write(self.path()), validator=None)
        box = report["bounding_box"]
        for got, want in zip(box["min"] + box["max"], [-2, 0, 4, 0, 2, 4]):
            self.assertAlmostEqual(got, want, places=12)

    def test_a_node_matrix_is_read_column_first(self):
        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 7, 8, 9, 1]  # a move by (7, 8, 9)
        report = self.measured(*quad(), matrix=matrix)
        self.assertEqual(report["bounding_box"]["min"], [7.0, 8.0, 9.0])

    def test_an_empty_scene_has_no_box(self):
        b = GlbBuilder()
        report = measure(b.write(self.path()), size=1.0, validator=None)
        self.assertIsNone(report["bounding_box"])
        self.assertIsNone(report["uvs"])
        self.assertEqual(report["totals"]["triangles"], 0)


class Uvs(MeasureCase):
    def test_a_quad_filling_the_square(self):
        uv = self.measured(*quad())["uvs"]
        self.assertEqual(uv["islands"], 1)
        self.assertEqual(uv["edges"], 5)        # four sides and the diagonal
        self.assertEqual(uv["seam_edges"], 0)
        self.assertEqual(uv["open_edges"], 4)   # the four sides
        self.assertEqual(uv["seam_share"], 0.0)
        self.assertEqual(uv["coverage"], 1.0)
        self.assertEqual(uv["triangle_area_sum"], 1.0)
        self.assertEqual(uv["triangles_outside_square"], 0)

    def test_a_quad_on_half_the_square(self):
        uv = self.measured(*quad(u=(0.0, 0.5)))["uvs"]
        self.assertEqual(uv["coverage"], 0.5)
        self.assertEqual(uv["triangle_area_sum"], 0.5)

    def test_cube_with_six_separate_faces(self):
        report = self.measured(*cube_six_faces())
        uv = report["uvs"]
        self.assertEqual(report["totals"]["vertices"], 24)
        self.assertEqual(uv["islands"], 6)
        self.assertEqual(uv["edges"], 18)
        self.assertEqual(uv["seam_edges"], 12)
        self.assertEqual(uv["open_edges"], 0)
        self.assertEqual(uv["seam_share"], 12 / 18)
        self.assertEqual(uv["coverage"], 6 / 16)
        self.assertAlmostEqual(uv["triangle_area_sum"], 6 / 16, places=12)

    def test_cube_unfolded_as_a_cross(self):
        report = self.measured(*cube_cross())
        uv = report["uvs"]
        self.assertEqual(report["totals"]["vertices"], 14)
        self.assertEqual(uv["islands"], 1)
        self.assertEqual(uv["edges"], 18)
        self.assertEqual(uv["seam_edges"], 7)
        self.assertEqual(uv["open_edges"], 0)
        self.assertEqual(uv["seam_share"], 7 / 18)
        self.assertEqual(uv["coverage"], 6 / 16)

    def test_a_split_for_a_normal_only_is_not_a_seam(self):
        # Two triangles of a quad that do not share vertices but agree on the UVs where they
        # meet, as an exporter writes a hard edge.
        positions, uvs, indices = quad()
        uv = self.measured([positions[i] for i in indices], [uvs[i] for i in indices],
                           list(range(6)))["uvs"]
        self.assertEqual((uv["islands"], uv["seam_edges"], uv["edges"]), (1, 0, 5))

    def test_overlapping_islands_are_covered_once_but_add_up_twice(self):
        b = GlbBuilder()
        positions, uvs, indices = quad(u=(0.0, 0.5))
        moved = [(x, y, 1.0) for x, y, _ in positions]
        b.node(b.mesh([b.primitive(positions, uvs, indices), b.primitive(moved, uvs, indices)]))
        uv = measure(b.write(self.path()), validator=None)["uvs"]
        self.assertEqual(uv["islands"], 2)
        self.assertEqual(uv["coverage"], 0.5)
        self.assertEqual(uv["triangle_area_sum"], 1.0)

    def test_uvs_outside_the_square_are_counted_and_not_covered(self):
        uv = self.measured(*quad(u=(0.5, 1.5)))["uvs"]
        self.assertEqual(uv["coverage"], 0.5)
        self.assertEqual(uv["triangle_area_sum"], 1.0)
        self.assertEqual(uv["triangles_outside_square"], 2)

    def test_primitives_of_one_mesh_are_welded_together(self):
        # A quad stored as two primitives of one triangle each: still one island, no seam.
        positions, uvs, _ = quad()
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(positions, uvs, [0, 1, 2]), b.primitive(positions, uvs, [0, 2, 3])]))
        uv = measure(b.write(self.path()), validator=None)["uvs"]
        self.assertEqual((uv["islands"], uv["seam_edges"], uv["edges"], uv["open_edges"]), (1, 0, 5, 4))

    def test_a_triangle_squashed_to_a_line_is_left_out_of_edges(self):
        positions, uvs, indices = quad()
        uv = self.measured(positions + [(0, 0, 0)], uvs + [(0.0, 0.0)], indices + [0, 4, 1])["uvs"]
        self.assertEqual(uv["triangles_without_area"], 1)
        self.assertEqual((uv["islands"], uv["edges"], uv["open_edges"]), (1, 5, 4))

    def test_no_uvs_means_no_uv_figures(self):
        positions, _, indices = quad()
        report = self.measured(positions, None, indices)
        self.assertIsNone(report["uvs"])
        self.assertIsNone(report["texel_density"])

    def test_normalised_integer_uvs_are_read_as_fractions(self):
        positions, _, indices = quad()
        b = GlbBuilder()
        uvs = [(0, 0), (65535, 0), (65535, 65535), (0, 65535)]
        b.node(b.mesh([b.primitive(positions, uvs, indices, uv_component=U16)]))
        uv = measure(b.write(self.path()), validator=None)["uvs"]
        self.assertEqual(uv["coverage"], 1.0)
        self.assertEqual(uv["triangle_area_sum"], 1.0)


class TexelDensity(MeasureCase):
    def textured(self, width, height, shape, size=None, **node):
        b = GlbBuilder()
        material = b.material("paint", b.image(png(width, height)))
        return self.measured(*shape, material=material, builder=b, size=size, **node)

    def test_a_metre_square_under_a_whole_64_pixel_texture(self):
        density = self.textured(64, 64, quad())["texel_density"]
        self.assertEqual(density["pixels_per_metre"], 64.0)
        self.assertEqual((density["p05"], density["median"], density["p95"]), (64.0, 64.0, 64.0))
        self.assertEqual(density["size"], 1.0)
        self.assertEqual(density["surface_area"], 1.0)
        self.assertEqual(density["by_primitive"][0]["pixels_per_metre"], 64.0)
        self.assertEqual(density["by_primitive"][0]["texture_pixels"], [64, 64])

    def test_scaling_to_twice_the_size_halves_it(self):
        density = self.textured(64, 64, quad(), size=2.0)["texel_density"]
        self.assertEqual(density["pixels_per_metre"], 32.0)
        self.assertEqual(density["size"], 2.0)
        self.assertEqual(density["surface_area"], 4.0)

    def test_a_node_scale_counts_as_part_of_the_model(self):
        density = self.textured(64, 64, quad(), scale=[4, 4, 4])["texel_density"]
        self.assertEqual(density["pixels_per_metre"], 16.0)
        self.assertEqual(density["size"], 4.0)

    def test_half_the_texture_on_the_same_surface(self):
        density = self.textured(64, 64, quad(u=(0.0, 0.25)))["texel_density"]
        self.assertEqual(density["pixels_per_metre"], 32.0)  # sqrt(0.25 * 64 * 64 / 1)

    def test_a_texture_that_is_not_square(self):
        density = self.textured(64, 32, quad())["texel_density"]
        self.assertAlmostEqual(density["pixels_per_metre"], math.sqrt(64 * 32), places=12)

    def test_the_spread_follows_surface_area(self):
        # Two quads sharing one 64 pixel texture: a 1 m square on a quarter of it (32 px/m)
        # and a 3 m square on another quarter (32 / 3 px/m). Nine tenths of the surface is
        # the large quad.
        b = GlbBuilder()
        material = b.material("paint", b.image(png(64, 64)))
        small = quad(u=(0.0, 0.5), v=(0.0, 0.5))
        large = quad(3.0, 3.0, u=(0.5, 1.0), v=(0.5, 1.0))
        large = ([(x, y, 5.0) for x, y, _ in large[0]],) + large[1:]
        b.node(b.mesh([b.primitive(*small, material=material), b.primitive(*large, material=material)]))
        density = measure(b.write(self.path()), validator=None)["texel_density"]
        self.assertAlmostEqual(density["pixels_per_metre"], math.sqrt(0.5 * 4096 / 10), places=12)
        self.assertAlmostEqual(density["p05"], 32 / 3, places=12)
        self.assertAlmostEqual(density["median"], 32 / 3, places=12)
        self.assertAlmostEqual(density["p95"], 32.0, places=12)
        self.assertEqual([round(p["pixels_per_metre"], 9) for p in density["by_primitive"]],
                         [32.0, round(32 / 3, 9)])

    def test_no_base_colour_texture_means_no_density(self):
        b = GlbBuilder()
        report = self.measured(*quad(), material=b.material("plain"), builder=b)
        self.assertIsNone(report["texel_density"])
        self.assertEqual(report["materials"], [{"index": 0, "name": "plain", "textures": {}}])

    def test_a_texture_transform_is_noted(self):
        b = GlbBuilder()
        material = b.material("paint", b.image(png(8, 8)))
        b.doc["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["extensions"] = {
            "KHR_texture_transform": {"scale": [2, 2]}}
        report = self.measured(*quad(), material=material, builder=b)
        self.assertTrue(any("KHR_texture_transform" in note for note in report["notes"]))


class MaterialsAndTextures(MeasureCase):
    def test_materials_list_the_textures_they_use(self):
        b = GlbBuilder()
        colour = b.image(png(64, 32), name="colour")
        bumps = b.image(png(16, 16), name="bumps")
        material = b.material("paint", colour)
        b.doc["textures"].append({"source": bumps})
        b.doc["materials"][0]["normalTexture"] = {"index": 1}
        report = self.measured(*quad(), material=material, builder=b)
        self.assertEqual(report["totals"]["materials"], 1)
        self.assertEqual(report["materials"][0]["textures"],
                         {"baseColorTexture": 0, "normalTexture": 1})
        first, second = report["textures"]
        self.assertEqual((first["name"], first["format"], first["width"], first["height"]),
                         ("colour", "png", 64, 32))
        self.assertEqual(first["bytes"], len(png(64, 32)))
        self.assertEqual(first["used_as"], ["baseColorTexture of paint"])
        self.assertEqual(second["used_as"], ["normalTexture of paint"])

    def test_png_header(self):
        self.assertEqual(glb.image_info(png(300, 7)), ("png", 300, 7))

    def test_jpeg_header(self):
        # Start of image, an application block to skip, then a baseline frame header.
        data = (b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + bytes(9)
                + b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, 480, 640, 3) + bytes(6))
        self.assertEqual(glb.image_info(data), ("jpeg", 640, 480))

    def test_webp_headers(self):
        def riff(kind, body):
            return b"RIFF" + struct.pack("<I", 4 + 8 + len(body)) + b"WEBP" + kind + \
                struct.pack("<I", len(body)) + body
        lossy = riff(b"VP8 ", bytes(3) + b"\x9d\x01\x2a" + struct.pack("<HH", 640, 480))
        lossless = riff(b"VP8L", b"\x2f" + struct.pack("<I", (640 - 1) | (480 - 1) << 14))
        extended = riff(b"VP8X", bytes(4) + (639).to_bytes(3, "little") + (479).to_bytes(3, "little"))
        for data in (lossy, lossless, extended):
            self.assertEqual(glb.image_info(data), ("webp", 640, 480))

    def test_an_unknown_image_is_reported_as_unknown(self):
        self.assertEqual(glb.image_info(b"not a picture"), ("unknown", None, None))


class Reading(MeasureCase):
    def test_interleaved_vertex_data_is_read_by_its_stride(self):
        positions, uvs, indices = quad()
        b = GlbBuilder()
        rows = b"".join(struct.pack("<5f", *p, *t) for p, t in zip(positions, uvs))
        view = b.view(rows, stride=20)
        b.doc["accessors"] += [
            {"bufferView": view, "byteOffset": 0, "componentType": FLOAT, "count": 4, "type": "VEC3"},
            {"bufferView": view, "byteOffset": 12, "componentType": FLOAT, "count": 4, "type": "VEC2"}]
        b.node(b.mesh([{"attributes": {"POSITION": 0, "TEXCOORD_0": 1},
                        "indices": b.accessor(indices, U16)}]))
        report = measure(b.write(self.path()), validator=None)
        self.assertEqual(report["bounding_box"]["max"], [1.0, 1.0, 0.0])
        self.assertEqual(report["uvs"]["coverage"], 1.0)

    def test_a_sparse_accessor_is_filled_in(self):
        # Positions stored as all zeros, with the three that are not zero given sparsely.
        positions, uvs, indices = quad(2.0, 3.0)
        b = GlbBuilder()
        primitive = b.primitive([(0, 0, 0)] * 4, uvs, indices)
        where = b.view(struct.pack("<3H", 1, 2, 3))
        what = b.view(b"".join(struct.pack("<3f", *positions[i]) for i in (1, 2, 3)))
        b.doc["accessors"][primitive["attributes"]["POSITION"]]["sparse"] = {
            "count": 3, "indices": {"bufferView": where, "componentType": U16},
            "values": {"bufferView": what}}
        b.node(b.mesh([primitive]))
        report = measure(b.write(self.path()), validator=None)
        self.assertEqual(report["bounding_box"]["max"], [2.0, 3.0, 0.0])

    def test_compressed_mesh_data_fails_with_a_clear_message(self):
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(*quad())]))
        b.doc["extensionsRequired"] = ["KHR_draco_mesh_compression"]
        with self.assertRaisesRegex(glb.GltfError, "KHR_draco_mesh_compression"):
            measure(b.write(self.path()), validator=None)

    def test_a_file_that_is_not_a_model_fails_with_a_clear_message(self):
        with open(self.path("notes.glb"), "wb") as f:
            f.write(b"hello")
        with self.assertRaisesRegex(glb.GltfError, "not a glTF file"):
            measure(self.path("notes.glb"), validator=None)

    def test_size_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.measured(*quad(), size=0)


class Validator(MeasureCase):
    def test_a_missing_validator_is_reported_not_raised(self):
        report = measure(self.one_mesh(*quad()), validator=self.path("no_such_validator"))
        self.assertFalse(report["validator"]["ran"])
        self.assertIn("not installed", report["validator"]["reason"])
        self.assertIn("tools/install_tools.sh", report["validator"]["reason"])
        self.assertIn("not run: ", render_text(report))

    @unittest.skipUnless(os.path.isfile(DEFAULT_VALIDATOR), "glTF validator not installed")
    def test_a_sound_file_passes(self):
        b = GlbBuilder()
        material = b.material("paint", b.image(png(8, 8)))
        verdict = measure(self.one_mesh(*cube_cross(), material=material, builder=b))["validator"]
        self.assertTrue(verdict["ran"])
        self.assertEqual(verdict["errors"], 0, verdict["messages"])

    @unittest.skipUnless(os.path.isfile(DEFAULT_VALIDATOR), "glTF validator not installed")
    def test_a_broken_file_gives_errors_with_messages(self):
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(*quad())]))
        b.doc["accessors"][0]["count"] = 400  # more vertices than the buffer holds
        b.doc["accessors"][1]["count"] = 400
        b.doc["meshes"][0]["primitives"][0].pop("indices")
        path = b.write(self.path())
        verdict = run_validator(path)
        self.assertGreater(verdict["errors"], 0)
        self.assertEqual(verdict["messages"][0]["severity"], "error")
        self.assertTrue(verdict["messages"][0]["message"])


class Specimens(unittest.TestCase):
    def test_both_specimens_are_measured(self):
        crate, boulder = (measure(path, size=0.8) for path in SPECIMENS)
        self.assertEqual(crate["totals"]["triangles"], 108)
        self.assertEqual(crate["totals"]["vertices"], 168)
        self.assertIsNone(crate["uvs"])
        self.assertIsNone(crate["texel_density"])
        self.assertEqual(boulder["totals"]["triangles"], 136)
        self.assertEqual(boulder["totals"]["vertices"], 115)
        self.assertEqual((boulder["textures"][0]["width"], boulder["textures"][0]["height"]),
                         (512, 512))
        self.assertGreater(boulder["uvs"]["islands"], 0)
        self.assertGreater(boulder["texel_density"]["pixels_per_metre"], 0)
        for report in (crate, boulder):
            self.assertEqual(report["size"]["given"], 0.8)
            json.dumps(report)
            self.assertIn("COUNTS", render_text(report))


class CommandLine(MeasureCase):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_json_output_is_the_report(self):
        path = self.one_mesh(*cube_six_faces())
        code, out, _ = self.run_main(path, "--json", "--size", "2", "--no-validator")
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report, json.loads(json.dumps(measure(path, size=2.0, validator=None))))
        self.assertEqual(report["uvs"]["islands"], 6)
        self.assertEqual(report["size"]["scale_factor"], 2.0)

    def test_text_output_names_every_part(self):
        code, out, _ = self.run_main(self.one_mesh(*cube_six_faces()), "--no-validator")
        self.assertEqual(code, 0)
        for heading in ("COUNTS", "BOUNDING BOX", "MATERIALS", "TEXTURES", "UVS",
                        "TEXEL DENSITY", "KHRONOS GLTF VALIDATOR"):
            self.assertIn(heading, out)

    def test_a_bad_file_exits_with_an_error(self):
        code, out, err = self.run_main(self.path("missing.glb"))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("missing.glb", err)


if __name__ == "__main__":
    unittest.main()
