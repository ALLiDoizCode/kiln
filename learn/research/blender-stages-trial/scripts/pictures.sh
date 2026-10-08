#!/usr/bin/env bash
# The eight review pictures of a model, into work/pics/<name>/ (ignored by git).
#   scripts/pictures.sh <name> <model.glb> [size, default 0.8]
set -uo pipefail
name="$1"; model="$(realpath "$2")"; size="${3:-0.8}"
repo="$(cd "$(dirname "$0")/../../../.." && pwd)"; out="$(pwd)/work/pics/$name"; mkdir -p "$out"
"$repo/target/release/review_pictures" "$model" --size "$size" --closest 0.5 --out "$out" > "$out/views.json" 2> "$out/renderer.log"
