#!/usr/bin/env bash
# Builds target/release/fur_strands_scrgb: fur_strands on a Bevy 0.19.1 whose bevy_render has
# one change (bevy_render_scrgb.patch, beside this script), so that a window's surface can be
# opened in scRGB and an HDR screen gets an HDR signal. Run it with --display-hdr.
#
# Nothing of the probe or of kiln is changed: a copy of bevy_render from cargo's registry is
# patched in a scratch folder inside the target folder, and a copy of the probe's Cargo.toml
# there points at it with [patch.crates-io]. The probe's own Cargo.toml, Cargo.lock and the
# fur_strands binary stay as they are. It builds bevy_render and everything above it a second
# time: 94 seconds and 385 MB of target folder on the development machine.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
probe="$(dirname "$here")"
repo="$(cd "$probe/../../../.." && pwd)"
target="${CARGO_TARGET_DIR:-$repo/target}"
scratch="$target/fur_strands_scrgb_build"
source="$(ls -d "${CARGO_HOME:-$HOME/.cargo}"/registry/src/*/bevy_render-0.19.1 | head -1)"

rm -rf "$scratch"
mkdir -p "$scratch"
cp -r "$source" "$scratch/bevy_render"
patch -d "$scratch" -p1 < "$here/bevy_render_scrgb.patch"
cp "$probe/Cargo.lock" "$scratch/Cargo.lock"
sed -e "s#path = \"../../../../crates/asset_view\"#path = \"$repo/crates/asset_view\"#" \
    -e "s#^publish = false#publish = false\nautobins = false#" \
    "$probe/Cargo.toml" > "$scratch/Cargo.toml"
cat >> "$scratch/Cargo.toml" <<MANIFEST

[[bin]]
name = "fur_strands_scrgb"
path = "$probe/src/bin/fur_strands.rs"

[patch.crates-io]
bevy_render = { path = "bevy_render" }
MANIFEST

# The bodies are found from the probe's folder, not from the scratch one.
cd "$scratch"
FUR_STRANDS_PROBE_DIR="$probe" CARGO_TARGET_DIR="$target" cargo build --release --bin fur_strands_scrgb --features overlay,scrgb
echo "built $target/release/fur_strands_scrgb; run it from the repo root with --display-hdr"
