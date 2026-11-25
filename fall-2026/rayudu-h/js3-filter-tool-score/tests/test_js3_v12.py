"""FILTER.md v1.2: R17 rejects a posting whose text asks for 5+ years; a range counts by its lower bound.
Postings are CONSTRUCTED. Also: the earlier versions are rebuilt exactly, so old results stay reproducible."""
from conftest import posting
from js3 import audit, filterdoc, score
from test_js3_wrong_versions import FILLER


def _r(text):
    return score.score(posting("v12", "Data Engineer", FILLER + f"<p>Python and SQL. {text}</p>"), filterdoc.load())


def test_five_years_is_rejected_by_r17():
    r = _r("You have 5+ years of experience building data pipelines.")
    assert r["decision"] == "rejected" and r["decided_by"] == "R17" and r["years_asked"] == 5


def test_four_years_is_not():
    assert _r("You have 4+ years of experience.")["decision"] == "kept"


def test_a_range_counts_by_its_lower_bound():          # the false friend found while measuring
    assert _r("Minimum 2-6 years of experience on relevant projects.")["decision"] == "kept"
    assert _r("6–10+ years of quality engineering experience.")["decision"] == "rejected"


def test_no_years_stated_is_not_rejected():
    assert _r("We value curiosity.")["decision"] == "kept"


def test_released_versions_are_rebuilt_exactly():
    vs = audit.versions()
    assert [vs[v]["filter_version"] for v in ("1.0", "1.1", "1.2")] == ["1.0", "1.1", "1.2"]
    assert "experience_years_min" not in vs["1.1"] and vs["1.0"]["seniority_ignore_phrases"] == []
    p = posting("v12b", "Data Engineer", FILLER + "<p>Python. 8+ years required.</p>")
    assert score.score(p, vs["1.1"])["decision"] == "kept" and score.score(p, vs["1.2"])["decision"] == "rejected"
