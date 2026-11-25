"""Phase 3d: candidate rule changes and the measurement criterion. Written by Claude Code
(claude-opus-5-5), 2026-11-25. All postings SEEDED."""
import js3kit  # noqa: F401
from filter_checks import line
from jobwatch import filter as flt
from jobwatch import measure

PY = ("<p>We use Python.</p>",)


def test_each_candidate_changes_only_its_one_rule():
    assert flt.evaluate(line(title="Forward Deployed AI Engineer", body=PY), flt.CANDIDATES["C1"][1])["decision"] == "reject"
    assert flt.evaluate(line(title="Software Engineer, Machine Learning", body=PY), flt.CANDIDATES["C2"][1])["decision"] == "keep"
    assert flt.evaluate(line(title="Software Engineer, Machine Learning", body=PY), flt.V1)["decision"] == "reject"
    o = flt.evaluate(line(body=("<p>Statistical inference daily.</p>",)), flt.CANDIDATES["C3"][1])
    assert o["topics"] == 0 and flt.evaluate(line(body=("<p>Model inference at scale.</p>",)), flt.CANDIDATES["C3"][1])["topics"] == 1
    assert flt.evaluate(line(location="N/A", body=PY), flt.CANDIDATES["C4"][1])["decision"] == "abstain"
    assert flt.evaluate(line(location="N/A", body=PY), flt.V1)["decision"] == "reject"
    assert flt.evaluate(line(title="ML Engineer Internship", body=PY), flt.CANDIDATES["C5"][1])["decision"] == "reject"
    assert flt.evaluate(line(title="ML Engineer Internship", body=PY), flt.V1)["decision"] == "keep"


def rows_and_lines(specs):
    rows, lines = [], []
    for i, (title, verdict) in enumerate(specs):
        ln = line(title=title, body=PY, key=f"seeded:b:{i}")
        lines.append(ln)
        rows.append({"posting_key": ln["key"], "group": "random_reject", "title": title, "verdict": verdict})
    return rows, lines


def test_criterion_adopts_only_when_an_error_is_fixed_and_none_created():
    rows, lines = rows_and_lines([("ML Engineer Internship", "not_relevant")])
    m = measure.measure("C5", rows, lines)
    assert (m["errors_before"], m["errors_after"], m["criterion_result"]) == (1, 0, "adopted (Deepak's Gate 3b criterion)")
    rows, lines = rows_and_lines([("ML Engineer Internship", "not_relevant"), ("AI Engineer Internship", "relevant")])
    m = measure.measure("C5", rows, lines)
    assert len(m["fixed"]) == 1 and len(m["created"]) == 1 and m["criterion_result"].startswith("rejected")
    rows, lines = rows_and_lines([("Account Executive", "not_relevant")])
    assert measure.measure("C5", rows, lines)["criterion_result"].startswith("rejected")


def test_new_terms_list_the_audited_titles_they_match_and_nothing_else():
    rows, lines = rows_and_lines([("Software Engineer, Machine Learning", "relevant"), ("Account Executive", "not_relevant")])
    terms = {t["rule"]: t["audited_titles_matched"] for t in measure.measure("C2", rows, lines)["new_terms"]}
    assert terms == {"R11": ["Software Engineer, Machine Learning"], "R12": ["Software Engineer, Machine Learning"],
                     "R13": [], "R14": ["Software Engineer, Machine Learning"]}
