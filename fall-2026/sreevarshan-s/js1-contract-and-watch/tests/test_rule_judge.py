import json
import unittest
from pathlib import Path

from js1.rule_judge import judge, judge_all, sentences

ROOT = Path(__file__).resolve().parent.parent
RESUME = json.loads((ROOT / "persona" / "priya-nair.resume.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "persona" / "priya-nair.profile.json").read_text(encoding="utf-8"))
# CONSTRUCTED postings, not real ones.
POSTINGS = json.loads((Path(__file__).parent / "fixtures" / "constructed_postings.json").read_text(encoding="utf-8"))["jobs"]
BY_ID = {p["id"]: p for p in POSTINGS}


def record(posting_id):
    return judge(BY_ID[posting_id], RESUME, PROFILE)


def failed(rec):
    return [c["check"] for c in rec["failed_checks"]]


def skills(rec):
    return [m["skill"] for m in rec["matched_skills"]]


class WrongVersionTests(unittest.TestCase):
    def test_senior_data_engineer_with_matching_skills_is_not_relevant(self):
        rec = record(8000001)
        self.assertGreaterEqual(len(rec["matched_skills"]), 2)
        self.assertEqual(rec["verdict"], "not relevant")
        self.assertEqual(failed(rec), [2])

    def test_no_sponsorship_text_gives_unknown(self):
        rec = record(8000002)
        self.assertEqual(rec["sponsorship"]["value"], "unknown")
        self.assertEqual(rec["sponsorship"]["evidence"], [])
        self.assertEqual(rec["verdict"], "relevant")


class RuleJudgeTests(unittest.TestCase):
    def test_every_result_posting_id_matches_its_input(self):
        results = judge_all(POSTINGS, RESUME, PROFILE)
        self.assertEqual(len(results), len(POSTINGS))
        for posting, rec in zip(POSTINGS, results):
            self.assertEqual(rec["posting_id"], posting["id"])
            self.assertEqual(rec["title"], posting["title"])
            self.assertEqual(rec["url"], posting["absolute_url"])
            self.assertEqual(rec["label"], "record")
            self.assertEqual(rec["company"], "Databricks")

    def test_all_seven_checks_always_run(self):
        for posting in POSTINGS:
            self.assertEqual([c["check"] for c in judge(posting, RESUME, PROFILE)["checks"]], [1, 2, 3, 4, 5, 6, 7])

    def test_several_failures_are_all_listed(self):
        rec = record(8000011)  # Sr. title and a 5-year minimum
        self.assertEqual(failed(rec), [2, 4])

    def test_ray_and_kubeflow_never_count(self):
        rec = record(8000003)
        self.assertNotIn("Ray", skills(rec))
        self.assertNotIn("Kubeflow", skills(rec))
        self.assertEqual(rec["familiar_not_counted"], ["Ray", "Kubeflow"])
        self.assertEqual(skills(rec), ["Python"])
        self.assertEqual(failed(rec), [3])

    def test_postgresql_does_not_match_sql(self):
        rec = record(8000004)
        self.assertNotIn("SQL", skills(rec))
        self.assertEqual(skills(rec), ["Python"])

    def test_leading_does_not_trigger_seniority(self):
        rec = record(8000005)
        self.assertNotIn(2, failed(rec))
        self.assertEqual(rec["verdict"], "relevant")

    def test_range_uses_lower_bound_and_preferred_years_are_ignored(self):
        rec = record(8000006)  # "2–4 years" required, "5+ years ... preferred"
        self.assertEqual(rec["min_years_required"], 2)
        self.assertEqual(rec["verdict"], "relevant")

    def test_preferred_only_clearance_does_not_reject(self):
        rec = record(8000007)
        self.assertNotIn(5, failed(rec))
        self.assertEqual(rec["verdict"], "relevant")

    def test_required_clearance_rejects(self):
        self.assertEqual(failed(record(8000008)), [5])

    def test_contract_denial_phrase_is_not_relevant(self):
        rec = record(8000012)  # "No visa sponsorship" (D6-B§6)
        self.assertEqual(rec["sponsorship"]["value"], "denied")
        self.assertEqual(failed(rec), [6])

    def test_added_denial_phrase_is_not_relevant(self):
        rec = record(8000009)  # "unable to sponsor" (approved list)
        self.assertEqual(rec["sponsorship"]["value"], "denied")
        self.assertEqual(failed(rec), [6])

    def test_will_not_provide_sponsorship_is_denied(self):
        rec = record(8000017)
        self.assertEqual(rec["sponsorship"]["value"], "denied")
        self.assertEqual(rec["sponsorship"]["evidence"][0]["phrase"], "will not provide sponsorship")
        self.assertEqual(failed(rec), [6])

    def test_offered_phrase_and_skill_cites_every_field(self):
        rec = record(8000010)
        self.assertEqual(rec["sponsorship"]["value"], "offered")
        mlflow = next(m for m in rec["matched_skills"] if m["skill"] == "MLflow")
        self.assertEqual(mlflow["resume_fields"],
                         ["skills.backend_automation[1]", "experience[0].bullets[1]", "projects[0].bullets[0]"])
        self.assertEqual(skills(rec).count("MLflow"), 1)
        self.assertEqual(rec["work_arrangement"], "hybrid")

    def test_aws_alias_and_slash_title(self):
        self.assertIn("AWS", skills(record(8000002)))
        self.assertNotIn(1, failed(record(8000007)))  # "ML/AI Engineer"

    def test_location_conflict_and_not_specified(self):
        rec = record(8000011)  # location "Remote", description "On-site"
        self.assertEqual(rec["work_arrangement"], "conflict")
        self.assertEqual(rec["work_arrangement_conflict"], {"location.name": ["remote"], "content": ["onsite"]})
        self.assertEqual(record(8000002)["work_arrangement"], "not specified")
        self.assertEqual(record(8000006)["work_arrangement"], "remote")

    def test_company_name_only_databricks_does_not_count(self):
        rec = record(8000013)
        self.assertNotIn("Databricks", skills(rec))
        self.assertEqual(skills(rec), ["Python"])
        self.assertEqual(failed(rec), [3])

    def test_experience_with_databricks_counts(self):
        rec = record(8000014)
        databricks = next(m for m in rec["matched_skills"] if m["skill"] == "Databricks")
        self.assertEqual(databricks["posting_evidence"][0]["phrase"], "experience with Databricks")
        self.assertEqual(skills(rec), ["Python", "Databricks"])
        self.assertEqual(rec["verdict"], "relevant")

    def test_years_bullet_under_preferred_heading_does_not_reject(self):
        rec = record(8000015)  # "5+ years" bullet under "Preferred Qualifications"
        self.assertEqual(rec["min_years_required"], 2)
        five = next(h for h in rec["checks"][3]["evidence"] if h["minimum"] == 5)
        self.assertTrue(five["under_preferred_heading"])
        self.assertTrue(five["optional"])
        self.assertEqual(rec["verdict"], "relevant")

    def test_preferred_heading_ends_at_next_heading(self):
        rec = record(8000016)  # bold "Nice to have": 4+ (optional); bold "What you need": 6+ (mandatory)
        self.assertEqual(rec["min_years_required"], 6)
        self.assertEqual(failed(rec), [4])

    def test_list_items_are_their_own_sentences(self):
        self.assertEqual(sentences("&lt;ul&gt;&lt;li&gt;A b&lt;/li&gt;&lt;li&gt;C d&lt;/li&gt;&lt;/ul&gt;"), ["A b", "C d"])


if __name__ == "__main__":
    unittest.main()
