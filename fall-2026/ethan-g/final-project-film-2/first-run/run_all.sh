#!/usr/bin/env bash
# DataSentry — the first piece, end to end. Free and local: no API keys, no accounts.
#
#   ./run_all.sh            # writes results/<today>/  (recorded output, logs, environment, hashes)
#
# 1. get_data.py        download NYC TLC yellow taxi Jan 2025 (public), make a clean 10,000-row sample
# 2. plant_defects.py   break a copy on purpose: 25 negative fares + 25 drop-offs before pick-up
# 3. run_first_piece.py one pandera check (fare_amount >= 0) on clean and broken; score vs the answer key
# 4. dbt                the same rule as a dbt test (dbt-duckdb)
# 5. gx_check.py        the same rule in Great Expectations (GX Core)
# 6. summarize.py       the three side by side + environment record
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
OUT="${OUT:-$HERE/results/$(date +%Y-%m-%d)}"
mkdir -p "$OUT"
LOG="$OUT/run.log"
: > "$LOG"

if [ ! -x .venv/bin/python ]; then
  echo "setting up a local Python environment (first run only)…"
  /opt/homebrew/bin/python3.11 -m venv .venv 2>/dev/null || python3 -m venv .venv
fi
.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt >> "$LOG" 2>&1
PY=.venv/bin/python

step(){ echo; echo "── $1"; echo "── $1" >> "$LOG"; }
step "1  data";            $PY get_data.py "$OUT"        2>>"$LOG" | tee -a "$LOG"
step "2  plant defects";   $PY plant_defects.py "$OUT"   2>>"$LOG" | tee -a "$LOG"
step "3  first piece (pandera)"; $PY run_first_piece.py "$OUT" 2>>"$LOG" | tee -a "$LOG"
step "4  dbt"
( cd dbt_compare && ../.venv/bin/dbt build --profiles-dir . --vars "{data_dir: '$HERE/data'}" --no-use-colors \
    > "$OUT/dbt.txt" 2>&1 ) || true      # dbt exits 1 when a test fails; that failure is the expected result
grep -E "PASS|FAIL|ERROR|Completed|Done\." "$OUT/dbt.txt" | tee -a "$LOG"
step "5  Great Expectations (GX Core)"; $PY gx_check.py "$OUT" 2>>"$LOG" | tee -a "$LOG"
step "6  side by side";    $PY summarize.py "$OUT"       2>>"$LOG" | tee -a "$LOG"
cp checks/fare_check.py "$OUT/fare_check.py"
echo
echo "saved: ${OUT#$HERE/}/  (first_piece.txt, dbt.txt, gx.txt, compare.txt, data.json, environment.json, run.log)"
