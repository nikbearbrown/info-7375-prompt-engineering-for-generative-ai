#!/usr/bin/env bash
# Score one round of Claude-written checks against the five planted defect types.
#
#   ./score_round.sh 1        # scores claude-checks/round1_checks.py
#   ./score_round.sh 2        # scores claude-checks/round2_checks.py
#
# Writes results/<today>/claude-round<N>.txt / .json, plus a held-out score on a second planting (seed 99),
# and the hand-written baseline for comparison. Free and local; no API keys.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
N="${1:?usage: ./score_round.sh <round number>}"
OUT="$HERE/results/$(date +%Y-%m-%d)"; mkdir -p "$OUT"
PY=.venv/bin/python
[ -f data/planted/25/answer_key.json ] || $PY plant_five.py 25
[ -f data/planted/99/answer_key.json ] || $PY plant_five.py 99
CHK="claude-checks/round${N}_checks.py"
[ -f "$CHK" ] || { echo "missing $CHK (paste Claude's reply into it first)"; exit 1; }
echo "── hand-written baseline (one rule)"; $PY score_checks.py checks/fare_check.py hand-written-baseline "$OUT" 25
echo; echo "── Claude, round $N"; $PY score_checks.py "$CHK" "claude-round${N}" "$OUT" 25
echo; echo "── Claude, round $N, held-out planting (seed 99)"; $PY score_checks.py "$CHK" "claude-round${N}-heldout" "$OUT" 99
echo; echo "── which rules flag the clean copy (feedback for the next round)"; $PY explain_clean.py "$CHK" "claude-round${N}" "$OUT"
cp "$CHK" "$OUT/"
echo; echo "saved: ${OUT#$HERE/}/claude-round${N}*.txt"
