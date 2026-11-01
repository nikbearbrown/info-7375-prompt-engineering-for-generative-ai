"""Tests against CONTRACT.md. Run: python3 -m unittest discover -s tests -v"""
import copy
import json
import os
import tempfile
import unittest

from agent import watch
from agent.claude_judge import ValidationError, judge_claude, validate_claude_output
from agent.resume import ResumeError, load_resume, validate_resume
from agent.rule import judge_rule

HERE = os.path.dirname(os.path.abspath(__file__))
PERSONA = os.path.join(HERE, "..", "personas", "priya-nair.resume.json")


def posting(pid, title):
    return {"id": pid, "title": title, "location": {"name": "Remote"}, "content": "", "departments": []}


# Constructed fixture postings (not from the board) whose verdicts are worked out by hand in CONTRACT.md.
FIXTURE = [
    posting(3, "Machine Learning Engineer, Inference"),  # relevant
    posting(1, "Senior ML Engineer"),                    # not: senior
    posting(2, "Account Executive"),                     # not: no keyword
    posting(4, "HTML Email Developer"),                  # not: 'ml' is not a whole word here
    posting(5, "Data Engineer"),                         # relevant
]
HAND = {3: "relevant", 1: "not_relevant", 2: "not_relevant", 4: "not_relevant", 5: "relevant"}


def check_pairing(results, postings, resume):
    """Every result must sit on its own posting: same id, same title, verdict recomputed from that posting."""
    by_id = {p["id"]: p for p in postings}
    for r in results:
        p = by_id[r["id"]]
        if r["title"] != p["title"] or r["rule"]["id"] != p["id"]:
            return False
        if r["rule"]["verdict"] != judge_rule(p, resume)["verdict"]:
            return False
    return True


def check_justification(verdict, resume):
    from agent.resume import field_exists
    return (bool(verdict.get("resume_fields")) and bool(verdict.get("posting_fields"))
            and all(field_exists(resume, f) for f in verdict["resume_fields"]))


def judge_all_mispaired(postings, resume):
    """WRONG VERSION 1: verdicts computed in title order, attached to ids in id order."""
    verdicts = [judge_rule(p, resume) for p in sorted(postings, key=lambda p: p["title"])]
    ordered = sorted(postings, key=lambda p: p["id"])
    return [{"id": p["id"], "title": p["title"], "rule": dict(v, id=p["id"])} for p, v in zip(ordered, verdicts)]


def judge_rule_uncited(p, resume):
    """WRONG VERSION 2: correct verdict, justification cites nothing."""
    v = judge_rule(p, resume)
    return dict(v, resume_fields=[], posting_fields=[])


class TestRule(unittest.TestCase):
    def setUp(self):
        self.resume = load_resume(PERSONA)

    def test_rule_matches_hand_examples(self):
        for p in FIXTURE:
            self.assertEqual(judge_rule(p, self.resume)["verdict"], HAND[p["id"]], p["title"])

    def test_rule_is_a_record_and_cites_real_fields(self):
        for p in FIXTURE:
            v = judge_rule(p, self.resume)
            self.assertEqual(v["kind"], "record")
            self.assertTrue(check_justification(v, self.resume), v)

    def test_no_keyword_always_cites_the_keyword_list(self):
        # Found by seeded run 2 (2026-11-01): "Contracts Manager, GTM" cited only the seniority term.
        v = judge_rule(posting(8, "Contracts Manager, GTM"), self.resume)
        self.assertEqual(v["resume_fields"], ["search.title_keywords", "search.exclude_title_terms[5]"])

    def test_seniority_never_relevant(self):
        for term in self.resume["search"]["exclude_title_terms"]:
            self.assertEqual(judge_rule(posting(9, f"{term} Machine Learning Engineer"), self.resume)["verdict"],
                             "not_relevant", term)


class TestWrongVersions(unittest.TestCase):
    def setUp(self):
        self.resume = load_resume(PERSONA)

    def test_wrong_version_mispaired_labels(self):
        self.assertTrue(check_pairing(watch.judge_all(FIXTURE, self.resume), FIXTURE, self.resume))
        self.assertFalse(check_pairing(judge_all_mispaired(FIXTURE, self.resume), FIXTURE, self.resume),
                         "the mis-paired wrong version must be caught")

    def test_wrong_version_empty_justification(self):
        for p in FIXTURE:
            self.assertFalse(check_justification(judge_rule_uncited(p, self.resume), self.resume))
        uncited = json.dumps({"verdict": "relevant", "resume_fields": [], "posting_fields": ["title"], "reason": "x"})
        with self.assertRaises(ValidationError):
            validate_claude_output(uncited, self.resume)
        invented = json.dumps({"verdict": "relevant", "resume_fields": ["certifications[0]"],
                               "posting_fields": ["title"], "reason": "x"})
        with self.assertRaises(ValidationError):
            validate_claude_output(invented, self.resume)


class TestClaudeValidator(unittest.TestCase):
    def setUp(self):
        self.resume = load_resume(PERSONA)
        self.good = {"verdict": "relevant", "resume_fields": ["search.title_keywords[0]", "skills.languages"],
                     "posting_fields": ["title", "content"], "reason": "ML title, Python stack."}

    def test_accepts_contract_shape(self):
        self.assertEqual(validate_claude_output(json.dumps(self.good), self.resume)["verdict"], "relevant")

    def test_rejects_everything_else(self):
        bad = [
            "```json\n" + json.dumps(self.good) + "\n```",
            "Sure! " + json.dumps(self.good),
            json.dumps(dict(self.good, verdict="maybe")),
            json.dumps(dict(self.good, confidence=0.9)),
            json.dumps({k: v for k, v in self.good.items() if k != "reason"}),
            json.dumps(dict(self.good, posting_fields=["salary"])),
            json.dumps([self.good]),
        ]
        for text in bad:
            with self.assertRaises(ValidationError, msg=text):
                validate_claude_output(text, self.resume)

    def test_judgment_is_labelled_and_rejections_are_not_verdicts(self):
        ok = judge_claude(FIXTURE[0], self.resume, caller=lambda prompt: (json.dumps(self.good), {}))
        self.assertEqual((ok["kind"], ok["status"]), ("judgment", "ok"))
        bad = judge_claude(FIXTURE[0], self.resume, caller=lambda prompt: ("relevant", {}))
        self.assertEqual(bad["status"], "rejected")
        self.assertNotIn("verdict", bad)

    def test_prompt_hides_contact_details(self):
        seen = {}
        judge_claude(FIXTURE[0], self.resume, caller=lambda prompt: (seen.setdefault("p", prompt), {}))
        for secret in ("priya.nair@example.com", "555-0163"):
            self.assertNotIn(secret, seen["p"])


class TestResume(unittest.TestCase):
    def test_refuses_non_fictional_resume(self):
        resume = load_resume(PERSONA)
        real = copy.deepcopy(resume)
        real["personal"]["email"] = "someone@gmail.com"
        with self.assertRaises(ResumeError):
            validate_resume(real)
        nophone = copy.deepcopy(resume)
        nophone["personal"]["phone"] = "(617) 373-2000"
        with self.assertRaises(ResumeError):
            validate_resume(nophone)


class TestWatch(unittest.TestCase):
    def test_allow_list_refuses_other_hosts(self):
        for url in ("https://api.lever.co/v0/postings/x", "http://boards-api.greenhouse.io/v1/boards/x/jobs",
                    "https://boards-api.greenhouse.io.evil.example/v1", "https://evil.example/?h=boards-api.greenhouse.io"):
            with self.assertRaises(watch.HostNotAllowed, msg=url):
                watch.fetch(url, opener=lambda *a, **k: self.fail("opener must not be called"))

    def test_baseline_then_new_since_last(self):
        first, second = FIXTURE[:3], FIXTURE
        self.assertEqual(watch.diff_new(first, None), [], "baseline reports none as new")
        state = watch.update_state(first, None, {"board": "t", "run_id": "1"})
        self.assertEqual([p["id"] for p in watch.diff_new(second, state)], [4, 5])
        state = watch.update_state(second, state, {"board": "t", "run_id": "2"})
        self.assertEqual(watch.diff_new(second, state), [], "nothing is new twice")

    def test_end_to_end_two_runs_from_files(self):
        resume_path = PERSONA
        with tempfile.TemporaryDirectory() as d:
            r1, r2 = os.path.join(d, "r1.json"), os.path.join(d, "r2.json")
            for path, jobs in ((r1, FIXTURE[:3]), (r2, FIXTURE)):
                with open(path, "w") as f:
                    json.dump({"jobs": jobs}, f)
            common = ["--resume", resume_path, "--state", os.path.join(d, "s.json"),
                      "--reports", os.path.join(d, "rep"), "--label", "test"]
            out1 = watch.main(common + ["--from-file", r1])
            out2 = watch.main(common + ["--from-file", r2])
        self.assertEqual(out1["new"], [])
        self.assertEqual({e["id"]: e["rule"]["verdict"] for e in out2["new"]}, {4: HAND[4], 5: HAND[5]})


if __name__ == "__main__":
    unittest.main()
