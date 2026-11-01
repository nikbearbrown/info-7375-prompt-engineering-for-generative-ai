import json
import tempfile
import unittest
from pathlib import Path

from jsagent.resume import NotFictional, load_resume, validate_persona
from tests import fixtures as F


class PersonaTests(unittest.TestCase):
    def test_shipped_persona_is_accepted(self):
        self.assertEqual(load_resume(F.PERSONA)["personal"]["name"], "Rohan Desai")

    def test_real_looking_resume_refused(self):
        for field, value in [("email", "someone@gmail.com"), ("phone", "(617) 373-2000")]:
            r = F.persona()
            r["personal"][field] = value
            with self.subTest(field=field), self.assertRaises(NotFictional):
                validate_persona(r)

    def test_unmarked_resume_refused(self):
        r = F.persona()
        r["_comment"] = "my resume"
        with self.assertRaises(NotFictional):
            validate_persona(r)

    def test_private_filename_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "resume.json"
            path.write_text(json.dumps(F.persona()))
            with self.assertRaises(NotFictional):
                load_resume(path)


if __name__ == "__main__":
    unittest.main()
