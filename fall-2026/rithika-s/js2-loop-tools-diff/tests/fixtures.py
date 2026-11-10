"""CONSTRUCTED fixture postings for offline tests.

None of these postings came from Greenhouse or any real board. They are
hand-written to exercise one rule boundary each. Content is HTML-escaped the
way the Greenhouse jobs feed escapes it.
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESUME_PATH = ROOT / "data" / "resume.example.json"
TARGET_PATH = ROOT / "data" / "target.example.json"


def constructed(pid, title, body_html):
    """A CONSTRUCTED posting with Greenhouse-style escaped HTML content."""
    return {
        "id": pid,
        "title": title,
        "absolute_url": f"https://example.invalid/constructed/{pid}",
        "content": html.escape(body_html),
        "_constructed": True,
    }


# CONSTRUCTED: all three conditions hold (Python, SQL, Databricks).
RELEVANT = constructed(
    9001, "Machine Learning Engineer, Data Platform",
    "<p>You will write <strong>Python</strong> and SQL on Databricks.</p>")

# CONSTRUCTED: strong skill and title match, but excluded term in content.
EXCLUDED = constructed(
    9002, "ML Engineer, Public Sector",
    "<p>Python, MLflow and AWS daily.</p><p>Active security clearance "
    "required.</p>")

# CONSTRUCTED: skills match but the title has no target keyword.
WRONG_TITLE = constructed(
    9003, "Account Executive",
    "<p>Comfort with Python and SQL dashboards in Power BI.</p>")

# CONSTRUCTED: exactly one counted skill (Python). PostgreSQL must not count
# as SQL; Ray and Kubeflow (familiar_with_not_shipped) never count.
ONE_SKILL = constructed(
    9004, "AI Engineer",
    "<p>Python services on PostgreSQL, scaled with Ray and Kubeflow.</p>")

# CONSTRUCTED: exactly two counted skills (Python, AWS).
TWO_SKILLS = constructed(
    9005, "Data Engineer",
    "<p>Build pipelines in Python on AWS.</p>")

# CONSTRUCTED: skills hidden behind entities. "&nbsp;" inside the HTML is
# double-escaped by html.escape, and "&amp;" joins two skills.
ENTITIES = constructed(
    9006, "ML Platform Engineer",
    "<p>Power&nbsp;BI reports, MLflow&amp;LangGraph agents.</p>")

ALL = [RELEVANT, EXCLUDED, WRONG_TITLE, ONE_SKILL, TWO_SKILLS, ENTITIES]


def write_board(path, postings):
    """Write a CONSTRUCTED Greenhouse-shaped board response to path."""
    body = {"_comment": "CONSTRUCTED test fixture, not a real board response",
            "jobs": postings, "meta": {"total": len(postings)}}
    Path(path).write_text(json.dumps(body), encoding="utf-8")
    return Path(path)


def load_example_inputs():
    from agent.resume import load_resume, load_target
    return load_resume(RESUME_PATH), load_target(TARGET_PATH)
