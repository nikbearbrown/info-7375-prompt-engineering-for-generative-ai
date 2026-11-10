"""The loop: exits, budgets, repeat rule, error policy, and GATE.md section 7's wrong versions.
Every response is CONSTRUCTED (tests/fakes.py)."""
import json
import pathlib
import tempfile
import unittest

from jsagent import loop, persona, policy, providers
from tests import fakes, wrong_versions

GH = providers.board_url("greenhouse", "oscar")
GH2 = providers.board_url("greenhouse", "klaviyo")
AS = providers.board_url("ashby", "linear")
LV = providers.board_url("lever", "palantir")
LV_EMPTY = providers.board_url("lever", "whoop")
LV_BAD = providers.board_url("lever", "oscarhealth-doesnotexist")
B = {"oscar": {"name": "oscar", "ats": "greenhouse", "token": "oscar"},
     "klaviyo": {"name": "klaviyo", "ats": "greenhouse", "token": "klaviyo"},
     "linear": {"name": "linear", "ats": "ashby", "token": "linear"},
     "palantir": {"name": "palantir", "ats": "lever", "token": "palantir"},
     "whoop": {"name": "whoop", "ats": "lever", "token": "whoop"},
     "bad": {"name": "bad", "ats": "lever", "token": "oscarhealth-doesnotexist"}}
BUDGETS = {"max_boards": 6, "max_requests": 12, "max_seconds": 120}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(json.loads((pathlib.Path(__file__).parent.parent / "persona" / "alex_morgan.json").read_text()))
        self.n = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, names, routes, budgets=BUDGETS, clock=None):
        self.n += 1
        self.transport = fakes.FakeTransport(routes)
        return loop.run([B[n] for n in names], budgets, self.transport, policy.Files(self.project, self.runs),
                        run_id=f"run{self.n}", resume=self.view, clock=clock or fakes.FakeClock())

    def board(self, report, name):
        return next(b for b in report["boards"] if b["name"] == name)


class Exits(Base):
    def test_three_boards_two_systems_finished(self):
        routes = {GH: [fakes.gh(1, 2)], AS: [fakes.ashby("a")], LV: [fakes.lever("p")]}
        r1 = self.run_loop(["oscar", "linear", "palantir"], routes)
        self.assertEqual(r1["exit"], "finished")
        self.assertTrue(all(b["baseline"] and b["new"] == 0 for b in r1["boards"]))
        r2 = self.run_loop(["oscar", "linear", "palantir"], {GH: [fakes.gh(1, 2, 3)], AS: [fakes.ashby("a")], LV: [fakes.lever("p")]})
        self.assertEqual(r2["exit"], "finished")
        self.assertEqual(self.board(r2, "oscar")["new"], 1)
        self.assertEqual(self.board(r2, "linear")["new"], 0)
        self.assertEqual([j["posting_id"] for j in self.board(r2, "oscar")["new_postings"]], ["3"])
        self.assertIn(self.board(r2, "oscar")["new_postings"][0]["verdict"], ("Relevant", "Not Relevant"))

    def test_unknown_system_is_error_before_any_request(self):
        bad = dict(B["oscar"], ats="workday")
        self.transport = fakes.FakeTransport({})
        r = loop.run([bad], BUDGETS, self.transport, policy.Files(self.project, self.runs), run_id="x",
                     resume=self.view, clock=fakes.FakeClock())
        self.assertEqual(r["exit"], "error")
        self.assertEqual(self.transport.calls, [])


class WrongVersions(Base):
    def test_wv1_empty_board_is_not_zero_new(self):
        r = self.run_loop(["oscar", "whoop"], {GH: [fakes.gh(1)], LV_EMPTY: [(200, b"[]")]})
        w = self.board(r, "whoop")
        self.assertEqual(w["status"], "empty")
        self.assertIsNone(w["new"])
        self.assertTrue(w["needs_review"])
        self.assertEqual(r["exit"], "incomplete")
        self.assertEqual(wrong_versions.wv1_empty_is_ok([])["status"], "ok", "the wrong version would say ok")

    def test_wv2_failed_board_not_finished(self):
        r = self.run_loop(["oscar", "bad"], {GH: [fakes.gh(1)]})
        self.assertEqual(self.board(r, "bad")["status"], "failed")
        self.assertEqual(r["exit"], "incomplete")
        self.assertNotEqual(r["exit"], wrong_versions.wv2_exit_ignoring_failures(r["boards"]))

    def test_wv3_prefix_trick(self):
        # The policy side is tests/test_policy.py row 10; here the wrong check is shown accepting it.
        self.assertTrue(wrong_versions.wv3_prefix_inside(self.project / "runs-evil" / "x", self.runs))
        with self.assertRaises(policy.PolicyViolation):
            policy.Files(self.project, self.runs).write(self.project / "runs-evil" / "x", b"x")

    def test_wv4_404_is_not_retried(self):
        self.run_loop(["bad"], {})
        self.assertEqual(self.transport.calls.count(LV_BAD), 1)
        t = fakes.FakeTransport({})
        wrong_versions.wv4_retry_until_ok(t, LV_BAD)
        self.assertEqual(t.calls.count(LV_BAD), 5, "the wrong version keeps retrying")

    def test_wv5_no_counts_from_failed_response(self):
        r = self.run_loop(["oscar", "bad"], {GH: [fakes.gh(1, 2)]})
        bad = self.board(r, "bad")
        self.assertIsNone(bad["fetched"])
        self.assertIsNone(bad["new"])
        self.assertEqual(r["verified_postings"], 2)
        self.assertIsNotNone(wrong_versions.wv5_count_after_failure(404, b'{"ok": false, "error": "Document not found"}'))


class ErrorPolicy(Base):
    def test_timeout_retried_once_then_ok(self):
        r = self.run_loop(["oscar"], {GH: [TimeoutError("slow"), fakes.gh(1)]})
        self.assertEqual(self.board(r, "oscar")["status"], "ok")
        self.assertEqual(self.transport.calls.count(GH), 2)

    def test_5xx_twice_fails_after_one_retry(self):
        r = self.run_loop(["oscar", "linear"], {GH: [(503, b"busy"), (503, b"busy")], AS: [fakes.ashby("a")]})
        self.assertEqual(self.board(r, "oscar")["status"], "failed")
        self.assertEqual(self.transport.calls.count(GH), 2)
        self.assertEqual(self.board(r, "linear")["status"], "ok", "the loop continues after a failed board")
        self.assertEqual(r["exit"], "incomplete")

    def test_bad_json_not_retried(self):
        r = self.run_loop(["oscar"], {GH: [(200, b"<html>not json")]})
        b = self.board(r, "oscar")
        self.assertEqual((b["status"], b["error"]), ("failed", "bad-json"))
        self.assertEqual(self.transport.calls.count(GH), 1)

    def test_failed_board_keeps_its_state(self):
        self.run_loop(["oscar"], {GH: [fakes.gh(1, 2)]})
        self.run_loop(["oscar"], {GH: [(404, b"{}")]})
        r = self.run_loop(["oscar"], {GH: [fakes.gh(1, 2, 3)]})
        self.assertEqual(self.board(r, "oscar")["new"], 1)

    def test_empty_board_keeps_its_state(self):
        self.run_loop(["oscar"], {GH: [fakes.gh(1, 2)]})
        self.run_loop(["oscar"], {GH: [fakes.gh()]})
        r = self.run_loop(["oscar"], {GH: [fakes.gh(1, 2)]})
        self.assertEqual(self.board(r, "oscar")["new"], 0)


class RepeatAndBudgets(Base):
    def test_duplicate_board_skipped_and_recorded(self):
        r = self.run_loop(["oscar", "oscar"], {GH: [fakes.gh(1)]})
        self.assertEqual([b["status"] for b in r["boards"]], ["ok", "skipped-duplicate"])
        self.assertEqual(self.transport.calls.count(GH), 1)

    def test_board_budget(self):
        names = ["oscar", "klaviyo", "linear", "palantir", "whoop", "bad", "oscar"]
        B["oscar2"] = {"name": "oscar2", "ats": "greenhouse", "token": "oscar2"}
        names[-1] = "oscar2"
        r = self.run_loop(names, {GH: [fakes.gh(1)], GH2: [fakes.gh(2)], AS: [fakes.ashby("a")],
                                  LV: [fakes.lever("p")], LV_EMPTY: [(200, b"[]")]})
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertEqual(self.board(r, "oscar2")["status"], "skipped-budget")
        self.assertLessEqual(len(self.transport.calls), 6)

    def test_request_budget_counts_retries(self):
        r = self.run_loop(["oscar", "linear", "palantir"], {GH: [TimeoutError("x"), fakes.gh(1)], AS: [fakes.ashby("a")],
                                                           LV: [fakes.lever("p")]},
                          budgets=dict(BUDGETS, max_requests=2))
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertEqual(len(self.transport.calls), 2)
        self.assertEqual(self.board(r, "palantir")["status"], "skipped-budget")

    def test_time_budget(self):
        r = self.run_loop(["oscar", "linear", "palantir"], {GH: [fakes.gh(1)], AS: [fakes.ashby("a")], LV: [fakes.lever("p")]},
                          clock=fakes.FakeClock(step=50))
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertIn("skipped-budget", [b["status"] for b in r["boards"]])

    def test_budgets_cannot_exceed_gate(self):
        gate = self.project / "GATE.md"
        gate.write_text("| Date | Boards | Requests | Seconds | Decided by |\n|---|---|---|---|---|\n| 2026-11-09 | 6 | 12 | 120 | S |\n")
        bj = self.project / "budgets.json"
        bj.write_text(json.dumps({"max_boards": 6, "max_requests": 12, "max_seconds": 120}))
        self.assertEqual(loop.load_budgets(bj, gate)["max_requests"], 12)
        bj.write_text(json.dumps({"max_boards": 6, "max_requests": 50, "max_seconds": 120}))
        with self.assertRaises(ValueError):
            loop.load_budgets(bj, gate)


class Evidence(Base):
    def test_trace_and_raw_for_every_response(self):
        r = self.run_loop(["oscar", "bad", "whoop"], {GH: [fakes.gh(1)], LV_EMPTY: [(200, b"[]")]})
        run_dir = self.runs / "run1"
        events = [json.loads(l) for l in (run_dir / "trace.jsonl").read_text().splitlines()]
        reqs = [e for e in events if e["event"] == "response"]
        self.assertEqual(len(reqs), 3)
        for e in reqs:
            self.assertTrue((self.project / e["raw_file"]).exists())
        self.assertEqual([e["event"] for e in events][-1], "exit")
        self.assertTrue((run_dir / "summary.json").exists())
        self.assertTrue(list((self.runs / "state").glob("state-run1.json")))


if __name__ == "__main__":
    unittest.main()
