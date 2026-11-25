#!/usr/bin/env bash
# The loop, end to end: Claude writes checks, the scorer grades them, the clean-copy results go back, up to 3 rounds.
#
#   ./run_loop.sh                          # live: Claude Code headless, on your logged-in Claude subscription (no API key)
#   ./run_loop.sh --fixture claude-checks  # replay the two saved replies instead of calling Claude (no login needed)
#
# First run only: sets up .venv and data/ (downloads NYC TLC Jan 2025) and plants seeds 25 and 99.
# Every run: the loop's tests first; the loop does not start if they fail. Writes loop-runs/<timestamp>/.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
if [ ! -x .venv/bin/python ] || [ ! -f data/clean.parquet ]; then
  echo "first run: setting up .venv and data/ (run_all.sh; its output goes to loop-runs/setup/)"
  OUT="$HERE/loop-runs/setup" ./run_all.sh > /dev/null
fi
PY=.venv/bin/python
for s in 25 99; do [ -f "data/planted/$s/answer_key.json" ] || $PY plant_five.py "$s"; done
$PY -m unittest discover -s tests > loop-runs/last-tests.txt 2>&1 || { cat loop-runs/last-tests.txt; echo "tests failed: loop not started"; exit 1; }
echo "tests: $(tail -1 loop-runs/last-tests.txt)"
$PY loop.py "$@"
