"""Tests written from FILTER.md v1 section 5 (evidence rules) before jsagent3/evidence.py existed."""
import unittest

from jsagent3.evidence import label_claim, sections

REQ_JAVA = ("About the team\nWe build payments.\nRequirements\n- 0-2 years of experience\n- Java and SQL\n"
            "Preferred qualifications\n- Kotlin\n")
PREF_JAVA = ("About the team\nWe build payments.\nRequirements\n- Strong Go skills\n- SQL\n"
             "Nice to have\n- Java\n")
INLINE_PREF = "Requirements\n- Python\n- Experience with Java is a plus\n"
NO_LANG = "About the team\nWe build payments.\nRequirements\n- Strong communication\n- Distributed systems\n"
ABOUT_ONLY = "About us\nOur stack includes Java and Ruby.\nRequirements\n- Strong communication\n"
SENIOR_YEARS = "Requirements\n- 6+ years of backend experience\n- Java\n"


def P(body, title="Software Engineer", location="Seattle, WA"):
    return {"id": "t:1", "title": title, "body": body, "location": location}


def java_req():
    return {"type": "skill", "skill": "Java", "strength": "required"}


class Sections(unittest.TestCase):
    def test_headings_classified(self):
        kinds = [k for k, _ in sections(REQ_JAVA)]
        self.assertIn("required", kinds)
        self.assertIn("preferred", kinds)
        self.assertIn("other", kinds)

    def test_intro_sentence_does_not_flip_section(self):
        body = ("Requirements\nThe preferred qualifications are a bonus, not a requirement.\n- Java\n")
        self.assertEqual(label_claim(java_req(), P(body))["label"], "supported")


class SkillClaims(unittest.TestCase):
    def test_required_section_supports(self):
        r = label_claim(java_req(), P(REQ_JAVA))
        self.assertEqual(r["label"], "supported")
        self.assertIn("Java", r["quote"])

    def test_preferred_only_contradicts_required_claim(self):  # W2, evidence half
        self.assertEqual(label_claim(java_req(), P(PREF_JAVA))["label"], "contradicted")

    def test_inline_plus_is_preferred(self):
        self.assertEqual(label_claim(java_req(), P(INLINE_PREF))["label"], "contradicted")

    def test_preferred_claim_supported_by_preferred_mention(self):
        c = {"type": "skill", "skill": "Java", "strength": "preferred"}
        self.assertEqual(label_claim(c, P(PREF_JAVA))["label"], "supported")

    def test_mention_outside_required_is_insufficient(self):  # Java only in "About us"
        self.assertEqual(label_claim(java_req(), P(ABOUT_ONLY))["label"], "insufficient")

    def test_javascript_never_supports_java(self):
        r = label_claim(java_req(), P("Requirements\n- JavaScript\n"))
        self.assertNotEqual(r["label"], "supported")


class Abstention(unittest.TestCase):
    def test_no_language_says_i_cannot_tell(self):  # s5 abstention
        r = label_claim(java_req(), P(NO_LANG, title="Java Developer"))
        self.assertEqual(r["label"], "insufficient")
        self.assertEqual(r["answer"], "I cannot tell")

    def test_other_language_only_is_insufficient_not_abstain(self):
        r = label_claim(java_req(), P("Requirements\n- Go\n"))
        self.assertEqual(r["label"], "insufficient")
        self.assertNotEqual(r.get("answer"), "I cannot tell")


class LevelAndLocation(unittest.TestCase):
    def test_years_contradict_early_career(self):
        c = {"type": "level", "value": "early-career"}
        self.assertEqual(label_claim(c, P(SENIOR_YEARS))["label"], "contradicted")
        self.assertEqual(label_claim(c, P(REQ_JAVA))["label"], "supported")
        self.assertEqual(label_claim(c, P(NO_LANG))["label"], "insufficient")

    def test_intern_title_supports_early_career(self):
        c = {"type": "level", "value": "early-career"}
        self.assertEqual(label_claim(c, P(NO_LANG, title="Software Engineer, Intern"))["label"], "supported")

    def test_us_claim(self):
        c = {"type": "us"}
        self.assertEqual(label_claim(c, P(NO_LANG, location="Seattle, WA"))["label"], "supported")
        self.assertEqual(label_claim(c, P(NO_LANG, location="Dublin"))["label"], "contradicted")
        self.assertEqual(label_claim(c, P(NO_LANG, location="N/A"))["label"], "insufficient")

    def test_every_label_has_reason(self):
        for c in [java_req(), {"type": "us"}, {"type": "level", "value": "early-career"}]:
            self.assertTrue(label_claim(c, P(NO_LANG))["why"])


if __name__ == "__main__":
    unittest.main()


class CurlyApostrophe(unittest.TestCase):
    """Found 2026-11-25 while inspecting held-out #14: Stripe writes "What you’ll do" with U+2019."""

    def test_curly_heading_is_required(self):
        body = "What you’ll do\n- Build REST APIs in Java\n"
        self.assertEqual([k for k, _ in sections(body)][1], "required")


class SpelledYears(unittest.TestCase):
    """Found 2026-11-25 reading shortlist postings stripe:8411927 / 8197135: 'four (4) years of experience'."""

    def test_parenthesised_years(self):
        from jsagent3.evidence import min_required_years
        body = "Minimum requirements\nMust have a degree plus four (4) years of related experience.\n"
        self.assertEqual(min_required_years(body)[0], 4)
        c = {"type": "level", "value": "early-career"}
        self.assertEqual(label_claim(c, P(body))["label"], "contradicted")


class StrictestYearsWins(unittest.TestCase):
    def test_base_requirement_beats_sub_skill_years(self):  # stripe:8411988 wording
        from jsagent3.evidence import min_required_years
        body = ("Minimum requirements\nMust have a degree plus three (3) years of work experience.\n"
                "Must also have one (1) year of experience in each of the following:\n")
        self.assertEqual(min_required_years(body)[0], 3)


class SentenceMeaning(unittest.TestCase):
    """Labeler fix 2026-11-25, designed from the 16 shortlist claims (dev set: labels/shortlist-claims-dev.csv).

    Being in a required section is not enough: the sentence must make the skill required.
    """

    def test_example_list_is_insufficient(self):  # stripe:6042172, stripe:8231439
        body = "Minimum requirements\n- Ability to write high-quality code (in programming languages like Go, Java, C/C++ etc.)\n"
        self.assertEqual(label_claim(java_req(), P(body))["label"], "insufficient")

    def test_or_list_is_insufficient(self):
        body = "Requirements\n- Writing high quality code in programming languages including Go, Java, or C/C++;\n"
        self.assertEqual(label_claim(java_req(), P(body))["label"], "insufficient")

    def test_plain_requirement_still_supported(self):
        body = "Requirements\n- Strong experience with Java and SQL\n"
        self.assertEqual(label_claim(java_req(), P(body))["label"], "supported")

    def test_helpful_curiosity_is_preferred(self):  # notion Collections Infra
        body = ("Skills you'll need\n- Curiosity about distributed systems, microservices, and data-layer trade-offs; "
                "experience in these areas is helpful\n")
        c = {"type": "skill", "skill": "distributed systems", "strength": "required"}
        self.assertEqual(label_claim(c, P(body))["label"], "contradicted")

    def test_prose_under_about_the_role_is_not_a_requirement(self):  # notion Collections Infra, microservices
        body = ("About the role\nAs an engineer you'll help scale infrastructure built on microservices across teams.\n"
                "Skills you'll need\n- Strong fundamentals\n")
        c = {"type": "skill", "skill": "microservices", "strength": "required"}
        self.assertEqual(label_claim(c, P(body))["label"], "insufficient")

    def test_open_ended_years_range_does_not_establish_early_career(self):  # stripe:6042172
        c = {"type": "level", "value": "early-career"}
        body = "Minimum requirements\n- 2–12+ years of professional software development experience\n"
        self.assertEqual(label_claim(c, P(body))["label"], "insufficient")
        self.assertEqual(label_claim(c, P("Requirements\n- 2+ years of backend experience\n"))["label"], "supported")


class AbstentionCounterexamples(unittest.TestCase):
    """The two counterexamples in SHORTLIST.md, now handled: the posting *does* say Java is not required."""

    def test_language_agnostic_contradicts_instead_of_abstaining(self):  # stripe:6567104
        body = ("Requirements\n- Strong coding skills in any programming language (you can learn new languages on the "
                "job, and our interview process is language agnostic)\n")
        r = label_claim(java_req(), P(body))
        self.assertEqual(r["label"], "contradicted")
        self.assertNotEqual(r["answer"], "I cannot tell")

    def test_can_be_learned_contradicts_required(self):  # stripe:8128744
        body = ("Requirements\n- Experience with programming. We work mostly in Java, Ruby, JavaScript, Scala, and Go. "
                "We believe new programming languages can be learned if the fundamentals are present.\n")
        self.assertEqual(label_claim(java_req(), P(body))["label"], "contradicted")
