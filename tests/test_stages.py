"""Tests for the stages after scale_to_size: clean, reduce and place. Each is a whole build
with the pinned Blender and the glTF validator, on a model small enough to know the answer
by hand; all are skipped when .tools/ does not hold the tools. The review pictures are stood
in for.

Run from the repo root:  python3 -m unittest tests.test_stages
"""
import os
import unittest

from kiln import run as kiln_run
from kiln.glb import load
from kiln.measure import measure
from tests.glb_fixture import GlbBuilder, ball, cube_cross, cube_six_faces, png
from tests.test_run import RunCase, SIZE_TOLERANCE, needs_tools, without_renderer


def moved(positions, by=(0.0, 0.0, 0.0), scale=1.0):
    return [tuple(scale * p + d for p, d in zip(position, by)) for position in positions]


def triangles_of(path):
    """Every triangle of a model as (three positions, three stored normals or None)."""
    model = load(path)
    out = []
    for mesh in model.json["meshes"]:
        for primitive in mesh["primitives"]:
            flat, _ = model.accessor(primitive["attributes"]["POSITION"])
            points = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
            normals = None
            if "NORMAL" in primitive["attributes"]:
                flat, _ = model.accessor(primitive["attributes"]["NORMAL"])
                normals = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
            order, _ = model.accessor(primitive["indices"])
            for t in range(0, len(order), 3):
                corners = order[t:t + 3]
                out.append(([points[i] for i in corners],
                            [normals[i] for i in corners] if normals else None))
    return out


def facing(a, b, c):
    """The way a triangle faces by its winding: not of unit length."""
    u, v = [b[k] - a[k] for k in range(3)], [c[k] - a[k] for k in range(3)]
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class StageCase(RunCase):
    def setUp(self):
        super().setUp()
        without_renderer(self)

    def finished(self, model, **more):
        """Build `model`: (the finished model's path, its record, its stages' facts by name)."""
        asset_dir, record = self.run_and_approve(model, **more)
        self.assertTrue(record["passed"], record["checks"])
        return (os.path.join(asset_dir, record["model"]["path"]), record,
                {stage["name"]: stage for stage in record["stages"]})

    def model(self, name, *primitives, **node):
        """A model file of one mesh. A primitive is (positions, uvs, indices[, normals])."""
        b = GlbBuilder()
        b.node(b.mesh([b.primitive(p[0], p[1], p[2], normals=p[3] if len(p) > 3 else None)
                       for p in primitives]), **node)
        return b.write(self.path(name))


@needs_tools
class Cleaning(StageCase):
    def test_a_piece_sealed_inside_another_is_deleted(self):
        positions, uvs, indices = cube_cross()
        inner = (moved(positions, by=(0.4, 0.4, 0.4), scale=0.2), uvs, indices)
        path, _, facts = self.finished(self.model("nested.glb", (positions, uvs, indices), inner))
        self.assertEqual((facts["clean"]["hidden_pieces_deleted"],
                          facts["clean"]["hidden_triangles_deleted"]), (1, 12))
        surface = measure(path, validator=None)["surface"]
        self.assertEqual((surface["triangles"], surface["pieces"], surface["open_edges"]),
                         (12, 1, 0))

    def test_a_piece_that_can_be_seen_is_kept(self):
        positions, uvs, indices = cube_cross()
        beside = (moved(positions, by=(3.0, 0.0, 0.0)), uvs, indices)
        path, _, facts = self.finished(self.model("pair.glb", (positions, uvs, indices), beside))
        self.assertEqual(facts["clean"]["hidden_pieces_deleted"], 0)
        surface = measure(path, validator=None)["surface"]
        self.assertEqual((surface["triangles"], surface["pieces"]), (24, 2))

    def test_a_face_turned_inside_out_is_turned_back_with_its_stored_normals(self):
        # A cube of six separate faces, each with its own flat normals. The first face is
        # made inside out: its triangles wind the other way and its normals point inward.
        positions, uvs, indices = cube_six_faces()
        normals = []
        for face in range(6):
            a, b, c = (positions[indices[6 * face + k]] for k in range(3))
            normals += [facing(a, b, c)] * 4
        indices[0:6] = [indices[0], indices[2], indices[1], indices[3], indices[5], indices[4]]
        normals[0:4] = [tuple(-x for x in normals[0])] * 4
        path, _, facts = self.finished(self.model("inside_out.glb",
                                                  (positions, uvs, indices, normals)))
        self.assertEqual(facts["clean"]["faces_turned"], 2)
        self.assertGreater(facts["clean"]["vertices_joined"], 0)  # the six faces were sheets
        triangles = triangles_of(path)
        self.assertEqual(len(triangles), 12)
        centre = [sum(p[k] for corners, _ in triangles for p in corners) / 36 for k in range(3)]
        for corners, stored in triangles:
            outward = [sum(p[k] for p in corners) / 3 - centre[k] for k in range(3)]
            self.assertGreater(dot(facing(*corners), outward), 0, "a triangle faces inward")
            for normal in stored:
                self.assertGreater(dot(normal, outward), 0, "a stored normal points inward")

    def test_a_model_with_nothing_wrong_comes_out_with_the_same_surface(self):
        model = self.model("cube.glb", cube_cross())
        path, _, facts = self.finished(model)
        # Its vertices are joined: a cube's hard edges are stored as doubled points.
        joined = facts["clean"].pop("vertices_joined")
        self.assertGreater(joined, 0)
        self.assertEqual(facts["clean"], {
            "name": "clean", "faces_dissolved": 0, "loose_bits_deleted": 0,
            "hidden_pieces_deleted": 0, "hidden_triangles_deleted": 0, "faces_turned": 0})
        before, after = measure(model, validator=None), measure(path, validator=None)
        self.assertEqual(after["surface"], before["surface"])
        self.assertEqual(after["uvs"]["islands"], before["uvs"]["islands"])


@needs_tools
class Reducing(StageCase):
    def setUp(self):
        super().setUp()
        self.profile("tight", "triangle_budget = 300\n", texture_size="texture_size = 64\n")

    def ball(self, name="ball.glb", textured=True):
        b = GlbBuilder()
        material = b.material("painted", b.image(png(32, 32))) if textured else None
        b.node(b.mesh([b.primitive(*ball(), material=material)]))
        return b.write(self.path(name))

    def test_a_textured_model_over_the_budget_is_reduced_and_its_look_is_baked(self):
        path, record, facts = self.finished(self.ball(), profile="tight")
        reduce = facts["reduce"]
        self.assertEqual((reduce["reduced"], reduce["baked"], reduce["triangles_before"],
                          reduce["triangles"], reduce["texture_size"]),
                         (True, True, 3480, 300, 64))
        self.assertEqual(reduce["maps"], ["normal", "base_colour"])
        # The bake's rays find the ball they came from, and the ball is still the ball: no
        # point of it is further from where it was than a fiftieth of its size.
        self.assertLess(reduce["rays_that_miss"], 0.02)
        self.assertLess(reduce["distance_to_the_surface_before"]["largest"], 0.8 / 50)
        self.assertLess(reduce["distance_from_the_surface_before"]["largest"], 0.8 / 50)

        report = measure(path, size=0.8)
        self.assertEqual(report["validator"]["errors"], 0)
        self.assertEqual(report["totals"]["triangles"], 300)
        self.assertEqual((report["surface"]["pieces"], report["surface"]["open_edges"]), (1, 0))
        self.assertLessEqual(abs(report["bounding_box"]["largest_dimension"] - 0.8),
                             SIZE_TOLERANCE * 0.8)
        self.assertEqual(report["totals"]["materials"], 1)
        slots = report["materials"][0]["textures"]
        self.assertEqual(sorted(slots), ["baseColorTexture", "normalTexture"])
        kinds = {slot: report["textures"][image] for slot, image in slots.items()}
        self.assertEqual({slot: (t["format"], t["width"], t["height"]) for slot, t in kinds.items()},
                         {"baseColorTexture": ("jpeg", 64, 64), "normalTexture": ("png", 64, 64)})
        # Tangents are stored: the normal map was baked for Blender's, not for Bevy's own.
        self.assertIn("TANGENT", report["meshes"][0]["primitives"][0]["attributes"])
        self.assertEqual(report["validator"]["warnings"], 0)
        self.assertEqual(report["uvs"]["triangles"], 300)
        self.assertEqual(report["uvs"]["triangles_outside_square"], 0)

    def test_a_model_with_no_texture_is_reduced_and_not_baked(self):
        path, _, facts = self.finished(self.ball(textured=False), profile="tight")
        self.assertEqual((facts["reduce"]["reduced"], facts["reduce"]["baked"]), (True, False))
        report = measure(path, validator=None)
        self.assertEqual((report["totals"]["triangles"], report["totals"]["textures"]), (300, 0))
        self.assertEqual((report["surface"]["pieces"], report["surface"]["open_edges"]), (1, 0))

    def test_a_model_inside_the_budget_is_not_reduced(self):
        path, _, facts = self.finished(self.ball(), profile="pit")
        self.assertEqual(facts["reduce"], {"name": "reduce", "reduced": False})
        report = measure(path, validator=None)
        self.assertEqual(report["totals"]["triangles"], 3480)
        self.assertEqual([(t["format"], t["width"]) for t in report["textures"]], [("png", 32)])

    def test_reducing_and_baking_twice_gives_the_same_bytes(self):
        model = self.ball()
        sums = []
        for store in (self.path("one"), self.path("two")):
            asset_dir, _ = kiln_run.run(model, 0.8, "tight", "CC0 1.0", "a test", store=store,
                                        profiles_dir=self.profiles)
            kiln_run.approve(asset_dir, self.profiles, today="2026-10-07")
            sums.append(self.files(asset_dir))
        self.assertIn("ball.glb", sums[0])
        self.assertEqual(sums[0], sums[1])


@needs_tools
class Placing(StageCase):
    def test_the_origin_is_put_at_the_bottom_centre(self):
        positions, uvs, indices = cube_cross()
        path, _, _ = self.finished(self.model("far.glb", (positions, uvs, indices),
                                              translation=[5.0, 3.0, -2.0]))
        box = measure(path, validator=None)["bounding_box"]
        for got, want in zip(box["min"] + box["max"], (-0.4, 0.0, -0.4, 0.4, 0.8, 0.4)):
            self.assertAlmostEqual(got, want, places=6)

    def test_the_turn_is_about_the_up_axis_and_anticlockwise_from_above(self):
        # A long slab lying along x, with its high end at the low-x end.
        slab = [(0, 0, 0), (4, 0, 0), (0, 1, 0)], None, [0, 1, 2]
        ends = {}
        for turn in (0, 90, 180):
            path, record, facts = self.finished(self.model(f"slab_{turn}.glb", slab), turn=turn)
            self.assertEqual((record["turn"], facts["place"]["turn"]), (turn, turn))
            (corners, _), = triangles_of(path)
            ends[turn] = max(corners, key=lambda p: p[1])
        for got, want in ((ends[0], (-0.4, 0.2, 0.0)), (ends[90], (0.0, 0.2, 0.4)),
                          (ends[180], (0.4, 0.2, 0.0))):
            for g, w in zip(got, want):
                self.assertAlmostEqual(g, w, places=6)


if __name__ == "__main__":
    unittest.main()
