"""The state file and the allow-list from CONTRACT.md 'The watch' and 'Refuses'."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jobwatch import net, state
from jobwatch.errors import RefusedError, StateError

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
MODEL_URL = "https://api.anthropic.com/v1/messages"


class StateFileTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "state.json"

    def tearDown(self):
        self.dir.cleanup()

    def test_no_state_file_means_first_run(self):
        self.assertIsNone(state.load_state(self.path))

    def test_saved_state_loads_back(self):
        state.save_state(self.path, state.new_state([303, 101]))
        self.assertEqual(state.load_state(self.path)["seen_ids"], [101, 303])

    def test_damaged_state_is_an_error(self):
        for text in ("{not json", "[]", json.dumps({"seen_ids": "101"}),
                     json.dumps(dict(state.new_state([101]), board="openai")),
                     json.dumps(dict(state.new_state([101]), seen_ids=[101, -3])),
                     json.dumps(dict(state.new_state([101]), seen_ids=[101, 101]))):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(StateError):
                    state.load_state(self.path)

    def test_failed_write_leaves_the_previous_state_intact(self):
        state.save_state(self.path, state.new_state([101]))
        before = self.path.read_bytes()
        with mock.patch("jobwatch.state.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                state.save_state(self.path, state.new_state([101, 202]))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(p.name for p in Path(self.dir.name).iterdir()), ["state.json"])


class NewIdsTest(unittest.TestCase):
    def test_new_ids_are_current_minus_everything_seen(self):
        self.assertEqual(state.new_ids([9, 3, 5], {3, 4}), [5, 9])

    def test_an_id_that_disappears_and_returns_is_not_new(self):
        seen = {101, 202}
        self.assertEqual(state.new_ids([101], seen), [])
        self.assertEqual(state.new_ids([101, 202], seen), [])


class AllowListTest(unittest.TestCase):
    def test_the_board_endpoint_is_allowed_for_get(self):
        net.check_allowed("GET", BOARD_URL)

    def test_the_model_endpoint_is_allowed_for_post(self):
        net.check_allowed("POST", MODEL_URL)

    def test_everything_else_is_refused(self):
        refused = [
            ("GET", "http://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"),
            ("GET", "https://boards-api.greenhouse.io/v1/boards/openai/jobs?content=true"),
            ("GET", "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"),
            ("GET", "https://boards-api.greenhouse.io.evil.example/v1/boards/anthropic/jobs?content=true"),
            ("GET", "https://boards-api.greenhouse.io:8443/v1/boards/anthropic/jobs?content=true"),
            ("GET", "https://job-boards.greenhouse.io/anthropic/jobs/4020305008"),
            ("POST", BOARD_URL),
            ("GET", MODEL_URL),
            ("POST", "https://api.anthropic.com/v1/complete"),
        ]
        for method, url in refused:
            with self.subTest(method=method, url=url), self.assertRaises(RefusedError):
                net.check_allowed(method, url)

    def test_the_allow_list_is_checked_before_opening_a_connection(self):
        opened = []
        with self.assertRaises(RefusedError):
            net.request("GET", "https://evil.example/jobs", opener=lambda *a, **k: opened.append(a))
        self.assertEqual(opened, [])

    def test_redirects_are_refused(self):
        handler = net.RefuseRedirects()
        with self.assertRaises(RefusedError):
            handler.redirect_request(None, None, 302, "Found", {}, "https://evil.example/")


if __name__ == "__main__":
    unittest.main()
