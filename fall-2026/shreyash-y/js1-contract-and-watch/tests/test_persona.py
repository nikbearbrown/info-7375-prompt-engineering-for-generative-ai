"""The resume is a validated fictional persona; no real contact details in the folder."""
import json
import re
import unittest

from jsagent import persona
from tests import helpers


class PersonaValidation(unittest.TestCase):
    def test_shipped_persona_is_valid(self):
        self.assertEqual(persona.validate(helpers.load_persona()), [])

    def test_missing_field_rejected(self):
        p = helpers.load_persona()
        del p["skills"]
        self.assertTrue(persona.validate(p))

    def test_real_looking_email_rejected(self):
        p = helpers.load_persona()
        p["contact"]["email"] = "someone@gmail.com"
        self.assertTrue(any("example.com" in e for e in persona.validate(p)))

    def test_non_555_phone_rejected(self):
        p = helpers.load_persona()
        p["contact"]["phone"] = "(617) 373-2000"
        self.assertTrue(any("555" in e for e in persona.validate(p)))

    def test_not_marked_fictional_rejected(self):
        p = helpers.load_persona()
        p["fictional"] = False
        self.assertTrue(persona.validate(p))

    def test_wrong_types_rejected(self):
        p = helpers.load_persona()
        p["experience_years"] = "three"
        self.assertTrue(persona.validate(p))

    def test_public_view_has_no_contact(self):
        view = persona.public_view(helpers.load_persona())
        self.assertNotIn("contact", view)
        self.assertNotIn("@", json.dumps(view))


class FolderHasNoRealContacts(unittest.TestCase):
    """Scans every text file in this folder. Emails must be @example.com (or the
    noreply addresses git and Anthropic use); phone numbers must use 555."""
    ALLOWED_EMAIL = re.compile(r"@(example\.com|anthropic\.com|users\.noreply\.github\.com)$")
    SKIP_DIRS = {"raw", "__pycache__", "calls"}

    def files(self):
        for path in helpers.FOLDER.rglob("*"):
            if path.is_file() and not (set(path.relative_to(helpers.FOLDER).parts) & self.SKIP_DIRS) \
                    and path.suffix in {".md", ".json", ".py", ".txt", ".csv", ".jsonl"}:
                yield path

    def test_emails(self):
        for path in self.files():
            for email in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", path.read_text(errors="ignore")):
                self.assertRegex(email, self.ALLOWED_EMAIL, f"{path}: {email}")

    def test_phones(self):
        for path in self.files():
            for m in re.findall(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b", path.read_text(errors="ignore")):
                digits = re.sub(r"\D", "", m)
                self.assertEqual(digits[3:6], "555", f"{path}: {m}")


if __name__ == "__main__":
    unittest.main()
