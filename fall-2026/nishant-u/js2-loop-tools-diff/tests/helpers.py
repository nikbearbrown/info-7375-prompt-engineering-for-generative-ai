"""Shared test data and a base class that imports the agent lazily.

The agent modules are imported in setUp, not at module level, so that before the
implementation exists each test reports its own failure instead of one import
error per file.
"""
import importlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resume():
    return load_json(ROOT / "data" / "resume.example.json")


def requirements():
    return load_json(ROOT / "data" / "requirements.json")


def postings():
    return load_json(FIXTURES / "postings.json")


def posting(posting_id):
    return next(p for p in postings() if p["id"] == posting_id)


def write_board(path, jobs):
    """Write a Greenhouse-shaped board response built from constructed postings."""
    body = {"jobs": jobs, "meta": {"total": len(jobs)}}
    Path(path).write_text(json.dumps(body), encoding="utf-8")
    return Path(path)


class ContractTest(unittest.TestCase):
    modules = ()

    def setUp(self):
        for name in self.modules:
            setattr(self, name.rsplit(".", 1)[-1], importlib.import_module(name))
