"""The check on a bake done on the graphics card (tools/paint.py, `bakes_disagree`), on textures made wrong here.

A card out of memory leaves a texture that is black all over, or wrong in part, and the bake
still reports that it finished. No card is needed to show the check telling those from a right
bake: the fine texture is drawn here, two islands with a gradient and a margin on black, and
the coarse one is what a bake eight times smaller gives of the same thing.

Usage: tools/bl tests/bake_check.py <right|black|part_wrong|island_missing>
Exits 1, naming `bake.agrees_with_cpu`, when the check calls the bake wrong.
"""

import sys
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import paint
from pipeline import script_args

(case,) = script_args()
SIZE = 512
small = SIZE // paint.CHECK_SHRINK
across = numpy.linspace(0.2, 0.8, SIZE, dtype=numpy.float32)
painted = numpy.zeros((SIZE, SIZE, 4), dtype=numpy.float32)
painted[:, :, 3] = 1.0
for rows, columns, tint in ((slice(16, 240), slice(16, 496), (1.0, 0.9, 0.8)), (slice(272, 496), slice(16, 240), (0.7, 1.0, 0.7))):
    painted[rows, columns, :3] = across[None, columns, None] * numpy.array(tint, dtype=numpy.float32)
# The small bake of the same thing: each of its texels the mean of the texels it covers, and no bled margin.
coarse = painted.reshape(small, paint.CHECK_SHRINK, small, paint.CHECK_SHRINK, 4).mean(axis=(1, 3))
fine = painted.copy()
# A right bake on the card: a margin bled round each island, and a texel in a hundred a level out.
fine[12:16, 16:496, :3] = fine[16:17, 16:496, :3]
fine[::10, ::10, :3] += 1 / 255

if case == "black":
    fine[:, :, :3] = 0.0  # what one bake out of memory gave: nothing baked at all
elif case == "part_wrong":
    fine[: SIZE // 5, :, :3] = 0.0  # a fifth of the texture never baked: the least wrong of the bakes measured
elif case == "island_missing":
    fine[272:496, 16:240, :3] = 0.0
elif case != "right":
    raise SystemExit(f"no such case: {case}")

share = paint.bakes_disagree(fine, coarse)
wrong = share > paint.CHECK_SHARE
print(f"{'FAIL' if wrong else 'ok'}   bake.agrees_with_cpu: {share:.3f} of the small bake's texels disagree (at most {paint.CHECK_SHARE})")
sys.exit(1 if wrong else 0)
