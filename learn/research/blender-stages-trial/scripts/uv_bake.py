"""Stage 4 of the trial: give a reduced mesh new UVs and bake the dense original's three maps
onto it.

    tools/bl uv_bake.py <low.glb> <out.glb> <facts.json> high=<dense.glb> [name=value ...]

<low.glb> is the mesh that will be kept (the reduced one). `high` is the model the look is
taken from: its shape and its base colour, metallic-roughness and normal textures.

  weld=0.000001       metres: join the low mesh's vertices closer than this first. A .glb stores
                      a point again wherever its normal or UV changes and the importer joins
                      only those whose normals agree, so without this the mesh arrives in sheets
UVs of the low mesh
  uv=smart            Smart UV Project: angle=<degrees, 66>, island_margin=<0..1, 0.003>
     sharp_unwrap     cut seams where faces meet at more than seam_angle=<degrees, 60>, then Unwrap
     keep             leave the UVs the mesh came with
  pack=none|concave|aabb   run Pack Islands afterwards with that island shape and pack_margin;
                      with uv=keep this lays the mesh's own islands out again, each scaled to
                      its share of the surface (Average Islands Scale), without cutting new ones
  margin_method=SCALED|ADD|FRACTION   how Blender reads island_margin and pack_margin. ADD is
                      the plainest: the margin is that share of the UV square on every side
Normals of the low mesh (the normal map is made for these, so they are set before the bake)
  normals=clear|keep  clear: drop the stored normals, smooth, edges over sharp_angle made sharp
  sharp_angle=<degrees, 0 = all smooth>
The bake (Cycles, selected to active: rays from the low mesh's surface find the dense one)
  size=2048           pixels each way of all three maps
  samples=1           Cycles samples
  device=GPU|CPU      GPU tries OptiX, then CUDA, and falls back to the CPU if neither starts
  cage_extrusion=0.02 metres the ray starts outside the low surface
  max_ray_distance=0.04 metres the ray may travel (0 = no limit)
  cage=fixed|auto     auto sets the two from the meshes instead: the extrusion is four times
                      the distance within which 99% of the low surface finds the dense one
                      (never under a millimetre), and the ray may travel twice that
  margin=8            pixels the baked colours are spread beyond each island
  margin_type=ADJACENT_FACES|EXTEND
  one_thread_normal=false   bake the normal map on the CPU with Blender's render threads set
                      to one, and the other two maps as `device` says: a try at making the
                      normal map come out the same bytes every time
  colour=emit|diffuse how base colour is read: emit sends the dense model's texture straight
                      out as light (nothing is lit); diffuse is Blender's Diffuse bake with only
                      the Color pass, which leaves out metal parts
  fit=none|bbox       bbox: first stretch the dense model onto the low mesh's bounding box, for
                      a low mesh that is not a reduction of this dense model
What is written
  jpeg=true           store base colour and metallic-roughness as JPEG at jpeg_quality (the
                      normal map stays PNG); false stores all three as PNG
The facts hold the seconds of each step, the device that ran, and a count made without Cycles
of how many of 20,000 points spread evenly over the low surface find the dense surface along
their normal within the ray settings ("ray_check").
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402
import stagelib as lib  # noqa: E402

DEFAULTS = {"high": None, "weld": 1e-6, "uv": "smart", "angle": 66.0, "island_margin": 0.003, "seam_angle": 60.0,
            "pack": "none", "pack_margin": 0.003, "margin_method": "SCALED", "normals": "clear", "sharp_angle": 0.0,
            "size": 2048, "samples": 1, "device": "GPU", "cage_extrusion": 0.02,
            "max_ray_distance": 0.04, "cage": "fixed", "margin": 8, "margin_type": "ADJACENT_FACES",
            "colour": "emit", "fit": "none", "one_thread_normal": False, "jpeg": True, "jpeg_quality": 90, "bake": True}


def edit(obj):
    lib.activate(obj)
    lib.finished(bpy.ops.object.mode_set(mode="EDIT"), "edit mode")
    lib.finished(bpy.ops.mesh.select_all(action="SELECT"), "select all")


def leave(obj):
    lib.finished(bpy.ops.object.mode_set(mode="OBJECT"), "object mode")


def make_uvs(obj, settings, facts):
    mesh = obj.data
    if settings["uv"] == "keep":
        if not mesh.uv_layers:
            raise SystemExit("uv=keep, but the mesh has no UVs")
    else:
        for layer in list(mesh.uv_layers):
            mesh.uv_layers.remove(layer)
        mesh.uv_layers.new(name="UVMap")
    if settings["uv"] == "keep":
        pass
    elif settings["uv"] == "smart":
        edit(obj)
        lib.finished(bpy.ops.uv.smart_project(
            angle_limit=math.radians(settings["angle"]), island_margin=settings["island_margin"],
            margin_method=settings["margin_method"], area_weight=0.0, correct_aspect=True,
            scale_to_bounds=False),
            "Smart UV Project")
        leave(obj)
    elif settings["uv"] == "sharp_unwrap":
        bm = bmesh.new()
        bm.from_mesh(mesh)
        limit, seams = math.radians(settings["seam_angle"]), 0
        for edge in bm.edges:
            sharp = len(edge.link_faces) != 2 or edge.calc_face_angle(0.0) > limit
            edge.seam = sharp
            seams += sharp
        bm.to_mesh(mesh)
        bm.free()
        facts["seams_marked"] = seams
        edit(obj)
        lib.finished(bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=settings["island_margin"]), "Unwrap")
        leave(obj)
    else:
        raise SystemExit(f"unknown uv={settings['uv']!r}")
    if settings["pack"] != "none":
        edit(obj)
        lib.finished(bpy.ops.uv.select_all(action="SELECT"), "select UVs")
        if settings["uv"] == "keep":
            lib.finished(bpy.ops.uv.average_islands_scale(), "Average Islands Scale")
        lib.finished(bpy.ops.uv.pack_islands(
            rotate=True, margin=settings["pack_margin"], margin_method=settings["margin_method"],
            shape_method=settings["pack"].upper(), scale=True), "Pack Islands")
        leave(obj)


def set_normals(obj, settings):
    mesh = obj.data
    if settings["normals"] != "clear":
        return
    if mesh.has_custom_normals:
        lib.activate(obj)
        lib.finished(bpy.ops.mesh.customdata_custom_splitnormals_clear(), "clear custom normals")
    mesh.shade_smooth()
    if settings["sharp_angle"] > 0:
        mesh.set_sharp_from_angle(angle=math.radians(settings["sharp_angle"]))


def ray_check(low, high, settings, samples=20000):
    """Without Cycles: from points on the low surface, does a ray along the surface normal,
    started cage_extrusion outside and limited to max_ray_distance, meet the dense surface?"""
    def tree(obj):
        mesh = obj.data
        mesh.calc_loop_triangles()
        world = obj.matrix_world
        points = [world @ v.co for v in mesh.vertices]
        tris = [tuple(t.vertices) for t in mesh.loop_triangles]
        return points, tris
    high_points, high_tris = tree(high)
    bvh = BVHTree.FromPolygons(high_points, high_tris)
    low_points, low_tris = tree(low)
    # Points are spread evenly over the surface, not over the triangles: a triangle is picked
    # with a chance in proportion to its area, then a point within it. The seed is fixed.
    rng = random.Random(1)
    areas = [((low_points[b] - low_points[a]).cross(low_points[c] - low_points[a])).length for a, b, c in low_tris]
    picked = rng.choices(low_tris, weights=areas, k=samples)
    reach = settings["max_ray_distance"] or 1e9
    out_by = settings["cage_extrusion"]
    missed, offsets, nearest = 0, [], []
    for a, b, c in picked:
        pa, pb, pc = low_points[a], low_points[b], low_points[c]
        normal = (pb - pa).cross(pc - pa)
        if normal.length < 1e-12:
            continue
        normal.normalize()
        u, v = rng.random(), rng.random()
        if u + v > 1.0:
            u, v = 1.0 - u, 1.0 - v
        centre = pa + (pb - pa) * u + (pc - pa) * v
        hit = bvh.ray_cast(centre + normal * out_by, -normal, reach)
        nearest.append(bvh.find_nearest(centre)[3])
        if hit[0] is None:
            missed += 1
        else:
            offsets.append(abs(hit[3] - out_by))
    offsets.sort(); nearest.sort()
    n = max(1, len(offsets))
    pick = lambda values, share: values[min(len(values) - 1, int(share * len(values)))] if values else None
    return {"points": len(nearest), "missed": missed, "missed_share": missed / max(1, len(nearest)),
            "hit_distance_from_low_surface": {"median": pick(offsets, 0.5), "p95": pick(offsets, 0.95),
                                              "p99": pick(offsets, 0.99), "largest": offsets[-1] if offsets else None},
            "nearest_dense_surface": {"median": pick(nearest, 0.5), "p95": pick(nearest, 0.95),
                                      "p99": pick(nearest, 0.99), "largest": nearest[-1] if nearest else None},
            "hits_further_than_twice_p99_nearest": sum(1 for o in offsets if o > 2 * (pick(nearest, 0.99) or 0)) / n}


def use_device(scene, wanted, facts):
    scene.render.engine = "CYCLES"
    facts["device_wanted"] = wanted
    if wanted == "GPU":
        prefs = bpy.context.preferences.addons["cycles"].preferences
        for kind in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                found = [d for d in prefs.devices if d.type == kind]
                if not found:
                    continue
                for device in prefs.devices:
                    device.use = device.type == kind
                scene.cycles.device = "GPU"
                facts["device"] = kind
                facts["device_names"] = [d.name for d in found]
                return
            except Exception as error:  # a device type this build or machine does not have
                facts.setdefault("device_errors", []).append(f"{kind}: {error}")
    scene.cycles.device = "CPU"
    facts["device"] = "CPU"


def texture_of(material, socket_name):
    """The Image Texture node feeding a Principled BSDF input, through any nodes between."""
    principled = next(n for n in material.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    seen, stack = set(), [principled.inputs[socket_name]]
    while stack:
        socket = stack.pop()
        for link in socket.links:
            node = link.from_node
            if node.bl_idname == "ShaderNodeTexImage":
                return node
            if node.name not in seen:
                seen.add(node.name)
                stack.extend(node.inputs)
    return None


def emit_only(material, image_node):
    """Rewire a material so that it gives off one texture as light and nothing else."""
    tree = material.node_tree
    output = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeOutputMaterial" and n.is_active_output)
    emission = tree.nodes.new("ShaderNodeEmission")
    tree.links.new(image_node.outputs["Color"], emission.inputs["Color"])
    for link in list(output.inputs["Surface"].links):
        tree.links.remove(link)
    tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return emission


def main():
    source, target, facts_path, settings = lib.arguments(DEFAULTS)
    clock = lib.Clock()
    low = lib.one_object(source)
    low.name = "low"
    clock.lap("import_low")
    facts = {"stage": "uv_bake", "source": source, "settings": settings, "low_before": lib.describe(low)}
    if settings["weld"] > 0:
        bm = bmesh.new()
        bm.from_mesh(low.data)
        before = len(bm.verts)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=settings["weld"])
        facts["weld_joined"] = before - len(bm.verts)
        bm.to_mesh(low.data)
        bm.free()
        clock.lap("weld")
    make_uvs(low, settings, facts)
    clock.lap("uvs")
    set_normals(low, settings)
    clock.lap("normals")

    size = settings["size"]
    scene = bpy.context.scene
    if settings["bake"]:
        if not settings["high"]:
            raise SystemExit("high=<dense.glb> is needed to bake")
        before = set(bpy.context.scene.objects)
        lib.finished(bpy.ops.import_scene.gltf(filepath=settings["high"], merge_vertices=True), "import high")
        highs = [o for o in bpy.context.scene.objects if o not in before and o.type == "MESH"]
        lib.activate(highs[0], highs)
        if len(highs) > 1:
            lib.finished(bpy.ops.object.join(), "join high")
        high = bpy.context.view_layer.objects.active
        high.name = "high"
        clock.lap("import_high")
        facts["high"] = lib.describe(high)
        if settings["fit"] == "bbox":
            (l0, l1), (h0, h1) = lib.bounds(low.data, low.matrix_world), lib.bounds(high.data, high.matrix_world)
            scale = [(l1[i] - l0[i]) / (h1[i] - h0[i]) for i in range(3)]
            move = Matrix.Translation(Vector(l0)) @ Matrix.Diagonal(Vector(scale + [1.0])) @ Matrix.Translation(-Vector(h0))
            high.data.transform(move @ high.matrix_world)
            high.matrix_world = Matrix.Identity(4)
            high.parent = None
            facts["fit_scale"] = scale
            clock.lap("fit")
        if settings["cage"] == "auto":
            first = ray_check(low, high, settings)
            settings["cage_extrusion"] = max(0.001, 4.0 * first["nearest_dense_surface"]["p99"])
            settings["max_ray_distance"] = 2.0 * settings["cage_extrusion"]
            facts["cage_chosen"] = {"cage_extrusion": settings["cage_extrusion"],
                                    "max_ray_distance": settings["max_ray_distance"]}
        facts["ray_check"] = ray_check(low, high, settings)
        clock.lap("ray_check")

        use_device(scene, settings["device"], facts)
        scene.cycles.samples = settings["samples"]
        scene.cycles.use_denoising = False
        scene.cycles.use_adaptive_sampling = False

        # The material the low mesh will be exported with: three images wired as glTF wants.
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
        images, nodes = {}, {}
        for key, colour_space in (("basecolor", "sRGB"), ("metallic_roughness", "Non-Color"), ("normal", "Non-Color")):
            image = bpy.data.images.new(f"baked_{key}", size, size, alpha=False, float_buffer=False)
            image.colorspace_settings.name = colour_space
            node = tree.nodes.new("ShaderNodeTexImage")
            node.image = image
            images[key], nodes[key] = image, node
        low.data.materials.clear()
        low.data.materials.append(material)

        high_material = high.data.materials[0]
        sources = {"basecolor": texture_of(high_material, "Base Color"),
                   "metallic_roughness": texture_of(high_material, "Roughness") or texture_of(high_material, "Metallic"),
                   "normal": texture_of(high_material, "Normal")}
        facts["high_textures"] = {k: (n.image.name if n and n.image else None) for k, n in sources.items()}

        def bake(key, kind, **more):
            for node in tree.nodes:
                node.select = False
            nodes[key].select = True
            tree.nodes.active = nodes[key]
            lib.activate(low, [high, low])
            lib.finished(bpy.ops.object.bake(
                type=kind, use_selected_to_active=True, cage_extrusion=settings["cage_extrusion"],
                max_ray_distance=settings["max_ray_distance"], margin=settings["margin"],
                margin_type=settings["margin_type"], use_clear=True, target="IMAGE_TEXTURES",
                save_mode="INTERNAL", **more), f"bake {key}")
            clock.lap("bake_" + key)

        def bake_all():
            # The normal map first, while the dense model's own material is still whole: the
            # bake then holds both the shape the low mesh lost and the dense model's own normal map.
            if settings["one_thread_normal"]:
                device, mode, threads = scene.cycles.device, scene.render.threads_mode, scene.render.threads
                scene.cycles.device, scene.render.threads_mode, scene.render.threads = "CPU", "FIXED", 1
            bake("normal", "NORMAL", normal_space="TANGENT", normal_r="POS_X", normal_g="POS_Y", normal_b="POS_Z")
            if settings["one_thread_normal"]:
                scene.cycles.device, scene.render.threads_mode = device, mode
                if mode == "FIXED":
                    scene.render.threads = threads
            if settings["colour"] == "diffuse":
                bake("basecolor", "DIFFUSE", pass_filter={"COLOR"})
            elif sources["basecolor"] is not None:
                emission = emit_only(high_material, sources["basecolor"])
                bake("basecolor", "EMIT")
                high_material.node_tree.nodes.remove(emission)
            if sources["metallic_roughness"] is not None:
                emit_only(high_material, sources["metallic_roughness"])
                bake("metallic_roughness", "EMIT")

        try:
            bake_all()
        except RuntimeError as error:
            if facts["device"] == "CPU":
                raise
            facts["gpu_bake_error"] = str(error)
            print("GPU bake failed, trying the CPU:", error, flush=True)
            scene.cycles.device = "CPU"
            facts["device"] = "CPU (after the GPU failed)"
            bake_all()

        # Wire the three images the way the glTF exporter reads them.
        tree.links.new(nodes["basecolor"].outputs["Color"], principled.inputs["Base Color"])
        if sources["metallic_roughness"] is not None:
            separate = tree.nodes.new("ShaderNodeSeparateColor")
            tree.links.new(nodes["metallic_roughness"].outputs["Color"], separate.inputs["Color"])
            tree.links.new(separate.outputs["Green"], principled.inputs["Roughness"])
            tree.links.new(separate.outputs["Blue"], principled.inputs["Metallic"])
        else:
            tree.nodes.remove(nodes["metallic_roughness"])
        normal_map = tree.nodes.new("ShaderNodeNormalMap")
        tree.links.new(nodes["normal"].outputs["Color"], normal_map.inputs["Color"])
        tree.links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
        material.use_backface_culling = True   # glTF doubleSided = false, as Tripo's own material
        # The exporter copies an image's bytes only when the image comes from a file and is
        # unchanged; anything else it encodes again as PNG, whatever file_format says. So each
        # baked image is saved beside the output, in the format wanted, and packed from there.
        folder = os.path.splitext(target)[0] + "_textures"
        os.makedirs(folder, exist_ok=True)
        for key, image in images.items():
            as_jpeg = settings["jpeg"] and key != "normal"
            image.filepath_raw = os.path.join(folder, f"{key}.{'jpg' if as_jpeg else 'png'}")
            image.file_format = "JPEG" if as_jpeg else "PNG"
            image.save(quality=settings["jpeg_quality"])
            image.source = "FILE"
            image.reload()
            image.pack()
        facts["images"] = {k: {"size": list(i.size), "file_format": i.file_format,
                               "colorspace": i.colorspace_settings.name, "is_dirty": i.is_dirty,
                               "source": i.source} for k, i in images.items()}
        bpy.data.objects.remove(high)
        clock.lap("material")

    facts["low_after"] = lib.describe(low)
    facts["after"] = lib.defects(low.data)
    lib.activate(low)
    lib.finished(bpy.ops.export_scene.gltf(
        filepath=target, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
        export_animations=False, export_skins=False, export_morph=False, export_cameras=False,
        export_lights=False, export_extras=False, export_image_format="AUTO",
        export_image_quality=settings["jpeg_quality"], export_materials="EXPORT",
        export_texcoords=True, export_normals=True, export_tangents=False,
        export_draco_mesh_compression_enable=False), "glTF export")
    clock.lap("export")
    facts["seconds"] = clock.steps
    lib.save_facts(facts_path, facts)


main()
