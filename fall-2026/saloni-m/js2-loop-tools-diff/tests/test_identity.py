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
    def test_schema1_state_is_rebaselined_not_reported_all_new(self):
        """Added WITH the patch (not before it): a JS1-shaped state of bare ids must not make
        every saved job look new after the key change."""
        old = {"schema": 1, "boards": {"greenhouse:a": {}, "greenhouse:b": {}, "ashby:c": {}},
               "seen": ["1001", "2002", "u-3"], "runs": [{"run_id": "old"}]}
        t = {GH.format("a"): ok((1001, "ML Engineer")), GH.format("b"): ok((2002, "Designer")),
             AS.format("c"): ok(("u-3", "Research Engineer"))}
        r, s, _, loop = run(Loop, BOARDS, t, state=old)
        self.assertEqual(r["total_new"], 0)
        self.assertTrue(all(b["baseline"] for b in r["boards"]))
        self.assertEqual(s["schema"], 2)
        self.assertIn("greenhouse:b:2002", s["seen"])
        self.assertEqual(s["runs"][0], {"run_id": "old"})
        # patch v2: the event is "state_migrated"; with no saved raw, every board is re-baselined
        ev = [e for e in loop.trace if e["event"] == "state_migrated"]
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["rebaselined_boards"], ["ashby:c", "greenhouse:a", "greenhouse:b"])

    def test_same_id_on_two_boards_is_two_jobs(self):
        self.assertEqual(check_same_id_on_two_boards(Loop), [])

    def test_wv3_bare_id_is_caught(self):
        self.assertNotEqual(check_same_id_on_two_boards(WV3BareId), [])


if __name__ == "__main__":
    unittest.main()
