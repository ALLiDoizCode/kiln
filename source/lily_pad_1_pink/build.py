"""lily_pad_1_pink: one draw of the lily pad generator (source/lily_pad/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("lily_pad").build_group(spec)
