#!/bin/sh
# Reproducibility check: clone the committed state into a temp dir, install, and run every offline check.
set -e
SRC="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
git clone -q "$SRC" "$TMP/js1"
cd "$TMP/js1"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python tests/mutation_check.py
.venv/bin/python scripts/verify_evidence.py
echo "clean clone at $(git rev-parse HEAD): all offline checks passed ($TMP/js1)"
