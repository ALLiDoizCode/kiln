#!/usr/bin/env bash
# Start ComfyUI on 127.0.0.1:8189 only. Extra arguments are passed on (e.g. --lowvram).
. "$(git rev-parse --show-toplevel)/.tools/local-gen/env.sh"
mkdir -p "$TMPDIR" "$BLENDER_USER_RESOURCES"
cd "$LG/src/ComfyUI"
exec "$LG/venv/bin/python" main.py --listen 127.0.0.1 --port 8189 \
  --output-directory "$LG/out" --input-directory "$LG/input" --user-directory "$LG/user" \
  --temp-directory "$LG/tmp" --disable-api-nodes "$@"
