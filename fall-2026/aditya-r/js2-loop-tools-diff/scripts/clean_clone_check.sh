#!/bin/sh
# Reproducibility check: extract this folder exactly as committed (default HEAD) into a temp dir,
# create a fresh venv, install requirements, and run every offline check. No network except pip;
# no model calls. Usage: sh scripts/clean_clone_check.sh [commit]
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
TOP="$(git -C "$HERE" rev-parse --show-toplevel)"
PREFIX="$(git -C "$HERE" rev-parse --show-prefix)"
REV="${1:-HEAD}"
TMP="$(mktemp -d)"
git -C "$TOP" archive "$REV:${PREFIX%/}" | tar -x -C "$TMP"
cd "$TMP"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python tests/mutation_check.py
.venv/bin/python tests/mutation_check_js2.py
.venv/bin/python scripts/check_run.py run out/runs/20261110T232115022Z_live
echo "clean extraction of $(git -C "$TOP" rev-parse --short "$REV"):${PREFIX%/}: all offline checks passed"
rm -rf "$TMP"
