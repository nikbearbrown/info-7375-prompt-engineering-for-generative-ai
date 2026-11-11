"""Review-packet test, written BEFORE the patch (REVIEW-PACKET.md). GATE.md §4: a 200 with 0 postings counts as a valid
empty result only after the board's identity is confirmed. Written by Claude from GATE §4's wording; it must fail on
loop v0 (24d6e27) and pass after the patch."""
from __future__ import annotations

from harness import EMPTY_SR, SR, board, run, sr_body, temp_root


def test_review_empty_200_without_identity_is_not_success():
    """The Canvaa case: a structurally valid empty board nobody has ever seen non-empty must not be 'success, 0'."""
    with temp_root():
        s, _ = run([board("smartrecruiters", "Canvaa")], {SR.format("Canvaa", 0): [(200, EMPTY_SR)]})
    b = s["boards"][0]
    assert (b["status"], b["reason"], b["postings"]) == ("failed", "empty_unverified", None)
    assert s["exit"] == "incomplete"


def test_review_empty_200_after_a_nonempty_run_is_valid():
    """A board an earlier run saw with postings is a confirmed board, so a later empty 200 is a real empty result."""
    with temp_root():
        run([board("smartrecruiters", "Tiny")], {SR.format("Tiny", 0): [(200, sr_body([1]))]})
        s, _ = run([board("smartrecruiters", "Tiny")], {SR.format("Tiny", 0): [(200, EMPTY_SR)]})
    b = s["boards"][0]
    assert (b["status"], b["postings"]) == ("success", 0) and s["exit"] == "finished"
