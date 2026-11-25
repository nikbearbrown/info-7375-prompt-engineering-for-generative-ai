"""Regression tests for v1.1's one change: "manager" inside the product name "Mission Manager" is not a seniority term.

The two observed titles come from development postings (audit rows 47 and 58, audit/FALSE-FRIENDS.md). Every other
seniority exclusion must still fire, including genuine manager titles and other terms next to the product name.
"""
import json
import unittest

from jobfilter.corpus import HERE
from jobfilter.filter import KEEP, REJECT, Filter, load_config
from tests.cases import BODY_3, posting

V10, V11 = Filter(load_config("v1.0")), Filter(load_config("v1.1"))
OBSERVED = {"lever/palantir/e168a922-a2f0-45d0-912c-678d66e15118": "Software Engineer - Mission Manager",
            "lever/palantir/c0b60d64-1244-4270-9d55-14115c97c24b": "Software Engineer - Mission Manager"}
STILL_EXCLUDED = [
    ("Software Engineer - Engineering Manager", "manager"),
    ("Software Engineer - Product Manager", "manager"),
    ("Software Engineer Manager - Mission Manager", "manager"),   # a second, genuine "manager"
    ("Senior Software Engineer - Mission Manager", "senior"),
    ("Software Engineer - Mission Manager Lead", "lead"),
    ("Staff Software Engineer, Mission Manager", "staff"),
]


def gate(f, title):
    return f.classify(posting(title=title, content=BODY_3))


class MissionManagerException(unittest.TestCase):
    def test_observed_titles_pass_the_gate_in_v11_only(self):
        for title in set(OBSERVED.values()) | {"Software Engineer, Mission Manager"}:
            with self.subTest(title):
                self.assertEqual(gate(V10, title)["reasons"][0], 'title contains excluded seniority term "manager"')
                d = gate(V11, title)
                self.assertEqual(d["decision"], KEEP)
                self.assertEqual(d["gate"]["seniority_exceptions_applied"], ["mission manager"])

    def test_other_seniority_exclusions_still_fire(self):
        for title, term in STILL_EXCLUDED:
            with self.subTest(title):
                d = gate(V11, title)
                self.assertEqual(d["decision"], REJECT)
                self.assertIn(f'title contains excluded seniority term "{term}"', d["reasons"])

    def test_no_role_phrase_still_rejects(self):
        for title in ("Mission Manager", "Engineering Manager, Mission Manager"):
            self.assertEqual(gate(V11, title)["reasons"][0], "title has no qualifying role phrase")

    def test_only_one_object_changed(self):
        a, b = load_config("v1.0"), load_config("v1.1")
        changed = {k for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
        self.assertEqual(changed, {"version", "document", "seniority_exceptions"})

    def test_development_decisions_differ_only_on_the_two_observed_postings(self):
        d0 = {d["key"]: d for d in json.loads((HERE / "runs" / "v1.0" / "decisions-dev.json").read_text())}
        d1 = {d["key"]: d for d in json.loads((HERE / "runs" / "v1.1" / "decisions-dev.json").read_text())}
        self.assertEqual(d0.keys(), d1.keys())
        moved = {k for k in d0 if d0[k]["decision"] != d1[k]["decision"]}
        self.assertEqual(moved, set(OBSERVED))
        self.assertTrue(all(d0[k]["decision"] == REJECT and d1[k]["decision"] == KEEP for k in moved))


if __name__ == "__main__":
    unittest.main()
