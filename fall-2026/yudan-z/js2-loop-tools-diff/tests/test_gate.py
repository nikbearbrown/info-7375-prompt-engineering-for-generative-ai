"""
Tests written from GATE.md BEFORE the loop, tools and policy code existed (commit order shows it).
Each test names the GATE section or wrong version (W1-W5) it enforces. Offline: fake fetcher, fake clock.

Run from the folder root:  python -m unittest discover -s tests -v
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from agent import ats, loop, policy, tools  # noqa: E402

HOSTS = ["boards-api.greenhouse.io", "api.ashbyhq.com", "api.lever.co"]
GH = "https://boards-api.greenhouse.io/v1/boards/{b}/jobs?content=true"


def gh_body(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "Data Analyst", "location": {"name": "Austin, TX"},
                                 "absolute_url": f"https://x/{i}", "content": "SQL and Python"} for i in ids]}).encode()


class FakeFetcher:
    """script: url -> list of outcomes, consumed in order. An outcome is (status, body) or an exception."""
    def __init__(self, script):
        self.script = {u: list(v) for u, v in script.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        out = self.script[url].pop(0)
        if isinstance(out, Exception):
            raise out
        return out


class FakeClock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step

    def __call__(self):
        self.t += self.step
        return self.t


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "runs"))
        os.makedirs(os.path.join(self.root, "persona"))
        open(os.path.join(self.root, "persona", "resume.json"), "w").write("{}")
        self.pol = policy.Policy(self.root, HOSTS, write_dir="runs")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def run_loop(self, boards, script, approvals=(), clock=None, **limits):
        pol = policy.Policy(self.root, HOSTS, write_dir="runs", approvals=approvals)
        f = FakeFetcher(script)
        res = loop.run(boards, os.path.join(self.root, "runs", "w"), pol, fetcher=f,
                       clock=clock or FakeClock(), stamp="20261109T000000Z", **limits)
        return res, f


# ---------------------------------------------------------------- GATE §6: boundary cases (predictions in POLICY.md)
class BoundaryTests(Base):
    def p(self, *parts):
        return os.path.join(self.root, *parts)

    def test_b01_allowed_host_get_passes(self):
        self.pol.check_fetch(GH.format(b="pinterest"))

    def test_b02_host_off_allowlist_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_fetch("https://evil.example.com/jobs")

    def test_b03_http_not_https_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_fetch("http://boards-api.greenhouse.io/v1/boards/pinterest/jobs")

    def test_b04_lookalike_host_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_fetch("https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs")

    def test_b05_post_to_allowed_host_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_fetch(GH.format(b="pinterest"), method="POST")

    def test_b06_write_inside_runs_allowed(self):
        self.pol.check_write(self.p("runs", "live", "x.json"))

    def test_b07_dotdot_escape_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_write(self.p("runs", "..", "GATE.md"))

    def test_b08_prefix_trick_refused(self):          # W3
        os.makedirs(self.p("runs-evil"))
        with self.assertRaises(policy.Refused):
            self.pol.check_write(self.p("runs-evil", "x.json"))

    def test_b09_symlink_escape_refused(self):
        outside = tempfile.mkdtemp()
        try:
            os.symlink(outside, self.p("runs", "link"), target_is_directory=True)
        except (OSError, NotImplementedError) as e:
            # Windows without Developer Mode cannot create symlinks (WinError 1314); a directory
            # junction is the link an ordinary Windows user can make, and it escapes the same way
            try:
                import _winapi
                _winapi.CreateJunction(outside, self.p("runs", "link"))
            except (ImportError, OSError):
                shutil.rmtree(outside, ignore_errors=True)
                self.skipTest(f"cannot create a symlink or junction on this machine: {e}")
        try:
            with self.assertRaises(policy.Refused):
                self.pol.check_write(self.p("runs", "link", "x.json"))
        finally:
            shutil.rmtree(outside, ignore_errors=True)

    def test_b10_read_inside_project_allowed(self):
        self.pol.check_read(self.p("persona", "resume.json"))

    def test_b11_read_outside_project_refused(self):
        with self.assertRaises(policy.Refused):
            self.pol.check_read(os.path.join(self.root, "..", "elsewhere.txt"))

    def test_b12_same_file_read_yes_write_no(self):
        self.pol.check_read(self.p("persona", "resume.json"))
        with self.assertRaises(policy.Refused):
            self.pol.check_write(self.p("persona", "resume.json"))

    def test_b13_reset_state_without_approval_needs_approval(self):
        with self.assertRaises(policy.NeedsApproval):
            self.pol.check_write(self.p("runs", "w", "state", "greenhouse-pinterest.json"),
                                 action="reset-state", approval_key="reset-state:greenhouse/pinterest")

    def test_b14_reset_state_with_approval_allowed(self):
        pol = policy.Policy(self.root, HOSTS, write_dir="runs", approvals=["reset-state:greenhouse/pinterest"])
        pol.check_write(self.p("runs", "w", "state", "greenhouse-pinterest.json"),
                        action="reset-state", approval_key="reset-state:greenhouse/pinterest")

    def test_b15_replace_evidence_needs_approval(self):
        with self.assertRaises(policy.NeedsApproval):
            self.pol.check_write(self.p("runs", "w", "evidence", "a.json"),
                                 action="replace-evidence", approval_key="replace-evidence:w/evidence/a.json")

    def test_b16_approval_for_another_board_does_not_count(self):
        pol = policy.Policy(self.root, HOSTS, write_dir="runs", approvals=["reset-state:ashby/ramp"])
        with self.assertRaises(policy.NeedsApproval):
            pol.check_write(self.p("runs", "w", "state", "greenhouse-pinterest.json"),
                            action="reset-state", approval_key="reset-state:greenhouse/pinterest")

    def test_b17_never_tools_refused(self):
        for name in ("apply", "send_email", "send_message", "login"):
            with self.assertRaises(policy.Refused):
                self.pol.check_tool(name)


# ---------------------------------------------------------------- tools: the policy is enforced on every call
class ToolTests(Base):
    def test_tool_write_outside_runs_is_refused_and_writes_nothing(self):
        t = tools.Tools(self.pol, loop.Budget(clock=FakeClock()), trace=[], fetcher=FakeFetcher({}))
        with self.assertRaises(policy.Refused):
            t.write_new(os.path.join(self.root, "GATE.md"), b"x")
        self.assertFalse(os.path.exists(os.path.join(self.root, "GATE.md")))

    def test_tool_refused_fetch_makes_no_request(self):
        f = FakeFetcher({})
        t = tools.Tools(self.pol, loop.Budget(clock=FakeClock()), trace=[], fetcher=f)
        with self.assertRaises(policy.Refused):
            t.fetch("https://evil.example.com/x")
        self.assertEqual(f.calls, [])

    def test_evidence_write_twice_is_refused(self):          # GATE §4
        t = tools.Tools(self.pol, loop.Budget(clock=FakeClock()), trace=[], fetcher=FakeFetcher({}))
        p = os.path.join(self.root, "runs", "w", "evidence", "a.json")
        t.write_new(p, b"1")
        with self.assertRaises(policy.Refused):
            t.write_new(p, b"2")
        self.assertEqual(open(p, "rb").read(), b"1")


# ---------------------------------------------------------------- GATE §2 exits, §3 budgets, §4 repeats, §5 errors
P, D = ("greenhouse", "pinterest"), ("greenhouse", "databricks")
PU, DU = GH.format(b="pinterest"), GH.format(b="databricks")
BAD = ("greenhouse", "no-such-board-js2")
BU = GH.format(b="no-such-board-js2")


class LoopTests(Base):
    def test_all_boards_ok_is_finished(self):
        res, _ = self.run_loop([P, D], {PU: [(200, gh_body(1, 2))], DU: [(200, gh_body(3))]})
        self.assertEqual(res["exit"], "finished")
        self.assertEqual(loop.EXIT_CODES["finished"], 0)

    def test_404_not_retried_and_run_is_incomplete(self):        # W1, W2
        res, f = self.run_loop([P, BAD], {PU: [(200, gh_body(1))], BU: [(404, b'{"status":404}')]})
        self.assertEqual(res["exit"], "incomplete")
        self.assertEqual(f.calls.count(BU), 1)
        bad = [b for b in res["boards"] if b["board"] == "no-such-board-js2"][0]
        self.assertEqual(bad["status"], "failed")
        self.assertNotIn("postings", bad)            # no invented count
        self.assertNotIn("new", bad)                 # no invented "0 new"

    def test_timeout_retried_once_then_ok(self):
        res, f = self.run_loop([P], {PU: [TimeoutError("t"), (200, gh_body(1))]})
        self.assertEqual(res["exit"], "finished")
        self.assertEqual(len(f.calls), 2)

    def test_timeout_twice_fails_after_two_requests(self):
        res, f = self.run_loop([P], {PU: [TimeoutError("t"), TimeoutError("t")]})
        self.assertEqual(res["exit"], "incomplete")
        self.assertEqual(len(f.calls), 2)

    def test_5xx_retried_once_only(self):                        # W2
        res, f = self.run_loop([P], {PU: [(503, b""), (503, b"")]})
        self.assertEqual(len(f.calls), 2)
        self.assertEqual(res["exit"], "incomplete")

    def test_retries_count_against_request_budget(self):        # W4
        res, f = self.run_loop([P, D, BAD], {PU: [TimeoutError("t"), (200, gh_body(1))], DU: [(200, gh_body(2))],
                                             BU: [(404, b"")]}, max_requests=3)
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertEqual(len(f.calls), 3)
        self.assertIn("no-such-board-js2", res["not_reached"])

    def test_seconds_budget(self):
        res, f = self.run_loop([P, D], {PU: [(200, gh_body(1))], DU: [(200, gh_body(2))]},
                               clock=FakeClock(step=50), max_seconds=120)
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertLessEqual(len(f.calls), 1)

    def test_board_budget(self):
        boards = [("greenhouse", f"b{i}") for i in range(7)]
        script = {GH.format(b=f"b{i}"): [(200, gh_body(i))] for i in range(7)}
        res, f = self.run_loop(boards, script)
        self.assertEqual(res["exit"], "budget-exhausted")
        self.assertEqual(len(f.calls), 6)

    def test_budget_can_be_lowered_not_raised(self):
        with self.assertRaises(ValueError):
            loop.Budget(max_requests=13)

    def test_board_listed_twice_fetched_once(self):              # GATE §4
        res, f = self.run_loop([P, P], {PU: [(200, gh_body(1))]})
        self.assertEqual(f.calls.count(PU), 1)
        self.assertTrue(any(o["outcome"] == "repeat-refused" for o in res["trace"]))

    def test_bad_shape_stops_with_error(self):
        res, f = self.run_loop([P, D], {PU: [(200, b'{"unexpected": true}')], DU: [(200, gh_body(2))]})
        self.assertEqual(res["exit"], "error")
        self.assertNotIn(DU, f.calls)

    def test_policy_refusal_stops_with_error(self):
        res, f = self.run_loop([("greenhouse", "x/../../evil")], {})
        self.assertEqual(res["exit"], "error")
        self.assertEqual(f.calls, [])

    def test_baseline_then_new_ids_only_per_board(self):
        self.run_loop([P], {PU: [(200, gh_body(1, 2))]})
        res, _ = self.run_loop([P], {PU: [(200, gh_body(1, 2, 3))]})
        b = res["boards"][0]
        self.assertEqual([j["id"] for j in b["new_postings"]], [3])

    def test_failed_board_keeps_its_seen_ids(self):              # W5
        self.run_loop([P], {PU: [(200, gh_body(1, 2))]})
        state = os.path.join(self.root, "runs", "w", "state", "greenhouse-pinterest.json")
        before = open(state, "rb").read()
        self.run_loop([P], {PU: [(404, b"")]})
        self.assertEqual(open(state, "rb").read(), before)

    def test_every_request_is_in_the_trace(self):
        res, f = self.run_loop([P, BAD], {PU: [TimeoutError("t"), (200, gh_body(1))], BU: [(404, b"")]})
        fetches = [o for o in res["trace"] if o["tool"] == "fetch" and o["outcome"] != "repeat-refused"]
        self.assertEqual(len(fetches), len(f.calls))

    def test_trace_and_raw_saved_under_runs(self):
        res, _ = self.run_loop([P], {PU: [(200, gh_body(1))]})
        self.assertTrue(os.path.exists(res["trace_path"]))
        self.assertTrue(any(n.endswith("greenhouse-pinterest.json")
                            for n in os.listdir(os.path.join(self.root, "runs", "w", "evidence"))))


# ---------------------------------------------------------------- three ATS shapes, normalised to one posting shape
class AtsTests(unittest.TestCase):
    def test_greenhouse(self):
        p = ats.parse("greenhouse", gh_body(7))[0]
        self.assertEqual((p["id"], p["location"]["name"]), (7, "Austin, TX"))

    def test_ashby(self):
        raw = json.dumps({"jobs": [{"id": "a1", "title": "Data Analyst", "location": "NYC", "jobUrl": "u",
                                    "descriptionHtml": "<p>SQL</p>", "isListed": True,
                                    "address": {"postalAddress": {"addressRegion": "NY", "addressCountry": "USA"}}}]}).encode()
        p = ats.parse("ashby", raw)[0]
        self.assertEqual(p["id"], "a1")
        self.assertIn("NY", p["location"]["name"])
        self.assertIn("US", p["location"]["name"])

    def test_lever(self):
        raw = json.dumps([{"id": "l1", "text": "Data Analyst", "hostedUrl": "u", "country": "US",
                           "categories": {"location": "New York, NY"}, "description": "<p>SQL</p>"}]).encode()
        p = ats.parse("lever", raw)[0]
        self.assertEqual((p["id"], p["title"]), ("l1", "Data Analyst"))
        self.assertIn("US", p["location"]["name"])

    def test_wrong_shape_raises(self):
        for name, raw in (("greenhouse", b"{}"), ("ashby", b"[]"), ("lever", b"{}")):
            with self.assertRaises(ats.BadShape):
                ats.parse(name, raw)

    def test_unknown_ats_refused(self):
        with self.assertRaises(ats.BadShape):
            ats.url("workday", "x")


if __name__ == "__main__":
    unittest.main()
