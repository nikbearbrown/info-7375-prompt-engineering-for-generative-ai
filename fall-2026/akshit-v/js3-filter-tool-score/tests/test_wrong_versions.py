"""FILTER.md section 4: each wrong version must be caught. All postings here are CONSTRUCTED.

Each test checks the real code, then shows the wrong version fails the same check.
"""
import unittest

from agent3 import claims, filter as flt
from tests import wrong_versions as wv

FILLER = " We value curiosity, collaboration, and clear writing about the systems we build together." * 4


def posting(pid, title, text, board="ashby:snowflake", employment_type="FullTime"):
    return {"id": f"{board}:{pid}", "board": board, "title": title, "content_text": text + FILLER,
            "employment_type": employment_type}


# CONSTRUCTED: the only "Snowflake" is the employer. Real score: role 4 + skills Python, SQL = 6.
EMPLOYER_ONLY = posting("c-wv1", "Data Engineer",
                        "Join Snowflake. At Snowflake you will write Python and SQL every day.")


class WV1EmployerNameAsSkill(unittest.TestCase):
    def check(self, cfg):
        r = flt.apply(EMPLOYER_ONLY, cfg)
        self.assertNotIn("Snowflake", r["skill_hits"])
        self.assertEqual(r["skills"], 2)
        self.assertEqual(r["score"], 6)

    def test_real_code(self):
        self.check(flt.V1_0)

    def test_same_text_on_another_board_counts_it(self):
        other = {**EMPLOYER_ONLY, "id": "lever:spotify:c-wv1", "board": "lever:spotify", "employment_type": "Permanent"}
        self.assertIn("Snowflake", flt.apply(other, flt.V1_0)["skill_hits"])

    def test_wrong_version_is_caught(self):
        with self.assertRaises(AssertionError):
            self.check(wv.WV1_CFG)

    def test_wrong_version_flips_a_verdict(self):
        # CONSTRUCTED: no role word; Python, SQL, Spark, dbt, AWS = 5, below 6. Counting the employer makes it 6.
        p = posting("c-wv1b", "Solution Engineer", "Snowflake customers use Python, SQL, Spark, dbt and AWS.")
        self.assertEqual(flt.apply(p, flt.V1_0)["verdict"], "reject")
        self.assertEqual(flt.apply(p, wv.WV1_CFG)["verdict"], "keep")


class WV2KeywordPresentIsSupported(unittest.TestCase):
    P = posting("c-wv2", "Data Engineer", "You will build pipelines in Python. Nice to have: experience with Spark.")
    CLAIM = {"kind": "has", "claim": "The role requires Spark, which the job seeker has.",
             "quote": "Nice to have: experience with Spark"}

    @staticmethod
    def meaning_says_insufficient(claim, posting):
        return {"label": "insufficient", "why": "a nice-to-have is not a requirement", "checked_by": "stub"}

    def test_real_code(self):
        self.assertTrue(claims.quote_in_posting(self.CLAIM["quote"], self.P))   # the quote IS verbatim
        out = claims.label_claim(self.CLAIM, self.P, self.meaning_says_insufficient)
        self.assertEqual(out["label"], "insufficient")

    def test_wrong_version_is_caught(self):
        out = wv.wv2_label_claim(self.CLAIM, self.P, self.meaning_says_insufficient)
        self.assertNotEqual(out["label"], "insufficient")

    def test_quote_not_in_posting_never_reaches_meaning_check(self):
        def boom(claim, posting):
            raise AssertionError("meaning check must not run on a fabricated quote")
        out = claims.label_claim({**self.CLAIM, "quote": "Spark is required"}, self.P, boom)
        self.assertEqual(out["label"], "insufficient")


class WV3MissingDataIsNotRelevant(unittest.TestCase):
    SHORT = {"id": "greenhouse:figma:c-wv3", "board": "greenhouse:figma", "title": "Data Engineer",
             "content_text": "Apply on our careers page. Details soon.", "employment_type": None}

    def test_real_code(self):
        r = flt.apply(self.SHORT, flt.V1_0)
        self.assertEqual(r["verdict"], "cannot_tell")
        self.assertEqual(claims.answer(r, [])["answer"], "cannot_tell")
        self.assertEqual(claims.answer(None, None, board_failed=True)["answer"], "cannot_tell")

    def test_wrong_version_is_caught(self):
        self.assertNotEqual(wv.wv3_answer(self.SHORT), "cannot_tell")
        self.assertNotEqual(wv.wv3_answer(None, board_failed=True), "cannot_tell")


class WV4ThresholdOffByOne(unittest.TestCase):
    # CONSTRUCTED: role 4 + skills Python, SQL = exactly 6.
    SIX = posting("c-wv4-6", "Data Engineer", "Daily work in Python and SQL.")
    # CONSTRUCTED: role 4 + skill Python + topic T1 (ETL) = 6 too; and a 5: role 4 + Python.
    FIVE = posting("c-wv4-5", "Data Engineer", "Daily work in Python.")

    def check(self, cfg):
        res = flt.run([self.FIVE, self.SIX], cfg)
        self.assertEqual(res["results"][self.SIX["id"]]["score"], 6)
        self.assertEqual(res["results"][self.SIX["id"]]["verdict"], "keep")
        self.assertEqual(res["results"][self.FIVE["id"]]["verdict"], "reject")
        self.assertEqual(res["ranked"], [self.SIX["id"]])

    def test_real_code(self):
        self.check(flt.V1_0)

    def test_wrong_version_is_caught(self):
        with self.assertRaises(AssertionError):
            self.check(wv.WV4_CFG)


if __name__ == "__main__":
    unittest.main()
