"""Tall grass, variant 2: one draw of the generator (source/tall_grass/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("tall_grass").build_clump(spec)
