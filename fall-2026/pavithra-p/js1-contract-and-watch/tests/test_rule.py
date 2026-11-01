"""CONTRACT.md The rule (four checks) and the two wrong versions.

Every posting here is a small CONSTRUCTED fixture, not a real Pinterest posting.
"""
import random
import unittest

from agent import config, resume, rule, wrong_versions

PERSONA = resume.load(config.RESUME)


def job(job_id, title, location="Remote, US", content="<p>Python and Kubernetes.</p>"):
    return {"id": job_id, "title": title, "location": {"name": location}, "content": content}


def pairing_errors(results, jobs):
    """Shuffle the results; each one must still match the rule applied to its own job."""
    by_id = {j["id"]: j for j in jobs}
    shuffled = results[:]
    random.Random(7).shuffle(shuffled)
    return [r.job_id for r in shuffled if r.verdict != rule.judge(by_id[r.job_id], PERSONA).verdict]


def reason_errors(verdict, posting):
    """The reason must name a posting field, a résumé field and every skill the rule matched."""
    errors = []
    if not any(f in verdict.reason for f in ("title", "description", "location")):
        errors.append("no posting field")
    if "skills." not in verdict.reason and "experience" not in verdict.reason:
        errors.append("no résumé field")
    errors += [f"skill {s} not named" for s in rule.judge(posting, PERSONA).matched_skills if s not in verdict.reason]
    return errors


class RuleTests(unittest.TestCase):
    def test_role_needs_engineer_and_role_word(self):
        self.assertTrue(rule.judge(job(1, "Software Engineer II"), PERSONA).checks["role"])
        self.assertTrue(rule.judge(job(2, "Machine Learning Engineer, Visual AI"), PERSONA).checks["role"])
        self.assertFalse(rule.judge(job(3, "Customer Success Engineer"), PERSONA).checks["role"])
        self.assertFalse(rule.judge(job(4, "Engineering Manager, Software"), PERSONA).checks["role"])

    def test_skills_need_two_whole_word_matches(self):
        one = rule.judge(job(1, "Software Engineer", content="<p>JavaScript and PostgreSQL</p>"), PERSONA)
        self.assertEqual(one.matched_skills, ["PostgreSQL"], "Java must not match JavaScript, SQL not PostgreSQL")
        self.assertFalse(one.checks["skills"])
        two = rule.judge(job(2, "Software Engineer", content="<p>Python &amp; Kubernetes</p>"), PERSONA)
        self.assertEqual(two.matched_skills, ["Python", "Kubernetes"])
        self.assertTrue(two.checks["skills"])

    def test_experience_rejects_senior_titles_and_interns(self):
        for title in ("Senior Software Engineer", "Sr. Software Engineer", "Software Engineer Intern 2027",
                      "Staff Backend Engineer", "Software Engineer, Tech Lead"):
            self.assertFalse(rule.judge(job(1, title), PERSONA).checks["experience"], title)
        for title in ("Software Engineer II", "Internal Tools Software Engineer"):
            self.assertTrue(rule.judge(job(1, title), PERSONA).checks["experience"], title)

    def test_experience_rejects_three_plus_years(self):
        for text in ("3+ years of experience", "5 years building APIs", "3-5 years in backend"):
            self.assertFalse(rule.judge(job(1, "Software Engineer", content=f"<p>{text}</p>"), PERSONA)
                             .checks["experience"], text)
        self.assertTrue(rule.judge(job(1, "Software Engineer", content="<p>2+ years</p>"), PERSONA)
                        .checks["experience"])

    def test_experience_reads_decimal_years_whole(self):
        """Experiment 2 found the record reading "1.5+ years" as 5 (Affirm 8003020003)."""
        self.assertTrue(rule.judge(job(1, "Software Engineer", content="<p>1.5+ years of experience</p>"), PERSONA)
                        .checks["experience"])
        self.assertFalse(rule.judge(job(1, "Software Engineer", content="<p>3.5 years of experience</p>"), PERSONA)
                         .checks["experience"])

    def test_location_accepts_us_usa_united_states(self):
        for where in ("San Francisco, CA, US", "New York, NY, USA; Hybrid", "Remote, United States"):
            self.assertTrue(rule.judge(job(1, "Software Engineer", where), PERSONA).checks["location"], where)

    def test_location_rejects_toronto_ca(self):
        for where in ("Toronto, ON, CA", "Buenos Aires, AR", "London, UK"):
            self.assertFalse(rule.judge(job(1, "Software Engineer", where), PERSONA).checks["location"], where)

    def test_all_four_needed_for_relevant(self):
        self.assertEqual(rule.judge(job(1, "Software Engineer II"), PERSONA).verdict, "Relevant")
        self.assertEqual(rule.judge(job(2, "Software Engineer II", "Toronto, ON, CA"), PERSONA).verdict, "Not Relevant")

    def test_verdict_labelled_as_record(self):
        self.assertEqual(rule.judge(job(1, "Software Engineer"), PERSONA).kind, "record (written rule)")


class WrongVersionTests(unittest.TestCase):
    JOBS = [job(1, "Zeta Software Engineer"), job(2, "Alpha Sales Manager", content="<p>Sales</p>"),
            job(3, "Backend Engineer", "Toronto, ON, CA")]

    def test_results_stay_paired_with_their_job_id(self):
        self.assertEqual(pairing_errors(rule.judge_all(self.JOBS, PERSONA), self.JOBS), [])

    def test_pairing_check_catches_wrong_version_1(self):
        self.assertNotEqual(pairing_errors(wrong_versions.judge_all_wrong_pairing(self.JOBS, PERSONA), self.JOBS), [])

    def test_reason_names_posting_field_resume_field_and_skills(self):
        for posting in self.JOBS:
            self.assertEqual(reason_errors(rule.judge(posting, PERSONA), posting), [], posting["title"])

    def test_reason_check_catches_wrong_version_2(self):
        posting = self.JOBS[0]
        self.assertNotEqual(reason_errors(wrong_versions.judge_without_reason(posting, PERSONA), posting), [])


if __name__ == "__main__":
    unittest.main()
