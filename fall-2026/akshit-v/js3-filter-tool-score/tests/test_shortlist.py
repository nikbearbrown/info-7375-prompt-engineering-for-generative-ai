"""The shortlist pipeline and the A1-A3 answer rules, with a stub in place of Claude. Postings are CONSTRUCTED."""
import json
import unittest

from agent3 import claims as cl, filter as flt, shortlist as sl

RESUME = {"name": "x", "email": "x@example.com", "phone": "555", "skills": ["Python"], "target_titles": ["Data Engineer"]}
TEXT = ("You will build batch and streaming data pipelines in Python and SQL. "
        "This is a full-time role. You have 3+ years of experience. You will manage a team of five engineers. "
        "Nice to have: experience with Spark. " + "We care about craft and kindness. " * 8)
P = {"id": "greenhouse:figma:c1", "board": "greenhouse:figma", "title": "Data Engineer", "location": "NYC",
     "url": "u", "content_text": TEXT, "employment_type": None}


def stub(justify_claims, check_labels, log):
    def ask(system, user):
        log.append((system[:20], user))
        if "CLAIMS:" in user:
            return {"raw_text": json.dumps({"labels": check_labels(user)})}
        return {"raw_text": json.dumps({"claims": justify_claims})}
    return ask


GOOD = [
    {"kind": "core_work", "claim": "The main work is building data pipelines.",
     "quote": "build batch and streaming data pipelines"},
    {"kind": "level", "claim": "The posting asks for 3+ years.", "quote": "3+ years of experience"},
    {"kind": "employment", "claim": "The role is full-time.", "quote": "This is a full-time role."},
    {"kind": "has", "claim": "The posting requires Spark.", "quote": "Nice to have: experience with Spark."},
    {"kind": "lacks", "claim": "The posting requires Scala.", "quote": "Scala is required"},   # fabricated
]


class Pipeline(unittest.TestCase):
    def run_with(self, labels_by_quote, claims=GOOD):
        log = []

        def check_labels(user):
            out, i = [], 0
            for line in user.splitlines():
                if line.strip().startswith("quote:"):
                    i += 1
                    q = line.split('"', 1)[1].rsplit('"', 1)[0]
                    out.append({"i": i, "label": labels_by_quote.get(q, "supported"), "why": "stub",
                                "contra_quote": "You will manage a team of five engineers."})
            return out
        fres = flt.apply(P)
        rec = sl.process(P, {**fres, "verdict": "keep"}, RESUME, "JUSTIFY", "CHECK", ask=stub(claims, check_labels, log))
        return rec, log

    def test_fabricated_quote_never_reaches_checker(self):
        rec, log = self.run_with({})
        check_msgs = [u for s, u in log if "CLAIMS:" in u]
        self.assertEqual(len(check_msgs), 1)
        self.assertNotIn("Scala is required", check_msgs[0])
        lab = {c["quote"]: c["label"] for c in rec["claims"]}
        self.assertEqual(lab["Scala is required"], "insufficient")

    def test_checker_does_not_see_resume_or_score(self):
        _, log = self.run_with({})
        check_msg = [u for s, u in log if "CLAIMS:" in u][0]
        self.assertNotIn("RÉSUMÉ", check_msg)
        self.assertNotIn("score", check_msg.lower())

    def test_supported_core_claims_answer_relevant(self):
        rec, _ = self.run_with({})
        self.assertEqual(rec["answer"]["answer"], "relevant")

    def test_contradicted_level_answers_not_relevant(self):
        rec, _ = self.run_with({"3+ years of experience": "contradicted"})
        self.assertEqual(rec["answer"], {"answer": "not_relevant", "rule": "A2",
                                         "why": "core claim 'level' is contradicted by the posting"})

    def test_insufficient_core_claim_abstains(self):
        rec, _ = self.run_with({"build batch and streaming data pipelines": "insufficient"})
        self.assertEqual(rec["answer"]["answer"], "cannot_tell")

    def test_nice_to_have_is_insufficient_when_checker_says_so(self):
        rec, _ = self.run_with({"Nice to have: experience with Spark.": "insufficient"})
        lab = {c["quote"]: c["label"] for c in rec["claims"]}
        self.assertEqual(lab["Nice to have: experience with Spark."], "insufficient")

    def test_malformed_justification_is_rejected_not_repaired(self):
        bad = [c for c in GOOD if c["kind"] != "level"]
        rec, log = self.run_with({}, claims=bad)
        self.assertIn("need exactly one level claim", rec["rejection"])
        self.assertEqual(rec["claims"], [])
        self.assertEqual(len(log), 1)   # the checker is never called


class Labels(unittest.TestCase):
    def test_validate_labels_requires_every_claim_once(self):
        self.assertIsNone(sl.validate_labels({"labels": [{"i": 1, "label": "supported"}]}, 2)[0])
        self.assertIsNone(sl.validate_labels({"labels": [{"i": 1, "label": "supported"},
                                                         {"i": 1, "label": "supported"}]}, 2)[0])
        self.assertIsNone(sl.validate_labels({"labels": [{"i": 1, "label": "maybe"}]}, 1)[0])

    def test_quote_normalization(self):
        self.assertTrue(cl.quote_in_posting("BUILD  batch and\nstreaming", P))
        self.assertFalse(cl.quote_in_posting("build ... pipelines", P))
        self.assertFalse(cl.quote_in_posting("ab", P))   # too short to count


if __name__ == "__main__":
    unittest.main()
