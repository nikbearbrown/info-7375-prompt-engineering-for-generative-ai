#!/bin/bash
# Test evidence -> logs/. Run from the js3 folder:  bash tools/make_logs.sh
# logs/00 (tests before any code) is made once, by hand, and never overwritten here.
cd "$(dirname "$0")/.." && mkdir -p logs
{ echo "\$ shasum -a 256 -c tests.frozen.sha256   ($(date '+%Y-%m-%d %H:%M'))"; shasum -a 256 -c tests.frozen.sha256; } > logs/01_tests_unchanged_since_freeze.txt 2>&1
for w in wv1_substring wv2_wordcount; do
  { echo "\$ JS3_FILTER=wrong_versions.$w python3 -m unittest tests.test_filter   ($(date '+%Y-%m-%d %H:%M'))";
    JS3_FILTER=wrong_versions.$w python3 -m unittest tests.test_filter 2>&1 | grep -E '^(FAIL|ERROR):|^Ran|^FAILED|^OK'; } > logs/02_tests_vs_$w.txt 2>&1
done
{ echo "\$ python3 -m unittest discover -s tests -t . -v   ($(date '+%Y-%m-%d %H:%M'))"; python3 -m unittest discover -s tests -t . -v; } > logs/03_all_tests_real_code.txt 2>&1
for f in logs/0[123]*.txt; do echo "$f: $(tail -1 $f)"; done
