"""audit/audit_v01.py reads the BLIND labels, so rerunning it reproduces the committed
audit/AUDIT-RESULTS.md (the blind reject audit of filter v0.1), even after the post-unblinding
corrections on rows 19, 29, 40 and 45. It needs nothing under the git-ignored out/ folder.
"""

import contextlib
import importlib.util
import io
import re

import pytest

from agent import PROJECT_DIR

AUDIT_DIR = PROJECT_DIR / "audit"
COMMITTED = (AUDIT_DIR / "AUDIT-RESULTS.md").read_text(encoding="utf-8")


def _load_script():
    spec = importlib.util.spec_from_file_location("audit_v01", AUDIT_DIR / "audit_v01.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def script():
    return _load_script()


@pytest.fixture(scope="module")
def output(script):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert script.main() == 0
    return buf.getvalue()


def _section(text, start, end):
    return text[text.index(start):text.index(end)].strip()


def test_per_row_table_is_reproduced_verbatim(output):
    table = _section(output, "## a. Per-row table", "## b. Confusion matrices")
    assert table.count("\n| ") == 49  # header row + 48 rows (the separator line starts with "|---")
    assert table in COMMITTED


def test_confusion_matrices_are_reproduced_verbatim(output):
    matrices = _section(output, "## b. Confusion matrices", "## c. Random rejects")
    assert "### Overall (48 rows, 28 agree)" in matrices
    assert matrices in COMMITTED


def test_false_friend_table_is_reproduced_verbatim(output):
    table = _section(output, "| word | v0.1 term? |", "boilerplate 'Stripe'")
    assert table in COMMITTED


def test_random_reject_miss_numbers_match_the_committed_report(output):
    line = next(ln for ln in output.splitlines() if ln.startswith("not reject (keep or cannot_tell)"))
    m = re.search(r"(\d+)/30 = .*?Wilson 95% \[([\d.]+%), ([\d.]+%)\] ≈ (\d+)–(\d+) of 951", line)
    k, lo, hi, n_lo, n_hi = m.groups()
    assert (k, lo, hi) == ("6", "9.5%", "37.3%")
    assert f"| keep or cannot_tell (not reject) | {k}/30 | 20.0% | {lo} – {hi} | about {n_lo} – {n_hi} |" in COMMITTED


def test_corrected_rows_report_their_blind_label(output):
    for row, title in (("19", "Account Executive, Product Sales - Link"), ("29", "Backend Engineer, Payments Experiences"),
                       ("40", "Software Engineer, Intern (Summer)"), ("45", "AI Engineer")):
        line = next(ln for ln in output.splitlines() if ln.startswith(f"| {row} | "))
        assert title in line and line.endswith("| keep |  | **disagree** |")


def test_blind_row_restores_verdict_and_note(script):
    corrected = {"my_verdict": "reject", "labeled_at": "2026-11-23T20:24:41-05:00",
                 "note": "[corrected 2026-11-23: was keep (labeled 2026-11-23T18:58:39-05:00), old note: k] post-unblinding"}
    assert script.blind_row(corrected) == {"my_verdict": "keep", "labeled_at": "2026-11-23T18:58:39-05:00",
                                           "note": "k"}
    no_old_note = dict(corrected, note="[corrected 2026-11-23: was cannot_tell (labeled T1)] why")
    assert script.blind_row(no_old_note)["my_verdict"] == "cannot_tell" and script.blind_row(no_old_note)["note"] == ""
    no_time = dict(corrected, note="[corrected 2026-11-23: was keep] why")   # row had no labeled_at
    assert script.blind_row(no_time)["my_verdict"] == "keep" and script.blind_row(no_time)["labeled_at"] == ""
    plain = {"my_verdict": "keep", "note": "fine", "labeled_at": "T"}
    assert script.blind_row(plain) == plain
