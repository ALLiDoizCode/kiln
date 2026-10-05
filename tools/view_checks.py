"""Gate L4c: bark as a player standing against the trunk sees it, measured in a Bevy screenshot.

The gate takes the picture with `asset_view --stand 0.5 --pitch 0`: a player's
eye 0.5 m from the trunk, looking straight at it. Bark is found by colour
(brown: more red than green, more green than blue, and not grey). The picture
is cut into windows about a hand across at that distance, and in each window
that is all bark two things are measured, after taking out the slope of the
light across it:

- tone: the step in lightness a few pixels (about 4 mm of bark) across the
  trunk, as a share of the window's mean lightness. It is the median step of
  the window, not the mean: the line where a lit side of the trunk meets a
  shaded one, or the edge of a cast shadow, is a large step along one line
  and no step anywhere else, and flat brown planes must score near nothing
  however they are lit.
- grain: that step, over the same step up and down the trunk. Streaks along
  the trunk score above 1.

The asset's score is the median window. The thresholds are in the spec
(`skeleton.min_view_tone`, `skeleton.min_view_grain`) and come from the
benchmark tree seen from the same camera (source/tree/brief.md).

Usage: tools/bl tools/view_checks.py <asset> <screenshot.png> [--measure]
       With --measure the asset's name is only a label, no spec is read and nothing fails.
"""

import statistics
import sys
from pathlib import Path

import bpy
import numpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline import Asset, Checks, script_args

WINDOW_PX = 160  # about 0.1 m of bark 0.3 m from the eye, in a 1024 px picture 75 degrees across
STRIDE_PX = 80
STEP_PX = 6  # about 4 mm of bark
MIN_WINDOWS = 3
LUMA = (0.2126, 0.7152, 0.0722)


def bark_windows(path):
    """(tone, grain) of every window of the picture that is all bark."""
    image = bpy.data.images.load(str(path))
    width, height = image.size
    pixels = numpy.empty(width * height * 4, dtype=numpy.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    rgb = pixels.reshape(height, width, 4)[::-1, :, :3]
    red, green, blue = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    bark = (red > green * 1.08) & (green > blue * 1.04) & (red - blue > 0.25 * red)
    light = rgb @ numpy.array(LUMA, dtype=numpy.float32)
    found = []
    for top in range(0, height - WINDOW_PX + 1, STRIDE_PX):
        for left in range(0, width - WINDOW_PX + 1, STRIDE_PX):
            if bark[top : top + WINDOW_PX, left : left + WINDOW_PX].mean() < 0.995:
                continue
            patch = light[top : top + WINDOW_PX, left : left + WINDOW_PX].astype(numpy.float64)
            # Take out the plane that fits it best: the light falling off round a trunk is not grain.
            ys, xs = numpy.mgrid[0:WINDOW_PX, 0:WINDOW_PX]
            basis = numpy.column_stack((xs.ravel(), ys.ravel(), numpy.ones(WINDOW_PX * WINDOW_PX)))
            level = patch - (basis @ numpy.linalg.lstsq(basis, patch.ravel(), rcond=None)[0]).reshape(patch.shape)
            across = numpy.median(numpy.abs(level[:, STEP_PX:] - level[:, :-STEP_PX]))
            along = numpy.median(numpy.abs(level[STEP_PX:, :] - level[:-STEP_PX, :]))
            # A window with no step either way has no grain to give a direction to.
            found.append((float(across / patch.mean()), float(across / along) if along > 1e-6 else 1.0))
    return found


if __name__ == "__main__":
    args = script_args()
    name, picture = args[0], Path(args[1])
    windows = bark_windows(picture)
    tone = statistics.median(w[0] for w in windows) if windows else 0.0
    grain = statistics.median(w[1] for w in windows) if windows else 0.0
    print(f"{name} bark in {picture.name}: {len(windows)} windows of bark; the typical step in tone across the trunk is {tone:.4f} of the mean; steps across the trunk are {grain:.2f} times steps along it")
    if "--measure" in args:
        sys.exit(0)
    asset = Asset(name)
    want = asset.spec()["skeleton"]
    checks = Checks("L4c-view", name)
    checks.check("view.bark_seen", len(windows) >= MIN_WINDOWS, f"{len(windows)} windows of {WINDOW_PX} px in {picture} are all bark; need {MIN_WINDOWS} to measure it: the trunk is not in the picture")
    checks.check("view.bark_tone", tone >= want["min_view_tone"], f"from 0.5 m the typical step in the bark's tone, 4 mm across the trunk in a hand-sized window, is {tone:.4f} of its mean; spec wants at least {want['min_view_tone']}: flat brown planes do not read as bark")
    checks.check("view.bark_grain", grain >= want["min_view_grain"], f"from 0.5 m, tone steps across the trunk are {grain:.2f} times the steps along it; spec wants at least {want['min_view_grain']}: grain runs along a trunk")
    checks.finish(asset.report("L4c-view"))
