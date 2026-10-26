"""Offline, deterministic tests. No network, no API key.

    python -m unittest discover -s tests -v
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from claimcheck import answerers, eval as ev  # noqa: E402
from claimcheck.checker import check  # noqa: E402
from claimcheck.contract import Answer, ContractError, parse  # noqa: E402
from claimcheck.grading import grade, shown  # noqa: E402

DOC_ID = "policy_ho3_synthetic.md"
DOCS = ev.load_docs()
GOLD = {q["id"]: q for q in ev.load_questions()}


def ans(answer, quote, status="answered", doc_id=DOC_ID):
    return Answer(answer=answer, quote=quote, doc_id=doc_id, status=status)


class ContractTests(unittest.TestCase):
    def test_valid_reply_parses(self):
        raw = json.dumps({"answer": "a", "quote": "b", "doc_id": DOC_ID, "status": "answered"})
        self.assertEqual(parse(raw).status, "answered")

    def test_broken_replies_are_rejected(self):
        cases = {
            "not json": "Sure! The answer is $350,000.",
            "missing field": json.dumps({"answer": "a", "quote": "b", "status": "answered"}),
            "extra field": json.dumps({"answer": "a", "quote": "b", "doc_id": DOC_ID, "status": "answered", "why": "x"}),
            "bad status": json.dumps({"answer": "a", "quote": "b", "doc_id": DOC_ID, "status": "maybe"}),
            "non-string": json.dumps({"answer": 1, "quote": "b", "doc_id": DOC_ID, "status": "answered"}),
        }
        for label, raw in cases.items():
            with self.subTest(label), self.assertRaises(ContractError):
                parse(raw)


class CheckerTests(unittest.TestCase):
    def test_verbatim_quote_passes(self):
        r = check(ans("Notice is due within 60 days.", "You must give us notice of any loss within 60 days after the loss."), DOCS)
        self.assertTrue(r.passed, r.reasons)

    def test_whitespace_and_curly_quotes_are_normalised(self):
        r = check(ans("Notice within 60 days.", "You must  give us notice of any loss\nwithin 60 days after the loss."), DOCS)
        self.assertTrue(r.passed, r.reasons)

    def test_invented_quote_is_rejected(self):
        r = check(ans("Earthquake is covered.", "We cover direct physical loss caused by earthquake."), DOCS)
        self.assertFalse(r.passed)
        self.assertIn("quote not found word for word in the document", r.reasons)

    def test_number_missing_from_quote_is_rejected(self):
        # real quote, but the answer states an amount the quote does not contain
        r = check(ans("Sewer backup is covered up to $20,000.",
                      "We cover direct physical loss caused by water that backs up through sewers or drains, up to $10,000 per loss."), DOCS)
        self.assertFalse(r.passed)
        self.assertTrue(any("$20,000" in reason for reason in r.reasons))

    def test_section_references_are_not_treated_as_numbers(self):
        r = check(ans("A pipe that bursts is covered under 4(b).",
                      "Sudden and accidental discharge or overflow of water from within a plumbing, heating or air conditioning system, including a pipe that bursts."), DOCS)
        self.assertTrue(r.passed, r.reasons)

    def test_short_quote_and_unknown_document_are_rejected(self):
        self.assertFalse(check(ans("Yes.", "Flood"), DOCS).passed)
        self.assertFalse(check(ans("Flood is excluded.", "Flood, surface water, waves", doc_id="other.md"), DOCS).passed)

    def test_unsupported_answer_words_are_rejected(self):
        r = check(ans("Hurricanes, tornadoes and lightning strikes are all insured perils.",
                      "Damage caused by windstorm or hail."), DOCS)
        self.assertFalse(r.passed)

    def test_refusal_always_passes(self):
        self.assertTrue(check(ans("", "", status="not_in_documents"), DOCS).passed)


class GradingTests(unittest.TestCase):
    def test_answering_a_not_in_documents_question(self):
        q = GOLD["Q08"]
        self.assertEqual(grade(q, ans("x", "y"), "ANSWERED"), "WRONG")
        self.assertEqual(grade(q, ans("x", "y"), "REJECTED"), "CAUGHT")
        self.assertEqual(grade(q, ans("", "", "not_in_documents"), "REFUSED"), "CORRECT")

    def test_real_quote_from_the_wrong_clause_passes_the_checker_but_grades_wrong(self):
        # The endorsement trap: 5(d) says backup is excluded, but Endorsement E-2 overrides it.
        a = ans("Water backup through sewers is excluded.", "Water that backs up through sewers or drains.")
        r = check(a, DOCS)
        self.assertTrue(r.passed, r.reasons)  # the checker cannot see the override
        self.assertEqual(grade(GOLD["Q06"], a, shown(a, r)), "WRONG")

    def test_correct_answer_and_missed_answer(self):
        a = ans("The dwelling limit is $350,000.", "| Coverage A - Dwelling | $350,000 |")
        self.assertEqual(grade(GOLD["Q01"], a, shown(a, check(a, DOCS))), "CORRECT")
        self.assertEqual(grade(GOLD["Q01"], None, "BROKEN"), "MISSED")


class EvalTests(unittest.TestCase):
    def test_question_set_is_still_frozen(self):
        self.assertEqual(ev.sha256(ev.QUESTIONS), ev.frozen_sha())

    def test_set_has_ten_questions_and_at_least_a_third_are_traps(self):
        qs = list(GOLD.values())
        self.assertEqual(len(qs), 10)
        self.assertGreaterEqual(sum(q["kind"].startswith("trap") for q in qs) / len(qs), 1 / 3)

    def test_baseline_run_is_offline_and_writes_a_dated_report(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(ev.main(["--answerer", "baseline", "--reports", tmp]), 0)
            reports = list(Path(tmp).glob("eval_report-*-baseline.md"))
            self.assertEqual(len(reports), 1)
            text = reports[0].read_text()
            self.assertIn("not Claude", text)
            self.assertIn("Results (failures first)", text)

    def test_claude_answerer_stops_cleanly_without_a_key(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit) as cm:
            answerers.ClaudeAnswerer()
        self.assertIn("ANTHROPIC_API_KEY", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
