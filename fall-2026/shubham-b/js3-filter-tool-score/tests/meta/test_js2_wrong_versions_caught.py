"""Mutation-style meta-test for GATE §8: ``tests/watch`` kills W1-W9.

Each case runs ``tests/watch`` in a child pytest with ``JSA_JS2_WRONG`` set, reads the
JUnit XML report and checks that the named tests are among the ones that fail.
"""

from __future__ import annotations

import os
import subprocess
import sys
import xml.etree.ElementTree as ET  # noqa: S405 - parses our own child's report
from pathlib import Path

import pytest

from tests.conftest import REPO_ROOT
from tests.wrong_versions.js2 import WRONG_VERSIONS

pytestmark = pytest.mark.subprocess

KILLED_BY: dict[str, set[str]] = {
    "W1": {"test_bad_board_name_is_not_retried_and_loop_is_incomplete"},
    "W2": {"test_empty_board_is_failed_not_no_new_jobs"},
    "W3": {"test_4xx_is_never_retried"},
    "W4": {"test_request_budget_stops_before_the_next_board"},
    "W5": {"test_b10_prefix_trick_sibling"},
    "W6": {"test_b11_symlink_pointing_out"},
    "W7": {"test_b04_allowed_name_as_prefix_or_substring"},
    "W8": {"test_same_board_in_other_case_is_fetched_once"},
    "W9": {"test_b17_no_terminal_means_no"},
}


def _failed_tests(wrong: str | None, tmp_path: Path) -> tuple[int, set[str]]:
    report = tmp_path / f"watch-{wrong or 'real'}.xml"
    env = {k: v for k, v in os.environ.items() if k != "JSA_JS2_WRONG"}
    if wrong is not None:
        env["JSA_JS2_WRONG"] = wrong
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/watch",
            "-p",
            "no:cacheprovider",
            "-q",
            f"--junitxml={report}",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    root = ET.parse(report).getroot()  # noqa: S314 - our own child's report
    failed = {
        case.attrib["name"].split("[", 1)[0]
        for case in root.iter("testcase")
        if case.find("failure") is not None or case.find("error") is not None
    }
    print(f"[{wrong}] exit={completed.returncode} killed by: {sorted(failed)}")
    return completed.returncode, failed


def test_every_wrong_version_has_a_named_killer() -> None:
    assert set(KILLED_BY) == set(WRONG_VERSIONS)


def test_watch_suite_passes_on_the_real_code(tmp_path: Path) -> None:
    assert _failed_tests(None, tmp_path) == (0, set())


@pytest.mark.parametrize("wrong", sorted(KILLED_BY))
def test_watch_suite_kills_wrong_version(wrong: str, tmp_path: Path) -> None:
    returncode, failed = _failed_tests(wrong, tmp_path)
    assert returncode != 0
    assert KILLED_BY[wrong] <= failed
