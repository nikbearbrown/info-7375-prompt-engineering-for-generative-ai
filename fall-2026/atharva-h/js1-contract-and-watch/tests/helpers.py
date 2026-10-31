import html
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import persona  # noqa: E402

RESUME = persona.load(os.path.join(ROOT, "persona", "resume.json"))
OFFER = "<p>We sponsor H-1B visas for this role.</p>"


def posting(title="Data Analyst", location="New York, NY", content=OFFER, pid=1, offices=None):
    """A Greenhouse-shaped posting. Greenhouse escapes its HTML once, so we do too."""
    return {"id": pid, "title": title, "location": {"name": location},
            "content": html.escape(content), "offices": offices or []}
