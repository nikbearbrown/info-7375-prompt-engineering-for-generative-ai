#!/usr/bin/env bash
# Recompute Run 1 -> Run 2 offline from the committed raw run folders, into a temp dir.
# Does not touch state/ or evidence/. No network, no Claude. Expect: baseline 0 new, then the same new postings
# and the same rule verdicts as the Run 2 report in evidence/runs/.
# Which run folder each run used is read from state/seen_ids.json (not guessed from file order).
set -euo pipefail
cd "$(dirname "$0")/.."
TMP="$(mktemp -d)"
RUN1_DIR="$(python3 -c "import json; print(json.load(open('state/seen_ids.json'))['runs'][0]['raw_dir'])")"
RUN2_DIR="$(python3 -c "import json; print(json.load(open('state/seen_ids.json'))['runs'][1]['raw_dir'])")"
COMMON=(--resume persona/evan-gordon.resume.json --state "$TMP/state.json" --runs-dir "$TMP/runs" --no-claude)
python3 -m jsagent.watch "${COMMON[@]}" --from-dir "$RUN1_DIR" --seeded "replay of Run 1 ($RUN1_DIR)"
echo
python3 -m jsagent.watch "${COMMON[@]}" --from-dir "$RUN2_DIR" --seeded "replay of Run 2's saved live run ($RUN2_DIR)"
echo; echo "temp output in $TMP"
