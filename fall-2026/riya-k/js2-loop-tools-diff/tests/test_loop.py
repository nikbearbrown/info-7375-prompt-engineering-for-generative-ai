"""Loop tests: exits, budgets, repeat rule, error policy, and GATE.md wrong versions 1-5.
All boards here are FAKE transports (scripted responses), not real board data. Offline; no sleeping (fake clock).
Run: python3 -m unittest tests.test_loop -v
"""

import json
import tempfile
import unittest
from pathlib import Path

from jsagent import loop
from jsagent.loop import Session, Transient
from jsagent.policy import Policy, PolicyError

ROOT = Path(__file__).resolve().parent.parent


def gh(*ids, title="AI Engineer"):
    return json.dumps({"jobs": [{"id": i, "title": title, "content": "Python SQL MLflow",
                                 "location": {"name": "Boston, MA"}, "absolute_url": f"https://x/{i}"}
                                for i in ids]}).encode()


def ashby(*ids):
    return json.dumps({"jobs": [{"id": f"u{i}", "title": "Data Engineer", "location": "New York, New York",
                                 "descriptionHtml": "Python and SQL", "jobUrl": f"https://y/{i}"}
                                for i in ids]}).encode()


SR_EMPTY = b'{"offset":0,"limit":100,"totalFound":0,"content":[]}'


class Clock:
    """Fake clock: each request costs `per_request` seconds; sleep() advances it."""
    def __init__(self, per_request=0.5):
        self.t, self.per = 0.0, per_request

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


class Script:
    """Fake transport. responses: url-substring -> list of (status, body) or Transient, used in order."""
    def __init__(self, clock, responses):
        self.clock, self.responses, self.calls = clock, {k: list(v) for k, v in responses.items()}, []

    def __call__(self, url, timeout):
        self.calls.append(url)
        self.clock.t += self.clock.per
        for k, seq in self.responses.items():
            if k in url:
                r = seq.pop(0) if len(seq) > 1 else seq[0]
                if isinstance(r, Exception):
                    raise r
                return r
        raise AssertionError(f"unexpected URL {url}")


def config(d, boards, cross=None):
    p = Path(d) / "cfg.json"
    p.write_text(json.dumps({"persona": "persona/arya-sahni.json", "boards": boards, "cross_check": cross or {}}))
    return p


B = lambda system, board: {"system": system, "board": board}
GOOD3 = [B("greenhouse", "alpha"), B("greenhouse", "beta"), B("ashby", "gamma")]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.out = self.d / "runs"

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, boards, responses, per_request=0.5, **kw):
        clock = Clock(per_request)
        script = Script(clock, responses)
        rep = loop.run(config(self.d, boards, kw.pop("cross", None)), self.out, get=script, clock=clock,
                       sleep=clock.sleep, extra_read_roots=[self.d], **kw)
        return rep, script

    def by(self, rep):
        return {b["board"]: b for b in rep["boards"]}


class TestExits(Base):
    def test_all_good_boards_finish(self):
        rep, _ = self.run_loop(GOOD3, {"alpha": [(200, gh(1, 2))], "beta": [(200, gh(3))], "gamma": [(200, ashby(4))]})
        self.assertEqual(rep["exit"], "finished")
        self.assertTrue(all(b["baseline"] for b in rep["boards"]))

    def test_second_run_reports_only_new_by_id_across_two_systems(self):
        self.run_loop(GOOD3, {"alpha": [(200, gh(1, 2))], "beta": [(200, gh(3))], "gamma": [(200, ashby(4))]})
        rep, _ = self.run_loop(GOOD3, {"alpha": [(200, gh(1, 2, 9))], "beta": [(200, gh(3))],
                                       "gamma": [(200, ashby(4, 5))]}, label="second")
        b = self.by(rep)
        self.assertEqual([v["id"] for v in b["greenhouse:alpha"]["new_postings"]], ["9"])
        self.assertEqual(b["greenhouse:beta"]["new"], 0)
        self.assertEqual([v["id"] for v in b["ashby:gamma"]["new_postings"]], ["u5"])

    def test_wrong_version_2_failed_board_is_null_not_zero(self):
        rep, script = self.run_loop(GOOD3 + [B("ashby", "notarealco-js2")],
                                    {"alpha": [(200, gh(1))], "beta": [(200, gh(2))], "gamma": [(200, ashby(3))],
                                     "notarealco": [(404, b"Not Found")]})
        bad = self.by(rep)["ashby:notarealco-js2"]
        self.assertIsNone(bad["postings"])
        self.assertNotIn("new", bad)
        self.assertEqual(bad["status"], "failed")
        self.assertIn("404", bad["reason"])
        self.assertEqual(rep["exit"], "incomplete")  # wrong version 3: never "finished" with a failed board
        self.assertEqual([e["board"] for e in rep["escalations"]], ["ashby:notarealco-js2"])

    def test_wrong_version_1_empty_board_is_flagged_not_success(self):
        rep, _ = self.run_loop([B("greenhouse", "alpha"), B("smartrecruiters", "hubspot")],
                               {"alpha": [(200, gh(1))], "hubspot": [(200, SR_EMPTY)]})
        hub = self.by(rep)["smartrecruiters:hubspot"]
        self.assertEqual(hub["status"], "suspect_empty")
        self.assertEqual(rep["exit"], "incomplete")
        self.assertFalse((self.out / "state" / "smartrecruiters-hubspot.json").exists())  # empty never baselined

    def test_naive_mode_is_the_finished_wrong_answer(self):
        """Demonstration mode (--no-empty-guard) reproduces wrong version 1: it says finished. Kept to prove the guard matters."""
        rep, _ = self.run_loop([B("smartrecruiters", "hubspot")], {"hubspot": [(200, SR_EMPTY)]}, empty_guard=False)
        self.assertEqual(rep["exit"], "finished")
        self.assertEqual(self.by(rep)["smartrecruiters:hubspot"]["postings"], 0)

    def test_bad_body_is_failed_not_retried(self):
        rep, script = self.run_loop([B("greenhouse", "alpha")], {"alpha": [(200, b"<html>maintenance</html>")]})
        self.assertEqual(self.by(rep)["greenhouse:alpha"]["status"], "failed")
        self.assertEqual(len(script.calls), 1)

    def test_config_outside_read_roots_is_refused(self):
        clock = Clock()
        rep = loop.run(config(self.d, GOOD3), self.out, get=Script(clock, {}), clock=clock, sleep=clock.sleep)
        self.assertEqual(rep["exit"], "error")
        self.assertIn("outside every read root", rep["stop_reason"])

    def test_bad_config_is_error_exit(self):
        rep, _ = self.run_loop([B("lever", "x")], {})
        self.assertEqual(rep["exit"], "error")

    def test_config_cannot_raise_budget(self):
        p = Path(self.d) / "cfg.json"
        p.write_text(json.dumps({"boards": GOOD3, "budget": {"requests": 999}}))
        rep = loop.run(p, self.out, get=Script(Clock(), {}), clock=Clock(), sleep=lambda s: None,
                       extra_read_roots=[self.d])
        self.assertEqual(rep["exit"], "error")
        self.assertIn("budgets live in GATE.md", rep["stop_reason"])


class TestErrorPolicy(Base):
    def test_wrong_version_4_404_is_never_retried(self):
        rep, script = self.run_loop([B("ashby", "bad")], {"bad": [(404, b"Not Found")]})
        self.assertEqual(len(script.calls), 1)
        self.assertEqual(self.by(rep)["ashby:bad"]["attempts"], 1)

    def test_timeout_retried_once_after_wait_then_succeeds(self):
        clock = Clock()
        script = Script(clock, {"alpha": [Transient("timed out"), (200, gh(1))]})
        rep = loop.run(config(self.d, [B("greenhouse", "alpha")]), self.out, get=script, clock=clock, sleep=clock.sleep,
                       extra_read_roots=[self.d])
        self.assertEqual(len(script.calls), 2)
        self.assertEqual(rep["exit"], "finished")
        waits = [e for e in self._trace(rep) if e["kind"] == "retry_wait"]
        self.assertEqual([w["seconds"] for w in waits], [loop.RETRY_WAIT])
        self.assertGreaterEqual(clock.t, loop.RETRY_WAIT + 2 * clock.per)  # the wait really happened

    def test_5xx_retried_at_most_once(self):
        rep, script = self.run_loop([B("greenhouse", "alpha")], {"alpha": [(503, b"busy"), (503, b"busy"), (200, gh(1))]})
        self.assertEqual(len(script.calls), 2)  # never a third try
        self.assertEqual(self.by(rep)["greenhouse:alpha"]["status"], "failed")
        self.assertEqual(rep["exit"], "incomplete")

    def test_one_failure_does_not_stop_other_boards(self):
        rep, script = self.run_loop([B("ashby", "bad")] + GOOD3, {"bad": [(404, b"x")], "alpha": [(200, gh(1))],
                                                                   "beta": [(200, gh(2))], "gamma": [(200, ashby(3))]})
        self.assertEqual(len(rep["boards"]), 4)

    def _trace(self, rep):
        return [json.loads(l) for l in (self.out / "trace" / f"{rep['run_id']}.jsonl").read_text().splitlines()]


class TestBudgetsAndRepeats(Base):
    def test_wrong_version_5_never_an_11th_request(self):
        boards = [B("greenhouse", f"b{i}") for i in range(6)]
        rep, script = self.run_loop(boards, {f"b{i}": [Transient("down")] for i in range(6)})
        self.assertLessEqual(len(script.calls), loop.MAX_REQUESTS)
        self.assertEqual(len(script.calls), 10)
        self.assertEqual(rep["exit"], "budget_exhausted")  # wrong version 3: not "finished", not "incomplete"
        self.assertTrue(rep["never_ran"])

    def test_seventh_board_never_runs(self):
        boards = [B("greenhouse", f"b{i}") for i in range(7)]
        rep, script = self.run_loop(boards, {f"b{i}": [(200, gh(i + 1))] for i in range(7)})
        self.assertEqual(rep["exit"], "budget_exhausted")
        self.assertEqual(rep["never_ran"], ["greenhouse:b6"])
        self.assertFalse(any("b6" in c for c in script.calls))

    def test_time_budget_stops_before_next_board(self):
        rep, script = self.run_loop(GOOD3, {"alpha": [(200, gh(1))], "beta": [(200, gh(2))], "gamma": [(200, ashby(3))]},
                                    per_request=31)
        self.assertEqual(rep["exit"], "budget_exhausted")
        self.assertEqual(len(script.calls), 2)
        self.assertEqual(rep["never_ran"], ["ashby:gamma"])

    def test_retry_not_started_if_wait_would_break_time_budget(self):
        rep, script = self.run_loop([B("greenhouse", "alpha")], {"alpha": [Transient("slow"), (200, gh(1))]},
                                    per_request=58.5)
        self.assertEqual(len(script.calls), 1)
        self.assertEqual(rep["exit"], "budget_exhausted")

    def test_repeat_rule_blocks_second_identical_request(self):
        s = Session(Policy(self.out, [ROOT]), Script(Clock(), {"alpha": [(200, gh(1))]}), clock=Clock())
        url = "https://boards-api.greenhouse.io/v1/boards/alpha/jobs?content=true"
        s.request(url)
        with self.assertRaises(PolicyError):
            s.request(url)
        self.assertEqual(s.trace[-1]["kind"], "repeat_blocked")
        s.request(url, retry=True)  # the one allowed repeat
        with self.assertRaises(PolicyError):
            s.request(url, retry=True)  # a second retry is a repeat
        self.assertEqual(s.requests, 2)

    def test_duplicate_board_in_config_read_once(self):
        rep, script = self.run_loop([B("greenhouse", "alpha"), B("greenhouse", "alpha")], {"alpha": [(200, gh(1))]})
        self.assertEqual(len(script.calls), 1)
        self.assertEqual(rep["duplicates_skipped"], ["greenhouse:alpha"])


class TestResetNeedsApproval(Base):
    def test_reset_refused_without_approve_then_allowed_with_it(self):
        self.run_loop([B("greenhouse", "alpha")], {"alpha": [(200, gh(1, 2))]})
        path = self.out / "state" / "greenhouse-alpha.json"
        before = path.read_bytes()
        with self.assertRaises(PolicyError):
            loop.reset(self.out, "greenhouse:alpha", approve=False)
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("removed 2 ids", loop.reset(self.out, "greenhouse:alpha", approve=True))


if __name__ == "__main__":
    unittest.main()
