"""kiln trials 2 and 3: a leaf-cluster atlas with alpha, and a sheet of brush-stroke alpha shapes.

    uv run --project <clone>/oil python kiln-trial/leaves_strokes.py <out_dir> [--seed 5]

The engine has no alpha channel. Each cv.stroke() returns a Mark with per-pixel coverage, so this script
accumulates that into its own alpha (alpha = 1 - prod(1 - coverage)). That is our code on top of the kit.
Writes leaf_atlas.png (RGBA, 1024x1024, 2x2 clusters), leaf_atlas_on_magenta.png (to check fringes),
stroke_alphas.png (L, 1024x512, 4x2 strokes) and a report line.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image

from atelier import Canvas, Palette, brush

pal = Palette(["lead_white", "yellow_ochre", "cadmium_yellow", "viridian", "terre_verte", "burnt_umber", "ultramarine"])


class Alpha:
    def __init__(self, shape):
        self.keep = np.ones(shape, np.float64)

    def add(self, mark):
        if len(mark.s):
            self.keep[mark.ys, mark.xs] *= 1 - np.clip(mark.coverage, 0, 1)

    def u8(self):
        return np.round(255 * (1 - self.keep)).astype(np.uint8)


def leaf_atlas(out, seed, N=1024):
    t0 = time.time()
    cv = Canvas(N, N, seed=seed)
    mid = pal.mix(("viridian", 1), ("yellow_ochre", 0.8), ("burnt_umber", 0.3))
    cv.ground(mid, texture="panel", tone=1.0)      # leaf-green under everything, so soft edges fringe green, not white
    rng, al = cv.rng, Alpha(cv.shape)
    half = N // 2
    for cy in (0, 1):
        for cx in (0, 1):
            ox, oy = cx * half, cy * half
            root = np.array([ox + half * 0.5 + rng.normal(0, 20), oy + half * 0.92])
            tip = np.array([ox + half * 0.5 + rng.normal(0, 40), oy + half * 0.12])
            bend = (root + tip) / 2 + [rng.normal(0, 40), 0]
            al.add(cv.stroke(brush("rigger", size=3.0), [root, bend, tip], "burnt_umber", pressure=[1.0, 0.7, 0.3]))
            leaves = []
            for t in np.linspace(0.12, 1.0, 11):
                p = (1 - t) ** 2 * root + 2 * t * (1 - t) * bend + t ** 2 * tip
                for side in (-1, 1):
                    a = -np.pi / 2 + side * rng.uniform(0.5, 1.2)
                    length = rng.uniform(55, 95) * (1.1 - 0.45 * t)
                    leaves.append((p, a, length, t))
            for i in rng.permutation(len(leaves)):
                p, a, length, t = leaves[i]
                d = np.array([np.cos(a), np.sin(a)])
                n = np.array([-d[1], d[0]])
                end = p + d * length
                # keep every leaf inside its cell with a margin, or the atlas bleeds across cells
                end = np.clip(end, [ox + 24, oy + 24], [ox + half - 24, oy + half - 24])
                midp = (p + end) / 2 + n * rng.normal(0, 0.12 * length)
                shade = rng.uniform(0, 1)
                dark = pal.mix(("viridian", 1), ("ultramarine", 0.25), ("burnt_umber", 0.35), ("lead_white", 0.1 + 0.3 * shade))
                light = pal.mix(("viridian", 0.6), ("cadmium_yellow", 0.7), ("lead_white", 0.5 + 0.6 * shade))
                al.add(cv.stroke(brush("filbert", size=1.5 * length / 80, load=1.4), [p, midp, end], dark, pressure=[0.25, 1.0, 0.2]))
                al.add(cv.stroke(brush("round_bristle", size=0.55 * length / 80, load=0.8),
                                 [p + 0.25 * (end - p) + 3 * n, midp + 4 * n, p + 0.8 * (end - p) + 2 * n], light,
                                 pressure=[0.3, 0.8, 0.2]))
    rgb, a = cv.to_srgb_uint8(), al.u8()
    Image.fromarray(np.dstack([rgb, a])).save(out / "leaf_atlas.png")
    bg = np.empty_like(rgb)
    bg[:] = (255, 0, 255)
    comp = (rgb * (a[..., None] / 255.0) + bg * (1 - a[..., None] / 255.0)).round().astype(np.uint8)
    Image.fromarray(comp).save(out / "leaf_atlas_on_magenta.png")
    Image.fromarray(a).save(out / "leaf_atlas_alpha.png")
    cells = [a[y:y + half, x:x + half] for y in (0, half) for x in (0, half)]
    border = max(int(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]).max()) for c in cells)
    return {"what": "leaf_atlas", "seconds": round(time.time() - t0, 1), "strokes": cv.strokes,
            "opaque_share": round(float((a > 128).mean()), 3), "semi_share": round(float(((a > 8) & (a < 247)).mean()), 3),
            "max_alpha_on_cell_borders": border}


def stroke_alphas(out, seed, W=1024, H=512):
    t0 = time.time()
    cv = Canvas(W, H, seed=seed)
    cv.ground("#000000", texture="linen", tone=1.0)   # the tooth is what makes a dry brush break up
    al = Alpha(cv.shape)
    names = ["filbert", "flat_bristle", "dry_bristle", "fan", "round_bristle", "palette_knife", "rigger", "round_soft"]
    cw, ch = W // 4, H // 2
    for i, name in enumerate(names):
        ox, oy = (i % 4) * cw, (i // 4) * ch
        xs = np.linspace(ox + 36, ox + cw - 36, 5)
        ys = oy + ch / 2 + 40 * np.sin(np.linspace(0, np.pi, 5) + i)
        b = brush(name)
        b = brush(name, size=min(3.0, 70 / b.width_px), load=0.7 if name in ("dry_bristle", "fan") else 1.0)
        al.add(cv.stroke(b, np.column_stack([xs, ys]), "#ffffff", pressure=[0.5, 1.0, 0.9, 0.7, 0.3]))
    a = al.u8()
    Image.fromarray(a).save(out / "stroke_alphas.png")
    cells = [a[(i // 4) * ch:(i // 4 + 1) * ch, (i % 4) * cw:(i % 4 + 1) * cw] for i in range(8)]
    border = max(int(np.concatenate([c[0], c[-1], c[:, 0], c[:, -1]]).max()) for c in cells)
    return {"what": "stroke_alphas", "seconds": round(time.time() - t0, 1), "strokes": cv.strokes,
            "coverage_per_cell": [round(float((c > 128).mean()), 3) for c in cells], "max_alpha_on_cell_borders": border}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    reports = [leaf_atlas(args.out, args.seed), stroke_alphas(args.out, args.seed)]
    (args.out / "leaves_strokes_report.json").write_text(json.dumps(reports, indent=2) + "\n")
    for r in reports:
        print(json.dumps(r))
