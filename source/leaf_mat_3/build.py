"""leaf_mat_3: one draw of the leaf mat generator (source/leaf_mat/generator.py), from this spec's seed and bounds.

Run through tools/build.py, which supplies an empty scene and saves the result.
"""

from plant_parts import family_generator


def build(spec):
    return family_generator("leaf_mat").build_mat(spec)
