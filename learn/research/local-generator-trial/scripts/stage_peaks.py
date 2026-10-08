"""Turn runs/<name>/run.json files into one CSV: seconds and peak memory per node of each run.

    python3 stage_peaks.py runs/crate_r2 runs/boulder_r1 ... > measurements/stages.csv

A node's window is rebuilt from the per-node seconds in the order the server ran them, so a peak is
attributed to the node running when the twice-a-second sample was taken. gpu_process is the ComfyUI
process (and Blender when a node starts it) as nvidia-smi reports it; gpu_card is the whole card,
desktop included.
"""
import csv, json, os, sys
w = csv.writer(sys.stdout)
w.writerow(["run", "node", "seconds", "peak_gpu_process_mib", "peak_gpu_card_mib", "peak_rss_mib"])
for d in sys.argv[1:]:
    r = json.load(open(os.path.join(d, "run.json"))); t = 0.0
    for node, sec in r["seconds_per_node"].items():
        s = [x for x in r["samples"] if t - 0.25 <= x[0] <= t + sec + 0.25]
        w.writerow([os.path.basename(d), node, sec, max([x[2] for x in s], default=""), max([x[1] for x in s], default=""),
                    max([x[3] for x in s], default="")])
        t += sec
    w.writerow([os.path.basename(d), "TOTAL (" + r["result"]["status"] + ")", r["total_seconds"], r["peak_gpu_process_mib"],
                r["peak_gpu_used_mib"], r["peak_rss_mib"]])
