"""FILTER.md v1 evidence rules C1-C4. Written from FILTER.md before agent3 existed.

Every posting here is CONSTRUCTED. Each label must quote the exact text it rests on
(a substring of the field it read), or say "no text found" when insufficient.
"""
import unittest

from tests.js3_helpers import FILLER, ashby, body, claim, flt, gh, skills, sl

NO_TEXT = "no text found"


class Quoting(unittest.TestCase):
    def assertLabel(self, posting, label_dict, label, quoted=None):
        self.assertEqual(label_dict["label"], label, label_dict)
        if label == "insufficient":
            self.assertEqual(label_dict["quote"], NO_TEXT)
            return
        quote = label_dict["quote"]
        self.assertTrue(quote and quote != NO_TEXT)
        source = posting["location"] if label_dict["field"] in ("location", "location.name") else posting["text"]
        self.assertIn(quote, source, "a quote must be exact text from the field it read")
        if quoted:
            self.assertIn(quoted.lower(), quote.lower())


class C1USBased(Quoting):
    def test_supported_quotes_the_us_part(self):
        p = gh(location="Toronto, ON; New York City, NY")
        self.assertLabel(p, claim(p, 1), "supported", "New York City, NY")

    def test_contradicted_when_every_part_is_outside_the_us(self):
        p = gh(location="London, UK; Toronto, ON")
        self.assertLabel(p, claim(p, 1), "contradicted", "London, UK")

    def test_insufficient_when_location_missing(self):
        p = gh(drop=("location",))
        self.assertLabel(p, claim(p, 1), "insufficient")


class C2UsesSkill(Quoting):
    def test_supported_for_a_skill_found_as_a_whole_word(self):
        p = gh(content=body("Pipelines run on Databricks with SQL."))
        self.assertLabel(p, claim(p, 2, "Databricks"), "supported", "Databricks")
        self.assertLabel(p, claim(p, 2, "SQL"), "supported", "SQL")

    def test_insufficient_for_a_skill_not_named(self):
        p = gh(content=body("Pipelines run on Databricks."))
        self.assertLabel(p, claim(p, 2, "Mem0"), "insufficient")

    def test_never_inferred_from_a_related_word(self):
        p = gh(content=body("We use Spark, PostgreSQL, a Lakehouse and Pythonic code."))
        for skill in ("Databricks", "SQL", "Delta Lake", "Python"):
            with self.subTest(skill=skill):
                self.assertLabel(p, claim(p, 2, skill), "insufficient")

    def test_quote_rests_on_the_whole_word_match(self):
        # Found in the real run (faire:8806617002): the quote showed the "MySQL" sentence.
        p = gh(content=body("Data lands from MySQL and Postgres. You will write SQL daily."))
        c = claim(p, 2, "SQL")
        self.assertLabel(p, c, "supported", "write SQL daily")
        self.assertNotIn("MySQL", c["quote"])

    def test_filter_defines_no_contradiction_for_c2(self):
        p = gh(content=body("We do not use Python here."))
        self.assertEqual(claim(p, 2, "Python")["label"], "supported")


class C3SponsorsVisas(Quoting):
    def test_supported_only_when_explicit(self):
        for sentence in ("We sponsor H-1B visas for this role.", "Visa sponsorship is available.",
                         "We will support your visa application."):
            with self.subTest(sentence=sentence):
                p = gh(content=body(sentence))
                self.assertLabel(p, claim(p, 3), "supported", sentence.rstrip("."))

    def test_contradicted_cases(self):
        for sentence in ("We are unable to sponsor visas for this position.",
                         "We do not sponsor visas.",
                         "Candidates must be authorized to work in the US without sponsorship.",
                         "This role requires US citizenship.",
                         "An active security clearance is required."):
            with self.subTest(sentence=sentence):
                p = gh(content=body(sentence))
                self.assertLabel(p, claim(p, 3), "contradicted", sentence.rstrip("."))

    def test_silence_is_insufficient_never_supported(self):
        p = gh(content=body("We sponsor community hackathons and support open source."))
        self.assertLabel(p, claim(p, 3), "insufficient")
        p = gh(content=body())
        self.assertLabel(p, claim(p, 3), "insufficient")


class C4Remote(Quoting):
    def test_supported_from_location(self):
        p = gh(location="Remote - US")
        self.assertLabel(p, claim(p, 4), "supported", "Remote")

    def test_supported_from_text(self):
        p = gh(location="New York City, NY", content=body("This is a fully remote role."))
        self.assertLabel(p, claim(p, 4), "supported", "remote")

    def test_contradicted_by_onsite_in_office_or_hybrid(self):
        for sentence in ("This role is onsite five days a week.", "This position is in-office only.",
                         "We work a hybrid schedule, three days a week."):
            with self.subTest(sentence=sentence):
                p = gh(location="New York City, NY", content=body(sentence))
                self.assertLabel(p, claim(p, 4), "contradicted", sentence.split(" ")[3].rstrip(",."))

    def test_contradicted_from_location(self):
        p = gh(location="Israel - Hybrid (3 days/week in office required)")
        self.assertLabel(p, claim(p, 4), "contradicted", "Hybrid")

    def test_insufficient_when_nothing_said(self):
        p = gh(location="New York City, NY")
        self.assertLabel(p, claim(p, 4), "insufficient")


class Shortlist(unittest.TestCase):
    def test_only_accepted_postings_are_shortlisted_with_four_claims(self):
        good = gh("Data Scientist", content=body("We use SQL and Python. Visa sponsorship is available."))
        bad = gh("Software Engineer", content=body("SQL"))
        entries = sl().build_shortlist([good, bad], skills())
        self.assertEqual([e["posting_id"] for e in entries], [good["posting_id"]])
        claims = entries[0]["claims"]
        self.assertEqual({c["claim"] for c in claims}, {"C1", "C2", "C3", "C4"})
        c2 = [c for c in claims if c["claim"] == "C2"]
        self.assertEqual({c["text"] for c in c2}, {"Uses SQL", "Uses Python"})
        self.assertTrue(all(c["label"] == "supported" for c in c2))

    def test_ranked_by_supported_claims_not_keyword_count(self):
        repeats = gh("Data Analyst", content=body(" ".join(["data"] * 10) + " SQL."))
        repeats["posting_id"] = "greenhouse:faire:repeats"
        fewer = gh("Data Analyst", location="Remote - US",
                   content=body("We use SQL and Python on data. We sponsor H-1B visas."))
        fewer["posting_id"] = "greenhouse:faire:fewer"
        entries = sl().build_shortlist([repeats, fewer], skills())
        self.assertEqual([e["posting_id"] for e in entries],
                         ["greenhouse:faire:fewer", "greenhouse:faire:repeats"])


if __name__ == "__main__":
    unittest.main()
