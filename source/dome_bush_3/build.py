"""Dome bush, variant 3: one draw of the generator (source/dome_bush/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("dome_bush").build_bush(spec)
