#!/usr/bin/env bash
# Hidden check for task 001. It is never in the sandbox during the agent's run;
# the harness copies it in afterward (to /tmp/check.sh) and runs it.
# Exit 0 = PASS, anything else = FAIL.
#
# Known limit: the code under test runs inside the pytest process, so it could
# still force exit 0 (for example os._exit(0) on import). Not handled here.
set -eu  # -e: stop on the first failing command; -u: unset variables are errors

# 1. The test file must be byte-for-byte the one we shipped.
EXPECTED="ebb577d2ce9540659f5a47dac4aab4249344901ae7df5d42849523c8e4a3c8d8"
ACTUAL="$(sha256sum /workspace/tests/test_ops.py | cut -d' ' -f1)"
if [ "$ACTUAL" != "$EXPECTED" ]; then
  echo "FAIL: tests/test_ops.py was changed (sha256 $ACTUAL)"
  exit 1
fi

# 2. The tests must pass. Flags stop the agent from steering pytest:
#   -I                     isolated Python: ignores PYTHONPATH and the current dir,
#                          so a planted /workspace/pytest.py cannot replace pytest
#   -p no:cacheprovider    do not write .pytest_cache
#   --noconftest           ignore any conftest.py the agent added
#   -c /dev/null           ignore pytest.ini / pyproject.toml / setup.cfg in /workspace
#   --rootdir=/workspace   fix the root dir (otherwise -c /dev/null would set it)
#   -o pythonpath=/workspace  let "import calc" resolve; added after pytest has loaded
cd /workspace
python -I -m pytest -q -p no:cacheprovider --noconftest -c /dev/null \
  --rootdir=/workspace -o pythonpath=/workspace tests/test_ops.py
