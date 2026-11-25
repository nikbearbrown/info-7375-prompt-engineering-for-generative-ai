"""Phase 6 experiment code on SEEDED data. Written by Claude Code (claude-opus-5-5), 2026-11-25.
No test reads labels/heldout.csv."""
import json

import js3kit  # noqa: F401
from filter_checks import line
from jobwatch import experiments


def picked():
    a = [("A", line(title="ML Engineer", location="Boston", body=("<p>We use PyTorch and Python and RAG.</p>",), key=f"g:s:{i}")) for i in range(3)]
    a.append(("A", line(title="ML Engineer", location="Boston", body=("<p>We use PyTorch.</p>",), key="g:s:9")))
    b = [("B", line(title="Software Engineer", location="Boston", body=("<p>Python.</p>",), key="g:s:20"))]
    return a + b


def test_e2_location_weight_zero_needs_three_topics():
    dec = experiments.filter_decisions(picked(), experiments.e2_arms())
    assert dec["v1 (location weight 2)"]["g:s:9"]["decision"] == "keep"
    assert dec["v1, location weight 0"]["g:s:9"]["decision"] == "reject"
    assert dec["v1, location weight 0"]["g:s:0"]["decision"] == "keep"


def test_report_counts_per_stratum_with_intervals_and_e3_movement():
    p = picked()
    rows = [{"posting_key": ln["key"], "label": lab, "override_reason": ""} for (_, ln), lab in
            zip(p, ["relevant", "relevant", "not_relevant", "relevant", "not_relevant"])]
    e1 = experiments.filter_decisions(p, [("v1", experiments.flt.V1)])
    e2 = experiments.filter_decisions(p, experiments.e2_arms())
    run = lambda labs: {ln["key"]: {"stratum": s, "label": lab, "error": None} for (s, ln), lab in zip(p, labs)}  # noqa: E731
    e3 = {"title_text-run1": run(["relevant", "relevant", "relevant", "relevant", "not_relevant"]),
          "title_text-run2": run(["relevant", "relevant", "not_relevant", "relevant", "not_relevant"]),
          "title_only-run1": run(["relevant", "not_relevant", "not_relevant", "not_relevant", "not_relevant"])}
    res = experiments.report(rows, p, e1, e2, e3)
    a = res["E1"]["v1"]["A"]
    assert (a["n"], a["kept"], a["rejected"]) == (4, 4, 0) and a["precision"]["k"] == 3 and a["precision"]["n"] == 4
    assert res["E1"]["v1"]["B"]["kept"] == 0 and res["E1"]["v1"]["B"]["precision"] is None
    mv = res["E3_movement"]["A"]
    assert mv["baseline_run1_vs_run2"] == {"moved": 1, "n": 4} and mv["baseline_run1_vs_title_only"] == {"moved": 3, "n": 4}
    assert "baseline run 1 vs run 2 (identical setup): 1/4" in experiments.render(res)


def test_report_refuses_a_sheet_whose_keys_differ_from_the_redraw():
    p = picked()
    rows = [{"posting_key": "other", "label": "relevant", "override_reason": ""}]
    try:
        experiments.report(rows, p, {}, {}, {})
    except ValueError as e:
        assert "differ from the held-out redraw" in str(e)
    else:
        raise AssertionError("no error")


def test_contexts_differ_only_by_the_text():
    ln = line(title="ML Engineer", body=("<p>Body.</p>",))
    assert experiments.context(ln, "title_only") == "Title: ML Engineer"
    assert experiments.context(ln, "title_text") == "Title: ML Engineer\nText:\nBody."
    assert experiments.parse_label(json.dumps({"label": "relevant"})) == "relevant" and experiments.parse_label("x") is None
