#!/usr/bin/env bash
# Tests for the gates themselves: every check must be able to fail. The cases are in tests/cases.sh.
# Needs a passing `tools/gate.sh` for tracer, crate, rock, tree_1, tree_2, tree_1_autumn, tree_sapling_1, blade_plant_1, tall_grass_1, reeds_1 and slab_1 first (uses their builds, exports and review tiles).
#
# Usage: tests/run.sh [selector...] [options]
#   no selector, no option   every case
#   <asset>                  the cases that read that asset: tracer, crate, rock, tree_1, ...
#   <gate>                   the cases of that gate: L0, L1, L2b, L2c, L4, L4b, L4c, L4d, L4e, L5b, L5c
#   <tool>                   the cases behind one tool: smoke, view, paint, validate, ... (`--list` shows every tag)
#       Several assets or tools select the cases with any of them, several gates likewise, and
#       gates together with assets or tools select the cases with both: `tests/run.sh L4 rock`.
#   --only <regex>           only the cases whose name or check id matches (grep -E, any case)
#   --changed                only the cases affected by the files changed since the last commit
#   --list                   name the selected cases with what each expects and its tags, and run nothing
#   -j, --jobs <n>           how many cases run at once (default: one per core)
#   --order <file|reverse|random>  the order cases are started in (default: file); the outcomes must not depend on it
#   --timings                after the run, the seconds each case took, slowest first
#   --results <file>         write `<outcome> <tab> <name>` for every case that ran, in file order
#   --fresh                  build every fixture again instead of reusing the kept ones (see "Fixtures" below)
#   --keep                   keep the scratch directory, with each case's output, and say where it is
# Exit code: 0 when every selected case passed, 1 when one failed, 2 when the run could not start
# or the selection named nothing. The last line always says how many cases ran and how many the
# selection skipped; only a line saying ALL ran is a full run.
#
# Fixtures: the rock and tree_1 built and painted with one thing wrong are most of the suite's
# work, a minute of one core each. They are kept in target/gate-test-fixtures beside a hash of
# everything they are made from, and built again only when that changes. --fresh builds them all.
set -uo pipefail
cd "$(dirname "$0")/.."
cases_file=tests/cases.sh
unset KILN_BAKE  # fixtures are baked on the CPU, as the gate bakes: only that bake is the same every time (tools/paint.py)

usage() { sed -n '2,/^set /p' "$0" | sed '$d; s/^# \{0,1\}//'; }
die() { echo "tests/run.sh: $*" >&2; exit 2; }

# The work is arithmetic on one thread per case (tests/run.sh gives each Blender cores / jobs
# threads), so one case per core is quickest; measured on 16 threads, 8 at a time is no quicker.
cores=$(nproc); jobs=$cores
selectors=(); only=""; changed=0; list=0; order=file; timings=0; results_file=""; keep=0; fresh=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -j|--jobs) jobs="${2:-}"; shift ;;
    -j[0-9]*) jobs="${1#-j}" ;;
    --only) only="${2:-}"; [[ -n $only ]] || die "--only needs a pattern"; shift ;;
    --changed) changed=1 ;;
    --list) list=1 ;;
    --order) order="${2:-}"; shift ;;
    --timings) timings=1 ;;
    --results) results_file="${2:-}"; [[ -n $results_file ]] || die "--results needs a file"; shift ;;
    --fresh) fresh=1 ;;
    --keep) keep=1 ;;
    -*) die "unknown option $1 (see --help)" ;;
    *) selectors+=("$1") ;;
  esac
  shift
done
[[ $jobs =~ ^[1-9][0-9]*$ ]] || die "--jobs needs a number, got '$jobs'"
[[ $order =~ ^(file|reverse|random)$ ]] || die "--order is file, reverse or random, got '$order'"

# ---- the cases: one per line of tests/cases.sh, read without running anything

kinds=(); wants=(); names=(); tags=(); lines=()
declare -A seen_name=() known_tag=()
uses=""
while IFS= read -r text || [[ -n $text ]]; do
  if [[ $text =~ ^[[:space:]]*(#|$) ]]; then continue
  elif [[ $text =~ ^uses[[:space:]]+(.+)$ ]]; then uses="${BASH_REMATCH[1]}"; continue
  elif [[ $text =~ ^expect[[:space:]]+([0-9]+)[[:space:]]+\"([^\"]+)\"[[:space:]] ]]; then kinds+=(exit); wants+=("${BASH_REMATCH[1]}"); names+=("${BASH_REMATCH[2]}")
  elif [[ $text =~ ^expect_id[[:space:]]+\"([^\"]+)\"[[:space:]]+\"([^\"]+)\"[[:space:]] ]]; then kinds+=(id); wants+=("${BASH_REMATCH[1]}"); names+=("${BASH_REMATCH[2]}")
  else die "$cases_file: not a case, a comment or a \`uses\` line: $text"
  fi
  name="${names[-1]}"; gate="${name%% *}"
  [[ $gate =~ ^L[0-9][a-z]?$ ]] || die "$cases_file: the name of a case starts with its gate: $name"
  [[ -z ${seen_name[$name]:-} ]] || die "$cases_file: two cases are named: $name"
  [[ -n $uses ]] || die "$cases_file: no \`uses\` line above: $name"
  seen_name[$name]=1
  tags+=("$gate $uses"); lines+=("$text")
  for tag in $gate $uses; do known_tag[$tag]=1; done
done < "$cases_file"
total=${#names[@]}

has_tag() { [[ " ${tags[$1]} " == *" $2 "* ]]; }

# ---- --changed: from the files changed since the last commit to the tags of the cases they affect

tags_of_file() { # <path> -> tags, ALL when every case may be affected, nothing when no case reads it
  case "$1" in
    docs/*|*.md|.claude/*|.gitignore|benchmarks/*|third_party/*) ;;
    # Run by the gate and by no case here: a change to one is proved by tools/gate.sh, not by this suite.
    tools/gate.sh|tools/build.py|tools/export.py|tools/review_render.py|tools/variants_sheet.sh|tools/side_by_side.sh) echo NONE ;;
    tools/lint_spec.py) echo lint_spec ;;
    tools/validate.py|tools/skeleton.py|tests/test_validate.py|tests/fixtures/*) echo validate ;;
    tools/paint.py|tools/foliage.py) echo paint ;;
    tests/paint_mutations.py) echo rock_mutations ;;
    tests/bake_check.py) echo bake_check ;;
    tests/tree_mutations.py) echo tree_mutations ;;
    tests/slab_mutations.py) echo slab_mutations ;;
    tests/pebble_mutations.py) echo pebble_mutations ;;
    tests/cover_mutations.py) echo cover_mutations ;;
    tests/flip_normals.py) echo flip_normals ;;
    crates/asset_smoke/*) echo smoke ;;
    crates/asset_view/*) echo view ;;
    tools/view_checks.py) echo view_checks ;;
    tools/shade_check.py) echo shade_check ;;
    tools/under_checks.py) echo under_checks ;;
    tools/bevy_lint.py) echo bevy_lint ;;
    tools/same_mesh.py) echo same_mesh ;;
    tools/baseline.py) echo baseline ;;
    tools/image_lint.py) echo image_lint ;;
    tools/review_aids.py) echo review_aids ;;
    source/tree/*) echo tree_1 tree_2 tree_3 tree_1_autumn ;;  # the generator, recipes and brief every tree shares
    source/blade_plant/*) echo blade_plant_1 blade_plant_2 blade_plant_3 ;;
    source/tall_grass/*) echo tall_grass_1 tall_grass_2 tall_grass_3 tall_grass_1_dry ;;
    source/reeds/*) echo reeds_1 reeds_2 reeds_3 reeds_1_winter ;;
    source/table_rock/*) echo table_rock_1 ;;  # the generator and the brief table_rock_1 is built with
    tools/stone.py) echo table_rock_1 ;;&  # and the kit; the line for the other families it builds follows
    source/standing_stone/*) echo standing_stone_1_mossy ;;  # the one standing stone a case reads
    source/slab/*) echo slab_1 slab_1_mossy ;;  # the generator and the brief slab_1 is built with
    source/crag/*) echo crag_1 crag_1_mossy ;;
    source/stack/*) echo stack_1 stack_2_mossy ;;
    source/block/*) echo block_2 ;;  # the generator and the brief block_2 is built with
    source/boulder/*) echo boulder_2 ;;  # the generator and the brief boulder_2 is built with
    source/pebble/*) echo pebble_1 pebble_2 pebble_3_mossy ;;  # the generator and the brief pebble_1 and pebble_2 are built with
    source/arch/*) echo arch_1 ;;  # the generator and the brief arch_1 is built with
    tools/stone.py) echo slab_1 crag_1 pebble_1 pebble_2 stack_1 ;;&  # the kit all four are built with
    tools/stone.py) echo arch_1 ;;  # and the arch
    tools/try_seeds.py) ;;  # an aid, read by no case
    source/*/*) local asset="${1#source/}"; echo "${asset%%/*}" ;;
    assets/models/*) local file="${1##*/}"; echo "${file%%.*}" ;;
    # The suite itself, what every script imports, the pinned tools and the standards they all read.
    *) echo ALL ;;
  esac
}

changed_tags=""; changed_all=0
if [[ $changed -eq 1 ]]; then
  files="$( { git diff --name-only HEAD && git ls-files --others --exclude-standard; } 2> /dev/null)" \
    || die "--changed needs git and a commit to compare with"
  echo "changed since the last commit:"
  while IFS= read -r file; do
    [[ -n $file ]] || continue
    found="$(tags_of_file "$file")"
    case "$found" in
      "") echo "  $file: not read by any case" ;;
      NONE) echo "  $file: run by tools/gate.sh and by no case here" ;;
      ALL) echo "  $file: may affect every case"; changed_all=1 ;;
      *) read_by=0; for tag in $found; do [[ -n ${known_tag[$tag]:-} ]] && read_by=1; done
         if [[ $read_by -eq 1 ]]; then echo "  $file: $found"; changed_tags+=" $found"; else echo "  $file: not read by any case"; fi ;;
    esac
  done <<< "$(sort -u <<< "$files")"
  [[ -n $files ]] || echo "  nothing"
  echo
fi

# ---- the selection

gate_selectors=(); tag_selectors=()
for selector in ${selectors[@]+"${selectors[@]}"}; do
  [[ -n ${known_tag[$selector]:-} ]] || die "no case has the tag '$selector'; the tags are: $(printf '%s\n' "${!known_tag[@]}" | sort | xargs)"
  if [[ $selector =~ ^L[0-9][a-z]?$ ]]; then gate_selectors+=("$selector"); else tag_selectors+=("$selector"); fi
done

selected() { # <case index>
  local i=$1 tag hit
  if [[ ${#gate_selectors[@]} -gt 0 ]]; then
    hit=0; for tag in "${gate_selectors[@]}"; do has_tag "$i" "$tag" && hit=1; done; [[ $hit -eq 1 ]] || return 1
  fi
  if [[ ${#tag_selectors[@]} -gt 0 ]]; then
    hit=0; for tag in "${tag_selectors[@]}"; do has_tag "$i" "$tag" && hit=1; done; [[ $hit -eq 1 ]] || return 1
  fi
  if [[ -n $only ]]; then
    grep -qiE -- "$only" <<< "${names[i]}"$'\n'"$([[ ${kinds[i]} == id ]] && echo "${wants[i]}")" || return 1
  fi
  if [[ $changed -eq 1 && $changed_all -eq 0 ]]; then
    hit=0; for tag in $changed_tags; do has_tag "$i" "$tag" && hit=1; done; [[ $hit -eq 1 ]] || return 1
  fi
  return 0
}

chosen=()
for ((i = 0; i < total; i++)); do selected "$i" && chosen+=("$i"); done
ran=${#chosen[@]}; skipped=$((total - ran))
selection="${selectors[*]:-}"
[[ -n $only ]] && selection+="${selection:+ }--only $only"
[[ $changed -eq 1 ]] && selection+="${selection:+ }--changed"

tally() { # the last line of every run: how much of the suite this was
  if [[ $skipped -eq 0 ]]; then echo "ran ALL $total cases$1"
  else echo "PARTIAL RUN: ran $ran of $total cases, $skipped skipped by the selection ($selection)$1"; fi
}

if [[ $list -eq 1 ]]; then
  for i in ${chosen[@]+"${chosen[@]}"}; do
    if [[ ${kinds[i]} == id ]]; then want="fails ${wants[i]}"; else want="exits ${wants[i]}"; fi
    printf '%s\t%s\t%s\n' "${names[i]}" "$want" "${tags[i]}"
  done
  echo; echo "listed, not run: $ran of $total cases${selection:+ ($selection)}"
  exit 0
fi
if [[ $ran -eq 0 ]]; then
  if [[ $changed -eq 1 ]]; then echo "no case is affected by those files"; tally ""; exit 0; fi
  die "the selection ($selection) names none of the $total cases; --list shows them all"
fi

# ---- what the cases run

run_id=$$
scratch="$(mktemp -d)"; fx="$scratch/fixtures"; out="$scratch/results"; mkdir -p "$fx" "$out"
cleanup() {
  rm -rf source/zz_lint_"${run_id}"_* source/tracer/review/zz_base_"${run_id}"_*
  if [[ $keep -eq 1 ]]; then echo "kept: $scratch (results/<n>.log is the output of case n, counted from 0 in file order)"; else rm -rf "$scratch"; fi
}
trap cleanup EXIT
trap 'kill $(jobs -p) 2> /dev/null; exit 130' INT TERM

glb=assets/models/tracer.glb; manifest=assets/models/tracer.manifest.json
rock=assets/models/rock.glb; rock_manifest=assets/models/rock.manifest.json
tree=assets/models/tree_1.glb; tree_manifest=assets/models/tree_1.manifest.json
slab=assets/models/slab_1.glb; slab_manifest=assets/models/slab_1.manifest.json

# The Bevy binaries are built once, here, and run directly: `cargo run` checks the whole workspace
# for changes every time it is called.
bin="${CARGO_TARGET_DIR:-target}/debug"
packages=()
for ((n = 0; n < ran; n++)); do
  has_tag "${chosen[n]}" smoke && [[ " ${packages[*]:-} " != *" asset_smoke "* ]] && packages+=(asset_smoke)
  has_tag "${chosen[n]}" view && [[ " ${packages[*]:-} " != *" asset_view "* ]] && packages+=(asset_view)
done
if [[ ${#packages[@]} -gt 0 ]]; then
  cargo build -q $(printf -- '-p %s ' "${packages[@]}") || die "cargo build failed"
fi
# A bake is all arithmetic and takes every thread it is given, so Blenders running side by side
# share the cores out between them. What a script builds does not depend on the number (tools/bl).
export KILN_BLENDER_THREADS="${KILN_BLENDER_THREADS:-$(( cores / jobs > 0 ? cores / jobs : 1 ))}"
smoke() { "$bin/asset_smoke" "$@"; }
cover() { smoke "assets/models/$1.glb" "assets/models/$1.manifest.json"; }  # <asset>: a gated cover as it is
view() {
  "$bin/asset_view" "$@"; local code=$?
  # Not retried: a crash is reported as the failure it is, with what is known about it.
  if [[ $code -ge 128 ]]; then
    echo "asset_view was killed by signal $((code - 128)) as it exited. It is known to crash now and then in the graphics" >&2
    echo "driver's teardown, mostly on a file it cannot load; run the case again alone (--only) to tell that from a real failure." >&2
  fi
  return $code
}
view_checks() { tools/bl tools/view_checks.py "$@"; }
shade_check() { python tools/shade_check.py "$@"; }
under_checks() { tools/bl tools/under_checks.py "$@"; }

# A case passes or fails here. Each runs in a shell of its own with $tmp to itself.
verdict() { # <ok|FAIL> <name> [why]
  if [[ $1 == ok ]]; then echo "ok         $2"; else echo "FAIL       $2: $3"; fi
  echo "$1" > "$out/$case_n.verdict"
}
fixtures_built() { # <name>: false, with the case failed, when something it was to read could not be made
  [[ ! -e "$tmp/fixture_failed" ]] && return 0
  verdict FAIL "$1" "$(sort -u "$tmp/fixture_failed" | paste -sd ';')"; cat "$tmp"/fixture_failed.log 2> /dev/null | tail -5
  return 1
}
expect() { # <expected exit code> <name> <command...>
  local want="$1" name="$2"; shift 2
  fixtures_built "$name" || return 1
  "$@" > "$tmp/out" 2>&1; local got=$?
  fixtures_built "$name" || return 1
  if [[ $got -eq $want ]]; then verdict ok "$name"
  else verdict FAIL "$name" "exit $got, wanted $want"; tail -6 "$tmp/out"; fi
}
expect_id() { # <check id> <name> <command...>: the command must fail, and name that check
  local id="$1" name="$2"; shift 2
  fixtures_built "$name" || return 1
  "$@" > "$tmp/out" 2>&1; local got=$?
  fixtures_built "$name" || return 1
  if [[ $got -eq 1 ]] && grep -q -- "$id" "$tmp/out"; then verdict ok "$name"
  else verdict FAIL "$name" "exit $got, wanted 1 and a failure of $id"; grep -E '^FAIL|"(painted|uv|flat|foliage)\.|asset_view|driver' "$tmp/out" | tail -6; fi
}

tamper() { # <python expression mutating m> [manifest] -> path of a tampered manifest
  python -c "import json,sys; m=json.load(open('${2:-$manifest}')); $1; json.dump(m, open('$tmp/m.json','w'))"
  echo "$tmp/m.json"
}

# Fixtures: files several cases read, or that take long to make. Each is made once per run, by
# whichever case asks first; the others wait for it. A fixture that cannot be made fails the
# cases that asked for it, so that none passes because the file it was to load is missing.
#
# A fixture given a key is also kept between runs, in $kept, and reused while its key is the same.
# The key is a hash of everything the fixture is made from (`key_of`), so a kept fixture is the
# file a rebuild would give: the builds are deterministic, byte for byte. --fresh rebuilds them all.
fixture() { # [--key <hash>] <file name> <command...> -> the path of that file, made by `command <path>`
  local key=""; if [[ $1 == --key ]]; then key="$2"; shift 2; fi
  local name="$1" file="$fx/$1"; shift
  (
    flock 9
    if [[ ! -e "$file.made" ]]; then
      if [[ -n $key && $fresh -eq 0 && "$(cat "$kept/$name.key" 2> /dev/null)" == "$key" ]] && cp "$kept/$name" "$file" 2> /dev/null; then
        echo yes > "$file.made"; : > "$file.reused"
      elif "$@" "$file" > "$file.log" 2>&1 && [[ -e "$file" ]]; then
        echo yes > "$file.made"
        if [[ -n $key ]]; then
          : > "$file.built"
          rm -f "$kept/$name.key"; cp "$file" "$kept/$name.new.$run_id" && mv "$kept/$name.new.$run_id" "$kept/$name" && echo "$key" > "$kept/$name.key"
        fi
      else echo no > "$file.made"; fi
    fi
  ) 9> "$file.lock"
  if [[ $(< "$file.made") != yes ]]; then
    echo "could not make ${file##*/}" >> "$tmp/fixture_failed"; cat "$file.log" >> "$tmp/fixture_failed.log"
  fi
  echo "$file"
}
once() { # <key> <command...>: the output and exit code of the command, run once per run however many cases ask
  local key="$fx/once_$1"; shift
  (
    flock 9
    [[ -e "$key.code" ]] || { "$@" > "$key.out" 2>&1; echo $? > "$key.code"; }
  ) 9> "$key.lock"
  cat "$key.out"; return "$(< "$key.code")"
}

key_of() { # <files...> -> a hash of those files, every tool the builds import, the standards and the pinned Blender
  { stat -c '%n %s %Y' .tools/blender/blender; sha256sum tools/bl tools/*.py conventions.toml "$@"; } | sha256sum | cut -d' ' -f1
}
kept="$bin/../gate-test-fixtures"; mkdir -p "$kept" || die "cannot make $kept"
rock_key="$(key_of tests/paint_mutations.py source/rock/build.py source/rock/spec.json)" || die "cannot hash the rock's sources"
slab_key="$(key_of tests/slab_mutations.py source/slab_1/build.py source/slab_1/spec.json source/slab/*.py)" || die "cannot hash slab_1's sources"
pebble_key="$(key_of tests/pebble_mutations.py source/pebble_1/build.py source/pebble_1/spec.json source/pebble/*.py)" || die "cannot hash pebble_1's sources"
tree_key="$(key_of tests/tree_mutations.py source/tree_1/build.py source/tree_1/spec.json source/tree/*.py)" || die "cannot hash tree_1's sources"

# The rock, or tree_1, built and painted with one thing wrong and exported. A mutation that only
# changes what painting left starts from the one painted asset of the run (the scripts say which
# may, and refuse the others); the rest build and bake their own.
rock_after_paint=" shrunk_uvs stacked_uvs uvs_off_the_texture tinted_factor jpeg "
tree_after_paint=" none single_sided gradient_within_piece no_cores core_open bark_inside_out two_textures glossy_leaves "
mutated() { tools/bl "$1" "$2" "${@:3}"; }                 # <script> <mutation> <out.glb>
mutated_painted() { tools/bl "$1" "$2" "$4" "$("$3")"; }  # <script> <mutation> <function naming the painted asset> <out.glb>
painted_rock() { fixture --key "$rock_key" rock_painted.blend mutated tests/paint_mutations.py painted; }
painted_tree() { fixture --key "$tree_key" tree_1_painted.blend mutated tests/tree_mutations.py painted; }
broken() {
  if [[ $rock_after_paint == *" $1 "* ]]; then fixture --key "$rock_key" "rock_$1.glb" mutated_painted tests/paint_mutations.py "$1" painted_rock
  else fixture --key "$rock_key" "rock_$1.glb" mutated tests/paint_mutations.py "$1"; fi
}
broken_tree() {
  if [[ $tree_after_paint == *" $1 "* ]]; then fixture --key "$tree_key" "tree_1_$1.glb" mutated_painted tests/tree_mutations.py "$1" painted_tree
  else fixture --key "$tree_key" "tree_1_$1.glb" mutated tests/tree_mutations.py "$1"; fi
}
broken_slab() { fixture --key "$slab_key" "slab_1_$1.glb" mutated tests/slab_mutations.py "$1"; }
# A mossy cover built and painted with its growth wrong one way (tests/cover_mutations.py).
broken_cover() { # <asset> <mutation>
  local family; family="$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['family'])" "source/$1/spec.json")" || return 3
  fixture --key "$(key_of tests/cover_mutations.py "source/$1/build.py" "source/$1/spec.json" "source/$family"/*.py)" "$1_$2.glb" mutated_cover "$1" "$2"
}
mutated_cover() { tools/bl tests/cover_mutations.py "$1" "$2" "$3"; }  # <asset> <mutation> <out.glb>
broken_pebble() { fixture --key "$pebble_key" "pebble_1_$1.glb" mutated tests/pebble_mutations.py "$1"; }
flipped_normals() { fixture flipped_normals.glb python tests/flip_normals.py "$glb"; }
bad_glb() { printf 'not a glb' > "$tmp/bad.glb"; echo "$tmp/bad.glb"; }

# A built asset changed in Blender and exported with the exporter's defaults.
exported() { fixture "$1.glb" export_scene "$1"; }
export_scene() { # <inside_out|hard_edges|two_pieces|piece_inside_out|draco> <out.glb>
  local script="$fx/$1.py"
  case "$1" in
    inside_out) cat > "$script" <<PY
import bmesh, bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
mesh = bpy.data.objects["tracer"].data
bm = bmesh.new(); bm.from_mesh(mesh); bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(mesh)
bpy.ops.export_scene.gltf(filepath="$2", export_format="GLB")
PY
    ;;
    hard_edges) cat > "$script" <<PY
import bmesh, bpy
bpy.ops.wm.open_mainfile(filepath="source/rock/out/rock.blend")
rock = bpy.data.objects["rock"]
bm = bmesh.new(); bm.from_mesh(rock.data)
for face in bm.faces: face.smooth = False
flat = bpy.data.meshes.new("rock_flat"); bm.to_mesh(flat); flat.materials.append(rock.data.materials[0])
rock.data = flat
bpy.ops.export_scene.gltf(filepath="$2", export_format="GLB")
PY
    ;;
    two_pieces|piece_inside_out) cat > "$script" <<PY
# The tracer with a small box pushed into its leg as a second closed piece (ADR 13), the right way out or inside out.
import bmesh, bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
mesh = bpy.data.objects["tracer"].data
bm = bmesh.new(); bm.from_mesh(mesh)
lo, hi = (0.0, 0.3, 0.5), (0.4, 0.5, 0.9)
corners = [bm.verts.new((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
faces = [bm.faces.new([corners[i] for i in face]) for face in ([0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3])]
if "$1" == "piece_inside_out": bmesh.ops.reverse_faces(bm, faces=faces)
bm.to_mesh(mesh)
bpy.ops.export_scene.gltf(filepath="$2", export_format="GLB")
PY
    ;;
    draco) cat > "$script" <<PY
import bpy
bpy.ops.wm.open_mainfile(filepath="source/tracer/out/tracer.blend")
bpy.ops.export_scene.gltf(filepath="$2", export_format="GLB", export_draco_mesh_compression_enable=True)
PY
    ;;
  esac
  tools/bl "$script"
}

# L1: one asset's mutations in one Blender process, or one share of them, or the asset unbroken.
l1() { # <asset> [--part <i>/<n> | --unbroken]
  tools/bl tests/test_validate.py --asset "$@" > "$tmp/l1" 2>&1; local code=$?
  grep -E '^(ok|NOT CAUGHT) ' "$tmp/l1" > "$out/$case_n.mutations"
  cat "$tmp/l1"; return $code
}

# L4b: the viewer with the manifest's bounds moved 300 m off. Two cases read the one run.
away_view() { once away view "$glb" "$(tamper 'b=m["bounds"]; b["min"][0] += 300; b["max"][0] += 300')" --screenshot "$fx/away.png"; }
away_picture_exists() { away_view > /dev/null 2>&1; test -e "$fx/away.png"; }

# L4c: tree_1 with its bark broken, seen as the gate takes the trunk. The check reads the picture,
# so only the picture is asked of the viewer here; L4b is where its exit code is tested.
bark_shot() { fixture "bark_$1.png" bark_view "$1"; }
bark_view() { view "$(broken_tree "$1")" "$tree_manifest" --stand 0.5 --pitch 0 --screenshot "$2"; [[ -e "$2" ]]; }

# L4d: slab_1 with its paint broken, seen as the gate takes a rock's shaded sides; the check reads
# what the viewer measured in its own picture.
shade_shot() { fixture "shade_$1.json" shade_view "$1"; }
shade_report() { # <python statements changing a passing report r> -> path of the report
  python -c "import json; r={'rays': 65536, 'asset_pixels': 15000, 'away': {'pixels': 3500, 'median': 0.075, 'tenth': 0.058}, 'toward': {'pixels': 1800, 'median': 0.26}}; $1; json.dump(r, open('$tmp/shade.json', 'w'))"
  echo "$tmp/shade.json"
}
shade_view() { view "$(broken_slab "$1")" "$slab_manifest" --back --close --screenshot "$2.png" --shade "$2"; [[ -e "$2" ]]; }
# L4e: tree_1 with its foliage broken, seen from under it as the gate takes that view. The check
# casts its rays at tree_1's own built mesh, so these mutations change colour and light, not shape.
under_shot() { fixture "under_$1.png" under_view "$1"; }
under_view() { view "$(broken_tree "$1")" "$tree_manifest" --stand 1 --pitch 78 --screenshot "$2"; [[ -e "$2" ]]; }

# L0: a copy of an asset's brief and spec under a name of its own, linted and removed.
lint_copy() { # <asset> <sed expression for the brief> <python statements for the spec s> -> lints the copy
  local name="zz_lint_${run_id}_${case_n}"
  rm -rf "source/$name"; mkdir "source/$name"
  sed "s/\`\\[\"$1\"\\]\`/\`[\"$name\"]\`/; $2" "source/$1/brief.md" > "source/$name/brief.md"
  python -c "import json; name='$name'; s=json.load(open('source/$1/spec.json')); s['asset']=name; s['objects']=[name]; p=s.get('painted_shading'); $3; json.dump(s, open('source/$name/spec.json','w'))"
  python tools/lint_spec.py "$name"; local code=$?
  rm -rf "source/$name"; return $code
}
lint_crate() { lint_copy crate "$1" 'pass'; }  # <sed expression applied to the copied brief>
lint_rock() { lint_copy rock '' "$1"; }        # <python statements changing spec s and its painted block p>
lint_tree() { lint_copy tree_1 '' "$1"; }      # <python statements changing spec s>
lint_season() { lint_copy tree_1_autumn '' "$1"; }  # <python statements changing spec s>
lint_blade() { lint_copy blade_plant_1 '' "$1"; } # <python statements changing spec s>
lint_grass() { lint_copy tall_grass_1 '' "$1"; } # <python statements changing spec s>
lint_reeds() { lint_copy reeds_1 '' "$1"; } # <python statements changing spec s>
lint_slab() { lint_copy slab_1 '' "$1"; }      # <python statements changing spec s>
lint_cover() { lint_copy crag_1_mossy '' "$1"; } # <python statements changing spec s and its painted block p>
lint_crag() { lint_copy crag_1 '' "$1"; }      # <python statements changing spec s>
lint_stack() { lint_copy stack_1 '' "$1"; }    # <python statements changing spec s>
lint_table() { lint_copy table_rock_1 '' "$1"; } # <python statements changing spec s>
lint_block() { lint_copy block_2 '' "$1"; }    # <python statements changing spec s>
lint_pebble() { lint_copy pebble_2 '' "$1"; }  # <python statements changing spec s>
lint_spire() { lint_copy spire_1 '' "$1"; }   # <python statements changing spec s>
lint_arch() { lint_copy arch_1 '' "$1"; }     # <python statements changing spec s>
lint_boulder() { lint_copy boulder_2 '' "$1"; } # <python statements changing spec s>

# L5b: a copy of the tracer's sheet as a review phase of its own.
baseline_check() { # <never_approved|approved|drawn_on>
  local phase="zz_base_${run_id}_${case_n}"; local dir="source/tracer/review/$phase"
  mkdir -p "$dir"; cp source/tracer/review/final/sheet.png "$dir/sheet.png"
  if [[ $1 != never_approved ]]; then python tools/baseline.py approve tracer "$phase" > /dev/null || return 3; fi
  if [[ $1 == drawn_on ]]; then magick "$dir/sheet.png" -fill red -draw 'rectangle 100,100 700,700' "$dir/sheet.png" || return 3; fi
  python tools/baseline.py check tracer "$phase"; local code=$?
  rm -rf "$dir"; return $code
}

# L5c: the rock's sheet saved another way, and the review aids made from it.
sheet_as() { magick source/rock/review/final/sheet.png "${@:2}" "$1:$tmp/sheet.png"; echo "$tmp/sheet.png"; }  # <PNG format> <magick options...>
review_aid() { # <views|blind>
  cp source/rock/review/final/sheet.png "$tmp/aid.png"
  if [[ $1 == views ]]; then python tools/review_aids.py views "$tmp/aid.png" > /dev/null; echo "$tmp/aid_aids.png"
  else python tools/review_aids.py blind "$tmp/aid.png" "$tmp/aid.png" "$tmp/blind.png" > /dev/null; echo "$tmp/blind.png"; fi
}

# ---- the run: up to $jobs cases at once, reported in file order as they finish

run_case() { # <case index>
  case_n=$1; tmp="$scratch/case_$1"; mkdir -p "$tmp"
  # Reports written by a tool under test go to the case, not over the asset's own from the gate.
  export KILN_REPORTS="$tmp/reports"
  local started=$EPOCHREALTIME
  eval "${lines[$1]}" > "$out/$1.log" 2>&1
  [[ -e "$out/$1.verdict" ]] || { echo "FAIL       ${names[$1]}: the case did not reach a verdict" >> "$out/$1.log"; echo FAIL > "$out/$1.verdict"; }
  awk -v a="$started" -v b="$EPOCHREALTIME" 'BEGIN { printf "%.1f\n", b - a }' > "$out/$1.seconds"
  [[ $keep -eq 1 ]] || rm -rf "$tmp"
  : > "$out/$1.done"
}

case "$order" in
  file) started_in=("${chosen[@]}") ;;
  reverse) started_in=(); for ((n = ran - 1; n >= 0; n--)); do started_in+=("${chosen[n]}"); done ;;
  random) mapfile -t started_in < <(printf '%s\n' "${chosen[@]}" | shuf) ;;
esac

failures=0; failed_names=(); mutations=0; next=0
report() { # print the cases that have finished, as far as file order allows
  while [[ $next -lt $ran && -e "$out/${chosen[next]}.done" ]]; do
    local i=${chosen[next]}
    cat "$out/$i.log"
    if [[ $(< "$out/$i.verdict") != ok ]]; then failures=$((failures + 1)); failed_names+=("${names[i]}"); fi
    [[ -e "$out/$i.mutations" ]] && mutations=$((mutations + $(wc -l < "$out/$i.mutations")))
    next=$((next + 1))
  done
}

began=$SECONDS; running=0
for i in "${started_in[@]}"; do
  while [[ $running -ge $jobs ]]; do wait -n; running=$((running - 1)); report; done
  run_case "$i" &
  running=$((running + 1))
done
while [[ $running -gt 0 ]]; do wait -n; running=$((running - 1)); report; done
report

if [[ -n $results_file ]]; then
  for i in "${chosen[@]}"; do
    printf '%s\t%s\n' "$(< "$out/$i.verdict")" "${names[i]}"
    [[ -e "$out/$i.mutations" ]] && awk '{ status = ($1 == "ok") ? "ok" : "FAIL"; sub(/^(ok|NOT CAUGHT) +/, ""); print status "\t  L1 " $1 " fails " $2 }' "$out/$i.mutations"
  done > "$results_file"
fi
if [[ $timings -eq 1 ]]; then
  echo; echo "seconds per case, slowest first (cases run $jobs at a time, so these add up to more than the run took):"
  for i in "${chosen[@]}"; do printf '%8s  %s\n' "$(< "$out/$i.seconds")" "${names[i]}"; done | sort -rn
fi

echo
[[ $mutations -gt 0 ]] && echo "$mutations L1 mutations were checked inside the L1 cases"
reused=$(find "$fx" -name '*.reused' | wc -l); built=$(find "$fx" -name '*.built' | wc -l)
[[ $((reused + built)) -gt 0 ]] && echo "$reused built assets were reused from $kept, $built were built (--fresh builds them all)"
if [[ $failures -eq 0 ]]; then
  [[ $skipped -eq 0 ]] && echo "all gate tests passed" || echo "the selected gate tests passed"
else
  echo "$failures gate tests failed:"; printf '  %s\n' "${failed_names[@]}"
fi
tally " in $((SECONDS - began)) s, $jobs at a time"
exit $((failures > 0))
