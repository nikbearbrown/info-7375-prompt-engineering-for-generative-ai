"""Docs that the contract requires stay true to the code (CONTRACT §11, §17)."""

from __future__ import annotations

import re

from tests.conftest import REPO_ROOT


def test_traceability_doc_names_existing_tests() -> None:
    doc = (REPO_ROOT / "docs/TRACEABILITY.md").read_text("utf-8")
    defined = {
        m
        for path in (REPO_ROOT / "tests").rglob("test_*.py")
        for m in re.findall(r"^def (test_\w+)", path.read_text("utf-8"), re.M)
    }
    named = set(re.findall(r"`(test_\w+)`", doc))
    assert named, "no test names found in docs/TRACEABILITY.md"
    assert sorted(named - defined) == []
    files = re.findall(r"`(tests/[\w/]+\.py)`", doc)
    assert [f for f in files if not (REPO_ROOT / f).exists()] == []


def test_network_doc_names_the_cli_limitation() -> None:
    doc = (REPO_ROOT / "docs/NETWORK.md").read_text("utf-8")
    assert "boards-api.greenhouse.io" in doc
    assert "cannot enforce which hosts" in doc
