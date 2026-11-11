#!/bin/bash
# Saves the test evidence as logs. Run from the js2 folder:  bash tools/make_logs.sh
# (logs/00 and logs/04 are the "before the code" logs; they are made once, by hand, and never overwritten here)
cd "$(dirname "$0")/.." && mkdir -p logs
{ echo "\$ shasum -a 256 -c (test files only)   ($(date '+%Y-%m-%d %H:%M'))"
  echo "# PREDICTIONS.md is left out on purpose: its authorship line was corrected after the freeze (see FRICTIONAL.md); its original hash stays in tests.frozen.sha256"
  grep ' tests/' tests.frozen.sha256 | shasum -a 256 -c
  [ -f tests.review-fixes.frozen.sha256 ] && shasum -a 256 -c tests.review-fixes.frozen.sha256; } > logs/01_tests_unchanged_since_freeze.txt 2>&1
for w in empty_as_zero retry_ignores_budget; do
  { echo "\$ WATCHER_LOOP=wrong_versions.$w python3 -m unittest tests.test_loop -v   ($(date '+%Y-%m-%d %H:%M'))";
    WATCHER_LOOP=wrong_versions.$w python3 -m unittest tests.test_loop -v; } > logs/02_tests_vs_wrong_$w.txt 2>&1
done
{ echo "\$ python3 -m unittest discover -s tests -t . -v   ($(date '+%Y-%m-%d %H:%M'))"; python3 -m unittest discover -s tests -t . -v; } > logs/03_all_tests_real_code.txt 2>&1
for f in logs/0[123]*.txt; do echo "$f: $(tail -1 $f)"; done
