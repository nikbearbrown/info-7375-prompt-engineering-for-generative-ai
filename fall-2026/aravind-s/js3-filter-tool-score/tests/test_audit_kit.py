"""The reject audit's kit (tools/audit_kit.py): a seeded sample by the written rule, blind cards, a sealed answer file.

Built from a filter run over CONSTRUCTED saved answers in a temporary folder.
"""

import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from job_agent import filter_run

from .loop_helpers import REPO, ashby_job, body
from .test_filter_run import save

spec = importlib.util.spec_from_file_location("audit_kit", REPO / "tools" / "audit_kit.py")
audit_kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_kit)

TOPIC = "We build APIs and design SQL schemas for our backend."
SIZES = {"n_random": 3, "n_close_kept": 1, "n_close_rejected": 2, "n_kept": 1}


class AuditKitTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-audit-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        runs = self.root / "runs"
        boards = self.root / "boards.json"
        boards.write_text(json.dumps({"boards": [{"system": "ashby", "name": "acme"}]}), encoding="utf-8")
        jobs = [ashby_job(f"k-{i}", title=f"Software Engineer, Team {i}", descriptionPlain=TOPIC) for i in range(4)]
        jobs += [ashby_job("k-near", title="Software Engineer, Near", descriptionPlain="We build APIs.")]
        jobs += [ashby_job(f"s-{i}", title=f"Senior Software Engineer, Team {i}", descriptionPlain=TOPIC)
                 for i in range(4)]
        jobs += [ashby_job("y-1", title="Software Engineer, Years", descriptionPlain="5+ years of experience. " + TOPIC)]
        save(runs, "2026-11-02T000000Z", "ashby-acme", body("ashby", jobs))
        clock = lambda: datetime(2026, 11, 21, 6, 0, 0, tzinfo=timezone.utc)  # noqa: E731
        self.run = filter_run.run(runs_root=runs, boards_path=boards, out_root=self.root / "runs-out", now=clock,
                                      rules_version="1.0")

    def build(self, seed=7):
        return audit_kit.build(self.run["out"], self.root / f"audit-{seed}-{len(list(self.root.iterdir()))}", seed,
                               **SIZES)

    def test_the_kit_holds_blind_cards_a_sheet_and_a_sealed_answer_file(self):
        out = self.build()
        answers = json.loads((out / "sealed" / "answers.json").read_text())["answers"]
        cards = (out / "CARDS.md").read_text()
        self.assertEqual(len(re.findall(r"^## Card \d\d$", cards, re.M)), len(answers))
        self.assertEqual(len(re.findall(r"^\| \d\d \| \| \|$", (out / "VERDICTS.md").read_text(), re.M)), len(answers))
        for word in ("Fate", "fate:", "Score", "score:", "Deciding", "rejected", "kept"):
            self.assertNotIn(word, cards.replace("Each shows the posting's facts only; nothing on a card says what "
                                                 "the filter decided.", ""))
        digest = hashlib.sha256((out / "sealed" / "answers.json").read_bytes()).hexdigest()
        self.assertIn(digest, (out / "SAMPLE.md").read_text())

    def test_the_groups_follow_the_written_rule(self):
        answers = json.loads((self.build() / "sealed" / "answers.json").read_text())["answers"]
        groups = {}
        for a in answers:
            groups.setdefault(a["group"], []).append(a)
        self.assertTrue(all(a["fate"] == "rejected" for a in groups["random reject"]))
        self.assertEqual(len(groups["random reject"]), 3)
        self.assertTrue(all(a["score"] in (55, 60) for a in groups["close call: kept near the cutoff"]))
        self.assertTrue(all(len(a["failed_rules"]) == 1 for a in groups.get("close call: failed one rule", [])))
        self.assertEqual(len({(a["board"], a["id"]) for a in answers}), len(answers))  # nobody drawn twice

    def test_the_same_seed_gives_the_same_sample(self):
        first = json.loads((self.build(7) / "sealed" / "answers.json").read_text())["answers"]
        second = json.loads((self.build(7) / "sealed" / "answers.json").read_text())["answers"]
        self.assertEqual(first, second)

    def test_topic_sentences_show_on_every_card_so_they_reveal_nothing(self):
        out = self.build()
        answers = json.loads((out / "sealed" / "answers.json").read_text())["answers"]
        cards = (out / "CARDS.md").read_text().split("## Card ")[1:]
        rejected = [a["card"] for a in answers if a["fate"] == "rejected"]
        self.assertTrue(rejected)
        for n in rejected:
            self.assertIn("(APIs)", cards[n - 1])


class CardKeepsStatusLinesTest(unittest.TestCase):
    """2026-11-22: the filter's splitter cut "U.S. Person Required" at "U.S.", so audit card 17 showed no status line
    although R5 had read one. A card must show, whole, every line R5's phrases match."""

    def test_status_lines_cut_at_us_are_shown_whole(self):
        from job_agent import filter as flt
        posting = {"id": "p1", "title": "Software Engineer", "jobUrl": "https://example.test/p1",
                   "location": "New York, NY", "employmentType": "FullTime", "publishedAt": "2026-11-20",
                   "descriptionPlain": "What We Require\nU.S. Person Required\nMust be graduating in Spring 2027\n"
                                       "To comply with a U.S. government contract, applicants must be U.S. citizens."}
        text = audit_kit.card(1, posting, "lever-test", flt.load_rules())
        status = text.split("**Sentences about status, sponsorship or clearance:**")[1].split("**Sentences with")[0]
        self.assertIn("- U.S. Person Required", status)
        self.assertIn("applicants must be U.S. citizens.", status)
        self.assertNotIn("- none", status)


if __name__ == "__main__":
    unittest.main()
