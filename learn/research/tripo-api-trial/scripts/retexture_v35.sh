#!/usr/bin/env bash
# Texture an existing Tripo task again with texture model v3.5 and `delight` on or off.
#
#   scripts/retexture_v35.sh <name> <task id> <reference image> <true|false>
#
# NOT TESTED AGAINST THE API: written on 2026-10-08 with no credits, from the reference page of
# POST /v3/models/texture. It exists because CLI 0.5.2 refuses the texture model `v3.5-20260815`
# on its own texture step (requests/dry-run/probe_retexture_v35_cli.dry-run.json), so the request
# is sent with curl. It uploads the image through the CLI (`tripo files upload`), posts the
# request, and then lets the CLI wait and download (`tripo task watch --download`).
# It does not check the balance or the ledger. Run it only through the balance checks written
# in run_all.sh, and read the balance before and after by hand. Expected cost: 10 credits
# ("Texture (Standard)" on the pricing page). The key is read from TRIPO_API_KEY and never written.
set -euo pipefail
name="$1"; task="$2"; image="$3"; delight="$4"
base="${TRIPO_API_BASE:-https://openapi.tripo3d.ai}"
mkdir -p requests "models/$name"
token=$(tripo files upload "$image" --json | python3 -c 'import json,sys; print(json.load(sys.stdin)["file_token"])')
python3 - "$task" "$token" "$delight" > "requests/$name.request.json" <<'PY'
import json, sys
task, token, delight = sys.argv[1:4]
print(json.dumps({"input": task, "model": "v3.5-20260815", "texture_prompt": {"image": {"file_token": token}},
                  "texture_quality": "standard", "pbr": True, "texture_seed": 1, "delight": delight == "true"}, indent=2))
PY
curl -sS -m 120 -X POST "$base/v3/models/texture" -H "Authorization: Bearer $TRIPO_API_KEY" \
  -H 'Content-Type: application/json' --data @"requests/$name.request.json" \
  -o "requests/$name.response.json" -w 'HTTP %{http_code}\n' | tee "requests/$name.status.txt"
new=$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("data",{}).get("task_id",""))' "requests/$name.response.json")
[ -n "$new" ] || { echo "no task was created: see requests/$name.response.json"; exit 1; }
tripo task watch "$new" --download -o "models/$name" --json --yes > "requests/$name.result.ndjson"
