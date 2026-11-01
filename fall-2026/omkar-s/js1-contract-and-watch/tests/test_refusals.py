"""Refuses (CONTRACT.md): allow-list, fictional résumé only, strict output validator.
Written by Claude Code, 2026-10-25. No network: every refusal happens before I/O."""
import copy
import json
import os
import unittest

from jsagent import claude_judge, fetch, persona

HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, "..", "persona", "aarav-patel.example.json")) as f:
    AARAV = json.load(f)


class AllowList(unittest.TestCase):
    def test_refuses_other_hosts(self):
        for url in ["https://api.lever.co/v0/postings/x", "http://boards-api.greenhouse.io/v1/boards/x/jobs",
                    "https://boards-api.greenhouse.io.evil.example/v1", "https://boards-api.greenhouse.io@evil.example/",
                    "https://boards-api.greenhouse.io:8443/v1", "https://evil.example/?h=boards-api.greenhouse.io"]:
            with self.subTest(url=url), self.assertRaises(fetch.RefusedFetch):
                fetch.fetch(url)

    def test_allows_the_one_host(self):
        self.assertEqual(fetch.check_allowed(fetch.board_url("klaviyo")), "boards-api.greenhouse.io")

    def test_board_token_cannot_change_the_path(self):
        for bad in ["../x", "klaviyo/jobs", "Klaviyo", "", "a?b"]:
            with self.subTest(bad=bad), self.assertRaises(fetch.RefusedFetch):
                fetch.board_url(bad)

    def test_redirects_are_refused(self):
        with self.assertRaises(fetch.RefusedFetch):
            fetch._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://evil.example/")


class FictionalResume(unittest.TestCase):
    def test_aarav_is_accepted(self):
        self.assertEqual(persona.problems(AARAV), [])

    def test_real_looking_resumes_are_refused(self):
        def mut(f):
            d = copy.deepcopy(AARAV); f(d); return d
        cases = {
            "real email": mut(lambda d: d["personal"].update(email="someone@gmail.com")),
            "real phone": mut(lambda d: d["personal"].update(phone="(617) 373-2000")),
            "not marked fictional": mut(lambda d: d.update(_comment="my resume")),
            "email hidden in a bullet": mut(lambda d: d["experience"][0]["bullets"].append("ask jane@northeastern.edu")),
        }
        for name, d in cases.items():
            with self.subTest(name):
                self.assertTrue(persona.problems(d))

    def test_refusal_message_does_not_echo_resume(self):
        path = os.path.join(HERE, "_tmp_real.json")
        d = copy.deepcopy(AARAV); d["personal"]["email"] = "someone@gmail.com"
        with open(path, "w") as f:
            json.dump(d, f)
        try:
            with self.assertRaises(persona.RefusedResume) as cm:
                persona.load(path)
            self.assertNotIn("someone", str(cm.exception))
        finally:
            os.remove(path)

    def test_contact_block_is_not_sent_to_the_model(self):
        shown = json.dumps(persona.for_model(AARAV))
        self.assertNotIn("example.com", shown)
        self.assertNotIn("555", shown)


class OutputValidator(unittest.TestCase):
    GOOD = {"posting_id": "42", "verdict": "relevant", "resume_fields": ["skills.languages"],
            "posting_fields": ["title", "content"], "reason": "Python and Kafka are in the posting."}

    def v(self, obj_or_text):
        text = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text)
        return claude_judge.validate(text, 42)

    def test_accepts_exact_contract(self):
        self.assertIsNotNone(self.v(self.GOOD)[0])

    def test_rejects_everything_else(self):
        g = self.GOOD
        bad = {
            "code fence": "```json\n" + json.dumps(g) + "\n```",
            "prose before": "Here you go: " + json.dumps(g),
            "not json": "relevant",
            "extra key": {**g, "confidence": 0.9},
            "missing key": {k: v for k, v in g.items() if k != "reason"},
            "wrong posting id": {**g, "posting_id": "43"},
            "int posting id": {**g, "posting_id": 42},
            "third verdict": {**g, "verdict": "maybe"},
            "cites nothing": {**g, "resume_fields": []},
            "unknown field": {**g, "posting_fields": ["salary"]},
            "empty reason": {**g, "reason": "  "},
            "reason too long": {**g, "reason": "x" * 501},
        }
        for name, case in bad.items():
            with self.subTest(name):
                parsed, why = self.v(case)
                self.assertIsNone(parsed)
                self.assertTrue(why)


if __name__ == "__main__":
    unittest.main()
