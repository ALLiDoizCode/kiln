"""Grass tuft, variant 2: one draw of the generator (source/grass_tuft/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("grass_tuft").build_tuft(spec)
