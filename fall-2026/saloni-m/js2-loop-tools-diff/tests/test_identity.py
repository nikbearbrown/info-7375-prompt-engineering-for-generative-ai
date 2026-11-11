"""GATE 6.3 (Saloni's words): "If two different boards return the same job ID, the agent treats
them as duplicates instead of identifying jobs using both the board name and job ID."

Written BEFORE the patch (commit JS2-3), and expected to FAIL on the JS2-2 code, which stores
the bare posting id the way JS1 did. Test data is constructed (labelled), because the real run-1
responses had 0 shared ids across the three boards.
"""
import unittest

from jsagent.loop import Loop
from tests.helpers import AS, GH, by_board, ok, run
from tests.wrong_versions import WV3BareId

BOARDS = [("greenhouse", "a"), ("greenhouse", "b"), ("ashby", "c")]


def check_same_id_on_two_boards(cls):
    """Baseline: board a has job 1001. Next run: board b posts a DIFFERENT job that also has id 1001.
    It must be reported new on board b. Returns the problems found."""
    t1 = {GH.format("a"): ok((1001, "ML Engineer")), GH.format("b"): ok((2002, "Designer")),
          AS.format("c"): ok(("u-3", "Research Engineer"))}
    _, s, _, _ = run(cls, BOARDS, t1)
    t2 = dict(t1)
    t2[GH.format("b")] = ok((2002, "Designer"), (1001, "Recruiter"))
    r, s2, _, _ = run(cls, BOARDS, t2, state=s)
    probs = []
    new_b = [n["id"] for n in by_board(r)["greenhouse:b"]["new"]]
    if new_b != ["1001"]:
        probs.append(f"board b's new job 1001 was hidden by board a's job 1001 (reported new: {new_b})")
    if by_board(r)["greenhouse:a"]["new"]:
        probs.append("board a reported a job new that it had already seen")
    # third run: nothing changed, so nothing may be new on either board
    r3, _, _, _ = run(cls, BOARDS, t2, state=s2)
    if r3["total_new"]:
        probs.append(f"third run reported {r3['total_new']} new with no change")
    return probs


class TestJobIdentity(unittest.TestCase):
    def test_same_id_on_two_boards_is_two_jobs(self):
        self.assertEqual(check_same_id_on_two_boards(Loop), [])

    def test_wv3_bare_id_is_caught(self):
        self.assertNotEqual(check_same_id_on_two_boards(WV3BareId), [])


if __name__ == "__main__":
    unittest.main()
