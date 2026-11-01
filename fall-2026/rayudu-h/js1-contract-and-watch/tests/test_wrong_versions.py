"""The two wrong versions named in CONTRACT.md, and the tests that must catch them.

Each check is run against the real implementation (must pass) and against a deliberately
wrong implementation written here (must be caught). All postings are CONSTRUCTED.
"""
import json

from conftest import ROOT, board, posting
from jsagent import cli, rule, watch


# ---- Wrong version 1: "new" keyed on the wrong id ------------------------------------------

def new_by_requisition_id(jobs, seen_reqs):
    """WRONG VERSION 1: remembers requisition_id instead of the posting id."""
    if seen_reqs is None:
        return []
    return [j for j in jobs if j["requisition_id"] not in seen_reqs]


def check_new_is_keyed_on_posting_id(new_fn, key):
    run1 = [posting(1, "AI Engineer", req="R")]
    run2 = run1 + [posting(2, "Applied AI Engineer", req="R")]   # same requisition, new posting
    assert new_fn(run1, None) == []                               # baseline reports none
    seen = {j[key] for j in run1}
    return [j["id"] for j in new_fn(run2, seen)] == [2]


def test_new_is_keyed_on_posting_id():
    assert check_new_is_keyed_on_posting_id(watch.new_postings, "id")


def test_wrong_version_1_is_caught():
    assert not check_new_is_keyed_on_posting_id(new_by_requisition_id, "requisition_id")


# ---- Wrong version 2: verdicts paired with the wrong postings -------------------------------

THREE_NEW = [
    posting(11, "Machine Learning Engineer", "<p>Python and AWS.</p>"),            # relevant
    posting(12, "Engineering Manager, Platform", "<p>Python.</p>"),                # not relevant (management)
    posting(13, "AI Research Engineer", ""),                                       # cannot judge (no content)
]
EXPECTED = {11: rule.RELEVANT, 12: rule.NOT_RELEVANT, 13: rule.CANNOT_JUDGE}


def check_pairing(rows, postings):
    by_id = {p["id"]: p for p in postings}
    for r in rows:
        if r["verdict"] != EXPECTED[r["id"]]:
            return False
        if f'"{by_id[r["id"]]["title"]}"' not in r["justification"] and r["verdict"] != rule.CANNOT_JUDGE:
            return False
    return len(rows) == len(postings)


def shifted_pairing(postings, resume):
    """WRONG VERSION 2: judges in title order but attaches results to postings in the original order."""
    verdicts = [rule.judge(p, resume) for p in sorted(postings, key=lambda p: p["title"])]
    return [dict(v, id=p["id"]) for p, v in zip(postings, verdicts)]


def test_verdicts_pair_with_their_postings(tmp_path, resume):
    """End to end through the CLI: baseline on one posting, then a run with three new ones."""
    raw1, raw2 = tmp_path / "r1.json", tmp_path / "r2.json"
    raw1.write_bytes(board(posting(10, "Data Analyst")))
    raw2.write_bytes(board(posting(10, "Data Analyst"), *THREE_NEW))
    common = ["run", "--board", "constructed", "--resume", str(ROOT / "persona" / "priya-nair.resume.json"),
              "--state", str(tmp_path / "seen.json"), "--runs-dir", str(tmp_path / "runs"),
              "--label", "constructed", "--no-claude"]
    assert cli.main(common + ["--from-raw", str(raw1)]) == 0
    assert cli.main(common + ["--from-raw", str(raw2)]) == 0
    run_dirs = sorted((tmp_path / "runs").iterdir())
    rows = [json.loads(line)["record"] for line in (run_dirs[-1] / "judgments.jsonl").read_text().splitlines()]
    assert check_pairing(rows, THREE_NEW)


def test_wrong_version_2_is_caught(resume):
    assert check_pairing([rule.judge(p, resume) for p in THREE_NEW], THREE_NEW)
    assert not check_pairing(shifted_pairing(THREE_NEW, resume), THREE_NEW)
