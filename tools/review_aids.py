"""Review aids: ways of looking at a render that show what detail hides.

    python tools/review_aids.py views <image.png> [more.png ...]
        Beside each image, writes <name>_aids.png: the image, its value map
        (five levels of grey) and its squint view (blurred). Put a reference
        or benchmark image through the same command to compare like with like.

    python tools/review_aids.py blind <a.png> <b.png> <out.png>
        Writes the two images side by side in a random order, labelled only
        "left" and "right", and writes which is which to <out>.key.txt. Judge
        the sheet first; open the key after the verdict is written down.

These are aids for the eye, not gates: nothing here passes or fails.
"""

import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

VALUE_LEVELS = 5
SQUINT_BLUR_SHARE = 0.02  # blur radius as a share of image width


def magick(*args):
    subprocess.run(["magick", *map(str, args)], check=True)


def views(image):
    image = Path(image)
    out = image.with_name(f"{image.stem}_aids.png")
    width = int(subprocess.run(["magick", "identify", "-format", "%w", str(image)], check=True, capture_output=True, text=True).stdout)
    with tempfile.TemporaryDirectory() as tmp:
        values, squint = Path(tmp) / "values.png", Path(tmp) / "squint.png"
        magick(image, "-colorspace", "Gray", "+dither", "-posterize", VALUE_LEVELS, values)
        magick(image, "-blur", f"0x{width * SQUINT_BLUR_SHARE:.1f}", squint)
        magick(
            "montage", "-background", "#202124", "-fill", "white", "-pointsize", "22",
            "-label", "as rendered", image,
            "-label", f"value map ({VALUE_LEVELS} levels)", values,
            "-label", "squint", squint,
            "-tile", "3x", "-geometry", "+4+4", out,
        )
    print(out)


def blind(a, b, out):
    out = Path(out)
    pair = [Path(a), Path(b)]
    if secrets.randbelow(2):
        pair.reverse()
    magick(
        "montage", "-background", "#202124", "-fill", "white", "-pointsize", "26",
        "-label", "left", pair[0], "-label", "right", pair[1],
        "-tile", "2x", "-geometry", "+6+6", out,
    )
    key = out.with_name(out.name + ".key.txt")
    key.write_text(f"left: {pair[0]}\nright: {pair[1]}\n")
    print(f"{out}\nkey (open after the verdict): {key}")


if len(sys.argv) >= 3 and sys.argv[1] == "views":
    for path in sys.argv[2:]:
        views(path)
elif len(sys.argv) == 5 and sys.argv[1] == "blind":
    blind(*sys.argv[2:])
else:
    sys.exit(__doc__)
