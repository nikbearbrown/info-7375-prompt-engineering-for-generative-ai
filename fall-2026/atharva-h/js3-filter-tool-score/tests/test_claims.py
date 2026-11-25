"""The claim checker and the abstention rule. No model is called: these test what happens to Claude's output."""
import unittest

import claims as C

P = {"title": "Data Analyst, SF", "locations": ["San Francisco", "US"],
     "text": "Minimum of 1+ years of experience.\nProficient in  SQL &\nExcel."}


class Checker(unittest.TestCase):
    def test_quote_found_after_whitespace_collapse(self):
        self.assertTrue(C.found("Proficient in SQL & Excel.", P))
        self.assertTrue(C.found("San Francisco; US", P))  # locations joined as the prompt shows them

    def test_field_names_and_paraphrases_are_not_posting_text(self):
        self.assertFalse(C.found("Locations: San Francisco", P))
        self.assertFalse(C.found("Proficient in SQL and Excel", P))
        self.assertFalse(C.found("", P))

    def test_an_unfound_quote_makes_the_claim_insufficient_whatever_claude_said(self):
        self.assertEqual(C.label({"status": "supported", "quote": "made up"}, P), ("insufficient", False))
        self.assertEqual(C.label({"status": "contradicted", "quote": "Minimum of 1+ years"}, P), ("contradicted", True))
        self.assertEqual(C.label(None, P), ("insufficient", False))

    def test_parse_takes_the_json_even_with_text_around_it(self):
        out = C.parse('Here:\n{"claims": [{"property": "role", "status": "supported", "quote": "Data Analyst"}]}')
        self.assertEqual(out["role"]["status"], "supported")


class Abstention(unittest.TestCase):
    def labels(self, **over):
        base = dict.fromkeys(C.CLAIMS, "supported")
        base.update(over)
        return base

    def test_abstains_on_role_seniority_or_location_only(self):
        for prop in C.ABSTAIN_ON:
            self.assertEqual(C.answer(self.labels(**{prop: "insufficient"}), P), "I cannot tell")
        for prop in ("years", "sponsorship", "skills"):
            self.assertEqual(C.answer(self.labels(**{prop: "insufficient"}), P), "keep")

    def test_a_missing_description_always_abstains(self):
        self.assertEqual(C.answer(self.labels(), dict(P, text=None)), "I cannot tell")

    def test_each_variant_changes_one_thing_in_the_prompt(self):
        base = C.prompt(P, "base")
        self.assertIn(C.EXACT, base)
        self.assertEqual(C.prompt(P, "loose-quote"), base.replace(C.EXACT, ""))
        self.assertEqual(C.prompt(P, "no-field-names"), base.replace(C.EXACT, C.EXACT + C.NO_FIELDS))
        self.assertNotIn("Proficient", C.prompt(P, "title-only"))
        self.assertEqual(C.prompt(P, "base-rerun"), base)


if __name__ == "__main__":
    unittest.main()
