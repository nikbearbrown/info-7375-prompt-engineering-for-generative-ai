"""The loop: exits, budgets, repeat rule, error policy, trace. All offline (FakeNet), constructed fixtures."""
import json
import os
import unittest

from agent import loop, persona
from tests.helpers import BUDGETS, FakeClock, FakeNet, TempBase, err, fixture_bytes, ok, rd, wr

GH2 = fixture_bytes("greenhouse-2.json")
GH3 = fixture_bytes("greenhouse-3.json")
AS2 = fixture_bytes("ashby-2.json")
LV2 = fixture_bytes("lever-2.json")
NOT_FOUND = ok(b'{"status":404,"error":"Job not found"}', 404)

B_GH = {"ats": "greenhouse", "slug": "alpha"}
B_AS = {"ats": "ashby", "slug": "beta"}
B_LV = {"ats": "lever", "slug": "gamma"}
B_BAD = {"ats": "greenhouse", "slug": "alphaa"}


def run(tb, boards, script, budgets=None, label=None, clock=None):
    clock = clock or FakeClock()
    net = FakeNet(script)
    r = loop.Run(tb.dir, tb.path("runs"), dict(BUDGETS, **(budgets or {})), boards,
                 persona.load(tb.path("persona", "aarav-patel.example.json")), label=label,
                 get=net, clock=clock, sleep=clock.sleep)
    return r.execute(), net, clock, r


def by_key(result):
    return {b["key"]: b for b in result["boards"]}


def trace(r):
    with open(r.trace_path) as f:
        return [json.loads(l) for l in f]


GOOD = {"/boards/alpha/": [ok(GH2)], "job-board/beta": [ok(AS2)], "postings/gamma": [ok(LV2)]}


class Exits(unittest.TestCase):
    def test_three_boards_two_plus_systems_finished(self):
        with TempBase() as tb:
            res, net, _, _ = run(tb, [B_GH, B_AS, B_LV], GOOD)
            self.assertEqual(res["exit"]["status"], "finished")
            self.assertEqual(res["exit"]["code"], 0)
            self.assertEqual(len({b["ats"] for b in res["boards"]}), 3)
            self.assertEqual(len(net.calls), 3)

    def test_404_board_makes_run_incomplete(self):  # W3
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_GH, B_AS, B_BAD], dict(GOOD, **{"/boards/alphaa/": [NOT_FOUND]}))
            self.assertEqual(res["exit"]["status"], "incomplete")
            self.assertNotEqual(res["exit"]["code"], 0)
            self.assertIn("greenhouse:alphaa", res["exit"]["why"])

    def test_failed_board_has_null_not_zero(self):  # W2
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_GH, B_BAD], dict(GOOD, **{"/boards/alphaa/": [NOT_FOUND]}))
            bad = by_key(res)["greenhouse:alphaa"]
            self.assertEqual(bad["status"], "error")
            self.assertIsNone(bad["postings"])
            self.assertIsNone(bad["new"])
            md = rd(os.path.join(tb.path("runs"), res["run_id"], "report.md"))
            self.assertIn("| `greenhouse:alphaa` | error | not_found | null | null |", md)

    def test_every_board_failed_is_error_and_escalates(self):
        with TempBase() as tb:
            res, _, _, _ = run(tb, [B_BAD], {"/boards/alphaa/": [NOT_FOUND]})
            self.assertEqual(res["exit"]["status"], "error")
            self.assertIn("ESCALATE", res["exit"]["why"])

    def test_budget_exhausted_lists_boards_not_attempted(self):
        with TempBase() as tb:
            res, net, _, _ = run(tb, [B_GH, B_AS, B_LV], GOOD, budgets={"max_requests": 2})
            self.assertEqual(res["exit"]["status"], "budget_exhausted")
            self.assertEqual(res["exit"]["code"], 4)
            self.assertEqual(by_key(res)["lever:gamma"]["status"], "not_attempted")
            self.assertEqual(len(net.calls), 2)

    def test_max_boards_budget(self):
        with TempBase() as tb:
            res, net, _, _ = run(tb, [B_GH, B_AS, B_LV], GOOD, budgets={"max_boards": 1})
            self.assertEqual(res["exit"]["status"], "budget_exhausted")
            self.assertEqual(len(net.calls), 1)

    def test_seconds_budget_stops_before_request(self):
        clock = FakeClock()

        class SlowNet(FakeNet):
            def __call__(s, url, timeout, max_bytes):
                clock.t += 50  # each request takes 50 s of a 90 s budget
                return FakeNet.__call__(s, url, timeout, max_bytes)

        with TempBase() as tb:
            net = SlowNet(GOOD)
            r = loop.Run(tb.dir, tb.path("runs"), dict(BUDGETS), [B_GH, B_AS, B_LV],
                         persona.load(tb.path("persona", "aarav-patel.example.json")),
                         get=net, clock=clock, sleep=clock.sleep)
            res = r.execute()
            self.assertEqual(res["exit"]["status"], "budget_exhausted")
            self.assertEqual(len(net.calls), 2)  # 0 s and 50 s start; at 100 s the third is never sent


class Budgets(unittest.TestCase):
    def test_request_budget_never_exceeded(self):  # W8
        flaky = {k: [err("timeout")] for k in ("/boards/alpha/", "job-board/beta", "postings/gamma")}
        for cap in range(0, 10):
            with TempBase() as tb:
                res, net, _, _ = run(tb, [B_GH, B_AS, B_LV], flaky, budgets={"max_requests": cap})
                self.assertLessEqual(len(net.calls), cap, f"cap {cap}")
                self.assertLessEqual(res["requests_used"], cap)


class ErrorPolicy(unittest.TestCase):
    def test_404_is_not_retried(self):  # W7
        with TempBase() as tb:
            res, net, clock, _ = run(tb, [B_BAD], {"/boards/alphaa/": [NOT_FOUND]})
            self.assertEqual(len(net.calls), 1)
            self.assertEqual(clock.sleeps, [])
            self.assertEqual(by_key(res)["greenhouse:alphaa"]["reason"], "not_found")

    def test_transient_failure_retries_at_most_twice(self):  # W10
        with TempBase() as tb:
            res, net, clock, _ = run(tb, [B_GH], {"/boards/alpha/": [err("timeout")]})
            self.assertEqual(len(net.calls), 3)  # 1 + 2 retries, never more
            self.assertEqual(clock.sleeps, [1, 2])
            self.assertEqual(by_key(res)["greenhouse:alpha"]["status"], "error")
            self.assertIsNone(by_key(res)["greenhouse:alpha"]["postings"])

    def test_transient_then_success(self):
        with TempBase() as tb:
            res, net, _, _ = run(tb, [B_GH], {"/boards/alpha/": [ok(b"", 503), ok(GH2)]})
            self.assertEqual(len(net.calls), 2)
            self.assertEqual(res["exit"]["status"], "finished")
            self.assertEqual(len(by_key(res)["greenhouse:alpha"]["attempts"]), 2)

    def test_retry_never_waits_past_deadline(self):
        with TempBase() as tb:
            res, net, clock, _ = run(tb, [B_GH], {"/boards/alpha/": [err("network")]}, budgets={"max_seconds": 1.5})
            self.assertEqual(len(net.calls), 2)  # waited 1 s, then 0.5 s left < 2 s wait: stop
            self.assertEqual(res["exit"]["status"], "budget_exhausted")
            # strengthened after mutant W10b survived: it must not even SLEEP past the deadline
            self.assertEqual(clock.sleeps, [1])
            self.assertLessEqual(res["seconds"], 1.5)

    def test_bad_json_is_permanent_and_raw_saved(self):
        with TempBase() as tb:
            res, net, _, r = run(tb, [B_GH], {"/boards/alpha/": [ok(b"<html>maintenance</html>")]})
            self.assertEqual(len(net.calls), 1)
            self.assertTrue(by_key(res)["greenhouse:alpha"]["reason"].startswith("bad_response"))
            raw = rd(os.path.join(r.raw_dir, "greenhouse-alpha-a1.json"), "rb")
            self.assertEqual(raw, b"<html>maintenance</html>")

    def test_wrong_schema_for_ats_is_bad_response(self):
        with TempBase() as tb:  # a Lever-shaped list served where Greenhouse is expected
            res, _, _, _ = run(tb, [B_GH], {"/boards/alpha/": [ok(LV2)]})
            self.assertEqual(by_key(res)["greenhouse:alpha"]["status"], "error")


class RepeatRule(unittest.TestCase):
    def test_duplicate_board_is_repeat_skipped(self):  # W9
        with TempBase() as tb:
            dup = {"ats": "Greenhouse", "slug": "ALPHA"}
            res, net, _, r = run(tb, [B_GH, B_AS, dup], GOOD)
            self.assertEqual(sum("/boards/alpha/" in u for u in net.calls), 1)
            self.assertEqual(res["boards"][2]["status"], "repeat_skipped")
            self.assertEqual(res["exit"]["status"], "incomplete")
            self.assertTrue(any(e["event"] == "repeat_skipped" for e in trace(r)))


class WatchAndTrace(unittest.TestCase):
    def test_baseline_then_new_posting_judged(self):
        with TempBase() as tb:
            r1, _, _, _ = run(tb, [B_GH], {"/boards/alpha/": [ok(GH2)]}, label="one")
            g = by_key(r1)["greenhouse:alpha"]
            self.assertTrue(g["baseline"])
            self.assertEqual(g["new"], 0)
            r2, _, _, _ = run(tb, [B_GH], {"/boards/alpha/": [ok(GH3)]}, label="two")
            g = by_key(r2)["greenhouse:alpha"]
            self.assertEqual(g["new"], 1)
            self.assertEqual(g["removed"], 1)
            p = g["new_postings"][0]
            self.assertEqual(p["id"], "103")
            self.assertEqual(p["rule_verdict"], "relevant")  # SWE, Denver CO + US office, Java/SQL/Kubernetes
            self.assertIn("Senior Software Engineer, Data", p["justification"][0])

    def test_every_request_is_an_observation_in_the_trace(self):
        with TempBase() as tb:
            res, net, _, r = run(tb, [B_GH, B_BAD], dict(GOOD, **{"/boards/alphaa/": [NOT_FOUND]}))
            evs = trace(r)
            obs = [e for e in evs if e["event"] == "observation"]
            self.assertEqual(len(obs), len(net.calls))
            self.assertEqual(evs[0]["event"], "run_start")
            self.assertEqual(evs[-1]["event"], "run_end")
            self.assertEqual(evs[-1]["exit"]["status"], res["exit"]["status"])
            for o in obs:
                self.assertTrue(os.path.exists(os.path.join(r.run_dir, o["raw"])))
            self.assertTrue(all(e["decision"] == "ALLOW" for e in evs if e["event"] == "policy"))

    def test_trace_records_request_and_read_decisions_with_relative_paths(self):
        """Added after review (GATE section 5 says every decision is written to the trace)."""
        with TempBase() as tb:
            run(tb, [B_GH], GOOD, label="one")
            _, _, _, r = run(tb, [B_GH], GOOD, label="two")  # second run reads the state file
            evs = trace(r)
            obs = [e for e in evs if e["event"] == "observation"]
            self.assertTrue(obs and all(o["request_policy"] == "ALLOW" for o in obs))
            reads = [e for e in evs if e["event"] == "policy" and e["kind"] == "read"]
            self.assertEqual([e["target"] for e in reads], ["runs/state/greenhouse-alpha.state.json"])
            self.assertNotIn(tb.dir, rd(r.trace_path))

    def test_run_cannot_overwrite_an_earlier_run(self):
        """Two runs with the same label in the same second (fixed clock). Found by the end-to-end
        check on 2026-11-09: the second run used to die with exit 5. Now it gets its own folder,
        and the first run's evidence stays byte-identical."""
        import datetime as dt
        fixed = dt.datetime(2026, 11, 9, 8, 0, 0, tzinfo=dt.timezone.utc)
        with TempBase() as tb:
            resume = persona.load(tb.path("persona", "aarav-patel.example.json"))

            def one():
                clock = FakeClock()
                return loop.Run(tb.dir, tb.path("runs"), dict(BUDGETS), [B_GH], resume, label="same",
                                get=FakeNet(GOOD), clock=clock, sleep=clock.sleep, now=fixed)
            r1 = one()
            r1.execute()
            before = {f: rd(os.path.join(r1.run_dir, f), "rb") for f in ("trace.jsonl", "report.json")}
            r2 = one()
            res2 = r2.execute()
            self.assertEqual(r1.run_id, "2026-11-09T08-00-00Z-same")
            self.assertEqual(r2.run_id, "2026-11-09T08-00-00Z-same-2")
            self.assertEqual(res2["exit"]["status"], "finished")
            for f, data in before.items():
                self.assertEqual(rd(os.path.join(r1.run_dir, f), "rb"), data)


class StateRead(unittest.TestCase):
    def test_state_file_symlinked_outside_is_not_read(self):
        """Added 2026-11-09 after review: the state read used to bypass policy.check_read."""
        import tempfile
        from agent import policy
        outside = os.path.realpath(tempfile.mkdtemp(prefix="js2-outside-"))
        try:
            wr(os.path.join(outside, "secret.json"), '{"seen_ids": ["x"], "runs": []}')
            with TempBase() as tb:
                os.makedirs(tb.path("runs", "state"))
                os.symlink(os.path.join(outside, "secret.json"),
                           tb.path("runs", "state", "greenhouse-alpha.state.json"))
                with self.assertRaises(policy.PolicyDenied) as cm:
                    run(tb, [B_GH], GOOD)
                self.assertEqual(cm.exception.decision["kind"], "read")
        finally:
            os.remove(os.path.join(outside, "secret.json"))
            os.rmdir(outside)


class Config(unittest.TestCase):
    def test_invalid_budgets_is_error_exit(self):
        with TempBase() as tb:
            with open(tb.path("config", "b.json"), "w") as f:
                json.dump({"max_boards": "eight"}, f)
            code = loop.main(["--base", tb.dir, "--budgets", "config/b.json", "--watchlist", "config/watchlist.json",
                              "--persona", "persona/aarav-patel.example.json"])
            self.assertEqual(code, 5)

    def test_real_resume_refused_before_any_request(self):
        with TempBase() as tb:
            p = json.loads(rd(tb.path("persona", "aarav-patel.example.json")))
            p["personal"]["email"] = "someone@gmail.com"
            wr(tb.path("persona", "real.json"), json.dumps(p))
            with open(tb.path("config", "b.json"), "w") as f:
                json.dump(BUDGETS, f)
            code = loop.main(["--base", tb.dir, "--budgets", "config/b.json", "--watchlist", "config/watchlist.json",
                              "--persona", "persona/real.json"])
            self.assertEqual(code, 5)
            self.assertEqual(os.listdir(tb.path("runs")), [])


if __name__ == "__main__":
    unittest.main()
