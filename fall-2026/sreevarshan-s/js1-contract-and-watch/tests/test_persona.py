import json
import unittest
from pathlib import Path

from js1.persona import PersonaRefused, load_persona, validate

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "persona" / "priya-nair.resume.json"
PROFILE = ROOT / "persona" / "priya-nair.profile.json"
SOURCE_RESUME = Path(
    "~/Downloads/Reallocation/the-reallocation-engine/"
    "search/examples/priya-nair/resume.example.json"
)


class PersonaTests(unittest.TestCase):
    def test_priya_persona_passes(self):
        resume, profile = load_persona(RESUME, PROFILE)
        self.assertEqual(resume["personal"]["email"], "priya.nair@example.com")
        self.assertTrue(profile["_source"].endswith("priya-nair/profile.yml"))

    @unittest.skipUnless(SOURCE_RESUME.exists(), "Reallocation Engine checkout not present")
    def test_resume_is_an_unchanged_copy(self):
        self.assertEqual(RESUME.read_bytes(), SOURCE_RESUME.read_bytes())

    def test_profile_contact_matches_resume(self):
        resume = json.loads(RESUME.read_text(encoding="utf-8"))
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile["candidate"]["email"], resume["personal"]["email"])
        self.assertEqual(profile["candidate"]["phone"], resume["personal"]["phone"])

    def test_refuses_real_looking_email(self):
        # CONSTRUCTED persona fragment
        with self.assertRaises(PersonaRefused):
            validate({"personal": {"email": "someone@gmail.com", "phone": "(617) 555-0100"}})

    def test_refuses_email_hidden_in_free_text(self):
        with self.assertRaises(PersonaRefused):
            validate({"bullets": ["Contact me at someone@northeastern.edu"]})

    def test_refuses_phone_without_555(self):
        with self.assertRaises(PersonaRefused):
            validate({"personal": {"email": "a@example.com", "phone": "(617) 373-2000"}})

    def test_refuses_phone_hidden_in_free_text(self):
        with self.assertRaises(PersonaRefused):
            validate({"notes": "call 617-373-2000"})

    def test_refuses_unparseable_phone_field_without_555(self):
        with self.assertRaises(PersonaRefused):
            validate({"phone": "+1 6173732000"})


if __name__ == "__main__":
    unittest.main()
