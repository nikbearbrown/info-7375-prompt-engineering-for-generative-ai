"""The watch state (GATE.md 'Repeat rule' and 'Error policy').

History is kept per board (ATS + slug) and posting key. The first usable snapshot of
a board is its baseline. Later, a key is new only if it was never saved for that
board, even if its title changed or it disappeared and came back. A damaged state
file is an error, never a silent fresh start."""

import copy
import json
import unittest

from jobwatch import state
from jobwatch.errors import StateError
from jobwatch.files import Files
from jobwatch.policy import Approval, Policy
from tests.fakes import Project


def two_board_state():
    return {
        "schema": "jobwatch-state/2",
        "boards": {
            "greenhouse/anthropic": {"ats": "greenhouse", "slug": "anthropic",
                                     "first_snapshot_run": "R1", "last_snapshot_run": "R2",
                                     "seen": {"101": "R1", "102": "R2"}},
            "greenhouse/databricks": {"ats": "greenhouse", "slug": "databricks",
                                      "first_snapshot_run": "R1", "last_snapshot_run": "R1",
                                      "seen": {"202": "R1"}},
        },
        "runs": [],
    }


class LoadTest(unittest.TestCase):
    def setUp(self):
        self.project = Project()
        self.addCleanup(self.project.cleanup)
        self.files = Files(Policy(self.project.root, "R3", set(), None))

    def write_state(self, text):
        self.project.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.project.state_path.write_text(text, encoding="utf-8")

    def test_no_state_file_means_no_history(self):
        self.assertIsNone(state.load_state(self.files))

    def test_a_valid_state_loads(self):
        self.write_state(json.dumps(two_board_state()))
        self.assertEqual(state.load_state(self.files), two_board_state())

    def test_unparseable_state_is_an_error(self):
        self.write_state('{"schema": "jobwatch-state/2", "boards": {')
        with self.assertRaises(StateError):
            state.load_state(self.files)

    def test_a_js1_state_file_is_not_silently_accepted(self):
        self.write_state(json.dumps({"schema": "jobwatch-state/1", "board": "anthropic", "endpoint": "x",
                                     "seen_ids": [1], "runs": []}))
        with self.assertRaises(StateError):
            state.load_state(self.files)

    def test_damaged_history_is_an_error(self):
        bad_key = two_board_state()
        bad_key["boards"]["greenhouse/anthropic"]["seen"] = {"101": 1}
        wrong_name = two_board_state()
        wrong_name["boards"]["greenhouse/anthropic"]["slug"] = "databricks"
        extra_field = two_board_state()
        extra_field["note"] = "?"
        for data in (bad_key, wrong_name, extra_field):
            with self.subTest(data=data):
                self.write_state(json.dumps(data))
                with self.assertRaises(StateError):
                    state.load_state(self.files)


class NewKeysTest(unittest.TestCase):
    def test_a_board_with_no_saved_snapshot_is_a_baseline(self):
        self.assertIsNone(state.new_keys(two_board_state(), "ashby/linear", ["u1", "u2"]))
        self.assertIsNone(state.new_keys(None, "greenhouse/anthropic", ["101"]))

    def test_new_keys_are_those_never_saved_for_that_board_in_response_order(self):
        self.assertEqual(state.new_keys(two_board_state(), "greenhouse/anthropic", ["900", "101", "800"]),
                         ["900", "800"])

    def test_a_key_seen_on_another_board_is_still_new_here(self):
        self.assertEqual(state.new_keys(two_board_state(), "greenhouse/databricks", ["202", "101"]), ["101"])

    def test_a_key_that_disappeared_and_came_back_is_not_new(self):
        # 101 was first seen in R1 and was absent from the R2 snapshot; it returns now.
        self.assertEqual(state.new_keys(two_board_state(), "greenhouse/anthropic", ["101", "102"]), [])


class AdvanceTest(unittest.TestCase):
    def test_a_first_snapshot_records_every_key_with_the_run(self):
        after = state.advanced(None, "R1", "2026-11-08T12:00:00Z",
                               {"ashby/linear": ("ashby", "linear", ["u1", "u2"])})
        self.assertEqual(after["boards"]["ashby/linear"],
                         {"ats": "ashby", "slug": "linear", "first_snapshot_run": "R1",
                          "last_snapshot_run": "R1", "seen": {"u1": "R1", "u2": "R1"}})
        self.assertEqual(after["runs"], [{"run_id": "R1", "finished_at": "2026-11-08T12:00:00Z",
                                          "boards": {"ashby/linear": {"jobs": 2, "new": 0, "baseline": True}}}])

    def test_a_later_snapshot_adds_only_unseen_keys_and_keeps_vanished_ones(self):
        before = two_board_state()
        after = state.advanced(before, "R3", "2026-11-09T12:00:00Z",
                               {"greenhouse/anthropic": ("greenhouse", "anthropic", ["102", "103"])})
        self.assertEqual(after["boards"]["greenhouse/anthropic"]["seen"], {"101": "R1", "102": "R2", "103": "R3"})
        self.assertEqual(after["boards"]["greenhouse/anthropic"]["first_snapshot_run"], "R1")
        self.assertEqual(after["boards"]["greenhouse/anthropic"]["last_snapshot_run"], "R3")
        self.assertEqual(after["boards"]["greenhouse/databricks"], before["boards"]["greenhouse/databricks"])
        self.assertEqual(after["runs"][-1]["boards"]["greenhouse/anthropic"], {"jobs": 2, "new": 1, "baseline": False})

    def test_advancing_does_not_change_the_state_it_was_given(self):
        before = two_board_state()
        untouched = copy.deepcopy(before)
        state.advanced(before, "R3", "t", {"greenhouse/anthropic": ("greenhouse", "anthropic", ["999"])})
        self.assertEqual(before, untouched)


class SaveTest(unittest.TestCase):
    def test_an_approved_save_round_trips(self):
        project = Project()
        self.addCleanup(project.cleanup)
        files = Files(Policy(project.root, "R3", set(), Approval("R3", "state/state.json")))
        state.save_state(files, two_board_state())
        self.assertEqual(state.load_state(files), two_board_state())


if __name__ == "__main__":
    unittest.main()
