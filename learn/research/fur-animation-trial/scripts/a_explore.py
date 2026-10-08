"""Prototype A, step 0: how far does each vertex of the fused model sit from a smoothed copy?
    tools/bl scripts/a_explore.py <model.glb> <facts.json>
"""
import numpy as np
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import furlib as F
import sys, os
src, out = F.args()
obj = F.load_one_mesh(src)
me = obj.data
co, e, tri = F.coords(me), F.edges(me), F.triangles(me)
el = np.linalg.norm(co[e[:, 0]] - co[e[:, 1]], axis=1)
facts = {"vertices": len(co), "edges": len(e), "triangles": len(tri),
         "edge_length": {"median": float(np.median(el)), "p5": float(np.percentile(el, 5)), "p95": float(np.percentile(el, 95))},
         "box_min": co.min(0).tolist(), "box_max": co.max(0).tolist(), "smoothings": {}}
for name, it, taubin in [("laplace_10", 10, False), ("laplace_30", 30, False), ("laplace_100", 100, False),
                         ("taubin_30", 30, True), ("taubin_100", 100, True), ("taubin_300", 300, True)]:
    s = F.smooth(co, e, it, taubin=taubin)
    d = np.linalg.norm(co - s, axis=1)
    facts["smoothings"][name] = {
        "box_size": (s.max(0) - s.min(0)).tolist(),
        "moved_m": {str(p): float(np.percentile(d, p)) for p in (10, 50, 75, 90, 95, 99, 100)},
        "over_5mm": int((d > 0.005).sum()), "over_10mm": int((d > 0.01).sum()), "over_20mm": int((d > 0.02).sum()),
    }
F.write_json(out, facts)
print(open(out).read())
