"""Gate L4d: a rock's sides turned away from the sun, as Bevy shows them, keep a value that can be read.

The gate takes the picture with `asset_view --back --close --shade <report.json>`.
The viewer says which pixels of its own picture are sides of the asset turned
away from its sun and which are turned toward it (by the triangle a ray through
each pixel meets, never by the picture), and gives the median luminance of
each, linear, as the picture shows it. Only the viewer's ambient light reaches a
side turned away, so what is painted there is all that sets its value: a base
colour, tints, side shade and crevice shadow that multiply down too far leave
it a dark field in which nothing painted can be seen.

The least value is in `conventions.toml` (`[shade]`), and is the benchmark
rock's own shaded side from the same camera under the same light.

Usage: python tools/shade_check.py <asset> <shade.json> [--report <out.json>]
"""

import json
import sys

from pipeline import Checks, conventions

name, measured = sys.argv[1:3]
report = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
with open(measured) as f:
    seen = json.load(f)
rules = conventions()["shade"]
away, toward = seen["away"], seen["toward"]
ratio = away["median"] / toward["median"] if toward["median"] > 0 else 0.0
print(f"{name} from the back: sides turned away from the sun have a median luminance of {away['median']:.4f} over {away['pixels']} sampled pixels; sides turned toward it {toward['median']:.4f} over {toward['pixels']}: the shaded side is at {ratio:.2f} of the lit")
checks = Checks("L4d-shade", name)
if checks.check("view.shade_seen", away["pixels"] >= rules["min_pixels"], f"{away['pixels']} sampled pixels of the picture are sides turned away from the sun; need {rules['min_pixels']} to measure them: the shaded side is not in the picture"):
    checks.check("view.shade_value", away["median"] >= rules["min_luminance"], f"seen from the back, the sides turned away from the sun have a median luminance of {away['median']:.4f} in the picture (linear); the conventions want at least {rules['min_luminance']}, the benchmark rock's: what is painted there cannot be read")
checks.finish(report)
