#!/usr/bin/env python3
"""Plant each wrong version from GATE.md §7, run the tests that should catch it, and report.

A wrong version is "caught" when at least one of its named tests FAILS with it planted.
  python3 scripts/wrong_versions.py
"""
import importlib.util
import io
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE / "src"), str(HERE / "tests")]
from jsa import loop, policy  # noqa: E402

spec = importlib.util.spec_from_file_location("check", HERE / "checker/check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
import test_checker  # noqa: E402
test_checker.check = check

WRONG = {
    "W1 prefix trick": (policy, "_inside", lambda p, b: str(p).startswith(str(b)), ["test_policy.Paths.test_B9_prefix_trick_sibling"]),
    "W2 symlink escape": (policy, "_resolve", lambda r, t: Path(os.path.abspath(os.path.join(r, t))), ["test_policy.Paths.test_B8_symlink_escape_on_write"]),
    "W3 truthy approval": (policy, "_approval_ok", lambda a, r: bool(a), ["test_policy.Paths.test_B14_truthy_approval"]),
    "W4 empty board = fine": (check, "classify", lambda c, s, f, p, t: ("ok", "fine") if s == 200 else ("error-response", ""), ["test_checker.Classify.test_W4_empty_board_is_suspect"]),
    "W5 failure as zero": (loop, "classify_response", lambda ats, st, b: ("ok", []) if st != 200 else ("ok", loop.boards.parse(ats, b)), ["test_loop.Exits.test_W5_failure_is_error_not_zero"]),
    "W6 stopped = success": (loop, "final_status", lambda *a: "finished", ["test_loop.Exits.test_W6_budget_exhausted_is_not_finished"]),
    "W7 repeat counted as progress": (loop, "repeat_key", lambda ats, slug: f"{ats}/{slug}", ["test_loop.Repeat.test_W7_same_board_other_case_and_encoding_is_skipped"]),
    "W8 host check by substring": (policy, "_host_ok", lambda h: any(a in h for a in policy.ALLOWED_HOSTS), ["test_policy.Hosts.test_B2_allowed_host_as_substring"]),
    "W9 state wiped on failure": (loop, "merge_seen", lambda old, r: [] if r["result"] != "ok" else sorted(set(old or []) | set(r["ids"])), ["test_loop.State.test_W9_failed_board_keeps_its_seen_ids"]),
}


def run(names):
    suite = unittest.TestSuite()
    for n in names:
        mod, cls, meth = n.split(".")
        if not hasattr(getattr(__import__(mod), cls), meth):
            return None
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(n))
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return res.testsRun, len(res.failures) + len(res.errors)


def main():
    caught = 0
    print(f"{'wrong version':32} {'tests run':>9} {'failed':>6}  result")
    for name, (mod, attr, bad, tests) in WRONG.items():
        good = getattr(mod, attr)
        base = run(tests)
        setattr(mod, attr, bad)
        try:
            planted = run(tests)
        finally:
            setattr(mod, attr, good)
        if base is None or planted is None:
            print(f"{name:32} {'-':>9} {'-':>6}  NO TEST YET ({tests[0]} not written)")
            continue
        ok = base[1] == 0 and planted[1] > 0
        caught += ok
        status = "CAUGHT" if ok else ("REAL CODE ALREADY FAILS THIS TEST" if base[1] else "NOT CAUGHT")
        print(f"{name:32} {planted[0]:>9} {planted[1]:>6}  {status}")
    print(f"\n{caught}/{len(WRONG)} wrong versions caught")
    return 0 if caught == len(WRONG) else 1


if __name__ == "__main__":
    sys.exit(main())
