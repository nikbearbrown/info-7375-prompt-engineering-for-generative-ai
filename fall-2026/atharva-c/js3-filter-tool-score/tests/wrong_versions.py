"""Check that each FILTER.md wrong version (W1-W5) makes its test fail.

Patches agent/filter.py in memory with the wrong version, runs that version's
test class, and expects at least one failure. Run from js3-filter-tool-score/:

    python3 -m tests.wrong_versions
"""

from __future__ import annotations

import re
import unittest
from contextlib import contextmanager

from agent import filter as F
from tests import test_filter as T


@contextmanager
def patched(**attrs):
    old = {k: getattr(F, k) for k in attrs}
    for k, v in attrs.items():
        setattr(F, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(F, k, v)


_real_filter = F.filter_postings


def _dedupe_then_filter(postings, skills):
    seen, first = set(), []
    for p in postings:
        key = (p.get("board"), p.get("title"))
        if key not in seen:
            seen.add(key)
            first.append(p)
    return _real_filter(first, skills)


WRONG = {
    "W1 'Engineer' substring is a role match": (
        T.W1EngineerSubstring, dict(R1=re.compile(r"Engineer", re.I))),
    "W2 trust title level I/II, ignore body years": (
        T.W2TitleLevel, dict(R3_TITLE=re.compile(r"\bEngineer II?\b"), find_years=lambda text: [])),
    "W3 rank by number of skill hits": (
        T.W3RankByHits, dict(rank=lambda ds: sorted(ds, key=lambda d: -len(d["skills"])))),
    "W4 dedupe by title before filtering": (
        T.W4DedupeBeforeFilter, dict(filter_postings=_dedupe_then_filter)),
    "W5 reject if ANY location part is non-US": (
        T.W5AnyNonUsPart, dict(g3_rejects=lambda parts: any(k == "non-us" for _, k in parts))),
}


def main() -> int:
    bad = 0
    for name, (case, attrs) in WRONG.items():
        with patched(**attrs):
            r = unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(
                unittest.defaultTestLoader.loadTestsFromTestCase(case))
        failed = len(r.failures) + len(r.errors)
        caught = failed > 0
        bad += not caught
        print(f"{'caught ' if caught else 'MISSED '} {name}: {failed} of {r.testsRun} tests in {case.__name__} fail")
    real = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(
        unittest.defaultTestLoader.loadTestsFromModule(T))
    print(f"real filter: {real.testsRun} tests, {len(real.failures) + len(real.errors)} fail")
    return 1 if bad or not real.wasSuccessful() else 0


if __name__ == "__main__":
    raise SystemExit(main())
