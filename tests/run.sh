#!/usr/bin/env bash
# Tests for the gates themselves: every check must be able to fail.
# Needs a passing `tools/gate.sh` for tracer, crate and rock first (uses their builds and exports).
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

expect_id() { # <check id> <name> <command...>: the command must fail, and name that check
  local id="$1" name="$2"; shift 2
  "$@" > "$tmp/out" 2>&1; local got=$?
  if [[ $got -eq 1 ]] && grep -q -- "$id" "$tmp/out"; then echo "ok         $name"
  else echo "FAIL       $name: exit $got, wanted 1 and a failure of $id"; grep -E '^FAIL|"(painted|uv|flat)\.' "$tmp/out" | tail -5; failures=$((failures + 1)); fi
}

tamper() { # <python expression mutating m> [manifest] -> path of a tampered manifest
  python -c "import json,sys; m=json.load(open('${2:-$manifest}')); $1; json.dump(m, open('$tmp/m.json','w'))"
  echo "$tmp/m.json"
}

expect 0 "L1 mutation tests" tools/bl tests/test_validate.py

smoke() { cargo run -q -p asset_smoke -- "$@"; }
cat_fail() { cat "$1"; return 1; }
expect 0 "L4 passes the real manifest"      smoke "$glb" "$manifest"
expect 1 "L4 catches a triangle mismatch"   smoke "$glb" "$(tamper 'm["triangles"] += 1')"
expect 1 "L4 catches a missing node"        smoke "$glb" "$(tamper 'm["nodes"] = ["nope"]')"
expect 1 "L4 catches a missing attribute"   smoke "$glb" "$(tamper 'm["attributes"] += ["TANGENT"]')"
expect 1 "L4 catches reversed facing"       smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"][2], b["max"][2] = -b["max"][2], -b["min"][2]')"
expect 1 "L4 catches a Z-up export"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["min"] = [-0.5, -1.5, 0.0]; b["max"] = [1.0, 0.5, 1.0]')"
expect 1 "L4 catches a wrong scale"         smoke "$glb" "$(tamper 'b=m["bounds"]; b["max"] = [v * 100 for v in b["max"]]')"
expect 1 "L4 catches a wrong colour"         smoke "$glb" "$(tamper 'm["materials"]["m_tracer"][0] += 0.05')"
expect 1 "L4 catches a renamed material"    smoke "$glb" "$(tamper 'm["materials"] = {"m_other": [0.5, 0.5, 0.5]}')"
python tests/flip_normals.py "$glb" "$tmp/flipped_normals.glb"
expect 1 "L4 catches normals against winding" smoke "$tmp/flipped_normals.glb" "$manifest"
cat > "$tmp/inside_out.py" <<PY
import bmesh, bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
mesh = bpy.data.objects["tracer"].data
bm = bmesh.new(); bm.from_mesh(mesh); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(mesh)
bpy.ops.export_scene.gltf(filepath="$tmp/inside_out.glb", export_format="GLB")
PY
tools/bl "$tmp/inside_out.py" > /dev/null 2>&1
expect 1 "L4 catches an inside-out mesh"    smoke "$tmp/inside_out.glb" "$manifest"
# The rock with every face lit flat: the same triangles, but no soft edges.
cat > "$tmp/hard_edges.py" <<PY
import bmesh, bpy
bpy.ops.wm.open_mainfile(filepath="source/rock/out/rock.blend")
rock = bpy.data.objects["rock"]
bm = bmesh.new(); bm.from_mesh(rock.data)
for face in bm.faces: face.smooth = False
flat = bpy.data.meshes.new("rock_flat"); bm.to_mesh(flat); flat.materials.append(rock.data.materials[0])
rock.data = flat
bpy.ops.export_scene.gltf(filepath="$tmp/hard_edges.glb", export_format="GLB")
PY
tools/bl "$tmp/hard_edges.py" > /dev/null 2>&1
expect 0 "L4 passes the real rock"          smoke assets/models/rock.glb assets/models/rock.manifest.json
expect 1 "L4 catches hard edges on a soft-edged asset" smoke "$tmp/hard_edges.glb" assets/models/rock.manifest.json

# Painted shading: the rock painted wrongly, or laid out wrongly, against the real manifest.
rock=assets/models/rock.glb; rock_manifest=assets/models/rock.manifest.json
broken() { tools/bl tests/paint_mutations.py "$1" "$tmp/$1.glb" > /dev/null 2>&1; echo "$tmp/$1.glb"; }
expect_id "flat.no_texture"        "L4 catches a texture on a flat-coloured asset"  smoke "$rock" "$(tamper 'del m["painted"]' "$rock_manifest")"
expect_id "painted.present"        "L4 catches a painted asset with no texture"     smoke "$(broken unpainted)" "$rock_manifest"
expect_id "painted.present"        "L4 catches painted shading asked of a flat asset" smoke "$glb" "$(tamper 'm["painted"] = json.load(open("'$rock_manifest'"))["painted"]')"
expect_id "painted.factor"         "L4 catches a tint multiplied over the texture"  smoke "$(broken tinted_factor)" "$rock_manifest"
expect_id "painted.texture_size"   "L4 catches a texture of the wrong size"         smoke "$(broken small_texture)" "$rock_manifest"
expect_id "painted.colour"         "L4 catches paint over the wrong colour"         smoke "$(broken wrong_colour)" "$rock_manifest"
expect_id "painted.gradient"       "L4 catches a missing base-to-top gradient"      smoke "$(broken no_gradient)" "$rock_manifest"
expect_id "painted.edges_lighter"  "L4 catches missing edge light"                  smoke "$(broken no_edge_light)" "$rock_manifest"
expect_id "painted.crevices_darker" "L4 catches a missing crevice shadow"           smoke "$(broken no_crevice_shadow)" "$rock_manifest"
expect_id "painted.range"          "L4 catches texels burnt out to white"           smoke "$(broken burnt_out)" "$rock_manifest"
expect_id "painted.open_faces"     "L4 catches an edge width that leaves no open face" smoke "$rock" "$(tamper 'm["painted"]["edge_width_m"] = 5.0' "$rock_manifest")"
expect_id "uv.no_overlap"          "L4 catches overlapping UVs"                     smoke "$(broken stacked_uvs)" "$rock_manifest"
expect_id "uv.in_unit_square"      "L4 catches UVs off the texture"                 smoke "$(broken uvs_off_the_texture)" "$rock_manifest"
smoke "$(broken shrunk_uvs)" "$rock_manifest" > "$tmp/shrunk.out" 2>&1
expect_id "uv.coverage"            "L4 catches a mostly unused texture"             cat_fail "$tmp/shrunk.out"
expect_id "uv.texel_density"       "L4 catches texels too coarse for 0.5 m"         cat_fail "$tmp/shrunk.out"

printf 'not a glb' > "$tmp/bad.glb"
expect 1 "L4 catches an unloadable file"    smoke "$tmp/bad.glb" "$manifest"

view() { cargo run -q -p asset_view -- "$@"; }
expect 0 "L4b renders the real asset"       view "$glb" "$manifest" --screenshot "$tmp/shot.png"
expect 1 "L4b fails on an unloadable file"  view "$tmp/bad.glb" "$manifest" --screenshot "$tmp/bad.png"

# A GLB that is valid glTF but outside the Bevy profile: Draco-compressed.
cat > "$tmp/draco.py" <<PY
import bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
bpy.ops.export_scene.gltf(filepath="$tmp/draco.glb", export_format="GLB", export_draco_mesh_compression_enable=True)
PY
tools/bl "$tmp/draco.py" > /dev/null 2>&1
expect 0 "L2b passes the real export"       python tools/bevy_lint.py "$glb"
expect 1 "L2b catches Draco compression"    python tools/bevy_lint.py "$tmp/draco.glb"
expect 0 "L2b passes the real painted rock" python tools/bevy_lint.py "$rock"
expect_id "images.decodable" "L2b catches a JPEG texture" python tools/bevy_lint.py "$(broken jpeg)"

# L0: a brief whose numbers disagree with its spec, and a spec number with no row in the brief.
lint_copy() { # <sed expression applied to the copied brief>
  rm -rf source/zz_lint; cp -r source/crate source/zz_lint
  sed -i 's/"asset": "crate"/"asset": "zz_lint"/; s/"objects": \["crate"\]/"objects": ["zz_lint"]/' source/zz_lint/spec.json
  sed -i "$1" source/zz_lint/brief.md
}
trap 'rm -rf "$tmp" source/zz_lint' EXIT
lint_copy 's/`\["crate"\]`/`["zz_lint"]`/'
expect 0 "L0 passes a consistent brief"     python tools/lint_spec.py zz_lint
lint_copy 's/`\["crate"\]`/`["zz_lint"]`/; s/| `recess_m.m_crate_panel` | `0.05` |/| `recess_m.m_crate_panel` | `0.03` |/'
expect 1 "L0 catches a brief/spec mismatch" python tools/lint_spec.py zz_lint
lint_copy 's/`\["crate"\]`/`["zz_lint"]`/; /`max_triangles`/d'
expect 1 "L0 catches an untraced spec number" python tools/lint_spec.py zz_lint
rm -rf source/zz_lint
# L0, painted shading: the rock's spec with one thing wrong.
paint_copy() { # <python expression mutating spec s and its painted block p>
  rm -rf source/zz_lint; mkdir source/zz_lint; cp source/rock/brief.md source/zz_lint/
  sed -i 's/`\["rock"\]`/`["zz_lint"]`/' source/zz_lint/brief.md
  python -c "import json; s=json.load(open('source/rock/spec.json')); s['asset']='zz_lint'; s['objects']=['zz_lint']; p=s['painted_shading']; $1; json.dump(s, open('source/zz_lint/spec.json','w'))"
}
paint_copy 'pass'
expect 0 "L0 passes the painted rock's spec"  python tools/lint_spec.py zz_lint
paint_copy 'del p["edge_width_m"]'
expect_id "spec.painted_shading"     "L0 catches a missing painted key"       python tools/lint_spec.py zz_lint
paint_copy 'p["growth"] = "moss green"'
expect_id "spec.painted_shading"     "L0 catches a colour that is not hex"    python tools/lint_spec.py zz_lint
paint_copy 'p["texture_px"] = 1000'
expect_id "spec.painted_texture_px"  "L0 catches an odd texture size"         python tools/lint_spec.py zz_lint
paint_copy 'p["base_tint"], p["top_tint"] = p["top_tint"], p["base_tint"]'
expect_id "spec.painted_base_darker" "L0 catches a base lighter than the top" python tools/lint_spec.py zz_lint
paint_copy 'p["crevice_shadow"] = 1.5'
expect_id "spec.painted_amounts"     "L0 catches an impossible shadow amount" python tools/lint_spec.py zz_lint
paint_copy 's["attributes"].remove("TEXCOORD_0")'
expect_id "spec.painted_needs_uvs"   "L0 catches painted shading with no UVs" python tools/lint_spec.py zz_lint
paint_copy 'del s["painted_shading"]'
expect_id "spec.painted_needs_uvs"   "L0 catches UVs on a flat-coloured asset" python tools/lint_spec.py zz_lint
rm -rf source/zz_lint

# L5b: an approved sheet, then the same sheet with something drawn on it.
base=source/tracer/review/zz_base
trap 'rm -rf "$tmp" source/zz_lint "$base"' EXIT
mkdir -p "$base"; cp source/tracer/review/final/sheet.png "$base/sheet.png"
expect 0 "L5b passes when never approved"   python tools/baseline.py check tracer zz_base
python tools/baseline.py approve tracer zz_base > /dev/null
expect 0 "L5b passes an unchanged sheet"    python tools/baseline.py check tracer zz_base
magick "$base/sheet.png" -fill red -draw 'rectangle 100,100 700,700' "$base/sheet.png"
expect 1 "L5b catches a changed sheet"      python tools/baseline.py check tracer zz_base
rm -rf "$base"

echo; [[ $failures -eq 0 ]] && echo "all gate tests passed" || echo "$failures gate tests failed"
exit $((failures > 0))
