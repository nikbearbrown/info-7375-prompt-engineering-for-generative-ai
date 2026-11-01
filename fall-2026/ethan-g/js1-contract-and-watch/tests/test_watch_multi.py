"""v3 end-to-end, offline: replay constructed multi-board run folders through the real CLI.

CONSTRUCTED data (not real postings). Expected verdicts computed by hand from R1-R5 for persona Evan Gordon.
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jsagent import watch

ROOT = Path(__file__).resolve().parent.parent
PERSONA = str(ROOT / "persona" / "evan-gordon.resume.json")


def job(i, title, loc, content=None):
    j = {"id": i, "title": title, "location": {"name": loc}, "absolute_url": f"https://example.com/{i}",
         "updated_at": "2026-10-31T12:00:00-04:00", "departments": []}
    if content is not None:
        j["content"] = content
    return j


RUN_A = {"alpha": [job(1001, "Data Engineer", "Remote - US"), job(2001, "Account Executive", "Boston, MA")],
         "beta": [job(3001, "Staff Data Engineer", "Remote - US")]}
RUN_B = {"alpha": RUN_A["alpha"] + [job(1002, "Data Analyst", "Boston, MA"), job(2002, "Recruiter", "Boston, MA")],
         "beta": RUN_A["beta"] + [job(3002, "Analytics Engineer", "Remote - Canada")]}
DETAILS_B = {("alpha", 1002): job(1002, "Data Analyst", "Boston, MA", "2+ years of experience. SQL and Tableau daily."),
             ("beta", 3002): job(3002, "Analytics Engineer", "Remote - Canada", "3+ years of experience with dbt and SQL.")}
RUN_C = dict(RUN_B, gamma=[job(4001, "Data Engineer", "Remote - US")])  # a board seen for the first time


def write_run(base, name, boards, details=()):
    d = Path(base) / name
    (d / "boards").mkdir(parents=True)
    (d / "jobs").mkdir()
    for b, jobs in boards.items():
        (d / "boards" / f"{b}.json").write_text(json.dumps({"jobs": jobs, "meta": {"total": len(jobs)}}))
    for (b, i), j in dict(details).items():
        (d / "jobs" / f"{b}_{i}.json").write_text(json.dumps(j))
    return str(d)


class TestMultiBoardWatch(unittest.TestCase):
    def run_cli(self, tmp, run_dir, note):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = watch.main(["--resume", PERSONA, "--state", f"{tmp}/state.json", "--runs-dir", f"{tmp}/runs",
                             "--from-dir", run_dir, "--seeded", note, "--no-claude"])
        reports = sorted(Path(f"{tmp}/runs").glob("*.json"), key=lambda p: p.stat().st_mtime_ns)
        return rc, json.loads(reports[-1].read_text())

    def test_baseline_then_change_then_new_board(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc, r1 = self.run_cli(tmp, write_run(tmp, "A", RUN_A), "fixture A")
            self.assertEqual((rc, r1["baseline"], r1["n_new_total"]), (0, True, 0))

            rc, r2 = self.run_cli(tmp, write_run(tmp, "B", RUN_B, DETAILS_B), "fixture B")
            self.assertEqual(rc, 0)
            self.assertEqual(r2["audit_errors"], [])
            self.assertEqual(r2["n_new_total"], 3)          # 1002, 2002, 3002
            self.assertEqual(r2["n_new_other"], 1)          # 2002 Recruiter: counted, not judged
            got = {p["id"]: p["rule_verdict_record"] for p in r2["new_postings"]}
            self.assertEqual(set(got), {"1002", "3002"})
            self.assertEqual(got["1002"]["verdict"], "relevant")       # Boston, 2+ yrs, SQL+Tableau
            self.assertTrue(got["1002"]["preferred_location"] and got["1002"]["preferred_years"])
            self.assertEqual(got["3002"]["verdict"], "not_relevant")   # R3: Remote - Canada

            rc, r3 = self.run_cli(tmp, write_run(tmp, "C", RUN_C), "fixture C")
            self.assertEqual((rc, r3["n_new_total"], r3["boards_baselined"]), (0, 0, ["gamma"]))

    def test_missing_detail_for_judged_posting_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.run_cli(tmp, write_run(tmp, "A", RUN_A), "fixture A")
            with self.assertRaises(FileNotFoundError):
                self.run_cli(tmp, write_run(tmp, "B", RUN_B), "fixture B without details")


if __name__ == "__main__":
    unittest.main()
