"""Sampling and experiment tools. Postings are CONSTRUCTED; every 'Claude reply' here is FAKE."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from jobwatch import judge, lab
from jobwatch.rule import NOT_RELEVANT, RELEVANT
from tests.helpers import RESUME, ROOT, make_posting

POSTINGS = {str(i): make_posting(i, title, "<p>Python and Redis.</p><ul><li>2+ years</li></ul>")
            for i, title in enumerate(["Software Engineer", "Senior Software Engineer", "Sales Engineer",
                                        "Account Executive", "Platform Engineer", "Recruiter"] * 5, start=100)}
SPARE = {str(i): make_posting(i, title, "<p>Python and Redis.</p>")      # pool postings select() leaves unused
         for i, title in enumerate(["Software Engineer II", "Staff Engineer", "Backend Engineer",
                                     "Data Engineer", "Platform Engineer", "Lead Engineer"], start=500)}
WITH_SPARE = {**POSTINGS, **SPARE}
PROTOCOL_TEXT = ("I label a posting RELEVANT when a new graduate backend engineer in Boston could apply today: "
                 "the title is a software or backend engineering role, it asks for at most one year of experience, "
                 "it is in Boston or US remote, and it names at least two of the persona's skills. Otherwise NOT_RELEVANT.")


def fake_claude(verdicts):
    """Returns a constructed reply per posting id: a verdict, or None for a malformed reply."""
    def caller(prompt):
        pid = json.loads(prompt.split("POSTING:\n", 1)[1])["posting_id"]
        v = verdicts.get(pid, NOT_RELEVANT)
        if v is None:
            return {"ok": True, "text": "```json\n{}\n```", "called_at": "2026-10-30T00:00:00Z", "model": "fake"}
        body = {"posting_id": pid, "verdict": v, "reason": "constructed",
                "evidence": [{"resume_field": "skills[0]", "posting_field": "content", "posting_quote": "python"}]}
        return {"ok": True, "text": json.dumps(body), "called_at": "2026-10-30T00:00:00Z", "model": "fake"}
    return caller


class Selection(unittest.TestCase):
    def test_seeded_split_is_reproducible_disjoint_and_from_the_pool(self):
        a = lab.select(POSTINGS, seed=7375)
        self.assertEqual(a, lab.select(POSTINGS, seed=7375))
        self.assertNotEqual(a["dev"], lab.select(POSTINGS, seed=1)["dev"])
        self.assertEqual((len(a["dev"]), len(a["heldout"])), (10, 10))
        self.assertFalse(set(a["dev"]) & set(a["heldout"]))
        self.assertTrue(all("ngineer" in POSTINGS[i]["title"] for i in a["dev"] + a["heldout"]))
        self.assertEqual(a["sampling"], a["dev"][:5])        # sampling never touches held-out

    def test_small_pool_is_refused(self):
        with self.assertRaises(lab.LabError):
            lab.select({k: POSTINGS[k] for k in list(POSTINGS)[:6]}, seed=1)


class Supplement(unittest.TestCase):
    def setUp(self):
        self.selection = lab.select(POSTINGS, seed=7375)
        self.supp = lab.supplement(WITH_SPARE, self.selection)

    def test_only_unused_postings_the_seniority_check_allows(self):
        used = set(self.selection["dev"] + self.selection["heldout"])
        added = self.supp["dev"] + self.supp["heldout"]
        self.assertEqual(len(set(added)), 4)
        self.assertFalse(set(added) & used)
        for i in added:
            self.assertIn(i, SPARE)
            self.assertNotRegex(WITH_SPARE[i]["title"], "Senior|Staff|Lead")
        self.assertEqual(self.supp, lab.supplement(WITH_SPARE, self.selection))      # same seed, same split

    def test_sampling_stays_dev_only_and_five_long(self):
        self.assertEqual(len(self.supp["sampling"]), 5)
        self.assertEqual(self.supp["sampling"][:2], self.supp["dev"])
        self.assertTrue(set(self.supp["sampling"]) <= set(self.supp["dev"] + self.selection["dev"]))

    def test_combined_adds_without_changing_the_original_sets_or_labels(self):
        original = {i: {"label": NOT_RELEVANT} for i in self.selection["dev"] + self.selection["heldout"]}
        before = json.dumps([self.selection, original], sort_keys=True)
        extra = {i: {"label": RELEVANT} for i in self.supp["dev"] + self.supp["heldout"]}
        sets, labels, origin = lab.combined(self.selection, original, self.supp, extra)
        self.assertEqual(json.dumps([self.selection, original], sort_keys=True), before)
        self.assertEqual(sets["dev"], self.selection["dev"] + self.supp["dev"])
        self.assertEqual(len(labels), 24)
        self.assertEqual(set(origin), set(extra))
        self.assertEqual(lab.combined(self.selection, original)[:2], (self.selection, original))  # no supplement

    def test_too_few_candidates_is_refused(self):
        everything = {"dev": [i for i in POSTINGS if "Senior" not in POSTINGS[i]["title"]], "heldout": [],
                      "seed": 1}
        with self.assertRaises(lab.LabError):
            lab.supplement(POSTINGS, everything)


class ViewAndLabel(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.protocol = self.dir / "LABELING-PROTOCOL.md"
        self.labels = self.dir / "labels.json"
        self.selection = lab.select(POSTINGS, seed=7375)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_view_shows_the_posting_but_no_verdicts(self):
        text = lab.view(POSTINGS["100"])
        self.assertIn("Software Engineer", text)
        self.assertIn("- 2+ years", text)
        for leak in ("RELEVANT", "rule", "held", "AI JUDGMENT"):
            self.assertNotIn(leak, text)

    def test_labeling_needs_a_written_protocol(self):
        with self.assertRaises(lab.LabError):
            lab.check_protocol(self.protocol)
        self.protocol.write_text("TODO: write my rule")
        with self.assertRaises(lab.LabError):
            lab.check_protocol(self.protocol)

    def test_labels_are_saved_resumable_and_tied_to_one_protocol(self):
        self.protocol.write_text(PROTOCOL_TEXT)
        answers = iter(["r", "Software title, Boston, two skills.", "x", "n", "Senior title.", "q"])
        out = lab.label_interactively(POSTINGS, self.selection, self.labels, ask=lambda _: next(answers),
                                      say=lambda _: None, protocol_path=self.protocol)
        self.assertEqual(sorted(v["label"] for v in out["labels"].values()), [NOT_RELEVANT, RELEVANT])
        again = iter(["q"])
        resumed = lab.label_interactively(POSTINGS, self.selection, self.labels, ask=lambda _: next(again),
                                          say=lambda _: None, protocol_path=self.protocol)
        self.assertEqual(len(resumed["labels"]), 2)
        self.protocol.write_text(PROTOCOL_TEXT + " Also interns.")
        with self.assertRaises(lab.LabError):
            lab.label_interactively(POSTINGS, self.selection, self.labels, ask=lambda _: "q",
                                    say=lambda _: None, protocol_path=self.protocol)


class ClaudeRuns(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.selection = lab.select(POSTINGS, seed=7375)
        ids = self.selection["dev"] + self.selection["heldout"]
        self.labels = {i: {"label": RELEVANT if POSTINGS[i]["title"] == "Software Engineer" else NOT_RELEVANT}
                       for i in ids}
        self.prompt = ROOT / "prompts" / "baseline-v1.md"

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_pass_means_valid_and_equal_to_my_label_and_invalid_counts_as_fail(self):
        dev = self.selection["dev"]
        verdicts = {i: self.labels[i]["label"] for i in dev}
        verdicts[dev[0]] = None                                     # one malformed reply
        verdicts[dev[1]] = RELEVANT if self.labels[dev[1]]["label"] == NOT_RELEVANT else NOT_RELEVANT   # one wrong
        folder = lab.experiment(POSTINGS, RESUME, self.selection, self.labels, self.prompt, "dev",
                                fake_claude(verdicts), out_root=self.dir)
        report = json.loads((folder / "results.json").read_text())
        self.assertEqual((report["passed"], report["total"], report["invalid"]), (8, 10, 1))
        self.assertEqual(sorted(p.name for p in (folder / "replies").iterdir()), sorted(f"{i}.txt" for i in dev))

    def test_results_report_original_and_supplement_separately(self):
        supp = lab.supplement(WITH_SPARE, self.selection)
        extra = {i: {"label": RELEVANT} for i in supp["dev"] + supp["heldout"]}
        sets, labels, origin = lab.combined(self.selection, self.labels, supp, extra)
        verdicts = {i: labels[i]["label"] for i in self.selection["dev"]}           # supplement answered NOT
        folder = lab.experiment(WITH_SPARE, RESUME, sets, labels, self.prompt, "dev", fake_claude(verdicts),
                                out_root=self.dir, origin=origin)
        report = json.loads((folder / "results.json").read_text())
        self.assertEqual(report["by_origin"], {"original": {"passed": 10, "total": 10},
                                               "supplement": {"passed": 0, "total": 2}})
        self.assertIn("supplement 0/2", (folder / "report.md").read_text())

    def test_heldout_needs_final_and_committed_prompts(self):
        args = (POSTINGS, RESUME, self.selection, self.labels, self.prompt, "heldout", fake_claude({}))
        with self.assertRaisesRegex(lab.LabError, "--final"):
            lab.experiment(*args, out_root=self.dir)
        with self.assertRaisesRegex(lab.LabError, "commit"):
            lab.experiment(*args, final=True, out_root=self.dir, committed=lambda p: False)
        folder = lab.experiment(*args, final=True, out_root=self.dir, committed=lambda p: True)
        self.assertIn("heldout", folder.name)

    def test_sampling_counts_spread_and_agreement_with_my_label(self):
        ids = self.selection["sampling"]
        flips = {"n": 0}

        def wobbly(prompt):
            flips["n"] += 1
            pid = json.loads(prompt.split("POSTING:\n", 1)[1])["posting_id"]
            v = RELEVANT if (pid == ids[0] and flips["n"] % 2) else NOT_RELEVANT
            return fake_claude({pid: v})(prompt)
        folder = lab.sample(POSTINGS, RESUME, ids, self.labels, self.prompt, 4, wobbly, out_root=self.dir, workers=1)
        report = json.loads((folder / "results.json").read_text())
        first = report["postings"][0]
        self.assertEqual(first["asks"], 4)
        self.assertFalse(first["unanimous"])
        self.assertEqual(len(report["calls"]), 20)
        self.assertEqual(len(list((folder / "replies").iterdir())), 20)
        self.assertIn("AI JUDGMENTS", (folder / "report.md").read_text())


if __name__ == "__main__":
    unittest.main()
