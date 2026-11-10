"""Résumé validation tests, using copies of the example persona."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from agent import resume, run
from fixtures import RESUME_PATH, TARGET_PATH

EXAMPLE = json.loads(RESUME_PATH.read_text(encoding="utf-8"))


def with_personal(**changes):
    data = copy.deepcopy(EXAMPLE)
    data["personal"].update(changes)
    return data


class ResumeValidationTests(unittest.TestCase):

    def test_example_persona_is_accepted(self):
        accepted = resume.validate_resume(copy.deepcopy(EXAMPLE))
        self.assertEqual(accepted["skills"]["languages"][0], "Python")

    def test_rejects_non_example_email_without_echoing_it(self):
        data = with_personal(email="priya.nair@gmail.com")
        with self.assertRaisesRegex(resume.ResumeInvalid, "@example.com") as c:
            resume.validate_resume(data)
        self.assertNotIn("gmail", str(c.exception))

    def test_rejects_lookalike_example_domain(self):
        with self.assertRaises(resume.ResumeInvalid):
            resume.validate_resume(with_personal(email="p@example.com.evil"))

    def test_rejects_non_555_phone(self):
        with self.assertRaisesRegex(resume.ResumeInvalid, "555"):
            resume.validate_resume(with_personal(phone="(617) 867-5309"))

    def test_rejects_missing_fields_and_empty_skills(self):
        missing_name = copy.deepcopy(EXAMPLE)
        del missing_name["personal"]["name"]
        empty_skills = copy.deepcopy(EXAMPLE)
        empty_skills["skills"] = {}
        for data in (missing_name, empty_skills, [], {"personal": {}}):
            with self.subTest(data=str(data)[:40]):
                with self.assertRaises(resume.ResumeInvalid):
                    resume.validate_resume(data)

    def test_invalid_resume_exits_nonzero_before_fetching(self):
        class ExplodingOpener:
            def open(self, *a, **k):
                raise AssertionError("fetched with an invalid résumé")

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "resume.json"
            bad.write_text(json.dumps(with_personal(email="real@gmail.com")),
                           encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                code = run.main(
                    ["--board", "scaleai", "--resume", str(bad),
                     "--target", str(TARGET_PATH),
                     "--state", str(Path(tmp) / "state.json"),
                     "--raw-dir", str(Path(tmp) / "raw"),
                     "--reports-dir", str(Path(tmp) / "reports")],
                    opener=ExplodingOpener())
            self.assertNotEqual(code, 0)
            self.assertNotIn("gmail", err.getvalue())
            self.assertFalse((Path(tmp) / "raw").exists())
            self.assertFalse((Path(tmp) / "state.json").exists())


if __name__ == "__main__":
    unittest.main()
