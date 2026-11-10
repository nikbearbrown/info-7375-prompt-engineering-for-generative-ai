#!/bin/sh
# Checks for Ashwin to run personally (script written by Claude Code, 2026-11-10).
# Works from any directory. Output is shown and saved to review-packet/checks-run-by-ashwin.txt;
# it refuses to overwrite an earlier saved run.
cd "$(dirname "$0")/.." || exit 1
OUT=review-packet/checks-run-by-ashwin.txt
[ -e "$OUT" ] && { echo "$OUT already exists; not overwriting it."; exit 1; }
{
  date -u
  echo "\$ whoami"; whoami
  echo "\$ pwd"; pwd
  echo "\$ git log --oneline -1"; git log --oneline -1
  echo "\$ python3 -m unittest tests.test_review_interrupt tests.test_gate_gaps -v"; python3 -m unittest tests.test_review_interrupt tests.test_gate_gaps -v; echo "exit $?"
  echo "\$ python3 -m unittest discover -s tests -t ."; python3 -m unittest discover -s tests -t .; echo "exit $?"
  echo "\$ /opt/homebrew/bin/python3.12 -m unittest discover -s tests -t ."; /opt/homebrew/bin/python3.12 -m unittest discover -s tests -t .; echo "exit $?"
  echo "\$ python3 review-packet/reproduce_interrupt.py"; python3 review-packet/reproduce_interrupt.py; echo "exit $?"
  echo "\$ python3 independent_check.py runs/2026-11-09T20-21-52Z-live"; python3 independent_check.py runs/2026-11-09T20-21-52Z-live; echo "exit $?"
} 2>&1 | tee "$OUT"
