"""Mutation-style meta-test for CONTRACT §14: the contract suite kills A and B.

Each test runs ``tests/contract`` in a child pytest against one implementation and
reads the JUnit XML report. The real implementation must pass every test; each
wrong version must fail, and the tests that "kill" it are named and checked.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET  # noqa: S405 - parses our own child's report
from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.conftest import REPO_ROOT

pytestmark = pytest.mark.subprocess

MIN_CONTRACT_TESTS = 10


@dataclass(frozen=True)
class SuiteResult:
    """Outcome of one child run of the contract suite."""

    returncode: int
    passed: frozenset[str]
    failed: frozenset[str]

    @property
    def failed_bases(self) -> frozenset[str]:
        """Failed test names without their parametrisation suffix."""
        return frozenset(name.split("[", 1)[0] for name in self.failed)


def _run_contract_suite(impl: str, tmp_path: Path) -> SuiteResult:
    report = tmp_path / f"contract-{impl}.xml"
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/contract",
            f"--rule-impl={impl}",
            "-p",
            "no:cacheprovider",
            "-q",
            f"--junitxml={report}",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    root = ET.parse(report).getroot()  # noqa: S314 - our own child's report
    passed: set[str] = set()
    failed: set[str] = set()
    for case in root.iter("testcase"):
        name = case.attrib["name"]
        if case.find("failure") is not None or case.find("error") is not None:
            failed.add(name)
        elif case.find("skipped") is None:
            passed.add(name)
    print(f"[{impl}] exit={completed.returncode} killed by: {sorted(failed)}")
    return SuiteResult(completed.returncode, frozenset(passed), frozenset(failed))


def test_contract_suite_passes_on_real_impl(tmp_path: Path) -> None:
    result = _run_contract_suite("real", tmp_path)
    assert result.returncode == 0
    assert result.failed == frozenset()
    assert len(result.passed) >= MIN_CONTRACT_TESTS


def test_contract_suite_fails_on_wrong_a(tmp_path: Path) -> None:
    """A (title-only) is killed by the skill, location and exclusion cases."""
    result = _run_contract_suite("wrong_a", tmp_path)
    assert result.returncode == 1
    assert result.failed_bases >= {
        "test_contract_case4_one_skill_is_no_match",
        "test_contract_case2_non_us_is_no_match",
        "test_contract_na_location_is_no_match",
        "test_contract_zero_skill_eligible_title_is_no_match",
        "test_contract_exclusion_phrase_is_no_match",
    }


def test_contract_suite_fails_on_wrong_b(tmp_path: Path) -> None:
    """B (substring counting) is killed by C#, REST, repeats and the validator."""
    result = _run_contract_suite("wrong_b", tmp_path)
    assert result.returncode == 1
    assert result.failed_bases >= {
        "test_contract_csharp_vs_plain_c",
        "test_contract_rest_of_the_team_not_rest",
        "test_contract_repeated_mentions_count_once",
        "test_contract_missing_evidence_path_rejected",
        "test_contract_wrong_resume_path_rejected",
    }
