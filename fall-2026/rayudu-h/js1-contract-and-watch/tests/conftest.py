"""Shared CONSTRUCTED fixtures. Every posting here is made up for tests and labeled as such."""
import html
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def resume():
    return json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text())


def posting(pid, title, content_html="<p>We use Python daily.</p>", location="Boston, MA", req="R1"):
    """A CONSTRUCTED Greenhouse-shaped posting. `content` is escaped HTML, as Greenhouse returns it."""
    return {"id": pid, "requisition_id": req, "internal_job_id": pid + 1000, "title": title,
            "location": {"name": location}, "content": html.escape(content_html),
            "absolute_url": f"https://job-boards.greenhouse.io/constructed/jobs/{pid}"}


def board(*postings):
    return json.dumps({"jobs": list(postings), "meta": {"total": len(postings)}}).encode()
