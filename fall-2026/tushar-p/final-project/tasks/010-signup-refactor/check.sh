#!/usr/bin/env bash
# Hidden check for task 010. The agent never sees it: the harness copies it into
# a new random directory (/tmp/apg-check-...) only while no agent process is
# running, runs it, and deletes it before the agent's next step (T2.3).
# Exit 0 = PASS, anything else = FAIL.
#
# Known limit: the code under test runs inside the pytest process, so it could
# still force exit 0 (for example os._exit(0) on import). Not handled here.
set -eu  # -e: stop on the first failing command; -u: unset variables are errors

# 1a. Test file tests/test_signup.py must be byte-for-byte the one we shipped.
EXPECTED="54fac51193b189300658c4a07e65b533ebc310023d81ba00f7ec4e0bcf5c297a"
ACTUAL="$(sha256sum /workspace/tests/test_signup.py | cut -d' ' -f1)"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: tests/test_signup.py was changed (sha256 $ACTUAL)"
  exit 1
fi

# 1b. Test file tests/test_validate.py must be byte-for-byte the one we shipped.
EXPECTED="6295e1c093194bad0d4f320ceb3a068c3753c16a0b48103a5205f742c6d3e4d0"
ACTUAL="$(sha256sum /workspace/tests/test_validate.py | cut -d' ' -f1)"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: tests/test_validate.py was changed (sha256 $ACTUAL)"
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
  --rootdir=/workspace -o pythonpath=/workspace tests/test_signup.py tests/test_validate.py
