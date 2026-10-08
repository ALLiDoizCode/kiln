"""Stage 1 of the trial: import a .glb and export it untouched, to see what the trip changes.

    tools/bl roundtrip.py <in.glb> <out.glb> <facts.json> [merge_vertices=true]
        [shading=NORMALS|SMOOTH|FLAT] [image_format=AUTO|JPEG|WEBP|NONE] [tangents=false]
        [clear_custom_normals=false]

The export settings are those of kiln's scale_to_size stage unless a setting says otherwise.
What changed is measured from outside, on the two files, by scripts/glb_diff.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
import stagelib as lib  # noqa: E402

DEFAULTS = {"merge_vertices": True, "shading": "NORMALS", "image_format": "AUTO",
            "tangents": False, "clear_custom_normals": False}


def main():
    source, target, facts_path, settings = lib.arguments(DEFAULTS)
    clock = lib.Clock()
    meshes = lib.read(source, settings["merge_vertices"], settings["shading"])
    clock.lap("import")
    facts = {"stage": "roundtrip", "source": source, "settings": settings,
             "objects": [dict(lib.describe(o), name=o.name) for o in meshes],
             "images": [{"name": i.name, "size": list(i.size), "file_format": i.file_format,
                         "colorspace": i.colorspace_settings.name, "packed": bool(i.packed_file),
                         "is_dirty": i.is_dirty, "source": i.source}
                        for i in bpy.data.images if i.size[0]]}
    if settings["clear_custom_normals"]:
        for obj in meshes:
            if obj.data.has_custom_normals:
                with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
                    lib.finished(bpy.ops.mesh.customdata_custom_splitnormals_clear(), "clear custom normals")
        clock.lap("clear_custom_normals")
    lib.write(target, image_format=settings["image_format"], tangents=settings["tangents"])
    clock.lap("export")
    facts["seconds"] = clock.steps
    lib.save_facts(facts_path, facts)


main()
