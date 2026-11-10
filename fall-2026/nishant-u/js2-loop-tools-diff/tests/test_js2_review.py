"""Review-packet regression test, written 2026-11-10 BEFORE the patch, from GATE.md's amendment
"before the review-packet patch". Fakes and CONSTRUCTED bodies only; no network.

Defect reproduced live in out/demo/runs/2026-11-10-2 (FINISHED-WRONG.md): Greenhouse poshmark
returned HTTP 200 with {"jobs":[],"meta":{"total":0}}; the run ended `finished` and report.md said
"0 postings, 0 new".

Two prior states, mirroring the two live demo runs:
  seen   the board is already in the state (as after run 2026-11-10-1): the defect prints "0 new"
  fresh  the board has never been seen (as before run 2026-11-10-1): the defect prints "baseline"
         and records the empty board in state as seen
"""
import json
import tempfile
import unittest
from pathlib import Path

from tests import helpers, js2_helpers as h

EMPTY = b'{"jobs":[],"meta":{"total":0}}'


class EmptyBoardRun(helpers.ContractTest):
    modules = ("agent2.loop", "agent2.policy")
    prior_boards = ()

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        policy = self.policy.Policy(self.out)
        # Prior state (constructed): faire seen with posting 1, plus the boards this case names.
        policy.update_state("state/seen_ids.json", ["greenhouse:faire:1"], boards=self.prior_boards)
        state_path = self.out / "state" / "seen_ids.json"
        self.state_before = json.loads(state_path.read_text(encoding="utf-8"))
        boards = [h.board("greenhouse", "faire"), h.board("greenhouse", "poshmark")]
        responses = {boards[0]["url"]: [(200, h.gh_body([h.gh_job(1), h.gh_job(2)]))],
                     boards[1]["url"]: [(200, EMPTY)]}
        clock = h.FakeClock()
        self.report = self.loop.Loop(boards, policy=policy, client=h.FakeClient(responses),
                                     clock=clock, sleep=clock.sleep).run()
        self.state_after = json.loads(state_path.read_text(encoding="utf-8"))
        self.md = (self.out / "runs" / self.report["run"] / "report.md").read_text(encoding="utf-8")

    def entry(self, board):
        return next(b for b in self.report["boards"] if (b["system"], b["board"]) == ("greenhouse", board))

    def poshmark_state(self, state):
        return ("greenhouse:poshmark" in state["boards"],
                sorted(i for i in state["seen_ids"] if i.startswith("greenhouse:poshmark:")))

    def assert_unverified_empty(self):
        self.assertEqual(self.report["exit"], "incomplete")
        empty = self.entry("poshmark")
        self.assertEqual(empty["status"], "unverified-empty")
        self.assertIsNone(empty["new_ids"], "an empty board's new ids are unknown, not []")
        self.assertNotIn("0 new", self.md)
        self.assertEqual(self.poshmark_state(self.state_after), self.poshmark_state(self.state_before),
                         "the empty board must not change the state")


class SeenEmptyBoard(EmptyBoardRun):
    prior_boards = ("greenhouse:faire", "greenhouse:poshmark")

    def test_seen_empty_board_is_unverified_empty_not_0_new(self):
        self.assert_unverified_empty()

    def test_control_board_with_postings_reports_normally(self):
        faire = self.entry("faire")
        self.assertEqual((faire["status"], faire["postings"], faire["baseline"]), ("parsed", 2, False))
        self.assertEqual(faire["new_ids"], ["greenhouse:faire:2"])
        self.assertIn("`greenhouse:faire` — parsed, HTTP 200, 2 postings, 1 new", self.md)
        self.assertEqual(self.state_after["seen_ids"], ["greenhouse:faire:1", "greenhouse:faire:2"])


class FreshEmptyBoard(EmptyBoardRun):
    prior_boards = ("greenhouse:faire",)

    def test_fresh_empty_board_is_unverified_empty_and_not_recorded_as_seen(self):
        self.assert_unverified_empty()


if __name__ == "__main__":
    unittest.main()
