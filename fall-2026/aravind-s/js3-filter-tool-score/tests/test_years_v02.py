"""My test for contract v0.2's years reading (my pick E, 2026-11-08), written before Claude Code's patch.

Check 7 must read a number of years in every sentence, not only in sentences that contain
"experience", except two wordings that are not requirements: "N years ago" and "the next N years".
Every line below is a real sentence, copied from a saved answer: posting 19 and "Software Engineer,
Data Infrastructure" on OpenAI (2026-10-30), and Verkada and Palantir from my live run 1 (2026-11-08).

Claude Code drafted this file from my pick; I ran it on 2026-11-08 at 5:45 PM ET, before any patch existed, and 4 of its
5 tests failed (the two that say a wording is not a requirement passed).
"""

import unittest
from pathlib import Path

from job_agent import providers, resume, rule

REPO = Path(__file__).resolve().parent.parent
JANE = resume.load(REPO / "persona" / "jane-doe.json")
POSTING_19 = "9efcef02-0515-4672-bace-81329944b38b"
DATA_INFRASTRUCTURE = "f763c6b3-5167-4a67-b691-4c3fa2c44156"


def years(line):
    return [n for n, _ in rule.years_asked(line)]


class YearsReadingV02Test(unittest.TestCase):
    def test_posting_19s_requirement_is_read(self):
        line = "- 5+ years in one or more of: ML systems, performance engineering, distributed systems, or HPC."
        self.assertEqual(years(line), [5])

    def test_a_greenhouse_requirement_without_the_word_experience_is_read(self):
        line = "2+ years productionizing modern LLMs, VLMs, or agentic systems (evals, guardrails, latency/cost tuning)."
        self.assertEqual(years(line), [2])

    def test_years_ago_is_not_a_requirement(self):
        line = ("The first of its kind in the tech industry, Palantir’s PCL team was formed 15+ years ago as a "
                "rejection of the prevailing view that privacy protections must be sacrificed to national security "
                "interest.")
        self.assertEqual(years(line), [])

    def test_the_next_n_years_is_not_a_requirement(self):
        line = ("Your job is to help us put down the right processes, expand the team, put together the right "
                "strategy, and be hands-on with our key partners to help us 5x the business over the next 3 years.")
        self.assertEqual(years(line), [])

    def test_both_openai_postings_are_no_longer_relevant_for_jane(self):
        postings = providers.read("ashby", 200, (REPO / "runs" / "2026-10-30T093102Z" / "response.json").read_bytes())
        for posting_id in (POSTING_19, DATA_INFRASTRUCTURE):
            posting = next(p for p in postings if p["id"] == posting_id)
            with self.subTest(title=posting["title"]):
                verdict = rule.judge(posting, JANE)
                self.assertEqual((verdict["verdict"], verdict["deciding_check"]), ("not_relevant", 7))


if __name__ == "__main__":
    unittest.main()
