"""Shortlist claim validation and the mechanical quote check (offline; fake Claude)."""
import json
import unittest

from jobfilter.claims import ABSTAIN, mechanical, run, validate_reply, w7_presence_only

VIEW = {"key": "g/b/1", "title": "Software Engineer", "location": "Boston, MA",
        "content": "We build services in Python. Java is not required. You have 0–2 years of experience."}


def claim(text, quote, field="content"):
    return {"claim": text, "quote": quote, "field": field}


class Validator(unittest.TestCase):
    def ok(self, claims):
        return json.dumps({"claims": claims})

    def test_valid_reply(self):
        cs, why = validate_reply(self.ok([claim("Python is used", "in Python"), claim(ABSTAIN + ": remote", ""),
                                          claim("Title is SE", "Software Engineer", "title")]))
        self.assertIsNone(why)
        self.assertEqual(len(cs), 3)

    def test_rejects_prose_fences_and_wrong_counts(self):
        good = [claim("a", "Python")] * 3
        self.assertIsNotNone(validate_reply("Here you go: " + self.ok(good))[1])
        self.assertIsNotNone(validate_reply("```json\n" + self.ok(good) + "\n```")[1])
        self.assertIsNotNone(validate_reply(self.ok(good[:2]))[1])
        self.assertIsNotNone(validate_reply(self.ok(good * 2))[1])

    def test_abstention_and_quote_must_agree(self):
        self.assertIsNotNone(validate_reply(self.ok([claim(ABSTAIN + ": x", "Python")] + [claim("a", "Python")] * 2))[1])
        self.assertIsNotNone(validate_reply(self.ok([claim("Python required", "")] + [claim("a", "Python")] * 2))[1])

    def test_unknown_field_or_extra_key(self):
        self.assertIsNotNone(validate_reply(self.ok([claim("a", "x", "salary")] * 3))[1])
        self.assertIsNotNone(validate_reply(self.ok([dict(claim("a", "Python"), label="supported")] * 3))[1])


class Mechanical(unittest.TestCase):
    def test_quote_found_is_never_called_supported(self):
        self.assertEqual(mechanical(claim("Python is used", "services in Python"), VIEW), "quote-found")

    def test_missing_quote(self):
        self.assertEqual(mechanical(claim("Kubernetes required", "Kubernetes"), VIEW), "quote-not-found")

    def test_quote_must_come_from_the_named_field(self):
        self.assertEqual(mechanical(claim("Boston", "Boston, MA", "content"), VIEW), "quote-not-found")
        self.assertEqual(mechanical(claim("Boston", "Boston, MA", "location"), VIEW), "quote-found")

    def test_dash_and_case_normalization(self):
        self.assertEqual(mechanical(claim("0-2 years", "0-2 YEARS of experience"), VIEW), "quote-found")

    def test_w7_negated_quote(self):
        """W7: "Java is not required" must not pass as support for a Java requirement."""
        c = claim("Java is required", "Java is not required")
        self.assertEqual(mechanical(c, VIEW), "quote-found-negation")
        self.assertEqual(w7_presence_only(c, VIEW), "supported")  # the wrong version is caught here

    def test_abstention(self):
        self.assertEqual(mechanical(claim(ABSTAIN + ": remote", ""), VIEW), "abstained")


class InvalidReplyIsAFailureNotAnEmptySet(unittest.TestCase):
    def test_run_records_failure(self):
        import shutil
        from jobfilter import claims as C
        old = C.OUT
        C.OUT = C.HERE / "tests" / "tmp" / "claims"
        try:
            out = run(caller=lambda prompt: {"ok": True, "text": "not json", "called_at": "2000-01-01T00:00:00Z"})
            res = json.loads((out / "results.json").read_text())["results"]
            self.assertTrue(res)
            self.assertTrue(all(r["valid"] is False and r["claims"] == [] and r["invalid_reason"] for r in res))
        finally:
            shutil.rmtree(C.OUT, ignore_errors=True)
            C.OUT = old


if __name__ == "__main__":
    unittest.main()
