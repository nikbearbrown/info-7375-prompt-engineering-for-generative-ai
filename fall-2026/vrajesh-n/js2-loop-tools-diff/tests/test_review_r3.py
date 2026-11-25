"""Review packet test, written BEFORE the patch (review/REVIEW-PACKET.md step 2).

Defect, reproduced in run2-live (2026-11-01): Greenhouse postings carry no country field, so R3 rejected every
one with "posting country is None", including Databricks "Software Engineer - New Grad (2027 Start)" in
Bellevue / Mountain View / San Francisco, and the validator flagged 10 records citing a field that does not exist.
All postings below are real, from the responses run2-live saved in data/raw/2026-11-01/.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from earlybird import boards, rule, validate  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402

RESUME = load_resume(ROOT / "data/resume/rohan-desai.example.json")
RAW = ROOT / "data/raw/2026-11-01"


def greenhouse(board):
    return boards.parse("greenhouse", (RAW / f"greenhouse_{board}.json").read_bytes())


def posting(board, pid):
    return next(p for p in greenhouse(board) if p["id"] == pid)


class GreenhouseCountry(unittest.TestCase):
    def test_us_new_grad_posting_is_not_rejected_by_r3(self):
        p = posting("databricks", "6865698002")  # Bellevue, Washington; ...; Vancouver, Canada
        rec = rule.judge(p, RESUME)
        self.assertNotEqual(rec["failed_check"], "R3", rec["justification"])
        self.assertEqual(validate.errors(rec, p, RESUME), [])

    def test_non_us_posting_still_fails_r3(self):
        rec = rule.judge(posting("stripe", "7895287"), RESUME)  # Sao Paulo
        self.assertEqual(rec["failed_check"], "R3")

    def test_every_greenhouse_record_cites_only_fields_that_exist(self):
        bad = []
        for board in ("stripe", "figma", "gleanwork", "databricks", "doordashusa", "twitch", "roblox"):
            for p in greenhouse(board):
                errs = validate.errors(rule.judge(p, RESUME), p, RESUME)
                if errs:
                    bad.append((board, p["title"], errs[0]))
        self.assertEqual(bad[:3], [], f"{len(bad)} records cite a missing field")

    def test_location_strings_seen_in_real_data(self):
        """Expected country for location strings copied from the 2026-11-01 Greenhouse responses."""
        cases = {
            "San Mateo, CA, United States": "USA",
            "United States": "USA",
            "San Francisco, CA • New York, NY • United States": "USA",
            "Mountain View, California; San Francisco, California": "USA",
            "United States - Remote": "USA",
            "Remote - US": "USA",
            "US-Remote": "USA",
            "Washington, D.C.": "USA",
            "Remote - California": "USA",
            "Bellevue, Washington; Mountain View, California; San Francisco, California; Vancouver, Canada": "USA",
            "Singapore": None,
            "Bengaluru, India": None,
            "London, United Kingdom": None,
            "Toronto, Canada": None,
            "Sao Paulo": None,
            "Dublin": None,
            "N/A": None,
        }
        for text, want in cases.items():
            p = boards.normalize("greenhouse", {"id": 1, "title": "x", "location": {"name": text}})
            got = ((p.get("address") or {}).get("postalAddress") or {}).get("addressCountry")
            self.assertEqual(got, want, text)


class Revision(unittest.TestCase):
    """Vrajesh's revision (review step 6, 2026-11-10), written BEFORE the revised code: 'Toronto, CA' is Canada;
    bare US city names resolve to the US; 'Keep It to United States Only' (no world city list).
    Every string below is copied from the 2026-11-01 Greenhouse responses (review/5-location-audit.txt)."""

    def country(self, text):
        p = boards.normalize("greenhouse", {"id": 1, "title": "x", "location": {"name": text}})
        return p["address"]["postalAddress"]["addressCountry"]

    def test_canadian_city_with_CA_is_not_california(self):
        for text in ("Toronto, CA",):
            self.assertIsNone(self.country(text), text)

    def test_california_CA_still_us(self):
        for text in ("Dublin, CA; San Francisco, CA", "San Francisco, CA", "Mountain View, CA"):
            self.assertEqual(self.country(text), "USA", text)

    def test_bare_us_city_names_resolve_to_us(self):
        for text in ("Chicago", "San Francisco", "San Francisco Bay Area", "Seattle", "NYC", "NYC, SF",
                     "New York City", "SEA, SF, NY, Toronto"):
            self.assertEqual(self.country(text), "USA", text)

    def test_non_us_bare_cities_stay_unknown(self):
        for text in ("Dublin", "London", "Toronto", "Bengaluru", "Singapore", "Sydney", "Barcelona", "Remote", "N/A"):
            self.assertIsNone(self.country(text), text)


if __name__ == "__main__":
    unittest.main()
