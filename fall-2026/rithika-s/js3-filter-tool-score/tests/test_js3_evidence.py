"""js3.evidence on CONSTRUCTED postings and fake Claude outputs."""

import json
import unittest

from js3 import evidence as ev

POSTING = {
    "board": "constructed", "id": "1",
    "title": "Senior ML Engineer, Inference",
    "location": "Boston,  MA",
    "body_text": "You will build\n\nLLM evaluation   pipelines with "
                 "PyTorch. Straße work.",
}


def output(*quotes):
    return json.dumps({"claims": [{"claim": f"claim {n}", "quote": q}
                                  for n, q in enumerate(quotes, 1)]})


class QuoteCheckTests(unittest.TestCase):

    def test_found_is_case_and_whitespace_insensitive(self):
        for quote in ("llm EVALUATION pipelines", "build LLM evaluation",
                      "  pytorch.  ", "boston, ma", "ml engineer"):
            with self.subTest(quote=quote):
                result = ev.check_quote(quote, POSTING)
                self.assertEqual(result["check"], ev.FOUND)
                self.assertEqual(result["verdict"], ev.CANDIDATE)

    def test_offsets_point_at_original_text(self):
        where = ev.find_quote("llm evaluation pipelines", POSTING)
        text = POSTING[where["field"]][where["start"]:where["end"]]
        self.assertEqual(text, "LLM evaluation   pipelines")
        where = ev.find_quote("strasse", POSTING)
        self.assertEqual(POSTING["body_text"][where["start"]:where["end"]],
                         "Straße")

    def test_not_found_paraphrase_ellipsis_and_cross_field(self):
        for quote in ("build LLM pipelines", "build ... pipelines",
                      "Inference Boston", "visa sponsorship", "", "   "):
            with self.subTest(quote=quote):
                result = ev.check_quote(quote, POSTING)
                self.assertEqual(result["check"], ev.NOT_FOUND)
                self.assertEqual(result["verdict"], ev.CANNOT_TELL)

    def test_not_stated_must_be_exact(self):
        self.assertEqual(ev.check_quote("NOT STATED", POSTING)["check"],
                         ev.STATED_NOT)
        self.assertEqual(ev.check_quote("NOT STATED", POSTING)["verdict"],
                         ev.CANNOT_TELL)
        self.assertEqual(ev.check_quote("not stated", POSTING)["check"],
                         ev.NOT_FOUND)

    def test_verdict_is_never_supported(self):
        result = ev.check_output(output("PyTorch", "NOT STATED", "nope"),
                                 POSTING)
        verdicts = {c["verdict"] for c in result["claims"]}
        self.assertEqual(verdicts, {ev.CANDIDATE, ev.CANNOT_TELL})
        self.assertNotIn("supported", json.dumps(result).lower())

    def test_context_is_300_chars_around_the_quote(self):
        posting = dict(POSTING, body_text="a" * 500 + " KEY PHRASE " +
                       "b" * 500)
        where = ev.find_quote("key phrase", posting)
        ctx = ev.context(posting, where)
        self.assertEqual(len(ctx), 300)
        self.assertIn("KEY PHRASE", ctx)
        self.assertEqual(ev.context(posting, None), "a" * 300)


class ParseTests(unittest.TestCase):

    def test_valid_output(self):
        claims = ev.parse_claims(output("a", "b", "c"))
        self.assertEqual(len(claims), 3)

    def test_parse_errors_are_reported_not_repaired(self):
        bad = [
            "",
            "Here is the JSON: {}",
            "```json\n" + output("a", "b", "c") + "\n```",
            output("a", "b"),
            output("a", "b", "c", "d", "e", "f"),
            json.dumps({"claims": [{"claim": "x", "quote": "y",
                                    "extra": 1}] * 3}),
            json.dumps({"claims": [{"claim": "x", "quote": 3}] * 3}),
            json.dumps({"claims": [], "notes": "x"}),
            json.dumps([{"claim": "x", "quote": "y"}] * 3),
        ]
        for raw in bad:
            with self.subTest(raw=raw[:40]):
                with self.assertRaises(ev.ParseError):
                    ev.parse_claims(raw)
                result = ev.check_output(raw, POSTING)
                self.assertTrue(result["parse_error"])
                self.assertEqual(result["claims"], [])


if __name__ == "__main__":
    unittest.main()
