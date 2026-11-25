"""The one held-out comparison, scored the way the student chose before it ran (FILTER.md, "After
the reject audit, before any held-out label was scored"). Written before jobwatch/held_out.py
existed. Rows, reasons and members here are CONSTRUCTED; none is a held-out label."""

import json
import tempfile
import unittest
from pathlib import Path

from jobwatch import held_out


def row(label, decision, reason="r"):
    return {"label": label, "decision": decision, "reason": reason}


def agreeing(n):
    return [row("no", "rejected") for _ in range(n)]


class UnmetRequirementTest(unittest.TestCase):
    def test_a_reason_stating_years_counts(self):
        self.assertTrue(held_out.names_an_unmet_requirement("The senior backend role lists 5+ years of software engineering experience."))
        self.assertTrue(held_out.names_an_unmet_requirement("The posting uses a senior title and sets a six-year experience minimum."))

    def test_years_said_to_be_preferred_do_not_count(self):
        self.assertFalse(held_out.names_an_unmet_requirement("The role leads executive content strategy and lists 12+ years under preferred qualifications."))

    def test_a_minimum_a_requirement_a_clearance_or_new_graduates_counts(self):
        for reason in ("The opening sets a minimum in enterprise sales.",
                       "The role requires a security clearance.",
                       "The minimums include active TS/SCI clearance with polygraph.",
                       "The posting explicitly places new graduates outside its intended audience.",
                       "It is not open to entry-level applicants."):
            self.assertTrue(held_out.names_an_unmet_requirement(reason), reason)

    def test_other_reasons_do_not_count(self):
        for reason in ("This is a direct sales opening in London.",
                       "The role centers on developer relations and helping developers adopt the platform.",
                       "This is a trademark and domain counsel role."):
            self.assertFalse(held_out.names_an_unmet_requirement(reason), reason)


class ScoreTest(unittest.TestCase):
    def test_cannot_tell_rows_are_left_out(self):
        result = held_out.score(agreeing(9) + [row("cannot tell", "reaches"), row("cannot tell", "rejected")])
        self.assertEqual((result["labelled"], result["cannot_tell"], result["decided"], result["matches"]), (11, 2, 9, 9))

    def test_pass_at_ninety_percent_of_the_decided_rows(self):
        nine_of_ten = held_out.score(agreeing(9) + [row("no", "reaches", "Sales in London.")])
        self.assertTrue(nine_of_ten["checks"]["at least 90% of the Yes and No rows match"])
        eight_of_nine = held_out.score(agreeing(8) + [row("no", "reaches", "Sales in London.")])
        self.assertFalse(eight_of_nine["checks"]["at least 90% of the Yes and No rows match"])
        self.assertFalse(eight_of_nine["passed"])

    def test_more_than_one_false_exclusion_fails(self):
        one = held_out.score(agreeing(18) + [row("yes", "rejected")])
        two = held_out.score(agreeing(28) + [row("yes", "rejected"), row("yes", "rejected")])
        self.assertTrue(one["checks"]["no more than one Yes rejected"])
        self.assertFalse(two["checks"]["no more than one Yes rejected"])
        self.assertFalse(two["passed"])

    def test_one_cleared_unmet_requirement_fails(self):
        cleared = held_out.score(agreeing(19) + [row("no", "reaches", "The role lists 6+ years in data engineering.")])
        listed = held_out.score(agreeing(19) + [row("no", "reaches", "This is a direct sales opening in London.")])
        self.assertEqual(len(cleared["unmet_requirements_cleared"]), 1)
        self.assertFalse(cleared["checks"]["no unmet requirement cleared"])
        self.assertFalse(cleared["passed"])
        self.assertEqual((len(listed["unmet_requirements_cleared"]), len(listed["false_inclusions"])), (0, 1))
        self.assertTrue(listed["passed"])

    def test_a_rejected_no_never_counts_as_cleared(self):
        result = held_out.score(agreeing(9) + [row("no", "rejected", "The role lists 6+ years.")])
        self.assertEqual(result["unmet_requirements_cleared"], [])


class OnceTest(unittest.TestCase):
    def test_only_the_held_out_members_are_compared(self):
        members = [{"board": "b", "key": "1", "stratum": "held-out rejected", "label_id": "P01"},
                   {"board": "b", "key": "2", "stratum": "audit random reject", "label_id": "P02"},
                   {"board": "b", "key": "3", "stratum": "held-out kept or review", "label_id": "P03"}]
        labels = {"P01": {"label": "no", "reason": "a"}, "P02": {"label": "yes", "reason": "b"},
                  "P03": {"label": "yes", "reason": "c"}}
        records = {("b", "1"): {"fate": "rejected", "score": 0}, ("b", "2"): {"fate": "rejected", "score": 0},
                   ("b", "3"): {"fate": "kept", "score": 3}}
        rows = held_out.rows(members, labels, records)
        self.assertEqual([r["label_id"] for r in rows], ["P01", "P03"])
        self.assertEqual([r["outcome"] for r in rows], ["agree", "agree"])

    def test_a_second_run_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            held_out.claim_the_single_run(out)
            (out / held_out.RESULTS).write_text(json.dumps({}), encoding="utf-8")
            with self.assertRaises(held_out.AlreadyMeasured):
                held_out.claim_the_single_run(out)


if __name__ == "__main__":
    unittest.main()
