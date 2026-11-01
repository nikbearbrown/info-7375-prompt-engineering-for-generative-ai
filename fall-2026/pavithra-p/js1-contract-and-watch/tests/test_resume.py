"""CONTRACT.md Refuses 2 and 6: only a clearly fictional résumé is used."""
import copy
import json
import unittest

from agent import config, resume


def persona():
    with open(config.RESUME, encoding="utf-8") as f:
        return json.load(f)


class ResumeTests(unittest.TestCase):
    def test_persona_file_passes(self):
        data = resume.load(config.RESUME)
        self.assertEqual(data["personal"]["name"], "Rohan Mehta")

    def test_refuses_resume_without_example_email(self):
        data = copy.deepcopy(persona())
        data["personal"]["email"] = "rohan.mehta@gmail.com"
        with self.assertRaisesRegex(resume.ResumeRefused, "example.com"):
            resume.validate(data)

    def test_refuses_resume_without_555_phone(self):
        data = copy.deepcopy(persona())
        data["personal"]["phone"] = "(617) 373-2000"
        with self.assertRaisesRegex(resume.ResumeRefused, "555"):
            resume.validate(data)

    def test_refuses_resume_missing_a_skill_list(self):
        data = copy.deepcopy(persona())
        del data["skills"]["devops_cicd"]
        with self.assertRaisesRegex(resume.ResumeRefused, "devops_cicd"):
            resume.validate(data)


if __name__ == "__main__":
    unittest.main()
