"""Gaps a third independent regrade found on 2026-11-10, written as tests before the fix.

1. A board entry with a bad token (a space) or no token crashed the run; GATE.md section 5 says a
   bad board is recorded and the run goes on.
2. A body cut off mid-read (http.client.IncompleteRead) or an SSL error escaped the transport.
3. A corrupt state file crashed the run before it could end with one of its exits.
4. The check never compared the raw files with the sha256 the trace recorded, so a raw file and
   summary rewritten together passed.
Every response here is CONSTRUCTED; the network is never used (the opener is replaced)."""
import hashlib
import http.client
import json
import pathlib
import ssl
import tempfile
import unittest
from unittest import mock

from jsagent import check, loop, persona, policy, providers, transport
from tests import fakes

FOLDER = pathlib.Path(__file__).resolve().parent.parent
BUDGETS = {"max_boards": 6, "max_requests": 12, "max_seconds": 120}
GH = providers.board_url("greenhouse", "oscar")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = pathlib.Path(self.tmp.name).resolve()
        self.runs = self.project / "runs"
        self.runs.mkdir()
        self.view = persona.public_view(persona.load(FOLDER / "persona" / "alex_morgan.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_loop(self, boards, routes, run_id="r1"):
        return loop.run(boards, BUDGETS, fakes.FakeTransport(routes), policy.Files(self.project, self.runs),
                        run_id=run_id, resume=self.view, clock=fakes.FakeClock())

    def last_trace(self, run_id="r1"):
        return json.loads((self.runs / run_id / "trace.jsonl").read_text().splitlines()[-1])


class BadBoardEntries(Base):
    def check_bad(self, bad):
        rep = self.run_loop([{"name": "oscar", "ats": "greenhouse", "token": "oscar"}, bad], {GH: [fakes.gh(1, 2)]})
        self.assertEqual(rep["exit"], "incomplete")
        self.assertEqual(rep["boards"][0]["status"], "ok", "the good board is still checked")
        b = rep["boards"][1]
        self.assertEqual((b["status"], b["error"], b["fetched"], b["needs_review"]), ("failed", "bad-config", None, True))
        self.assertEqual((self.last_trace()["event"], self.last_trace()["exit"]), ("exit", "incomplete"))

    def test_a_token_with_a_space_fails_that_board_only(self):
        self.check_bad({"name": "bad name", "ats": "lever", "token": "bad name"})

    def test_a_board_with_no_token_fails_that_board_only(self):
        self.check_bad({"name": "no-token", "ats": "lever"})


class CutOffBodies(unittest.TestCase):
    """The Live transport turns a body cut off mid-read, or an SSL failure, into a network error."""

    def live_get_raising(self, exc):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.status, resp.geturl.return_value = 200, GH
        resp.read.side_effect = exc
        opener = mock.Mock()
        opener.open.return_value = resp
        with mock.patch.object(transport.urllib.request, "build_opener", return_value=opener):
            return transport.Live().get(GH, timeout=5)

    def test_incomplete_read_is_a_network_error(self):
        with self.assertRaises(ConnectionError):
            self.live_get_raising(http.client.IncompleteRead(b"{\"jobs\": [", 5000))

    def test_ssl_error_is_a_network_error(self):
        with self.assertRaises(ConnectionError):
            self.live_get_raising(ssl.SSLError("constructed"))


class CorruptState(Base):
    def test_a_corrupt_state_file_ends_the_run_as_error_with_an_exit_line(self):
        (self.runs / "state").mkdir()
        (self.runs / "state" / "state-old.json").write_text("{not json")
        rep = self.run_loop([{"name": "oscar", "ats": "greenhouse", "token": "oscar"}], {GH: [fakes.gh(1)]})
        self.assertEqual(rep["exit"], "error")
        self.assertIn("state", rep["fatal"])
        self.assertEqual((self.last_trace()["event"], self.last_trace()["exit"]), ("exit", "error"))
        self.assertEqual(sorted(p.name for p in (self.runs / "state").iterdir()), ["state-old.json"],
                         "no new state is written on error")


class CheckComparesRawHashes(Base):
    def test_a_raw_file_rewritten_with_its_summary_is_flagged(self):
        self.run_loop([{"name": "oscar", "ats": "greenhouse", "token": "oscar"}], {GH: [fakes.gh(*range(1, 11))]})
        self.assertEqual(check.check_run(self.runs / "r1", self.project), [])
        s = json.loads((self.runs / "r1" / "summary.json").read_text())
        raw = self.project / s["boards"][0]["raw_files"][-1]
        raw.write_bytes(fakes.gh(1, 2, 3)[1])  # consistent on its own: 3 jobs, meta.total 3
        s["boards"][0]["fetched"] = 3
        (self.runs / "r1" / "summary.json").write_text(json.dumps(s))
        findings = check.check_run(self.runs / "r1", self.project)
        self.assertTrue(any("sha256" in f for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
