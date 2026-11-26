#!/bin/sh
# Build the Canvas ZIP from exactly one commit of this folder and compare its file list with the commit's tree.
#   sh scripts/package.sh <commit> <output.zip>
set -eu
COMMIT="$(git rev-parse "$1")"; OUT="$2"
SUB="$(git rev-parse --show-prefix)"; SUB="${SUB%/}"
REPO="$(git rev-parse --show-toplevel)"
git -C "$REPO" archive --format=zip -o "$OUT" "$COMMIT" "$SUB"
git -C "$REPO" ls-tree -r --name-only "$COMMIT" "$SUB" | sort > "$OUT.tree.txt"
unzip -Z1 "$OUT" | grep -v '/$' | sort > "$OUT.zip.txt"
if cmp -s "$OUT.tree.txt" "$OUT.zip.txt"; then echo "ZIP matches commit $COMMIT: $(wc -l < "$OUT.tree.txt" | tr -d ' ') files"; else diff "$OUT.tree.txt" "$OUT.zip.txt"; exit 1; fi
rm -f "$OUT.tree.txt" "$OUT.zip.txt"
