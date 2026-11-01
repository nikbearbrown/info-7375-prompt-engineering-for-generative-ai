"""Shared test helpers. Every posting built here is CONSTRUCTED, not a real posting."""
import json

from agent.config import ROOT

JACK = json.loads((ROOT / "data" / "resume_jack_spencer.json").read_text(encoding="utf-8"))


def constructed_posting(pid: int, title: str, content: str = "") -> dict:
    return {
        "id": pid,
        "title": title,
        "location_name": "CONSTRUCTED",
        "absolute_url": f"https://example.com/constructed/{pid}",
        "updated_at": "",
        "content_text": content,
    }


def constructed_greenhouse_job(pid: int, title: str, content_html: str = "") -> dict:
    """Same shape as a Greenhouse job object, for end-to-end tests."""
    return {"id": pid, "title": title, "location": {"name": "CONSTRUCTED"},
            "absolute_url": f"https://example.com/constructed/{pid}",
            "updated_at": "2026-10-31T00:00:00-04:00", "content": content_html}
