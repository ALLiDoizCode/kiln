"""kiln trial 5: repaint one of our own Blender renders with the engine's Hertzmann pass (paint_from_design).

    uv run --project <clone>/oil python kiln-trial/repaint.py <render.png> <out_dir> [--seed 2]

An offline painterly filter: the render is the 'design'. Writes repaint.png, its review sheet, and a blind-free
side-by-side (render | repaint). SKILL.md's own flow never does this (its rule is 'no reference images').
"""
import sys, time, json
from pathlib import Path
import numpy as np
from PIL import Image
from atelier import Canvas, studio

src, out = Path(sys.argv[1]), Path(sys.argv[2])
seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 2
img = np.asarray(Image.open(src).convert("RGB"))
H, W = img.shape[:2]
t0 = time.time()
cv = Canvas(W, H, seed=seed)
cv.ground("raw_umber", texture="panel", tone=0.5)
stats = cv.paint_from_design(img, passes=3)
out.mkdir(parents=True, exist_ok=True)
flat = cv.to_srgb_uint8()
studio.save(flat, out / "repaint.png", canvas=cv)
Image.fromarray(np.concatenate([img, flat], axis=1)).save(out / "render_vs_repaint.png")
print(json.dumps({"size": [W, H], "seconds": round(time.time() - t0, 1), "strokes": cv.strokes,
                  "error": [round(s["error"], 3) for s in stats]}))
