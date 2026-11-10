"""Independent check (GATE.md, Exits: "finished is not correct"), written before check_run.py existed.
The check must not trust the loop's report: it recomputes from saved raw files and cross-checks suspects.
Constructed fixtures only.
"""
import datetime as dt
import json
import pathlib
import shutil
import tempfile
import unittest

import check_run
from jobwatch2 import loop
from test_loop import BOARDS, OK, Clock, FakeNet, ashby, gh

HERE = pathlib.Path(__file__).resolve().parents[1]
TODAY = dt.date(2026, 11, 9)


def stale_gh():
    body = json.loads(gh((99, "Copy of Chief Legal Officer", "New York", "US")))
    body["jobs"][0]["first_published"] = "2026-10-23T04:49:35-04:00"
    return json.dumps(body).encode()


class IndependentCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        (self.root / "runs").mkdir()
        shutil.copytree(HERE / "personas", self.root / "personas")
        (self.root / "checks.json").write_text(json.dumps({
            "cross_check": {"greenhouse/ramp": {"ats": "ashby", "slug": "ramp"}},
            "min_postings": 3, "max_newest_age_days": 14}))
        self.boards = BOARDS + [{"ats": "greenhouse", "slug": "ramp"}]
        self.table = {**OK, "boards/ramp/jobs": [(200, stale_gh())]}

    def tearDown(self):
        self.tmp.cleanup()

    def loop_run(self):
        c = Clock()
        return loop.run(self.root, self.boards, fetcher=FakeNet(self.table), now=c.now, sleep=c.sleep)

    def test_finished_wrong_answer_is_caught(self):
        res = self.loop_run()
        self.assertEqual(res["exit"], "finished")  # the loop's own report is clean...
        cross = FakeNet({"job-board/ramp": [(200, ashby(*[(f"r{i}", "Role", "NYC", "United States")
                                                          for i in range(175)]))]})
        rep = check_run.check(self.root, res["run_dir"], fetcher=cross, today=TODAY)
        flags = {f["board"]: f for f in rep["flags"]}
        self.assertIn("greenhouse/ramp", flags)                  # ...and the independent check catches it
        self.assertEqual(flags["greenhouse/ramp"]["kind"], "finished-wrong")
        self.assertEqual(flags["greenhouse/ramp"]["cross_check_postings"], 175)
        self.assertEqual(rep["verdict"], "wrong")
        self.assertEqual(len(cross.calls), 1)

    def test_recomputes_counts_from_raw_not_the_report(self):
        res = self.loop_run()
        rec = pathlib.Path(res["record_path"])
        data = json.loads(rec.read_text())
        next(b for b in data["boards"] if b["key"] == "greenhouse/stripe")["fetched"] = 999
        rec.write_text(json.dumps(data))
        rep = check_run.check(self.root, res["run_dir"], fetcher=FakeNet({}), today=TODAY)
        kinds = {(f["board"], f["kind"]) for f in rep["flags"]}
        self.assertIn(("greenhouse/stripe", "count-mismatch"), kinds)

    def test_clean_run_passes(self):
        self.boards = BOARDS
        self.table = {**OK}
        # give every fixture board 3+ postings so none is "suspect"
        self.table["boards/stripe/jobs"] = [(200, gh(*[(i, "X", "US", "US") for i in range(3)]))]
        self.table["job-board/openai"] = [(200, ashby(*[(f"a{i}", "X", "SF", "United States") for i in range(3)]))]
        from test_loop import lever
        self.table["postings/palantir"] = [(200, lever(*[(f"l{i}", "X", "NYC", "US") for i in range(3)]))]
        res = self.loop_run()
        rep = check_run.check(self.root, res["run_dir"], fetcher=FakeNet({}), today=TODAY)
        self.assertEqual(rep["flags"], [])
        self.assertEqual(rep["verdict"], "consistent")

    def test_check_never_writes_state(self):
        res = self.loop_run()
        before = {p: p.read_bytes() for p in (self.root / "runs" / "state").iterdir()}
        check_run.check(self.root, res["run_dir"], fetcher=FakeNet({}), today=TODAY)
        after = {p: p.read_bytes() for p in (self.root / "runs" / "state").iterdir()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
