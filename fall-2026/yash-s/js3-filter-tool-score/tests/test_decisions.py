"""FILTER.md Rules 1, 5, 6 and the section 4 decision order. CONSTRUCTED postings."""
import unittest

from helpers import GOOD_BODY, J, evaluate, rules

NO_SKILL_BODY = "<p>You will build data pipelines and machine learning models.</p>"


class Roles(unittest.TestCase):
    def test_excluded_title_is_rejected_before_scoring_but_score_is_kept(self):
        r = evaluate(title="Data Center Electrical Engineer")
        self.assertEqual(r["role"], "excluded")
        self.assertEqual((r["decision"], r["decision_step"]), ("rejected", 1))
        self.assertGreater(r["score"], 0)

    def test_forward_deployed_ai_engineer_is_special_review_not_target(self):
        r = evaluate(title="AI Engineer – Forward Deployed Engineering (AI FDE)")
        self.assertEqual(r["role"], "special_review")
        self.assertEqual(r["points"]["role"], 20)
        self.assertEqual(r["decision"], "review")

    def test_solutions_engineer_is_special_review_with_exactly_20_points(self):
        r = evaluate(title="Solutions Engineer")
        self.assertEqual((r["role"], r["points"]["role"]), ("special_review", 20))
        self.assertNotEqual(r["decision"], "confirmed")

    def test_target_titles(self):
        for t in ("Applied AI Engineer, Startups", "Machine Learning Engineer, Core", "Data Engineer, Product",
                  "ML/Research Engineer, Safeguards", "Research Engineer, Machine Learning (RL)"):
            with self.subTest(t=t):
                self.assertEqual(J.title_role(t, rules())[0], "target")

    def test_related_role_needs_a_topic_in_the_job_text(self):
        self.assertEqual(evaluate(title="Software Engineer, Payments", body=NO_SKILL_BODY)["role"], "related")
        r = evaluate(title="Software Engineer, Payments", body="<p>Build payment screens in Python.</p>")
        self.assertEqual(r["role"], "none")
        self.assertIn("no matching role", r["hard_exclusions"])

    def test_policy_is_not_an_exclusion_word(self):
        self.assertEqual(J.title_role("Applied AI Architect, International Policy", rules())[0], "special_review")
        self.assertEqual(evaluate(title="Policy Development, Technical AI Governance")["role"], "none")


class SeniorityAndPrograms(unittest.TestCase):
    def test_seniority_overrides_a_high_score(self):
        r = evaluate(title="Senior Data Engineer")
        self.assertEqual(r["score"], 100)
        self.assertEqual((r["decision"], r["decision_step"]), ("rejected", 1))

    def test_senior_engineers_in_the_description_do_not_make_the_role_senior(self):
        body = "<p>You will collaborate with senior engineers.</p>" + GOOD_BODY
        self.assertEqual(evaluate(body=body)["decision"], "confirmed")

    def test_as_a_senior_field_engineer_triggers_seniority(self):
        body = "<p>As a Senior Field Engineer, you will work side by side with the team.</p>" + GOOD_BODY
        r = evaluate(body=body)
        self.assertEqual(r["decision"], "rejected")
        self.assertTrue(any(x.startswith("seniority statement") for x in r["hard_exclusions"]))

    def test_leader_triggers_seniority(self):
        r = evaluate(title="Data Engineering Leader")
        self.assertIn("seniority word 'Leader' in title", r["hard_exclusions"])

    def test_emerging_talent_2027_is_a_special_program(self):
        r = evaluate(title="Software Engineer, Applied Emerging Talent (2027)")
        self.assertEqual(r["decision"], "rejected")
        self.assertTrue(any(x.startswith("special program") for x in r["hard_exclusions"]))

    def test_fellows_program_is_a_special_program(self):
        self.assertEqual(J.special_program("Anthropic Fellows Program, ML Systems", rules()), "Fellows")


class DecisionOrder(unittest.TestCase):
    def test_full_match_is_confirmed(self):
        r = evaluate()
        self.assertEqual((r["decision"], r["score"]), ("confirmed", 100))

    def test_score_70_without_a_skill_goes_to_review_never_confirmed(self):
        r = evaluate(body=NO_SKILL_BODY)  # title 35 + topics 20 + US 15
        self.assertEqual(r["score"], 70)
        self.assertEqual(r["decision"], "review")
        self.assertIn("matches no résumé skill", r["review_reasons"])

    def test_no_skill_still_review_even_with_compatible_experience(self):
        r = evaluate(body=NO_SKILL_BODY + "<p>No prior experience required.</p>")
        self.assertEqual((r["score"], r["decision"]), (80, "review"))
        self.assertEqual(r["review_reasons"], ["matches no résumé skill"])

    def test_below_65_is_rejected_even_when_information_is_unknown(self):
        r = evaluate(title="Software Engineer", location="Remote", body=NO_SKILL_BODY)
        self.assertLess(r["score"], 65)
        self.assertEqual((r["decision"], r["decision_step"]), ("rejected", 2))

    def test_within_cutoff_minimum_goes_to_review(self):
        body = NO_SKILL_BODY + "<p>Python and SQL.</p><p>2+ years of experience.</p>"
        r = evaluate(body=body)
        self.assertEqual(r["decision"], "review")
        self.assertTrue(any(x.startswith("minimum experience 2") for x in r["review_reasons"]))

    def test_outside_us_only_is_rejected(self):
        r = evaluate(location="London, UK; Dublin, IE")
        self.assertIn("every location part is outside the US", r["hard_exclusions"])
        self.assertEqual(evaluate(location="London, UK · San Francisco")["location_status"], "us")


class TheTwoLists(unittest.TestCase):
    @staticmethod
    def rec(board, pid, score, decision):
        return {"board": board, "id": pid, "score": score, "decision": decision}

    def test_review_candidates_order_is_score_then_board_then_id(self):
        results = [self.rec("OpenAI", "b", 80, "review"), self.rec("Anthropic", "z", 80, "review"),
                   self.rec("OpenAI", "a", 80, "review"), self.rec("Databricks", "1", 90, "review"),
                   self.rec("Anthropic", "q", 70, "review")]
        got = [(r["board"], r["id"]) for r in J.review_candidates(results, rules())]
        self.assertEqual(got, [("Databricks", "1"), ("Anthropic", "z"), ("OpenAI", "a"), ("OpenAI", "b"), ("Anthropic", "q")])
        self.assertEqual(got, [(r["board"], r["id"]) for r in J.review_candidates(list(reversed(results)), rules())])

    def test_review_candidates_exist_even_with_confirmed_postings_and_never_overlap(self):
        results = [self.rec("Databricks", str(i), 100, "confirmed") for i in range(3)]
        results += [self.rec("OpenAI", str(i), 60 + i, "review") for i in range(15)]
        cands, conf = J.review_candidates(results, rules()), J.confirmed_shortlist(results)
        self.assertEqual(len(cands), 10)
        self.assertEqual(len(conf), 3)
        self.assertFalse({(r["board"], r["id"]) for r in cands} & {(r["board"], r["id"]) for r in conf})


if __name__ == "__main__":
    unittest.main()
