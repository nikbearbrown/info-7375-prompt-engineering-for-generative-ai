"""Reading the student's pasted label table, and keeping the held-out labels out of the development
comparison. Tables, members and records in the first two classes are CONSTRUCTED; the last class
checks the committed files."""

import hashlib
import json
import unittest
from pathlib import Path

from jobwatch import hand_labels, sample

ROOT = Path(__file__).resolve().parent.parent
HEADER = "ID\tVerdict\tReason"


def table(rows, legend="A legend line."):
    return "\n".join([legend, HEADER] + ["\t".join(r) for r in rows]) + "\n"


class ParseTest(unittest.TestCase):
    def test_verdicts_map_to_the_page_labels(self):
        rows = [("P01", "Yes", "r1"), ("P02", "No", "r2"), ("P03", "Can’t tell", "r3"), ("P04", "Can't tell", "r4")]
        parsed = hand_labels.parse(table(rows), ids=["P01", "P02", "P03", "P04"])
        self.assertEqual({k: v["label"] for k, v in parsed["labels"].items()},
                         {"P01": "yes", "P02": "no", "P03": "cannot tell", "P04": "cannot tell"})

    def test_verdict_and_reason_are_kept_as_written(self):
        reason = "The posting asks for a “very experienced” Python programmer."
        parsed = hand_labels.parse(table([("P01", "Can’t tell", reason)]), ids=["P01"])
        self.assertEqual(parsed["labels"]["P01"]["reason"], reason)
        self.assertEqual(parsed["labels"]["P01"]["verdict_as_written"], "Can’t tell")

    def test_the_legend_is_kept_and_not_read_as_a_row(self):
        parsed = hand_labels.parse(table([("P01", "No", "r")], legend="Yes means worth showing."), ids=["P01"])
        self.assertEqual(parsed["legend"], ["Yes means worth showing."])
        self.assertEqual(list(parsed["labels"]), ["P01"])

    def test_an_unknown_verdict_is_refused(self):
        with self.assertRaises(ValueError):
            hand_labels.parse(table([("P01", "Maybe", "r")]), ids=["P01"])

    def test_a_row_without_a_reason_is_refused(self):
        with self.assertRaises(ValueError):
            hand_labels.parse(table([("P01", "No", "")]), ids=["P01"])

    def test_every_sample_id_exactly_once(self):
        with self.assertRaises(ValueError):   # P02 missing
            hand_labels.parse(table([("P01", "No", "r")]), ids=["P01", "P02"])
        with self.assertRaises(ValueError):   # P01 twice
            hand_labels.parse(table([("P01", "No", "r"), ("P01", "Yes", "r")]), ids=["P01"])
        with self.assertRaises(ValueError):   # P99 is not in the sample
            hand_labels.parse(table([("P01", "No", "r"), ("P99", "No", "r")]), ids=["P01"])

    def test_no_header_no_labels(self):
        with self.assertRaises(ValueError):
            hand_labels.parse("P01\tNo\tr\n", ids=["P01"])


def member(label_id, stratum, key):
    return {"board": "greenhouse/anthropic", "key": key, "stratum": stratum, "label_id": label_id}


class DevelopmentRowsTest(unittest.TestCase):
    MEMBERS = [member("P01", "held-out rejected", "1"), member("P02", "audit random reject", "2"),
               member("P03", "held-out kept or review", "3"), member("P04", "audit kept sample", "4"),
               member("P05", "audit at the cutoff", "5"), member("P06", "audit one point under the cutoff", "6")]
    LABELS = {f"P0{n}": {"label": label, "reason": f"reason {n}"}
              for n, label in zip(range(1, 7), ["yes", "yes", "no", "no", "cannot tell", "yes"])}
    RECORDS = {("greenhouse/anthropic", str(n)): {"fate": fate, "score": score}
               for n, fate, score in [(1, "rejected", 0), (2, "rejected", 0), (3, "kept", 3), (4, "kept", 3),
                                      (5, "kept", 2), (6, "rejected", 1)]}

    def test_the_split_names_both_held_out_groups_and_nothing_else(self):
        self.assertEqual(sorted(sample.HELD_OUT), ["held-out kept or review", "held-out rejected"])
        self.assertEqual([m["label_id"] for m in sample.development(self.MEMBERS)], ["P02", "P04", "P05", "P06"])
        self.assertEqual([m["label_id"] for m in sample.held_out(self.MEMBERS)], ["P01", "P03"])

    def test_development_rows_never_carry_a_held_out_label(self):
        rows = hand_labels.development_rows(self.MEMBERS, self.LABELS, self.RECORDS)
        self.assertEqual([r["label_id"] for r in rows], ["P02", "P04", "P05", "P06"])
        self.assertEqual([r["outcome"] for r in rows], ["false exclusion", "false inclusion", "cannot tell", "false exclusion"])
        self.assertEqual([r["stratum"] for r in rows],
                         ["audit random reject", "audit kept sample", "audit at the cutoff", "audit one point under the cutoff"])
        self.assertEqual(rows[0]["reason"], "reason 2")


class CommittedLabelsTest(unittest.TestCase):
    """The committed labels are the pasted table, unchanged, and cover the sample exactly."""

    def test_the_json_matches_the_pasted_table_and_the_sample(self):
        pasted = ROOT / "labels" / "hand-labels-as-pasted.tsv"
        converted = json.loads((ROOT / "labels" / "hand-labels.json").read_text(encoding="utf-8"))
        sheet_bytes = (ROOT / "labels" / "v0.1-sample.json").read_bytes()
        self.assertEqual(converted["source_sha256"], hashlib.sha256(pasted.read_bytes()).hexdigest())
        self.assertEqual(converted["sample_sha256"], hashlib.sha256(sheet_bytes).hexdigest())
        ids = [m["label_id"] for m in json.loads(sheet_bytes)["members"]]
        self.assertEqual(converted, {**converted, **hand_labels.parse(pasted.read_text(encoding="utf-8"), ids)})


if __name__ == "__main__":
    unittest.main()
