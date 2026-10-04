"""kiln trial 1: a painted rock texture from the atelier oil engine, and how well it tiles.

    uv run --project <clone>/oil python kiln-trial/rock.py <out_dir> [--size 1024] [--seed 3]

Writes rock_flat.png (albedo: canvas colour, no lighting), rock_lit.png (the skill's finish(): raking
light, weave, gloss baked in), rock_tiled2x2.png (flat, repeated, to look at the seams), and prints a seam
measurement: mean abs difference across the wrap edge against the same measure between interior neighbours.
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

from atelier import Canvas, Palette, brush, fields, studio
from atelier.color import linear_to_srgb

pal = Palette(["lead_white", "raw_umber", "burnt_umber", "yellow_ochre", "ultramarine", "terre_verte", "ivory_black"])


def srgb8(lin):
    return np.round(linear_to_srgb(np.clip(lin, 0, 1)) * 255).astype(np.uint8)


def design_map(N, rng):
    """Angular rock planes: Voronoi cells, each one flat value with a top-lit gradient, dark cracks between."""
    y, x = np.mgrid[:N, :N].astype(np.float32)
    pts = rng.uniform(0, N, (22, 2))
    # periodic copies so the PLAN itself tiles; whether the strokes do is what the trial measures
    tiled = np.concatenate([pts + [dx * N, dy * N] for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
    d, idx = cKDTree(tiled).query(np.column_stack([x.ravel(), y.ravel()]), k=2)
    cell = (idx[:, 0] % len(pts)).reshape(N, N)
    edge = np.clip(1 - (d[:, 1] - d[:, 0]).reshape(N, N) / (0.012 * N), 0, 1)
    value = rng.uniform(0.25, 0.75, len(pts))[cell]
    warm = rng.uniform(0, 1, len(pts))[cell]
    cool_grey = pal.mix(("raw_umber", 1), ("ultramarine", 0.35), ("lead_white", 1.4))
    warm_grey = pal.mix(("yellow_ochre", 0.6), ("burnt_umber", 0.7), ("lead_white", 1.6))
    moss = pal.mix(("terre_verte", 1), ("raw_umber", 0.4), ("lead_white", 0.5))
    base = cool_grey + (warm_grey - cool_grey) * warm[..., None]
    base = base + (moss - base) * (0.5 * (warm > 0.85))[..., None]
    img = base * (0.55 + 0.9 * value)[..., None]
    crack = pal.mix(("ivory_black", 1), ("burnt_umber", 0.5))
    img = img + (crack - img) * (0.85 * edge)[..., None]
    return img.astype(np.float32), edge


def paint(out, N, seed):
    S = N / 2048
    t0 = time.time()
    cv = Canvas(N, N, seed=seed)
    design, edge = design_map(N, np.random.default_rng([seed, 1]))
    cv.ground("raw_umber", texture="panel", tone=0.6)
    flow = fields.combine((fields.contour(design, sigma=0.01 * N), 1.0), (fields.noise(0.15 * N, cv.rng), 0.4))
    passes = [brush("flat_bristle", size=3.0 * S, impasto=0.03), brush("flat_bristle", size=1.4 * S, impasto=0.06),
              brush("round_bristle", size=0.7 * S, impasto=0.08)]
    stats = cv.paint_from_design(design, passes, field=flow)
    cv.dry()
    cv.scumble(gaussian_filter(1 - edge, 6 * S), pal.mix(("lead_white", 3), ("yellow_ochre", 0.3)), coverage=0.12, size=0.9 * S)
    cv.dry()
    flat = cv.to_srgb_uint8()
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(srgb8(design)).save(out / "rock_design.png")
    Image.fromarray(flat).save(out / "rock_flat.png")
    studio.save(cv.finish(scale=S, weave=0.0, varnish=0.0), out / "rock_lit.png", canvas=cv)
    Image.fromarray(np.tile(flat, (2, 2, 1))).resize((N, N), Image.LANCZOS).save(out / "rock_tiled2x2.png")

    f = flat.astype(np.float32)
    seam_x = np.abs(f[:, 0] - f[:, -1]).mean()
    seam_y = np.abs(f[0] - f[-1]).mean()
    inner_x = np.abs(np.diff(f, axis=1)).mean()
    inner_y = np.abs(np.diff(f, axis=0)).mean()
    d = srgb8(design).astype(np.float32)
    report = {"size": N, "seed": seed, "seconds": round(time.time() - t0, 1), "strokes": cv.strokes,
              "seam_x": round(float(seam_x), 2), "inner_x": round(float(inner_x), 2),
              "seam_y": round(float(seam_y), 2), "inner_y": round(float(inner_y), 2),
              "design_seam_x": round(float(np.abs(d[:, 0] - d[:, -1]).mean()), 2),
              "passes": stats}
    (out / "rock_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "passes"}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out", type=Path)
    ap.add_argument("--size", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    paint(a.out, a.size, a.seed)
