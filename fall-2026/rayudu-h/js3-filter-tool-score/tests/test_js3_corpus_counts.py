"""The hit counts printed in FILTER.md v1.0 (measured with exploratory scripts before any js3 code)
must be reproduced by the js3 code on the frozen corpus. Word lists are the v1.0 lists, written
out here so a later filter version cannot silently change what this test checks."""
import hashlib

from conftest import ROOT
from js3 import corpus, score

V1_ROLE = ["AI", "Engineer", "Engineering", "ML", "Machine Learning", "Data"]
V1_EXCLUDE = ["Manager", "Director", "Head", "Intern", "Internship", "VP", "Vice President", "Chief",
              "Recruiter", "Sales", "Account", "Counsel", "Finance", "Marketing", "Partner"]
V1_SENIORITY = ["Staff", "Principal", "Senior", "Sr", "Lead"]


def test_corpus_matches_the_frozen_manifest():
    lines = (ROOT / "CORPUS.sha256").read_text().split("\n")
    for line in filter(None, lines):
        digest, path = line.split(maxsplit=1)
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path


def test_unique_postings_by_board():
    c = corpus.load()
    assert len(c["postings"]) == 1176
    by_board = {}
    for p in c["postings"].values():
        by_board[p["board"]] = by_board.get(p["board"], 0) + 1
    assert by_board == {"anthropic": 815, "notion": 193, "perplexity": 168}


def test_filter_md_hit_counts():
    ps = list(corpus.load()["postings"].values())

    def titles_with_any(words):
        return sum(1 for p in ps if score.find(words, p["title"]))

    def text_with(word):
        return sum(1 for p in ps if score.find([word], p["title"] + " " + p["text"]))

    assert titles_with_any(V1_ROLE) == 491
    assert titles_with_any(V1_EXCLUDE) == 507
    assert titles_with_any(V1_SENIORITY) == 322
    assert sum(1 for p in ps if score.find(["security clearance"], p["text"])) == 17
    assert sum(1 for p in ps if score.find(["MS"], p["text"])) == 15
    assert {w: text_with(w) for w in ["Python", "SQL", "AWS", "Databricks", "Power BI", "Delta Lake"]} == \
        {"Python": 302, "SQL": 139, "AWS": 124, "Databricks": 6, "Power BI": 6, "Delta Lake": 1}
