#!/bin/sh
# Build the Canvas ZIP from the committed HEAD only (untracked files, .venv, caches and the
# assignment PDF are excluded by construction). Refuses to run with uncommitted tracked changes.
set -e
cd "$(dirname "$0")/.."
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then echo "Uncommitted changes; commit first." >&2; exit 1; fi
git archive --format=zip --prefix=js1-contract-and-watch/ -o Raj_Aditya_INFO7375_JS1.zip HEAD
echo "Built Raj_Aditya_INFO7375_JS1.zip from commit $(git rev-parse HEAD)"
