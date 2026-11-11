#!/usr/bin/env bash
# Run BY MAYANK (not by Claude): the review-packet commands, output saved verbatim.
#   bash review/run-review-commands.sh
# Writes review/05-review-commands-run-by-mayank.txt
set -u
cd "$(dirname "$0")/.."
OUT=review/05-review-commands-run-by-mayank.txt
{
  echo "# Review commands run by Mayank Bhadrasen in his own terminal"
  echo "# date: $(date '+%Y-%m-%d %H:%M %Z')   commit: $(git rev-parse --short HEAD)   python: $(python3 -c 'import sys;print(sys.version.split()[0])')"
  run() { echo; echo "\$ $*"; bash -c "$*" 2>&1; echo "[exit $?]"; }
  run 'git show 6050272:./src/jsa/policy.py > /tmp/js2-policy-before.py && cp src/jsa/policy.py /tmp/js2-policy-after.py && cp /tmp/js2-policy-before.py src/jsa/policy.py && (cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write 2>&1 | tail -3); cp /tmp/js2-policy-after.py src/jsa/policy.py'
  run '(cd tests && python3 -m unittest test_policy.Paths.test_B8_symlink_escape_on_write test_policy.Paths.test_B8b_returned_path_is_the_resolved_one 2>&1 | tail -3)'
  run 'python3 -m unittest discover -s tests -p "test_*.py" 2>&1 | tail -3'
  run 'python3 scripts/wrong_versions.py'
  run 'python3 review/probe_still_missed.py'
  run 'git diff --stat 6050272 3ab4582 -- .'
} > "$OUT"
find . -name __pycache__ -prune -exec rm -rf {} +
echo "saved $OUT"; grep -E '^\$|\[exit|FAILED|OK$|caught|ALLOWED' "$OUT"
