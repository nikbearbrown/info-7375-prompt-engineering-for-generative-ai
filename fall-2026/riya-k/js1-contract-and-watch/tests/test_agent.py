"""Tests for CONTRACT.md. Postings here are CONSTRUCTED test inputs, not real Databricks postings.

Run: python3 -m unittest discover -s tests -v   (offline; no network, no Claude calls)
"""

import json
import tempfile
import unittest
from pathlib import Path

from jsagent import rules
from jsagent.contract import ContractError, parse_claude_output, validate_resume, validate_verdict
from jsagent.watch import attach_verdicts, fetch, run

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "arya-sahni.json").read_text())


def posting(pid, title, content="", location="Boston, Massachusetts"):
    return {"id": pid, "title": title, "content": content, "location": {"name": location}}


GOOD = posting(1, "AI Engineer", "<p>We use Python and SQL with MLflow.</p>")
SENIOR = posting(2, "Senior AI Engineer", "<p>Python, SQL, MLflow.</p>")
SALES = posting(3, "Account Executive", "<p>Python, SQL.</p>")


class TestRule(unittest.TestCase):
    """Hand-computed cases: each expected verdict follows from CONTRACT.md 'The rule'."""

    def test_title_word_two_skills_us_is_relevant(self):
        v = rules.judge(GOOD, RESUME)
        self.assertEqual(v["verdict"], "relevant")
        self.assertIn("skills.languages: Python", v["justification"])

    def test_seniority_word_excludes(self):
        self.assertEqual(rules.judge(SENIOR, RESUME)["verdict"], "not_relevant")
        self.assertEqual(rules.judge(posting(4, "Sr. Data Engineer", "Python SQL"), RESUME)["verdict"], "not_relevant")

    def test_no_title_word_excludes(self):
        self.assertEqual(rules.judge(SALES, RESUME)["verdict"], "not_relevant")

    def test_one_skill_is_not_enough(self):
        self.assertEqual(rules.judge(posting(5, "Data Engineer", "Python only"), RESUME)["verdict"], "not_relevant")

    def test_databricks_is_not_a_free_skill(self):
        p = posting(6, "Data Engineer", "Databricks and Python")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")
        # Amendment 1: Unity Catalog is in Databricks' boilerplate, so it is not counted either.
        p = posting(8, "Data Engineer", "Python. Databricks offers ... Lakehouse, and Unity Catalog.")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")

    def test_location(self):
        self.assertTrue(rules.is_us_location("Remote - California"))
        self.assertTrue(rules.is_us_location("Northeast - United States"))
        self.assertTrue(rules.is_us_location("Remote"))
        self.assertFalse(rules.is_us_location("London, United Kingdom"))
        self.assertFalse(rules.is_us_location("Remote - Germany"))
        self.assertFalse(rules.is_us_location("Bengaluru, India"))
        # Amendment 2: state codes are capitals only, so "Montréal" is not Alabama.
        self.assertFalse(rules.is_us_location("Montréal, Canada"))
        self.assertTrue(rules.is_us_location("Austin, TX"))

    def test_out_fields_present(self):
        v = rules.judge({**GOOD, "absolute_url": "https://example.com/1"}, RESUME)
        self.assertEqual((v["location"], v["url"]), ("Boston, Massachusetts", "https://example.com/1"))

    def test_extra_substring_skill_match_is_caught(self):
        # Extra check: 'SQL' inside 'NoSQL' and 'AI' inside 'maintain' must not count.
        self.assertFalse(rules.find_word("SQL", "experience with NoSQL stores"))
        self.assertFalse(rules.find_word("AI", "maintain pipelines"))
        p = posting(7, "Data Engineer", "NoSQL and Python")
        self.assertEqual(rules.judge(p, RESUME)["verdict"], "not_relevant")


def wrong_attach_shifted(postings, judge_fn):
    """WRONG VERSION 1 (from CONTRACT.md): verdicts shifted by one onto the next posting's id."""
    verdicts = [judge_fn(p) for p in postings]
    return [{**v, "id": postings[(i + 1) % len(postings)]["id"]} for i, v in enumerate(verdicts)]


def wrong_judge_cites_nothing(p):
    """WRONG VERSION 2 (from CONTRACT.md): a justification that cites nothing."""
    return {"id": p["id"], "verdict": "relevant", "resume_fields": ["skills"],
            "posting_fields": ["title"], "justification": "Good fit."}


def recompute_check(verdicts, postings):
    """Recompute every verdict by id from the written rule; raise if any differs."""
    by_id = {p["id"]: p for p in postings}
    for v in verdicts:
        if rules.judge(by_id[v["id"]], RESUME)["verdict"] != v["verdict"]:
            raise AssertionError(f"verdict for {v['id']} does not match the rule")


class TestWrongVersions(unittest.TestCase):
    postings = [GOOD, SENIOR, SALES]

    def test_wrong_version_1_labels_on_wrong_posting_is_caught(self):
        judge_fn = lambda p: rules.judge(p, RESUME)
        recompute_check(attach_verdicts(self.postings, judge_fn), self.postings)  # correct version passes
        with self.assertRaises(AssertionError):
            recompute_check(wrong_attach_shifted(self.postings, judge_fn), self.postings)

    def test_wrong_version_1_claude_reply_for_another_posting_is_rejected(self):
        reply = json.dumps({"id": 2, "verdict": "relevant", "resume_fields": ["skills.languages"],
                            "posting_fields": ["title"], "justification": "skills.languages matches title."})
        with self.assertRaises(ContractError):
            parse_claude_output(reply, expected_id=1)

    def test_wrong_version_2_justification_citing_nothing_is_rejected(self):
        with self.assertRaises(ContractError):
            attach_verdicts([GOOD], wrong_judge_cites_nothing)
        with self.assertRaises(ContractError):
            validate_verdict({**rules.judge(GOOD, RESUME), "resume_fields": []}, 1)

    def test_every_rule_verdict_cites_both_sides(self):
        for p in self.postings:
            validate_verdict(rules.judge(p, RESUME), p["id"])


class TestClaudeValidator(unittest.TestCase):
    ok = {"id": 1, "verdict": "relevant", "resume_fields": ["skills.languages"],
          "posting_fields": ["title", "content"], "justification": "skills.languages Python appears in content."}

    def test_accepts_exact_format_and_labels_it_a_judgment(self):
        v = parse_claude_output(json.dumps(self.ok), 1)
        self.assertEqual((v["judge"], v["kind"]), ("claude", "judgment"))

    def test_rejects_prose_fences_extra_keys_bad_verdict(self):
        bad = ["Relevant: good fit.", "```json\n" + json.dumps(self.ok) + "\n```",
               json.dumps({**self.ok, "confidence": 0.9}), json.dumps({**self.ok, "verdict": "maybe"}),
               json.dumps({**self.ok, "posting_fields": ["salary"]})]
        for text in bad:
            with self.assertRaises(ContractError, msg=text):
                parse_claude_output(text, 1)


class TestWatchAndRefusals(unittest.TestCase):
    def _board(self, d, name, ps):
        f = Path(d) / name
        f.write_text(json.dumps({"jobs": ps}))
        return str(f)

    def test_baseline_then_only_new_and_never_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            state, out, resume = f"{d}/state.json", f"{d}/out", str(ROOT / "persona" / "arya-sahni.json")
            r1 = run("t", resume, state, out, self._board(d, "a.json", [GOOD, SENIOR]), "seeded")
            self.assertTrue(r1["baseline"])
            self.assertEqual(r1["rule_verdicts"], [])
            r2 = run("t", resume, state, out, self._board(d, "b.json", [GOOD, SENIOR, SALES]), "seeded")
            self.assertEqual([v["id"] for v in r2["rule_verdicts"]], [3])
            # Extra check: a posting already seen is never reported as new again.
            r3 = run("t", resume, state, out, self._board(d, "c.json", [GOOD, SENIOR, SALES]), "seeded")
            self.assertEqual(r3["rule_verdicts"], [])
            self.assertEqual(len(list(Path(out, "raw").iterdir())), 3)  # raw response saved every run

    def test_refuses_hosts_off_allow_list(self):
        for url in ["https://evil.example.com/jobs", "http://boards-api.greenhouse.io/v1/boards/x/jobs",
                    "https://api.lever.co/v0/postings/x"]:
            with self.assertRaises(ContractError):
                fetch(url)

    def test_refuses_non_fictional_resume(self):
        real = {**RESUME, "personal": {**RESUME["personal"], "email": "someone@gmail.com"}}
        with self.assertRaises(ContractError):
            validate_resume(real)
        validate_resume(RESUME)


if __name__ == "__main__":
    unittest.main()
