"""Shared test fixtures.

Every posting in this file is CONSTRUCTED for testing. None of them is a real
Greenhouse posting, and no output produced from them is Claude output.
"""

import copy
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONA_PATH = ROOT / "persona" / "alex_morgan.json"


def persona():
    return json.loads(PERSONA_PATH.read_text(encoding="utf-8"))


def esc(markup):
    """Greenhouse returns posting content HTML-escaped; build fixtures the same way."""
    return html.escape(markup, quote=True)


def job(job_id, title, location, content_markup):
    """One job record shaped like a Greenhouse Job Board API job with content=true."""
    return {
        "absolute_url": f"https://job-boards.greenhouse.io/constructed/jobs/{job_id}",
        "data_compliance": [
            {
                "type": "gdpr",
                "requires_consent": False,
                "requires_processing_consent": False,
                "requires_retention_consent": False,
                "retention_period": None,
                "demographic_data_consent_applies": False,
            }
        ],
        "internal_job_id": job_id + 1,
        "location": {"name": location},
        "metadata": None,
        "id": job_id,
        "updated_at": "2026-10-27T12:00:00-04:00",
        "requisition_id": f"REQ-{job_id}",
        "title": title,
        "company_name": "Constructed Co",
        "first_published": "2026-10-20T12:00:00-04:00",
        "language": "en",
        "content": esc(content_markup),
        "departments": [],
        "offices": [],
    }


def board_bytes(*jobs):
    return json.dumps({"jobs": [copy.deepcopy(j) for j in jobs], "meta": {"total": len(jobs)}}).encode("utf-8")


# Two constructed postings with different ids and opposite rule outcomes
# (CONTRACT.md, wrong version 1). They differ only in the word "Senior".
RELEVANT_101 = job(101, "Software Engineer, Inference", "San Francisco, CA", "<p>You write Python and PyTorch daily.</p>")
NOT_RELEVANT_202 = job(202, "Senior Software Engineer, Inference", "San Francisco, CA", "<p>You write Python and PyTorch daily.</p>")
OTHER_1 = job(1, "Recruiting Coordinator", "Dublin, IE", "<p>Scheduling.</p>")


def supported_response(posting_input, verdict):
    """A model response whose every citation exists in the supplied inputs."""
    return json.dumps(
        {
            "posting_id": str(posting_input["id"]),
            "verdict": verdict,
            "justification": "The title and the content are cited below.",
            "resume_evidence": [{"field": "resume.skills", "quote": "python"}],
            "posting_evidence": [{"field": "posting.title", "quote": posting_input["title"]}],
        }
    )


class ScriptedModel:
    """Stands in for the external model call. Answers by posting id; records each call."""

    def __init__(self, verdicts=None, replies=None):
        self.verdicts = verdicts or {}
        self.replies = replies or {}
        self.calls = []

    def __call__(self, system, user):
        self.calls.append((system, user))
        posting = json.loads(user)["posting"]
        if posting["id"] in self.replies:
            return self.replies[posting["id"]]
        return supported_response(posting, self.verdicts[posting["id"]])
