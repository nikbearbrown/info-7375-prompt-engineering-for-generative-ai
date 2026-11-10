"""Tests from the TA-style review (2026-11-10), written BEFORE the fixes (patch v3).
Each class names the review finding it pins down. Offline: fakes only; one test copies a committed
real run into a temporary folder (no network: the cross-check uses a fake)."""
import contextlib
import io
import json
import pathlib
import shutil
import tempfile
import unittest
import datetime as dt

import check_run
from jobwatch2 import __main__ as cli
from jobwatch2 import loop
from test_loop import BOARDS, OK, Clock, FakeNet, LoopCase, ashby, gh

HERE = pathlib.Path(__file__).resolve().parents[1]
REAL_RUN = "20261109T204623Z-906e94"  # the committed finished-wrong run


class D1_ChecksWorkOnAFreshClone(unittest.TestCase):
    """A TA's clone lives at a different path; committed records must still be checkable."""

    def test_committed_finished_wrong_run_checks_in_another_folder(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d) / "elsewhere" / "js2"
            (root / "runs").mkdir(parents=True)
            shutil.copy(HERE / "checks.json", root / "checks.json")
            shutil.copytree(HERE / "runs" / REAL_RUN, root / "runs" / REAL_RUN)
            cross = FakeNet({"job-board/ramp": [(200, ashby(*[(f"r{i}", "R", "NYC", "United States")
                                                              for i in range(175)]))]})
            rep = check_run.check(root, root / "runs" / REAL_RUN, fetcher=cross, today=dt.date(2026, 11, 9))
            self.assertEqual(rep["verdict"], "wrong")
            self.assertEqual([f["board"] for f in rep["flags"] if f["kind"] == "finished-wrong"], ["greenhouse/ramp"])

    def test_new_records_store_raw_path_relative_to_run(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "runs").mkdir()
            shutil.copytree(HERE / "personas", root / "personas")
            c = Clock()
            res = loop.run(root, BOARDS, fetcher=FakeNet(OK), now=c.now, sleep=c.sleep)
            for b in json.loads(pathlib.Path(res["record_path"]).read_text())["boards"]:
                self.assertFalse(pathlib.Path(b["raw_path"]).is_absolute(), b["raw_path"])
                self.assertTrue(b["raw_path"].startswith("raw/"), b["raw_path"])


class D2_CheckRecomputesAndTraces(LoopCase):
    def setUp(self):
        super().setUp()
        (self.root / "checks.json").write_text(json.dumps(
            {"cross_check": {}, "min_postings": 1, "max_newest_age_days": 400}))
        self.run_loop(BOARDS, OK)  # baseline
        table = dict(OK)
        table["boards/stripe/jobs"] = [(200, gh((1, "Product Manager, Billing", "NYC", "US"),
                                               (2, "Data Scientist", "US", "US"),
                                               (3, "Senior Product Manager, Risk", "Seattle", "US")))]
        self.res, _ = self.run_loop(BOARDS, table)
        self.rec = pathlib.Path(self.res["record_path"])

    def tamper(self, fn):
        data = json.loads(self.rec.read_text())
        fn(next(b for b in data["boards"] if b["key"] == "greenhouse/stripe"))
        self.rec.write_text(json.dumps(data))
        return check_run.check(self.root, self.res["run_dir"], fetcher=FakeNet({}), today=dt.date(2026, 11, 10))

    def test_untampered_is_consistent(self):
        rep = check_run.check(self.root, self.res["run_dir"], fetcher=FakeNet({}), today=dt.date(2026, 11, 10))
        self.assertEqual(rep["verdict"], "consistent", rep["flags"])

    def test_relevant_count_recomputed(self):
        rep = self.tamper(lambda b: b.update(relevant=0))
        self.assertIn(("greenhouse/stripe", "count-mismatch"), {(f["board"], f["kind"]) for f in rep["flags"]})

    def test_new_ids_must_exist_in_raw(self):
        def bad(b):
            b["new_postings"][0]["id"] = "greenhouse/stripe:999"
        rep = self.tamper(bad)
        self.assertIn(("greenhouse/stripe", "new-not-in-raw"), {(f["board"], f["kind"]) for f in rep["flags"]})

    def test_check_writes_its_own_trace(self):
        check_run.check(self.root, self.res["run_dir"], fetcher=FakeNet({}), today=dt.date(2026, 11, 10))
        lines = [json.loads(l) for l in (pathlib.Path(self.res["run_dir"]) / "check-trace.jsonl").read_text().splitlines()]
        steps = {(t["step"], t["decision"]) for t in lines}
        self.assertIn(("read", "allow"), steps)
        self.assertIn(("write", "allow"), steps)


class D3_D4_CliReadsThroughPolicy(unittest.TestCase):
    def call(self, argv):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(argv)
        return code, err.getvalue()

    def test_boards_file_outside_folder_refused_before_any_request(self):
        code, err = self.call(["run", "--boards", "../../../../../../etc/hosts"])
        self.assertEqual(code, 3)
        self.assertIn("outside the assignment folder", err)

    def test_run_accepts_approve_reset_flag(self):
        code, err = self.call(["run", "--boards", "../../../../../../etc/hosts", "--approve-reset", "greenhouse/stripe"])
        self.assertEqual(code, 3)  # parsed (not an argparse error, which would exit 2 via SystemExit)


class D7_MoreWrongVersionCoverage(LoopCase):
    def count(self, net, part):
        return sum(part in c for c in net.calls)

    def test_other_4xx_not_retried(self):
        for code in (400, 403, 410):
            with self.subTest(code=code):
                table = dict(OK)
                table["boards/stripe/jobs"] = [(code, b"{}")]
                res, net = self.run_loop(BOARDS, table)
                self.assertEqual(self.count(net, "boards/stripe"), 1)

    def test_429_retried_exactly_once(self):
        table = dict(OK)
        table["boards/stripe/jobs"] = [(429, b"slow down"), (429, b"slow down"), (429, b"slow down")]
        res, net = self.run_loop(BOARDS, table)
        self.assertEqual(self.count(net, "boards/stripe"), 2)

    def test_404_board_counts_null_and_no_state_written(self):
        res, _ = self.run_loop(BOARDS + [{"ats": "greenhouse", "slug": "stripe-js2-bad"}], OK)
        bad = self.board(res, "greenhouse/stripe-js2-bad")
        self.assertEqual((bad["fetched"], bad["new"], bad["relevant"]), (None, None, None))
        self.assertFalse((self.root / "runs" / "state" / "greenhouse__stripe-js2-bad.json").exists())

    def test_5xx_twice_counts_null(self):
        table = dict(OK)
        table["postings/palantir"] = [(502, b"bad gateway"), (500, b"err")]
        res, _ = self.run_loop(BOARDS, table)
        b = self.board(res, "lever/palantir")
        self.assertEqual(b["status"], "failed")
        self.assertIsNone(b["fetched"])


if __name__ == "__main__":
    unittest.main()
