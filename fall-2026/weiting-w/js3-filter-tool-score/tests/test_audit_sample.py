"""The audit sample must still cover what FILTER.md §6 promised.

The form was generated under F-v2 / S-v2, and two amendments have moved the
buckets since. A sample that no longer covers the strata it was drawn for
would quietly stop satisfying the thing it was drawn for, and the labels would
be spent on the wrong postings -- which is only discoverable before somebody
spends twenty minutes labelling, not after.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from jobfilter import pipeline, score as scorer

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / "audit" / "audit-form.html"

pytestmark = pytest.mark.skipif(
    not FORM.exists(), reason="the audit form has not been generated"
)


def form_ids() -> set[str]:
    text = FORM.read_text(encoding="utf-8")
    data = json.loads(re.search(r"const DATA = (\[.*?\]);\n", text, re.S).group(1))
    return {row["id"] for row in data}


def test_the_form_holds_48_postings():
    assert len(form_ids()) == 48


def test_every_shortlisted_posting_is_in_the_sample(decisions):
    ids = form_ids()
    missing = [
        d.posting.identity for d in decisions
        if d.bucket == pipeline.SHORTLISTED and d.posting.identity not in ids
    ]
    assert missing == [], "the kept sample must cover everything kept"


def test_every_near_threshold_posting_is_in_the_sample(decisions):
    """FILTER.md §6: 'every posting within ±2 of the threshold', not a sample."""
    ids = form_ids()
    missing = [
        d.posting.identity for d in decisions
        if d.score is not None
        and abs(d.score.total - scorer.THRESHOLD) <= 2
        and d.posting.identity not in ids
    ]
    assert missing == []


def test_at_least_thirty_gated_postings_are_in_the_sample(decisions):
    ids = form_ids()
    n = sum(
        1 for d in decisions
        if d.bucket == pipeline.GATED and d.posting.identity in ids
    )
    assert n >= 30


def test_the_form_still_leaks_nothing(decisions):
    text = FORM.read_text(encoding="utf-8")
    for leak in ('"bucket"', "shortlisted", "below_threshold",
                 "gate_failed", "cannot_score", "_strata"):
        assert leak not in text, f"the form leaks {leak}"
