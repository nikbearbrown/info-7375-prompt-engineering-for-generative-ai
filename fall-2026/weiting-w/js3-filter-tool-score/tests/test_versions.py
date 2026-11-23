"""The current versions, asserted in exactly one place.

Each amendment used to assert the version it produced, so every new amendment
broke the previous one's test and I rewrote a line in three files. That churn
is not evidence of anything -- it is a structure problem -- so the current
versions live here and the amendment tests assert only what their amendment
established and what later amendments did not change.

FILTER.md §7 is the history; this file is the present.
"""

from __future__ import annotations

from jobfilter import evidence, pipeline, score as scorer


def test_current_versions():
    assert pipeline.FILTER_VERSION == "F-v2"     # A1
    assert scorer.SCORER_VERSION == "S-v5"       # A2, A3, A4, A5
    assert evidence.EVIDENCE_VERSION == "E-v1a"  # A3


def test_the_current_buckets(decisions):
    s = pipeline.summary(decisions)
    assert s["counts"] == {
        "shortlisted": 4, "below_threshold": 20, "gated": 417, "cannot_score": 11,
    }
    assert s["scored"] == 24
    assert s["score_range"] == [-6, 8]
    assert sum(s["counts"].values()) == 452
