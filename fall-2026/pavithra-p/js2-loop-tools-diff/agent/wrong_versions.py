"""The three plausible-but-wrong versions of the loop from GATE.md, as real code.

Each is the real loop with one hook changed. The watcher never uses them; tests/test_wrong_versions.py must catch all
three, and wrong version 3 is the finished-wrong-answer demonstration (FINISHED-WRONG.md).
"""
from .loop import Hooks


def _always_transient(outcome):
    return "ok" if outcome == 200 else "transient"


# 1. Treats every failure as temporary and keeps retrying, so a wrong board name is asked for again and again.
RETRIES_FOREVER = Hooks(classify=_always_transient, max_attempts=10)

# 2. Skips the budget and host checks, so it can go over the request budget or call a host off the allow-list.
NO_LIMITS = Hooks(check_budgets=False, check_hosts=False)

# 3. Counts a failed board as checked with 0 jobs, so the run ends `finished` and says "no new jobs".
FAILED_AS_EMPTY = Hooks(failed_as_empty=True)

VERSIONS = {1: RETRIES_FOREVER, 2: NO_LIMITS, 3: FAILED_AS_EMPTY}
