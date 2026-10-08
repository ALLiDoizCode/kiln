#!/usr/bin/env bash
# One object through generation and the chain, with up to three tries, keeping the results.
#   run_chain.sh <name> <image in ComfyUI's input folder> <generator> <target triangles>
# Needs ComfyUI running (start_comfy.sh). Run from learn/research/local-generator-trial/.
set -u
name="$1"; image="$2"; gen="$3"; tris="$4"
LG="$(git rev-parse --show-toplevel)/.tools/local-gen"
python3 scripts/make_prompt.py "runs/$name.prompt.json" --image "$image" --name "$name" --generator "$gen" \
  --resolution 1024 --chain video --close remesh --close-resolution 512 --dense-tris 1000000 \
  --target-tris "$tris" --texture 4096 --blender "$LG/blender-factory"
for try in 1 2 3; do
  out="runs/$name"; [ $try -gt 1 ] && out="runs/${name}_try$try"
  if "$LG/venv/bin/python" scripts/run_prompt.py "runs/$name.prompt.json" "$out" > "$out.stdout.txt" 2>&1; then
    for kind in raw closed highpoly lowpoly; do
      f=$(ls -t "$LG"/out/3d/${name}_${kind}_*.glb 2>/dev/null | head -1); [ -n "$f" ] && cp "$f" "models/${name}_${kind}.glb"
    done
    mkdir -p "$out/bake_maps"; cp "$LG"/out/LODTailorBakeForger/latest/*.png "$out/bake_maps/"
    cp "$LG/out/LODTailorBakeForger/latest/blender_process.log" "$out/bake_forger.log"
    echo "$name: ok on try $try"; exit 0
  fi
  echo "$name: try $try failed: $(grep -m1 '"message"' "$out.stdout.txt" | cut -c1-160)"
done
exit 1
