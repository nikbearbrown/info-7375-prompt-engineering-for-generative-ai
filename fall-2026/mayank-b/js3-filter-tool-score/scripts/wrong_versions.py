#!/usr/bin/env python3
"""Plant each wrong version from FILTER.md section 4, run the tests that should catch it, and report.

A wrong version is CAUGHT when its named tests pass on the real code and at least one FAILS with it planted.
  python3 scripts/wrong_versions.py
"""
import io
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(HERE / "src"), str(HERE / "tests")]
from jsa3 import filter as F, shortlist as S  # noqa: E402


def substring_find(text, form):  # WF1: "intern" in title
    t, f = (text or "").lower(), F.collapse(form).lower()
    return [m.start() for m in re.finditer(re.escape(f), t)]


WRONG = {
    "WF1 substring match": (F, "find_term", substring_find,
                            ["test_filter.TitleRules.test_WF1_exclude_is_whole_word", "test_filter.TitleRules.test_role_word_is_whole_word"]),
    "WF2 raw keyword count": (F, "score", lambda hits: sum(h["count"] for h in hits),
                              ["test_filter.TextRules.test_WF2_repeats_count_once"]),
    "WF3 relevance as entailment": (S, "prelabel", lambda c, p: "supported" if S.quote_found(c.get("quote", ""), p) else "insufficient",
                                    ["test_shortlist.Prelabel.test_WF3_never_supported_even_when_the_word_matches"]),
    "WF4 silent drop of no-text": (F, "no_text_verdict", lambda: "reject",
                                   ["test_filter.TextRules.test_WF4_no_text_is_cannot_tell_not_reject"]),
}


def run(names):
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in names)
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return res.testsRun, len(res.failures) + len(res.errors)


def main():
    caught = 0
    print(f"{'wrong version':30} {'tests run':>9} {'failed':>6}  result")
    for name, (mod, attr, bad, tests) in WRONG.items():
        good = getattr(mod, attr)
        base = run(tests)
        setattr(mod, attr, bad)
        try:
            planted = run(tests)
        finally:
            setattr(mod, attr, good)
        ok = base[1] == 0 and planted[1] > 0
        caught += ok
        print(f"{name:30} {planted[0]:>9} {planted[1]:>6}  {'CAUGHT' if ok else ('REAL CODE FAILS' if base[1] else 'NOT CAUGHT')}")
    print(f"\n{caught}/{len(WRONG)} wrong versions caught")
    return 0 if caught == len(WRONG) else 1


if __name__ == "__main__":
    sys.exit(main())
