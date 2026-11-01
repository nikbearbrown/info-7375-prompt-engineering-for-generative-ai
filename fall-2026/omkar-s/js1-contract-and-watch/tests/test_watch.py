"""The watch: baseline, new-since-last by id, raw evidence, pairing, labels.
Written by Claude Code, 2026-10-25. Uses constructed fixtures only (no network)."""
import datetime as dt
import filecmp
import json
import os
import shutil
import tempfile
import unittest

from jsagent import watch

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
RESUME = os.path.join(ROOT, "persona", "aarav-patel.example.json")
A = os.path.join(HERE, "fixtures", "board-a.json")
B = os.path.join(HERE, "fixtures", "board-b.json")
T1 = dt.datetime(2026, 10, 25, 12, 0, tzinfo=dt.timezone.utc)
T2 = dt.datetime(2026, 10, 26, 12, 0, tzinfo=dt.timezone.utc)
T3 = dt.datetime(2026, 10, 27, 12, 0, tzinfo=dt.timezone.utc)


def jobs(path):
    with open(path) as f:
        return {j["id"]: j for j in json.load(f)["jobs"]}


class Watch(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.state = os.path.join(self.dir, "state.json")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def go(self, fixture, now):
        return watch.run("klaviyo", RESUME, self.state, self.dir, fixture=fixture, now=now)

    # --- wrong version 2: baseline must report none ---------------------------------
    def test_baseline_reports_zero_new_and_records_every_id(self):
        r = self.go(A, T1)
        self.assertTrue(r["baseline"])
        self.assertEqual(r["new_since_last_run"], 0)
        self.assertEqual(r["records"], [])
        with open(self.state) as f:
            self.assertEqual(sorted(json.load(f)["seen_ids"]), sorted(jobs(A)))

    def test_second_run_reports_exactly_the_new_ids(self):
        self.go(A, T1)
        r = self.go(B, T2)
        self.assertFalse(r["baseline"])
        self.assertEqual(sorted(x["posting_id"] for x in r["records"]), sorted(set(jobs(B)) - set(jobs(A))))
        self.assertEqual(r["removed_since_last_run"], [102])

    def test_state_is_updated_so_old_postings_are_not_re_reported(self):
        self.go(A, T1)
        self.go(B, T2)
        r = self.go(B, T3)
        self.assertEqual(r["new_since_last_run"], 0)

    # --- wrong version 1: each verdict belongs to its own posting --------------------
    def test_each_record_is_judged_on_its_own_posting(self):
        self.go(A, T1)
        r = self.go(B, T2)
        b = jobs(B)
        self.assertGreaterEqual(len(r["records"]), 2, "pairing needs two or more new postings to be testable")
        for rec in r["records"]:
            p = b[rec["posting_id"]]
            self.assertEqual(rec["title"], p["title"])
            self.assertEqual(rec["rule"]["clauses"]["A"]["value"], p["title"])
            self.assertEqual(rec["rule"]["clauses"]["B"]["value"], p["location"]["name"])
            self.assertIn(f'posting.title="{p["title"]}"', rec["rule"]["justification"][0])

    def test_known_verdicts_on_fixture(self):
        # Hand-computed by Claude Code from CONTRACT.md: 104 has only Python (JavaScript, MySQL,
        # Rust, Terraform don't count) -> C fails; 105 is US remote with TypeScript, Node.js, AWS.
        self.go(A, T1)
        r = {x["posting_id"]: x["rule"]["verdict"] for x in self.go(B, T2)["records"]}
        self.assertEqual(r, {104: "not_relevant", 105: "relevant"})

    # --- evidence and labels ---------------------------------------------------------
    def test_raw_response_saved_byte_identical(self):
        r = self.go(A, T1)
        self.assertTrue(filecmp.cmp(A, os.path.join(self.dir, r["raw_response"]), shallow=False))

    def test_seeded_run_is_labelled(self):
        r = self.go(A, T1)
        self.assertEqual(r["source"]["type"], "seeded")
        self.assertIn("SEEDED", watch.render(r))


class Judgment(unittest.TestCase):
    """The Claude verdict is labelled a judgment and never coerced. Fake caller, no network."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.state = os.path.join(self.dir, "state.json")
        self.prompt = os.path.join(ROOT, "prompts", "baseline.txt")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_with(self, reply):
        def fake(prompt):
            pid = prompt.split('"posting_id": "')[1].split('"')[0]
            return {"result": reply(pid), "session_id": "fake", "modelUsage": {"fake-model": {}}}
        watch.run("klaviyo", RESUME, self.state, self.dir, fixture=A, now=T1)
        return watch.run("klaviyo", RESUME, self.state, self.dir, fixture=B, now=T2,
                         use_claude=True, prompt_path=self.prompt, claude_caller=fake)

    def test_valid_judgment_is_labelled_not_fact(self):
        ok = lambda pid: json.dumps({"posting_id": pid, "verdict": "relevant", "resume_fields": ["skills.languages"],
                                     "posting_fields": ["content"], "reason": "Python appears."})
        r = self.run_with(ok)
        for rec in r["records"]:
            self.assertEqual(rec["claude"]["kind"], "judgment")
            self.assertEqual(rec["claude"]["status"], "valid")
            self.assertEqual(rec["rule"]["kind"], "record")
        self.assertIn("not a fact", watch.render(r))

    def test_rejected_output_stays_rejected(self):
        r = self.run_with(lambda pid: "```json\n{}\n```")
        for rec in r["records"]:
            self.assertEqual(rec["claude"]["status"], "rejected")
            self.assertIsNone(rec["claude"]["verdict"])
        self.assertIn("REJECTED", watch.render(r))


if __name__ == "__main__":
    unittest.main()
