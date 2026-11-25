"""Cases 1-5 and 16 (Watch). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. All postings are constructed."""
import json
from datetime import timedelta

from conftest import BOARD_URL, FIXED_NOW, FakeOpener, board_body, job, latest_report, run_args, run_cli

A = [job(201, "Machine Learning Engineer"), job(202, "Account Executive"), job(203, "Data Scientist")]
X = "202"  # the id B drops
B = [j for j in A if str(j["id"]) != X] + [job(204, "AI Engineer"), job(205, "Recruiter")]


def _run(workdir, jobs, minute):
    opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {"Content-Type": "application/json"})})
    assert run_cli(run_args(), opener=opener, now=FIXED_NOW + timedelta(minutes=minute)) == 0
    return latest_report(workdir)


def _new_ids(report):
    return [r["posting_id"] for r in report["records"]]


def _seen_ids(workdir):
    return json.loads((workdir / "state" / "acme.json").read_text(encoding="utf-8"))["seen_ids"]


def test_ac01_baseline_reports_nothing_new_and_remembers_every_id(workdir):
    report = _run(workdir, A, 0)
    assert report["label"] == "baseline"
    assert report["counts"]["new"] == 0
    assert report["records"] == []
    assert _seen_ids(workdir) == ["201", "202", "203"]


def test_ac02_second_run_reports_exactly_the_added_ids(workdir):
    _run(workdir, A, 0)
    report = _run(workdir, B, 1)
    assert sorted(_new_ids(report)) == ["204", "205"]
    assert report["counts"]["new"] == 2
    assert X not in _new_ids(report)


def test_ac03_same_response_again_reports_nothing_new(workdir):
    _run(workdir, A, 0)
    _run(workdir, B, 1)
    report = _run(workdir, B, 2)
    assert report["counts"]["new"] == 0
    assert report["records"] == []


def test_ac16_returning_id_is_not_new(workdir):
    _run(workdir, A, 0)
    _run(workdir, B, 1)
    assert X in _seen_ids(workdir)
    report = _run(workdir, A, 2)
    assert X not in _new_ids(report)
    assert report["counts"]["new"] == 0


def test_ac04_duplicate_id_in_one_response_is_reported_once(workdir):
    _run(workdir, [], 0)
    report = _run(workdir, [job(301, "AI Engineer"), job(301, "Recruiter"), job(302, "Data Scientist")], 1)
    assert _new_ids(report) == ["301", "302"]
    assert report["duplicates_dropped"] == 1
    assert report["records"][0]["title"] == "AI Engineer"  # first occurrence kept


def test_ac05_integer_and_string_id_are_the_same_posting_in_one_response(workdir):
    _run(workdir, [], 0)
    report = _run(workdir, [job(123, "AI Engineer"), job("123", "AI Engineer")], 1)
    assert _new_ids(report) == ["123"]
    assert report["duplicates_dropped"] == 1


def test_ac05_integer_and_string_id_are_the_same_posting_across_runs(workdir):
    _run(workdir, [job(123, "AI Engineer")], 0)
    report = _run(workdir, [job("123", "AI Engineer")], 1)
    assert report["counts"]["new"] == 0
    assert _seen_ids(workdir) == ["123"]
