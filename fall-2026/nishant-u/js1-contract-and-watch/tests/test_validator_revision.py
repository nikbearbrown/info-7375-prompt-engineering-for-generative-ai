"""The revision-1 schema: the baseline schema plus failed_check (CONTRACT.md amendment 2026-10-29)."""
import unittest

from tests import helpers
from tests.test_validator import NEW_IDS, valid_judgment


def valid_revision():
    return dict(valid_judgment(), failed_check=None)


def valid_not_relevant():
    return dict(valid_judgment(), verdict="not_relevant", failed_check="R4")


class RevisionSchema(helpers.ContractTest):
    modules = ("agent.validator",)

    def errors(self, judgment, schema="revision-1"):
        return self.validator.validate(judgment, helpers.resume(), NEW_IDS, schema=schema)

    def test_valid_revision_reply_is_accepted(self):
        self.assertEqual(self.errors(valid_revision()), [])
        self.assertEqual(self.errors(valid_not_relevant()), [])

    def test_missing_failed_check_is_rejected(self):
        self.assertTrue(self.errors(valid_judgment()))

    def test_bad_failed_check_value_is_rejected(self):
        for bad in ("R5", "r2", "", "R1, R2", 2, ["R1"]):
            with self.subTest(value=bad):
                self.assertTrue(self.errors(dict(valid_not_relevant(), failed_check=bad)))

    def test_null_with_not_relevant_is_rejected(self):
        self.assertTrue(self.errors(dict(valid_not_relevant(), failed_check=None)))

    def test_check_with_relevant_is_rejected(self):
        self.assertTrue(self.errors(dict(valid_revision(), failed_check="R2")))

    def test_baseline_schema_unchanged(self):
        # The baseline still accepts its own shape and rejects the extra key.
        self.assertEqual(self.errors(valid_judgment(), schema="baseline"), [])
        self.assertTrue(self.errors(valid_revision(), schema="baseline"))


if __name__ == "__main__":
    unittest.main()
