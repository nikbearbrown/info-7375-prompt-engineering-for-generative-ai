"""Shared CONSTRUCTED fixtures. Every posting here is made up for tests and labeled as such."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent.rule import plain_text  # noqa: E402


@pytest.fixture
def resume():
    return json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text())


def posting(pid, title, content_html="<p>We use Python daily.</p>", location="Boston, MA",
            system="greenhouse", board="constructed"):
    """A CONSTRUCTED posting in the normalized shape providers.py produces."""
    return {"key": f"{system}:{board}:{pid}", "system": system, "board": board, "id": pid,
            "title": title, "location": location, "text": plain_text(content_html),
            "url": f"https://example.invalid/{pid}"}


def greenhouse_board(*jobs):
    """CONSTRUCTED Greenhouse response bytes. jobs: (id, title, content_html)."""
    return json.dumps({"jobs": [{"id": i, "title": t, "location": {"name": "Boston, MA"},
                                 "content": c.replace("<", "&lt;").replace(">", "&gt;"),
                                 "absolute_url": f"https://example.invalid/{i}"} for i, t, c in jobs]}).encode()


def ashby_board(*jobs):
    """CONSTRUCTED Ashby response bytes. jobs: (id, title, text)."""
    return json.dumps({"apiVersion": "1", "jobs": [{"id": i, "title": t, "location": "Remote", "isListed": True,
                                                    "descriptionPlain": c, "jobUrl": f"https://example.invalid/{i}"}
                                                   for i, t, c in jobs]}).encode()
