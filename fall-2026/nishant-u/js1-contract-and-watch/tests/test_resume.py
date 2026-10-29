"""Refuses: a résumé without the FICTIONAL marker or with a non-@example.com email."""
import copy
import unittest

from tests import helpers


class ResumeRefusal(helpers.ContractTest):
    modules = ("agent.resume",)

    def test_fictional_persona_loads(self):
        data = self.resume.load_resume(helpers.ROOT / "data" / "resume.example.json")
        self.assertEqual(data["personal"]["email"], "priya.nair@example.com")

    def test_non_fictional_resume_is_refused(self):
        with self.assertRaises(self.resume.RefusedResume):
            self.resume.load_resume(helpers.FIXTURES / "resume_not_fictional.json")

    def test_missing_marker_is_refused_even_with_example_email(self):
        data = copy.deepcopy(helpers.resume())
        data["_comment"] = "Example persona."
        with self.assertRaises(self.resume.RefusedResume):
            self.resume.check_resume(data)

    def test_lookalike_email_domains_are_refused(self):
        for email in ("p@sub.example.com", "p@example.com.org", "p@notexample.org"):
            data = copy.deepcopy(helpers.resume())
            data["personal"]["email"] = email
            with self.subTest(email=email), self.assertRaises(self.resume.RefusedResume):
                self.resume.check_resume(data)


if __name__ == "__main__":
    unittest.main()
