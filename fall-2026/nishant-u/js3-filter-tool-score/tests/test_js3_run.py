"""The agent3.run CLI: dedupe by system:board:id, board-level abstention, offline, deterministic.

Written with the implementation (step 3), not before it. Constructed raw directories are
CONSTRUCTED; the last class reads the real saved JS2 responses under out/.
"""
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.js3_helpers import ROOT, body, gh_job

RESUME = ROOT / "data" / "resume.example.json"


def write_raw(root, run, step, system, board, jobs, fetched_at, status=200, board_status="parsed"):
    raw = Path(root) / run / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    name = f"{step:02d}-{system}-{board}"
    (raw / f"{name}.body").write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
    (raw / f"{name}.meta.json").write_text(json.dumps(
        {"system": system, "board": board, "http_status": status, "fetched_at": fetched_at}), encoding="utf-8")
    report = Path(root) / run / "report.json"
    data = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {"boards": []}
    data["boards"].append({"system": system, "board": board, "status": board_status})
    report.write_text(json.dumps(data), encoding="utf-8")


def no_network(*args, **kwargs):
    raise AssertionError("agent3.run must not open a network connection")


class RunOnConstructedRaw(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "raw"
        self.out = Path(self.tmp.name) / "out"
        old = gh_job("Data Scientist", content=body("Nothing shipped."), job_id=7)
        new = gh_job("Data Scientist", content=body("We use SQL."), job_id=7)
        other = gh_job("Software Engineer", content=body("SQL"), job_id=8)
        write_raw(self.root, "r1", 1, "greenhouse", "faire", [old, other], "2026-11-10T10:00:00+00:00")
        write_raw(self.root, "r2", 1, "greenhouse", "faire", [new], "2026-11-10T11:00:00+00:00")
        write_raw(self.root, "r2", 2, "greenhouse", "poshmark", [], "2026-11-10T11:00:00+00:00",
                  board_status="unverified-empty")
        write_raw(self.root, "r2", 3, "greenhouse", "gone", [], "2026-11-10T11:00:00+00:00", status=404,
                  board_status="failed")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self):
        from agent3 import run
        with mock.patch.object(socket, "create_connection", no_network), \
                mock.patch.object(socket.socket, "connect", no_network):
            run.run(self.root, self.out, RESUME)
        return json.loads((self.out / "results.json").read_text(encoding="utf-8"))

    def test_dedupes_by_system_board_id_and_keeps_the_latest_copy(self):
        doc = self.run_cli()
        ids = [r["posting_id"] for r in doc["results"]]
        self.assertEqual(ids, ["greenhouse:faire:7", "greenhouse:faire:8"])
        self.assertEqual(doc["results"][0]["verdict"], "accept")
        self.assertTrue(doc["results"][0]["source"].startswith("r2/"))

    def test_every_posting_has_verdict_reason_and_abstain_flag(self):
        for r in self.run_cli()["results"]:
            self.assertIn(r["verdict"], ("accept", "reject", "abstain"))
            self.assertIsInstance(r["abstain"], bool)
            self.assertTrue(r["reason"])

    def test_unverified_empty_board_is_a_board_level_abstention(self):
        doc = self.run_cli()
        self.assertEqual([b["board"] for b in doc["board_abstentions"]], ["greenhouse:poshmark"])
        self.assertIn("abstain: cannot tell", doc["board_abstentions"][0]["reason"])

    def test_output_is_deterministic(self):
        first = (self.run_cli(), (self.out / "shortlist.md").read_text(encoding="utf-8"))
        second = (self.run_cli(), (self.out / "shortlist.md").read_text(encoding="utf-8"))
        self.assertEqual(first, second)


class RunOnSavedJS2Responses(unittest.TestCase):
    def test_182_unique_postings_from_the_saved_raw_responses(self):
        from agent3 import run
        postings, sources, unverified = run.collect(ROOT / "out")
        boards = {}
        for p in postings:
            key = f"{p['system']}:{p['board']}"
            boards[key] = boards.get(key, 0) + 1
        self.assertEqual(len(postings), 182)
        self.assertEqual(boards, {"greenhouse:faire": 68, "greenhouse:instacart": 92, "ashby:poshmark": 22})
        self.assertEqual(len(sources), 22)
        self.assertEqual(unverified, ["greenhouse:poshmark"])


if __name__ == "__main__":
    unittest.main()
