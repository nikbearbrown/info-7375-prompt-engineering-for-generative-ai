#!/bin/sh
# The review-packet checks (written by Claude Code, 2026-11-10). Run by Claude Code at Ashwin's request.
# Works from any directory: it moves to the js2-loop-tools-diff folder first.
# Output is shown and saved to review-packet/checks-run-by-claude-code.txt.
cd "$(dirname "$0")/.." || exit 1
{
  date -u
  echo "\$ pwd"; pwd
  echo "\$ git --no-pager diff --stat -- jobloop/loop.py"; git --no-pager diff --stat -- jobloop/loop.py
  echo "\$ python3 -m unittest tests.test_review_interrupt -v"; python3 -m unittest tests.test_review_interrupt -v; echo "exit $?"
  echo "\$ /opt/homebrew/bin/python3.12 -m unittest discover -s tests -t ."; /opt/homebrew/bin/python3.12 -m unittest discover -s tests -t .; echo "exit $?"
  echo "\$ python3 -m unittest discover -s tests -t ."; python3 -m unittest discover -s tests -t .; echo "exit $?"
  echo "\$ python3 review-packet/reproduce_interrupt.py"; python3 review-packet/reproduce_interrupt.py; echo "exit $?"
} 2>&1 | tee review-packet/checks-run-by-claude-code.txt
