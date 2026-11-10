#!/usr/bin/env bash
# Finished-wrong-answer demo. SEEDED: no network. Run from the JS2 folder:
#   bash review/finished_wrong_demo.sh > logs/04-finished-wrong-demo.txt 2>&1
set -u
D=runs/finished-wrong-demo
J1RAW=../js1-contract-and-watch/evidence/raw/databricks-2026-10-30T204649Z.json.gz
EMPTY=$D/inputs/greenhouse-databricks-EMPTY-constructed.json
JS1ARGS=(--seeded --state "$D/js1/state.json" --raw-dir "$D/js1/raw" --report-dir "$D/js1/reports")
show() { echo "\$ $*"; "$@"; echo "# process exit code: $?"; }

echo "# Finished-wrong-answer demo. SEEDED (no network). Ran $(date -u +%Y-%m-%dT%H:%M:%SZ) at commit $(git log -1 --format=%h)"
echo; echo "## Step 1. JS1 watcher (agent/watch.py, unchanged from JS1). Baseline from a REAL response JS1 saved on 2026-10-30"
show python3 -B -m agent.watch --from-file "$J1RAW" "${JS1ARGS[@]}"
python3 -c "import time; time.sleep(1.2)"   # so run 2 gets a different timestamp
echo; echo "## Step 2. Same JS1 watcher, next run. The board answers 200 with 0 jobs (CONSTRUCTED input)"
show python3 -B -m agent.watch --from-file "$EMPTY" "${JS1ARGS[@]}"
R2=$(ls "$D"/js1/reports/*.json | tail -1); RAW2=$(ls "$D"/js1/raw/*.gz | tail -1)
echo; echo "## Step 3. Independent check (check.py imports nothing from agent/) on step 2's report"
show python3 -B check.py --js1 "$R2" --raw "$RAW2" --previous-count 903
echo; echo "## Step 4. JS2 loop on the SAME empty response"
show python3 -B -m agent.loop --boards "$D/boards.json" --fixtures "$D/fixtures.json" --seeded < /dev/null
R4=$(ls -d runs/*-seeded | tail -1)
echo; echo "## Step 5. Independent check on step 4's report"
show python3 -B check.py "$R4/report.json"
