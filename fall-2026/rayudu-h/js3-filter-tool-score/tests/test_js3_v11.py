"""FILTER.md v1.1 (X1, accepted by Hemanth): "Staff" inside "Technical Staff" is not a seniority word.
Postings are CONSTRUCTED; the titles copy the shape of real Perplexity and Anthropic titles."""
import copy

from conftest import posting
from js3 import filterdoc, score
from test_js3_wrong_versions import FILLER


def test_member_of_technical_staff_is_not_senior():
    flt = filterdoc.load()
    r = score.score(posting("x1a", "Member of Technical Staff (Software Engineer, API Platform)",
                            FILLER + "<p>Python.</p>"), flt)
    assert r["seniority"] == [] and r["score"] == 4.5 and r["decision"] == "kept"


def test_staff_engineer_is_still_senior():
    flt = filterdoc.load()
    r = score.score(posting("x1b", "Staff+ Software Engineer, Platform", FILLER + "<p>Python.</p>"), flt)
    assert r["seniority"] == ["Staff"] and r["score"] == 2.5


def test_role_ignore_phrases_option_works_for_the_rejected_x4():
    flt = copy.deepcopy(filterdoc.load())
    flt["role_ignore_phrases"] = ["Data Center"]                 # X4, measured and rejected (FILTER.md 6)
    r = score.score(posting("x4", "Data Center Architect", FILLER + "<p>Python.</p>"), flt)
    assert r["role_words"] == []
