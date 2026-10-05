"""flower_scatter_1: one draw of the flower scatter generator (source/flower_scatter/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("flower_scatter").build_scatter(spec)
