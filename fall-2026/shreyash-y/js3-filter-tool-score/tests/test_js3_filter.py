"""FILTER.md v1, as tests. Written by Claude Code on 2026-11-25 from FILTER.md (commits 5e6a7703 and
3163fdb5) BEFORE js3/filtering.py existed, so the first run fails on the import. Each test names the
FILTER.md answer it checks. Shreyash's five wrong versions (answer 12) are WV1-WV5.

Constructed postings are marked "constructed"; the Physician Reviewer posting is REAL (JS2 fixture)."""
import json
import pathlib
import unittest

from js3 import filtering, sections
from jsagent import posting as js2_posting

HERE = pathlib.Path(__file__).resolve().parent.parent
PERSONA = json.loads((HERE / "persona" / "alex_morgan.json").read_text())
CFG = filtering.load_config(HERE / "filter-v1.json")

GOOD_LINES = ("What you'll do:", "Build backend services for our product.",
              "Requirements:", "You write Python and SQL every day.",
              "2+ years of experience building web services.")


def P(title="Software Engineer II", departments=("Engineering",), location="Boston, MA", offices=("Boston",),
      lines=GOOD_LINES, board="testboard", ats="greenhouse", employment_type=None, workplace_type=None,
      pid="1"):
    """A constructed posting with plain-text lines (one block per line)."""
    content = "\n".join(lines)
    return {"board": board, "ats": ats, "id": pid, "key": f"{board}:{pid}", "title": title,
            "departments": list(departments), "location": location, "offices": list(offices),
            "content": content, "blocks": sections.blocks_for_plain(content),
            "employment_type": employment_type, "workplace_type": workplace_type, "url": None}


def ev(p):
    return filtering.evaluate(p, PERSONA, CFG)


def outcome(rec, n):
    return rec["rules"][n - 1]["outcome"]


PASS, FAIL, UNSURE = "pass", "fail", "cannot tell"


class Baseline(unittest.TestCase):
    def test_constructed_good_posting_passes_all_six(self):
        rec = ev(P())
        self.assertEqual([outcome(rec, n) for n in range(1, 7)], [PASS] * 6)
        self.assertEqual(rec["verdict"], "Relevant")
        self.assertFalse(rec["closest_call"])
        self.assertEqual(rec["filter_version"], "v1")


class Rule1Title(unittest.TestCase):
    """Answer 4: the title must contain a role phrase."""

    def test_role_phrase(self):
        self.assertEqual(outcome(ev(P(title="Software Engineer II, Growth")), 1), PASS)
        self.assertEqual(outcome(ev(P(title="AI/ML Engineer")), 1), PASS)

    def test_no_role_phrase(self):
        self.assertEqual(outcome(ev(P(title="Product Engineer")), 1), FAIL)

    def test_whole_phrase_only(self):
        self.assertEqual(outcome(ev(P(title="Software Engineering Coordinator")), 1), FAIL)
        self.assertEqual(outcome(ev(P(title="HTML Engineer")), 1), FAIL)

    def test_missing_title_fails_and_says_missing(self):
        line = ev(P(title=""))["rules"][0]
        self.assertEqual(line["outcome"], FAIL)
        self.assertIn("missing", line["detail"])


class Rule2Department(unittest.TestCase):
    """Answer 5, with review/19: Palantir's Dev counts as engineering, for Palantir only."""

    def test_listed_department(self):
        self.assertEqual(outcome(ev(P(departments=["Product", "Engineering"])), 2), PASS)

    def test_palantir_dev_is_engineering(self):
        self.assertEqual(outcome(ev(P(board="palantir", ats="lever", departments=["Dev"])), 2), PASS)

    def test_dev_elsewhere_is_not(self):
        self.assertEqual(outcome(ev(P(board="otherco", ats="lever", departments=["Dev"])), 2), FAIL)

    def test_missing_department_fails(self):
        line = ev(P(departments=[]))["rules"][1]
        self.assertEqual(line["outcome"], FAIL)
        self.assertIn("missing", line["detail"])


class Rule3Location(unittest.TestCase):
    """Answer 6, 6a, 6b and follow-up A. WV1: a remote job that cannot be worked from Massachusetts."""

    def test_boston(self):
        self.assertEqual(outcome(ev(P()), 3), PASS)

    def test_wv1_remote_tag_limited_to_another_state(self):
        p = P(location="Remote", offices=["Remote (Florida)"])
        self.assertEqual(outcome(ev(p), 3), FAIL)

    def test_wv1_ad_lists_states_without_massachusetts(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "You must reside in one of the following states: Texas, Florida, Georgia.",))
        self.assertEqual(outcome(ev(p), 3), FAIL)

    def test_remote_anywhere_in_the_us(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This role is remote anywhere in the United States.",))
        self.assertEqual(outcome(ev(p), 3), PASS)

    def test_remote_massachusetts_tag(self):
        self.assertEqual(outcome(ev(P(location="Remote", offices=["Remote (Massachusetts)"])), 3), PASS)

    def test_6a_tag_and_ad_disagree_is_cannot_tell(self):
        p = P(location="Remote", offices=["Remote (Arizona)"], lines=GOOD_LINES + (
            "This is a remote position, open to candidates who reside in the United States.",))
        self.assertEqual(outcome(ev(p), 3), UNSURE)

    def test_6a_real_physician_reviewer_is_cannot_tell(self):
        """REAL Oscar posting (JS2 fixture). Office tag 'Remote (Arizona)'; the ad says 'reside in the
        United States'. Shreyash's answer 6a: when they disagree, say I cannot tell."""
        fx = json.loads((HERE / "tests" / "fixtures" / "physician_reviewer.json").read_text())
        rec = ev(filtering.from_raw("greenhouse", "oscar", fx["job"]))
        self.assertEqual(outcome(rec, 3), UNSURE)
        self.assertEqual(rec["verdict"], "Not Relevant", "title, department and skills still fail")

    def test_A_remote_tag_but_ad_says_hybrid_elsewhere_is_rejected(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This is a hybrid role with 3 days a week in our New York office.",))
        self.assertEqual(outcome(ev(p), 3), FAIL)

    def test_A_still_unclear_is_cannot_tell(self):
        p = P(location="Remote", offices=["Remote"], lines=GOOD_LINES + (
            "This is a hybrid role with 3 days a week in our New York office.",
            "Fully remote work within the United States is also possible."))
        self.assertEqual(outcome(ev(p), 3), UNSURE)

    def test_hybrid_in_boston_passes(self):
        p = P(lines=GOOD_LINES + ("This is a hybrid role with 3 days a week in our Boston office.",))
        self.assertEqual(outcome(ev(p), 3), PASS)

    def test_6b_field_and_offices_disagree_description_says_boston(self):
        p = P(location="San Francisco, CA", offices=["Boston"], lines=GOOD_LINES + (
            "You will work from our Boston office.",))
        self.assertEqual(outcome(ev(p), 3), PASS)

    def test_6b_description_says_the_other_city(self):
        p = P(location="San Francisco, CA", offices=["Boston"], lines=GOOD_LINES + (
            "You will work from our San Francisco office.",))
        self.assertEqual(outcome(ev(p), 3), FAIL)

    def test_6b_description_silent_is_cannot_tell(self):
        p = P(location="San Francisco, CA", offices=["Boston"])
        self.assertEqual(outcome(ev(p), 3), UNSURE)

    def test_not_boston_not_remote(self):
        self.assertEqual(outcome(ev(P(location="New York, NY", offices=["New York"])), 3), FAIL)

    def test_missing_location_fails_and_says_missing(self):
        line = ev(P(location="", offices=[]))["rules"][2]
        self.assertEqual(line["outcome"], FAIL)
        self.assertIn("missing", line["detail"])


class Rule4Skills(unittest.TestCase):
    """Answer 7. WV2: skills named only under employee benefits do not count."""

    def test_wv2_skills_only_in_benefits_fail(self):
        p = P(lines=("What you'll do:", "Build backend services.", "Benefits:",
                     "A learning budget for Python and SQL courses."))
        self.assertEqual(outcome(ev(p), 4), FAIL)

    def test_same_skills_in_requirements_pass(self):
        p = P(lines=("What you'll do:", "Build backend services.", "Requirements:",
                     "You know Python and SQL."))
        self.assertEqual(outcome(ev(p), 4), PASS)

    def test_whole_terms_only(self):
        p = P(lines=("Requirements:", "You know JavaScript and PostgreSQL."))
        self.assertEqual(outcome(ev(p), 4), FAIL)

    def test_one_skill_is_not_enough(self):
        self.assertEqual(outcome(ev(P(lines=("Requirements:", "You know Python."))), 4), FAIL)


class Rule5Experience(unittest.TestCase):
    """Answer 8 and follow-up B. WV3: a job that requires more than 3 years."""

    def test_wv3_five_years_fails(self):
        p = P(lines=("Requirements:", "You know Python and SQL.",
                     "5+ years of professional software engineering experience."))
        self.assertEqual(outcome(ev(p), 5), FAIL)

    def test_two_years_passes(self):
        self.assertEqual(outcome(ev(P()), 5), PASS)

    def test_range_starting_at_three_passes(self):
        p = P(lines=("Requirements:", "You know Python and SQL.", "3-5 years of experience in backend work."))
        self.assertEqual(outcome(ev(p), 5), PASS)

    def test_preferred_years_do_not_count(self):
        p = P(lines=("Requirements:", "You know Python and SQL.", "Preferred qualifications:",
                     "5+ years of experience with distributed systems."))
        self.assertEqual(outcome(ev(p), 5), PASS)

    def test_B_not_stated_passes_marked_not_stated_with_no_quote(self):
        line = ev(P(lines=("Requirements:", "You know Python and SQL.")))["rules"][4]
        self.assertEqual(line["outcome"], PASS)
        self.assertIn("not stated", line["detail"])
        self.assertEqual(line["evidence"], [], "no quote may be invented for a missing requirement")


class Rule6Exclusions(unittest.TestCase):
    """Answer 9 and follow-up C."""

    def test_seniority_words(self):
        for t in ("Staff Software Engineer", "Lead Software Engineer", "Principal Software Engineer",
                  "Software Engineering Manager, Software Engineer track", "Director, Software Engineer Hiring"):
            self.assertEqual(outcome(ev(P(title=t)), 6), FAIL, t)

    def test_senior_and_leadership_are_not_excluded_words(self):
        self.assertEqual(outcome(ev(P(title="Senior Software Engineer")), 6), PASS)
        self.assertEqual(outcome(ev(P(title="Software Engineer, Leadership Tools")), 6), PASS)

    def test_internships_are_out(self):
        self.assertEqual(outcome(ev(P(title="Software Engineer, Intern")), 6), FAIL)
        self.assertEqual(outcome(ev(P(title="Software Engineer", employment_type="Internship")), 6), FAIL)

    def test_C_part_time_and_temporary_are_out(self):
        self.assertEqual(outcome(ev(P(title="Part-time Software Engineer")), 6), FAIL)
        self.assertEqual(outcome(ev(P(lines=GOOD_LINES + ("This is a temporary position for six months.",))), 6), FAIL)
        self.assertEqual(outcome(ev(P(employment_type="PartTime")), 6), FAIL)

    def test_full_time_type_passes(self):
        self.assertEqual(outcome(ev(P(employment_type="FullTime")), 6), PASS)
        self.assertEqual(outcome(ev(P(employment_type="Full-time")), 6), PASS)

    def test_contract_unpaid_relocation(self):
        self.assertEqual(outcome(ev(P(title="Software Engineer (Contract)")), 6), FAIL)
        self.assertEqual(outcome(ev(P(lines=GOOD_LINES + ("This is an unpaid position.",))), 6), FAIL)
        p = P(location="Austin, TX", offices=["Austin"], lines=GOOD_LINES + ("Relocation is required.",))
        self.assertEqual(outcome(ev(p), 6), FAIL)


class FinalDecision(unittest.TestCase):
    """Answer 10, the closest call, and how 'I cannot tell' combines with the rest (FILTER-NOTES.md)."""

    def test_one_fail_is_a_closest_call(self):
        rec = ev(P(title="Product Engineer"))
        self.assertEqual(rec["verdict"], "Not Relevant")
        self.assertEqual(rec["failed"], [1])
        self.assertTrue(rec["closest_call"])

    def test_two_fails_is_not_a_closest_call(self):
        rec = ev(P(title="Product Engineer", location="New York, NY", offices=["New York"]))
        self.assertEqual(rec["failed"], [1, 3])
        self.assertFalse(rec["closest_call"])

    def test_cannot_tell_and_nothing_failed(self):
        rec = ev(P(location="San Francisco, CA", offices=["Boston"]))
        self.assertEqual(rec["verdict"], "I cannot tell")
        self.assertEqual(rec["unsure"], [3])
        self.assertFalse(rec["closest_call"])

    def test_a_fail_wins_over_cannot_tell(self):
        rec = ev(P(title="Product Engineer", location="San Francisco, CA", offices=["Boston"]))
        self.assertEqual(rec["verdict"], "Not Relevant")
        self.assertFalse(rec["closest_call"], "the other rules do not all pass")


class EvidenceQuotes(unittest.TestCase):
    """Evidence rules (answer 11). WV4: the agent makes up a quote when information is missing."""

    def postings(self):
        fx = json.loads((HERE / "tests" / "fixtures" / "physician_reviewer.json").read_text())
        return [P(), P(title="Product Engineer"), P(location="San Francisco, CA", offices=["Boston"]),
                P(lines=("Requirements:", "You know Python.")),
                filtering.from_raw("greenhouse", "oscar", fx["job"])]

    def test_every_quote_is_in_the_field_it_names(self):
        for p in self.postings():
            rec = ev(p)
            self.assertEqual(filtering.verify_quotes(rec, p), [], p["title"])
            self.assertTrue(any(line["evidence"] for line in rec["rules"]))

    def test_wv4_a_made_up_quote_is_caught(self):
        p = P()
        rec = ev(p)
        rec["rules"][4]["evidence"] = [{"field": "content", "quote": "1+ years of experience required"}]
        problems = filtering.verify_quotes(rec, p)
        self.assertEqual(len(problems), 1)
        self.assertIn("not in posting.content", problems[0])

    def test_from_raw_content_is_exactly_js2s(self):
        fx = json.loads((HERE / "tests" / "fixtures" / "physician_reviewer.json").read_text())
        self.assertEqual(filtering.from_raw("greenhouse", "oscar", fx["job"])["content"],
                         js2_posting.normalize(fx["job"], "oscar")["content"])


if __name__ == "__main__":
    unittest.main()
