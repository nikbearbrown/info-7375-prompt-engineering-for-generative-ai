"""Regression test for the defect found in patch revision 1 by reading its behavior diff
(review/03-finding-rev1.txt). Written 2026-11-09, BEFORE patch revision 2. It must fail on rev 1.

The 16 REAL Linear postings (tests/fixtures/linear_perk_postings.json) list the perk "Paid month
off after 4 years & every 2 years thereafter" after "Health coverage (based on country
requirements)". Rule v1 did not fail condition 5 on any of them; rev 1 did, because of the perk."""
import json
import pathlib
import unittest

from jsagent import persona, providers, rule
from tests import helpers

FX = json.loads((pathlib.Path(__file__).parent / "fixtures" / "linear_perk_postings.json").read_text())
POSTINGS = providers.parse("ashby", "linear", 200, json.dumps({"jobs": FX["jobs"]}).encode())[0]
VIEW = persona.public_view(helpers.load_persona())


class PerkIsNotARequirement(unittest.TestCase):
    def test_sixteen_real_postings(self):
        self.assertEqual(len(POSTINGS), 16)
        for p in POSTINGS:
            rec = rule.judge(p, VIEW)
            c5 = next(l for l in rec["conditions"] if l["n"] == 5)
            self.assertNotIn("thereafter", c5["detail"], p["title"])
            self.assertNotIn(5, rec["failed_conditions"], p["title"])

    def test_constructed_requirement_word_inside_benefits(self):
        # CONSTRUCTED: the same trap in a small posting.
        p = providers.parse("ashby", "x", 200, json.dumps({"jobs": [{
            "id": "c1", "title": "Software Engineer", "department": "Engineering", "location": "Boston, MA",
            "descriptionPlain": "You will build services in Python and SQL. What we offer: Health coverage "
                                "(based on country requirements). Paid month off after 4 years."}]}).encode())[0][0]
        self.assertNotIn(5, rule.judge(p, VIEW)["failed_conditions"])


if __name__ == "__main__":
    unittest.main()
