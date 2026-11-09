"""Each loop-level wrong version from GATE.md section 6 is caught (1-10, 13, 16).

Pattern: a scenario returns a list of broken expectations. Against the real code the list is
empty; with wrong version n applied it is not. That shows the expectation actually detects
that wrong version, rather than passing for any implementation. The permission-policy wrong
versions (11, 12, 14, 15) are in tests/test_boundaries.py, written after Ashwin's predictions.
"""
from __future__ import annotations

import unittest
from dataclasses import replace

from jobloop import loop
from tests.helpers import (FakeClock, FakeTransport, Project, ashby_body, gh_body, lever_body, ok,
                           state_for, status, timeout, url)
from wrong_versions import WRONG, applied

GH, AS, LV = "greenhouse", "ashby", "lever"
THREE = [(GH, "alpha", "watch"), (AS, "beta", "watch"), (LV, "gamma", "watch")]
SEEN = state_for({"greenhouse/alpha": [1], "ashby/beta": ["b1"], "lever/gamma": ["g1"]})


def happy():
    return {url(GH, "alpha"): [ok(gh_body([1]))], url(AS, "beta"): [ok(ashby_body(["b1"]))],
            url(LV, "gamma"): [ok(lever_body(["g1"]))]}


def execute(boards, script, state=None, **kw):
    clock = FakeClock()
    project = Project(boards, state)
    transport = FakeTransport(clock, script)
    before = project.state_bytes()
    try:
        report = loop.run(project.root, transport=transport, clock=clock, sleep=clock.sleep, wall=clock.wall, **kw)
        return report, transport, project.state_bytes() != before, clock
    finally:
        project.cleanup()


def board(report, name):
    return next(b for b in report["boards"] if f"{b['provider']}/{b['board']}" == name)


# ---- scenarios: each returns the list of expectations that were broken

def s_empty_board():
    report, *_ = execute(THREE, {**happy(), url(AS, "beta"): [ok(ashby_body([]))]}, SEEN)
    beta, broken = board(report, "ashby/beta"), []
    if report["run"]["status"] == loop.FINISHED:
        broken.append("empty board let the run finish")
    if beta["new"] == []:
        broken.append("empty board reported as 0 new ('no new jobs')")
    return broken


def s_404_is_failure():
    report, *_ = execute(THREE, {**happy(), url(AS, "beta"): [status(404)]}, SEEN)
    beta = board(report, "ashby/beta")
    return [] if beta["outcome"] == loop.FAILED and beta["postings_observed"] is None else [f"404 became {beta['outcome']}"]


def s_failure_visible_in_exit():
    boards = THREE + [(GH, "nope", "deliberate-failure")]
    report, *_ = execute(boards, {**happy(), url(GH, "nope"): [status(404)]}, SEEN)
    return [] if report["run"]["exit_code"] == 1 else [f"exit {report['run']['exit_code']} hides the failure"]


def s_404_not_retried():
    report, transport, *_ = execute([(GH, "alpha", "watch")], {url(GH, "alpha"): [status(404), status(404)]})
    broken = []
    if len(transport.calls) != 1:
        broken.append(f"404 requested {len(transport.calls)} times")
    if report["run"]["status"] != loop.INCOMPLETE:
        broken.append(f"status {report['run']['status']}")
    return broken


def s_failures_count():
    script = {url(GH, "alpha"): [timeout(1), timeout(1)], url(AS, "beta"): [ok(ashby_body(["b1"]))],
              url(LV, "gamma"): [ok(lever_body(["g1"]))]}
    report, transport, *_ = execute(THREE, script, SEEN, budget=replace(loop.CEILINGS, max_attempts=3))
    broken = []
    if len(transport.calls) > 3:
        broken.append(f"{len(transport.calls)} requests sent under a budget of 3")
    if report["run"]["attempts_used"] != len(transport.calls):
        broken.append("attempts_used does not match requests sent")
    return broken


def s_timeout_within_budget():
    script = {url(GH, "alpha"): [ok(gh_body([1]), elapsed=7.0)], url(AS, "beta"): [ok(ashby_body(["b1"]))]}
    _, transport, _, clock = execute(THREE[:2], script, budget=replace(loop.CEILINGS, max_seconds=8.0))
    return [] if all(t <= 8.0 - 7.0 + 1e-9 for _, t in transport.calls[1:]) else \
        [f"second request allowed {transport.calls[1][1]}s with 1s left"]


def s_unvisited_not_zero():
    script = {url(GH, "alpha"): [timeout(1), timeout(1)]}
    report, *_ = execute(THREE, script, SEEN, budget=replace(loop.CEILINGS, max_attempts=2))
    gamma = board(report, "lever/gamma")
    return [] if gamma["outcome"] == loop.NOT_OBSERVED and gamma["new"] is None else \
        [f"unvisited board reported as {gamma['outcome']} with new={gamma['new']}"]


def s_duplicates_before_network():
    report, transport, *_ = execute([(GH, "alpha", "watch"), (GH, "alpha", "watch")],
                                    {url(GH, "alpha"): [ok(gh_body([1])), ok(gh_body([1]))]})
    return [] if transport.calls == [] and report["run"]["status"] == loop.ERROR else \
        [f"{len(transport.calls)} request(s) sent for a duplicate config"]


def s_incomplete_keeps_state():
    report, _, changed, _ = execute(THREE, {**happy(), url(LV, "gamma"): [status(404)]}, SEEN,
                                    approve_state_write=True)
    broken = []
    if changed:
        broken.append("state changed after an incomplete run")
    if report["run"]["status"] != loop.INCOMPLETE:
        broken.append(f"status {report['run']['status']} instead of incomplete")
    return broken


def s_ids_scoped_by_board():
    boards = [(GH, "alpha", "watch"), (GH, "other", "watch")]
    state = state_for({"greenhouse/alpha": [7], "greenhouse/other": [8]})
    report, *_ = execute(boards, {url(GH, "alpha"): [ok(gh_body([7]))], url(GH, "other"): [ok(gh_body([7, 8]))]}, state)
    new = board(report, "greenhouse/other")["new"] or []
    return [] if [n["key"] for n in new] == ["greenhouse/other/7"] else [f"other's new ids: {new}"]


def s_redirect_not_followed():
    evil = "https://evil.example/jobs"
    script = {url(GH, "alpha"): [status(301, headers={"location": evil})], evil: [ok(gh_body([1]))]}
    report, transport, *_ = execute([(GH, "alpha", "watch")], script)
    return [] if [c[0] for c in transport.calls] == [url(GH, "alpha")] else ["redirect target was requested"]


def s_replay_labeled():
    report, *_ = execute(THREE, happy(), SEEN, replay="seeded/test")
    return [] if report["run"]["mode"] == loop.SEEDED else [f"replay labeled {report['run']['mode']}"]


SCENARIOS = {1: s_empty_board, 2: s_404_is_failure, 3: s_failure_visible_in_exit, 4: s_404_not_retried,
             5: s_failures_count, 6: s_timeout_within_budget, 7: s_unvisited_not_zero,
             8: s_duplicates_before_network, 9: s_incomplete_keeps_state, 10: s_ids_scoped_by_board,
             13: s_redirect_not_followed, 16: s_replay_labeled}


class TestWrongVersionsAreCaught(unittest.TestCase):
    def test_every_scenario_holds_for_the_real_code(self):
        for n, scenario in SCENARIOS.items():
            with self.subTest(wrong_version=n):
                self.assertEqual(scenario(), [])

    def test_each_wrong_version_breaks_its_scenario(self):
        for n, scenario in SCENARIOS.items():
            with self.subTest(wrong_version=n, gate=WRONG[n].gate_text):
                try:
                    with applied(n):
                        broken = scenario()
                except AssertionError as exc:      # e.g. the fake transport saw an unexpected request
                    broken = [f"crashed the scenario: {exc}"]
                self.assertNotEqual(broken, [], f"wrong version {n} was NOT caught")


if __name__ == "__main__":
    unittest.main()
