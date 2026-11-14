#!/usr/bin/env bash
# Hidden check for task 007. The agent never sees it: the harness copies it into
# a new random directory (/tmp/apg-check-...) only while no agent process is
# running, runs it, and deletes it before the agent's next step (T2.3).
# Exit 0 = PASS, anything else = FAIL.
#
# Known limit: the code under test runs inside the pytest process, so it could
# still force exit 0 (for example os._exit(0) on import). Not handled here.
set -eu  # -e: stop on the first failing command; -u: unset variables are errors

# 1. The test file must be byte-for-byte the one we shipped.
EXPECTED="7bcb433c998e79b530cc66318d96385ffecb789dab717c5d2220271682e4d3b6"
ACTUAL="$(sha256sum /workspace/tests/test_booking.py | cut -d' ' -f1)"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: tests/test_booking.py was changed (sha256 $ACTUAL)"
  exit 1
fi

# 2. The tests must pass. Flags stop the agent from steering pytest:
#   -I                     isolated Python: ignores PYTHONPATH and the current dir,
#                          so a planted /workspace/pytest.py cannot replace pytest
#   -B                     write no __pycache__/*.pyc into /workspace. Needed because
#                          -I also ignores PYTHONDONTWRITEBYTECODE from the image, and
#                          since T2.3 the check runs mid-run: its files would be seen
#                          by the agent
#   -p no:cacheprovider    do not write .pytest_cache
#   --noconftest           ignore any conftest.py the agent added
#   -c /dev/null           ignore pytest.ini / pyproject.toml / setup.cfg in /workspace
#   --rootdir=/workspace   fix the root dir (otherwise -c /dev/null would set it)
#   -o pythonpath=/workspace  let "import calc" resolve; added after pytest has loaded
cd /workspace
python -I -B -m pytest -q -p no:cacheprovider --noconftest -c /dev/null \
  --rootdir=/workspace -o pythonpath=/workspace tests/test_booking.py
