"""The filter run (python3 -m job_agent filter): the newest saved answer of each board, verdicts.json and report.md.

Every saved answer here is a CONSTRUCTED fixture written into a temporary runs folder.
"""

import gzip
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

from job_agent import filter_run
from job_agent.__main__ import main
from job_agent.errors import Refused

from .loop_helpers import ashby_job, body, greenhouse_job

GOOD = "We build APIs and design SQL schemas for our backend."


def save(runs: Path, run_id: str, key: str, data: bytes, status: int = 200, attempt: int = 1):
    folder = runs / run_id / "boards" / key
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"attempt-{attempt}.json.gz").write_bytes(gzip.compress(data, mtime=0))
    meta = {"status": status, "sha256": hashlib.sha256(data).hexdigest(), "body_file": f"attempt-{attempt}.json.gz"}
    (folder / f"attempt-{attempt}.meta.json").write_text(json.dumps(meta), encoding="utf-8")


class FilterRunTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-filter-run-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.runs, self.out = self.root / "runs", self.root / "out"
        boards = [{"system": "ashby", "name": "acme", "company": "Acme"},
                  {"system": "greenhouse", "name": "beta", "company": "Beta"},
                  {"system": "greenhouse", "name": "gone", "company": "(made-up)", "deliberate_failure": True}]
        self.boards = self.root / "boards.json"
        self.boards.write_text(json.dumps({"boards": boards}), encoding="utf-8")
        old = [ashby_job("a-old", descriptionPlain=GOOD)]
        new = [ashby_job("a-1", descriptionPlain=GOOD), ashby_job("a-2", title="Senior Software Engineer"),
               ashby_job("a-3", title=""), ashby_job("a-4", title="Software Engineer, Example Team",
                                                     descriptionPlain=GOOD, publishedAt="2026-11-02T00:00:00+00:00")]
        save(self.runs, "2026-11-01T000000Z", "ashby-acme", body("ashby", old))
        save(self.runs, "2026-11-02T000000Z", "ashby-acme", body("ashby", new))
        save(self.runs, "2026-11-02T000000Z", "greenhouse-beta", body("greenhouse", [greenhouse_job(7)]))
        save(self.runs, "2026-11-02T000000Z", "greenhouse-gone", b'{"status":404}', status=404)

    def run_once(self, **kw):
        clock = lambda: datetime(2026, 11, 21, 5, 0, 0, tzinfo=timezone.utc)  # noqa: E731
        kw.setdefault("rules_version", "1.0")  # these tests pin FILTER.md v1.0's numbers
        return filter_run.run(runs_root=self.runs, boards_path=self.boards, out_root=self.out, now=clock, **kw)

    def test_the_newest_answer_of_each_board_is_filtered(self):
        result = self.run_once()
        sources = {s["key"]: s for s in result["meta"]["sources"]}
        self.assertEqual(sources["ashby-acme"]["run"], "2026-11-02T000000Z")  # not the older run
        self.assertIsNone(sources["greenhouse-gone"]["run"])
        ids = sorted(r["id"] for r in result["records"])
        self.assertEqual(ids, ["7", "a-1", "a-2", "a-3", "a-4"])
        fates = result["summary"]["fates"]
        self.assertEqual(fates, {"kept": 3, "rejected": 1, "cannot_tell": 1})
        self.assertEqual(result["summary"]["deciding_rule"]["R3"], 1)
        self.assertEqual(result["summary"]["cannot_tell"][0]["id"], "a-3")

    def test_duplicates_keep_the_newest_and_the_files_are_written(self):
        result = self.run_once()
        # a-1 and a-4 share board and title; a-4 is newer, so a-1 is the removed copy.
        self.assertEqual([d["id"] for d in json.loads((result["out"] / "verdicts.json").read_text())
                          ["duplicates_removed"]], ["a-1"])
        report = (result["out"] / "report.md").read_text(encoding="utf-8")
        for heading in ("## Sources", "## Fates", "## Rejected, by rule", "## \"I cannot tell\"",
                        "## The shortlist", "## How often Section 6's implementation choices fired",
                        "## Counts FILTER.md quoted before the build", "## Fingerprints"):
            self.assertIn(heading, report)
        self.assertEqual(result["out"].name, "2026-11-21T050000Z")

    def test_a_run_never_overwrites_another(self):
        self.run_once()
        with self.assertRaises(Refused):
            self.run_once()

    def test_a_saved_answer_that_does_not_match_its_hash_is_broken_input(self):
        path = self.runs / "2026-11-02T000000Z" / "boards" / "greenhouse-beta" / "attempt-1.json.gz"
        path.write_bytes(gzip.compress(b'{"jobs": []}', mtime=0))
        from job_agent.errors import BrokenInput
        with self.assertRaises(BrokenInput):
            self.run_once()

    def test_section_6_counts_are_reported(self):
        new = [ashby_job("c-1", descriptionPlain="The company saw 10x growth over 6 years. We build APIs in SQL."),
               ashby_job("c-2", descriptionPlain="You will start in Dec. 2026."),
               ashby_job("c-3", descriptionPlain="Start date: Spring 2027. We build APIs.")]
        save(self.runs, "2026-11-03T000000Z", "ashby-acme", body("ashby", new))
        s6 = self.run_once()["summary"]["section6"]
        self.assertEqual(s6["company_words"]["growth"]["count"], 1)
        self.assertEqual(s6["dec_merges"]["count"], 1)
        self.assertEqual(s6["season_rule"]["outcomes"], {"cannot tell": 1})

    def test_the_command_line(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(["filter", "--runs", str(self.runs), "--boards", str(self.boards), "--out", str(self.out)])
        self.assertEqual(code, 0)
        self.assertIn("5 postings, 3 kept, 1 rejected, 1 cannot tell", out.getvalue())


if __name__ == "__main__":
    unittest.main()
