"""Shared helpers for the table tests. Offline only: no test touches the network."""

import json
import sys
from pathlib import Path

JS1 = Path(__file__).resolve().parents[1]
EXPECTED = JS1 / "tests" / "expected"

if str(JS1) not in sys.path:
    sys.path.insert(0, str(JS1))

from agent.persona import load_persona  # noqa: E402


def load_table(name):
    return json.loads((EXPECTED / name).read_text(encoding="utf-8"))


def persona():
    """The §1 final persona, from the resume_persona.json the agent itself reads."""
    return load_persona(JS1 / "resume_persona.json")


def table_posting(row):
    """A board posting built from a table row.

    The tables write location.name as "location". A row without "content"
    builds a posting with no content field at all (rule case R11).
    """
    posting = {"posting_id": row.get("id", "T"), "title": row["title"], "location": {"name": row["location"]}}
    if "content" in row:
        posting["content"] = row["content"]
    return posting
