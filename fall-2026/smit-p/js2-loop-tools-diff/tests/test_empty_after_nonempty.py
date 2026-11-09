"""GATE.md wrong version W1: an empty board after a non-empty baseline must not be "no news".

Written before the patch (see REVIEW_PACKET.md). Expected per GATE.md's error policy:
status suspect:empty_after_nonempty, the run is incomplete rather than finished, a NEEDS
HUMAN line names the board, and the old baseline is kept so the next good run does not
report every old posting as new.
"""

import unittest

from agent import loop
from tests.test_loop import BOARDS, GH, LoopCase, gh_body


class EmptyAfterNonEmpty(LoopCase):
    def vanish(self):
        self.go(self.healthy(a=("1", "2", "3")))
        script = self.healthy()
        script[GH.format("a")] = [(200, gh_body([]))]
        return self.go(script)

    def test_W1_run_is_not_finished(self):
        s = self.vanish()
        self.assertEqual((s["exit"], s["exit_code"]), ("incomplete", 2))

    def test_W1_board_flagged_suspect(self):
        a = self.board(self.vanish(), "a")
        self.assertEqual(a["status"], "suspect:empty_after_nonempty")
        self.assertEqual(a["previous_count"], 3)

    def test_W1_untrusted_zero_is_not_reported_as_count(self):
        # Added in the revise step: GATE.md's Exits table says a suspect board reports
        # count null; the observed zero is kept separately so nothing is hidden.
        a = self.board(self.vanish(), "a")
        self.assertEqual((a["count"], a["observed_count"]), (None, 0))

    def test_W1_escalated_to_human(self):
        s = self.vanish()
        self.assertTrue(any(line.startswith("a: suspect:empty_after_nonempty")
                            for line in s["needs_human"]), s["needs_human"])

    def test_W1_baseline_kept(self):
        self.vanish()
        self.assertEqual(loop.load_state(self.base, "a", self.state_dir)["ids"], ["1", "2", "3"])

    def test_W1_next_good_run_reports_nothing_old_as_new(self):
        self.vanish()
        s = self.go(self.healthy(a=("1", "2", "3")))
        self.assertEqual(self.board(s, "a")["new_ids"], [])

    def test_empty_first_observation_is_still_ok(self):
        # No baseline to contradict: an empty first board is recorded as observed, not suspect.
        script = self.healthy()
        script[GH.format("a")] = [(200, gh_body([]))]
        s = self.go(script)
        self.assertEqual((self.board(s, "a")["status"], s["exit"]), ("ok", "finished"))

    def test_shrinking_but_nonempty_board_is_ok(self):
        self.go(self.healthy(a=("1", "2", "3")))
        s = self.go(self.healthy(a=("1",)))
        self.assertEqual((self.board(s, "a")["status"], s["exit"]), ("ok", "finished"))


if __name__ == "__main__":
    unittest.main()
