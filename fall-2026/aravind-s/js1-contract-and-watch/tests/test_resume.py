"""CONTRACT.md In (Résumé) and Refuses 2: only a fictional persona passes, and Claude never gets contact fields.

Bad emails and phone numbers are assembled from pieces, so the privacy scan of this file finds none.
"""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from job_agent import resume
from job_agent.errors import Refused

from .helpers import PERSONA

JANE = json.loads(PERSONA.read_text(encoding="utf-8"))


def without(data, dotted):
    data = copy.deepcopy(data)
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node[part]
    del node[last]
    return data


def changed(data, dotted, value):
    data = copy.deepcopy(data)
    *parents, last = dotted.split(".")
    node = data
    for part in parents:
        node = node[part]
    node[last] = value
    return data


class ResumeTest(unittest.TestCase):
    def test_jane_doe_is_a_valid_fictional_persona(self):
        self.assertEqual(resume.problems_with(JANE), [])
        self.assertEqual(resume.load(PERSONA)["fictional"], True)

    def test_janes_rule_fields_match_the_contract(self):
        # CONTRACT.md, In, lists Jane's values; the rule reads these, so they must agree.
        self.assertEqual(resume.lookup(JANE, "experience.full_time_years"), (True, 3))
        self.assertEqual(resume.lookup(JANE, "work_authorization.needs_sponsorship"), (True, True))
        self.assertEqual(resume.lookup(JANE, "work_authorization.us_person"), (True, False))
        self.assertEqual(resume.lookup(JANE, "availability.earliest_full_time_start"), (True, "2027-05"))
        self.assertEqual(JANE["preferences"]["employment_types"], ["FullTime"])
        self.assertEqual(JANE["preferences"]["regions"], ["California"])
        self.assertEqual(JANE["preferences"]["cities"], ["Austin", "Boston", "Cambridge", "New York", "Seattle", "Bellevue", "Redmond"])
        self.assertEqual(JANE["preferences"]["remote_locations"], ["US - Remote", "Remote - US", "United States - Remote"])
        self.assertEqual(len(JANE["preferences"]["title_includes"]), 10)
        self.assertEqual(len(JANE["preferences"]["title_excludes"]), 19)

    def test_anything_that_could_be_a_real_resume_is_refused(self):
        cases = {
            "not marked fictional": without(JANE, "fictional"),
            "marked not fictional": changed(JANE, "fictional", False),
            "fictional as a string": changed(JANE, "fictional", "true"),
            "a real-looking email": changed(JANE, "email", "jane.doe" + "@" + "gmail.com"),
            "an email that only contains example.com": changed(JANE, "email", "jane" + "@" + "example.com.evil.org"),
            "a phone outside 555-0100 to 555-0199": changed(JANE, "phone", "(617) 555-" + "0999"),
            "a phone without the 555 exchange": changed(JANE, "phone", "(617) 432-" + "0142"),
            "no name": without(JANE, "name"),
            "links not a list": changed(JANE, "links", "https://example.com"),
        }
        for name, data in cases.items():
            with self.subTest(name):
                self.assertNotEqual(resume.problems_with(data), [])

    def test_every_rule_field_is_required_with_its_type(self):
        for dotted in resume.RULE_FIELDS:
            with self.subTest(missing=dotted):
                self.assertIn(f"{dotted} is missing", resume.problems_with(without(JANE, dotted)))
        wrong = {
            "experience.full_time_years": "3",
            "work_authorization.needs_sponsorship": 1,
            "work_authorization.us_person": "no",
            "availability.earliest_full_time_start": "2027-13",
            "preferences.employment_types": [],
            "preferences.title_includes": ["Software Engineer", ""],
            "preferences.cities": "Austin",
        }
        for dotted, value in wrong.items():
            with self.subTest(wrong=dotted):
                self.assertTrue(any(p.startswith(dotted) for p in resume.problems_with(changed(JANE, dotted, value))))
        self.assertNotEqual(resume.problems_with(changed(JANE, "experience.full_time_years", True)), [])

    def test_a_refusal_names_fields_but_never_their_values(self):
        bad = changed(JANE, "email", "jane.doe" + "@" + "gmail.com")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "real.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(Refused) as caught:
                resume.load(path)
        self.assertIn("email", str(caught.exception))
        self.assertNotIn("gmail", str(caught.exception))

    def test_claude_never_gets_contact_fields(self):
        sent = resume.for_claude(JANE)
        for key in resume.CONTACT_FIELDS:
            self.assertNotIn(key, sent)
        text = json.dumps(sent)
        for value in (JANE["name"], JANE["email"], JANE["phone"], *JANE["links"]):
            self.assertNotIn(value, text)
        self.assertEqual(sent["preferences"], JANE["preferences"])

    def test_field_paths_cover_nested_fields_and_list_items(self):
        paths = resume.field_paths(resume.for_claude(JANE))
        for path in ("experience.full_time_years", "experience.roles", "experience.roles[0].title", "skills.languages",
                     "education[0].degree", "preferences.title_excludes"):
            self.assertIn(path, paths)
        self.assertNotIn("email", paths)


if __name__ == "__main__":
    unittest.main()
