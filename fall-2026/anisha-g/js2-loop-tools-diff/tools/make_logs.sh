#!/bin/bash
# Saves the test evidence as logs. Run from the js2 folder:  bash tools/make_logs.sh
cd "$(dirname "$0")/.." && mkdir -p logs
{ echo "\$ shasum -a 256 -c tests.frozen.sha256   ($(date '+%Y-%m-%d %H:%M'))"; shasum -a 256 -c tests.frozen.sha256; } > logs/01_tests_unchanged_since_freeze.txt 2>&1
for w in empty_as_zero retry_ignores_budget; do
  { echo "\$ WATCHER_LOOP=wrong_versions.$w python3 -m unittest tests.test_loop -v   ($(date '+%Y-%m-%d %H:%M'))";
    WATCHER_LOOP=wrong_versions.$w python3 -m unittest tests.test_loop -v; } > logs/02_tests_vs_wrong_$w.txt 2>&1
done
{ echo "\$ python3 -m unittest discover -s tests -t . -v   ($(date '+%Y-%m-%d %H:%M'))"; python3 -m unittest discover -s tests -t . -v; } > logs/03_all_tests_real_code.txt 2>&1
for f in logs/0[123]*.txt; do echo "$f: $(tail -1 $f)"; done
