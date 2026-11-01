"""CONTRACT.md's worked example, checked against the REAL posting saved by the 2026-10-30 live baseline."""
import hashlib
import json
import unittest

from jobwatch import board, rule
from jobwatch.text import find_phrase, normalize
from tests.helpers import RESUME, ROOT, assert_justification_is_supported

FIXTURE = ROOT / "tests" / "fixtures" / "klaviyo-7855798003.json"


class WorkedExample(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.posting = board.parse_board(FIXTURE.read_bytes())[0]

    def test_fixture_is_the_posting_inside_the_saved_raw_response(self):
        raw_path = ROOT / self.data["_source"]["raw_response"]
        raw = raw_path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.data["_source"]["raw_sha256"])
        original = next(j for j in json.loads(raw)["jobs"] if j["id"] == 7855798003)
        self.assertEqual(original, self.posting)

    def test_hand_evaluation_in_the_contract_matches_the_rule(self):
        r = rule.classify(self.posting, RESUME)
        self.assertEqual(r["verdict"], rule.RELEVANT)
        self.assertEqual(r["checks"], {"title": True, "seniority": True, "location": True, "skills": True})
        self.assertEqual([m["skill"] for m in r["details"]["skills"]["matched"]],
                         ["Python", "Redis", "Kubernetes", "Distributed Systems"])
        assert_justification_is_supported(self, self.posting, r)

    def test_contract_limitations_are_visible_in_the_real_text(self):
        content = normalize(self.posting["content"])
        self.assertIn("2+ years of professional software engineering", content)   # Engineer II limitation
        self.assertIsNotNone(find_phrase("postgres", content))                     # says Postgres ...
        self.assertIsNone(find_phrase("postgresql", content))                      # ... so PostgreSQL is not counted


if __name__ == "__main__":
    unittest.main()
