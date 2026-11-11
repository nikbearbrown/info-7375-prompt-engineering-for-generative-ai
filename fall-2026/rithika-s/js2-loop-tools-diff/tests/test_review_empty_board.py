"""Review-packet test, written BEFORE the patch (2026-11-10).

Reproduces the finished-wrong-answer defect from the SEEDED demo:
a board with postings in saved state returns 200 with zero postings,
and the agent reports `finished` with 0 new. GATE.md error-policy log
(2026-11-10) says this must be a failed board instead.
Drafted with Claude (chat); reviewed and run by me.
"""
import unittest

import js2_harness as h
from agent import loop
from test_loop import LoopCase


class EmptyAfterNonemptyReviewTests(LoopCase):

    def test_review_board_with_postings_before_now_empty_is_failed(self):
        root = self.root(boards=[h.BOARDS[0]])
        h.write_state(root, "scaleai", [1, 2, 3])
        before = h.state_path(root, "scaleai").read_bytes()
        fake = h.FakeTransport({h.SCALE: [h.ok(h.gh_body([]))]})

        exit_name, _ = h.run(root, fake)

        self.assertEqual(exit_name, loop.INCOMPLETE)
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual(b["reason"], "empty_after_nonempty")
        self.assertIsNone(b["new"])                       # unknown, never 0
        self.assertEqual(h.state_path(root, "scaleai").read_bytes(), before)
        self.assertEqual(len(fake.calls), 1)              # not retried

    def test_review_first_run_empty_board_is_still_valid(self):
        # Guards against over-fixing: no saved state means zero is believable.
        root = self.root(boards=[h.BOARDS[0]])
        fake = h.FakeTransport({h.SCALE: [h.ok(h.gh_body([]))]})

        exit_name, _ = h.run(root, fake)

        self.assertEqual(exit_name, loop.FINISHED)
        b = h.board(h.summary(root), "scaleai")
        self.assertEqual(b["new"], 0)


if __name__ == "__main__":
    unittest.main()
