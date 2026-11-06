"""The JS2 loop (GATE.md v0.2 §1-§4, §6; CONTRACT.md v0.5 items 3-8, v0.6 items 1-2).

Every test builds its own project folder in a temporary directory, with
constructed board bodies (not real postings). The tool layer's _send is
replaced by a script keyed by URL, and any socket would fail the test, so no
request leaves the process. A fake clock drives the time budget.
"""

import io
import json
import shutil
import socket
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from support import JS1, persona

from agent import run as run_module
from agent import tool_layer
from agent.adapters import ashby, greenhouse
from agent.config import Board, parse_config
from agent.fetch import utc_stamp
from agent.policy import Policy, PolicyRefusal
from agent.rule import clean_content, judge, posting_field
from agent.run import JUDGE_LINE, Loop, run
from agent.state import STATE_NAME
from agent.tool_layer import ToolLayer

GH, AS = "greenhouse", "ashby"
FIVE = [(GH, "stripe"), (AS, "notion"), (GH, "duolingo"), (GH, "robinhood"), (AS, "js2nosuchboard")]
BASE = datetime(2026, 11, 6, 12, 0, 0, tzinfo=timezone.utc)


def url(ats, name):
    return Board(ats, name).url


def gh_job(job_id, title="Product Manager", location="New York", content="Python and SQL"):
    return {"id": job_id, "title": title, "location": {"name": location}, "content": content,
            "absolute_url": f"https://example.invalid/gh/{job_id}"}


def gh_body(*jobs):
    return json.dumps({"jobs": list(jobs), "meta": {"total": len(jobs)}}).encode()


def ashby_job(job_id, title="Product Manager", location="New York, New York", secondaries=(),
              plain="Python and SQL", **extra):
    job = {"id": job_id, "title": title, "location": location,
           "secondaryLocations": [{"location": s, "address": {}} for s in secondaries],
           "descriptionPlain": plain, "descriptionHtml": "<p>constructed</p>",
           "jobUrl": f"https://example.invalid/ashby/{job_id}", "isRemote": False, "workplaceType": "OnSite"}
    job.update(extra)
    return job


def ashby_body(*jobs):
    return json.dumps({"jobs": list(jobs), "apiVersion": "1"}).encode()


def ok(body, advance=0.1):
    return {"kind": "status", "status": 200, "body": body, "advance": advance}


def status(code, body=b"", advance=0.1, **headers):
    return {"kind": "status", "status": code, "body": body, "advance": advance, "headers": headers}


def timeout(advance=0.1):
    return {"kind": "timeout", "advance": advance}


def connection(advance=0.1):
    return {"kind": "connection", "advance": advance}


NOT_FOUND_ASHBY = status(404, b"Not Found", **{"Content-Type": "text/plain; charset=utf-8"})


class _Response:
    def __init__(self, code, body, headers):
        self.status, self._body, self.headers = code, body, headers

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


class LoopCase(unittest.TestCase):
    boards = FIVE

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        shutil.copy(JS1 / "resume_persona.json", self.root / "resume_persona.json")
        (self.root / "evidence" / "snapshots").mkdir(parents=True)
        self.write_config(self.boards)
        self.script, self.sent, self.clock, self.calls = {}, [], Clock(), 0
        for patcher in (mock.patch.object(tool_layer, "_send", self.fake_send),
                        mock.patch.object(socket, "create_connection",
                                          mock.Mock(side_effect=AssertionError("a socket would have been opened")))):
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_config(self, boards, **changes):
        config = {
            "boards": [{"ats": ats, "name": name} for ats, name in boards],
            "allow_list": ["boards-api.greenhouse.io", "api.ashbyhq.com"],
            "resume_path": "resume_persona.json",
            "state_dir": "state",
            "evidence_dir": "evidence",
            "output_dir": "output",
        }
        config.update(changes)
        (self.root / "config.json").write_text(json.dumps(config), encoding="utf-8")

    def now(self):
        moment = BASE + timedelta(seconds=self.calls)
        self.calls += 1
        return moment

    def fake_send(self, request, timeout):
        self.sent.append(request.full_url)
        steps = self.script.get(request.full_url)
        if not steps:
            raise AssertionError(f"unscripted request {request.full_url}")
        step = steps.pop(0)
        self.clock.t += step.get("advance", 0.1)
        if step["kind"] == "timeout":
            raise TimeoutError("timed out")
        if step["kind"] == "connection":
            raise urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))
        if step["kind"] == "interrupt":
            raise KeyboardInterrupt
        headers = {"Content-Type": "application/json", **step.get("headers", {})}
        if 200 <= step["status"] < 300:
            return _Response(step["status"], step["body"], headers)
        raise urllib.error.HTTPError(request.full_url, step["status"], "constructed", headers, io.BytesIO(step["body"]))

    def on(self, ats, name, *steps):
        self.script.setdefault(url(ats, name), []).extend(steps)

    def all_ok(self, stripe=(1,), duolingo=(2,), robinhood=(3,), notion=("n-1",)):
        self.on(GH, "stripe", ok(gh_body(*map(gh_job, stripe))))
        self.on(AS, "notion", ok(ashby_body(*map(ashby_job, notion))))
        self.on(GH, "duolingo", ok(gh_body(*map(gh_job, duolingo))))
        self.on(GH, "robinhood", ok(gh_body(*map(gh_job, robinhood))))
        self.on(AS, "js2nosuchboard", NOT_FOUND_ASHBY)

    def go(self, seeds=None, approvals=()):
        return run(self.root / "config.json", seeds=seeds, approvals=approvals, clock=self.clock, now=self.now)

    def write_state(self, name, sections):
        (self.root / "state").mkdir(exist_ok=True)
        (self.root / "state" / name).write_text(json.dumps(sections), encoding="utf-8")

    def state_files(self):
        folder = self.root / "state"
        return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []

    def newest_state(self):
        names = [n for n in self.state_files() if STATE_NAME.fullmatch(n)]
        return json.loads((self.root / "state" / names[-1]).read_text(encoding="utf-8")) if names else None

    def line(self, report, key):
        return next(line for line in report["boards"] if line["board"] == key)

    def tree(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}


# ---- GATE.md §6: W3 and W4.

class WrongVersions(LoopCase):
    def test_W3_failed_board_is_not_laundered_into_an_empty_board(self):
        self.write_state("state_2026-11-01T000000Z.json", {"ashby:js2nosuchboard": ["kept"]})
        self.all_ok()
        report = self.go()
        line = self.line(report, "ashby:js2nosuchboard")
        self.assertEqual((line["status"], line["reason"], line["attempts"]), ("failed", "not found (404)", 1))
        self.assertTrue(line["line"].startswith("failed — not found (404)"))
        for key in ("jobs_fetched", "new_ids", "new_postings"):
            self.assertNotIn(key, line)
        self.assertEqual(self.newest_state()["ashby:js2nosuchboard"], ["kept"])
        self.assertEqual(report["exit"]["kind"], "finished")
        self.assertEqual(report["exit"]["line"], "finished — with failures: ashby:js2nosuchboard")

    def test_W4_same_id_on_two_boards_is_new_on_each(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:duolingo": [], "greenhouse:robinhood": []})
        self.all_ok(duolingo=(777,), robinhood=(777,))
        report = self.go()
        for key in ("greenhouse:duolingo", "greenhouse:robinhood"):
            with self.subTest(board=key):
                line = self.line(report, key)
                self.assertEqual(line["new_ids"], ["777"])
                self.assertEqual([r["posting_id"] for r in line["new_postings"]], ["777"])
        state = self.newest_state()
        self.assertEqual((state["greenhouse:duolingo"], state["greenhouse:robinhood"]), (["777"], ["777"]))


# ---- CONTRACT v0.5 item 8: the seven known consequences, and v0.5 item 3's step 4 only.

class KnownConsequences(unittest.TestCase):
    def conditions(self, posting):
        return judge(posting, persona())[1]["conditions"]

    def test_c2_passes_on_a_secondary_location_alone(self):
        posting = ashby(ashby_body(ashby_job("a", location="San Francisco, California", secondaries=[" New York, New York "])))[0]
        self.assertEqual(posting["location"]["name"], "San Francisco, California; New York, New York")
        self.assertTrue(self.conditions(posting)["C2"]["result"])

    def test_isremote_alone_never_passes_c2(self):
        posting = ashby(ashby_body(ashby_job("a", location="San Francisco, California", isRemote=True)))[0]
        self.assertFalse(self.conditions(posting)["C2"]["result"])

    def test_workplacetype_remote_with_a_city_fails_c2(self):
        posting = ashby(ashby_body(ashby_job("a", location="San Francisco, California", workplaceType="Remote")))[0]
        self.assertFalse(self.conditions(posting)["C2"]["result"])

    def test_remote_dash_california_passes_c2_by_substring(self):
        posting = greenhouse(gh_body(gh_job(1, location="Remote - California")))[0]
        self.assertTrue(self.conditions(posting)["C2"]["result"])

    def test_skill_split_across_a_line_break_still_matches(self):
        posting = ashby(ashby_body(ashby_job("a", plain="Experience with A/B\ntesting and\n\nPython.")))[0]
        c3 = self.conditions(posting)["C3"]
        self.assertIn("A/B testing", c3["matched_resume_values"])
        self.assertTrue(c3["result"])

    def test_same_id_on_two_boards_is_two_postings(self):
        """Pinned by WrongVersions.test_W4_same_id_on_two_boards_is_new_on_each (GATE.md §6)."""
        self.assertTrue(hasattr(WrongVersions, "test_W4_same_id_on_two_boards_is_new_on_each"))

    def test_ashby_content_gets_step_4_only(self):
        """Prasad, CP5b: "&amp;" and a "<b>" span stay as written in Ashby; Greenhouse unescapes and strips (JS1)."""
        text = "Python &amp;  SQL\n<b>roadmapping</b>"
        ashby_posting = ashby(ashby_body(ashby_job("a", plain=text)))[0]
        gh_posting = greenhouse(gh_body(gh_job(1, content=text)))[0]
        self.assertEqual(posting_field(ashby_posting, "content"), "Python &amp; SQL <b>roadmapping</b>")
        self.assertEqual(posting_field(gh_posting, "content"), "Python & SQL roadmapping ")
        self.assertEqual(posting_field(gh_posting, "content"), clean_content(text))


class AshbyNotFound(LoopCase):
    boards = [(AS, "js2nosuchboard")]

    def test_status_is_checked_before_the_body(self):
        """v0.5 item 8: a plain-text 404, and even a 404 whose body looks like an empty job list, is failed."""
        for body in (b"Not Found", b'{"jobs": []}'):
            with self.subTest(body=body):
                self.on(AS, "js2nosuchboard", status(404, body))
                line = self.line(self.go(), "ashby:js2nosuchboard")
                self.assertEqual((line["status"], line["reason"]), ("failed", "not found (404)"))
                self.assertNotIn("jobs_fetched", line)


# ---- GATE.md §1: every exit.

class Exits(LoopCase):
    def test_finished_plain_when_every_board_succeeds(self):
        self.write_config(FIVE[:4])
        self.all_ok()
        report = self.go()
        self.assertEqual(report["exit"]["line"], "finished")
        self.assertEqual(report["exit"]["failed_boards"], [])

    def test_finished_with_failures_names_the_failed_board(self):
        self.all_ok()
        report = self.go()
        self.assertEqual(report["exit"]["line"], "finished — with failures: ashby:js2nosuchboard")
        self.assertEqual(len(report["exit"]["completed_boards"]), 5)

    def test_incomplete_on_operator_interrupt(self):
        self.all_ok()
        self.script[url(AS, "notion")] = [{"kind": "interrupt"}]
        report = self.go()
        self.assertEqual(report["exit"]["line"], "incomplete — operator interrupt")
        self.assertEqual(report["exit"]["completed_boards"], ["greenhouse:stripe"])
        self.assertEqual(report["exit"]["not_completed_boards"], ["ashby:notion"])
        self.assertEqual(report["exit"]["not_attempted_boards"],
                         ["greenhouse:duolingo", "greenhouse:robinhood", "ashby:js2nosuchboard"])
        self.assertEqual(sorted(self.newest_state()), ["greenhouse:stripe"])

    def test_incomplete_when_a_required_write_is_refused(self):
        self.all_ok()
        # The first attempt's evidence name; it already exists, and overwriting needs approval.
        taken = self.root / "evidence" / f"greenhouse_stripe_{utc_stamp(BASE + timedelta(seconds=1))}_a1.json"
        taken.write_bytes(b"already here")
        report = self.go()
        self.assertEqual(report["exit"]["kind"], "incomplete")
        self.assertIn("a required write was refused", report["exit"]["line"])
        self.assertEqual(taken.read_bytes(), b"already here")
        self.assertEqual(self.line(report, "greenhouse:stripe")["status"], "not completed")
        self.assertEqual(self.newest_state(), {})

    def test_error_mid_loop_keeps_completed_boards(self):
        self.all_ok()
        real = run_module.save_evidence

        def failing(tools, evidence_dir, board, *args, **kwargs):
            if board.key == "ashby:notion":
                raise OSError("disk full (constructed)")
            return real(tools, evidence_dir, board, *args, **kwargs)

        with mock.patch.object(run_module, "save_evidence", failing):
            report = self.go()
        self.assertEqual(report["exit"]["line"], "error — disk full (constructed)")
        self.assertEqual(self.line(report, "ashby:notion")["status"], "not completed")
        self.assertEqual(sorted(self.newest_state()), ["greenhouse:stripe"])

    def test_error_on_a_corrupt_newest_state_file(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:stripe": ["1"]})
        (self.root / "state" / "state_2026-11-02T000000Z.json").write_text("{not json", encoding="utf-8")
        report = self.go()
        self.assertEqual(report["exit"]["kind"], "error")
        self.assertIn("state_2026-11-02T000000Z.json", report["exit"]["line"])
        self.assertEqual(self.sent, [])
        self.assertEqual(self.state_files(), ["state_2026-11-01T000000Z.json", "state_2026-11-02T000000Z.json"])
        self.assertTrue((self.root / report["report_file"]).is_file())

    def test_error_on_a_budget_in_the_config(self):
        self.write_config(FIVE, max_requests=20)
        report = self.go()
        self.assertEqual(report["exit"]["kind"], "error")
        self.assertIn("GATE.md §5", report["exit"]["line"])
        self.assertEqual(self.sent, [])

    def test_error_on_a_board_listed_twice(self):
        self.write_config(FIVE + [(GH, "stripe")])
        report = self.go()
        self.assertEqual(report["exit"]["line"], "error — invalid config config.json: board greenhouse:stripe is listed twice")
        self.assertEqual(self.sent, [])

    def test_refused_before_any_fetch_or_write(self):
        cases = {
            "extra host": (FIVE, dict(allow_list=["boards-api.greenhouse.io", "api.ashbyhq.com", "evil.example"])),
            "output into snapshots": (FIVE, dict(output_dir="evidence/snapshots")),
            "evidence outside the folder": (FIVE, dict(evidence_dir="../elsewhere")),
            "board name off the URL form": ([(GH, "../stripe")], {}),
        }
        for label, (boards, change) in cases.items():
            with self.subTest(case=label):
                self.write_config(boards, **change)
                before = self.tree()
                report = self.go()
                self.assertEqual(report["exit"]["kind"], "refused", report["exit"]["line"])
                self.assertEqual(self.sent, [])
                self.assertEqual(self.tree(), before)
                self.assertIsNone(report["report_file"])


# ---- GATE.md §2: budgets.

class Budgets(LoopCase):
    def test_worst_case_fits_the_request_budget_exactly(self):
        for ats, name in FIVE:
            self.on(ats, name, timeout(), timeout())
        report = self.go()
        self.assertEqual(report["budgets"]["requests"], {"used": 10, "max": 10})
        self.assertEqual(report["exit"]["kind"], "finished")
        self.assertEqual(len(report["exit"]["failed_boards"]), 5)

    def test_request_budget_stops_the_retry(self):
        for ats, name in FIVE:
            self.on(ats, name, timeout(), timeout())
        with mock.patch.multiple(run_module, MAX_REQUESTS=3, BUDGET_LIMITS={"boards": 5, "requests": 3, "seconds": 60}):
            report = self.go()
        notion = self.line(report, "ashby:notion")
        self.assertEqual(notion["line"], "not completed — timeout on attempt 1; retry not started: requests budget exhausted")
        self.assertEqual(report["exit"]["line"], "budget-exhausted — requests budget (3 per run) ran out on ashby:notion")
        self.assertEqual(report["exit"]["not_attempted_boards"],
                         ["greenhouse:duolingo", "greenhouse:robinhood", "ashby:js2nosuchboard"])
        self.assertEqual(len(self.sent), 3)

    def test_time_budget_stops_the_retry(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:stripe": [], "ashby:notion": ["old"]})
        self.on(GH, "stripe", ok(gh_body(gh_job(1)), advance=5))
        self.on(AS, "notion", timeout(advance=60))
        report = self.go()
        notion = self.line(report, "ashby:notion")
        self.assertEqual(notion["line"], "not completed — timeout on attempt 1; retry not started: seconds budget exhausted")
        self.assertEqual(report["exit"]["line"], "budget-exhausted — seconds budget (60 per run) ran out on ashby:notion")
        state = self.newest_state()
        self.assertEqual((state["greenhouse:stripe"], state["ashby:notion"]), (["1"], ["old"]))

    def test_time_budget_between_boards(self):
        self.on(GH, "stripe", ok(gh_body(gh_job(1)), advance=61))
        report = self.go()
        self.assertEqual(report["exit"]["line"], "budget-exhausted — seconds budget (60 per run) ran out on ashby:notion")
        self.assertEqual(self.line(report, "greenhouse:stripe")["status"], "ok")
        self.assertEqual(self.line(report, "ashby:notion")["status"], "not attempted")

    def test_board_budget(self):
        self.write_config(FIVE + [(GH, "extra")])
        self.all_ok()
        report = self.go()
        self.assertEqual(report["exit"]["line"], "budget-exhausted — boards budget (5 per run) ran out on greenhouse:extra")
        self.assertEqual(self.line(report, "greenhouse:extra")["status"], "not attempted")
        self.assertNotIn(url(GH, "extra"), self.sent)


# ---- GATE.md §4: retry and no retry, evidence per attempt (v0.5 item 5; Prasad, CP5b).

class ErrorPolicy(LoopCase):
    boards = [(GH, "stripe")]

    def test_timeout_then_ok_retries_once(self):
        self.on(GH, "stripe", timeout(), ok(gh_body(gh_job(1))))
        report = self.go()
        line = self.line(report, "greenhouse:stripe")
        self.assertEqual((line["status"], line["attempts"]), ("ok", 2))
        self.assertEqual([(t["attempt"], t.get("status"), t["saved"]) for t in report["trace"]],
                         [(1, None, None), (2, 200, report["trace"][1]["saved"])])
        evidence = sorted(p.name for p in (self.root / "evidence").iterdir() if p.is_file())
        self.assertEqual(len([n for n in evidence if "_a1" in n]), 1)  # timeout: sidecar only
        self.assertTrue(all(n.endswith(".sidecar.json") for n in evidence if "_a1" in n))
        self.assertEqual(len([n for n in evidence if "_a2" in n]), 2)  # body and sidecar
        sidecar = json.loads((self.root / "evidence" / report["trace"][1]["sidecar"]).read_text(encoding="utf-8"))
        self.assertEqual((sidecar["status"], sidecar["url"], sidecar["fetched_at"]),
                         (200, url(GH, "stripe"), (BASE + timedelta(seconds=2)).isoformat(timespec="seconds")))

    def test_retryable_failures(self):
        cases = [
            ((timeout(), timeout()), "failed", "timeout after 2 attempts"),
            ((status(503), status(502)), "failed", "5xx / connection error after 2 attempts"),
            ((connection(), connection()), "failed", "5xx / connection error after 2 attempts"),
            ((connection(), ok(gh_body(gh_job(1)))), "ok", ""),
            ((status(500), ok(gh_body(gh_job(1)))), "ok", ""),
        ]
        for steps, expect_status, expect_reason in cases:
            with self.subTest(steps=[s["kind"] + str(s.get("status", "")) for s in steps]):
                self.sent.clear()
                self.on(GH, "stripe", *steps)
                line = self.line(self.go(), "greenhouse:stripe")
                self.assertEqual((line["status"], line.get("reason", ""), line["attempts"]), (expect_status, expect_reason, 2))
                self.assertEqual(len(self.sent), 2)

    def test_no_retry(self):
        cases = [
            (status(404, b'{"status":404,"error":"Job not found"}'), "not found (404)"),
            (status(301, Location="https://evil.example/"), "redirect refused"),
            (ok(b"<html>not json</html>"), "unexpected shape"),
            (ok(b'{"jobs": [{"title": "no id"}]}'), "unexpected shape"),
            (status(429), "HTTP 429"),
            (status(403), "HTTP 403"),
            (status(204), "HTTP 204"),
        ]
        for step, reason in cases:
            with self.subTest(reason=reason, status=step["status"]):
                self.sent.clear()
                self.on(GH, "stripe", step)
                report = self.go()
                line = self.line(report, "greenhouse:stripe")
                self.assertEqual((line["status"], line["reason"], line["attempts"]), ("failed", reason, 1))
                self.assertEqual(len(self.sent), 1)
                self.assertIsNotNone(report["trace"][-1]["saved"])  # a response with a status is saved
        self.assertEqual(report["exit"]["line"], "finished — with failures: greenhouse:stripe")

    def test_redirect_location_is_recorded_not_followed(self):
        self.on(GH, "stripe", status(302, Location="https://evil.example/jobs"))
        report = self.go()
        self.assertEqual(report["trace"][0]["location"], "https://evil.example/jobs")
        self.assertEqual(self.sent, [url(GH, "stripe")])


class ZeroJobs(LoopCase):
    boards = [(GH, "stripe")]

    def test_zero_jobs_is_ok_and_keeps_saved_ids(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:stripe": ["1", "2"]})
        self.on(GH, "stripe", ok(gh_body()))
        report = self.go()
        line = self.line(report, "greenhouse:stripe")
        self.assertEqual((line["status"], line["line"]), ("ok", "ok — 0 jobs, 0 new"))
        self.assertEqual(self.newest_state(), {"greenhouse:stripe": ["1", "2"]})
        self.assertEqual(report["exit"]["line"], "finished")

    def test_zero_jobs_at_baseline_saves_nothing(self):
        """§4 as written, no empty-board guard: no ids to keep, so the board stays without a section."""
        self.on(GH, "stripe", ok(gh_body()))
        self.go()
        self.assertEqual(self.newest_state(), {})


# ---- GATE.md §3: repeat versus retry, at the loop level.

class RepeatRule(LoopCase):
    def loop(self):
        config = parse_config((self.root / "config.json").read_bytes())
        tools = ToolLayer(Policy(self.root, config.board_pairs))
        return Loop(tools, config, persona(), None, {}, self.clock, self.now, self.clock()), config

    def test_retry_executes_and_a_repeat_does_not(self):
        loop, config = self.loop()
        board = config.boards[0]
        self.on(GH, "stripe", timeout(), ok(gh_body(gh_job(1))))
        first = loop.fetch_board(board)
        self.assertEqual((first.status, first.attempts, first.repeat, loop.requests), ("ok", 2, False, 2))
        again = loop.fetch_board(board)
        self.assertEqual((again.status, again.attempts, again.repeat, loop.requests), ("ok", 2, True, 2))
        self.assertEqual(len(self.sent), 2)
        self.assertEqual(loop.trace[-1]["note"], "repeat — not re-run")

    def test_a_final_failure_is_repeated_not_refetched(self):
        loop, config = self.loop()
        board = config.boards[4]
        self.on(AS, "js2nosuchboard", NOT_FOUND_ASHBY)
        loop.fetch_board(board)
        again = loop.fetch_board(board)
        self.assertEqual((again.status, again.reason, again.repeat), ("failed", "not found (404)", True))
        self.assertEqual(len(self.sent), 1)

    def test_same_write_is_not_rerun(self):
        tools = ToolLayer(Policy(self.root, []))
        first = tools.write("output/x.json", b"same")
        self.assertIs(tools.write("output/x.json", b"same"), first)
        self.assertEqual(tools.repeats, [{"tool": "write", "path": "output/x.json", "note": "repeat — not re-run"}])
        with self.assertRaises(PolicyRefusal):
            tools.write("output/x.json", b"different")
        self.assertEqual((self.root / "output" / "x.json").read_bytes(), b"same")


# ---- CONTRACT v0.6 items 1-2: state.

class State(LoopCase):
    boards = [(GH, "stripe")]

    def test_baseline_then_the_diff(self):
        self.on(GH, "stripe", ok(gh_body(gh_job(1), gh_job(2))))
        first = self.line(self.go(), "greenhouse:stripe")
        self.assertEqual((first["baseline"], first["new_ids"], first["line"]), (True, [], "ok — 2 jobs, 0 new (baseline)"))
        self.on(GH, "stripe", ok(gh_body(gh_job(1), gh_job(2), gh_job(3))))
        second = self.line(self.go(), "greenhouse:stripe")
        self.assertEqual((second["baseline"], second["new_ids"], second["already_seen"]), (False, ["3"], 2))
        self.assertEqual(len([n for n in self.state_files() if STATE_NAME.fullmatch(n)]), 2)

    def test_newest_state_is_read_and_temporary_files_are_ignored(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:stripe": ["1"]})
        self.write_state("state_2026-11-03T000000Z.json", {"greenhouse:stripe": ["1", "2"]})
        (self.root / "state" / "state_2026-11-09T000000Z.json.tmp").write_text("{half", encoding="utf-8")
        (self.root / "state" / "notes.txt").write_text("not state", encoding="utf-8")
        self.on(GH, "stripe", ok(gh_body(gh_job(1), gh_job(2), gh_job(3))))
        report = self.go()
        self.assertEqual(report["state"]["read"], "state/state_2026-11-03T000000Z.json")
        self.assertEqual(self.line(report, "greenhouse:stripe")["new_ids"], ["3"])

    def test_state_is_moved_into_place_after_the_report(self):
        self.on(GH, "stripe", ok(gh_body(gh_job(1))))
        report = self.go()
        self.assertEqual(report["state"]["written"], f"state/state_{utc_stamp(BASE)}.json")
        self.assertFalse([n for n in self.state_files() if n.endswith(".tmp")])

    def test_no_report_means_the_state_stays_temporary(self):
        (self.root / "output").mkdir()
        (self.root / "output" / f"run_report_{utc_stamp(BASE)}.json").write_text("taken", encoding="utf-8")
        self.on(GH, "stripe", ok(gh_body(gh_job(1))))
        report = self.go()
        self.assertIsNone(report["report_file"])
        self.assertEqual(self.state_files(), [f"state_{utc_stamp(BASE)}.json.tmp"])
        self.assertIsNone(self.newest_state())


# ---- Report: the judge line (v0.5 item 7), the trace, budgets and approvals (GATE.md §1, §5).

class Report(LoopCase):
    def test_every_new_posting_carries_the_exact_judge_line(self):
        self.write_state("state_2026-11-01T000000Z.json", {"greenhouse:stripe": [], "ashby:notion": []})
        self.all_ok(stripe=(1, 2), notion=("n-1",))
        report = self.go()
        records = [r for line in report["boards"] for r in line.get("new_postings", [])]
        self.assertEqual(len(records), 3)
        for record in records:
            self.assertEqual(record["claude_line"], "rejected — no saved reply (judge not run in JS2)")
            self.assertEqual(record["claude_line"], JUDGE_LINE)
            self.assertEqual((record["claude_verdict"], record["claude_verdict_label"]), ("rejected", "judgment (Claude)"))

    def test_report_holds_trace_budgets_and_approvals(self):
        self.all_ok()
        report = self.go(approvals=["config.json"])
        written = json.loads((self.root / report["report_file"]).read_text(encoding="utf-8"))
        self.assertEqual(written["exit"], report["exit"])
        self.assertTrue(report["report_file"].startswith("output/run_report_"))
        self.assertEqual(len(report["trace"]), 5)
        for entry in report["trace"]:
            self.assertLessEqual({"board", "attempt", "url", "elapsed_s", "saved", "sidecar"}, set(entry))
            self.assertTrue("status" in entry or "error" in entry)
        self.assertEqual(report["budgets"]["boards"], {"used": 5, "max": 5})
        self.assertEqual(report["budgets"]["requests"], {"used": 5, "max": 10})
        self.assertEqual(report["approvals"], [{"flag": "config.json", "path": str(self.root / "config.json"), "used": False}])


# ---- Seeded boards (Prasad's CP5b decision): --seed board_key=path under evidence/.

class Seeded(LoopCase):
    def test_seeded_board_is_marked_and_not_fetched(self):
        (self.root / "evidence" / "snapshots" / "seed.json").write_bytes(gh_body(gh_job(1)))
        self.all_ok()
        del self.script[url(GH, "stripe")]
        report = self.go(seeds={"greenhouse:stripe": "evidence/snapshots/seed.json"})
        stripe = self.line(report, "greenhouse:stripe")
        self.assertEqual((stripe["mode"], stripe["status"], stripe["source"]["file"]), ("seeded", "ok", "snapshots/seed.json"))
        self.assertNotIn(url(GH, "stripe"), self.sent)
        self.assertEqual({line["mode"] for line in report["boards"] if line["board"] != "greenhouse:stripe"}, {"live"})
        self.assertFalse(list((self.root / "evidence").glob("greenhouse_stripe_*")))
        self.assertEqual(report["budgets"]["requests"]["used"], 4)

    def test_seed_outside_evidence_is_refused(self):
        (self.root / "seed.json").write_bytes(gh_body(gh_job(1)))
        report = self.go(seeds={"greenhouse:stripe": "seed.json"})
        self.assertEqual(report["exit"]["kind"], "refused")
        self.assertEqual(self.sent, [])

    def test_seed_for_a_board_not_in_the_config_is_an_error(self):
        (self.root / "evidence" / "snapshots" / "seed.json").write_bytes(gh_body(gh_job(1)))
        report = self.go(seeds={"greenhouse:nosuch": "evidence/snapshots/seed.json"})
        self.assertEqual(report["exit"]["line"], "error — --seed names board greenhouse:nosuch, which is not in the config")


if __name__ == "__main__":
    unittest.main()
