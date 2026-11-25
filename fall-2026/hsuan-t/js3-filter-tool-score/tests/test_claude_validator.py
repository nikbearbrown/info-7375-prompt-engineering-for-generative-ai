"""CONTRACT validator table (R20): one rejected example per row, taken from the table itself, plus
the accepted case, so each row can be traced from the CONTRACT to a test by its number.
"""

import json

import pytest

from job_agent.judges.validator import Rejected, squash, validate

FIELDS = {
    "title": "Backend Engineer, Core Technology",
    "location.name": "US-Remote, Chicago",
    "content": "You will write programming languages like Go, Java, C/C++ every day.",
}
LINE = {"posting_field": "content", "compared_to": "resume.skills[].keywords[]",
        "result": "requires Java, which the résumé lists", "quote": "programming languages like Go, Java, C/C++"}
GOOD = {"posting_id": 6042172, "verdict": "relevant", "justification": [LINE]}


def _check(reply) -> tuple[str, list]:
    return validate(reply if isinstance(reply, str) else json.dumps(reply), 6042172, FIELDS)


def test_a_reply_that_follows_every_row_is_accepted():
    assert _check(GOOD) == ("relevant", [LINE])


@pytest.mark.parametrize("row, reply, reason", [
    ("1 only JSON", "This job looks like a good fit!", "not valid JSON"),
    ("1 only JSON", "```json\n" + json.dumps(GOOD) + "\n```", "not valid JSON"),
    ("1 only JSON", "Here you go: " + json.dumps(GOOD), "not valid JSON"),
    ("2 exact keys", {k: v for k, v in GOOD.items() if k != "justification"}, "exactly the keys"),
    ("2 exact keys", {**GOOD, "confidence": 0.9}, "exactly the keys"),
    ("3 same posting", {**GOOD, "posting_id": 8138044}, "does not match"),
    ("3 same posting", {**GOOD, "posting_id": "6042172"}, "does not match"),
    ("4 verdict word", {**GOOD, "verdict": "maybe"}, "verdict must be"),
    ("5 lines", {**GOOD, "justification": []}, "non-empty list"),
    ("5 lines", {**GOOD, "justification": [{k: v for k, v in LINE.items() if k != "quote"}]}, "exactly the keys"),
    ("5 lines", {**GOOD, "justification": [{**LINE, "quote": ""}]}, "non-empty strings"),
    ("6 posting_field", {**GOOD, "justification": [{**LINE, "posting_field": "salary"}]}, "posting_field"),
    ("7 compared_to", {**GOOD, "justification": [{**LINE, "compared_to": "common sense"}]}, "compared_to"),
    ("8 quote exists", {**GOOD, "justification": [{**LINE, "quote": "5+ years of Rust required"}]}, "quote not found"),
    ("8 quote exists", {**GOOD, "justification": [{**LINE, "posting_field": "title"}]}, "quote not found in posting.title"),
])
def test_each_contract_row_rejects_its_example(row, reply, reason):
    with pytest.raises(Rejected, match=reason):
        _check(reply)


def test_quote_match_ignores_html_case_and_spacing():
    # CONTRACT row 8: compare after removing HTML, lowercasing, and treating any run of spaces as one.
    quote = {**LINE, "quote": "<b>PROGRAMMING</b>   languages like\n Go, Java, C/C++"}
    assert _check({**GOOD, "justification": [quote]})[0] == "relevant"
    assert squash("<p>A  &amp;\tB</p>") == "a & b"


def test_first_bad_line_is_named():
    lines = [LINE, {**LINE, "quote": "not there"}]
    with pytest.raises(Rejected, match=r"justification\[1\]"):
        _check({**GOOD, "justification": lines})
