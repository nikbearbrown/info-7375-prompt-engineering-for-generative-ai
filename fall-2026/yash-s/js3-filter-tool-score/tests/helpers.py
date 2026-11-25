"""Shared test helpers. Every posting built here is CONSTRUCTED for a test, not a
real JS2 posting. The rules come from the real rules/*.json files."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import job_filter as J  # noqa: E402
import postings as P  # noqa: E402

PERSONA_PATH = P.DEFAULT_JS2 / "persona" / P.PERSONA_NAME

# The résumé's skills section, used only if the real persona file is not present.
# tests/test_rules_files.py checks the real file separately.
CONSTRUCTED_SKILLS = {"skills": {
    "languages": ["Python", "SQL"], "data_bi": ["Databricks", "Unity Catalog", "Power BI"],
    "backend_automation": ["LangGraph", "MLflow", "Mem0"], "database_cloud": ["Delta Lake", "AWS"],
    "familiar_with_not_shipped": ["Ray", "Kubeflow"]}}


def persona():
    if PERSONA_PATH.exists():
        return json.loads(PERSONA_PATH.read_text(encoding="utf-8"))
    return CONSTRUCTED_SKILLS


def rules(boilerplate=None):
    """Real rules. A test can pass its own boilerplate list instead of rules/boilerplate.json."""
    r = J.load_rules(persona=persona())
    if boilerplate is not None:
        r = copy.copy(r)
        r["boilerplate"] = {"sentences": boilerplate}
        r["approved_boilerplate"] = J.approved_boilerplate(r["boilerplate"])
    else:
        # Tests never depend on whatever I have labeled in rules/boilerplate.json.
        r = copy.copy(r)
        r["approved_boilerplate"] = {}
    return r


# A body that earns full topic and skill points and says no experience is required.
GOOD_BODY = ("<p>You will build data pipelines and machine learning models.</p>"
             "<ul><li>Write Python and SQL on AWS.</li></ul>"
             "<p>No prior experience required.</p>")


def posting(title="Data Engineer", location="San Francisco", body=GOOD_BODY, board="Databricks", pid="t-1"):
    return {"board": board, "id": pid, "title": title, "location": location, "url": "",
            "markup": body, "source_run": "constructed", "source_file": "constructed"}


def evaluate(**kw):
    rr = kw.pop("rules", None) or rules()
    return J.evaluate(posting(**kw), rr)


def exp(*paragraphs, headings=None):
    """Experience status for constructed paragraphs (each becomes one <p>)."""
    body = "".join(f"<p>{x}</p>" for x in paragraphs)
    if headings:
        body = headings + body
    return J.experience(P.sentences(body), rules())
