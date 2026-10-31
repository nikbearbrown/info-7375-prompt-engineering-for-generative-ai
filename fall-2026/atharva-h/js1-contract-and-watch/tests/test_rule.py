import unittest
from unittest import mock

from helpers import OFFER, RESUME, posting

import rule


def verdict(p):
    return rule.judge(p, RESUME)["verdict"]


class WrongVersionOneBroadTitles(unittest.TestCase):
    """CONTRACT wrong version 1: accepting any title with "analyst" or "analytics"."""

    def test_target_title_is_relevant_when_every_check_passes(self):
        self.assertEqual(verdict(posting("Data Analyst")), "relevant")

    def test_near_miss_titles_are_not_relevant_with_other_fields_constant(self):
        for title in ("Payer Analytics Consultant", "Sales Operations Analyst"):
            with self.subTest(title=title):
                record = rule.judge(posting(title), RESUME)
                self.assertEqual(record["verdict"], "not_relevant")
                self.assertEqual(record["checks"]["title"]["outcome"], "fail")

    def test_the_broad_keyword_mutant_is_caught(self):
        def broad(p, resume):
            hit = any(w in p["title"].lower() for w in ("analyst", "analytics"))
            return {"outcome": "pass" if hit else "fail", "reason": "broad", "cites": [], "matched": "x"}
        with mock.patch.object(rule, "check_title", broad):
            self.assertEqual(verdict(posting("Payer Analytics Consultant")), "relevant")
            self.assertEqual(verdict(posting("Sales Operations Analyst")), "relevant")


class WrongVersionTwoSilenceMeansRejection(unittest.TestCase):
    """CONTRACT wrong version 2: treating no sponsorship statement as not_relevant."""
    SILENT = "<p>Join our analytics team and build dashboards.</p>"

    def test_silence_on_sponsorship_is_needs_human(self):
        record = rule.judge(posting("Data Analyst", "Boston, MA", self.SILENT), RESUME)
        self.assertEqual(record["verdict"], "needs_human")
        self.assertEqual(record["checks"]["sponsorship"]["outcome"], "unclear")

    def test_the_silence_means_rejection_mutant_is_caught(self):
        def strict(p, resume):
            found = "sponsor" in rule.description_text(p["content"]).lower()
            return {"outcome": "pass" if found else "fail", "reason": "strict", "cites": []}
        with mock.patch.object(rule, "check_sponsorship", strict):
            self.assertEqual(verdict(posting("Data Analyst", "Boston, MA", self.SILENT)), "not_relevant")


class Seniority(unittest.TestCase):
    def test_excluded_words_rule_out_a_matching_title(self):
        for title in ("Senior Business and Data Analyst", "Sr. Data Analyst", "Lead BI Analyst",
                      "Data Analyst Manager", "Head of Business Intelligence Analyst Team"):
            with self.subTest(title=title):
                self.assertEqual(verdict(posting(title)), "not_relevant")

    def test_allowed_words_and_contractor_prefix(self):
        for title in ("Junior Data Analyst", "Associate Business Analyst", "Entry Level BI Analyst",
                      "Contractor: Data Analyst"):
            with self.subTest(title=title):
                self.assertEqual(verdict(posting(title)), "relevant")


class Location(unittest.TestCase):
    def test_us_locations_pass(self):
        for loc in ("US Remote", "Remote - US", "United States", "New York, NY; Pittsburgh, PA",
                    "Santa Fe, New Mexico", "Bengaluru, India; Boston, MA", "Lebanon, NH"):
            with self.subTest(location=loc):
                self.assertEqual(verdict(posting(location=loc)), "relevant")

    def test_only_non_us_places_are_not_relevant(self):
        for loc in ("Pune, India", "India", "Nepal", "Beirut, Lebanon", "ES - Barcelona, Spain"):
            with self.subTest(location=loc):
                self.assertEqual(verdict(posting(location=loc)), "not_relevant")

    def test_remote_without_country_is_needs_human(self):
        self.assertEqual(verdict(posting(location="Remote")), "needs_human")

    def test_conflicting_location_fields_are_needs_human(self):
        p = posting(location="India", offices=[{"name": "US", "location": "United States"}])
        self.assertEqual(verdict(p), "needs_human")


class Sponsorship(unittest.TestCase):
    def test_denials_are_not_relevant(self):
        for text in ("We are unable to sponsor visas for this position.",
                     "Candidates must be authorized to work without current or future sponsorship.",
                     "This role is open to U.S. citizens and permanent residents only.",
                     "We accept H-1B transfers only."):
            with self.subTest(text=text):
                self.assertEqual(verdict(posting(content=f"<p>{text}</p>")), "not_relevant")

    def test_vague_or_generic_statements_are_needs_human(self):
        for text in ("Visa sponsorship may be available for exceptional candidates.",
                     "Applicants must be authorized to work in the United States."):
            with self.subTest(text=text):
                self.assertEqual(verdict(posting(content=f"<p>{text}</p>")), "needs_human")

    def test_explicit_offers_pass(self):
        for text in ("We sponsor H-1B visas for this role.", "We offer visa sponsorship."):
            with self.subTest(text=text):
                self.assertEqual(verdict(posting(content=f"<p>{text}</p>")), "relevant")


class Experience(unittest.TestCase):
    def check(self, body):
        return verdict(posting(content=OFFER + body))

    def test_mandatory_minimum_above_two_years_is_not_relevant(self):
        self.assertEqual(self.check("<h3>Requirements</h3><ul><li>3+ years of experience in SQL</li></ul>"),
                         "not_relevant")

    def test_preferred_experience_is_ignored(self):
        self.assertEqual(self.check("<h3>Preferred Qualifications</h3><ul><li>5+ years of experience</li></ul>"),
                         "relevant")

    def test_two_years_or_a_range_starting_low_passes(self):
        self.assertEqual(self.check("<p>2+ years of experience required.</p>"), "relevant")
        self.assertEqual(self.check("<p>1-3 years of experience required.</p>"), "relevant")

    def test_masters_alternative_passes(self):
        self.assertEqual(self.check("<h3>Requirements</h3><ul><li>3+ years of experience or a Master's "
                                    "degree in analytics</li></ul>"), "relevant")

    def test_unclear_whether_mandatory_is_needs_human(self):
        self.assertEqual(self.check("<p>You have 4+ years of experience with dashboards.</p>"), "needs_human")

    def test_years_that_are_not_experience_are_ignored(self):
        self.assertEqual(self.check("<p>We have been growing for 10+ years.</p>"), "relevant")


class ExclusionsFirst(unittest.TestCase):
    """CONTRACT failure sentence: never `relevant` despite a clear exclusion."""

    def test_clear_exclusion_wins_over_missing_fields(self):
        self.assertEqual(verdict(posting(title="", location="Pune, India")), "not_relevant")

    def test_no_clear_exclusion_ever_yields_relevant(self):
        exclusions = [posting(title="Payer Analytics Consultant"), posting(title="Senior Data Analyst"),
                      posting(location="Nepal"), posting(content="<p>We cannot sponsor visas.</p>"),
                      posting(content=OFFER + "<h3>Requirements</h3><p>5+ years of experience required.</p>")]
        for p in exclusions:
            for loc in ("Remote", "Boston, MA"):
                with self.subTest(title=p["title"], location=loc):
                    q = dict(p, location={"name": loc}) if p["location"]["name"] != "Nepal" else p
                    self.assertEqual(verdict(q), "not_relevant")


if __name__ == "__main__":
    unittest.main()
