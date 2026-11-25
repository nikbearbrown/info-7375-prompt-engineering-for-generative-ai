import json
import socket
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

PERSONA_PATH = PROJECT / "persona_arjun_mehta.json"
POSTINGS_PATH = Path(__file__).resolve().parent / "fixtures" / "postings.json"


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Any DNS lookup or socket connection fails the test."""
    def blocked(*args, **kwargs):
        raise RuntimeError("network access attempted in a test")

    monkeypatch.setattr(socket, "getaddrinfo", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.fixture
def postings():
    """Fake Greenhouse postings, keyed by case name."""
    return json.loads(POSTINGS_PATH.read_text())


@pytest.fixture
def resume():
    """The persona read directly, so rule tests do not depend on load_resume."""
    return json.loads(PERSONA_PATH.read_text())
