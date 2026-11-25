"""The fresh blind set for FILTER.md v1.1 (tools/fresh_kit.py) and its scorer (tools/score_fresh.py).

The kit is rebuilt once from the committed filter runs into a temporary folder: every card meets its stratum's rule,
nothing already shown to Aravind is drawn, no job appears twice, the cards say nothing about the filter, the published
hash is the sealed file's, and the committed kit is byte for byte the rebuilt one. The scorer is checked on copies of
the rebuilt kit with made-up verdicts, never on the committed one.
"""

import collections
import hashlib
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from job_agent import filter as flt

from .loop_helpers import REPO


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fresh_kit = load("fresh_kit")
score_fresh = load("score_fresh")
chat_cards = load("chat_cards")
BUILT = {}


def setUpModule():
    """One rebuild for the whole file: judging the 1,509 saved postings three times takes about ten seconds."""
    BUILT["root"] = Path(tempfile.mkdtemp(prefix="job-agent-fresh-"))
    BUILT["out"] = fresh_kit.build(BUILT["root"] / "built")


def tearDownModule():
    shutil.rmtree(BUILT["root"], ignore_errors=True)

RUN_ID = "2026-11-22T084738Z"
RUN10 = "2026-11-21T044414Z"
COMMITTED = REPO / "js3" / "fresh" / RUN_ID
KIT_FILES = ("sealed/answers.json", "CARDS.md", "README.md", "PREDICTIONS.md", "INSTRUCTIONS.md")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def card_keys(cards: str) -> list:
    return re.findall(r"^- Board: (\S+)\n- Posting id: `([^`]+)`", cards, re.M)


class FreshKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = BUILT["out"]
        cls.answers = read_json(cls.out / "sealed" / "answers.json")["answers"]
        cls.cards = (cls.out / "CARDS.md").read_text(encoding="utf-8")

    def test_the_strata_have_the_sizes_the_rule_gives(self):
        self.assertEqual(collections.Counter(a["stratum"] for a in self.answers), {"A": 12, "B": 3, "C": 3, "D": 2})
        self.assertEqual([a["card"] for a in self.answers], list(range(1, 21)))

    def test_every_card_meets_its_strata_rule(self):
        for a in self.answers:
            with self.subTest(card=a["card"]):
                if a["stratum"] == "A":
                    self.assertTrue(a["recommended_v11"] and not a["recommended_v10"])
                elif a["stratum"] == "B":
                    self.assertEqual(a["fate"], "kept")
                    self.assertTrue(a["cautions"])
                    self.assertTrue(a["recommended_without_penalty"] and not a["recommended_v11"])
                elif a["stratum"] == "C":
                    self.assertTrue(a["recommended_v10"] and a["recommended_v11"])
                else:
                    self.assertEqual(a["fate"], "rejected")
                    self.assertEqual(len(a["failed_rules"]), 1)

    def test_nothing_already_shown_and_no_copy_of_it_is_drawn(self):
        mcp_client = (REPO / "tools" / "mcp_client.py").read_text(encoding="utf-8")
        for board, pid in fresh_kit.MCP_POSTINGS:  # the same two postings the MCP client scores
            self.assertIn(f'("{board}", "{pid}")', mcp_client)
        shown = set(fresh_kit.MCP_POSTINGS)
        for kit in ("audit", "heldout"):
            shown |= {(a["board"], a["id"])
                      for a in read_json(REPO / "js3" / kit / RUN10 / "sealed" / "answers.json")["answers"]}
        records = []
        for run in (RUN_ID, RUN10):
            data = read_json(REPO / "js3" / "filter-run" / run / "verdicts.json")
            shown |= {(k["board"], k["id"]) for k in data["shortlist"]}
            records = data["records"]
        titles = {(r["board"], flt.normalized_title(r["title"])) for r in records if (r["board"], r["id"]) in shown}
        for a in self.answers:
            self.assertNotIn((a["board"], a["id"]), shown)
            self.assertNotIn((a["board"], flt.normalized_title(a["title"])), titles)

    def test_no_job_appears_twice(self):
        jobs = [(a["board"], flt.normalized_title(a["title"])) for a in self.answers]
        self.assertEqual(len(jobs), len(set(jobs)))

    def test_the_cards_are_in_the_sealed_order_and_say_nothing_about_the_filter(self):
        self.assertEqual(card_keys(self.cards), [(a["board"], a["id"]) for a in self.answers])
        for word in ("stratum", "Stratum", "recommended", *fresh_kit.NAMES.values(), "score_v1", "penalty"):
            self.assertNotIn(word, self.cards)

    def test_the_published_hash_is_the_sealed_files(self):
        digest = hashlib.sha256((self.out / "sealed" / "answers.json").read_bytes()).hexdigest()
        self.assertIn(f"`{digest}`", (self.out / "README.md").read_text(encoding="utf-8"))

    def test_the_verdict_sheet_is_blank_with_one_row_per_card(self):
        rows = [line for line in (self.out / "VERDICTS.md").read_text(encoding="utf-8").splitlines()
                if re.match(r"^\| \d\d \|", line)]
        self.assertEqual(rows, [f"| {n:02} | | |" for n in range(1, 21)])

    def test_a_second_build_in_the_same_place_is_refused(self):
        with self.assertRaises(SystemExit):
            fresh_kit.build(BUILT["root"] / "built")

    @unittest.skipUnless(COMMITTED.exists(), "the fresh set is not committed yet")
    def test_the_chat_view_is_made_from_the_cards_alone(self):
        cards = (COMMITTED / "CARDS.md").read_text(encoding="utf-8")
        view = (COMMITTED / "CHAT-CARDS.md").read_text(encoding="utf-8")
        self.assertEqual(view, chat_cards.render(cards))
        self.assertEqual(re.findall(r"^\*\*(\d\d)\. ", view, re.M), [f"{n:02}" for n in range(1, 21)])
        for a in self.answers:  # no answer field reaches the view
            self.assertNotIn(a["stratum_name"], view)

    def test_build_systems_moves_no_recommendation(self):
        self.assertIn("No posting's v1.1 recommendation changes with \"build systems\" back",
                      (self.out / "README.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(COMMITTED.exists(), "the fresh set is not committed yet")
    def test_the_committed_kit_is_byte_for_byte_the_rebuilt_one(self):
        for name in KIT_FILES:
            with self.subTest(file=name):
                self.assertEqual((COMMITTED / name).read_bytes(), (self.out / name).read_bytes())
        sheet = (COMMITTED / "VERDICTS.md").read_text(encoding="utf-8").splitlines()
        blank = (self.out / "VERDICTS.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(sheet[:6], blank[:6])  # the same heading, instructions and table head
        self.assertEqual([line[:6] for line in sheet if re.match(r"^\| \d\d \|", line)],
                         [line[:6] for line in blank if re.match(r"^\| \d\d \|", line)])


class ScoreFreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = BUILT["root"]
        cls.built = BUILT["out"]
        cls.answers = read_json(cls.built / "sealed" / "answers.json")["answers"]

    def kit(self, verdict_of):
        kit = Path(tempfile.mkdtemp(prefix="kit-", dir=self.root)) / RUN_ID
        shutil.copytree(self.built, kit)
        sheet = [line for line in (kit / "VERDICTS.md").read_text(encoding="utf-8").splitlines()
                 if not re.match(r"^\| \d\d \|", line)]
        sheet += [f"| {a['card']:02} | {verdict_of(a)} | made up for the test |" for a in self.answers
                  if verdict_of(a)]
        (kit / "VERDICTS.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
        return kit

    @staticmethod
    def expected(a):
        return {"A": "Keep", "B": "?", "C": "Keep", "D": "Reject"}[a["stratum"]]

    def test_the_predicted_verdicts_hold_every_prediction(self):
        s = score_fresh.score(self.kit(self.expected), require_committed=False)
        self.assertEqual(s["predictions"], {"A": "held", "B": "held", "controls": "held", "controls_off": 0})
        t = s["tally"]
        self.assertEqual((t["A"]["v1.1"], t["A"]["v1.0"], t["A"]["judged"]), (12, 0, 12))
        self.assertEqual((t["all"]["judged"], t["all"]["v1.1"], t["all"]["v1.0"]), (17, 17, 5))
        self.assertEqual(t["B"]["?"], 3)
        self.assertEqual(s["bound_A"], score_fresh.upper_bound(0, 12))

    def test_keeping_everything_breaks_the_penalty_and_control_predictions(self):
        s = score_fresh.score(self.kit(lambda a: "Keep"), require_committed=False)
        self.assertEqual(s["predictions"], {"A": "held", "B": "not held", "controls": "not held", "controls_off": 2})
        self.assertEqual(s["tally"]["B"]["v1.1 without the penalty"], 3)
        self.assertEqual(s["tally"]["B"]["v1.1"], 0)

    def test_more_rejects_than_keeps_on_a_is_not_held(self):
        s = score_fresh.score(self.kit(lambda a: "Reject" if a["stratum"] == "A" else self.expected(a)),
                              require_committed=False)
        self.assertEqual(s["predictions"]["A"], "not held")
        self.assertEqual((s["tally"]["A"]["v1.0"], s["tally"]["A"]["v1.1"]), (12, 0))

    def test_a_changed_answer_file_is_refused(self):
        kit = self.kit(self.expected)
        path = kit / "sealed" / "answers.json"
        path.write_text(path.read_text(encoding="utf-8").replace('"stratum": "A"', '"stratum": "C"', 1),
                        encoding="utf-8")
        with self.assertRaises(SystemExit):
            score_fresh.score(kit, require_committed=False)

    def test_a_missing_verdict_is_refused(self):
        with self.assertRaises(SystemExit):
            score_fresh.score(self.kit(lambda a: None if a["card"] == 7 else "Keep"), require_committed=False)

    def test_verdicts_that_are_not_committed_are_refused(self):
        with self.assertRaises(SystemExit):
            score_fresh.score(self.kit(self.expected))  # a temporary folder is in no git repository

    def test_the_results_are_the_same_bytes_twice(self):
        kit = self.kit(self.expected)
        first = score_fresh.write_results(kit, score_fresh.score(kit, require_committed=False))
        second = score_fresh.write_results(kit, score_fresh.score(kit, require_committed=False))
        self.assertEqual(first, second)
        self.assertEqual((kit / "RESULTS.md").read_text(encoding="utf-8"), first)

    def test_checks_after_the_reveal_are_reported_beside_the_frozen_result(self):
        kit = self.kit(self.expected)
        b = next(a["card"] for a in self.answers if a["stratum"] == "B")
        (kit / "AFTER-REVEAL.md").write_text(
            f"| {b:02} | Reject | 2026-11-25 | asked after the reveal | made up for the test |\n", encoding="utf-8")
        s = score_fresh.score(kit, require_committed=False)
        self.assertEqual(s["tally"]["B"]["?"], 3)  # the frozen result is unchanged
        self.assertEqual(s["after"]["tally"]["B"]["Reject"], 1)
        self.assertEqual(s["after"]["predictions"]["B"], "held")  # 2 of 3 still ?
        self.assertIn("## With the checks asked after the reveal", score_fresh.write_results(kit, s))


if __name__ == "__main__":
    unittest.main()
