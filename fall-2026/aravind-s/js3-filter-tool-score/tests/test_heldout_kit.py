"""The fresh held-out set (tools/heldout_kit.py): 15 kept and 15 rejected postings by a written rule and a new seed,
leaving out the audit's postings, the shortlist and their same-title copies; blind cards, a sealed answer file, a blank
verdict sheet.

The draw tests use a filter run over CONSTRUCTED saved answers; the last class checks the committed set.
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
from .test_claims_kit import blank_labels
from .test_filter_run import save

spec = importlib.util.spec_from_file_location("heldout_kit", REPO / "tools" / "heldout_kit.py")
heldout_kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(heldout_kit)

RUN_ID = "2026-11-21T044414Z"
COMMITTED = REPO / "js3" / "heldout" / RUN_ID
AUDIT = REPO / "js3" / "audit" / RUN_ID / "sealed" / "answers.json"
TOPIC = "We build APIs and design SQL schemas for our backend."
VERDICT_ROW = re.compile(r"^\| \d\d \|")
HEADER = "Each shows the posting's facts only; nothing on a card says what the filter decided."
EXCLUDED = {"t-1", "t-2", "t-1-copy", "k-0", "k-0-copy", "r-0", "r-0-copy"}
LEFT_KEPT = {f"k-{i}" for i in range(1, 6)}
LEFT_REJECTED = {f"r-{i}" for i in range(1, 6)}


def card_keys(cards: str) -> list:
    return re.findall(r"^- Board: (\S+)\n- Posting id: `([^`]+)`", cards, re.M)


class HeldoutKitTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="job-agent-heldout-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        runs, boards = self.root / "runs", self.root / "boards.json"
        boards.write_text(json.dumps({"boards": [{"system": "ashby", "name": "acme"}]}), encoding="utf-8")
        jobs = [ashby_job("t-1", title="Software Engineer, Top 1", descriptionPlain=TOPIC),
                ashby_job("t-2", title="Software Engineer, Top 2", descriptionPlain=TOPIC),
                ashby_job("t-1-copy", title="Software Engineer, Top 1", descriptionPlain=TOPIC),
                ashby_job("k-0-copy", title="Software Engineer, Team 0"),
                ashby_job("r-0-copy", title="Senior Software Engineer, Team 0"),
                ashby_job("c-1", title="")]
        jobs += [ashby_job(f"k-{i}", title=f"Software Engineer, Team {i}") for i in range(6)]  # kept, score 50
        jobs += [ashby_job(f"r-{i}", title=f"Senior Software Engineer, Team {i}") for i in range(6)]  # rejected (R3)
        save(runs, "2026-11-02T000000Z", "ashby-acme", body("ashby", jobs))
        clock = lambda: datetime(2026, 11, 21, 8, 0, 0, tzinfo=timezone.utc)  # noqa: E731
        self.run = filter_run.run(runs_root=runs, boards_path=boards, out_root=self.root / "runs-out", now=clock,
                                      rules_version="1.0")
        self.audit = self.root / "answers.json"
        self.audit.write_text(json.dumps({"answers": [{"board": "ashby-acme", "id": "k-0", "fate": "kept"},
                                                      {"board": "ashby-acme", "id": "r-0", "fate": "rejected"}]}),
                              encoding="utf-8")

    def build(self, seed=11, n_kept=3, n_rejected=3, audit=None):
        out_root = self.root / f"heldout-{seed}-{len(list(self.root.iterdir()))}"
        return heldout_kit.build(self.run["out"], out_root, audit or self.audit, seed, n_kept, n_rejected)

    def answers(self, out):
        return json.loads((out / "sealed" / "answers.json").read_text(encoding="utf-8"))["answers"]

    def test_the_shortlist_is_the_one_the_test_expects(self):
        self.assertEqual([r["id"] for r in self.run["shortlist"]["top"]], ["t-1", "t-2"])

    def test_the_draw_leaves_out_the_audit_the_shortlist_and_their_copies(self):
        answers = self.answers(self.build())
        ids = [a["id"] for a in answers]
        self.assertEqual(len(ids), len(set(ids)))  # nobody drawn twice
        self.assertFalse(EXCLUDED & set(ids))
        self.assertNotIn("c-1", ids)  # "I cannot tell" is in neither pool
        kept = [a for a in answers if a["pool"] == "random kept"]
        rejected = [a for a in answers if a["pool"] == "random rejected"]
        self.assertEqual((len(kept), len(rejected)), (3, 3))
        self.assertTrue(all(a["fate"] == "kept" for a in kept) and all(a["fate"] == "rejected" for a in rejected))

    def test_whole_pools_draw_exactly_what_is_left(self):
        ids = {a["id"] for a in self.answers(self.build(n_kept=5, n_rejected=5))}
        self.assertEqual(ids, LEFT_KEPT | LEFT_REJECTED)

    def test_the_same_seed_gives_the_same_set(self):
        first, second = self.build(11), self.build(11)
        for name in ("CARDS.md", "VERDICTS.md", "README.md", "INSTRUCTIONS.md", "sealed/answers.json"):
            self.assertEqual((first / name).read_bytes(), (second / name).read_bytes(), name)

    def test_the_cards_and_the_sheet_leak_nothing_and_the_hash_is_in_the_readme(self):
        out = self.build()
        cards = (out / "CARDS.md").read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"^## Card \d\d$", cards, re.M)), 6)
        for word in ("Fate", "fate", "Score", "score", "Deciding", "rejected", "kept", "random", "pool", "Pool"):
            self.assertNotIn(word, cards.replace(HEADER, ""))
        rows = [line for line in (out / "VERDICTS.md").read_text(encoding="utf-8").splitlines()
                if VERDICT_ROW.match(line)]
        self.assertEqual(rows, [f"| {n:02} | | |" for n in range(1, 7)])
        digest = hashlib.sha256((out / "sealed" / "answers.json").read_bytes()).hexdigest()
        self.assertIn(f"`{digest}`", (out / "README.md").read_text(encoding="utf-8"))

    def test_a_pool_too_small_a_missing_audit_and_a_second_build_are_refused(self):
        with self.assertRaises(SystemExit):
            self.build(n_kept=6)
        with self.assertRaises(SystemExit):
            self.build(audit=self.root / "no-such-answers.json")
        out_root = self.root / "heldout-once"
        heldout_kit.build(self.run["out"], out_root, self.audit, 11, 3, 3)
        with self.assertRaises(SystemExit):
            heldout_kit.build(self.run["out"], out_root, self.audit, 11, 3, 3)


@unittest.skipUnless(COMMITTED.exists(), "the committed held-out set is not in this copy of the repo")
class CommittedHeldoutKitTest(unittest.TestCase):
    """The committed set is what its recorded seed rebuilds, its hash is in its README, and its cards leak nothing."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="job-agent-heldout-committed-"))
        readme = (COMMITTED / "README.md").read_text(encoding="utf-8")
        cls.seed = int(re.search(r"Seed \*\*(\d+)\*\*", readme).group(1))
        cls.run_dir = REPO / "js3" / "filter-run" / RUN_ID
        cls.fresh = heldout_kit.build(cls.run_dir, cls.tmp, AUDIT, cls.seed)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_the_committed_set_rebuilds_from_its_seed(self):
        self.assertNotEqual(self.seed, 20261121)  # a new seed, not the audit's
        for name in ("CARDS.md", "README.md", "INSTRUCTIONS.md", "sealed/answers.json"):
            self.assertEqual((self.fresh / name).read_bytes(), (COMMITTED / name).read_bytes(), name)
        fresh, committed = [blank_labels((d / "VERDICTS.md").read_text(encoding="utf-8"), VERDICT_ROW, 1)
                            for d in (self.fresh, COMMITTED)]
        self.assertEqual(fresh, committed)  # the same sheet, whatever verdicts Aravind has written into it since

    def test_the_sealed_files_hash_is_in_the_readme(self):
        digest = hashlib.sha256((COMMITTED / "sealed" / "answers.json").read_bytes()).hexdigest()
        self.assertIn(f"`{digest}`", (COMMITTED / "README.md").read_text(encoding="utf-8"))

    def test_no_audit_or_shortlisted_posting_or_copy_of_one_is_on_a_card(self):
        data = json.loads((self.run_dir / "verdicts.json").read_text(encoding="utf-8"))
        audit = {(a["board"], a["id"]) for a in json.loads(AUDIT.read_text(encoding="utf-8"))["answers"]}
        short = {(k["board"], k["id"]) for k in data["shortlist"]}
        self.assertEqual((len(audit), len(short)), (55, 10))
        keys = card_keys((COMMITTED / "CARDS.md").read_text(encoding="utf-8"))
        self.assertEqual((len(keys), len(set(keys))), (30, 30))
        self.assertFalse(set(keys) & heldout_kit.left_out(data["records"], audit | short))
        answers = json.loads((self.fresh / "sealed" / "answers.json").read_text(encoding="utf-8"))["answers"]
        pools = [(a["pool"], a["fate"]) for a in answers]
        self.assertEqual(sorted(set(pools)), [("random kept", "kept"), ("random rejected", "rejected")])
        self.assertEqual(sum(1 for p, _ in pools if p == "random kept"), 15)

    def test_no_card_shows_what_the_filter_decided(self):
        cards = (COMMITTED / "CARDS.md").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^## Card (\d\d)$", cards, re.M), [f"{n:02}" for n in range(1, 31)])
        self.assertIsNone(re.search(r"(?m)^- (Fate|Score|Pool|Group|Deciding|Rule)\b", cards))
        for word in ("random kept", "random rejected", "deciding_rule", "failed_rules"):
            self.assertNotIn(word, cards)


if __name__ == "__main__":
    unittest.main()
