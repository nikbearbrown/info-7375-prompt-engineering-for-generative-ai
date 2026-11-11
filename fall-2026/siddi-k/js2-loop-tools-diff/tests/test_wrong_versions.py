"""One test per GATE.md §6 wrong version (numbered in GATE order), plus the loop's other exits. Run: python tests/run_tests.py"""
from __future__ import annotations

from harness import BUDGETS, EMPTY_SR, GH, SR, FakeClock, board, gh_body, run, sr_body, temp_root


def test_wv_1_failures_never_become_zero():
    """GATE wv1: a non-success response, a timeout or a malformed body is never reported as zero postings."""
    with temp_root():
        s, _ = run([board("greenhouse", "stripee"), board("greenhouse", "slow"), board("greenhouse", "broken")],
                   {GH.format("stripee"): [(404, b'{"status":404}')], GH.format("slow"): ["timeout"],
                    GH.format("broken"): [(200, b"<html>not json</html>")]})
    by = {b["slug"]: b for b in s["boards"]}
    assert [by[x]["reason"] for x in ("stripee", "slow", "broken")] == ["not_found", "timeout", "malformed"]
    assert all(by[x]["status"] == "failed" and by[x]["postings"] is None for x in by)
    assert s["total_postings_successful_boards"] == 0 and s["exit"] == "incomplete"


def test_wv_2_retries_bounded():
    """GATE wv2: no retry on 404; at most two retries on timeout; request and time budgets respected."""
    with temp_root():
        s404, f404 = run([board("greenhouse", "stripee")], {GH.format("stripee"): [(404, b"{}")]})
        sto, fto = run([board("greenhouse", "slow")], {GH.format("slow"): ["timeout"]})
        sreq, freq = run([board("greenhouse", "slow")], {GH.format("slow"): ["timeout"]},
                         budgets={**BUDGETS, "requests": 2})
        clock = FakeClock(step=50.0)
        stime, ftime = run([board("greenhouse", "slow")], {GH.format("slow"): ["timeout"]}, clock=clock)
    assert len(f404.calls) == 1 and s404["boards"][0]["reason"] == "not_found"
    assert len(fto.calls) == 3 and sto["boards"][0]["reason"] == "timeout"
    assert len(freq.calls) == 2 and sreq["exit"] == "budget-exhausted" and sreq["budget_reached"] == "requests"
    assert stime["exit"] == "budget-exhausted" and stime["budget_reached"] == "seconds" and len(ftime.calls) < 3


def test_wv_3_repeat_is_not_new_work():
    """GATE wv3: the same action twice is skipped and recorded, never requested again or counted as success."""
    with temp_root():
        s, f = run([board("greenhouse", "stripe"), board("greenhouse", "stripe", "Stripe again")],
                   {GH.format("stripe"): [(200, gh_body(3))]})
    assert len(f.calls) == 1
    assert s["boards"][1]["status"] == "failed" and s["boards"][1]["reason"] == "repeat_guard"
    assert s["exit"] == "incomplete"


def test_wv_4_a_200_is_not_automatically_a_valid_board():
    """GATE wv4 (structure part): a 200 whose body lacks the board structure is malformed, not an empty board."""
    with temp_root():
        s, _ = run([board("greenhouse", "a"), board("smartrecruiters", "b")],
                   {GH.format("a"): [(200, b"{}")], SR.format("b", 0): [(200, b'{"content": []}')]})
    assert [(x["status"], x["reason"], x["postings"]) for x in s["boards"]] == [("failed", "malformed", None)] * 2


def test_wv_5_finished_only_when_everything_succeeded():
    """GATE wv5: never 'finished' with a failed board or after a budget stopped the run."""
    with temp_root():
        mixed, _ = run([board("greenhouse", "stripe"), board("greenhouse", "stripee")],
                       {GH.format("stripe"): [(200, gh_body(2))], GH.format("stripee"): [(404, b"{}")]})
        capped, _ = run([board("greenhouse", f"b{i}") for i in range(5)],
                        {GH.format(f"b{i}"): [(200, gh_body(1))] for i in range(5)})
        clean, _ = run([board("greenhouse", "stripe"), board("smartrecruiters", "Canva")],
                       {GH.format("stripe"): [(200, gh_body(2))], SR.format("Canva", 0): [(200, sr_body([1, 2]))]})
    assert mixed["exit"] == "incomplete"
    assert capped["exit"] == "budget-exhausted" and capped["budget_reached"] == "boards" and capped["remaining"] == ["b4"]
    assert clean["exit"] == "finished"


def test_pagination_and_error_exit():
    """SmartRecruiters pages by offset until totalFound; an invalid configuration ends with exit 'error'."""
    with temp_root():
        paged, f = run([board("smartrecruiters", "Big")],
                       {SR.format("Big", 0): [(200, sr_body(range(100), total=150))],
                        SR.format("Big", 100): [(200, sr_body(range(100, 150), total=150))]})
        bad, _ = run([{"provider": "greenhouse", "slug": "x"}], {}, budgets={"boards": 1})
    assert paged["boards"][0]["postings"] == 150 and len(f.calls) == 2 and paged["exit"] == "finished"
    assert bad["exit"] == "error" and bad["error"]
