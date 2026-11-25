"""Loop and parser tests, written before loop.py and parsers.py exist.

L1-L15 and P1-P2 are the tests Claude Code proposed on 2026-11-04 and Swathi
approved; R1-R5 check the items of GATE.md's "Revision (2026-11-04, before any
loop code)" section, one test each. Every docstring names the GATE.md item it
checks. Written by Claude Code.

Every board response below is SIMULATED: built in this file by a fake
transport, never fetched, never Claude output and never a real posting. The
fake clock advances only when the test says so, so nothing really waits.
Every test runs inside no_network(): socket connections fail.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import policy  # noqa: E402
import rule  # noqa: E402
import loop  # noqa: E402  (does not exist until the loop code is written)
import parsers  # noqa: E402  (does not exist until the parser code is written)

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{}"
TIMEOUT = object()  # in a script: the fake transport raises loop.Timeout
WIDE = {"boards": 50, "requests": 100, "seconds": 10 ** 6}  # budgets that never bind


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def gh_board(name, slug=None):
    return {"name": name, "system": "greenhouse", "slug": slug or name}


def ashby_board(name, slug=None):
    return {"name": name, "system": "ashby", "slug": slug or name}


def gh_body(*jobs):
    """SIMULATED Greenhouse body: jobs are (id, title, location) tuples."""
    return json.dumps({"jobs": [{"id": i, "title": t, "location": {"name": loc},
                                 "absolute_url": f"https://example.invalid/gh/{i}"}
                                for i, t, loc in jobs],
                       "meta": {"total": len(jobs)}}).encode()


def ashby_job(job_id, title, location, secondary=(), listed=True):
    return {"id": job_id, "title": title, "location": location,
            "secondaryLocations": [{"location": s} for s in secondary],
            "jobUrl": f"https://example.invalid/ashby/{job_id}", "isListed": listed}


def ashby_body(*jobs):
    """SIMULATED Ashby body: jobs are dicts from ashby_job()."""
    return json.dumps({"apiVersion": "1", "jobs": list(jobs)}).encode()


OK_A = gh_body((1, "Data Engineer", "Boston, Massachusetts"), (2, "Senior Data Scientist", "Remote - US"))
OK_B = gh_body((11, "Machine Learning Engineer", "New York, New York"))
OK_C = ashby_body(ashby_job("c-uuid-1", "Analytics Engineer", "San Francisco, CA"))


class FakeClock:
    def __init__(self):
        self.t = 0.0
        self.sleeps = []

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.t += seconds


class FakeTransport:
    """SIMULATED transport. script maps url -> list of responses; the last one repeats.

    A response is (status, body bytes), TIMEOUT, or an exception to raise.
    Each call advances the fake clock by `cost` seconds.
    """

    def __init__(self, clock, script, cost=0.0):
        self.clock = clock
        self.script = {url: list(responses) for url, responses in script.items()}
        self.cost = cost
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append((url, timeout))
        self.clock.t += self.cost
        queue = self.script.get(url)
        if not queue:
            raise AssertionError(f"unscripted request to {url}")
        response = queue.pop(0) if len(queue) > 1 else queue[0]
        if response is TIMEOUT:
            raise loop.Timeout("SIMULATED timeout")
        if isinstance(response, BaseException):
            raise response
        return response

    def count(self, url):
        return sum(1 for called, _ in self.calls if called == url)


class LoopCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / "js2"
        for folder in ("runs", "state", "persona"):
            (self.root / folder).mkdir(parents=True)
        for name in ("priya-nair.resume.example.json", "priya-nair.targets.json"):
            shutil.copy(HERE / "persona" / name, self.root / "persona" / name)
        self.state_file = self.root / "state" / "seen_ids.json"
        self.targets = json.loads((self.root / "persona" / "priya-nair.targets.json").read_text(encoding="utf-8"))
        self.clock = FakeClock()
        self.runs = 0

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, boards, script, budgets=None, cost=0.0, policy_obj=None, run_id=None, **kwargs):
        self.runs += 1
        transport = FakeTransport(self.clock, script, cost)
        with no_network():
            result = loop.run_loop(boards, dict(budgets or WIDE),
                                   policy=policy_obj or policy.Policy(self.root),
                                   transport=transport, clock=self.clock, sleep=self.clock.sleep,
                                   run_id=run_id or f"run{self.runs}", **kwargs)
        return result, transport

    def write_state(self, boards):
        self.state_file.write_text(json.dumps({"boards": boards}), encoding="utf-8")
        return self.state_file.read_bytes()

    def read_state(self):
        return json.loads(self.state_file.read_text(encoding="utf-8"))["boards"]

    def observations(self, result, board=None, action=None):
        return [o for o in result.trace
                if (board is None or o["board"] == board) and (action is None or o["action"] == action)]


class EmptyAndFailedBoards(LoopCase):
    def test_L1_empty_board_is_not_zero_new(self):
        """L1, GATE.md wrong version 1 and error policy (empty response). SIMULATED: a 200 with
        {"jobs": []} and a 200 with no body are each "empty, unverified", never "0 new"; no retry;
        that board's state is unchanged; the run ends incomplete, never finished."""
        before = {"empty-list": ["9"], "no-body": ["8"]}
        self.write_state(dict(before))
        boards = [gh_board("a"), gh_board("empty-list"), gh_board("no-body")]
        result, t = self.run_loop(boards, {GH.format("a"): [(200, OK_A)],
                                           GH.format("empty-list"): [(200, gh_body())],
                                           GH.format("no-body"): [(200, b"")]})
        self.assertEqual(result.exit, "incomplete")
        for name in ("empty-list", "no-body"):
            self.assertEqual(result.boards[name]["status"], "empty, unverified")
            self.assertEqual(result.boards[name]["new_ids"], [])
            self.assertEqual(t.count(GH.format(name)), 1)
            self.assertEqual(self.read_state()[name], before[name])
        self.assertEqual(self.clock.sleeps, [])

    def test_L2_failed_board_is_reported_not_dropped(self):
        """L2, GATE.md wrong version 2. SIMULATED: one board 404s, the others are fine; the
        failed board is in the report with its reason, and the run ends incomplete."""
        boards = [gh_board("a"), gh_board("bad"), ashby_board("c")]
        result, _ = self.run_loop(boards, {GH.format("a"): [(200, OK_A)],
                                           GH.format("bad"): [(404, b'{"status":404,"error":"Job not found"}')],
                                           ASHBY.format("c"): [(200, OK_C)]})
        self.assertEqual(result.exit, "incomplete")
        self.assertEqual(result.boards["bad"]["status"], "failed")
        self.assertIn("404", result.boards["bad"]["reason"])
        self.assertEqual(result.boards["a"]["status"], "ok")
        self.assertEqual(result.boards["c"]["status"], "ok")

    def test_L3_404_is_requested_exactly_once(self):
        """L3, GATE.md wrong version 3 and error policy (404: no retry). SIMULATED: a 404 makes
        exactly 1 request to that URL and no retry wait."""
        result, t = self.run_loop([gh_board("bad")], {GH.format("bad"): [(404, b"")]})
        self.assertEqual(t.count(GH.format("bad")), 1)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(self.observations(result, "bad", "retry"), [])

    def test_L4_temporary_failures_retry_once_never_twice(self):
        """L4, GATE.md wrong version 3 and error policy (timeout or 5xx: retry once). SIMULATED:
        timeout then 200 -> 2 requests, ok; timeout twice -> 2 requests, failed; 503 twice -> 2
        requests, failed; 503 then 200 -> 2 requests, ok. Never 3."""
        cases = {"t-ok": ([TIMEOUT, (200, OK_A)], "ok"),
                 "t-t": ([TIMEOUT], "failed"),
                 "503-503": ([(503, b"")], "failed"),
                 "503-ok": ([(503, b""), (200, OK_B)], "ok")}
        boards = [gh_board(name) for name in cases]
        result, t = self.run_loop(boards, {GH.format(n): r for n, (r, _) in cases.items()})
        for name, (_, status) in cases.items():
            with self.subTest(board=name):
                self.assertEqual(t.count(GH.format(name)), 2)
                self.assertEqual(result.boards[name]["status"], status)
                self.assertEqual(result.boards[name]["attempts"], 2)


class Budgets(LoopCase):
    def test_L5_requests_budget_checked_before_each_request(self):
        """L5, GATE.md wrong version 4 and Budgets (15 requests, retries included). SIMULATED: with
        boards that always time out, the transport is called exactly 15 times; with requests=3,
        exactly 3 times, then budget-exhausted naming the requests budget and the boards not tried."""
        boards = [gh_board(f"slow{i}") for i in range(10)]
        script = {GH.format(b["name"]): [TIMEOUT] for b in boards}
        result, t = self.run_loop(boards, script, budgets=dict(WIDE, requests=15))
        self.assertEqual(len(t.calls), 15)
        self.assertEqual(result.exit, "budget-exhausted")
        self.assertEqual(result.budgets["exhausted"], "requests")

        result, t = self.run_loop(boards, script, budgets=dict(WIDE, requests=3))
        self.assertEqual(len(t.calls), 3)
        self.assertEqual(result.exit, "budget-exhausted")
        self.assertEqual(result.budgets["exhausted"], "requests")
        self.assertEqual(result.budgets["requests_used"], 3)
        for b in boards[2:]:
            self.assertEqual(result.boards[b["name"]]["status"], "not tried")

    def test_L6_boards_budget(self):
        """L6, GATE.md Budgets (maximum 5 boards). SIMULATED: 6 boards passed in with boards=5;
        the 6th is never requested; budget-exhausted."""
        boards = [gh_board(f"b{i}") for i in range(6)]
        result, t = self.run_loop(boards, {GH.format(b["name"]): [(200, OK_A)] for b in boards},
                                  budgets=dict(WIDE, boards=5))
        self.assertEqual(t.count(GH.format("b5")), 0)
        self.assertEqual(len(t.calls), 5)
        self.assertEqual(result.exit, "budget-exhausted")
        self.assertEqual(result.budgets["exhausted"], "boards")
        self.assertEqual(result.boards["b5"]["status"], "not tried")

    def test_L7_seconds_budget_checked_before_each_request(self):
        """L7, GATE.md Budgets (maximum 60 seconds, checked before each request). SIMULATED: a fake
        clock moving 25 s per request; requests at t = 0, 25 and 50 are sent, the one at t = 75 is
        not; budget-exhausted."""
        boards = [gh_board(n) for n in ("a", "b", "c", "d")]
        result, t = self.run_loop(boards, {GH.format(b["name"]): [(200, OK_A)] for b in boards},
                                  budgets=dict(WIDE, seconds=60), cost=25.0)
        self.assertEqual([url for url, _ in t.calls], [GH.format(n) for n in ("a", "b", "c")])
        self.assertEqual(result.exit, "budget-exhausted")
        self.assertEqual(result.budgets["exhausted"], "seconds")
        self.assertEqual(result.boards["d"]["status"], "not tried")


class RepeatRule(LoopCase):
    def test_L8_permitted_retry_is_not_a_repeat(self):
        """L8, GATE.md wrong version 5 (first half) and Repeat rule. SIMULATED: a timeout then a
        retry; the retry is sent, not skipped as a repeat."""
        url = GH.format("a")
        result, t = self.run_loop([gh_board("a")], {url: [TIMEOUT, (200, OK_A)]})
        self.assertEqual([called for called, _ in t.calls], [url, url])
        self.assertEqual([o["action"] for o in self.observations(result, "a")
                          if o["action"] in ("request", "retry", "skipped repeat")], ["request", "retry"])
        self.assertEqual(result.boards["a"]["status"], "ok")

    def test_L9_duplicate_request_is_skipped(self):
        """L9, GATE.md wrong version 5 (second half) and Repeat rule. SIMULATED: the same board URL
        listed twice; the second is skipped, the trace says "skipped repeat", one call is made."""
        boards = [gh_board("stripe"), gh_board("stripe-again", slug="stripe")]
        result, t = self.run_loop(boards, {GH.format("stripe"): [(200, OK_B)]})
        self.assertEqual(len(t.calls), 1)
        self.assertEqual(len(self.observations(result, "stripe-again", "skipped repeat")), 1)
        self.assertEqual(result.boards["stripe-again"]["status"], "skipped repeat")


class State(LoopCase):
    def test_L10_failed_board_is_not_filled_from_previous_run(self):
        """L10, GATE.md wrong version 8. SIMULATED: the previous state has board b's ids and b fails
        this run; b's ids are unchanged, the report shows no postings or new ids for b, and the trace
        has no "parsed" observation for b."""
        self.write_state({"a": ["1"], "b": ["11", "12"]})
        result, _ = self.run_loop([gh_board("a"), gh_board("b")],
                                  {GH.format("a"): [(200, OK_A)], GH.format("b"): [(503, b"")]})
        self.assertEqual(result.boards["b"]["status"], "failed")
        self.assertEqual(result.boards["b"]["postings"], [])
        self.assertEqual(result.boards["b"]["new_ids"], [])
        self.assertEqual(result.boards["b"].get("new", []), [])
        self.assertEqual(self.observations(result, "b", "parsed"), [])
        self.assertEqual(self.read_state()["b"], ["11", "12"])

    def test_L11_all_boards_ok_is_finished(self):
        """L11, GATE.md Exits (finished). SIMULATED: all boards ok -> finished. The first run is a
        baseline (0 new, marked baseline); the next run reports the ids that are new since then."""
        boards = [gh_board("a"), gh_board("b"), ashby_board("c")]
        script = {GH.format("a"): [(200, OK_A)], GH.format("b"): [(200, OK_B)], ASHBY.format("c"): [(200, OK_C)]}
        first, _ = self.run_loop(boards, script)
        self.assertEqual(first.exit, "finished")
        for name in ("a", "b", "c"):
            self.assertEqual(first.boards[name]["status"], "ok")
            self.assertTrue(first.boards[name]["baseline"])
            self.assertEqual(first.boards[name]["new_ids"], [])
        self.assertEqual(sorted(self.read_state()["a"]), ["1", "2"])

        script[GH.format("a")] = [(200, gh_body((1, "Data Engineer", "Boston, Massachusetts"),
                                                (2, "Senior Data Scientist", "Remote - US"),
                                                (3, "ML Engineer", "Remote - US")))]
        second, _ = self.run_loop(boards, script)
        self.assertEqual(second.exit, "finished")
        self.assertFalse(second.boards["a"]["baseline"])
        self.assertEqual(second.boards["a"]["new_ids"], ["3"])
        self.assertEqual(second.boards["b"]["new_ids"], [])
        self.assertEqual(sorted(self.read_state()["a"]), ["1", "2", "3"])

    def test_L12_unreadable_state_or_invalid_persona_is_error(self):
        """L12, GATE.md Exits (error: unreadable state file, invalid persona). SIMULATED transport,
        never called: exit error, no request sent, state unchanged."""
        script = {GH.format("a"): [(200, OK_A)]}
        self.state_file.write_text("not json {", encoding="utf-8")
        before = self.state_file.read_bytes()
        result, t = self.run_loop([gh_board("a")], script)
        self.assertEqual(result.exit, "error")
        self.assertTrue(result.error)
        self.assertEqual(t.calls, [])
        self.assertEqual(self.state_file.read_bytes(), before)

        before = self.write_state({"a": ["1"]})
        resume = self.root / "persona" / "priya-nair.resume.example.json"
        data = json.loads(resume.read_text(encoding="utf-8"))
        data["_comment"] = "a real résumé"
        resume.write_text(json.dumps(data), encoding="utf-8")
        result, t = self.run_loop([gh_board("a")], script)
        self.assertEqual(result.exit, "error")
        self.assertTrue(result.error)
        self.assertEqual(t.calls, [])
        self.assertEqual(self.state_file.read_bytes(), before)


class TraceAndPolicy(LoopCase):
    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in (self.root / "runs").rglob("*") if p.is_file()}

    def test_L13_every_call_traced_and_saved_never_overwritten(self):
        """L13, GATE.md Evidence and wrong version 10. SIMULATED: every transport call has exactly
        one trace observation with url, status, bytes and sha256; each response is saved in a new raw
        file under runs/<run id>/, and the trace too; a second run writes new files and overwrites
        nothing; reusing a run id is refused, ends in error, and changes nothing."""
        boards = [gh_board("a"), gh_board("b")]
        script = {GH.format("a"): [TIMEOUT, (200, OK_A)], GH.format("b"): [(404, b'{"status":404}')]}
        result, t = self.run_loop(boards, script, run_id="run1")
        calls = [o for o in result.trace if o["action"] in ("request", "retry")]
        self.assertEqual([o["url"] for o in calls], [url for url, _ in t.calls])
        self.assertEqual([o["seq"] for o in result.trace], list(range(1, len(result.trace) + 1)))
        run_dir = (self.root / "runs" / "run1").resolve()
        for o in calls:
            for key in ("seq", "t", "board", "action", "url", "status", "bytes", "sha256", "raw_file", "outcome"):
                self.assertIn(key, o)
            if o["status"] == "timeout":
                self.assertIsNone(o["raw_file"])
                continue
            raw = (self.root / o["raw_file"]).resolve()
            self.assertEqual(raw.parent, run_dir)
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), o["sha256"])
            self.assertEqual(len(raw.read_bytes()), o["bytes"])
        saved = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["exit"], result.exit)
        self.assertEqual(saved["trace"], result.trace)

        first_files = self.snapshot()
        self.run_loop(boards, script, run_id="run2")
        after = self.snapshot()
        self.assertEqual({k: after[k] for k in first_files}, first_files)
        self.assertTrue(any(k.startswith("runs/run2/") for k in after))

        state_before = self.state_file.read_bytes()
        files_before = self.snapshot()
        again, _ = self.run_loop(boards, script, run_id="run1")
        self.assertEqual(again.exit, "error")
        self.assertEqual(self.snapshot(), files_before)
        self.assertEqual(self.state_file.read_bytes(), state_before)

    def test_L14_board_off_the_allow_list_is_refused_by_policy(self):
        """L14, GATE.md Permission policy (Hosts), in the loop. SIMULATED: a board whose URL is on a
        lookalike host is refused by the policy before any call; the board is failed "refused by
        policy"; the allowed board is still fetched."""
        urls = {"greenhouse": "https://boards-api.greenhouse.io.evil.example/v1/boards/{slug}/jobs",
                "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}"}
        result, t = self.run_loop([gh_board("a"), ashby_board("c")], {ASHBY.format("c"): [(200, OK_C)]}, urls=urls)
        self.assertEqual([url for url, _ in t.calls], [ASHBY.format("c")])
        self.assertEqual(result.boards["a"]["status"], "failed")
        self.assertIn("host_not_allowed", result.boards["a"]["reason"])
        self.assertEqual(len(self.observations(result, "a", "refused by policy")), 1)
        self.assertEqual(result.exit, "incomplete")


class GateSync(unittest.TestCase):
    def test_L15_boards_and_budgets_match_gate_md(self):
        """L15, GATE.md Boards table, Budgets and Revision ("Only I can change a budget"): BOARDS,
        BUDGETS, TIMEOUT_SECONDS and RETRY_WAIT_SECONDS in loop.py equal what GATE.md says."""
        gate = (HERE / "GATE.md").read_text(encoding="utf-8")
        table = gate.split("## Boards", 1)[1].split("\n## ", 1)[0]
        rows = [[c.strip() for c in line.strip("|").split("|")] for line in table.splitlines()
                if line.startswith("|") and not line.startswith("|---") and "Endpoint host" not in line]
        self.assertEqual(len(loop.BOARDS), len(rows))
        for board, (name, system, host) in zip(loop.BOARDS, rows):
            with self.subTest(board=board["name"]):
                self.assertEqual(board["system"], system.lower())
                self.assertEqual(loop.board_url(board).split("/")[2], host)
                if name.startswith("Deliberate failure"):
                    self.assertTrue(board.get("deliberate_failure"))
                else:
                    self.assertEqual(board["name"], name.lower())
                    self.assertFalse(board.get("deliberate_failure", False))

        budgets = gate.split("## Budgets", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(loop.BUDGETS, {
            "boards": int(re.search(r"Maximum (\d+) boards", budgets).group(1)),
            "requests": int(re.search(r"Maximum (\d+) requests", budgets).group(1)),
            "seconds": int(re.search(r"Maximum (\d+) seconds", budgets).group(1))})

        revision = gate.split("## Revision (2026-11-04, before any loop code)", 1)[1]
        self.assertEqual(loop.TIMEOUT_SECONDS, int(re.search(r"Per-request timeout: (\d+) seconds", revision).group(1)))
        self.assertEqual(loop.RETRY_WAIT_SECONDS, int(re.search(r"permitted retry: (\d+) seconds", revision).group(1)))


class Parsers(unittest.TestCase):
    def test_P1_greenhouse_parser(self):
        """P1, GATE.md Exits (finished needs a valid, parsed response) and Revision (a valid response
        of the wrong shape is failed). SIMULATED bodies: the normal shape normalizes to id (string),
        title, location, url; invalid JSON, the wrong shape, or a posting without id or title raises
        ParseError; an empty job list parses to no postings."""
        with no_network():
            postings, unlisted = parsers.parse_greenhouse(gh_body((101, "Data Engineer", "Boston, Massachusetts")))
            self.assertEqual(postings, [{"id": "101", "title": "Data Engineer", "location": "Boston, Massachusetts",
                                         "url": "https://example.invalid/gh/101"}])
            self.assertEqual(unlisted, 0)
            self.assertEqual(parsers.parse_greenhouse(gh_body()), ([], 0))
            for bad in (b"<html>not json</html>", b'{"jobs": "none"}', b'{"data": []}', b"[]",
                        json.dumps({"jobs": [{"title": "No id", "location": {"name": "US"}}]}).encode(),
                        json.dumps({"jobs": [{"id": 5, "location": {"name": "US"}}]}).encode()):
                with self.subTest(body=bad[:40]):
                    with self.assertRaises(parsers.ParseError):
                        parsers.parse_greenhouse(bad)

    def test_P2_ashby_parser(self):
        """P2, GATE.md Exits and Revision (wrong shape is failed; Ashby isListed and
        secondaryLocations). SIMULATED bodies: string ids stay strings, jobUrl becomes url; invalid
        JSON, the wrong shape, or a posting without id or title raises ParseError."""
        with no_network():
            postings, unlisted = parsers.parse_ashby(ashby_body(
                ashby_job("6f1c-uuid", "Data Engineer", "San Francisco, CA")))
            self.assertEqual(postings, [{"id": "6f1c-uuid", "title": "Data Engineer",
                                         "location": "San Francisco, CA",
                                         "url": "https://example.invalid/ashby/6f1c-uuid"}])
            self.assertEqual(unlisted, 0)
            self.assertEqual(parsers.parse_ashby(ashby_body()), ([], 0))
            for bad in (b"not json", b'{"apiVersion": "1", "jobs": {}}', b'{"apiVersion": "1"}',
                        ashby_body({"title": "No id", "location": "US", "isListed": True}),
                        ashby_body({"id": "x", "location": "US", "isListed": True})):
                with self.subTest(body=bad[:40]):
                    with self.assertRaises(parsers.ParseError):
                        parsers.parse_ashby(bad)


class Revision(LoopCase):
    def test_R1_exit_precedence(self):
        """R1, GATE.md Revision (exit precedence: error > budget-exhausted > incomplete > finished).
        SIMULATED: an empty board beside ok boards -> incomplete; a 404 board plus a requests-budget
        stop -> budget-exhausted; the same plus a SIMULATED bug while saving state -> error, with
        the error reported and the state unchanged."""
        result, _ = self.run_loop([gh_board("a"), gh_board("e")],
                                  {GH.format("a"): [(200, OK_A)], GH.format("e"): [(200, gh_body())]})
        self.assertEqual(result.exit, "incomplete")

        boards = [gh_board("bad"), gh_board("b"), gh_board("c")]
        script = {GH.format("bad"): [(404, b"")], GH.format("b"): [(200, OK_B)], GH.format("c"): [(200, OK_A)]}
        result, _ = self.run_loop(boards, script, budgets=dict(WIDE, requests=2))
        self.assertEqual(result.exit, "budget-exhausted")
        self.assertEqual(result.boards["bad"]["status"], "failed")

        class BrokenStatePolicy(policy.Policy):
            def write_state(self, data):
                raise RuntimeError("SIMULATED bug while saving state")

        before = self.write_state({"b": ["99"]})
        result, _ = self.run_loop(boards, script, budgets=dict(WIDE, requests=2),
                                  policy_obj=BrokenStatePolicy(self.root))
        self.assertEqual(result.exit, "error")
        self.assertIn("SIMULATED bug while saving state", result.error)
        self.assertEqual(self.state_file.read_bytes(), before)

    def test_R2_timeout_and_retry_wait(self):
        """R2, GATE.md Revision (per-request timeout 15 s, or the seconds left if fewer; 2 s wait
        before the one retry). SIMULATED, fake clock: the first request gets 15 s; a request at
        t = 50 of a 60 s budget gets 10 s; a timeout is followed by exactly one 2 s wait, then the
        retry at t + 2. Nothing really waits."""
        started = time.monotonic()
        boards = [gh_board("a"), gh_board("b")]
        result, t = self.run_loop(boards, {GH.format("a"): [(200, OK_A)], GH.format("b"): [(200, OK_B)]},
                                  budgets=dict(WIDE, seconds=60), cost=50.0)
        self.assertEqual(t.calls[0], (GH.format("a"), 15))
        self.assertEqual(t.calls[1][0], GH.format("b"))
        self.assertAlmostEqual(t.calls[1][1], 10)

        self.clock = FakeClock()
        result, t = self.run_loop([gh_board("s")], {GH.format("s"): [TIMEOUT, (200, OK_A)]})
        self.assertEqual(self.clock.sleeps, [2])
        retry = self.observations(result, "s", "retry")
        self.assertEqual(len(retry), 1)
        self.assertAlmostEqual(retry[0]["t"], 2)
        self.assertLess(time.monotonic() - started, 1.0)

    def test_R3_other_failures_are_failed_without_retry(self):
        """R3, GATE.md Revision (other 4xx such as 403 or 429, invalid JSON, or a valid response of
        the wrong shape: failed, no retry). SIMULATED: each makes exactly 1 request, no wait, and the
        board is failed."""
        cases = {"forbidden": (gh_board("forbidden"), GH.format("forbidden"), (403, b"")),
                 "limited": (gh_board("limited"), GH.format("limited"), (429, b"")),
                 "not-json": (gh_board("not-json"), GH.format("not-json"), (200, b"<html>not json</html>")),
                 "gh-shape": (gh_board("gh-shape"), GH.format("gh-shape"), (200, b'{"jobs": "none"}')),
                 "ashby-shape": (ashby_board("ashby-shape"), ASHBY.format("ashby-shape"),
                                 (200, b'{"apiVersion": "1", "jobs": {}}'))}
        result, t = self.run_loop([b for b, _, _ in cases.values()],
                                  {url: [response] for _, url, response in cases.values()})
        for name, (_, url, _) in cases.items():
            with self.subTest(board=name):
                self.assertEqual(t.count(url), 1)
                self.assertEqual(result.boards[name]["status"], "failed")
                self.assertEqual(result.boards[name]["attempts"], 1)
        self.assertEqual(self.clock.sleeps, [])
        self.assertEqual(result.exit, "incomplete")

    def test_R4_ashby_unlisted_skipped_and_secondary_locations_included(self):
        """R4, GATE.md Revision (Ashby: isListed false postings are skipped and counted in the trace;
        secondaryLocations are included in a posting's location). SIMULATED Ashby body."""
        body = ashby_body(ashby_job("p-1", "Data Engineer", "San Francisco, CA", secondary=("New York, NY",)),
                          ashby_job("p-2", "Analytics Engineer", "Remote - US"),
                          ashby_job("p-hidden", "Hidden Role", "Remote - US", listed=False))
        result, _ = self.run_loop([ashby_board("plaid")], {ASHBY.format("plaid"): [(200, body)]})
        board = result.boards["plaid"]
        self.assertEqual(board["status"], "ok")
        self.assertEqual(sorted(p["id"] for p in board["postings"]), ["p-1", "p-2"])
        parsed = self.observations(result, "plaid", "parsed")
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["unlisted_skipped"], 1)
        location = next(p["location"] for p in board["postings"] if p["id"] == "p-1")
        self.assertTrue(location.startswith("San Francisco, CA"))
        self.assertIn("New York, NY", location)

    def test_R5_each_new_posting_gets_the_js1_rule_verdict_as_a_record(self):
        """R5, GATE.md Revision (each new posting gets my JS1 rule's verdict, labeled as a record).
        SIMULATED: with a previous state, each new posting carries rule.judge's record, recomputable
        by hand; old postings and baseline runs carry none; verdicts do not change the exit."""
        self.write_state({"a": ["1"]})
        body = gh_body((1, "Data Engineer", "Boston, Massachusetts"),
                       (2, "Machine Learning Engineer", "Remote - US"),
                       (3, "Senior Data Scientist", "Remote - US"))
        result, _ = self.run_loop([gh_board("a"), gh_board("b")],
                                  {GH.format("a"): [(200, body)], GH.format("b"): [(200, OK_B)]})
        self.assertEqual(result.exit, "finished")
        new = result.boards["a"]["new"]
        self.assertEqual([p["id"] for p in new], ["2", "3"])
        for posting in new:
            with self.subTest(id=posting["id"]):
                self.assertEqual(posting["judgment"]["source"], "written rule (record)")
                self.assertEqual(posting["judgment"], rule.judge(posting["title"], posting["location"], self.targets))
        self.assertEqual([p["judgment"]["verdict"] for p in new], [rule.RELEVANT, rule.NOT_RELEVANT])
        self.assertTrue(result.boards["b"]["baseline"])
        self.assertEqual(result.boards["b"]["new"], [])


if __name__ == "__main__":
    unittest.main()
