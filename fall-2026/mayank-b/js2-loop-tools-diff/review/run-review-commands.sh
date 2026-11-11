#!/usr/bin/env bash
# Run BY MAYANK (not by Claude): the review-packet commands, output saved verbatim.
# Works from any folder:
#   bash ~/Desktop/AgenticAI/Week_1/info-7375-repo/fall-2026/mayank-b/js2-loop-tools-diff/review/run-review-commands.sh
# Writes review/05-review-commands-run-by-mayank.txt
set -u
cd "$(cd "$(dirname "$0")" && pwd)/.." || exit 1
OUT="${OUT:-review/05-review-commands-run-by-mayank.txt}"
{
  echo "# Review commands run by Mayank Bhadrasen in his own terminal"
  echo "# date: $(date '+%Y-%m-%d %H:%M %Z')   commit: $(git rev-parse --short HEAD)   python: $(python3 -c 'import sys;print(sys.version.split()[0])')"
  run() { echo; echo "# expect: $1"; shift; echo "\$ $*"; bash -o pipefail -c "$*" 2>&1; echo "[exit $?]"; }
  run "FAIL: before the patch (policy.py as in CP5 6050272), B8 is not refused" \
      'git show 6050272:./src/jsa/policy.py > /tmp/js2-policy-before.py && cp src/jsa/policy.py /tmp/js2-policy-after.py && cp /tmp/js2-policy-before.py src/jsa/policy.py; (cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write 2>&1 | grep -E "^(Ran|OK|FAILED|AssertionError)"); status=$?; cp /tmp/js2-policy-after.py src/jsa/policy.py; exit $status'
  run "OK: after the patch (current code), B8 and B8b pass" \
      '(cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write test_policy.Paths.test_B8b_returned_path_is_the_resolved_one 2>&1 | grep -E "^(Ran|OK|FAILED)")'
  run "Ran 50 tests ... OK" \
      'python3 -m unittest discover -s tests -p "test_*.py" 2>&1 | grep -E "^(Ran|OK|FAILED)"'
  run "9/9 wrong versions caught" 'python3 scripts/wrong_versions.py'
  run "ALLOWED ... outside the project? True (the case the test still misses)" 'python3 review/probe_still_missed.py'
  run "the patch changed one source file: src/jsa/policy.py | 5 +++--" 'git diff --stat 6050272 3ab4582 -- src/jsa'
  run "nothing modified by these commands (policy.py restored)" 'git status --short -- src/'
} > "$OUT"
find . -name __pycache__ -prune -exec rm -rf {} +
echo "saved $OUT"; cat "$OUT"
