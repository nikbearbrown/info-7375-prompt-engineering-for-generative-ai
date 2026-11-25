"""The claim checker (FILTER.md section 5) and the audit report helpers. CONSTRUCTED postings."""
import unittest

from helpers import J, posting, rules
import audit_report as A
import shortlist as S

BODY = ("<h2>About the team</h2><p>The team ships agentic systems.</p>"
        "<h2>Minimum qualifications</h2><ul><li>Python and SQL.</li></ul>"
        "<h2>Preferred qualifications</h2><ul><li>AWS experience.</li><li>5+ years of experience.</li></ul>")


def claims(body, title="Software Engineer, Agents"):
    p = posting(title=title, body=body)
    r = J.evaluate(p, rules())
    return r, {(c["claim_kind"], c["claim"]): c for c in S.claims_for(p, r, rules())}


def label(cl, kind, contains=""):
    hits = [c for (k, text), c in cl.items() if k == kind and contains in text]
    assert len(hits) == 1, (kind, contains, list(cl))
    return hits[0]["checker_label"]


class Headings(unittest.TestCase):
    def test_kinds(self):
        for h, kind in [("Minimum qualifications", "requirement"), ("You might thrive in this role if you:", "requirement"),
                        ("Preferred qualifications", "preferred"), ("Strong candidates may also have:", "preferred"),
                        ("Candidates need not have:", "not required"), ("About the Team", "company or team"),
                        ("In this role, you will:", "responsibility"), ("Representative projects", "responsibility"),
                        ("What You’ll Do", "responsibility"), ("", "other"), ("Visualization & communication", "other")]:
            with self.subTest(h=h):
                self.assertEqual(S.heading_kind(h), kind)


class Claims(unittest.TestCase):
    def test_a_mention_is_supported_but_the_work_claim_is_not_when_it_is_only_team_text(self):
        r, cl = claims(BODY)
        self.assertEqual(label(cl, "mention", "AI applications"), "supported")
        self.assertEqual(label(cl, "work", "AI applications"), "insufficient")

    def test_required_skill_needs_a_requirement_heading(self):
        _, cl = claims(BODY)
        self.assertEqual(label(cl, "skill-required", "Python"), "supported")
        self.assertEqual(label(cl, "skill-required", "AWS"), "insufficient")  # only under Preferred
        self.assertEqual(label(cl, "skill-named", "AWS"), "supported")

    def test_unknown_experience_is_insufficient_and_the_agent_abstains(self):
        r, cl = claims(BODY)
        self.assertEqual(r["experience_status"], "unknown")
        exp = next(c for (k, _), c in cl.items() if k == "experience")
        self.assertEqual(exp["checker_label"], "insufficient")
        self.assertIn("I cannot tell", exp["caution"])
        self.assertIn("Preferred, not required", exp["source_excerpt"])

    def test_a_mandatory_minimum_contradicts_both_experience_claims(self):
        body = "<p>Build data pipelines in Python.</p><h2>Minimum qualifications</h2><ul><li>3+ years of experience.</li></ul>"
        _, cl = claims(body, title="Data Engineer")
        self.assertEqual(label(cl, "experience"), "contradicted")
        self.assertEqual(label(cl, "early-career"), "contradicted")

    def test_an_explicit_no_experience_statement_supports_both(self):
        _, cl = claims("<p>Build data pipelines in Python.</p><p>No prior experience required.</p>", title="Data Engineer")
        self.assertEqual(label(cl, "experience"), "supported")
        self.assertEqual(label(cl, "early-career"), "supported")

    def test_working_with_another_team_is_flagged(self):
        body = "<h2>About the role</h2><p>You'll partner closely with Finance and the central data engineering team.</p><p>Python.</p>"
        _, cl = claims(body, title="Data Engineer")
        work = next(c for (k, _), c in cl.items() if k == "work")
        self.assertEqual(work["checker_label"], "supported")
        self.assertIn("another team", work["caution"])


class AuditReport(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(A.category({"MY_VERDICT": "correct reject", "filter_decision": "rejected"}), "correctly rejected")
        self.assertEqual(A.category({"MY_VERDICT": "should have been kept for review", "filter_decision": "rejected"}),
                         "rejected, should have been kept for review")
        self.assertEqual(A.category({"MY_VERDICT": "should have been rejected", "filter_decision": "review"}),
                         "in review, should have been rejected")

    def test_removing_a_false_friend_can_change_the_decision(self):
        p = posting(title="Security Engineer, Agent Security", body="<p>Secure our agentic systems.</p><p>Python and AWS.</p>")
        r = J.evaluate(p, rules())
        self.assertEqual((r["score"], r["decision"]), (65, "review"))
        fx = A.false_friend_effect({"FALSE_FRIEND_WORD": "agentic systems"}, r, p, rules())
        self.assertEqual((fx["score_after"], fx["decision_after"], fx["effect"]), (35, "rejected", "changes the decision"))
        self.assertEqual(A.false_friend_effect({"FALSE_FRIEND_WORD": "AI"}, r, p, rules())["effect"], "nothing to remove")


if __name__ == "__main__":
    unittest.main()
