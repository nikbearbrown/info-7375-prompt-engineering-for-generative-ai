"""The exact interval (jobwatch/stats.py) against closed forms and against the independent
recomputation (scripts/clopper_pearson_check.py), and audit-stats on a SEEDED sheet.
Written by Claude Code (claude-opus-5-5), 2026-11-25."""
import importlib.util

import pytest

import js3kit
from jobwatch import auditstats
from jobwatch.stats import clopper_pearson

spec = importlib.util.spec_from_file_location("cpcheck", js3kit.ROOT / "scripts" / "clopper_pearson_check.py")
cpcheck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpcheck)


def test_zero_and_all_successes_have_closed_forms():
    lo, hi = clopper_pearson(0, 30)
    assert lo == 0.0 and hi == pytest.approx(1 - 0.025 ** (1 / 30), abs=1e-9)
    lo, hi = clopper_pearson(30, 30)
    assert hi == 1.0 and lo == pytest.approx(0.025 ** (1 / 30), abs=1e-9)


@pytest.mark.parametrize("k,n", [(0, 30), (1, 30), (2, 30), (5, 30), (15, 30), (29, 30), (3, 12), (1, 3)])
def test_two_independent_methods_agree(k, n):
    a, b = clopper_pearson(k, n), cpcheck.interval(k, n)
    assert a[0] == pytest.approx(b[0], abs=1e-7) and a[1] == pytest.approx(b[1], abs=1e-7)


def test_known_value_1_of_30():
    # Published value for k=1, n=30: [0.000844, 0.172169] (exact binomial).
    lo, hi = clopper_pearson(1, 30)
    assert round(lo, 6) == 0.000844 and round(hi, 6) == 0.172169


def test_audit_stats_errors_overrides_and_candidates_on_a_seeded_sheet():
    rows = [{"posting_key": "s:b:1", "group": "random_reject", "title": "SEEDED", "location": "", "verdict": "relevant", "override_reason": ""},
            {"posting_key": "s:b:2", "group": "random_reject", "title": "SEEDED", "location": "", "verdict": "not_relevant", "override_reason": "odd"},
            {"posting_key": "s:b:3", "group": "close_call_keep", "title": "SEEDED", "location": "", "verdict": "not_relevant", "override_reason": ""}]
    outs = [{"key": "s:b:1", "decision": "reject", "reasons": ["no role word R01-R10 in the title"], "matched": []},
            {"key": "s:b:2", "decision": "reject", "reasons": ["x"], "matched": []},
            {"key": "s:b:3", "decision": "keep", "reasons": ["score 8 >= T=8"],
             "matched": [{"rule": "T12", "field": "text", "start": 4, "end": 13, "quote": "inference"},
                         {"rule": "X05", "field": "title", "start": 0, "end": 1, "quote": "I"}]}]
    lines = [{"key": "s:b:3", "text": "Run inference fast.", "title": "SEEDED", "location": "",
              "sentences": [{"start": 0, "end": 19, "boilerplate": False}]}]
    st = auditstats.compute(rows, outs, lines, ["random_reject: 2 drawn of 30 asked; pool 100"])
    assert len(st["groups"]["random_reject"]["errors"]) == 1 and len(st["groups"]["close_call_keep"]["errors"]) == 1
    assert st["random_reject_miss"]["k"] == 1 and st["random_reject_miss"]["n"] == 2 and st["random_reject_miss"]["frame"] == 100
    assert [o["posting_key"] for o in st["overrides"]] == ["s:b:2"]
    (c,) = st["false_friend_candidates"]
    assert (c["rule"], c["quote"], c["sentence"]) == ("T12", "inference", "Run inference fast.")


def test_section0_consistency_lists_relevant_verdicts_with_rule_words_or_other_locations():
    rows = [{"posting_key": "s:b:1", "group": "random_reject", "title": "SEEDED Intern", "location": "Boston", "verdict": "relevant", "override_reason": ""},
            {"posting_key": "s:b:2", "group": "random_reject", "title": "SEEDED Analyst", "location": "Sydney", "verdict": "relevant", "override_reason": ""},
            {"posting_key": "s:b:3", "group": "random_reject", "title": "SEEDED Analyst", "location": "Seattle", "verdict": "relevant", "override_reason": ""},
            {"posting_key": "s:b:4", "group": "random_reject", "title": "SEEDED Intern", "location": "Sydney", "verdict": "relevant", "override_reason": "why"}]
    outs = [{"key": r["posting_key"], "decision": "reject", "reasons": ["x"], "matched": []} for r in rows]
    st = auditstats.compute(rows, outs, [], [])
    got = {(c["posting_key"], tuple(c["section0_title_words"]), c["location_state"]) for c in st["section0_consistency"]}
    assert got == {("s:b:1", ("intern",), "match"), ("s:b:2", (), "nonmatch")}


def test_audit_stats_counts_checklist_failures_and_skips_the_mechanical_check_for_checklist_rows():
    rows = [{"posting_key": "s:b:1", "group": "random_reject", "title": "SEEDED Manager", "location": "Sydney", "verdict": "relevant",
             "override_reason": "", "check_family": "y", "check_seniority": "y", "check_location": "y"},
            {"posting_key": "s:b:2", "group": "random_reject", "title": "SEEDED", "location": "", "verdict": "not_relevant",
             "override_reason": "", "check_family": "y", "check_seniority": "n", "check_location": ""},
            {"posting_key": "s:b:3", "group": "random_reject", "title": "SEEDED", "location": "", "verdict": "not_relevant",
             "override_reason": "", "check_family": "n", "check_seniority": "", "check_location": ""}]
    outs = [{"key": r["posting_key"], "decision": "reject", "reasons": ["x"], "matched": []} for r in rows]
    st = auditstats.compute(rows, outs, [], [])
    assert st["groups"]["random_reject"]["checklist"] == {"answered": 3, "failed_family": 1, "failed_seniority": 1,
                                                          "failed_location": 0, "failed_experience": 0, "all_yes": 1}
    assert st["section0_consistency"] == []
    assert "| random_reject | 3/3 | 1/3 | 1/3 | 0/3 | 0/3 | 1/3 |" in auditstats.render(st, "x.csv", "v1")
