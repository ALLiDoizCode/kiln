"""Send one ComfyUI prompt (API format) to a local server and time it.

    venv/bin/python run_prompt.py <prompt.json> <out_dir> [--server 127.0.0.1:8189]

Writes <out_dir>/run.json: wall-clock seconds per node (from the server's own "executing" events),
the peak of the graphics card's used memory (whole card, by nvidia-smi, sampled twice a second),
the card's used memory just before the prompt, the peak resident memory of the ComfyUI process and
its children (Blender, when a node starts it), and the error if the prompt failed.
Reads nothing but the prompt; the server does the work.
"""
import asyncio, json, os, subprocess, sys, time, uuid
import aiohttp

def gpu_used_mib():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.strip()
    return int(out.splitlines()[0])

def gpu_proc_mib(pids):
    out = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout
    total = 0
    for line in out.splitlines():
        try:
            pid, mem = [x.strip() for x in line.split(",")]
            if int(pid) in pids: total += int(mem)
        except ValueError: pass
    return total

def tree_pids(root):
    pids, todo = set(), [root]
    while todo:
        p = todo.pop()
        if p in pids: continue
        pids.add(p)
        try:
            for t in os.listdir(f"/proc/{p}/task"):
                with open(f"/proc/{p}/task/{t}/children") as fh:
                    todo += [int(c) for c in fh.read().split()]
        except OSError: pass
    return pids

def rss_mib(pids):
    total = 0
    for p in pids:
        try:
            with open(f"/proc/{p}/status") as fh:
                for line in fh:
                    if line.startswith("VmRSS:"): total += int(line.split()[1]) // 1024
        except OSError: pass
    return total

def server_pid(port):
    out = subprocess.run(["pgrep", "-f", f"main.py --listen 127.0.0.1 --port {port}"], capture_output=True, text=True).stdout.split()
    return int(out[0]) if out else None

async def main():
    prompt_path, out_dir = sys.argv[1], sys.argv[2]
    server = sys.argv[sys.argv.index("--server") + 1] if "--server" in sys.argv else "127.0.0.1:8189"
    os.makedirs(out_dir, exist_ok=True)
    prompt = json.load(open(prompt_path))
    titles = {k: v.get("_meta", {}).get("title", v["class_type"]) for k, v in prompt.items()}
    client = uuid.uuid4().hex
    pid = server_pid(server.split(":")[1])
    stats = {"baseline_gpu_used_mib": gpu_used_mib(), "peak_gpu_used_mib": 0, "peak_gpu_process_mib": 0,
             "peak_rss_mib": 0, "min_ram_available_mib": 10**9, "samples": []}
    stop = False
    t0 = time.time()

    async def sampler():
        loop = asyncio.get_running_loop()
        while not stop:
            pids = tree_pids(pid) if pid else set()
            g = await loop.run_in_executor(None, gpu_used_mib)
            gp = await loop.run_in_executor(None, gpu_proc_mib, pids)
            r = rss_mib(pids)
            avail = 0
            with open("/proc/meminfo") as fh:
                for line in fh:
                    if line.startswith("MemAvailable:"): avail = int(line.split()[1]) // 1024
            stats["peak_gpu_used_mib"] = max(stats["peak_gpu_used_mib"], g)
            stats["peak_gpu_process_mib"] = max(stats["peak_gpu_process_mib"], gp)
            stats["peak_rss_mib"] = max(stats["peak_rss_mib"], r)
            stats["min_ram_available_mib"] = min(stats["min_ram_available_mib"], avail)
            stats["samples"].append([round(time.time() - t0, 1), g, gp, r, avail])
            await asyncio.sleep(0.5)

    events, result = [], {"status": "unknown"}
    async with aiohttp.ClientSession() as s:
        async with s.ws_connect(f"http://{server}/ws?clientId={client}", max_msg_size=0) as ws:
            task = asyncio.create_task(sampler())
            async with s.post(f"http://{server}/prompt", json={"prompt": prompt, "client_id": client}) as r:
                body = await r.json()
                if "prompt_id" not in body:
                    result = {"status": "rejected", "error": body}
                    stop = True
            pid_ = body.get("prompt_id")
            while not stop:
                msg = await ws.receive()
                if msg.type != aiohttp.WSMsgType.TEXT:
                    if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        result = {"status": "connection lost"}; break
                    continue
                m = json.loads(msg.data); d = m.get("data", {})
                if d.get("prompt_id") != pid_: continue
                now = round(time.time() - t0, 2)
                if m["type"] == "executing":
                    events.append([now, d.get("node")])
                    if d.get("node") is None: result = {"status": "ok"}; break
                elif m["type"] == "execution_cached":
                    events.append([now, "cached:" + ",".join(d.get("nodes", []))])
                elif m["type"] == "execution_success":
                    result = {"status": "ok"}; break
                elif m["type"] == "execution_error":
                    result = {"status": "error", "node": d.get("node_id"), "node_type": d.get("node_type"),
                              "message": d.get("exception_message"), "type": d.get("exception_type"),
                              "traceback": d.get("traceback")}
                    break
            stop = True
            await task
    total = round(time.time() - t0, 2)
    per_node, order = {}, []
    ev = [e for e in events if e[1] and not str(e[1]).startswith("cached:")]
    for i, (t, n) in enumerate(ev):
        end = ev[i + 1][0] if i + 1 < len(ev) else total
        key = f"{n} {titles.get(n, '?')}"
        if key not in per_node: order.append(key)
        per_node[key] = round(per_node.get(key, 0) + end - t, 2)
    out = {"prompt": os.path.basename(prompt_path), "result": result, "total_seconds": total,
           "seconds_per_node": {k: per_node[k] for k in order},
           "cached": [e[1] for e in events if str(e[1]).startswith("cached:")], **stats}
    json.dump(out, open(os.path.join(out_dir, "run.json"), "w"), indent=1)
    brief = {k: v for k, v in out.items() if k != "samples"}
    print(json.dumps(brief, indent=1))
    sys.exit(0 if result.get("status") == "ok" else 1)

asyncio.run(main())
