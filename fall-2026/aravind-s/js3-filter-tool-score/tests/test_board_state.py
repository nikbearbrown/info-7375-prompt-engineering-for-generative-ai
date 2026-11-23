"""One state file per board (GATE.md): new and gone per board, ids never removed, layer 1's state read
for the move into this format, and a state that belongs to another board refused."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from job_agent import board_state
from job_agent.errors import BrokenInput

REPO = Path(__file__).resolve().parent.parent


def posting(i, title="Software Engineer"):
    return {"id": i, "title": title}


class BoardStateTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)

    def test_no_state_means_a_baseline(self):
        self.assertIsNone(board_state.load(self.dir / "greenhouse-verkada.json", "greenhouse", "verkada"))
        self.assertTrue(board_state.diff(None, [posting("1")]).baseline)

    def test_new_and_gone_against_the_last_answer(self):
        first = board_state.next_state(None, "greenhouse", "verkada", "u", [posting("1"), posting("2")],
                                       {"run_id": "r1"}, [])
        found = board_state.diff(first, [posting("2"), posting("3")])
        self.assertEqual(([p["id"] for p in found.new], found.gone), (["3"], [("1", "Software Engineer")]))

    def test_seen_ids_are_never_removed_and_a_returning_posting_is_not_new(self):
        state = board_state.next_state(None, "lever", "palantir", "u", [posting("1")], {"run_id": "r1"}, [])
        state = board_state.next_state(state, "lever", "palantir", "u", [posting("2")], {"run_id": "r2"}, [])
        self.assertEqual(state["seen_ids"], ["1", "2"])
        self.assertEqual(board_state.diff(state, [posting("1"), posting("2")]).new, [])
        self.assertEqual([r["run_id"] for r in state["runs"]], ["r1", "r2"])

    def test_a_saved_state_reads_back_and_must_belong_to_its_board(self):
        path = self.dir / "greenhouse-verkada.json"
        state = board_state.next_state(None, "greenhouse", "verkada", "u", [posting("1")], {"run_id": "r1"}, ["1"])
        board_state.save(path, state)
        self.assertEqual(board_state.load(path, "greenhouse", "verkada"), state)
        self.assertFalse(path.with_name(path.name + ".tmp").exists())
        with self.assertRaises(BrokenInput):
            board_state.load(path, "lever", "palantir")

    def test_a_broken_state_file_is_broken_input(self):
        path = self.dir / "greenhouse-verkada.json"
        for text in ("not json", json.dumps({"schema": 1}), json.dumps({"schema": 2, "seen_ids": [1]})):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(BrokenInput):
                    board_state.load(path, "greenhouse", "verkada")

    def test_layer_1_state_is_read_as_the_openai_board(self):
        # A trimmed copy of layer 1's state/seen.json from JS1's final commit (d8b3896); the live one was moved
        # into state/ashby-openai.json by my run of 2026-11-08 with --approve.
        js1 = json.loads((REPO / "tests" / "fixtures" / "js1-state-seen-trimmed.json").read_text(encoding="utf-8"))
        path = self.dir / "seen.json"
        path.write_text(json.dumps(js1), encoding="utf-8")
        moved = board_state.load_js1(path)
        self.assertEqual((moved["schema"], moved["system"], moved["name"]), (2, "ashby", "openai"))
        self.assertEqual(set(moved["seen_ids"]), set(js1["seen_ids"]))
        self.assertEqual(moved["runs"], js1["runs"])
        self.assertEqual(moved["pending_claude"], [])

    def test_a_layer_1_file_in_another_format_is_broken_input(self):
        path = self.dir / "seen.json"
        path.write_text(json.dumps({"schema": 2}), encoding="utf-8")
        with self.assertRaises(BrokenInput):
            board_state.load_js1(path)


if __name__ == "__main__":
    unittest.main()
