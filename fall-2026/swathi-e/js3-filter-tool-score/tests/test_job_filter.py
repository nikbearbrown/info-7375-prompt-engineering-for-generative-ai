"""Tests for job_filter.py (FILTER.md v1 and its revisions), written before the code.

R1a-R7b, SC1-SC7, E1-E5, W1 and W3 come from the test design Claude Code
proposed on 2026-11-17 and Swathi approved; D1-D6 check FILTER.md's
"Revision (2026-11-17, before any JS3 filter code): decisions D1-D7" (D7 is
about saved data and has no test). Wrong versions 2, 4, 5 and 6 are checked by
R6b, R5c, E4 and E3. The expected outcome of every test is recorded in
TEST-PREDICTIONS.md.

Every posting built in this file is SIMULATED: titles, locations and
descriptions are made up here in the shape of Stripe (h2 headings), Databricks
(bold-paragraph headings, content-intro/-conclusion blocks) or Plaid. Tests
marked REAL read the saved Nov 5 Plaid response, read-only. Nothing is
fetched. Written by Claude Code. Every test runs inside no_network().

job_filter, descriptions and the parser change are imported or called inside
each test, so each test reports its own missing piece.
"""
from contextlib import contextmanager
import importlib
import json
from pathlib import Path
import re
import socket
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import parsers  # noqa: E402
import rule  # noqa: E402

REAL_NOV5_PLAID = HERE / "runs" / "2026-11-05T23-11-48-228373-0500" / "005-plaid-request.json"
FRAUD_ANALYST = "1bcfe93d-97bd-4618-b81e-dc308ef69d30"
VERDICTS = {"shortlisted", "not shortlisted", "rejected", "I cannot tell"}

EXPORT_CONTROL = (  # SIMULATED, modeled on the kind of "Compliance" paragraph Databricks posts; not real text
    "If access to export-controlled technology or source code is required for performance of job "
    "duties, it is within the Employer's discretion whether to apply for a U.S. government license "
    "for such positions, and the Employer may decline to proceed with an applicant on this basis alone.")
EEO = (  # SIMULATED equal-opportunity sentence
    "We consider qualified applicants without regard to race, color, religion, sex, national origin, "
    "citizenship status, disability or veteran status.")


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def jf():
    return importlib.import_module("job_filter")


def stripe_html(*sections):
    """SIMULATED Stripe-style description: (heading, text) pairs as <h2> headings and paragraphs."""
    return "".join(f"<h2><strong>{h}</strong></h2>\n<p>{t}</p>\n" for h, t in sections)


def databricks_html(intro, sections, conclusion):
    """SIMULATED Databricks-style description: content-intro, bold-paragraph sections, content-conclusion."""
    body = "".join(f"<p><strong>{h}</strong></p>\n<ul><li>{t}</li></ul>\n" for h, t in sections)
    return (f'<div class="content-intro"><p>{intro}</p></div>\n{body}'
            f'<div class="content-conclusion"><p><strong>About Databricks</strong></p><p>{conclusion}</p>'
            f'<p><strong>Benefits</strong></p><p>Comprehensive benefits.</p></div>')


def posting(title="Machine Learning Engineer", location="Boston, Massachusetts", description=None, pid="sim-1"):
    """SIMULATED posting. The default description passes every rule: R5 0-1 years, R7 two topic words."""
    if description is None:
        description = stripe_html(("Responsibilities", "Build machine learning features in Python."),
                                  ("Who you are", "0-1 years of experience."))
    return {"id": pid, "title": title, "location": location, "url": "https://example.invalid/sim",
            "description_html": description}


def evaluate(p):
    with no_network():
        return jf().evaluate(p)


def result(res, rule_id):
    return res["rules"][rule_id]["result"]


def claim(res, name):
    return next(c for c in res["claims"] if c["claim"] == name)


def real_plaid():
    """REAL saved Nov 5 Plaid postings, parsed with descriptions (needs the parser change)."""
    with no_network():
        postings, _ = parsers.parse_ashby(REAL_NOV5_PLAID.read_bytes(), include_description=True)
    return {p["id"]: p for p in postings}


class R1Role(unittest.TestCase):
    def test_R1a_role_terms_whole_words(self):
        """R1a, FILTER.md R1 (role, title). SIMULATED titles: each role term matches as a whole
        word; "Maintenance" and "Email" do not match "AI"."""
        for title in ("AI Engineer", "ML Engineer", "Machine Learning Engineer", "GenAI Engineer",
                      "Data Engineer", "Data Engineering Associate", "Data Scientist", "Data Science Associate",
                      "Analytics Engineer"):
            with self.subTest(title=title):
                self.assertEqual(result(evaluate(posting(title=title)), "R1"), "pass")
        for title in ("Maintenance Technician", "Email Marketing Associate"):
            with self.subTest(title=title):
                self.assertEqual(result(evaluate(posting(title=title)), "R1"), "fail")

    def test_R1b_software_engineer_needs_early_career_word(self):
        """R1b, FILTER.md R1: "Software Engineer" counts only with New Grad, Early Career, Entry or
        University in the title. SIMULATED titles."""
        for title in ("Software Engineer, New Grad", "Software Engineer, Early Career",
                      "Entry Level Software Engineer", "Software Engineer - University Graduate"):
            with self.subTest(title=title):
                self.assertEqual(result(evaluate(posting(title=title)), "R1"), "pass")
        self.assertEqual(result(evaluate(posting(title="Software Engineer")), "R1"), "fail")


class R2Analyst(unittest.TestCase):
    BOILER_INTRO = "We are the data and AI company; our machine learning platform runs on SQL."

    def test_R2a_analyst_with_data_words_in_responsibilities(self):
        """R2a, FILTER.md R2. SIMULATED: a "Fraud Analyst" whose Responsibilities name SQL and data
        passes R2, and with 0-1 years is shortlisted."""
        res = evaluate(posting(title="Fraud Analyst", description=stripe_html(
            ("Responsibilities", "Write SQL queries to analyze data."), ("Who you are", "0-1 years of experience."))))
        self.assertEqual(result(res, "R2"), "pass")
        self.assertEqual(res["verdict"], "shortlisted")

    def test_R2b_data_words_only_in_boilerplate_do_not_count(self):
        """R2b, FILTER.md R2 and Revision (R2 sections). SIMULATED Databricks-style: data/AI words
        appear ONLY in the intro, About and Benefits blocks; R2 fails, so not shortlisted."""
        res = evaluate(posting(title="Fraud Analyst", description=databricks_html(
            self.BOILER_INTRO,
            [("Responsibilities", "Investigate suspicious accounts and escalate cases."),
             ("What we look for", "0-1 years of experience.")],
            "Databricks is the data and AI company, built on machine learning.")))
        self.assertEqual(result(res, "R2"), "fail")
        self.assertEqual(res["verdict"], "not shortlisted")

    def test_R2c_data_words_only_under_about_the_team_do_not_count(self):
        """R2c, FILTER.md Revision (R2 sections): "About the team" does not count. SIMULATED: data/AI
        words only under "About the team"; R2 fails, not shortlisted."""
        res = evaluate(posting(title="Fraud Analyst", description=stripe_html(
            ("About the team", "Our team builds SQL dashboards and AI tools on data."),
            ("Responsibilities", "Investigate suspicious accounts and escalate cases."),
            ("Who you are", "0-1 years of experience."))))
        self.assertEqual(result(res, "R2"), "fail")
        self.assertEqual(res["verdict"], "not shortlisted")

    def test_R2d_no_recognized_section_is_cannot_tell(self):
        """R2d, FILTER.md Revision (R2 sections): an Analyst posting with no recognized
        responsibilities or skills section gives "I cannot tell". SIMULATED."""
        res = evaluate(posting(title="Fraud Analyst", description=stripe_html(
            ("About Stripe", "Stripe builds data and AI infrastructure."),
            ("About the team", "We use SQL every day."))))
        self.assertEqual(result(res, "R2"), "cannot tell")
        self.assertEqual(res["verdict"], "I cannot tell")

    def test_R2e_real_fraud_analyst_passes_r2_from_responsibilities(self):
        """R2e, FILTER.md R2 (the JS2 Fraud Intelligence Analyst). REAL saved Plaid posting 1bcfe93d:
        R2 passes with a quote taken from a "counts" section; the posting is still rejected (R5)."""
        res = evaluate(real_plaid()[FRAUD_ANALYST])
        self.assertEqual(result(res, "R2"), "pass")
        self.assertTrue(res["rules"]["R2"]["quotes"])
        self.assertEqual(res["verdict"], "rejected")


class R3Seniority(unittest.TestCase):
    def test_R3a_each_seniority_term_rejects(self):
        """R3a, FILTER.md R3 (seniority, title). SIMULATED titles: each term rejects."""
        for title in ("Senior ML Engineer", "Staff ML Engineer", "Principal ML Engineer", "Lead ML Engineer",
                      "ML Team Leader", "ML Engineering Manager", "Director of AI", "Head of AI",
                      "ML Intern", "Machine Learning Internship"):
            with self.subTest(title=title):
                res = evaluate(posting(title=title))
                self.assertEqual(result(res, "R3"), "fail")
                self.assertEqual(res["verdict"], "rejected")

    def test_R3b_sr_and_sr_dot_are_the_same(self):
        """R3b, FILTER.md R3: "Sr" and "Sr." are treated the same; "Sr" inside a word does not count.
        SIMULATED titles."""
        for title in ("Sr ML Engineer", "Sr. ML Engineer"):
            with self.subTest(title=title):
                self.assertEqual(evaluate(posting(title=title))["verdict"], "rejected")
        self.assertEqual(result(evaluate(posting(title="Data Engineer, Srinivasan Lab")), "R3"), "pass")


class R4Location(unittest.TestCase):
    def test_R4a_us_locations_pass(self):
        """R4a, FILTER.md R4. SIMULATED locations in the US, and remote allowing the US, pass."""
        for location in ("Boston, Massachusetts", "United States", "Remote - US"):
            with self.subTest(location=location):
                self.assertEqual(result(evaluate(posting(location=location)), "R4"), "pass")

    def test_R4b_remote_limited_to_another_country_is_rejected(self):
        """R4b, FILTER.md R4: a remote posting limited to another country is rejected. SIMULATED."""
        for location in ("Remote - Germany", "London, United Kingdom"):
            with self.subTest(location=location):
                res = evaluate(posting(location=location))
                self.assertEqual(result(res, "R4"), "fail")
                self.assertEqual(res["verdict"], "rejected")

    def test_R4c_real_plaid_office_with_us_address_passes(self):
        """R4c, FILTER.md R4 and Plaid's address country (JS2 fix). REAL saved Plaid posting 1bcfe93d,
        "San Francisco HQ (United States)": R4 passes."""
        p = real_plaid()[FRAUD_ANALYST]
        self.assertEqual(p["location"], "San Francisco HQ (United States)")
        self.assertEqual(result(evaluate(p), "R4"), "pass")


class R5Experience(unittest.TestCase):
    def with_experience(self, text, heading="Who you are"):
        return posting(description=stripe_html(("Responsibilities", "Build machine learning features in Python."),
                                               (heading, text)))

    def test_R5a_early_career_evidence_passes(self):
        """R5a, FILTER.md R5. SIMULATED: "0-1 years", "new grad" and "entry level" in a "counts"
        section pass R5 with early-career evidence (2 points)."""
        for text in ("0-1 years of experience.", "This is a new grad role.", "This is an entry level role."):
            with self.subTest(text=text):
                res = evaluate(self.with_experience(text))
                self.assertEqual(result(res, "R5"), "pass")
                self.assertEqual(res["points"]["early"], 2)

    def test_R5b_more_than_one_year_is_rejected(self):
        """R5b, FILTER.md R5. SIMULATED: "2+ years" and "3-5 years" are rejected."""
        for text in ("2+ years of experience.", "3-5 years of experience."):
            with self.subTest(text=text):
                res = evaluate(self.with_experience(text))
                self.assertEqual(result(res, "R5"), "fail")
                self.assertEqual(res["verdict"], "rejected")

    def test_R5c_zero_to_two_years_is_rejected(self):
        """R5c, FILTER.md Revision (R5 ranges) and wrong version 4: "0-2 years" is rejected even
        though it starts at 0. SIMULATED."""
        res = evaluate(self.with_experience("0-2 years of experience."))
        self.assertEqual(result(res, "R5"), "fail")
        self.assertEqual(res["verdict"], "rejected")

    def test_R5d_en_dash_ranges_are_rejected(self):
        """R5d, FILTER.md R5. SIMULATED "2–4 years" (en dash) is rejected, and the REAL saved Plaid
        posting whose description asks "4–6 years" (en dash) is rejected with that quote."""
        res = evaluate(self.with_experience("2–4 years of experience."))
        self.assertEqual(res["verdict"], "rejected")
        real = [p for p in real_plaid().values() if p["id"].startswith("d2c9d8b1")]
        self.assertEqual(len(real), 1)
        res = evaluate(real[0])
        self.assertEqual(result(res, "R5"), "fail")
        self.assertTrue(any("4–6 years" in q for q in res["rules"]["R5"]["quotes"]))

    def test_R5e_not_for_new_graduates_is_rejected(self):
        """R5e, FILTER.md R5: a posting that says it is not for new graduates is rejected. SIMULATED."""
        res = evaluate(self.with_experience("This role is not for new graduates."))
        self.assertEqual(res["verdict"], "rejected")


class R6Authorization(unittest.TestCase):
    def with_text(self, text, heading="Who you are"):
        return posting(description=stripe_html(("Responsibilities", "Build machine learning features in Python."),
                                               ("Who you are", "0-1 years of experience."), (heading, text)))

    def test_R6a_requirement_wording_rejects(self):
        """R6a, FILTER.md R6 and D5. SIMULATED requirement sentences each reject."""
        for text in ("U.S. citizenship is required.", "An active security clearance is required.",
                     "We will not sponsor visas for this role.", "We are unable to sponsor visas.",
                     "You must be authorized to work without sponsorship."):
            with self.subTest(text=text):
                res = evaluate(self.with_text(text))
                self.assertEqual(result(res, "R6"), "fail")
                self.assertEqual(res["verdict"], "rejected")

    def test_R6b_export_control_paragraph_is_not_a_citizenship_requirement(self):
        """R6b, FILTER.md R6 and wrong version 2. SIMULATED export-control "Compliance" paragraph
        (modeled on Databricks, not real text): R6 passes and the posting is not rejected."""
        res = evaluate(self.with_text(EXPORT_CONTROL, heading="Compliance"))
        self.assertEqual(result(res, "R6"), "pass")
        self.assertEqual(res["verdict"], "shortlisted")

    def test_R6c_real_sponsorship_assets_is_not_a_visa_refusal(self):
        """R6c, FILTER.md R6 and D5 (only requirement wording rejects). REAL saved Plaid posting that
        mentions "sponsorship assets" (event sponsorship): R6 does not fail."""
        real = [p for p in real_plaid().values() if "sponsorship assets" in p["description_html"]]
        self.assertGreaterEqual(len(real), 1)
        for p in real:
            with self.subTest(id=p["id"]):
                self.assertNotEqual(result(evaluate(p), "R6"), "fail")


class R7Topics(unittest.TestCase):
    def test_R7a_distinct_topic_words_capped_at_three(self):
        """R7a, FILTER.md R7 and the score (each distinct topic word 1 point, at most 3). SIMULATED:
        five distinct topic words, one repeated, give 3 points."""
        res = evaluate(posting(description=stripe_html(
            ("Responsibilities", "Use machine learning, deep learning, LLM and NLP methods in Python. Python again."),
            ("Who you are", "0-1 years of experience."))))
        self.assertEqual(res["points"]["topics"], 3)

    def test_R7b_whole_words_only(self):
        """R7b, FILTER.md R7. SIMULATED: partial words such as "sparked" and "Pythonic" are not topic
        words; 0 topic points."""
        res = evaluate(posting(description=stripe_html(
            ("Responsibilities", "Our launch sparked growth; write Pythonic scripts."),
            ("Who you are", "0-1 years of experience."))))
        self.assertEqual(res["points"]["topics"], 0)


class Score(unittest.TestCase):
    def test_SC1_role_plus_early_career_is_shortlisted(self):
        """SC1, FILTER.md score: role 3 + early-career 2 = 5 >= threshold 5. SIMULATED posting with
        no topic words: score 5, shortlisted."""
        res = evaluate(posting(description=stripe_html(("Responsibilities", "Build features."),
                                                       ("Who you are", "0-1 years of experience."))))
        self.assertEqual((res["score"], res["verdict"]), (5, "shortlisted"))

    def test_SC2_role_plus_two_topics_reaches_threshold(self):
        """SC2, FILTER.md score arithmetic: role 3 + two topic words = 5, shortlisted (score function)."""
        f = jf()
        self.assertEqual(f.score_points(role=True, early=False, topics=2), 5)
        self.assertTrue(f.is_shortlisted(5, role=True))

    def test_SC3_role_plus_one_topic_is_below_threshold(self):
        """SC3, FILTER.md score arithmetic: role 3 + one topic word = 4, not shortlisted."""
        f = jf()
        self.assertEqual(f.score_points(role=True, early=False, topics=1), 4)
        self.assertFalse(f.is_shortlisted(4, role=True))

    def test_SC4_topic_points_capped(self):
        """SC4, FILTER.md score: topic points stop at 3, so role + 5 topic words = 6."""
        self.assertEqual(jf().score_points(role=True, early=False, topics=5), 6)

    def test_SC5_no_role_match_is_never_shortlisted(self):
        """SC5, FILTER.md score: without R1/R2 a posting is not shortlisted, whatever its other
        points: no role + early 2 + 3 topics = 5 is not shortlisted (function), and a SIMULATED
        posting with that profile gets score 5 and "not shortlisted"."""
        f = jf()
        self.assertEqual(f.score_points(role=False, early=True, topics=3), 5)
        self.assertFalse(f.is_shortlisted(5, role=False))
        res = evaluate(posting(title="Platform Engineer, New Grad", description=stripe_html(
            ("Responsibilities", "Use Python, SQL and Spark daily."), ("Who you are", "0-1 years of experience."))))
        self.assertEqual((res["score"], res["verdict"]), (5, "not shortlisted"))

    def test_SC6_rejected_posting_has_no_score(self):
        """SC6, FILTER.md score: a posting failing R3, R4, R5 or R6 is rejected with no score.
        SIMULATED "Senior" title with an otherwise passing description."""
        res = evaluate(posting(title="Senior Machine Learning Engineer"))
        self.assertEqual((res["verdict"], res["score"]), ("rejected", None))

    def test_SC7_numbers_match_filter_md(self):
        """SC7, FILTER.md score and R3/R7 lists: weights 3/2/1, topic cap 3, threshold 5, the R7
        topic words and the R3 seniority words in job_filter.py are exactly those in FILTER.md."""
        f = jf()
        text = " ".join((HERE / "FILTER.md").read_text(encoding="utf-8").split())
        weights = re.search(r"role match \(R1/R2\) = (\d+) points; explicit early-career evidence \(R5\) = (\d+) "
                            r"points; each distinct R7 topic word = (\d+) point, at most (\d+)", text)
        self.assertEqual(f.WEIGHTS, {"role": int(weights.group(1)), "early": int(weights.group(2)),
                                     "topic": int(weights.group(3))})
        self.assertEqual(f.TOPIC_MAX, int(weights.group(4)))
        self.assertEqual(f.THRESHOLD, int(re.search(r"Shortlist threshold: (\d+) or more points", text).group(1)))
        topics = re.search(r"Count distinct topic words: (.*?)\. Why", text).group(1)
        self.assertEqual(set(f.TOPIC_WORDS), {w.strip() for w in topics.split(",")})
        senior = re.search(r"Reject titles with (.*?)\. \"Sr\"", text).group(1).replace(" or ", ", ")
        self.assertEqual(set(f.SENIORITY_TERMS), {w.strip() for w in senior.split(",")})


class Evidence(unittest.TestCase):
    def test_E1_real_plaid_every_quote_is_exact(self):
        """E1, FILTER.md evidence rules (exact quotes). REAL: all saved Plaid postings get one of the
        four verdicts, and every quote in every rule and claim is an exact substring of the title,
        the location or the description text."""
        d = importlib.import_module("descriptions")
        postings = real_plaid()
        self.assertEqual(len(postings), 144)
        for p in postings.values():
            with self.subTest(id=p["id"]):
                res = evaluate(p)
                self.assertIn(res["verdict"], VERDICTS)
                sources = (p["title"], p["location"], d.html_to_text(p["description_html"]))
                quotes = [q for r in res["rules"].values() for q in r.get("quotes", [])]
                quotes += [c["quote"] for c in res["claims"] if c["quote"] is not None]
                for q in quotes:
                    self.assertTrue(any(q in s for s in sources), q)

    def test_E2_more_than_a_year_contradicts_the_claim(self):
        """E2, FILTER.md evidence rules (contradicted). SIMULATED "5+ years": the claim "asks 0-1 years"
        is contradicted, quoting "5+ years"."""
        res = evaluate(posting(description=stripe_html(("Responsibilities", "Build models."),
                                                       ("Who you are", "5+ years of experience in ML."))))
        c = claim(res, "asks 0-1 years")
        self.assertEqual(c["label"], "contradicted")
        self.assertIn("5+ years", c["quote"])

    def test_E3_no_sponsorship_sentence_is_insufficient(self):
        """E3, FILTER.md evidence rules and wrong version 6: no sponsorship sentence gives
        "insufficient" for "no sponsorship restriction", never "supported". SIMULATED."""
        c = claim(evaluate(posting()), "no sponsorship restriction")
        self.assertEqual((c["label"], c["quote"]), ("insufficient", None))

    def test_E4_missing_or_empty_description_is_cannot_tell(self):
        """E4, FILTER.md Expected sources and wrong version 5: a missing or empty description gives
        "I cannot tell" with no score, never "not relevant", even for a "Senior" title. SIMULATED."""
        for p in (posting(description=""), posting(description="   "),
                  {k: v for k, v in posting().items() if k != "description_html"},
                  posting(title="Senior ML Engineer", description="")):
            with self.subTest(title=p["title"], description=p.get("description_html")):
                res = evaluate(p)
                self.assertEqual((res["verdict"], res["score"]), ("I cannot tell", None))

    def test_E5_unanswered_experience_is_cannot_tell(self):
        """E5, FILTER.md evidence rules ("I cannot tell" when R5 stays unanswered). SIMULATED: no
        experience statement and no early-career words anywhere."""
        res = evaluate(posting(description=stripe_html(("Responsibilities", "Build machine learning features."),
                                                       ("Who you are", "You enjoy Python."))))
        self.assertEqual(result(res, "R5"), "cannot tell")
        self.assertEqual(res["verdict"], "I cannot tell")


class WrongVersions(unittest.TestCase):
    def test_W1_false_friend_training_is_not_a_topic_word(self):
        """W1, FILTER.md wrong version 1. SIMULATED sales posting with "sales training", "model" and
        "data-driven pitch" in its Responsibilities: 0 topic points."""
        res = evaluate(posting(title="Sales Enablement Specialist", description=stripe_html(
            ("Responsibilities", "Run sales training sessions and model business cases with a data-driven pitch."),
            ("Who you are", "0-1 years of experience."))))
        self.assertEqual(res["points"]["topics"], 0)

    def test_W3_real_plaid_title_only_rule_vs_filter(self):
        """W3, FILTER.md wrong version 3. REAL saved Plaid response: the 8 postings my JS1 title-only
        rule calls relevant (including the Fraud Intelligence Analyst) all ask for more than 1 year,
        so the filter rejects each of them by R5, with a "years" quote, and shortlists none."""
        postings = real_plaid()
        js1 = [p for p in postings.values() if rule.judge(p["title"], p["location"])["verdict"] == rule.RELEVANT]
        self.assertEqual(len(js1), 8)
        self.assertIn(FRAUD_ANALYST, {p["id"] for p in js1})
        for p in js1:
            with self.subTest(id=p["id"], title=p["title"]):
                res = evaluate(p)
                self.assertEqual(res["verdict"], "rejected")
                self.assertEqual(result(res, "R5"), "fail")
                self.assertTrue(any("year" in q for q in res["rules"]["R5"]["quotes"]))


class Decisions(unittest.TestCase):
    def test_D1_topic_words_in_boilerplate_earn_nothing(self):
        """D1, FILTER.md Revision (decisions D1-D7). SIMULATED Databricks-style posting: machine
        learning, Python, SQL and Spark appear only in the intro and "About Databricks"; 0 topic points."""
        res = evaluate(posting(description=databricks_html(
            "Databricks is the data and AI company: machine learning, Python, SQL and Spark at scale.",
            [("The impact you will have", "Build features."), ("What we look for", "0-1 years of experience.")],
            "We created Spark and lead in machine learning and statistics.")))
        self.assertEqual(res["points"]["topics"], 0)

    def test_D2_remote_with_no_country_is_cannot_tell(self):
        """D2, FILTER.md Revision (decisions D1-D7): "Remote" with no country gives "I cannot tell".
        SIMULATED."""
        res = evaluate(posting(location="Remote"))
        self.assertEqual(result(res, "R4"), "cannot tell")
        self.assertEqual(res["verdict"], "I cannot tell")

    def test_D3_new_grad_counts_only_when_it_describes_the_job(self):
        """D3, FILTER.md Revision (decisions D1-D7). SIMULATED: "new grad" only in company boilerplate
        or about an unrelated program does NOT count (no experience stated, so "I cannot tell");
        "New Grad" in the title or in a "counts" section does (R5 passes, 2 points)."""
        not_job = [
            stripe_html(("About Stripe", "We hire new grads every year across many teams."),
                        ("Responsibilities", "Build machine learning features.")),
            stripe_html(("Responsibilities", "Build machine learning features."),
                        ("Our programs", "Ask about our new grad rotation program for other teams.")),
        ]
        for description in not_job:
            with self.subTest(case="does not count"):
                res = evaluate(posting(description=description))
                self.assertEqual(result(res, "R5"), "cannot tell")
                self.assertEqual(res["verdict"], "I cannot tell")
        in_job = [
            posting(title="Machine Learning Engineer, New Grad",
                    description=stripe_html(("Responsibilities", "Build machine learning features."))),
            posting(description=stripe_html(("Responsibilities", "Build machine learning features."),
                                            ("Who you are", "You are a new grad in computer science."))),
        ]
        for p in in_job:
            with self.subTest(case="counts", title=p["title"]):
                res = evaluate(p)
                self.assertEqual(result(res, "R5"), "pass")
                self.assertEqual(res["points"]["early"], 2)

    def test_D4_one_plus_years_is_rejected(self):
        """D4, FILTER.md Revision (decisions D1-D7): "1+ years" is rejected (open upper end). SIMULATED."""
        res = evaluate(posting(description=stripe_html(("Responsibilities", "Build models."),
                                                       ("Who you are", "1+ years of experience."))))
        self.assertEqual(result(res, "R5"), "fail")
        self.assertEqual(res["verdict"], "rejected")

    def test_D5_only_requirement_wording_rejects(self):
        """D5, FILTER.md Revision (decisions D1-D7). SIMULATED: "citizenship status" in equal-opportunity
        text and the export-control paragraph do NOT reject; "must be a U.S. citizen" and "will not
        sponsor" do."""
        base = (("Responsibilities", "Build machine learning features in Python."),
                ("Who you are", "0-1 years of experience."))
        for heading, text in (("Equal opportunity", EEO), ("Compliance", EXPORT_CONTROL)):
            with self.subTest(keeps=heading):
                res = evaluate(posting(description=stripe_html(*base, (heading, text))))
                self.assertNotEqual(result(res, "R6"), "fail")
                self.assertEqual(res["verdict"], "shortlisted")
        for text in ("You must be a U.S. citizen.", "We will not sponsor work visas."):
            with self.subTest(rejects=text):
                res = evaluate(posting(description=stripe_html(*base, ("Requirements", text))))
                self.assertEqual(result(res, "R6"), "fail")
                self.assertEqual(res["verdict"], "rejected")

    def test_D6_non_english_description_is_cannot_tell(self):
        """D6, FILTER.md Revision (decisions D1-D7): a description not in English gives "I cannot tell".
        SIMULATED Japanese description (made up, in the shape of a Databricks Tokyo posting)."""
        res = evaluate(posting(location="Tokyo, Japan", description=stripe_html(
            ("職務内容", "お客様と協力して、データとAIのプラットフォームを構築します。"),
            ("応募資格", "関連する経験をお持ちの方。"))))
        self.assertEqual(res["verdict"], "I cannot tell")


if __name__ == "__main__":
    unittest.main()
