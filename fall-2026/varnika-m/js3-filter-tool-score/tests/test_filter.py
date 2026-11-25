"""FILTER.md v1: the rules, the outcomes, grouping, ranking, the M1 variant, and wrong versions WF1-WF6.

Every posting here is constructed, in the shape JS1's rule reads. None is a real posting.
"""

import html
import unittest

from js3.filter import evaluate, must_have_markup, run_filter
from js3.load import load_persona

RESUME = load_persona()
GOOD_BODY = "<ul><li>2+ years building backend services</li><li>Experience with Python and AWS</li></ul>"


def posting(key="greenhouse/x/1", title="Software Engineer", location="Boston, MA", body=GOOD_BODY,
            company="Example"):
    return {"key": key, "id": key.rsplit("/", 1)[1], "title": title, "location": {"name": location},
            "content": html.escape(body), "absolute_url": "https://example.invalid/" + key, "company_name": company}


def r(result, rule):
    return next(c for c in result["checks"] if c["rule"] == rule)


class Rules(unittest.TestCase):
    def test_a_good_posting_is_kept(self):
        result = evaluate(posting(), RESUME)
        self.assertEqual((result["score"], result["outcome"]), (5, "keep"))

    def test_one_rule_short_is_a_close_call(self):
        result = evaluate(posting(title="Senior Software Engineer"), RESUME)
        self.assertEqual((result["score"], result["outcome"], result["failed"]), (4, "close_call", ["R2"]))

    def test_wf1_engineer_alone_is_not_a_role_word(self):
        for title in ("Solutions Engineer", "Sales Engineer", "Customer Success Engineer"):
            self.assertFalse(r(evaluate(posting(title=title), RESUME), "R1")["passed"], title)

    def test_wf2_javascript_is_not_java(self):
        result = evaluate(posting(body="<li>JavaScript and SQL</li>"), RESUME)
        self.assertEqual(result["skills"], ["SQL"])
        self.assertFalse(r(result, "R5")["passed"])

    def test_wf6_a_missing_field_is_cannot_tell_not_a_verdict(self):
        for missing in ({"location": ""}, {"title": ""}, {"body": ""}):
            result = evaluate(posting(**missing), RESUME)
            self.assertEqual(result["outcome"], "cannot_tell", missing)
            self.assertIsNone(result["score"])


class Grouping(unittest.TestCase):
    def test_wf5_the_same_job_in_three_cities_is_one_shortlist_entry(self):
        same = [posting(key="lever/p/%d" % i, location=city) for i, city in
                enumerate(("Boston, MA", "New York, NY", "Denver, CO"), 1)]
        _, shortlist = run_filter(same, RESUME)
        self.assertEqual(len(shortlist), 1)
        self.assertEqual(len(shortlist[0]["ids"]), 3)

    def test_same_title_different_description_stays_two_jobs(self):
        a = posting(key="lever/p/1")
        b = posting(key="lever/p/2", body=GOOD_BODY + "<li>Active Top Secret clearance</li>")
        self.assertEqual(len(run_filter([a, b], RESUME)[1]), 2)

    def test_wf3_ranking_counts_different_skills_not_repeats(self):
        repeats = posting(key="g/x/1", title="Software Engineer A",
                          body="<li>Python " * 10 + "and SQL</li><li>2+ years</li>")
        varied = posting(key="g/x/2", title="Software Engineer B",
                         body="<li>Python, Java, Kafka and AWS</li><li>2+ years</li>")
        _, shortlist = run_filter([repeats, varied], RESUME)
        self.assertEqual([s["posting"]["key"] for s in shortlist], ["g/x/2", "g/x/1"])


class MustHavesOnly(unittest.TestCase):
    BODY = ("<h3>Requirements</h3><ul><li>2+ years with Python and AWS</li></ul>"
            "<h3>Preferred qualifications</h3><ul><li>5+ years in distributed systems</li></ul>")

    def test_v1_counts_preferred_years(self):
        self.assertFalse(r(evaluate(posting(body=self.BODY), RESUME), "R4")["passed"])

    def test_m1_ignores_years_under_a_preferred_heading(self):
        result = evaluate(posting(body=self.BODY), RESUME, must_haves_only=True)
        self.assertTrue(r(result, "R4")["passed"])
        self.assertEqual(result["outcome"], "keep")

    def test_m1_ignores_a_single_nice_to_have_line(self):
        body = "<ul><li>2+ years with Python and AWS</li><li>6+ years of Go is a plus</li></ul>"
        self.assertNotIn("6+", html.unescape(must_have_markup(html.escape(body))))

    def test_m1_still_counts_must_have_years(self):
        body = "<h3>Requirements</h3><ul><li>5+ years with Python and AWS</li></ul>"
        self.assertFalse(r(evaluate(posting(body=body), RESUME, must_haves_only=True), "R4")["passed"])


class Version1_1(unittest.TestCase):
    """FILTER.md v1.1, A and B, with v1 kept reproducible."""

    def test_a_washington_dc_with_dots_is_a_us_location(self):
        p = posting(location="Washington, D.C.")
        self.assertTrue(r(evaluate(p, RESUME), "R3")["passed"])
        self.assertFalse(r(evaluate(p, RESUME, version="v1"), "R3")["passed"])  # the v1 bug the audit found

    def test_a_dc_alone_still_needs_the_comma(self):
        self.assertFalse(r(evaluate(posting(location="D.C. United fan club, London"), RESUME), "R3")["passed"])

    def test_b_must_be_graduating_later_than_his_degree_fails(self):
        for when in ("in December 2026 or Spring 2027", "in 2028", "in Dec 2026"):
            p = posting(body=GOOD_BODY + "<li>Must be graduating %s.</li>" % when)
            result = evaluate(p, RESUME)
            self.assertFalse(r(result, "R2")["passed"], when)
            self.assertEqual(result["outcome"], "close_call")
            self.assertEqual(evaluate(p, RESUME, version="v1")["outcome"], "keep")

    def test_b_a_degree_already_finished_is_fine(self):
        p = posting(body=GOOD_BODY + "<li>Recently completed a Bachelor's or Master's degree.</li>")
        self.assertTrue(r(evaluate(p, RESUME), "R2")["passed"])


if __name__ == "__main__":
    unittest.main()
