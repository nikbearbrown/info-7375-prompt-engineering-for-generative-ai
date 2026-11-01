"""CONTRACT §6 — each wrong version is built here as a mutant, and the checks must catch it."""

import copy
import unittest

from jsagent import rule
from jsagent.checks import alignment_errors, evidence_errors, rule_record_as_evidence
from jsagent.resume import skill_fields
from tests import fixtures as F

JOBS = [F.RELEVANT, F.NON_US, F.SENIOR]  # unique ids, different verdicts, all with skill evidence


class WrongVersion1MisPairing(unittest.TestCase):
    def setUp(self):
        skills = skill_fields(F.persona())
        self.records = [rule_record_as_evidence(rule.judge(j, skills)) for j in JOBS]

    def test_correct_pairing_passes(self):
        self.assertEqual(alignment_errors(JOBS, self.records), [])
        self.assertEqual({r["posting_id"]: r["verdict"] for r in self.records},
                         {k: F.EXPECTED[k] for k in ("101", "103", "105")})

    def test_rotated_verdicts_and_justifications_caught(self):
        wrong = copy.deepcopy(self.records)
        bodies = [{k: r[k] for k in ("verdict", "evidence", "title")} for r in wrong]
        for i, r in enumerate(wrong):  # keep ids, shift everything else by one posting
            r.update(bodies[(i + 1) % len(bodies)])
        self.assertTrue(alignment_errors(JOBS, wrong))

    def test_ids_relabelled_after_sort_caught(self):
        wrong = copy.deepcopy(self.records)
        ids = sorted(r["posting_id"] for r in wrong)[::-1]
        for r, i in zip(wrong, ids):
            r["posting_id"] = i
        self.assertTrue(alignment_errors(JOBS, wrong))

    def test_missing_or_duplicated_record_caught(self):
        self.assertTrue(alignment_errors(JOBS, self.records[:2]))
        self.assertTrue(alignment_errors(JOBS, self.records + self.records[:1]))


class WrongVersion2NoEvidence(unittest.TestCase):
    def setUp(self):
        self.resume = F.persona()
        self.good = rule_record_as_evidence(rule.judge(F.RELEVANT, skill_fields(self.resume)))

    def test_real_evidence_passes(self):
        self.assertEqual(evidence_errors(self.good, F.RELEVANT, self.resume), [])

    def test_generic_justification_caught(self):
        wrong = dict(self.good, evidence=[])  # "Strong match for a backend role."
        self.assertTrue(evidence_errors(wrong, F.RELEVANT, self.resume))

    def test_one_citation_caught(self):
        wrong = dict(self.good, evidence=self.good["evidence"][:1])
        self.assertTrue(evidence_errors(wrong, F.RELEVANT, self.resume))

    def test_invented_quote_caught(self):
        wrong = copy.deepcopy(self.good)
        wrong["evidence"][0]["posting_quote"] = "Expert in Python required"
        self.assertTrue(evidence_errors(wrong, F.RELEVANT, self.resume))

    def test_wrong_resume_field_caught(self):
        wrong = copy.deepcopy(self.good)
        wrong["evidence"][0]["resume_field"] = "skills.frontend[0]"  # React, not Python
        self.assertTrue(evidence_errors(wrong, F.RELEVANT, self.resume))

    def test_same_skill_twice_caught(self):
        wrong = copy.deepcopy(self.good)
        wrong["evidence"] = [wrong["evidence"][0], wrong["evidence"][0]]
        self.assertTrue(evidence_errors(wrong, F.RELEVANT, self.resume))


if __name__ == "__main__":
    unittest.main()
