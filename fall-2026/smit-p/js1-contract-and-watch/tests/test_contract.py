"""Tests written against CONTRACT.md. Expected verdicts below were worked out (by Claude, step
by step from the rule in the contract), not read back from the code's output.

The fixture postings (ids 101-107, tests/fixture-day*.json) are CONSTRUCTED: invented by
Claude on 2026-10-24 for testing. They are not real postings.

    python3 -m unittest discover -s tests -v
"""
import copy
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import claude_judge  # noqa: E402
import rule  # noqa: E402
import watch  # noqa: E402

RESUME_PATH = os.path.join(ROOT, "persona", "aarav-patel.resume.json")
DAY1 = os.path.join(HERE, "fixture-day1.json")
DAY2 = os.path.join(HERE, "fixture-day2.json")


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


RESUME = load(RESUME_PATH)
JOBS1 = {j["id"]: j for j in load(DAY1)["jobs"]}
JOBS2 = {j["id"]: j for j in load(DAY2)["jobs"]}
ALL = {**JOBS1, **JOBS2}

# Hand-worked from CONTRACT.md "The rule" (title / seniority / >=2 skills, whole word).
HAND = {
    101: "relevant",      # Software Engineer; Java, Kafka, AWS
    102: "not_relevant",  # "Senior"
    103: "not_relevant",  # JavaScript is not Java; only PostgreSQL -> 1 skill
    104: "not_relevant",  # "Data Scientist" has no role keyword
    105: "not_relevant",  # Kubernetes only; Rust/Terraform are familiar_with_not_shipped
    106: "relevant",      # Kubernetes, Docker, Python
    107: "not_relevant",  # "Staff"
}


class TheRule(unittest.TestCase):
    def test_hand_worked_verdicts(self):
        for pid, expected in HAND.items():
            with self.subTest(pid=pid):
                self.assertEqual(rule.judge(ALL[pid], RESUME)["verdict"], expected)

    def test_every_rule_verdict_passes_its_own_validator(self):
        for pid, job in ALL.items():
            with self.subTest(pid=pid):
                self.assertTrue(rule.validate_verdict(rule.judge(job, RESUME), job, RESUME))

    def test_whole_word_matching(self):
        self.assertIsNone(rule.find_whole("Java", "We write JavaScript"))
        self.assertIsNone(rule.find_whole("SQL", "data in PostgreSQL"))
        self.assertIsNone(rule.find_whole("Go", "work at Google, it is good"))
        self.assertEqual(rule.find_whole("Go", "services in Go."), "Go")
        self.assertEqual(rule.find_whole("Node.js", "a Node.js backend"), "Node.js")

    def test_role_keyword_strips_parentheses(self):
        self.assertIn("Software Engineer", [k for _, k in rule.role_keywords(RESUME)])

    def test_unshipped_skills_do_not_count(self):
        skills = [s for _, s in rule.resume_skills(RESUME)]
        self.assertNotIn("Rust", skills)
        self.assertNotIn("Terraform", skills)

    def test_contract_worked_example(self):
        job = {"id": 1, "title": "Software Engineer, Payments", "content": "Java, Kafka and AWS."}
        self.assertEqual(rule.judge(job, RESUME)["verdict"], "relevant")
        job["title"] = "Senior Software Engineer, Payments"
        self.assertEqual(rule.judge(job, RESUME)["verdict"], "not_relevant")


# ---------------------------------------------------------------- wrong version 1
def wrong_shifted_labels(jobs, resume):
    """WRONG VERSION 1: right verdicts, attached to the wrong posting ids (off by one after a sort)."""
    verdicts = [rule.judge(j, resume) for j in sorted(jobs, key=lambda j: j["id"])]
    ids = [v["posting_id"] for v in verdicts]
    for v, pid in zip(verdicts, ids[1:] + ids[:1]):
        v["posting_id"] = pid
    return verdicts


class WrongVersion1_LabelsOnWrongPostings(unittest.TestCase):
    def test_validator_catches_every_shifted_label(self):
        verdicts = wrong_shifted_labels(list(ALL.values()), RESUME)
        for v in verdicts:
            with self.subTest(claimed_id=v["posting_id"]), self.assertRaises(rule.JustificationError):
                rule.validate_verdict(v, ALL[v["posting_id"]], RESUME)

    def test_same_title_different_id_rejected(self):
        """Real case: Airbnb listed three separate «Senior Compliance Lead, EMEA» postings
        (8318103, 8318152, 8318155). Titles and text can match; only the id tells them apart."""
        twin = {**JOBS1[101], "id": 999}  # constructed twin of 101
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(rule.judge(JOBS1[101], RESUME), twin, RESUME)

    def test_watch_pairs_verdicts_with_postings_whatever_the_board_order(self):
        """End to end: reverse the board order in the second response; watch.run must still
        attach each verdict to its own posting."""
        with tempfile.TemporaryDirectory() as tmp:
            day2 = load(DAY2)
            day2["jobs"] = list(reversed(day2["jobs"]))
            shuffled = os.path.join(tmp, "day2-reversed.json")
            with open(shuffled, "w", encoding="utf-8") as f:
                json.dump(day2, f)
            state, out = os.path.join(tmp, "s.json"), os.path.join(tmp, "o")
            for fixture, label in ((DAY1, "seeded-a"), (shuffled, "seeded-b")):
                with redirect_stdout(io.StringIO()):
                    watch.main(["--board", "airbnb", "--resume", RESUME_PATH, "--state", state,
                                "--out", out, "--fixture", fixture, "--label", label])
            rec = load(os.path.join(out, next(f for f in os.listdir(out) if f.startswith("run-") and "seeded-b" in f)))
            for e in rec["judged"]:
                v = e["rule"]
                self.assertEqual(v["posting_title"], ALL[v["posting_id"]]["title"])
                self.assertEqual(v["verdict"], HAND[v["posting_id"]])
                rule.validate_verdict(v, ALL[v["posting_id"]], RESUME)

    def test_verdict_checked_against_another_posting_rejected(self):
        """Even when the quoted text would match (101 and 102 share wording), a verdict
        claiming id 101 must not validate against posting 102."""
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(rule.judge(JOBS1[101], RESUME), JOBS1[102], RESUME)


# ---------------------------------------------------------------- wrong version 2
def wrong_empty_justification(job, resume):
    """WRONG VERSION 2: a verdict that cites nothing."""
    v = rule.judge(job, resume)
    v["citations"] = []
    return v


class WrongVersion2_JustificationCitesNothing(unittest.TestCase):
    def test_empty_justification_rejected(self):
        for pid, job in ALL.items():
            with self.subTest(pid=pid), self.assertRaises(rule.JustificationError):
                rule.validate_verdict(wrong_empty_justification(job, RESUME), job, RESUME)

    def test_invented_citation_rejected(self):
        v = rule.judge(JOBS1[101], RESUME)
        bad = copy.deepcopy(v)
        bad["citations"][0]["resume_field"] = "skills.languages[99]"
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(bad, JOBS1[101], RESUME)
        bad = copy.deepcopy(v)
        bad["citations"][-1]["posting_text"] = "Haskell"
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(bad, JOBS1[101], RESUME)

    def test_part_word_citation_rejected(self):
        """«Java» must not validate as evidence in a posting that only says «JavaScript»."""
        v = rule.judge(JOBS1[103], RESUME)
        v["citations"].append({"resume_field": "skills.languages[2]", "resume_value": "Java",
                               "posting_field": "content", "posting_text": "Java", "effect": "skill found"})
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(v, JOBS1[103], RESUME)

    def test_resume_only_citation_rejected(self):
        v = rule.judge(JOBS1[101], RESUME)
        v["citations"] = [{"resume_field": "skills.languages[0]", "resume_value": "TypeScript"}]
        with self.assertRaises(rule.JustificationError):
            rule.validate_verdict(v, JOBS1[101], RESUME)


# ---------------------------------------------------------------- the watch
class TheWatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = os.path.join(self.tmp.name, "state.json")
        self.out = os.path.join(self.tmp.name, "out")

    def tearDown(self):
        self.tmp.cleanup()

    def run_watch(self, fixture, label="seeded"):
        argv = ["--board", "airbnb", "--resume", RESUME_PATH, "--state", self.state, "--out", self.out,
                "--fixture", fixture, "--label", label]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(watch.main(argv), 0)
        runs = sorted(f for f in os.listdir(self.out) if f.startswith("run-") and label in f)
        return load(os.path.join(self.out, runs[-1]))

    def test_baseline_reports_nothing(self):
        rec = self.run_watch(DAY1, "seeded-a")
        self.assertTrue(rec["baseline"])
        self.assertEqual(rec["new"], 0)
        self.assertEqual(rec["judged"], [])
        self.assertEqual(load(self.state)["seen_ids"], sorted(JOBS1))

    def test_second_run_reports_exactly_the_added_postings(self):
        """CONTRACT failure sentence: no missed new posting, no already-seen one reported."""
        self.run_watch(DAY1, "seeded-a")
        rec = self.run_watch(DAY2, "seeded-b")
        self.assertFalse(rec["baseline"])
        self.assertEqual(rec["new_ids"], [106, 107])
        self.assertEqual(rec["removed"], 1)  # 104 left the board
        self.assertEqual({e["rule"]["posting_id"]: e["rule"]["verdict"] for e in rec["judged"]},
                         {106: HAND[106], 107: HAND[107]})

    def test_third_run_with_no_change_reports_nothing(self):
        self.run_watch(DAY1, "seeded-a")
        self.run_watch(DAY2, "seeded-b")
        self.assertEqual(self.run_watch(DAY2, "seeded-c")["new"], 0)

    def test_raw_response_saved_untouched(self):
        rec = self.run_watch(DAY1, "seeded-a")
        with open(rec["raw_file"], encoding="utf-8") as a, open(DAY1, encoding="utf-8") as b:
            self.assertEqual(a.read(), b.read())

    def test_failed_fetch_leaves_state_alone(self):
        self.run_watch(DAY1, "seeded-a")
        before = load(self.state)
        argv = ["--board", "airbnb", "--resume", RESUME_PATH, "--state", self.state, "--out", self.out]
        with mock.patch.object(watch, "fetch", side_effect=urllib.error.URLError("offline")), \
                redirect_stderr(io.StringIO()):
            self.assertEqual(watch.main(argv), 3)
        self.assertEqual(load(self.state), before)

    def test_fixture_run_must_be_labelled(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            watch.main(["--board", "airbnb", "--resume", RESUME_PATH, "--state", self.state,
                        "--out", self.out, "--fixture", DAY1])


class Refuses(unittest.TestCase):
    def test_host_not_on_allow_list(self):
        for url in ("https://api.lever.co/v0/postings/x", "https://evil.example/boards-api.greenhouse.io",
                    "http://boards-api.greenhouse.io/v1/boards/airbnb/jobs"):
            with self.subTest(url=url), self.assertRaises(watch.InputError):
                watch.check_host(url)
        self.assertTrue(watch.check_host(watch.board_url("airbnb")))

    def test_bad_board_slug(self):
        with self.assertRaises(watch.InputError):
            watch.board_url("airbnb/../../x")

    def test_real_looking_resume_refused(self):
        real = copy.deepcopy(RESUME)
        real["personal"]["email"] = "someone@gmail.com"
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(real, f)
        try:
            with self.assertRaises(watch.InputError):
                watch.load_resume(f.name)
        finally:
            os.unlink(f.name)

    def test_persona_accepted(self):
        self.assertEqual(watch.load_resume(RESUME_PATH)["personal"]["name"], "Aarav Patel")


# ---------------------------------------------------------------- Claude reply validator
class ClaudeReplyValidator(unittest.TestCase):
    job = JOBS1[101]
    good = {"posting_id": 101, "verdict": "relevant",
            "resume_fields": ["experience[0].title", "skills.languages[2]"],
            "posting_evidence": [{"field": "title", "text": "Software Engineer"},
                                 {"field": "content", "text": "Java and Kafka"}],
            "reason": "Title matches and Java, Kafka, AWS appear."}

    def check(self, obj_or_text):
        text = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text)
        return claude_judge.validate_reply(text, self.job, RESUME)

    def test_accepts_the_fixed_format(self):
        self.assertEqual(self.check(self.good)["verdict"], "relevant")

    def test_rejects_everything_else(self):
        bad_cases = {
            "code fence": "```json\n" + json.dumps(self.good) + "\n```",
            "prose": "Here is my answer: " + json.dumps(self.good),
            "extra key": {**self.good, "confidence": 0.9},
            "wrong posting id": {**self.good, "posting_id": 102},
            "verdict word": {**self.good, "verdict": "maybe"},
            "no resume fields": {**self.good, "resume_fields": []},
            "invented field": {**self.good, "resume_fields": ["skills.frameworks[0]"]},
            "whole section, not a field": {**self.good, "resume_fields": ["personal"]},
            "no evidence": {**self.good, "posting_evidence": []},
            "invented quote": {**self.good, "posting_evidence": [{"field": "content", "text": "10 years of Haskell"}]},
            "long reason": {**self.good, "reason": "word " * 41},
        }
        for name, case in bad_cases.items():
            with self.subTest(case=name), self.assertRaises(claude_judge.ReplyRejected):
                self.check(case)

    def test_failed_cli_call_is_recorded_not_raised(self):
        with mock.patch.object(claude_judge, "call_claude", side_effect=RuntimeError("claude exited 1")):
            rec = claude_judge.judge(self.job, RESUME)
        self.assertEqual(rec["status"], "CALL_FAILED")
        self.assertIsNone(rec["verdict"])
        self.assertEqual(rec["label"], "JUDGMENT (model)")


if __name__ == "__main__":
    unittest.main()
