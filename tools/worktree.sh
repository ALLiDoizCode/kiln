#!/usr/bin/env bash
# A working copy of this repo beside it, for work done in parallel: ../kiln-<name> on a new branch
# <name>, or on that branch if it exists. It is given links to the pinned tools, the benchmarks and
# the reference images, which git does not carry, and a copy of this checkout's target/ so that its
# first cargo build compiles only the crates of this repo and not Bevy. The copy shares disk blocks
# with the original where the filesystem can (btrfs), and is each checkout's own from then on: a
# target/ is never shared, or checkouts would run each other's binaries.
# Usage: tools/worktree.sh <name>            then, when its branch is merged: git worktree remove ../kiln-<name>
set -euo pipefail
cd "$(dirname "$0")/.."
name="$1"; copy="../kiln-$name"
if git show-ref --verify --quiet "refs/heads/$name"; then git worktree add -q "$copy" "$name"
else git worktree add -q "$copy" -b "$name"; fi
ln -s "$PWD/.tools" "$copy/.tools"
ln -s "$PWD/benchmarks" "$copy/benchmarks"
ln -s "$PWD/docs/style/refs" "$copy/docs/style/refs"
[[ -d target ]] && cp -a --reflink=auto target "$copy/target"
echo "$(cd "$copy" && pwd) on branch $name"
