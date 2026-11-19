"""Scoring for the sampling report and the prompt experiment. Constructed call records only."""

import tempfile
import unittest
from pathlib import Path

from experiments import scoring
from jobwatch.errors import InputError


def call(posting_id, verdict=None, valid=True):
    return {"posting_id": posting_id, "valid": valid, "verdict": verdict if valid else None,
            "error": None if valid else "rejected"}


class ScoreTest(unittest.TestCase):
    def test_a_rejected_reply_is_a_failure_and_never_a_not_relevant_verdict(self):
        summary = scoring.score([call(1, valid=False)], hand_labels={1: "not_relevant"}, rule_verdicts={1: "not_relevant"})
        self.assertEqual(summary["calls"], 1)
        self.assertEqual(summary["valid"], 0)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["per_posting"][1]["verdicts"], {"relevant": 0, "not_relevant": 0, "rejected": 1})

    def test_pass_means_valid_and_equal_to_the_hand_label(self):
        calls = [call(1, "relevant"), call(1, "not_relevant"), call(2, "not_relevant"), call(2, "not_relevant")]
        summary = scoring.score(calls, hand_labels={1: "relevant", 2: "not_relevant"},
                                rule_verdicts={1: "relevant", 2: "relevant"})
        self.assertEqual((summary["calls"], summary["valid"], summary["passed"]), (4, 4, 3))
        # Rule says relevant for both: only the first call on posting 1 agrees.
        self.assertEqual(summary["agrees_with_rule"], 1)
        self.assertEqual(summary["per_posting"][1]["verdicts"], {"relevant": 1, "not_relevant": 1, "rejected": 0})
        self.assertFalse(summary["per_posting"][1]["unanimous"])
        self.assertTrue(summary["per_posting"][2]["unanimous"])
        self.assertEqual(summary["postings_all_calls_passed"], 1)


ALL_EIGHT = ("Engineering role passes (resume.preferences.title_word, resume.preferences.focus_terms, posting.title); "
             "seniority passes (resume.preferences.excluded_title_words); location passes "
             "(resume.preferences.location_terms, posting.location.name); skills pass (resume.skills, posting.content).")


class TraceabilityTest(unittest.TestCase):
    """Pre-registered secondary measure for the v2 change: does the justification itself
    name every field path the rule reads (5 résumé + 3 posting)?"""

    def test_counts_only_valid_replies_that_name_every_path(self):
        calls = [
            dict(call(1, "relevant"), justification=ALL_EIGHT),
            dict(call(2, "relevant"), justification="posting.title, posting.location.name and posting.content all pass."),
            dict(call(3, "not_relevant"), justification="The title has no engineer."),
            call(4, valid=False),
        ]
        self.assertEqual(scoring.traceability(calls),
                         {"valid": 3, "names_all_8_paths": 1, "names_all_3_posting_paths": 2})


class HandLabelTest(unittest.TestCase):
    def write(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "hand_labels.csv"
        lines = ["n,posting_id,title,label,failed_conditions,labeled_at,notes"]
        lines += [f'{i},{pid},"Title, {pid}",{label},,,' for i, (pid, label) in enumerate(rows, 1)]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_reads_labels_for_the_requested_ids(self):
        path = self.write([(11, "relevant"), (22, "not_relevant")])
        self.assertEqual(scoring.load_hand_labels(path, [11, 22]), {11: "relevant", 22: "not_relevant"})

    def test_a_missing_label_stops_the_experiment(self):
        path = self.write([(11, "relevant"), (22, "")])
        with self.assertRaises(InputError):
            scoring.load_hand_labels(path, [11, 22])

    def test_an_unknown_label_stops_the_experiment(self):
        path = self.write([(11, "maybe")])
        with self.assertRaises(InputError):
            scoring.load_hand_labels(path, [11])


if __name__ == "__main__":
    unittest.main()
