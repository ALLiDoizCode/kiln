#!/usr/bin/env python3
"""Run one command and record what it cost: the trial's stand-in for `/usr/bin/time -v`,
which this machine does not have.

    python3 scripts/timed.py <run name> <log folder> -- <command> [args...]

Writes <log folder>/<run name>.log (the command's output) and <run name>.run.json:
wall-clock seconds, the peak resident memory of the process itself (from wait4, the same
figure `time -v` prints as "Maximum resident set size"; a command that only starts another,
as tools/bl does with exec, is that other), the exit status or the signal that killed it, and
the least memory the whole machine had available while it ran (MemAvailable in /proc/meminfo,
read every half second). The command is killed when that falls under FLOOR_MB, so a run cannot
push the machine into swap; the record then says "stopped_for_memory".
Exits with the command's own status (128 + signal if it was killed).
"""
import json
import os
import signal
import subprocess
import sys
import threading
import time

FLOOR_MB = int(os.environ.get("TRIAL_MEMORY_FLOOR_MB", "2000"))


def available_mb():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return -1


def main():
    name, folder = sys.argv[1:3]
    command = sys.argv[sys.argv.index("--") + 1:]
    os.makedirs(folder, exist_ok=True)
    log_path = os.path.join(folder, name + ".log")
    state = {"least": available_mb(), "stopped": False, "done": False}
    started = time.time()
    with open(log_path, "wb") as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)

        def watch():
            while not state["done"]:
                now = available_mb()
                state["least"] = min(state["least"], now)
                if 0 <= now < FLOOR_MB:
                    state["stopped"] = True
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    return
                time.sleep(0.5)

        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
        _, status, usage = os.wait4(child.pid, 0)
        state["done"] = True
    wall = time.time() - started
    killed_by = os.WTERMSIG(status) if os.WIFSIGNALED(status) else None
    code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 128 + killed_by
    record = {
        "name": name, "command": command,
        "started": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(started)),
        "wall_seconds": round(wall, 2),
        "user_seconds": round(usage.ru_utime, 2), "system_seconds": round(usage.ru_stime, 2),
        "peak_rss_mb": round(usage.ru_maxrss / 1024, 1),
        "exit_status": code,
        "signal": signal.Signals(killed_by).name if killed_by else None,
        "core_dumped": bool(os.WCOREDUMP(status)) if killed_by else False,
        "least_available_mb": state["least"], "stopped_for_memory": state["stopped"],
        "threads": os.environ.get("KILN_BLENDER_THREADS", "all"),
    }
    with open(os.path.join(folder, name + ".run.json"), "w") as f:
        json.dump(record, f, indent=1)
        f.write("\n")
    print(f"TIMED {name}: {wall:.1f} s, peak {record['peak_rss_mb']:.0f} MB, exit {code}"
          + (f" ({record['signal']})" if killed_by else "")
          + (" STOPPED FOR MEMORY" if state["stopped"] else ""))
    return code


if __name__ == "__main__":
    sys.exit(main())
