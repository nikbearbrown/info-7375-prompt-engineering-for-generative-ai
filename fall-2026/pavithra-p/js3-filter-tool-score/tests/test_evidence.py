"""The evidence rules (FILTER.md section 4) on CONSTRUCTED postings and claims."""
import unittest

from agent import evidence as ev
from tests.jobs import SKILLS, SPEC, job

J = job(content="<p>We’re hiring a backend engineer. 1-2 years building services in Python and Kafka.</p>")


def label(about, claim, quote, j=J):
    return ev.label_claim({"about": about, "claim": claim, "quote": quote}, j, SPEC, SKILLS)


class Labels(unittest.TestCase):
    def test_quote_not_in_posting_is_insufficient(self):
        self.assertEqual(label("role", "Backend role", "You will lead the backend team")[0], ev.INSUFFICIENT)

    def test_empty_quote_is_insufficient(self):
        self.assertEqual(label("role", "Backend role", "")[0], ev.INSUFFICIENT)

    def test_quote_present_is_supported_but_marked_for_a_hand_check(self):
        lab, _, hand = label("role", "Backend role", "hiring a backend engineer")
        self.assertEqual((lab, hand), (ev.SUPPORTED, True))

    def test_curly_quote_and_spacing_are_normalised(self):
        self.assertEqual(label("role", "Backend role", "We're  hiring a backend engineer")[0], ev.SUPPORTED)

    def test_experience_contradicted_by_years(self):
        j = job(content="<p>5+ years of Python and Kafka</p>")
        self.assertEqual(label("experience", "Fits two years", "Python and Kafka", j)[0], ev.CONTRADICTED)

    def test_experience_claim_that_states_the_years_is_not_contradicted(self):
        j = job(content="<p>5+ years of Python and Kafka</p>")
        self.assertEqual(label("experience", "It asks for 5+ years, so Rohan falls short", "5+ years of Python and Kafka", j)[0],
                         ev.SUPPORTED)

    def test_experience_contradicted_by_senior_in_the_text(self):
        j = job(content="<p>We're looking for a Senior Backend Engineer to build Python and Kafka services.</p>")
        self.assertEqual(label("experience", "Fits two years", "build Python and Kafka services", j)[0], ev.CONTRADICTED)

    def test_location_contradicted_outside_the_us(self):
        j = job(location="London, UK")
        self.assertEqual(label("location", "Can work there", "London, UK", j)[0], ev.CONTRADICTED)

    def test_skills_quote_without_a_resume_skill_is_insufficient(self):
        self.assertEqual(label("skills", "Uses Python", "hiring a backend engineer")[0], ev.INSUFFICIENT)

    def test_claim_about_something_not_covered_is_cannot_tell(self):
        lab, why, _ = label("role", "Offers visa sponsorship", "hiring a backend engineer")
        self.assertEqual(lab, ev.INSUFFICIENT)
        self.assertIn("cannot tell", why)


class Abstain(unittest.TestCase):
    def test_all_three_supported_does_not_abstain(self):
        self.assertFalse(ev.abstain([("role", ev.SUPPORTED), ("experience", ev.SUPPORTED), ("location", ev.SUPPORTED),
                                     ("skills", ev.INSUFFICIENT)]))

    def test_experience_not_supported_abstains(self):
        self.assertTrue(ev.abstain([("role", ev.SUPPORTED), ("experience", ev.INSUFFICIENT), ("location", ev.SUPPORTED)]))

    def test_missing_location_claim_abstains(self):
        self.assertTrue(ev.abstain([("role", ev.SUPPORTED), ("experience", ev.SUPPORTED)]))


if __name__ == "__main__":
    unittest.main()
