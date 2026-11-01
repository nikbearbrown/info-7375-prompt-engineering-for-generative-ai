"""CONTRACT.md Wrong versions: each check passes on the real code and fails on the wrong version."""
import json
import re
import time
import unittest

from agent import claude_judge, rule
from tests import wrong_versions
from tests.helpers import JACK, constructed_posting

# CONSTRUCTED postings with known, different expected rule verdicts.
PAIRING_SET = [
    constructed_posting(101, "Staff Data Engineer", "Python SQL Spark Airflow Kafka"),  # disqualified
    constructed_posting(102, "Data Platform Engineer", "Python SQL Spark"),               # (a) relevant
    constructed_posting(103, "Account Executive", "Python"),                              # not relevant
    constructed_posting(104, "Backend Engineer", "Python SQL Spark Kafka"),               # (b) relevant
]
EXPECTED = {101: "not_relevant", 102: "relevant", 103: "not_relevant", 104: "relevant"}


def rule_pairing_problems(judge_all_fn) -> list[str]:
    got = judge_all_fn(PAIRING_SET, JACK)
    return [f"id {pid}: expected {want}, got {got[pid]['verdict']}"
            for pid, want in EXPECTED.items() if got[pid]["verdict"] != want]


def slow_stub_caller(system_prompt, user_prompt):
    """Stands in for Claude: answers by the id it was asked about; earlier ids answer slower,
    so replies complete in reverse order."""
    pid = int(re.search(r"^id: (\d+)$", user_prompt, re.M).group(1))
    time.sleep((105 - pid) * 0.05)
    reply = {"verdict": EXPECTED[pid], "cited_resume_fields": ["skills"],
             "cited_posting_fields": ["title"], "reason": f"stub answer for {pid}"}
    return {"asked_at_utc": "CONSTRUCTED", "model_requested": "stub", "raw_text": json.dumps(reply)}


def claude_pairing_problems(judge_all_fn) -> list[str]:
    got = judge_all_fn(PAIRING_SET, JACK, "{RESUME_FIELDS} {POSTING_FIELDS}", caller=slow_stub_caller)
    return [f"id {pid}: expected {want}, got {got[pid]['verdict']}"
            for pid, want in EXPECTED.items() if got[pid]["verdict"] != want]


# CONSTRUCTED: mentions PostgreSQL and NoSQL but never SQL as its own word.
W2_POSTING = constructed_posting(201, "Data Engineer", "We use PostgreSQL and NoSQL stores, with Python and Spark.")


def whole_word_problems(judge_fn) -> list[str]:
    got = judge_fn(W2_POSTING, JACK)
    problems = []
    if "SQL" in got["skills_found"]:
        problems.append("counted SQL inside PostgreSQL/NoSQL")
    if got["verdict"] != "not_relevant":  # only Python, Spark = 2 skills
        problems.append(f"verdict flipped to {got['verdict']}")
    return problems


class W1Pairing(unittest.TestCase):
    def test_rule_pairs_by_id(self):
        self.assertEqual(rule_pairing_problems(rule.judge_all), [])

    def test_catches_w1_rule(self):
        self.assertNotEqual(rule_pairing_problems(wrong_versions.w1_rule_judge_all), [])

    def test_claude_pairs_by_id_even_when_replies_arrive_out_of_order(self):
        self.assertEqual(claude_pairing_problems(claude_judge.judge_all), [])

    def test_catches_w1_claude(self):
        self.assertNotEqual(claude_pairing_problems(wrong_versions.w1_claude_judge_all), [])


class W2WholeWord(unittest.TestCase):
    def test_rule_matches_whole_words(self):
        self.assertEqual(whole_word_problems(rule.judge), [])

    def test_catches_w2(self):
        self.assertNotEqual(whole_word_problems(wrong_versions.w2_judge), [])


if __name__ == "__main__":
    unittest.main()
