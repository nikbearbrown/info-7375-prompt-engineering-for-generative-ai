"""GATE.md v0.3 §6 W5, through the live path (JS2-CP8b; written before any fix).

W5, as written in GATE.md v0.3 §6:

    W5: a board whose saved state holds ids returns zero jobs, and the loop
    reports it as an ordinary empty board — "ok — 0 jobs, 0 new" — so a board
    whose jobs all vanished looks like a board that never had any, and the run
    ends a plain finished. Caught by: the test that reproduces CP7's demo
    (evidence/demo_finished_wrong_answer/) through the live path, with the
    network patched as in the other loop tests: saved state holding 59 ids for
    greenhouse:duolingo, as after run 1, and a constructed 200 response with
    zero jobs. The board's line must say "failed — empty board: 0 jobs, 59 ids
    saved before", its 59 saved ids must be unchanged, its response must be
    saved as evidence, and the run must end finished — with failures, naming
    greenhouse:duolingo.

Setup: a temporary project folder (LoopCase from test_loop.py: _send replaced
by a script keyed by URL, any socket fails the test, no seeding). Run 1's state
file, state/state_2026-11-07T000611Z.json, is copied into it unchanged; the
real state/ is only read. Duolingo's one scripted answer is a 200 whose body is
the bytes of evidence/constructed/duolingo_EMPTY_constructed_2026-11-07.json.
The run's clock starts after run 1's state file, so the run's own state file
is a later one. The four assertions are W5's four, and nothing more.
"""

import json
import shutil
from datetime import datetime, timedelta, timezone

from support import JS1 as PROJECT  # support's name for this project folder (carried over from JS1)
from test_loop import GH, LoopCase, ok

BOARD = "greenhouse:duolingo"
RUN1_STATE = "state/state_2026-11-07T000611Z.json"
EMPTY_BODY = "evidence/constructed/duolingo_EMPTY_constructed_2026-11-07.json"
START = datetime(2026, 11, 7, 12, 0, 0, tzinfo=timezone.utc)  # after run 1 (00:06:11Z)


class W5EmptyBoardWithSavedIds(LoopCase):
    boards = [(GH, "duolingo")]

    def now(self):
        moment = START + timedelta(seconds=self.calls)
        self.calls += 1
        return moment

    def test_W5_board_with_saved_ids_returning_zero_jobs_is_failed_not_empty(self):
        (self.root / "state").mkdir()
        shutil.copy(PROJECT / RUN1_STATE, self.root / RUN1_STATE)
        saved_before = json.loads((PROJECT / RUN1_STATE).read_text(encoding="utf-8"))[BOARD]
        self.assertEqual(len(saved_before), 59)  # the premise: run 1 saved 59 duolingo ids
        body = (PROJECT / EMPTY_BODY).read_bytes()
        self.on(GH, "duolingo", ok(body))

        report = self.go()

        with self.subTest("1. the board line"):
            self.assertEqual(self.line(report, BOARD)["line"], "failed — empty board: 0 jobs, 59 ids saved before")

        with self.subTest("2. the 59 saved ids are unchanged in the new state file"):
            written = report["state"]["written"]
            self.assertIsNotNone(written)
            self.assertNotEqual(written, RUN1_STATE)
            after = json.loads((self.root / written).read_text(encoding="utf-8"))
            self.assertCountEqual(after[BOARD], saved_before)

        with self.subTest("3. the response is saved as evidence, attempt 1, sidecar status 200"):
            bodies = [p for p in (self.root / "evidence").glob("greenhouse_duolingo_*_a1.json")]
            self.assertEqual(len(bodies), 1, bodies)
            self.assertEqual(bodies[0].read_bytes(), body)
            sidecar = bodies[0].with_name(bodies[0].name + ".sidecar.json")
            self.assertEqual(json.loads(sidecar.read_text(encoding="utf-8"))["status"], 200)

        with self.subTest("4. the run ends finished — with failures, naming greenhouse:duolingo"):
            self.assertEqual(report["exit"]["kind"], "finished")
            self.assertTrue(report["exit"]["line"].startswith("finished — with failures"), report["exit"]["line"])
            self.assertIn(BOARD, report["exit"]["line"])
