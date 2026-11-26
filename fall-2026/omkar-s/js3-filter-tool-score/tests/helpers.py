"""Constructed postings for tests (labelled CONSTRUCTED: none of these is a real posting)."""
import copy
import os

from js3 import scorer
from js3.js2 import persona as persona_mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA = persona_mod.load(os.path.join(BASE, "persona", "aarav-patel.example.json"))
FILLER = (" We build software for restaurants and care about craft, testing and fast feedback. "
          "You will work with product managers and designers on a team of eight engineers. ") * 3


def cfg(version=None):
    if version is None:
        return scorer.load_filter()
    return scorer.load_filter(os.path.join(BASE, "filter", f"filter-v{version}.json"))


def posting(title="Software Engineer", location="Boston, MA", body="", offices=(), html=None, pid="1"):
    content = body + FILLER
    return {"id": pid, "source": "test:fixture", "company": "Fixture", "title": title,
            "location": {"name": location}, "offices": [{"location": o} for o in offices],
            "content": content, "html": html if html is not None else content, "absolute_url": ""}


def persona():
    return copy.deepcopy(PERSONA)
