"""The written rule (CONTRACT.md, The rule; wrong version 2).

Constructed postings test each check on its own; the worked example and the whole-board counts use
the real baseline response committed in runs/2026-10-30T093102Z/.
"""

import collections
import copy
import json
import unittest

from job_agent import rule
from job_agent import resume as resume_mod

from .helpers import PERSONA, REPO, job

JANE = resume_mod.load(PERSONA)
BASELINE = REPO / "runs" / "2026-10-30T093102Z" / "response.json"
EXPORT = ("To comply with U.S. export control laws and regulations, candidates for this role may need to meet "
          "certain legal status requirements as provided in those laws and applicable regulations.")


def posting(title="Software Engineer, Example Team", text="Build backend services.", **extra):
    return job("t-1", title, descriptionPlain=text, **extra)


def address(country, region=None, city=None):
    return {"postalAddress": {"addressCountry": country, "addressRegion": region, "addressLocality": city}}


def verdict(p, persona=JANE):
    return rule.judge(p, persona)


class EachCheckTest(unittest.TestCase):
    def assertDecided(self, p, check, persona=JANE):
        result = verdict(p, persona)
        self.assertEqual(result["verdict"], "not_relevant", result["lines"])
        self.assertEqual(result["deciding_check"], check, result["lines"])

    def assertRelevant(self, p, persona=JANE):
        result = verdict(p, persona)
        self.assertEqual(result["verdict"], "relevant", result["lines"])
        return result

    def test_1_employment_type(self):
        self.assertDecided(posting(employmentType="Contract"), 1)
        self.assertDecided(posting(employmentType=None), 1)
        self.assertRelevant(posting(employmentType="fulltime"))  # matching ignores case

    def test_2_location(self):
        self.assertRelevant(posting(location="Seattle", address=address("United States", "Washington", "Seattle")))
        self.assertRelevant(posting(location="US - Remote", address=address("United States")))
        self.assertDecided(posting(location="Washington, DC", address=address("United States", "District of Columbia", "Washington")), 2)
        self.assertDecided(posting(location="London, UK", address=address("United Kingdom", "Greater London", "London")), 2)
        # A city on the list counts only in the United States.
        self.assertDecided(posting(location="Cambridge, UK", address=address("United Kingdom", "Cambridgeshire", "Cambridge")), 2)
        self.assertDecided(posting(location="Ontario - Remote", address=address("Canada", "Ontario")), 2)
        # A secondary location can fit when the primary one does not.
        london = dict(location="London, UK", address=address("United Kingdom", "Greater London", "London"))
        seattle = {"location": "Seattle", "address": address("United States", "Washington", "Seattle")}
        self.assertRelevant(posting(**london, secondaryLocations=[seattle]))

    def test_3_level(self):
        for title in ("Senior Software Engineer", "Sr. Software Engineer, API", "Staff Software Engineer",
                      "Software Engineer, Lead", "Engineering Manager, Platform", "Software Engineer Intern"):
            with self.subTest(title):
                self.assertDecided(posting(title), 3)
        # Whole words only: "Leadership" does not contain the word "Lead".
        self.assertRelevant(posting("Software Engineer, Leadership Tools"))

    def test_4_role(self):
        for title in ("Full Stack Software Engineer, Sales Platform", "Software Engineer - Codex for Finance",
                      "Backend Software Engineer, Applied Foundations", "Software Engineer (Backend)",
                      "Data Engineer", "Full-Stack Engineer, Education", "Studios Software Engineer"):
            with self.subTest(title):
                self.assertRelevant(posting(title))
        for title in ("Sales Engineer", "Research Engineer", "Machine Learning Engineer, Growth",
                      "Frontend Software Engineer, Codex App", "iOS Software Engineer",
                      "Forward Deployed Software Engineer - NYC", "Robotics Software Engineer",
                      "Network Infrastructure Engineer, WAN", "Security Engineer, Application Security"):
            with self.subTest(title):
                self.assertDecided(posting(title), 4)

    def test_5_status_blocks_only_on_the_listed_phrases(self):
        for text in ("This position requires U.S. person status as defined by the applicable government contract.",
                     "Applicants for this position must be U.S. citizens with the ability to obtain a background check.",
                     "Hold an active TS/SCI clearance and a current polygraph.",
                     "We are unable to sponsor visas for this role.",
                     "You must be authorized to work without sponsorship."):
            with self.subTest(text):
                self.assertDecided(posting(text=text), 5)

    def test_5_executive_sponsor_does_not_block(self):
        # Wrong version 2 ("any 'sponsor' blocks") fails here. A real sentence from the board.
        text = "You will serve as an executive technical sponsor for critical engagements."
        self.assertRelevant(posting(text=text))

    def test_5_itar_as_a_skill_does_not_block(self):
        self.assertRelevant(posting(text="Familiarity with public sector compliance frameworks (e.g., FedRAMP, ITAR/EAR)."))

    def test_5_the_export_control_sentence_passes_with_a_caution(self):
        result = self.assertRelevant(posting(text="Build backend services.\n" + EXPORT))
        self.assertEqual(len(result["cautions"]), 1)
        self.assertIn("may need to meet certain legal status requirements", result["cautions"][0])

    def test_5_phrases_follow_the_resume(self):
        us_person = copy.deepcopy(JANE)
        us_person["work_authorization"].update(us_person=True, needs_sponsorship=False)
        for text in ("This position requires U.S. person status.", "We are unable to sponsor visas for this role."):
            with self.subTest(text):
                self.assertRelevant(posting(text=text), persona=us_person)

    def test_6_start_date(self):
        for text in ("Candidates must be able to start immediately.", "We hope you can start in January 2027.",
                     "Ideal start date: Mar 2027, start then."):
            with self.subTest(text):
                self.assertDecided(posting(text=text), 6)
        for text in ("You would start in June 2027.", "Start dates are flexible.",
                     "Teams starting in January 2027 are hiring."):  # only the word "start" counts, as written
            with self.subTest(text):
                self.assertRelevant(posting(text=text))

    def test_7_years(self):
        passing = {"2-4 years of experience with Go.": 2, "1-3 years of experience, or 5+ years for senior scope.": 1,
                   "Three years of experience in backend systems.": 3, "3 to 5 years of experience.": 3,
                   "0–1 years of experience.": 0}
        for text, n in passing.items():
            with self.subTest(text):
                result = self.assertRelevant(posting(text=text))
                self.assertIn(f"N = {n}", result["checks"][6]["because"])
        for text in ("5+ years of experience building distributed systems.", "Four years of experience.",
                     "4 or more years of professional experience.", "Experienced engineers with 6+ years."):
            with self.subTest(text):
                self.assertDecided(posting(text=text), 7)

    def test_7_silence_and_years_outside_experience_sentences_pass(self):
        for text in ("Build backend services.", "We have grown 10x in 2 years. You will build services.",
                     "10+ years in the industry is a plus.", "1 year of experience is enough.",
                     "A 4 year degree or equivalent experience."):  # "years" only, as the contract writes it
            with self.subTest(text):
                result = self.assertRelevant(posting(text=text))
        self.assertIn("states no years", result["checks"][6]["because"])


class VerdictShapeTest(unittest.TestCase):
    def test_the_first_failing_check_decides_and_later_checks_are_not_run(self):
        result = verdict(posting("Senior Software Engineer", text="8+ years of experience."))
        self.assertEqual(result["deciding_check"], 3)
        self.assertEqual([c["number"] for c in result["checks"]], [1, 2, 3])

    def test_every_citation_names_a_posting_field_and_a_resume_field(self):
        for p in (posting(), posting("Senior Software Engineer"), posting(text="5+ years of experience.")):
            for c in verdict(p)["checks"]:
                self.assertTrue(c["posting_field"] and c["resume_field"], c)
                self.assertIn(c["resume_field"].split(",")[0].split(".")[0], json.dumps(JANE))

    def test_a_relevant_posting_cites_all_seven_checks(self):
        result = verdict(posting())
        self.assertEqual([c["number"] for c in result["checks"]], [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(len(result["lines"]), 7)


class RealBoardTest(unittest.TestCase):
    """On the real baseline response (2026-10-30T093102Z)."""

    @classmethod
    def setUpClass(cls):
        cls.jobs = json.loads(BASELINE.read_bytes())["jobs"]
        cls.verdicts = {j["id"]: rule.judge(j, JANE) for j in cls.jobs}

    def test_the_contracts_worked_example(self):
        result = self.verdicts["55150071-fce8-48f5-aea4-14ed78b83511"]
        self.assertEqual(result["verdict"], "relevant")
        self.assertTrue(all(c["passed"] for c in result["checks"]))
        self.assertIn("0-1 years of experience in software engineering or a relevant field", result["checks"][6]["because"])
        self.assertIn("N = 0", result["checks"][6]["because"])
        self.assertIn('region "California"', result["checks"][1]["because"])
        self.assertIn('"Software Engineer"', result["checks"][3]["because"])

    def test_the_whole_board_gives_the_same_counts_as_when_the_rule_was_chosen(self):
        # 95 relevant of 814 is the count shown when the years and title choices were made.
        decided = collections.Counter(v["deciding_check"] for v in self.verdicts.values())
        self.assertEqual(len(self.jobs), 814)
        self.assertEqual(decided[None], 95)
        self.assertEqual(dict(decided), {None: 95, 1: 1, 2: 196, 3: 239, 4: 234, 5: 1, 7: 48})

    def test_no_real_sponsor_sentence_blocks(self):
        sponsored = [j for j in self.jobs if "sponsor" in (j.get("descriptionPlain") or "").lower()]
        self.assertEqual(len(sponsored), 16)
        self.assertFalse(any(self.verdicts[j["id"]]["deciding_check"] == 5 and "sponsor" in
                             self.verdicts[j["id"]]["checks"][-1]["because"].lower() for j in sponsored))


if __name__ == "__main__":
    unittest.main()
