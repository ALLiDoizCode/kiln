#!/usr/bin/env bash
# Tests for the gates themselves: every check must be able to fail.
# Needs a passing `tools/gate.sh tracer` first (uses its exported GLB).
set -uo pipefail
cd "$(dirname "$0")/.."
glb=assets/models/tracer.glb
manifest=assets/models/tracer.manifest.json
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
failures=0

expect() { # <expected exit code> <name> <command...>
  local want="$1" name="$2"; shift 2
  "$@" > "$tmp/out" 2>&1; local got=$?
  if [[ $got -eq $want ]]; then echo "ok         $name"
  else echo "FAIL       $name: exit $got, wanted $want"; tail -5 "$tmp/out"; failures=$((failures + 1)); fi
}

tamper() { # <python expression mutating m> -> path of a tampered manifest
  python -c "import json,sys; m=json.load(open('$manifest')); $1; json.dump(m, open('$tmp/m.json','w'))"
  echo "$tmp/m.json"
}

expect 0 "L1 mutation tests" tools/bl tests/test_validate.py

smoke() { cargo run -q -p asset_smoke -- "$@"; }
expect 0 "L4 passes the real manifest"      smoke "$glb" "$manifest"
expect 1 "L4 catches a triangle mismatch"   smoke "$glb" "$(tamper 'm["triangles"] += 1')"
expect 1 "L4 catches a missing node"        smoke "$glb" "$(tamper 'm["nodes"] = ["nope"]')"
expect 1 "L4 catches a missing attribute"   smoke "$glb" "$(tamper 'm["attributes"] += ["TANGENT"]')"
expect 1 "L4 catches reversed facing"       smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"][2], b["max"][2] = -b["max"][2], -b["min"][2]')"
expect 1 "L4 catches a Z-up export"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"] = [-0.5, -1.5, 0.0]; b["max"] = [1.0, 0.5, 1.0]')"
expect 1 "L4 catches a wrong scale"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["max"] = [v * 100 for v in b["max"]]')"
printf 'not a glb' > "$tmp/bad.glb"
expect 1 "L4 catches an unloadable file"    smoke "$tmp/bad.glb" "$manifest"

# A GLB that is valid glTF but outside the Bevy profile: Draco-compressed.
cat > "$tmp/draco.py" <<PY
import bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
bpy.ops.export_scene.gltf(filepath="$tmp/draco.glb", export_format="GLB", export_draco_mesh_compression_enable=True)
PY
tools/bl "$tmp/draco.py" > /dev/null 2>&1
expect 0 "L2b passes the real export"       python tools/bevy_lint.py "$glb"
expect 1 "L2b catches Draco compression"    python tools/bevy_lint.py "$tmp/draco.glb"

echo; [[ $failures -eq 0 ]] && echo "all gate tests passed" || echo "$failures gate tests failed"
exit $((failures > 0))
