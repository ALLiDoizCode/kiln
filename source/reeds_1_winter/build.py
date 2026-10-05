"""reeds_1_winter: one draw of the reeds generator (source/reeds/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("reeds").build_bed(spec)
