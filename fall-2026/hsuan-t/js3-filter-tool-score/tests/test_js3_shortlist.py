"""JS3 shortlist (reports/shortlist.py) on fake postings: labels, verbatim quotes, insufficient claims.

The fake postings are judged by the real rule judge, so the justification lines are the ones
audit/all_verdicts.json holds. Everything is written under tmp_path; the repo's shortlist/ and
audit/ folders are never touched. The script is loaded from its file because reports/ is a
folder of scripts, not a package.
"""

import html
import importlib.util
import json
from pathlib import Path

import pytest

from job_agent import inputs
from job_agent.common.paths import Paths
from job_agent.judges import rule
from job_agent.judges.words import strip_html
from job_agent.watch.boards import greenhouse

ROOT = Path(__file__).resolve().parents[1]
RAW_REL = "evidence/raw/2026-11-08T000000Z/stripe_content.json"
FULL_HTML = (
    "<p>You will build backend services in Java.</p>"
    "<p>You need 2 years of experience. Ideally 4 years with Python!</p>"
    "<p>Pay is $70,000 to $120,000.</p>"
    "<p>You will learn Kubernetes on the job.</p>"
)
FULL = {"id": 11, "title": "Backend Engineer", "location": "Boston, US", "html": FULL_HTML}
BARE = {"id": 12, "title": "Platform Engineer", "location": "", "html": "<p>We write Python services</p>"}
CUT = {"id": 13, "title": "Staff Backend Engineer", "location": "US", "html": FULL_HTML}


@pytest.fixture
def criteria(tmp_path):
    """The shipped Aarav résumé + profile, built here so this file does not depend on conftest.py
    (it is also run on its own, where conftest fixtures may not be loaded)."""
    paths = Paths(out=tmp_path / "paths_out")
    return inputs.load_criteria(paths.default_resume, paths.default_profile, paths)


def _load():
    spec = importlib.util.spec_from_file_location("shortlist_test_module", ROOT / "reports" / "shortlist.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _audit(tmp_path, criteria, specs):
    raw = tmp_path / RAW_REL
    raw.parent.mkdir(parents=True)
    jobs = [{"id": s["id"], "title": s["title"], "location": {"name": s["location"]}, "offices": [],
             "content": html.escape(s["html"]), "absolute_url": f"https://example.test/{s['id']}"} for s in specs]
    raw.write_text(json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}), encoding="utf-8")
    entries = []
    for p in greenhouse.parse(raw.read_bytes()):
        r = rule.judge(p, criteria)
        entries.append({"board": "stripe", "posting_id": p.id, "title": p.title, "location": p.location,
                        "url": f"https://example.test/{p.id}", "raw_file": RAW_REL,
                        "verdict": r.verdict["verdict"], "status": r.verdict["status"],
                        "failed_check": r.failed_check, "justification": r.verdict["justification"]})
    audit = tmp_path / "audit"
    audit.mkdir()
    doc = {"generated_from": ["2026-11-08T000000Z"], "total": len(entries), "postings": entries}
    (audit / "all_verdicts.json").write_text(json.dumps(doc), encoding="utf-8")
    return audit


def _run(tmp_path, criteria, specs):
    audit = _audit(tmp_path, criteria, specs)
    out = tmp_path / "shortlist"
    assert _load().run(audit, out, repo_root=tmp_path) == 0
    data = json.loads((out / "shortlist.json").read_text(encoding="utf-8"))
    return {str(p["posting_id"]): p for p in data["postings"]}, (out / "SHORTLIST.md").read_text(encoding="utf-8")


def _rule(posting, rid):
    return [c for c in posting["claims"] if c["rule"] == rid]


def test_only_kept_postings_get_claims_with_code_labels(tmp_path, criteria):
    postings, _ = _run(tmp_path, criteria, [FULL, BARE, CUT])
    assert set(postings) == {"11", "12"}
    for p in postings.values():
        for c in p["claims"]:
            assert c["rule"] in {"1b", "2", "3", "4", "5", "6"}
            assert c["label"] in {"supported", "insufficient"}
            assert c["label_by"] == "code"
            assert (c["final_label"], c["final_by"], c["note"]) == ("", "", "")
            assert (c["quote"] is None) == (c["label"] == "insufficient")


def test_quotes_are_verbatim_and_pick_the_deciding_sentence(tmp_path, criteria):
    postings, _ = _run(tmp_path, criteria, [FULL])
    p = postings["11"]
    plain = strip_html(html.escape(FULL_HTML))
    for c in p["claims"]:
        if c["quote"] is None:
            continue
        field = {"1b": p["title"], "2": p["location"]}.get(c["rule"], plain)
        assert c["quote"] in field
    assert _rule(p, "1b")[0]["claim"] == "The title is an engineering role Aarav targets (backend)"
    assert _rule(p, "2")[0]["label"] == "supported"
    # FILTER v2 (B2): rule 4 decides on the largest years number, so that sentence is the evidence.
    assert _rule(p, "4")[0]["quote"] == "Ideally 4 years with Python"
    assert _rule(p, "6")[0]["quote"] == "Pay is $70,000 to $120,000"
    skills = {c["claim"]: c for c in _rule(p, "3")}
    assert skills["The JD asks for Java, which Aarav has"]["quote"] == "You will build backend services in Java"
    assert skills["The JD asks for Python, which Aarav has"]["quote"] == "Ideally 4 years with Python"
    # Code does not judge the sense: "learn Kubernetes" is still quoted; the hand review may relabel it.
    k8s = skills["The JD asks for Kubernetes, which Aarav has"]
    assert (k8s["label"], k8s["quote"]) == ("supported", "You will learn Kubernetes on the job")


def test_a_skill_with_a_dot_is_quoted_whole(tmp_path, criteria):
    # Real openai JDs list "Python, Go, Node.js, Rust"; splitting on every "." cut Node.js in two and
    # the claim lost its quote. The sentence must stay whole so the skill keeps its evidence.
    jd = {"id": 14, "title": "Backend Engineer", "location": "US",
          "html": "<p>Backend services in Python, Go, Node.js, or Rust. We ship daily.</p>"}
    postings, _ = _run(tmp_path, criteria, [jd])
    node = [c for c in _rule(postings["14"], "3") if "Node.js" in c["claim"]][0]
    assert (node["label"], node["quote"]) == ("supported", "Backend services in Python, Go, Node.js, or Rust")


def test_missing_information_is_insufficient_with_null_quote(tmp_path, criteria):
    postings, _ = _run(tmp_path, criteria, [FULL, BARE])
    bare = postings["12"]
    expected = {"2": "The job location is in the US", "4": "The JD requires at most 4 years of experience",
                "5": "The JD does not refuse visa sponsorship", "6": "The pay reaches $75,000"}
    for rid, text in expected.items():
        (c,) = _rule(bare, rid)
        assert (c["claim"], c["label"], c["quote"]) == (text, "insufficient", None)
    (visa,) = _rule(postings["11"], "5")
    assert (visa["label"], visa["quote"]) == ("insufficient", None)


def test_summary_line_names_insufficient_rules_in_order(tmp_path, criteria):
    postings, md = _run(tmp_path, criteria, [FULL, BARE])
    assert postings["11"]["summary"] == "relevant — insufficient: visa"
    assert postings["12"]["summary"] == "relevant — insufficient: location, years, visa, salary"
    for p in postings.values():
        assert p["summary"] in md and p["title"] in md and p["url"] in md
    assert "| claim | code label | quote |" in md


def test_no_relevant_postings_still_writes_both_files(tmp_path, criteria):
    audit = _audit(tmp_path, criteria, [CUT])
    out = tmp_path / "new" / "shortlist"
    assert _load().run(audit, out, repo_root=tmp_path) == 0
    data = json.loads((out / "shortlist.json").read_text(encoding="utf-8"))
    assert data["postings"] == []
    assert "no relevant postings" in data["message"]
    assert "no relevant postings" in (out / "SHORTLIST.md").read_text(encoding="utf-8").lower()
