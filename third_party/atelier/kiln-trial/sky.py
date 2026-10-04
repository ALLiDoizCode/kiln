"""kiln trial 4: a painted sky backdrop with cumulus, in the 'gouache' settings SKILL.md gives
(oil engine, impasto near 0, no weave, no varnish).

    uv run --project <clone>/oil python kiln-trial/sky.py <out_dir> [--width 2048] [--seed 11]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

from atelier import Canvas, Palette, brush, fields, studio
from atelier.color import linear_to_srgb

pal = Palette(["titanium_white", "naples_yellow", "cobalt_blue", "cerulean_blue", "ultramarine", "madder_lake", "raw_umber"])


def srgb8(lin):
    return np.round(linear_to_srgb(np.clip(lin, 0, 1)) * 255).astype(np.uint8)


def mottle(rng, shape, scale):
    h, w = shape
    s = max(1, int(scale))
    z = zoom(rng.standard_normal((h // s + 4, w // s + 4)), s, order=3)[:h, :w]
    return (z - z.mean()) / z.std()


def paint(out, W, seed):
    H, S = W // 2, W / 2048
    t0 = time.time()
    rng = np.random.default_rng([seed, 1])
    y, x = np.mgrid[:H, :W].astype(np.float32)
    v = y / H
    top = pal.mix(("cobalt_blue", 1), ("ultramarine", 0.4), ("titanium_white", 0.6))
    low = pal.mix(("cerulean_blue", 0.5), ("titanium_white", 2.5), ("naples_yellow", 0.3))
    img = top + (low - top) * (v ** 0.8)[..., None]
    # cumulus: thresholded noise at two scales, flat bases, lit tops, cool shadow undersides
    n = mottle(rng, (H, W), 0.11 * W) + 0.45 * mottle(rng, (H, W), 0.035 * W)
    cloud = np.clip((n - 0.55 + 0.9 * (v - 0.45)) / 0.25, 0, 1) * np.clip((0.92 - v) / 0.1, 0, 1)
    lit = np.clip(gaussian_filter(cloud, 0.012 * W) - np.roll(gaussian_filter(cloud, 0.012 * W), int(0.03 * W), axis=0), 0, 1)
    shadow = pal.mix(("cobalt_blue", 0.5), ("madder_lake", 0.15), ("raw_umber", 0.15), ("titanium_white", 1.6))
    light = pal.mix(("titanium_white", 3), ("naples_yellow", 0.35))
    body = shadow + (light - shadow) * np.clip(2.5 * lit, 0, 1)[..., None]
    img = (img + (body - img) * cloud[..., None]).astype(np.float32)

    cv = Canvas(W, H, seed=seed)
    cv.ground(low, texture="panel", tone=0.9)
    flow = fields.combine((fields.constant(0), 1 - cloud), (fields.contour(cloud, sigma=0.008 * W), cloud),
                          (fields.noise(0.12 * W, cv.rng, spread=20), 0.3))
    passes = [brush("flat_bristle", size=3.6 * S, impasto=0.0), brush("flat_bristle", size=1.6 * S, impasto=0.0),
              brush("filbert", size=0.8 * S, impasto=0.02)]
    stats = cv.paint_from_design(img, passes, field=flow, jitter=0.03)
    cv.wet_in_wet(gaussian_filter((v < 0.4).astype(np.float32), 20 * S), strength=0.5, reach=16 * S, angle=0)
    cv.dry()
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(srgb8(img)).save(out / "sky_design.png")
    studio.save(cv.to_srgb_uint8(), out / "sky_flat.png", canvas=cv)
    f = cv.to_srgb_uint8().astype(np.float32)
    report = {"size": [W, H], "seed": seed, "seconds": round(time.time() - t0, 1), "strokes": cv.strokes,
              "wrap_seam_x": round(float(np.abs(f[:, 0] - f[:, -1]).mean()), 2),
              "inner_x": round(float(np.abs(np.diff(f, axis=1)).mean()), 2), "passes": stats}
    (out / "sky_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "passes"}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--width", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    paint(a.out, a.width, a.seed)
