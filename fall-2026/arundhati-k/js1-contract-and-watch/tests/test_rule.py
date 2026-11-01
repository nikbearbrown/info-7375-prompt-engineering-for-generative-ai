import unittest

from jsagent import rule
from jsagent.resume import skill_fields
from tests import fixtures as F


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.skills = skill_fields(F.persona())

    def verdict(self, job):
        return rule.judge(job, self.skills)

    def test_expected_verdicts_on_constructed_postings(self):
        for job in F.ALL:
            with self.subTest(id=job["id"], title=job["title"]):
                self.assertEqual(self.verdict(job)["verdict"], F.EXPECTED[str(job["id"])])

    def test_relevant_cites_resume_and_posting_fields(self):
        r = self.verdict(F.RELEVANT)
        cited = {m["skill"]: m["resume_field"] for m in r["conditions"]["skills"]["matches"]}
        self.assertEqual(cited, {"Python": "skills.languages[0]", "Java": "skills.languages[2]", "AWS": "skills.database_cloud[3]"})
        self.assertIn("skills.languages[2]='Java'", r["justification"])

    def test_one_skill_is_not_enough(self):
        c = self.verdict(F.ONE_SKILL)["conditions"]
        self.assertTrue(c["role"]["passed"] and c["level"]["passed"] and c["location"]["passed"])
        self.assertEqual([m["skill"] for m in c["skills"]["matches"]], ["Java"])  # "Go build" is the verb, not Go

    def test_internal_is_not_intern(self):
        self.assertFalse(self.verdict(F.INTERNAL)["conditions"]["level"]["passed"])

    def test_early_career_is_not_on_the_contract_list(self):
        self.assertFalse(self.verdict(F.EARLY_CAREER)["conditions"]["level"]["passed"])

    def test_location_markers(self):
        for loc, us in [("US-Remote", True), ("NYC, SF", True), ("Seattle, WA", True), ("US / Canada", True),
                        ("Dublin", False), ("Remote", False), ("N/A", False), ("AMER", False), ("Toronto, Canada", False)]:
            with self.subTest(loc=loc):
                self.assertEqual(self.verdict(F.job(1, "Software Engineer, Intern", loc, "Java and SQL"))["conditions"]["location"]["passed"], us)

    def test_aliases(self):
        r = self.verdict(F.job(1, "Backend Engineer, Intern", "Chicago", "We use Golang and Postgres on k8s."))
        self.assertEqual([m["skill"] for m in r["conditions"]["skills"]["matches"]], ["Go", "PostgreSQL", "Kubernetes"])
        self.assertEqual(r["verdict"], "RELEVANT")

    def test_javascript_does_not_count_as_java(self):
        r = self.verdict(F.job(1, "Software Engineer, Intern", "Chicago", "JavaScript only."))
        self.assertEqual([m["skill"] for m in r["conditions"]["skills"]["matches"]], ["JavaScript"])

    def test_never_cites_a_skill_missing_from_resume(self):
        resume = F.persona()
        resume["skills"]["devops_cicd"] = ["Docker"]  # drop Jenkins/Kubernetes
        r = rule.judge(F.job(1, "Software Engineer, Intern", "Chicago", "Jenkins and Kubernetes."), skill_fields(resume))
        self.assertEqual(r["conditions"]["skills"]["matches"], [])

    def test_deterministic(self):
        self.assertEqual(self.verdict(F.RELEVANT), self.verdict(F.RELEVANT))


if __name__ == "__main__":
    unittest.main()
