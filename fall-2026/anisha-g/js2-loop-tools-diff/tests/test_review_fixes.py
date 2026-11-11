"""Tests for the problems found by reviewers on 2026-11-09 ~3:30 pm (Claude Code on my Mac = CC, ChatGPT = GPT).
Written BEFORE the fixes; logs/04 shows them failing on the stage-B code, logs/05 passing after the fixes.
NOT covered here on purpose: CC problem 1 (an empty list wipes seen ids) - that is my review packet."""
import io, json, os, tempfile, unittest
from pathlib import Path
from tests.fakes import gh, Clock, ScriptedFetch, TIMEOUT
from watcher.fetch import Response
from watcher.loop import Budget, run
from watcher.policy import Policy, Blocked, NeedsApproval

K = "greenhouse:klaviyo"; B = {"ats": "greenhouse", "slug": "klaviyo"}
GH2 = "https://boards-api.greenhouse.io/v1/boards/klaviyo2/jobs"

def redirect(to): return Response(302, b"", location=to)
def st(r, k): return next(b for b in r["boards"] if b["board"] == k)

class RedirectsCount(unittest.TestCase):            # GPT 1 + CC smaller: every request counts, redirects included (my 15-cap decision)
    def test_allowed_redirect_is_a_second_counted_request(self):
        c = Clock(); f = ScriptedFetch({K: [redirect(GH2), gh(1, 2)]}, clock=c)
        r = run([B], f, clock=c)
        self.assertEqual(len(f.calls), 2); self.assertEqual(r["used"]["requests"], 2); self.assertEqual(st(r, K)["jobs"], 2)
    def test_redirect_hops_cannot_pass_the_request_cap(self):
        c = Clock(); f = ScriptedFetch({K: [redirect(GH2), redirect(GH2), redirect(GH2), gh(1)]}, clock=c)
        r = run([B], f, budget=Budget(requests=3), clock=c)
        self.assertEqual(len(f.calls), 3)                          # the 4th request is never sent
        self.assertEqual(r["exit"], "budget-exhausted"); self.assertEqual(st(r, K)["status"], "failed")
    def test_redirect_to_blocked_host_fails_the_board_and_names_it(self):
        c = Clock(); f = ScriptedFetch({K: [redirect("https://evil.com/x"), Blocked("host evil.com is not on the allow-list")]}, clock=c)
        r = run([B], f, clock=c)
        self.assertEqual(st(r, K)["status"], "failed"); self.assertIn("evil.com", st(r, K)["error"])
    def test_too_many_redirects_fails(self):
        c = Clock(); f = ScriptedFetch({K: [redirect(GH2)] * 4 + [gh(1)]}, clock=c)
        r = run([B], f, clock=c)
        self.assertEqual(st(r, K)["status"], "failed"); self.assertIn("redirect", st(r, K)["error"])
    def test_fetch_does_not_follow_redirects_by_itself(self):
        from watcher.fetch import PolicyRedirectHandler
        import urllib.request
        h = PolicyRedirectHandler(Policy(tempfile.mkdtemp()))
        self.assertIsNone(h.redirect_request(urllib.request.Request(GH2), None, 302, "Found", {}, GH2))

class Deadline(unittest.TestCase):                  # GPT 3 + CC smaller: no request may run past the 60 s budget
    def test_timeout_never_exceeds_time_left(self):
        seen = []
        class C:
            t = 59.5
            def __call__(self): return self.t
        c = C(); t0 = [True]
        def clock():
            if t0[0]: t0[0] = False; return 0.0
            return c.t
        def fetch(board, url, timeout): seen.append(timeout); return gh(1)
        run([B], fetch, clock=clock)
        self.assertTrue(seen and seen[0] <= 0.5 + 1e-9, seen)

class UnexpectedErrors(unittest.TestCase):          # CC 3: an unexpected failure still ends as 'error' with a report
    def test_unexpected_exception_gives_error_exit_and_where(self):
        def boom(*a): raise RuntimeError("disk full")
        c = Clock(); f = ScriptedFetch({K: [gh(1)]}, clock=c)
        r = run([B], f, clock=c, on_raw=boom)
        self.assertEqual(r["exit"], "error"); self.assertIn("disk full", r["why"]); self.assertEqual(r["stopped_at"], K)
    def test_invalid_board_entry_is_reported_not_crashed(self):
        c = Clock(); f = ScriptedFetch({K: [gh(1)]}, clock=c)
        r = run([{"ats": "workday", "slug": "x"}, B], f, clock=c)
        self.assertEqual(r["exit"], "incomplete"); self.assertIn("invalid board", r["boards"][0]["error"])

class PolicyEdges(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp()); (self.base / "reports/job-watch").mkdir(parents=True); self.p = Policy(self.base)
    def test_bad_port_is_blocked_not_a_crash(self):                       # CC 4
        with self.assertRaises(Blocked): self.p.check_request("GET", "https://api.lever.co:abc/v0/postings/x")
    def test_approval_is_for_one_specific_file(self):                     # CC 5
        a = self.base / "reports/job-watch/a.json"; b = self.base / "reports/job-watch/b.json"; a.write_text("{}"); b.write_text("{}")
        self.p.check_write(a, approved=a)
        with self.assertRaises(NeedsApproval): self.p.check_write(b, approved=a)
    def test_report_folder_itself_is_not_a_file_target(self):            # CC 6
        with self.assertRaises(Blocked): self.p.check_write(self.base / "reports/job-watch", approved=True)
    def test_board_name_with_capitals_or_underscore_is_allowed(self):    # CC 7
        self.p.check_request("GET", "https://boards-api.greenhouse.io/v1/boards/My_Board/jobs")
    def test_report_folder_symlinked_outside_is_blocked(self):           # GPT 2: through the real writer
        from watcher.store import Store
        base = Path(tempfile.mkdtemp()); outside = Path(tempfile.mkdtemp()); (base / "reports").mkdir()
        os.symlink(outside, base / "reports/job-watch")
        s = Store(base)
        with self.assertRaises(Blocked): s.write(s.run_dir / "trace.json", "{}")
        self.assertEqual(list(outside.rglob("*")), [])                     # nothing was created outside

class LargeResponses(unittest.TestCase):            # CC smaller: a too-large response is an explicit failure, not silently cut
    def test_oversize_body_raises(self):
        from watcher.fetch import read_capped, FetchError
        with self.assertRaises(FetchError): read_capped(io.BytesIO(b"x" * 11), 10)
        self.assertEqual(read_capped(io.BytesIO(b"x" * 10), 10), b"x" * 10)

class Config(unittest.TestCase):                    # GPT 4: a broken boards.json ends as 'error' with a trace, no crash
    def test_malformed_boards_file_gives_error_trace(self):
        import watch
        tmp = Path(tempfile.mkdtemp()); (tmp / "reports/job-watch").mkdir(parents=True); (tmp / "bad.json").write_text('{"boards": [ {"ats": "greenhouse" ')
        old = watch.HERE; watch.HERE = tmp
        try:
            with self.assertRaises(SystemExit): watch.cmd_run(watch.argparse.Namespace(boards="bad.json", wrong=None))
        finally: watch.HERE = old
        traces = list((tmp / "reports/job-watch/runs").glob("*/trace.json"))
        self.assertEqual(len(traces), 1); self.assertEqual(json.loads(traces[0].read_text())["exit"], "error")

class IndependentCheckLive(unittest.TestCase):      # CC 2 + GPT 4: the check must not only trust the agent's own files
    def _run(self, boards, raws):
        from tests.test_check import make_run
        return make_run(boards, raws)
    def test_live_recount_catches_self_consistent_empty_answer(self):
        from watcher.check import check_run
        d = self._run([{"board": K, "status": "ok", "jobs": 0, "attempts": [{"raw_file": "raw/k1"}]}], {"k1": (200, b'{"jobs":[]}')})
        self.assertEqual(check_run(d), [])                                       # the agent's own files agree with themselves...
        problems = check_run(d, live=lambda board: (200, 151))                   # ...but a fresh, separate count does not
        self.assertEqual(len(problems), 1); self.assertIn("151", problems[0])
    def test_trace_with_no_boards_is_rejected(self):
        from watcher.check import check_run
        d = self._run([], {})
        self.assertEqual(len(check_run(d)), 1)

if __name__ == "__main__": unittest.main()
