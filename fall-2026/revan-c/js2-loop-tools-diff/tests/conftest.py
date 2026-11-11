"""Shared fixtures. Postings here are CONSTRUCTED test fixtures, not board results."""
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESUME_PATH = ROOT / "resumes" / "aarav-patel.json"


@pytest.fixture
def resume():
    return json.loads(RESUME_PATH.read_text())


@pytest.fixture
def resume_path():
    return RESUME_PATH


def make_posting(pid, title, location, content):
    # Greenhouse returns `content` as HTML that is itself entity-escaped.
    escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return {"id": pid, "title": title, "location": {"name": location}, "content": escaped}


RELEVANT = make_posting(
    1001,
    "Software Engineer - Platform Tools",
    "Boston, MA",
    "<p>You will build services in <b>TypeScript</b> and run them on Kubernetes.</p>",
)
IRRELEVANT = make_posting(
    1002,
    "Enterprise Account Executive",
    "London, UK",
    "<p>Own a book of enterprise accounts. Salesforce experience preferred.</p>",
)


def board_response(*postings):
    return {"jobs": list(postings), "meta": {"total": len(postings)}}


def write_board(path, *postings):
    path.write_text(json.dumps(board_response(*postings)))
    return path
