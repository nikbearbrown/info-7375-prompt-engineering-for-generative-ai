#!/bin/sh
# Fresh extraction of one commit of this folder -> new venv -> tests, mutants, replay, byte-for-byte compare.
#   sh scripts/clean_clone_check.sh [commit]      (default HEAD; run from this folder)
set -eu
REV="${1:-HEAD}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
SUB="$(git -C "$HERE" rev-parse --show-prefix)"
SUB="${SUB%/}"
COMMIT="$(git -C "$HERE" rev-parse "$REV")"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "== clean check of $SUB at $COMMIT ($(date -u +%FT%TZ))"
git -C "$REPO" archive "$COMMIT" "$SUB" | tar -x -C "$TMP"
cd "$TMP/$SUB"
python3 -m venv .venv >/dev/null && .venv/bin/pip install -q -r requirements.txt
echo "== tests";          .venv/bin/python -m pytest -q -p no:cacheprovider | tail -1
echo "== wrong versions"; .venv/bin/python tests/mutation_check.py | tail -1
echo "== replay"
.venv/bin/python -m js3.corpus >/dev/null
for v in v1.0 v1.1; do .venv/bin/python -m js3.run --filter "$v" >/dev/null; done
.venv/bin/python -m js3.boilerplate >/dev/null
.venv/bin/python -m js3.audit >/dev/null
.venv/bin/python -m js3.reader_labels >/dev/null && .venv/bin/python -m js3.shortlist --filter v1.1 >/dev/null
[ -f labels/heldout2_labels.csv ] && .venv/bin/python -m js3.experiment --labels labels/heldout2_labels.csv --out experiments/RESULTS_H2.json >/dev/null
echo "== regenerated outputs identical to the committed ones?"
CHANGED=0
for f in corpus/PROVENANCE.json runs/v1.0/scores.csv runs/v1.0/summary.json runs/v1.1/scores.csv runs/v1.1/summary.json \
         filters/boilerplate_segments.json audit/audit_results.json shortlist/claims.json shortlist/SHORTLIST.md \
         shortlist/reader_labels.json experiments/RESULTS_H2.json; do
  [ -f "$f" ] || continue
  if git -C "$REPO" show "$COMMIT:$SUB/$f" | cmp -s - "$f"; then echo "  same  $f"; else echo "  DIFF  $f"; CHANGED=1; fi
done
[ "$CHANGED" = 0 ] && echo "== all replayed outputs identical" || { echo "== some outputs differ"; exit 1; }
