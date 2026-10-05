#!/usr/bin/env bash
# Tests for the gates themselves: every check must be able to fail.
# Needs a passing `tools/gate.sh` for tracer, crate, rock and tree_1 first (uses their builds, exports and review tiles).
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
expect_id "painted.banding"        "L4 catches a gradient in visible steps"          smoke "$(broken banded)" "$rock_manifest"
expect_id "painted.growth_height"  "L4 catches a rock with no growth at its base"    smoke "$(broken no_growth)" "$rock_manifest"
expect_id "painted.growth_height"  "L4 catches growth all the way up the sides"      smoke "$(broken growth_everywhere)" "$rock_manifest"
expect_id "painted.growth_up"      "L4 catches bare upward-facing surfaces"          smoke "$(broken no_growth_up)" "$rock_manifest"
expect_id "painted.growth_up"      "L4 catches growth carpeting the top, not patchy" smoke "$(broken growth_carpets_the_top)" "$rock_manifest"
expect_id "painted.growth_edges"   "L4 catches bare upper edges"                     smoke "$(broken no_growth_edges)" "$rock_manifest"
expect_id "painted.growth_darker"  "L4 catches growth no darker than the rock"       smoke "$(broken growth_not_darker)" "$rock_manifest"
expect_id "painted.growth_patches" "L4 catches growth in broad patches"              smoke "$(broken growth_broad_patches)" "$rock_manifest"
expect_id "painted.blotches"       "L4 catches planes with no blotches"              smoke "$(broken no_blotches)" "$rock_manifest"
expect_id "painted.blotches"       "L4 catches blotches stronger than asked"         smoke "$(broken harsh_blotches)" "$rock_manifest"
expect_id "painted.blotches_broad" "L4 catches blotches as fine grain"               smoke "$(broken speckle)" "$rock_manifest"
expect_id "painted.side_shade"     "L4 catches sides not darker at mid height"       smoke "$(broken no_side_shade)" "$rock_manifest"
expect_id "painted.open_faces"     "L4 catches an edge width that leaves no open face" smoke "$rock" "$(tamper 'm["painted"]["edge_width_m"] = 5.0' "$rock_manifest")"
expect_id "uv.no_overlap"          "L4 catches overlapping UVs"                     smoke "$(broken stacked_uvs)" "$rock_manifest"
expect_id "uv.in_unit_square"      "L4 catches UVs off the texture"                 smoke "$(broken uvs_off_the_texture)" "$rock_manifest"
smoke "$(broken shrunk_uvs)" "$rock_manifest" > "$tmp/shrunk.out" 2>&1
expect_id "uv.coverage"            "L4 catches a mostly unused texture"             cat_fail "$tmp/shrunk.out"
expect_id "uv.texel_density"       "L4 catches texels too coarse for 0.5 m"         cat_fail "$tmp/shrunk.out"

# Foliage: tree_1 with its leaf pieces coloured, lit or exported wrongly, against the real manifest.
tree=assets/models/tree_1.glb; tree_manifest=assets/models/tree_1.manifest.json
broken_tree() { tools/bl tests/tree_mutations.py "$1" "$tmp/$1.glb" > /dev/null 2>&1; echo "$tmp/$1.glb"; }
expect 0 "L4 passes the real tree"          smoke "$tree" "$tree_manifest"
expect 0 "L4 passes an unbroken tree from the mutation script" smoke "$(broken_tree none)" "$tree_manifest"
expect_id "foliage.two_sided"      "L4 catches leaves seen from one side only"      smoke "$(broken_tree single_sided)" "$tree_manifest"
expect_id "foliage.flat_colour"    "L4 catches a gradient within a leaf piece"      smoke "$(broken_tree gradient_within_piece)" "$tree_manifest"
expect_id "foliage.palette"        "L4 catches leaves painted from another colour"  smoke "$(broken_tree wrong_leaf_colour)" "$tree_manifest"
expect_id "foliage.colour_varies"  "L4 catches neighbouring leaves all one tone"    smoke "$(broken_tree one_tone)" "$tree_manifest"
expect_id "foliage.lighter_above"  "L4 catches pads no lighter above than below"    smoke "$(broken_tree no_gradient)" "$tree_manifest"
expect_id "foliage.bluer_below"    "L4 catches undersides darker but no bluer"      smoke "$(broken_tree grey_underside)" "$tree_manifest"
expect_id "foliage.pieces"         "L4 catches foliage asked of an asset with none" smoke "$rock" "$(tamper 'm["foliage"] = json.load(open("'$tree_manifest'"))["foliage"]; m["foliage"]["material"] = "m_rock"' "$rock_manifest")"
expect_id "painted.present"        "L4 catches bark and leaf on two copies of the texture" smoke "$(broken_tree two_textures)" "$tree_manifest"
expect_id "signed volume"          "L4 catches inside-out bark under open leaves"   smoke "$(broken_tree bark_inside_out)" "$tree_manifest"
# The core under the leaf pieces (ADR 9 as amended), and the bark's grain and close-range texels (ADR 12).
expect_id "foliage.cores"          "L4 catches pads with no core under their leaves" smoke "$(broken_tree no_cores)" "$tree_manifest"
expect_id "foliage.cores"          "L4 catches cores that are not closed"           smoke "$(broken_tree core_open)" "$tree_manifest"
expect_id "foliage.core_colour"    "L4 catches a core as light as the leaves"       smoke "$(broken_tree light_core)" "$tree_manifest"
expect_id "painted.grain"          "L4 catches bark with no grain"                  smoke "$(broken_tree no_grain)" "$tree_manifest"
expect_id "painted.grain_along"    "L4 catches grain running round the limbs"       smoke "$(broken_tree grain_across)" "$tree_manifest"
expect_id "uv.close_density"       "L4 catches a trunk with no more texels than a twig" smoke "$(broken_tree no_close_texels)" "$tree_manifest"

printf 'not a glb' > "$tmp/bad.glb"
expect 1 "L4 catches an unloadable file"    smoke "$tmp/bad.glb" "$manifest"

view() { cargo run -q -p asset_view -- "$@"; }
expect 0 "L4b renders the real asset"       view "$glb" "$manifest" --screenshot "$tmp/shot.png"
expect 1 "L4b fails on an unloadable file"  view "$tmp/bad.glb" "$manifest" --screenshot "$tmp/bad.png"
expect 0 "L4b renders the asset's back"     view "$glb" "$manifest" --back --screenshot "$tmp/back.png"
# The manifest's bounds moved 300 m off: the camera frames empty ground, and no picture may be saved.
expect_id "asset.in_picture" "L4b fails when the asset is not in the picture" view "$glb" "$(tamper 'b=m["bounds"]; b["min"][0] += 300; b["max"][0] += 300')" --screenshot "$tmp/away.png"
expect 1 "L4b saves no picture without the asset in it" test -e "$tmp/away.png"

# L4c: bark seen from 0.5 m, as the gate takes it, with and without its grain.
view_checks() { tools/bl tools/view_checks.py "$@"; }
expect 0 "L4c passes the real tree's bark"  view_checks tree_1 source/tree_1/review/final/bevy_trunk.png
view "$(broken_tree no_grain)" "$tree_manifest" --stand 0.5 --pitch 0 --screenshot "$tmp/flat_bark.png" > /dev/null 2>&1
expect_id "view.bark_tone"  "L4c catches bark that is flat brown at arm's length" view_checks tree_1 "$tmp/flat_bark.png"
view "$(broken_tree grain_across)" "$tree_manifest" --stand 0.5 --pitch 0 --screenshot "$tmp/hoop_bark.png" > /dev/null 2>&1
expect_id "view.bark_grain" "L4c catches grain seen running round the trunk" view_checks tree_1 "$tmp/hoop_bark.png"

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
paint_copy 'del p["blotch_size_m"]'
expect_id "spec.painted_shading"     "L0 catches a blotch with no size"       python tools/lint_spec.py zz_lint
paint_copy 'del p["growth"], p["growth_height_m"]'
expect_id "spec.painted_shading"     "L0 catches growth placed with no growth colour" python tools/lint_spec.py zz_lint
paint_copy 'p["side_shade"] = 1.0'
expect_id "spec.painted_amounts"     "L0 catches a side shade that leaves no light" python tools/lint_spec.py zz_lint
paint_copy 's["fullness"]["min_volume_share"] = 1.5'
expect_id "spec.fullness"            "L0 catches a fullness above the whole box" python tools/lint_spec.py zz_lint
paint_copy 'p["growth_darker"] = 1.0'
expect_id "spec.painted_amounts"     "L0 catches growth darkened to black"    python tools/lint_spec.py zz_lint
paint_copy 'del s["pieces"]["min_step_ratio"]'
expect_id "spec.pieces"              "L0 catches a pieces block with a key missing" python tools/lint_spec.py zz_lint
paint_copy 's["foot"]["min_sides"] = 5'
expect_id "spec.foot"                "L0 catches a foot on more sides than there are" python tools/lint_spec.py zz_lint
paint_copy 's["chamfers"]["min_m2"] = 0.5'
expect_id "spec.chamfers"            "L0 catches a chamfer as big as a large plane" python tools/lint_spec.py zz_lint
paint_copy 's["lean"]["max_upright_share"] = 1.5'
expect_id "spec.lean"                "L0 catches an upright share above the whole" python tools/lint_spec.py zz_lint
paint_copy 's["planes"]["ledge_plane_m2"] = 0.9'
expect_id "spec.planes"              "L0 catches a ledge's smaller plane set above a large one" python tools/lint_spec.py zz_lint
paint_copy 's["planes"]["min_ledge_views"] = 9'
expect_id "spec.planes"              "L0 catches more ledge views than there are views" python tools/lint_spec.py zz_lint
paint_copy 'del s["painted_shading"]'
expect_id "spec.painted_needs_uvs"   "L0 catches UVs on a flat-coloured asset" python tools/lint_spec.py zz_lint
rm -rf source/zz_lint
# L0, trees: tree_1's spec with one thing wrong. Its numbers come from its own brief and its family's.
tree_copy() { # <python expression mutating spec s>
  rm -rf source/zz_lint; mkdir source/zz_lint; cp source/tree_1/brief.md source/zz_lint/
  sed -i 's/`\["tree_1"\]`/`["zz_lint"]`/' source/zz_lint/brief.md
  python -c "import json; s=json.load(open('source/tree_1/spec.json')); s['asset']='zz_lint'; s['objects']=['zz_lint']; $1; json.dump(s, open('source/zz_lint/spec.json','w'))"
}
tree_copy 'pass'
expect 0 "L0 passes a tree variant's spec"   python tools/lint_spec.py zz_lint
tree_copy 's["max_triangles"] = 6000'
expect_id "brief.numbers_match_spec" "L0 catches a variant that disagrees with its family's brief" python tools/lint_spec.py zz_lint
tree_copy 's["family"] = "zz_nope"'
expect_id "spec.family"              "L0 catches a family with no brief"       python tools/lint_spec.py zz_lint
tree_copy 's["open_materials"] = ["m_zz_nope"]'
expect_id "spec.open_materials"      "L0 catches an open material the asset does not have" python tools/lint_spec.py zz_lint
tree_copy 's["open_materials"] = []'
expect_id "spec.foliage_amounts"     "L0 catches foliage that is not an open material" python tools/lint_spec.py zz_lint
tree_copy 'del s["foliage"]["tones"]'
expect_id "spec.foliage"             "L0 catches a missing foliage key"        python tools/lint_spec.py zz_lint
tree_copy 'f=s["foliage"]; f["under_tint"], f["top_tint"] = f["top_tint"], f["under_tint"]'
expect_id "spec.foliage_under_darker" "L0 catches an underside lighter than the top" python tools/lint_spec.py zz_lint
tree_copy 'del s["painted_shading"]; s["attributes"].remove("TEXCOORD_0")'
expect_id "spec.foliage_needs_paint" "L0 catches foliage with no texture to take colour from" python tools/lint_spec.py zz_lint
tree_copy 's["materials"]["m_tree_bark"] = "#e0e0d0"'
expect_id "spec.bark_darker"         "L0 catches bark lighter than the leaves" python tools/lint_spec.py zz_lint
tree_copy 'del s["skeleton"]["min_roots"]'
expect_id "spec.skeleton"            "L0 catches a missing skeleton key"       python tools/lint_spec.py zz_lint
tree_copy 's["skeleton"]["fork_m"] = [3.5, 2.0]'
expect_id "spec.skeleton_amounts"    "L0 catches a fork range given backwards" python tools/lint_spec.py zz_lint
tree_copy 's["variants"]["siblings"] = ["zz_lint"]'
expect_id "spec.variants_amounts"    "L0 catches a variant listed as its own sibling" python tools/lint_spec.py zz_lint
# The core, the lobes, the view from below and the bark's grain (ADR 9 as amended, ADR 12).
tree_copy 's["foliage"]["core_tint"] = "#9fc0c8"'
expect_id "spec.foliage_core_darker" "L0 catches a core lighter than the leaves' underside" python tools/lint_spec.py zz_lint
tree_copy 's["foliage"]["lobes"] = [4, 2]'
expect_id "spec.foliage_core"        "L0 catches a lobe count given backwards" python tools/lint_spec.py zz_lint
tree_copy 's["foliage"]["max_core_seen"] = 1.5'
expect_id "spec.foliage_core"        "L0 catches more core seen than there is foliage" python tools/lint_spec.py zz_lint
tree_copy 'del s["foliage"]["max_seen_into"]'
expect_id "spec.foliage"             "L0 catches a missing limit on the view from below" python tools/lint_spec.py zz_lint
tree_copy 'del s["painted_shading"]["grain_width_m"]'
expect_id "spec.painted_shading"     "L0 catches grain with no width"          python tools/lint_spec.py zz_lint
tree_copy 's["painted_shading"]["grain"] = 1.5'
expect_id "spec.painted_grain"       "L0 catches an impossible grain"          python tools/lint_spec.py zz_lint
tree_copy 'del s["painted_shading"]["close_height_m"]'
expect_id "spec.painted_shading"     "L0 catches close texels with no height"  python tools/lint_spec.py zz_lint
tree_copy 's["painted_shading"]["close_texels_per_m"] = 50.0'
expect_id "spec.painted_close"       "L0 catches close faces asked for fewer texels than any face gets" python tools/lint_spec.py zz_lint
tree_copy 's["skeleton"]["min_view_grain"] = 0.5'
expect_id "spec.skeleton_view"       "L0 catches grain in view asked to run across the trunk" python tools/lint_spec.py zz_lint
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

# L5c: a sheet saved as viewers show it, then the same sheet 16 bits deep with alpha, which they band.
expect 0 "L5c passes the real sheet"        python tools/image_lint.py source/rock/review/final/sheet.png
magick source/rock/review/final/sheet.png -depth 16 "PNG48:$tmp/deep.png"
expect_id "image.eight_bit" "L5c catches a 16-bit sheet"        python tools/image_lint.py "$tmp/deep.png"
magick source/rock/review/final/sheet.png -alpha on "PNG32:$tmp/alpha.png"
expect_id "image.opaque"    "L5c catches a sheet with alpha"    python tools/image_lint.py "$tmp/alpha.png"
# The review aids are review images too.
cp source/rock/review/final/sheet.png "$tmp/aid.png"; python tools/review_aids.py views "$tmp/aid.png" > /dev/null
expect 0 "L5c passes a review aid"          python tools/image_lint.py "$tmp/aid_aids.png"
python tools/review_aids.py blind "$tmp/aid.png" "$tmp/aid.png" "$tmp/blind.png" > /dev/null
expect 0 "L5c passes a blind comparison"    python tools/image_lint.py "$tmp/blind.png"

echo; [[ $failures -eq 0 ]] && echo "all gate tests passed" || echo "$failures gate tests failed"
exit $((failures > 0))
