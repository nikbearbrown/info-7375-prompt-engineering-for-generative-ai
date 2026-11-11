#!/bin/sh
# SEEDED two-run demo: run 1 = constructed earlier snapshot (baseline), run 2 = the real saved response.
# Usage: sh scripts/run_seeded.sh [--claude]
set -e
RAW=evidence/raw/anthropic-20261101T185817Z.json
SEED=evidence/seeded/anthropic-SEEDED-before-2026-10-29.json
python3 scripts/make_seeded_snapshot.py "$RAW" 2026-10-29 "$SEED"
rm -f state/seeded_seen_ids.json
python3 -m agent.watch --resume personas/priya-nair.resume.json --state state/seeded_seen_ids.json \
  --from-file "$SEED" --label seeded-run1-baseline | tee results/seeded-run1-baseline.txt
python3 -m agent.watch --resume personas/priya-nair.resume.json --state state/seeded_seen_ids.json \
  --from-file "$RAW" --label seeded-run2-real-response "$@" | tee results/seeded-run2.txt
