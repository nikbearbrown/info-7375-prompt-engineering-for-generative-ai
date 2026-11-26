"""Fixtures for the contract suite."""

from __future__ import annotations

import pytest

from tests.contract.impls import RuleImpl, load_impl


@pytest.fixture
def impl(rule_impl: str) -> RuleImpl:
    """The implementation selected with ``--rule-impl`` (default ``real``)."""
    return load_impl(rule_impl)
