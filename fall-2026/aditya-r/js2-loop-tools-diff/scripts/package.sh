#!/bin/sh
# Build the Canvas ZIP from the committed folder only (no untracked files, venv, caches, or local/).
# Refuses to run with uncommitted changes in this folder. Usage: sh scripts/package.sh [commit] [out.zip]
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
TOP="$(git -C "$HERE" rev-parse --show-toplevel)"
PREFIX="$(git -C "$HERE" rev-parse --show-prefix)"
REV="${1:-HEAD}"
OUT="${2:-$TOP/../Raj_Aditya_INFO7375_JS2.zip}"
if [ -n "$(git -C "$HERE" status --porcelain -- .)" ]; then echo "Uncommitted changes in $PREFIX; commit first." >&2; exit 1; fi
git -C "$TOP" archive --format=zip --prefix=js2-loop-tools-diff/ -o "$OUT" "$REV:${PREFIX%/}"
echo "Built $(basename "$OUT") from commit $(git -C "$TOP" rev-parse "$REV") (folder $PREFIX)"
