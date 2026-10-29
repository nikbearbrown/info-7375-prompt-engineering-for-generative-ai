"""Claude's output schema, and the separate support check."""
import copy
import json
import unittest

from tests import helpers

NEW_IDS = {9000000008}


def valid_judgment():
    return {
        "posting_id": 9000000008,
        "verdict": "relevant",
        "citations": [
            {"resume_field": "skills.languages", "posting_field": "content", "quote": "SQL"},
        ],
        "label": "judgment",
    }


class Schema(helpers.ContractTest):
    modules = ("agent.validator",)

    def errors(self, judgment):
        return self.validator.validate(judgment, helpers.resume(), NEW_IDS)

    def assert_rejected(self, judgment):
        self.assertTrue(self.errors(judgment), f"should be rejected: {judgment}")

    def test_valid_judgment_is_accepted(self):
        self.assertEqual(self.errors(valid_judgment()), [])

    def test_valid_judgment_as_json_text_is_accepted(self):
        self.assertEqual(self.errors(json.dumps(valid_judgment())), [])

    def test_missing_key(self):
        for key in valid_judgment():
            judgment = valid_judgment()
            del judgment[key]
            with self.subTest(missing=key):
                self.assert_rejected(judgment)

    def test_extra_key(self):
        self.assert_rejected(dict(valid_judgment(), confidence=0.9))

    def test_bad_verdict_value(self):
        self.assert_rejected(dict(valid_judgment(), verdict="maybe"))

    def test_wrong_label(self):
        self.assert_rejected(dict(valid_judgment(), label="record"))

    def test_empty_citations(self):
        self.assert_rejected(dict(valid_judgment(), citations=[]))

    def test_unknown_resume_field(self):
        judgment = valid_judgment()
        judgment["citations"][0]["resume_field"] = "skills.cooking"
        self.assert_rejected(judgment)

    def test_unknown_posting_field(self):
        judgment = valid_judgment()
        judgment["citations"][0]["posting_field"] = "department"
        self.assert_rejected(judgment)

    def test_posting_id_not_in_this_run(self):
        self.assert_rejected(dict(valid_judgment(), posting_id=9000000001))

    def test_empty_or_whitespace_quote(self):
        # CONTRACT.md amendment, 2026-10-29.
        for quote in ("", "   ", "\n"):
            judgment = valid_judgment()
            judgment["citations"][0]["quote"] = quote
            with self.subTest(quote=quote):
                self.assert_rejected(judgment)


class Support(helpers.ContractTest):
    modules = ("agent.validator",)

    def test_quote_present_in_field_is_supported(self):
        citation = valid_judgment()["citations"][0]
        self.assertEqual(self.validator.support_check(citation, helpers.posting(9000000008)), "supported")

    def test_quote_absent_from_field_is_not_supported(self):
        citation = {"resume_field": "skills.data_bi", "posting_field": "content", "quote": "Databricks"}
        self.assertEqual(self.validator.support_check(citation, helpers.posting(9000000008)), "not supported")

    def test_empty_quote_is_not_supported(self):
        citation = {"resume_field": "skills.languages", "posting_field": "content", "quote": ""}
        self.assertEqual(self.validator.support_check(citation, helpers.posting(9000000008)), "not supported")

    def test_quote_present_in_a_different_field_is_not_supported(self):
        citation = {"resume_field": "skills.languages", "posting_field": "title", "quote": "SQL"}
        self.assertEqual(self.validator.support_check(citation, helpers.posting(9000000008)), "not supported")


if __name__ == "__main__":
    unittest.main()
