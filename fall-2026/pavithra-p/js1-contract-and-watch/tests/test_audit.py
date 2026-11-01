"""The label audit scores each prompt against my labels and against the written rule. Every job, label
and Claude verdict here is a CONSTRUCTED fixture; no saved reply is read and no Claude call is made.
"""
import unittest

from agent import config, experiments, resume

PASSES = {"id": 1, "title": "Software Engineer", "location": {"name": "Remote, US"},
          "content": "&lt;p&gt;Python and AWS&lt;/p&gt;"}
TOO_MANY_YEARS = {"id": 2, "title": "Software Engineer", "location": {"name": "Remote, US"},
                  "content": "&lt;p&gt;Python and AWS, 5+ years of experience&lt;/p&gt;"}
JOBS = [({"id": 1, "split": "dev", "company": "C", "title": "Software Engineer"}, PASSES),
        ({"id": 2, "split": "dev", "company": "C", "title": "Software Engineer"}, TOO_MANY_YEARS)]
LABELS = {1: "Not Relevant", 2: "Relevant"}
CLAUDE = {("baseline", 1): "Relevant", ("baseline", 2): "Not Relevant",
          ("revision-no-years", 1): "Relevant", ("revision-no-years", 2): "Relevant"}


class AuditTests(unittest.TestCase):
    def test_each_prompt_is_scored_against_my_labels_and_against_the_rule(self):
        rows = experiments.audit(resume.load(config.RESUME), jobs=JOBS, labels=LABELS,
                                 read=lambda prompt, split, job_id: CLAUDE[(prompt, job_id)])
        self.assertEqual([r["rule"] for r in rows], ["Relevant", "Not Relevant"])
        self.assertEqual(rows[1]["not_met"], ["experience"])
        self.assertEqual(experiments.agreement(rows, "dev", "baseline", "hand"), (0, 2))
        self.assertEqual(experiments.agreement(rows, "dev", "baseline", "rule"), (2, 2))
        self.assertEqual(experiments.agreement(rows, "dev", "revision-no-years", "hand"), (1, 2))
        self.assertEqual(experiments.agreement(rows, "dev", "revision-no-years", "rule"), (1, 2))
        self.assertEqual(LABELS, {1: "Not Relevant", 2: "Relevant"}, "the labels are read, never changed")


if __name__ == "__main__":
    unittest.main()
