"""tall_grass_1_dry: one draw of the tall grass generator (source/tall_grass/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("tall_grass").build_clump(spec)
