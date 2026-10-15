"""Run: python -m unittest discover -s tests -v"""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from stopline.checks import ACCEPT, HUMAN_REVIEW, NEEDS_EVIDENCE
from stopline.engine import evaluate, evaluate_all, index_evidence, pick_outcome

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


INCIDENTS = load("incidents.json")
EVIDENCE = load("evidence.json")
LABELS = load("labels.json")
INDEX, _ = index_evidence(EVIDENCE)
BY_ID = {i["id"]: i for i in INCIDENTS}


def run(incident_id):
    return evaluate(BY_ID[incident_id], INDEX)


class PrecedenceTests(unittest.TestCase):
    def test_human_review_beats_needs_evidence(self):
        self.assertEqual(pick_outcome({NEEDS_EVIDENCE, HUMAN_REVIEW}), HUMAN_REVIEW)

    def test_needs_evidence_beats_accept(self):
        self.assertEqual(pick_outcome({NEEDS_EVIDENCE}), NEEDS_EVIDENCE)

    def test_no_failures_is_accept(self):
        self.assertEqual(pick_outcome(set()), ACCEPT)


class LabelledCaseTests(unittest.TestCase):
    def test_every_non_limitation_case_matches_its_label(self):
        for iid, label in LABELS.items():
            if label["known_limitation"]:
                continue
            with self.subTest(incident=iid):
                self.assertEqual(run(iid)["outcome"], label["expected"], label["why"])

    def test_known_limitations_are_still_missed(self):
        # These document current blind spots. If one starts passing, the rules
        # changed: update the label's known_limitation flag and the brief.
        for iid in ("INC-016", "INC-017"):
            with self.subTest(incident=iid):
                self.assertEqual(run(iid)["outcome"], ACCEPT)
                self.assertEqual(LABELS[iid]["expected"], HUMAN_REVIEW)


class AuditRecordTests(unittest.TestCase):
    def test_all_failed_checks_recorded_not_only_decisive(self):
        record = run("INC-011")
        self.assertEqual(record["outcome"], HUMAN_REVIEW)
        self.assertIn("claims_match_evidence", record["failed_checks"])
        self.assertIn("required_evidence_kinds", record["failed_checks"])
        self.assertEqual(record["decided_by"], ["claims_match_evidence"])

    def test_contradiction_detail_names_both_values(self):
        details = next(c for c in run("INC-003")["checks"] if c["check"] == "claims_match_evidence")["details"]
        self.assertEqual(len(details), 1)
        self.assertIn("defects_found=0", details[0])
        self.assertIn("records 3", details[0])

    def test_deterministic(self):
        first = [json.dumps(r, sort_keys=True) for r in evaluate_all(INCIDENTS, EVIDENCE)[0]]
        second = [json.dumps(r, sort_keys=True) for r in evaluate_all(INCIDENTS, EVIDENCE)[0]]
        self.assertEqual(first, second)

    def test_input_change_changes_hash(self):
        changed = copy.deepcopy(BY_ID["INC-001"])
        changed["description"] += " (edited)"
        self.assertNotEqual(evaluate(changed, INDEX)["input_sha256"], run("INC-001")["input_sha256"])


class RobustnessTests(unittest.TestCase):
    def test_garbage_inputs_escalate_without_crashing(self):
        for bad in (None, [], {}, {"id": "X", "proposed_action": "release"}, {"id": "Y", "proposed_action": {"claims": [1]}}):
            with self.subTest(value=bad):
                self.assertEqual(evaluate(bad, INDEX)["outcome"], HUMAN_REVIEW)

    def test_invalid_and_duplicate_evidence_rejected(self):
        index, errors = index_evidence([EVIDENCE[0], EVIDENCE[0], {"id": "E-BAD", "kind": "rumour"}])
        self.assertEqual(list(index), [EVIDENCE[0]["id"]])
        # duplicate + four problems in E-BAD (kind, lot, collected_at, fields)
        self.assertEqual(len(errors), 5)

    def test_cli_prints_one_outcome_and_one_record_per_incident(self):
        proc = subprocess.run(
            [sys.executable, "-m", "stopline", str(DATA / "incidents.json")],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        lines = proc.stdout.splitlines()
        self.assertEqual(len(lines), 2 * len(INCIDENTS))
        for outcome_line, record_line in zip(lines[::2], lines[1::2]):
            record = json.loads(record_line)
            self.assertTrue(outcome_line.startswith(f"{record['incident_id']}  {record['outcome']}"))


if __name__ == "__main__":
    unittest.main()
