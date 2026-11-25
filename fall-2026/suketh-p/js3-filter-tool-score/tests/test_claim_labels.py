"""Reading the student's pasted claim labels (a label per claim suffix for every rank, then notes by
claim ID), and the flip challenge's reply. Texts in the first two classes are CONSTRUCTED; the last
class checks the committed files."""

import hashlib
import json
import unittest
from pathlib import Path

from jobwatch import claim_labels, flip

ROOT = Path(__file__).resolve().parent.parent
IDS = [f"R{r}-C{c}" for r in (1, 2) for c in (1, 2, 3)]


def paste(suffix_rows, note_rows, before="Claims done.", after="A closing remark."):
    lines = [before, "", "Claim suffix\tLabel"] + ["\t".join(r) for r in suffix_rows] + ["", "",
             "Insufficient claim IDs\tNote"] + ["\t".join(r) for r in note_rows] + ["", "", after]
    return "\n".join(lines) + "\n"


GOOD = paste([("C1, C2", "Supported"), ("C3", "Insufficient")],
             [("R1-C3", "The posting leaves it unstated."), ("R2-C3", "The posting ties it to level.")])


class ParseTest(unittest.TestCase):
    def test_a_suffix_label_applies_to_every_rank(self):
        parsed = claim_labels.parse(GOOD, IDS)
        self.assertEqual({k: v["label"] for k, v in parsed["labels"].items()},
                         {"R1-C1": "supported", "R1-C2": "supported", "R1-C3": "insufficient",
                          "R2-C1": "supported", "R2-C2": "supported", "R2-C3": "insufficient"})

    def test_notes_attach_by_id_and_by_suffix_at_all_ranks(self):
        text = paste([("C1, C2", "Supported"), ("C3", "Insufficient")], [("C3 at all two ranks", "Unstated everywhere.")])
        parsed = claim_labels.parse(text, IDS)
        self.assertEqual((parsed["labels"]["R1-C3"]["note"], parsed["labels"]["R2-C3"]["note"]),
                         ("Unstated everywhere.", "Unstated everywhere."))
        self.assertIsNone(parsed["labels"]["R1-C1"]["note"])
        self.assertEqual(claim_labels.parse(GOOD, IDS)["labels"]["R2-C3"]["note"], "The posting ties it to level.")

    def test_the_text_around_the_tables_is_kept_as_written(self):
        parsed = claim_labels.parse(GOOD, IDS)
        self.assertEqual((parsed["text_before"], parsed["text_after"]), (["Claims done."], ["A closing remark."]))

    def test_every_claim_gets_exactly_one_label(self):
        with self.assertRaises(ValueError):   # C3 not covered
            claim_labels.parse(paste([("C1, C2", "Supported")], []), IDS)
        with self.assertRaises(ValueError):   # C2 twice
            claim_labels.parse(paste([("C1, C2", "Supported"), ("C2, C3", "Insufficient")], [("R1-C3", "a"), ("R2-C3", "b")]), IDS)

    def test_an_unknown_label_is_refused(self):
        with self.assertRaises(ValueError):
            claim_labels.parse(paste([("C1, C2", "Supported"), ("C3", "Probably")], []), IDS)

    def test_an_insufficient_claim_needs_a_note(self):
        with self.assertRaises(ValueError):   # R2-C3 has no note
            claim_labels.parse(paste([("C1, C2", "Supported"), ("C3", "Insufficient")], [("R1-C3", "a")]), IDS)

    def test_a_note_under_the_wrong_label_is_refused(self):
        with self.assertRaises(ValueError):   # R1-C1 is supported, not insufficient
            claim_labels.parse(paste([("C1, C2", "Supported"), ("C3", "Insufficient")],
                                     [("R1-C3", "a"), ("R2-C3", "b"), ("R1-C1", "c")]), IDS)

    def test_the_rank_count_in_words_must_match(self):
        with self.assertRaises(ValueError):   # "eight" ranks, but there are two
            claim_labels.parse(paste([("C1, C2", "Supported"), ("C3", "Insufficient")], [("C3 at all eight ranks", "a")]), IDS)


ITEM_TEXT = "We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate."


class FlipReplyTest(unittest.TestCase):
    def reply(self, challenges):
        return json.dumps({"result": json.dumps({"challenges": challenges}), "is_error": False})

    def test_every_claim_must_be_challenged_once(self):
        with self.assertRaises(flip.FlipError):
            flip.parse_reply(self.reply([{"id": "R1-C1", "sentence": None, "argues_for": None, "why": "w"}]), ["R1-C1", "R1-C2"])

    def test_argues_for_must_be_a_label_or_null(self):
        with self.assertRaises(flip.FlipError):
            flip.parse_reply(self.reply([{"id": "R1-C1", "sentence": "s", "argues_for": "maybe", "why": "w"}]), ["R1-C1"])

    def test_each_sentence_is_checked_against_the_posting(self):
        challenges = flip.parse_reply(self.reply([
            {"id": "R1-C1", "sentence": "However, we aren't able to successfully sponsor visas for every role and every candidate.",
             "argues_for": "insufficient", "why": "w"},
            {"id": "R1-C2", "sentence": "We sponsor every candidate.", "argues_for": "contradicted", "why": "w"},
            {"id": "R1-C3", "sentence": None, "argues_for": None, "why": "w"}]), ["R1-C1", "R1-C2", "R1-C3"])
        checked = flip.checked(ITEM_TEXT, challenges, {"R1-C1": "supported", "R1-C2": "supported", "R1-C3": "insufficient"})
        self.assertEqual([(c["sentence_check"], c["proposes_a_change"]) for c in checked],
                         [("quote found", True), ("quote not found", False), ("no quote", False)])


class CommittedClaimLabelsTest(unittest.TestCase):
    def test_the_json_matches_the_paste_and_the_claims(self):
        pasted = ROOT / "shortlist" / "v0.1" / "claim-labels-as-pasted.tsv"
        converted = json.loads((ROOT / "shortlist" / "v0.1" / "claim-labels.json").read_text(encoding="utf-8"))
        claims_bytes = (ROOT / "shortlist" / "v0.1" / "claims.jsonl").read_bytes()
        ids = [f"R{r['rank']}-C{r['n']}" for r in map(json.loads, claims_bytes.decode("utf-8").splitlines())]
        self.assertEqual(converted["source_sha256"], hashlib.sha256(pasted.read_bytes()).hexdigest())
        self.assertEqual(converted["claims_sha256"], hashlib.sha256(claims_bytes).hexdigest())
        self.assertEqual(converted, {**converted, **claim_labels.parse(pasted.read_text(encoding="utf-8"), ids)})
        counts = [v["label"] for v in converted["labels"].values()]
        self.assertEqual((counts.count("supported"), counts.count("insufficient"), counts.count("contradicted")), (48, 16, 0))


if __name__ == "__main__":
    unittest.main()
