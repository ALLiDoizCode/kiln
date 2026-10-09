"""Reduce a model to a triangle budget and bake the look it had onto what is left. Runs inside
the pinned Blender, not under the system Python:

    tools/bl kiln/blender_scripts/reduce.py <in.glb> <out.glb> <facts.json> \\
        <triangle budget> <texture size in pixels> <size in metres>

A model already inside the budget is left alone: nothing is written but the facts, which say
"reduced": false. Otherwise, in one Blender session (settings and what each was measured
against are in learn/research/blender-stages-trial.md, sections 5, 6 and 8):

  join and weld   every mesh becomes one, and vertices closer than a thousandth of a
                  millimetre are joined (see kiln_bl.weld for why)
  reduce          the Decimate modifier's Collapse, in one pass, to the budget. The few
                  faces it leaves with no area are dissolved. The stored normals no longer
                  fit the surface afterwards and are dropped
  lay out UVs     the reduced mesh's own UV islands are each scaled to their share of the
                  surface and packed again. No new islands are cut
  bake            the model as it was before reducing is kept beside the reduced one, and its
                  look is drawn into new textures of the given size for the reduced one: a
                  normal map, which holds both the shape that was lost and the model's own
                  normal map; base colour; and metallic and roughness in one image, if the
                  model had them. How far the bake's rays start outside the surface is worked
                  out from the two meshes
  resize          reducing can take off the model's outermost point, so it is scaled back to
                  the size

A baked model is written with tangents (see kiln_bl.write). A model with no UVs or no texture
is reduced and not baked: its edges sharper than 30 degrees are kept sharp, and its materials
are left as they were.

The bake runs on the CPU with one sample. Start Blender with one thread (KILN_BLENDER_THREADS=1,
as kiln does): with more, a few pixels of the normal map, and the tangents, differ from one
run to the next.

The input is only read. Textures are saved in the folder of <out.glb> before they are packed.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402
import kiln_bl as lib  # noqa: E402

WELD = 1e-6            # metres
DEGENERATE = 1e-6      # metres
SHARP = 30.0           # degrees, for a reduced model that is not baked
POINTS = 20000         # points taken on a surface to measure with
ISLAND_MARGIN = 0.001  # of the UV square, on every side of an island
JPEG_QUALITY = 90


def one_object(meshes):
    lib.activate(meshes[0], meshes)
    if len(meshes) > 1:
        lib.finished(bpy.ops.object.join(), "join")
    return bpy.context.view_layer.objects.active


def collapse(obj, budget):
    """Collapse to the budget. One pass lands on it or just under; the loop is for a mesh
    where it lands over."""
    for _ in range(6):
        now = lib.triangles(obj.data)
        if now <= budget:
            return
        modifier = obj.modifiers.new("reduce", "DECIMATE")
        modifier.decimate_type = "COLLAPSE"
        modifier.ratio = budget / now
        modifier.use_collapse_triangulate = True
        lib.activate(obj)
        lib.finished(bpy.ops.object.modifier_apply(modifier=modifier.name), "Collapse")
    raise RuntimeError(f"Collapse left {lib.triangles(obj.data)} triangles, over the budget "
                       f"of {budget}")


def dissolve_faces_with_no_area(mesh):
    """Collapse leaves a few faces with no area. Such a face has no tangent, and a file that
    stores one for it fails the glTF validator."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.dissolve_degenerate(bm, dist=DEGENERATE, edges=bm.edges)
    bm.to_mesh(mesh)
    bm.free()


def drop_stored_normals(obj, sharp_angle):
    mesh = obj.data
    if mesh.has_custom_normals:
        lib.activate(obj)
        lib.finished(bpy.ops.mesh.customdata_custom_splitnormals_clear(), "clear stored normals")
    mesh.shade_smooth()
    if sharp_angle:
        mesh.set_sharp_from_angle(angle=math.radians(sharp_angle))


def lay_out_uvs(obj):
    lib.activate(obj)
    lib.finished(bpy.ops.object.mode_set(mode="EDIT"), "edit mode")
    lib.finished(bpy.ops.mesh.select_all(action="SELECT"), "select all")
    lib.finished(bpy.ops.uv.select_all(action="SELECT"), "select UVs")
    lib.finished(bpy.ops.uv.average_islands_scale(), "Average Islands Scale")
    lib.finished(bpy.ops.uv.pack_islands(rotate=True, margin=ISLAND_MARGIN, margin_method="ADD",
                                         shape_method="CONCAVE", scale=True), "Pack Islands")
    lib.finished(bpy.ops.object.mode_set(mode="OBJECT"), "object mode")


# ---- measuring one surface against another -------------------------------------------------

def surface_of(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = [vertex.co.copy() for vertex in mesh.vertices]
    return points, [tuple(t.vertices) for t in mesh.loop_triangles]


def points_on(surface, seed):
    """POINTS points spread evenly over a surface, each with the way its triangle faces. A
    triangle is picked with a chance in proportion to its area, so a model that keeps most
    of its triangles in one corner is not measured mostly there."""
    points, tris = surface
    rng = random.Random(seed)
    areas = [(points[b] - points[a]).cross(points[c] - points[a]).length for a, b, c in tris]
    out = []
    for a, b, c in rng.choices(tris, weights=areas, k=POINTS):
        pa, pb, pc = points[a], points[b], points[c]
        normal = (pb - pa).cross(pc - pa)
        u, v = rng.random(), rng.random()
        if normal.length < 1e-12:
            continue
        if u + v > 1.0:
            u, v = 1.0 - u, 1.0 - v
        out.append((pa + (pb - pa) * u + (pc - pa) * v, normal.normalized()))
    return out


def share_at(values, share):
    values = sorted(values)
    return values[min(len(values) - 1, int(share * len(values)))]


def distances(points, tree):
    """How far the points lie from a surface: the distance 99% are within, and the largest."""
    found = [tree.find_nearest(point)[3] for point, _ in points]
    return {"within_for_99_percent": share_at(found, 0.99), "largest": max(found)}


# ---- the bake ------------------------------------------------------------------------------

def principled_of(material):
    if material is None or material.node_tree is None:
        return None
    return next((n for n in material.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"),
                None)


def texture_of(material, socket_name):
    """The Image Texture node feeding an input of a material's Principled BSDF, through any
    nodes between; None if there is none."""
    principled = principled_of(material)
    if principled is None:
        return None
    seen, stack = set(), [principled.inputs[socket_name]]
    while stack:
        socket = stack.pop()
        for link in socket.links:
            node = link.from_node
            if node.bl_idname == "ShaderNodeTexImage" and node.image is not None:
                return node
            if node.name not in seen:
                seen.add(node.name)
                stack.extend(node.inputs)
    return None


def metallic_roughness_of(material):
    return texture_of(material, "Roughness") or texture_of(material, "Metallic")


def give_off(material, image_node, plain):
    """Rewire a material so that it gives off one texture as light, or the colour `plain`
    where it has no such texture, and nothing else. An Emit bake then copies it unlit."""
    tree = material.node_tree
    output = next((n for n in tree.nodes
                   if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output), None)
    if output is None:
        return
    emission = tree.nodes.new("ShaderNodeEmission")
    if image_node is not None:
        tree.links.new(image_node.outputs["Color"], emission.inputs["Color"])
    else:
        emission.inputs["Color"].default_value = plain
    for link in list(output.inputs["Surface"].links):
        tree.links.remove(link)
    tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])


def bake(low, dense, texture_size, folder, facts):
    """Draw the look of `dense` into new textures for `low`, and give `low` one material that
    uses them. Returns nothing; the facts gain what the rays found."""
    dense_surface, low_surface = surface_of(dense), surface_of(low)
    dense_tree = BVHTree.FromPolygons(*dense_surface)
    on_low = points_on(low_surface, 1)
    near = distances(on_low, dense_tree)
    facts["distance_to_the_surface_before"] = near
    facts["distance_from_the_surface_before"] = distances(points_on(dense_surface, 2),
                                                          BVHTree.FromPolygons(*low_surface))
    # The ray for a pixel starts this far outside the reduced surface and may travel twice as
    # far. Too little and it starts inside the dense surface and misses; too much and it
    # finds another part of the model, as from one spike to the next.
    cage = max(0.001, 4.0 * near["within_for_99_percent"])
    reach = 2.0 * cage
    hits = [dense_tree.ray_cast(point + normal * cage, -normal, reach)[3]
            for point, normal in on_low]
    astray = 2.0 * near["within_for_99_percent"]
    facts["cage"] = cage
    facts["rays_that_miss"] = sum(1 for hit in hits if hit is None) / len(hits)
    facts["rays_that_stray"] = sum(1 for hit in hits
                                   if hit is not None and abs(hit - cage) > astray) / len(hits)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False

    sources = [m for m in dense.data.materials if principled_of(m) is not None]
    with_metal = any(metallic_roughness_of(m) is not None for m in sources)
    first = principled_of(sources[0])
    roughness, metallic = (first.inputs[name].default_value for name in ("Roughness", "Metallic"))

    material = bpy.data.materials.new("baked")
    tree = material.node_tree
    if tree is None:
        material.use_nodes = True
        tree = material.node_tree
    for node in list(tree.nodes):
        tree.nodes.remove(node)
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    principled = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tree.links.new(principled.outputs["BSDF"], output.inputs["Surface"])
    wanted = [("normal", "Non-Color"), ("base_colour", "sRGB")]
    if with_metal:
        wanted.append(("metallic_roughness", "Non-Color"))
    nodes = {}
    for key, colour_space in wanted:
        image = bpy.data.images.new("baked_" + key, texture_size, texture_size, alpha=False,
                                    float_buffer=False)
        image.colorspace_settings.name = colour_space
        nodes[key] = tree.nodes.new("ShaderNodeTexImage")
        nodes[key].image = image
    low.data.materials.clear()
    low.data.materials.append(material)

    def bake_into(key, kind, **more):
        for node in tree.nodes:
            node.select = False
        nodes[key].select = True
        tree.nodes.active = nodes[key]
        lib.activate(low, [dense, low])
        lib.finished(bpy.ops.object.bake(
            type=kind, use_selected_to_active=True, cage_extrusion=cage,
            max_ray_distance=reach, margin=max(2, texture_size // 256),
            margin_type="ADJACENT_FACES", use_clear=True, target="IMAGE_TEXTURES",
            save_mode="INTERNAL", **more), "the bake of " + key)

    # The normal map first, while the dense model's own materials are still whole.
    bake_into("normal", "NORMAL", normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y",
              normal_b="POS_Z")
    for source in sources:
        give_off(source, texture_of(source, "Base Color"),
                 principled_of(source).inputs["Base Color"].default_value[:])
    bake_into("base_colour", "EMIT")
    if with_metal:
        for source in sources:
            # glTF keeps roughness in an image's green and metallic in its blue.
            give_off(source, metallic_roughness_of(source),
                     (0.0, principled_of(source).inputs["Roughness"].default_value,
                      principled_of(source).inputs["Metallic"].default_value, 1.0))
        bake_into("metallic_roughness", "EMIT")

    tree.links.new(nodes["base_colour"].outputs["Color"], principled.inputs["Base Color"])
    if with_metal:
        separate = tree.nodes.new("ShaderNodeSeparateColor")
        tree.links.new(nodes["metallic_roughness"].outputs["Color"], separate.inputs["Color"])
        tree.links.new(separate.outputs["Green"], principled.inputs["Roughness"])
        tree.links.new(separate.outputs["Blue"], principled.inputs["Metallic"])
    else:
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metallic
    normal_map = tree.nodes.new("ShaderNodeNormalMap")
    tree.links.new(nodes["normal"].outputs["Color"], normal_map.inputs["Color"])
    tree.links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    material.use_backface_culling = True   # glTF's doubleSided = false

    # The exporter copies an image's own bytes only when the image comes from a file; a baked
    # image, which lives in memory, it writes as PNG whatever format it is marked with. So
    # each one is saved, read back and packed. The normal map stays PNG: JPEG would smear it.
    for key, node in nodes.items():
        image = node.image
        as_jpeg = key != "normal"
        image.filepath_raw = os.path.join(folder, f"{key}.{'jpg' if as_jpeg else 'png'}")
        image.file_format = "JPEG" if as_jpeg else "PNG"
        image.save(quality=JPEG_QUALITY)
        image.source = "FILE"
        image.reload()
        image.pack()
    facts["maps"] = list(nodes)


def main(source, target, facts_path, budget, texture_size, size):
    budget, texture_size, size = int(budget), int(texture_size), float(size)
    meshes = lib.read(source)
    before = sum(lib.triangles(obj.data) for obj in meshes)
    if before <= budget:
        lib.save_facts(facts_path, {"reduced": False})
        return
    low = one_object(meshes)
    lib.weld(low.data, WELD)
    facts = {"reduced": True, "triangles_before": before}

    textured = any(texture_of(material, name) is not None for material in low.data.materials
                   for name in ("Base Color", "Roughness", "Metallic", "Normal"))
    baked = bool(low.data.uv_layers) and textured
    if baked:
        dense = low.copy()
        dense.data = low.data.copy()
        bpy.context.scene.collection.objects.link(dense)

    collapse(low, budget)
    dissolve_faces_with_no_area(low.data)
    facts["triangles"] = lib.triangles(low.data)
    drop_stored_normals(low, 0.0 if baked else SHARP)
    facts["baked"] = baked
    if baked:
        lay_out_uvs(low)
        facts["texture_size"] = texture_size
        bake(low, dense, texture_size, os.path.dirname(os.path.abspath(target)), facts)
        bpy.data.objects.remove(dense)

    low_corner, high_corner = lib.bounds([low])
    factor = size / max(h - l for l, h in zip(low_corner, high_corner))
    low.data.transform(Matrix.Scale(factor, 4))
    facts["resized_by"] = factor
    lib.write(target, tangents=baked)
    lib.save_facts(facts_path, facts)


if __name__ == "__main__":
    main(*lib.arguments())
