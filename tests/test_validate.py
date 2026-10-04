"""Proves each L1 check goes red: breaks the tracer one way at a time and
asserts that the matching check, by id, fails.

Usage: tools/bl tests/test_validate.py
"""

import runpy
import sys
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from pipeline import Asset, Checks, conventions
from validate import check_scene

TRACER = Asset("tracer")


def edit(fn):
    """Apply fn(bm) to the tracer mesh."""
    mesh = bpy.data.objects["tracer"].data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    fn(bm)
    bm.to_mesh(mesh)
    bm.free()


def delete_face(spec):
    edit(lambda bm: bmesh.ops.delete(bm, geom=[bm.faces[0]], context="FACES_ONLY"))


def flip_all(spec):
    edit(lambda bm: bmesh.ops.reverse_faces(bm, faces=bm.faces))


def flip_one(spec):
    edit(lambda bm: bmesh.ops.reverse_faces(bm, faces=[bm.faces[0]]))


def unapplied_scale(spec):
    bpy.data.objects["tracer"].scale = (2, 2, 2)


def rotated(spec):
    bpy.data.objects["tracer"].rotation_euler = (0, 0, 1.5708)


def shifted(spec):
    edit(lambda bm: bmesh.ops.translate(bm, verts=bm.verts, vec=(0.1, 0, 0)))


def mirrored_front_to_back(spec):
    def mirror(bm):
        bmesh.ops.scale(bm, verts=bm.verts, vec=(1, -1, 1))
        bmesh.ops.reverse_faces(bm, faces=bm.faces)

    edit(mirror)


def default_name(spec):
    bpy.data.objects["tracer"].data.name = "Cube.001"


def stray_object(spec):
    stray = bpy.data.objects.new("leftover", bpy.data.objects["tracer"].data.copy())
    bpy.context.scene.collection.objects.link(stray)


def ngon(spec):
    def dissolve(bm):
        cap = [f for f in bm.faces if f.normal.x > 0.9]
        bmesh.ops.dissolve_faces(bm, faces=cap)

    edit(dissolve)


def loose_vertex(spec):
    edit(lambda bm: bm.verts.new((0, 0, 0.5)))


def duplicate_vertices(spec):
    edit(lambda bm: bmesh.ops.split_edges(bm, edges=bm.edges))


def no_material(spec):
    bpy.data.objects["tracer"].data.materials.clear()


def emission_material(spec):
    tree = bpy.data.materials["m_tracer"].node_tree
    emission = tree.nodes.new("ShaderNodeEmission")
    output = next(n for n in tree.nodes if n.type == "OUTPUT_MATERIAL")
    tree.links.new(emission.outputs[0], output.inputs["Surface"])


def wrong_colour(spec):
    bsdf = bpy.data.materials["m_tracer"].node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.8, 0.1, 1.0)


def extra_material(spec):
    bpy.data.objects["tracer"].data.materials.append(bpy.data.materials.new("m_extra"))


def over_budget(spec):
    spec["max_triangles"] = 10


# mutation -> the check id that must fail because of it
CASES = [
    (delete_face, "tracer.manifold"),
    (flip_all, "tracer.normals_outward"),
    (flip_one, "tracer.winding_consistent"),
    (unapplied_scale, "tracer.transform_applied"),
    (rotated, "tracer.transform_applied"),
    (shifted, "bounds.match_spec"),
    (mirrored_front_to_back, "bounds.match_spec"),
    (default_name, "tracer.naming"),
    (stray_object, "objects.unexpected"),
    (ngon, "tracer.no_ngons"),
    (loose_vertex, "tracer.no_loose_vertices"),
    (duplicate_vertices, "tracer.no_duplicate_vertices"),
    (no_material, "tracer.materials_assigned"),
    (emission_material, "m_tracer.principled"),
    (wrong_colour, "m_tracer.base_colour"),
    (extra_material, "materials.match_spec"),
    (over_budget, "budget.triangles"),
]


def failures_after(mutate):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    spec = TRACER.spec()
    runpy.run_path(str(TRACER.source / "build.py"))["build"](spec)
    if mutate:
        mutate(spec)
    checks = Checks("L1-mesh", "tracer")
    check_scene(checks, spec, conventions())
    return {r["id"] for r in checks.failed()}


problems = []
if clean := failures_after(None):
    problems.append(f"unmodified tracer fails {sorted(clean)}")
for mutate, expected in CASES:
    failed = failures_after(mutate)
    status = "ok" if expected in failed else "NOT CAUGHT"
    print(f"{status:10} {mutate.__name__:24} -> {sorted(failed)}")
    if expected not in failed:
        problems.append(f"{mutate.__name__} did not fail {expected}")

for problem in problems:
    print("FAIL", problem)
print(f"{len(CASES) + 1 - len(problems)}/{len(CASES) + 1} validate tests passed")
sys.exit(1 if problems else 0)
