"""CONTRACT Wrong version 4 — case or spacing changes a verdict.

The contract's fix is that every check calls the ONE splitter in judges/words.py. The first test
is the contract's table, verbatim. The others prove the checks really go through that splitter:
a posting written in messy case/spacing must get exactly the same verdict as the clean version.
"""

import pytest

from job_agent.common.posting import Posting
from job_agent.judges import rule
from job_agent.judges.words import words


@pytest.mark.parametrize("check, text, expected", [
    ("1 title", "\tSoftware   Engineer/Backend", ["software", "engineer", "backend"]),
    ("2 location", "US-Remote, Chicago", ["us", "remote", "chicago"]),
    ("3 JD text (HTML removed)", "Experience with JAVA, Node.js", ["experience", "with", "java", "node", "js"]),
    ("3 résumé keyword", "Fluent Bit", ["fluent", "bit"]),
    ("5 visa phrase", "Without  Sponsorship", ["without", "sponsorship"]),
])
def test_contract_splitter_table(check, text, expected):
    assert words(text) == expected, check


def test_splitter_drops_empty_pieces_and_underscores():
    assert words("  --/,  ") == []
    assert words("node_js") == ["node", "js"]


def _judge(criteria, title, location, content):
    return rule.judge(Posting(1, title, location, content), criteria).verdict


@pytest.mark.parametrize("messy", [
    # Same posting as the clean one below, written the way real boards sometimes do.
    ("\tBACKEND   Engineer", "us-REMOTE", "<p>JAVA required. 2+ YEARS.</p>"),
    ("Backend/Engineer", "US - Remote", "<p>java,\n\t2+   years</p>"),
])
def test_messy_case_and_spacing_give_the_same_verdict(criteria, messy):
    clean = _judge(criteria, "Backend Engineer", "US Remote", "<p>Java required. 2+ years.</p>")
    dirty = _judge(criteria, *messy)
    assert clean["verdict"] == dirty["verdict"] == "relevant"
    assert [l["result"] for l in clean["justification"]] == [l["result"] for l in dirty["justification"]]


def test_exclude_word_is_found_in_any_case(criteria):
    v = _judge(criteria, "SENIOR Backend Engineer", "US", "<p>Java</p>")
    assert v["justification"][-1]["result"] == "match: senior"


def test_multi_word_skill_matches_across_punctuation(criteria):
    # Aarav lists "Fluent Bit"; the JD writes it with a hyphen and capitals — the only skill present.
    v = _judge(criteria, "Backend Engineer", "US", "<p>We ship logs with FLUENT-BIT.</p>")
    assert v["justification"][3]["result"] == "1 found: Fluent Bit"


@pytest.mark.parametrize("loc", ["", "   ", "N/A", "n/a", "na", "Remote", "Remote "])
def test_missing_location_passes_check_2(criteria, loc):
    """Isaac's rule: no location written (or a bare "Remote") counts as a pass, like checks 4-6."""
    v = _judge(criteria, "Backend Engineer", loc, "<p>Java required. 2+ years.</p>")
    assert v["verdict"] == "relevant"
    assert v["justification"][2]["result"] == "skipped: no location in posting"


@pytest.mark.parametrize("loc", ["Dublin", "Remote - Canada", "Seattle, WA"])
def test_a_real_place_outside_the_list_still_fails(criteria, loc):
    v = _judge(criteria, "Backend Engineer", loc, "<p>Java required. 2+ years.</p>")
    assert v["justification"][-1] == {"posting_field": "location.name", "compared_to": "profile.locations[]", "result": "no match"}
