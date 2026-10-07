#!/usr/bin/env bash
# Installs the pinned external tools into .tools/ (no root needed).
# Versions here are the pins.
set -euo pipefail

BLENDER_VERSION=5.2.2
BLENDER_SHA256=84098912789dc450e95697c4184fb8a90acbe5111c2ba4aede3fecb57806a168
VALIDATOR_VERSION=2.0.0-dev.3.10
VALIDATOR_SHA256=168eba887964125abe17ae97899b38d0b3cfd73c266c78424c194929ddcbc522

root="$(cd "$(dirname "$0")/.." && pwd)"
dest="$root/.tools"
mkdir -p "$dest"

fetch() { # url sha256 file
  curl -fL --retry 3 -C - -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}

name="blender-${BLENDER_VERSION}-linux-x64"
if [[ ! -x "$dest/$name/blender" ]]; then
  fetch "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/${name}.tar.xz" \
    "$BLENDER_SHA256" "$dest/$name.tar.xz"
  tar -xJf "$dest/$name.tar.xz" -C "$dest"
  rm "$dest/$name.tar.xz"
fi
ln -sfn "$name" "$dest/blender"

name="gltf_validator-${VALIDATOR_VERSION}"
if [[ ! -x "$dest/$name/gltf_validator" ]]; then
  fetch "https://github.com/KhronosGroup/glTF-Validator/releases/download/${VALIDATOR_VERSION}/${name}-linux64.tar.xz" \
    "$VALIDATOR_SHA256" "$dest/$name.tar.xz"
  mkdir -p "$dest/$name"
  tar -xJf "$dest/$name.tar.xz" -C "$dest/$name"
  rm "$dest/$name.tar.xz"
fi
ln -sfn "$name/gltf_validator" "$dest/gltf_validator"

"$dest/blender/blender" --version | head -1
"$dest/gltf_validator" --version 2>&1 | head -1 || true
