"""SHORTLIST.md: every generated block is checks/shortlist_report.py's verbatim output, and the
script's key-word, agreement and abstention logic behaves at its boundaries. Offline; no API call."""

import contextlib
import importlib.util
import io
import re

import pytest

from agent import PROJECT_DIR

SHORTLIST = (PROJECT_DIR / "SHORTLIST.md").read_text(encoding="utf-8")


def _module():
    spec = importlib.util.spec_from_file_location("shortlist_report", PROJECT_DIR / "checks" / "shortlist_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sr = _module()


def _run(section):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert sr.main(["--section", section]) == 0
    return buf.getvalue()


def _block(section):
    begin = f"<!-- BEGIN checks/shortlist_report.py --section {section} output -->\n"
    end = f"<!-- END checks/shortlist_report.py --section {section} output -->"
    return SHORTLIST[SHORTLIST.index(begin) + len(begin):SHORTLIST.index(end)]


@pytest.mark.parametrize("section", sr.SECTIONS)
def test_every_block_is_the_script_output_verbatim(section):
    assert _block(section) == _run(section)


@pytest.fixture(scope="module")
def data():
    return sr.load()


def test_sheet_and_claims_join_one_to_one(data):
    rows, postings = data
    assert len(rows) == 96 and len(postings) == 17
    assert [r["row"] for r in rows] == list(range(1, 97))
    assert {r["me"] for r in rows} <= set(sr.LABELS) and {r["claude"] for r in rows} <= set(sr.LABELS)


def test_headline_numbers(data):
    rows, postings = data
    a = sr.agreement(rows)
    assert a["overall"] == (85, 96) and a["quoted"] == (55, 66) and a["empty"] == (30, 30)
    assert sum(a["matrix"].values()) == 96
    ab = sr.abstention(rows, postings)
    assert sum(p["verdict"] == "keep" for p in ab) == 0
    assert all("sponsorship" in p["insufficient"] for p in ab)
    assert len(sr.relevance_not_entailment(rows, sr._skills())) == 20


def test_relevance_rows_cited_in_prose_are_in_the_table(data):
    rows, _ = data
    found = {r["row"] for r in sr.relevance_not_entailment(rows, sr._skills())}
    assert {48, 77, 3, 8, 13, 18, 23} <= found


SKILLS = ["Python", "PostgreSQL", "TypeScript"]


@pytest.mark.parametrize("kind,claim,quote,expected", [
    ("skill", "The role requires PostgreSQL.", "familiarity with databases like Postgres or MySQL", ["Postgres"]),
    ("skill", "The work uses Python.", "Strong coding skills in any programming language", []),
    ("skill", "The work uses Python.", "We use TypeScript.", []),          # only skills the claim names
    ("skill", "The work uses Java.", "We use Java and JavaScript.", []),    # Java is not in SKILLS here
    ("experience", "At most 2 years.", "2+ years of experience", ["year", "experience"]),
    ("experience", "At most 2 years.", "Pursuing a bachelor's degree", []),
    ("location", "The job is in the US.", "For roles based in San Francisco, the salary is", ["San Francisco"]),
    ("location", "The job is in the US.", "us and them", []),               # "US" is uppercase-only
    ("role", "A software engineering role.", "so product engineers can ship", ["Engineer"]),
    ("role", "A software engineering role.", "familiarity with programming", []),
    ("seniority", "Early-career.", "partner with senior engineers", ["Senior"]),
    ("seniority", "Entry level.", "As an IC4 on this team", []),
])
def test_key_words(kind, claim, quote, expected):
    assert sr.key_words(kind, claim, quote, SKILLS) == expected


def test_key_words_are_whole_word_and_deduplicated():
    assert sr.key_words("location", "US", "San Francisco or New York", []) == ["San Francisco", "New York"]
    assert sr.key_words("role", "AI role", "maintain the system", []) == []  # "ai" inside a word


def _row(n, pid, kind, me, claude, quote="q", found=True, claim="c"):
    return {"row": n, "posting_id": pid, "kind": kind, "me": me, "claude": claude, "quote": quote,
            "quote_found": found, "claim": claim, "title": "t", "note": ""}


def _postings(*pids):
    return {p: {"board": "b", "posting_id": p, "title": "t", "locations": "", "text": "no mention"} for p in pids}


def test_abstention_boundaries():
    rows = [_row(1, "A", k, "supported", "supported") for k in sr.CRITICAL]
    rows += [_row(5, "B", k, "supported", "supported") for k in ("role", "location", "experience")]
    rows += [_row(8, "B", "sponsorship", "insufficient", "insufficient", quote="", found=None)]
    rows += [_row(9, "C", k, "supported", "supported") for k in sr.CRITICAL]
    rows += [_row(13, "C", "skill", "insufficient", "insufficient")]          # non-critical: no abstention
    rows += [_row(14, "D", k, "supported", "supported") for k in ("role", "location", "sponsorship")]
    rows += [_row(17, "D", "experience", "contradicted", "contradicted")]
    ab = {p["posting_id"]: p for p in sr.abstention(rows, _postings("A", "B", "C", "D"))}
    assert ab["A"]["verdict"] == "keep"
    assert ab["B"]["verdict"] == "cannot_tell" and ab["B"]["insufficient"] == ["sponsorship"]
    assert ab["C"]["verdict"] == "keep"
    # contradicted is not insufficient: the rule as written does not abstain, and it is reported
    assert ab["D"]["verdict"] == "keep" and ab["D"]["contradicted"] == ["experience"]


def test_relevance_excludes_supported_empty_and_not_found():
    rows = [_row(1, "A", "skill", "supported", "supported", claim="uses Python", quote="Python"),
            _row(2, "A", "skill", "insufficient", "insufficient", claim="uses Python", quote="", found=None),
            _row(3, "A", "skill", "insufficient", "insufficient", claim="uses Python", quote="Python", found=False),
            _row(4, "A", "skill", "insufficient", "supported", claim="uses Python", quote="Python is a plus")]
    assert [r["row"] for r in sr.relevance_not_entailment(rows, ["Python"])] == [4]


def test_agreement_separates_empty_quotes():
    rows = [_row(1, "A", "role", "supported", "supported"),
            _row(2, "A", "role", "insufficient", "supported"),
            _row(3, "A", "sponsorship", "insufficient", "insufficient", quote="", found=None)]
    a = sr.agreement(rows)
    assert a["overall"] == (2, 3) and a["quoted"] == (1, 2) and a["empty"] == (1, 1)
    assert a["by_kind"]["seniority"] == (0, 0)


def test_load_refuses_a_bad_label(tmp_path):
    sheet = tmp_path / "sheet.csv"
    text = sr.SHEET.read_text(encoding="utf-8")
    sheet.write_text(re.sub(r",s,", ",supported,", text, count=1), encoding="utf-8")
    with pytest.raises(ValueError, match="my_label"):
        sr.load(sheet=sheet)


def test_load_refuses_a_misaligned_sheet(tmp_path):
    sheet = tmp_path / "sheet.csv"
    lines = sr.SHEET.read_text(encoding="utf-8").splitlines(keepends=True)
    sheet.write_text(lines[0] + "".join(lines[2:]), encoding="utf-8")
    with pytest.raises(ValueError):
        sr.load(sheet=sheet)
