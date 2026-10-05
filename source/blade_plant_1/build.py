"""Blade plant, variant 1: one draw of the generator (source/blade_plant/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("blade_plant").build_plant(spec)
