"""JS2 tests, one block per GATE.md section. Responses built in this file are CONSTRUCTED (fake network);
tests that name a file under data/raw/ use real saved responses."""
import ast
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from earlybird import Refused, boards, check, gate, loop, watch  # noqa: E402
from earlybird.__main__ import change_boards, main  # noqa: E402
from earlybird.policy import Policy  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402
from earlybird.tools import Tools, Trace  # noqa: E402
import wrong_versions as wv  # noqa: E402

RESUME = load_resume(ROOT / "data/resume/rohan-desai.example.json")
B = {k: {"key": k, "platform": k.split(":")[0], "name": k.split(":")[1]}
     for k in ("ashby:acme", "greenhouse:beta", "lever:gamma", "greenhouse:typo", "greenhouse:slow")}


def jobs(platform, ids):
    """CONSTRUCTED board response in the platform's real shape."""
    if platform == "lever":
        return json.dumps([{"id": i, "text": "Software Engineer", "country": "US"} for i in ids]).encode()
    return json.dumps({"jobs": [{"id": i, "title": "Software Engineer"} for i in ids]}).encode()


class FakeNet:
    """Answers by URL from a script: bytes = 200 with that body, int = HTTP error, Exception = raised."""

    def __init__(self, script):
        self.script = {url: list(v) if isinstance(v, list) else [v] for url, v in script.items()}
        self.calls = []

    def __call__(self, req, timeout=None):
        url = req.full_url
        self.calls.append(url)
        answers = self.script[url]
        a = answers.pop(0) if len(answers) > 1 else answers[0]
        if isinstance(a, int):
            raise urllib.error.HTTPError(url, a, "err", {}, io.BytesIO(b'{"status":%d}' % a))
        if isinstance(a, Exception):
            raise a
        return io.BytesIO(a)

    def count(self, board):
        return self.calls.count(boards.url(board))


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sleeps = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, board_list, net=None, state=None, budget=None, tools_cls=Tools, parse=boards.parse,
                 replay=False, root=None, day="2026-10-31", label="t"):
        budget = budget or gate.Budget()
        trace = Trace(budget)
        tools = tools_cls(Policy(root or self.root), budget, trace, day, replay=replay, opener=net,
                          sleep=self.sleeps.append)
        state = state if state is not None else watch.empty_state()
        result = loop.run(board_list, tools, budget, trace, state, RESUME, day, label, parse=parse)
        return result, trace, state

    @staticmethod
    def by_key(result):
        return {b["key"]: b for b in result["boards"]}


# ---------------------------------------------------------------- loop, exits, error policy
class Loop(LoopCase):
    def test_three_boards_two_platforms_finished_baseline(self):
        net = FakeNet({boards.url(B[k]): jobs(B[k]["platform"], ["1", "2"])
                       for k in ("ashby:acme", "greenhouse:beta", "lever:gamma")})
        r, trace, state = self.run_loop([B["ashby:acme"], B["greenhouse:beta"], B["lever:gamma"]], net)
        self.assertEqual(r["exit"], "finished")
        self.assertEqual([b["postings"] for b in r["boards"]], [2, 2, 2])
        self.assertTrue(all(b["baseline"] and b["new"] == 0 for b in r["boards"]))
        self.assertEqual(trace.events[-1]["action"], "exit")
        self.assertEqual(set(state["boards"]), {"ashby:acme", "greenhouse:beta", "lever:gamma"})

    def test_second_run_reports_only_new_ids(self):
        state = watch.empty_state()
        self.run_loop([B["lever:gamma"]], FakeNet({boards.url(B["lever:gamma"]): jobs("lever", ["1", "2"])}), state)
        r, _, _ = self.run_loop([B["lever:gamma"]],
                                FakeNet({boards.url(B["lever:gamma"]): jobs("lever", ["1", "2", "3"])}), state)
        self.assertEqual(r["boards"][0]["new"], 1)
        self.assertEqual(r["boards"][0]["rows"][0]["record"]["posting_id"], "3")

    def test_404_no_retry_board_error_run_incomplete_no_invented_count(self):
        net = FakeNet({boards.url(B["ashby:acme"]): jobs("ashby", ["1"]), boards.url(B["greenhouse:typo"]): 404})
        r, _, state = self.run_loop([B["ashby:acme"], B["greenhouse:typo"]], net)
        typo = self.by_key(r)["greenhouse:typo"]
        self.assertEqual(r["exit"], "incomplete")
        self.assertEqual(net.count(B["greenhouse:typo"]), 1, "a 404 must not be retried")
        self.assertEqual((typo["status"], typo["postings"], typo["new"]), ("error", None, None))
        self.assertNotIn("greenhouse:typo", state["boards"], "no state for a failed board")
        self.assertIn("ashby:acme", state["boards"])
        self.assertTrue((self.root / "data/raw/2026-10-31/greenhouse_typo.error.txt").exists())

    def test_timeout_retried_once_then_error(self):
        url = boards.url(B["greenhouse:slow"])
        net = FakeNet({url: [urllib.error.URLError("timed out"), urllib.error.URLError("timed out")]})
        r, trace, _ = self.run_loop([B["greenhouse:slow"]], net)
        self.assertEqual(net.count(B["greenhouse:slow"]), 2)
        self.assertEqual(self.sleeps, [gate.RETRY_WAIT_SECONDS])
        self.assertEqual((r["exit"], r["boards"][0]["status"]), ("incomplete", "error"))
        self.assertIn("retry 1/1", [e.get("result") for e in trace.events])

    def test_5xx_then_ok_recovers_with_one_retry(self):
        url = boards.url(B["greenhouse:slow"])
        r, _, _ = self.run_loop([B["greenhouse:slow"]], FakeNet({url: [503, jobs("greenhouse", ["9"])]}))
        self.assertEqual((r["exit"], r["boards"][0]["postings"]), ("finished", 1))

    def test_wrong_shape_is_error_not_empty_board(self):
        for body in (b"<html>maintenance</html>", b"[]", b'{"jobs": null}'):
            r, _, _ = self.run_loop([B["greenhouse:beta"]], FakeNet({boards.url(B["greenhouse:beta"]): body}))
            self.assertEqual((r["exit"], r["boards"][0]["postings"]), ("incomplete", None), body)

    def test_repeat_rule_refuses_same_url_without_network_or_budget(self):
        net = FakeNet({boards.url(B["ashby:acme"]): jobs("ashby", ["1"])})
        budget = gate.Budget()
        r, trace, _ = self.run_loop([B["ashby:acme"], dict(B["ashby:acme"], key="ashby:acme-again")], net,
                                    budget=budget)
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(budget.used["requests"], 1)
        self.assertEqual(r["boards"][1]["status"], "repeat-refused")
        self.assertIn("repeat-refused", [e.get("result") for e in trace.events])

    def test_permission_refusal_stops_whole_run_with_error(self):
        with mock.patch.dict(boards.URLS, {"ashby": "https://evil.example.com/{name}"}):
            net = FakeNet({})
            r, _, _ = self.run_loop([B["ashby:acme"], B["greenhouse:beta"]], net)
        self.assertEqual(r["exit"], "error")
        self.assertIn("allow-list", r["reason"])
        self.assertEqual(net.calls, [])
        self.assertEqual(r["not_attempted"], ["ashby:acme", "greenhouse:beta"])


class Budgets(LoopCase):
    def three(self):
        keys = ("ashby:acme", "greenhouse:beta", "lever:gamma")
        return [B[k] for k in keys], FakeNet({boards.url(B[k]): jobs(B[k]["platform"], ["1"]) for k in keys})

    def test_request_budget_checked_before_sending(self):
        board_list, net = self.three()
        r, _, _ = self.run_loop(board_list, net, budget=gate.Budget(requests=2))
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertEqual(len(net.calls), 2, "request 3 must never go out")
        self.assertEqual(r["not_attempted"], ["lever:gamma"])

    def test_board_budget(self):
        board_list, net = self.three()
        r, _, _ = self.run_loop(board_list, net, budget=gate.Budget(boards=1))
        self.assertEqual((r["exit"], len(net.calls)), ("budget-exhausted", 1))

    def test_seconds_budget(self):
        board_list, net = self.three()
        ticks = iter([0, 0, 0, 0, 0, 0, 0, 200] + [200] * 50)
        r, _, _ = self.run_loop(board_list, net, budget=gate.Budget(seconds=100, clock=lambda: next(ticks)))
        self.assertEqual(r["exit"], "budget-exhausted")
        self.assertIn("seconds", r["reason"])
        self.assertLess(len(net.calls), 3)

    def test_budget_can_be_lowered_never_raised(self):
        gate.Budget(boards=1, requests=1, seconds=1)
        for kw in ({"boards": gate.MAX_BOARDS + 1}, {"requests": gate.MAX_REQUESTS + 1},
                   {"seconds": gate.MAX_SECONDS + 1}, {"requests": -1}):
            with self.assertRaises(Refused, msg=kw):
                gate.Budget(**kw)

    def test_cli_refuses_a_raised_budget(self):
        self.assertEqual(main(["run", "--replay", "2026-10-23", "--label", "never-written",
                               "--max-requests", str(gate.MAX_REQUESTS + 1)]), 2)
        self.assertFalse((ROOT / "reports/never-written.md").exists())


# ---------------------------------------------------------------- permission boundary cases (GATE.md B1-B16)
class Boundary(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "proj"
        for d in ("reports", "data/raw", "data/state", "config"):
            (self.root / d).mkdir(parents=True)
        (self.root / "config/boards.json").write_text("[]", encoding="utf-8")
        self.outside = Path(self.tmp.name) / "outside"
        self.outside.mkdir()
        self.p = Policy(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def refused(self, fn, *args, **kw):
        with self.assertRaises(Refused):
            fn(*args, **kw)

    def test_B01_allowed_host(self):
        """expected: allowed"""
        self.p.check_fetch("https://boards-api.greenhouse.io/v1/boards/stripe/jobs")

    def test_B02_host_off_allowlist(self):
        """expected: refused, host not on allow-list"""
        self.refused(self.p.check_fetch, "https://evil.example.com/jobs")

    def test_B03_allowed_host_as_prefix(self):
        """expected: refused, host not on allow-list"""
        self.refused(self.p.check_fetch, "https://api.lever.co.evil.com/v0/postings/x")

    def test_B04_plain_http(self):
        """expected: refused, https only"""
        self.refused(self.p.check_fetch, "http://api.lever.co/v0/postings/palantir")

    def test_B05_credentials_in_url(self):
        """expected: refused, credentials in URL"""
        self.refused(self.p.check_fetch, "https://me:pw@api.ashbyhq.com/posting-api/job-board/commure")

    def test_B06_write_reports(self):
        """expected: allowed"""
        self.assertEqual(self.p.check_write("reports/run.md"), (self.root / "reports/run.md").resolve())

    def test_B07_dotdot_escape(self):
        """expected: refused, outside writable folders"""
        self.refused(self.p.check_write, "reports/../GATE.md")
        self.refused(self.p.check_write, "reports/../../outside/x.md")

    def test_B08_sibling_prefix(self):
        """expected: refused, outside writable folders"""
        (self.root / "reports-evil").mkdir()
        self.refused(self.p.check_write, "reports-evil/x.md")

    def test_B09_symlink_escape(self):
        """expected: refused, resolves outside. Windows without Developer Mode cannot make symlinks, so the
        test falls back to a directory junction, which escapes the same way."""
        link = self.root / "reports/link"
        try:
            os.symlink(self.outside, link, target_is_directory=True)
            kind = "symlink"
        except OSError:
            if os.name != "nt":
                raise
            import _winapi
            _winapi.CreateJunction(str(self.outside), str(link))
            kind = "junction"
        self.assertEqual(self.p.resolve("reports/link/x.md"), (self.outside / "x.md").resolve(), kind)
        self.refused(self.p.check_write, "reports/link/x.md")
        if os.name == "nt" and kind == "junction":
            os.rmdir(link)

    def test_B10_read_inside(self):
        """expected: allowed"""
        self.p.check_read("config/boards.json")

    def test_B11_read_outside(self):
        """expected: refused"""
        (self.outside / "secret.txt").write_text("x")
        self.refused(self.p.check_read, self.outside / "secret.txt")
        self.refused(self.p.check_read, "../outside/secret.txt")

    def test_B12_board_list_needs_approval(self):
        """expected: refused, needs approval"""
        self.refused(self.p.check_write, "config/boards.json")

    def test_B13_board_list_with_yes(self):
        """expected: allowed"""
        self.p.check_write("config/boards.json", approval="yes")

    def test_B14_board_list_with_y_or_nothing(self):
        """expected: refused"""
        for answer in ("y", "", "Yes please", None):
            self.refused(self.p.check_write, "config/boards.json", approval=answer)

    def test_B15_write_state(self):
        """expected: allowed"""
        self.p.check_write("data/state/seen.json")

    def test_B16_post(self):
        """expected: refused, GET only"""
        self.refused(self.p.check_fetch, "https://api.ashbyhq.com/posting-api/job-board/commure", method="POST")

    def test_writing_a_writable_folder_itself_or_other_paths_refused(self):
        for path in ("reports", "data", "GATE.md", "earlybird/policy.py", "config/other.json"):
            self.refused(self.p.check_write, path)

    def test_boards_cli_approval(self):
        shutil.copy(ROOT / "config/boards.json", self.root / "config/boards.json")
        before = (self.root / "config/boards.json").read_text()
        self.assertEqual(change_boards(self.root, "add", ask=lambda _: "y", platform="lever", name="x"), 2)
        self.assertEqual((self.root / "config/boards.json").read_text(), before, "refused = unchanged")
        self.assertEqual(change_boards(self.root, "add", ask=lambda _: "yes", platform="lever", name="x"), 0)
        self.assertIn("lever:x", (self.root / "config/boards.json").read_text())


# ---------------------------------------------------------------- real saved responses and the independent check
REAL_1023 = {"ashby:commure": 81, "greenhouse:stripe": 726, "greenhouse:figma": 141,
             "greenhouse:databricks": 898, "lever:palantir": 308}


def real(key):
    p, n = key.split(":")
    return {"key": key, "platform": p, "name": n}


class RealSnapshots(LoopCase):
    def replay_1023(self, parse=boards.parse, state=None):
        return self.run_loop([real(k) for k in REAL_1023], replay=True, root=ROOT, day="2026-10-23",
                             parse=parse, state=state)

    def write_trace(self, trace):
        path = self.root / "trace.jsonl"
        path.write_text(trace.jsonl(), encoding="utf-8")
        return path

    def test_parse_counts_match_saved_responses(self):
        r, _, _ = self.replay_1023()
        self.assertEqual(r["exit"], "finished")
        self.assertEqual({b["key"]: b["postings"] for b in r["boards"]}, REAL_1023)

    def test_independent_check_passes_correct_run(self):
        _, trace, _ = self.replay_1023()
        self.assertEqual(check.check(ROOT, self.write_trace(trace))["verdict"], "PASS")

    def test_wrong_version_1_finishes_cleanly_and_check_catches_it(self):
        r, trace, state = self.replay_1023(parse=wv.parse_jobs_key_or_empty)
        self.assertEqual(r["exit"], "finished", "the wrong version looks like a clean run")
        self.assertEqual(self.by_key(r)["lever:palantir"]["postings"], 0)
        out = check.check(ROOT, self.write_trace(trace))
        self.assertEqual(out["verdict"], "FAIL")
        self.assertTrue(any("lever:palantir" in p and "308" in p for p in out["problems"]), out["problems"])

    def test_check_flags_drop_to_zero_against_earlier_state(self):
        state = watch.empty_state()
        self.replay_1023(state=state)
        _, trace, _ = self.run_loop([real("lever:palantir")], replay=True, root=ROOT, day="2026-10-23",
                                    parse=wv.parse_jobs_key_or_empty, state=state, label="t2")
        spath = self.root / "seen.json"
        spath.write_text(json.dumps(state), encoding="utf-8")
        out = check.check(ROOT, self.write_trace(trace), spath)
        self.assertTrue(any("0 postings now" in p for p in out["problems"]), out["problems"])

    def test_check_shares_no_code_with_the_agent(self):
        tree = ast.parse((ROOT / "earlybird/check.py").read_text(encoding="utf-8"))
        imported = {n.module if isinstance(n, ast.ImportFrom) else a.name
                    for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))
                    for a in (n.names if isinstance(n, ast.Import) else [None])}
        self.assertEqual(imported, {"json", "pathlib"})


# ---------------------------------------------------------------- the other wrong versions (GATE.md 2-5)
class WrongVersions(LoopCase):
    def test_wrong_version_2_swallowed_404_is_caught(self):
        def outcome(tools_cls):
            net = FakeNet({boards.url(B["greenhouse:typo"]): 404})
            r, _, _ = self.run_loop([B["greenhouse:typo"]], net, tools_cls=tools_cls)
            return r["exit"]
        self.assertEqual(outcome(Tools), "incomplete")
        self.assertEqual(outcome(wv.Swallow404Tools), "finished", "wrong version 2 hides the failure")

    def test_wrong_version_3_prefix_check_is_caught(self):
        root = self.root / "proj"
        (root / "reports").mkdir(parents=True)
        with self.assertRaises(Refused):
            Policy(root).check_write("reports-evil/x.md")
        wv.PrefixPolicy(root).check_write("reports-evil/x.md")  # wrong version 3 lets it through

    def test_wrong_version_4_budget_after_request_is_caught(self):
        keys = ("ashby:acme", "greenhouse:beta", "lever:gamma")

        def calls(tools_cls):
            net = FakeNet({boards.url(B[k]): jobs(B[k]["platform"], ["1"]) for k in keys})
            self.run_loop([B[k] for k in keys], net, budget=gate.Budget(requests=2), tools_cls=tools_cls)
            return len(net.calls)
        self.assertEqual(calls(Tools), 2)
        self.assertEqual(calls(wv.BudgetAfterTools), 3, "wrong version 4 sends an over-budget request")

    def test_wrong_version_5_retry_on_404_is_caught(self):
        def calls(tools_cls):
            net = FakeNet({boards.url(B["greenhouse:typo"]): 404})
            self.run_loop([B["greenhouse:typo"]], net, tools_cls=tools_cls)
            return net.count(B["greenhouse:typo"])
        self.assertEqual(calls(Tools), 1)
        self.assertEqual(calls(wv.RetryOn404Tools), 2, "wrong version 5 retries a 404")


if __name__ == "__main__":
    unittest.main()
